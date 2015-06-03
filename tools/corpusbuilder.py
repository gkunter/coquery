from __future__ import unicode_literals
import codecs

import logging
import collections
import os, os.path
import string
try:
    import nltk
    no_nltk = False
except ImportError:
    no_nltk = True    
import dbconnection
import argparse
import re
import time
import sys
import textwrap
import fnmatch
import inspect
try:
    import progressbar
    show_progress = True
except ImportError:
    show_progress = False

class BaseCorpusBuilder(object):
    logger = None
    module_code = None
    name = None
    table_description = None
    lexicon_features = None
    corpus_features = None
    arguments = None
    name = None
    additional_arguments = None
    parser = None
    Con = None
    additional_stages = []
    start_time = None
    file_filter = None
    
    def __init__(self, ):
        self.module_code = """# -*- coding: utf-8 -*-
#
# FILENAME: {name}.py -- a corpus module for the Coquery corpus query tool
# 
# This module was automatically created by corpusbuilder.py.
#

from corpus import *

class Resource(SQLResource):
    name = '{name}'
    db_name = '{db_name}'
{variables}
{resource_code}
    
class Lexicon(SQLLexicon):
    provides = {lexicon_provides}
    
{lexicon_code}
class Corpus(SQLCorpus):
    provides = {corpus_provides}
    
{corpus_code}
"""
        self.table_description = {}
        self.lexicon_features = []
        self.corpus_features = []
        self._tables = {}
        self._id_count = {}
        self._primary_keys = {}
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("name", help="name of the corpus", type=str)
        self.parser.add_argument("path", help="location of the text files", type=str)
        self.parser.add_argument("--db_name", help="name of the MySQL database to be used (default: same as 'name')", type=str)
        self.parser.add_argument("-o", help="optimize field structure (can be slow)", action="store_true")
        self.parser.add_argument("-w", help="Actually do something; default behaviour is simulation.", action="store_false", dest="dry_run")
        self.parser.add_argument("-v", help="produce verbose output", action="store_true", dest="verbose")
        self.parser.add_argument("-i", help="create indices (can be slow)", action="store_true")
        if not no_nltk:
            self.parser.add_argument("-no_nltk", help="Do not use NLTK library for automatic part-of-speech tagging", action="store_false", dest="use_nltk")
        self.parser.add_argument("-l", help="load source files", action="store_true")
        self.parser.add_argument("-c", help="Create database tables", action="store_true")
        self.parser.add_argument("--corpus_path", help="target location of the corpus library (default: $COQUERY_HOME/corpora)", type=str)
        self.parser.add_argument("--self_join", help="create a self-joined table (can be very big)", action="store_true")

    def check_arguments(self):
        self.arguments, unknown = self.parser.parse_known_args()
        self.name = self.arguments.name
        if not self.arguments.db_name:
            self.arguments.db_name = self.arguments.name
        
    def add_argument(self, *args):
        pass
    
    def add_table_description(self, table_name, primary_key, table_description):
        for i, x in enumerate(table_description["CREATE"]):
            if "`{}`".format(primary_key) in x:
                table_description["CREATE"][i] = "{} AUTO_INCREMENT".format(
                    table_description["CREATE"][i])
        table_description["CREATE"].append("PRIMARY KEY (`{}`)".format(primary_key))
        self.table_description[table_name] = table_description
        
        self._tables[table_name] = {}
        self._primary_keys[table_name] = primary_key
        self._id_count[table_name] = 0
        
    def table_add(self, table_name, values):
        """ Add an entry containing the values to the table. A new unique
        id is also provided, and the class counter is updated. """
        self.Con.insert(table_name, values)
        return 
    
    def table_get(self, table_name, values):
        """ This function returns the id of the entry matching the values 
        from the table. If there is no entry matching the values in the
        table, a new entry is added to the table based on the values.
        The values have to be given in the same order as the column 
        specifications in the table description."""
        key= "".join(["%s" % x for x in values.values()])
        if key in self._tables[table_name]:
            return self._tables[table_name][key]
        try_entry = self.Con.find(
            table_name, values, [self._primary_keys[table_name]])
        if not try_entry:
            self.Con.insert(table_name, values)
            entry = self.Con.find(table_name, values, [self._primary_keys[table_name]])
        else:
            entry = try_entry
        try:
            self._tables[table_name][key] = entry[0]
        except Exception as e:
            print entry
            print values
            print key
            raise e

        return entry[0]

    def setup_logger(self):
        class TextwrapFormatter(logging.Formatter):
            def __init__(self, fmt):
                super(TextwrapFormatter, self).__init__(fmt=fmt)
                self.wrap = textwrap.TextWrapper(width=79, subsequent_indent="        ").fill
                
            def format(self, entry):
                return "\n%s\n" % self.wrap(super(TextwrapFormatter, self).format(entry))
        
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel (logging.INFO)
        log_file_name = "%s.log" % self.name
        file_handler = logging.FileHandler(log_file_name)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
        self.logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(TextwrapFormatter("%(levelname)s %(message)s"))
        stream_handler.setLevel(logging.WARNING)
        self.logger.addHandler(stream_handler)

    def create_tables(self):
        if show_progress:
            progress = progressbar.ProgressBar(widgets=["Creating tables ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=len(self.table_description))
            progress.start()
        for i, current_table in enumerate(self.table_description):
            if not self.Con.has_table(current_table):
                self.Con.create_table(current_table, ", ".join(self.table_description[current_table]["CREATE"]), override=True)
            if show_progress:
                progress.update(i)
        self.Con.commit()    
        if show_progress:
            progress.finish()

    def get_file_list(self, path):
        L = []
        for source_path, folders, files in os.walk(path):
            for current_file in files:
                full_name = os.path.join(source_path, current_file)
                if not self.file_filter or fnmatch.fnmatch(current_file, self.file_filter):
                    L.append(full_name)
        return L

    def get_corpus_code(self):
        try:
            lines = [x for x in inspect.getsourcelines(self._corpus_code)[0] if not x.strip().startswith("class")]
        except AttributeError:
            lines = []
        return "".join(lines)
    
    def get_lexicon_code(self):
        return ""
    
    def get_resource_code(self):
        return ""
    
    def get_method_code(self, method):
        pass

    def process_file(self, current_file):
        with codecs.open(current_file, "rt", encoding="utf8") as input_file:
            raw_text = input_file.read()
        if self.arguments.use_nltk:
            tokens = nltk.word_tokenize(raw_text)
            pos_map = nltk.pos_tag(tokens)
        else:
            tokens = raw_text.split(" ")
            pos_map = zip(tokens, [""] * len(tokens))
        
        for current_token, current_pos in pos_map:
            current_token = current_token.strip()
            if current_token in string.punctuation:
                current_pos = "PUNCT"
                
            lemma_id = self.table_get(self.lemma_table, 
                                {self.lemma_label: current_token.lower()})[self.lemma_id]
            
            word_id = self.table_get(self.word_table, 
                                {self.word_lemma_id: lemma_id, 
                                self.word_pos_id: current_pos, 
                                self.word_label: current_token})[self.word_id]

            self.Con.insert(self.corpus_table, 
                {self.corpus_word_id: word_id,
                 self.corpus_source_id: self._file_id})

    def load_files(self):
        files = self.get_file_list(self.arguments.path)
        if not files:
            self.logger.warning("No files found at %s" % self.arguments.path)
            return
        if no_nltk:
            self.logger.warning("This script can use the NLTK library for automatic part-of-speech tagging. However, this library is not installed on this computer. Follow the steps from http://www.nltk.org/install.html to install this library.")
        
        if show_progress:
            progress = progressbar.ProgressBar(widgets=["Loading data files ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=len(files))
            progress.start()
            
        for x in self.table_description:
            #self._tables[x] = self.Con.read_table(x, lambda x: "".join(["%s" % y for y in x[1:]]))
            self._id_count[x] = self.Con.get_max(x, self._primary_keys[x])
        
        for file_count, file_name in enumerate(files):
            if not self.Con.find(self.file_table, {self.file_label: file_name}):
                self.logger.info("Loading file %s" % (file_name))
                self._file_id = self.table_get(self.file_table, 
                    {self.file_label: file_name})[self.file_id]
                self.process_file(file_name)
                
            if show_progress:
                progress.update(file_count)

            self.Con.commit()
        if show_progress:
            progress.finish()
    
    def create_joined_table(self):
        pass
    
    def optimize(self):
        totals = 0
        for current_table in self.table_description:
            totals += len(self.table_description[current_table]["CREATE"]) - 1
        
        if show_progress:
            progress = progressbar.ProgressBar(widgets=["Optimizing field type ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=totals)
            progress.start()
            
        column_count = 0
        for current_table in self.table_description:
            field_specs = self.table_description[current_table]["CREATE"]
            for current_spec in field_specs:
                match = re.match ("`(\w+)`", current_spec)
                if match:
                    current_field = match.group(1)
                    self.logger.info("Determine current and optimal type for column {}.{}".format(
                        current_table, current_field))
                    optimal_type = self.Con.get_optimal_field_type(current_table, current_field)
                    current_type = self.Con.get_field_type(current_table, current_field)
                    if current_type.lower() != optimal_type.lower():
                        self.logger.info("Optimising column {}.{} from {} to {}".format(
                            current_table, current_field, current_type, optimal_type))
                        try:
                            self.Con.modify_field_type(current_table, current_field, optimal_type)
                        except dbconnection.mysql.OperationalError as e:
                            if self.logger:
                                self.logger.error(e)
                    column_count += 1
            if show_progress:
                progress.update(column_count)
            self.Con.commit()
        if show_progress:
            progress.finish()
        
    def create_indices(self):
        total_indices = 0
        for current_table in self.table_description:
            if "INDEX" in self.table_description[current_table]:
                total_indices += len(self.table_description[current_table]["INDEX"])
        
        if show_progress:
            progress = progressbar.ProgressBar(widgets=["Indexing ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_indices)
            progress.start()
        index_count = 0
        for current_table in self.table_description:
            description = self.table_description[current_table]
            if "INDEX" in description:
                for variables, length, index_type in description["INDEX"]:
                    current_index = "_".join(variables)
                    if not self.Con.has_index(current_table, current_index):
                        self.logger.info("Creating index {} on table '{}'".format(
                            current_index, current_table))
                        self.Con.create_index(current_table, current_index, variables, index_type, length)
                    index_count += 1
            if show_progress:
                progress.update(index_count)
            self.Con.commit()
        if show_progress:
            progress.finish()
    
    def get_class_variables(self):
        return dir(BaseCorpusBuilder)

    def write_python_module(self, corpora_path):
        base_variables = self.get_class_variables()
        
        # all class variables that are defined in this class and which...
        # - are note stored in the base class
        # - do not start with an underscore '_'
        # - are not class methods
        # are considered to be part of the database specification and will
        # be included with their value in the Python code:
        variable_names = [x for x in dir(self) 
                          if x not in base_variables 
                          and not x.startswith("_")
                          and not inspect.ismethod(self.__getattribute__(x))]
        variable_strings = []
        for variable_name in sorted(variable_names):
            variable_strings.append("    {} = '{}'".format(
                variable_name, self.__dict__[variable_name]))
        variable_code = "\n".join(variable_strings)
        
        lexicon_provides = "[{}]".format(", ".join(self.lexicon_features))
        corpus_provides = "[{}]".format(", ".join(self.corpus_features))
        
        output_code = self.module_code.format(
                name=self.name,
                db_name=self.arguments.db_name,
                variables=variable_code,
                lexicon_provides=lexicon_provides,
                corpus_provides=corpus_provides,
                corpus_code=self.get_corpus_code(),
                lexicon_code=self.get_lexicon_code(),
                resource_code=self.get_resource_code())
        
        path = os.path.join(corpora_path, "{}.py".format(self.name))
        # Handle existing versions of the corpus library
        if os.path.exists(path):
            # Read existing code as string:
            with open(path, "rt") as input_file:
                existing_code = input_file.read()
            # Keep if existing code is the same as the new code:
            if existing_code == output_code:
                self.logger.info("Identical corpus library %s already exists." % path)
                return
            # Ask if the existing code should be overwritten:
            else:
                self.logger.warning("A different version of the corpus library already exists in %s." % path)
                print("Enter Y to overwrite the existing version.")
                print("Enter N to keep the existing version.")
                while True:
                    try:
                        input = raw_input("Overwrite? [Y or N] ")
                    except NameError:
                        input = input("Overwrite? [Y or N] ")
                    if input.upper() != "Y":
                        return
                    else:
                        self.logger.warning("Overwriting library.")
                    break
        # write library code:
        with open(path, "wt") as output_file:
            output_file.write(output_code)
            self.logger.info("Library %s written." % path)
            
    def setup_db(self):
        dbconnection.verbose = self.arguments.verbose
        dbconnection.logger = self.logger
        self.Con = dbconnection.DBConnection(self.arguments.db_name, local_infile=1)
        self.Con.dry_run = self.arguments.dry_run
        if not self.arguments.dry_run:
            self.Con.set_variable("autocommit", 0)
            self.Con.set_variable("unique_checks", 0)
            self.Con.set_variable("foreign_key_checks", 0)

    def add_building_stage(self, stage):
        self.additional_stages.append(stage)

    def get_description(self):
        return ""


    def get_speaker_data(self, *args):
        return []

    def initialize_build(self):
        self.start_time = time.time()
        if self.arguments.dry_run:
            self.logger.info("--- Starting (dry run) ---")
        else:
            self.logger.info("--- Starting ---")
        self.logger.info("Building corpus %s" % self.name)
        self.logger.info("Command line arguments: %s" % " ".join(sys.argv[1:]))
        print("\n%s\n" % textwrap.TextWrapper(width=79).fill(self.get_description()))

    def finalize_build(self):
        self.logger.info("--- Done (after %.3f seconds) ---" % (time.time() - self.start_time))

    def build(self):
        self.check_arguments()
        self.setup_logger()
        self.setup_db()
        
        self.initialize_build()
        
        if self.arguments.c:
            self.create_tables()
        if self.arguments.l:
            self.load_files()
        if self.arguments.self_join:
            self.self_join()
            
        for stage in self.additional_stages:
            stage()
            
        if self.arguments.o:
            self.optimize()
        if self.arguments.i:
            self.create_indices()
        if self.arguments.corpus_path:
            self.write_python_module(self.arguments.corpus_path)

        self.finalize_build()
                
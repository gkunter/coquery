# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
import codecs

import logging
import collections
import os, os.path
import string

import dbconnection
import argparse
import re
import time
import sys
import textwrap
import fnmatch
import inspect
import xml.etree.ElementTree as ET

try:
    from pyqt_compat import QtCore, QtGui
    import options
    import corpusBuilderUi
    import error_box
    use_gui = True
except ImportError:
    print("Import error; GUI will not be available.")
    use_gui = False
    pass

try:
    import nltk
except ImportError:
    print("NLTK module not available.")
    try:
        QtGui.QMessageBox.warning("No NLTK module – Coquery", "The NLTK module could not be loaded. Automatic part-of-speech tagging will not be available.", QtGui.QMessageBox.Ok)
    except NameError:        
        pass
    nltk_available = False
else:
    nltk_available = True

try:
    import progressbar
    show_progress = True
except ImportError:
    show_progress = False


insert_cache = collections.defaultdict(list)

class NLTKTokenizerError(Exception):
    def __init__(self, e, logger):
        logger.error("The NLTK tokenizer failed. This may be caused by a missing NLTK component. Please consult the 'Installing NLTK Data' guide on http://www.nltk.org/data.html for instructions on how to add the necessary components. Alternatively, you may want to use --no-nltk argument to disable the use of NLTK.")
        logger.error(e)
        if use_gui:
            error_box.ErrorBox.show(sys.exc_info(), self)
        
class NLTKTaggerError(Exception):
    def __init__(self, e, logger):
        logger.error("The NLTK tagger failed. This may be caused by a missing NLTK component. Please consult the 'Installing NLTK Data' guide on http://www.nltk.org/data.html for instructions on how to add the necessary components. Alternatively, you may want to use --no-nltk argument to disable the use of NLTK.")
        logger.error(e)
        if use_gui:
            error_box.ErrorBox.show(sys.exc_info(), self)

class MethodNotImplementedError(Exception):
    msg = "Function not impemented."

# module_code contains the Python skeleton code that will be used to write
# the Python corpus module."""
module_code = """# -*- coding: utf-8 -*-
#
# FILENAME: {name}.py -- a corpus module for the Coquery corpus query tool
# 
# This module was automatically created by corpusbuilder.py.
#

from __future__ import unicode_literals
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

# Corpus builders should include code that determines word counts for 
# subcorpora. More specifically, they should produce a table with all
# combinations of corpus features and the associated number of words.
# For example, COCA should have a table with Genre, Year and Frequency,
# with 5 x 23 rows (5 Genres, 23 Years). 

in_memory = False

class Column(object):
    """ Define an object that stores the description of a column in one 
    MySQL table."""
    primary = False
    key = False
    
    def __init__(self, name, data_type, index=True):
        """ Initialize the column. 'name' is the column name, 'data_type' is
        the MySQL data type for this column. If 'index' is True (the 
        default), an index will be created for this column."""
        self._name = name
        self._data_type = data_type
        self._index = index
        
    def __repr__(self):
        return "Column({}, {}, {})".format(self._name, self._data_type, self._index)
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):
        self._name = new_name
    
    @property
    def data_type(self):
        return self._data_type
    
    @data_type.setter
    def data_type(self, new_type):
        self._data_type = new_type
        
class Primary(Column):
    """ Define a Column class that acts as the primary key in a table."""
    primary = True

    def __init__(self, name, data_type):
        super(Primary, self).__init__(name, data_type, False)

    def __repr__(self):
        return "Primary(name='{}', data_type='{}', {})".format(self._name, self._data_type, self._index)
        
    
class Link(Column):
    """ Define a Column class that links a table to another table. In MySQL
    terms, this acts like a foreign key."""
    key = True
    def __init__(self, name, table_name):
        super(Link, self).__init__(name, "", True)
        self._link = table_name

    def __repr__(self):
        return "Link(name='{}', '{}', data_type='{}')".format(self._name, self._link, self._data_type)
        
class Table(object):
    """ Define a class that is used to store table definitions."""
    def __init__(self, name):
        self._name = name
        self.columns = list()
        self.primary = None
        self._current_id = 0
        self._add_cache = collections.OrderedDict()
        self._commited = {}
        self._col_names = None
        
    def commit(self, db_connector):
        if self._add_cache:
            sql_string = "INSERT INTO {} ({}) VALUES ({})".format(
                self._name, ", ".join([self.primary.name] + self._col_names), ", ".join(["%s"] * (len(self._col_names) + 1)))
            data = []
            for row in self._add_cache:
                row_id, row_data = self._add_cache[row]
                if row_data:
                    data.append([row_id] + row_data.values())
            #data = [[row_id] + row.values() for row_id, row in self._add_cache if row]
            if data: 
                db_connector.executemany(sql_string, data)
                for row in self._add_cache:
                    row_id, row_data = self._add_cache[row]
                    self._add_cache[row] = (row_id, None)        
    
    def add_data(self, row):
        """ Add a valid primary key to the data in the 'row' dictionary, 
        and store the data in add cache of the table. """ 
        if not self._col_names:
            self._col_names = row.keys()
        self._current_id += 1
        
        self._add_cache[tuple([row[x] for x in sorted(row)])] = (self._current_id, row)
        return self._current_id
        
    def get_or_insert(self, row):
        """ Either return the id of the cached row, or insert the row as a
        new entry and return the new id."""
        
        try:
            return self._add_cache[tuple([row[x] for x in sorted(row)])][0]
        except KeyError:
            return self.add_data(row)
        
    def get_data_id(self, row):
        try:
            return self._add_cache[tuple([row[x] for x in sorted(row)])][0]
        except KeyError:
            return None
        
    def add_column(self, column):
        self.columns.append(column)
        if column.primary:
            self.primary = column
            
    def get_create_string(self):
        str_list = []
        for column in self.columns:
            if column.primary:
                if in_memory:
                    str_list.insert(0, "`{}` {}".format(
                        column.name,
                        column.data_type))
                else:
                    str_list.insert(0, "`{}` {} AUTO_INCREMENT".format(
                        column.name,
                        column.data_type))
                    str_list.append("PRIMARY KEY (`{}`)".format(column.name))
            else:
                str_list.append("`{}` {}".format(
                    column.name,
                    column.data_type))
        return ", ".join(str_list)
    
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
    
    def __init__(self, gui=False):
        self.module_code = module_code
        self.table_description = {}
        self.lexicon_features = []
        self.corpus_features = []
        self._tables = {}
        self._id_count = {}
        self._primary_keys = {}
        
        self._new_tables = {}
        
        self._corpus_buffer = []
        
        self._widget = gui
        
        if not gui:        
            # set up argument parser:
            self.parser = argparse.ArgumentParser()
            self.parser.add_argument("name", help="name of the corpus", type=str)
            self.parser.add_argument("path", help="location of the text files", type=str)
            self.parser.add_argument("--db_user", help="name of the MySQL user (default: coquery)", type=str, default="coquery", dest="db_user")
            self.parser.add_argument("--db_password", help="password of the MySQL user (default: coquery)", type=str, default="coquery", dest="db_password")
            self.parser.add_argument("--db_host", help="name of the MySQL server (default: localhost)", type=str, default="localhost", dest="db_host")
            self.parser.add_argument("--db_port", help="port of the MySQL server (default: 3306)", type=int, default=3306, dest="db_port")
            self.parser.add_argument("--db_name", help="name of the MySQL database to be used (default: same as 'name')", type=str)
            self.parser.add_argument("-o", help="optimize field structure (can be slow)", action="store_true")
            self.parser.add_argument("-w", help="Actually do something; default behaviour is simulation.", action="store_false", dest="dry_run")
            self.parser.add_argument("-v", help="produce verbose output", action="store_true", dest="verbose")
            self.parser.add_argument("-i", help="create indices (can be slow)", action="store_true")
            if nltk_available:
                self.parser.add_argument("--no-nltk", help="Do not use NLTK library for automatic part-of-speech tagging", action="store_false", dest="use_nltk")
            self.parser.add_argument("-l", help="load source files", action="store_true")
            self.parser.add_argument("-c", help="Create database tables", action="store_true")
            self.parser.add_argument("--corpus_path", help="target location of the corpus library (default: $COQUERY_HOME/corpora)", type=str)
            self.parser.add_argument("--self_join", help="create a self-joined table (can be very big)", action="store_true")
            self.parser.add_argument("--encoding", help="select a character encoding for the input files (e.g. latin1, default: utf8)", type=str, default="utf8")
            self.parser.add_argument("--in_memory", help="try to improve writing speed by retaining tables in working memory. May require a lot of memory for big corpora.", action="store_true")
            self.additional_arguments()

    def add_tag_table(self):
        """ Corpora should usually have a tag table that is used to store
        text information. This method is called by the build() method and
        adds a tag table if none is present yet."""
        
        if "tag_table" in dir(self):
            return
        
        self.tag_table = "tags"
        self.tag_id = "TagId"
        self.tag_label = "Tag"
        self.tag_type = "Type"
        self.tag_corpus_id = self.corpus_id
        self.tag_attribute = "Attribute"
        
        self.add_table_description(self.tag_table, self.tag_id,
            {"CREATE": [
                "`{}` MEDIUMINT(6) UNSIGNED NOT NULL".format(self.tag_id),
                "`{}` ENUM('open', 'close', 'empty')".format(self.tag_type),
                "`{}` TINYTEXT NOT NULL".format(self.tag_label),
                "`{}` MEDIUMINT(6) UNSIGNED NOT NULL".format(self.tag_corpus_id),
                "`{}` TINYTEXT NOT NULL".format(self.tag_attribute)],
            "INDEX": [
                ([self.tag_corpus_id], 0, "HASH"),
                ([self.tag_label], 0, "BTREE"),
                ([self.tag_type], 0, "BTREE")]})
            
        self.add_new_table_description(self.tag_table,
            [Primary(self.tag_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.tag_type, "ENUM('open', 'close', 'empty')"),
             Column(self.tag_label, "TINYTEXT NOT NULL"),
             Link(self.tag_corpus_id, self.corpus_table),
             Column(self.tag_attribute, "TINYTEXT NOT NULL", index=False)])

    def check_arguments(self):
        global in_memory
        """ Check the command line arguments. Add defaults if necessary."""
        if not self._widget:
            self.arguments, unknown = self.parser.parse_known_args()
            if not nltk_available:
                self.arguments.use_nltk = False
            if not self.arguments.db_name:
                self.arguments.db_name = self.arguments.name
            if not self.arguments.corpus_path:
                self.arguments.corpus_path = os.path.normpath(os.path.join(sys.path[0], "../coquery/corpora"))
            self.name = self.arguments.name
            
            in_memory = self.arguments.in_memory
            
    def additional_arguments(self):
        """ Use this function if your corpus installer requires additional arguments."""
        pass
    
    def commit_data(self):
        if in_memory:
            for table in self._new_tables:
                self._new_tables[table].commit(self.Con)
        elif self._corpus_buffer:
            sql_string = "INSERT INTO {} ({}) VALUES ({})".format(
                self.corpus_table, ", ".join(self._corpus_keys), ", ".join(["%s"] * (len(self._corpus_keys))))
            data = [row.values() for row in self._corpus_buffer]
            if data: 
                try:
                    self.Con.executemany(sql_string, data)
                except TypeError as e:
                    print(sql_string, data[0])
                    raise(e)
            self._corpus_buffer = []        
            
        self.Con.commit()

    
    def add_new_table_description(self, table_name, column_list):
        new_table = Table(table_name)
        for x in column_list:
            if isinstance(x, Link):
                x.data_type = self._new_tables[x._link].primary.data_type
            new_table.add_column(x)
        self._new_tables[table_name] = new_table
                
    def add_table_description(self, table_name, primary_key, table_description):
        """ Add a primary key to the table description and the internal
        tables."""
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
        return self.Con.insert(table_name, values)
    
    def table_find(self, table_name, values):
        """ Return the first row that matches the values, or None
        otherwise."""
        
        if in_memory:
            keys_values = set(values.keys())
            table = self._new_tables[table_name]
            keys_table = sorted(table._col_names)
            lookup_list = {}
            
            for key in values:
                try:
                    lookup_list[key] = keys_table.index(key)
                except IndexError:
                    pass

            if lookup_list:
                for key in table._add_cache:
                    for lookup in lookup_list:
                        if values[lookup] != key[lookup_list[lookup]]:
                            break
                        else:
                            row_id, _ = table._add_cache[key]
                            return 
            return None
        else:
            try:
                return self.Con.find(table_name, values, [self._primary_keys[table_name]])[0]
            except IndexError:
                return None
    
    def table_get(self, table_name, values, case=False):
        """ This function returns the id of the first entry matching the 
        values from the table. If there is no entry matching the values in 
        the table, a new entry is added to the table based on the values.
        The values have to be given in the same order as the column 
        specifications in the table description."""

        # use new internal tables:
        
        if in_memory:
            row_id = self._new_tables[table_name].get_data_id(values)
            if row_id:
                return row_id
            else:
                return self._new_tables[table_name].add_data(values)

        key = tuple(values.values())
        if key in self._tables[table_name]:
            return self._tables[table_name][key]
        else:
            last = self.Con.insert(table_name, values)
            self._tables[table_name][key] = last
            return last
        

    def setup_logger(self):
        """ initializes a logger."""
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
        """ go through the table description and create a table in the
        database, using the information from the "CREATE" key of the
        table description entry."""
        
        self.Con.start_transaction()
        self.add_tag_table()
        if self._widget:
            self._widget.ui.progress_bar.setFormat("Creating tables... (%v of %m)")
            self._widget.ui.progress_bar.setMaximum(len(self.table_description))
            self._widget.ui.progress_bar.setValue(0)
        elif show_progress:
            progress = progressbar.ProgressBar(widgets=["Creating tables ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=len(self.table_description))
            progress.start()
        for i, current_table in enumerate(self.table_description):
            if not self.Con.has_table(current_table):
                if self._new_tables:
                    self.Con.create_table(current_table, self._new_tables[current_table].get_create_string())
                else:
                    self.Con.create_table(current_table, ", ".join(self.table_description[current_table]["CREATE"]), override=True)
            if self._widget:
                self._widget.ui.progress_bar.setValue(i)
            elif show_progress:
                progress.update(i + 1)
        self.Con.commit()

        if show_progress and not self._widget:
            progress.finish()

    def get_file_list(self, path):
        """ returns a list of file names from the given path that match
        the file filter from self.file_filter."""
        L = []
        for source_path, folders, files in os.walk(path):
            for current_file in files:
                full_name = os.path.join(source_path, current_file)
                if not self.file_filter or fnmatch.fnmatch(current_file, self.file_filter):
                    L.append(full_name)
        return L

    def get_corpus_code(self):
        """ return a text string containing the Python source code from
        the class attribute self._corpus_code. This function is needed
        to add corpus-specifc to the Python corpus module."""
        try:
            lines = [x for x in inspect.getsourcelines(self._corpus_code)[0] if not x.strip().startswith("class")]
        except AttributeError:
            lines = []
        return "".join(lines)
    
    def get_lexicon_code(self):
        """ return a text string containing the Python source code from
        the class attribute self._lexicon_code. This function is needed
        to add lexicon-specific code the Python corpus module."""
        try:
            lines = [x for x in inspect.getsourcelines(self._lexicon_code)[0] if not x.strip().startswith("class")]
        except AttributeError:
            lines = []
        return "".join(lines)
    
    def get_resource_code(self):
        """ return a text string containing the Python source code from
        the class attribute self._resource_code. This function is needed
        to add resource-specific code the Python corpus module."""
        try:
            lines = [x for x in inspect.getsourcelines(self._resource_code)[0] if not x.strip().startswith("class")]
        except AttributeError:
            lines = []
        return "".join(lines)
    
    def get_method_code(self, method):
        pass

    def store_filename(self, current_file):
        self._file_name = current_file
        self._file_id = self.table_get(self.file_table, 
            {self.file_path: current_file,
             self.file_name: 
                 os.path.splitext(os.path.basename(current_file))[0]
                 })

    def get_lemma(self, word):
        """ Return a lemma for the word. By default, this is simply the
        word in lower case, but this method can be overloaded with methods
        that use e.g. lemma dictionaries. 
        The method is used by the default file processing methods. If your
        corpus implements a specific file processing method, get_lemma() may
        be obsolete. """
        return word.lower()
    
    def get_lemma_id(self, word):
        """ Return a lemma identifier for the word. If there is a separate 
        lemma table, the identifier is an index to that table. Otherwise, 
        the identifier is the lemma label."""
        
        if "lemma_table" in self.table_description:
            return self.table_get(self.lemma_table, 
                {self.lemma_label: self.get_lemma(word)})
        else:
            return self.get_lemma(word)
    
    def get_pos(self, word):
        """ Return the part-of-speech for the word. By default, an empty
        string is returned, but this method may be overloaded with methods
        that use for example a pos-tagged dictionary.
        The method is used by the default file processing methods. If your
        corpus implements a specific file processing method, get_lemma() may
        be obsolete. """
        return ""
    
    def get_pos_id(self, word):
        """ Return a part-of-speech identifier for the word. If there is a 
        separate part-of-speech table, the identifier is an index to that 
        table. Otherwise, the identifier is the part-of-speech label."""
        
        if "pos_table" in self.table_description:
            return self.table_get(self.pos_table, 
                {self.pos_label: self.get_pos(word)})
        else:
            return self.get_pos(word)        

    def get_transcript(self, word):
        """ Return the phonemic transcript for the word. By default, an 
        empty string is returned, but this method may be overloaded with 
        methods that use for example a pronunciation dictionary.
        The method is used by the default file processing methods. If your
        corpus implements a specific file processing method, get_lemma() may
        be obsolete. """
        return ""
    
    def get_transcript_id(self, word):
        """ Return a transcription identifier for the word. If there is a 
        separate transcription table, the identifier is an index to that 
        table. Otherwise, the identifier is the transcript label."""
        
        if "transcript_table" in self.table_description:
            return self.table_get(self.transcript_table, 
                {self.transcript_label: self.get_transcript(word)})
        else:
            return self.get_transcript(word)        

    def process_xlabel_file(self, current_file):
        """ Process an xlabel file.
        xlabel files are used by ESPS/waves+ to store phonetic 
        annotations. Some spoken corpora are provided in this format.
        A description can be found here:
        http://staffhome.ecm.uwa.edu.au/~00014742/research/speech/local/entropic/ESPSDoc/waves/manual/xlabel.pdf
        """
        
        # xlabel files consist of a header and a file body, separated by a
        # row containing only the hash mark '#'. Everything preceding this 
        # mark is ignored:
        file_body = False
        try:
            with codecs.open(current_file, "rt", encoding=self.arguments.encoding) as input_file:
                input_data = input_file.read()
        except UnicodeDecodeError:
            with codecs.open(current_file, "rt", encoding="ISO-8859-1") as input_file:
                input_data = input_file.read()
        input_data = input_data.splitlines()
        for row in input_data:
            # only process the lines after the hash mark:
            if row.strip() == "#":
                file_body = True
            elif file_body:
                try:
                    time, color, word = row.split()
                # in xlabel files, rows can contain only the time tag,
                # but no other labels. In this case, the row is ignored:
                except ValueError:
                    continue
                
                # create a dictionary containing the word label, plus
                # additional labels if provided by the lexicon:
                word_dict = {}
                word_dict[self.word_label] = word
                if "LEX_LEMMA" in self.lexicon_features:
                    word_dict[self.word_lemma_id] = self.get_lemma_id(word)
                if "LEX_POS" in self.lexicon_features:
                    word_dict[self.word_pos] = self.get_pos_id(word)
                if "LEX_PHON" in self.lexicon_features:
                    word_dict[self.word_transcript_id] = self.get_transcript_id(word)

                # get a word id for the current word:
                word_id = self.table_get(self.word_table, word_dict)
                
                # add the word as a new token to the corpus:
                self.table_add(self.corpus_table, 
                    {self.corpus_word_id: word_id, 
                        self.corpus_file_id: self._file_id,
                        self.corpus_time: time})
                
    def process_text_file(self, current_file):
        """ Process a text file.
        First, attempt to tokenize the text, and to assign a POS tag to each
        token (using NLTK if possible).
        Then, if the token does not exist in the word table, add a new word
        with its POS tag to the word table.
        Then, try to lemmatize any new word
        Finally, add the token with its word identifier to the corpus table."""
        
        # Read raw text from file:
        try:
            with codecs.open(current_file, "rt", encoding=self.arguments.encoding) as input_file:
                raw_text = input_file.read()
        except UnicodeDecodeError:
            with codecs.open(current_file, "rt", encoding="ISO-8859-1") as input_file:
                raw_text = input_file.read()
            
        tokens = []
        pos_map = []

        if self.arguments.use_nltk:
            self.lemmatize = lambda x,y: nltk.stem.wordnet.WordNetLemmatizer().lemmatize(x, pos=y)
            self.pos_translate = lambda x:{'NN':nltk.corpus.wordnet.NOUN, 
                 'JJ':nltk.corpus.wordnet.ADJ,
                 'VB':nltk.corpus.wordnet.VERB,
                 'RB':nltk.corpus.wordnet.ADV} [x.upper()[:2]]

            sentence_list = nltk.sent_tokenize(raw_text)
            for sentence in sentence_list:
                tokens = nltk.word_tokenize(sentence)
                pos_map = nltk.pos_tag(tokens)
                if not sentence:
                    print("empty")
                for current_token, current_pos in pos_map:
                    if current_token in string.punctuation:
                        current_pos = "PUNCT"

                    self.add_token(current_token.strip(), current_pos)
            return
        else:
        # The default lemmatizer is pretty dumb and simply turns the 
        # word-form to lower case so that at least 'Dogs' and 'dogs' are 
        # assigned the same lemma -- which is a different lemma from the
        # one assigned to 'dog' and 'Dog'.
        #
        # If NLTK is used, the lemmatizer will use the data from WordNet,
        # which will result in much better results.
            self.lemmatize = lambda x: x.lower()
            self.pos_translate = lambda x: x
            # create a list of all tokens, either using NLTK or using a 
            # dumb tokenizer that simply splits by spaces.        
            
            tokens = raw_text.split(" ")
            tokens = [x.strip() for x in tokens if x.strip()]
            if not pos_map:
                pos_map = zip(tokens, [""] * len(tokens))
                if "LEX_POS" in self.lexicon_features:
                    self.lexicon_features.remove("LEX_POS")
            
            for current_token, current_pos in pos_map:
                # any punctuation at the beginning of the token is added to the
                # corpus as a punctuation token, and is also stripped from the
                # token:
                while current_token and current_token[0] in string.punctuation:
                    self.add_token(current_token[0], "PUNCT")
                    current_token = current_token[1:]
                if current_token:
                    # add the token to the corpus:
                    self.add_token(current_token, current_pos)
    
    def add_token_to_corpus(self, values):
        if len(values) <> len(self.table_description[self.corpus_table]["CREATE"]) - 2:
            print(self.table_description[self.corpus_table]["CREATE"])
            print(len(values), values)
            raise IndexError

        self._corpus_id += 1
        values[self.corpus_id] = self._corpus_id
        self._corpus_keys = values.keys()
        self._corpus_buffer.append(values)
    
    def add_token(self, token_string, token_pos):
        if token_string in string.punctuation:
            token_pos = "PUNCT"
            lemma = token_string
        else:
            try:
                # use the current lemmatizer to assign the token to a lemma: 
                lemma = self.lemmatize(token_string, self.pos_translate(token_pos)).lower()
            except Exception as e:
                lemma = token_string.lower()
        # get word id, and create new word if necessary:
        word_dict = {self.word_lemma: lemma, 
                    self.word_label: token_string}
        if token_pos and "word_pos" in dir(self):
            word_dict[self.word_pos] = token_pos 

        word_id = self.table_get(self.word_table, word_dict, case=True)
        # store new token in corpus table:
        self.Con.insert(self.corpus_table, 
            {self.corpus_word_id: word_id,
                self.corpus_file_id: self._file_id})

    
    ### METHODS FOR XML FILES

    def xml_parse_file(self, file_object):
        """ Return the root of the XML parsed tree from the file object. 
        If there is a parsing error, print the surrounding environment and 
        raise an exception."""
        try:
            e = ET.parse(file_object).getroot()
        except ET.ParseError as e:
            # in case of a parsing error, print the environment that caused
            # the failure:
            m = re.search(r"line (\d*), column (\d*)", str(e))
            if m:
                line = int(m.group(1))
                column = int(m.group(2))
                start_line = max(0, line - 5)
                end_line = line + 5
            else:
                start_line = 0
                end_line = 999999
            S = S.splitlines()
            self.logger.error(e)
            for i, x in enumerate(S):                
                if i > start_line:
                    print("{:<3}: {}".format(i, x.decode("utf8")))
                if i == line - 1:
                    print("      " + " " * (column - 1) + "^")
                if i > end_line:
                    break
            raise e
        return e

    def xml_get_body(self, root):
        """ Return the XML body from the root."""
        raise MethodNotImplementedError

    def xml_get_meta_information(self, root):
        """ Retrieve and store all meta information from the root."""
        raise MethodNotImplementedError
        
    def xml_process_element(self, element):
        """ Process the XML element. Processing involves several stages:
        
        1. Call xml_preprocess_tag(element) for tag actions when entering 
        2. Call xml_process_content(element.text) to process the content
        3. Call xml_process_element() for every nested element
        4. Call xml_process_tail(element.tail) to process the tail
        5. Call xml_postprocess_tag(element) for tag actions when leaving

        """
        
        self.xml_preprocess_tag(element)
        if element.text:
            self.xml_process_content(element)
        for child in element:
            self.xml_process_element(child)
        if element.tail:
            self.xml_process_tail(element)
        self.xml_postprocess_tag(element)
    
    def xml_preprocess_tag(self, element):
        """ Take any action that is triggered by the tag when entering the 
        element."""
        pass
    
    def xml_process_content(self, element):
        pass
    
    def xml_process_tail(self, element):
        pass
    
    def xml_postprocess_tag(self, element):
        """ Take any action that is triggered by the tag when leaving the 
        element."""
        pass

    def tag_next_token(self, tag, attributes):
        """ Add an entry to the tag table that marks the next corpus_id.
        The tag is marked as an opening tag and contains the 'tag' and a 
        string representation of the dictionary 'attributes'. 
        
        The closing counterpart can be added by calling tag_last_token()."""
        self.table_add(self.tag_table,
            {self.tag_label: "{}".format(tag),
                self.tag_corpus_id: self._corpus_id + 1,
                self.tag_type: "open",
                self.tag_attribute: ", ".join(
                    ["{}={}".format(x, attributes[x]) for x in attributes])})

    def tag_last_token(self, tag, attributes):
        """ Add an entry to the tag table that marks the last corpus_id.
        The tag is marked as a closing tag and contains the 'tag' and a 
        string representation of the dictionary 'attributes'. 
        
        The opening counterpart can be added by calling tag_next_token()."""
        self.table_add(self.tag_table,
            {self.tag_label: "{}".format(tag),
                self.tag_corpus_id: self._corpus_id,
                self.tag_type: "close",
                self.tag_attribute: ", ".join(
                    ["{}={}".format(x, attributes[x]) for x in attributes])})

    def add_empty_tag(self, tag, attributes):
        """ Add an entry to the tag table that precedes the next corpus_id.
        The tag is marked as an empty element and contains the 'tag' and a 
        string representation of the dictionary 'attributes'. """
        self.table_add(self.tag_table,
            {self.tag_label: "{}".format(tag),
                self.tag_corpus_id: self._corpus_id,
                self.tag_type: "empty",
                self.tag_attribute: ", ".join(
                    ["{}={}".format(x, attributes[x]) for x in attributes])})

    ### END XML

    def process_file(self, current_file):
        """ process_file(current_file) reads the content from current_file,
        parses the information relevant for the corpus from the file, and
        stores the information to the database. The default implementation
        simply calls process_text_file() on current_file, assuming that
        the file is a plain text file. """
        self.process_text_file(current_file)

    def load_files(self):
        """ Goes through the list of suitable files, and calls process_file()
        on each file name. File names are added to the file table.""" 
        files = self.get_file_list(self.arguments.path)
        if not files:
            self.logger.warning("No files found at %s" % self.arguments.path)
            return
        if not self._widget and not nltk_available:
            self.logger.warning("This script can use the NLTK library for automatic part-of-speech tagging. However, this library is not installed on this computer. Follow the steps from http://www.nltk.org/install.html to install this library.")
        
        if self._widget:
            self._widget.ui.progress_bar.setFormat("Reading text files... (%v of %m)")
            self._widget.ui.progress_bar.setMaximum(len(files))
            self._widget.ui.progress_bar.setValue(0)
        elif show_progress:
            progress = progressbar.ProgressBar(widgets=["Reading data files ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=len(files))
            progress.start()
            
        for x in self.table_description:
            self._id_count[x] = self.Con.get_max(x, self._primary_keys[x])
        
        for i, file_name in enumerate(files):
            if not self.Con.find(self.file_table, {self.file_path: file_name}):
                self.logger.info("Loading file %s" % (file_name))
                self.store_filename(file_name)
                self.process_file(file_name)
                
            if self._widget:
                self._widget.ui.progress_bar.setValue(i)
            elif show_progress:
                progress.update(i + 1)

            self.commit_data()

        if show_progress and not self._widget:
            progress.finish()
    
    def create_joined_table(self):
        pass
    
    def optimize(self):
        """ Optimizes the table columns so that they use a minimal amount
        of disk space."""
        totals = 0
        for current_table in self.table_description:
            totals += len(self.table_description[current_table]["CREATE"])
        totals -= 1
        
        if self._widget:
            self._widget.ui.progress_bar.setFormat("Optimizing table columns... (%v of %m)")
            self._widget.ui.progress_bar.setMaximum(totals)
            self._widget.ui.progress_bar.setValue(0)
        elif show_progress:
            progress = progressbar.ProgressBar(widgets=["Optimizing table columns ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=totals)
            progress.start()
            
        column_count = 0
        self.Con.start_transaction()
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
                        optimal_type = optimal_type.decode("utf-8")
                        self.logger.info("Optimising column {}.{} from {} to {}".format(
                            current_table, current_field, current_type, optimal_type))
                        try:
                            self.Con.modify_field_type(current_table, current_field, optimal_type)
                        except dbconnection.mysql.OperationalError as e:
                            if self.logger:
                                self.logger.error(e)
                column_count += 1
                if self._widget:
                    self._widget.ui.progress_bar.setValue(column_count)
                elif show_progress:
                    progress.update(column_count - 1)
        self.Con.commit()
        if show_progress and not self._widget:
            progress.finish()
        
    def create_indices(self, final):
        """ Creates the table indices as specified in the table description."""
        total_indices = 0
        for current_table in self.table_description:
            if "INDEX" in self.table_description[current_table]:
                total_indices += len(self.table_description[current_table]["INDEX"])
        
        if self._widget:
            self._widget.ui.progress_bar.setFormat("Creating indices... (%v of %m)")
            self._widget.ui.progress_bar.setMaximum(total_indices)
            self._widget.ui.progress_bar.setValue(0)
        elif show_progress:
            progress = progressbar.ProgressBar(widgets=["Indexing ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_indices)
            progress.start()
        index_count = 0
        self.Con.start_transaction()
        for i, current_table in enumerate(self.table_description):
            # only create indices for the corpus table in the final pass:
            if not final and current_table == self.corpus_table:
                continue

            description = self.table_description[current_table]
            if "INDEX" in description:
                for variables, length, index_type in description["INDEX"]:
                    current_index = "_".join(variables)
                    if not self.Con.has_index(current_table, current_index):
                        self.logger.info("Creating index {} on table '{}'".format(
                            current_index, current_table))
                        self.Con.create_index(current_table, current_index, variables, index_type, length)
                    index_count += 1
                    if self._widget:
                        self._widget.ui.progress_bar.setValue(i)
                    elif show_progress:
                        progress.update(index_count)
        self.Con.commit()
        if show_progress and not self._widget:
            progress.finish()
    
    def get_class_variables(self):
        return dir(BaseCorpusBuilder)

    def verify_corpus(self):
        """ Returns True if the database and all tables in the table
        description exist."""
        no_fail = True
        if not self.Con.has_database(self.arguments.db_name):
            no_fail = False
            self.logger.warning("Database {} not found.".format(self.arguments.db_name))
        for x in self.table_description:
            if not self.Con.has_table(x):
                self.logger.warning("Table {} not found.".format(x))
                no_fail = False
        return no_fail
    
    def ask_overwrite(self, warning_msg):
        if not self._widget:
            print("Enter Y to overwrite the existing version.")
            print("Enter N to keep the existing version.")
            try:
                response = raw_input("Overwrite? [Y or N] ")
            except NameError:
                response = input("Overwrite? [Y or N] ")
            return response.upper() == "Y"
                    
            return 
        else:
            warning_msg = "<p>{}</p><p>Do you really want to overwrite the existing version?</p>".format(warning_msg)
            return QtGui.QMessageBox.question(self._widget, "Library exists.", warning_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
                
    def write_python_module(self, corpus_path):
        """ Writes a Python module with the necessary specifications to the
        Coquery corpus module directory."""
        if self.arguments.dry_run:
            return
        
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
        
        path = os.path.join(corpus_path, "{}.py".format(self.name))
        # Handle existing versions of the corpus module
        if os.path.exists(path):
            # Read existing code as string:
            with codecs.open(path, "rt") as input_file:
                existing_code = input_file.read()
            # Keep if existing code is the same as the new code:
            if existing_code == output_code:
                self.logger.info("Identical corpus module %s already exists." % path)
                return
            # Ask if the existing code should be overwritten:
            else:
                msq_module_exists = "A different version of the corpus module already exists in %s." % path
                try:
                    self.logger.warning(msq_module_exists)
                except NameError:
                    pass
                if self.ask_overwrite(msq_module_exists):
                    self.logger.warning("Overwriting existing corpus module.")
                else:
                    return
        # write module code:
        with codecs.open(path, "wt") as output_file:
            output_file.write(output_code)
            self.logger.info("Library %s written." % path)
            
    def setup_db(self):
        """ Creates a connection to the server, and creates the database if
        necessary."""
        dbconnection.verbose = self.arguments.verbose
        dbconnection.logger = self.logger
        self.Con = dbconnection.DBConnection(
            db_host=self.arguments.db_host,
            db_user=self.arguments.db_user,
            db_pass=self.arguments.db_password,
            db_port=self.arguments.db_port,
            local_infile=1)
        if not self.Con.has_database(self.arguments.db_name):
            self.Con.create_database(self.arguments.db_name)
        self.Con.use_database(self.arguments.db_name)
        # if this is a dry run, database access will only be emulated:
        self.Con.dry_run = self.arguments.dry_run

        cursor = self.Con.Con.cursor()
        self.Con.execute(cursor, "SET autocommit=0")
        self.Con.execute(cursor, "SET unique_checks=0")
        self.Con.execute(cursor, "SET foreign_key_checks=0")

    def add_building_stage(self, stage):
        """ The parameter stage is a function that will be executed
        after the database tables have been created and the data data files
        have been processed, but before the tables are optimized and
        indexed. More than one function can be added."""
        self.additional_stages.append(stage)

    def get_description(self):
        return ""

    def get_speaker_data(self, *args):
        return []

    def initialize_build(self):
        """ Starts logging, starts the timer."""
        self.start_time = time.time()
        if self.arguments.dry_run:
            self.logger.info("--- Starting (dry run) ---")
        else:
            self.logger.info("--- Starting ---")
        self.logger.info("Building corpus %s" % self.name)
        self.logger.info("Command line arguments: %s" % " ".join(sys.argv[1:]))
        if not self._widget:
            print("\n%s\n" % textwrap.TextWrapper(width=79).fill(self.get_description()))

    def finalize_build(self):
        """ Logs duration of build. """
        self.Con.close()
        self.logger.info("--- Done (after %.3f seconds) ---" % (time.time() - self.start_time))

    def build(self):
        self.check_arguments()
        if not self._widget:
            self.setup_logger()
        self.setup_db()

        self.initialize_build()
        
        if self.arguments.c:
            self.create_tables()

        #if self.arguments.i:
            #self.create_indices(final=False)

        if self.arguments.l:
            self.load_files()

        if self.arguments.self_join:
            self.self_join()
            
        for stage in self.additional_stages:
            stage()
            
        if self.arguments.o:
            self.optimize()

        if self.arguments.i:
            self.create_indices(final=True)

        if self.verify_corpus():
            self.write_python_module(self.arguments.corpus_path)
        self.finalize_build()
                
if use_gui:

    class BuilderGui(QtGui.QDialog):
        def __init__(self, builder_class, parent=None):
            super(BuilderGui, self).__init__(parent)

            import __init__
            self.logger = logging.getLogger(__init__.NAME)        
            
            self.ui = corpusBuilderUi.Ui_CorpusBuilder()
            self.ui.setupUi(self)
            self.ui.button_input_path.clicked.connect(self.select_path)
            self.ui.radio_build_corpus.toggled.connect(self.changed_radio)
            self.ui.radio_only_module.toggled.connect(self.changed_radio)
            
            self.accepted = False
            self.builder_class = builder_class
            if not nltk_available:
                self.ui.use_pos_tagging.setChecked(False)
                self.ui.use_pos_tagging.setEnabled(False)
                self.ui.label_3.setEnabled(False)
            else:
                self.ui.use_pos_tagging.setChecked(True)

            self.exec_()

        def select_path(self):
            name = QtGui.QFileDialog.getExistingDirectory()
            if type(name) == tuple:
                name = name[0]
            if name:
                self.ui.input_path.setText(name)

        def keyPressEvent(self, e):
            if e.key() == QtCore.Qt.Key_Escape:
                self.reject()
                
        def changed_radio(self):
            if self.ui.radio_build_corpus.isChecked():
                self.ui.box_build_options.setEnabled(True)
            else:
                self.ui.box_build_options.setEnabled(False)
                
                
        def accept(self):
            self.accepted = True
            self.builder = self.builder_class(gui = self)
            self.builder.logger = self.logger
            self.builder.arguments = self.get_arguments_from_gui()
            self.builder.name = self.builder.arguments.name
            try:
                self.builder.build()
            except Exception as e:
                error_box.ErrorBox.show(sys.exc_info(), self)
            else:
                self.parent().ui.statusbar.showMessage("Finished building new corpus.")
            super(BuilderGui, self).accept()

        def get_arguments_from_gui(self):
            namespace = argparse.Namespace()
            namespace.dry_run = False
            namespace.verbose = False
            namespace.o = True
            namespace.i = True
            namespace.no_nltk = True
            namespace.l = True
            namespace.c = True
            namespace.self_join = False

            namespace.encoding = "utf-8"
            
            namespace.name = str(self.ui.corpus_name.text())
            namespace.path = str(self.ui.input_path.text())
            namespace.use_nltk = self.ui.use_pos_tagging.checkState()
            namespace.corpus_path = os.path.join(sys.path[0], "corpora/")
            namespace.db_name = str(self.ui.corpus_name.text())
            namespace.db_host = options.cfg.db_host
            namespace.db_user = options.cfg.db_user
            namespace.db_password = options.cfg.db_password
            namespace.db_port = options.cfg.db_port
            
            
            return namespace

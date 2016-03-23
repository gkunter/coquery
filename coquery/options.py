# -*- coding: utf-8 -*-
"""
options.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import absolute_import

# Python 3.x: import configparser 
# Python 2.x: import ConfigParser as configparser
try:
    from ConfigParser import *
except ImportError:
    try:
        from configparser import * 
    except ImportError as e:
        raise e

import sys
import os
import argparse
import logging
import platform
import warnings
import codecs
import ast
import collections
import inspect
import glob
import importlib
import imp

# make ast work in all Python versions:
if not hasattr(ast, "TryExcept"):
    ast.TryExcept = ast.Try
if not hasattr(ast, "TryFinally"):
    ast.TryFinally = ast.Try

import hashlib
from collections import defaultdict

from . import tokens
from .unicode import utf8
from .defines import *
from .errors import *

# Define a HelpFormatter class that works with Unicode corpus names both in 
# Python 2.7 and Python 3.x:
if sys.version_info < (3, 0):
    class CoqHelpFormatter(argparse.HelpFormatter):
        """
        A HelpFormatter class that is able to handle Unicode argument options.
        
        The code for _format_actions_usage() is a copy from 
        python2.7/argparse.py, with the addition of the utf8() conversion in
        one space.
        """
        def _format_actions_usage(self, actions, groups):
            # find group indices and identify actions in groups
            group_actions = set()
            inserts = {}
            for group in groups:
                try:
                    start = actions.index(group._group_actions[0])
                except ValueError:
                    continue
                else:
                    end = start + len(group._group_actions)
                    if actions[start:end] == group._group_actions:
                        for action in group._group_actions:
                            group_actions.add(action)
                        if not group.required:
                            if start in inserts:
                                inserts[start] += ' ['
                            else:
                                inserts[start] = '['
                            inserts[end] = ']'
                        else:
                            if start in inserts:
                                inserts[start] += ' ('
                            else:
                                inserts[start] = '('
                            inserts[end] = ')'
                        for i in range(start + 1, end):
                            inserts[i] = '|'

            # collect all actions format strings
            parts = []
            for i, action in enumerate(actions):

                # suppressed arguments are marked with None
                # remove | separators for suppressed arguments
                if action.help is argparse.SUPPRESS:
                    parts.append(None)
                    if inserts.get(i) == '|':
                        inserts.pop(i)
                    elif inserts.get(i + 1) == '|':
                        inserts.pop(i + 1)

                # produce all arg strings
                elif not action.option_strings:
                    part = self._format_args(action, action.dest)

                    # if it's in a group, strip the outer []
                    if action in group_actions:
                        if part[0] == '[' and part[-1] == ']':
                            part = part[1:-1]

                    # add the action string to the list
                    parts.append(part)

                # produce the first way to invoke the option in brackets
                else:
                    option_string = action.option_strings[0]

                    # if the Optional doesn't take a value, format is:
                    #    -s or --long
                    if action.nargs == 0:
                        part = '%s' % option_string

                    # if the Optional takes a value, format is:
                    #    -s ARGS or --long ARGS
                    else:
                        default = action.dest.upper()
                        args_string = self._format_args(action, default)
                        part = '%s %s' % (option_string, args_string)

                    # make it look optional if it's not required or in a group
                    if not action.required and action not in group_actions:
                        part = '[%s]' % part

                    # add the action string to the list
                    parts.append(part)

            # insert things at the necessary indices
            for i in sorted(inserts, reverse=True):
                parts[i:i] = [inserts[i]]

            # join all the action items with spaces
            text = u' '.join([item.decode("utf-8") for item in parts if item is not None])

            # clean up separators for mutually exclusive groups
            open = r'[\[(]'
            close = r'[\])]'
            text = argparse._re.sub(r'(%s) ' % open, r'\1', text)
            text = argparse._re.sub(r' (%s)' % close, r'\1', text)
            text = argparse._re.sub(r'%s *%s' % (open, close), r'', text)
            text = argparse._re.sub(r'\(([^|]*)\)', r'\1', text)
            text = text.strip()

            # return the text
            return text

        def _join_parts(self, part_strings):
            part_strings = [utf8(x) for x in part_strings if utf8(x) and x is not argparse.SUPPRESS]
            return "".join(part_strings)
else:
    class CoqHelpFormatter(argparse.HelpFormatter):
        pass

class Options(object):
    def __init__(self):
        self.args = argparse.Namespace()
        
        self.args.coquery_home = get_home_dir(create=True)

        self.prog_name = NAME
        self.config_name = "%s.cfg" % NAME.lower()
        self.version = VERSION
        self.parser = argparse.ArgumentParser(prog=self.prog_name, add_help=False, formatter_class=CoqHelpFormatter)

        self.args.config_path = os.path.join(self.args.coquery_home, self.config_name)
        self.args.disabled_columns = set([])
        self.args.version = self.version
        self.args.query_label = ""
        self.args.input_path = ""
        self.args.query_string = ""
        self.args.ask_on_quit = True
        self.args.save_query_string = True
        self.args.save_query_file = True
        self.args.reaggregate_data = True
        self.args.server_side = True
        self.args.server_configuration = dict()
        self.args.current_server = None
        self.args.current_resources = None
        self.args.main_window = None
        self.args.first_run = False

        self.args.filter_list = []
        self.args.stopword_list = []
        self.args.use_stopwords = False
        self.args.use_corpus_filters = False
        
        if getattr(sys, "frozen", None):
            self.args.base_path = os.path.dirname(sys.executable)
        elif __file__:
            self.args.base_path = os.path.dirname(__file__)

        self.args.query_file_path = os.path.expanduser("~")
        self.args.results_file_path = os.path.expanduser("~")
        self.args.uniques_file_path = os.path.expanduser("~")
        self.args.textgrids_file_path = os.path.expanduser("~")
        self.args.text_source_path = os.path.join(self.args.base_path, "texts", "alice")
        self.args.corpus_source_path = os.path.expanduser("~")
        self.args.stopwords_file_path = os.path.expanduser("~")
        self.args.filter_file_path = os.path.expanduser("~")

        self.args.connections_path = os.path.join(self.args.coquery_home, "connections")
        self.args.installer_path = os.path.join(self.args.base_path, "installer")
        
        self.args.custom_installer_path = os.path.join(self.args.coquery_home, "installer")
        self.args._use_mysql = True
        
        try:
            self.args.parameter_string = " ".join([x.decode("utf8") for x in sys.argv [1:]])
        except AttributeError:
            self.args.parameter_string = " ".join([x for x in sys.argv [1:]])

        self.args.selected_features= []
        self.args.external_links = {}
        #self.args.external_links = defaultdict(list)
        self.args.selected_functions = []
        
        self.args.context_left = 0
        self.args.context_right = 0
        # these attributes are used only in the GUI:
        self.args.column_width = {}
        self.args.column_color = {}
        self.args.column_names = {}
        self.args.column_visibility = collections.defaultdict(dict)
        self.args.row_visibility = collections.defaultdict(dict)
        self.args.row_color = {}
        # Set defaults for CSV files:
        self.args.query_column_number = 1
        self.args.skip_lines = 0
        self.args.input_separator = ','
        self.args.output_separator = ","
        self.args.quote_char = '"'
        self.args.xkcd = None
        
        self.args.output_to_lower = True

    @property
    def cfg(self):
        return self.args
        
    def setup_parser(self):
        self.parser.add_argument("MODE", help="determine the query mode (default: TOKEN)", choices=(QUERY_MODE_TOKENS, QUERY_MODE_FREQUENCIES, QUERY_MODE_DISTINCT, QUERY_MODE_STATISTICS, QUERY_MODE_CONTINGENCY, QUERY_MODE_COLLOCATIONS), type=str, nargs="?")
        if sys.version_info < (3, 0):
            l = [x.encode("utf-8") for x in self.corpus_argument_dict["choices"]]
            self.corpus_argument_dict["choices"] = l
        self.parser.add_argument("corpus", nargs="?", **self.corpus_argument_dict)
        
        # If Qt is available, the GUI is used by default. The command line 
        # interface can be selected by using the --con option:
        if _use_qt:
            self.parser.add_argument("--con", help="Run Coquery as a console program", dest="gui", action="store_false")
        
        # General options:
        self.parser.add_argument("-o", "--outputfile", help="write results to OUTPUTFILE (default: write to console)", type=str, dest="output_path")
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-i", "--inputfile", help="read query strings from INPUTFILE", type=str, dest="input_path")
        group.add_argument("-q", "--query", help="use QUERY for search, ignoring any INPUTFILE", dest="query_list")
        self.parser.add_argument("-F", "--filter", help="use FILTER to query only a selection of texts", type=str, default="", dest="source_filter")

        # File options:
        group = self.parser.add_argument_group("File options")
        group.add_argument("-a", "--append", help="append output to OUTPUTFILE, if specified (default: overwrite)", action="store_true")
        group.add_argument("-k", "--skip", help="skip SKIP lines in INPUTFILE (default: 0)", type=int, dest="skip_lines")
        group.add_argument("-H", "--header", help="use first row of INPUTFILE as headers", action="store_true", dest="file_has_headers")
        group.add_argument("-n", "--number", help="use column NUMBER in INPUTFILE for queries", type=int, dest="query_column_number")
        group.add_argument("--is", "--input_separator", help="use CHARACTER as separator in input CSV file",  metavar="CHARACTER", dest="input_separator")
        group.add_argument("--os", "--output_separator", help="use CHARACTER as separator in output CSV file", metavar="CHARACTER", dest="output_separator")
        group.add_argument("--quote_character", help="use CHARACTER as quoting character", metavar="CHARACTER", dest="quote_char")
        group.add_argument("--input_encoding", help="use INPUT-ENCODING as the encoding scheme for the input file (default: utf-8)", type=str, default="utf-8", dest="input_encoding")
        group.add_argument("--output_encoding", help="use OUTPUT-ENCODING as the encoding scheme for the output file (default: utf-8)", type=str, default="utf-8", dest="output_encoding")

        # Debug options:
        group = self.parser.add_argument_group("Debug options")
        #group.add_argument("-d", "--dry-run", help="dry run (do not query, just log the query strings)", action="store_true")
        group.add_argument("-v", "--verbose", help="produce a verbose output", action="store_true", dest="verbose")
        #group.add_argument("-V", "--super-verbose", help="be super-verbose (i.e. log function calls)", action="store_true")
        group.add_argument("-E", "--explain", help="explain mySQL queries in log file", action="store_true", dest="explain_queries")
        group.add_argument("--benchmark", help="benchmarking of Coquery", action="store_true")
        group.add_argument("--profile", help="deterministic profiling of Coquery", action="store_true")
        group.add_argument("--memory-dump", help="list objects that consume much memory after queries", action="store_true", dest="memory_dump")
        group.add_argument("--experimental", help="use experimental features (may be buggy)", action="store_true")
        group.add_argument("--comment", help="a comment that is shown in the log file", type=str)

        # Query options:
        group = self.parser.add_argument_group("Query options")
        group.add_argument("-C", "--output_case", help="be case-sensitive in the output (default: ignore case)", action="store_true", dest="output_case_sensitive")
        group.add_argument("--query_case", help="be case-sensitive when querying (default: ignore case)", action="store_true", dest="query_case_sensitive")
        group.add_argument("--one_by_one", help="retrieve results from server one by one (somewhat slower, but uses less memory)", action="store_true", dest="server_side")
        #group.add_argument("-L", "--lemmatize-tokens", help="treat all tokens in query as lemma searches (default: be COCA-compatible and only do lemma searches if explicitly specified in query string)", action="store_true")
        group.add_argument("-r", "--regexp", help="use regular expressions", action="store_true", dest="regexp")

        # Output options:
        group = self.parser.add_argument_group("Output options")
        group.add_argument("--suppress_header", help="exclude column header from the output (default: include)", action="store_false", dest="show_header")
        
        group.add_argument("--context_mode", help="specify the way the context is included in the output", choices=[CONTEXT_KWIC, CONTEXT_STRING, CONTEXT_COLUMNS], type=str)
        group.add_argument("-c", "--context_span", help="include context with N words to the left and the right of the keyword, or with N words to the left and M words to the right if the notation '-c N, M' is used", default=0, type=int, dest="context_span")
        group.add_argument("--sentence", help="include the sentence of the token as a context (not supported by all corpora, currently not implemented)", dest="context_sentence", action="store_true")

        group.add_argument("--digits", help="set the number of digits after the period", dest="digits", default=3, type=int)

        group.add_argument("--number_of_tokens", help="output up to NUMBER different tokens (default: all tokens)", default=0, type=int, dest="number_of_tokens", metavar="NUMBER")
        #group.add_argument("-u", "--unique-id", help="include the token id for the first token matching the output", action="store_true", dest="show_id")
        group.add_argument("-Q", "--show_query", help="include query string in the output", action="store_true", dest="show_query")
        group.add_argument("-P", "--show_parameters", help="include the parameter string in the output", action="store_true", dest="show_parameters")
        group.add_argument("-f", "--show_filter", help="include the filter strings in the output", action="store_true", dest="show_filter")
        group.add_argument("--freq-label", help="use this label in the heading line of the output (default: Freq)", default="Freq", type=str, dest="freq_label")
        group.add_argument("--no_align", help="Control if quantified token columns are aligned. If not set (the default), the columns in the result table are aligned so that row cells belonging to the same query token are placed in the same column. If set, this alignment is disabled. In that case, row cells are padded to the right.", action="store_false", dest="align_quantified")

    def get_options(self):
        """ 
        Read the values from the configuration file, and merge them with 
        the command-line options. Values set in the configuration file are
        overwritten by command-line arguments. 
        
        If a GUI is used, no corpus needs to be specified, and all values 
        from the configuration file are used. If the command-line interface 
        is used, both a corpus and a query mode have to be specified, and 
        only the database settings from the configuration file are used.
        """
        self.corpus_argument_dict = {
            "help": "specify the corpus to use", 
            "choices": [utf8(x) for x in get_available_resources(DEFAULT_CONFIGURATION).keys()], 
            "type": type(str(""))}

        self.setup_parser()
        
        # Do a first argument parse to get the corpus to be used, and 
        # whether a GUI is requested. This parse doesn't raise an argument 
        # error.
        args, unknown = self.parser.parse_known_args()
        if _use_qt:
            self.args.gui = args.gui
        else:
            self.args.gui = False
            
        self.read_configuration()
        self.setup_default_connection()
        try:
            if args.corpus:
                self.args.corpus = args.corpus
            elif not self.args.corpus:
                self.args.corpus = ""
        except AttributeError:
            self.args.corpus = ""
        self.args.corpus = utf8(self.args.corpus)
        # if no corpus is selected and no GUI is requested, display the help
        # and exit.
        if not self.args.corpus and not (self.args.gui):
            self.parser.print_help()
            sys.exit(1)
        
        D = {}
        
        if self.args.corpus:
            try:
                # build a dictionary D for the selected corpus that contains as 
                # values the features provided by each of the tables defined in
                # the resource. The features are included as tuples, with first,
                # the display name and second, the resource feature name.
                resource, _, _ = get_resource(self.args.corpus, self.args.current_server)
                corpus_features = resource.get_corpus_features()
                lexicon_features = resource.get_lexicon_features()
                for rc_feature, column in corpus_features + lexicon_features:
                    if "_denorm_" not in rc_feature:
                        table = "{}_table".format(rc_feature.split("_")[0])
                        if table not in D:
                            D[table] = set([])
                        D[table].add((column, rc_feature))
            
                if self.args.corpus == "COCA":
                    group = self.parser.add_argument_group("COCA compatibility", "These options apply only to the COCA corpus module, and are unsupported by any other corpus.")
                    # COCA compatibility options
                    group.add_argument("--exact-pos-tags", help="part-of-speech tags must match exactly the label used in the query string (default: be COCA-compatible and match any part-of-speech tag that starts with the given label)", action="store_true", dest="exact_pos_tags")
                    group.add_argument("-@", "--use-pos-diacritics", help="use undocumented characters '@' and '%%' in queries using part-of-speech tags (default: be COCA-compatible and ignore these characters in part-of-speech tags)", action="store_true", dest="ignore_pos_chars")
            except KeyError:
                pass

        if D:
            # add choice arguments for the available table columns:
            for rc_table in D.keys():
                table = type(resource).__getattribute__(resource, str(rc_table))
                if len(D[rc_table]) > 1:
                    D[rc_table].add(("ALL", None))
                    group_help = "These options specify which data columns from the table '{0}' will be included in the output. You can either repeat the option for every column that you wish to add, or you can use --{0} ALL if you wish to include all columns from the table in the output.".format(table)
                    group_name = "Output options for table '{0}'".format(table)
                else:
                    group_name = "Output option for table '{0}'".format(table)
                    group_help = "This option will include the data column '{1}' from the table '{0}' in the output.".format(table, list(D[rc_table])[0][0])
                group = self.parser.add_argument_group(group_name, group_help)
                group.add_argument("--{}".format(table), choices=sorted([x for x, _ in D[rc_table]]), dest=rc_table, action="append")

            # add output column shorthand options
            group=self.parser.add_argument_group("Output column shorthands", "These options are shorthand forms that select some commonly used output columns. The equivalent shows the corresponding longer output option.")
            if "word_label" in dir(resource) or "corpus_word" in dir(resource):
                if "word_label" in dir(resource):
                    s = "--{} {}".format(resource.word_table, resource.word_label)
                else:
                    s = "--{} {}".format(resource.corpus_table, resource.corpus_word)
                group.add_argument("-O", help="show orthographic forms of each token, equivalent to: {}".format(s), action="store_true", dest="show_orth")
            if "pos_label" in dir(resource) or "word_pos" in dir(resource):
                if "pos_label" in dir(resource):
                    s = "--{} {}".format(resource.pos_table, resource.pos_label)
                else:
                    s = "--{} {}".format(resource.word_table, resource.word_pos)
                group.add_argument("-p", help="show the part-of-speech tag of each token, equivalent to: {}".format(s), action="store_true", dest="show_pos")
            if "lemma_label" in dir(resource) or "word_lemma" in dir(resource):
                if "lemma_label" in dir(resource):
                    s = "--{} {}".format(resource.lemma_table, resource.lemma_label)
                else:
                    s = "--{} {}".format(resource.word_table, resource.word_lemma)
                group.add_argument("-l", help="show the lemma of each token, equivalent to: {}".format(s), action="store_true", dest="show_lemma")
            if "transcript_label" in dir(resource) or "word_transcript" in dir(resource):
                if "transcript_label" in dir(resource):
                    s = "--{} {}".format(resource.transcript_table, resource.transcript_label)
                else:
                    s = "--{} {}".format(resource.word_table, resource.word_transcript)
                group.add_argument("--phon", help="show the phonological transcription of each token, equivalent to: {}".format(s), action="store_true", dest="show_phon")
            if "file_label" in dir(resource) or "corpus_file" in dir(resource):
                if "file_label" in dir(resource):
                    s = "--{} {}".format(resource.file_table, resource.file_label)
                else:
                    s = "--{} {}".format(resource.corpus_table, resource.corpus_file)
                group.add_argument("--filename", help="show the name of the file containing each token, equivalent to: {}".format(s), action="store_true", dest="show_filename")
            if "time_label" in dir(resource) or "corpus_time" in dir(resource):
                if "time_label" in dir(resource):
                    s = "--{} {}".format(resource.time_table, resource.time_label)
                else:
                    s = "--{} {}".format(resource.corpus_table, resource.corpus_time)
                group.add_argument("--time", help="show the time code for each token, equivalent to: {}".format(s), action="store_true", dest="show_time")

        #group.add_argument("-u", "--unique-id", help="include the token id for the first token matching the output", action="store_true", dest="show_id")

        self.parser.add_argument("-h", "--help", help="show this help message and exit", action="store_true")
        
        # reparse the arguments, this time with options that allow feature
        # selection based on the table structure of the corpus
        args, unknown = self.parser.parse_known_args()
        if unknown:
            self.parser.print_help()
            raise UnknownArgumentError(unknown)
        if args.help:
            self.parser.print_help()
            sys.exit(0)

        if args.input_path:
            self.args.input_path_provided = True
        else:
            self.args.input_path_provided = False
        
        # merge the newly-parsed command-line arguments with those read from
        # the configation file.
        for command_argument in vars(args).keys():
            if command_argument in vars(self.args) and not vars(args)[command_argument]:
                # do not overwrite the command argument if it was set in the 
                # config file stored self.args, but not set at the command 
                # line
                continue 
            else:
                # overwrite the setting from the configuration file with the
                # command-line setting:
                vars(self.args)[command_argument] = vars(args)[command_argument]
        
        # evaluate the shorthand options. If set, add the corresponding 
        # resource feature to the list of selected features
        try:
            if self.args.show_orth:
                if "word_table" in dir(resource):
                    self.args.selected_features.append("word_label")
                else:
                    self.args.selected_feature.append("corpus_word")
        except AttributeError:
            pass
        try:
            if self.args.show_pos:
                if "pos_table" in dir(resource):
                    self.args.selected_features.append("pos_label")
                else:
                    self.args.selected_features.append("word_pos")
        except AttributeError:
            pass
        try:
            if self.args.show_lemma:
                if "lemma_table" in dir(resource):
                    self.args.selected_features.append("lemma_label")
                else:
                    self.args.selected_features.append("word_lemma")
        except AttributeError:
            pass
        try:
            if self.args.show_phon:
                if "transcript_table" in dir(resource):
                    self.args.selected_features.append("transcript_label")
                else:
                    self.args.selected_features.append("word_transcript")
        except AttributeError:
            pass
        try:
            if self.args.show_filename:
                if "file_table" in dir(resource):
                    self.args.selected_features.append("file_label")
                else:
                    self.args.selected_features.append("corpus_file")
        except AttributeError:
            pass
        try:
            if self.args.show_time:
                if "time_table" in dir(resource):
                    self.args.selected_features.append("time_label")
                else:
                    self.args.selected_features.append("corpus_time")
        except AttributeError:
            pass
        
        try:
            if self.args.show_query:
                self.args.selected_features.append("coquery_query_string")
        except AttributeError:
            pass
        
        if self.args.source_filter:
            Genres, Years, Negated = tokens.COCATextToken(self.args.source_filter, None).get_parse()
            
            date_label = ""
            genre_label = ""
            
            if Genres:
                if "corpus_genre" in dir(resource):
                    genre_label = resource.corpus_genre
                elif "source_genre" in dir(resource):
                    genre_label = resource.source_genre
                elif "source_info_genre" in dir(resource):
                    genre_label = resource.source_info_genre
                elif "genre_label" in dir(resource):
                    genre_label = resource.genre_label
            if Years:
                if "corpus_year" in dir(resource):
                    date_label = resource.corpus_year
                elif "corpus_date" in dir(resource):
                    date_label = resource.corpus_date
                elif "source_year" in dir(resource):
                    date_label = resource.source_year
                elif "source_date" in dir(resource):
                    date_label = resource.source_date
            
            if date_label:
                for year in Years:
                    self.args.filter_list.append("{} = {}".format(date_label,  year))
            if genre_label:
                for genre in Genres:
                    self.args.filter_list.append("{} = {}".format(genre_label,  genre))
        # Go through the table dictionary D, and add the resource features 
        # to the list of selected features if the corresponding choice 
        # parameter was set:
        for rc_table in D:
            argument_list = vars(self.args)[rc_table]
            if argument_list:
                # if ALL was selected, all resource features for the current
                # table are added to the list of selected features:                
                if "ALL" in argument_list:
                    self.args.selected_features += [x for _, x in D[rc_table] if x]
                else:
                    # otherwise, go through each argument, and find the 
                    # resource feature for which the display name matches 
                    # the argument:
                    for arg in argument_list:
                        for column, rc_feature in D[rc_table]:
                            if column == arg:
                                self.args.selected_features.append(rc_feature)
        
        self.args.selected_features = set(self.args.selected_features)

        # the following lines are deprecated and should be removed once
        # feature selection is fully implemented:
        self.args.show_source = "source" in vars(self.args)
        self.args.show_filename = "file" in vars(self.args)
        self.args.show_speaker = "speaker" in vars(self.args)
        self.args.show_time = "corpus_time" in self.args.selected_features
        self.args.show_id = False
        self.args.show_phon = False

        self.args.context_sentence = False

        try:
            self.args.input_separator = self.args.input_separator.decode('string_escape')
        except AttributeError:
            self.args.input_separator = codecs.getdecoder("unicode_escape") (self.args.input_separator) [0]
        try:
            self.args.output_separator = self.args.output_separator.decode('string_escape')
        except AttributeError:
            self.args.output_separator = codecs.getdecoder("unicode_escape") (self.args.output_separator) [0]
        
        if self.args.context_span:
            self.args.context_left = self.args.context_span
            self.args.context_right = self.args.context_span
            
        # make sure that a command query consisting of one string is still
        # stored as a list:
        if self.args.query_list:
            if type(self.args.query_list) != list:
                self.args.query_list = [self.args.query_list]
            try:
                self.args.query_list = [x.decode("utf8") for x in self.args.query_list]
            except AttributeError:
                pass
        logger.info("Command line parameters: " + self.args.parameter_string)
        
    def setup_default_connection(self):
        """
        Create the default SQLite connection.
        """
        if not self.args.current_server or "Default" not in self.args.server_configuration:
            d = {"name": "Default", "type": SQL_SQLITE, "path": ""}
            self.args.server_configuration[d["name"]] = d
            self.args.current_server = d["name"]
            self.args.current_resources = get_available_resources(self.args.current_server)

    def read_configuration(self):
        if os.path.exists(self.cfg.config_path):
            logger.info("Using configuration file %s" % self.cfg.config_path)
            config_file = ConfigParser()
            config_file.read(self.cfg.config_path)
            
            if "sql" in config_file.sections():
                server_configuration = defaultdict(dict)

                for name, value in config_file.items("sql"):
                    if name.startswith("config_"):
                        try:
                            _, number, variable = name.split("_")
                        except ValueError:
                            continue
                        else:
                            if variable == "port":
                                try:
                                    server_configuration[number][variable] = int(value)
                                except ValueError:
                                    continue
                            elif variable in ["name", "host", "type", "user", "password", "path"]:
                                server_configuration[number][variable] = value
                for i in server_configuration:
                    d = server_configuration[i]
                    if "type" not in d:
                        d["type"] = SQL_MYSQL
                    if d["type"] == SQL_MYSQL:
                        required_vars = ["name", "host", "port", "user", "password"]
                    elif d["type"] == SQL_SQLITE:
                        if "path" not in d:
                            d["path"] = ""
                        required_vars = ["name", "path"]
                    try:
                        if all(var in d for var in required_vars):
                            self.args.server_configuration[d["name"]] = d
                    except KeyError:
                        pass

                try:
                    self.args.current_server = config_file.get("sql", "active_configuration")
                    if self.args.current_server in self.args.server_configuration:
                        self.args.current_resources = get_available_resources(self.args.current_server)
                    else:
                        raise ValueError
                except (NoOptionError, ValueError):
                    self.args.current_server = "Default"
                    self.args.current_resources = get_available_resources(self.args.current_server)
                
            # only use the other settings from the configuration file if a 
            # GUI is used:
            if self.args.gui:
                for section in config_file.sections():
                    if section == "main":
                        try:
                            default_corpus = config_file.get("main", "default_corpus")
                        except (NoOptionError, ValueError):
                            default_corpus = self.corpora_dict.keys()[0]
                        self.args.corpus = default_corpus
                        try:
                            mode = config_file.get("main", "query_mode")
                            self.args.MODE = mode
                        except (NoOptionError, ValueError):
                            self.args.MODE = QUERY_MODE_DISTINCT
                        try:
                            last_query = config_file.get("main", "query_string")
                            self.args.query_list = decode_query_string(last_query)
                        except (NoOptionError, ValueError):
                            pass
                        try:
                            self.args.server_side = config_file.get("main", "one_by_one")
                        except NoOptionError:
                            self.args.server_side = True
                        try:
                            self.args.context_mode = config_file.get("main", "context_mode")
                        except NoOptionError:
                            self.args.context_mode = CONTEXT_NONE
                        try:
                            self.args.output_case_sensitive = config_file.getboolean("main", "output_case_sensitive")
                        except NoOptionError:
                            self.args.output_case_sensitive = False
                        try:
                            self.args.output_to_lower = config_file.getboolean("main", "output_to_lower")
                        except NoOptionError:
                            self.args.output_to_lower = True
                        try:
                            self.args.query_case_sensitive = config_file.getboolean("main", "query_case_sensitive")
                        except NoOptionError:
                            self.args.query_case_sensitive = True
                        try:
                            self.args.custom_installer_path = config_file.get("main", "custom_installer_path")
                        except NoOptionError:
                            pass
                        
                        try:
                            self.args.input_path = config_file.get("main", "csv_file")
                        except (NoOptionError, ValueError):
                            pass
                        else:
                            # Read CSV options, but only if a CSV file name
                            # is also in the configuration. If the file name
                            # was provided as an argument, we shouldn't use
                            # the saved values.
                            try:
                                self.args.input_separator = config_file.get("main", "csv_separator")
                            except (NoOptionError, ValueError):
                                pass
                            try:
                                self.args.query_column_number = config_file.getint("main", "csv_column")
                            except (NoOptionError, ValueError):
                                pass
                            try:
                                self.args.file_has_headers = config_file.getboolean("main", "csv_has_header")
                            except (NoOptionError, ValueError):
                                pass
                            try:
                                self.args.skip_lines = config_file.getint("main", "csv_line_skip")
                            except (NoOptionError, ValueError):
                                pass
                            try:
                                self.args.quote_char = config_file.get("main", "csv_quote_char")
                            except (NoOptionError, ValueError):
                                pass
                        try:
                            self.args.xkcd = config_file.getboolean("main", "xkcd")
                        except (NoOptionError, ValueError):
                            pass

                    elif section == "output":
                        for variable, value in config_file.items("output"):
                            if value:
                                self.args.selected_features.append(variable)
                    elif section == "filter":
                        for _, filt_text in config_file.items("filter"):
                            self.args.filter_list.append(filt_text.strip('"'))

                    elif section == "context":
                        try:
                            self.args.context_left = config_file.getint("context", "words_left")
                        except (NoOptionError, ValueError):
                            pass
                        try:
                            self.args.context_right = config_file.getint("context", "words_right")
                        except (NoOptionError, ValueError):
                            pass
                        try:
                            self.args.context_mode = config_file.get("context", "mode")
                        except (NoOptionError, ValueError):
                            pass

                    elif section == "gui":
                        try:
                            stopwords = config_file.get("gui", "stopword_list")
                            self.args.stopword_list = decode_query_string(stopwords).split("\n")
                        except (NoOptionError, ValueError):
                            self.args.stopword_list = []                            
                        try:
                            self.args.ask_on_quit = bool(config_file.getboolean("gui", "ask_on_quit"))
                        except (NoOptionError, ValueError):
                            self.args.ask_on_quit = True
                        try:
                            self.args.save_query_string = config_file.getboolean("gui", "save_query_string")
                        except (NoOptionError, ValueError):
                            self.args.save_query_string = True
                        try:
                            self.args.save_query_file = config_file.getboolean("gui", "save_query_file")
                        except (NoOptionError, ValueError):
                            self.args.save_query_file = True
                        try:
                            self.args.query_file_path = config_file.get("gui", "query_file_path")
                        except (NoOptionError, ValueError):
                            self.args.query_file_path = os.path.expanduser("~")
                        try:
                            self.args.textgrids_file_path = config_file.get("gui", "textgrids_file_path")
                        except (NoOptionError, ValueError):
                            self.args.textgrids_file_path = os.path.expanduser("~")
                        try:
                            self.args.results_file_path = config_file.get("gui", "results_file_path")
                        except (NoOptionError, ValueError):
                            self.args.results_file_path = os.path.expanduser("~")
                        try:
                            self.args.stopwords_file_path = config_file.get("gui", "stopwords_file_path")
                        except (NoOptionError, ValueError):
                            self.args.stopwords_file_path = os.path.expanduser("~")
                        try:
                            self.args.filter_file_path = config_file.get("gui", "filter_file_path")
                        except (NoOptionError, ValueError):
                            self.args.filter_file_path = os.path.expanduser("~")
                        try:
                            self.args.uniques_file_path = config_file.get("gui", "uniques_file_path")
                        except (NoOptionError, ValueError):
                            self.args.uniques_file_path = os.path.expanduser("~")
                        try:
                            self.args.corpus_source_path = config_file.get("gui", "corpus_source_path")
                        except (NoOptionError, ValueError):
                            self.args.corpus_source_path = os.path.expanduser("~")
                        try:
                            self.args.text_source_path = config_file.get("gui", "text_source_path")
                        except (NoOptionError, ValueError):
                            self.args.text_source_path = os.path.expanduser("~")
                        try:
                            self.args.use_corpus_filters = config_file.getboolean("gui", "use_corpus_filters")
                        except (NoOptionError, ValueError):
                            self.args.use_corpus_filters = False
                        try:
                            self.args.use_stopwords = config_file.getboolean("gui", "use_stopwords")
                        except (NoOptionError, ValueError):
                            self.args.use_stopwords = False                        
                        try:
                            self.args.reaggregate_data = config_file.getboolean("gui", "reaggregate_data")
                        except NoOptionError:
                            self.args.reaggregate_data = True
                        try:
                            self.args.width = config_file.getint("gui", "width")
                        except (NoOptionError, ValueError):
                            self.args.width = None
                        try:
                            self.args.height = config_file.getint("gui", "height")
                        except (NoOptionError, ValueError):
                            self.args.height = None

                        context_dict = {}
                        # get column defaults:
                        for name, value in config_file.items("gui"):
                            if name.startswith("column_"):
                                col = name.partition("_")[2]
                                column, _, attribute = col.rpartition("_")
                                if not column.startswith("coquery_invisible"):
                                    try:
                                        if attribute == "color":
                                            if "column_color" not in vars(self.args):
                                                self.args.column_color = {}
                                            self.args.column_color[column] = value
                                        elif attribute == "width":
                                            if "column_width" not in vars(self.args):
                                                self.args.column_width = {}
                                            if int(value):
                                                self.args.column_width[column] = int(value)
                                    except ValueError:
                                        pass
        else:
            self.args.first_run = True

cfg = None

class UnicodeConfigParser(RawConfigParser):
    """
    Define a subclass of RawConfigParser that works with Unicode (hopefully).
    """
    def write(self, fp):
        """Fixed for Unicode output"""
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, unicode(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s = %s\n" %
                             (key, unicode(value).replace('\n','\n\t')))
            fp.write("\n")

    # This function is needed to override default lower-case conversion
    # of the parameter's names. They will be saved 'as is'.
    def optionxform(self, strOut):
        return strOut

def save_configuration():
    config = UnicodeConfigParser()
    if os.path.exists(cfg.config_path):
        with codecs.open(cfg.config_path, "r", "utf-8") as input_file:
            try:
                config.read(input_file)
            except (IOError, TypeError):
                warnings.warn("Configuration file {} could not be read.".format(cfg.config_path))
    if not "main" in config.sections():
        config.add_section("main")
    config.set("main", "default_corpus", cfg.corpus)
    config.set("main", "query_mode", cfg.MODE)
    if cfg.query_list and cfg.save_query_string:
        config.set("main", "query_string", encode_query_string("\n".join(cfg.query_list)))
    if cfg.input_path and cfg.save_query_file:
        config.set("main", "csv_file", cfg.input_path)
        config.set("main", "csv_separator", cfg.input_separator)
        config.set("main", "csv_column", cfg.query_column_number)
        config.set("main", "csv_has_header", cfg.file_has_headers)
        config.set("main", "csv_line_skip", cfg.skip_lines)
        config.set("main", "csv_quote_char", cfg.quote_char)
    config.set("main", "one_by_one", cfg.server_side)
    config.set("main", "context_mode", cfg.context_mode)
    config.set("main", "output_case_sensitive", cfg.output_case_sensitive)
    config.set("main", "query_case_sensitive", cfg.query_case_sensitive)
    try:
        config.set("main", "output_to_lower", cfg.output_to_lower)
    except AttributeError:
        pass
    if cfg.xkcd != None:
        config.set("main", "xkcd", cfg.xkcd)
    
    if cfg.custom_installer_path:
        config.set("main", "custom_installer_path", cfg.custom_installer_path)
        
    if not "sql" in config.sections():
        config.add_section("sql")
    if cfg.current_server:
        config.set("sql", "active_configuration", cfg.current_server)

    for i, server in enumerate(cfg.server_configuration):
        d = cfg.server_configuration[server]
        if d["type"] == SQL_MYSQL:
            required_vars = ["name", "host", "port", "user", "password", "type"]
        elif d["type"] == SQL_SQLITE:
            required_vars = ["name", "type", "path"]
        else:
            required_vars = []
        for x in required_vars:
            config.set("sql", "config_{}_{}".format(i, x), d[x])
    
    if cfg.selected_features:
        if not "output" in config.sections():
            config.add_section("output")
        for feature in cfg.selected_features:
            config.set("output", feature, True)

    if cfg.filter_list:
        if not "filter" in config.sections():
            config.add_section("filter")
        for i, filt in enumerate(cfg.filter_list):
            config.set("filter", "filter{}".format(i+1), '"{}"'.format(filt))
        
    if not "context" in config.sections():
        config.add_section("context")
    config.set("context", "mode", cfg.context_mode)
    if cfg.context_left or cfg.context_right:
        config.set("context", "words_left", cfg.context_left)
        config.set("context", "words_right", cfg.context_right)

    if cfg.gui:
        if not "gui" in config.sections():
            config.add_section("gui")

        if cfg.stopword_list:
            config.set("gui", "stopword_list", 
                       encode_query_string("\n".join(cfg.stopword_list)))
        config.set("gui", "use_stopwords", cfg.use_stopwords)
        config.set("gui", "use_corpus_filters", cfg.use_corpus_filters)        

        for x in cfg.column_width:
            if not x.startswith("coquery_invisible") and cfg.column_width[x]:
                config.set("gui", 
                        "column_{}_width".format(x.replace(" ", "_").replace(":", "_")), 
                        cfg.column_width[x])
        for x in cfg.column_color:
            config.set("gui", 
                       "column_{}_color".format(x), 
                       cfg.column_color[x])

        try:
            config.set("gui", "ask_on_quit", cfg.ask_on_quit)
        except AttributeError:
            config.set("gui", "ask_on_quit", True)
            
        try:
            config.set("gui", "save_query_file", cfg.save_query_file)
        except AttributeError:
            config.set("gui", "save_query_file", True)

        try:
            config.set("gui", "query_file_path", cfg.query_file_path)
        except AttributeError:
            config.set("gui", "query_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "results_file_path", cfg.results_file_path)
        except AttributeError:
            config.set("gui", "results_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "textgrids_file_path", cfg.textgrids_file_path)
        except AttributeError:
            config.set("gui", "textgrids_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "stopwords_file_path", cfg.stopwords_file_path)
        except AttributeError:
            config.set("gui", "stopwords_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "filter_file_path", cfg.filter_file_path)
        except AttributeError:
            config.set("gui", "filter_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "uniques_file_path", cfg.uniques_file_path)
        except AttributeError:
            config.set("gui", "uniques_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "corpus_source_path", cfg.corpus_source_path)
        except AttributeError:
            config.set("gui", "corpus_source_path", os.path.expanduser("~"))
        try:
            config.set("gui", "text_source_path", cfg.text_source_path)
        except AttributeError:
            config.set("gui", "text_source_path", os.path.expanduser("~"))

        try:
            config.set("gui", "reaggregate_data", cfg.reaggregate_data)
        except AttributeError:
            config.set("gui", "reaggregate_data", True)

        try:
            config.set("gui", "save_query_string", cfg.save_query_string)
        except AttributeError:
            config.set("gui", "save_query_string", True)

    with codecs.open(cfg.config_path, "w", "utf-8") as output_file:
        config.write(output_file)

def get_con_configuration():
    """
    Returns a tuple containing the currently active connection configuration.
    
    The method uses the configuration name stored in the attribute 
    'current_server' to retrieve the configuration values from the
    dictionary 'server_configuration'.
    
    Returns
    -------
    tup : tuple or None
        If there is a configuration for the currently selected server,
        the method returns the tuple (db_host, db_port, db_name, 
        db_password). If no configuration is available, the method
        returns None.
    """
    if cfg.current_server in cfg.server_configuration:
        d = cfg.server_configuration[cfg.current_server]
        if d["type"] == SQL_MYSQL:
            return (d["host"], d["port"], d["type"], d["user"], d["password"])
        elif d["type"] == SQL_SQLITE:
            return (None, None, SQL_SQLITE, None, None)
    else:
        return None

def process_options():
    global cfg
    options = Options()
    cfg = options.cfg
    options.get_options()

def validate_module(path, expected_classes, whitelisted_modules, allow_if=False, hash=True):
    """
    Read the Python code from path, and validate that it contains only 
    the required class definitions and whitelisted module imports.
    
    The corpus modules are plain Python code, which opens an attack 
    vector for people who want to compromise the system: if an attacker
    managed to plant a Python file in the corpus module directory, this 
    file wouldbe processed automatically, and without validation, the 
    content would also be executed. 
    
    This method raises an exception if the Python file in the specified 
    path contains unexpected code.
    """
    
    return hashlib.md5(utf8("Dummy").encode("utf-8"))
    
    allowed_parents = (ast.If, ast.FunctionDef, ast.TryExcept, ast.TryFinally, ast.While, ast.For,
                       ast.With)

    if sys.version_info < (3, 0):
        allowed_statements = (ast.FunctionDef, ast.Assign, ast.AugAssign, 
                              ast.Return, ast.TryExcept, ast.TryFinally, 
                              ast.Pass, ast.Raise, ast.Assert, ast.Print)
    else:
        allowed_statements = (ast.FunctionDef, ast.Assign, ast.AugAssign, 
                              ast.Return, ast.TryExcept, ast.TryFinally, 
                              ast.Pass, ast.Raise, ast.Assert)

    def validate_node(node, parent):
        if isinstance(node, ast.ClassDef):
            if node.name in expected_classes:
                expected_classes.remove(node.name)
        
        elif isinstance(node, ast.ImportFrom):
            if whitelisted_modules != "all" and node.module not in whitelisted_modules:
                raise IllegalImportInModuleError(corpus_name, cfg.current_server, node.module, node.lineno)

        elif isinstance(node, ast.Import):
            for element in node.names:
                if whitelisted_modules != "all" and element not in whitelisted_modules:
                    raise IllegalImportInModuleError(corpus_name, cfg.current_server, element, node.lineno)
        
        elif isinstance(node, allowed_statements):
            pass
        
        elif isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Str):
                pass
            else:
                if not isinstance(parent, allowed_parents):
                    raise IllegalCodeInModuleError(corpus_name, cfg.current_server, node.lineno)
        
        elif isinstance(node, ast.If):
            if parent == None:
                if not allow_if:

                    raise IllegalCodeInModuleError(corpus_name, cfg.current_server, node.lineno)
            elif not isinstance(parent, allowed_parents):
                raise IllegalCodeInModuleError(corpus_name, cfg.current_server, node.lineno)
        
        elif isinstance(node, (ast.While, ast.For, ast.With, ast.Continue, ast.Break)):
            # these types are only allowed if the node is nested in 
            # a legal node type:
            if not isinstance(parent, allowed_parents):
                raise IllegalCodeInModuleError(corpus_name, cfg.current_server, node.lineno)
        else:
            print(node)
            raise IllegalCodeInModuleError(corpus_name, cfg.current_server, node.lineno)

        # recursively validate the content of the node:
        if hasattr(node, "body"):
            for child in node.body:
                validate_node(child, node)
    
    corpus_name = os.path.splitext(os.path.basename(path))[0]
    try:
        with codecs.open(path, "r") as module_file:
            content = module_file.read()
            tree = ast.parse(content)
            
            for node in tree.body:
                validate_node(node, None)
    except Exception as e:
        logger.error(e)

    if expected_classes:
        raise ModuleIncompleteError(corpus_name, cfg.current_server, expected_classes)
    if hash:
        #return hashlib.md5(content.encode("utf-8"))
        return hashlib.md5(utf8("MD5 hash not available").encode("utf-8"))

def set_current_server(name):
    """
    Changes the current server name. Also, update the currently available 
    resources.
    
    This method changes the content of the configuration variable 
    'current_server' to the content of the argument 'name'. It also calls the 
    method get_available_resources() for this configuration, and stores the 
    result in the configuration variable 'current_resources'.    
    
    Parameters
    ----------
    name : str 
        The name of the MySQL configuration
    """
    global cfg
    cfg.current_server = name
    
    if name:
        cfg.current_resources = get_available_resources(name)
    else:
        cfg.current_resources = None

    # make sure that a subdirectory exists in "connections" for the current
    # connection:
    path = os.path.join(cfg.connections_path, name)
    if not os.path.exists(path):
        os.makedirs(path)

    cfg.corpora_path = os.path.join(path, "corpora")
    if not os.path.exists(cfg.corpora_path):
        os.makedirs(cfg.corpora_path)

    cfg.adhoc_path = os.path.join(path, "adhoc")
    if not os.path.exists(cfg.adhoc_path):
        os.makedirs(cfg.adhoc_path)
    
    if cfg.server_configuration[name]["type"] == SQL_SQLITE:
        cfg.database_path = os.path.join(path, "databases")
        if not os.path.exists(cfg.database_path):
            os.makedirs(cfg.database_path)

def get_resource_of_database(db_name):
    """
    Get the resource that uses the database.
    """
    for name in cfg.current_resources:
        resource, _, _, _ = cfg.current_resources[name]
        if resource.db_name == db_name:
            return resource
    return None

def get_available_resources(configuration):
    """ 
    Return a dictionary with the available corpus module resource classes
    as values, and the corpus module names as keys.
    
    This method scans the content of the sub-directory 'corpora' for valid
    corpus modules. This directory has additional subdirectories for each 
    MySQL configuration. If a corpus module is found, the three resource 
    classes Resource, Corpus, and Lexicon are retrieved from the module.
    
    Parameters
    ----------
    configuration : str
        The name of the MySQL configuration, which corresponds to the 
        directory name in which the resources are stored.
    
    Returns
    -------
    d : dict
        A dictionary with resource names as keys, and tuples of resource
        classes as values:
        (module.Resource, module.Corpus, module.Lexicon, module_name)
    """
    
    def ensure_init_file(path):
        """
        Creates an empty file __init__.py in the given path if necessary.
        """
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(os.path.join(path, "__init__.py")):
            open(os.path.join(path, "__init__.py"), "a").close()
        
    d  = {}
    if configuration == None:
        return d

    # add corpus_path to sys.path so that modules can be imported from
    # that location:
    corpora_path = os.path.join(get_home_dir(), "connections", configuration, "corpora")

    # create the directory if it doesn't exist yet: 
    # cycle through the modules in the corpus path:
    for module_name in glob.glob(os.path.join(corpora_path, "*.py")):
        corpus_name, ext = os.path.splitext(os.path.basename(module_name))
        corpus_name = utf8(corpus_name)
        #try:
            #validate_module(
                #module_name, 
                #expected_classes = ["Resource", "Corpus", "Lexicon"],
                #whitelisted_modules = ["corpus", "__future__"],
                #allow_if = False,
                #hash = False)
        #except (ModuleIncompleteError, 
                #IllegalImportInModuleError, IllegalFunctionInModuleError,
                #IllegalCodeInModuleError) as e:
            #warnings.warn(str(e))
        #except SyntaxError as e:
            #warnings.warn("There is a syntax error in corpus module {}. Please remove this corpus module, and reinstall it afterwards.".format(corpus_name))
            #continue
        #except IndentationError as e:
            #warnings.warn("There is an indentation error in corpus module {}. Please remove this corpus module, and reinstall it afterwards.".format(corpus_name))
            #continue
        
        try:
            find = imp.find_module(corpus_name, [corpora_path])
            module = imp.load_module(corpus_name, *find)
        except SyntaxError as e:
            logger.warn("There is a syntax error in corpus module {}. The corpus is not available for queries. contact the corpus module maintainer.".format(corpus_name))
        except UnicodeEncodeError as e:
            logger.warn("There is a Unicode error in corpus module {}: {}".format(corpus_name, str(e)))
        except Exception as e:
            logger.warn("There is an error in corpus module {}: {}".format(corpus_name, str(e)))
        else:
            try:
                d[module.Resource.name] = (module.Resource, module.Corpus, module.Lexicon, module_name)
            except (AttributeError, ImportError) as e:
                warnings.warn("{} does not appear to be a valid corpus module.".format(corpus_name))
    return d

def get_resource(name, configuration):
    """
    Return a tuple containing the Resource, Corpus, and Lexicon of the 
    corpus module specified by 'name'.
    
    Arguments
    ---------
    name : str
        The name of the corpus module
    configuration : str
        The name of the MySQL configuration
        
    Returns
    -------
    res : tuple
        A tuple consisting of the Resource class, Corpus class, and Lexicon 
        class defined in the corpus module
    """
    Resource, Corpus, Lexicon, _ = get_available_resources(configuration)[name]
    return Resource, Corpus, Lexicon

def get_home_dir(create=True):
    """
    Return the path to the Coquery home directory. Also, create all required
    directories.
    
    The coquery_home path points to the directory where Coquery stores (and 
    looks for) the following files:
    
    $COQ_HOME/coquery.cfg               configuration file
    $COQ_HOME/coquery.log               log files
    $COQ_HOME/installer/                additional corpus installers
    $COQ_HOME/connections/$MYSQL_CONFIG/corpora
                                        installed corpus modules
    $COQ_HOME/connections/$MYSQL_CONFIG/adhoc
                                        adhoc installer modules
    $COQ_HOME/connections/$MYSQL_CONFIG/databases
                                        SQLite databases
    
    The location of $COQ_HOME depends on the operating system:
    
    Linux           either $XDG_CONFIG_HOME or ~/.config/Coquery
    Windows         %APPDATA%/Coquery
    Mac OS X        ~/Library/Application Support/Coquery
    """

    if platform.system() == "Linux":
        try:
            basepath = os.environ["XDG_CONFIG_HOME"]
        except KeyError:
            basepath = os.path.expanduser("~/.config")
    elif platform.system() == "Windows":
        try:
            basepath = os.environ["APPDATA"]
        except KeyError:
            basepath = os.path.expanduser("~")
    elif platform.system() == "Darwin":
        basepath = os.path.expanduser("~/Library/Application Support")
        
    coquery_home = os.path.join(basepath, "Coquery")
    connections_path = os.path.join(coquery_home, "connections")
    custom_installer_path = os.path.join(coquery_home, "installer")
    
    if create:
        # create Coquery home if it doesn't exist yet:
        if not os.path.exists(coquery_home):
            os.makedirs(coquery_home)
            
        # create custom installer directory if it doesn't exist yet:
        if not os.path.exists(custom_installer_path):
            os.makedirs(custom_installer_path)
            
        # create connection directory if it doesn't exist yet:
        if not os.path.exists(connections_path):
            os.makedirs(connections_path)

    return coquery_home

def decode_query_string(s):
    """
    Decode a query string that has been read from the configuration file.
    
    This method is the inverse of encode_query_string(). It takes a 
    comma-separated, quoted and escaped string and transforms it into 
    a newline-separated string without unneeded quotes and escapes.
    """
    in_quote = False
    escape = False
    l = []
    char_list = []
    last_ch = None
    for ch in s:
        if escape:
            char_list.append(ch)
            escape = False
        else:
            if ch == "\\":
                escape = True
            elif ch == '"':
                in_quote = not in_quote
            elif ch == ",":
                if in_quote:
                    char_list.append(ch)
                else:
                    l.append("".join(char_list))
                    char_list = []
            else:
                char_list.append(ch)
    l.append("".join(char_list))
    return "\n".join(l)

def encode_query_string(s):
    """
    Encode a query string that has can be written to a configuration file.
    
    This method is the inverse of decode_query_string(). It takes a newline-
    separated strinbg as read from the query string field, and transformes it
    into a comma-separated, quoted and escaped string that can be passed on 
    to the configuration file.
    """
    l = s.split("\n")
    str_list = []
    for s in l:
        s = s.replace("\\", "\\\\")
        s = s.replace('"', '\\"')
        str_list.append(s)
    return ",".join(['"{}"'.format(x) for x in str_list])
        
def has_module(name):
    """
    Check if the Python module 'name' is available.
    
    Parameters
    ----------
    name : str 
        The name of the Python module, as used in an import instruction.
        
    This function uses ideas from this Stack Overflow question:
    http://stackoverflow.com/questions/14050281/
        
    Returns
    -------
    b : bool
        True if the module exists, or False otherwise.
    """

    if sys.version_info > (3, 3):
        import importlib.util
        return importlib.util.find_spec(name) is not None
    elif sys.version_info > (2, 7, 99):
        import importlib
        return importlib.find_loader(name) is not None
    else:
        import pkgutil
        return pkgutil.find_loader(name) is not None

_recent_python = sys.version_info < (2, 7)
_use_nltk = has_module("nltk")
_use_mysql = has_module("pymysql")
_use_seaborn = has_module("seaborn")
_use_pdfminer = has_module("pdfminer")
_use_qt = has_module("PyQt4") or has_module("PySide")
_use_chardet = has_module("chardet")
_use_tgt = has_module("tgt")
_use_docx = has_module("docx")
_use_odfpy = has_module("odf")
_use_bs4 = has_module("bs4")

missing_modules = []
for mod in ["sqlalchemy", "pandas"]:
    if not has_module(mod):
        missing_modules.append(mod)

logger = logging.getLogger(NAME)

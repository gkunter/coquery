# -*- coding: utf-8 -*-
"""
options.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import __init__

# Python 3.x: import configparser 
# Python 2.x: import ConfigParser as configparser
try:
    import ConfigParser as configparser
except ImportError:
    try:
        import configparser
    except ImportError as e:
        raise e

import sys
import os
import argparse
import logging
import codecs
import tokens

from defines import *
from errors import *

class Options(object):
    def __init__(self):
        try:
            self.base_path = os.path.dirname(__init__.__file__)
        except AttributeError:
            self.base_path = "."

        self.corpus_argument_dict = {
            "help": "specify the corpus to use", 
            "choices": get_available_resources().keys(), 
            "type": type(str(""))}

        self.prog_name = __init__.NAME
        self.config_name = "%s.cfg" % __init__.NAME
        self.version = __init__.__version__
        self.parser = argparse.ArgumentParser(prog=self.prog_name, add_help=False)
        self.setup_parser()

        self.args = argparse.Namespace()

        self.args.config_path = os.path.join(self.base_path, self.config_name)
        self.args.filter_list = []
        self.args.program_location = self.base_path
        self.args.version = self.version
        self.args.query_label = ""
        self.args.input_path = ""
        self.args.query_string = ""
        self.args.save_query_string = True
        self.args.save_query_file = True
        try:
            self.args.parameter_string = " ".join([x.decode("utf8") for x in sys.argv [1:]])
        except AttributeError:
            self.args.parameter_string = " ".join([x for x in sys.argv [1:]])

        self.args.selected_features= []
        self.args.external_links = {}
        self.args.selected_functions = []
        
        self.args.context_left = 0
        self.args.context_right = 0
        
        # these attributes are used only in the GUI:
        self.args.column_width = {}
        self.args.column_color = {}
        self.args.column_visibility = {}
        self.args.row_visibility = {}
        self.args.row_color = {}

    @property
    def cfg(self):
        return self.args
        
    def setup_parser(self):
        group = self.parser.add_mutually_exclusive_group()
        self.parser.add_argument("MODE", help="determine the query mode (default: TOKEN)", choices=(QUERY_MODE_TOKENS, QUERY_MODE_FREQUENCIES, QUERY_MODE_DISTINCT, QUERY_MODE_STATISTICS, QUERY_MODE_COLLOCATIONS), type=str, nargs="?")
        self.parser.add_argument("corpus", nargs="?", **self.corpus_argument_dict)
        
        group.add_argument("--gui", help="Use a graphical user interface (requires Qt)", action="store_true")
        # General options:
        self.parser.add_argument("-o", "--outputfile", help="write results to OUTPUTFILE (default: write to console)", type=str, dest="output_path")
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-i", "--inputfile", help="read query strings from INPUTFILE", type=str, dest="input_path")
        group.add_argument("-q", "--query", help="use QUERY for search, ignoring any INPUTFILE", dest="query_list")
        self.parser.add_argument("-F", "--filter", help="use FILTER to query only a selection of texts", type=str, default="", dest="source_filter")

        # File options:
        group = self.parser.add_argument_group("File options")
        group.add_argument("-a", "--append", help="append output to OUTPUTFILE, if specified (default: overwrite)", action="store_true")
        group.add_argument("-k", "--skip", help="skip SKIP lines in INPUTFILE (default: 0)", type=int, default=0, dest="skip_lines")
        group.add_argument("-H", "--header", help="use first row of INPUTFILE as headers", action="store_true", dest="file_has_headers")
        group.add_argument("-n", "--number", help="use column NUMBER in INPUTFILE for queries", type=int, default=1, dest="query_column_number")
        group.add_argument("--is", "--input-separator", help="use CHARACTER as separator in input CSV file",  default=',', metavar="CHARACTER", dest="input_separator")
        group.add_argument("--os", "--output-separator", help="use CHARACTER as separator in output CSV file", default=',', metavar="CHARACTER", dest="output_separator")
        group.add_argument("--quote-character", help="use CHARACTER as quoting character", default='"', metavar="CHARACTER", dest="quote_char")
        group.add_argument("--input-encoding", help="use INPUT-ENCODING as the encoding scheme for the input file (default: utf-8)", type=str, default="utf-8", dest="input_encoding")
        group.add_argument("--output-encoding", help="use OUTPUT-ENCODING as the encoding scheme for the output file (default: utf-8)", type=str, default="utf-8", dest="output_encoding")

        # Debug options:
        group = self.parser.add_argument_group("Debug options")
        group.add_argument("-d", "--dry-run", help="dry run (do not query, just log the query strings)", action="store_true")
        group.add_argument("-v", "--verbose", help="produce a verbose output", action="store_true", dest="verbose")
        group.add_argument("-V", "--super-verbose", help="be super-verbose (i.e. log function calls)", action="store_true")
        group.add_argument("-E", "--explain", help="explain mySQL queries in log file", action="store_true", dest="explain_queries")
        group.add_argument("--benchmark", help="benchmarking of Coquery", action="store_true")
        group.add_argument("--profile", help="deterministic profiling of Coquery", action="store_true")
        group.add_argument("--memory-dump", help="list objects that consume much memory after queries", action="store_true", dest="memory_dump")
        group.add_argument("--experimental", help="use experimental features (may be buggy)", action="store_true")
        group.add_argument("--comment", help="a comment that is shown in the log file", type=str)

        # Query options:
        group = self.parser.add_argument_group("Query options")
        group.add_argument("-C", "--case", help="be case-sensitive (default: be COCA-compatible and ignore case)", action="store_true", dest="case_sensitive")
        group.add_argument("-L", "--lemmatize-tokens", help="treat all tokens in query as lemma searches (default: be COCA-compatible and only do lemma searches if explicitly specified in query string)", action="store_true")
        group.add_argument("-r", "--regexp", help="use regular expressions", action="store_true", dest="regexp")

        # Output options:
        group = self.parser.add_argument_group("Output options")
        group.add_argument("--suppress-header", help="exclude column header from the output (default: include)", action="store_false", dest="show_header")
        
        group.add_argument("--context_mode", help="specify the way the context is included in the output", choices=[CONTEXT_KWIC, CONTEXT_STRING, CONTEXT_COLUMNS], default=CONTEXT_KWIC, type=str)
        group.add_argument("-c", "--context_span", help="include context with N words to the left and the right of the keyword, or with N words to the left and M words to the right if the notation '-c N, M' is used", default=0, type=int, dest="context_span")
        group.add_argument("--sentence", help="include the sentence of the token as a context (not supported by all corpora, currently not implemented)", dest="context_sentence", action="store_true")

        group.add_argument("--digits", help="set the number of digits after the period", dest="digits", default=3, type=int)

        group.add_argument("--number-of-tokens", help="output up to NUMBER different tokens (default: all tokens)", default=0, type=int, dest="number_of_tokens", metavar="NUMBER")
        #group.add_argument("-u", "--unique-id", help="include the token id for the first token matching the output", action="store_true", dest="show_id")
        group.add_argument("-Q", "--show-query", help="include query string in the output", action="store_true", dest="show_query")
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
        
        # Do a first argument parse to get the corpus to be used, and 
        # whether a GUI is requested. This parse doesn't raise an argument 
        # error.
        args, unknown = self.parser.parse_known_args()
        self.args.gui = args.gui
        
        self.read_configuration()
        try:
            if args.corpus:
                self.args.corpus = args.corpus
            elif not self.args.corpus:
                self.args.corpus = ""
        except AttributeError:
            self.args.corpus = ""
        # if no corpus is selected and no GUI is requested, display the help
        # and exit.
        if not self.args.corpus and not (args.gui):
            self.parser.print_help()
            sys.exit(1)
        
        D = {}
        
        if self.args.corpus:
            try:
                # build a dictionary D for the selected corpus that contains as 
                # values the features provided by each of the tables defined in
                # the resource. The features are included as tuples, with first,
                # the display name and second, the resource feature name.
                resource, _, _ = get_resource(self.args.corpus)
                corpus_features = resource.get_corpus_features()
                lexicon_features = resource.get_lexicon_features()
                for rc_feature, column in corpus_features + lexicon_features:
                    if "_denorm_" not in rc_feature:
                        table = "{}_table".format(rc_feature.split("_")[0])
                        if table not in D:
                            D[table] = set([])
                        D[table].add((column, rc_feature))
            
                if self.args.corpus.upper() == "COCA":
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

        if self.args.context_mode == CONTEXT_COLUMNS:
            self.args.context_columns = True
        else:
            self.args.context_columns = False
            
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
        
    def read_configuration(self):
        # defaults:
        db_user = "mysql"
        db_password = "mysql"
        db_port = 3306
        db_host = "localhost"
        if os.path.exists(self.cfg.config_path):
            logger.info("Using configuration file %s" % self.cfg.config_path)
            config_file = configparser.ConfigParser()
            config_file.read(self.cfg.config_path)
            
            if "sql" in config_file.sections():
                try:
                    db_user = config_file.get("sql", "db_user")
                except configparser.NoOptionError:
                    pass
                try:
                    db_password = config_file.get("sql", "db_password")
                except configparser.NoOptionError:
                    pass
                try:
                    db_port = int(config_file.get("sql", "db_port"))
                except configparser.NoOptionError:
                    pass
                try:
                    db_host = config_file.get("sql", "db_host")
                except configparser.NoOptionError:
                    pass
                
            # only use the other settings from the configuration file if a 
            # GUI is used:
            if self.args.gui:
                for section in config_file.sections():
                    if section == "main":
                        try:
                            default_corpus = config_file.get("main", "default_corpus")
                        except configparser.NoOptionError:
                            default_corpus = self.corpora_dict.keys()[0]
                        vars(self.args) ["corpus"] = default_corpus
                        try:
                            mode = config_file.get("main", "query_mode")
                            vars(self.args)["MODE"] = mode
                        except configparser.NoOptionError:
                            default_corpus = QUERY_MODE_DISTINCT
                        try:
                            last_query = config_file.get("main", "query_string")
                            vars(self.args)["query_list"] = [last_query.strip('"')]
                        except configparser.NoOptionError:
                            pass
                        try:
                            vars(self.args)["input_path"] = config_file.get("main", "query_file")
                        except configparser.NoOptionError:
                            pass

                    elif section == "output":
                        for variable, value in config_file.items("output"):
                            if value:
                                vars(self.args)["selected_features"].append(variable)
                    elif section == "filter":
                        for _, filt_text in config_file.items("filter"):
                            vars(self.args)["filter_list"].append(filt_text.strip('"'))

                    elif section == "context":
                        try:
                            vars(self.args)["context_left"] = int(config_file.get("context", "words_left"))
                        except (configparser.NoOptionError, ValueError):
                            pass
                        try:
                            vars(self.args)["context_right"] = int(config_file.get("context", "words_right"))
                        except (configparser.NoOptionError, ValueError):
                            pass
                        try:
                            vars(self.args)["context_mode"] = config_file.get("context", "mode")
                        except (configparser.NoOptionError, ValueError):
                            pass

                    elif section == "gui":
                        try:
                            self.args.ask_on_quit = bool(config_file.get("gui", "ask_on_quit"))
                        except configparser.NoOptionError:
                            self.args.ask_on_quit = True
                        try:
                            self.args.save_query_string = config_file.get("gui", "save_query_string")
                        except configparser.NoOptionError:
                            self.args.save_query_string = True
                        try:
                            self.args.save_query_file = config_file.get("gui", "save_query_file")
                        except configparser.NoOptionError:
                            self.args.save_query_file = True

                        try:
                            vars(self.args)["width"] = int(config_file.get("gui", "width"))
                        except (configparser.NoOptionError, ValueError):
                            vars(self.args)["width"] = None
                        try:
                            vars(self.args)["height"] = int(config_file.get("gui", "height"))
                        except (configparser.NoOptionError, ValueError):
                            vars(self.args)["height"] = None

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
                            if name.startswith("context_view_") or name.startswith("error_box_") or name.startswith("context_manager"):
                                try:
                                    vars(self.args)[name] = int(value)
                                except ValueError:
                                    pass
                            
        vars(self.args) ["db_user"] = db_user
        vars(self.args) ["db_password"] = db_password
        vars(self.args) ["db_port"] = db_port
        vars(self.args) ["db_host"] = db_host

cfg = None

class UnicodeConfigParser(configparser.RawConfigParser):
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
            config.read(input_file)
    
    if not "main" in config.sections():
        config.add_section("main")
    config.set("main", "default_corpus", cfg.corpus)
    config.set("main", "query_mode", cfg.MODE)
    if cfg.query_list and cfg.save_query_string:
        config.set("main", "query_string", ",".join(['"{}"'.format(x) for x in cfg.query_list]))
    if cfg.input_path and cfg.save_query_file:
        config.set("main", "query_file", cfg.input_path)
    
    if not "sql" in config.sections():
        config.add_section("sql")
    config.set("sql", "db_user", cfg.db_user)
    config.set("sql", "db_password", cfg.db_password)
    config.set("sql", "db_port", cfg.db_port)
    config.set("sql", "db_host", cfg.db_host)
    
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
        window_size = cfg.main_window.size()
        config.set("gui", "height", window_size.height())
        config.set("gui", "width", window_size.width())

        for x in cfg.column_width:
            if not x.startswith("coquery_invisible") and cfg.column_width[x]:
                config.set("gui", 
                        "column_{}_width".format(x), 
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
            config.set("gui", "save_query_string", cfg.save_query_string)
        except AttributeError:
            config.set("gui", "save_query_string", True)

        try:
            config.set("gui", "context_view_width", cfg.context_view_width)
        except AttributeError:
            pass
        try:
            config.set("gui", "context_view_height", cfg.context_view_height)
        except AttributeError:
            pass
        try:
            config.set("gui", "context_view_words", cfg.context_view_words)
        except AttributeError:
            pass

        try:
            config.set("gui", "corpus_manager_view_width", cfg.corpus_manager_view_width)
        except AttributeError:
            pass
        try:
            config.set("gui", "corpus_manager_view_height", cfg.corpus_manager_view_height)
        except AttributeError:
            pass
        
        try:
            config.set("gui", "error_box_width", cfg.error_box_width)
        except AttributeError:
            pass
        try:
            config.set("gui", "error_box_height", cfg.error_box_height)
        except AttributeError:
            pass

    with codecs.open(cfg.config_path, "w", "utf-8") as output_file:
        config.write(output_file)

def process_options():
    global cfg
    options = Options()
    options.get_options()
    cfg = options.cfg

try:
    logger = logging.getLogger(__init__.NAME)
except AttributeError:
    pass


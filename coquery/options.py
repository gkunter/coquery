# -*- coding: utf-8 -*-
"""
options.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from __future__ import unicode_literals

try:
    # Python 2.x: import ConfigParser as _configparser
    from ConfigParser import ConfigParser as _configparser, RawConfigParser
    from ConfigParser import NoOptionError, ParsingError, NoSectionError
except ImportError:
    # Python 3.x: import configparser as _configparser
    from configparser import ConfigParser as _configparser, RawConfigParser
    from configparser import NoOptionError, ParsingError, NoSectionError

import argparse
import warnings
import codecs
import ast
import glob
import imp
import os
import sys
import logging
import re

import hashlib
from collections import defaultdict

from . import general, NAME
from .errors import (
    IllegalImportInModuleError, IllegalCodeInModuleError,
    ConfigurationError, ModuleIncompleteError,
    add_source_path)
from .defines import (
    DEFAULT_CONFIGURATION,
    SQL_SQLITE, SQL_MYSQL,
    DEFAULT_MISSING_VALUE,
    QUERY_MODES, QUERY_MODE_TOKENS,
    CONTEXT_NONE, CONTEXT_COLUMNS, CONTEXT_KWIC, CONTEXT_STRING)
from .unicode import utf8
from .links import parse_link_text
from .filters import parse_filter_text
from .connections import get_connection, SQLiteConnection

# make ast work in all Python versions:
if not hasattr(ast, "TryExcept"):
    ast.TryExcept = ast.Try
if not hasattr(ast, "TryFinally"):
    ast.TryFinally = ast.Try


CONSOLE_DEPRECATION = """The command-line version of Coquery is deprecated.

It doesn't support all features of the graphical interface, may contain
untested code, and generally produce unexpected "results.

Command-line support may be altogether removed in a future release.

"""


class CoqConfigParser(_configparser, object):
    """
    A config parser with enhanced type methods
    """
    def items(self, section):
        try:
            return super(CoqConfigParser, self).items(section)
        except (NoSectionError, AttributeError):
            return []

    def str(self, section, option, fallback=None, d=None):
        if d:
            fallback = d.get(option, fallback)
        try:
            val = self.get(section, option)
        except (NoOptionError, ValueError, AttributeError) as e:
            if fallback is not None:
                val = fallback
            else:
                raise e
        return val

    def bool(self, section, option, fallback=None, d=None):
        if d:
            fallback = d.get(option, fallback)
        try:
            val = self.getboolean(section, option)
        except (NoOptionError, ValueError, AttributeError) as e:
            if fallback is not None:
                val = fallback
            else:
                raise e
        return val

    def int(self, section, option, fallback=None, d=None):
        if d:
            fallback = d.get(option, fallback)
        try:
            val = self.getint(section, option)
        except (NoOptionError, ValueError, AttributeError) as e:
            if fallback is not None:
                val = fallback
            else:
                raise e
        return val

    def float(self, section, option, fallback=None, d=None):
        if d:
            fallback = d.get(option, fallback)
        try:
            val = self.getfloat(section, option)
        except (NoOptionError, ValueError, AttributeError) as e:
            if fallback is not None:
                val = fallback
            else:
                raise e
        return val


class UnicodeConfigParser(RawConfigParser):
    """
    Define a subclass of RawConfigParser that works with Unicode (hopefully).
    """
    def write(self, fp, DEFAULTSECT="main"):
        """Fixed for Unicode output"""
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, utf8(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s = %s\n" %
                             (key, utf8(value).replace('\n', '\n\t')))
            fp.write("\n")

    # This function is needed to override default lower-case conversion
    # of the parameter's names. They will be saved 'as is'.
    def optionxform(self, strOut):
        return strOut


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

        self.args.coquery_home = general.get_home_dir(create=True)
        if getattr(sys, "frozen", None):
            self.args.base_path = os.path.dirname(sys.executable)
        elif __file__:
            self.args.base_path = os.path.dirname(__file__)
        self.prog_name = NAME
        self.config_name = "%s.cfg" % NAME.lower()
        self.parser = argparse.ArgumentParser(prog=self.prog_name, add_help=False, formatter_class=CoqHelpFormatter)

        self.args.config_path = os.path.join(self.args.coquery_home,
                                             self.config_name)
        connection = SQLiteConnection(DEFAULT_CONFIGURATION)
        self.args.connections = dict(Default=connection)

        self.args.reference_corpus = {}
        self.args.main_window = None
        self.args.first_run = False
        self.args.limit_matches = False
        self.args.number_of_tokens = 50
        self.args.sample_matches = False
        self.args.sample_size = 50
        self.args.last_number_of_tokens = 50
        self.args.output_separator = ","
        self.args.corpus = None
        self.args.gui = True
        self.args.csv_restrict = None

        self.args.table_links = defaultdict(list)

        # set up paths:
        self.args.installer_path = os.path.join(
            self.args.base_path, "installer")
        self.args.connections_path = os.path.join(
            self.args.coquery_home, "connections")
        self.args.cache_path = os.path.join(
            self.args.coquery_home, "cache")
        self.args.stopword_path = os.path.join(
            self.args.base_path, "stopwords")

        self.args.verbose = False
        self.args.comment = None

        self.args.use_mysql = True

        try:
            self.args.parameter_string = " ".join(
                [x.decode("utf8") for x in sys.argv[1:]])
        except AttributeError:
            self.args.parameter_string = " ".join(
                [x for x in sys.argv[1:]])

        self.args.filter_list = []
        self.args.selected_features = set("word_label")
        self.args.external_links = {}

        # these attributes are used only in the GUI:
        self.args.column_width = {}
        self.args.column_color = {}
        self.args.column_names = {}
        self.args.row_color = {}
        self.args.no_ngram = False

        self.args.managers = {}
        self.args.summary_group = []

    @property
    def cfg(self):
        return self.args

    def setup_parser(self):
        self.parser.add_argument("MODE", help="determine the query mode (default: TOKEN)", choices=QUERY_MODES.keys(), type=str, nargs="?")

        # If Qt is available, the GUI is used by default. The command line
        # interface can be selected by using the --con option:
        if use_qt:
            self.parser.add_argument("--con", help="Run Coquery as a console program", dest="gui", action="store_false")

        # General options:
        self.parser.add_argument("-o", "--outputfile", help="write results to OUTPUTFILE (default: write to console)", type=str, dest="output_path")
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-i", "--inputfile", help="read query strings from INPUTFILE", type=str, dest="input_path")
        group.add_argument("-q", "--query", help="use QUERY for search, ignoring any INPUTFILE", dest="query_list")
        self.parser.add_argument("-f", "--filter", help="use FILTER to query only a selection of texts", type=str, default="", dest="source_filter")

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
        group.add_argument("-v", "--verbose", help="produce a verbose output", action="store_true", dest="verbose")
        group.add_argument("-E", "--explain", help="explain mySQL queries in log file", action="store_true", dest="explain_queries")
        group.add_argument("--no_ngram", help="do not use N-gram lookup tables", action="store_true")
        group.add_argument("--benchmark", help="benchmarking of Coquery", action="store_true")
        group.add_argument("--profile", help="deterministic profiling of Coquery", action="store_true")
        group.add_argument("--memory-dump", help="list objects that consume much memory after queries", action="store_true", dest="memory_dump")
        group.add_argument("--experimental", help="use experimental features (may be buggy)", action="store_true")
        group.add_argument("--comment", help="a comment that is shown in the log file", type=str)

        # Query options:
        group = self.parser.add_argument_group("Query options")
        group.add_argument("-C", "--output_case", help="be case-sensitive in the output (default: ignore case)", action="store_true", dest="output_case_sensitive")
        group.add_argument("--query_case", help="be case-sensitive when querying (default: ignore case)", action="store_true", dest="query_case_sensitive")
        group.add_argument("-r", "--regexp", help="use regular expressions", action="store_true", dest="regexp")

        # Output options:
        group = self.parser.add_argument_group("Output options")

        group.add_argument("--context_mode", help="specify the way the context is included in the output", choices=[CONTEXT_KWIC, CONTEXT_STRING, CONTEXT_COLUMNS], type=str)
        group.add_argument("-c", "--context_span", help="include context with N words to the left and the right of the keyword, or with N words to the left and M words to the right if the notation '-c N, M' is used", default=0, type=int, dest="context_span")
        group.add_argument("--sentence", help="include the sentence of the token as a context (not supported by all corpora, currently not implemented)", dest="context_sentence", action="store_true")

        group.add_argument("--digits", help="set the number of digits after the period", dest="digits", default=3, type=int)

        group.add_argument("--number_of_tokens", help="output up to NUMBER different tokens (default: all tokens)", default=0, type=int, dest="number_of_tokens", metavar="NUMBER")
        group.add_argument("--show_filter", help="include the filter strings in the output", action="store_true", dest="show_filter")
        group.add_argument("--freq-label", help="use this label in the heading line of the output (default: Freq)", default="Freq", type=str, dest="freq_label")
        group.add_argument("--no_align", help="Control if quantified token columns are aligned. If not set (the default), the columns in the result table are aligned so that row cells belonging to the same query token are placed in the same column. If set, this alignment is disabled. In that case, row cells are padded to the right.", action="store_false", dest="align_quantified")

    def get_options(self, read_file):
        """
        Read the values from the configuration file, and merge them with
        the command-line options. Values set in the configuration file are
        overwritten by command-line arguments.

        If a GUI is used, no corpus needs to be specified, and all values
        from the configuration file are used. If the command-line interface
        is used, both a corpus and a query mode have to be specified, and
        only the database settings from the configuration file are used.
        """

        self.setup_parser()

        # Do a first argument parse to get the corpus to be used, and
        # whether a GUI is requested. This parse doesn't raise an argument
        # error.
        args, unknown = self.parser.parse_known_args()

        self.args.gui = args.gui
        self.args.to_file = False

        self.read_configuration(read_file)

        args, unknown = self.parser.parse_known_args()

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

        self.parser.add_argument("-h", "--help", help="show this help message and exit", action="store_true")

        # reparse the arguments, this time with options that allow feature
        # selection based on the table structure of the corpus
        args, unknown = self.parser.parse_known_args()
        if unknown:
            self.parser.print_help()
            sys.exit(1)
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

        try:
            self.args.MODE = QUERY_MODES[self.args.MODE]
        except KeyError:
            if self.args.MODE not in QUERY_MODES.values():
                self.args.MODE = QUERY_MODE_TOKENS


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
            self.args.input_separator = (
                codecs.getdecoder("unicode_escape")(self.args.input_separator)[0])

        # make sure that a command query consisting of one string is still
        # stored as a list:
        if self.args.query_list:
            if type(self.args.query_list) != list:
                self.args.query_list = [self.args.query_list]
            try:
                self.args.query_list = [x.decode("utf8") for x in self.args.query_list]
            except AttributeError:
                pass
        logging.info("Command line parameters: " + self.args.parameter_string)

    def read_configuration(self, read_file):
        defaults = {
            "default_corpus": "",
            "query_mode": QUERY_MODE_TOKENS,
            "query_string": "",
            "query_cache_size": 500 * 1024 * 1024,
            "use_cache": use_cachetools,
            "query_case_sensitive": False,
            "output_case_sensitive": False,
            "regexp": False,
            "experimental": False,
            "output_to_lower": True,
            "drop_duplicates": True,
            "na_string": DEFAULT_MISSING_VALUE,
            "custom_installer_path": os.path.join(
                self.args.coquery_home, "installer"),
            "binary_path": os.path.join(
                self.args.coquery_home, "binary"),
            "csv_file": "",
            "csv_separator": ",",
            "csv_column": 1,
            "csv_has_header": False,
            "csv_line_skip": 0,
            "csv_quote_char": '"',
            "context_mode": CONTEXT_NONE,
            "context_left": 3,
            "context_right": 3,
            "collo_left": 3,
            "collo_right": 3,
            "context_restrict": False,
            "show_log_messages": "ERROR,WARNING,INFO",
            "decimal_digits": 3,
            "drop_on_na": False,
            }

        import inspect
        from . import functions
        from .managers import Group, Summary

        func_types = {}
        for _, cls in inspect.getmembers(functions):
            if callable(cls):
                try:
                    func_types[cls._name] = cls
                except AttributeError:
                    pass

        self.args.first_run = True
        config_file = CoqConfigParser()

        if os.path.exists(self.cfg.config_path) and read_file:
            logging.info("Using configuration file %s" % self.cfg.config_path)
            try:
                config_file.read(self.cfg.config_path)
            except (IOError, TypeError, ParsingError) as e:
                warnings.warn("Configuration file {} could not be read.".format(cfg.config_path))
                raise ConfigurationError((str(e).replace("\\n", "\n")
                                                .replace("\n", "<br>")))
            else:
                self.args.first_run = False

        for x in ["main", "sql", "gui", "output", "filter", "context",
                  "links", "reference_corpora", "functions", "groups"]:
            if x not in config_file.sections():
                config_file.add_section(x)

        # read SQL configuration:
        connection_dict = defaultdict(dict)
        for name, value in config_file.items("sql"):
            if name.startswith("config_"):
                fields = name.split("_")
                if len(fields) != 3:
                    continue
                else:
                    _, number, variable = fields
                if variable == "port":
                    try:
                        connection_dict[number][variable] = int(value)
                    except ValueError:
                        continue
                elif variable in {"name", "host", "type", "user", "password",
                                  "path"}:
                    connection_dict[number][variable] = value

                    # for backward compatibility:
                    if variable == "type":
                        connection_dict[number]["dbtype"] = value

        for i in connection_dict:
            connection = get_connection(**connection_dict[i])
            self.args.connections[connection.name] = connection

        # select active SQL configuration, or use Default as fallback
        connection_name = DEFAULT_CONFIGURATION
        try:
            connection_name = config_file.str("sql", "active_configuration")
        except Exception:
            pass
        self.args.current_connection = self.args.connections[connection_name]

        # read reference corpora
        for key, val in config_file.items("reference_corpora"):
            if re.match("reference\d+$", key):
                configuration, corpus = val.split(",")
                self.args.reference_corpus[configuration] = corpus

        # only use the other settings from the configuration file if a
        # GUI is used:
        if self.args.gui:
            # Read MAIN section:
            self.args.corpus = config_file.str("main", "default_corpus", d=defaults)
            self.args.MODE = config_file.str("main", "query_mode", d=defaults)
            last_query = config_file.str("main", "query_string", d=defaults)

            try:
                self.args.query_list = decode_query_string(last_query)
            except (ValueError):
                self.args.query_list = []
                pass
            self.args.query_cache_size = config_file.int("main", "query_cache_size", d=defaults)
            self.args.query_case_sensitive = config_file.bool("main", "query_case_sensitive", d=defaults)
            self.args.output_case_sensitive = config_file.bool("main", "output_case_sensitive", d=defaults)
            self.args.regexp = config_file.bool("main", "regexp", d=defaults)
            self.args.experimental = config_file.bool("main", "experimental", d=defaults)
            self.args.output_to_lower = config_file.bool("main", "output_to_lower", d=defaults)
            self.args.drop_on_na = config_file.bool("main", "drop_on_na", d=defaults)
            self.args.na_string = config_file.str("main", "na_string", d=defaults)
            self.args.custom_installer_path = config_file.str(
                "main", "custom_installer_path", d=defaults)
            self.args.binary_path = config_file.str(
                "main", "binary_path", d=defaults)
            if use_cachetools:
                self.args.use_cache = config_file.bool("main", "use_cache", d=defaults)
            else:
                self.args.use_cache = False
            self.args.input_path = config_file.str("main", "csv_file", d=defaults)
            self.args.input_separator = config_file.str("main", "csv_separator", d=defaults)
            self.args.query_column_number = config_file.int("main", "csv_column", d=defaults)
            self.args.file_has_headers = config_file.bool("main", "csv_has_header", d=defaults)
            self.args.skip_lines = config_file.int("main", "csv_line_skip", d=defaults)
            self.args.quote_char = config_file.str("main", "csv_quote_char", d=defaults)
            self.args.xkcd = config_file.bool("main", "xkcd", fallback=False)
            # read CONTEXT section:
            self.args.context_left = config_file.int("context", "context_left", d=defaults)
            self.args.context_right = config_file.int("context", "context_right", d=defaults)
            self.args.context_mode = config_file.str("context", "context_mode", d=defaults)
            self.args.context_restrict = config_file.bool("context", "context_restrict", d=defaults)
            self.args.collo_left = config_file.int("context", "collo_left", d=defaults)
            self.args.collo_right = config_file.int("context", "collo_right", d=defaults)

            # read OUTPUT section:
            for variable, value in config_file.items("output"):
                if value and variable.strip():
                    self.args.selected_features.add(variable)

            # read LINKS section
            for _, val in config_file.items("links"):
                try:
                    connection, _, link_text = val.partition(",")
                except ValueError:
                    pass
                else:
                    try:
                        link = parse_link_text(link_text)
                    except ValueError:
                        pass
                    else:
                        self.args.table_links[connection].append(link)

            # read GUI section:
            group = config_file.str("gui", "group_columns", fallback="")
            self.args.group_columns = group.split(",")
            self.args.last_toolbox = config_file.int("gui", "last_toolbox", fallback=0)
            self.args.select_radio_query_file = config_file.bool("gui", "select_radio_query_file", fallback=False)
            stopwords = config_file.str("gui", "stopword_list", fallback="")
            self.args.stopword_list = [x for x
                                       in decode_query_string(stopwords).split("\n")
                                       if x]
            group = config_file.str("gui", "group_columns", fallback="")
            self.args.ask_on_quit = config_file.bool("gui", "ask_on_quit", fallback=True)
            self.args.word_wrap = config_file.bool("gui", "word_wrap", fallback=False)
            self.args.save_query_string = config_file.bool("gui", "save_query_string", fallback=True)
            self.args.save_query_file = config_file.bool("gui", "save_query_file", fallback=True)

            # various paths:
            self.args.query_file_path = config_file.str("gui", "query_file_path", fallback=os.path.expanduser("~"))
            self.args.textgrids_file_path = config_file.str("gui", "textgrids_file_path", fallback=os.path.expanduser("~"))
            self.args.results_file_path = config_file.str("gui", "results_file_path", fallback=os.path.expanduser("~"))
            self.args.output_file_path = config_file.str("gui", "output_file_path", fallback=os.path.expanduser("~"))
            self.args.export_file_path = config_file.str(
                "gui", "export_file_path", fallback=os.path.expanduser("~"))
            self.args.stopwords_file_path = config_file.str("gui", "stopwords_file_path", fallback=os.path.expanduser("~"))
            self.args.filter_file_path = config_file.str("gui", "filter_file_path", fallback=os.path.expanduser("~"))
            self.args.uniques_file_path = config_file.str("gui", "uniques_file_path", fallback=os.path.expanduser("~"))
            self.args.corpus_table_source_path = config_file.str("gui", "corpus_table_source_path", fallback="")
            self.args.text_source_path = config_file.str(
                "gui", "text_source_path",
                fallback=os.path.join(self.args.base_path, "texts", "alice"))

            self.args.show_data_management = config_file.bool("gui", "show_data_management", fallback=True)
            self.args.show_output_columns = config_file.bool("gui", "show_output_columns", fallback=True)

            self.args.drop_duplicates = config_file.bool("gui", "drop_duplicates", fallback=False)
            self.args.number_of_tokens = config_file.int("gui", "number_of_tokens", fallback=0)
            self.args.limit_matches = config_file.bool("gui", "limit_matches", fallback=False)
            self.args.sample_size = config_file.int("gui", "sample_size", fallback=0)
            self.args.sample_matches = config_file.bool("gui", "sample_matches", fallback=False)

            s = config_file.str("gui", "show_log_messages", d=defaults)
            try:
                self.args.show_log_messages = [x.strip() for x in s.split(",") if x]
            except:
                s = defaults["show_log_messages"]
            self.args.digits = config_file.int(
                "gui", "decimal_digits", d=defaults)
            self.args.float_format = config_file.str(
                "gui", "float_format",
                fallback="{:.%if}" % self.args.digits)

            # read FILTER section

            for var, value in config_file.items("filter"):
                f_type, _, n = var.partition("_")
                try:
                    filt = parse_filter_text(value)
                except ValueError:
                    pass
                else:
                    self.args.filter_list.append(filt)

            # read FUNCTIONS section
            sum_columns = {}
            sum_values = {}
            sum_aggrs = {}
            sum_names = {}
            sum_types = {}
            max_sum_func = 0

            for var, value in config_file.items("functions"):
                try:
                    parsed = var.split("_")
                    if len(parsed) == 3:
                        f_type, s_num, cat = parsed
                        try:
                            num = int(s_num)
                        except ValueError:
                            continue
                        if f_type == "func":
                            max_sum_func = max(num, max_sum_func)
                            if cat == "name":
                                sum_names[num] = value
                            elif cat == "columns":
                                sum_columns[num] = value.split(",")
                            elif cat == "value":
                                sum_values[num] = value
                            elif cat == "aggr":
                                sum_aggrs[num] = value
                            elif cat == "type":
                                sum_types[num] = value
                except Exception as e:
                    print(e)
                    pass

            # process [groups]
            grp_names = {}
            grp_columns = {}
            grp_function_types = defaultdict(dict)
            grp_function_columns = defaultdict(dict)
            grp_filters = defaultdict(dict)
            grp_distinct = {}

            for var, value in config_file.items("groups"):
                parsed = var.split("_", 2)
                if (len(parsed) == 3 and parsed[0] == "group"):
                    num = parsed[1]
                    attr = parsed[2]

                    if attr.startswith("fnc"):
                        # group functions
                        f_parsed = attr.split("_")
                        if len(f_parsed) == 3:
                            _, f_num, f_attr = f_parsed
                            if f_attr == "type":
                                grp_function_types[num][f_num] = value
                            elif f_attr == "columns":
                                grp_function_columns[num][f_num] = value

                    elif attr.startswith("filter"):
                        f_parsed = attr.split("_")
                        if len(f_parsed) == 2:
                            try:
                                filt = parse_filter_text(value)
                            except ValueError:
                                pass
                            else:
                                print("---")
                                print(filt)
                                print("---")
                                _, f_num = f_parsed
                                grp_filters[num][f_num] = filt

                    elif attr == "name":
                        grp_names[num] = value

                    elif attr == "columns":
                        grp_columns[num] = value

                    elif attr == "distinct":
                        grp_distinct[num] = value == "True"

            self.args.groups = []
            for num in grp_names:
                # build group function list
                function_list = []
                for f_num in grp_function_types.get(num, {}):
                    f_type = grp_function_types[num][f_num]
                    f_columns = grp_function_columns[num].get(f_num, None)
                    if f_columns is not None:
                        fnc = func_types.get(f_type, None)
                        if fnc:
                            function_list.append(
                                (fnc, f_columns.strip().split(",")))

                name = grp_names.get(num)
                distinct = grp_distinct.get(num, False)
                columns = grp_columns.get(num, None)
                filters = grp_filters.get(num, {})
                filter_list = [filters[x] for x in sorted(filters.keys())]

                if columns is not None:
                    group = Group(name=name,
                                  columns=columns.split(","),
                                  functions=function_list,
                                  filters=filter_list,
                                  distinct=distinct)
                    self.args.groups.append(group)

            # process [summary]
            self.args.show_distinct = False
            sum_names = {}
            sum_columns = {}
            sum_function_types = defaultdict(dict)
            sum_function_columns = defaultdict(dict)

            for var, value in config_file.items("summary"):
                parsed = var.split("_", 2)
                if (len(parsed) == 3 and parsed[0] == "summary"):
                    num = parsed[1]
                    attr = parsed[2]
                    if attr.startswith("fnc"):
                        # summary functions
                        f_parsed = attr.split("_")
                        if len(f_parsed) == 3:
                            _, f_num, f_attr = f_parsed
                            if f_attr == "type":
                                sum_function_types[num][f_num] = value
                            elif f_attr == "columns":
                                sum_function_columns[num][f_num] = value
                    elif attr == "name":
                        sum_names[num] = value
                    elif attr == "columns":
                        sum_columns[num] = value
                elif (len(parsed) == 2 and parsed[-1] == "distinct"):
                    self.args.show_distinct = value == "True"

            for num in sum_names:
                name = sum_names.get(num)
                columns = sum_columns.get(num, None)
                function_list = []
                for f_num in sum_function_types.get(num, {}):
                    f_type = sum_function_types[num][f_num]
                    f_columns = sum_function_columns[num].get(f_num, None)
                    if f_columns is not None:
                        fnc = func_types.get(f_type, None)
                        if fnc:
                            if f_columns:
                                cols = f_columns.strip().split(",")
                            else:
                                cols = []
                            function_list.append((fnc, cols))

                if columns:
                    cols = columns.strip().split(",")
                else:
                    cols = []
                summary = Summary(name, cols, function_list)
            if not sum_names:
                summary = Summary("summary", [], [])
            self.args.summary_group.append(summary)

        # Use QSettings?
        if settings:
            column_properties = {}
            try:
                column_properties = settings.value("column_properties", {})
            finally:
                settings.setValue("column_properties", column_properties)
            if column_properties:
                current_properties = column_properties.get(self.args.corpus, {})
            else:
                current_properties = {}
            self.args.column_color = current_properties.get("colors", {})

            for x in [str(x) for x in settings.allKeys()]:
                if x.startswith("column_width_"):
                    _, _, column = x.partition("column_width_")
                    self.args.column_width[column] = settings.value(x, int)

cfg = None
settings = None


def save_configuration():
    """
    Saves the current configuration.

    Currently, two files are still used: an .ini text file that uses
    sections, and a QSettings file. Eventually, the two should be merged.
    """
    connection_name = cfg.current_connection.name
    config = UnicodeConfigParser()
    if os.path.exists(cfg.config_path):
        with codecs.open(cfg.config_path, "r", "utf-8") as input_file:
            try:
                config.read(input_file)
            except (IOError, TypeError):
                warnings.warn("Configuration file {} could not be read.".format(cfg.config_path))
    if "main" not in config.sections():
        config.add_section("main")
    config.set("main", "default_corpus", cfg.corpus)

    config.set("main", "query_mode", cfg.MODE)
    if cfg.query_list and cfg.save_query_string:
        config.set("main", "query_string",
                   encode_query_string("\n".join(cfg.query_list)))
    if cfg.input_path and cfg.save_query_file:
        config.set("main", "csv_file", cfg.input_path)
        config.set("main", "csv_separator", cfg.input_separator)
        config.set("main", "csv_column", cfg.query_column_number)
        config.set("main", "csv_has_header", cfg.file_has_headers)
        config.set("main", "csv_line_skip", cfg.skip_lines)
        config.set("main", "csv_quote_char", cfg.quote_char)
    config.set("main", "context_mode", cfg.context_mode)
    config.set("main", "output_case_sensitive", cfg.output_case_sensitive)
    config.set("main", "query_case_sensitive", cfg.query_case_sensitive)
    config.set("main", "regexp", cfg.regexp)
    config.set("main", "experimental", cfg.experimental)
    config.set("main", "drop_on_na", cfg.drop_on_na)
    config.set("main", "na_string", cfg.na_string)
    try:
        config.set("main", "output_to_lower", cfg.output_to_lower)
    except AttributeError:
        pass
    if cfg.xkcd is not None:
        config.set("main", "xkcd", cfg.xkcd)
    config.set("main", "query_cache_size", cfg.query_cache_size)
    config.set("main", "use_cache", bool(cfg.use_cache))

    if cfg.custom_installer_path:
        config.set("main", "custom_installer_path", cfg.custom_installer_path)
    config.set("main", "binary_path", cfg.binary_path)

    if "sql" not in config.sections():
        config.add_section("sql")

    config.set("sql", "active_configuration", connection_name)

    for i, name in enumerate(cfg.connections):
        connection = cfg.connections[name]
        if connection.db_type() == SQL_MYSQL:
            required_vars = ["name", "host", "port", "user", "password"]
        else:
            required_vars = ["name", "path"]

        config.set("sql", "config_{}_type".format(i), connection.db_type())

        for var in required_vars:
            config.set("sql",
                       "config_{}_{}".format(i, var),
                       getattr(connection, var))

    if cfg.selected_features:
        if "output" not in config.sections():
            config.add_section("output")
        for feature in cfg.selected_features:
            if feature.strip():
                config.set("output", feature, True)

    # store reference corpora:
    if "reference_corpora" not in config.sections():
        config.add_section("reference_corpora")
    for i, item in enumerate(cfg.reference_corpus.items()):
        config.set("reference_corpora",
                   "reference{}".format(i), ",".join(item))

    if "filter" not in config.sections():
        config.add_section("filter")

    for i, filt in enumerate(cfg.filter_list):
        config.set("filter", "filter_{}".format(i), str(filt))

    if "functions" not in config.sections():
        config.add_section("functions")

    if "groups" not in config.sections():
        config.add_section("groups")

    for i, grp in enumerate(cfg.groups):
        config.set("groups", "group_{}_name".format(i), grp.name)
        config.set("groups", "group_{}_distinct".format(i), str(grp.show_distinct))
        config.set("groups", "group_{}_columns".format(i),
                   ",".join(grp.columns))
        for j, (fnc, columns) in enumerate(grp.functions):
            config.set("groups", "group_{}_fnc_{}_type".format(i, j),
                       fnc._name)
            config.set("groups", "group_{}_fnc_{}_columns".format(i, j),
                       ",".join(columns))
        for j, filt in enumerate(grp.filters):
            config.set("groups", "group_{}_filter_{}".format(i, j),
                       str(filt))

    if "summary" not in config.sections():
        config.add_section("summary")

    config.set("summary", "summary_distinct", cfg.show_distinct)

    for i, grp in enumerate(cfg.summary_group):
        config.set("summary", "summary_{}_name".format(i), grp.name)
        config.set("summary", "summary_{}_columns".format(i),
                   ",".join(grp.columns))
        for j, (fnc, columns) in enumerate(grp.functions):
            config.set("summary", "summary_{}_fnc_{}_type".format(i, j),
                       fnc._name)
            config.set("summary", "summary_{}_fnc_{}_columns".format(i, j),
                       ",".join(columns))

    if cfg.table_links:
        if "links" not in config.sections():
            config.add_section("links")
        for i, link in enumerate(cfg.table_links[connection_name]):
            config.set("links",
                       "link{}".format(i+1),
                       '{},{}'.format(connection_name, link))

    if "context" not in config.sections():
        config.add_section("context")
    config.set("context", "context_mode", cfg.context_mode)
    config.set("context", "context_restrict", cfg.context_restrict)
    if cfg.context_left or cfg.context_right:
        config.set("context", "context_left", cfg.context_left)
        config.set("context", "context_right", cfg.context_right)
        config.set("context", "collo_left", cfg.collo_left)
        config.set("context", "collo_right", cfg.collo_right)

    if cfg.gui:
        for x in cfg.column_width:
            if (not x.startswith("coquery_invisible") and
                    cfg.column_width[x] and x):
                settings.setValue("column_width_{}".format(x), cfg.column_width[x])

        if "gui" not in config.sections():
            config.add_section("gui")

        if cfg.stopword_list:
            config.set("gui", "stopword_list",
                       encode_query_string("\n".join(cfg.stopword_list)))
        config.set("gui", "show_data_management", cfg.show_data_management)
        config.set("gui", "show_output_columns", cfg.show_output_columns)
        config.set("gui", "last_toolbox", cfg.last_toolbox)
        config.set("gui", "drop_duplicates", cfg.drop_duplicates)
        config.set("gui", "decimal_digits", cfg.digits)

        try:
            config.set("gui", "select_radio_query_file", cfg.select_radio_query_file)
        except AttributeError:
            config.set("gui", "select_radio_query_file", False)
        try:
            config.set("gui", "ask_on_quit", cfg.ask_on_quit)
        except AttributeError:
            config.set("gui", "ask_on_quit", True)
        try:
            config.set("gui", "word_wrap", bool(cfg.word_wrap))
        except AttributeError:
            config.set("gui", "word_wrap", False)
        try:
            config.set("gui", "save_query_file", cfg.save_query_file)
        except AttributeError:
            config.set("gui", "save_query_file", True)

        try:
            config.set("gui", "group_columns", ",".join(cfg.group_columns))
        except (NoOptionError, ValueError):
            pass
        try:
            config.set("gui", "query_file_path", cfg.query_file_path)
        except AttributeError:
            config.set("gui", "query_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "results_file_path", cfg.results_file_path)
        except AttributeError:
            config.set("gui", "results_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "output_file_path", cfg.output_file_path)
        except AttributeError:
            config.set("gui", "output_file_path", os.path.expanduser("~"))
        try:
            config.set("gui", "export_file_path", cfg.export_file_path)
        except AttributeError:
            config.set("gui", "export_file_path", os.path.expanduser("~"))
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
            config.set("gui", "corpus_table_source_path", cfg.corpus_table_source_path)
        except AttributeError:
            config.set("gui", "corpus_table_source_path", "")
        try:
            config.set("gui", "text_source_path", cfg.text_source_path)
        except AttributeError:
            config.set("gui", "text_source_path", os.path.expanduser("~"))
        try:
            config.set("gui", "number_of_tokens", cfg.number_of_tokens)
        except AttributeError:
            config.set("gui", "number_of_tokens", 0)
        try:
            config.set("gui", "sample_size", cfg.sample_size)
        except AttributeError:
            config.set("gui", "sample_size", 0)
        try:
            config.set("gui", "limit_matches", cfg.limit_matches)
        except AttributeError:
            config.set("gui", "limit_matches", False)
        try:
            config.set("gui", "sample_matches", cfg.sample_matches)
        except AttributeError:
            config.set("gui", "sample_matches", False)

        try:
            config.set("gui", "save_query_string", cfg.save_query_string)
        except AttributeError:
            config.set("gui", "save_query_string", True)

        if cfg.show_log_messages:
            config.set("gui", "show_log_messages", ",".join(cfg.show_log_messages))
        else:
            config.set("gui", "show_log_messages", None)

    with codecs.open(cfg.config_path, "w", "utf-8") as output_file:
        config.write(output_file)


def process_options(use_file=True):
    global cfg
    global settings
    if use_qt:
        try:
            from .gui.pyqt_compat import QtCore, CoqSettings
            settings = CoqSettings(
                        os.path.join(general.get_home_dir(), "coquery.ini"),
                        QtCore.QSettings.IniFormat)
        except IOError:
            settings = None
    else:
        settings = None

    options = Options()
    cfg = options.cfg
    options.get_options(use_file)
    if use_cachetools:
        from . import cache
        cfg.query_cache = cache.CoqQueryCache(cfg.use_cache)
    else:
        cfg.query_cache = None
    add_source_path(cfg.custom_installer_path)


def set_current_server(name):
    """
    Changes the current server paths. Also, update the currently available
    resources.

    Parameters
    ----------
    name : str
        The name of the MySQL configuration
    """
    global cfg
    cfg.current_connection = cfg.connections.get(name, None)
    cfg.current_connection.find_resources()

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

    if cfg.current_connection.db_type() == SQL_SQLITE:
        cfg.database_path = cfg.current_connection.path
        if not os.path.exists(cfg.database_path):
            os.makedirs(cfg.database_path)


def get_resource_of_database(db_name):
    """
    Get the resource that uses the database.
    """
    resources = cfg.current_connection.resources()
    for name in resources:
        resource, _, _ = resources[name]
        if resource.db_name == db_name:
            return resource
    return None


def get_available_resources(configuration):
    """
    Return a dictionary with the available corpus module resource classes
    as values, and the corpus module names as keys.

    This method scans the content of the sub-directory 'corpora' for valid
    corpus modules. This directory has additional subdirectories for each
    MySQL configuration. If a corpus module is found, the resource classes
    Resource and Corpus are retrieved from the module.

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
        (module.Resource, module.Corpus, module_name)
    """

    d = {}
    if configuration is None:
        return d

    # add corpus_path to sys.path so that modules can be imported from
    # that location:
    corpora_path = os.path.join(general.get_home_dir(),
                                "connections", configuration, "corpora")

    # create the directory if it doesn't exist yet:
    # cycle through the modules in the corpus path:
    for module_name in glob.glob(os.path.join(corpora_path, "*.py")):
        corpus_name, ext = os.path.splitext(os.path.basename(module_name))
        corpus_name = utf8(corpus_name)

        try:
            find = imp.find_module(corpus_name, [corpora_path])
            module = imp.load_module(corpus_name, *find)
        except Exception as e:
            s = "There is an error in corpus module '{}': {}\nThe corpus is not available for queries.".format(corpus_name, str(e))
            print(s)
            logging.warning(s)
        else:
            try:
                d[module.Resource.name] = (module.Resource,
                                           module.Corpus,
                                           module_name)
            except (AttributeError, ImportError) as e:
                print(e)
                warnings.warn("{} does not appear to be a valid corpus module.".format(corpus_name))
    return d


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
    s = s.replace("%%", "%")
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
        s = s.replace("%", "%%")
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
use_xlrd = has_module("xlrd")
use_nltk = has_module("nltk")
use_mysql = has_module("pymysql")
use_seaborn = has_module("seaborn")
use_pdfminer = has_module("pdfminer")
use_qt = has_module("PyQt5")
use_chardet = has_module("chardet")
use_tgt = has_module("tgt")
use_docx = has_module("docx")
use_odfpy = has_module("odf")
use_bs4 = has_module("bs4")
use_cachetools = has_module("cachetools")
use_statsmodels = has_module("statsmodels")
use_alsaaudio = has_module("alsaaudio")
use_winsound = has_module("winsound")


missing_modules = []
for mod in ["sqlalchemy", "pandas", "scipy", "PyQt5", "lxml"]:
    if not has_module(mod):
        missing_modules.append(mod)

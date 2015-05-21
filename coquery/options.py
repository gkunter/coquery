# -*- coding: utf-8 -*-
"""
FILENAME: options.py -- part of Coquery corpus query tool

This module handles command-line arguments and configuration files.

LICENSE:
Copyright (c) 2015 Gero Kunter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

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
import glob, imp

from defines import *
from errors import *

class Options(object):
    
    def __init__(self):
        try:
            self.base_path = os.path.dirname(__init__.__file__)
        except AttributeError:
            self.base_path = "."
        try:
            prog_name = __init__.NAME
            config_name = "%s.cfg" % __init__.NAME
            version = __init__.__version__
        except AttributeError:
            prog_name = "[unknown]"
            config_name = "__main__.cfg"            
            version = ""
        
        default_config_path = os.path.join(self.base_path, config_name)
        
        self.corpora_dict = {}

        for corpus in glob.glob(os.path.join(self.base_path, "corpora/*.py")):
            corpus_name, ext = os.path.splitext(os.path.basename(corpus))
            #module = imp.load_source(corpus_name, corpus)
            self.corpora_dict [corpus_name.upper()] = corpus
            
        self.parser = argparse.ArgumentParser(prog=prog_name, description=
"""This program provides an interface to linguistic corpora (currently only 
COCA). A query can either be specified at the command line using the -q 
argument, or queries can also be read from a text file using the -i 
argument. The results are either printed on the screen, our can be stored 
in a text file using the -o argument. The output of a query can either be 
all tokens found in the corpus (the default), or frequency of occurrence of 
that query (using the FREQ argument). Other arguments can be used to specify 
which additional information should be contained in the output, as well as 
the format of the input and output text files.

The texts to be queried can be filtered using the -t argument. The format 
of the argument is GENRE.[YEAR]. GENRE is any combination of SPOK, ACAD, 
NEWS, FIC, or MAG (use '|' to combine genres). YEAR can be a single year, 
a combination of years (using '|'), or a range of years (using '-'). 
Examples of valid text filters:

  -t ACAD|NEWS          texts from ACAD or NEWS, any year
  -t [1992-1999]        texts from between 1992 and 1999, any genre
  -t SPOK.[2011|2012]   texts from SPOK, years 2011 or 2012""", epilog=
"""Examples:

  coquery -q residualized FREQ
                        Query the frequency of the word 'residualized'
                        
  coquery -q "residualized scores" -p -c 5
                        Query all occurrences of the two-word sequence
                        'residualized scores'. Also print the part-of-speech
                        tags and a five-word context for each occurrence.
                        
  coquery -q "[happy|sad]" FREQ
                        Query the cummulative token frequency of the lemmas 
                        HAPPY and SAD.
                        
  coquery -q "[happy|sad]" FREQ -l
                        Query the token frequencies of the lemmas HAPPY and 
                        SAD.
  
  coquery -q "[happy|sad]" FREQ -O
                        Query the frequency of each word-form of the lemmas
                        HAPPY and SAD (i.e. 'happy', 'happier', 
                        'happiest', 'sad', 'sadder', 'saddest').
                        
  coquery -q "the [n*]" -c 5
                        Query all five-word contexts containing the sequence
                        '<the> NOUN'.
                        
  coquery -q "a|an|the [n*]" -c 5 -o noun_phrases.csv
                        Query all occurrences of the sequence ARTICLE NOUN,
                        together with the preceding and following five 
                        words. Write the results to the output file 
                        noun_phrases.csv.
                        
  coquery -i table.csv -n 3 --is ';' --os '\\t' -p -t -T [2000-2012] -T
                        Use the third column of the input file table.csv
                        (delimited by semicolon ';') as query strings. For
                        each query string, select texts from years 2000 up 
                        to 2012, and print all matches. Include text 
                        information and part-of-speech tags in the output.
                        Output columns are separated by tabulators.
                        
""", 
formatter_class=argparse.RawDescriptionHelpFormatter)
        
        self.parser.add_argument("--corpus", help="specify the corpus to use (default: COCA)", choices=self.corpora_dict.keys(), type=str)
        self.parser.add_argument ("MODE", help="determine the query mode (default: TOKEN)", choices=(QUERY_MODE_TOKENS, QUERY_MODE_FREQUENCIES, QUERY_MODE_DISTINCT, QUERY_MODE_STATISTICS), default=QUERY_MODE_DISTINCT, type=str, nargs="?")
        
        # General options:
        self.parser.add_argument("-o", "--outputfile", help="print results to OUTPUTFILE (default: print to console)", type=str, dest="output_path")
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-i", "--inputfile", help="read query strings from INPUTFILE", type=str, dest="input_path")
        group.add_argument("-q", "--query", help="use QUERY for search, ignoring any INPUTFILE", dest="query_list")
        self.parser.add_argument("-F", "--filter", help="use FILTER to query only a selection of texts", type=str, default="", dest="source_filter")
        self.parser.add_argument("--configuration", help="use CONF_FILE as the configuration file (default: use config file in the same location as program file, i.e. %s)" % default_config_path, default=default_config_path, dest="config_path")
        self.parser.add_argument("--db-name", help="use DB_NAME as the SQL database", type=str, dest="db_name")

        # File options:
        self.parser.add_argument("-a", "--append", help="append output to OUTPUTFILE, if specified (default: overwrite)", action="store_true")
        self.parser.add_argument("-k", "--skip", help="skip SKIP lines in INPUTFILE (default: 0)", type=int, default=0, dest="skip_lines")
        self.parser.add_argument("-H", "--header", help="use first row of INPUTFILE as headers", action="store_true", dest="file_has_headers")
        self.parser.add_argument("-n", "--number", help="use column NUMBER in INPUTFILE for queries", type=int, default=1, dest="query_column_number")
        self.parser.add_argument("--is", "--input-separator", help="use CHARACTER as separator in input CSV file",  default=',', metavar="CHARACTER", dest="input_separator")
        self.parser.add_argument("--os", "--output-separator", help="use CHARACTER as separator in output CSV file", default=',', metavar="CHARACTER", dest="output_separator")

        # Debug options:
        self.parser.add_argument("-d", "--dry-run", help="dry run (do not query, just log the query strings)", action="store_true")
        self.parser.add_argument("-v", "--verbose", help="produce a verbose output", action="store_true", dest="verbose")
        self.parser.add_argument("-V", "--super-verbose", help="be super-verbose (i.e. log function calls)", action="store_true")
        self.parser.add_argument("-E", "--explain", help="explain mySQL queries in log file", action="store_true", dest="explain_queries")
        self.parser.add_argument("--no-cache", help="attempts to circumwent the mySQL cache", action="store_true")
        self.parser.add_argument("--profile", help="deterministic profiling of Coquery", action="store_true")

        # Query options:
        self.parser.add_argument("-C", "--case", help="be case-sensitive (default: be COCA-compatible and ignore case)", action="store_true", dest="case_sensitive")
        self.parser.add_argument("-L", "--lemmatize-tokens", help="treat all tokens in query as lemma searches (default: be COCA-compatible and only do lemma searches if explicitly specified in query string)", action="store_true")
        self.parser.add_argument("-r", "--regexp", help="use regular expressions", action="store_true", dest="regexp")

        # Output options:
        self.parser.add_argument("--suppress-header", help="exclude column header from the output (default: include)", action="store_false", dest="show_header")
        self.parser.add_argument("-Q", "--show-query", help="include query string in the output", action="store_true", dest="show_query")
        self.parser.add_argument("-O", "--orth", help="include orthographic word in the output", action="store_true", dest="show_orth")
        #self.parser.add_argument("-c", "--context", help="include context with SPAN words to the left and the right", default=0, type=int, dest="context_span")
        
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-c", "--context", help="include context with N words to the left and the right as one text string", default=0, type=int, dest="context_span")
        group.add_argument("--context_columns", help="include context with N words to the left and the right in separate columns", default=0, type=int, dest="context_columns")
        group.add_argument("--sentence", help="include the sentence of the token as a context (not supported by all corpora)", dest="context_sentence", action="store_true")


        self.parser.add_argument("--number-of-tokens", help="output up to NUMBER different tokens (default: all tokens)", default=0, type=int, dest="number_of_tokens", metavar="NUMBER")
        self.parser.add_argument("-l", "--lemma", help="include a lemma column for each token in the output", action="store_true", dest="show_lemma")
        self.parser.add_argument("-p", "--POS", help="include a part-of-speech column for each token in the output", action="store_true", dest="show_pos")
        self.parser.add_argument("-s", "--source", help="include the source information column specified as an argument in the output (use ALL for all columns)", action="append", dest="source_columns")
        self.parser.add_argument("-u", "--unique-id", help="include the token id for the first token matching the output", action="store_true", dest="show_id")
        self.parser.add_argument("-P", "--include-parameters", help="include the parameter string in the output", action="store_true", dest="show_parameters")
        self.parser.add_argument("-f", "--include-filter", help="include the filter string in the output", action="store_true", dest="show_filter")
        self.parser.add_argument("--phon", help="include phonological transcriptions in the output", action="store_true", dest="show_phon")
        self.parser.add_argument("--filename", help="include filename information in the output", action="store_true", dest="show_filename")
        self.parser.add_argument("--speaker", help="include speaker information in the output", action="store_true", dest="show_speaker")
        self.parser.add_argument("--time", help="include timing information in the output", action="store_true", dest="show_time")
        self.parser.add_argument("--freq-label", help="use this label in the heading line of the output", default="Freq", type=str, dest="freq_label")
 
        # COCA compatibility options
        self.parser.add_argument("--exact-pos-tags", help="part-of-speech tags must match exactly the label used in the query string (default: be COCA-compatible and match any part-of-speech tag that starts with the given label)", action="store_true", dest="exact_pos_tags")
        self.parser.add_argument("-@", "--use-pos-diacritics", help="use undocumented characters '@' and '%%' in queries using part-of-speech tags (default: be COCA-compatible and ignore these characters in part-of-speech tags)", action="store_true", dest="ignore_pos_chars")
 
        try:
            self.args, unknown = self.parser.parse_known_args()
            if unknown:
                raise UnknownArgumentError(unknown)
        except Exception as e:
            raise e

        self.args.show_text = self.args.source_columns != []

        vars(self.args) ["program_location"] = self.base_path
        vars(self.args) ["version"] = version
        vars(self.args) ["parameter_string"] = " ".join(sys.argv [1:])
        vars(self.args) ["corpora"] = self.corpora_dict

        self.read_configuration()

        # make sure that a command query consisting of one string is still
        # stored as a list:
        if "query_list" in vars(self.args):
            if type(vars(self.args) ["query_list"]) is not list:
                if vars(self.args)["query_list"]:
                    vars(self.args) ["query_list"] = [vars(self.args) ["query_list"]]

        logger.info("Command line parameters: " + self.args.parameter_string)
        

    def read_configuration(self):
        # defaults:
        db_name = None
        db_user = "mysql"
        db_password = "mysql"
        db_port = 3306
        db_host = "localhost"
        if os.path.exists(self.args.config_path):
            logger.info("Using configuration file %s" % self.args.config_path)
            config_file = configparser.ConfigParser()
            config_file.read(self.args.config_path)
            
            if "main" in config_file.sections():
                if self.args.corpus == None:
                    try:
                        default_corpus = config_file.get("main", "default_corpus")
                    except configparser.NoOptionError:
                        default_corpus = self.corpora_dict.keys()[0]
                        logger.warning("No default corpus specified in config file. Using %s." % default_corpus)                
                    vars(self.args) ["corpus"] = default_corpus

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

            current_corpus = self.args.corpus.lower()
            if current_corpus not in config_file.sections():
                logger.warning("No [%s] section found in config file." % self.args.corpus)
            else:
                try:
                    db_name = config_file.get(current_corpus, "db_name")
                except configparser.NoOptionError:
                    logger.warning("Option 'db_name' not found in section %s of config file. Using default." % current_corpus)
        else:
            logger.warning("Configuration file %s not found, using defaults." % self.args.config_path)

        if db_name:
            vars(self.args) ["db_name"] = db_name
        vars(self.args) ["db_user"] = db_user
        vars(self.args) ["db_password"] = db_password
        vars(self.args) ["db_port"] = db_port
        vars(self.args) ["db_host"] = db_host
    
cfg = None

def process_options():
    global cfg
    cfg = Options().args

logger = logging.getLogger(__init__.NAME)


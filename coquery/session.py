# -*- coding: utf-8 -*-
"""
session.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import time, datetime
import fileinput
import codecs
import logging
import collections

import pandas as pd

import __init__
import options
from errors import *
from corpus import *
from defines import *
import queries
import tokens

class Session(object):
    def __init__(self):
        self.header = None
        self.max_number_of_input_columns = 0
        self.query_list = []
        self.requested_fields = []
        options.cfg.query_label = ""
            
        # load current corpus module depending on the value of options.cfg.corpus,
        # i.e. the corpus specified as an argumment:        
        ResourceClass, CorpusClass, LexiconClass, Path = get_available_resources(options.cfg.current_server)[options.cfg.corpus]
        
        current_lexicon = LexiconClass()
        current_corpus = CorpusClass()
        current_resource = ResourceClass(current_lexicon, current_corpus)

        self.Corpus = current_corpus
        self.Corpus.lexicon = current_lexicon
        self.Corpus.resource = current_resource
        
        self.Lexicon = current_lexicon
        self.Lexicon.corpus = current_corpus
        self.Lexicon.resource= current_resource
        
        self.Resource = current_resource

        self.show_header = options.cfg.show_header

        # select the query class depending on the value of options.cfg.MODE, i.e.
        # which mode has been specified in the options:
        if options.cfg.MODE == QUERY_MODE_TOKENS:
            self.query_type = queries.TokenQuery
        elif options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            self.query_type = queries.FrequencyQuery
        elif options.cfg.MODE == QUERY_MODE_DISTINCT:
            self.query_type = queries.DistinctQuery
        elif options.cfg.MODE == QUERY_MODE_COLLOCATIONS:
            self.query_type = queries.CollocationQuery
        elif options.cfg.MODE == QUERY_MODE_STATISTICS:
            self.query_type = queries.StatisticsQuery

        logger.info("Corpus: %s" % options.cfg.corpus)
        
        self.data_table = pd.DataFrame()
        self.output_object = None
        self.output_order = []
        self.header_shown = False
        self.input_columns = []

        # verify filter list:
        new_list = []
        for filt in options.cfg.filter_list:
            if isinstance(filt, queries.QueryFilter):
                new_list.append(filt)
            else:
                new_filt = queries.QueryFilter()
                new_filt.resource = self.Resource
                new_filt.text = filt
                new_list.append(new_filt)
        self.filter_list = new_list
        self.Resource.filter_list = new_list
        
    def get_max_token_count(self):
        """
        Return the maximal number of tokens that may be produced by the 
        queries from this session.
        """
        maximum = 0
        for query in self.query_list:
            maximum = max(maximum, query.get_max_tokens())
        return maximum

    def open_output_file(self):
        if options.cfg.gui:
            self.output_object = pd.DataFrame()
        else:
            if not options.cfg.output_path:
                self.output_object = sys.stdout
            else:
                if options.cfg.append:
                    file_mode = "a"
                else:
                    file_mode = "w"
                
                self.output_object = codecs.open(options.cfg.output_path, file_mode, encoding=options.cfg.output_encoding)
    
    def run_queries(self):
        """ Process all queries. For each query, go through the entries in 
        query_list() and yield the results for that subquery. Then, write
        all results to the output file. """

        self.start_time = datetime.datetime.now()
        self.end_time = None
        if options.cfg.gui:
            self.storage_created = False
        
        self.data_table = pd.DataFrame()
        self.quantified_number_labels = []
        for current_query in self.query_list:
            if not self.quantified_number_labels:
                self.quantified_number_labels = [current_query.get_token_numbering(i) for i in range(self.get_max_token_count())]
            start_time = time.time()
            logger.info("Start query: '{}'".format(current_query.query_string))
            current_query.run()
            self.data_table = current_query.append_results(self.data_table)
            logger.info("Query executed (%.3f seconds)" % (time.time() - start_time))

        self.end_time = datetime.datetime.now()
        self.data_table.index = range(1, len(self.data_table.index) + 1)
        
        self.aggregate_data()

        if not options.cfg.gui:
            if not options.cfg.output_path:
                output_file = sys.stdout
            else:
                if options.cfg.append:
                    file_mode = "a"
                else:
                    file_mode = "w"
                
                output_file = codecs.open(
                    options.cfg.output_path, 
                    file_mode, 
                    encoding=options.cfg.output_encoding)

            self.output_object.to_csv(
                output_file,
                header = [self.translate_header(x) for x in self.output_object.columns.values], 
                sep=options.cfg.output_separator,
                encoding="utf-8",
                float_format = "%.{}f".format(options.cfg.digits),
                index=False)

    def aggregate_data(self):
        """
        Apply the aggegate function from the current query type to the 
        data table produced in this session.
        """
        self.output_object = self.query_type.aggregate_it(self.data_table, self.Corpus)
        self.output_object.fillna("", inplace=True)
        self.output_object.index = range(1, len(self.output_object.index) + 1)

    def translate_header(self, header, ignore_alias=False):
        """ 
        Return a string that contains the display name for the header 
        string. 
        
        Translation removes the 'coq_' prefix and any numerical suffix, 
        determines the resource feature from the remaining string, translates 
        it to its display name, and returns the display name together with 
        the numerical suffix attached.
        
        Parameters
        ----------
        header : string
            The resource string that is to be translated
        ignore_alias : bool
            True if user names should be ignored, and False if user names 
            should be used.
            
        Returns
        -------
        s : string
            The display name of the resource string
        """
        
        # If the column has been renamed by the user, that name has top
        # priority, unless ignore_alias is used:
        if not ignore_alias and header in options.cfg.column_names:
            return options.cfg.column_names[header]
        
        # Retain the column header if the query string was from an input file
        if header == "coquery_query_string" and options.cfg.query_label:
            return options.cfg.query_label

        # treat frequency columns:
        if header == "coq_frequency":
            if options.cfg.query_label:
                return "{}({})".format(COLUMN_NAMES[header], options.cfg.query_label)
            else:
                return "{}".format(COLUMN_NAMES[header])
        
        # other features:
        if header in COLUMN_NAMES:
            return COLUMN_NAMES[header]
        
        # strip coq_ prefix:
        if header.startswith("coq_"):
            header = header.partition("coq_")[2]

        rc_feature, _, number = header.rpartition("_")
        
        # If there is only one query token, number is set to "" so that no
        # number suffix is added to the labels in this case:
        if self.get_max_token_count() == 1:
            number = ""

        # special treatment of query tokens:
        if rc_feature == "coquery_query_token":
            try:
                number = self.quantified_number_labels[int(number) - 1]
            except ValueError:
                pass
            return "{}{}".format(COLUMN_NAMES[rc_feature], number)
        
        # special treatment of lexicon freatures:
        if rc_feature in [x for x, _ in self.Resource.get_lexicon_features()]:
            try:
                number = self.quantified_number_labels[int(number) - 1]
            except ValueError:
                pass
            return "{}{}".format(self.Resource.__getattribute__(str(rc_feature)), number)

        # treat any other feature that is provided by the corpus:
        try:
            return "{}".format(self.Resource.__getattribute__(str(rc_feature)))
        except AttributeError:
            pass

        # treat linked columns:
        if "." in rc_feature:
            pass

        # treat functions:
        if rc_feature.startswith("func_"):
            func_counter = collections.Counter()
            for res, _, label in options.cfg.selected_functions:
                resource = res.rpartition(".")[-1]
                func_counter[resource] += 1
                fc = func_counter[resource]
                
                new_name = "func_{}_{}".format(resource, fc)
                if new_name == rc_feature:
                    column_name = self.Resource.__getattribute__(str(resource))
                    function_label = label
                    break
            else:
                column_name = resource
                function_label = rc_feature
            try:
                number = self.quantified_number_labels[int(number) - 1]
            except ValueError:
                pass
            return str(function_label).replace(column_name, "{}{}".format(column_name, number))

        # other features:
        if rc_feature in COLUMN_NAMES:
            try:
                number = self.quantified_number_labels[int(number) - 1]
            except ValueError:
                pass
            return "{}{}".format(COLUMN_NAMES[rc_feature], number)

        return header

class StatisticsSession(Session):
    def __init__(self):
        super(StatisticsSession, self).__init__()
        self.query_list.append(queries.StatisticsQuery(self.Corpus, self))
        self.header = ["Variable", "Value"]
        self.output_order = self.header

class SessionCommandLine(Session):
    def __init__(self):
        super(SessionCommandLine, self).__init__()
        if len(options.cfg.query_list) > 1:
            logger.info("{} queries".format(len(options.cfg.query_list)))
        for query_string in options.cfg.query_list:
            if self.query_type:
                new_query = self.query_type(query_string, self, tokens.COCAToken)
            else: 
                raise CorpusUnavailableQueryTypeError(options.cfg.corpus, options.cfg.MODE)
            self.query_list.append(new_query)
        self.max_number_of_input_columns = 0

class SessionInputFile(Session):
    def __init__(self):
        super(SessionInputFile, self).__init__()
        with open(options.cfg.input_path, "rt") as InputFile:
            read_lines = 0
            
            try:
                input_file = pd.read_table(
                    filepath_or_buffer=InputFile,
                    header=0 if options.cfg.file_has_headers else None,
                    sep=options.cfg.input_separator,
                    quotechar=options.cfg.quote_char,
                    encoding=options.cfg.input_encoding,
                    na_filter=False)
            except ValueError:
                raise EmptyInputFileError(InputFile)
            if self.header == None:
                if options.cfg.file_has_headers:
                    self.header = input_file.columns.values.tolist()
                else:
                    self.header = ["X{}".format(i+1) for i, _ in enumerate(input_file.columns)]
                    input_file.columns = self.header
            options.cfg.query_label = self.header.pop(options.cfg.query_column_number - 1)
            for current_line in input_file.iterrows():
                current_line = list(current_line[1])
                if options.cfg.query_column_number > len(current_line):
                    raise IllegalArgumentError("Column number for queries too big (-n %s)" % options.cfg.query_column_number)
                
                if read_lines >= options.cfg.skip_lines:
                    try:
                        query_string = current_line.pop(options.cfg.query_column_number - 1)
                    except AttributeError:
                        continue
                    new_query = self.query_type(query_string, self, tokens.COCAToken)
                    new_query.input_frame = pd.DataFrame(
                        [current_line], columns=self.header)
                    self.query_list.append(new_query)
                self.max_number_of_input_columns = max(len(current_line), self.max_number_of_input_columns)
                read_lines += 1
            self.input_columns = ["coq_{}".format(x) for x in self.header]
            

        logger.info("Input file: {} ({} {})".format(options.cfg.input_path, len(self.query_list), "query" if len(self.query_list) == 1 else "queries"))
        if options.cfg.skip_lines:
            logger.info("Skipped first {}.".format("query" if options.cfg.skip_lines == 1 else "{} queries".format(options.cfg.skip_lines)))
            

class SessionStdIn(Session):
    def __init__(self):
        super(SessionStdIn, self).__init__()

        for current_string in fileinput.input("-"):
            read_lines = 0
            current_line = [x.strip() for x in current_string.split(options.cfg.input_separator)]
            if current_line:
                if options.cfg.file_has_headers and not self.header:
                    self.header = current_line
                else:
                    if read_lines >= options.cfg.skip_lines:
                        query_string = current_line.pop(options.cfg.query_column_number - 1)
                        new_query = self.query_type(query_string, self, tokens.COCAToken)
                        self.query_list.append(new_query)
                self.max_number_of_input_columns = max(len(current_line), self.max_number_of_input_columns)
            read_lines += 1
        logger.info("Reading standard input ({} {})".format(len(self.query_list), "query" if len(self.query_list) == 1 else "queries"))            
        if options.cfg.skip_lines:
            logger.info("Skipping first %s %s." % (options.cfg.skip_lines, "query" if options.cfg.skip_lines == 1 else "queries"))
    
logger = logging.getLogger(__init__.NAME)
    
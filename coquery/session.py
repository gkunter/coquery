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
        ResourceClass, CorpusClass, LexiconClass, Path = get_available_resources()[options.cfg.corpus]
        current_resource = ResourceClass()
        current_resource.connect_to_database()
        self.Corpus  = CorpusClass(LexiconClass(current_resource), current_resource)

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

        if any([x.startswith("frequency_") for x in options.cfg.selected_features]):
            try:
                options.cfg.selected_features.pop(options.cfg.selected_features.index("frequency_absolute_frequency"))
            except ValueError:
                pass
            self.query_type = queries.FrequencyQuery
            
        logger.info("Corpus: %s" % options.cfg.corpus)
        
        self.data_table = pd.DataFrame()
        self.output_object = None
        self.output_order = []
        self.header_shown = False
        self.input_columns = []
        
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

        # verify filter list:
        new_list = []
        for filt in options.cfg.filter_list:
            if isinstance(filt, queries.QueryFilter):
                new_list.append(filt)
            else:
                new_filt = queries.QueryFilter()
                new_filt.resource = self.Corpus.resource
                new_filt.text = filt
                new_list.append(new_filt)
        options.cfg.filter_list = new_list

        self.start_time = datetime.datetime.now()
        self.end_time = None
        if options.cfg.gui:
            self.storage_created = False
        
        self.open_output_file()

        for current_query in self.query_list:
            self.literal_query_string = current_query.query_string
            start_time = time.time()
            logger.info("Start query: '{}'".format(current_query.query_string))
            for sub_query in current_query.query_list:
                current_query._current_number_of_tokens = len(sub_query)
                current_query.Results = self.Corpus.yield_query_results(current_query, sub_query)
                current_query.write_results(self.output_object)
            logger.info("Query executed (%.3f seconds)" % (time.time() - start_time))
        
        self.end_time = datetime.datetime.now()
        
        if not options.cfg.gui:
            self.output_object.close()
        else:
            self.output_object = self.query_type.aggregate_it(self.data_table, self.Corpus)
            self.output_object.fillna("", inplace=True)
            self.output_object.reset_index(drop=True, inplace=True)

class StatisticsSession(Session):
    def __init__(self):
        super(StatisticsSession, self).__init__()
        self.query_list.append(queries.StatisticsQuery(self.Corpus, self))
        self.header = ["Variable", "Value"]
        self.output_order = self.header

class SessionCommandLine(Session):
    def __init__(self):
        super(SessionCommandLine, self).__init__()
        logger.info("{} queries".format(len(options.cfg.query_list)) if len(options.cfg.query_list) > 1 else "Single query")
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
        input_header = None
        with open(options.cfg.input_path, "rt") as InputFile:
            read_lines = 0
            
            input_file = pd.read_table(
                filepath_or_buffer=InputFile,
                sep=options.cfg.input_separator,
                quotechar=options.cfg.quote_char,
                encoding=options.cfg.input_encoding,
                na_filter=False)

            if options.cfg.file_has_headers and self.header == None:
                self.header = input_file.columns.values.tolist()
                input_header = self.header
                options.cfg.query_label = input_header.pop(options.cfg.query_column_number - 1)
            for current_line in input_file.iterrows():
                current_line = list(current_line[1])
                if options.cfg.query_column_number > len(current_line):
                    raise IllegalArgumentError("Column number for queries too big (-n %s)" % options.cfg.query_column_number)
                
                if read_lines >= options.cfg.skip_lines:
                    query_string = current_line.pop(options.cfg.query_column_number - 1)
                    new_query = self.query_type(query_string, self, tokens.COCAToken)
                    new_query.input_frame = pd.DataFrame(
                        [current_line], columns=input_header)
                    self.query_list.append(new_query)
                self.max_number_of_input_columns = max(len(current_line), self.max_number_of_input_columns)
                read_lines += 1
            
            self.input_columns = ["coq_{}".format(x) for x in input_header]
            

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
    
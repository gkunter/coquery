# -*- coding: utf-8 -*-
""" session.py -- part of Coquery corpus query tool

This module defines the Session class. """

from __future__ import print_function
from __future__ import unicode_literals

import sys
import copy
import time, datetime
import fileinput
import codecs

import pandas as pd

import __init__
import options
from errors import *
from corpus import *
from defines import *

import queries
import tokens

import logging

class Session(object):
    def __init__(self):
        self.header = None
        self.max_number_of_input_columns = 0
        self.max_number_of_tokens = 0
        self.query_list = []
        self.requested_fields = []
            
        # load current corpus module depending on the value of options.cfg.corpus,
        # i.e. the corpus specified as an argumment:        
        ResourceClass, CorpusClass, LexiconClass, Path = get_available_resources()[options.cfg.corpus]
        current_resource = ResourceClass()
        current_resource.connect_to_database()
        self.Corpus  = CorpusClass(LexiconClass(current_resource), current_resource)

        self.show_header = options.cfg.show_header

        # select the query class depending on the value of options.cfg.MODE, i.e.
        # which mode has been specified in the options:
        if options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            self.query_type = queries.FrequencyQuery
        elif options.cfg.MODE == QUERY_MODE_TOKENS:
            self.query_type = queries.TokenQuery
        elif options.cfg.MODE == QUERY_MODE_DISTINCT:
            self.query_type = queries.CorpusQuery
        elif options.cfg.MODE == QUERY_MODE_COLLOCATIONS:
            self.query_type = queries.CollocationQuery
            
        logger.info("Corpus: %s" % options.cfg.corpus)
        self.output_object = None
        self.output_order = []
        self.header_shown = False
        self.input_columns = []

    def expand_header(self):
        """
        Session.expand_header() ensures that the list Session.header 
        contains all column labels that are required for the current 
        session. The set of labels depends on the command line flags. For 
        example, -p adds one or more numbered part-of-speech labels to the 
        header. The number of labels depends on the maximum number of query 
        tokens in this session. """

        return []

        if options.cfg.MODE == QUERY_MODE_COLLOCATIONS:
            self.header = ["coquery_query_string"]
            lexicon_features = self.Corpus.resource.get_lexicon_features()
            for rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in lexicon_features]:
                    self.header.append("coq_collocate_{}".format(rc_feature))
            self.header.append("coq_frequency")
            self.header.append("coq_collocate_frequency")
            self.header.append("coq_collocate_frequency_left")
            self.header.append("coq_collocate_frequency_right")
            self.header.append("coq_mutual_information")
            self.header.append("coq_conditional_probability")
            self.header.append("coquery_invisible_corpus_id")
            self.header.append("coquery_invisible_origin_id")
            self.header.append("coquery_invisible_number_of_tokens")
            return
            
        corpus_features = [x for x, _ in self.Corpus.resource.get_corpus_features() if x in options.cfg.selected_features]
        lexicon_features = [x for x, _ in self.Corpus.resource.get_lexicon_features() if x in options.cfg.selected_features]
        corpus_names = [x for _, x in self.Corpus.resource.get_corpus_features() if _ in options.cfg.selected_features]
        lexicon_names = [x for _, x in self.Corpus.resource.get_lexicon_features() if _ in options.cfg.selected_features]
        h = []
        for rc_feature in self.Corpus.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features and rc_feature in lexicon_features:
                h += ["{}{}".format(lexicon_names[lexicon_features.index(rc_feature)], i+1) for i in range(self.max_number_of_tokens)]
        for rc_feature in self.Corpus.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features and rc_feature in corpus_features:
                h += [corpus_names[corpus_features.index(rc_feature)]]
        for rc_feature in options.cfg.selected_features:
            if rc_feature.startswith("coquery"):
                name = self.Corpus.resource.__getattribute__(rc_feature)
                h.append(name)
        self.header = h
        if options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            self.header.append (options.cfg.freq_label)
        if options.cfg.context_left:
            self.header.append("Left_context")
        if options.cfg.context_right:
            self.header.append("Right_context")
        # if a GUI is used, include source features so the entries in the
        # result table can be made clickable to show the context:
        if options.cfg.MODE != QUERY_MODE_FREQUENCIES and (options.cfg.gui):
            self.header.append("coq_invisible_token_id")
            self.header.append("coq_invisible_source_id")
            self.header.append("coq_invisible_number_of_tokens")

    def get_expected_column_number(self, max_number_of_tokens):
        """ Return the expected number of columns, based on the maximum 
        number of tokens in all query strings from the current session. The 
        number is calculated by multiplying the maximum number of tokens by 
        the number of lexicon features that were selected, and adding the 
        number of selected corpus features."""
        corpus_features = [x for x, _ in self.Corpus.resource.get_corpus_features() if x in options.cfg.selected_features]
        lexicon_features = [x for x, _ in self.Corpus.resource.get_lexicon_features() if x in options.cfg.selected_features]
        length = len(corpus_features) + max_number_of_tokens * len(lexicon_features)
        if options.cfg.context_columns:
            length += options.cfg.context_left
            length += options.cfg.context_right
            length += max_number_of_tokens
        elif options.cfg.context_span:
            length += 1
        if options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            length += 1
        for rc_feature in options.cfg.selected_features:
            if rc_feature.startswith("coquery"):
                length += 1
        # if a GUI is used, include source features so the entries in the
        # result table can be made clickable to show the context:
        if options.cfg.MODE != QUERY_MODE_FREQUENCIES and (options.cfg.gui):
            length += 3
        return length

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
        self.expand_header()
        self._queries = {}
        self._results = {}

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
            if len(current_query.query_list) > 1:
                start_time = time.time()
                any_result = False
                for sub_query in current_query.query_list:
                    query_results = []
                    for current_result in self.Corpus.yield_query_results(sub_query):
                        query_results.append(current_result)
                    sub_query.Results = query_results
                    if query_results:
                        any_result = True
                        sub_query.write_results(self.output_object)
                if not any_result:
                    current_query.write_results(self.output_object)
                logger.info("Query executed (%.3f seconds)" % (time.time() - start_time))
                
            else:
                start_time = time.time()
                logger.info("Start query: '{}'".format(current_query))

                if current_query.tokens:
                    current_query.Results = self.Corpus.yield_query_results(current_query)
                start_time = time.time()
                current_query.write_results(self.output_object)
                logger.info("Query executed (%.3f seconds)" % (time.time() - start_time))
        self.end_time = datetime.datetime.now()
        if not options.cfg.gui:
            self.output_object.close()
        else:
            self.output_object.index = range(1, 1 + len(self.output_object))

class StatisticsSession(Session):
    def __init__(self):
        super(StatisticsSession, self).__init__()
        if self.Corpus.provides_feature(CORP_STATISTICS):
            self.query_list.append(queries.StatisticsQuery(self.Corpus, self))
        else:
            raise QueryModeError(options.cfg.corpus, options.cfg.MODE)
        self.header = ["Variable", "Value"]
        self.output_order = self.header
    
    def expand_header(self):
        self.header = ["Variable", "Value"]
        self.output_odrer = self.header

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
            self.max_number_of_tokens = max(new_query.max_number_of_tokens, self.max_number_of_tokens)
        self.max_number_of_input_columns = 0

class SessionInputFile(Session):
    def __init__(self):
        super(SessionInputFile, self).__init__()
        input_header = None
        with open(options.cfg.input_path, "rt") as InputFile:
            read_lines = 0
            for current_line in UnicodeReader(InputFile, delimiter=options.cfg.input_separator, encoding=options.cfg.input_encoding):
                if current_line:
                    if options.cfg.query_column_number > len(current_line):
                        raise IllegalArgumentError("Column number for queries too big (-n %s)" % options.cfg.query_column_number)
                    
                    if options.cfg.file_has_headers and self.header == None:
                        self.header = copy.copy(current_line)
                        input_header = self.header
                        input_header.pop(options.cfg.query_column_number - 1)
                        
                        self.input_columns = ["coq_{}".format(x) for x in input_header]
                        
                    else:
                        if read_lines >= options.cfg.skip_lines:
                            query_string = current_line.pop(options.cfg.query_column_number - 1)
                            new_query = self.query_type(query_string, self, tokens.COCAToken)
                            new_query.InputLine = copy.copy(current_line)
                            new_query.input_frame = pd.DataFrame(
                                [current_line], columns=input_header)
                            self.query_list.append(new_query)
                            self.max_number_of_tokens = max(new_query.max_number_of_tokens, self.max_number_of_tokens)
                    self.max_number_of_input_columns = max(len(current_line), self.max_number_of_input_columns)
                read_lines += 1
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
                        new_query.InputLine = copy.copy(current_line)
                        self.query_list.append(new_query)
                        self.max_number_of_tokens = max(new_query.max_number_of_tokens, self.max_number_of_tokens)
                self.max_number_of_input_columns = max(len(current_line), self.max_number_of_input_columns)
            read_lines += 1
        logger.info("Reading standard input ({} {})".format(len(self.query_list), "query" if len(self.query_list) == 1 else "queries"))            
        if options.cfg.skip_lines:
            logger.info("Skipping first %s %s." % (options.cfg.skip_lines, "query" if options.cfg.skip_lines == 1 else "queries"))
    
logger = logging.getLogger(__init__.NAME)
    
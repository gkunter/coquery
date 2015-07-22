# -*- coding: utf-8 -*-
"""
FILENAME: session.py -- part of Coquery corpus query tool

This module defines the Session class.

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

from __future__ import print_function
from __future__ import unicode_literals

import sys
import copy
import time, datetime
import fileinput

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
        ResourceClass, CorpusClass, LexiconClass, Path = resource_list.get_available_resources()[options.cfg.corpus]
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
            self.query_type = queries.DistinctQuery
            
        if options.cfg.show_orth:
            self.requested_fields.append(LEX_ORTH)        
        if options.cfg.show_lemma:
            self.requested_fields.append(LEX_LEMMA)
        if options.cfg.show_pos:
            self.requested_fields.append(LEX_POS)
        try:
            if options.cfg.show_phon:
                self.requested_fields.append(LEX_PHON)
        except AttributeError:
            pass
        if options.cfg.show_source:
            self.requested_fields.append(CORP_SOURCE)
        if options.cfg.show_filename:
            self.requested_fields.append(CORP_FILENAME)
        if options.cfg.show_speaker:
            self.requested_fields.append(CORP_SPEAKER)
        if options.cfg.show_time:
            self.requested_fields.append(CORP_TIMING)
        if options.cfg.context_span or options.cfg.context_columns or options.cfg.context_sentence:
            self.requested_fields.append(CORP_CONTEXT)
            
        self.output_fields = set([x for x in self.requested_fields if self.Corpus.provides_feature(x)])

        logger.info("Corpus: %s" % options.cfg.corpus)
        self.output_file = None

    def expand_header(self):
        """
        Session.expand_header() ensures that the list Session.header 
        contains all column labels that are required for the current 
        session. The set of labels depends on the command line flags. For 
        example, -p adds one or more numbered part-of-speech labels to the 
        header. The number of labels depends on the maximum number of query 
        tokens in this session. """
    
        if not self.header:
            # If there is no header yet (e.g. because the input file did not
            # contain headsers), create a new header with column labels 
            # 'Inputx' for the maximum number of input columns available, 
            # with x corresponding to the number of the column.
            # The column containing the query string is labelled 'Query'.
            self.header = ["Input%s" % (x+1) for x in range(self.max_number_of_input_columns - 1)]
            if options.cfg.show_query:
                self.header.insert (options.cfg.query_column_number - 1, "Query")
        
        if options.cfg.show_parameters:
            self.header.append ("Parameters")
            
        if options.cfg.show_filter:
            self.header.append ("Filter")
        
        if options.cfg.show_id:
            self.header.append("ID")
            
        if options.cfg.show_orth:
            self.header += ["W%s" % (x+1) for x in range(self.max_number_of_tokens)]

        if options.cfg.show_phon and self.Corpus.provides_feature(LEX_PHON):
            self.header += ["W_Phon%s" % (x+1) for x in range(self.max_number_of_tokens)]
            
        if options.cfg.show_lemma and self.Corpus.provides_feature(LEX_LEMMA):
            self.header += ["L%s" % (x + 1) for x in range(self.max_number_of_tokens)]
            
        if options.cfg.show_pos and self.Corpus.provides_feature(LEX_POS):
            self.header += ["PoS%s" % (x + 1) for x in range(self.max_number_of_tokens)]
        
        if options.cfg.show_source and self.Corpus.provides_feature(CORP_SOURCE):
            self.header += self.Corpus.get_source_info_header()
        if options.cfg.show_speaker and self.Corpus.provides_feature(CORP_SPEAKER):
            self.header += self.Corpus.get_speaker_info_header()
        if options.cfg.show_filename and self.Corpus.provides_feature(CORP_FILENAME):
            self.header += self.Corpus.get_file_info_header()
        if options.cfg.show_time and self.Corpus.provides_feature(CORP_TIMING):
            self.header += self.Corpus.get_time_info_header()
            
        if (options.cfg.context_span or options.cfg.context_columns) and self.Corpus.provides_feature(CORP_CONTEXT):
            self.header += self.Corpus.get_context_header(self.max_number_of_tokens)
        if options.cfg.context_sentence and self.Corpus.provides_feature(CORP_CONTEXT):
            self.header += self.Corpus.get_context_sentence_header()

        if options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            self.header.append (options.cfg.freq_label)
        
        if options.cfg.experimental:
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
            if options.cfg.MODE != QUERY_MODE_FREQUENCIES and (options.cfg.gui or options.cfg.wizard):
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
        if options.cfg.MODE != QUERY_MODE_FREQUENCIES and (options.cfg.gui or options.cfg.wizard):
            length += 3
        return length

    def open_output_file(self):
        if self.output_file:
            return
        if options.cfg.gui and not self.storage_created:
            self.output_storage = []
            self.storage_created = True
            return
        elif not options.cfg.output_path:
            self.output_file = UnicodeWriter(sys.stdout, delimiter=options.cfg.output_separator)
        else:
            if options.cfg.append:
                FileMode = "at"
            else:
                FileMode = "wt"
            self.output_file_object = open(options.cfg.output_path, FileMode)
            self.output_file = UnicodeWriter(self.output_file_object, delimiter=options.cfg.output_separator)
        if not options.cfg.append and self.show_header:
            self.output_file.writerow (self.header)
    
    def run_queries(self):
        """ Process all queries. For each query, go through the entries in 
        query_list() and yield the results for that subquery. Then, write
        all results to the output file. """
        self.expand_header()
        self._queries = {}
        self._results = {}

        self.start_time = datetime.datetime.now()
        self.end_time = None
        if options.cfg.gui:
            self.storage_created = False
        for current_query in self.query_list:
            if len(current_query.query_list) > 1:
                start_time = time.time()
                any_result = False
                for sub_query in current_query.query_list:
                    query_results = []
                    if options.cfg.experimental:
                        for current_result in self.Corpus.yield_query_results_new(sub_query):
                            query_results.append(current_result)
                    else:
                        for current_result in self.Corpus.yield_query_results(sub_query):
                            query_results.append(current_result)
                        
                    sub_query.set_result_list(query_results)
                    if query_results:
                        any_result = True
                        if not self.output_file:
                            self.open_output_file()
                        sub_query.write_results(
                            self.output_file, 
                            sub_query.number_of_tokens, 
                            self.max_number_of_tokens)                
                if not any_result:
                    if not self.output_file:
                        self.open_output_file()
                    current_query.write_results(
                        self.output_file,
                        sub_query.number_of_tokens,
                        self.max_number_of_tokens)
                logger.info("Query executed (%.3f seconds)" % (time.time() - start_time))
                
            else:
                start_time = time.time()
                logger.info("Start query: '{}'".format(current_query))

                if current_query.tokens:
                    if options.cfg.experimental:
                        current_query.set_result_list(self.Corpus.yield_query_results_new(current_query))

                        if not options.cfg.dry_run:
                            if not self.output_file:
                                self.open_output_file()
                        start_time = time.time()
                        current_query.write_results(
                            self.output_file, 
                            current_query.number_of_tokens,
                            self.max_number_of_tokens)
                        logger.info("Query executed (%.3f seconds)" % (time.time() - start_time))
                        self.end_time = datetime.datetime.now()
                    else:
                        current_query.set_result_list(self.Corpus.yield_query_results(current_query))
                        if not options.cfg.dry_run:
                            if not self.output_file:
                                self.open_output_file()
                            start_time = time.time()
                            current_query.write_results(
                                self.output_file, 
                                current_query.number_of_tokens,
                                self.max_number_of_tokens)
                            logger.info("Query executed (%.3f seconds)" % (time.time() - start_time))
        self.end_time = datetime.datetime.now()

class StatisticsSession(Session):
    def __init__(self):
        super(StatisticsSession, self).__init__()
        if self.Corpus.provides_feature(CORP_STATISTICS):
            self.query_list.append(queries.StatisticsQuery(self.Corpus, self))
        else:
            raise QueryModeError(options.cfg.corpus, options.cfg.MODE)
    
    def expand_header(self):
        self.header = ["Variable", "Value"]

class SessionCommandLine(Session):
    def __init__(self):
        super(SessionCommandLine, self).__init__()
        logger.info("{} queries".format(len(options.cfg.query_list)) if len(options.cfg.query_list) > 1 else "Single query")
        for query_string in options.cfg.query_list:
            if self.query_type:
                new_query = self.query_type(query_string, self, tokens.COCAToken, options.cfg.source_filter)
            else: 
                raise CorpusUnavailableQueryTypeError(options.cfg.corpus, options.cfg.MODE)
            self.query_list.append(new_query)
            self.max_number_of_tokens = max(new_query.max_number_of_tokens, self.max_number_of_tokens)
        self.max_number_of_input_columns = 0

class SessionInputFile(Session):
    def __init__(self):
        super(SessionInputFile, self).__init__()
        with open(options.cfg.input_path, "rt") as InputFile:
            read_lines = 0
            for current_line in UnicodeReader(InputFile, delimiter=options.cfg.input_separator):
                if current_line:
                    if options.cfg.query_column_number > len(current_line):
                        raise IllegalArgumentError("Column number for queries too big (-n %s)" % options.cfg.query_column_number)
                    if options.cfg.file_has_headers and self.header == None:
                        self.header = copy.copy(current_line)
                        if not options.cfg.show_query:
                            self.header.pop(options.cfg.query_column_number - 1)
                    else:
                        if read_lines >= options.cfg.skip_lines:
                            query_string = current_line.pop(options.cfg.query_column_number - 1)
                            new_query = self.query_type(query_string, self, tokens.COCAToken, options.cfg.source_filter)
                            new_query.InputLine = copy.copy(current_line)
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
                        new_query = self.query_type(
                                query_string, self, tokens.COCAToken, options.cfg.source_filter)
                        
                        new_query.InputLine = copy.copy(current_line)
                        self.query_list.append(new_query)
                        self.max_number_of_tokens = max(new_query.max_number_of_tokens, self.max_number_of_tokens)
                self.max_number_of_input_columns = max(len(current_line), self.max_number_of_input_columns)
            read_lines += 1
        logger.info("Reading standard input ({} {})".format(len(self.query_list), "query" if len(self.query_list) == 1 else "queries"))            
        if options.cfg.skip_lines:
            logger.info("Skipping first %s %s." % (options.cfg.skip_lines, "query" if options.cfg.skip_lines == 1 else "queries"))
    
logger = logging.getLogger(__init__.NAME)
    
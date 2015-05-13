# -*- coding: utf-8 -*-
"""
FILENAME: queries.py -- part of Coquery corpus query tool

This module defines classes for query types.

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

try:
    range = xrange
except NameError:
    pass

import copy
import string
import collections

from errors import *
from corpus import *
import tokens
import options

def expand_list(L, length, fill=""):
    """ expands the list L so that it has length elements, using the content
    of fill for additional elements. """
    return L + [fill] * (length - len(L))

def collapse_context (ContextList):
    stop_words = ["<p>", "<P>"]
    conflate_words = ["n't", "'s", "'ve"]
    token_list = []
    punct = '!\'),-./:;?^_`}’'
    quote_list = ['"', "'"]
    context_list = [x.strip() for x in ContextList]
    open_quote = {}
    open_quote ['"'] = False
    open_quote ["'"] = False
    for i, current_token in enumerate(context_list):
        if current_token not in stop_words:
            if current_token not in punct and current_token not in conflate_words:
                if i > 0 and context_list[i-1] not in '([{‘':
                    token_list.append(" ")
            token_list.append(current_token)
    return "".join(token_list)

class QueryResult(object):
    """ A little class that represents a single row of results from a query."""
    def __init__(self, query, args):
        self.data = args
        self.query = query
        
    def get_wordid_list(self, number_of_columns):
        """ returns a list containing all word_id values stored in the word 
        columns, i.e. columns named W1, ..., Wn. """
        start = int(self.data["TokenId"]) + 1
        end = start + number_of_columns - 1
        return [self.data["W1"]] + [self.query.Corpus.get_word_id(x) for x in range(start,end)]


    def get_lexicon_entries(self, number_of_columns):
        """ returns a list of lexicon entries representing the tokens in
        the current row matching the query."""
        if not self.data:
            return []
        return [self.query.Corpus.lexicon.get_entry(x, self.query.request_list) for x in self.get_wordid_list(number_of_columns)]
     
    def get_expected_length(self, max_number_of_tokens):
        count = 0
        if options.cfg.show_id:
            count += 1
        if LEX_ORTH in self.query.request_list:
            count += max_number_of_tokens
        if LEX_PHON in self.query.request_list:
            count += max_number_of_tokens
        if LEX_LEMMA in self.query.request_list:
            count += max_number_of_tokens
        if LEX_POS in self.query.request_list:
            count += max_number_of_tokens
        if CORP_SOURCE in self.query.request_list:
            count += len(self.query.Corpus.get_source_info_header())
        if CORP_SPEAKER in self.query.request_list:
            count += len(self.query.Corpus.get_speaker_info_header())
        if CORP_FILENAME in self.query.request_list:
            count += len(self.query.Corpus.get_file_info_header())
        if CORP_TIMING in self.query.request_list:
            count += len(self.query.Corpus.get_time_info_header())
        if CORP_CONTEXT in self.query.request_list:
            count += len(self.query.Corpus.get_context_header())
        return count
    
    def get_row(self, number_of_token_columns, max_number_of_tokens):
        L = []
        entry_list = self.get_lexicon_entries(number_of_token_columns)
        if not self.data or not entry_list:
            return ["<NA>"] * self.get_expected_length(max_number_of_tokens)
        Words = []
        Lemmas = []
        POSs = []
        Phon = []
        for current_entry in entry_list:
            if options.cfg.case_sensitive:
                Words.append(current_entry.orth)
            else:
                Words.append(current_entry.orth.upper())
            if LEX_LEMMA in self.query.request_list:
                Lemmas.append(current_entry.lemma)
            if LEX_POS in self.query.request_list:
                POSs.append(current_entry.pos)
            if LEX_PHON in self.query.request_list:
                Phon.append(current_entry.phon)
        if options.cfg.show_id:
            L += [self.data["TokenId"]]
        if LEX_ORTH in self.query.request_list:
            L += expand_list(Words, max_number_of_tokens)
        if LEX_PHON in self.query.request_list:
            L += expand_list(Phon, max_number_of_tokens)
        if LEX_LEMMA in self.query.request_list:
            L += expand_list(Lemmas, max_number_of_tokens)
        if LEX_POS in self.query.request_list:
            L += expand_list(POSs, max_number_of_tokens)
        if CORP_SOURCE in self.query.request_list:
            L += self.query.Corpus.get_source_info(self.data["SourceId"])
        if CORP_SPEAKER in self.query.request_list:
            L += self.query.Corpus.get_speaker_info(self.data["SpeakerId"])
        if CORP_FILENAME in self.query.request_list:
            L += self.query.Corpus.get_file_info(self.data["SourceId"])
        if CORP_TIMING in self.query.request_list:
            L += self.query.Corpus.get_time_info(self.data["TokenId"])
        if CORP_CONTEXT in self.query.request_list:
            if options.cfg.context_sentence:
                context = self.query.Corpus.get_context_sentence(self.data["SourceId"]) 
            else:
                context_left, context_right = self.query.Corpus.get_context(self.data["TokenId"], self.data["SourceId"], self.query.number_of_tokens, True)
                context = context_left + Words + context_right
            if options.cfg.context_columns:
                L += context
            else:
                L += [collapse_context(context)]
        return L

class CorpusQuery(object):
    class ResultList(list):
        """ A class that represents the results from a query. It is iterable, 
        and the iterator returns QueryResult() objects."""
        def __init__(self, query, data):
            self.data = data
            self.query = query
            
        def __iter__(self):
            self.count = 0
            return self

        def next(self):
            if not self.data:
                raise StopIteration
            try:
                return QueryResult(self.query, next(self.data))
            except AttributeError:
                try:
                    self.count += 1
                    return QueryResult(self.data[self.count - 1])
                except IndexError:
                    raise StopIteration

        def __next__(self):
            return self.next()

        def append(self, *args):
            self.data.append(*args)

    ErrorInQuery = False

    def __init__(self, S, Session, token_class, source_filter):
        
        self.query_list = []
        self.max_number_of_tokens = 0
        repeated_queries = tokens.preprocess_query(S)
        if len(repeated_queries) > 1:
            for current_string in repeated_queries:
                current_query = self.__class__(current_string, Session, token_class, source_filter)
                self.query_list.append(current_query)
                self.max_number_of_tokens = max(self.max_number_of_tokens, current_query.number_of_tokens)
        else:
            self.tokens = [token_class(x, Session.Corpus.lexicon) for x in tokens.parse_query_string(S, token_class)]
            self.number_of_tokens = len(self.tokens)
            self.max_number_of_tokens = len(self.tokens)
            
        self.query_string = S
        self._current = 0
        self.Session = Session
        self.Corpus = Session.Corpus
        self.Results = self.ResultList(self, [])
        self.InputLine = []
        self.request_list = []

        if self.Corpus.provides_feature(CORP_SOURCE):
            self.source_filter = source_filter
        else:
            self.source_filter = None
        
        if options.cfg.show_orth:
            self.request_list.append(LEX_ORTH)        
        if options.cfg.show_lemma:
            self.request_list.append(LEX_LEMMA)
        if options.cfg.show_pos:
            self.request_list.append(LEX_POS)
        if options.cfg.show_phon:
            self.request_list.append(LEX_PHON)
        if options.cfg.show_text:
            self.request_list.append(CORP_SOURCE)
        if options.cfg.show_filename:
            self.request_list.append(CORP_FILENAME)
        if options.cfg.show_speaker:
            self.request_list.append(CORP_SPEAKER)
        if options.cfg.show_time:
            self.request_list.append(CORP_TIMING)
        if options.cfg.context_span or options.cfg.context_columns or options.cfg.context_sentence:
            self.request_list.append(CORP_CONTEXT)
            
        self.request_list = [x for x in self.request_list if self.Corpus.provides_feature(x)]
            
    def __iter__(self):
        return self
    
    def next(self):
        if self._current >= len(self.tokens):
            raise StopIteration
        else:
            self._current += 1
            return self.tokens[self._current - 1]

    def __str__(self):
        return " ".join(map(str, self.tokens))
    
    def __len__(self):
        return len(self.tokens)

    def set_result_list(self, data):
        self.Results = self.ResultList(self, data)
        return

    def get_result_list(self):
        return self.Results
    
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        for CurrentLine in self.get_result_list():
            output_file.writerow(CurrentLine)

class TokenQuery(CorpusQuery):
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        for current_result in self.get_result_list():
            if self.InputLine:
                output_list = copy.copy(self.InputLine)
            else:
                output_list = []
            if options.cfg.show_query:
                output_list.insert(options.cfg.query_column_number - 1, self.query_string)
            if current_result != None:
                if options.cfg.show_parameters:
                    output_list.append(options.cfg.parameter_string)
                if options.cfg.show_filter:
                    output_list.append(self.source_filter)
                output_list += current_result.get_row(number_of_token_columns, max_number_of_token_columns)
                
                output_file.writerow(output_list)

class DistinctQuery(CorpusQuery):
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        output_cache = []
        for current_result in self.get_result_list():
            if self.InputLine:
                output_list = copy.copy(self.InputLine)
            else:
                output_list = []
            if options.cfg.show_query:
                output_list.insert(options.cfg.query_column_number - 1, self.query_string)
            if current_result != None:
                if options.cfg.show_parameters:
                    output_list.append(options.cfg.parameter_string)
                if options.cfg.show_filter:
                    output_list.append(self.source_filter)
                output_list += current_result.get_row(number_of_token_columns, max_number_of_token_columns)
                if output_list not in output_cache:
                    output_file.writerow(output_list)
                    output_cache.append(output_list)

class StatisticsQuery(CorpusQuery):
    def __init__(self, corpus):
        self.Results = corpus.get_statistics()
        self.tokens = []
        
    def write_results(self, output_file, number_of_token_columns):
        output_file.writerow(["Variable", "Value"])
        
        for x in sorted(self.Results):
            output_file.writerow([x, self.Results[x]])

class FrequencyQuery(CorpusQuery):
    def __init__(self, *args):
        super(FrequencyQuery, self).__init__(*args)
        self.request_list.append(LEX_FREQ)

    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        Lines = collections.Counter()
        results = self.get_result_list()
        for current_result in results:
            # current_result can be None if the query token was not in the
            # lexicon
            if current_result:
                output_list = current_result.get_row(number_of_token_columns, max_number_of_token_columns)
                LineKey = "<|>".join(output_list)
                Lines[LineKey] += 1
        if not Lines:
            empty_result = QueryResult(self, {}) 
            output_list = empty_result.get_row(number_of_token_columns, max_number_of_token_columns)
            LineKey = "<|>".join(output_list)
            Lines[LineKey] = 0
            
        for current_key in Lines:
            if self.InputLine:
                output_list = copy.copy(self.InputLine)
            else:
                output_list = []
            if options.cfg.show_query:
                output_list.insert(options.cfg.query_column_number - 1, self.query_string)
            if options.cfg.show_parameters:
                output_list.append(options.cfg.parameter_string)
            if options.cfg.show_filter:
                output_list.append(self.source_filter)
            if current_key:
                output_list += current_key.split("<|>")
            output_list.append(Lines[current_key])
            if self.ErrorInQuery:
                output_list[-1] = -1
            output_file.writerow(output_list)

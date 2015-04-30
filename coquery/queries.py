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

import copy
import string

from errors import *
from corpus import *
import tokens
import options

def expand_list(L, length, fill=""):
    """ expands the list L so that it has length elements, using the content
    of fill for additional elements. """
    return L + [fill] * (length - len(L))

def CollapseContext (ContextList):
    ContextString = " ".join (ContextList)
    ContextString = ContextString.replace ('""""', '"')
    S = ""
    Punct = '!\'),-./:;?^_`}'
    for i, CurrentChar in enumerate(ContextString):
        if CurrentChar == " ":
            if ContextString [i + 1] in Punct:
                pass
            else:
                if ContextString [i - 1] in '([{"':
                    pass
                else:
                    S += CurrentChar
        else:
            S += CurrentChar
    return S

class QueryResult(dict):
    """ A little class that represents a single row of results from a query."""
    def __init__(self, query, *args):
        super(QueryResult, self).__init__(*args)
        self.query = query
        
    def get_wordid_list(self):
        """ returns a list containing all word_id values stored in the word 
        columns, i.e. columns named W1, ..., Wn. """
        try:
            L = [self["W%s" % (x + 1)] for x in range(self.query.number_of_tokens)]
        except KeyError:
            L = ["NA"] * self.query.number_of_tokens
        return L

    def __getitem__(self, *args):
        try:
            return super(QueryResult, self).__getitem__(*args)
        except KeyError:
            return None

    def get_lexicon_entries(self):
        """ returns a list of lexicon entries representing the tokens in
        the current row matching the query."""
        return [self.query.Corpus.lexicon.get_entry(x, self.query.request_list) for x in self.get_wordid_list()]
        
    def get_row(self, number_of_token_columns):
        L = []
        entry_list = self.get_lexicon_entries()
        Words = []
        Lemmas = []
        POSs = []
        Phon = []
        for current_entry in entry_list:
            if options.cfg.case_sensitive:
                Words.append(current_entry.orth)
            else:
                Words.append(current_entry.orth.lower())
            if self.query.requested(LEX_LEMMA):
                Lemmas.append(current_entry.lemma)
            if self.query.requested(LEX_POS):
                POSs.append(current_entry.pos)
            if self.query.requested(LEX_PHON):
                Phon.append(current_entry.phon)
        if options.cfg.show_id:
            L += [self["TokenId"]]
        if self.query.requested(LEX_ORTH):
            L += expand_list(Words, number_of_token_columns)
        if self.query.requested(LEX_PHON):
            L += expand_list(Phon, number_of_token_columns)
        if self.query.requested(LEX_LEMMA):
            L += expand_list(Lemmas, number_of_token_columns)
        if self.query.requested(LEX_POS):
            L += expand_list(POSs, number_of_token_columns)
        if self.query.requested(CORP_SOURCE):
            L += self.query.Corpus.get_source_info(self["SourceId"])
        if self.query.requested(CORP_SPEAKER):
            L += self.query.Corpus.get_speaker_info(self["SpeakerId"])
        if self.query.requested(CORP_FILENAME):
            L += self.query.Corpus.get_file_info(self["SourceId"])
        if self.query.requested(CORP_TIMING):
            L += self.query.Corpus.get_time_info(self["TokenId"])
        if self.query.requested(CORP_CONTEXT):
            context = self.query.Corpus.get_context(self["TokenId"], self.query.number_of_tokens)
            if options.cfg.separate_columns:
                L += context
            else:
                L += [CollapseContext(context)]
        if self.query.requested(LEX_FREQ):
            if options.cfg.freq_label in self:
                L += [self[options.cfg.freq_label]]
            else:
                L += [1]
        return L

class CorpusQuery(object):
    class ResultList(list):
        """ A class that represents the results from a query. It is iterable, 
        and the iterator returns QueryResult() objects."""
        def __init__(self, query, data):
            self.data = data
            self.current = None
            self.query = query
            
        def __iter__(self):
            self.count = 0
            return self
        
        def next(self):
            if "next" in dir(self.data):
                next_result = self.data.next()
            else: 
                try:
                    next_result = self.data[self.count]
                except IndexError:
                    next_result = None
                self.count += 1
            self.current = next_result
            if next_result == None:
                raise StopIteration
            else:
                return QueryResult(self.query, next_result)

        def __next__(self):
            return self.next()

        def append(self, *args):
            self.data.append(*args)

    ErrorInQuery = False

    def __init__(self, S, Corpus, token_class, source_filter):
        self.tokens = [token_class(x, Corpus.lexicon) for x in tokens.parse_query_string(S, token_class)]
        self.number_of_tokens = len(self.tokens)
        self.query_string = S
        self._current = 0
        self.Corpus = Corpus
        self.Results = [None]
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
        if options.cfg.context_span:
            self.request_list.append(CORP_CONTEXT)
            
        self.request_list = [x for x in self.request_list if self.Corpus.provides_feature(x)]
            
    def requested(self, feature):
        return feature in self.request_list

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
    
    def write_results(self, output_file, number_of_token_columns):
        for CurrentLine in self.get_result_list():
            output_file.writerow(CurrentLine)

class TokenQuery(CorpusQuery):
    def write_results(self, output_file, number_of_token_columns):
        for current_result in self.get_result_list():
            output_list = copy.copy(self.InputLine)
            if options.cfg.show_query:
                output_list.insert(options.cfg.query_column_number - 1, self.query_string)
            if current_result != None:
                if options.cfg.show_parameters:
                    output_list.append(options.cfg.parameter_string)
                if self.source_filter:
                    output_list.append(self.source_filter)
                output_list += current_result.get_row(number_of_token_columns)
                
                output_file.writerow(output_list)

class DistinctQuery(CorpusQuery):
    def write_results(self, output_file, number_of_token_columns):
        output_cache = []
        for current_result in self.get_result_list():
            output_list = copy.copy(self.InputLine)
            if options.cfg.show_query:
                output_list.insert(options.cfg.query_column_number - 1, self.query_string)
            if current_result != None:
                if options.cfg.show_parameters:
                    output_list.append(options.cfg.parameter_string)
                if self.source_filter:
                    output_list.append(self.source_filter)
                output_list += current_result.get_row(number_of_token_columns)
                if output_list not in output_cache:
                    output_file.writerow(output_list)
                    output_cache.append(output_list)


class StatisticsQuery(CorpusQuery):
    def __init__(self, corpus):
        self.Results = corpus.get_statistics()
        self.tokens = []
        
    def write_results(self, output_file, number_of_token_columns):
        for x in self.Results:
            output_file.writerow([x, self.Results[x]])

class FrequencyQuery(CorpusQuery):
    def __init__(self, *args):
        super(FrequencyQuery, self).__init__(*args)
        self.request_list.append(LEX_FREQ)

    def write_results(self, output_file, number_of_token_columns):
        Lines = {}
        results = self.get_result_list()
        for current_result in results:
            output_list = copy.copy (self.InputLine)
            if options.cfg.show_query:
                output_list.insert (options.cfg.query_column_number - 1, self.query_string)
            if options.cfg.show_parameters:
                output_list.append (options.cfg.parameter_string)
            if self.source_filter:
                output_list.append (self.source_filter)
            output_list += current_result.get_row(number_of_token_columns)
            
            LineKey = "".join(map(str, output_list[:-1]))
            if LineKey in Lines:
                output_list[-1] += Lines[LineKey][-1]
            Lines[LineKey] = output_list

        if not Lines:
            # write entry with frequency of zero for query results with no hits:
            empty_result = QueryResult(self) 
            empty_result[options.cfg.freq_label] = 0
            output_list = copy.copy (self.InputLine)
            if options.cfg.show_query:
                output_list.insert (options.cfg.query_column_number - 1, self.query_string)
            if options.cfg.show_parameters:
                output_list.append (options.cfg.parameter_string)
            if self.source_filter:
                output_list.append (self.source_filter)
            output_list += empty_result.get_row(number_of_token_columns)
            
            output_file.writerow(output_list)
        else:
            # otherwise, write entry with token frequency:
            for current_key in Lines:
                current_line = Lines[current_key]
                if self.ErrorInQuery:
                    current_line[-1] = -1
                output_file.writerow(current_line)

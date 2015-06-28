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

from __future__ import unicode_literals

try:
    range = xrange
except NameError:
    pass

import __init__
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
        try:
            if '""""' in current_token:
                current_token = '"'
            if current_token not in stop_words:
                if current_token not in punct and current_token not in conflate_words:
                    if i > 0 and context_list[i-1] not in '([{‘':
                        token_list.append(" ")
                token_list.append(current_token)
        except (UnicodeEncodeError, UnicodeDecodeError):
            token_list.append(unicode(current_token.decode("utf-8")))
    return "".join(token_list)

class QueryResult(object):
    """ A little class that represents a single row of results from a query."""
    def __init__(self, query, args):
        self.data = args
        self.query = query
        
    def get_expected_length(self, max_number_of_tokens):
        output_fields = self.query.Session.output_fields
        count = 0
        if options.cfg.show_id:
            count += 1
        if LEX_ORTH in output_fields:
            count += max_number_of_tokens
        if LEX_PHON in output_fields:
            count += max_number_of_tokens
        if LEX_LEMMA in output_fields:
            count += max_number_of_tokens
        if LEX_POS in output_fields:
            count += max_number_of_tokens
        if CORP_SOURCE in output_fields:
            count += len(self.query.Corpus.get_source_info_header())
        if CORP_SPEAKER in output_fields:
            count += len(self.query.Corpus.get_speaker_info_header())
        if CORP_FILENAME in output_fields:
            count += len(self.query.Corpus.get_file_info_header())
        if CORP_TIMING in output_fields:
            count += len(self.query.Corpus.get_time_info_header())
        if CORP_CONTEXT in output_fields:
            count += len(self.query.Corpus.get_context_header(max_number_of_tokens))
        if options.cfg.experimental or len(self.query.Session.output_fields) == 1:
            if LEX_FREQ in output_fields:
                count += 1
        return count
    
    def get_row(self, number_of_token_columns, max_number_of_tokens, row_length=None):
        
        output_row = [""] * (row_length)
        if not self.data:
            return tuple(output_row)
        output_fields = self.query.Session.output_fields
        # create a list of lexicon entries for each word W1, ..., Wn in 
        # the results row:
    
        entry_list = [self.query.Corpus.lexicon.get_entry(
            x, self.query.Session.output_fields) for x in [self.data["W{}".format(x)] for x in range(1, number_of_token_columns + 1)]]

        index = 0

        if options.cfg.show_id:
            output_row[index] = [self.data["TokenId"]]
            index += 1
        if LEX_ORTH in output_fields or CORP_CONTEXT in output_fields:
            if options.cfg.case_sensitive:
                words = [x.orth for x in entry_list]
            else:
                words = [x.orth.upper() for x in entry_list]
            if LEX_ORTH in output_fields:
                output_row[index:(index+number_of_token_columns)] = words
                index += max_number_of_tokens

        if LEX_PHON in output_fields:
            output_row[index:(index+number_of_token_columns)] = [x.phon for x in entry_list]
            index += max_number_of_tokens

        if LEX_LEMMA in output_fields:
            output_row[index:(index+number_of_token_columns)] = [x.lemma for x in entry_list]
            index += max_number_of_tokens

        if LEX_POS in output_fields:
            output_row[index:(index+number_of_token_columns)] = [x.pos for x in entry_list]
            index += max_number_of_tokens

        if CORP_SOURCE in output_fields:
            source_info = self.query.Corpus.get_source_info(self.data["SourceId"])
            output_row[index:(index+len(source_info))] = source_info
            index += len(source_info)
            
        if CORP_SPEAKER in output_fields:
            speaker_info = self.query.Corpus.get_speaker_info(self.data["SpeakerId"])
            output_row[index:(index+len(speaker_info))] = speaker_info
            index += len(speaker_info)

        if CORP_FILENAME in output_fields:
            file_info = self.query.Corpus.get_file_info(self.data["SourceId"])
            output_row[index:(index+len(file_info))] = file_info
            index += len(file_info)

        if CORP_TIMING in output_fields:
            time_info = self.query.Corpus.get_time_info(self.data["TokenId"])
            output_row[index:(index+len(time_info))] = time_info
            index += len(time_info)

        if CORP_CONTEXT in output_fields:
            if options.cfg.context_sentence:
                context = self.query.Corpus.get_context_sentence(self.data["SourceId"]) 
            else:
                context_left, context_right = self.query.Corpus.get_context(self.data["TokenId"], self.data["SourceId"], self.query.number_of_tokens, True)
                context = context_left + words + context_right
            if options.cfg.context_columns:
                output_row[index:] = context
            else:
                output_row[index] = collapse_context(context)
        return tuple(output_row)

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
            #return QueryResult(self.query, next(self.data))
            if not self.data:
                raise StopIteration
            #try:
                #next_thing = next(self.data)
            #except (AttributeError, TypeError):
                #try:
                    #self.count += 1
                    #print(1)
                    #return QueryResult(self.query, self.data[self.count - 1])
                #except IndexError:
                    #raise StopIteration
            next_thing = next(self.data)
            return QueryResult(self.query, next_thing)

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

        if self.Corpus.provides_feature(CORP_SOURCE):
            self.source_filter = source_filter
        else:
            self.source_filter = None
        
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
        if options.cfg.experimental:
            self.Results = data
        else:
            self.Results = self.ResultList(self, data)
            #self.Results = data

    def get_result_list(self):
        return self.Results
    
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        for CurrentLine in self.get_result_list():
            output_file.writerow(CurrentLine)
            
    def get_row(self, query_result, number_of_token_columns, max_number_of_tokens, row_length=None):
        output_row = [""] * (row_length)
        if not query_result:
            return tuple(output_row)
        output_fields = self.Session.output_fields
        index = 0
        if options.cfg.show_id:
            output_row[index] = [query_result["TokenId"]]
            index += 1
        if LEX_ORTH in output_fields or CORP_CONTEXT in output_fields:
            if options.cfg.case_sensitive:
                words = [query_result["W{}_orth".format(x)] for x in range(1, number_of_token_columns + 1)]
            else:
                words = [query_result["W{}_orth".format(x)].upper() for x in range(1, number_of_token_columns + 1)]
            if LEX_ORTH in output_fields:
                output_row[index:(index+number_of_token_columns)] = words
                index += max_number_of_tokens

        if LEX_PHON in output_fields:
            output_row[index:(index+number_of_token_columns)] = [query_result["W{}_phon".format(x)] for x in range(1, number_of_token_columns + 1)]
            index += max_number_of_tokens

        if LEX_LEMMA in output_fields:
            output_row[index:(index+number_of_token_columns)] = [query_result["L{}_orth".format(x)] for x in range(1, number_of_token_columns + 1)]
            index += max_number_of_tokens

        if LEX_POS in output_fields:
            output_row[index:(index+number_of_token_columns)] = [query_result["W{}_pos".format(x)] for x in range(1, number_of_token_columns + 1)]
            index += max_number_of_tokens

        if CORP_SOURCE in output_fields:
            source_info = self.Corpus.get_source_info(query_result["SourceId"])
            output_row[index:(index+len(source_info))] = source_info
            index += len(source_info)
            
        if CORP_SPEAKER in output_fields:
            speaker_info = self.Corpus.get_speaker_info(query_result["SpeakerId"])
            output_row[index:(index+len(speaker_info))] = speaker_info
            index += len(speaker_info)

        if CORP_FILENAME in output_fields:
            file_info = self.Corpus.get_file_info(query_result["SourceId"])
            output_row[index:(index+len(file_info))] = file_info
            index += len(file_info)

        if CORP_TIMING in output_fields:
            time_info = self.Corpus.get_time_info(query_result["TokenId"])
            output_row[index:(index+len(time_info))] = time_info
            index += len(time_info)

        if CORP_CONTEXT in output_fields:
            context_width = max(options.cfg.context_span, options.cfg.context_columns)
            L = list(range(context_width))
            context_left = [query_result["LC{}".format(x + 1)] for x in L[::-1]]
            context_right = [query_result["RC{}".format(x + 1)] for x in L]
            context = context_left + words + context_right
            if options.cfg.context_columns:
                output_row[index:] = context
            else:
                output_row[index] = collapse_context(context)
        if options.cfg.experimental or len(self.Session.output_fields) == 1:
            if LEX_FREQ in output_fields:
                output_row[index] = query_result[options.cfg.freq_label]
                index += 1
        return tuple(output_row)

class TokenQuery(CorpusQuery):
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        result_columns = QueryResult(self, None).get_expected_length(max_number_of_token_columns)
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
                output_list += current_result.get_row(number_of_token_columns, max_number_of_token_columns, result_columns)
                
                if options.cfg.gui:
                    self.Session.output_storage.append(output_list)
                else:
                    output_file.writerow(output_list)

class DistinctQuery(CorpusQuery):
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        output_cache = []
        result_columns = QueryResult(self, None).get_expected_length(max_number_of_token_columns)

        # construct that part of output lines that stays constant in all
        # lines:
        if self.InputLine:
            constant_line = copy.copy(self.InputLine)
        else:
            constant_line = []
        if options.cfg.show_query:
            constant_line.insert(options.cfg.query_column_number - 1, self.query_string)
        if options.cfg.show_parameters:
            constant_line.append(options.cfg.parameter_string)
        if options.cfg.show_filter:
            constant_line.append(self.source_filter)

        for current_result in self.Results:
            if constant_line:
                output_list = copy.copy(constant_line)
            else:
                output_list = []

            if current_result != None:
                if options.cfg.experimental:
                    output_list.extend(self.get_row(current_result, number_of_token_columns, max_number_of_token_columns, result_columns))
                else:
                    output_list.extend(current_result.get_row(number_of_token_columns, max_number_of_token_columns, result_columns))
                if output_list not in output_cache:
                    if options.cfg.gui:
                        self.Session.output_storage.append(output_list)
                    else:
                        output_file.writerow(output_list)
            if output_list not in output_cache:
                output_cache.append(output_list)

class StatisticsQuery(CorpusQuery):
    def __init__(self, corpus, session):
        super(StatisticsQuery, self).__init__("", session, None, None)
        self.Results = self.Session.Corpus.get_statistics()
        
        # convert all values to strings (the Unicode writer needs that):
        self.Results = {key: str(self.Results[key]) for key in self.Results}
    
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        output_file.writerow(["Variable", "Value"])
        
        for x in sorted(self.Results):
            if options.cfg.gui:
                self.Session.output_storage.append([x, self.Results[x]])
            else:
                output_file.writerow([x, self.Results[x]])

class FrequencyQuery(CorpusQuery):
    def __init__(self, *args):
        super(FrequencyQuery, self).__init__(*args)
        self.Session.output_fields.add(LEX_FREQ)
        
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        
        # make the experimental query mode the default if there is exactly
        # one query token, but optional otherwise:
        if options.cfg.experimental or len(self.Session.output_fields) == 1:
            output_cache = []
            result_columns = QueryResult(self, None).get_expected_length(max_number_of_token_columns)

            # construct that part of output lines that stays constant in all
            # lines:
            if self.InputLine:
                constant_line = copy.copy(self.InputLine)
            else:
                constant_line = []
            if options.cfg.show_query:
                constant_line.insert(options.cfg.query_column_number - 1, self.query_string)
            if options.cfg.show_parameters:
                constant_line.append(options.cfg.parameter_string)
            if options.cfg.show_filter:
                constant_line.append(self.source_filter)

            for current_result in self.Results:
                if constant_line:
                    output_list = copy.copy(constant_line)
                else:
                    output_list = []

                if current_result != None:
                    output_list.extend(self.get_row(current_result, number_of_token_columns, max_number_of_token_columns, result_columns))
                    if output_list not in output_cache:
                        if options.cfg.gui:
                            self.Session.output_storage.append(output_list)
                        else:
                            output_file.writerow(output_list)
                if output_list not in output_cache:
                    output_cache.append(output_list)
            return
        
        # Check if the same query string has been queried in this session.
        # If so, use the cached results:
        
        if self.query_string in self.Session._results:
            Lines = self.Session._results[self.query_string]
        else:
            # Collapse all identical lines in the result list:
            Lines = collections.Counter()
            result_columns = QueryResult(self, None).get_expected_length(max_number_of_token_columns)
            for current_result in self.Results:
                if options.cfg.experimental:
                    if current_result:
                        Lines[self.get_row(current_result, number_of_token_columns, max_number_of_token_columns, result_columns)] += 1
                else:
                    # current_result can be None if the query token was not in the
                    # lexicon
                    if current_result:
                        Lines[current_result.get_row(number_of_token_columns, max_number_of_token_columns, result_columns)] += 1
            if not Lines:
                empty_result = QueryResult(self, {}) 
                Lines[empty_result.get_row(number_of_token_columns, max_number_of_token_columns, result_columns)] = 0
            self.Session._results[self.query_string] = Lines
        
        if options.cfg.order_frequency:
            data = Lines.most_common()
            get_key = lambda x: x[0]
        else:
            data = Lines
            get_key = lambda x: x
        
        # construct that part of output lines that stays constant in all
        # lines:
        if self.InputLine:
            constant_line = copy.copy(self.InputLine)
        else:
            constant_line = []
        if options.cfg.show_query:
            constant_line.insert(options.cfg.query_column_number - 1, self.query_string)
        if options.cfg.show_parameters:
            constant_line.append(options.cfg.parameter_string)
        if options.cfg.show_filter:
            constant_line.append(self.source_filter)

        # Output the collapsed lines:
        for current_line in data:
            key = get_key(current_line)
            # copy constant part of output
            if constant_line:
                output_list = copy.copy(constant_line)
            else:
                output_list = []
            # add data:
            output_list.extend(list(key))
            # add frequency:
            output_list.append(Lines[key])
            if options.cfg.gui:
                self.Session.output_storage.append(output_list)
            else:
                output_file.writerow(output_list)

logger = logging.getLogger(__init__.NAME)

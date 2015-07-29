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
from __future__ import division
import math

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

class QueryFilter(object):
    """ Define a class that stores a query filter. 
    
    Query filters are text strings that follow a very simple syntax. Valid
    filter strings are:
    
    variable operator value
    variable operator value value ...
    variable operator value, value, ...
    variable operator value-value
    
    'variable' contains the display name of a table column. If the display
    name is ambiguous, i.e. if two or more tables contain a name with the
    same column, the name is disambiguated by preceding it with the table
    name, linked by a '.'.

    """
    
    operators = (">", "<", "<>", "IN", "IS", "=", "LIKE")

    def __init__(self, text = ""):
        """ Initialize the filter. """
        self._text = text
        self._table = ""
        self._resource = None
        self._parsed = False
        
    @property
    def resource(self):
        return self._resource
    
    @resource.setter
    def resource(self, resource_class):
        self._resource = resource_class
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, s):
        if self.validate(s):
            self._text = s
            self._variable, self._op, self._value_list, self._value_range = self.parse_filter(s)
        else:
            raise InvalidFilterError
    def __repr__(self):
        return "QueryFilter('{}', {})".format(self.text, self.resource)
    
    def __str__(self):
        l = [name for  _, name in self.resource.get_corpus_features() if name.lower == self._variable.lower()]        
        if l:
            variable_name = l[0]
        else:
            variable_name = self._variable
        
        if self._value_list:
            return "{} {} {}".format(variable_name.capitalize(), self._op.lower(), ", ".join(sorted(self._value_list)))
        elif self._value_range:
            return "{} {} {}-{}".format(variable_name.capitalize(), self.op.lower(), min(self._value_range), max(self._value_range))
        else:
            return self._text.strip()
            
    def parse_filter(self, text):
        """ Parse the text and return a tuple with the query filter 
        components.  The tuple contains the components (in order) variable, 
        operator, value_list, value_range.
        
        The component value_list is a list of all specified values. The 
        componment value_range is a tuple with the lower and the upper limit
        of the range specified in the text. Only one of the two components 
        value_list and value_range contains valid values, the other is None.
        
        If the text is not a valid filter text, the tuple None, None, None, 
        None is returned."""
        
        error_value = None, None, None, None
        
        if "<>" in text:
            text.replace("<>", " <> ")
        elif "=" in text:
            text = text.replace("=", " = ")
        elif "<" in text:
            text = text.replace("<", " < ")
        elif ">" in text:
            text = text.replace(">", " > ")
        
        fields = str(text).split()
        try:
            self.var = fields[0]
        except:
            return error_value
        try:
            self.operator = fields[1]
        except:
            return error_value            
        try:
            values = fields[2:]
        except:
            return error_value
        
        if not values:
            return error_value
        
        # check for range:
        collapsed_values = "".join(fields[2:])
        if collapsed_values.count("-") == 1:
            self.value_list = None
            self.value_range = tuple(collapsed_values.split("-"))
        else:
            self.value_range = None
            self.value_list = sorted([x.strip("(),").strip() for x in values])

        if (self.value_range or len(self.value_list) > 1) and self.operator.lower() in ("is", "="):
            self.operator = "in"

        if self.operator == "LIKE":
            if self.value_range or len(self.value_list) > 1:
                return error_value

        self._parsed = True
        return self.var, self.operator, self.value_list, self.value_range
            
    def validate(self, s):
        """ Check if the text contains a valid filter. A filter is valid if
        it has the form 'x OP y', where x is a resource variable name, OP is
        a comparison operator, and value is either a string, a number or a 
        list. """
        var, op, value_range, value_list = self.parse_filter(s)
        if not var:
            return False
        variable_names = [name.lower() for  _, name in self.resource.get_corpus_features() + [("coq_frequency", "freq")]]
        if var.lower() not in variable_names:
            return False
        if variable_names.count(var.lower()) > 1:
            print("ambiguous!")
            print(variable_names, var.lower())
            return True
        if op.lower() not in [x.lower() for x in self.operators]:
            return False
        return True
    
    def check_number(self, n):
        """ Return true if the number n is not filtered by this filter, or
        false otherwise."""
        if not self._parsed:
            self.parse_filter(self._text)
            
        try:
            n = float(n)
            if self.operator in ("=", "IS", "LIKE"):
                return n == float(self.value_list[0])
            elif self.operator == ">":
                return n > float(self.value_list[0])
            elif self.operator == "<":
                return n < float(self.value_list[0])
            elif self.operator == "<>":
                return n <> float(self.value_list[0])
            elif self.operator == "IN":
                return n >= float(self.value_range[0]) and n <= float(self.value_range[1])
        except ValueError:
            return False

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
        if options.cfg.experimental:
            if LEX_FREQ in output_fields:
                count += 1
        return count
    
    def get_row(self, number_of_token_columns, max_number_of_tokens, row_length=None):
        """ get_row() from QueryResult """
        output_row = [""] * (row_length)
        if not self.data:
            return tuple(output_row)
        output_fields = self.query.Session.output_fields
        # create a list of lexicon entries for each word W1, ..., Wn in 
        # the results row:


        index = 0

        if options.cfg.show_id:
            output_row[index] = [self.data["TokenId"]]
            index += 1
        if LEX_ORTH in output_fields or CORP_CONTEXT in output_fields:
            entry_list = [self.query.Corpus.lexicon.get_entry(
                x, self.query.Session.output_fields) for x in [self.data["W{}".format(x)] for x in range(1, number_of_token_columns + 1)]]
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
                output_row[index] = collapse_words(context)
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
        self.token_class = token_class
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

    def get_result_list(self):
        return self.Results
    
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        for CurrentLine in self.get_result_list():
            output_file.writerow(CurrentLine)
    
    def use_flat_query(self):
        """ Return True if a flat query should be used, or False otherwise.
        A flat query is a query that uses only a single SQL statement that
        retrieves the content of all columns in the result table. """
        if len(self.Session.output_fields) == 1:
            return True
        else:
            return False
    
    def get_row(self, query_result, number_of_token_columns, max_number_of_tokens, row_length=None):
        """ get_row() from CorpusQuery."""
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

        if options.cfg.experimental:
            print("###")
            if options.cfg.experimental:
                print("info", self.Corpus.get_source_info_header())
                source_info = self.Corpus.get_source_info(query_result["SourceId"])
        else:
            if CORP_SOURCE in output_fields:
                source_info = self.Corpus.get_source_info(query_result["SourceId"])
                output_row[index:(index+len(source_info))] = source_info
                index += len(source_info)
                
            if CORP_SPEAKER in output_fields:
                speaker_info = self.Corpus.get_speaker_info(query_result["SpeakerId"])
                output_row[index:(index+len(speaker_info))] = speaker_info
                index += len(speaker_info)

            if CORP_FILENAME in output_fields:
                if options.cfg.experimental:
                    file_info = [query_result[self.Corpus.resource.file_label]]
                else:
                    file_info = self.Corpus.get_file_info(query_result["SourceId"])
                output_row[index:(index+len(file_info))] = file_info
                index += len(file_info)

            if CORP_TIMING in output_fields:
                if options.cfg.experimental:
                    time_info = [query_result[self.Corpus.resource.corpus_time]]
                else:
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
                    output_row[index] = collapse_words(context)
        if options.cfg.experimental or len(self.Session.output_fields) == 1 or self.number_of_queries == 1:
            if LEX_FREQ in output_fields:
                try:
                    output_row[index] = query_result.data[options.cfg.freq_label]
                except AttributeError:
                    output_row[index] = query_result[options.cfg.freq_label]
                index += 1
        return tuple(output_row)

class DistinctQuery(CorpusQuery):
    """ Define a CorpusQuery subclass that reformats the query results in a 
    beautified way that is suitable for CSV or GUI output."""
    
    collapse_identical = True
    
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns, data = None):
        output_cache = set([])
        if options.cfg.experimental:
            result_columns = self.Session.get_expected_column_number(max_number_of_token_columns)
        else:
            result_columns = QueryResult(self, None).get_expected_length(max_number_of_token_columns)

        # construct that part of output lines that stays constant in all
        # lines:
        if self.InputLine:
            constant_line = copy.copy(self.InputLine)
        else:
            constant_line = []

        if options.cfg.experimental:
            for current_result in self.Results:
                if constant_line:
                    output_list = copy.copy(constant_line)
                else:
                    output_list = []

                if not options.cfg.case_sensitive:
                    for x in current_result:
                        try:
                            current_result[x] = current_result[x].lower()
                        except AttributeError:
                            pass

                # store values from visible columns into output_list:
                output_list.extend([current_result[x] for x in self.Session.output_order if not x.startswith("coquery_invisible_")])
                output_list = tuple(output_list)

                if self.collapse_identical:
                    if output_list not in output_cache:
                        if options.cfg.gui:
                            self.Session.output_storage.append(current_result)
                        else:
                            output_file.writerow(output_list)
                        output_cache.add(output_list)
                else:
                    if options.cfg.gui:
                        self.Session.output_storage.append(current_result)
                    else:
                        output_file.writerow(output_list)
        else:
            for current_result in self.Results:
                if constant_line:
                    output_list = copy.copy(constant_line)
                else:
                    output_list = []
                    
                if current_result != None:
                    output_list.extend(current_result.get_row(number_of_token_columns, max_number_of_token_columns, result_columns))
                    output_list = tuple(output_list)
                    if output_list not in output_cache:
                        if options.cfg.gui:
                            self.Session.output_storage.append(output_list)
                        else:
                            output_file.writerow(output_list)
                        if self.collapse_identical:
                            output_cache.add(output_list)

class TokenQuery(DistinctQuery):
    """ Define a subclass of DistinctQuery. The only difference between this
    subclass and the parent class DistinctQuery is that the attribute
    collapse_identical is set to False in the subclass. This attribute is 
    evaluated in the write_results() method. 
    
    If collapse_identical is True (as in DistinctQuery), query results with 
    identical output lines are collapsed into a single row, i.e. are included 
    in the output only once.

    If collapse_identical is False (as in this subclass), query results with
    identical output lines are always included in the output. """
    collapse_identical = False

class StatisticsQuery(CorpusQuery):
    def __init__(self, corpus, session):
        super(StatisticsQuery, self).__init__("", session, None, None)
        self.Results = self.Session.Corpus.get_statistics()
        
        # convert all values to strings (the Unicode writer needs that):
        self.Results = {key: str(self.Results[key]) for key in self.Results}

    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns):
        for x in sorted(self.Results):
            if options.cfg.gui:
                self.Session.output_storage.append([x, self.Results[x]])
            else:
                output_file.writerow([x, self.Results[x]])

class FrequencyQuery(CorpusQuery):
    def __init__(self, *args):
        super(FrequencyQuery, self).__init__(*args)
        if not options.cfg.experimental:
            self.Session.output_fields.add(LEX_FREQ)
        
    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns, data = None):
        if options.cfg.experimental:
            frequency_filters = []

            # construct that part of output lines that stays constant in all
            # lines:
            if self.InputLine:
                constant_line = copy.copy(self.InputLine)
            else:
                constant_line = []

            # Apply any frequency filter:
            for x in options.cfg.filter_list:
                try:
                    parse = x.parse_filter(x.text)
                except AttributeError:
                    pass
                else:
                    if x.var.lower() == options.cfg.freq_label.lower():
                        frequency_filters.append(x)

            for current_result in self.Results:
                freq = current_result["coq_frequency"]
                fail = False
                for filt in frequency_filters:
                    if not filt.check_number(freq):
                        fail = True
                if not fail:
                    if not options.cfg.case_sensitive:
                        for x in current_result:
                            try:
                                current_result[x] = current_result[x].lower()
                            except AttributeError:
                                pass
                    if constant_line:
                        output_list = copy.copy(constant_line)
                    else:
                        output_list = []

                    if options.cfg.gui:
                        self.Session.output_storage.append(current_result)
                    else:
                        output_list.extend([current_result[x] for x in self.Session.output_order])
                        output_file.writerow(output_list)
            return
        
        # Check if the same query string has been queried in this session.
        # If so, use the cached results:
        
        if self.InputLine:
            constant_line = copy.copy(self.InputLine)
        else:
            constant_line = []

        # construct that part of output lines that stays constant in all
        # lines:
        if options.cfg.show_query:
            constant_line.insert(options.cfg.query_column_number - 1, self.query_string)
        if options.cfg.show_parameters:
            constant_line.append(options.cfg.parameter_string)
        if options.cfg.show_filter:
            constant_line.append(self.source_filter)

        # get from cache, if possible:
        if self.query_string in self.Session._results:
            Lines = self.Session._results[self.query_string]
        else:
            # Collapse all identical lines in the result list:
            Lines = collections.Counter()
            #result_columns = self.Session.get_expected_column_number(max_number_of_token_columns)
            result_columns = QueryResult(self, None).get_expected_length(max_number_of_token_columns)
            for current_result in self.Results:
                # current_result can be None if the query token was not in the
                # lexicon
                if current_result:
                    key = tuple(constant_line + list(current_result.get_row(number_of_token_columns, max_number_of_token_columns, result_columns)))
                    Lines[key] += 1
            if not Lines:
                empty_result = QueryResult(self, {}) 
                Lines[tuple(constant_line + list(empty_result.get_row(number_of_token_columns, max_number_of_token_columns, result_columns)))] = 0
            
            # write to cache:
            self.Session._results[self.query_string] = Lines
        
        if options.cfg.order_frequency:
            data = Lines.most_common()
            get_key = lambda x: x[0]
        else:
            data = Lines
            get_key = lambda x: x

        # Output the collapsed lines:
        for current_line in data:
            key = get_key(current_line)
            # copy constant part of output
            output_list = []
            # add data:
            #print(list(key))
            output_list.extend(list(key))
            # add frequency:
            output_list.append(Lines[key])
            if options.cfg.gui:
                self.Session.output_storage.append(output_list)
            else:
                output_file.writerow(output_list)

class CollocationQuery(TokenQuery):
    def __init__(self, S, Session, token_class, source_filter):
        self.left_span = options.cfg.context_left
        self.right_span = options.cfg.context_right

        self._query_string = S
        # build query string so that the neighbourhood is also queried:
        S = "{}{}{}".format("* " * self.left_span, S, " *" * self.right_span)

        # and then use this string for a normal TokenQuery:
        super(CollocationQuery, self).__init__(S, Session, token_class, source_filter)
        self.Session.output_order = self.Session.header

    def mutual_information(self, f_1, f_2, f_coll, size, span):
        """ Calculate the Mutual Information for two words. f_1 and f_2 are
        the frequencies of the two words, f_coll is the frequency of 
        word 2 in the neighbourhood of word 1, size is the corpus size, and
        span is the size of the neighbourhood in words to the left and right
        of word 2.
        
        Following http://corpus.byu.edu/mutualinformation.asp, MI is 
        calculated as:

            MI = log ( (f_coll * size) / (f_1 * f_2 * span) ) / log (2)
        
        """

        return math.log((f_coll * size) / (f_1 * f_2 * span)) / math.log(2)

    def conditional_propability(self, freq_left, freq_total):
        """ Calculate the conditional probability Pcond to encounter the query 
        token given that the collocate occurred in the left neighbourhood of
        the token.

        Pcond(q | c) = P(c, q) / P(c) = f(c, q) / f(c),
        
        where f(c, q) is the number of occurrences of word c as a left 
        collocate of query token q, and f(c) is the total number of 
        occurrences of c in the corpus. """
        
        return float(freq_left) / float(freq_total)

    def write_results(self, output_file, number_of_token_columns, max_number_of_token_columns, data = None):
        self.Session.output_order = self.Session.header
        count_left = collections.Counter()
        count_right = collections.Counter()
        count_total = collections.Counter()
        
        left_span = options.cfg.context_left
        right_span = options.cfg.context_right

        features = []
        lexicon_features = self.Corpus.resource.get_lexicon_features()
        for rc_feature in options.cfg.selected_features:
            if rc_feature in [x for x, _ in lexicon_features]:
                features.append("coq_{}".format(rc_feature))
            
        corpus_size = self.Corpus.get_corpus_size()
        query_freq = 0
        context_info = {}
        
        for current_result in self.Results:
            query_freq += 1
            # increase the count for all items in the left neighbourhood:
            for i in range(left_span):
                tup = []
                for feature in features:
                    lookup = "{}_{}".format(feature, i+1)
                    # normally, collocations will be case-insensitive, but
                    # the option to heed case is provided:
                    if options.cfg.case_sensitive:
                        tup.append(current_result[lookup])
                    else:
                        tup.append(current_result[lookup].lower())
                count_left[tuple(tup)] += 1
                count_total[tuple(tup)] += 1

                context_info[tuple(tup)] = (
                    current_result["coquery_invisible_corpus_id"],
                    current_result["coquery_invisible_origin_id"],
                    current_result["coquery_invisible_number_of_tokens"])


            # increase the count for all items in the right neighbourhood:
            for i in range(right_span):
                tup = []
                for feature in features:
                    lookup = "{}_{}".format(feature, self.number_of_tokens - left_span +i+1)
                    # normally, collocations will be case-insensitive, but
                    # the option to heed case is provided:
                    if options.cfg.case_sensitive:
                        tup.append(current_result[lookup])
                    else:
                        tup.append(current_result[lookup].lower())
                count_right[tuple(tup)] += 1
                count_total[tuple(tup)] += 1
                context_info[tuple(tup)] = (
                    current_result["coquery_invisible_corpus_id"],
                    current_result["coquery_invisible_origin_id"],
                    current_result["coquery_invisible_number_of_tokens"])

        self.Session.output_order = self.Session.header
        
        S = ""
        for collocate_tuple in count_total:
            try:
                word = collocate_tuple[features.index("coq_word_label")]
            except ValueError:
                try:
                    word = collocate_tuple[features.index("coq_corpus_word")]
                except ValueError:
                    word = ""
            try:
                lemma = collocate_tuple[features.index("coq_word_lemma")]
            except ValueError:
                try:
                    lemma = collocate_tuple[features.index("coq_lemma_label")]
                except ValueError:
                    lemma = ""
            try:
                pos = collocate_tuple[features.index("coq_word_pos")]
            except ValueError:
                try:
                    pos = collocate_tuple[features.index("coq_pos_label")]
                except ValueError:
                    pos  = ""
            if word:
                S = word
            elif lemma:
                S = "[{}]".format(lemma)
            if S and pos:
                S = "{}.[{}]".format(S, pos)
            elif pos:
                S = "[{}]".format(pos)
            coll_freq = self.Corpus.get_frequency(self.token_class(S, self.Corpus.lexicon))
            # build a new token from the tuple:
        
            current_result = {}
            
            current_result["coquery_query_string"] = self._query_string
            for i, feature in enumerate(features):
                feature = feature.partition("_")[2]
                current_result["coq_collocate_{}".format(feature)] = collocate_tuple[i]
            current_result["coq_frequency"] = count_total[collocate_tuple]
            current_result["coq_collocate_frequency"] = coll_freq
            current_result["coq_collocate_frequency_right"] = count_right[collocate_tuple]
            current_result["coq_collocate_frequency_left"] = count_left[collocate_tuple]
            current_result["coq_mutual_information"] = round(self.mutual_information(
                query_freq,
                coll_freq, 
                count_total[collocate_tuple], 
                corpus_size, 
                self.left_span + self.right_span), 3)
            current_result["coq_conditional_probability"] = round(
                self.conditional_propability(count_left[collocate_tuple], coll_freq), 3)
            
            corpus_id, origin_id, number = context_info[collocate_tuple]
            
            current_result["coquery_invisible_corpus_id"] = corpus_id
            current_result["coquery_invisible_origin_id"] = origin_id 
            current_result["coquery_invisible_number_of_tokens"] = number

            if options.cfg.gui:
                self.Session.output_storage.append(current_result)
            else:
                output_list = [current_result[x] for x in self.Session.output_order]
                output_file.writerow(output_list)

    def get_collocates(self):
        """ Run a normal query base on the token string, but pad the query by
        empty queries '*' for each word in the left and right context. This
        query respects the output column selection, so it can be restricted to
        only some parts of the corpus. Also, it can be restricted to lemmas
        and POS tags.
        
        Then, for each neighbourhood column, make a word count: for each word
        in the neighbourhood span, form tuples (based on all selected lexicon
        features), and count how often the tuple occurs. Then, calculate the 
        MI for each tuple. Finally, construct the output rows.
        
        Each output row consists of these columns:
        
        - Query string
        - Collocate tuple (one column for each feature)
        - Collocate frequency
        - Collocate frequency (left)
        - Collocate frequency (right)
        - MI
        
        This output may also be supplemented by other lexical measures, for 
        example, the conditional probability. """
        
        
logger = logging.getLogger(__init__.NAME)

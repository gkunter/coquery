# -*- coding: utf-8 -*-
""" FILENAME: queries.py -- part of Coquery corpus query tool

This module defines classes for query types. """

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
import math

try:
    range = xrange
except NameError:
    pass

import __init__
import collections
import datetime

from errors import *
import tokens
import options

import pandas as pd

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
        """ 
        Check if the text contains a valid filter. 
        
        A filter is valid if it has the form 'x OP y', where x is a resource 
        variable name, OP is a comparison operator, and value is either a 
        string, a number or a list. 
        
        Parameters
        ----------
        s : string
            The text of the filter
            
        Returns
        -------
        b : boolean
            True if the argumnet is a valid filter text, or False otherwise.
        """
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
        """
        Check whether the integer value n is filtered by this filter.
        
        Parameters
        ----------
        n : int
            The value to be checked against the filter
            
        Returns
        -------
        b : boolean
            True if the value is filtered by this filter, or False otherwise.
        """
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
                return n != float(self.value_list[0])
            elif self.operator == "IN":
                return n >= float(self.value_range[0]) and n <= float(self.value_range[1])
        except ValueError:
            return False

class CorpusQuery(object):
    """ 
    This class manages the query string, and is responsible for the output 
    of the query results. 
    """
    
    collapse_identical = True

    def __init__(self, S, Session, token_class):
        self.token_class = token_class
        self.query_list = []
        self.max_number_of_tokens = 0
        repeated_queries = set(tokens.preprocess_query(S))
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
        self.Results = []
        self.InputLine = []
        self.input_header = []
        self.input_frame = pd.DataFrame()

    def __str__(self):
        return " ".join(["{}".format(x) for x in self.tokens])
    
    def __len__(self):
        return len(self.tokens)

    def aggregate_data(self, df):
        """ Aggregate the data frame. """
        return df
    
    def filter_data(self, df):
        """ Apply filters to the data frame. """
        return df
    
    def insert_static_data(self, df):
        """ 
        Insert columns that are constant for each query result in the query.
        
        Static data is the data that is not obtained from the database, but
        is derived from external sources, e.g. the current system time, 
        the other columns in the input file, the query string, etc. 
        
        Parameters
        ----------
        df : DataFrame
            The data frame into which the static data is inserted.
        
        Returns
        -------
        df : DataFrame
            The data frame containing also the static data.
        """
        
        for column in self.Session.output_order:
            if column == "coquery_invisible_number_of_tokens":
                df[column] = self.number_of_tokens
            if column == "coquery_query_string":
                df[column] = self.Session.literal_query_string
            elif column == "coquery_expanded_query_string":
                df[column] = self.query_string
            elif column == "coquery_query_file":
                if options.cfg.input_path:
                    df[column] = options.cfg.input_path
                else:
                    df[column] = ""
            elif column == "coquery_current_date":
                df[column] = datetime.datetime.now().strftime("%Y-%m-%d")
            elif column == "coquery_current_time":
                df[column] = datetime.datetime.now().strftime("%H:%M:%S")
            elif column.startswith("coquery_query_token"):
                n = int(column.rpartition("_")[-1])
                df[column] = self.tokens[n - 1].S
            else:
                # add column labels for the columns in the input file:
                if all([x == None for x in self.input_frame.columns]):
                    # no header in input file, so use X1, X2, ..., Xn:
                    input_columns = [("coq_X{}".format(x), x) for x in range(len(self.input_frame.columns))]
                else:
                    input_columns = [("coq_{}".format(x), x) for x in self.input_frame.columns]
                for df_col, input_col in input_columns:
                    df[df_col] = self.input_frame[input_col][0]
        return df

    def no_result_data_frame(self):
        """
        Return a data frame that represents a query without results.
        
        This method creates a new data frame that contains '<NA>' for all
        output columns that would be filled by data from the data base if the
        query matched any token from the corpus. Columns that contain static
        data, i.e. values that are not provided by the data base, but by 
        Coquery itself (e.g. the query string, the name of the input file),
        the data frame contains the appropriate values.
        
        Returns
        -------
        df : DataFrame
            A data frame with strings '<NA>' in data columns, and appropriate
            values for the static columns.
        """
        df = pd.DataFrame([["<NA>"] * len(self.Session.output_order)], columns=self.Session.output_order)
        df = self.insert_static_data(df)
        return df

    def write_results(self, output_object):
        """ Transform the query results to a pandas DataFrame that is either
        directly written to a CSV file, or stored for later processing in
        the GUI. """
        # turn query results into a pandas DataFrame:
        df = pd.DataFrame(self.Results)
        df = self.insert_static_data(df)

        vis_cols = [x for x in self.Session.output_order if not x.startswith("coquery_invisible")]
        # check if the results table contains rows and columns
        if len(df.index) and len(vis_cols):
            # word and lemma columns are lower-cased, unless requested otherwise:
            if not options.cfg.case_sensitive and len(df.index) > 0:
                for x in df.columns:
                    if x.startswith("coq_word") or x.startswith("coq_lemma"):
                        df[x] = df[x].apply(lambda x: x.lower() if x else x)

            # for DISTINCT query mode, duplicates are dropped from the dataframe:
            if self.collapse_identical:
                df.drop_duplicates(subset=vis_cols, inplace=True)
                df.reset_index(drop=True, inplace=True)
        else:
            # create an empty data frame
            df = pd.DataFrame(columns=vis_cols)

        df = self.aggregate_data(df)
        df = self.filter_data(df)
        if options.cfg.gui:
            # append the data frame to the existing data frame
            self.Session.output_object = self.Session.output_object.append(df)
            self.Session.output_object.fillna("", inplace=True)
        else:
            # write data frame to output_file as a CSV file, using the 
            # current output_separator. Encoding is always "utf-8".
            df[vis_cols].to_csv(output_object, 
                header=None if self.Session.header_shown else [self.Corpus.resource.translate_header(x) for x in vis_cols], 
                sep=options.cfg.output_separator,
                encoding="utf-8",
                index=False)
            # remember that the header columns have already been included in
            # the output so that multiple queries in a single session do not
            # produce multiple headers:
            self.Session.header_shown = True
        return

class TokenQuery(CorpusQuery):
    """ 
    TokenQuery is a subclass of CorpusQuery. 
    
    In this subclass, the attribute collapse_identical is set to False so 
    that :func:`write_results` does not remove the duplicate rows from the
    data frame containing the query results.
    """
    collapse_identical = False

class FrequencyQuery(TokenQuery):
    """ 
    FrequencyQuery is a subclass of TokenQuery.
    
    In this subclass, :func:`write_results` creates an aggregrate table of
    the data frame containing the query results. The results are grouped by 
    all columns that are currently visible. The invisible coulmns are sampled 
    so that each aggregate row contains the first value from each aggregate 
    group. The aggregate table contains an additional column with the lengths
    of the groups as a frequency value.
    
    The aggregated table is also filtered by applying the currently active
    frequency filters.
    """
    
    def aggregate_data(self, df):
        """
        Aggregate the data frame by obtaining the row frequencies for each
        group specified by the visible data columns.
        
        Parameters
        ----------
        df : DataFrame
            The data frame to be aggregated
            
        Returns
        -------
        df : DataFrame
            A new data frame that contains in the column coq_frequency the
            row frequencies of the aggregated groups.
        """
        # get a list of grouping and sampling columns:
        columns = []
        for x in df.columns.values:
            try:
                n = int(x.rpartition("_")[-1])
            except ValueError:
                columns.append(x)
            else:
                if n <= self.number_of_tokens:
                    columns.append(x)

        group_columns = [x for x in columns if not x.startswith("coquery_invisible")]
        sample_columns = [x for x in columns if x not in group_columns]
        
        # Add a frequency column:
        df["coq_frequency"] = 0
        self.Session.output_order.append("coq_frequency")
        
        if len(df.index) == 0:
            df = self.no_result_data_frame()
            df["coq_frequency"] = 0
            return df
        elif len(group_columns) == 0:
            # if no grouping variables are selected, simply return the first
            # row of the data frame together with the total length of the 
            # data frame as the frequency:
            freq = len(df.index)
            df = df.iloc[[0]]
            df["coq_frequency"] = freq
            return df
        else:
            # create a dictionary that contains the aggregate functions for
            # the different columns. For the sampling columns, this function
            # simply returns the first entry in the column, and for the 
            # frequency column, the function returns the length of the 
            # column:
            aggr_dict = {"coq_frequency": len}
            aggr_dict.update(
                {col: lambda x: x.head(1) for col in sample_columns})
            # group the data frame by the group columns, apply the aggregate
            # functions to each group, and return the aggregated data frame:

            gp = df.groupby(group_columns)
            return gp.agg(aggr_dict).reset_index()

    def filter_data(self, df):
        """ 
        Apply the frequency filters to the frequency column. 
        
        Parameters
        ----------
        df : DataFrame
            The data frame to be filtered.

        Returns
        -------
        df : DataFrame
            A new data frame that contains the filtered rows from the 
            argument data frame.
        """
        for filt in options.cfg.filter_list:
            if filt.var == options.cfg.freq_label:
                try:
                    df = df[df["coq_frequency"].apply(filt.check_number)]
                except AttributeError:
                    pass
        return df

class StatisticsQuery(CorpusQuery):
    def __init__(self, corpus, session):
        super(StatisticsQuery, self).__init__("", session, None)
        self.Results = self.Session.Corpus.get_statistics()
        
        # convert all values to strings (the Unicode writer needs that):
        self.Results = {key: str(self.Results[key]) for key in self.Results}

    def write_results(self, output_file):
        df = pd.DataFrame({"Variable": list(self.Results.keys()), "Value": list(self.Results.values())})[["Variable", "Value"]].sort("Variable")
        #for x in sorted(self.Results):
            #if options.cfg.gui:
                #self.Session.output_storage.append([x, self.Results[x]])
            #else:
                #output_file.writerow([x, self.Results[x]])

        if options.cfg.gui:
            # append the data frame to the existing data frame
            self.Session.output_object = pd.concat([self.Session.output_object, df])
        else:
            # write data frame to output_file as a CSV file, using the 

            df.to_csv(self.Session.output_object, 
                header=None if self.Session.header_shown else df.columns.values, 
                sep=options.cfg.output_separator,
                encoding="utf-8",
                index=False)
            # remember that the header columns have already been included in
            # the output so that multiple queries in a single session do not
            # produce multiple headers:
            self.Session.header_shown = True
        return

class CollocationQuery(TokenQuery):
    def __init__(self, S, Session, token_class):
        self.left_span = options.cfg.context_left
        self.right_span = options.cfg.context_right

        self._query_string = S
        # build query string so that the neighbourhood is also queried:
        S = "{}{}{}".format("* " * self.left_span, S, " *" * self.right_span)

        # and then use this string for a normal TokenQuery:
        super(CollocationQuery, self).__init__(S, Session, token_class)
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

    def write_results(self, output_file):
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

        df = pd.DataFrame(self.Results)

        # FIXME: Be more generic than always using coq_word_label!
        fix_col = ["coquery_invisible_corpus_id", 
                   "coquery_invisible_origin_id"]
        left_cols = ["coq_word_label_{}".format(x + 1) for x in range(options.cfg.context_left)]
        right_cols = ["coq_word_label_{}".format(x + self.number_of_tokens - options.cfg.context_right + 1) for x in range(options.cfg.context_right)]
        left_context_span = df[fix_col + left_cols]
        right_context_span = df[fix_col + right_cols]

        left = left_context_span[left_cols].stack().value_counts()
        right = right_context_span[right_cols].stack().value_counts()

        all_words = set(left.index + right.index)
        
        left = left.reindex(all_words).fillna(0)
        right = right.reindex(all_words).fillna(0)
        
        collocates = pd.concat([left, right], axis=1)
        collocates = collocates.reset_index()
        collocates.columns = ["coq_word_label", "coq_collocate_frequency_left", "coq_collocate_frequency_right"]
        collocates["coq_collocate_frequency"] = collocates.sum(axis=1)
        collocates["coq_frequency"] = collocates["coq_word_label"].apply(self.Corpus.get_frequency)
        collocates["coquery_query_string"] = self._query_string
        
        self.Session.output_order = collocates.columns.values

        if options.cfg.gui:
            # append the data frame to the existing data frame
            self.Session.output_object = pd.concat([self.Session.output_object, collocates])
        else:
            # write data frame to output_file as a CSV file, using the 
            # current output_separator. Encoding is always "utf-8".
            collocates[vis_cols].to_csv(output_object, 
                header=None if self.Session.header_shown else [self.Corpus.resource.translate_header(x) for x in vis_cols], 
                sep=options.cfg.output_separator,
                encoding="utf-8",
                index=False)
            # remember that the header columns have already been included in
            # the output so that multiple queries in a single session do not
            # produce multiple headers:
            self.Session.header_shown = True
        return

        
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
            
            current_result["coquery_query_string"] = self.Session.literal_query_string
            for i, feature in enumerate(features):
                feature = feature.partition("_")[2]
                current_result["coq_collocate_{}".format(feature)] = collocate_tuple[i]
            current_result["coq_frequency"] = count_total[collocate_tuple]
            current_result["coq_collocate_frequency"] = coll_freq
            current_result["coq_collocate_frequency_right"] = count_right[collocate_tuple]
            current_result["coq_collocate_frequency_left"] = count_left[collocate_tuple]
            try:
                current_result["coq_mutual_information"] = round(self.mutual_information(
                    query_freq,
                    coll_freq, 
                    count_total[collocate_tuple], 
                    corpus_size, 
                    self.left_span + self.right_span), 3)
            except ZeroDivisionError:
                current_result["coq_mutual_information"] = "<NA>"
            try:
                current_result["coq_conditional_probability"] = round(
                    self.conditional_propability(count_left[collocate_tuple], coll_freq), 3)
            except ZeroDivisionError:
                current_result["coq_conditional_probability"] = "<NA>"
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

# -*- coding: utf-8 -*-
""" FILENAME: queries.py -- part of Coquery corpus query tool

This module defines classes for query types. """

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
import math
import re

try:
    range = xrange
except NameError:
    pass

import __init__
import collections
import datetime

try:
    from numba import jit
except ImportError:
    def jit(f):
        def inner(f, *args):
            return f(*args)
        return lambda *args: inner(f, *args)
        
import pandas as pd

from errors import *
import tokens
import options

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

class TokenQuery(object):
    """ 
    This class manages the query string, and is responsible for the output 
    of the query results. 
    """
    def __init__(self, S, Session, token_class):
        self.token_class = token_class
        self.query_list = tokens.preprocess_query(S)
        self.query_string = S
        self.Session = Session
        self.Corpus = Session.Corpus
        self.Results = []
        self.input_frame = pd.DataFrame()
        self.results_frame = pd.DataFrame()

    def __str__(self):
        return " ".join(["{}".format(x) for x in self.tokens])
    
    def __len__(self):
        return len(self.tokens)

    @staticmethod
    def aggregate_data(df, resource):
        """ Aggregate the data frame. """
        return df
    
    @staticmethod
    def filter_data(df):
        """ Apply filters to the data frame. """
        return df
    
    def run(self):
        """
        Run the query, and store the results in an internal data frame.
        
        This method runs all required subqueries for the query string, e.g.
        the quantified queries if quantified tokens are used. The results are 
        stored in self.results_frame.
        """
        self.results_frame = pd.DataFrame()
        
        for self._sub_query in self.query_list:
            self._current_number_of_tokens = len(self._sub_query)
            self._current_subquery_string = " ".join(["%s" % x for _, x in self._sub_query])
            
            df = pd.DataFrame(
                self.Corpus.yield_query_results(self, self._sub_query))
            df = self.insert_static_data(df)
            self.add_output_columns()

            if not options.cfg.case_sensitive and len(df.index) > 0:
                for x in df.columns:
                    if x.startswith("coq_word") or x.startswith("coq_lemma"):
                        df[x] = df[x].apply(lambda x: x.lower() if x else x)
            df = self.apply_functions(df)

            if self.results_frame.empty:
                self.results_frame = df
            else:
                self.results_frame = self.results_frame.append(df)

    def append_results(self, df):
        """
        Append the last results to the data frame.
        
        Parameters
        ----------
        df : pandas.DataFrame
            The data frame to which the last query results will be added.
        """
        if df.empty:
            return self.results_frame
        else:
            return df.append(self.results_frame)

    def get_max_tokens(self):
        """
        Return the maximum number of tokens that this query produces.
        
        The maximum number of tokens is determined by the number of token
        strings, modified by the quantifiers. For each query, query_list 
        contains the quantified sub-queries. The maximum number of tokens is
        the maximum of number_of_tokens for these sub-queris.
        
        Returns
        -------
        maximum : int
            The maximum number of tokens that may be produced by this query.
        """
        maximum = 0
        for token_list in self.query_list:
            maximum = max(maximum, len(token_list))
        return maximum
    
    def get_token_numbering(self, n):
        """
        Create a suitable number label for the nth lexical column.

        If the specified column was not created by a quantified query token,
        or if the maximum quantificatin of that query token was 1, the label
        will correspond to the query token number. Otherwise, it will take
        the form "x.y", where x is the query token number, and y is the 
        repetition number of that query token.
        
        If the quantified columns are not aligned (i.e. if 
        options.cfg.align_quantified is not set), this function simply 
        returns a string representation of n.
        
        Parameters
        ----------
        n : int 
            An lexical output column number
        
        Returns
        -------
        s : string
            A string representing a suitable number label
        """
        if not options.cfg.align_quantified:
            return "{}".format(n + 1)
        L = []
        current_pos = 0
        for i, x in enumerate(self.query_string.split(" ")):
            _, _, length = tokens.get_quantifiers(x)
            if length == 1:
                L.append("{}".format(i+1))
            else:
                for y in range(length):
                    L.append("{}.{}".format(i + 1, y + 1))
        return L[n]
    
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
                df[column] = self._current_number_of_tokens
            if column == "coquery_query_string":
                df[column] = self.query_string
            elif column == "coquery_expanded_query_string":
                df[column] = self._current_subquery_string
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
                token_list = self.query_string.split() 
                n = int(column.rpartition("_")[-1])
                # construct a list with the maximum number of quantified
                # token repetitions. This is used to look up the query token 
                # string.
                L = []
                for x in token_list:
                    token, _, length = tokens.get_quantifiers(x)
                    L += [token] * length
                try:
                    df[column] = L[n-1]
                except IndexError:
                    df[column] = ""
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

    def apply_functions(self, df):
        """
        Applies the selected functions to the data frame.
        
        This method applies the functions that were selected as output 
        columns to the associated column from the data frame. The result of 
        each function is added as a new column to the data frame. The name 
        of this column takes the form
        
        coq_func_{resource}_{n},
        
        where 'resource' is the resource feature on which the function was 
        applied, and 'n' is the count of that function. For example, the 
        results from the first function that was applied on the resource 
        feature 'word_label' is stored in the column 'coq_func_word_label_1',
        the second function on that feature in 'coq_func_word_label_2', and
        so on. 
        
        Parameters
        ----------
        df : DataFrame
            The data frame on which the selected function will be applied.
        
        Returns
        -------
        df : DataFrame
            The data frame with new columns for each function.
        """
        
        func_counter = collections.Counter()
        for x in options.cfg.selected_functions:
            resource = x.rpartition(".")[-1]
            func_counter[resource] += 1
            name = "coq_func_{}_{}".format(resource, func_counter[resource])
            df[name] = df[name].apply(options.cfg.selected_functions[x])
        return df

    def add_output_columns(self):
        """
        Add any column that is specific to this query type to the list of 
        output columns in Session.output_order.
        
        This is needed, for example, to add the frequency column in
        FrequencyQuery.
        """
        return
 
    @classmethod
    def aggregate_it(cls, df, resource):
        agg = cls.aggregate_data(df, resource)
        agg = cls.filter_data(agg)
        
        agg_cols = list(agg.columns.values)
        for col in list(agg_cols):
            if col.startswith("coquery_invisible"):
                agg_cols.remove(col)
                agg_cols.append(col)
        agg = agg[agg_cols]
        return agg

class DistinctQuery(TokenQuery):
    """ 
    DistinctQuery is a subclass of TokenQuery. 
    
    This subclass reimplements :func:`aggregate_data` so that duplicate rows 
    are removed.
    """

    #@jit
    @classmethod
    def aggregate_data(cls, df, resource):
        vis_cols = [x for x in list(df.columns.values) if not x.startswith("coquery_invisible")]
        #vis_cols = [x for x in cls.Session.output_order if not x.startswith("coquery_invisible")]
        df = df.drop_duplicates(subset=vis_cols)
        df = df.reset_index(drop=True)
        return df

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
    
    def add_output_columns(self):
        self.Session.output_order.append("coq_frequency")
        
    @staticmethod
    def do_the_grouping(df, group_columns, aggr_dict):
        gp = df.fillna("").groupby(group_columns, sort=False)
        return gp.agg(aggr_dict).reset_index()
    
    @classmethod
    def aggregate_data(cls, df, resource):
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
                #if n <= self._current_number_of_tokens:
                columns.append(x)

        group_columns = [x for x in columns if not x.startswith("coquery_invisible")]
        sample_columns = [x for x in columns if x not in group_columns]
        
        # Add a frequency column:
        df["coq_frequency"] = 0
        
        if len(df.index) == 0:
            result = pd.DataFrame({"coq_frequency": [0]})
            #result = self.insert_static_data(pd.DataFrame(), resource)
        elif len(group_columns) == 0:
            # if no grouping variables are selected, simply return the first
            # row of the data frame together with the total length of the 
            # data frame as the frequency:
            freq = len(df.index)
            df = df.iloc[[0]]
            result = df 
            result["coq_frequency"] = freq
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

            result = cls.do_the_grouping(df, group_columns, aggr_dict)
        if "coquery_relative_frequency" in options.cfg.selected_features:
            total_frequency = result.coq_frequency.sum()
            result["coquery_relative_frequency"] = result["coq_frequency"].apply(
                lambda x: x / total_frequency)

        if "coquery_per_million_words" in options.cfg.selected_features:
            corpus_size = resource.get_corpus_size()
            result["coquery_per_million_words"] = result["coq_frequency"].apply(
                lambda x: x / (corpus_size / 1000000))
            
        return result

    @staticmethod
    def filter_data(df):
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

class StatisticsQuery(TokenQuery):
    def __init__(self, corpus, session):
        super(StatisticsQuery, self).__init__("", session, None)
        self.Results = self.Session.Corpus.get_statistics()
        
        # convert all values to strings (the Unicode writer needs that):
        self.Results = {key: str(self.Results[key]) for key in self.Results}

    def write_results(self, output_file):
        df = pd.DataFrame({"Variable": list(self.Results.keys()), "Value": list(self.Results.values())})[["Variable", "Value"]].sort("Variable")

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
    @staticmethod
    def filter_data(df):
        """ 
        Apply the frequency filters to the collocate frequency column. 
        
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
                    df = df[df["coq_collocate_frequency"].apply(filt.check_number)]
                except AttributeError:
                    pass
        return df

    def __init__(self, S, Session, token_class):
        self.left_span = options.cfg.context_left
        self.right_span = options.cfg.context_right
        
        if not self.left_span and not self.right_span:
            raise CollocationNoContextError

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
        try:
            MI = math.log((f_coll * size) / (f_1 * f_2 * span)) / math.log(2)
        except (ZeroDivisionError, TypeError):
            return None
        return MI

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
            
        self.corpus_size = self.Corpus.get_corpus_size()
        query_freq = 0
        context_info = {}

        df = pd.DataFrame(self.Results)

        fix_col = ["coquery_invisible_corpus_id"]

        # FIXME: Be more generic than always using coq_word_label!
        left_cols = ["coq_word_label_{}".format(x + 1) for x in range(options.cfg.context_left)]
        right_cols = ["coq_word_label_{}".format(x + self.number_of_tokens - options.cfg.context_right + 1) for x in range(options.cfg.context_right)]
        left_context_span = df[fix_col + left_cols]
        right_context_span = df[fix_col + right_cols]
        if not options.cfg.case_sensitive:
            for column in left_cols:
                left_context_span[column] = left_context_span[column].apply(lambda x: x.lower())
            for column in right_cols:
                right_context_span[column] = right_context_span[column].apply(lambda x: x.lower())

        left = left_context_span[left_cols].stack().value_counts()
        right = right_context_span[right_cols].stack().value_counts()

        # Build a lookup table for contexts. This table is used to provide
        # the corpus_id to the collocations table so that # the entries can 
        # be clicked to see an example of that collocation.
        # The lookup table is basically a long data frame containing all
        # collocate words 
        lookup_header = ["coq_word_label", "coquery_invisible_corpus_id"]
        lookup = pd.DataFrame(columns=lookup_header)
        for i in range(1, left_span + 1):
            tmp_table = df[["coq_word_label_{}".format(i),"coquery_invisible_corpus_id"]]
            col = tmp_table.columns.values
            col[0] = "coq_word_label"
            tmp_table.columns = col
            lookup = lookup.append(tmp_table)
        for i in range(self.number_of_tokens + 1 - right_span, self.number_of_tokens + 1):
            tmp_table = df[["coq_word_label_{}".format(i),"coquery_invisible_corpus_id"]]
            col = tmp_table.columns.values
            col[0] = "coq_word_label"
            tmp_table.columns = col
            lookup = lookup.append(tmp_table)
        lookup["coquery_invisible_number_of_tokens"] = self.number_of_tokens

        all_words = set(left.index + right.index)
        
        left = left.reindex(all_words).fillna(0).astype(int)
        right = right.reindex(all_words).fillna(0).astype(int)
        
        collocates = pd.concat([left, right], axis=1)
        collocates = collocates.reset_index()
        collocates.columns = ["coq_word_label", "coq_collocate_frequency_left", "coq_collocate_frequency_right"]
        collocates["coq_collocate_frequency"] = collocates.sum(axis=1)
        collocates["coq_frequency"] = collocates["coq_word_label"].apply(self.Corpus.get_frequency)
        collocates["coquery_query_string"] = self._query_string
        collocates["coq_conditional_probability"] = collocates.apply(
            lambda x: self.conditional_propability(
                x["coq_collocate_frequency_left"],
                x["coq_frequency"]) if x["coq_frequency"] else None, 
            axis=1)
        
        collocates["coq_mutual_information"] = collocates.apply(
            lambda x: self.mutual_information(
                    f_1=len(df.index),
                    f_2=x["coq_frequency"], 
                    f_coll=x["coq_collocate_frequency"],
                    size=self.corpus_size, 
                    span=self.left_span + self.right_span),
            axis=1)

        collocates = collocates.merge(lookup, on="coq_word_label", how="left")
        
        collocates = collocates.dropna()
        
        self.Session.output_order = collocates.columns.values

        collocates = self.filter_data(collocates)
        aggregate = collocates.drop_duplicates(subset="coq_word_label")

        if options.cfg.gui:
            # append the data frame to the existing data frame
            self.Session.data_table = collocates
            self.Session.output_object = pd.concat([self.Session.output_object, aggregate])
        else:
            # write data frame to output_file as a CSV file, using the 
            # current output_separator. Encoding is always "utf-8".
            collocates[vis_cols].to_csv(output_object, 
                header=None if self.Session.header_shown else [self.Session.translate_header(x) for x in vis_cols], 
                sep=options.cfg.output_separator,
                encoding=options.cfg.output_encoding,
                index=False)
            # remember that the header columns have already been included in
            # the output so that multiple queries in a single session do not
            # produce multiple headers:
            self.Session.header_shown = True
        
logger = logging.getLogger(__init__.NAME)

# -*- coding: utf-8 -*-
"""
queries.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import math
import re

try:
    range = xrange
except NameError:
    pass

import collections
import datetime

try:
    from numba import jit
except (ImportError, OSError):
    def jit(f):
        def inner(f, *args):
            return f(*args)
        return lambda *args: inner(f, *args)

import numpy as np        
import pandas as pd

from .defines import *
from .errors import *
from . import corpus
from . import tokens
from . import options

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
            raise RuntimeError(msg_invalid_filter.format(s))
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
        variable_names = [name.lower() for  _, name in self.resource.get_corpus_features() + [("statistics_frequency", "freq")]]
        if var.lower() not in variable_names:
            return False
        if variable_names.count(var.lower()) > 1:
            logger.warning("Query filter may be ambiguous: {}".format(s))
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
    def __init__(self, S, Session):
        self.query_list = tokens.preprocess_query(S)
        self.query_string = S
        self.Session = Session
        self.Resource = Session.Resource
        self.Corpus = Session.Corpus
        self.Results = []
        self.input_frame = pd.DataFrame()
        self.results_frame = pd.DataFrame()
        TokenQuery.filter_list = Session.filter_list
        self._keys = []

    def string_folder(self, results):
        """
        Yield the rows from the results with all string values folded.

        This folder is used in yield_query_results, and helps to reduce the
        amount of memory consumed by the query results data frames. It does 
        so by keeping a map of string values so that each occurrence of a 
        string in the query result is mapped to the identical string object,
        and not to a new string object with the same content. 
        
        This string folder is based on:
        http://www.mobify.com/blog/sqlalchemy-memory-magic/
        """
        string_map = {}
        self._keys = []
        for row in results:
            self._keys = row.keys()
            l = []
            for key, value in row.items():
                if isinstance(value, str):
                    s = string_map.get(value, None)
                    if s is None:
                        s = string_map[value] = value
                    l.append(s)
                else:
                    l.append(value)
            yield l

    def __len__(self):
        return len(self.tokens)

    @staticmethod
    def aggregate_data(df, resource, **kwargs):
        """ Aggregate the data frame. """
        return df
    
    @staticmethod
    def filter_data(df, filter_list):
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
        
        self._max_number_of_tokens = 0
        for x in self.query_list:
            self._max_number_of_tokens = max(self._max_number_of_tokens, len(x))
        
        for i, self._sub_query in enumerate(self.query_list):
            self._current_number_of_tokens = len(self._sub_query)
            self._current_subquery_string = " ".join(["%s" % x for _, x in self._sub_query])

            if len(self.query_list) > 1:
                logger.info("Subquery #{} of {}: {}".format(i+1, len(self.query_list), self._current_subquery_string))

            if self.Resource.db_type == SQL_SQLITE:
                # SQLite: keep track of databases that need to be attached. 
                self.Resource.attach_list = set([])
                # This list is filled by get_query_string().
            
            # This SQLAlchemy optimization including the string folder 
            # is based on http://www.mobify.com/blog/sqlalchemy-memory-magic/
            query_string = self.Resource.get_query_string(self, self._sub_query)
            
            with self.Resource.get_engine().connect() as connection:
                if not query_string:
                    df = pd.DataFrame()
                else:
                    if options.cfg.verbose:
                        logger.info(query_string)
                    
                    # SQLite: attach external databases
                    if self.Resource.db_type == SQL_SQLITE:
                        for db_name in self.Resource.attach_list:
                            path = os.path.join(options.cfg.database_path, "{}.db".format(db_name))
                            S = "ATTACH DATABASE '{}' AS {}".format(path, db_name)
                            connection.execute(S)

                    try:
                        results = connection.execution_options(stream_results=True).execute(query_string.replace("%", "%%"))
                    except Exception as e:
                        connection.close()
                        print(query_string)
                        print(e)
                        raise e
                    df = pd.DataFrame(self.string_folder(results))
                    if not len(df.index):
                        df = pd.DataFrame(columns=results.keys())
                    else:
                        df.columns = results.keys()
                    results = None

                df = self.insert_static_data(df)
                df = self.insert_context(df, connection)
                connection.close()
                self.add_output_columns(self.Session)

            if not options.cfg.output_case_sensitive and len(df.index) > 0:
                for x in df.columns:
                    word_column = getattr(self.Resource, QUERY_ITEM_WORD, None)
                    lemma_column = getattr(self.Resource, QUERY_ITEM_LEMMA, None)
                    if ((word_column and word_column in x) or 
                        (lemma_column and lemma_column in x)):
                        try:
                            if options.cfg.output_to_lower:
                                df[x] = df[x].apply(lambda x: x.lower() if x else x)
                            else:
                                df[x] = df[x].apply(lambda x: x.upper() if x else x)

                        except AttributeError:
                            pass
            df = self.apply_functions(df)
            if not df.empty:
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
            
        Returns
        -------
        df : pandas.DataFrame
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
        if n > len(L) - 1:
            return n
        return L[n]
    
    def insert_context(self, df, connection):
        def insert_kwic(row):
            row["coq_context_left"] = corpus.collapse_words(row[left_columns])
            row["coq_context_right"] = corpus.collapse_words(row[right_columns])
            return row

        def insert_string(row):
            row["coq_context_string"] = corpus.collapse_words(
                list(row[left_columns]) + 
                [x.upper() if hasattr(x, "upper") else x for x in list(row[target_columns])] + 
                list(row[right_columns]))
            return row
        
        def insert_columns(row):
            left, target, right = self.Session.Resource.get_context(
                row["coquery_invisible_corpus_id"], 
                row["coquery_invisible_origin_id"],
                self._current_number_of_tokens, True, connection)
            for i in range(len(left)):
                row["coq_context_lc{}".format(len(left) - i)] = left[i]
            for i in range(len(right)):
                row["coq_context_rc{}".format(i + 1)] = right[i]
            if options.cfg.context_mode == CONTEXT_STRING:
                if word_feature not in options.cfg.selected_features:
                    for i in range(len(target)):
                        row["coq_context_t{}".format(i + 1)] = target[i]

            return row

        if not options.cfg.token_origin_id:
            return df
        if options.cfg.context_mode == CONTEXT_NONE:
            return df
        if not (options.cfg.context_left or options.cfg.context_right):
            return df
        if not hasattr(self.Session.Resource, QUERY_ITEM_WORD):
            return df
        else:
            word_feature = getattr(self.Session.Resource, QUERY_ITEM_WORD)
        
        df = df.apply(insert_columns, axis=1)        
        
        if options.cfg.context_mode == CONTEXT_KWIC:
            left_columns = ["coq_context_lc{}".format(options.cfg.context_left - x) for x in range(options.cfg.context_left)]
            right_columns = ["coq_context_rc{}".format(x + 1) for x in range(options.cfg.context_right)]
            df = df.apply(insert_kwic, axis=1)

        elif options.cfg.context_mode == CONTEXT_STRING:
            left_columns = ["coq_context_lc{}".format(options.cfg.context_left - x) for x in range(options.cfg.context_left)]
            right_columns = ["coq_context_rc{}".format(x + 1) for x in range(options.cfg.context_right)]
            #if word_feature in options.cfg.selected_features:
                #target_columns = ["coq_{}_{}".format(word_feature, x + 1) for x in range(self._current_number_of_tokens)]
            #else:
                #target_columns = ["coq_context_t{}".format(x + 1) for x in range(self._current_number_of_tokens)]
            if word_feature in options.cfg.selected_features:
                target_columns = ["coq_{}_{}".format(word_feature, x + 1) for x in range(self._max_number_of_tokens)]
            else:
                target_columns = ["coq_context_t{}".format(x + 1) for x in range(self._max_number_of_tokens)]
            df = df.apply(insert_string, axis=1)
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
        if "statistics_query_entropy" in self.Session.output_order or "statistics_query_proportion" in self.Session.output_order:
            columns = [x for x in df.columns if not x.startswith("coquery_invisible")]
            if not columns:
                self.freqs = pd.DataFrame(
                    {"statistics_frequency": [len(df.index)],
                     "statistics_query_proportion": [1]})
                self.entropy = 0
            else:
                # get a frequency table for the current data frame:
                if options.cfg.output_case_sensitive:
                    self.freqs = df.groupby(columns).count().reset_index()
                else:
                    df2 = df
                    for column in df2.columns:
                        word_column = getattr(self.Resource, QUERY_ITEM_WORD, None)
                        lemma_column = getattr(self.Resource, QUERY_ITEM_LEMMA, None)
                        if ((word_column and word_column in column) or 
                            (lemma_column and lemma_column in column)) and df2[column].dtype == object:
                            if options.cfg.output_to_lower:
                                df2[column] = df2[column].str.lower()
                            else:
                                df2[column] = df2[column].str.upper()
                    self.freqs = df2.groupby(columns).count().reset_index()
                columns.append("statistics_frequency")
                self.freqs.columns = columns
                columns.remove("statistics_frequency")
                # calculate the propabilities of the different results:
                self.freqs["statistics_query_proportion"] = self.freqs.statistics_frequency.divide(len(df.index))
                if len(self.freqs.index) == 1:
                    self.entropy = 0
                else:
                    self.entropy = -self.freqs.statistics_query_proportion.apply(lambda x: x * math.log(x, 2)).sum()


        
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
            elif column == "statistics_query_entropy":
                df[column] = self.entropy
            elif column == "statistics_query_proportion":
                try:
                    df = pd.merge(df, self.freqs, on=columns)
                except ValueError:
                    df[column] = self.freqs[column]
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
        
        # If the data frame is empty, no function can be applied anyway:
        if df.empty:
            return df

        lexicon_features = [x for x, _ in self.Resource.get_lexicon_features()]

        func_counter = collections.Counter()
        for rc_feature, fun, _ in options.cfg.selected_functions:
            _, db, table, feature = self.Resource.split_resource_feature(rc_feature)
            if db != self.Resource.db_name:
                resource = "{}_{}_{}".format(db, table, feature)
            else:
                resource = "{}_{}".format(table, feature)
            func_counter[resource] += 1
            fc = func_counter[resource]
                        
            # handle functions added to lexicon features:
            if self.Resource.is_lexical(rc_feature):
                for n in range(self.get_max_tokens()):
                    new_name = "coq_func_{}_{}_{}".format(resource, fc, n + 1)
                    col_name = "coq_{}_{}".format(resource, n + 1)
                    df[new_name] = df[col_name].apply(fun)
            # handle other functions:
            else:
                new_name = "coq_func_{}_{}_1".format(resource, fc)
                col_name = "coq_{}_1".format(resource)
                df[new_name] = df[col_name].apply(fun)
        return df

    @staticmethod
    def add_output_columns(session):
        """
        Add any column that is specific to this query type to the list of 
        output columns in Session.output_order.
        
        This is needed, for example, to add the frequency column in
        FrequencyQuery.
        """
        return

    @staticmethod
    def remove_output_columns(session):
        """
        Remove any column that was added by add_output_columns from the
        current session's output_order list.
        
        This is needed when changing the aggregation mode.
        """
        return
 
    @classmethod
    def aggregate_it(cls, df, resource, **kwargs):
        agg = cls.aggregate_data(df, resource, **kwargs)
        #agg = cls.filter_data(agg, cls.filter_list)
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

    @classmethod
    def aggregate_data(cls, df, resource, **kwargs):
        vis_cols = [x for x in list(df.columns.values) if not x.startswith("coquery_invisible") and x in kwargs["session"].output_order and
                    options.cfg.column_visibility.get(x, True)]
        try:
            df = df.drop_duplicates(subset=vis_cols)
        except ValueError:
            # ValueError is raised if df is empty
            pass
        df = df.reset_index(drop=True)
        return df

class FrequencyQuery(TokenQuery):
    """ 
    FrequencyQuery is a subclass of TokenQuery.
    
    In this subclass, :func:`aggregate_data` creates an aggregrate table of
    the data frame containing the query results. The results are grouped by 
    all columns that are currently visible. The invisible coulmns are sampled 
    so that each aggregate row contains the first value from each aggregate 
    group. The aggregate table contains an additional column with the lengths
    of the groups as a frequency value.
    """
    
    @staticmethod
    def add_output_columns(session):
        if "statistics_frequency" not in session.output_order:
            session.output_order.append("statistics_frequency")

    @staticmethod
    def remove_output_columns(session):
        try:
            session.output_order.remove("statistics_frequency")
        except ValueError:
            pass
        
    @staticmethod
    def do_the_grouping(df, group_columns, aggr_dict):
        gp = df.fillna("").groupby(group_columns, sort=False)
        return gp.agg(aggr_dict).reset_index()
    
    @classmethod
    def aggregate_data(cls, df, resource, **kwargs):
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
        
        # Drop frequency column if it is already in the data frame (this is
        # needed for re-aggregation):
        
        if "statistics_frequency" in list(df.columns.values):
            df.drop("statistics_frequency", axis=1, inplace=True)
        if "statistics_overall_entropy" in list(df.columns.values):
            df.drop("statistics_overall_entropy", axis=1, inplace=True)
        if "statistics_overall_proportion" in list(df.columns.values):
            df.drop("statistics_overall_proportion", axis=1, inplace=True)

        columns = []
        for x in df.columns.values:
            if x in kwargs["session"].output_order:
                try:
                    n = int(x.rpartition("_")[-1])
                except ValueError:
                    columns.append(x)
                else:
                    columns.append(x)

        # Group by those columns which are neither intrinsically invisible 
        # nor currently hidden:
        group_columns = [x for x in columns if not x.startswith("coquery_invisible") and options.cfg.column_visibility.get(x, True)]
        sample_columns = [x for x in columns if x not in group_columns]
        # Add a frequency column:
        df["statistics_frequency"] = 0
        
        if len(df.index) == 0:
            result = pd.DataFrame({"statistics_frequency": [0]})
        elif len(group_columns) == 0:
            # if no grouping variables are selected, simply return the first
            # row of the data frame together with the total length of the 
            # data frame as the frequency:
            freq = len(df.index)
            df = df.iloc[[0]]
            result = df 
            result["statistics_frequency"] = freq
        else:
            # create a dictionary that contains the aggregate functions for
            # the different columns. For the sampling columns, this function
            # simply returns the first entry in the column, and for the 
            # frequency column, the function returns the length of the 
            # column:
            aggr_dict = {"statistics_frequency": len}
            aggr_dict.update(
                {col: lambda x: x.iloc[0] for col in sample_columns})
            # group the data frame by the group columns, apply the aggregate
            # functions to each group, and return the aggregated data frame:
            result = cls.do_the_grouping(df, group_columns, aggr_dict)

        if "statistics_per_million_words" in options.cfg.selected_features:
            corpus_size = resource.get_corpus_size()
            result["statistics_per_million_words"] = result["statistics_frequency"].apply(
                lambda x: x / (corpus_size / 1000000))

        result["statistics_overall_proportion"] = result.statistics_frequency.divide(result.statistics_frequency.sum())
        if len(result.index) == 1:
            result["statistics_overall_entropy"] = 0
        else:
            result["statistics_overall_entropy"] = -result.statistics_overall_proportion.apply(lambda x: x * math.log(x, 2)).sum()

        # entries with no corpus_id are the result of empty frequency 
        # queries. Their frequency is set to zero:
        try:
            result.statistics_frequency[result.coquery_invisible_corpus_id == ""] = 0
        except (TypeError, AttributeError):
            pass

        return result

class ContingencyQuery(TokenQuery):
    """ 
    ContingencyQuery is a subclass of TokenQuery.
    
    In this subclass, :func:`aggregate_data` creates an aggregrate table of
    the data frame containing the query results. The results are grouped so
    that a contingency table is produced.
    """

    @staticmethod
    def add_output_columns(session):
        if not hasattr(session, "_old_output_order"):
            session._old_output_order = list(session.output_order)
        if hasattr(session, "_contingency_order"):
            session.output_order = list(session._contingency_order)

    @staticmethod
    def remove_output_columns(session):
        session._contingency_order = list(session.output_order)
        session.output_order = list(session._old_output_order)
    
    @classmethod
    def aggregate_data(cls, df, resource, **kwargs):
        """
        Parameters
        ----------
        df : DataFrame
            The data frame to be aggregated
            
        Returns
        -------
        result : DataFrame
        """
        
        if not len(df.index):
            kwargs["session"].output_order += ["statistics_column_total"]
            return pd.DataFrame(columns=kwargs["session"].output_order)
        
        if hasattr(kwargs["session"], "_old_output_order"):
            kwargs["session"].output_order = list(kwargs["session"]._old_output_order)

        if options.cfg.main_window:
            output_order = kwargs["session"].output_order
            tab = getattr(options.cfg.main_window, "table_model", None)
            if tab:
                header = options.cfg.main_window.ui.data_preview.horizontalHeader()
                logical_header = [tab.header[header.logicalIndex(i)] for i in range(header.count())]
                logical_header = [x for x in logical_header if x.startswith("coq")]
                for x in output_order:
                    if x not in logical_header:
                        logical_header.append(x)
                if logical_header:
                    output_order = logical_header
            kwargs["session"].output_order = output_order

        columns = []
        for x in kwargs["session"].output_order:
            if not x.startswith("coquery_invisible") and options.cfg.column_visibility.get(x, True):
                columns.append(x)

        row_columns = columns[:-1]
        row_list = [df[x] for x in row_columns if x in df.columns]

        if len(columns) == 0:
            result = pd.DataFrame({"statistics_column_total": [len(df.index)]})
        elif len(columns) > 1:
            col_column = columns[-1]
            result = pd.crosstab(row_list, df[col_column], margins=True).reset_index()
            kwargs["session"].output_order.remove(col_column)
            new_columns = list(result.columns)
            for i in range(len(row_columns), len(new_columns) - 1):
                col_label = "{}: {}".format(
                    kwargs["session"].translate_header(col_column), new_columns[i])
                new_columns[i] = col_label
                kwargs["session"].output_order.append(col_label)
            new_columns[-1] = "statistics_column_total"
            result.columns = new_columns  
            result
        else:
            col_column = ""
            result = pd.crosstab(df[columns[0]], columns=[], margins=True).reset_index()
            result.columns = [columns[0], "statistics_column_total"]

        if len(columns):
            #for x in columns[:-1]:
                #result[x][len(result.index)-1] = "---"
            result[result.columns[0]][len(result.index)-1] = COLUMN_NAMES["statistics_column_total"]

        kwargs["session"].output_order.append("statistics_column_total")
        return result.fillna("")

class StatisticsQuery(TokenQuery):
    def __init__(self, corpus, session):
        super(StatisticsQuery, self).__init__("", session)
        
    def insert_static_data(self, df):
        return df
        
    def append_results(self, df):
        """
        Append the last results to the data frame.
        
        Parameters
        ----------
        df : pandas.DataFrame
            The data frame to which the last query results will be added.
            
        Returns
        -------
        df : pandas.DataFrame
        """
        self.results_frame = self.Session.Resource.get_statistics()
        self.Session.output_order = [
            "coq_statistics_table",
            "coq_statistics_column",
            "coq_statistics_entries",
            "coq_statistics_uniques",
            "coq_statistics_uniquenessratio",
            "coq_statistics_averagefrequency",
            "coquery_invisible_rc_feature"]
        self.results_frame.columns = self.Session.output_order
        return self.results_frame

class CollocationQuery(TokenQuery):
    
    @staticmethod
    def mutual_information(f_1, f_2, f_coll, size, span):
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
        except (ZeroDivisionError, TypeError, Exception) as e:
            logger.error("Error while calculating mutual information: f1={} f2={} fcol={} size={} span={}".format(f_1, f_2, f_coll, size, span))
            return None
        return MI

    @staticmethod
    def conditional_probability(freq_left, freq_total):
        """ Calculate the conditional probability Pcond to encounter the query 
        token given that the collocate occurred in the left neighbourhood of
        the token.

        Pcond(q | c) = P(c, q) / P(c) = f(c, q) / f(c),
        
        where f(c, q) is the number of occurrences of word c as a left 
        collocate of query token q, and f(c) is the total number of 
        occurrences of c in the corpus. """
        return float(freq_left) / float(freq_total)

    @classmethod
    def aggregate_data(cls, df, corpus, **kwargs):
        if options.cfg.context_mode != CONTEXT_NONE:
            count_left = collections.Counter()
            count_right = collections.Counter()
            count_total = collections.Counter()
            
            left_span = options.cfg.context_left
            right_span = options.cfg.context_right

            features = []
            lexicon_features = corpus.resource.get_lexicon_features()
            for rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in lexicon_features]:
                    features.append("coq_{}".format(rc_feature))
                
            corpus_size = corpus.get_corpus_size()
            query_freq = 0
            context_info = {}

            fix_col = ["coquery_invisible_corpus_id"]

            # FIXME: Be more generic than always using coq_word_label!
            left_cols = ["coq_context_lc{}".format(x + 1) for x in range(options.cfg.context_left)]
            # FIXME: currently, the token number is set to 1, because this class 
            # method doesn't know about the maximum token number in this query.
            # Somehow, get_max_tokens() needs to be passed to this method to 
            # effect something like max_tokens = cls.get_max_tokens(cls)
            max_tokens = 1 + left_span + right_span
            right_cols = ["coq_context_rc{}".format(x + 1) for x in range(options.cfg.context_right)]
            left_context_span = df[fix_col + left_cols]
            right_context_span = df[fix_col + right_cols]
            if not options.cfg.output_case_sensitive:
                if options.cfg.output_to_lower:
                    for column in left_cols:
                        left_context_span[column] = left_context_span[column].apply(lambda x: x.lower())
                    for column in right_cols:
                        right_context_span[column] = right_context_span[column].apply(lambda x: x.lower())
                else:
                    for column in left_cols:
                        left_context_span[column] = left_context_span[column].apply(lambda x: x.upper())
                    for column in right_cols:
                        right_context_span[column] = right_context_span[column].apply(lambda x: x.upper())

            left = left_context_span[left_cols].stack().value_counts()
            right = right_context_span[right_cols].stack().value_counts()

            all_words = set(list(left.index) + list(right.index))
        else:
            all_words = []
        
        engine = corpus.resource.get_engine()
        if all_words and options.cfg.context_mode != CONTEXT_NONE:
            
            left = left.reindex(all_words).fillna(0).astype(int)
            right = right.reindex(all_words).fillna(0).astype(int)
            
            collocates = pd.concat([left, right], axis=1)
            collocates = collocates.reset_index()
            collocates.columns = ["coq_collocate_label", "coq_collocate_frequency_left", "coq_collocate_frequency_right"]
            collocates["coq_collocate_frequency"] = collocates.sum(axis=1)
            collocates["statistics_frequency"] = collocates["coq_collocate_label"].apply(corpus.get_frequency, engine=engine)
            
            collocates["coq_conditional_probability_left"] = collocates.apply(
                lambda x: cls.conditional_probability(
                    x["coq_collocate_frequency_left"],
                    x["statistics_frequency"]) if x["statistics_frequency"] else None, 
                axis=1)
            collocates["coq_conditional_probability_right"] = collocates.apply(
                lambda x: cls.conditional_probability(
                    x["coq_collocate_frequency_right"],
                    x["statistics_frequency"]) if x["statistics_frequency"] else None, 
                axis=1)
            
            collocates["coq_mutual_information"] = collocates.apply(
                lambda x: cls.mutual_information(
                        f_1=len(df.index),
                        f_2=x["statistics_frequency"], 
                        f_coll=x["coq_collocate_frequency"],
                        size=corpus_size, 
                        span=left_span + right_span),
                axis=1)
            aggregate = collocates.drop_duplicates(subset="coq_collocate_label")
        else:
            aggregate = pd.DataFrame(columns=["coq_collocate_label", "coq_collocate_frequency_left", "coq_collocate_frequency_right", "coq_collocate_frequency", "statistics_frequency", "coq_conditional_probability_left", "coq_conditional_probability_right", "coq_mutual_information"])
        engine.dispose()
        return aggregate

    @staticmethod
    def add_output_columns(session):
        session._old_output_order = session.output_order
        session.output_order = []
        for label in ["coq_collocate_label", "coq_collocate_frequency_left", "coq_collocate_frequency_right", "coq_collocate_frequency", "statistics_frequency", "coq_conditional_probability_left", "coq_conditional_probability_right", "coq_mutual_information", "coquery_invisible_corpus_id", "coquery_invisible_number_of_tokens"]:
            if label not in session.output_order:
                session.output_order.append(label)

    @staticmethod
    def remove_output_columns(session):
        session.output_order = session._old_output_order
        
logger = logging.getLogger(NAME)

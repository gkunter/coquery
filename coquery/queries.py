# -*- coding: utf-8 -*-
"""
queries.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import hashlib
import logging
import os

import pandas as pd
import numpy as np

from coquery.defines import QUERY_ITEM_LEMMA, QUERY_ITEM_WORD, CONTEXT_NONE
from coquery.errors import SQLQueryCancelled

from . import tokens
from . import options
from coquery.connections import SQLiteConnection
from coquery.unicode import utf8


class TokenQuery(object):
    _id = 0
    """
    This class manages the query string, and is responsible for the output
    of the query results.
    """

    def __init__(self, query_string, session):
        self.query_list = []
        for s in query_string.split("\n"):
            if s:
                self.query_list += tokens.preprocess_query(s)
        self.query_string = query_string
        self.Session = session
        self.Resource = session.Resource
        self.Corpus = session.Corpus
        self.Results = []
        self.input_frame = pd.DataFrame()
        self.results_frame = pd.DataFrame()
        self._keys = []
        self.empty_query = False
        self.sql_list = []

    def attach_databases(self, connection, attach_list):
        """
        Attach databases on SQLite connections.
        """
        if isinstance(options.cfg.current_connection, SQLiteConnection):
            for db_name in attach_list:
                path = os.path.join(options.cfg.database_path,
                                    "{}.db".format(db_name))
                S = "ATTACH DATABASE '{}' AS {}".format(
                    path, db_name)
                try:
                    connection.execute(S)
                    self.sql_list.append(S)
                except Exception:
                    error = ("Exception raised when executing {}").format(S)
                    logging.warning(error)

    def fix_case(self, df):
        if not options.cfg.output_case_sensitive and len(df.index) > 0:
            word_column = getattr(self.Resource, QUERY_ITEM_WORD, None)
            lemma_column = getattr(self.Resource, QUERY_ITEM_LEMMA, None)
            for x in df.columns:
                if ((word_column and word_column in x) or
                        (lemma_column and lemma_column in x)):
                    try:
                        if options.cfg.output_to_lower:
                            fnc = str.lower
                        else:
                            fnc = str.upper
                        df[x] = pd.Series(
                            map(lambda s: fnc(s) if not pd.isna(s) else
                                          pd.NA,
                                df[x].values))
                    except AttributeError:
                        print("attribute error!")
                        pass
        return df

    def run(self, connection=None, to_file=False, **kwargs):
        """
        Run the query, and store the results in an internal data frame.

        This method runs all required subqueries for the query string, e.g.
        the quantified queries if quantified tokens are used. The results are
        stored in self.results_frame.

        Parameters
        ----------
        to_file : bool
            True if the query results are directly written to a file, and
            False if they will be displayed in the GUI. Data that is written
            directly to a file contains less information, e.g. it doesn't
            contain an origin ID or a corpus ID (unless requested).
        """
        manager = self.Session.get_manager(options.cfg.MODE)
        manager_hash = manager.get_hash()

        self.results_frame = pd.DataFrame()

        self._max_number_of_tokens = 0
        for x in self.query_list:
            self._max_number_of_tokens = max(self._max_number_of_tokens,
                                             len(x))

        tokens.QueryToken.set_pos_check_function(
            self.Resource.pos_check_function)

        self.sql_list = []

        if isinstance(options.cfg.current_connection, SQLiteConnection):
            attach_list = self.Resource.get_attach_list(
                options.cfg.selected_features)
            self.attach_databases(connection, attach_list)

        for i, sub_query in enumerate(self.query_list):
            sub_str = [item if item else "_NULL"
                       for _, item in sub_query]
            self.sql_list.append(
                "-- query string: {}".format(" ".join(sub_str)))
            lst = [utf8(x) for _, x in sub_query if x]
            self._current_number_of_tokens = len(lst)
            self._current_subquery_string = " ".join(lst)

            if len(self.query_list) > 1:
                s = "Subquery #{} of {}: {}".format(
                            i+1,
                            len(self.query_list),
                            self._current_subquery_string)
                logging.info(s)

            query_string = self.Resource.get_query_string(
                query_items=sub_query,
                selected=options.cfg.selected_features,
                to_file=to_file)

            self.sql_list.append(query_string)

            df = None
            md5 = None

            if options.cfg.use_cache and query_string:
                try:
                    s = "".join(sorted(query_string)).encode()
                    md5 = hashlib.md5(s).hexdigest()
                    df = options.cfg.query_cache.get((self.Resource.name,
                                                      manager_hash, md5))
                except KeyError:
                    md5 = ""

            if df is None:
                if not query_string:
                    df = pd.DataFrame()
                else:
                    if options.cfg.verbose:
                        logging.info(query_string)

                    try:
                        results = (connection
                                   .execution_options(stream_results=True)
                                   .execute(query_string.replace("%", "%%")))
                    except Exception as e:
                        print(query_string)
                        raise e

                    try:
                        df = pd.DataFrame(results, columns=results.keys())
                    except Exception as e:
                        if not self.Session._query_connection:
                            raise SQLQueryCancelled
                        raise e

                    if len(df) == 0:
                        try:
                            df = pd.DataFrame(columns=results.keys())
                        except Exception as e:
                            if not self.Session._query_connection:
                                raise SQLQueryCancelled
                            raise e

                    del results

                    if options.cfg.use_cache:
                        options.cfg.query_cache.add(
                            (self.Resource.name, manager_hash, md5),
                            df)

            df = self.fix_case(df)

            n = self._current_number_of_tokens
            df["coquery_invisible_number_of_tokens"] = n

            if len(df) > 0:
                if self.results_frame.empty:
                    self.results_frame = df
                else:
                    self.results_frame = self.results_frame.append(df)

        self.results_frame = self.results_frame.reset_index(drop=True)
        TokenQuery._id += 1
        self._query_id = TokenQuery._id
        return self.results_frame

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
        for i, x in enumerate(self.query_string.split(" ")):
            _, _, length = tokens.get_quantifiers(x)
            if length == 1:
                L.append("{}".format(i+1))
            else:
                for y in range(length):
                    L.append("{}.{}".format(i + 1, y + 1))
        if n > len(L) - 1:
            return n + 1
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

        # if df is empty, a dummy data frame is created with NAs in all
        # content columns. This is needed so that frequency queries with empty
        # results can be displayed as 0.
        # FIXME: "coquery_invisible_dummy" is used to handle empty queries.
        # There is probably a better way of doing this.
        if (len(df) == 0):
            col = []
            for x in options.cfg.selected_features:
                if x.startswith("coquery_"):
                    col.append(x)
                else:
                    col += [y for y
                            in self.Resource.format_resource_feature(
                                x, self._max_number_of_tokens)
                            if y not in col]
            col.append("coquery_invisible_dummy")
            if options.cfg.context_mode != CONTEXT_NONE:
                col.append("coquery_invisible_corpus_id")
                col.append("coquery_invisible_origin_id")
            df = pd.DataFrame([[np.nan] * len(col)], columns=col)
            n = self._current_number_of_tokens
            df["coquery_invisible_number_of_tokens"] = n
            self.empty_query = True
        else:
            df["coquery_invisible_dummy"] = 0
            self.empty_query = False

        columns = [x for x in options.cfg.selected_features
                   if x.startswith("coquery_")]
        columns += list(self.input_frame.columns)

        for column in columns:
            if column == "coquery_query_string":
                df[column] = self.query_string
            #elif column == "coquery_expanded_query_string":
                #df[column] = self._current_subquery_string
            elif column.startswith("coquery_query_token"):
                token_list = self.query_string.split()
                # construct a list with the maximum number of quantified
                # token repetitions. This is used to look up the query token
                # string.
                L = []
                for x in token_list:
                    token, _, length = tokens.get_quantifiers(x)
                    L += [token] * length
                for i, item in enumerate(L):
                    df["{}_{}".format(column, i+1)] = item
            else:
                # add column labels for the columns in the input file:
                if all([x is None for x in self.input_frame.columns]):
                    # no header in input file, so use X1, X2, ..., Xn:
                    input_columns = [
                        ("coq_X{}".format(x), x)
                        for x in range(len(self.input_frame.columns))]
                else:
                    input_columns = [
                        ("coq_{}".format(x), x)
                        for x in self.input_frame.columns]
                for df_col, input_col in input_columns:
                    df[df_col] = self.input_frame[input_col][0]
        df["coquery_invisible_query_id"] = self._query_id
        return df


class StatisticsQuery(TokenQuery):
    def __init__(self, corpus, session):
        super(StatisticsQuery, self).__init__("", session)

    def insert_static_data(self, df):
        return df

    def run(self, connection=None, to_file=False, **kwargs):
        self.results_frame = self.Session.Resource.get_statistics(connection,
                                                                  **kwargs)
        return self.results_frame

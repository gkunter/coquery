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
import hashlib

try:
    range = xrange
except NameError:
    pass

try:
    from numba import jit
except (ImportError, OSError):
    def jit(f):
        def inner(f, *args):
            return f(*args)
        return lambda *args: inner(f, *args)

import pandas as pd

from .defines import *
from .errors import *
from .general import *
from . import tokens
from . import options
from . import managers


class TokenQuery(object):
    """
    This class manages the query string, and is responsible for the output
    of the query results.
    """

    def __init__(self, S, Session):
        try:
            self.query_list = tokens.preprocess_query(S)
        except TokenParseError as e:
            logger.error(str(e))
            S = ""
            self.query_list = []
        self.query_string = S
        self.Session = Session
        self.Resource = Session.Resource
        self.Corpus = Session.Corpus
        self.Results = []
        self.input_frame = pd.DataFrame()
        self.results_frame = pd.DataFrame()
        self._keys = []
        self.empty_query = False

    def __len__(self):
        return len(self.tokens)

    @staticmethod
    def get_visible_columns(df, session, ignore_hidden=False):
        """
        Return a list with the column names that are currently visible.
        """
        print("TokenQuery.get_visible_columns() is deprecated.")
        if ignore_hidden:
            return [x for x in list(df.columns.values) if (
                not x.startswith("coquery_invisible") and
                x in session.output_order)]
        else:
        # FIXME: use manager for column visibility
            return [x for x in list(df.columns.values) if (
                not x.startswith("coquery_invisible") and
                x in session.output_order)]

            #return [x for x in list(df.columns.values) if (
                #not x.startswith("coquery_invisible") and
                #x in session.output_order and
                #options.cfg.column_visibility.get(x, True))]

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
        manager_hash = managers.get_manager(options.cfg.MODE, self.Resource.name).get_hash()
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

            query_string = self.Resource.get_query_string(self, self._sub_query, to_file)

            df = None
            if options.cfg.use_cache and query_string:
                try:
                    md5 = hashlib.md5("".join(sorted(query_string)).encode()).hexdigest()
                    df = options.cfg.query_cache.get((self.Resource.name, manager_hash, md5))
                except KeyError:
                    pass
            if df is None:
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
                        results = (connection
                                   .execution_options(stream_results=True)
                                   .execute(query_string.replace("%", "%%")))
                    except Exception as e:
                        print(query_string)
                        print(e)
                        raise e

                    df = pd.DataFrame(list(iter(results)), columns=results.keys())

                    if len(df) == 0:
                        df = pd.DataFrame(columns=results.keys())

                    del results

                    if options.cfg.use_cache:
                        options.cfg.query_cache.add((self.Resource.name, manager_hash, md5), df)

            if not options.cfg.output_case_sensitive and len(df.index) > 0:
                word_column = getattr(self.Resource, QUERY_ITEM_WORD, None)
                lemma_column = getattr(self.Resource, QUERY_ITEM_LEMMA, None)
                for x in df.columns:
                    if ((word_column and word_column in x) or
                            (lemma_column and lemma_column in x)):
                        try:
                            if options.cfg.output_to_lower:
                                df[x] = df[x].apply(lambda x: x.lower() if x else x)
                            else:
                                df[x] = df[x].apply(lambda x: x.upper() if x else x)

                        except AttributeError:
                            pass

            df["coquery_invisible_number_of_tokens"] = self._current_number_of_tokens

            if len(df) > 0:
                if self.results_frame.empty:
                    self.results_frame = df
                else:
                    # apply clumsy hack that tries to make sure that the dtypes of
                    # data frames containing NaNs or empty strings does not change
                    # when appending the new data frame to the previous.

                    if df.dtypes.tolist() != self.results_frame.dtypes.tolist():
                        print("DIFFERENT DTYPES!")

                    ## The same hack is also needed in session.run_queries().
                    #if len(self.results_frame) > 0 and df.dtypes.tolist() != dtype_list.tolist():
                        #for x in df.columns:
                            ## the idea is that pandas/numpy use the 'object'
                            ## dtype as a fall-back option for strange results,
                            ## including those with NaNs.
                            ## One problem is that integer columns become floats
                            ## in the process. This is so because Pandas does not
                            ## have an integer NA type:
                            ## http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na

                            #if df.dtypes[x] != dtype_list[x]:
                                #_working = None
                                #if df.dtypes[x] == object:
                                    #if not df[x].any():
                                        #df[x] = [np.nan] * len(df)
                                        #dtype_list[x] = self.results_frame[x].dtype
                                #elif dtype_list[x] == object:
                                    #if not self.results_frame[x].any():
                                        #self.results_frame[x] = [np.nan] * len(self.results_frame)
                                        #dtype_list[x] = df[x].dtype
                    #else:
                        #dtype_list = df.dtypes
                    #print(dtype_list)

                    self.results_frame = self.results_frame.append(df)

        self.results_frame.reset_index(drop=True)
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
        if (len(df) == 0):
            col = []
            for x in options.cfg.selected_features:
                if x.startswith("coquery_"):
                    col.append(x)
                else:
                    col += [y for y in self.Resource.format_resource_feature(x, self._max_number_of_tokens) if y not in col]
            col.append("coquery_dummy")
            if options.cfg.context_mode != CONTEXT_NONE:
                col.append("coquery_invisible_corpus_id")
                col.append("coquery_invisible_origin_id")
            df = pd.DataFrame([[pd.np.nan] * len(col)], columns=col)
            self.empty_query = True
        else:
            df["coquery_dummy"] = 0
            self.empty_query = False

        columns = self.Session.output_order
        group_functions = self.Session.group_functions
        if group_functions or options.cfg.group_filter_list:
            columns += options.cfg.group_columns

        for column in columns:
            if column == "coquery_query_string":
                df[column] = self.query_string
            elif column == "coquery_expanded_query_string":
                df[column] = self._current_subquery_string
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
                if all([x is None for x in self.input_frame.columns]):
                    # no header in input file, so use X1, X2, ..., Xn:
                    input_columns = [("coq_X{}".format(x), x) for x in range(len(self.input_frame.columns))]
                else:
                    input_columns = [("coq_{}".format(x), x) for x in self.input_frame.columns]
                for df_col, input_col in input_columns:
                    df[df_col] = self.input_frame[input_col][0]
        return df


class ContrastQuery(TokenQuery):
    """
    ContrastQuery is a subclass of TokenQuery.

    In this subclass, :func:`aggregate_data` creates a square matrix with all
    occurring combinations of output columns in the result data frame as rows
    columns. Each cell contains the log likelihood that the query frequency
    in the subcorpus that is defined by the row is statistically different
    from the token frequency in the subcorpus that is defined by the column.

    Calculations are based on http://ucrel.lancs.ac.uk/llwizard.html.

    Clicking on a contrast cell opens a dialog that gives further statistical
    details.
    """

    _ll_cache = {}

    @classmethod
    def collapse_columns(cls, df, session):
        """
        Return a list of strings. Each string contains the concatinated
        content of the feature cells in each row of the data frame.
        """
        # FIXME: columns should be processed in the order that they appear in
        # the None results table view.

        # FIXME: use manager for column visibility
        vis_cols = [x for x in cls.get_visible_columns(df, session) if not x.startswith("statistics")]
        return df.apply(lambda x: ":".join([x[col] for col in vis_cols]), axis=1).unique()

    @staticmethod
    def g_test(freq_1, freq_2, total_1, total_2):
        """
        This method calculates the G test statistic as described here:
        http://ucrel.lancs.ac.uk/llwizard.html

        For a formal description of the G² test, see Agresti (2013: 76).
        """
        if (freq_1, freq_2, total_1, total_2) not in ContrastQuery._ll_cache:
            exp1 = total_1 * (freq_1 + freq_2) / (total_1 + total_2)
            exp2 = total_2 * (freq_1 + freq_2) / (total_1 + total_2)

            G = 2 * (
                (freq_1 * math.log(freq_1 / exp1)) +
                (freq_2 * math.log(freq_2 / exp2)))

            #obs = [ [freq_1, freq_2], [total_1 - freq_1, total_2 - freq_2]]
            #exp =

            #total_1 * (total_1 + freq_1)/(total_1 + total_2)
            #total_2 * (total_1 + total_2)/(total_1 + total_2)

            #not_1 = total_1 - freq_1
            #not_2 = total_2 - freq_2


#e11 = (freq_1 + freq_2)*total_1/(total_1 + total_2)
#e21 = (freq_1 + freq_2)*total_2/(total_1 + total_2)
#e12 = (not_1 + not_2) * total_1/(total_1 + total_2)
#e22 = (not_1 + not_2) * total_2/(total_1 + total_2)

#l11 = freq_1 * math.log(freq_1)
#l21 = freq_2 * math.log(freq_2)
#l12 = not_1 * math.log(not_1)
#l22 = not_2 * math.log(not_2)

#G2 = 2 * (
    #sum(c(l11, l12, l21, l22, math.log(total_1))) -
    #sum(c((not_1 + not_2) * math.log(not_1 + not_2),
        #(freq_1 + freq_2) * math.log(freq_1 + freq_2),
        #total_1 * log(total_1),
        #total_2 * log(total_2))))

#G2 = 2 * ( sum(l11, l12, l21, l22, log(total_1 + total_2 - freq_1 - freq_2))
          #- sum((total_1 + total_2

            ContrastQuery._ll_cache[(freq_1, freq_2, total_1, total_2)] = G
        return ContrastQuery._ll_cache[(freq_1, freq_2, total_1, total_2)]

    @classmethod
    def retrieve_loglikelihood(cls, *args, **kwargs):
        if options.use_scipy:
            from scipy import stats

        label = kwargs["label"]
        df = kwargs["df"]
        row = args[0]

        freq_1 = row.statistics_frequency
        total_1 = row.statistics_subcorpus_size

        freq_2 = df[df._row_id == label].statistics_frequency.values[0]
        total_2 = df[df._row_id == label].statistics_subcorpus_size.values[0]

        obs = [[freq_1, freq_2], [total_1 - freq_1, total_2 - freq_2]]
        try:
            if options.use_scipy:
                g2, p_g2, _, _ = stats.chi2_contingency(obs, correction=False, lambda_="log-likelihood")
                return g2
            else:
                return cls.g_test(freq_1, freq_2, total_1, total_2)
        except ValueError:
            print(label)
            print(df)
            print(obs)
            return None

    @classmethod
    def get_cell_content(cls, index, df, session):
        """
        Return that content for the indexed cell that is needed to handle
        a click on it for the current aggregation.
        """
        # FIXME: use manager for column visibility
        vis_col = cls.get_visible_columns(session.output_object, session, ignore_hidden=True)

        row = df.iloc[index.row()]
        column = df.iloc[index.column() - len(vis_col)]

        freq_1 = row.statistics_frequency
        total_1 = row.statistics_subcorpus_size
        label_1 = row._row_id

        freq_2 = column.statistics_frequency
        total_2 = column.statistics_subcorpus_size
        label_2 = column._row_id

        return {"freq_row": freq_1, "freq_col": freq_2,
                "total_row": total_1, "total_col": total_2,
                "label_row": label_1, "label_col": label_2}

        try:
            return df.iloc[index.row()]
        except:
            return None

    @classmethod
    def aggregate_data(cls, df, corpus, **kwargs):
        """
        Parameters
        ----------
        df : DataFrame
            The data frame to be aggregated

        Returns
        -------
        result : DataFrame
        """
        session = kwargs["session"]
        if not len(df.index):
            return pd.DataFrame(columns=session.output_order)

        labels = cls.collapse_columns(df, session)
        freq = super(ContrastQuery, cls).aggregate_data(df, corpus, contrasts=True, **kwargs)
        freq["_row_id"] = labels
        session.output_order = session.output_order + ["statistics_g_test_{}".format(x) for x in labels]

        for x in labels:
            freq["statistics_g_test_{}".format(x)] = freq.apply(cls.retrieve_loglikelihood, axis=1, label=x, df=freq)
        return freq


class StatisticsQuery(TokenQuery):
    def __init__(self, corpus, session):
        super(StatisticsQuery, self).__init__("", session)

    def insert_static_data(self, df):
        return df

    def run(self, connection=None, to_file=False, **kwargs):
        self.results_frame = self.Session.Resource.get_statistics(connection, **kwargs)
        return self.results_frame


def get_query_type(MODE):
    if MODE == QUERY_MODE_CONTRASTS:
        return ContrastQuery
    elif MODE == QUERY_MODE_STATISTICS:
        return StatisticsQuery
    else:
        return TokenQuery

logger = logging.getLogger(NAME)

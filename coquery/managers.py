# -*- coding: utf-8 -*-
"""
managers.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import logging
import itertools
import collections
import pandas as pd
import re
import scipy

from .defines import (QUERY_MODE_TYPES, QUERY_MODE_FREQUENCIES,
                      QUERY_MODE_CONTINGENCY, QUERY_MODE_COLLOCATIONS,
                      QUERY_MODE_CONTRASTS,
                      COLUMN_NAMES, ROW_NAMES,
                      CONTEXT_NONE, CONTEXT_COLUMNS, CONTEXT_KWIC,
                      CONTEXT_STRING,
                      QUERY_ITEM_WORD)
from .functions import (Freq,
                        ContextColumns, ContextKWIC, ContextString,
                        MutualInformation, ConditionalProbability,
                        SubcorpusSize)
from .functionlist import FunctionList
from .general import CoqObject, get_visible_columns
from . import options, NAME
from .defines import FILTER_STAGE_BEFORE_TRANSFORM, FILTER_STAGE_FINAL


class Sorter(CoqObject):
    def __init__(self, column, ascending=True, reverse=False, position=0):
        super(Sorter, self).__init__()
        self.column = column
        self.ascending = ascending
        self.reverse = reverse
        self.position = position


class Group(CoqObject):
    def __init__(self, name="", columns=None, functions=None):
        self.columns = []
        self.functions = []

        if columns is not None:
            self.columns = columns
        if functions is not None:
            self.functions = functions

        self.name = name

    def __repr__(self):
        S = ("Group(name='{}', columns=[{}], functions=[{}])")
        return S.format(self.name,
                        ", ".join(["'{}'".format(x) for x in self.columns]),
                        ", ".join(["'{}'".format(x) for x in self.functions]))

    def process(self, df, session, manager):
        if self.columns:
            function_list = FunctionList(self.get_functions())
            df = (df.groupby(self.columns, as_index=False)
                    .apply(function_list.lapply,
                           session=session, manager=manager))
        return df

    def get_functions(self):
        return [fnc(columns=columns, group=self)
                for fnc, columns in self.functions]


class Summary(Group):
    def process(self, df, session, manager):
        function_list = FunctionList(self.get_functions())
        df = function_list.lapply(
            df, session=session, manager=manager)

        return df

    def __repr__(self):
        S = ("Summary(name='{}', functions=[{}])")
        return S.format(self.name,
                        ", ".join(["'{}'".format(x) for x in self.functions]))


class Manager(CoqObject):
    name = "RESULTS"
    ignore_user_functions = False

    def __init__(self):
        super(Manager, self).__init__()
        self._functions = []
        self._subst = {}
        self.sorters = []
        self._len_pre_filter = None
        self._len_post_filter = None
        self._len_pre_group_filter = {}
        self._len_post_group_filter = {}
        self.drop_on_na = None
        self.stopwords_failed = False
        self.dropped_na_count = 0
        self.reset_hidden_columns()
        self.unique_values = {}
        self.removed_duplicates = 0

        self.manager_functions = FunctionList()

        self._groups = []
        self._filters = []
        self._column_order = []
        self._last_query_id = None
        self.reset_context_cache()

    def reset_context_cache(self):
        self._context_cache = {}
        self._context_cache_corpus = None

    def reset_hidden_columns(self):
        self.hidden_columns = set([])

    def hide_column(self, column):
        self.hidden_columns.add(column)

    def show_column(self, column):
        self.hidden_columns.remove(column)

    def is_hidden_column(self, column):
        return column in self.hidden_columns

    def get_function(self, id):
        for fun in self._functions:
            if type(fun) == type:
                logger.warning("Function {} not found in manager".format(fun))
                return None
            if fun.get_id() == id:
                return fun

    def get_functions(self):
        return self._functions

    def set_filters(self, filter_list):
        self._filters = filter_list

    def set_groups(self, groups):
        self._groups = groups

    def set_column_substitutions(self, d):
        self._subst = d

    def get_column_substitutions(self, d):
        return self._subst

    def set_column_order(self, l):
        self._column_order = l

    def _get_main_functions(self, df, session):
        """
        Returns a list of functions that are provided by this manager.
        They will be executed after user functions.
        """
        l = []

        if options.cfg.context_mode != CONTEXT_NONE:
            # the context columns are only retrieved if there is no cached
            # context for the current context mode and the current query.
            if self._last_query_id != session.query_id:
                self.reset_context_cache()
                self._last_query_id = session.query_id

            if options.cfg.context_mode == CONTEXT_COLUMNS:
                l.append(ContextColumns())
            elif options.cfg.context_mode == CONTEXT_KWIC:
                l.append(ContextKWIC())
            elif options.cfg.context_mode == CONTEXT_STRING:
                l.append(ContextString())

        return l

    @staticmethod
    def _apply_function(df, fun, session):
        try:
            if fun.single_column:
                df = df.assign(COQ_FUNCTION=lambda d: fun.evaluate(d, session=session))
                return df.rename(columns={"COQ_FUNCTION": fun.get_id()})
            else:
                new_df = df.apply(lambda x: fun.evaluate(x, session=session), axis="columns")
                return pd.concat([df, new_df], axis=1)
        except Exception as e:
            print(e)
            raise e

    def mutate_groups(self, df, session):
        if not self._groups:
            return df

        if options.cfg.verbose:
            print("\tmutate_groups({})".format(self._groups))

        for group in self._groups:
            df = group.process(df, session=session, manager=self)

        if options.cfg.verbose:
            print("\tDone mutate_groups")

        return df

    def mutate(self, df, session, stage="first"):
        """
        Modify the transformed data frame by applying all needed functions.
        """
        if len(df) == 0:
            return df

        if options.cfg.verbose:
            print("\tmutate(stage='{}')".format(stage))

        # separate general functions from context functions:
        fnc_all = self._get_main_functions(df, session)
        fnc_general = [x for x in fnc_all
                       if not x.get_id().startswith("coq_context")]
        fnc_contexts = [x for x in fnc_all if x not in fnc_general]

        # apply mutate functions, excluding context functions:
        mutate_functions = FunctionList(fnc_general)
        df = mutate_functions.lapply(df, session=session, manager=self)

        # only apply context functions during the first stage:
        if stage == "first" and fnc_contexts:
            context_key = (options.cfg.context_mode,
                           options.cfg.context_left,
                           options.cfg.context_right)
            if context_key in self._context_cache:
                # use the cached context columns if available:
                df = pd.concat([df,
                                self._context_cache[context_key]], axis=1)
            else:
                # run the context functions:
                context_functions = FunctionList(fnc_contexts)
                df = context_functions.lapply(df,
                                              session=session, manager=self)
                context_columns = [x for x in df.columns
                                if x.startswith(("coq_context"))]
                # and store context in cache
                self._context_cache[context_key] = df[context_columns]

        # apply user functions, i.e. functions that were added to
        # individual columns:
        kwargs = {"session": session,
                  "manager": self,
                  "df": df}

        self.stage_one_functions = []
        if stage == "first":
            self.stage_two_functions = []
            for fnc in session.column_functions:
                all_available = all([col in df.columns
                                     for col in fnc.columns])
                if all_available:
                    self.stage_one_functions.append(fnc)
                else:
                    self.stage_two_functions.append(fnc)

        fl = None
        if stage == "first" and self.stage_one_functions:
            fl = FunctionList(self.stage_one_functions)
        if stage == "second" and self.stage_two_functions:
            fl = FunctionList(self.stage_two_functions)
        if fl:
            df = fl.lapply(df, session=session, manager=self)
        df = df.reset_index(drop=True)

        if options.cfg.verbose:
            print("\tdone")
        return df

    def substitute(self, df, session, stage="first"):
        def _get_unique(column):
            try:
                values = column.dropna().unique()
            except AttributeError:
                print(column.head())
            to_bool = values.astype(bool)
            if (to_bool == values).all():
                return to_bool
            else:
                return values

        if stage == "first":
            self.unique_values = {}
            self._unresolved_subst = {}
            if self._subst:
                for col in self._subst:
                    if col not in df.columns:
                        self._unresolved_subst[col] = self._subst[col]
                    else:
                        self.unique_values[col] = _get_unique(df[col])
                try:
                    return df.replace(self._subst)
                except ValueError as e:
                    print(str(e), self._subst)
                except TypeError as e:
                    print(str(e))
        elif stage == "second":
            if self._unresolved_subst:
                for col in self._unresolved_subst:
                    if col in df:
                        self.unique_values[col] = _get_unique(df[col])
                try:
                    return df.replace(self._unresolved_subst)
                except TypeError as e:
                    print(e)
        return df

    def remove_sorter(self, column):
        self.sorters.remove(self.get_sorter(column))
        for i, x in enumerate(self.sorters):
            x.position = i

    def add_sorter(self, column, ascending=True, reverse=False):
        if self.get_sorter(column):
            self.remove_sorter(column)
        self.sorters.append(Sorter(column, ascending, reverse, len(self.sorters)))

    def get_sorter(self, column):
        for x in self.sorters:
            if x.column == column:
                return x
        return None

    def arrange_groups(self, df, session):
        if len(df) == 0 or len(self._groups) == 0:
            return df

        if options.cfg.verbose:
            print("\tarrange_groups({})".format(self._groups))

        for group in self._groups:
            # always sort minimally by the token ID
            columns = group.columns + ["coquery_invisible_corpus_id"]
            directions = [True] * len(columns)

            df = df.sort_values(by=columns,
                                ascending=directions,
                                axis="index")

        df = df.reset_index(drop=True)
        if options.cfg.verbose:
            print("\tdone")
        return df

    def arrange(self, df, session):
        if len(df) == 0:
            print("exit arrange")
            return df

        print("\tarrange()")

        original_columns = df.columns
        columns = []
        directions = []

        # list that stores unusuable sorters (e.g. because the sorter
        # refers to a function column and the function has been deleted):
        drop_list = []

        # gather sorting information:
        for sorter in self.sorters:
            # create dummy columns for reverse sorting:
            if sorter.reverse:
                target = "{}__rev".format(sorter.column)
                df[target] = (df[sorter.column].apply(lambda x: x[::-1]))
            else:
                target = sorter.column

            if target not in df.columns:
                drop_list.append(target)
            else:
                columns.append(target)
                directions.append(sorter.ascending)
        # drop illegal sorters:
        self.sorters = [x for x in self.sorters if x.column not in drop_list]
        # filter columns that should be in the data frame, but which aren't
        # (this may happen for example with the contingency table which
        # takes one column and rearranges it)
        column_check = [x in original_columns for x in columns]
        for i, col in enumerate(column_check):
            if not col and not columns[i].endswith("__rev"):
                directions.pop(i)
                columns.pop(i)

        if COLUMN_NAMES["statistics_column_total"] in df.index:
            # make sure that the row containing the totals is the last row:
            df_data = df[df.index != COLUMN_NAMES["statistics_column_total"]]
            df_totals = df[df.index == COLUMN_NAMES["statistics_column_total"]]
        else:
            df_data = df

        if len(columns) == 0:
            return df

        # sort the data frame (excluding a totals row)
        df_data = df_data.sort_values(by=columns,
                                      ascending=directions,
                                      axis="index")[original_columns]

        df_data = df_data.reset_index(drop=True)

        if COLUMN_NAMES["statistics_column_total"] in df.index:
            # return sorted data frame plus a potentially totals row:
            df = pd.concat([df_data, df_totals])
        else:
            df = df_data
        print("\tdone")

        df = df[[x for x in df.columns if not x.endswith("__rev")]]
        return df

    def summarize(self, df, session):
        if options.cfg.verbose:
            print("\tsummarize()")
        vis_cols = get_visible_columns(df, manager=self, session=session)

        df = self.manager_functions.lapply(df, session=session, manager=self)
        if not self.ignore_user_functions:
            df = session.summary_group.process(
                df, session=session, manager=self)

        cols = [x for x in vis_cols
                if x.startswith("coq_") and not x.startswith("coq_context_")]

        if options.cfg.drop_on_na and cols:
            ix = (df[vis_cols].dropna(axis="index", subset=cols, how="all")
                              .index)
            self.dropped_na_count = len(df) - len(ix)
            df = df.loc[ix]
        if options.cfg.verbose:
            print("\tdone")
        return df

    def distinct(self, df, session):
        vis_cols = get_visible_columns(df, manager=self, session=session)
        try:
            df = df.drop_duplicates(subset=vis_cols)
        except ValueError:
            # ValueError is raised if df is empty
            pass
        return df.reset_index(drop=True)

    def filter(self, df, session, stage):
        if (len(df) == 0 or not self._filters):
            return df

        self.reset_group_filter_statistics()
        self._len_pre_filter = len(df)
        if options.cfg.verbose or True:
            print("\tfilter()")
        for filt in self._filters:
            if filt.stage == stage:
                df = filt.apply(df).reset_index(drop=True)
        if options.cfg.verbose or True:
            print("\tdone")
        self._len_post_filter = len(df)
        return df

    def get_available_columns(self, session):
        pass

    def reset_filter_statistics(self):
        self._len_pre_filter = None
        self._len_post_filter = None

    def reset_group_filter_statistics(self):
        self._len_pre_group_filter = {}
        self._len_post_group_filter = {}

    def filter_groups(self, df, session):
        return df

        if (len(df) == 0 or
                len(options.cfg.group_columns) == 0 or
                len(options.cfg.group_filter_list) == 0):
            return df

        print("\tfilter_groups()")
        self.reset_group_filter_statistics()

        columns = self.get_group_columns(df, session)
        grouped = df.groupby(columns)

        sub_list = []
        for x in grouped.groups:
            dsub = df.iloc[grouped.groups[x]]
            self._len_pre_group_filter[x] = len(dsub)
            for filt in options.cfg.group_filter_list:
                dsub = filt.apply(dsub)

            sub_list.append(dsub)
            self._len_post_group_filter[x] = len(dsub)

        df = pd.concat(sub_list, axis=0)
        df = df.reset_index(drop=True)

        print("\tdone")
        return df

    def select(self, df, session):
        """
        Select the columns that will appear in the final output. Also, put
        them into the preferred order.
        """
        if options.cfg.verbose:
            print("\tselect()")

        resource = session.Resource

        columns = list(df.columns)

        # align context columns around word columns:
        first_word_pos = -1
        last_word_pos = -1
        word_column = "coq_{}_".format(
            getattr(session.Resource, QUERY_ITEM_WORD))
        left_context_columns = []
        right_context_columns = []
        # find word columns as well as context columns:
        for i, col in enumerate(columns):
            if col.startswith(word_column):
                if first_word_pos == -1:
                    first_word_pos = i
                last_word_pos = i
            elif col.startswith("coq_context_l"):
                left_context_columns.append(col)
            elif col.startswith("coq_context_r"):
                right_context_columns.append(col)

        # insert right context columns after word columns:
        if right_context_columns and first_word_pos > -1:
            for col in right_context_columns[::-1]:
                columns.remove(col)
                columns.insert(last_word_pos + 1, col)
        # insert left context columns before word columns:
        if left_context_columns and first_word_pos > -1:
            for col in left_context_columns[::-1]:
                columns.remove(col)
                columns.insert(first_word_pos, col)

        try:
            columns.remove("coquery_invisible_dummy")
        except ValueError:
            pass
        df = df[columns]
        if options.cfg.verbose:
            print("\tdone")
        return df

    def filter_stopwords(self, df, session):
        self.stopwords_failed = False

        if not options.cfg.stopword_list:
            return df

        print("\tfilter_stopwords({})".format(options.cfg.stopword_list))
        word_id_column = getattr(session.Resource, QUERY_ITEM_WORD)
        columns = []
        for col in df.columns:
            if col.startswith("coq_{}_".format(word_id_column)):
                columns.append(col)
        if columns == []:
            self.stopwords_failed = True
            return df

        stopwords = [x.lower() for x in options.cfg.stopword_list]
        valid = ~(df[columns].apply(lambda x: x.str.lower()
                                                   .isin(stopwords))
                             .any(axis=1))
        print("\tdone")
        return df[valid]

    def process(self, df, session, recalculate=True):
        """
        Process the data frame.

        Processing a data frame involves the following stages:

        1.  mutate(df, stage="first")
            Apply all main functions (including context functions) as well as
            user functions.

        2.  substitute(df, stage="first")
            Apply the substitution table from the current session

        3.  filter_groups(df)
            For each group, apply the group filters.

        4.  arrange_groups(df)
            Sort the entries within each group.

        5.  mutate_groups(df)
            Apply group functions to each group.

        6.  filter(df, stage=FILTER_STAGE_BEFORE_TRANSFORM)
            Apply the filters to the ungrouped data frame.

        7.  summarize(df)
            Take the data frame, and transform it according to the current
            transformation.

        8.  mutate(df, stage="second")
            Apply all user functions that could not be applied because they
            referred to function columns that were not available in step (1)
            yet.

        9.  substitute(df, stage="second")
            Apply the substitution table for the remaining columns

        10.  filter(df, stage=FILTER_STAGE_FINAL)
            Apply remaining filters to the transformed data frame.

        11. select(df)
            Discard the columns that are not needed for the current
            transformation.
        """
        if options.cfg.verbose:
            print("process()")

        df = df.reset_index(drop=True)
        if len(self._column_order):
            columns = ([x for x in self._column_order] +
                       [x for x in df.columns if x not in self._column_order])
            df = df[columns]

        # Get index of rows that are retained if duplicates are removed from
        # the data frame after sorting it by the number of query tokens that
        # returned the rows. This ensures that if the same token is returned
        # several times by a quantified query string, e.g. by a string like
        # 'get *{0,1}', the index of the most specific match is retained, for
        # example a match such as 'get happy', whereas the index of the less
        # specific matches, for example 'get <NA>', are discarded.
        self.removed_duplicates = 0
        id_cols = ["coquery_invisible_corpus_id",
                   "coquery_invisible_query_id"]
        id_cols = [x for x in id_cols if x in df.columns]
        if id_cols and options.cfg.drop_duplicates:
            # get index of duplicates, sorted so that those rows with the
            # highest number of query tokens are used:
            tmp = (df.sort_values(by=id_cols + ["coquery_invisible_number_of_tokens"],
                                ascending=[True] * len(id_cols) + [False])
                     .drop_duplicates(id_cols))
            ix = tmp.index
            self.removed_duplicates = len(df) - len(ix)
            # use the index to discard all rows that contain duplicate corpus
            # ids.
            df = df.loc[ix.sort_values()]

        df = df.reset_index(drop=True)

        self.drop_on_na = None

        if options.cfg.stopword_list:
            df = self.filter_stopwords(df, session)

        df = self.substitute(df, session, "first")

        _columns = df.columns
        df = df[[x for x in df.columns if not x.startswith("func_")]]
        if len(_columns) != len(df.columns):
            print("Unexpectedly discarded functions:", "\n\t".join(list(_columns)))

        df = self.mutate(df, session)
        df = self.filter_groups(df, session)
        df = self.arrange_groups(df, session)
        df = self.mutate_groups(df, session)
        df = self.filter(df, session, stage=FILTER_STAGE_BEFORE_TRANSFORM)
        df = self.summarize(df, session)
        df = self.mutate(df, session, stage="second")
        df = self.substitute(df, session, "second")
        df = self.filter(df, session, stage=FILTER_STAGE_FINAL)
        df = self.select(df, session)

        functions = list(itertools.chain.from_iterable(
            [group.get_functions() for group in self._groups]))

        self._functions = (session.column_functions.get_list() +
                           session.summary_group.get_functions() +
                           self.manager_functions.get_list() +
                           functions)

        return df


class Types(Manager):
    def summarize(self, df, session):
        df = super(Types, self).summarize(df, session)
        return self.distinct(df, session)


class FrequencyList(Manager):
    name = "FREQUENCY"

    def summarize(self, df, session):
        vis_cols = get_visible_columns(df, manager=self, session=session)
        freq_function = Freq(columns=vis_cols)
        freq_exists = False
        for fnc, col in session.summary_group.functions:
            if fnc == Freq and sorted(col) == sorted(vis_cols):
                freq_exists = True
                existing_func = fnc
                break
        if not freq_exists:
            #FIXME: add test that this actually works
            self.manager_functions = FunctionList([freq_function])
        else:
            self.manager_functions = FunctionList([existing_func])
        df = super(FrequencyList, self).summarize(df, session)
        return self.distinct(df, session)


class ContingencyTable(FrequencyList):
    name = "CONTINGENCY"

    def select(self, df, session):
        l = list(super(ContingencyTable, self).select(df, session).columns)
        for col in [x for x in df.columns if x != "coquery_invisible_dummy"]:
            if col not in l:
                l.append(col)

        # make sure that the frequency column is shown last:
        freq = self.manager_functions.get_list()[0].get_id()
        l.remove(freq)
        l.append(freq)
        df = df[l]
        l[-1] = "statistics_column_total"
        df.columns = l
        return df

    def summarize(self, df, session):
        def _get_column_label(row):
            if row[1] == "All":
                if agg_fnc[row[0]] == sum:
                    s = "{}(TOTAL)"
                elif agg_fnc[row[0]] == pd.np.mean:
                    s = "{}(MEAN)"
                else:
                    s = "{}({}=ANY)"
                return s.format(row[0], row.index[1])
            elif row[1]:
                return "{}({}='{}')".format(row[0],
                                            session.translate_header(row.index[1]),
                                            row[1].replace("'", "''"))
            else:
                return row[0]

        df = super(ContingencyTable, self).summarize(df, session)

        vis_cols = get_visible_columns(df, manager=self, session=session)

        cat_col = list(df[vis_cols]
                       .select_dtypes(include=[object]).columns.values)
        num_col = (list(df[vis_cols]
                        .select_dtypes(include=[pd.np.number]).columns.values) +
                   ["coquery_invisible_number_of_tokens",
                    "coquery_invisible_corpus_id",
                    "coquery_invisible_origin_id"])

        # determine appropriate aggregation functions:
        # - internal columns that are needed for context look-up take
        #   the first value (so clicking on a cell in the contingency
        #   table returns the first matching context)
        # - frequency functions return the sum
        # - all other numeric columns return the mean
        agg_fnc = {}
        for col in num_col:
            if col.startswith(("coquery_invisible")):
                agg_fnc[col] = lambda x: int(x.values[0])
            elif col.startswith(("func_statistics_frequency_")):
                agg_fnc[col] = sum
            else:
                agg_fnc[col] = pd.np.mean

        if len(cat_col) > 1:
            # Create pivot table:
            piv = df.pivot_table(index=cat_col[:-1],
                                columns=[cat_col[-1]],
                                values=num_col,
                                aggfunc=agg_fnc,
                                fill_value=0)
            piv = piv.reset_index()

            # handle the multi-index that pivot_table() creates:
            l1 = pd.Series(piv.columns.levels[-2][piv.columns.labels[-2]])
            l2 = pd.Series(piv.columns.levels[-1][piv.columns.labels[-1]])

            piv.columns = pd.concat([l1, l2], axis=1).apply(_get_column_label, axis="columns")
        else:
            piv = df

        # Ensure that the pivot columns have the same dtype as the original
        # column:
        for x in piv.columns:
            match = re.search("(.*)\(.*\)", x)
            if match:
                name = match.group(1)
            else:
                name = x
            if piv.dtypes[x] != df.dtypes[name]:
                piv[x] = piv[x].astype(df.dtypes[name])

        if len(cat_col) > 1:
            # Sort the pivot table
            try:
                # pandas <= 0.16.2:
                piv = piv.sort(columns=cat_col[:-1], axis="index")
            except AttributeError:
                # pandas >= 0.17.0
                piv = piv.sort_values(by=cat_col[:-1], axis="index")

        bundles = collections.defaultdict(list)
        d = {}

        # row-wise apply the aggregate function
        for x in piv.columns[(len(cat_col)-1):]:
            col = x.rpartition("(")[0]
            if col:
                bundles[col].append(x)
        for col in bundles:
            piv[col] = piv[bundles[col]].apply(agg_fnc[col], axis="columns")
        # add summary row:
        for x in piv.columns[(len(cat_col)-1):]:
            rc_feature = x.partition("(")[0]
            if rc_feature in agg_fnc:
                fnc = agg_fnc[rc_feature]
                d[x] = fnc(piv[x])
        row_total = pd.DataFrame([pd.Series(d)],
                                columns=piv.columns,
                                index=[ROW_NAMES["row_total"]]).fillna("")
        piv = piv.append(row_total)
        return piv


class Collocations(Manager):
    """
    Manager class which calculates the collocation measures for the
    current results table.

    The basic algorithm works like this:
    (1) Get a list of all words in the left and right context
    (2) Count how often each word occurs (separately either in the
        left or in the right context)
    """

    ignore_user_functions = True

    def _get_main_functions(self, df, session):
        """
        This manager will always use a ContextColumn function.
        """
        # FIXME:
        # If the context span is zero (i.e. neither a left nor a right
        # context, the program should alert the user somehow.
        return [ContextColumns()]

    def summarize(self, df, session):
        """
        This returns a completely different data frame than the argument.
        """

        # FIXME: reimplement a function that returns the corpus
        # size taking current filters into account.
        # Alternatively, get rid of this function call if the
        # corpus size can be handled correctly by an appropriate
        # function
        # Probably, the best solution is to take the queried corpus
        # features into account when calculating the collcations.
        # This would make a comparison of collactions in e.g. COCA across
        # genres fairly easy. In order to do this, all corpus features
        # should be included in the aggregation, and the _subcorpus_size()
        # function should be used to get the correct size.
        # If no corpus features are selected, the whole corpus will be
        # used.
        corpus_size = session.Resource.corpus.get_corpus_size()

        left_cols = ["coq_context_lc{}".format(x + 1) for x in range(options.cfg.context_left)]
        right_cols = ["coq_context_rc{}".format(x + 1) for x in range(options.cfg.context_right)]

        try:
            left_context_span = df[left_cols]
            right_context_span = df[right_cols]
        except KeyError:
            left_context_span = pd.DataFrame(
                data=[[None] * options.cfg.context_left],
                columns=left_cols)
            right_context_span = pd.DataFrame(
                data=[[None] * options.cfg.context_right],
                columns=left_cols)
        else:
            # convert all context columns to upper or lower case unless
            # the current setting says otherwise
            if not options.cfg.output_case_sensitive:
                if options.cfg.output_to_lower:
                    left_context_span = left_context_span.apply(
                        lambda col: col.str.lower())
                    right_context_span = right_context_span.apply(
                        lambda col: col.str.lower())
                else:
                    left_context_span = left_context_span.apply(
                        lambda col: col.str.upper())
                    right_context_span = right_context_span.apply(
                        lambda col: col.str.upper())

        left = left_context_span.stack().value_counts()
        right = right_context_span.stack().value_counts()

        all_words = [x for x in set(list(left.index) + list(right.index)) if x]

        left = left.reindex(all_words).fillna(0).astype(int)
        right = right.reindex(all_words).fillna(0).astype(int)

        collocates = pd.concat([left, right], axis=1)
        collocates = collocates.reset_index()
        collocates.columns = ["coq_collocate_label", "coq_collocate_frequency_left", "coq_collocate_frequency_right"]

        # calculate collocate frequency (i.e. occurrences of the collocate
        # in the context
        collocates["coq_collocate_frequency"] = collocates[["coq_collocate_frequency_left", "coq_collocate_frequency_right"]].sum(axis=1)
        # calculate total frequency of collocate
        collocates["statistics_frequency"] = collocates["coq_collocate_label"].apply(
            session.Resource.corpus.get_frequency, engine=session.db_engine,
            literal=True)
        # calculate conditional probabilities:
        func = ConditionalProbability()
        collocates["coq_conditional_probability"] = func.evaluate(
            collocates,
            freq_cond="coq_collocate_frequency",
            freq_total="statistics_frequency")
        collocates["coq_conditional_probability_left"] = func.evaluate(
            collocates,
            freq_cond="coq_collocate_frequency_left",
            freq_total="statistics_frequency")
        collocates["coq_conditional_probability_right"] = func.evaluate(
            collocates,
            freq_cond="coq_collocate_frequency_right",
            freq_total="statistics_frequency")

        func = MutualInformation()
        collocates["coq_mutual_information"] = func.evaluate(collocates,
                            f_1=len(df),
                            f_2="statistics_frequency",
                            f_coll="coq_collocate_frequency",
                            size=corpus_size,
                            span=len(left_cols) + len(right_cols))

        aggregate = collocates.drop_duplicates(subset="coq_collocate_label")

        # FIXME:
        # now that we have the collocations table, the summarize filters
        # should be applied, and perhaps also summarize functions?

        for filt in self._filters:
            aggregate = filt.apply(aggregate)
        aggregate = aggregate.reset_index(drop=True)

        order = ["coq_collocate_label",
                 "statistics_frequency",
                 "coq_collocate_frequency",
                 "coq_collocate_frequency_left",
                 "coq_collocate_frequency_right",
                 "coq_conditional_probability",
                 "coq_conditional_probability_left",
                 "coq_conditional_probability_right",
                 "coq_mutual_information"]

        if not len(aggregate) and not options.cfg.drop_on_na:
            return pd.DataFrame(data=[[None] * len(aggregate.columns)],
                                columns=aggregate.columns)
        else:
            return aggregate[order]


class ContrastMatrix(FrequencyList):
    _ll_cache = {}
    ignore_user_functions = True

    def matrix(self, df, session):
        df = df.reset_index(drop=True)
        labels = self.collapse_columns(df, session)
        df["coquery_invisible_row_id"] = labels
        #df = df.sort_values(by="coquery_invisible_row_id")

        self.p_values = pd.Series()

        for i, x in enumerate(labels):
            columns = ["statistics_g_test_{}".format(x),
                       "COQ_P_{}".format(x)]

            try:
                df[columns] = df.apply(
                    self.retrieve_loglikelihood, axis=1, label=x, df=df)
            except KeyError as e:
                print(e)
                return df
            else:
                self.p_values = self.p_values.append(df[columns[-1]][i:])
        df = df[[col for col in df.columns if not col.startswith("COQ_P_")]]
        return df

    def summarize(self, df, session):
        """
        Calculate a G-test matrix.

        The G-test matrix performs a G-test for each frequency of occurrence
        of value cominbantions in the data frame, taking the subcorpus sizes
        into account.

        Depending on the number of value combinations, the test matrix can
        become relatively large, and therefore, many multiple comparisons can
        be performed. To correct for an inflation of significant test
        results, a corrected alpha value is determined using the False
        Discovery Rate method (Benjamini & Hochberg 1995, described in
        Narum 2006).

        The corrected alpha is used by CoqLikelihoodDelegate class to
        visualize the test results in the results table.
        """

        # first, get the frequency list:
        df = super(ContrastMatrix, self).summarize(df, session)
        self._freq_function = self.manager_functions.get_list()[0]
        l = [x if x != self._freq_function.get_id()
             else "coquery_invisible_count"
             for x in df.columns]
        df.columns = l
        self._freq_function.alias = "coquery_invisible_count"

        # now, get a subcorpus size for each row:
        vis_cols = [x for x
                    in get_visible_columns(df, manager=self, session=session)
                    if not x == self._freq_function.get_id()]
        self._subcorpus_size = SubcorpusSize(columns=vis_cols,
                                             alias="coquery_invisible_size")
        self.manager_functions = FunctionList([self._subcorpus_size])
        df = super(FrequencyList, self).summarize(df, session)

        # finally, calculate the test matrix:
        df = df.sort_values(by=vis_cols)
        df = self.matrix(df, session)
        df = df.reset_index(drop=True)

        # determine critical value, adjusted for the number of comparisons,
        # using the False Discovery Rate method (Benjamini & Hochberg 1995,
        # described in Narum 2006).
        self.p_values = self.p_values.sort_values().reset_index(drop=True)
        threshold = ((pd.Series(pd.np.arange(len(self.p_values))) + 1) /
                     len(self.p_values)) * 0.05
        check = (self.p_values <= threshold)
        try:
            self.alpha = min(0.05, self.p_values.loc[check[::-1].idxmax()])
        except ValueError:
            self.alpha = None
            self.threshold = 0
        else:
            self.threshold = scipy.stats.chi2.ppf(1 - self.alpha, 1)
        return df

    def select(self, df, session):
        df = super(ContrastMatrix, self).select(df, session)
        vis_cols = get_visible_columns(df, manager=self, session=session)
        for i, x in enumerate(vis_cols):
            if x.startswith("statistics_g_test"):
                self._start_pos = i
                break
        return df

    def collapse_columns(self, df, session):
        """
        Return a list of strings. Each string contains the concatinated
        content of the feature cells in each row of the data frame.
        """
        # FIXME: columns should be processed in the order that they appear in
        # the None results table view.

        def fnc(x, cols=None):
            if cols is None:
                cols = []
            l = [x[col] for col in cols]
            return ":".join([str(x).strip() for x in l])

        vis_cols = get_visible_columns(df, manager=self, session=session)
        vis_cols = [x for x in vis_cols
                    if x not in (self._freq_function.get_id(),
                                 self._subcorpus_size.get_id())]
        return df.apply(fnc, cols=vis_cols, axis=1).unique()

    def retrieve_loglikelihood(self, row, df, label):
        freq = self._freq_function.get_id()
        size = self._subcorpus_size.get_id()

        freq_1 = row[freq]
        total_1 = row[size]

        freq_2 = df[df["coquery_invisible_row_id"] == label][freq].values[0]
        total_2 = df[df["coquery_invisible_row_id"] == label][size].values[0]

        obs = [[freq_1, freq_2], [total_1 - freq_1, total_2 - freq_2]]
        try:
            g2, p_g2, _, _ = scipy.stats.chi2_contingency(obs,
                                                          correction=False,
                                                          lambda_="log-likelihood")
            if (freq_1 / total_1) < (freq_2 / total_2):
                df = pd.Series([-g2, p_g2])
            else:
                df = pd.Series([g2, p_g2])
            return df
        except ValueError as e:
            raise e

    def get_cell_content(self, index, df, session):
        """
        Return that content for the indexed cell that is needed to handle
        a click on it for the current aggregation.
        """
        row = df.iloc[index.row()]
        column = df.iloc[index.column() - self._start_pos]

        freq_1 = row[self._freq_function.get_id()]
        total_1 = row[self._subcorpus_size.get_id()]
        label_1 = row["coquery_invisible_row_id"]

        freq_2 = column[self._freq_function.get_id()]
        total_2 = column[self._subcorpus_size.get_id()]
        label_2 = column["coquery_invisible_row_id"]

        return {"freq_row": freq_1, "freq_col": freq_2,
                "total_row": total_1, "total_col": total_2,
                "label_row": label_1, "label_col": label_2}


def manager_factory(manager):
    if manager == QUERY_MODE_TYPES:
        return Types()
    elif manager == QUERY_MODE_FREQUENCIES:
        return FrequencyList()
    elif manager == QUERY_MODE_CONTINGENCY:
        return ContingencyTable()
    elif manager == QUERY_MODE_COLLOCATIONS:
        return Collocations()
    elif manager == QUERY_MODE_CONTRASTS:
        return ContrastMatrix()
    else:
        return Manager()


def get_manager(manager, resource):
    """
    Returns a data manager
    """
    if resource is None:
        return None
    try:
        return options.cfg.managers[resource][manager]
    except KeyError:
        if resource not in options.cfg.managers:
            options.cfg.managers[resource] = {}
        new_manager = manager_factory(manager)
        options.cfg.managers[resource][manager] = new_manager
    finally:
        return options.cfg.managers[resource][manager]

logger = logging.getLogger(NAME)

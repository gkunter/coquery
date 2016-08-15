# -*- coding: utf-8 -*-
"""
managers.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from .defines import *
from .functions import *
from . import options

class Group(object):
    pass

class Sorter(object):
    def __init__(self, column, ascending=True, reverse=False, position=0):
        self.column = column
        self.ascending = ascending
        self.reverse = reverse
        self.position = position

class Manager(object):
    name = "RESULTS"
    
    def __init__(self):
        self.functions = []
        self.sorters = []
        self.hidden_columns = set([])
        self._columns = []

    def get_visible_columns(self, df, session):
        """
        Return a list with the column names that are currently visible.
        """
        l = [x for x in list(df.columns.values) if (
                    not x.startswith("coquery_invisible") and 
                    not x in self.hidden_columns)]

        resource_order = session.Resource.get_preferred_output_order()

        for x in resource_order[::-1]:
            lex_list = [y for y in l if x in y]
            lex_list = sorted(lex_list)[::-1]
            for lex in lex_list:
                l.remove(lex)
                l.insert(0, lex)
        return l
        
    def hide_column(self, column):
        self.hidden_columns.add(column)
        
    def show_column(self, column):
        self.hidden_columns.remove(column)
        
    def is_hidden_column(self, column):
        return column in self.hidden_columns
    
    def get_data_columns(self):
        """
        Return a list of data columns. The list is based on the last call to
        process(). If process() was not called for this data manager yet,
        the function raises a ValueError.
        """
        return self._columns
    
    def get_additional_columns(self):
        return [x.get_id() for x in self.functions]
    
    def get_function(self, id):
        for fun in self.functions:
            if fun.get_id() == id:
                return fun 
            
    def get_manager_functions(self, df, session):
        """
        Returns a list of functions that are provided by this manager. They
        will be executed after user functions.
        """
        l = []
        vis_cols = self.get_visible_columns(df, session)
        if "statistics_frequency" in options.cfg.selected_features:
            l.append(Freq(columns=vis_cols))
        if "statistics_normalized" in options.cfg.selected_features:
            l.append(FreqNorm(session=session, columns=vis_cols))
        if "statistics_per_million_words" in options.cfg.selected_features:
            l.append(FreqPMW(session=session, columns=vis_cols))
        if "statistics_proportion" in options.cfg.selected_features:
            l.append(Proportion(columns=vis_cols))
        if "statistics_corpus_size" in options.cfg.selected_features:
            l.append(CorpusSize(session=session))
        if "statistics_subcorpus_size" in options.cfg.selected_features:
            l.append(SubcorpusSize(session=session, columns=vis_cols))
        if "statistics_entropy" in options.cfg.selected_features:
            l.append(Entropy(columns=vis_cols))
        if "statistics_tokens" in  options.cfg.selected_features:
            l.append(Tokens())
        if "statistics_types" in  options.cfg.selected_features:
            l.append(Types(columns=vis_cols))
        if "statistics_ttr" in  options.cfg.selected_features:
            l.append(TypeTokenRatio(columns=vis_cols))
        return l
    
    def get_group_functions(self, df, session):
        vis_cols = self.get_visible_columns(df, session)
        groups = []
        for rc_feature in options.cfg.group_columns:
            groups += session.Resource.format_resource_feature(rc_feature,
                        session.get_max_token_count())
                    
        if not groups:
            return []
        l = []
        if "statistics_group_proportion" in options.cfg.selected_features:
            l.append(Proportion(columns=vis_cols, group=groups))
        if "statistics_group_entropy" in options.cfg.selected_features:
            l.append(Entropy(columns=vis_cols, group=groups))
        if "statistics_group_tokens" in  options.cfg.selected_features:
            l.append(Tokens(group=groups))
        if "statistics_group_types" in  options.cfg.selected_features:
            l.append(Types(columns=vis_cols, group=groups))
        if "statistics_group_ttr" in  options.cfg.selected_features:
            l.append(TypeTokenRatio(columns=vis_cols, group=groups))
        return l
    
    @staticmethod
    def _apply_function(df, fun):
        df = df.assign(COQ_FUNCTION=lambda d: fun.evaluate(d))
        return df.rename(columns={"COQ_FUNCTION": fun.get_id()})
    
    def mutate_groups(self, df, session):
        group_functions = self.get_group_functions(df, session)
        self.functions += group_functions
        
        for fun in group_functions:
            grouped = df.groupby(fun.group)
            if len(grouped.groups) == 1:
                df = Manager._apply_function(df, fun)
            else:
                val = grouped.apply(lambda d: fun.evaluate(d))
                val.index = val.index.labels[-1]
                df[fun.get_id()] = val

        df.fillna("", inplace=True)
        return df
    
    def transform(self, df, session):
        """
        Transform the data frame into a shape that is required by the data 
        manager.
        """
        return df
    
    def mutate(self, df, session):
        """
        Modify the transformed data frame by applying all needed functions.
        """
        
        self.functions = []
        #self.functions = session.get_functions()
        self.functions += self.get_manager_functions(df, session)
        
        for fun in self.functions:
            df = Manager._apply_function(df, fun)

        df.fillna("", inplace=True)

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
    
    def arrange(self, df, session):
        original_columns = df.columns
        columns = []
        if self.sorters:
            # gather sorting information:
            directions = []
            for sorter in self.sorters:
                directions.append(sorter.ascending)
                if sorter.reverse:
                    target = "{}_rev".format(sorter.column)
                    df[target] = (df[sorter.column].apply(lambda x: x[::-1]))
                else:
                    target = sorter.column
                columns.append(target)
        else:
            # no sorters specified, use group columns as sorters
            for column in options.cfg.group_columns:
                columns += session.Resource.format_resource_feature(column,
                    session.get_max_token_count())
            directions = [True] * len(columns)

        if not columns:
            return df
        
        # make sure that the row containing the totals is the last row:
        df_data = df[df.index != COLUMN_NAMES["statistics_column_total"]]
        df_totals = df[df.index == COLUMN_NAMES["statistics_column_total"]]
        
        # sort the data frame (excluding a totals row) with backward 
        # compatibility:
        try:
            # pandas <= 0.16.2:
            df_sorted = df_data.sort(columns=columns, 
                            ascending=directions,
                            axis="index")[original_columns]
        except AttributeError:
            # pandas >= 0.17.0
            df_sorted = df_data.sort_values(by=columns, 
                                    ascending=directions,
                                    axis="index")[original_columns]
        # return sorted data frame plus a potentially totals row:
        return pd.concat([df_sorted, df_totals])
    
    def summarize(self, df, session):
        return df

    def distinct(self, df, session):
        vis_cols = self.get_visible_columns(df, session)
        try:
            df = df.drop_duplicates(subset=vis_cols)
        except ValueError:
            # ValueError is raised if df is empty
            pass
        return df.reset_index(drop=True)

    def filter(self, df, session):
        return df
    
    def filter_groups(self, df, session):
        return df

    def process(self, df, session):
        df = self.transform(df, session)
        df = self.mutate(df, session)
        df = self.filter(df, session)
        df = self.mutate_groups(df, session)
        df = self.filter_groups(df, session)
        df = self.arrange(df, session)
        df = self.summarize(df, session)
        
        l = self.get_visible_columns(df, session)
        for col in df.columns:
            if col not in l:
                l.append(col)
        df = df[l]

        self._columns = df.columns
        return df
    
class Distinct(Manager):
    name = "DISTINCT"
    summarize = Manager.distinct

class Contingency(Distinct):
    def summarize(self, df, session):
        return df
    
    def mutate(self, df, session):
        def _get_column_label(row):
            col_label = session.translate_header(row[0])
            if row[1] == "All":
                if agg_fnc[row[0]] == sum:
                    s = "{}(TOTAL)"
                elif agg_fnc[row[0]] == np.mean:
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

        # collapse the data frame:
        df = super(Contingency, self).mutate(df, session)
        df = super(Contingency, self).filter(df, session)
        df = super(Contingency, self).summarize(df, session)

        vis_col = self.get_visible_columns(df, session)

        cat_col = list(df[vis_col].select_dtypes(include=[object]).columns.values)
        num_col = list(df[vis_col].select_dtypes(include=[np.number]).columns.values) + ["coquery_invisible_number_of_tokens", "coquery_invisible_corpus_id"]

        agg_fnc = {}
        for col in num_col:
            if col.startswith(("func_FREQUENCY", "func_PROPORTION")):
                agg_fnc[col] = sum
            elif col.startswith(("coquery_invisible")):
                agg_fnc[col] = lambda x: int(x.iloc[0])
            else:
                agg_fnc[col] = np.mean

        piv = df.pivot_table(index=cat_col[:-1], 
                             columns=[cat_col[-1]], 
                             values=num_col, 
                             margins=True, 
                             margins_name="",
                             aggfunc=agg_fnc,
                             fill_value=0)
        
        piv = piv.reset_index()

        l1 = pd.Series(piv.columns.levels[-2][piv.columns.labels[-2]])
        l2 = pd.Series(piv.columns.levels[-1][piv.columns.labels[-1]]) 

        piv.columns = pd.concat([l1, l2], axis=1).apply(_get_column_label, axis="columns")
        piv.index = list(piv.index[:-1]) + [COLUMN_NAMES["statistics_column_total"]]
        return piv

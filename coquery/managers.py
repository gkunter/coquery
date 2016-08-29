# -*- coding: utf-8 -*-
"""
managers.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import hashlib

from .defines import *
from .functions import *
from .general import CoqObject
from . import options

class Sorter(CoqObject):
    def __init__(self, column, ascending=True, reverse=False, position=0):
        self.column = column
        self.ascending = ascending
        self.reverse = reverse
        self.position = position

class Manager(CoqObject):
    name = "RESULTS"
    
    def __init__(self):
        self._functions = []
        self._column_functions = []
        self.sorters = []
        self.hidden_columns = set([])
        self._columns = []
        self._gf = []
        self._summary_functions = []
        self._group_filters = []
        self._filters = []

    def get_visible_columns(self, df, session, hidden=False):
        """
        Return a list with the column names that are currently visible.
        """
        if hidden:
            l = list(df.columns.values)
        else:
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
    
    def get_function(self, id):
        for fun in self._functions:
            if fun.get_id() == id:
                return fun 
    
    def add_column_function(self, fun):
        self._column_functions.append(fun)
        
    def remove_column_function(self, fun):
        self._column_functions.remove(fun)
        
        for x in self._column_functions:
            if fun.get_id() in x.columns:
                self.remove_column_function(x)
    
    def replace_column_function(self, old, new):
        ix = self._column_functions.index(old)
        self._column_functions[ix] = new
    
    def _get_main_functions(self, df, session):
        """
        Returns a list of functions that are provided by this manager. They
        will be executed after user functions.
        """
        l = []
        vis_cols = self.get_visible_columns(df, session)

        for func_type in self._summary_functions:
            l.append(func_type(columns=vis_cols, session=session))

        if options.cfg.context_mode == CONTEXT_COLUMNS:
            l.append(ContextColumns(session=session))
        elif options.cfg.context_mode == CONTEXT_KWIC:
            l.append(ContextKWIC(session=session))
        elif options.cfg.context_mode == CONTEXT_STRING:
            l.append(ContextString(session=session))

        print(l)
        return l
    
    def _get_group_functions(self, df, session):
        vis_cols = self.get_visible_columns(df, session, hidden=True)
        vis_cols = [x for x in vis_cols if not x.startswith("coquery_invisible")]
        groups = []
        for rc_feature in options.cfg.group_columns:
            groups += session.Resource.format_resource_feature(rc_feature,
                        session.get_max_token_count())
                    
        if not groups:
            return []

        l = []
        for func_type in self._gf:
            l.append(func_type(columns=vis_cols, group=groups))
        return l
    
    def _get_summary_functions(self, df, session):
        return self._summary_functions
    
    @staticmethod
    def _apply_function(df, fun, connection):
        if fun.single_column:
            df = df.assign(COQ_FUNCTION=lambda d: fun.evaluate(d, connection=connection))
            return df.rename(columns={"COQ_FUNCTION": fun.get_id()})
        else:
            new_df = df.apply(lambda x: fun.evaluate(x, connection=connection), axis="columns")
            return pd.concat([df, new_df], axis=1)
    
    def mutate_groups(self, df, session, connection):
        for fun in self._group_functions:
            grouped = df.groupby(fun.group)
            if len(grouped.groups) == 1:
                df = self._apply_function(df, fun, connection)
            else:
                if fun.single_column:
                    val = grouped.apply(lambda d: fun.evaluate(d))
                    val.index = val.index.labels[-1]
                    df[fun.get_id()] = val
                else:
                    new_df = grouped.apply(lambda d: fun.evaluate(d))
                    new_df.index = new_df.index.labels[-1]

        return df
    
    def mutate(self, df, session, connection):
        """
        Modify the transformed data frame by applying all needed functions.
        """
        for fun in self._main_functions:
            df = Manager._apply_function(df, fun, connection)
        
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
        if len(df) == 0:
            return df
        
        original_columns = df.columns
        columns = []
        directions = []
        
        if self.sorters:
            # gather sorting information:
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

        # filter columns that should be in the data frame, but which aren't 
        # (this may happen for example with the contingency table which 
        # takes one column and rearranges it)
        column_check = [x in original_columns for x in columns]
        for i, col in enumerate(column_check):
            if not col and not columns[i].endswith("_rev"):
                directions.pop(i)
                columns.pop(i)
                
        if COLUMN_NAMES["statistics_column_total"] in df.index:
            # make sure that the row containing the totals is the last row:
            df_data = df[df.index != COLUMN_NAMES["statistics_column_total"]]
            df_totals = df[df.index == COLUMN_NAMES["statistics_column_total"]]
        else:
            df_data = df

        # always sort by coquery_invisible_corpus_id if there is no other
        # sorter -- but not if the session covered multiple queries.
        if len(columns) == 0:
            if len(session.query_list) == 1:
                columns = ["coquery_invisible_corpus_id"]
                directions = [True]
            else:
                if COLUMN_NAMES["statistics_column_total"] in df.index:
                    # return sorted data frame plus a potentially totals row:
                    return pd.concat([df_data, df_totals])
                else:
                    return df_data

        # sort the data frame (excluding a totals row) with backward 
        # compatibility:
        try:
            # pandas <= 0.16.2:
            df_data = df_data.sort(columns=columns, 
                            ascending=directions,
                            axis="index")[original_columns]
        except AttributeError:
            # pandas >= 0.17.0
            df_data = df_data.sort_values(by=columns, 
                                    ascending=directions,
                                    axis="index")[original_columns]
        if COLUMN_NAMES["statistics_column_total"] in df.index:
            # return sorted data frame plus a potentially totals row:
            df = pd.concat([df_data, df_totals])
        else:
            df = df_data
        df = df.reset_index(drop=True)
        return df
        
    def summarize(self, df, session, connection):
        for fun in self._column_functions + self._summary_functions:
            df = Manager._apply_function(df, fun, connection)
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
        for filt in self._filters:
            try:
                df = df.query(filt)
            except Exception:
                pass
        return df
    
    def filter_groups(self, df, session):
        return df

    def select(self, df, session):
        l = self.get_visible_columns(df, session, hidden=True)
        self._columns = df.columns
        return df[l]

    def process(self, df, session, recalculate=True):
        engine = session.Resource.get_engine()
        with engine.connect() as connection:
            if recalculate:
                df = df[[x for x in df.columns if not x.startswith("func_")]]
                self._main_functions = self._get_main_functions(df, session)
                df = self.mutate(df, session, connection)
                self._group_functions = self._get_group_functions(df, session)
                df = self.mutate_groups(df, session, connection)
                df = self.filter_groups(df, session)
            df = self.arrange(df, session)
            
            self._summary_functions = self._get_summary_functions(df, session)
            df = self.summarize(df, session, connection)
            df = self.filter(df, session)
            df = self.select(df, session)
            df = df.fillna("")

        self._functions = (self._main_functions + self._group_functions +
                           self._column_functions + self._summary_functions)
        return df
    
class Distinct(Manager):
    name = "DISTINCT"
    
    def summarize(self, df, session, connection):
        df = super(Distinct, self).summarize(df, session, connection)
        return self.distinct(df, session)

class FrequencyList(Distinct):
    name = "FREQUENCY"
    
    def _get_summary_functions(self, df, session):
        return self._summary_functions + [Freq(columns=self.get_visible_columns(df, session))]
    
class ContingencyTable(FrequencyList):
    name = "CONTINGENCY"
    
    def select(self, df, session):
        l = list(super(ContingencyTable, self).select(df, session).columns)
        for col in df.columns:
            if col not in l:
                l.append(col)
        return df[l]

    def mutate(self, df, session, connection):
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
        df = super(ContingencyTable, self).mutate(df, session)
        df = super(ContingencyTable, self).filter(df, session)
        df = super(ContingencyTable, self).summarize(df, session)

        vis_col = self.get_visible_columns(df, session)

        cat_col = list(df[vis_col].select_dtypes(include=[object]).columns.values)
        num_col = list(df[vis_col].select_dtypes(include=[np.number]).columns.values) + ["coquery_invisible_number_of_tokens", "coquery_invisible_corpus_id"]

        agg_fnc = {}
        for col in num_col:
            func = self.get_function(col)
            if isinstance(func, Freq):
                agg_fnc[col] = sum
            elif col.startswith(("coquery_invisible")):
                agg_fnc[col] = lambda x: int(x.values[0])
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

        return piv

def manager_factory(manager):
    if manager == QUERY_MODE_FREQUENCIES:
        return FrequencyList()
    elif manager == QUERY_MODE_DISTINCT:
        return Distinct()
    elif manager == QUERY_MODE_CONTINGENCY:
        return ContingencyTable()
    elif manager == QUERY_MODE_COLLOCATIONS:
        return Collocations()
    else:
        return Manager()

def get_manager(manager, resource):
    """
    Returns a data manager 
    """
    try:
        return options.cfg.managers[resource][manager]
    except KeyError:
        if resource not in options.cfg.managers:
            options.cfg.managers[resource] = {}
        new_manager = manager_factory(manager)
        options.cfg.managers[resource][manager] = new_manager
    finally:
        return options.cfg.managers[resource][manager]


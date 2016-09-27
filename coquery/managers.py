#fef # -*- coding: utf-8 -*-
"""
managers.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import hashlib
import logging

from .defines import *
from .errors import *
from .functions import *
from . import filters
from .general import CoqObject, get_visible_columns
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
        self.drop_on_na = None
        
        self.manager_group_functions = FunctionList()
        self.manager_summary_functions = FunctionList()
        self.user_summary_functions = FunctionList()

        self._group_filters = []
        self._filters = []

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
            if type(fun) == type:
                logger.warning("Function {} not found in manager".format(fun))
                return None
            if fun.get_id() == id:
                return fun 
    
    def add_column_function(self, fun):
        self._column_functions.append(fun)
        
    def remove_column_function(self, fun):
        self._column_functions.remove(fun)
        
        for x in self._column_functions:
            if fun.get_id() in x.columns(df=None):
                self.remove_column_function(x)
    
    def replace_column_function(self, old, new):
        ix = self._column_functions.index(old)
        self._column_functions[ix] = new
    
    def set_filters(self, filter_list):
        self._filters = filter_list
    
    def _get_main_functions(self, df, session):
        """
        Returns a list of functions that are provided by this manager. They
        will be executed after user functions.
        """
        l = []
        vis_cols = get_visible_columns(df, manager=self, session=session)
        
        if options.cfg.use_context:
            if options.cfg.context_mode == CONTEXT_COLUMNS:
                l.append(ContextColumns())
            elif options.cfg.context_mode == CONTEXT_KWIC:
                l.append(ContextKWIC())
            elif options.cfg.context_mode == CONTEXT_STRING:
                l.append(ContextString())

        return l
    
    def _get_group_functions(self, df, session, connection):
        return self.manager_group_functions.get_list() + session.group_functions.get_list()
    
    @staticmethod
    def _apply_function(df, fun, connection, session):
        try:
            if fun.single_column:
                df = df.assign(COQ_FUNCTION=lambda d: fun.evaluate(d, connection=connection, session=session))
                return df.rename(columns={"COQ_FUNCTION": fun.get_id()})
            else:
                new_df = df.apply(lambda x: fun.evaluate(x, connection=connection, session=session), axis="columns")
                return pd.concat([df, new_df], axis=1)
        except Exception as e:
            print(e)
            raise e
        
    def mutate_groups(self, df, session, connection):
        if len(df) == 0 or len(options.cfg.group_columns) == 0:
            return df
        print("\tmutate_groups({})".format(options.cfg.group_columns))
        vis_cols = get_visible_columns(df, manager=self, session=session, hidden=True)
        l = session.group_functions.get_list()
        l = [fun(columns=vis_col, connection=connection) if type(fun) == type else fun for fun in l]
        session.group_functions = FunctionList(l)
        columns = []
        # use group columns as sorters
        for col in options.cfg.group_columns:
            formatted_cols = session.Resource.format_resource_feature(col, session.get_max_token_count())
            for x in formatted_cols:
                if x in df.columns:
                    columns.append(x)

        if len(columns) == 0:
            return df

        grouped = df.groupby(columns)
        for fun in self._get_group_functions(df, session, connection):
            l = pd.Series()
            for x in grouped.groups:
                val = fun.evaluate(df.iloc[grouped.groups[x]], connection, session=session, manager=self)
                l = l.append(val)
            df[fun.get_id()] = l
            
        return df
    
    def mutate(self, df, session, connection):
        """
        Modify the transformed data frame by applying all needed functions.
        """
        if len(df) == 0:
            return df
        print("\tmutate()")
        df = FunctionList(self._get_main_functions(df, session)).apply(df, connection, session=session, manager=self)
        df = FunctionList(self._column_functions).apply(df, connection, session=session, manager=self)
        df = df.reset_index(drop=True)
        print("\tdone")
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
        if len(df) == 0 or len(options.cfg.group_columns) == 0:
            return df

        print("\tarrange_groups({})".format(options.cfg.group_columns))

        columns = []
        # use group columns as sorters
        for col in options.cfg.group_columns:
            formatted_cols = session.Resource.format_resource_feature(col, session.get_max_token_count())
            for x in formatted_cols:
                if x in df.columns:
                    columns.append(x)
        directions = [True] * len(columns)

        columns += ["coquery_invisible_corpus_id"]
        directions += [True]

        # filter columns that should be in the data frame, but which aren't 
        # (this may happen for example with the contingency table which 
        # takes one column and rearranges it)
        column_check = [x in df.columns for x in columns]
        for i, col in enumerate(column_check):
            if not col:
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

        # sort the data frame (excluding a totals row) with backward 
        # compatibility:
        try:
            # pandas <= 0.16.2:
            df_data = df_data.sort(columns=columns, 
                            ascending=directions,
                            axis="index")[df.columns]
        except AttributeError:
            # pandas >= 0.17.0
            df_data = df_data.sort_values(by=columns, 
                                    ascending=directions,
                                    axis="index")[df.columns]
        if COLUMN_NAMES["statistics_column_total"] in df.index:
            # return sorted data frame plus a potentially totals row:
            df = pd.concat([df_data, df_totals])
        else:
            df = df_data
        df = df.reset_index(drop=True)
        print("\tdone")
        return df
        
    
    def arrange(self, df, session):
        if len(df) == 0:
            return df
        
        print("\tarrange()")

        original_columns = df.columns
        columns = []
        directions = []
        
        if self.sorters:
            # gather sorting information:
            for sorter in self.sorters:
                directions.append(sorter.ascending)
                # create dummy columns for reverse sorting:
                if sorter.reverse:
                    target = "{}_rev".format(sorter.column)
                    df[target] = (df[sorter.column].apply(lambda x: x[::-1]))
                else:
                    target = sorter.column
                columns.append(target)

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

        if len(columns) == 0:
            return df

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
        print("\tdone")
        return df
        
    def summarize(self, df, session, connection):
        #if len(df) == 0:
            #return df
        
        print("\tsummarize()")
        df = self.manager_summary_functions.apply(df, connection, session=session, manager=self)
        if options.cfg.use_summarize:
            df = self.user_summary_functions.apply(df, connection, session=session, manager=self)
        if self.drop_on_na and df.isnull().values.any():
            print("summarize drop")
            df = df.dropna(axis="index")

        if options.cfg.drop_duplicates:
            df = self.distinct(df, session)
                          
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

    def filter(self, df, session):
        if len(df) == 0 or not options.cfg.use_summarize_filters:
            return df

        print("\tfilter()")
        new_list = []
        for filt in self._filters:
            new_filt = filters.QueryFilter()
            new_filt.resource = session.Resource
            new_filt.text = filt
            new_list.append(new_filt)

        print("\t\t".join(session.Resource.translate_filters(new_list)))
        return df


            #if filt.count("=") == 1:
                #filt = filt.replace("=", "==")
            #try:
                #df = df.query(filt)
            #except Exception as e:
                #print(e)
                #pass
        print("\tdone")
        return df
    
    def get_available_columns(self, session):
        pass
    
    def filter_groups(self, df, session):
        if len(df) == 0 or len(options.cfg.group_columns) == 0:
            return df

        print("\tfilter_groups()")
        print("\tdone")
        return df

    def select(self, df, session):
        if len(df) == 0:
            return df

        print("\tselect()")

        # 'coquery_dummy' is used to manage frequency queries with zero 
        # matches. It is never displayed:
        vis_cols = [x for x in df.columns if x != "coquery_dummy"]
        self._columns = df.columns

        print("\tdone")
        return df[vis_cols]

    def filter_stopwords(self, df, session):
        self.stopwords_failed = False

        if not options.cfg.use_stopwords or not options.cfg.stopword_list:
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
        
        print("\tdone")
        valid = (df[columns].
                 apply(lambda x: x.apply(lambda y: y in options.cfg.stopword_list)).
                 apply(lambda x: not any(x), axis="columns"))
        return df[valid]

    def process(self, df, session, recalculate=True):
        print("process()")
        self.drop_on_na = None
        self._main_functions = []
        self._group_functions = []
        engine = session.Resource.get_engine()
        with engine.connect() as connection:
            df = self.filter_stopwords(df, session)
            if recalculate:
                df = df[[x for x in df.columns if not x.startswith("func_")]]
                self._main_functions = self._get_main_functions(df, session)
                df = self.mutate(df, session, connection)
                df = self.arrange_groups(df, session)
                df = self.mutate_groups(df, session, connection)
                df = self.filter_groups(df, session)
            df = self.arrange(df, session)
            df = self.summarize(df, session, connection)
            df = self.filter(df, session)
            df = self.select(df, session)

            self._functions = (self._main_functions + self._group_functions +
                            self._column_functions + 
                            self._get_group_functions(df, session, connection) + 
                            self.manager_summary_functions.get_list() + 
                            self.user_summary_functions.get_list())
        print("done")
        return df
    
class FrequencyList(Manager):
    name = "FREQUENCY"
    
    def __init__(self, *args, **kwargs):
        super(FrequencyList, self).__init__(*args, **kwargs)
    
    def summarize(self, df, session, connection):
        vis_cols = get_visible_columns(df, manager=self, session=session)
        freq_function = Freq(columns=vis_cols)
        
        if not self.user_summary_functions.has_function(freq_function):
            self.manager_summary_functions = FunctionList([freq_function])
        return super(FrequencyList, self).summarize(df, session, connection)
        
class ContingencyTable(FrequencyList):
    name = "CONTINGENCY"
    
    def select(self, df, session):
        l = list(super(ContingencyTable, self).select(df, session).columns)
        for col in df.columns:
            if col not in l:
                l.append(col)
        return df[l]

    def mutate(self, df, session, connection):
        print("mutate()")
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
        df = super(ContingencyTable, self).mutate(df, session, connection=connection)
        df = super(ContingencyTable, self).filter(df, session)
        df = super(ContingencyTable, self).summarize(df, session, connection=connection)

        vis_cols = get_visible_columns(df, manager=self, session=session)

        cat_col = list(df[vis_cols].select_dtypes(include=[object]).columns.values)
        num_col = list(df[vis_cols].select_dtypes(include=[np.number]).columns.values) + ["coquery_invisible_number_of_tokens", "coquery_invisible_corpus_id"]

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

logger = logging.getLogger(NAME)

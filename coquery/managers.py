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

class Manager(object):
    name = "RESULTS"
    
    def __init__(self):
        self.functions = []
        pass
    
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
        vis_cols = Function.get_visible_columns(df)
        if "statistics_frequency" in options.cfg.selected_features:
            l.append(Freq(columns=vis_cols))
        if "statistics_corpus_size" in options.cfg.selected_features:
            l.append(CorpusSize(session=session))
        if "statistics_subcorpus_size" in options.cfg.selected_features:
            l.append(SubcorpusSize(session=session, columns=vis_cols))
        if "statistics_per_million_words" in options.cfg.selected_features:
            l.append(FreqPMW(session=session, columns=vis_cols))
        if "statistics_proportion" in options.cfg.selected_features:
            l.append(Proportion(columns=vis_cols))
        if "statistics_entropy" in options.cfg.selected_features:
            l.append(Entropy(columns=vis_cols))
        if "statistics_normalized" in options.cfg.selected_features:
            l.append(FreqNorm(session=session, columns=vis_cols))
        if "statistics_tokens" in  options.cfg.selected_features:
            l.append(Tokens())
        if "statistics_types" in  options.cfg.selected_features:
            l.append(Types(columns=vis_cols))
        if "statistics_ttr" in  options.cfg.selected_features:
            l.append(TypeTokenRatio(columns=vis_cols))
        return l
    
    def get_group_functions(self, df, session):
        vis_cols = Function.get_visible_columns(df)
        groups = []
        for rc_feature in options.cfg.group_columns:
            groups += session.Resource.format_resource_feature(rc_feature,
                        session.get_max_token_count())
                    
        if not groups:
            return []
        l = []
        if "statistics_query_proportion" in options.cfg.selected_features:
            l.append(Proportion(columns=vis_cols, group=groups))
        if "statistics_query_entropy" in options.cfg.selected_features:
            l.append(Entropy(columns=vis_cols, group=groups))
        if "statistics_query_tokens" in  options.cfg.selected_features:
            l.append(Tokens(group=groups))
        if "statistics_query_types" in  options.cfg.selected_features:
            l.append(Types(columns=vis_cols, group=groups))
        if "statistics_query_ttr" in  options.cfg.selected_features:
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
    
    def mutate(self, df, session):
        self.functions = []
        #self.functions = session.get_functions()
        self.functions += self.get_manager_functions(df, session)
        
        for fun in self.functions:
            df = Manager._apply_function(df, fun)

        df.fillna("", inplace=True)

        return df
    
    def arrange(self, df, session):
        group_functions = self.get_group_functions(df, session)
        columns = []
        for fun in group_functions:
            columns += fun.group
        columns = list(set(columns))
        try:
            # pandas <= 0.16.2:
            return df.sort(columns=columns, axis="index")
        except AttributeError:
            # pandas >= 0.17.0
            return df.sort_values(by=columns, axis="index")
    
    def summarize(self, df):
        return df

    def distinct(self, df):
        vis_cols = Function.get_visible_columns(df)
        try:
            df = df.drop_duplicates(subset=vis_cols)
        except ValueError:
            # ValueError is raised if df is empty
            pass
        return df.reset_index(drop=True)
    
class Distinct(Manager):
    name = "DISTINCT"
    summarize = Manager.distinct
           
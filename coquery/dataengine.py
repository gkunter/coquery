# -*- coding: utf-8 -*-
"""
dataengine.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division

import re
import pandas as pd
import numpy as np
from scipy import stats

try:
    import numexpr
    _query_engine = "numexpr"
except ImportError:
    _query_engine ="python"

from . import options
from .defines import *

def get_engine(mode):
    if mode == QUERY_MODE_FREQUENCIES:
        return Frequency
    elif mode == QUERY_MODE_DISTINCT:
        return Distinct
    else:
        return Raw

try:
    _iqr = stats.iqr
except (AttributeError):
    _iqr = lambda x: np.subtract(*np.percentile(x, [75, 25]))

def _save_first(x):
    l = [y for y in x if y]
    try:
        return l[0]
    except IndexError:
        return None
        
def _save_last(x):
    l = [y for y in x if y]
    try:
        return l[-1]
    except IndexError:
        return None

function_map = {
    "all": all,
    "any": any,
    "sum": sum,
    "max": max,
    "min": min,
    "mean": np.mean,
    "sd": np.std,
    "median": np.median,
    "mode": stats.mode,
    "IQR": _iqr,
    "first": _save_first,
    "last": _save_last,
    "random": lambda x: np.random.choice(x),
    }

class Function(object):
    name = "id"

    def __init__(self, aggr=None, sweep=False):
        """
        Parameters
        ----------
        sweep: bool
            True if the function sweeps through the coluns, and False if it 
            sticks to one row at a time during evaluation
        """
        self.sweep = sweep
        if aggr:
            self.select = function_map[aggr]

    def func(self, col):
        """
        Defines the function that is applied the columns in the data frame 
        that is passed to this function.
        
        Parameters
        ----------
        col : pandas.Series
            A column from a data frame
        
        Returns
        -------
        col : pandas.Series
            The column after the function has been applied
        """
        return col
    
    def evaluate(self, df, columns):
        val = (df[columns].apply(self.func)
                          .apply(self.select, axis="columns"))

        assert isinstance(val, pd.Series)
        assert len(val) == len(df)
        
        return val

    def select(self, row):
        return row[0]
    
class Length(Function):
    name = "LENGTH"
    
    def func(self, cols):
        return cols.apply(len)
    
class Count(Function):
    name = "COUNT"
    
    def __init__(self, value, *args, **kwargs):
        super(Count, self).__init__(*args, **kwargs)
        self.value = value
    
    def func(self, col):
        return col.apply(lambda x: x.count(self.value))
    
class Chain(Function):
    name = "CHAIN"
    
    def __init__(self, value, *args, **kwargs):
        super(Chain, self).__init__(*args, **kwargs)
        self.value = "{}".format(value)
    
    def select(self, row):
        return self.value.join(row)

class Calc(Function):
    name = "CALC"
    
    def __init__(self, sign, value=None, *args, **kwargs):
        super(Calc, self).__init__(*args, **kwargs)
        self.sign = sign
        self.value = value
        
    def evaluate(self, df, columns):
        def _calc(val1, val2):
            if self.sign == "+":
                val1 = val1 + val2
            elif self.sign == "-":
                val1 = val1 - val2
            elif self.sign == "/":
                val1 = val1 / val2
            elif self.sign == "*":
                val1 = val1 * val2
            return val1
            
        val = df[columns[0]]
        for x in columns[1:]:
            val = _calc(val, df[x])
        if self.value:
            val = _calc(val, self.value)

        return val

class Match(Function):
    name = "MATCH"
    
    def __init__(self, regex, *args, **kwargs):
        super(Match, self).__init__(*args, **kwargs)
        self.re = re.compile(regex)
    
    def func(self, col):
        return col.apply(lambda x: self.re.search(str(x)) != None)

class Extract(Match):
    name = "EXTRACT"
    
    def func(self, col):
        def _match(s):
            re = self.re.search(str(s))
            try:
                return re.group()
            except AttributeError:
                return ""

        return col.apply(lambda x: _match(x))

class Freq(Function):
    name = "FREQUENCY"
    
    def evaluate(self, df, columns):
        def _get_query(pairs):
            s = " & ".join(["{} == '{}'".format(col, val) for col, val in pairs])
            return s
        
        def _get_freq(row):
            try:
                return self._cache[tuple(row)]
            except KeyError:
                i = len(df.query(_get_query(zip(columns, row)), engine=_query_engine))
                self._cache[tuple(row)] = i
                return i
        
        self._cache = {}
        return df[columns].apply(_get_freq, axis="columns") 

class FreqPMW(Freq):
    name = "FREQEUNCY_PMW"
    words = 1000000

    def __init__(self, session, *args, **kwargs):
        super(FreqPMW, self).__init__(*args, **kwargs)
        self.session = session
    
    def evaluate(self, df, columns):
        val = super(FreqPMW, self).evaluate(df, columns)
        corpus_size = self.session.Corpus.get_corpus_size(filters=self.session.filter_list)
        return val / (corpus_size / self.words)
    
class FreqPTW(FreqPMW):
    name = "FREQUENCY_PTW"
    words = 1000

class Proportion(Freq):
    name = "PROPORTION"
    
    def evaluate(self, df, columns):
        val = super(Proportion, self).evaluate(df, columns)
        return  val / len(df)
        
class Entropy(Proportion):
    name = "ENTROPY"
    
    def evaluate(self, df, columns):
        val = super(Entropy, self).evaluate(df, columns)
        _df = df
        _df["COQ_PROBABILITIES"] = val 
        _df = _df[list(columns) + ["COQ_PROBABILITIES"]].drop_duplicates()
        entropy = -sum([p * np.log2(p) for p in _df.COQ_PROBABILITIES])
        return [entropy] * len(df)

class CorpusSize(Function):
    name = "CORPUSSIZE"

    def __init__(self, session, *args, **kwargs):
        super(CorpusSize, self).__init__(*args, **kwargs)
        self.session = session
    
    def evaluate(self, df, columns):
        corpus_size = self.session.Corpus.get_corpus_size(filters=self.session.filter_list)
        return [corpus_size] * len(df)

class SubcorpusSize(CorpusSize):
    name = "SUBCORPUSSIZE"

    def evaluate(self, df, columns):
        corpus_features = [x for x, _ in self.session.Resource.get_corpus_features()]
        column_list = [x for x in corpus_features if "coq_{}_1".format(x) in columns]
        print(column_list)
        
        val = df.apply(self.session.Corpus.get_subcorpus_size, 
                       columns=column_list,
                       axis=1,
                       filters=self.session.filter_list)
        print(val)
        return val

class Engine(object):
    name = "UNDEFINED"
    
    def __init__(self, session):
        self.session = session
        pass
    
    def mutate(self, df):
        functions = [
            #(Length(), ["coq_word_label_1"]),
            #(Length(aggr="max"), ["coq_word_label_1", "coq_word_label_2"]),
            #(Count("e"), ["coq_word_label_2"]),
            #(Count("e", aggr="sum"), ["coq_word_label_1", "coq_word_label_2"]),
            #(Chain(" "), ["coq_word_label_1"]),
            #(Chain("-"), ["coq_word_label_1", "coq_word_label_2"]),
            #(Match("exp"), ["coq_word_label_2"]),
            #(Match("s", aggr="any"), ["coq_word_label_1", "coq_word_label_2"]),
            #(Extract("exp"), ["coq_word_label_2"]),
            #(Extract("s", aggr="first"), ["coq_word_label_1", "coq_word_label_2"]),
            #(Freq(), ["func_EXTRACT_1"]),
            #(Freq(), ["coq_word_label_1"]),
            #(Freq(), ["coq_word_label_1", "coq_word_label_2"]),
            #(FreqPTW(self.session), ["coq_word_label_1", "coq_word_label_2"]),
            #(FreqPMW(self.session), ["coq_word_label_1", "coq_word_label_2"]),
            #(CorpusSize(self.session), []), 
            #(Calc(sign="/"), ["func_FREQUENCY_1", "func_CORPUSSIZE_4"]),
            #(Calc(sign="/", value=1/1000), ["func_FREQUENCY_1", "func_CORPUSSIZE_4"]),
            #(Calc(sign="/", value=1/1000000), ["func_FREQUENCY_1", "func_CORPUSSIZE_4"]),
            #(SubcorpusSize(self.session), ["coq_source_category_1"]),
            #(SubcorpusSize(self.session), ["coq_source_category_1", "coq_source_title_1"]),
            (Proportion(), ["coq_word_label_1"]),
            (Proportion(), ["coq_word_label_1", "coq_word_label_2"]),
            (Entropy(), ["coq_word_label_1"]),
            ]
        
        for i, (fun, columns) in enumerate(functions):
            df = df.assign(COQ_FUNCTION=lambda d: fun.evaluate(d, columns))
            df = df.rename(columns={"COQ_FUNCTION": "func_{}_{}".format(fun.name, i+1)})

        #print(df[["coq_word_label_1", "coq_word_label_2"] + list(df.columns.values[-2:])])
        print(df.head(10))
        return df
    
    def apply(self, df):
        return df

    def get_visible_columns(self, df):
        """
        Return a list with the column names that are currently visible.
        """
        return [x for x in list(df.columns.values) if not x.startswith("coquery_invisible")]
        
    def distinct(self, df):
        vis_cols = self.get_visible_columns(df)
        try:
            df = df.drop_duplicates(subset=vis_cols)
        except ValueError:
            # ValueError is raised if df is empty
            pass
        return df.reset_index(drop=True)
    
class Raw(Engine):
    name = "RAW"
    pass

class Distinct(Engine):
    name = "DISTINCT"

    def apply(self, df):
        print(self.name)
        print(self.distinct(df))
        return self.distinct(df)
        
class Frequency(Engine):
    name = "FREQUENCY"
    
    def apply(self, df):
        group_cols = self.get_visible_columns(df)
        dat_cols = [x for x in df.columns.values if x not in group_cols]

        d = {group_cols[0]: "count"}
        d.update({x: "first" for x in dat_cols})
        
        return (df.groupby(group_cols)
                  .agg(d)
                  .rename(columns={group_cols[0]: "statistics_frequency"})
                  .reset_index())
    
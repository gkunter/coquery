# -*- coding: utf-8 -*-
"""
functions.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division

import re
import hashlib
import pandas as pd
import numpy as np
from scipy import stats

try:
    import numexpr
    _query_engine = "numexpr"
except ImportError:
    _query_engine ="python"

from . import options
from coquery.defines import *
from coquery.general import *

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

combine_map = {
    "all": all,
    "any": any,
    "none": lambda x: not any(x),
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
    "join": lambda x, y: y.join(x),
    }

bool_combine = ["all", "any", "none"]
seq_combine = ["first", "last", "random", "mode", "max", "min"]
num_combine = ["sum", "mean", "sd", "median", "IQR"]
no_combine = []

str_combine = seq_combine + bool_combine
num_combine = num_combine + seq_combine
all_combine = num_combine + seq_combine + bool_combine

#############################################################################
## Base function
#############################################################################

class Function(object):
    _name = "id"
    parameters = 0
    default_aggr = "first"
    allow_null = False
    combine_modes = all_combine
    no_column_labels = False
    single_column = True

    def __init__(self, columns=[], value=None, label=None, alias=None, sweep=False, aggr=None, group=[]):
        """
        Parameters
        ----------
        sweep: bool
            True if the function sweeps through the coluns, and False if it 
            sticks to one row at a time during evaluation
        """
        self.columns = columns
        self.sweep = sweep
        self.group = group
        self.alias = alias
        self.value = value
        self.label = label
        if aggr != None:
            self.aggr = aggr
        else:
            self.aggr = self.default_aggr
        self.select = combine_map[self.aggr]

    @classmethod
    def get_name(cls):
        if cls._name in COLUMN_NAMES:
            return COLUMN_NAMES[cls._name]
        else:
            return cls._name

    def get_hash(self):
        l = []
        for x in sorted(dir(self)):
            if not x.startswith("_") and not hasattr(getattr(self, x), "__call__"):
                l.append(str(getattr(self, x)))
        return hashlib.md5(u"".join(l).encode()).hexdigest()
    
    def get_label(self, session):
        if self.label:
            return self.label
        else:
            if self.no_column_labels:
                return self.get_name()
            
            if self.group:
                return "{}({})".format(
                    self.get_name(), 
                    ",".join([session.translate_header(x) for x in self.group]))
            else:
                return "{}({},\"{}\")".format(
                    self.get_name(), 
                    ",".join([session.translate_header(x) for x in self.columns]),
                    self.aggr)
                
            if self.group:
                return "{}({},group={})".format(
                    self.get_name(), 
                    ",".join([session.translate_header(x) for x in self.columns]),
                    ",".join([session.translate_header(x) for x in self.group]))
            else:
                return "{}({},\"{}\")".format(
                    self.get_name(), 
                    ",".join([session.translate_header(x) for x in self.columns]),
                    self.aggr)
    
    def set_label(self, label):
        self.label = label
        
    def _func(self, col):
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
    
    def get_id(self):
        if self.alias:
            return self.alias
        else:
            return "func_{}_{}".format(self.get_name(), self.get_hash())
    
    def find_function(self, df, fun):
        fun_id = fun.get_id()
        for col in df.columns.values:
            if col == fun_id:
                return col
        return None            
    
    def evaluate(self, df, *args, **kwargs):
        val = (df[self.columns].apply(self._func)
                          .apply(self.select, axis="columns"))

        assert isinstance(val, pd.Series)
        assert len(val) == len(df)
        
        return val

#############################################################################
## String functions
#############################################################################

class StringFunction(Function):
    combine_modes = str_combine
    pass

class StringLength(StringFunction):
    _name = "LENGTH"
    combine_modes = num_combine
    
    def _func(self, cols):
        return cols.apply(lambda x: len(str(x)))
    
class StringCount(StringFunction):
    _name = "COUNT"
    parameters = 1
    combine_modes = num_combine
    
    def __init__(self, value, columns=[], *args, **kwargs):
        super(StringCount, self).__init__(columns=columns, value=value, *args, **kwargs)
    
    def _func(self, col):
        return col.apply(lambda x: str(x).count(self.value))
    
class StringChain(StringFunction):
    _name = "CHAIN"
    parameters = 1
    allow_null = True
    combine_modes = ["join"]
    
    def __init__(self, value, columns=[], *args, **kwargs):
        super(StringChain, self).__init__(columns, value=value, *args, **kwargs)
        self.select = self._select
    
    def _select(self, row):
        return self.value.join([str(x) for x in row])

class StringMatch(StringFunction):
    _name = "MATCH"
    parameters = 1
    combine_modes = str_combine
    
    def __init__(self, value, columns=[], *args, **kwargs):
        super(StringMatch, self).__init__(columns, *args, **kwargs)
        self.re = re.compile(value)
    
    def _func(self, col):
        return col.apply(lambda x: self.re.search(str(x)) != None)

class StringExtract(StringMatch):
    _name = "EXTRACT"
    parameters = 1
    combine_modes = str_combine
    
    def _func(self, col):
        def _match(s):
            re = self.re.search(str(s))
            try:
                return re.group()
            except AttributeError:
                return ""

        return col.apply(lambda x: _match(x))

####################
## Numeric functions
####################

class Calc(Function):
    _name = "CALC"
    combine_modes = num_combine
    
    def __init__(self, sign, value=None, columns=[], *args, **kwargs):
        super(Calc, self).__init__(columns, *args, **kwargs)
        self.sign = sign
        self.value = value
        
    def evaluate(self, df, *args, **kwargs):
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
            
        val = df[self.columns[0]]
        for x in self.columns[1:]:
            val = _calc(val, df[x])
        if self.value:
            val = _calc(val, self.value)
        return val

#############################################################################
## Frequency functions
#############################################################################

class Freq(Function):
    _name = "statistics_frequency"
    combine_modes = no_combine
    no_column_labels = True
    default_aggr = "sum"
    
    def evaluate(self, df, *args, **kwargs):
        # do not calculate the frequencies again if the data frame already 
        # contains an identical frequency column:
        fun = Freq(columns=self.columns, group=self.group)
        if self.find_function(df, fun):
            print(self._name, "using df.Freq()")
            return df[fun.get_id()]
        else:
            print(self._name, "calculating df.Freq()")
            
        if len(df) == 0:
            return pd.Series()
        if len(self.columns) == 0:
            return pd.Series(dict(zip(range(1, len(df)+1), [len(df)] * len(df))))
        
        d = {self.columns[0]: "count"}
        d.update({x: "first" for x in [x for x in df.columns.values if x not in self.columns and not x.startswith("coquery_invisible")]})
        val = df.merge((df.groupby(self.columns)
                          .agg(d)
                          .rename(columns={self.columns[0]: self.get_id()})
                          .reset_index()),
                        on=self.columns, how="left")[self.get_id()]
        return val

class FreqPMW(Freq):
    _name = "FREQUENCY_PMW"
    words = 1000000

    def __init__(self, session, columns=[], *args, **kwargs):
        super(FreqPMW, self).__init__(columns, *args, **kwargs)
        self.session = session
    
    def evaluate(self, df, *args, **kwargs):
        val = super(FreqPMW, self).evaluate(df, *args, **kwargs)
        if len(val) > 0:
            corpus_size = self.session.Corpus.get_corpus_size(filters=self.session.filter_list)
        val = val.apply(lambda x: x / (corpus_size / self.words))
        val.index = df.index
        return val
    
class FreqPTW(FreqPMW):
    _name = "FREQUENCY_PTW"
    words = 1000

class FreqNorm(Freq):
    """
    This function returns the normalized frequency, i.e. the number of 
    occurrences relative to the current subcorpus size.
    """
    _name = "FREQ_NORM"
    
    def __init__(self, session, columns=[], *args, **kwargs):
        super(FreqNorm, self).__init__(columns, *args, **kwargs)
        self.session = session

    def evaluate(self, df, *args, **kwargs):
        val = super(FreqNorm, self).evaluate(df, *args, **kwargs)

        if len(val) == 0:
            return pd.Series([])
            
        fun = SubcorpusSize(session=self.session, 
                            columns=self.columns,
                            group=self.group)
        subsize = fun.evaluate(df, *args, **kwargs)

        d = pd.concat([val, subsize], axis=1)
        d.columns = ["val", "subsize"]
        val = d.apply(lambda row: row.val / row.subsize, axis="columns")
        val.index = df.index
        return val

#############################################################################
## Distributional functions
#############################################################################

class Proportion(Freq):
    _name = "PROPORTION"
    no_column_labels = True
    
    def evaluate(self, df, *args, **kwargs):
        fun = Proportion(columns=self.columns, group=self.group)
        if self.find_function(df, fun):
            print(self._name, "using df.Proportion()")
            return df[fun.get_id()]
        else:
            print(self._name, "calculating df.Proportion()")
        val = super(Proportion, self).evaluate(df, *args, **kwargs)
        val = val.apply(lambda x: x / len(df))
        val.index = df.index
        return val
        
class Entropy(Proportion):
    _name = "ENTROPY"
    
    def evaluate(self, df, *args, **kwargs):
        _df = df[self.columns]
        _df["COQ_PROP"] = super(Entropy, self).evaluate(df, *args, **kwargs)
        _df = _df.drop_duplicates()
        if len(_df) == 1:
            entropy = 0.0
        else:
            entropy = -sum(_df["COQ_PROP"].apply(lambda p: p * np.log2(p)))
        return pd.Series([entropy] * len(df), index=df.index)

class Tokens(Function):
    _name = "TOKENS"
    no_column_labels = True
    
    def evaluate(self, df, *args, **kwargs):
        return pd.Series([len(df)] * len(df), index=df.index)

class Types(Function):
    _name = "TYPES"
    no_column_labels = True
    
    def evaluate(self, df, *args, **kwargs):
        length = len(df[self.columns].drop_duplicates())
        return pd.Series([length] * len(df), index=df.index)

class TypeTokenRatio(Types):
    _name = "TYPETOKENRATIO"
    no_column_labels = True
    
    def evaluate(self, df, *args, **kwargs):
        val = super(TypeTokenRatio, self).evaluate(df, *args, **kwargs)
        fun = Tokens(group=self.group).evaluate(df, *args, **kwargs)
        return (pd.DataFrame({"types": val, "tokens": fun}, index=df.index)
                    .apply(lambda row: row.types / row.tokens, axis="columns"))

#############################################################################
## Corpus functions
#############################################################################

class CorpusSize(Function):
    _name = "CORPUSSIZE"
    combine_modes = no_combine
    no_column_labels = True

    def __init__(self, session, columns=[], *args, **kwargs):
        super(CorpusSize, self).__init__(columns, *args, **kwargs)
        self.session = session
    
    def evaluate(self, df, *args, **kwargs):
        corpus_size = self.session.Corpus.get_corpus_size(filters=self.session.filter_list)
        return pd.Series([corpus_size] * len(df), index=df.index)

class SubcorpusSize(CorpusSize):
    _name = "SUBCORPUSSIZE"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        fun = SubcorpusSize(session=self.session, columns=self.columns, group=self.group)
        if self.find_function(df, fun):
            print(self._name, "using df.SubcorpusSize()")
            return df[fun.get_id()]
        else:
            print(self._name, "calculating df.SubcorpusSize()")
        
        corpus_features = [x for x, _ in self.session.Resource.get_corpus_features()]
        column_list = [x for x in corpus_features if "coq_{}_1".format(x) in self.columns]
        
        val = df.apply(self.session.Corpus.get_subcorpus_size, 
                       columns=column_list,
                       axis=1,
                       filters=self.session.filter_list)

        return val

#############################################################################
## Context functions
#############################################################################

class ContextColumns(Function):
    _name = "CONTEXT_COLUMN"
    single_column = False

    def __init__(self, session, *args):
        super(ContextColumns, self).__init__(*args)
        self.session = session
        self.left_cols = ["coq_context_lc{}".format(i+1) for i in range(options.cfg.context_left)][::-1]
        self.right_cols = ["coq_context_rc{}".format(i+1) for i in range(options.cfg.context_right)]

    def evaluate(self, df, connection, *args, **kwargs):
        left, target, right = self.session.Resource.get_context(
            df["coquery_invisible_corpus_id"], 
            df["coquery_invisible_origin_id"],
            df["coquery_invisible_number_of_tokens"], True, connection)
        return pd.Series(
            data=left + right, 
            index=self.left_cols + self.right_cols)

class ContextKWIC(ContextColumns):
    _name = "CONTEXT_KWIC"
    
    def evaluate(self, df, *args, **kwargs):
        row = super(ContextKWIC, self).evaluate(df, *args, **kwargs)
        return pd.Series(
            data=[collapse_words(row[self.left_cols]), collapse_words(row[self.right_cols])], 
            index=[["coq_context_left", "coq_context_right"]])

class ContextString(ContextColumns):
    _name = "CONTEXT_STRING"
    
    def __init__(self, session, *args):
        super(ContextString, self).__init__(session, *args)
        self.word_feature = getattr(self.session.Resource, QUERY_ITEM_WORD)

    def evaluate(self, df, connection, *args, **kwargs):
        left, target, right = self.session.Resource.get_context(
            df["coquery_invisible_corpus_id"], 
            df["coquery_invisible_origin_id"],
            df["coquery_invisible_number_of_tokens"], True, connection)
        return pd.Series(
            data=[collapse_words(list(pd.Series(left + [x.upper() for x in target] + right)))],
            index=["coq_context_string"])

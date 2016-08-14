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

from coquery.defines import *

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
    _name = "id"

    def __init__(self, columns=[], label=None, sweep=False, aggr=None, group=[]):
        """
        Parameters
        ----------
        sweep: bool
            True if the function sweeps through the coluns, and False if it 
            sticks to one row at a time during evaluation
        """
        self.columns = columns
        self.sweep = sweep
        self.label = None
        self.group = group
        
        if aggr:
            self.select = function_map[aggr]

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
            if self.group:
                return "{}({})".format(self._name, ",".join([session.translate_header(x) for x in self.group]))
            else:
                return self._name
                
            if self.group:
                return "{}({},group={})".format(
                    self._name, 
                    ",".join([session.translate_header(x) for x in self.columns]),
                    ",".join([session.translate_header(x) for x in self.group]))
            else:
                return "{}({})".format(self._name, ",".join([session.translate_header(x) for x in self.columns]))
    
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
        return "func_{}_{}".format(self._name, self.get_hash())
    
    def find_function(self, df, fun):
        fun_id = fun.get_id()
        for col in df.columns.values:
            if col == fun_id:
                return col
        return None            
    
    def evaluate(self, df):
        val = (df[self.columns].apply(self._func)
                          .apply(self.select, axis="columns"))

        assert isinstance(val, pd.Series)
        assert len(val) == len(df)
        
        return val

    def select(self, row):
        return row[0]
    
class StringLength(Function):
    _name = "STRING_LENGTH"
    
    def _func(self, cols):
        return cols.apply(len)
    
class StringCount(Function):
    _name = "STRING_COUNT"
    
    def __init__(self, value, columns=[], *args, **kwargs):
        super(Count, self).__init__(columns, *args, **kwargs)
        self.value = value
    
    def _func(self, col):
        return col.apply(lambda x: x.count(self.value))
    
class StringChain(Function):
    _name = "STRING_CHAIN"
    
    def __init__(self, value, columns=[], *args, **kwargs):
        super(Chain, self).__init__(columns, *args, **kwargs)
        self.value = "{}".format(value)
    
    def select(self, row):
        return self.value.join(row)

class StringMatch(Function):
    _name = "STRING_MATCH"
    
    def __init__(self, regex, columns=[], *args, **kwargs):
        super(Match, self).__init__(columns, *args, **kwargs)
        self.re = re.compile(regex)
    
    def _func(self, col):
        return col.apply(lambda x: self.re.search(str(x)) != None)

class StringExtract(StringMatch):
    _name = "STRING_EXTRACT"
    
    def _func(self, col):
        def _match(s):
            re = self.re.search(str(s))
            try:
                return re.group()
            except AttributeError:
                return ""

        return col.apply(lambda x: _match(x))

class Calc(Function):
    _name = "CALC"
    
    def __init__(self, sign, value=None, columns=[], *args, **kwargs):
        super(Calc, self).__init__(columns, *args, **kwargs)
        self.sign = sign
        self.value = value
        
    def evaluate(self, df):
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

class Freq(Function):
    _name = "FREQUENCY"
    
    def evaluate(self, df):
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
    
    def evaluate(self, df):
        val = super(FreqPMW, self).evaluate(df)
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

    def evaluate(self, df):
        val = super(FreqNorm, self).evaluate(df)

        if len(val) == 0:
            return pd.Series([])
            
        fun = SubcorpusSize(session=self.session, 
                            columns=self.columns,
                            group=self.group)
        subsize = fun.evaluate(df)

        d = pd.concat([val, subsize], axis=1)
        d.columns = ["val", "subsize"]
        val = d.apply(lambda row: row.val / row.subsize, axis="columns")
        val.index = df.index
        return val

class Proportion(Freq):
    _name = "PROPORTION"
    
    def evaluate(self, df):
        fun = Proportion(columns=self.columns, group=self.group)
        if self.find_function(df, fun):
            print(self._name, "using df.Proportion()")
            return df[fun.get_id()]
        else:
            print(self._name, "calculating df.Proportion()")
        val = super(Proportion, self).evaluate(df)
        val = val.apply(lambda x: x / len(df))
        val.index = df.index
        return val
        
class Entropy(Proportion):
    _name = "ENTROPY"
    
    def evaluate(self, df):
        _df = df[self.columns]
        _df["COQ_PROP"] = super(Entropy, self).evaluate(df)
        _df = _df.drop_duplicates()
        if len(_df) == 1:
            entropy = 0.0
        else:
            entropy = -sum(_df["COQ_PROP"].apply(lambda p: p * np.log2(p)))
        return pd.Series([entropy] * len(df), index=df.index)

class Tokens(Function):
    _name = "TOKENS"
    
    def evaluate(self, df):
        return pd.Series([len(df)] * len(df), index=df.index)

class Types(Function):
    _name = "TYPES"
    
    def evaluate(self, df):
        length = len(df[self.columns].drop_duplicates())
        return pd.Series([length] * len(df), index=df.index)

class TypeTokenRatio(Types):
    _name = "TYPETOKENRATIO"
    
    def evaluate(self, df):
        val = super(TypeTokenRatio, self).evaluate(df)
        fun = Tokens(group=self.group).evaluate(df)
        return (pd.DataFrame({"types": val, "tokens": fun}, index=df.index)
                    .apply(lambda row: row.types / row.tokens, axis="columns"))

class CorpusSize(Function):
    _name = "CORPUSSIZE"

    def __init__(self, session, columns=[], *args, **kwargs):
        super(CorpusSize, self).__init__(columns, *args, **kwargs)
        self.session = session
    
    def evaluate(self, df):
        corpus_size = self.session.Corpus.get_corpus_size(filters=self.session.filter_list)
        return pd.Series([corpus_size] * len(df), index=df.index)

class SubcorpusSize(CorpusSize):
    _name = "SUBCORPUSSIZE"

    def evaluate(self, df):
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


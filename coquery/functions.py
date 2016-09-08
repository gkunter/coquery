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
from .general import *

try:
    _iqr = stats.iqr
except (AttributeError):
    _iqr = lambda x: np.subtract(*np.percentile(x, [75, 25]))

def _save_first(x):
    l = [y for y in x if y != None]
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

class Function(CoqObject):
    _name = "id"
    parameters = 0
    default_aggr = "first"
    allow_null = False
    combine_modes = all_combine
    no_column_labels = False
    single_column = True

    def __init__(self, columns=[], value=None, label=None, alias=None, sweep=False, aggr=None, group=[], **kwargs):
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

    def get_label(self, session):
        if self.label:
            return self.label
        else:
            if self.group:
                return "{}({})".format(
                    self.get_name(), 
                    "+".join([session.translate_header(x) for x in self.group]))
            if self.no_column_labels:
                return self.get_name()
            else:
                args = []
                args.append(",".join([session.translate_header(x) for x in self.columns]))
                if self.value:
                    args.append('"{}"'.format(self.value))
                if len(self.columns) > 1:
                    args.append('"{}"'.format(self.aggr))
                
                return "{}({})".format(self.get_name(), ", ".join(args))
                    
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
        try:
            val = df[self.columns].apply(self._func)
            val = val.apply(self.select, axis="columns")
        except KeyError:
            val = [np.nan] * len(df)
        return val
    
    @classmethod
    def validate_input(cls, value):
        return bool(value) or cls.allow_null

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
        return cols.apply(lambda x: len(x) if isinstance(x, str) else len(str(x)))
    
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
        self.value = value
        try:
            self.re = re.compile(value)
        except Exception as e:
            self.re = None
    
    def _func(self, col):
        return col.apply(lambda x: ["no", "yes"][bool(self.re.search(str(x)))])
    
    @classmethod
    def validate_input(cls, value):
        try:
            re.compile(value)
        except Exception as e: 
            return False
        else:
            return True

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

class MathFunction(Function):
    _name = "virtual"

class Calc(MathFunction):
    _name = "CALC"
    combine_modes = num_combine
    parameters = 2
    
    def __init__(self, sign="+", value=None, columns=[], *args, **kwargs):
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

class BaseFreq(Function):
    _name = "virtual"

class Freq(BaseFreq):
    _name = "statistics_frequency"
    combine_modes = no_combine
    no_column_labels = True
    default_aggr = "sum"
    
    def evaluate(self, df, *args, **kwargs):
        """
        Count the number of rows with equal values in the target columns.
        """
        fun = Freq(columns=self.columns, group=self.group)
        # do not calculate the frequencies again if the data frame already 
        # contains an identical frequency column:
        if self.find_function(df, fun):
            if options.cfg.verbose:
                print(self._name, "using df.Freq()")
            return df[fun.get_id()]
        else:
            if options.cfg.verbose:
                print(self._name, "calculating df.Freq()")
            
        # ignore external columns:
        columns = [x for x in self.columns if not x.startswith("db_")]
            
        if len(df) == 0:
            return pd.Series(index=df.index)
        if len(columns) == 0:
            # if the function is applied over no columns (e.g. because all 
            # columns are hidden), the function returns a Series containing 
            # simply the length of the data frame:
            return pd.Series([len(df)] * len(df), index = df.index)
        d = {columns[0]: "count"}
        d.update(
            {x: "first" for x in 
                [y for y in df.columns.values if y not in columns and not y.startswith("coquery_invisible")]})
        val = df.merge(df.groupby(columns)
                         .agg(d)
                         .rename(columns={columns[0]: self.get_id()})
                         .reset_index(), 
                       on=columns, how="left")[self.get_id()]
        val.index = df.index
        return val

class FreqPMW(Freq):
    _name = "statistics_per_million_words"
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
    _name = "statistics_per_thousand_words"
    words = 1000

class FreqNorm(Freq):
    """
    This function returns the normalized frequency, i.e. the number of 
    occurrences relative to the current subcorpus size.
    """
    _name = "statistics_normalized"
    
    def __init__(self, session, columns=[], *args, **kwargs):
        super(FreqNorm, self).__init__(columns, *args, **kwargs)
        self.session = session

    def evaluate(self, df, *args, **kwargs):
        val = super(FreqNorm, self).evaluate(df, *args, **kwargs)

        if len(val) == 0:
            return pd.Series([], index=df.index)
            
        fun = SubcorpusSize(session=self.session, 
                            columns=self.columns,
                            group=self.group)
        subsize = fun.evaluate(df, *args, **kwargs)

        d = pd.concat([val, subsize], axis=1)
        d.columns = ["val", "subsize"]
        val = d.apply(lambda row: row.val / row.subsize, axis="columns")
        val.index = df.index
        return val

class RowNumber(Freq):
    _name = "statistics_row_number"
    
    def evaluate(self, df, *args, **kwargs):
        val = pd.Series(range(1, len(df)+1), index=df.index)
        return val


#############################################################################
## Distributional functions
#############################################################################

class BaseProportion(Freq):
    _name = "virtual"

class Proportion(BaseProportion):
    _name = "statistics_proportion"
    no_column_labels = True
    
    def __init__(self, *args, **kwargs):
        super(Proportion, self).__init__(*args, **kwargs)
    
    def evaluate(self, df, *args, **kwargs):
        fun = Proportion(columns=self.columns, group=self.group)
        if self.find_function(df, fun):
            if options.cfg.verbose:
                print(self._name, "using df.Proportion()")
            return df[fun.get_id()]
        else:
            if options.cfg.verbose:
                print(self._name, "calculating df.Proportion()")
        val = super(Proportion, self).evaluate(df, *args, **kwargs)
        val = val.apply(lambda x: x / len(df))
        val.index = df.index
        return val

class Percent(Proportion):
    _name = "statistics_percent"
    
    def evaluate(self, *args, **kwargs):
        return 100 * super(Percent, self).evaluate(*args, **kwargs)
        
class Entropy(Proportion):
    _name = "statistics_entropy"
    # This is a very informative discussion of the relation between entropy 
    # in physics and information science:
    
    # http://www.askamathematician.com/2010/01/q-whats-the-relationship-between-entropy-in-the-information-theory-sense-and-the-thermodynamics-sense/

    # It also contains one of the most useful definitons of entropy that I've
    # come across so far: entropy is a measure of "how hard it is to describe
    # this thing".
    
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
    _name = "statistics_tokens"
    no_column_labels = True
    
    def evaluate(self, df, *args, **kwargs):
        return pd.Series([len(df)] * len(df), index=df.index)

class Types(Function):
    _name = "statistics_types"
    no_column_labels = True
    
    def evaluate(self, df, *args, **kwargs):
        length = len(df[self.columns].drop_duplicates())
        return pd.Series([length] * len(df), index=df.index)

class TypeTokenRatio(Types):
    _name = "statistics_ttr"
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
    _name = "statistics_corpus_size"
    combine_modes = no_combine
    no_column_labels = True

    def __init__(self, session, columns=[], *args, **kwargs):
        super(CorpusSize, self).__init__(columns, *args, **kwargs)
        self.session = session
    
    def evaluate(self, df, *args, **kwargs):
        corpus_size = self.session.Corpus.get_corpus_size(filters=self.session.filter_list)
        return pd.Series([corpus_size] * len(df), index=df.index)

class SubcorpusSize(CorpusSize):
    _name = "statistics_subcorpus_size"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        fun = SubcorpusSize(session=self.session, columns=self.columns, group=self.group)
        if self.find_function(df, fun):
            if options.cfg.verbose:
                print(self._name, "using df.SubcorpusSize()")
            return df[fun.get_id()]
        else:
            if options.cfg.verbose:
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

    def _func(self, row, connection):
        left, target, right = self.session.Resource.get_context(
            row["coquery_invisible_corpus_id"], 
            row["coquery_invisible_origin_id"],
            row["coquery_invisible_number_of_tokens"], True, connection)
        return pd.Series(
            data=left + right, 
            index=self.left_cols + self.right_cols)

    def evaluate(self, df, connection, *args, **kwargs):
        val = df.apply(lambda x: self._func(x, connection), axis="columns")
        val.index = df.index
        return val
        
class ContextKWIC(ContextColumns):
    _name = "CONTEXT_KWIC"
    
    def _func(self, row, connection):
        row = super(ContextKWIC, self)._func(row, connection)
        return pd.Series(
            data=[collapse_words(row[self.left_cols]), collapse_words(row[self.right_cols])], 
            index=[["coq_context_left", "coq_context_right"]])

class ContextString(ContextColumns):
    _name = "CONTEXT_STRING"
    single_column = True
    
    def __init__(self, session, *args):
        super(ContextString, self).__init__(session, *args)
        self.word_feature = getattr(self.session.Resource, QUERY_ITEM_WORD)

    def _func(self, row, connection):
        left, target, right = self.session.Resource.get_context(
            row["coquery_invisible_corpus_id"], 
            row["coquery_invisible_origin_id"],
            row["coquery_invisible_number_of_tokens"], True, connection)
        return pd.Series(
            data=[collapse_words(list(pd.Series(left + [x.upper() for x in target] + right)))],
            index=["coq_context_string"])

#############################################################################
## FunctionList class
#############################################################################

class FunctionList(CoqObject):
    def __init__(self, l=[], *args, **kwargs):
        self._list = l

    def apply(self, df, connection, manager=None):
        if self._list == []:
            return df
        for fun in self._list:
            if fun.single_column:
                df[fun.get_id()] = fun.evaluate(df, connection=connection)
            else:
                val = fun.evaluate(df, connection=connection)
                df = pd.concat([df, val], axis="columns")
        return df

    def get_list(self):
        return self._list
    
    def set_list(self, l):
        self._list = l

    def has_function(self, fun):
        for x in self._list:
            if x.get_id() == fun.get_id():
                return True
        return False

    def add_function(self, fun):
        self._list.append(fun)
        
    def remove_function(self, fun):
        self._list.remove(fun)
        
        for x in self._list:
            if x.get_id() == fun.get_id():
                self.remove_function(x)
    
    def replace_function(self, old, new):
        ix = self._list.index(old)
        self._list[ix] = new
        
    def __iter__(self, *args, **kwargs):
        return self._list.__iter__(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return self._list.__repr__(*args, **kwargs)


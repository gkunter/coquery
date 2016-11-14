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

import random
import string
import re
import sys
import pandas as pd
import numpy as np
from scipy import stats

from . import options
from .defines import *
from .general import *

try:
    max_int = sys.maxint
except AttributeError:
    max_int = sys.maxsize

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
    _name = "virtual"
    parameters = 0
    default_aggr = "first"
    allow_null = False
    combine_modes = all_combine
    no_column_labels = False
    single_column = True
    drop_on_na = True

    @staticmethod
    def get_description():
        return "Base functions"

    def __init__(self, columns=[], value=None, label=None, alias=None, group=[], sweep=False, aggr=None, hidden=False, **kwargs):
        """
        Parameters
        ----------
        sweep: bool
            True if the function sweeps through the coluns, and False if it 
            sticks to one row at a time during evaluation
        """
        self._columns = columns
        self._hidden = hidden
        self.sweep = sweep
        self.alias = alias
        self.group = group
        #if group:
            #print("---- GROUP ARGUMENT USED ----")
        self.value = value
        self._label = label
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

    def get_label(self, session, manager, unlabel=False):
        cols = self.columns(df=None, manager=manager, session=session)
        
        if self._label and not unlabel:
            return self._label
        else:
            if self.group:
                template = "{func}(groups={cols})"
                return template.format(
                    func=self.get_name(), 
                    cols=":".join(["'{}'".format(session.translate_header(x)) for x in options.cfg.group_columns]))
            
            if self.no_column_labels:
                return self.get_name()
            else:
                args = []
                args.append(",".join([session.translate_header(x) for x in cols]))
                if self.value:
                    args.append('"{}"'.format(self.value))
                if len(self.columns(df=None)) > 1:
                    args.append('"{}"'.format(self.aggr))
                
                return "{}({})".format(self.get_name(), ", ".join(args))
                    
    def set_label(self, label):
        self._label = label
        
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
    
    def columns(self, df, **kwargs):
        if df is None or not self.sweep:
            return self._columns
        else:
            return get_visible_columns(df, 
                                        manager=kwargs["manager"],
                                        session=kwargs["session"],
                                        hidden=self._hidden)

    def evaluate(self, df, *args, **kwargs):
        try:
            val = df[self.columns(df, **kwargs)].apply(self._func)
            if len(val.columns) > 1:
                val = val.apply(self.select, axis="columns")
        except (KeyError, ValueError):
            val = pd.Series(data=[np.nan] * len(df))

        return val
    
    @classmethod
    def validate_input(cls, value):
        return bool(value) or cls.allow_null

#############################################################################
## String functions
#############################################################################

class StringFunction(Function):
    combine_modes = str_combine

    @staticmethod
    def get_description():
        return "String functions"

class StringRegEx(StringFunction):

    def __init__(self, value, columns=[], *args, **kwargs):
        super(StringRegEx, self).__init__(columns, *args, **kwargs)
        self.value = value
        try:
            self.re = re.compile(value)
        except Exception as e:
            self.re = None
    
    @classmethod
    def validate_input(cls, value):
        try:
            re.compile(value)
        except Exception as e: 
            return False
        else:
            return True

class StringLength(StringFunction):
    _name = "LENGTH"
    combine_modes = num_combine
    
    def _func(self, cols):
        return cols.apply(lambda x: len(x) if isinstance(x, str) else len(str(x)) if x != None else x)

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

class StringCount(StringRegEx):
    _name = "COUNT"
    parameters = 1
    combine_modes = num_combine
    
    def _func(self, col):
        if self.re == None:
            return pd.Series([pd.np.nan] * len(col), index=col.index)
        else:
            return col.apply(lambda x: len(self.re.findall(x)) if x != None else None)
        #return col.apply(lambda x: str(x).count(self.value) if x != None else x)
    
class StringMatch(StringRegEx):
    _name = "MATCH"
    parameters = 1
    combine_modes = str_combine
    
    def _func(self, col):
        def _match_str(x):
            if x is pd.np.nan or x is None:
                return None
            return bool(self.re.search(x))
                
        def _match(x):
            if x is pd.np.nan or x is None:
                return None
            else: 
                return (self.re.search(str(x)))
                
        if pd.Series(col.dropna().tolist()).dtypes == object:
            return col.apply(lambda x: _match_str(x))
        else:
            return col.apply(lambda x: _match(x))
    
class StringExtract(StringRegEx):
    _name = "EXTRACT"
    parameters = 1
    combine_modes = str_combine
    
    def _func(self, col):
        def _match(s):
            if s == None:
                return None
            re = self.re.search(str(s))
            try:
                return re.group()
            except AttributeError:
                return ""

        return col.apply(lambda x: _match(x))

class StringDecategoricalize(StringFunction):
    _name = "DECAT"
    
    def _func(self, col):
        return col

####################
## Numeric functions
####################

class MathFunction(Function):
    _name = "virtual"

    @staticmethod
    def get_description():
        return "Mathematical functions"

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
            try:
                if self.sign == "+":
                    val1 = val1 + val2
                elif self.sign == "-":
                    val1 = val1 - val2
                elif self.sign == "/":
                    val1 = val1 / val2
                elif self.sign == "*":
                    val1 = val1 * val2
            except:
                val1 = pd.Series([pd.np.nan] * len(val1), index=val1.index)
            return val1
            
        val = df[self.columns(df, **kwargs)[0]]
        for x in self.columns(df, **kwargs)[1:]:
            val = _calc(val, df[x])
        if self.value:
            val = _calc(val, self.value)
        return val

#############################################################################
## Frequency functions
#############################################################################

class BaseFreq(Function):
    _name = "virtual"

    @staticmethod
    def get_description():
        return "Frequency functions"

class Freq(BaseFreq):
    _name = "statistics_frequency"
    combine_modes = no_combine
    no_column_labels = True
    default_aggr = "sum"
    drop_on_na = False
    
    def evaluate(self, df, *args, **kwargs):
        """
        Count the number of rows with equal values in the target columns.
        """
        fun = Freq(columns=self.columns(df, **kwargs), group=self.group)
        # do not calculate the frequencies again if the data frame already 
        # contains an identical frequency column:
        if self.find_function(df, fun):
            if options.cfg.verbose:
                print(self._name, "using df.Freq()")
            return df[fun.get_id()]
        else:
            if options.cfg.verbose:
                print(self._name, "calculating df.Freq()")

        if len(df) == 0:
            return pd.Series(index=df.index)
        try:
            if df["coquery_dummy"].isnull().all():
                return pd.Series([0] * len(df), index = df.index)
        except KeyError:
            # this happens if the data frame does not have the column 
            # 'coquery_dummy'
            pass

        # ignore external columns:
        columns = [x for x in self.columns(df, **kwargs) if not x.startswith("db_")]

        # There is an ugly, ugly bug/feature in Pandas up to at least 0.18.0 
        # which makes grouping unreliable if there are columns with missing 
        # values. 
        # Reference: 
        # http://pandas.pydata.org/pandas-docs/stable/missing_data.html#na-values-in-groupby
        # This is considered rather a bug in this Github issue:
        # https://github.com/pydata/pandas/issues/3729
        
        # The replacement workaround is suggested here:
        # http://stackoverflow.com/questions/18429491
        
        replace_dict = {}
        for x in columns:
            if df[x].isnull().any():
                while True:
                    if df[x].dtype == object:
                        # Random string implementation taken from here:
                        # http://stackoverflow.com/a/2257449/5215507                        
                        repl = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
                    elif df[x].dtype == int:
                        repl = random.randint(-sys.maxsize, +sys.maxsize)
                    elif df[x].dtype == float:
                        repl = random.random()
                    elif df[x].dtype == bool:
                        raise TypeError
                    if (df[x] != repl).all():
                        replace_dict[x] = repl
                        break

                df[x] = df[x].fillna(replace_dict[x])
        
        if len(columns) == 0:
            # if the function is applied over no columns (e.g. because all 
            # columns are hidden), the function returns a Series containing 
            # simply the length of the data frame:
            return pd.Series([len(df)] * len(df), index = df.index)

        d = {columns[0]: "count"}
        d.update(
            {x: "first" for x in 
                [y for y in df.columns.values if y not in columns and not y.startswith(("coquery_invisible"))]})

        val = df.merge(df.groupby(columns)
                         .agg(d)
                         .rename(columns={columns[0]: self.get_id()})
                         .reset_index(), on=columns, how="left")[self.get_id()]
        val.index = df.index

        val.apply(lambda x:int(x) if x != None else x)
        if "coquery_dummy" in df.columns:
            val[df["coquery_dummy"].isnull()] = 0
            
        for x in replace_dict:
            df[x] = df[x].replace(replace_dict[x], pd.np.nan)
            
        return val

class FreqPMW(Freq):
    _name = "statistics_per_million_words"
    words = 1000000

    def __init__(self, columns=[], *args, **kwargs):
        super(FreqPMW, self).__init__(columns, *args, **kwargs)
    
    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        val = super(FreqPMW, self).evaluate(df, *args, **kwargs)
        if len(val) > 0:
            corpus_size = session.Corpus.get_corpus_size(filters=session.filter_list)
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
    
    def __init__(self, columns=[], *args, **kwargs):
        super(FreqNorm, self).__init__(columns, *args, **kwargs)

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]

        val = super(FreqNorm, self).evaluate(df, *args, **kwargs)

        if len(val) == 0:
            return pd.Series([], index=df.index)
            
        fun = SubcorpusSize(session=session,
                            columns=self.columns(df, **kwargs),
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

class Rank(Freq):
    _name = "statistics_rank"
    
    def evaluate(self, df, *args, **kwargs):
        rank_df = df[self.columns(df, **kwargs)].drop_duplicates().reset_index(drop=True)
        rank_df[self._name] = rank_df.sort_values(by=rank_df.columns.tolist()).index.tolist()
        val = df.merge(rank_df, how="left")[self._name]
        val = val + 1
        val.index = df.index
        return val

#############################################################################
## Filter functions
#############################################################################

class BaseFilter(Function):
    _name = "virtual"
    
class FilteredRows(BaseFilter):
    _name = "statistics_filtered_rows"
    
    def evaluate(self, df, *args, **kwargs):
        manager = kwargs["manager"]
        key = kwargs.get("key", None)
        if key:
            pre = manager._len_pre_group_filter.get(key, None)
        else:
            pre = manager._len_pre_filter
        if pre == None:
            pre = len(df)
        val = pd.Series([pre] * len(df), index = df.index)
        return val

class PassingRows(BaseFilter):
    _name = "statistics_passing_rows"
    
    def evaluate(self, df, *args, **kwargs):
        manager = kwargs["manager"]
        key = kwargs.get("key", None)
        if key:
            post = manager._len_post_group_filter.get(key, None)
        else:
            post = manager._len_post_filter
        if post == None:
            post = len(df)
        val = pd.Series([post] * len(df), index = df.index)
        return val

#############################################################################
## Distributional functions
#############################################################################

class BaseProportion(Freq):
    _name = "virtual"

    @staticmethod
    def get_description():
        return "Distribution functions"

class Proportion(BaseProportion):
    _name = "statistics_proportion"
    no_column_labels = True
    
    def __init__(self, *args, **kwargs):
        super(Proportion, self).__init__(*args, **kwargs)
    
    def evaluate(self, df, *args, **kwargs):
        fun = Proportion(columns=self.columns(df, **kwargs), group=self.group)
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
        _df = df[self.columns(df, **kwargs)]
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
        return pd.Series([len(df.dropna())] * len(df), index=df.index)

class Types(Function):
    _name = "statistics_types"
    no_column_labels = True
    
    def evaluate(self, df, *args, **kwargs):
        cols = self.columns(df, **kwargs)
        length = len(df[cols].drop_duplicates())
        return pd.Series([length] * len(df), index=df.index)

class TypeTokenRatio(Types):
    _name = "statistics_ttr"
    no_column_labels = True
    
    def evaluate(self, df, *args, **kwargs):
        types = super(TypeTokenRatio, self).evaluate(df, *args, **kwargs)
        tokens = Tokens(group=self.group, columns=self._columns, hidden=self._hidden).evaluate(df, *args, **kwargs)
        return (pd.DataFrame({"types": types, "tokens": tokens}, index=df.index)
                    .apply(lambda row: row.types / row.tokens, axis="columns"))

class ConditionalProbability(Proportion):
    _name = "statistics_conditional_probability"
    """
    Calculate conditional probabilities for the event ``q`` under the 
    condition ``c``.
    
    The function needs two arguments for ``evaluate()``. ``freq_cond`` 
    specifies the frequency of ``q`` given condition ``c``. 
    ``freq_total`` is the total (unconditioned) frequency of ``q``.
    
    The conditional probability Pcond(q | c) is calculated as 

    Pcond(q | c) = P(c, q) / P(c) = f(c, q) / f(c),
    
    where f(c, q) is the number of occurrences of word c as a left 
    collocate of query token q, and f(c) is the total number of 
    occurrences of c in the corpus. """

    def evaluate(self, df, *args, **kwargs):
        freq_cond = kwargs["freq_cond"]
        freq_total = kwargs["freq_total"]
        return df[freq_cond] / df[freq_total]

class MutualInformation(Proportion):
    _name = "statistics_mutual_information"
    """ Calculate the Mutual Information for two words. f_1 and f_2 are
    the frequencies of the two words, f_coll is the frequency of 
    word 2 in the neighbourhood of word 1, size is the corpus size, and
    span is the size of the neighbourhood in words to the left and right
    of word 2.
    
    Following http://corpus.byu.edu/mutualinformation.asp, MI is 
    calculated as:

        MI = log ( (f_coll * size) / (f_1 * f_2 * span) ) / log (2)
    
    """

    def evaluate(self, df, *args, **kwargs):
        f_1 = kwargs["f_1"]
        f_2 = kwargs["f_2"]
        f_coll = kwargs["f_coll"]
        size = kwargs["size"]
        span = kwargs["span"]

        try:
            val = pd.np.log((df[f_coll] * size) / (df[f_1] * df[f_2] * span)) / pd.np.log(2)
        except (ZeroDivisionError, TypeError, Exception) as e:
            print("Error while calculating mutual information: f1={} f2={} fcol={} size={} span={}".format(f_1, f_2, f_coll, size, span))
            print(e)
            return None
        return val

#############################################################################
## Corpus functions
#############################################################################

class CorpusSize(Function):
    _name = "statistics_corpus_size"
    combine_modes = no_combine
    no_column_labels = True

    @staticmethod
    def get_description():
        return "Corpus size functions"

    def __init__(self, columns=[], *args, **kwargs):
        super(CorpusSize, self).__init__(columns, *args, **kwargs)
    
    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        corpus_size = session.Corpus.get_corpus_size(filters=session.filter_list)
        return pd.Series([corpus_size] * len(df), index=df.index)

class SubcorpusSize(CorpusSize):
    _name = "statistics_subcorpus_size"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        fun = SubcorpusSize(session=session, columns=self.columns(df, **kwargs), group=self.group)
        if self.find_function(df, fun):
            if options.cfg.verbose:
                print(self._name, "using df.SubcorpusSize()")
            return df[fun.get_id()]
        else:
            if options.cfg.verbose:
                print(self._name, "calculating df.SubcorpusSize()")
        
        corpus_features = [x for x, _ in session.Resource.get_corpus_features()]
        column_list = [x for x in corpus_features if "coq_{}_1".format(x) in self.columns(df, **kwargs)]
        
        val = df.apply(session.Corpus.get_subcorpus_size, 
                       columns=column_list,
                       axis=1,
                       filters=session.filter_list)

        return val

#############################################################################
## Context functions
#############################################################################

class SentenceId(Function):
    _name = "coq_sentence_id"
    
    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        val = session.Resource.get_sentence_ids(df["coquery_invisible_corpus_id"])
        assert len(val) == len(df)
        return val

class ContextColumns(Function):
    _name = "coq_context_column"
    single_column = False

    @staticmethod
    def get_description():
        return "Context functions"

    def __init__(self, *args):
        super(ContextColumns, self).__init__(*args)
        self.left_cols = ["coq_context_lc{}".format(i+1) for i in range(options.cfg.context_left)][::-1]
        self.right_cols = ["coq_context_rc{}".format(i+1) for i in range(options.cfg.context_right)]

    def get_id(self):
        if self.alias:
            return self.alias
        return self._name

    def _func(self, row, session):
        if self._sentence_column:
            sentence_id = row[self._sentence_column]
        else:
            sentence_id = None
        left, target, right = session.Resource.get_context(
            row["coquery_invisible_corpus_id"], 
            row["coquery_invisible_origin_id"],
            row["coquery_invisible_number_of_tokens"], session.db_connection,
            sentence_id=sentence_id)
        return pd.Series(
            data=left + right, 
            index=self.left_cols + self.right_cols)

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        if ("coquery_invisible_corpus_id" not in df.columns or
            "coquery_invisible_origin_id" not in df.columns or
            "coquery_invisible_number_of_tokens" not in df.columns or 
            df["coquery_invisible_number_of_tokens"].isnull().any()):
            return pd.Series([None] * len(df), index=df.index, name="coquery_invisible_dummy")
        else:
            self._sentence_column = None
            if options.cfg.context_restrict:
                if hasattr(session.Resource, "corpus_sentence_id"):
                    self._sentence_column = session.Resource.corpus_sentence_id
                elif hasattr(session.Resource, "corpus_sentence"):
                    self._sentence_column = session.Resource.corpus_sentence
                if self._sentence_column:
                    self._sentence_column = "coq_{}_1".format(sentence_col)
                    if self._sentence_column not in df.columns:
                        val = SentenceId(session=session).evaluate(df, session=session)
                        df["coquery_invisible_sentence_id"] = val
                        self._sentence_column = "coquery_invisible_sentence_id"
            val = df.apply(lambda x: self._func(row=x, 
                                            session=session), axis="columns")
            val.index = df.index
            return val
        
class ContextKWIC(ContextColumns):
    _name = "coq_context_kwic"
    
    def _func(self, row, session):
        row = super(ContextKWIC, self)._func(row, session)
        return pd.Series(
            data=[collapse_words(row[self.left_cols]), collapse_words(row[self.right_cols])], 
            index=[["coq_context_left", "coq_context_right"]])

class ContextString(ContextColumns):
    _name = "coq_context_string"
    single_column = True
    
    def __init__(self, *args):
        super(ContextString, self).__init__(*args)

    def _func(self, row, session):
        if self._sentence_column:
            sentence_id = row[self._sentence_column]
        else:
            sentence_id = None
        left, target, right = session.Resource.get_context(
            row["coquery_invisible_corpus_id"], 
            row["coquery_invisible_origin_id"],
            row["coquery_invisible_number_of_tokens"], session.db_connection,
            sentence_id=sentence_id)
        return pd.Series(
            data=[collapse_words(list(pd.Series(left + [x.upper() for x in target] + right)))],
            index=[self._name])

#############################################################################
## Logic functions
#############################################################################

class LogicFunction(Function):
    _name = "virtual"
    combine_modes = bool_combine
    
    @staticmethod
    def get_description():
        return "Logical functions"
    
    def _func(self, cols):
        
        ## make string column comparison:
        if cols.dtype == object:
            return cols.apply(lambda x: self._comp(x, str(self.value)))
        else:
            return cols.apply(lambda x: self._comp(x, float(self.value)))

class Equal(LogicFunction):
    _name = "EQUAL"
    
    def _comp(self, x, y):
        return x == y
    
class NotEqual(LogicFunction):
    _name = "NOTEQUAL"

    def _comp(self, x, y):
        return x != y

class GreaterThan(LogicFunction):
    _name = "GREATERTHAN"

    def _comp(self, x, y):
        return x > y

class LessThan(LogicFunction):
    _name = "LESSTHAN"

    def _comp(self, x, y):
        return x < y

class And(LogicFunction):
    _name = "AND"
    
    def _comp(self, x, y):
        return bool(x and y)

class Or(LogicFunction):
    _name = "OR"
    
    def _comp(self, x, y):
        return bool(x or y)

class Xor(LogicFunction):
    _name = "XOR"
    
    def _comb(self, x, y):
        return bool(x) != bool(y)

class IsTrue(LogicFunction):
    _name = "ISTRUE"
    parameters = 0
    
    def _func(self, cols):
        return cols.apply(lambda x: bool(x))
        
class IsFalse(LogicFunction):
    _name = "ISFALSE"
    parameters = 0
    
    def _func(self, cols):
        return cols.apply(lambda x: not bool(x))

##############################################################################
### Query functions
##############################################################################

#class QueryFunction(Function):
    #_name = "virtual"
    #combine_modes = bool_combine
    
    #@staticmethod
    #def get_description():
        #return "Query functions"

#class QueryString(QueryFunction):
    #_name = "coquery_query_string"
    
    #def _func(self, row, session):
        #return session.queries[row["coquery_invisible_query_number"]].S
    
    #def evaluate(self, df, *args, **kwargs):
        #session = kwargs["session"]
        #val = df.apply(lambda row: session.queries[row["coquery_invisible_query_number"]].query_string, axis="columns")
        #print(val)
        #val.index = df.index
        #return val


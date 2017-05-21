# -*- coding: utf-8 -*-
"""
functions.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

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
import sqlalchemy
import operator
import logging

from . import options, sqlhelper, NAME
from .defines import *
from .general import CoqObject, collapse_words, get_visible_columns
from .gui.pyqt_compat import get_toplevel_window

try:
    max_int = sys.maxint
except AttributeError:
    max_int = sys.maxsize

# use stats.iqr() and stats.mode() if possible, otherwise use
# replacement methods:
try:
    from scipy import stats
    if "iqr" not in dir (stats):
        # the 'iqr' method is not available in Python 2.7:
        raise ImportError
except ImportError:
    import collections

    def _mode(x):
        return collections.Counter(x).most_common()[0][0]

    def _iqr(x):
        return np.subtract(*np.percentile(x, [75, 25]))
else:
    _iqr = stats.iqr
    _mode = stats.mode

def _save_first(x):
    l = [y for y in x if y is not None]
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
    "mode": _mode,
    "IQR": _iqr,
    "first": _save_first,
    "last": _save_last,
    "random": lambda x: np.random.choice(x),
    "join": lambda x, y: y.join(x),
    }

BOOL_COMBINE = ["all", "any", "none"]
SEQ_COMBINE = ["first", "last", "random", "mode", "max", "min"]
NUM_COMBINE = ["sum", "mean", "sd", "median", "IQR"]
NO_COMBINE = []

STR_COMBINE = SEQ_COMBINE + BOOL_COMBINE
NUM_COMBINE = NUM_COMBINE + SEQ_COMBINE
ALL_COMBINE = NUM_COMBINE + SEQ_COMBINE + BOOL_COMBINE


#############################################################################
## Base function
#############################################################################

class Function(CoqObject):
    _name = "virtual"
    parameters = 0
    toggle_parameters = {}
    default_aggr = "first"
    allow_null = False
    combine_modes = ALL_COMBINE
    no_column_labels = False # True if the columns appear in the function name
    single_column = True
    drop_on_na = True

    minimum_columns = None
    maximum_columns = None

    @staticmethod
    def get_description():
        return "Base functions"

    def __init__(self, columns=None, value=None, label=None, alias=None,
                 group=None, aggr=None, **kwargs):
        """
        """
        if columns is None:
            columns = []
        super(Function, self).__init__()
        self.columns = columns
        self.alias = alias
        self.group = group
        self.value = value
        self._label = label
        if aggr is not None:
            self.aggr = aggr
        else:
            self.aggr = self.default_aggr
        self.select = combine_map[self.aggr]

    def __repr__(self):
        return "{}(columns=[{}], value={}, group={}".format(
            self._name, ", ".format(self.columns),
            self.value, self.group)

    @classmethod
    def get_name(cls):
        if cls._name in COLUMN_NAMES:
            return COLUMN_NAMES[cls._name]
        else:
            return cls._name

    def get_flag(self, flag):
        return False

    def get_label(self, session, manager, unlabel=False):
        if self._label and not unlabel:
            return self._label

        if self.group:
            return "{}:{}".format(self.group.name, self.get_name())
        elif self.no_column_labels:
            return self.get_name()
        else:
            args = []
            args.append(",".join([session.translate_header(x)
                                  for x in self.columns]))
            if self.value:
                args.append('"{}"'.format(self.value))
            if len(self.columns) > 1:
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
            if self.group:
                return "func_{}_group_{}".format(self._name, self.get_hash())
            else:
                return "func_{}_{}".format(self._name, self.get_hash())

    def find_function(self, df, fun):
        fun_id = fun.get_id()
        for col in df.columns.values:
            if col == fun_id:
                return col
        return None

    def evaluate(self, df, *args, **kwargs):
        try:
            val = df[self.columns].apply(self._func)
            if len(val.columns) > 1:
                val = val.apply(self.select, axis="columns")
        except (KeyError, ValueError):
            val = self.constant(df, None)

        return val

    @classmethod
    def validate_input(cls, value):
        return bool(value) or cls.allow_null

    def constant(self, df, value):
        """
        Return a Series with constant values.
        """
        return pd.Series(data=[value] * len(df), index=df.index)


#############################################################################
## String functions
#############################################################################

class StringFunction(Function):
    combine_modes = STR_COMBINE

    @staticmethod
    def get_description():
        return "String functions"

    @classmethod
    def validate_regex(cls, value):
        try:
            re.compile(value, re.UNICODE)
        except Exception:
            return False
        else:
            return True

    @classmethod
    def validate_input(cls, value):
        return True


class StringRegEx(StringFunction):
    validate_input = StringFunction.validate_regex

    def __init__(self, value, columns=None, *args, **kwargs):
        super(StringRegEx, self).__init__(columns, *args, **kwargs)
        self.value = value
        try:
            self.re = re.compile(value, re.UNICODE)
        except Exception:
            self.re = None


class StringChain(StringFunction):
    _name = "CONCAT"
    parameters = 1
    allow_null = True

    def evaluate(self, df, *args, **kwargs):
        val = df[self.columns].apply(
                    lambda x: (x.astype(str).str.cat(sep=self.value)
                               if x.dtype != object
                               else x.str.cat(sep=self.value)),
                    axis="columns")
        return val


class StringCount(StringRegEx):
    _name = "COUNT"
    parameters = 1

    def _func(self, cell):
        if cell is None:
            return None

        try:
            match = self.re.findall(cell)
        except TypeError:
            return None

        try:
            return len(match)
        except TypeError:
            return 0

    def evaluate(self, df, *args, **kwargs):
        try:
            if self.re is None:
                raise ValueError
            val = df[self.columns].applymap(self._func)
            if len(val.columns) > 1:
                val = val.apply(self.select, axis="columns")
        except (KeyError, ValueError):
            val = self.constant(df, None)
        return val


class StringSeriesFunction(StringFunction):
    single_column = False

    def evaluate(self, df, value=None, *args, **kwargs):
        # ensure that regex functions use unicode:
        if self.str_func in ("contains", "extract", "count"):
            if "(?u)" not in value:
                value = "(?u){}".format(value)
        if value:
            _df = pd.concat([getattr(df[col].astype(str).str
                                     if df[col].dtype != object
                                     else df[col].str,
                                     self.str_func)
                             (value, *args, **kwargs)
                             for col in self.columns], axis="columns")
        else:
            _df = pd.concat([getattr(df[col].astype(str).str
                                     if df[col].dtype != object
                                     else df[col].str,
                                     self.str_func)
                             (*args, **kwargs)
                             for col in self.columns], axis="columns")

        groups = len(_df.columns) // len(self.columns)
        if groups > 1 or len(self.columns) > 1:
            _df.columns = ["{}_{}_{}".format(self.get_id(), grp + 1, col + 1)
                           for grp in range(groups)
                           for col, _ in enumerate(self.columns)]
        else:
            _df.columns = [self.get_id()]

        return _df.fillna("")


class StringMatch(StringSeriesFunction):
    _name = "MATCH"
    parameters = 1
    toggle_parameters = { "case": ("Case-sensitive", False) }
    str_func = "contains"
    validate_input = StringFunction.validate_regex

    def evaluate(self, df, *args, **kwargs):
        val = super(StringMatch, self).evaluate(df, self.value,
                                                self.get_flag("case"))
        # replace empty strings (which may be caused if the column contains
        # a Null value) by False:
        val = val.replace("", False)
        return val


class StringExtract(StringSeriesFunction):
    _name = "EXTRACT"
    parameters = 1
    toggle_parameter = ("Case-sensitive", False)
    str_func = "extract"
    validate_input = StringFunction.validate_regex

    def evaluate(self, df, *args, **kwargs):
        # put the regex into parentheses if there is no match group:
        if not re.search(r"\([^)]*\)", self.value):
            val = "({})".format(self.value)
        else:
            val = self.value
        return super(StringExtract, self).evaluate(df, val, expand=True)


class StringUpper(StringSeriesFunction):
    _name = "UPPER"
    parameters = 0
    str_func = "upper"

    def evaluate(self, df, *args, **kwargs):
        return super(StringUpper, self).evaluate(df)


class StringLower(StringSeriesFunction):
    _name = "LOWER"
    parameters = 0
    str_func = "lower"

    def evaluate(self, df, *args, **kwargs):
        return super(StringLower, self).evaluate(df)


class StringLength(StringSeriesFunction):
    _name = "LENGTH"
    parameters = 0
    str_func = "len"

    def evaluate(self, df, *args, **kwargs):
        return super(StringLength, self).evaluate(df)


####################
## Numeric functions
####################

class MathFunction(Function):
    _name = "virtual"
    combine_modes = NUM_COMBINE

    @staticmethod
    def get_description():
        return "Mathematical functions"

    def coerce_value(self, df, **kwargs):
        column_dtypes = df[self.columns].dtypes

        if all([dt in (int, float) for dt in column_dtypes]):
            # if all columns are numeric, the value is coerced to float
            return float(self.value)
        elif any([dt == object for dt in column_dtypes]):
            # if there is any string column, the value is coerced to a string:
            return str(self.value)
        elif any([dt == bool for dt in column_dtypes]):
            # if there is any bool column, the value is coerced to a bool:
            return bool(self.value)
        else:
            # undefined behavior
            raise TypeError


class CalcFunction(MathFunction):
    """
    CalcFunction is a meta class that uses the Numpy representation of the
    data frame for the calculations, thus speeding up performance.
    """
    _name = "virtual"

    def evaluate(self, df, *args, **kwargs):
        val = df[self.columns[0]].values
        for x in self.columns[1:]:
            val = self._func(val, df[x].values)
        if self.value:
            const = self.coerce_value(df, **kwargs)
            val = self._func(val, const)
        return pd.Series(data=val, index=df.index)


class Add(CalcFunction):
    _name = "ADD"
    _func = operator.add


class Sub(CalcFunction):
    _name = "SUB"
    _func = operator.sub


class Mul(CalcFunction):
    _name = "MUL"
    _func = operator.mul


class Div(CalcFunction):
    _name = "DIV"
    _func = operator.truediv


class NumpyFunction(CalcFunction):
    """
    NumpyFunction is a wrapper for mathematical functions provided by Numpy.
    The function is specified in the class attribute `_func`.
    """
    _name = "virtual"
    parameters = 0

    def evaluate(self, df, *args, **kwargs):
        _df = df[self.columns]
        val = self._func(_df.values)
        return pd.Series(data=val, index=df.index)


class Min(NumpyFunction):
    _name = "MIN"

    def _func(self, values):
        return pd.np.nanmin(values, axis=1)


class Max(NumpyFunction):
    _name = "MAX"

    def _func(self, values):
        return pd.np.nanmax(values, axis=1)


class Mean(NumpyFunction):
    _name = "MEAN"

    def _func(self, values):
        return pd.np.mean(values, axis=1)


class Median(NumpyFunction):
    _name = "MEDIAN"

    def _func(self, values):
        return pd.np.median(values, axis=1)


class StandardDeviation(NumpyFunction):
    _name = "SD"

    def _func(self, values):
        return pd.np.std(values, axis=1)


class InterquartileRange(NumpyFunction):
    _name = "IQR"

    def _func(self, values):
        return pd.np.subtract(*pd.np.percentile(values, [75, 25], axis=1))


#############################################################################
## Comparisons and Logic functions
#############################################################################

class Comparison(CalcFunction):
    _name = "virtual"
    combine_modes = BOOL_COMBINE

    @staticmethod
    def get_description():
        return "Comparisons"


class Equal(Comparison):
    _name = "EQUAL"
    _func = operator.eq


class NotEqual(Comparison):
    _name = "NOTEQUAL"
    _func = operator.ne


class GreaterThan(Comparison):
    _name = "GREATER"
    _func = operator.gt


class GreaterEqual(Comparison):
    _name = "GREATEREQUAL"
    _func = operator.ge


class LessThan(Comparison):
    _name = "LESS"
    _func = operator.lt


class LessEqual(Comparison):
    _name = "LESSEQUAL"
    _func = operator.le


class LogicFunction(CalcFunction):
    _name = "virtual"
    combine_modes = BOOL_COMBINE

    @staticmethod
    def get_description():
        return "Logical functions"


class And(LogicFunction):
    _name = "AND"
    _func = pd.np.logical_and


class Or(LogicFunction):
    _name = "OR"
    _func = pd.np.logical_or


class Xor(LogicFunction):
    _name = "XOR"
    _func = pd.np.logical_xor

#class IsTrue(LogicFunction):
    #_name = "ISTRUE"
    #parameters = 0

    #def _func(self, cols):
        #return cols.apply(lambda x: bool(x))


#class IsFalse(LogicFunction):
    #_name = "ISFALSE"
    #parameters = 0

    #def _func(self, cols):
        #return cols.apply(lambda x: not bool(x))


#class IsNotMissing(LogicFunction):
    #_name = "ISNOTMISSING"
    #parameters = 0

    #def evaluate(self, df, *args, **kwargs):
        #columns = self.columns(df, **kwargs)
        #val = df[columns].notnull()
        #if len(val.columns) > 1:
            #val = val.apply(self.select, axis="columns")
        #return val


#class IsMissing(IsNotMissing):
    #_name = "ISMISSING"
    #parameters = 0

    #def evaluate(self, df, *args, **kwargs):
        #return ~super(IsMissing, self).evaluate(df, *args, **kwargs)


#class IsNotEmpty(LogicFunction):
    #_name = "ISNOTEMPTY"
    #parameters = 0

    #def evaluate(self, df, *args, **kwargs):
        #columns = self.columns(df, **kwargs)
        #val = df[columns].apply(lambda x: x.notnull() &
                                          #x.index.isin(x.nonzero()[0]))
        #if len(val.columns) > 1:
            #val = val.apply(self.select, axis="columns")
        #return val


#class IsEmpty(IsNotEmpty):
    #_name = "ISEMPTY"

    #def evaluate(self, df, *args, **kwargs):
        #return ~super(IsEmpty, self).evaluate(df, *args, **kwargs)


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
    combine_modes = NO_COMBINE
    no_column_labels = True
    default_aggr = "sum"
    drop_on_na = False

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
        if len(df) == 0:
            return pd.Series(index=df.index)
        try:
            if df["coquery_invisible_dummy"].isnull().all():
                return self.constant(df, 0)
        except KeyError:
            # this happens if the data frame does not have the column
            # 'coquery_invisible_dummy'
            pass
        # ignore external columns:
        columns = [x for x in self.columns if not x.startswith("db_")]
        if len(columns) == 0:
            # if the function is applied over no columns (e.g. because all
            # columns are hidden), the function returns a Series containing
            # simply the length of the data frame:
            val = self.constant(df, len(df))
            return val
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
        d = {columns[0]: "count"}
        d.update(
            {x: "first" for x in
                [y for y in df.columns.values if y not in columns and not y.startswith(("coquery_invisible"))]})
        val = df.merge(df.groupby(columns)
                         .agg(d)
                         .rename(columns={columns[0]: self.get_id()})
                         .reset_index(), on=columns, how="left")[self.get_id()]
        val.index = df.index

        val.apply(lambda x: int(x) if x is not None else x)
        if "coquery_invisible_dummy" in df.columns:
            val[df["coquery_invisible_dummy"].isnull()] = 0

        for x in replace_dict:
            df[x] = df[x].replace(replace_dict[x], pd.np.nan)
        return val


class FreqPMW(Freq):
    _name = "statistics_frequency_pmw"
    words = 1000000

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        val = super(FreqPMW, self).evaluate(df, *args, **kwargs)
        if len(val) > 0:
            corpus_size = session.Corpus.get_corpus_size()
        val = val.apply(lambda x: x / (corpus_size / self.words))
        val.index = df.index
        return val


class FreqPTW(FreqPMW):
    _name = "statistics_frequency_ptw"
    words = 1000


class FreqNorm(Freq):
    """
    This function returns the normalized frequency, i.e. the number of
    occurrences relative to the current subcorpus size.
    """
    _name = "statistics_frequency_normalized"

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]

        val = super(FreqNorm, self).evaluate(df, *args, **kwargs)

        if len(val) == 0:
            return pd.Series([], index=df.index)

        if self.group:
            fun = SubcorpusSize(session=session,
                                columns=self.group.columns,
                                group=self.group)

        else:
            fun = SubcorpusSize(session=session,
                                columns=self.columns, group=self.group)
        subsize = fun.evaluate(df, *args, **kwargs)

        d = pd.concat([val, subsize], axis=1)
        d.columns = ["val", "subsize"]
        val = d.apply(lambda row: row.val / row.subsize, axis="columns")
        val.index = df.index
        return val


class RowNumber(Freq):
    _name = "statistics_row_number"
    maximum_columns = 0

    def evaluate(self, df, *args, **kwargs):
        val = pd.Series(range(1, len(df)+1), index=df.index)
        return val


class Rank(Freq):
    _name = "statistics_rank"

    def evaluate(self, df, *args, **kwargs):
        rank_df = df[self.columns].drop_duplicates().reset_index(drop=True)
        rank_df[self._name] = rank_df.sort_values(by=rank_df.columns.tolist()).index.tolist()
        val = df.merge(rank_df, how="left")[self._name]
        val = val + 1
        val.index = df.index
        return val


#############################################################################
## Reference corpus functions
#############################################################################

import hashlib

class BaseReferenceCorpus(Function):
    _name = "virtual"

    def _get_current_corpus(self):
        ref_corpus = options.cfg.reference_corpus.get(
                         options.cfg.current_server, None)
        res = options.cfg.current_resources[ref_corpus]
        ResourceClass, CorpusClass, LexiconClass, _ = res
        self._current_lexicon = LexiconClass()
        self._current_corpus = CorpusClass()
        self._current_resource = ResourceClass(self._current_lexicon,
                                              self._current_corpus)
        self._current_corpus.resource = self._current_resource
        self._current_corpus.lexicon = self._current_lexicon
        self._current_lexicon.resource = self._current_resource


class ReferenceCorpusFrequency(BaseReferenceCorpus):
    _name = "reference_frequency"
    single_column = True

    def __init__(self, *args, **kwargs):
        super(ReferenceCorpusFrequency, self).__init__(*args, **kwargs)

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        ref_corpus = options.cfg.reference_corpus.get(
                         options.cfg.current_server, None)
        if (not ref_corpus or
                ref_corpus not in options.cfg.current_resources):
            return self.constant(df, None)

        self._get_current_corpus()
        url = sqlhelper.sql_url(options.cfg.current_server,
                                self._current_resource.db_name)
        engine = sqlalchemy.create_engine(url)
        word_feature = getattr(session.Resource, QUERY_ITEM_WORD)
        word_columns = [x for x in df.columns if word_feature in x]
        # concatenate the word columns, separated by space
        self._s = (df[word_columns].astype(str)
                                  .apply(lambda x: x + " ").sum(axis=1))

        # get the frequency from the reference corpus for the concatenated
        # columns:
        val = self._s.apply(lambda x:
                                self._current_corpus.get_frequency(x, engine))
        val.index = df.index
        engine.dispose()
        return val


class ReferenceCorpusFrequencyPMW(ReferenceCorpusFrequency):
    _name = "reference_frequency_pmw"
    words = 1000000

    def evaluate(self, df, *args, **kwargs):
        val = super(ReferenceCorpusFrequencyPMW, self).evaluate(
            df, *args, **kwargs)
        ref_corpus = options.cfg.reference_corpus.get(
                            options.cfg.current_server, None)
        if (not ref_corpus or
                ref_corpus not in options.cfg.current_resources):
            return self.constant(df, None)

        if len(val) > 0:
            corpus_size = self._current_corpus.get_corpus_size()
        val = val.apply(lambda x: x / (corpus_size / self.words))
        val.index = df.index
        return val


class ReferenceCorpusFrequencyPTW(ReferenceCorpusFrequencyPMW):
    words = 1000
    _name = "reference_frequency_ptw"


class ReferenceCorpusLLKeyness(ReferenceCorpusFrequency):
    _name = "reference_ll_keyness"

    def _func(self, x, size, ext_size, width):
        obs = pd.np.array(
            [[x.freq1, x.freq2],
             [size - x.freq1 * width, ext_size - x.freq2 * width]])
        try:
            tmp = stats.chi2_contingency(obs,
                                         lambda_="log-likelihood")
        except ValueError as e:
            print(e)
            return pd.np.nan

        return tmp[0]

    def evaluate(self, df, *args, **kwargs):

        session = kwargs["session"]

        word_feature = getattr(session.Resource, QUERY_ITEM_WORD)
        word_columns = [x for x in df.columns if word_feature in x]

        fun = Freq(columns=word_columns, group=self.group)

        # do not calculate the frequencies again if the data frame already
        # contains an identical frequency column:
        if self.find_function(df, fun):
            if options.cfg.verbose:
                print(self._name, "using df.Freq()")
            freq = df[fun.get_id()]
        else:
            if options.cfg.verbose:
                print(self._name, "calculating df.Freq()")
            freq = fun.evaluate(df)

        if self.columns:
            fun = SubcorpusSize(session=session,
                                columns=self.columns,
                                group=self.group)
            size = fun.evaluate(df, *args, **kwargs).unique()
        else:
            fun = CorpusSize(session=session)
            size = fun.evaluate(df, *args, **kwargs).unique()

        ext_freq = super(ReferenceCorpusLLKeyness, self).evaluate(
            df, *args, **kwargs)
        if len(ext_freq) > 0:
            ext_size = self._current_corpus.get_corpus_size()

        _df = pd.DataFrame({"freq1": freq, "freq2": ext_freq})
        if len(word_columns) > 1:
            logger.warning("LL calculation for more than one column is experimental!")
        val = _df.apply(lambda x: self._func(x,
                                             size=size, ext_size=ext_size,
                                             width=len(word_columns)),
                        axis="columns")
        return val


class ReferenceCorpusSize(BaseReferenceCorpus):
    _name = "reference_corpus_size"

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        self._get_current_corpus()
        ext_size = self._current_corpus.get_corpus_size()
        return self.constant(df, ext_size)


class ReferenceCorpusDiffKeyness(ReferenceCorpusLLKeyness):
    _name = "reference_diff_keyness"

    def _func(self, x, size, ext_size, width):
        return ((x.freq1/size - x.freq2/ext_size) * 100 /
                (x.freq2/ext_size))


#############################################################################
## Filter functions
#############################################################################

#class BaseFilter(Function):
    #_name = "virtual"


#class FilteredRows(BaseFilter):
    #_name = "statistics_filtered_rows"

    #def evaluate(self, df, *args, **kwargs):
        #manager = kwargs["manager"]
        #key = kwargs.get("key", None)
        #if key:
            #pre = manager._len_pre_group_filter.get(key, None)
        #else:
            #pre = manager._len_pre_filter
        #if pre is None:
            #pre = len(df)
        #val = self.constant(df, pre)
        #return val


#class PassingRows(BaseFilter):
    #_name = "statistics_passing_rows"

    #def evaluate(self, df, *args, **kwargs):
        #manager = kwargs["manager"]
        #key = kwargs.get("key", None)
        #if key:
            #post = manager._len_post_group_filter.get(key, None)
        #else:
            #post = manager._len_post_filter
        #if post is None:
            #post = len(df)
        #val = self.constant(df, post)
        #return val


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
        val = val / len(val)
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
        props = _df["COQ_PROP"].values
        if len(_df) == 1:
            entropy = 0.0
        else:
            entropy = -sum(props * np.log2(props))
        val = self.constant(df, entropy)
        return val

class Tokens(Function):
    _name = "statistics_tokens"
    no_column_labels = True
    maximum_columns = 0

    def evaluate(self, df, *args, **kwargs):
        val = self.constant(df, len(df.dropna(how="all")))
        return val


class Types(Function):
    _name = "statistics_types"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        val = self.constant(df, len(df[self.columns].drop_duplicates()))
        return val


class TypeTokenRatio(Types):
    _name = "statistics_ttr"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        types = super(TypeTokenRatio, self).evaluate(df, *args, **kwargs)
        tokens = Tokens(group=self.group,
                        columns=self.columns).evaluate(df, *args, **kwargs)
        df = pd.DataFrame(data={"types": types, "tokens": tokens},
                          index=df.index)
        val = df.apply(lambda row: row.types / row.tokens, axis="columns")
        return val


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

    def evaluate(self, df, freq_cond, freq_total, *args, **kwargs):
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

    def evaluate(self, df, f_1, f_2, f_coll, size, span, *args, **kwargs):
        try:
            val = pd.np.log((df[f_coll] * size) / (f_1 * df[f_2] * span)) / pd.np.log(2)
        except (ZeroDivisionError, TypeError, Exception) as e:
            print("Error while calculating mutual information:\nf1={} f2='{}' fcol='{}' size={} span={}".format(f_1, f_2, f_coll, size, span))
            print(df.head())
            print(e)
            return None
        return val


#############################################################################
## Corpus functions
#############################################################################

class CorpusSize(Function):
    _name = "statistics_corpus_size"
    combine_modes = NO_COMBINE
    no_column_labels = True

    @staticmethod
    def get_description():
        return "Corpus size functions"

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        corpus_size = session.Corpus.get_corpus_size()
        val = self.constant(df, corpus_size)
        return val


class SubcorpusSize(CorpusSize):
    _name = "statistics_subcorpus_size"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        try:
            session = kwargs["session"]
            manager = kwargs["manager"]
            fun = SubcorpusSize(session=session,
                                columns=self.columns, group=self.group)
            if self.find_function(df, fun):
                if options.cfg.verbose:
                    print(self._name, "using {}".format(self))
                return df[fun.get_id()]
            else:
                if options.cfg.verbose:
                    print(self._name, "calculating {}".format(self))
            corpus_features = [x for x, _
                               in session.Resource.get_corpus_features()]
            column_list = [x for x in corpus_features
                           if "coq_{}_1".format(x) in self.columns]
            if df.iloc[0].coquery_invisible_dummy is not pd.np.nan:
                val = df.apply(session.Corpus.get_subcorpus_size,
                            columns=column_list,
                            axis=1,
                            subst=manager.get_column_substitutions)
            else:
                val = df.Series(name=self.get_id())
            return val
        except Exception as e:
            print(e)
            raise e

class SubcorpusRangeMin(CorpusSize):
    _name = "statistics_subcorpus_range_min"

    def _func(self, row, session):
        min_r, max_r = session.Corpus.get_subcorpus_range(row)
        return min_r

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]

        corpus_features = [x for x, _ in
                           session.Resource.get_corpus_features()]
        column_list = [col for col in self.columns if col in
                       ["coq_{}_1".format(y) for y in corpus_features]]
        val = df.apply(lambda x: self._func(x[column_list], session), axis=1)
        return val


class SubcorpusRangeMax(SubcorpusRangeMin):
    _name = "statistics_subcorpus_range_max"

    def _func(self, row, session):
        min_r, max_r = session.Corpus.get_subcorpus_range(row)
        return max_r


#############################################################################
## Context functions
#############################################################################

class SentenceId(Function):
    _name = "coq_sentence_id"

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        _df = pd.merge(df,
                        session.Resource.get_sentence_ids(
                       df["coquery_invisible_corpus_id"]),
                       how="left", on="coquery_invisible_corpus_id")
        return _df["coquery_invisible_sentence_id"]


class ContextColumns(Function):
    _name = "coq_context_column"
    single_column = False

    @staticmethod
    def get_description():
        return "Context functions"

    def __init__(self, *args):
        super(ContextColumns, self).__init__(*args)
        self.left_cols = ["coq_context_lc{}".format(options.cfg.context_left - i) for i in range(options.cfg.context_left)]
        self.right_cols = ["coq_context_rc{}".format(i+1) for i in range(options.cfg.context_right)]

    def get_id(self):
        if self.alias:
            return self.alias
        return self._name

    def _func(self, row, session, connection):
        if self._sentence_column:
            sentence_id = row[self._sentence_column]
        else:
            sentence_id = None
        left, target, right = session.Resource.get_context(
            row["coquery_invisible_corpus_id"],
            row["coquery_invisible_origin_id"],
            row["coquery_invisible_number_of_tokens"],
            connection,
            sentence_id=sentence_id)

        val = pd.Series(
            data=left + right,
            index=self.left_cols + self.right_cols)
        return val

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        with session.db_engine.connect() as db_connection:
            if ("coquery_invisible_corpus_id" not in df.columns or
                "coquery_invisible_origin_id" not in df.columns or
                "coquery_invisible_number_of_tokens" not in df.columns or
                df["coquery_invisible_number_of_tokens"].isnull().any()):
                    val = self.constant(df, None)
                    val.name = "coquery_invisible_dummy"
                    return val
            else:
                self._sentence_column = None
                if options.cfg.context_restrict:
                    if hasattr(session.Resource, "corpus_sentence_id"):
                        self._sentence_column = session.Resource.corpus_sentence_id
                    elif hasattr(session.Resource, "corpus_sentence"):
                        self._sentence_column = session.Resource.corpus_sentence
                    if self._sentence_column:
                        self._sentence_column = "coq_{}_1".format(self._sentence_column)
                        if self._sentence_column not in df.columns:
                            val = SentenceId(session=session).evaluate(df, session=session)
                            df["coquery_invisible_sentence_id"] = val
                            self._sentence_column = "coquery_invisible_sentence_id"
                get_toplevel_window().useContextConnection.emit(db_connection)
                val = df.apply(lambda x: self._func(row=x,
                                                    session=session,
                                                    connection=db_connection),
                               axis="columns")
                get_toplevel_window().closeContextConnection.emit(db_connection)
                val.index = df.index
                return val


class ContextKWIC(ContextColumns):
    _name = "coq_context_kwic"

    def _func(self, row, session, connection):
        row = super(ContextKWIC, self)._func(row, session, connection)
        val = pd.Series(
            data=[collapse_words(row[self.left_cols]),
                  collapse_words(row[self.right_cols])],
            index=[["coq_context_left", "coq_context_right"]])
        return val


class ContextString(ContextColumns):
    _name = "coq_context_string"
    single_column = True

    def __init__(self, *args):
        super(ContextString, self).__init__(*args)

    def _func(self, row, session, connection):
        if self._sentence_column:
            sentence_id = row[self._sentence_column]
        else:
            sentence_id = None
        left, target, right = session.Resource.get_context(
            row["coquery_invisible_corpus_id"],
            row["coquery_invisible_origin_id"],
            row["coquery_invisible_number_of_tokens"], connection,
            sentence_id=sentence_id)
        return pd.Series(
            data=[collapse_words(list(pd.Series(
                                        left +
                                        [x.upper() for x in target if x] +
                                        right)))],
                                        index=[self._name])


##############################################################################
### Query functions
##############################################################################

#class QueryFunction(Function):
    #_name = "virtual"
    #combine_modes = BOOL_COMBINE

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

logger = logging.getLogger(NAME)

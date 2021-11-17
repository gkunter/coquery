# -*- coding: utf-8 -*-
"""
functions.py is part of Coquery.

Copyright (c) 2016-2020 Gero Kunter (gero.kunter@coquery.org)

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
import operator
import logging
import numbers
from scipy import stats

from . import options
from .defines import COLUMN_NAMES, QUERY_ITEM_WORD
from .general import CoqObject, collapse_words
from .gui.pyqt_compat import get_toplevel_window
from .errors import RegularExpressionError

# make sure reduce() is available
try:
    from functools import reduce
except (ImportError):
    # in python 2.7, reduce() is still a built-in method
    pass
assert reduce


def get_base_func(fun):
    """
    Returns the base function class for `fun`, which may either be a function
    instance or a function class.

    A base function class is defined as a function class that has name other
    than "virtual".
    """
    if type(fun) is not type:
        fun_class = type(fun)
    else:
        fun_class = fun

    if fun_class._name == "virtual":
        return fun_class

    for parent in fun_class.__bases__:
        try:
            return get_base_func(parent)
        except AttributeError:
            return fun_class
    return fun_class


#############################################################################
## Base function
#############################################################################

class Function(CoqObject):
    _name = "virtual"
    allow_null = False

    # set no_column_lables to True if the columns appear in the function name
    no_column_labels = False
    single_column = True
    drop_on_na = True

    minimum_columns = None
    maximum_columns = None

    # The property 'arguments' contains the number and type of arguments that
    # the function requires.
    # Each element of the two lists is a tuple that specifies an argument.
    # The tuples contain three elements:
    #   (1) the internal name of the argument
    #   (2) the label displayed on the widget
    #   (3) the default value

    arguments = {"string": [],
                 "check": []}

    @staticmethod
    def get_group():
        return "Base functions"

    def __init__(self, columns=None, label=None, alias=None,
                 group=None, **kwargs):
        """
        """
        if columns is None:
            columns = []
        super(Function, self).__init__()
        self.columns = columns
        self.alias = alias
        self.group = group
        self._label = label
        self.kwargs = kwargs

    def __repr__(self):
        return "{}(columns=[{}], kwargs={}, group={})".format(
            self._name, ", ".join(["'{}'".format(x) for x in self.columns]),
            str(self.kwargs), self.group)

    @classmethod
    def get_name(cls):
        if cls._name in COLUMN_NAMES:
            return COLUMN_NAMES[cls._name]
        else:
            return cls._name

    @classmethod
    def get_description(cls):
        return getattr(cls, "_description", None)

    def get_flag(self, flag):
        if flag == "case":
            try:
                ignore_case = self.kwargs["case"] is False
            except KeyError:
                ignore_case = True

            return re.IGNORECASE if ignore_case else 0

        return False

    def get_label(self, session, unlabel=False):
        if self._label and not unlabel:
            return self._label

        if self.group:
            return "{}:{}".format(self.group.name, self.get_name())
        elif self.no_column_labels:
            return self.get_name()
        else:
            args = []
            if session is not None:
                args.append(",".join([session.translate_header(x)
                                      for x in self.columns]))
            else:
                args.append(",".join(self.columns))

            for kw in [x for x in self.kwargs if x not in ("session")]:
                val = self.kwargs[kw]
                if val is not None:
                    if isinstance(val, numbers.Number):
                        fmt = "{}"
                    else:
                        fmt = "'{}'"
                    args.append(fmt.format(self.kwargs[kw]))

            return "{}({})".format(self.get_name(), ", ".join(args))

    def set_label(self, label):
        self._label = label

    def _func(self, series, *args, **kwargs):
        """
        Defines the function that is applied the columns in the data frame
        that is passed to this function.

        Parameters
        ----------
        series : pandas.Series
            A column from a data frame

        Returns
        -------
        series : pandas.Series
            The column after the function has been applied
        """
        return series

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

    def evaluate(self, df, **kwargs):
        try:
            val = df[self.columns].apply(self._func)
        except (KeyError, ValueError):
            val = self.constant(df, None)

        return val

    @classmethod
    def validate_input(cls, value):
        return bool(value) or cls.allow_null

    @staticmethod
    def constant(df, value):
        """
        Return a Series with constant values.
        """
        return pd.Series(data=[value] * len(df), index=df.index)

    def get_reference(self, **kwargs):
        """
        Return an instance of the currently active reference corpus.
        """
        ref_corpus = options.cfg.reference_corpus.get(
            options.cfg.current_connection.name, None)
        if ref_corpus is None:
            return None
        res = options.cfg.current_connection.resources()[ref_corpus]
        ResourceClass, CorpusClass, _ = res
        corpus = CorpusClass()
        resource = ResourceClass(None, corpus)
        corpus.resource = resource

        return resource

#############################################################################
## Conversion functions
#############################################################################


class ConversionFunction(Function):
    @staticmethod
    def get_group():
        return "Conversion"


class ToCategory(ConversionFunction):
    _name = "CATEGORICAL"

    def evaluate(self, df, **kwargs):
        d = {}

        for col in self.columns:
            d[col] = df[col].astype(str)
            d[col][df[col].isnull()] = None

        return pd.DataFrame(d)


class ToNumeric(ConversionFunction):
    _name = "NUMERICAL"

    def evaluate(self, df, **kwargs):
        return pd.DataFrame({col: pd.to_numeric(df[col], errors="coerce")
                             for col in self.columns})

class ToInteger(ConversionFunction):
    _name = "INTEGER"
    _description = "Round to integer"

    def evaluate(self, df, **kwargs):
        return pd.DataFrame(
            {col: pd.to_numeric(df[col], errors="coerce").round().astype(int)
             for col in self.columns})

#############################################################################
## String functions
#############################################################################


class StringFunction(Function):
    @staticmethod
    def get_group():
        return "Strings"

    @classmethod
    def validate_regex(cls, value):
        try:
            re.compile(value, re.UNICODE)
        except re.error:
            return False
        else:
            return True

    @classmethod
    def validate_input(cls, value):
        return True


class StringChain(StringFunction):
    _name = "CONCAT"
    allow_null = True

    arguments = {"string": [("sep", "Separator:", "-")]}

    def evaluate(self, df, **kwargs):
        val = df[self.columns].apply(
                    lambda x: (x.astype(str).str.cat(**kwargs)
                               if x.dtype != object
                               else x.str.cat(**kwargs)),
                    axis="columns")
        return val


class StringSeriesFunction(StringFunction):
    single_column = False
    fill_na = ""

    def evaluate(self, df, **kwargs):

        # eliminate 'session' and 'manager' keywords because they are not
        # accepted by the Series string functions:
        try:
            kwargs.pop("session")
        except KeyError:
            pass
        try:
            kwargs.pop("manager")
        except KeyError:
            pass

        if self.str_func in ("replace", "contains", "extract", "count"):
            # ensure that regex functions use unicode:
            pat = kwargs["pat"]
            if "(?u)" not in pat:
                kwargs["pat"] = "(?u){}".format(pat)

            # add case-sensitivity flag:
            kwargs["flags"] = self.get_flag("case")
            try:
                kwargs.pop("case")
            except KeyError:
                pass

        columns = []

        for col in self.columns:
            if df[col].dtype != object:
                # get string function from converted column
                fnc = getattr(df[col].astype(str).str, self.str_func)
            else:
                # get string function from original column
                fnc = getattr(df[col].str, self.str_func)

            try:
                val = fnc(**kwargs)
            except re.error as e:
                pos = e.pos
                if "(?u)" not in pat:
                    pos = pos - 3
                raise RegularExpressionError(self.get_name(), pat, pos, e.msg)
            columns.append(val)
        _df = pd.concat(columns, axis="columns")

        groups = len(_df.columns) // len(self.columns)
        if groups > 1 or len(self.columns) > 1:
            _df.columns = ["{}_{}_{}".format(self.get_id(), grp + 1, col + 1)
                           for grp in range(groups)
                           for col, _ in enumerate(self.columns)]
        else:
            _df.columns = [self.get_id()]

        return _df.fillna(self.fill_na) if self.fill_na is not None else _df


class StringCount(StringSeriesFunction):
    _name = "COUNT"
    str_func = "count"
    fill_na = 0
    validate_input = StringFunction.validate_regex
    arguments = {"string": [("pat", "Regular expression:", "")],
                 "check": [("case", "Case-sensitive:", False)]}


class StringMatch(StringSeriesFunction):
    _name = "MATCH"
    str_func = "contains"
    fill_na = False
    validate_input = StringFunction.validate_regex
    arguments = {"string": [("pat", "Regular expression:", "")],
                 "check": [("case", "Case-sensitive:", False)]}

    def evaluate(self, df, **kwargs):
        val = super(StringMatch, self).evaluate(df, **kwargs)
        # replace empty strings (which may be caused if the column contains
        # a Null value) by False:
        val = val.replace("", self.fill_na)
        return val


class StringExtract(StringSeriesFunction):
    _name = "EXTRACT"
    str_func = "extract"
    validate_input = StringFunction.validate_regex
    arguments = {"string": [("pat", "Regular expression:", "")],
                 "check": [("case", "Case-sensitive:", False)]}

    def evaluate(self, df, **kwargs):
        pat = kwargs["pat"]
        # put the regex into parentheses if there is no match group:
        if not re.search(r"\([^)]*\)", pat):
            pat = "({})".format(pat)
        kwargs["pat"] = pat
        kwargs["expand"] = True

        return super(StringExtract, self).evaluate(df, **kwargs)


class StringReplace(StringSeriesFunction):
    _name = "REPLACE"
    str_func = "replace"
    fill_na = None

    arguments = {"string": [("pat", "Find:", ""),
                            ("repl", "Replace:", "")],
                 "check": [("case", "Case-sensitive:", False)]}


class StringUpper(StringSeriesFunction):
    _name = "UPPER"
    str_func = "upper"
    fill_na = None


class StringLower(StringSeriesFunction):
    _name = "LOWER"
    str_func = "lower"
    fill_na = None


class StringLength(StringSeriesFunction):
    _name = "LENGTH"
    str_func = "len"
    fill_na = 0


####################
## Numeric functions
####################

class NumFunction(Function):
    _name = "virtual"

    @staticmethod
    def get_group():
        return "Mathematics"

    def coerce_value(self, df, value):
        """
        Coerce the function argument to the appropriate type depending on the
        values of the supplied data frame.
        """

        column_dtypes = df[self.columns].dtypes

        if all([dt in (int, float) for dt in column_dtypes]):
            # if all columns are numeric, the value is coerced to float
            return float(value)
        elif any([dt == object for dt in column_dtypes]):
            # if there is any string column, the value is coerced to a string:
            return str(value)
        elif any([dt == bool for dt in column_dtypes]):
            # if there is any bool column, the value is coerced to a bool:
            return bool(value)
        else:
            # undefined behavior
            raise TypeError


class CalcFunction(NumFunction):
    """
    CalcFunction is a meta class that uses the Numpy representation of the
    data frame for the calculations, thus speeding up performance.
    """
    _name = "virtual"
    _ignore_na = False
    arguments = {"float": [("value", "Value:", None)]}

    def evaluate(self, df, **kwargs):
        parameter = kwargs.get("value", None)
        if len(self.columns) == 1 and not parameter:
            val = reduce(self._func, df[self.columns[0]].values)
        else:
            val = df[self.columns[0]].values
            for x in self.columns[1:]:
                val = self._func(val, df[x].values)
            if parameter:
                const = self.coerce_value(df, parameter)
                val = self._func(val, const)
            if not self._ignore_na:
                nan_rows = np.any(pd.isnull(df[self.columns].values),
                                     axis=1)
                if nan_rows.any():
                    val = val.astype(object)
                    val[nan_rows] = None
        return pd.Series(data=val, index=df.index)


class OperatorFunction(CalcFunction):
    """
    Functions that define mathematical operations (addition, subtraction,
    division, multiplication).
    """

    @staticmethod
    def get_group():
        return "Calculations"


class Add(OperatorFunction):
    _name = "ADD"
    _func = operator.add


class Sub(OperatorFunction):
    _name = "SUB"
    _func = operator.sub


class Mul(OperatorFunction):
    _name = "MUL"
    _func = operator.mul


class Div(OperatorFunction):
    _name = "DIV"
    _func = operator.truediv


class Log(OperatorFunction):
    _name = "LOG"
    single_column = False
    arguments = {"choose": [("base", "Base:", "Log",
                             ("Log2", "Log10", "LogN"))]}

    def evaluate(self, df, **kwargs):
        base = kwargs.get("base")
        func = {"Log2": np.log2,
                "Log10": np.log10,
                "LogN": np.log}[base]

        val = func(df[self.columns].values)
        if len(self.columns) > 1:
            columns = ["{}_{}".format(self.get_id(), col + 1)
                       for col, _ in enumerate(self.columns)]
        else:
            columns = [self.get_id()]

        val = pd.DataFrame(data=val, index=df.index, columns=columns)
        return val


class Modulo(OperatorFunction):
    _name = "MOD"
    _func = operator.mod
    _description = ("Apply the modulo operation, i.e. determine the "
                    "remainder after division")


class Binning(OperatorFunction):
    _name = "BINNING"
    _description = ("Transforms a number to the bin value given the "
                    "argument")

    def _func(self, val, bw):
        return (val // bw) * bw

class StatisticalFunction(CalcFunction):
    """
    NumpyFunction is a wrapper for statistical functions provided by Numpy.
    The function is specified in the class attribute `_func`.
    """
    _name = "virtual"
    arguments = {}

    @staticmethod
    def get_group():
        return "Statistics"

    def evaluate(self, df, **kwargs):
        _df = df[self.columns]
        if len(self.columns) == 1:
            val = self._func(_df.values, axis=None, **kwargs)
        else:
            val = self._func(_df.values, **kwargs)

        return pd.Series(data=val, index=df.index)


class Min(StatisticalFunction):
    _name = "MIN"

    def _func(self, values, axis=1, **kwargs):
        return np.nanmin(values, axis=axis)


class Max(StatisticalFunction):
    _name = "MAX"

    def _func(self, values, axis=1, **kwargs):
        return np.nanmax(values, axis=axis)


class Mean(StatisticalFunction):
    _name = "MEAN"

    def _func(self, values, axis=1, **kwargs):
        return np.mean(values, axis=axis)


class Median(StatisticalFunction):
    _name = "MEDIAN"

    def _func(self, values, axis=1, **kwargs):
        return np.median(values, axis=axis)


class StandardDeviation(StatisticalFunction):
    _name = "SD"

    def _func(self, values, axis=1, **kwargs):
        return np.std(values, axis=axis)


class InterquartileRange(StatisticalFunction):
    _name = "IQR"

    def _func(self, values, axis=1, **kwargs):
        return np.subtract(
            *np.percentile(values, [75, 25], axis=axis))


class Percentile(StatisticalFunction):
    _name = "Percentile"
    arguments = {"float": [("value", "Percentile", 95, (0, 100))]}

    def _func(self, values, axis=1, **kwargs):
        return np.percentile(values, kwargs["value"], axis=axis)


#############################################################################
## Comparisons and Logic functions
#############################################################################

class Comparison(CalcFunction):
    _name = "virtual"
    _ignore_na = True
    arguments = {"string": [("value", "Value:", "")]}

    @staticmethod
    def get_group():
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
    _ignore_na = False

    @staticmethod
    def get_group():
        return "Logic"


class And(LogicFunction):
    _name = "AND"
    _func = np.logical_and


class Or(LogicFunction):
    _name = "OR"
    _func = np.logical_or


class Xor(LogicFunction):
    _name = "XOR"
    _func = np.logical_xor


class Not(LogicFunction):
    _name = "NOT"
    _func = np.logical_not


class If(And):
    _name = "IF"
    arguments = {"string": [("value1", "Then:", ""),
                            ("value2", "Else:", "")]}

    def evaluate(self, df, **kwargs):
        then_val = kwargs.pop("value1")
        else_val = kwargs.pop("value2")
        kwargs["value"] = True
        val = super(If, self).evaluate(df, **kwargs)

        # apply conditional replacement:
        recode = np.where(val, then_val, else_val)

        _null = pd.isnull(val)
        # replace NaN results by NaN (because np.nan AND True evaluates to
        # True, see e.g. https://stackoverflow.com/q/17273312/)
        if _null.any():
            recode = recode.astype(object)
            recode[val.index[_null]] = None
        return pd.Series(data=recode, index=val.index)


class IfAny(If, Or):
    _name = "IFANY"


class IsTrue(LogicFunction):
    _name = "TRUE"
    parameters = 0

    def evaluate(self, df, **kwargs):
        return pd.DataFrame(data=np.vectorize(operator.truth)(df.values),
                            index=df.index,
                            columns=df.columns)


class IsFalse(IsTrue):
    _name = "FALSE"
    parameters = 0

    def evaluate(self, df, **kwargs):
        return ~super(IsFalse, self).evaluate(df, **kwargs)


class Missing(LogicFunction):
    _name = "MISSING"
    arguments = {}

    def evaluate(self, df, **kwargs):
        val = ~df[self.columns].notnull()
        return val


class Empty(LogicFunction):
    _name = "EMPTY"
    arguments = {}

    def evaluate(self, df, **kwargs):
        val = (~df[self.columns].notnull() |
               df[self.columns].apply(
                   lambda x: ~x.index.isin(x.nonzero()[0])))
        return val


#############################################################################
## Frequency functions
#############################################################################

class BaseFreq(Function):
    _name = "virtual"

    @staticmethod
    def get_group():
        return "Frequencies"


class Freq(BaseFreq):
    _name = "statistics_frequency"
    no_column_labels = True
    drop_on_na = False

    DUMMY_STR = np.array(list(string.ascii_uppercase + string.digits))

    def evaluate(self, df, **kwargs):
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
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html#na-values-in-groupby
        # This is considered rather a bug in this Github issue:
        # https://github.com/pydata/pandas/issues/3729

        # The replacement workaround based on this post:
        # https://stackoverflow.com/a/18431417
        #
        # What the workaround does is this:
        # 1. Try to find a replacement value that doesn't occur as a valid
        #    value in the involved columns
        # 2. Replace the missing values in that column by the replacement value
        # 3. Calculate the frequencies of each valid value in the selected
        #    columns
        # 4. Replace the replacement value by NaN

        replace_dict = {}
        for x in columns:
            if df[x].isnull().any():
                while True:
                    if df[x].dtype == object:
                        repl = "".join(np.random.choice(Freq.DUMMY_STR, 20))
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

        d = {x: "first"
             for x in [y for y in df.columns.values
                       if y not in columns and
                       not y.startswith(("coquery_invisible"))]}
        d[columns[0]] = "count"

        val = df.merge(df.groupby(columns)
                         .agg(d)
                         .rename(columns={columns[0]: self.get_id()})
                         .reset_index(), on=columns, how="left")[self.get_id()]
        val.index = df.index

        val.apply(lambda x: int(x) if x is not None else x)
        if "coquery_invisible_dummy" in df.columns:
            val[df["coquery_invisible_dummy"].isnull()] = 0

        for x in replace_dict:
            df[x] = df[x].replace(replace_dict[x], np.nan)

        return val


class FreqPMW(Freq):
    _name = "statistics_frequency_pmw"
    words = 1000000

    def evaluate(self, df, **kwargs):
        session = get_toplevel_window().Session
        val = super(FreqPMW, self).evaluate(df, **kwargs)
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

    def evaluate(self, df, **kwargs):
        val = super(FreqNorm, self).evaluate(df, **kwargs)

        if len(val) == 0:
            return pd.Series([], index=df.index)

        if self.group:
            fun = SubcorpusSize(columns=self.group.columns, group=self.group)

        else:
            fun = SubcorpusSize(columns=self.columns, group=self.group)
        subsize = fun.evaluate(df, **kwargs)

        d = pd.concat([val, subsize], axis=1)
        d.columns = ["val", "subsize"]
        val = d.apply(lambda row: row.val / row.subsize, axis="columns")
        val.index = df.index
        return val


class RowNumber(Freq):
    _name = "statistics_row_number"
    maximum_columns = 0

    def evaluate(self, df, **kwargs):
        val = pd.Series(range(1, len(df)+1), index=df.index)
        return val


class Rank(Freq):
    _name = "statistics_rank"

    arguments = {"choose": [("direction", "Direction:", "Ascending",
                             ("Ascending", "Descending"))]}

    def evaluate(self, df, **kwargs):
        rank_df = df[self.columns].drop_duplicates().reset_index(drop=True)
        rank_df[self._name] = rank_df.sort_values(
            by=rank_df.columns.tolist(),
            ascending=kwargs["direction"] == "Ascending").index.tolist()
        val = df.merge(rank_df, how="left")[self._name]
        val = val + 1
        val.index = df.index
        return val


#############################################################################
## Reference corpus functions
#############################################################################

class BaseReferenceCorpus(Function):
    _name = "virtual"

    @staticmethod
    def get_group():
        return "Reference corpus functions"


class ReferenceCorpusFrequency(BaseReferenceCorpus):
    _name = "reference_frequency"
    single_column = True

    def __init__(self, **kwargs):
        super(ReferenceCorpusFrequency, self).__init__(**kwargs)

    def evaluate(self, df, **kwargs):
        session = get_toplevel_window().Session

        self._res = self.get_reference()
        engine = options.cfg.current_connection.get_engine(self._res.db_name)
        word_feature = getattr(session.Resource, QUERY_ITEM_WORD)
        word_columns = [x for x in df.columns if word_feature in x]
        # concatenate the word columns, separated by space
        l = []
        sep = self.constant(df, " ")
        for col in word_columns:
            val = (df[col].replace("{", "\\{", regex=True)
                          .replace("\[", "\\[", regex=True)
                          .replace("\*", "\\*", regex=True)
                          .replace("\?", "\\?", regex=True))
            l += [val, sep]
        _s = pd.concat(l, axis=1).astype(str).sum(axis=1)

        # get the frequency from the reference corpus for the concatenated
        # columns:
        val = _s.apply(lambda x: self._res.corpus.get_frequency(x, engine))
        val.index = df.index
        engine.dispose()
        return val


class ReferenceCorpusFrequencyPMW(ReferenceCorpusFrequency):
    _name = "reference_frequency_pmw"
    words = 1000000

    def evaluate(self, df, **kwargs):
        val = super(ReferenceCorpusFrequencyPMW, self).evaluate(
            df, **kwargs)

        if len(val) > 0:
            corpus_size = self._res.corpus.get_corpus_size()
        val = val.apply(lambda x: x / (corpus_size / self.words))
        val.index = df.index
        return val


class ReferenceCorpusFrequencyPTW(ReferenceCorpusFrequencyPMW):
    words = 1000
    _name = "reference_frequency_ptw"


class ReferenceCorpusSize(BaseReferenceCorpus):
    _name = "reference_corpus_size"

    def evaluate(self, df, **kwargs):
        self._res = self.get_reference()
        ext_size = self._res.corpus.get_corpus_size()
        return self.constant(df, ext_size)


class ReferenceCorpusLLKeyness(ReferenceCorpusFrequency):
    _name = "reference_ll_keyness"

    def _func(self, x, size, ext_size, width):
        obs = np.array(
            [[x.freq1, x.freq2],
             [size - x.freq1 * width, ext_size - x.freq2 * width]])
        try:
            tmp = stats.chi2_contingency(obs,
                                         lambda_="log-likelihood")
        except ValueError as e:
            print(e)
            return np.nan

        return tmp[0]

    def evaluate(self, df, **kwargs):
        session = get_toplevel_window().Session

        self._res = self.get_reference()

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
        else:
            fun = CorpusSize(session=session)
        size = fun.evaluate(df, **kwargs)

        ext_freq = super(ReferenceCorpusLLKeyness, self).evaluate(
            df, **kwargs)
        if len(ext_freq) > 0:
            ext_size = self._res.corpus.get_corpus_size()

        _df = pd.DataFrame({"freq1": freq, "freq2": ext_freq, "size": size})
        if len(word_columns) > 1:
            s = "LL calculation for more than one column is experimental!"
            logging.warning(s)
        val = _df.apply(lambda x: self._func(x[["freq1", "freq2"]],
                                             size=x["size"],
                                             ext_size=ext_size,
                                             width=len(word_columns)),
                        axis="columns")
        return val


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

    #def evaluate(self, df, **kwargs):
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

    #def evaluate(self, df, **kwargs):
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

class BaseProportion(Function):
    _name = "virtual"

    @staticmethod
    def get_group():
        return "Distribution statistics"


class Tokens(BaseProportion):
    _name = "statistics_tokens"
    no_column_labels = True
    maximum_columns = 0

    def evaluate(self, df, **kwargs):
        val = self.constant(df, len(df.dropna(how="all")))
        return val


class Types(BaseProportion):
    _name = "statistics_types"
    no_column_labels = True

    def evaluate(self, df, **kwargs):
        val = self.constant(df, len(df[self.columns].drop_duplicates()))
        return val


class TypeTokenRatio(Types):
    _name = "statistics_ttr"
    no_column_labels = True

    def evaluate(self, df, **kwargs):
        types = super(TypeTokenRatio, self).evaluate(df, **kwargs)
        tokens = Tokens(group=self.group,
                        columns=self.columns).evaluate(df, **kwargs)
        val = pd.Series(data=types.values / tokens.values,
                        index=df.index)
        return val


class StandardizedTypeTokenRatio(Types):
    _name = "STTR"
    no_column_labels = True

    arguments = {"int": [("value", "Bandwidth:", 2500)]}

    def evaluate(self, df, **kwargs):
        parameter = kwargs.get("value", 2500)
        tty_list = []
        ix = df.sample(len(df)).index
        for i in range(len(df) // parameter):
            dsub = df.loc[ix].iloc[(i * parameter):(i + 1) * parameter]
            types = super(StandardizedTypeTokenRatio, self).evaluate(dsub,
                                                                     **kwargs)
            tokens = Tokens(group=self.group,
                            columns=self.columns).evaluate(dsub, **kwargs)
            n_types = types.values[0]
            n_tokens = tokens.values[0]
            tty_list.append(n_types / n_tokens)

        if tty_list:
            val = self.constant(df, sum(tty_list) / len(tty_list))
        else:
            val = None
        return val


class StandardizedTypeTokenRatio250(StandardizedTypeTokenRatio):
    _name = "STTR250"

    def evaluate(self, df, **kwargs):
        return super(StandardizedTypeTokenRatio250, self).evaluate(df, value=250)


class Proportion(BaseProportion):
    _name = "statistics_proportion"
    no_column_labels = True

    def evaluate(self, df, **kwargs):
        fun = Proportion(columns=self.columns, group=self.group)
        if self.find_function(df, fun):
            if options.cfg.verbose:
                print(self._name, "using df.Proportion()")
            return df[fun.get_id()]
        else:
            if options.cfg.verbose:
                print(self._name, "calculating df.Proportion()")
        fun_freq = Freq(columns=self.columns, group=self.group)
        if self.find_function(df, fun):
            val = df[fun_freq.get_id()]
        else:
            val = fun_freq.evaluate(df, **kwargs)

        val = val / len(val)
        val.index = df.index
        return val


class Percent(Proportion):
    _name = "statistics_percent"

    def evaluate(self, df, **kwargs):
        return 100 * super(Percent, self).evaluate(df, **kwargs)


class Entropy(Proportion):
    _name = "statistics_entropy"
    # This is a very informative discussion of the relation between entropy
    # in physics and information science:

    # http://www.askamathematician.com/2010/01/q-whats-the-relationship-between-entropy-in-the-information-theory-sense-and-the-thermodynamics-sense/

    # It also contains one of the most useful definitons of entropy that I've
    # come across so far: entropy is a measure of "how hard it is to describe
    # this thing".

    def evaluate(self, df, **kwargs):
        _df = df[self.columns]
        _df["COQ_PROP"] = super(Entropy, self).evaluate(df, **kwargs)
        _df = _df.drop_duplicates()
        props = _df["COQ_PROP"].values
        if len(_df) == 1:
            entropy = 0.0
        else:
            entropy = -sum(props * np.log2(props))
        val = self.constant(df, entropy)
        return val


class ConditionalProbability2(Proportion):
    """
    Calculate the conditional probability P(B|A) for the selected columns.

    This function expects two columns that represent A and B, respectively.
    Usually, A corresponds to words preceding the target string B.

    For every row _i_, P(B_i_|A_i_) = f(A_i_ + B_i_) / P(A_i_).

    """
    _name = "frequency_condprob"
    minimum_columns = 2
    maximum_columns = 2

    def get_resource(self, **kwargs):
        session = get_toplevel_window().Session
        return session.Resource

    def evaluate(self, df, **kwargs):
        resource = self.get_resource(**kwargs)
        if resource is None:
            return self.constant(df, None)

        span = df[self.columns[0]] + " " + df[self.columns[1]]
        left = df[self.columns[0]]
        engine = options.cfg.current_connection.get_engine(resource.db_name)
        try:
            freq_full = span.apply(
                lambda x: resource.corpus.get_frequency(x, engine))
            freq_part = left.apply(
                lambda x: resource.corpus.get_frequency(x, engine))
        except Exception as e:
            print(str(e))
            logging.error(str(e))
            val = self.constant(df, None)
        else:
            val = freq_full / freq_part
        finally:
            engine.dispose()
        return val


class ExternalConditionalProbability2(ConditionalProbability2):
    _name = "frequency_ext_condprob"

    def get_resource(self, **kwargs):
        res = self.get_reference()
        return res


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

    def evaluate(self, df, freq_cond, freq_total, **kwargs):
        return df[freq_cond] / df[freq_total]


class MutualInformation(ConditionalProbability2):
    """ Calculate the Mutual Information for the words in the first and the
    second column using this formula (cf. Bezina 2018):

    MI = log f(C1, C2) * N / (f(C1) * f(C2)),

    where f(C1, C2) is the frequency of the bigram, N is the size of the
    corpus, and f(C1) and f(C2) are the frequencies of the words,
    respectively.

    """

    _name = "Mutual Information"
    def evaluate(self, df, **kwargs):
        resource = self.get_resource(**kwargs)
        if resource is None:
            return self.constant(df, None)

        span = df[self.columns[0]] + " " + df[self.columns[1]]
        left = df[self.columns[0]]
        right = df[self.columns[1]]
        engine = options.cfg.current_connection.get_engine(resource.db_name)
        session = get_toplevel_window().Session
        try:
            freq_full = span.apply(
                lambda x: resource.corpus.get_frequency(x, engine))
            freq_left = left.apply(
                lambda x: resource.corpus.get_frequency(x, engine))
            freq_right = right.apply(
                lambda x: resource.corpus.get_frequency(x, engine))
            size = session.Corpus.get_corpus_size()
        except Exception as e:
            print(str(e))
            logging.error(str(e))
            val = self.constant(df, None)
        else:
            val = np.log2(freq_full * size / (freq_left * freq_right))
        finally:
            engine.dispose()
        return val


#############################################################################
## Corpus functions
#############################################################################

class BaseCorpusFunction(Function):
    _name = "virtual"

    @staticmethod
    def get_group():
        return "Corpus statistics"


class CorpusSize(BaseCorpusFunction):
    _name = "statistics_corpus_size"
    no_column_labels = True

    @staticmethod
    def get_group():
        return "Corpus size functions"

    def evaluate(self, df, **kwargs):
        session = get_toplevel_window().Session
        corpus_size = session.Corpus.get_corpus_size()
        val = self.constant(df, corpus_size)
        return val


class SubcorpusSize(CorpusSize):
    _name = "statistics_subcorpus_size"
    no_column_labels = True

    def evaluate(self, df, **kwargs):
        try:
            session = get_toplevel_window().Session
            manager = session.get_manager(options.cfg.MODE)
            fun = SubcorpusSize(session=session,
                                columns=self.columns, group=self.group)
            if options.cfg.verbose:
                print(self._name,
                      f"using {self}" if self.find_function(df, fun)
                      else f"calculating(self)")
            if self.find_function(df, fun):
                return df[fun.get_id()]
            corpus_features = [x for x, _
                               in session.Resource.get_corpus_features()]
            column_list = [x for x in corpus_features
                           if "coq_{}_1".format(x) in self.columns]
            if df.iloc[0].coquery_invisible_dummy is not np.nan:
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
        min_r, _ = session.Corpus.get_subcorpus_range(row)
        return min_r

    def evaluate(self, df, *args, **kwargs):
        session = get_toplevel_window().Session

        corpus_features = [x for x, _ in
                           session.Resource.get_corpus_features()]
        column_list = [col for col in self.columns if col in
                       ["coq_{}_1".format(y) for y in corpus_features]]
        val = df.apply(lambda x: self._func(x[column_list], session), axis=1)
        return val


class SubcorpusRangeMax(SubcorpusRangeMin):
    _name = "statistics_subcorpus_range_max"

    def _func(self, row, session):
        _, max_r = session.Corpus.get_subcorpus_range(row)
        return max_r


#############################################################################
## Context functions
#############################################################################

class SentenceId(Function):
    _name = "coq_sentence_id"

    def evaluate(self, df, **kwargs):
        session = get_toplevel_window().Session
        _df = pd.merge(df,
                       session.Resource.get_sentence_ids(
                           df["coquery_invisible_corpus_id"]),
                       how="left", on="coquery_invisible_corpus_id")
        return _df["coquery_invisible_sentence_id"]


class ContextColumns(Function):
    _name = "coq_context_column"
    single_column = False

    def __init__(self, left=None, right=None, *args):
        super(ContextColumns, self).__init__(*args)
        if left is None:
            self.left = options.cfg.context_left
        else:
            self.left = left
        if right is None:
            self.right = options.cfg.context_right
        else:
            self.right = right

        self.left_cols = ["coq_context_lc{}".format(self.left - i)
                          for i in range(self.left)]
        self.right_cols = ["coq_context_rc{}".format(i + 1)
                           for i in range(self.right)]
        self._sentence_column = None

    @staticmethod
    def get_group():
        return "Context functions"

    def get_id(self):
        if self.alias:
            return self.alias
        return self._name

    def evaluate(self, df, **kwargs):
        session = get_toplevel_window().Session
        resource = session.Resource
        with session.db_engine.connect() as db_connection:
            # check if df misses information needed to produce the context
            # columns:
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
                    col = (getattr(resource, "corpus_sentence_id", None) or
                           getattr(resource, "corpus_sentence", None) or
                           getattr(resource, "corpus_utterance_id", None) or
                           getattr(resource, "corpus_utterance"))
                    if col:
                        self._sentence_column = "coq_{}_1".format(col)
                        if self._sentence_column not in df.columns:
                            sentence_col = "coquery_invisible_sentence_id"
                            fun = SentenceId(session=session)
                            val = fun.evaluate(df, session=session)
                            df[sentence_col] = val
                            self._sentence_column = sentence_col

                get_toplevel_window().useContextConnection.emit(db_connection)
                val = df.apply(lambda x: self._func(row=x,
                                                    session=session,
                                                    connection=db_connection),
                               axis="columns")
                get_toplevel_window().closeContextConnection.emit(
                    db_connection)
                val.index = df.index
                return val

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
                                left=self.left, right=self.right,
                                sentence_id=sentence_id)

        val = pd.Series(data=left + right,
                        index=self.left_cols + self.right_cols)
        return val


class ContextKWIC(ContextColumns):
    _name = "coq_context_kwic"

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
                                left=self.left, right=self.right,
                                sentence_id=sentence_id)

        language = session.Resource.get_language()
        val = pd.Series(data=[collapse_words(left, language),
                              collapse_words(right, language)],
                        index=["coq_context_left", "coq_context_right"])
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
                                row["coquery_invisible_number_of_tokens"],
                                connection,
                                left=self.left, right=self.right,
                                sentence_id=sentence_id)

        words = left + [x.upper() for x in target if x] + right
        language = session.Resource.get_language()
        return pd.Series(data=[collapse_words(words, language)],
                         index=[self._name])


##############################################################################
### Query functions
##############################################################################

#class QueryFunction(Function):
    #_name = "virtual"

    #@staticmethod
    #def get_group():
        #return "Query functions"


#class QueryString(QueryFunction):
    #_name = "coquery_query_string"

    #def _func(self, row, session):
        #return session.queries[row["coquery_invisible_query_number"]].S

    #def evaluate(self, df, *args, **kwargs):
        #session = kwargs["session"]
        #val = df.apply(lambda row: session.queries[
            #row["coquery_invisible_query_number"]].query_string,
            #axis="columns")
        #print(val)
        #val.index = df.index
        #return val

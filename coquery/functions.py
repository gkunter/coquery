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


from . import options
from . import sqlhelper
from .defines import *
from .general import CoqObject, collapse_words, get_visible_columns


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
    no_column_labels = False # True if the columns appear in the function name
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
        self.column_list = columns
        self._hidden = hidden
        self.sweep = sweep
        self.alias = alias
        self.group = group
        self.value = value
        self._label = label
        if aggr is not None:
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
                template = "{func} by {cols}"
                return template.format(
                    func=self.get_name(),
                    cols="/".join(["{}".format(session.translate_header(x)) for x in self.group]))

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
            return "func_{}_{}".format(self._name, self.get_hash())

    def find_function(self, df, fun):
        fun_id = fun.get_id()
        for col in df.columns.values:
            if col == fun_id:
                return col
        return None

    def columns(self, df, **kwargs):
        if df is None or not self.sweep:
            return self.column_list
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
        except Exception:
            self.re = None

    @classmethod
    def validate_input(cls, value):
        try:
            re.compile(value)
        except Exception:
            return False
        else:
            return True


class StringLength(StringFunction):
    _name = "LENGTH"
    combine_modes = num_combine

    def _func(self, cols):
        return cols.apply(lambda x: len(x) if isinstance(x, str) else len(str(x)) if x is not None else None)


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
        if self.re is None:
            return pd.Series([pd.np.nan] * len(col), index=col.index)
        else:
            return col.apply(lambda x: len(self.re.findall(x)) if x is not None else None)
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
            if s is None:
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
                return self.constant(df, 0)
        except KeyError:
            # this happens if the data frame does not have the column
            # 'coquery_dummy'
            pass

        # ignore external columns:
        columns = [x for x in self.columns(df, **kwargs) if not x.startswith("db_")]

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
        if "coquery_dummy" in df.columns:
            val[df["coquery_dummy"].isnull()] = 0

        for x in replace_dict:
            df[x] = df[x].replace(replace_dict[x], pd.np.nan)

        return val


class FreqPMW(Freq):
    _name = "statistics_frequency_pmw"
    words = 1000000

    def __init__(self, columns=[], *args, **kwargs):
        super(FreqPMW, self).__init__(columns, *args, **kwargs)

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
## Reference corpus functions
#############################################################################

import hashlib

class BaseReferenceCorpus(Function):
    _name = "virtual"


class ReferenceCorpusFrequency(BaseReferenceCorpus):
    _name = "statistics_reference_corpus_frequency"
    single_column = True

    def __init__(self, *args, **kwargs):
        super(ReferenceCorpusFrequency, self).__init__(*args, **kwargs)

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        ref_corpus = options.cfg.reference_corpus.get(
                         options.cfg.current_server, None)
        if not ref_corpus or ref_corpus not in options.cfg.current_resources:
            return self.constant(df, None)

        res = options.cfg.current_resources[ref_corpus]
        ResourceClass, CorpusClass, LexiconClass, _ = res
        self._current_lexicon = LexiconClass()
        self._current_corpus = CorpusClass()
        self._current_resource = ResourceClass(self._current_lexicon,
                                              self._current_corpus)
        self._current_corpus.resource = self._current_resource
        self._current_corpus.lexicon = self._current_lexicon
        self._current_lexicon.resource = self._current_resource

        engine = sqlalchemy.create_engine(
            sqlhelper.sql_url(options.cfg.current_server,
                              self._current_resource.db_name))

        word_feature = getattr(session.Resource, QUERY_ITEM_WORD)
        word_columns = [x for x in df.columns if word_feature in x]
        # concatenate the word columns, separated by space
        self._s = (df[word_columns].astype(str)
                                  .apply(lambda x: x + " ").sum(axis=1))

        # get the frequency from the reference corpus for the concatenated
        # columns:
        val = self._s.apply(lambda x: self._current_corpus.get_frequency(x, engine))
        val.index = df.index
        engine.dispose()
        return val


class ReferenceCorpusFrequencyPMW(ReferenceCorpusFrequency):
    _name = "reference_per_million_words"
    words = 1000000

    def evaluate(self, df, *args, **kwargs):
        val = super(ReferenceCorpusFrequencyPMW, self).evaluate(df, *args, **kwargs)
        ref_corpus = options.cfg.reference_corpus.get(
                            options.cfg.current_server, None)
        if not ref_corpus or ref_corpus not in options.cfg.current_resource:
            return self.constant(df, None)

        if len(val) > 0:
            corpus_size = self._current_corpus.get_corpus_size()
        val = val.apply(lambda x: x / (corpus_size / self.words))
        val.index = df.index
        return val


class ReferenceCorpusFrequencyPTW(ReferenceCorpusFrequencyPMW):
    words = 1000
    _name = "reference_per_thousand_words"


class ReferenceCorpusLLKeyness(ReferenceCorpusFrequency):
    _name = "reference_ll_keyness"

    def _func(self, x, size, ext_size, width):
        obs = pd.np.array(
            [[x.freq1, x.freq2],
             [size - x.freq1 * width, ext_size - x.freq2 * width]])
        try:
            tmp = stats.chi2_contingency(obs,
                                         lambda_="log-likelihood")
        except ValueError:
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
        size = session.Resource.corpus.get_corpus_size()

        ext_freq = super(ReferenceCorpusLLKeyness, self).evaluate(df, *args, **kwargs)
        if len(ext_freq) > 0:
            ext_size = self._current_corpus.get_corpus_size()

        _df = pd.DataFrame({"freq1": freq, "freq2": ext_freq})

        val = _df.apply(lambda x: self._func(x, size=size, ext_size=ext_size,
                                             width=len(word_columns)),
                        axis="columns")
        return val


class ReferenceCorpusDiffKeyness(ReferenceCorpusLLKeyness):
    _name = "reference_diff_keyness"

    def _func(self, x, size, ext_size, width):
        return (x.freq1/size - x.freq2/ext_size) * 100 / (x.freq2/ext_size)


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
        if pre is None:
            pre = len(df)
        val = self.constant(df, pre)
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
        if post is None:
            post = len(df)
        val = self.constant(df, post)
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
        val = self.constant(df, entropy)
        return val

class Tokens(Function):
    _name = "statistics_tokens"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        val = self.constant(df, len(df.dropna(how="all")))
        return val


class Types(Function):
    _name = "statistics_types"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        cols = self.columns(df, **kwargs)
        val = self.constant(df, len(df[cols].drop_duplicates()))
        return val


class TypeTokenRatio(Types):
    _name = "statistics_ttr"
    no_column_labels = True

    def evaluate(self, df, *args, **kwargs):
        types = super(TypeTokenRatio, self).evaluate(df, *args, **kwargs)
        tokens = Tokens(group=self.group, columns=self.column_list, hidden=self._hidden).evaluate(df, *args, **kwargs)
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
    combine_modes = no_combine
    no_column_labels = True

    @staticmethod
    def get_description():
        return "Corpus size functions"

    def __init__(self, columns=[], *args, **kwargs):
        super(CorpusSize, self).__init__(columns, *args, **kwargs)

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]
        corpus_size = session.Corpus.get_corpus_size()
        val = self.constant(df, corpus_size)
        return val


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
                       axis=1)

        return val


class SubcorpusRangeMin(CorpusSize):
    _name = "statistics_subcorpus_range_min"

    def _func(self, row, session):
        min_r, max_r = session.Corpus.get_subcorpus_range(row)
        return min_r

    def evaluate(self, df, *args, **kwargs):
        session = kwargs["session"]

        corpus_features = [x for x, _ in session.Resource.get_corpus_features()]
        column_list = [x for x in self.columns(df, **kwargs) if x in
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
                val = df.apply(lambda x: self._func(row=x,
                                                    session=session,
                                                    connection=db_connection),
                            axis="columns")
                val.index = df.index
                return val


class ContextKWIC(ContextColumns):
    _name = "coq_context_kwic"

    def _func(self, row, session, connection):
        row = super(ContextKWIC, self)._func(row, session, connection)
        return pd.Series(
            data=[collapse_words(row[self.left_cols]), collapse_words(row[self.right_cols])],
            index=[["coq_context_left", "coq_context_right"]])


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


#############################################################################
## Logic functions
#############################################################################

class LogicFunction(Function):
    _name = "virtual"
    combine_modes = bool_combine

    @staticmethod
    def get_description():
        return "Logical functions"

    def _func_value(self, cols):
        if cols.dtype == object:
            # make string column comparison:
            return cols.apply(lambda x: self._comp(x, str(self.value)))
        else:
            # make float comparison:
            return cols.apply(lambda x: self._comp(x, float(self.value)))

    def _func_columns(self, cols):
        if len(cols) == 1:
            return self.constant(cols, np.nan)
        else:
            val = cols[0]
            for x in cols[1:]:
                val = self._comp(val, x)
            return self.constant(cols, val)

    def evaluate(self, df, *args, **kwargs):
        try:
            if self.value:
                val = df[self.columns(df, **kwargs)].apply(self._func_value)
            else:
                val = df[self.columns(df, **kwargs)].apply(self._func_columns, axis="columns")
            if len(val.columns) > 1:
                val = val.apply(self.select, axis="columns")
        except (KeyError, ValueError):
            val = self.constant(df, np.nan)

        return val


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

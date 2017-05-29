# -*- coding: utf-8 -*-
"""
link.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals

import logging
import pandas as pd

from . import NAME
from .general import CoqObject

# Since Filter.__repr__() uses globals() to look up the strings corresponding
# to the operator type, a complete import of the constants from defines.py is
# necessary:
from .defines import *

try:
    import numexpr
    _query_engine = "numexpr"
except ImportError:
    _query_engine = "python"

try:
    string_types = (unicode, str)
except NameError:
    string_types = (str, )


class Filter(CoqObject):
    def __init__(self, feature, dtype, operator, value, stage=FILTER_STAGE_FINAL):
        super(Filter, self).__init__()
        if operator not in OPERATOR_STRINGS:
            raise ValueError("Invalid filter operator '{}'".format(operator))
        if not feature:
            raise ValueError("No filter column specified")

        self.feature = feature
        self.operator = operator
        self.value = value
        self.dtype = dtype
        self.stage = stage

    def __repr__(self):
        # This is a bit of a hack. In order to get the __repr__, we look up
        # the name of the constant from defines (which is imported into the
        # global namespace) that matches the value of the instance attribute
        # self.operator:
        op = [key for key, val in globals().items()
              if val == self.operator][0]
        value = ("'{}'".format(self.value)
                 if isinstance(self.value, string_types)
                 else self.value)
        stage = ("FILTER_STAGE_FINAL"
                 if self.stage == FILTER_STAGE_FINAL
                 else "FILTER_STAGE_BEFORE_TRANSFORM")
        S = "Filter(feature='{}', operator={}, value={}, dtype={}, stage={})"
        return S.format(self.feature, op, value, self.dtype, stage)

    def fix(self, x):
        """
        Fixes the value x so it can be used in a Pandas query() call.

        A fixed string is enclosed in simple quotation marks. Quotation
        marks inside the string are escaped.
        """
        if pd.np.issubdtype(self.dtype, pd.np.number):
            if x == "":
                val = None
            else:
                # attempt to coerce the value to a numeric variable
                if not isinstance(x, (int, float)):
                    val = pd.np.float(x)
                    try:
                        if x == pd.np.int(x):
                            val = pd.np.int(x)
                    except ValueError:
                        pass
                else:
                    val = x

        elif self.dtype == bool:
            if isinstance(x, (float, int)):
                val = bool(x)

            # all operators except the MATCH operators require boolean
            # values
            elif self.operator not in [OP_MATCH, OP_NMATCH]:
                if x.lower() in ["yes", "y", "1", "true", "t"]:
                    val = True
                elif x.lower() in ["no", "n", "0", "false", "f"]:
                    val = False
                else:
                    S = "Filter value has to be either 'yes' or 'no'"
                    raise ValueError(S)
            else:
                val = "'{}'".format(self.value)
        else:
            if "'" in x:
                val = x.replace("'", "\\'")
            else:
                val = x
            val = "'{}'".format(val)

        return str(val)

    def get_filter_string(self):
        # if the value is an NA (either None or np.nan), a trick described
        # here is used: http://stackoverflow.com/a/26535881/5215507
        #
        # This trick involves testing equality between values and themselves,
        # i.e. ``df.query("value1 == value1")``. Cells with NAs in the column
        # ``value1`` will return ``False`` because ``pd.np.nan == pd.np.nan``
        # is always ``False``.
        #
        # Thus, testing whether FEATURE equals NA returns the query string
        # FEATURE != FEATURE.

        op = self.operator

        if op == OP_MATCH:
            raise ValueError("RegEx filters do not use query strings.")
        if op == OP_RANGE:
            if len(self.value) == 0:
                raise ValueError("Filter uses an empty range.")
            if not isinstance(min(self.value), type(max(self.value))):
                raise TypeError("Range values have different types.")
        if self.value is None or self.value is pd.np.nan:
            if op not in [OP_NE, OP_EQ]:
                raise ValueError("Only OP_EQ and OP_NE are allowed with NA values")

        if (self.value is None or self.value is pd.np.nan or
            (pd.np.issubdtype(self.dtype, pd.np.number)
             and self.value == "") or
            (self.dtype == bool and self.value == "")):
            val = self.feature
            if op == OP_EQ:
                op = OP_NE
            else:
                op = OP_EQ

        elif isinstance(self.value, list):
            if op == OP_RANGE:
                return "{} <= {} < {}".format(
                                            self.fix(min(self.value)),
                                            self.feature,
                                            self.fix(max(self.value)))
            else:
                val = "[{}]".format(", ".join([self.fix(x) for x
                                               in self.value]))
        else:
            val = self.fix(self.value)

        S = "{} {} {}".format(
            self.feature, OPERATOR_STRINGS[op], val)
        return S

    def apply(self, df):
        # ignore filters that refer to non-existing columns:
        if self.feature not in df.columns:
            return df

        if self.operator in (OP_MATCH, OP_NMATCH):
            if self.dtype == object:
                col = df[self.feature].dropna()
            else:
                # coerce non-string columns to string:
                col = df[self.feature].dropna().astype(str)
            if self.operator == OP_MATCH:
                matching = col.str.contains(self.value)
            else:  # OP_NMATCH
                matching = ~col.str.contains(self.value)
            return df.iloc[col[matching].index]
        else:
            try:
                return df.query(self.get_filter_string(),
                                engine=_query_engine)
            except SyntaxError as e:
                S = "Could not apply filter {}: {}".format(self, str(e))
                print(S)
                logger.warn(S)
                return df
            except TypeError as e:
                S = "Could not apply filter {}: are there missing values in your data?"
                raise RuntimeError(S)

logger = logging.getLogger(NAME)

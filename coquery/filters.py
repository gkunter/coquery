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
    def __init__(self, feature, operator, value, stage=FILTER_STAGE_FINAL):
        if operator not in OPERATOR_STRINGS:
            raise ValueError("Invalid filter operator '{}'".format(operator))
        if not feature:
            raise ValueError("No filter column specified")
        if not value:
            raise ValueError("No filter value specified")

        self.feature = feature
        self.operator = operator
        self.value = value
        self.dtype = None
        self.stage = stage

    def __repr__(self):
        return "Filter(feature='{}', operator={}, value={}, dtype={}, stage={})".format(
            self.feature,
            [x for x in globals() if eval(x) == self.operator][0],
            "'{}'".format(self.value) if isinstance(self.value, string_types) else self.value,
            self.dtype,
            ("FILTER_STAGE_FINAL" if self.stage == FILTER_STAGE_FINAL else
             "FILTER_STAGE_BEFORE_TRANSFORM"))

    def fix(self, x):
        """
        Fixes the value x so it can be used in a Pandas query() call.

        A fixed string is enclosed in simple quotation marks. Quotation
        marks inside the string are escaped.
        """
        if self.dtype == object:
            if "'" in x:
                val = x.replace("'", "\\'")
            else:
                val = x
            val = "'{}'".format(val)
        elif self.dtype == bool:
            if x.lower() in ["yes", "y", "1", "true", "t"]:
                val = True
            elif x.lower() in ["no", "n", "0", "false", "f"]:
                val = False
            else:
                raise ValueError("Filter value has to be either 'yes' or 'no'")
        else:
            val = str(x)
        return val

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

        if self.operator == OP_MATCH:
            raise ValueError("RegEx filters do not use query strings.")
        if self.operator == OP_RANGE:
            if len(self.value) == 0:
                raise ValueError("Filter uses an empty range.")
            if not isinstance(min(self.value), type(max(self.value))):
                raise TypeError("Range values have different types.")
        if self.value is None or self.value is pd.np.nan:
            if self.operator not in [OP_NE, OP_EQ]:
                raise ValueError("Only OP_EQ and OP_NE are allowed with NA values")

        if self.value is None or self.value is pd.np.nan:
            val = self.feature
            if self.operator == OP_EQ:
                self.operator = OP_NE
            else:
                self.operator = OP_EQ

        elif isinstance(self.value, list):
            if self.operator == OP_RANGE:
                return "{} <= {} < {}".format(
                                            self.fix(min(self.value)),
                                            self.feature,
                                            self.fix(max(self.value)))
            else:
                val = "[{}]".format(", ".join([self.fix(x) for x
                                               in self.value]))
        else:
            val = self.fix(self.value)

        return "{} {} {}".format(self.feature,
                                 OPERATOR_STRINGS[self.operator],
                                 val)

    def apply(self, df):
        # ignore filters that refer to non-existing columns:
        if self.feature not in df.columns:
            return df

        self.dtype = pd.Series(list(df[self.feature].dropna())).dtype
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
            except Exception as e:
                S = "Could not apply filter {}: {}".format(self, str(e))
                print(S)
                logger.warn(S)
                return df

logger = logging.getLogger(NAME)

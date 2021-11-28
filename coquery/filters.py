# -*- coding: utf-8 -*-
"""
link.py is part of Coquery.

Copyright (c) 2016-2020 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals

import logging
import re
import numpy as np

from coquery.general import CoqObject
from coquery.defines import (OP_MATCH, OP_NMATCH, OP_RANGE, OP_NE, OP_EQ,
                             OPERATOR_STRINGS, FILTER_STAGE_FINAL)


try:
    string_types = (unicode, str)
except NameError:
    string_types = (str, )


def parse_filter_text(s):
    """
    Parse the string, and return a Filter instance that matches the string.

    This function is used by the option file parser to restore saved filters.

    The string is assumed to be produced by Filter.__repr__. No attempt is
    made to parse other strings (e.g. those with different argument orders).

    If the string cannot be parsed for whatever reason, the function rises a
    ValueError.
    """
    try:
        regex = re.match(r"^Filter\((.*)\)$", s)
        arguments = [x.split("=") for x in regex.group(1).split(", ")]
        kwargs = {}
        for kwd, value in arguments:
            val = value.strip("'")

            # coerce the value to a numeric type:
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    pass
            kwargs[kwd] = val
    except Exception as e:
        raise ValueError("Exception with filter '{}': {}".format(s, e))

    return Filter(**kwargs)


class Filter(CoqObject):
    def __init__(self, feature, dtype, operator, value,
                 stage=FILTER_STAGE_FINAL):
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
        if isinstance(self.value, string_types):
            val = "'{}'".format(self.value)
        else:
            val = self.value

        S = "Filter(feature='{}', operator='{}', value={}, dtype={}, stage={})"
        return S.format(self.feature, self.operator, val,
                        self.dtype, self.stage)

    def fix(self, x):
        """
        Fixes the value x so it can be used in a Pandas query() call.

        A fixed string is enclosed in simple quotation marks. Quotation
        marks inside the string are escaped.
        """
        if np.issubdtype(self.dtype, np.number):
            if x == "":
                val = None
            else:
                # attempt to coerce the value to a numeric variable
                if not isinstance(x, (int, float)):
                    val = np.float(x)
                    try:
                        if x == np.int(x):
                            val = np.int(x)
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
        # ``value1`` will return ``False`` because ``np.nan == np.nan``
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
        if self.value is None or self.value is np.nan:
            if op not in [OP_NE, OP_EQ]:
                msg = "Only OP_EQ and OP_NE are allowed with NA values"
                raise ValueError(msg)

        if (self.value is None or
                self.value is np.nan or
                (np.issubdtype(self.dtype, np.number) and self.value == "") or
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

        s = "{} {} {}".format(self.feature, OPERATOR_STRINGS[op], val)
        return s

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
                return df.query(self.get_filter_string())
            except SyntaxError as e:
                s = "Could not apply filter {}: {}".format(self, str(e))
                logging.warning(s)
                return df
            except TypeError:
                s = "Could not apply filter {}: undetectable format"
                raise RuntimeError(s)

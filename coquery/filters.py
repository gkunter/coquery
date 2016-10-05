# -*- coding: utf-8 -*-
"""
link.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals

import logging
import pandas as pd

from .defines import *
from . import options
from .general import CoqObject

try:
    import numexpr
    _query_engine = "numexpr"
except ImportError:
    _query_engine ="python"

try:
    string_types = (unicode, str)
except NameError:
    string_types = (str, )

class Filter(CoqObject):
    def __init__(self, feature, operator, value):
        self.feature = feature
        self.operator = operator
        self.value = value
        
    def __repr__(self):
        return "Filter(feature='{}', operator={}, value={})".format(
            self.feature, 
            [x for x in globals() if eval(x) == self.operator][0], 
            "'{}'".format(self.value) if isinstance(self.value, string_types) else self.value)
        
    @staticmethod
    def fix(x):
        """
        Fixes the value x so it can be used in a Pandas query() call.
        
        A fixed string is enclosed in simple quotation marks. Quotation 
        marks inside the string are escaped.
        """
        if isinstance(x, string_types):                
            if "'" in x:
                val = x.replace("'", "\\'")
            else:
                val = x
            val = "'{}'".format(val)
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
            if type(min(self.value)) != type(max(self.value)):
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
                val = "[{}]".format(", ".join([self.fix(x) for x in self.value]))
        else:
            val = self.fix(self.value)

        return "{} {} {}".format(self.feature, OPERATOR_STRINGS[self.operator], val)
        
    def apply(self, df):
        if self.operator == OP_MATCH:
            if df[self.feature].dropna().dtype == object:
                return df.iloc[df[self.feature].dropna().str.contains(self.value).index]
            else:
                # coerce non-string columns to string:
                S = df[self.feature].dropna().astype(str)
                return df.iloc[S[S.str.contains(self.value)].index]
        else:
            return df.query(self.get_filter_string(), engine=_query_engine)

class QueryFilter(CoqObject):
    """ Define a class that stores a query filter. 
    
    Query filters are text strings that follow a very simple syntax. Valid
    filter strings are:
    
    variable operator value
    variable operator value value ...
    variable operator value, value, ...
    variable operator value-value
    
    'variable' contains the display name of a table column. If the display
    name is ambiguous, i.e. if two or more tables contain a name with the
    same column, the name is disambiguated by preceding it with the table
    name, linked by a '.'.

    """
    
    operators = (">", "<", "<>", "IN", "IS", "=", "LIKE")

    def __init__(self, text = ""):
        """ Initialize the filter. """
        self._text = text
        self._table = ""
        self._resource = None
        self._parsed = False
        
    def __str__(self):
        # FIXME: this should rather be something like a canonical 
        # representation of the filter, not the filter as it was entered by 
        # the user. For instance, operators should be capitalized 
        # automatically.
        return self._text
        
    @property
    def resource(self):
        return self._resource
    
    @resource.setter
    def resource(self, resource_class):
        self._resource = resource_class
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, s):
        if self.validate(s):
            self._text = s
            self._variable, self._op, self._value_list, self._value_range = self.parse_filter(s)
        else:
            raise RuntimeError(msg_invalid_filter.format(s))

    def __repr__(self):
        return "QueryFilter('{}', {})".format(self.text, self.resource)
    
    def __str__(self):
        l = [name for  _, name in self.resource.get_corpus_features() if name.lower == self._variable.lower()]        
        if l:
            variable_name = l[0]
        else:
            variable_name = self._variable
        
        if self._value_list:
            return "{} {} {}".format(variable_name.capitalize(), self._op.lower(), ", ".join(sorted(self._value_list)))
        elif self._value_range:
            return "{} {} {}-{}".format(variable_name.capitalize(), self.op.lower(), min(self._value_range), max(self._value_range))
        else:
            return self._text.strip()
            
    def parse_filter(self, text):
        """ Parse the text and return a tuple with the query filter 
        components.  The tuple contains the components (in order) variable, 
        operator, value_list, value_range.
        
        The component value_list is a list of all specified values. The 
        componment value_range is a tuple with the lower and the upper limit
        of the range specified in the text. Only one of the two components 
        value_list and value_range contains valid values, the other is None.
        
        If the text is not a valid filter text, the tuple None, None, None, 
        None is returned."""
        
        error_value = None, None, None, None
        
        if "<>" in text:
            text.replace("<>", " <> ")
        elif "=" in text:
            text = text.replace("=", " = ")
        elif "<" in text:
            text = text.replace("<", " < ")
        elif ">" in text:
            text = text.replace(">", " > ")
        
        fields = str(text).split()
        try:
            self.var = fields[0]
        except:
            return error_value
        try:
            self.operator = fields[1]
        except:
            return error_value            
        try:
            values = fields[2:]
        except:
            return error_value
        
        if not values:
            return error_value
        
        if self.operator.upper() in ("IS", "="):
            self.value_range = None
            self.value_list = [str(text).partition(self.operator)[-1].strip()]
        else:
            # check for range:
            collapsed_values = "".join(fields[2:])
            if collapsed_values.count("-") == 1:
                self.value_list = None
                self.value_range = tuple(collapsed_values.split("-"))
            else:
                self.value_range = None
                self.value_list = sorted([x.strip("(),").strip() for x in values])

        if (self.value_range or len(self.value_list) > 1) and self.operator.lower() in ("is", "="):
            self.operator = "in"

        if self.operator == "LIKE":
            if self.value_range or len(self.value_list) > 1:
                return error_value

        self._parsed = True
        return self.var, self.operator, self.value_list, self.value_range
            
    def validate(self, s):
        """ 
        Check if the text contains a valid filter. 
        
        A filter is valid if it has the form 'x OP y', where x is a resource 
        variable name, OP is a comparison operator, and value is either a 
        string, a number or a list. 
        
        Parameters
        ----------
        s : string
            The text of the filter
            
        Returns
        -------
        b : boolean
            True if the argumnet is a valid filter text, or False otherwise.
        """
        return True
        
        var, op, value_range, value_list = self.parse_filter(s)
        if not var:
            return False
        variable_names = [name.lower() for  _, name in self.resource.get_corpus_features() + [("statistics_frequency", COLUMN_NAMES["statistics_frequency"])] if isinstance(name, str)]
        if var.lower() not in variable_names:
            return False
        if variable_names.count(var.lower()) > 1:
            logger.warning("Query filter may be ambiguous: {}".format(s))
            return True
        if op.lower() not in [x.lower() for x in self.operators]:
            return False
        return True
    
    def check_number(self, n):
        """
        Check whether the integer value n is filtered by this filter.
        
        Parameters
        ----------
        n : int
            The value to be checked against the filter
            
        Returns
        -------
        b : boolean
            True if the value is filtered by this filter, or False otherwise.
        """
        if not self._parsed:
            self.parse_filter(self._text)
            
        try:
            n = float(n)
            if self.operator in ("=", "IS", "LIKE"):
                return n == float(self.value_list[0])
            elif self.operator == ">":
                return n > float(self.value_list[0])
            elif self.operator == "<":
                return n < float(self.value_list[0])
            elif self.operator == "<>":
                return n != float(self.value_list[0])
            elif self.operator == "IN":
                return n >= float(self.value_range[0]) and n <= float(self.value_range[1])
        except ValueError:
            return False

logger = logging.getLogger(NAME)

# -*- coding: utf-8 -*-
"""
functionlist.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import pandas as pd

from . import options
from .general import CoqObject


class FunctionList(CoqObject):
    def __init__(self, l=[], *args, **kwargs):
        self._list = l

    def lapply(self, df, session, manager=None):
        """
        Apply all functions in the list to the data frame.
        """

        # apply value substitution to df:
        subst = options.get_column_properties().get("substitutions", {})

        # in order to allow zero frequencies for empty result tables, empty
        # data frames can be retained if a function demands it. This is
        # handled by keeping track of the drop_on_na attribute. As soon as
        # one function in the list wishes to retain a data frame that contains
        # NAs, the data frame will not be dropped.
        # This code only keeps track of the attributes. The actual dropping
        # takes place (or doesn't) in the summarize() method of the manager.
        if manager:
            if manager.drop_on_na is not None:
                drop_on_na = True
            else:
                drop_on_na = manager.drop_on_na
        else:
            drop_on_na = True

        for fun in list(self._list):
            if options.cfg.drop_on_na:
                drop_on_na = True
            else:
                drop_on_na = drop_on_na and fun.drop_on_na

            try:
                if subst:
                    val = fun.evaluate(df.replace(subst), session=session, manager=manager)
                else:
                    val = fun.evaluate(df, session=session, manager=manager)
            except KeyError as e:
                print(e)
                self._list.remove(fun)
                # can be caused by a function applied to a non-existing column
            else:
                # Functions can return either single columns or data frames.
                # Handle the function result accordingly:
                if fun.single_column:
                    df[fun.get_id()] = val
                else:
                    df = pd.concat([df, val], axis="columns")

        # tell the manager whether rows with NA will be dropped:
        if manager:
            manager.drop_on_na = drop_on_na
        return df

    def get_list(self):
        return self._list

    def set_list(self, l):
        self._list = l

    def find_function(self, fun_id):
        for x in self._list:
            print("\t", x.get_id())
            if x.get_id() == fun_id:
                return x
        return None

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

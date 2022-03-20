# -*- coding: utf-8 -*-
"""
aggregator.py is part of Coquery.

Copyright (c) 2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import collections

from PyQt5 import QtCore

import pandas as pd
from scipy import stats as st


class Aggregator(QtCore.QObject):
    def __init__(self, id_column=None):
        super(Aggregator, self).__init__()
        self._names_dict = None
        self._aggs_dict = None
        self._id_column = id_column or "coquery_invisible_corpus_id"

    def reset(self):
        self._aggs_dict = collections.defaultdict(list)
        self._names_dict = collections.defaultdict(list)

    def add(self, column, fnc, name=None):
        if fnc == "mode":
            fnc = self._get_most_frequent
        elif fnc == "ci":
            fnc = self._get_interval
        self._aggs_dict[column].append(fnc)
        self._names_dict[column].append(name or column)

    def process(self, df, grouping):

        # if there is an id column in the data frame, make sure that the
        # aggregation samples the first ID
        if self._id_column not in df.columns:
            if self._id_column in self._aggs_dict:
                self._aggs_dict.pop(self._id_column)
            if self._id_column in self._names_dict:
                self._names_dict.pop(self._id_column)
        else:
            self.add(self._id_column, "first")

        df = df.groupby(grouping).agg(self._aggs_dict)
        agg_columns = pd.Index()
        for names in [self._names_dict[x] for x in df.columns.levels[0]]:
            agg_columns += names
        df.columns = agg_columns
        df = df.reset_index()
        return df

    @staticmethod
    def _get_most_frequent(x):
        counts = x.value_counts()
        val = counts[counts == counts.max()].sort_index().index[0]
        return val

    @staticmethod
    def _get_interval(x):
        return x.sem() * st.t.ppf(1 - 0.025, len(x))

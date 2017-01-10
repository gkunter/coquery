# -*- coding: utf-8 -*-
"""
results.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import logging

from coquery import options
from coquery.defines import *
from coquery.unicode import utf8
from coquery import managers

from .pyqt_compat import QtCore, QtGui, get_toplevel_window
from . import classes


class CoqResultsTableView(classes.CoqTableView):

    def __init__(self, *args, **kwargs):
        super(CoqResultsTableView, self).__init__(*args, **kwargs)
        self.next_ix = None

        self.setWordWrap(options.cfg.word_wrap)
        self.setFont(options.cfg.table_font)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSortingEnabled(False)
        self.setSelectionBehavior(self.SelectItems)
        self.setSelectionMode(self.ExtendedSelection)

        h_header = classes.CoqHorizontalHeader(QtCore.Qt.Horizontal)
        h_header.setMovable(True)
        h_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        h_header.setSelectionBehavior(QtGui.QAbstractItemView.SelectColumns)
        h_header.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setHorizontalHeader(h_header)

        v_header = self.verticalHeader()
        v_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        v_header.setDefaultSectionSize(QtGui.QLabel().sizeHint().height() + 2)

    def setDelegates(self):
        h_header = self.horizontalHeader()
        session = get_toplevel_window().Session
        for i in range(h_header.count()):
            column = self.model().header[h_header.logicalIndex(i)]
            if column.startswith("func_"):
                manager = managers.get_manager(options.cfg.MODE, session)
                fun = manager.get_function(column)
                try:
                    retranslate = dict(zip(COLUMN_NAMES.values(), COLUMN_NAMES.keys()))[fun.get_name()]
                except (KeyError, AttributeError):
                    pass
                else:
                    column = retranslate
            if column in ("statistics_proportion",
                      "statistics_normalized", "statistics_ttr",
                      "statistics_group_proportion", "statistics_group_ttr",
                      "coq_conditional_probability",
                      "coq_conditional_probability_left",
                      "coq_conditional_probability_right",
                      "coq_statistics_uniquenessratio"):
                deleg = classes.CoqProbabilityDelegate(self)
            elif column in ("statistics_percent", "statistics_group_percent"):
                deleg = classes.CoqPercentDelegate(self)
            elif column in ("statistics_column_total"):
                deleg = classes.CoqTotalDelegate(self)
            elif column.startswith("statistics_g_test"):
                deleg = classes.CoqLikelihoodDelegate(self)
            else:
                deleg = classes.CoqResultCellDelegate(self)
            self.setItemDelegateForColumn(i, deleg)

        # reset row delegates if an ALL row has previously been set:
        if hasattr(self, "_old_row_delegate"):
            row, delegate = self._old_row_delegate
            self.setItemDelegateForRow(row, delegate)
            del self._old_row_delegate

        # set row delegate for ALL row of Contingency aggregates:
        if (options.cfg.MODE == QUERY_MODE_CONTINGENCY and
            not session.is_statistics_session()):
            row = self.model().rowCount() - 1
            self._old_row_delegate = (row, self.itemDelegateForRow(row))
            self.setItemDelegateForRow(row, classes.CoqTotalDelegate(self))


class CoqHiddenResultsTable(CoqResultsTableView):
    def setDelegates(self):
        pass
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

from .pyqt_compat import QtCore, QtGui
from . import classes

class CoqResultsTable(classes.CoqTableView):
    
    def __init__(self, *args, **kwargs):
        super(CoqResultsTable, self).__init__(*args, **kwargs)

        options.cfg.word_wrap = [0, int(QtCore.Qt.TextWordWrap)][bool(getattr(options.cfg, "word_wrap", False))]
        self.setWordWrap(options.cfg.word_wrap)
        self.setFont(options.cfg.table_font)

        self.setHorizontalHeader(classes.CoqHorizontalHeader(QtCore.Qt.Horizontal))
        self.horizontalHeader().setMovable(True)
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().setSelectionBehavior(QtGui.QAbstractItemView.SelectColumns)
        self.horizontalHeader().setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.verticalHeader().setDefaultSectionSize(QtGui.QLabel().sizeHint().height() + 2)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSortingEnabled(False)
        self.setSelectionBehavior(self.SelectItems)
        self.setSelectionMode(self.ExtendedSelection)

    def setDelegates(self):
        
        header = self.horizontalHeader()
        for i in range(header.count()):
            column = self.model().header[header.logicalIndex(i)]
            if column.startswith("func_"):
                manager = managers.get_manager(options.cfg.MODE, options.cfg.main_window.Session.Resource.name)
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
        if options.cfg.MODE == QUERY_MODE_CONTINGENCY:
            row = self.model().rowCount() - 1
            self._old_row_delegate = (row, self.itemDelegateForRow(row))
            self.setItemDelegateForRow(row, classes.CoqTotalDelegate(self))
        


# -*- coding: utf-8 -*-
"""
findwidget.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from .pyqt_compat import QtWidgets, QtCore

from .ui.findWidgetUi import Ui_FindWidget

class CoqFindWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(CoqFindWidget, self).__init__(*args, **kwargs)
        self.ui = Ui_FindWidget()
        self.ui.setupUi(self)

        self.ui.edit_find.textChanged.connect(self.find)
        self.ui.button_find_next.clicked.connect(self.go_to_next)
        self.ui.button_find_prev.clicked.connect(self.go_to_prev)
        self.ui.button_find_close.clicked.connect(lambda: self.hide())
        self.table_view = None
        self.reset()

    def setTableView(self, table_view):
        self.table_view = table_view

    def tableView(self):
        return self.table_view

    def hide(self):
        super(CoqFindWidget, self).hide()
        self.ui.edit_find.setEnabled(False)
        self.ui.button_find_next.setEnabled(False)
        self.ui.button_find_prev.setEnabled(False)
        self.ui.button_find_close.setEnabled(False)

    def show(self):
        if (self.table_view and
            self.table_view.model()):
            super(CoqFindWidget, self).show()
            self.ui.edit_find.setEnabled(True)
            self.ui.button_find_next.setEnabled(True)
            self.ui.button_find_prev.setEnabled(True)
            self.ui.edit_find.setFocus()
            self.ui.button_find_close.setEnabled(True)

    def reset(self):
        self.search_string = None
        self.options = None
        self.matches = None
        self.match_index = None
        self.current_match = None

    def go_to_next(self):
        if not self.matches:
            return
        if self.match_index == len(self.matches) - 1:
            self.match_index = 0
        else:
            self.match_index += 1
        self.go_to_index(self.match_index)

    def go_to_prev(self):
        if not self.matches:
            return
        if self.match_index > 0:
            self.match_index -= 1
        else:
            self.match_index = len(self.matches) - 1
        self.go_to_index(self.match_index)

    def go_to_index(self, i):
        if not self.matches:
            return
        self.go_to_match(self.matches[i])
        self.match_index = i

    def go_to_match(self, match):
        self.table_view.setCurrentIndex(match)
        self.table_view.scrollTo(match)
        self.current_match = match

    def find(self, text, options=QtCore.Qt.MatchContains):
        self.matches = []
        for col in range(self.table_view.model().columnCount()):
            start_index = self.table_view.model().index(0, col)
            self.matches += list(self.table_view.model().match(
                start_index, QtCore.Qt.DisplayRole, text, -1, options))

        if self.matches:
            if self.current_match in self.matches:
                self.go_to_match(self.current_match)
            else:
                self.go_to_index(0)
            self.search_string = text
            self.options = options
        else:
            self.reset()

# -*- coding: utf-8 -*-
"""
searchLine.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery.unicode import utf8

from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window


class CoqSearchLine(QtWidgets.QWidget):
    dataFound = QtCore.Signal(object)
    noDataFound = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        from .ui import coqSearchLineUi
        super(CoqSearchLine, self).__init__(parent=parent)

        self.ui = coqSearchLineUi.Ui_CoqSearchLine()
        self.ui.setupUi(self)

        self.ui.edit_search.textChanged.connect(self.search)
        self.ui.edit_search.returnPressed.connect(self.search_next)
        self._find = self.findFunction
        self._data = None

    def setData(self, data):
        self._data = data
        self._pos = 0

    def data(self):
        return self._data

    def search_next(self):
        text = utf8(self.ui.edit_search.text())
        self.search(text, find_next=True)

    def findFunction(self, text, data):
        return text in data

    def setFindFunction(self, func):
        self._find = func

    def search(self, text, find_next=False):
        text = utf8(text.lower())
        if not text or not self._data:
            return

        if find_next:
            pos = self._pos + 1
        else:
            self._pos = 0
            pos = 0

        data = self._data[pos:] + self._data[:pos]

        for i, content in enumerate(pos):
            row = i + pos
            if row > len(data):
                row = i + pos - len(data)

            if self.findFunction(text, content):
                self.dataFound.emit(data)
                break
        else:
            self.noDataFound.emit()


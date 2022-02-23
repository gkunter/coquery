# -*- coding: utf-8 -*-
"""
linkedlists.py is part of Coquery.

Copyright (c) 2017-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal

from coquery.gui.ui import coqLinkedListsUi


class CoqLinkedLists(QtWidgets.QAbstractItemView):
    """
    A QWidget that presents two hierarchical lists. The entries in the left
    list represent the higher order of the entries in the right list.
    """
    itemSelectionChanged = pyqtSignal()
    currentItemChanged = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(CoqLinkedLists, self).__init__(*args, **kwargs)
        self.ui = coqLinkedListsUi.Ui_CoqLinkedLists()
        self.ui.setupUi(self)
        self._width_left = None
        self._set_left_width(0)
        self.models = []
        self.ui.list_classes.currentRowChanged.connect(
            self.setCurrentCategoryRow)
        self.ui.list_functions.activated.connect(self.setCurrentListRow)

    def verticalOffset(self):
        return 0

    def horizontalOffset(self):
        return 0

    def _set_left_width(self, w):
        max_w = QtWidgets.QWidget.sizeHint(self).width()
        self.ui.splitter.setSizes([w, max_w - w])
        self._width_left = w

    def addList(self, left_item, right_items):
        self.ui.list_classes.addItem(left_item)
        w = QtWidgets.QLabel(left_item.text()).sizeHint().width()
        self._set_left_width(max(self._width_left, w))

        new_model = QtGui.QStandardItemModel()
        for item in right_items:
            new_model.appendRow(item)
        self.models.append(new_model)

    def list_(self, index):
        return self.models[index]

    def indexOfCategory(self, item):
        for i in range(self.ui.list_classes.count()):
            list_item = self.ui.list_classes.item(i)
            if item == list_item:
                return i
        return None

    def listCount(self):
        return len(self.models)

    def setCurrentListRow(self, i):
        if type(i) == int:
            index = self.ui.list_functions.model().index(i, 0)
        else:
            index = i
        self.ui.list_functions.edit(index)

    def setAlternatingRowColors(self, value):
        self.ui.list_functions.setAlternatingRowColors(value)

    def setCurrentCategoryRow(self, i):
        self.ui.list_functions.setModel(self.models[i])
        self.ui.list_classes.setCurrentRow(i)

    def setListDelegate(self, delegate):
        delegate.setParent(self.ui.list_functions)
        self.ui.list_functions.setItemDelegate(delegate)

    def setCategoryDelegate(self, delegate):
        delegate.setParent(self.ui.list_classes)
        self.ui.list_classes.setDelegate(delegate)

    def setEditTriggers(self, *args, **kwargs):
        self.ui.list_functions.setEditTriggers(*args, **kwargs)

    def event(self, ev, *args, **kwargs):
        if ev.type() == ev.UpdateRequest:
            self.ui.list_functions.update()
        return super(CoqLinkedLists, self).event(ev, *args, **kwargs)

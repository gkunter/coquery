# -*- coding: utf-8 -*-
"""
listwidget.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import warnings


from coquery import options
from coquery.defines import *
from coquery.unicode import utf8

from .pyqt_compat import QtCore, QtWidgets, QtGui, get_toplevel_window
from . import classes
from .ui.buttonListUi import Ui_ButtonList


class CoqButtonList(QtWidgets.QWidget):
    listOrderChanged = QtCore.Signal()

    def __init__(self, remove=False, parent=None):
        super(CoqButtonList, self).__init__(parent)
        self.ui = Ui_ButtonList()
        self.ui.setupUi(self)

        if remove:
            self.ui.button_remove_group.hide()

        self.columns = []
        self._check_available = lambda x: x

        self.ui.button_remove_group.setIcon(
            get_toplevel_window().get_icon("Delete"))
        self.ui.button_group_up.setIcon(
            get_toplevel_window().get_icon("Circled Chevron Up"))
        self.ui.button_group_down.setIcon(
            get_toplevel_window().get_icon("Circled Chevron Down"))

        #self.ui.button_remove_group.clicked.connect(self._remove_feature)
        self.ui.list_widget.itemActivated.connect(self._check_buttons)

        self._old_drop = self.ui.list_widget.dropEvent
        self.ui.list_widget.dropEvent = self.dropEvent

        self.ui.button_group_up.clicked.connect(
            lambda: self._move_group_column(direction="up"))
        self.ui.button_group_down.clicked.connect(
            lambda: self._move_group_column(direction="down"))

        self._check_buttons()

    def dropEvent(self, *args, **kwargs):
        self._old_drop(*args, **kwargs)
        self.listOrderChanged.emit()

    def setItems(self, rows):
        self.ui.list_widget.clear()
        if rows:
            if type(rows[0]) != tuple or len(rows[0]) != 2:
                rows = [(x, x) for x in rows]

            for label, data in rows:
                item = QtWidgets.QListWidgetItem(label)
                item.setData(QtCore.Qt.UserRole, data)
                self.ui.list_widget.addItem(item)

    def items(self):
        items = []
        for i in range(self.ui.list_widget.count()):
            item = self.ui.list_widget.item(i)
            items.append((item, item.data(QtCore.Qt.UserRole)))
        return items

    def _check_buttons(self):
        current_row = self.ui.list_widget.currentRow()
        self.ui.button_remove_group.setEnabled(current_row > -1)
        self.ui.button_group_up.setEnabled(current_row > 0)
        self.ui.button_group_down.setEnabled(
            current_row < self.ui.list_widget.count() - 1)

    def _move_group_column(self, direction):
        current_row = self.ui.list_widget.currentRow()
        item = self.ui.list_widget.takeItem(current_row)
        new_row = current_row - 1 if direction == "up" else current_row + 1
        self.ui.list_widget.insertItem(new_row, item)
        self.ui.list_widget.setCurrentRow(new_row)
        self.listOrderChanged.emit()
        self._check_buttons()


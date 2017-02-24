# -*- coding: utf-8 -*-
"""
groupcolumns.py is part of Coquery.

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
from .ui.groupColumnsUi import Ui_GroupColumns


class CoqGroupColumns(QtWidgets.QWidget):
    featureDropped = QtCore.Signal(str)
    featureRemoved = QtCore.Signal(str)
    groupsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(CoqGroupColumns, self).__init__(parent)
        self.ui = Ui_GroupColumns()
        self.ui.setupUi(self)

        self.columns = []
        self._check_available = lambda x: x

        self.ui.list_widget.viewport().setAcceptDrops(True)

        self.ui.button_remove_group.setIcon(
            get_toplevel_window().get_icon("Delete"))
        self.ui.button_group_up.setIcon(
            get_toplevel_window().get_icon("Circled Chevron Up"))
        self.ui.button_group_down.setIcon(
            get_toplevel_window().get_icon("Circled Chevron Down"))

        self.ui.button_remove_group.clicked.connect(self._remove_feature)
        self.ui.list_widget.featureAdded.connect(self._add_feature)
        self.ui.list_widget.itemActivated.connect(self._check_buttons)
        self.groupsChanged.connect(self._check_buttons)
        self.groupsChanged.connect(self.checkGroupColumns)

        self.ui.button_group_up.clicked.connect(
            lambda: self._move_group_column(direction="up"))
        self.ui.button_group_down.clicked.connect(
            lambda: self._move_group_column(direction="down"))

    def setCheckAvailableFunction(self, func):
        self._check_available = func

    def checkAvailableFunction(self):
        return self._check_available

    def checkGroupColumns(self, selected=None):
        if not selected:
            selected = get_toplevel_window().column_tree.selected()
        for i in range(len(self.columns)):
            item = self.ui.list_widget.item(i)
            rc_feature = item.data(QtCore.Qt.UserRole)
            if not self.checkAvailableFunction()(rc_feature):
                item.setIcon(get_toplevel_window().get_icon("Error"))
                item.setToolTip(msg_column_not_in_data)
            else:
                item.setIcon(QtGui.QIcon())
                item.setToolTip("")

    def addFeature(self, rc_feature):
        self.ui.list_widget.addFeature(rc_feature)

    def _check_buttons(self):
        current_row = self.ui.list_widget.currentRow()
        self.ui.button_remove_group.setEnabled(current_row > -1)
        self.ui.button_group_up.setEnabled(current_row > 0)
        self.ui.button_group_down.setEnabled(current_row <
                                                 len(self.columns) - 1)

    def _add_feature(self, rc_feature):
        self.columns.append(rc_feature)
        self.groupsChanged.emit()

    def _remove_feature(self):
        current_row = self.ui.list_widget.currentRow()
        item = self.ui.list_widget.takeItem(current_row)
        self.columns.remove(item.data(QtCore.Qt.UserRole))
        self.groupsChanged.emit()

    def _move_group_column(self, direction):
        current_row = self.ui.list_widget.currentRow()
        item = self.ui.list_widget.takeItem(current_row)
        new_row = current_row - 1 if direction == "up" else current_row + 1
        self.ui.list_widget.insertItem(new_row, item)
        self.ui.list_widget.setCurrentRow(new_row)
        self.groupsChanged.emit()


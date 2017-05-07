# -*- coding: utf-8 -*-
"""
groups.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

import re

from coquery import options
from coquery.unicode import utf8
from coquery.managers import Group
from coquery.functions import (
    Freq, FreqNorm, FreqPTW, FreqPMW,
    RowNumber, Tokens, Types, TypeTokenRatio,
    Entropy, Percent, Proportion)

from .pyqt_compat import QtWidgets, QtGui, QtCore, get_toplevel_window
from .classes import CoqDetailBox, CoqClickableLabel
from .addfunction import FunctionItem
from .ui.groupDialogUi import Ui_GroupDialog
from .listselect import CoqListSelect, SelectionDialog


class FunctionWidget(QtWidgets.QWidget):
    """
    A FunctionWidget is a widget that manages a group function.

    It stores a check state, a function class type, and a list of columns.
    """

    def __init__(self, cls, checked, columns, available, *args, **kwargs):
        super(FunctionWidget, self).__init__(*args, **kwargs)
        self._function_class = cls
        self._columns = columns
        self._available_columns = available
        self.setupUi()
        self._update_text()
        self.setCheckState(checked)
        self.checkbox.toggled.connect(self.change_highlight)
        self.change_highlight()

    def setupUi(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.layout = QtWidgets.QHBoxLayout()
        self.column_text = QtWidgets.QLabel()

        # use smaller font for the label that displays the selected columns:
        font = self.column_text.font()
        font.setPointSize(font.pointSize() * 0.8)
        self.column_text.setFont(font)

        self.column_text.setWordWrap(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Expanding)
        self.column_text.setSizePolicy(sizePolicy)

        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.column_text)

        self.checkbox = QtWidgets.QCheckBox()
        self.function_label = CoqClickableLabel(
            self.functionClass().get_name())
        self.function_label.clicked.connect(self.checkbox.toggle)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Preferred)
        self.function_label.setSizePolicy(sizePolicy)

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.function_label)

        if (not self.functionClass().maximum_columns or
            self.functionClass().maximum_columns > 0):
            self.button = QtWidgets.QPushButton("Change columns...")
            self.button.clicked.connect(self.selectColumns)
            self.layout.addWidget(self.button)

    def change_highlight(self):
        palette = QtWidgets.QApplication.instance().palette()

        if self.isChecked():
            style_sheet = """
                CoqClickableLabel {{ background-color: {0};
                                     color: {1};
                                     padding: 2px;
                                     border: 1px inset {2}; }}
                CoqClickableLabel::hover {{
                        padding: 2px;
                        border: 1px solid {2}; }}
                """.format(
                    palette.color(QtGui.QPalette.Highlight).name(),
                    palette.color(QtGui.QPalette.HighlightedText).name(),
                    palette.color(QtGui.QPalette.HighlightedText).name())
        else:
            style_sheet ="""
                CoqClickableLabel {{ padding: 2px; }}
                CoqClickableLabel::hover {{
                        padding: 2px;
                        border: 1px solid {0}; }}
                """.format(
                    palette.color(QtGui.QPalette.Highlight).name())
        self.setStyleSheet(style_sheet)

    def isChecked(self):
        return self.checkbox.isChecked()

    def setCheckState(self, check):
        self.checkbox.setCheckState(check)

    def functionClass(self):
        return self._function_class

    def setFunctionClass(self, cls):
        self._function_class = cls

    def columns(self):
        return self._columns

    def availableColumns(self):
        return self._available_columns

    def setColumns(self, columns):
        new_avail = []
        new_columns = []

        for col in self._columns + self._available_columns:
            if col in columns:
                new_columns.append(col)
            else:
                new_avail.append(col)

        self._columns = new_columns
        self._available_columns = new_avail
        self._update_text()

    def _update_text(self):
        if self.columns():
            cols = [get_toplevel_window().Session.translate_header(x)
                    for x in self.columns()]
            S = "Columns: {}".format(", ".join(cols))
        else:
            S = ""
        self.column_text.setText(S)

    def selectColumns(self):
        selected = SelectionDialog.show(
            "Column selection – Coquery",
            self.columns(), self.availableColumns(),
            translator=get_toplevel_window().Session.translate_header,
            parent=self)
        self.setColumns(selected)


class GroupDialog(QtWidgets.QDialog):
    function_list = (Freq, FreqNorm, FreqPTW, FreqPMW,
                     RowNumber, Tokens, Types, TypeTokenRatio,
                     Entropy, Percent, Proportion)

    def __init__(self, group, df, parent=None, icon=None):
        super(GroupDialog, self).__init__(parent)
        self.ui = Ui_GroupDialog()
        self.ui.setupUi(self)

        # Remove group function columns as they may not be available yet
        # when the group is formed.
        # FIXME: at some point, this needs to be redone so that earlier
        # group columns are available for later groups.
        selected_columns = [x for x in group.columns
                   if not re.match("func_.*_group_", x)]
        available_columns = [x for x in df.columns
                             if x not in group.columns and
                             not re.match("func_.*_group_", x)]

        self.ui.edit_label.setText(group.name)
        self.ui.widget_selection.setSelectedList(
            selected_columns,
            get_toplevel_window().Session.translate_header)
        self.ui.widget_selection.setAvailableList(
            available_columns,
            get_toplevel_window().Session.translate_header)

        function_columns = {fnc_class: columns
                            for fnc_class, columns in group.functions}

        for x in sorted(self.function_list,
                        key=lambda x: x.get_name()):

            if x in function_columns:
                columns = function_columns[x]
            else:
                columns = group.columns
            available_columns = [x for x in df.columns if x not in columns]
            function_widget = FunctionWidget(x,
                                             False,
                                             selected_columns,
                                             available_columns)
            self.ui.scroll_layout.addWidget(function_widget)
            if x in function_columns:
                function_widget.setCheckState(QtCore.Qt.Checked)

    def exec_(self, *args, **kwargs):
        result = super(GroupDialog, self).exec_(*args, **kwargs)
        if result == QtWidgets.QDialog.Accepted:
            name = utf8(self.ui.edit_label.text())
            columns = [x.data(QtCore.Qt.UserRole)
                       for x in self.ui.widget_selection.selectedItems()]
            functions = []
            for i in range(self.ui.scroll_layout.count()):
                item = self.ui.scroll_layout.itemAt(i).widget()
                if item.isChecked():
                    functions.append((item.functionClass(), item.columns()))
            group = Group(name, columns, functions)
            return group
        else:
            return None

    @staticmethod
    def add(group, df, parent=None):
        dialog = GroupDialog(group, df, parent=parent)
        dialog.setVisible(True)
        dialog.setTitle("Add a data group – Coquery")
        return dialog.exec_()

    @staticmethod
    def edit(group, df, parent=None):
        dialog = GroupDialog(group, df, parent=parent)
        dialog.setVisible(True)
        dialog.setWindowTitle("Edit a data group – Coquery")
        return dialog.exec_()

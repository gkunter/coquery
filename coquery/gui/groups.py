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

from coquery.defines import FUNCTION_DESC
from coquery.unicode import utf8
from coquery.managers import Group, Summary
from coquery.functions import (
                    #FilteredRows, PassingRows,
                    Entropy,
                    Freq, FreqNorm,
                    FreqPTW, FreqPMW,
                    ReferenceCorpusSize,
                    ReferenceCorpusFrequency,
                    ReferenceCorpusFrequencyPTW,
                    ReferenceCorpusFrequencyPMW,
                    ReferenceCorpusLLKeyness,
                    ReferenceCorpusDiffKeyness,
                    RowNumber,
                    Percent, Proportion,
                    Tokens, Types,
                    TypeTokenRatio,
                    CorpusSize, SubcorpusSize)

from .pyqt_compat import QtWidgets, QtGui, QtCore, get_toplevel_window
from .classes import CoqClickableLabel
from .ui.groupDialogUi import Ui_GroupDialog
from .listselect import SelectionDialog


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
        self.main_layout = QtWidgets.QGridLayout(self)
        self.main_layout.setSpacing(4)

        self.column_text = QtWidgets.QLabel()

        # use smaller font for the label that displays the selected columns:
        font = self.column_text.font()
        font.setPointSize(font.pointSize() * 0.8)
        self.column_text.setFont(font)

        self.column_text.setWordWrap(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Expanding)
        self.column_text.setSizePolicy(sizePolicy)
        self.column_text.setStyleSheet("padding-left: 3px; ")

        self.checkbox = QtWidgets.QCheckBox()
        desc = FUNCTION_DESC.get(self.functionClass()._name,
                                 "no description available")
        self.function_label = CoqClickableLabel(
            "{} – <span style='font-size: small;'>{}</span>".format(
                self.functionClass().get_name(), desc))
        self.function_label.setWordWrap(True)
        self.function_label.clicked.connect(self.checkbox.toggle)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Preferred)
        self.function_label.setSizePolicy(sizePolicy)

        self.main_layout.addWidget(self.checkbox, 0, 0)
        self.main_layout.addWidget(self.function_label, 0, 1)
        self.main_layout.addWidget(self.column_text, 1, 1, 1, 2)

        if (self.functionClass().maximum_columns is None or
                self.functionClass().maximum_columns > 0):
            self.button = QtWidgets.QPushButton("Change columns...")
            self.button.clicked.connect(self.selectColumns)
            self.main_layout.addWidget(self.button, 0, 2)

        h = self.function_label.sizeHint().height() + 1
        self.function_label.setMinimumHeight(h)
        self.function_label.setMaximumHeight(h)

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
            style_sheet = """
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
                     ReferenceCorpusLLKeyness,
                     ReferenceCorpusDiffKeyness,
                     SubcorpusSize,
                     Entropy, Percent, Proportion)

    def __init__(self, group, all_columns, parent=None):
        super(GroupDialog, self).__init__(parent)
        self.ui = Ui_GroupDialog()
        self.ui.setupUi(self)

        self.ui.scroll_layout.setSpacing(0)
        palette = QtWidgets.QApplication.instance().palette()
        self.ui.scroll_content.setStyleSheet("""
            background-color: {}; """.format(
                palette.color(QtGui.QPalette.Base).name()))

        # Remove group function columns as they may not be available yet
        # when the group is formed.
        # FIXME: at some point, this needs to be redone so that earlier
        # group columns are available for later groups.

        all_columns = [x for x in all_columns
                       if not re.match("func_.*_group_", x)]
        selected_columns = [x for x in group.columns
                            if not re.match("func_.*_group_", x)]
        self.ui.edit_label.setText(group.name)
        self.ui.widget_selection.setSelectedList(
            selected_columns,
            get_toplevel_window().Session.translate_header)

        self.ui.widget_selection.setAvailableList(
            [x for x in all_columns
             if x not in group.columns],
            get_toplevel_window().Session.translate_header)

        function_columns = {fnc_class: columns
                            for fnc_class, columns in group.functions}

        # add function widgets:
        for x in sorted(self.function_list,
                        key=lambda x: x.get_name()):

            # check if this function needs and uses columns:
            if (x.maximum_columns is None or x.maximum_columns > 0):
                cols = function_columns.get(x, selected_columns)
            else:
                cols = []

            function_widget = FunctionWidget(
                x, False,
                cols,
                [x for x in all_columns if x not in cols])

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
    def add(group, all_columns, parent=None):
        dialog = GroupDialog(group, all_columns, parent=parent)
        dialog.setVisible(True)
        dialog.setTitle("Add a data group – Coquery")
        return dialog.exec_()

    @staticmethod
    def edit(group, all_columns, parent=None):
        dialog = GroupDialog(group, all_columns, parent=parent)
        dialog.setVisible(True)
        dialog.setWindowTitle("Edit a data group – Coquery")
        result = dialog.exec_()
        return result

class SummaryDialog(GroupDialog):
    function_list = (
                    #FilteredRows, PassingRows,
                    Entropy,
                    Freq, FreqNorm,
                    FreqPTW, FreqPMW,
                    ReferenceCorpusSize,
                    ReferenceCorpusFrequency,
                    ReferenceCorpusFrequencyPTW,
                    ReferenceCorpusFrequencyPMW,
                    ReferenceCorpusLLKeyness,
                    ReferenceCorpusDiffKeyness,
                    RowNumber,
                    Percent, Proportion,
                    Tokens, Types,
                    TypeTokenRatio,
                    CorpusSize, SubcorpusSize)


    def __init__(self, group, all_columns, parent=None):
        super(SummaryDialog, self).__init__(group, all_columns, parent)
        self.ui.label.hide()
        self.ui.label_2.hide()
        self.ui.widget_selection.hide()
        self.ui.edit_label.hide()
        self.ui.verticalLayout.setRowStretch(2, 0)

    @staticmethod
    def edit(group, all_columns, parent=None):
        dialog = SummaryDialog(group, all_columns, parent=parent)
        dialog.setVisible(True)
        dialog.setWindowTitle("Edit summary functions – Coquery")
        group = dialog.exec_()
        if group:
            return Summary(name=group.name, functions=group.functions)


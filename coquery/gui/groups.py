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
                    get_base_func,
                    Entropy,
                    Add,
                    Min, Max, Mean, Median, StandardDeviation,
                    InterquartileRange,
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
from .listselect import SelectionDialog
from .ui import groupFunctionWidgetUi


class GroupFunctionWidget(QtWidgets.QWidget):
    """
    A GroupFunctionWidget is a widget that manages a group function.

    It stores a check state, a function class type, and a list of columns.
    """
    dataChanged = QtCore.Signal()
    columnsClicked = QtCore.Signal()
    lostFocus = QtCore.Signal()

    def __init__(self, cls, *args, **kwargs):
        super(GroupFunctionWidget, self).__init__(*args, **kwargs)
        self.ui = groupFunctionWidgetUi.Ui_GroupFunctionWidget()
        self.ui.setupUi(self)

        for signal in (self.ui.checkbox.stateChanged, ):
            signal.connect(self.fireDataChanged)

        self.ui.button_columns.clicked.connect(self.selectColumns)

        margins = self.ui.gridLayout.contentsMargins()
        margins.setRight(
            margins.right() +
            QtWidgets.QScrollBar(QtCore.Qt.Vertical).sizeHint().width())
        self.ui.gridLayout.setContentsMargins(margins)

        self._columns = []
        self._available_columns = []
        self._function_class = cls

        desc = FUNCTION_DESC.get(cls._name, "(no description available)")
        self.ui.label_title.setText(
            "{}<br><span style='font-size: small;'>{}</span>".format(
                cls.get_name(), desc))

        self.hideArguments()

    def fireDataChanged(self, *args, **kwargs):
        self.dataChanged.emit()

    def content(self):
        return [self.functionClass(),
                self.columns(),
                self.availableColumns(),
                self.checkState()]

    def setContent(self, data):
        cls, columns, available, checkstate = data
        if (cls.maximum_columns == 0):
            self.ui.button_columns.hide()
            self.ui.label_columns.hide()
        self.setColumns(columns)
        self.ui.checkbox.setCheckState(checkstate)
        self.ui.button_columns.setDisabled(len(columns + available) == 0)

    def hideArguments(self):
        self.ui.button_columns.hide()

    def showArguments(self):
        self.ui.button_columns.show()

    def checkState(self):
        return self.ui.checkbox.checkState()

    def setCheckState(self, check):
        self.ui.checkbox.setCheckState(check)

    def functionClass(self):
        return self._function_class

    def setFunctionClass(self, cls):
        self._function_class = cls

    def columns(self):
        return self._columns

    def availableColumns(self):
        return self._available_columns

    def setColumns(self, columns):
        self._columns = columns
        template = "<span style='font-size: small;'>{}</span>"
        if self.columns():
            try:
                cols = [get_toplevel_window().Session.translate_header(x)
                        for x in columns]
            except AttributeError:
                cols = columns
            S = template.format(", ".join(cols))
        else:
            S = "(none)"
        self.ui.label_columns.setText(S)

    def setAvailableColumns(self, columns):
        self._available_columns = columns

    def selectColumns(self):
        try:
            translator = get_toplevel_window().Session.translate_header
        except AttributeError:
            translator = None

        available = self.availableColumns()
        columns = self.columns()
        selected, available = SelectionDialog.show(
            "Column selection – Coquery",
            columns, available,
            translator=translator,
            parent=self)
        self.setColumns(selected)
        self.setAvailableColumns(available)
        self.fireDataChanged()

    def event(self, ev, *args, **kwargs):
        return super(GroupFunctionWidget, self).event(ev, *args, **kwargs)


class GroupFunctionDelegate(QtWidgets.QItemDelegate):
    """
    This delegate is used to display a GroupFunctionWidget in a QListView or
    similar views.
    """
    def __init__(self, *args, **kwargs):
        super(GroupFunctionDelegate, self).__init__(*args, **kwargs)
        self._editor = None

    def editor(self):
        return self._editor

    def paint(self, painter, option, index):
        painter.save()
        data = self._get_data(index)
        cls, columns, available, checkstate = data

        widget = GroupFunctionWidget(cls)
        widget.setContent(data)
        widget.setMaximumWidth(self.parent().size().width())
        widget.setMinimumWidth(self.parent().size().width())

        rect = option.rect
        rect.adjust(0, 0, 0, 0)
        if (option.state & QtWidgets.QStyle.State_Selected):
            painter.fillRect(rect, option.palette.highlight())

        paint_widget = True
        if self._editor is not None:
            paint_widget = False
            try:
                if self._editor.isHidden():
                    paint_widget = True
            except RuntimeError:
                paint_widget = True

        if (not (option.state & QtWidgets.QStyle.State_Selected) or
                paint_widget):
            painter.translate(rect.topLeft())
            widget.render(painter, QtCore.QPoint(), QtGui.QRegion(),
                          widget.DrawChildren)

        painter.restore()

    def createEditor(self, parent, option, index):
        data = self._get_data(index)
        cls, columns, available, checkstate = data
        editor = GroupFunctionWidget(cls, parent=parent)
        editor.setMaximumWidth(self.parent().size().width())
        editor.setMinimumWidth(self.parent().size().width())
        editor.setContent(data)
        editor.showArguments()
        self._editor = editor
        self._index = index
        self._editor.dataChanged.connect(self.pushData)
        return editor

    def pushData(self):
        item = self.parent().model().item(self._index.row(),
                                          self._index.column())
        item.setData(self._editor.content(), QtCore.Qt.UserRole)

    def setEditorData(self, editor, index):
        model = self.parent().model()
        data = model.data(index, QtCore.Qt.UserRole)
        editor.setContent(data)

    def setModelData(self, editor, model, index):
        cls = editor.functionClass()
        columns = editor.columns()
        available = editor.availableColumns()
        checkstate = editor.checkState()
        data = [cls, columns, available, checkstate]
        model.itemFromIndex(index).setData(data, QtCore.Qt.UserRole)
        self._editor = None

    def _get_data(self, index):
        data = self.parent().model().data(index, QtCore.Qt.UserRole)
        return data

    def sizeHint(self, item, index):
        data = self._get_data(index)
        cls, columns, available, checkstate = data
        widget = GroupFunctionWidget(cls, parent=self.parent())
        widget.setContent(data)
        widget.showArguments()
        widget.setMaximumWidth(self.parent().sizeHint().width())
        widget.setMinimumWidth(self.parent().sizeHint().width())
        return widget.sizeHint()


class GroupDialog(QtWidgets.QDialog):
    function_list = (Freq, FreqNorm, FreqPTW, FreqPMW,
                     RowNumber, Tokens, Types, TypeTokenRatio,
                     Add,
                     Min, Max, Mean, Median, StandardDeviation,
                     InterquartileRange,
                     ReferenceCorpusLLKeyness,
                     ReferenceCorpusDiffKeyness,
                     SubcorpusSize,
                     Entropy, Percent, Proportion)

    def __init__(self, group, all_columns, parent=None):
        super(GroupDialog, self).__init__(parent)
        from .ui.groupDialogUi import Ui_GroupDialog
        self.ui = Ui_GroupDialog()
        self.ui.setupUi(self)

        self.ui.ok_button = self.ui.buttonBox.button(
            QtWidgets.QDialogButtonBox.Ok)

        # Remove group function columns as they may not be available yet
        # when the group is formed.
        # FIXME: at some point, this needs to be redone so that earlier
        # group columns are available for later groups.
        self.all_columns = [x for x in all_columns
                            if not re.match("func_.*_group_", x)]
        group.columns = [x for x in group.columns if x in all_columns]
        selected_columns = [x for x in group.columns
                            if not re.match("func_.*_group_", x)]

        self.ui.edit_label.setText(group.name)
        self.ui.radio_remove_duplicates.setChecked(group.show_distinct)

        self.ui.widget_selection.setSelectedList(
            selected_columns,
            get_toplevel_window().Session.translate_header)
        self.ui.widget_selection.setAvailableList(
            [x for x in self.all_columns
             if x not in group.columns],
            get_toplevel_window().Session.translate_header)

        self.ui.widget_selection.itemSelectionChanged.connect(
            self.check_buttons)
        self.ui.widget_selection.itemSelectionChanged.connect(
            self.update_tabs)
        self.check_buttons(selected=self.ui.widget_selection.selectedItems())
        function_columns = {fnc_class: columns
                            for fnc_class, columns in group.functions}

        delegate = GroupFunctionDelegate()
        self.ui.linked_functions.setListDelegate(delegate)

        function_groups = self.get_function_groups()

        for fun_base in sorted(function_groups,
                               key=lambda x: x.get_description()):

            group_item = QtWidgets.QListWidgetItem(
                fun_base.get_description())
            function_items = []
            for fnc in function_groups[fun_base]:
                list_item = QtGui.QStandardItem()
                if fnc in function_columns:
                    columns = function_columns[fnc]
                    available = [x for x in self.all_columns
                                 if x not in columns]
                    check = QtCore.Qt.Checked
                else:
                    columns = self.all_columns
                    available = []
                    check = QtCore.Qt.Unchecked
                list_item.setData([fnc, columns, available, check],
                                  QtCore.Qt.UserRole)
                function_items.append(list_item)

            self.ui.linked_functions.addList(group_item, function_items)

        self.ui.linked_functions.setCurrentCategoryRow(0)

        self.dtypes = []

        vis_cols = list(get_toplevel_window().table_model.content.columns)
        hidden_cols = list(get_toplevel_window().hidden_model.content.columns)

        vis_dtypes = get_toplevel_window().table_model.content.dtypes
        hidden_dtypes = get_toplevel_window().hidden_model.content.dtypes

        for col in self.all_columns:
            if col in vis_cols:
                dtype = vis_dtypes[col]
            else:
                dtype = hidden_dtypes[col]
            self.dtypes.append(dtype)

        self.ui.widget_filters.setData(self.all_columns,
                                       self.dtypes,
                                       group.filters,
                                       get_toplevel_window().Session)

    def _get_dtypes(self, columns):
        return [self.dtypes[self.all_columns.index(col)] for col in columns]

    def check_buttons(self, selected=None):
        selected = selected or []
        self.ui.ok_button.setEnabled(len(selected) > 0)

    def update_tabs(self, selected):
        features = [item.data(QtCore.Qt.UserRole) for item in selected]
        columns = [col for col in self.all_columns if col not in features]
        dtypes = self._get_dtypes(columns)
        filters = self.ui.widget_filters.filters()

        return
        self.ui.widget_filters.setData(columns,
                                       dtypes,
                                       filters,
                                       get_toplevel_window().Session)
        self.ui.widget_filters.setEnabled(len(columns))




    def setup_values(self, group):
        self.ui.edit_label.setText(group.name)

    def get_function_groups(self):
        """
        Return a dictionary with base function classes as keys and lists of
        function classes as values. This dictionary can be used to populate
        the class list and function list of the dialog.
        """
        function_groups = {}
        for fun in self.function_list:
            fun_base = get_base_func(fun)
            if fun_base not in function_groups:
                function_groups[fun_base] = []
            function_groups[fun_base].append(fun)
        for fun_base in function_groups:
            function_groups[fun_base] = sorted(function_groups[fun_base],
                                               key=lambda x: x._name)
        return function_groups

    def get_selected_items(self):
        selected = []
        for i in range(self.ui.linked_functions.listCount()):
            sublist = self.ui.linked_functions.list_(i)
            for row in range(sublist.rowCount()):
                item = sublist.item(row, 0)
                data = item.data(QtCore.Qt.UserRole)
                cls, columns, available, checkstate = data
                if checkstate == QtCore.Qt.Checked:
                    selected.append((cls, columns))
        return selected

    def exec_(self, *args, **kwargs):
        result = super(GroupDialog, self).exec_(*args, **kwargs)
        if result == self.Accepted:
            kwargs = dict(
                name=utf8(self.ui.edit_label.text()),
                columns=[x.data(QtCore.Qt.UserRole)
                         for x in self.ui.widget_selection.selectedItems()],
                functions=self.get_selected_items(),
                filters=self.ui.widget_filters.filters(),
                distinct=bool(self.ui.radio_remove_duplicates.isChecked()))
            return Group(**kwargs)
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
        self.ui.radio_remove_duplicates.hide()
        self.ui.radio_keep_duplicates.hide()
        self.ui.widget_selection.hide()
        self.ui.edit_label.hide()
        edit_search = self.ui.layout_functions.takeAt(0).widget()
        function_list = self.ui.layout_functions.takeAt(0).widget()
        self.ui.tabWidget.hide()
        self.ui.gridLayout.addWidget(edit_search, 0, 0)
        self.ui.gridLayout.addWidget(function_list, 1, 0)
        self.ui.gridLayout.setColumnStretch(0, 1)
        self.ui.gridLayout.setColumnStretch(1, 0)

    def check_buttons(self, selected=False):
        pass

    @staticmethod
    def edit(group, all_columns, parent=None):
        dialog = SummaryDialog(group, all_columns, parent=parent)
        dialog.setVisible(True)
        dialog.setWindowTitle("Edit summary functions – Coquery")
        group = dialog.exec_()
        if group:
            return Summary(name=group.name, functions=group.functions,
                           columns=all_columns, distinct=group.show_distinct)

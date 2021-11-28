# -*- coding: utf-8 -*-
"""
addfunction.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery import options
from coquery import functions
from coquery.defines import FUNCTION_DESC
from coquery.unicode import utf8
from .classes import CoqFloatEdit, CoqIntEdit
from .pyqt_compat import QtCore, QtWidgets, QtGui, get_toplevel_window
from .listselect import SelectionDialog


class Argument(QtWidgets.QWidget):
    valueChanged = QtCore.Signal()

    def __init__(self, wtype, tup, parent):
        super(Argument, self).__init__(parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.wtype = wtype
        try:
            self.name, label, default, val_range = tup
        except ValueError:
            val_range = []
            self.name, label, default = tup

        self.label = QtWidgets.QLabel(label)

        if wtype == "string":
            self.widget = QtWidgets.QLineEdit()
            self.widget.textChanged.connect(self._fire)
        elif wtype == "int":
            self.widget = CoqIntEdit()
            self.widget.valueChanged.connect(self._fire)
        elif wtype == "float":
            self.widget = CoqFloatEdit()
            self.widget.valueChanged.connect(self._fire)
        elif wtype == "check":
            self.widget = QtWidgets.QCheckBox()
            self.widget.stateChanged.connect(self._fire)
        elif wtype == "choose":
            self.widget = QtWidgets.QComboBox()
            self.widget.addItems(val_range)
            self.widget.currentIndexChanged.connect(self._fire)

        self.setObjectName(self.name)
        self.setValue(default)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.widget)
        self.layout.setStretch(1, 1)

    def _fire(self):
        self.valueChanged.emit()

    def setValue(self, val):
        if self.wtype == "string":
            self.widget.setText(val)
        elif self.wtype in ("int", "float"):
            self.widget.setValue(val)
        elif self.wtype == "check":
            self.widget.setCheckState(QtCore.Qt.Checked if val else
                                      QtCore.Qt.Unchecked)
        elif self.wtype == "choose":
            self.widget.setCurrentIndex(self.widget.findText(val))

    def value(self):
        if self.wtype == "string":
            return self.widget.text()
        elif self.wtype in ("int", "float"):
            return self.widget.value()
        elif self.wtype == "check":
            return self.widget.checkState()
        elif self.wtype == "choose":
            return self.widget.currentText()

    def setFocus(self):
        return self.widget.setFocus()


class FunctionWidget(QtWidgets.QWidget):
    argumentsChanged = QtCore.Signal()

    def __init__(self, func, checkable=True, is_checked=False,
                 *args, **kwargs):
        super(FunctionWidget, self).__init__(*args, **kwargs)
        self.checkable = checkable
        self.argument_list = []

        name = func.get_name()
        desc = (func.get_description() or
                FUNCTION_DESC.get(func._name, "(no description available)"))

        self.checkable = checkable

        self.outerLayout = QtWidgets.QHBoxLayout(self)
        self.outerLayout.setContentsMargins(4, 4, 4, 4)
        self.outerLayout.setSpacing(8)

        self.innerLayout = QtWidgets.QVBoxLayout()
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)

        self.label_1 = QtWidgets.QLabel(name, self)
        self.innerLayout.addWidget(self.label_1)

        if desc is not None:
            self.label_2 = QtWidgets.QLabel(desc, self)
            self.innerLayout.addWidget(self.label_2)

            font = self.label_1.font()
            font.setPointSize(font.pointSize() * 0.8)
            self.label_2.setFont(font)

        self.arguments = QtWidgets.QWidget()
        self.argumentLayout = QtWidgets.QHBoxLayout(self.arguments)
        self.argumentLayout.setContentsMargins(0, 0, 0, 0)
        self.argumentLayout.setSpacing(8)

        # Add widgets for each of the arguments, sorted by type
        for wtype in ("string", "int", "float", "choose", "check"):
            try:
                for tup in func.arguments[wtype]:
                    argument = Argument(wtype, tup, self)
                    self.argumentLayout.addWidget(argument)
                    argument.valueChanged.connect(self._fire)
                    self.argument_list.append(argument)
            except KeyError:
                # ignore if an argument type is not used by function
                pass

        self.innerLayout.addWidget(self.arguments)

        if self.checkable:
            self.checkbox = QtWidgets.QCheckBox()
            self.outerLayout.insertWidget(0, self.checkbox)
            self._arguments_shown = True
        else:
            self.arguments.hide()
            self._arguments_shown = False

        self.setCheckState(QtCore.Qt.Checked if is_checked else
                           QtCore.Qt.Unchecked)

        self.outerLayout.addLayout(self.innerLayout)
        self.outerLayout.setStretch(1, 1)

    def _fire(self):
        self.argumentsChanged.emit()

    def setCheckState(self, *args, **kwargs):
        if self.checkable:
            return self.checkbox.setCheckState(*args, **kwargs)
        else:
            return None

    def checkState(self, *args, **kwargs):
        if self.checkable:
            return self.checkbox.checkState(*args, **kwargs)
        else:
            return False

    def hideArguments(self):
        if not self.checkable:
            self.arguments.hide()
            self._arguments_shown = False

    def showArguments(self):
        self.arguments.show()
        self._arguments_shown = True

    def sizeHint(self):
        size_hint = self.innerLayout.sizeHint()

        height = (self.label_1.sizeHint().height() +
                  self.label_2.sizeHint().height() +
                  8)

        if self._arguments_shown:
            height += self.arguments.sizeHint().height()

        size_hint.setHeight(height)
        return size_hint

    def values(self):
        d = {}
        for i in range(self.argumentLayout.count()):
            item = self.argumentLayout.itemAt(i)
            argument = item.widget()
            d[utf8(argument.objectName())] = argument.value()
        return d

    def setValues(self, d):
        for i in range(self.argumentLayout.count()):
            item = self.argumentLayout.itemAt(i)
            argument = item.widget()
            argument.setValue(d[utf8(argument.objectName())])

    def setFocus(self):
        if self.argument_list:
            return self.argument_list[0].setFocus()
        else:
            return super(FunctionWidget, self).setFocus()


class FunctionList(QtWidgets.QListWidget):
    contentChanged = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(FunctionList, self).__init__(*args, **kwargs)
        self.currentItemChanged.connect(self.change_current_item)
        self.itemSelectionChanged.connect(self.change_selection)

        border = QtGui.QPalette().color(QtGui.QPalette.Active,
                                        QtGui.QPalette.Button)
        selected = QtGui.QPalette().color(QtGui.QPalette.Active,
                                          QtGui.QPalette.Highlight)
        selected_text = QtGui.QPalette().color(QtGui.QPalette.Active,
                                               QtGui.QPalette.HighlightedText)
        border = QtGui.QPalette().color(QtGui.QPalette.Active,
                                        QtGui.QPalette.Button)

        self.setStyleSheet(("""
            FunctionList::item {{ border-bottom: 1px solid {border}; }}
            FunctionList::item:selected {{ background: {selected};
                                          color: {selected_text}; }}
            """).format(
                border=border.name(),
                selected=selected.name(),
                selected_text=selected_text.name()))

    def find_function(self, func):
        """
        Return the list item that stores the function, or None if the function
        is not in the list.
        """
        for i in range(self.count()):
            if func == self.item(i).data(QtCore.Qt.UserRole):
                return self.item(i)
        else:
            return None

    def expandItem(self, item):
        widget = self.itemWidget(item)
        if widget:
            widget.showArguments()
            item.setSizeHint(widget.sizeHint())
            widget.setFocus()

    def collapseItem(self, item):
        widget = self.itemWidget(item)
        if widget:
            widget.hideArguments()
            item.setSizeHint(widget.sizeHint())

    def change_current_item(self, new_item, prev_item):
        if prev_item:
            self.collapseItem(prev_item)

        if new_item:
            self.expandItem(new_item)

    def change_selection(self):
        """
        Ensure that there is always only one item that is selected.

        Due to the resizing of entries with arguments when selecting and
        deselecting them, it appears to be possible to have more than one
        selected item. In that case, only the first selection is retained.
        """
        if len(self.selectedItems()) > 1:
            self.setCurrentItem(self.selectedItems()[0])

    def setItemWidget(self, item, widget):
        widget.argumentsChanged.connect(self._fire)
        return super(FunctionList, self).setItemWidget(item, widget)

    def _fire(self):
        self.contentChanged.emit()


class FunctionDialog(QtWidgets.QDialog):
    def __init__(self, df, func=None, columns=None, parent=None):
        super(FunctionDialog, self).__init__(parent)
        from .ui.addFunctionUi import Ui_FunctionsDialog
        self.ui = Ui_FunctionsDialog()
        self.ui.setupUi(self)

        self.df = df
        self.columns = columns or []
        self.available_columns = [x for x in self.df.columns
                                  if x not in self.columns]

        self.available_functions = {}

        self.ui.label_selected_columns.clicked.connect(self.select_columns)
        self.ui.button_select_columns.clicked.connect(self.select_columns)

        self.ui.list_classes.currentRowChanged.connect(
            self.set_function_group)
        self.ui.list_functions.currentRowChanged.connect(
            self.set_function_label)
        self.ui.list_functions.contentChanged.connect(self.set_function_label)

        try:
            self.resize(options.settings.value("functionapply_size"))
        except TypeError:
            pass

    def select_columns(self):
        selected, available = SelectionDialog.show(
            "Column selection – Coquery",
            self.columns, self.available_columns,
            minimum=1,
            translator=get_toplevel_window().Session.translate_header,
            parent=self)
        self.set_columns(selected)

    def set_columns(self, columns):
        self.columns = columns
        self.available_columns = [x for x in self.df.columns
                                  if x not in columns]
        session = get_toplevel_window().Session
        labels = ["{:2} {}".format(i+1, session.translate_header(x))
                  for i, x in enumerate(self.columns)]
        self.ui.label_selected_columns.setText("\n".join(labels))

        self.blockSignals(True)
        func, values = self.get_function_values()
        self.add_function_groups()
        self.set_function_values(func, values)
        self.blockSignals(False)

    def get_function_values(self):
        item = self.ui.list_functions.currentItem()
        widget = self.ui.list_functions.itemWidget(item)
        values = widget.values()
        return item.data(QtCore.Qt.UserRole), values

    def set_function_values(self, func, values):
        for i in self.available_functions:
            for fun in [x for x in self.available_functions[i]
                        if x._name != "virtual"]:
                if fun == func:
                    self.set_function_group(i)
                    item = self.ui.list_functions.find_function(func)
                    widget = self.ui.list_functions.itemWidget(item)
                    widget.setValues(values)
                    widget.setFocus()
                    self.ui.list_functions.setCurrentItem(item)

    def get_function_groups(self):
        if all([x == object for x in self.df[self.columns].dtypes]):
            function_groups = (functions.StringFunction,
                               functions.Comparison,
                               functions.BaseProportion,
                               functions.BaseFreq,
                               functions.LogicFunction,
                               functions.ConversionFunction)
        elif all([x != object for x in self.df[self.columns].dtypes]):
            function_groups = (functions.OperatorFunction,
                               functions.StatisticalFunction,
                               functions.Comparison,
                               functions.BaseProportion,
                               functions.BaseFreq,
                               functions.LogicFunction,
                               functions.ConversionFunction)
        else:
            function_groups = (functions.Comparison,
                               functions.BaseProportion,
                               functions.BaseFreq,
                               functions.LogicFunction, )
        return function_groups

    def set_function_label(self):
        func, values = self.get_function_values()
        session = get_toplevel_window().Session
        tmp_func = func(columns=self.columns, session=session, **values)
        self.ui.edit_label.setText(tmp_func.get_label(session=session))

    def add_function_groups(self):
        self.blockSignals(True)
        self.ui.list_classes.blockSignals(True)

        self.ui.list_classes.clear()
        self.available_functions = {}

        all_functions = []
        for attr_name in functions.__dict__:
            cls = getattr(functions, attr_name)
            try:
                if issubclass(cls, functions.Function):
                    all_functions.append(cls)
            except TypeError:
                # this is raised if attr is not a class, but e.g. a string
                pass

        for i, fun_class in enumerate(self.get_function_groups()):
            group = QtWidgets.QListWidgetItem(fun_class.get_group())
            self.ui.list_classes.addItem(group)

            fun_list = []
            for fun in all_functions:
                if (issubclass(fun, fun_class) and fun != fun_class):
                    fun_list.append(fun)

            self.available_functions[i] = sorted(fun_list,
                                                 key=lambda x: x.get_name())
        self.set_function_group(0)
        self.blockSignals(False)
        self.ui.list_classes.blockSignals(False)

    def set_function_group(self, i):
        self.blockSignals(True)
        self.ui.list_classes.blockSignals(True)
        self.ui.list_functions.blockSignals(True)

        self.ui.list_functions.clear()

        for fun in [x for x in self.available_functions[i]
                    if x._name != "virtual"]:
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, fun)
            widget = FunctionWidget(fun, False)
            self.ui.list_functions.addItem(item)
            self.ui.list_functions.setItemWidget(item, widget)
            item.setSizeHint(widget.sizeHint())

        self.ui.list_classes.setCurrentRow(i)
        self.ui.list_functions.setCurrentRow(0)
        self.ui.list_functions.expandItem(self.ui.list_functions.item(0))
        self.set_function_label()
        self.blockSignals(False)
        self.ui.list_classes.blockSignals(False)
        self.ui.list_functions.blockSignals(False)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        options.settings.setValue("functionapply_size", self.size())

    def exec_(self):
        result = super(FunctionDialog, self).exec_()
        if result == QtWidgets.QDialog.Accepted:
            func, values = self.get_function_values()
            columns = self.columns
            return (func, columns, values)
        else:
            return None

    @staticmethod
    def set_function(columns, df, parent=None):
        dialog = FunctionDialog(df, parent=parent)
        dialog.add_function_groups()
        dialog.set_columns(columns)
        dialog.setVisible(True)

        return dialog.exec_()

    @staticmethod
    def edit_function(func, df, parent=None):
        dialog = FunctionDialog(df.drop(func.get_id(), axis=1), parent=parent)
        dialog.add_function_groups()
        dialog.set_function_values(type(func), func.kwargs)
        dialog.set_columns(func.columns)
        dialog.setVisible(True)

        return dialog.exec_()

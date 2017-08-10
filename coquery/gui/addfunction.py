# -*- coding: utf-8 -*-
"""
addfunction.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

from coquery import options
from coquery import functions
from coquery import managers
from coquery.defines import FUNCTION_DESC
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtWidgets, QtGui, get_toplevel_window


class Argument(QtWidgets.QWidget):
    def __init__(self, wtype, tup, parent):
        super(Argument, self).__init__(parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.wtype = wtype
        self.name, label, default = tup
        self.label = QtWidgets.QLabel(label)

        if wtype == "input":
            self.widget = QtWidgets.QLineEdit()
            self.widget.setText(default)
        elif wtype == "toggle":
            self.widget = QtWidgets.QCheckBox()
            self.widget.setCheckState(default)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.widget)
        self.layout.setStretch(1, 1)

    def getValue(self):
            if self.wtype == "input":
                return self.widget.text()
            elif self.wtype == "toggle":
                return self.widget.checkState()


class FunctionWidget(QtWidgets.QWidget):
    def __init__(self, func, checkable=True, *args, **kwargs):
        super(FunctionWidget, self).__init__(*args, **kwargs)
        self.checkable = checkable

        name = func.get_name()
        desc = FUNCTION_DESC.get(func._name, "(no description available)")

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

        if "input" in func.arguments:
            for tup in func.arguments["input"]:
                argument = Argument("input", tup, self)
                self.argumentLayout.addWidget(argument)

        if "toggle" in func.arguments:
            for tup in func.arguments["toggle"]:
                argument = Argument("toggle", tup, self)
                self.argumentLayout.addWidget(argument)

        self.innerLayout.addWidget(self.arguments)

        if self.checkable:
            self.checkbox = QtWidgets.QCheckBox()
            self.outerLayout.insertWidget(0, self.checkbox)
            self._arguments_shown = True
        else:

            self.arguments.hide()
            self._arguments_shown = False

        self.outerLayout.addLayout(self.innerLayout)
        self.outerLayout.setStretch(1, 1)

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
                  self.label_2.sizeHint().height())

        if self._arguments_shown:
            height += self.arguments.sizeHint().height()

        size_hint.setHeight(height)
        return size_hint


class FunctionList(QtWidgets.QListWidget):
    def __init__(self, *args, **kwargs):
        super(FunctionList, self).__init__(*args, **kwargs)
        self.currentItemChanged.connect(self.change_selection)

        border = QtGui.QPalette().color(QtGui.QPalette.Active,
                                        QtGui.QPalette.Button)
        selected = QtGui.QPalette().color(QtGui.QPalette.Active,
                                          QtGui.QPalette.Highlight)
        selected_text = QtGui.QPalette().color(QtGui.QPalette.Active,
                                               QtGui.QPalette.HighlightedText)
        border = QtGui.QPalette().color(QtGui.QPalette.Active,
                                        QtGui.QPalette.Button)

        self.setStyleSheet(("""
            QListWidget::item {{ border-bottom: 1px solid {border}; }}
            QListWidget::item:selected {{ background: {selected};
                                          color: {selected_text}; }}
            QListWidget::item:focus {{ background: {selected};
                                          color: {selected_text}; }}
            """).format(
                border=border.name(),
                selected=selected.name(),
                selected_text=selected_text.name()))

    def change_selection(self, new_item, prev_item):
        self.blockSignals(True)
        old = [self.itemWidget(self.item(i)).label_1.text()
               for i in range(self.count())]

        if prev_item:
            prev_widget = self.itemWidget(prev_item)
            if prev_widget:
                prev_widget.hideArguments()
                prev_item.setSizeHint(prev_widget.sizeHint())

        if new_item:
            new_widget = self.itemWidget(new_item)
            if new_widget:
                new_widget.showArguments()
                new_item.setSizeHint(new_widget.sizeHint())

        new = [self.itemWidget(self.item(i)).label_1.text()
               for i in range(self.count())]

        for x in zip(old, new):
            print("{:5}   {} - {}".format(str(x[0] == x[1]), *x))
        self.blockSignals(False)


class ColumnFunctionDialog(QtWidgets.QDialog):
    def __init__(self, columns, df, parent=None):
        super(ColumnFunctionDialog, self).__init__(parent)
        from .ui.addFunctionUi import Ui_FunctionsDialog
        self.ui = Ui_FunctionsDialog()
        self.ui.setupUi(self)

        self.ui.parameter_box.hide()

        self.df = df
        self.columns = columns
        self.available_columns = [x for x in df.columns if x not in columns]

        self.edit_label = ""
        self.session = get_toplevel_window().Session
        self.available_functions = {}

        self.ui.widget_selection.setSelectedList(
            self.columns, self.session.translate_header)
        self.ui.widget_selection.setAvailableList(
            self.available_columns, self.session.translate_header)

        self.ui.widget_selection.setMinimumItems(1)

        self.ui.widget_selection.itemSelectionChanged.connect(
            self.change_columns)
        self.ui.list_classes.currentRowChanged.connect(
            self.set_function_group)

        try:
            self.resize(options.settings.value("functionapply_size"))
        except TypeError:
            pass

    def get_function_values(self):
        return (None, None)

    def set_function_values(self, func, values):
        pass

    def get_function_groups(self):
        if all([x == object for x in self.df[self.columns].dtypes]):
            function_groups = (functions.StringFunction,
                               functions.Comparison,
                               functions.BaseProportion,
                               functions.LogicFunction)
        elif all([x != object for x in self.df[self.columns].dtypes]):
            function_groups = (functions.MathFunction,
                               functions.Comparison,
                               functions.LogicFunction)
        else:
            function_groups = (functions.Comparison,
                               functions.LogicFunction, )
        return function_groups

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
            group = QtWidgets.QListWidgetItem(fun_class.get_description())
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
        self.blockSignals(False)
        self.ui.list_classes.blockSignals(False)
        self.ui.list_functions.blockSignals(False)

    def change_columns(self):
        self.blockSignals(True)
        self.columns = [x.data(QtCore.Qt.UserRole) for x
                        in self.ui.widget_selection.selectedItems()]
        func, values = self.get_function_values()
        self.add_function_groups()
        self.set_function_values(func, values)
        self.blockSignals(False)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        options.settings.setValue("functionapply_size", self.size())

    def exec_(self):
        result = super(ColumnFunctionDialog, self).exec_()
        if result == QtWidgets.QDialog.Accepted:
            if self.checkable:
                l = []
                for i in range(self.ui.list_functions.count()):
                    item = self.ui.list_functions.item(i)
                    if self.ui.list_functions.itemWidget(item).checkState():
                        l.append(item.data(QtCore.Qt.UserRole))
                return l
            else:
                value = utf8(self.ui.edit_value_1.text())
                escaped_value = value.replace("'", "\'")
                columns = [x.data(QtCore.Qt.UserRole) for x
                           in self.ui.widget_selection.selectedItems()]

                if self._auto_label:
                    label = None
                else:
                    label = utf8(self.ui.edit_label.text())
                func = self.function_list[self.ui.list_functions.currentRow()]
                aggr = utf8(self.ui.combo_combine.currentText())
                if aggr == "":
                    aggr = func.default_aggr

                return (func, columns, escaped_value, aggr, label)
        else:
            return None

    @staticmethod
    def set_function(**kwargs):
        dialog = ColumnFunctionDialog(**kwargs)
        dialog.add_function_groups()
        dialog.setVisible(True)

        return dialog.exec_()


class FunctionDialog(QtWidgets.QDialog):
    def __init__(self,
                 columns=None, available_columns=None,
                 function_class=None,
                 function_types=None,
                 value=None,
                 func=None, max_parameters=1,
                 checkable=False, checked=None,
                 edit_label=True, parent=None):

        if columns is None:
            columns = []
        if available_columns is None:
            available_columns = []
        if function_types is None:
            function_types = []
        if checked is None:
            checked = []

        super(FunctionDialog, self).__init__(parent)
        from .ui.addFunctionUi import Ui_FunctionsDialog
        self.ui = Ui_FunctionsDialog()
        self.ui.setupUi(self)

        self.session = get_toplevel_window().Session

        self.ui.widget_selection.setSelectedList(columns, self.session.translate_header)
        self.ui.widget_selection.setAvailableList(
            available_columns, self.session.translate_header)

        max_width = 0
        for x in functions.combine_map:
            max_width = max(max_width, QtWidgets.QLabel(x).sizeHint().width() +
                            QtWidgets.QComboBox().sizeHint().width())
        self.ui.combo_combine.setMaximumWidth(max_width)
        self.ui.combo_combine.setMinimumWidth(max_width)

        self.max_parameters = max_parameters
        self.edit_label = edit_label

        self.checkable = checkable
        self.checked = checked
        self.columns = columns
        self._auto_label = True

        self.function_types = function_types
        self._func = []

        if value:
            self.ui.edit_value_1.setText(utf8(value))

        self.ui.edit_value_1.textChanged.connect(lambda: self.check_gui())
        self.ui.edit_label.textEdited.connect(self.check_label)
        #self.ui.list_functions.currentRowChanged.connect(lambda: self.check_gui())
        self.ui.widget_selection.itemSelectionChanged.connect(self.change_columns)

        self.ui.widget_selection.setMinimumItems(1)

        spacer = self.ui.layout_arguments.itemAt(1).widget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        spacer.setMinimumHeight(self.ui.edit_value_1.sizeHint().height())
        spacer.setMaximumHeight(self.ui.edit_value_1.sizeHint().height())

        if max_parameters == 0:
            self.ui.parameter_box.hide()

        if not available_columns and not columns:
            self.ui.widget_selection.hide()
            #sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
            #sizePolicy.setHorizontalStretch(0)
            #sizePolicy.setVerticalStretch(0)
            #sizePolicy.setHeightForWidth(self.ui.list_functions.sizePolicy().hasHeightForWidth())
            #self.ui.list_functions.setSizePolicy(sizePolicy)

        if not function_class:
            # remove function class selection widget
            widget = self.ui.list_classes
            self.ui.horizontalLayout.removeWidget(widget)
            widget.hide()
            del widget
            self.function_list = self.fill_list(function_types)
            self.ui.list_functions.setCurrentRow(0)
            self.ui.list_functions.setFocus(1)
        else:
            for i, fc in enumerate(function_class):
                group = QtWidgets.QListWidgetItem(fc.get_description())
                self.ui.list_classes.addItem(group)

                l = []
                for attr in [getattr(functions, x) for x in functions.__dict__]:
                    try:
                        if (issubclass(attr, fc) and attr != fc):
                            l.append(attr)
                    except TypeError:
                        # this is raised if attr is not a class, but e.g. a
                        # string
                        pass
                l = sorted(l, key=lambda x: x.get_name())
                self._func.append(l)

            self.ui.list_classes.currentRowChanged.connect(self.set_function_group)
            self.set_function_group(0)

        if func:
            self.select_function(func)

        self.check_gui()

        try:
            self.resize(options.settings.value("functionapply_size"))
        except TypeError:
            pass

    def change_columns(self, *args):
        self.columns = [x.data(QtCore.Qt.UserRole) for x
                        in self.ui.widget_selection.selectedItems()]
        self.check_gui()

    def set_function_group(self, i):
        self.blockSignals(True)

        self.function_list = [x for x in self._func[i] if x._name != "virtual"]
        self.ui.list_functions.clear()
        for x in sorted(self.function_list,
                        key=lambda x: x.get_name(), reverse=True):
            desc = FUNCTION_DESC.get(x._name, "no description available")
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, x.get_name())
            item_widget = FunctionWidget(x, checkable=False)
            item_widget.arguments.hide()
            item.setSizeHint(item_widget.sizeHint())

            self.ui.list_functions.addItem(item)
            self.ui.list_functions.setItemWidget(item, item_widget)

        self.ui.list_classes.setCurrentRow(i)
        self.ui.list_functions.setCurrentRow(0)
        self.blockSignals(False)

    def select_function(self, func):
        self.ui.edit_value_1.setText(func.value)
        self.columns = func.columns
        try:
            row = self.function_list.index(type(func))
            self.ui.list_functions.setCurrentRow(row)
        except ValueError:
            pass
        self.ui.edit_value_1.setText(func.value)
        try:
            ix = func.combine_modes.index(func.aggr)
            self.ui.combo_combine.setCurrentIndex(ix)
        except ValueError:
            pass
        if func._label:
            self.ui.edit_label.setText(func._label)
            self._auto_label = False

    def fill_list(self, function_class):
        if self.function_types:
            func_list = self.function_types
        else:
            func_list = []
            for fc in function_class:
                l = []
                for attr in [getattr(functions, x) for x in functions.__dict__]:
                    try:
                        if (issubclass(attr, fc) and
                            attr != fc and
                            attr._name != "virtual"):
                            l.append(attr)
                    except TypeError:
                        pass
                func_list += sorted(l, key=lambda x: x.get_name())

        widget = self.ui.list_functions
        for x in sorted(func_list, key=lambda x: x.get_name(), reverse=True):
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, x)
            item_widget = FunctionWidget(x)
            item.setSizeHint(item_widget.sizeHint())

            if self.checkable:
                item_widget.setCheckState(QtCore.Qt.Checked if x in self.checked else QtCore.Qt.Unchecked)

            widget.addItem(item)
            widget.setItemWidget(item, item_widget)

        return func_list

    def check_label(self):
        s = utf8(self.ui.edit_label.text())
        if self._auto_label:
            self._auto_label = False
        elif not s:
            self._auto_label = True

    def check_gui(self, func=None, only_label=False):
        self.ui.parameter_box.setEnabled(self.max_parameters > 0)
        self.ui.box_combine.setEnabled(len(self.columns) > 1)

        if not self.edit_label:
            self.ui.widget_label.hide()
        else:
            self.ui.widget_label.show()

        func = self.function_list[self.ui.list_functions.currentRow()]
        if not only_label:
            current_combine = str(self.ui.combo_combine.currentText())
            self.ui.combo_combine.clear()
            for x in func.combine_modes:
                self.ui.combo_combine.addItem(x)
            if current_combine in func.combine_modes:
                self.ui.combo_combine.setCurrentIndex(func.combine_modes.index(current_combine))
            else:
                self.ui.combo_combine.setCurrentIndex(0)

            self.ui.parameter_box.setEnabled(True)
            self.ui.edit_value_2.show()
            self.ui.label_argument_2.show()

            if func.parameters < 2:
                self.ui.edit_value_2.hide()
                self.ui.label_argument_2.hide()
            if func.parameters < 1:
                self.ui.parameter_box.setEnabled(False)

            if func.parameters == 0 or self.max_parameters == 0:
                self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
                self.ui.edit_value_1.setStyleSheet('QLineEdit { background-color: white; }')
            else:
                if not func.validate_input(utf8(self.ui.edit_value_1.text())):
                    self.ui.edit_value_1.setStyleSheet('QLineEdit { background-color: rgb(255, 255, 192) }')
                    self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
                else:
                    self.ui.edit_value_1.setStyleSheet('QLineEdit { background-color: white; }')
                    self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

        aggr = str(self.ui.combo_combine.currentText())
        if aggr == "":
            aggr = func.default_aggr

        session = get_toplevel_window().Session
        tmp_func = func(
            columns=self.columns,
            value=utf8(self.ui.edit_value_1.text()),
            aggr=aggr,
            session=session)

        if self._auto_label:
            try:
                manager = managers.get_manager(options.cfg.MODE, session.Resource.name)
            except AttributeError:
                pass
            else:
                # only set the auto label if a manager is available
                self.ui.edit_label.setText(tmp_func.get_label(session=session, manager=manager))

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        options.settings.setValue("functionapply_size", self.size())

    def exec_(self):
        result = super(FunctionDialog, self).exec_()
        if result == QtWidgets.QDialog.Accepted:
            if self.checkable:
                l = []
                for i in range(self.ui.list_functions.count()):
                    item = self.ui.list_functions.item(i)
                    if self.ui.list_functions.itemWidget(item).checkState():
                        l.append(item.data(QtCore.Qt.UserRole))
                return l
            else:
                value = utf8(self.ui.edit_value_1.text())
                escaped_value = value.replace("'", "\'")
                columns = [x.data(QtCore.Qt.UserRole) for x
                           in self.ui.widget_selection.selectedItems()]

                if self._auto_label:
                    label = None
                else:
                    label = utf8(self.ui.edit_label.text())
                func = self.function_list[self.ui.list_functions.currentRow()]
                aggr = utf8(self.ui.combo_combine.currentText())
                if aggr == "":
                    aggr = func.default_aggr

                return (func, columns, escaped_value, aggr, label)
        else:
            return None

    @staticmethod
    def set_function(columns, **kwargs):
        dialog = FunctionDialog(columns=columns, **kwargs)
        dialog.setVisible(True)

        return dialog.exec_()

    @staticmethod
    def edit_function(func, parent=None, **kwargs):
        return FunctionDialog.set_function(
            columns=func.columns,
            value=func.value)

        #dialog = FunctionDialog(func=func, parent=parent, **kwargs)
        #dialog.setVisible(True)
        #return dialog.exec_()

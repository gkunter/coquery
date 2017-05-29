# -*- coding: utf-8 -*-
"""
functionapply.py is part of Coquery.

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
from coquery.defines import *
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window
from .ui.addFunctionUi import Ui_FunctionsDialog
from .classes import CoqListItem

class FunctionItem(QtWidgets.QWidget):
    def __init__(self, func, checkable=True, *args, **kwargs):
        super(FunctionItem, self).__init__(*args, **kwargs)
        self.checkable = checkable

        name = func.get_name()
        desc = FUNCTION_DESC.get(func._name, "(no description available)")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.outerLayout = QtWidgets.QHBoxLayout(self)
        self.outerLayout.setContentsMargins(4, 2, 4, 2)
        self.outerLayout.setSpacing(4)

        if checkable:
            self.checkbox = QtWidgets.QCheckBox()
        self.innerLayout = QtWidgets.QVBoxLayout()
        self.innerLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
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

        if checkable:
            self.outerLayout.addWidget(self.checkbox)
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

    def sizeHint(self):
        size_hint = self.innerLayout.sizeHint()
        if self.checkable:
            height = max(size_hint.height(),
                        QtWidgets.QLabel().sizeHint().height(),
                        QtWidgets.QCheckBox().sizeHint().height(),
                        self.innerLayout.sizeHint().height() * 1.1)
        else:
            height = max(size_hint.height(),
                        QtWidgets.QLabel().sizeHint().height(),
                        self.innerLayout.sizeHint().height() * 1.1)

        size_hint.setHeight(height)
        return size_hint

class FunctionDialog(QtWidgets.QDialog):
    def __init__(self, columns=None, available_columns=None,
                 function_class=None,
                 function_types=None,
                 func=None, max_parameters=1, checkable=False, checked=None,
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
        self.ui.edit_function_value.textChanged.connect(lambda: self.check_gui())
        self.ui.edit_label.textEdited.connect(self.check_label)

        self.function_types = function_types
        self._func = []

        self.ui.list_functions.currentRowChanged.connect(lambda: self.check_gui())

        self.ui.widget_selection.itemSelectionChanged.connect(self.change_columns)
        self.ui.widget_selection.setMinimumItems(1)

        if max_parameters == 0:
            self.ui.parameter_box.hide()

        if not available_columns and not columns:
            self.ui.widget_selection.hide()
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.ui.list_functions.sizePolicy().hasHeightForWidth())
            self.ui.list_functions.setSizePolicy(sizePolicy)

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
                group = CoqListItem(fc.get_description())
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
        self.function_list = [x for x in self._func[i] if x._name != "virtual"]
        self.ui.list_functions.blockSignals(True)
        self.ui.list_classes.blockSignals(True)
        self.ui.list_functions.clear()
        for x in sorted(self.function_list,
                        key=lambda x: x.get_name(), reverse=True):
            desc = FUNCTION_DESC.get(x._name, "no description available")
            item = CoqListItem()
            item.setData(QtCore.Qt.UserRole, x.get_name())
            item_widget = FunctionItem(x, checkable=False)
            item.setSizeHint(item_widget.sizeHint())
            item.setObjectName(x)

            self.ui.list_functions.addItem(item)
            self.ui.list_functions.setItemWidget(item, item_widget)

        self.ui.list_classes.setCurrentRow(i)
        self.ui.list_functions.blockSignals(False)
        self.ui.list_classes.blockSignals(False)
        self.ui.list_functions.setCurrentRow(0)

    def select_function(self, func):
        self.columns = func.columns()
        try:
            row = self.function_list.index(type(func))
            self.ui.list_functions.setCurrentRow(row)
        except ValueError:
            pass
        self.ui.edit_function_value.setText(func.value)
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
            item = CoqListItem()
            item.setData(QtCore.Qt.UserRole, x)
            item_widget = FunctionItem(x)
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

            if func.parameters == 0 or self.max_parameters == 0:
                self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
                self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: white; }')
            else:
                if not func.validate_input(utf8(self.ui.edit_function_value.text())):
                    self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: rgb(255, 255, 192) }')
                    self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
                else:
                    self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: white; }')
                    self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

            self.ui.list_functions.item(self.ui.list_functions.currentRow()).setSelected(True)

        aggr = str(self.ui.combo_combine.currentText())
        if aggr == "":
            aggr = func.default_aggr

        session = get_toplevel_window().Session
        tmp_func = func(
            columns=self.columns,
            value=utf8(self.ui.edit_function_value.text()),
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
                value = utf8(self.ui.edit_function_value.text())
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
        dialog = FunctionDialog(func=func, parent=parent, **kwargs)
        dialog.setVisible(True)

        return dialog.exec_()

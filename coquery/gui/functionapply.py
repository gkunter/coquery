# -*- coding: utf-8 -*-
"""
functionapply.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

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
from .pyqt_compat import QtCore, QtGui
from .ui.addFunctionUi import Ui_FunctionsDialog
from .classes import CoqListItem

class FunctionDialog(QtGui.QDialog):
    def __init__(self, columns=[], available_columns=[],
                 function_class=[], 
                 function_types=None,
                 func=None, max_parameters=1, checkable=False, checked=[],
                 edit_label=True, parent=None):
        super(FunctionDialog, self).__init__(parent)
        self.ui = Ui_FunctionsDialog()
        self.ui.setupUi(self)

        self.ui.button_up.setIcon(options.cfg.main_window.get_icon("sign-up"))
        self.ui.button_down.setIcon(options.cfg.main_window.get_icon("sign-down"))
        self.ui.button_add.setIcon(options.cfg.main_window.get_icon("sign-left"))
        self.ui.button_remove.setIcon(options.cfg.main_window.get_icon("sign-right"))

        self.session = options.cfg.main_window.Session
        for x in available_columns:
            item = CoqListItem(self.session.translate_header(x))
            item.setObjectName(x)
            self.ui.list_available_columns.addItem(item)        
        for x in columns:
            item = CoqListItem(self.session.translate_header(x))
            item.setObjectName(x)
            self.ui.list_selected_columns.addItem(item)        

        max_width = 0
        for x in functions.combine_map:
            max_width = max(max_width, QtGui.QLabel(x).sizeHint().width() + 
                            QtGui.QComboBox().sizeHint().width())
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

        self.ui.button_add.clicked.connect(self.add_selected)
        self.ui.button_remove.clicked.connect(self.remove_selected)
        self.ui.button_up.clicked.connect(self.selected_up)
        self.ui.button_down.clicked.connect(self.selected_down)

        self.function_types = function_types
        self._func = []

        self.ui.list_functions.currentRowChanged.connect(lambda: self.check_gui())

        if max_parameters == 0:
            self.ui.parameter_box.hide()
        
        if available_columns == []:
            self.ui.widget_column_select.hide()
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.ui.list_functions.sizePolicy().hasHeightForWidth())
            self.ui.list_functions.setSizePolicy(sizePolicy)

        if function_class == []:
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

    def set_function_group(self, i):
        self.function_list = self._func[i]
        self.ui.list_functions.blockSignals(True)
        self.ui.list_classes.blockSignals(True)
        self.ui.list_functions.clear()
        for x in self.function_list:
            desc = FUNCTION_DESC.get(x._name, "no description available")
            item = CoqListItem("{} – {}".format(x.get_name(), desc))
            item.setObjectName(x)
            self.ui.list_functions.addItem(item)
        self.ui.list_classes.setCurrentRow(i)
        self.ui.list_functions.blockSignals(False)
        self.ui.list_classes.blockSignals(False)
        self.ui.list_functions.setCurrentRow(0)

    def add_selected(self):
        selected = self.ui.list_available_columns.selectedItems()
        for x in selected:
            i = self.ui.list_available_columns.row(x)
            self.ui.list_available_columns.takeItem(i)
            self.ui.list_selected_columns.insertItem(self.ui.list_selected_columns.count(), x)
            self.columns.append(x.objectName())
        self.check_gui()
        
    def remove_selected(self):
        selected = self.ui.list_selected_columns.selectedItems()
        for x in selected:
            i = self.ui.list_selected_columns.row(x)
            self.ui.list_selected_columns.takeItem(i)
            self.ui.list_available_columns.insertItem(self.ui.list_available_columns.count(), x)
            self.columns.remove(x.objectName())
        self.check_gui()
        
    def selected_up(self):
        pass
    
    def selected_down(self):
        pass
    
    def select_function(self, func):
        self.columns = func.columns
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
        if func.label:
            self.ui.edit_label.setText(func.label)
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
        for x in func_list:
            desc = FUNCTION_DESC.get(x._name, "no description available")
            item = CoqListItem("{} – {}".format(x.get_name(), desc))
            item.setObjectName(x)
            if self.checkable:
                item.setCheckState(QtCore.Qt.Checked if x in self.checked else QtCore.Qt.Unchecked)
                item.setData(QtCore.Qt.UserRole, x)
            widget.addItem(item)
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
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
                self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: white; }')
            else:
                if not func.validate_input(utf8(self.ui.edit_function_value.text())):
                    self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: rgb(255, 255, 192) }')
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
                else:
                    self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: white; }')
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)

            self.ui.list_functions.item(self.ui.list_functions.currentRow()).setSelected(True)
    
        aggr = str(self.ui.combo_combine.currentText())
        if aggr == "":
            aggr = func.default_aggr
        
        session = options.cfg.main_window.Session
        tmp_func = func(
            columns = self.columns,
            value = utf8(self.ui.edit_function_value.text()),
            aggr = aggr,
            session = session)
        
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
        if result == QtGui.QDialog.Accepted:
            if self.checkable:
                l = []
                for i in range(self.ui.list_functions.count()):
                    if self.ui.list_functions.item(i).checkState():
                        l.append(self.ui.list_functions.item(i).objectName())
                        #l.append(self.function_list[i])
                return l
            else:
                value = utf8(self.ui.edit_function_value.text())
                escaped = value.replace("'", "\'")
                
                if self._auto_label:
                    label = None
                else:
                    label = utf8(self.ui.edit_label.text())
                func = self.function_list[self.ui.list_functions.currentRow()]
                aggr = utf8(self.ui.combo_combine.currentText())
                if aggr == "":
                    aggr = func.default_aggr

                return (func, escaped, aggr, label)
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

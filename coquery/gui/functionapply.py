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
from .pyqt_compat import QtCore, QtGui
from .ui.addFunctionUi import Ui_FunctionsDialog

class FunctionDialog(QtGui.QDialog):
    def __init__(self, table, feature, columns=[], function_class=functions.StringFunction, func=None, parent=None):
        super(FunctionDialog, self).__init__(parent)
        self.ui = Ui_FunctionsDialog()
        self.ui.setupUi(self)
        self.function_list = self.fill_list(function_class)
        self.ui.list_functions.setCurrentRow(0)
        self.columns = columns
        self._auto_label = True
        self.ui.list_functions.currentItemChanged.connect(lambda: self.check_gui())
        self.ui.edit_function_value.textChanged.connect(lambda: self.check_gui())
        self.ui.edit_label.textEdited.connect(self.check_label)
        
        if func:
            self.select_function(func)
        
        self.set_header(self.columns)
        self.check_gui()
        self.ui.list_functions.setFocus(1)
                
        try:
            self.resize(options.settings.value("functionapply_size"))
        except TypeError:
            pass

    def set_header(self, columns):
        session = options.cfg.main_window.Session
        self.ui.label_description.setText(
            self.ui.label_description.text().format(
                ", ".join([session.translate_header(x) for x in columns])))

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
        l = self.ui.list_functions
        func_list = []
        for attr in [getattr(functions, x) for x in functions.__dict__]:
            try:
                if (issubclass(attr, function_class) and attr != function_class):
                    func_list.append(attr)
            except TypeError:
                pass
        func_list= sorted(func_list, key=lambda x: x.get_name())
        for x in func_list:
            l.insertItem(
                l.count(), 
                QtGui.QListWidgetItem("{} – {}".format(x.get_name(), "no description")))
        return func_list

    def check_label(self):
        s = str(self.ui.edit_label.text())
        if self._auto_label:
            self._auto_label = False
        elif not s:
            self._auto_label = True

    def check_gui(self, func=None, only_label=False):
        func = self.function_list[self.ui.list_functions.currentRow()]
        if not only_label:
            if len(self.columns) == 1:
                self.ui.box_combine.setDisabled(True)
                self.ui.label_remark.show()
            else:
                self.ui.label_remark.hide()
            
            current_combine = str(self.ui.combo_combine.currentText())
            self.ui.combo_combine.clear()
            for x in func.combine_modes:
                self.ui.combo_combine.addItem(x)
            if current_combine in func.combine_modes:
                self.ui.combo_combine.setCurrentIndex(func.combine_modes.index(current_combine))
            else:
                self.ui.combo_combine.setCurrentIndex(0)
            
            if func.parameters == 0:
                self.ui.parameter_box.setDisabled(True)
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
                self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: white; }')
            else:
                self.ui.parameter_box.setEnabled(True)
                if (str(self.ui.edit_function_value.text()) == "" and not func.allow_null):
                    self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: rgb(255, 255, 192) }')
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
                else:
                    self.ui.edit_function_value.setStyleSheet('QLineEdit { background-color: white; }')
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)

            self.ui.list_functions.item(self.ui.list_functions.currentRow()).setSelected(True)
    
        aggr = str(self.ui.combo_combine.currentText())
        if aggr == "":
            aggr = func.default_aggr
            
        tmp_func = func(
            columns = self.columns,
            value = str(self.ui.edit_function_value),
            aggr = aggr)
        
        if self._auto_label:
            self.ui.edit_label.setText(tmp_func.get_label(session=options.cfg.main_window.Session))

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        options.settings.setValue("functionapply_size", self.size())

    def exec_(self):
        result = super(FunctionDialog, self).exec_()
        if result == QtGui.QDialog.Accepted:

            value = self.ui.edit_function_value.text()
            escaped = str(value).replace("\\", "\\\\")
            escaped = escaped.replace("'", "\\'")
            escaped = escaped.replace("{", "{{")
            escaped = escaped.replace("}", "}}")
            
            if self._auto_label:
                label = None
            else:
                label = str(self.ui.edit_label.text())
            func = self.function_list[self.ui.list_functions.currentRow()]
            aggr = str(self.ui.combo_combine.currentText())
            if aggr == "":
                aggr = func.default_aggr

            return (func, escaped, aggr, label)
        else:
            return None

    @staticmethod
    def set_function(columns, function_class=None, parent=None):
        dialog = FunctionDialog("", "", columns=columns, function_class=function_class, parent=parent)
        dialog.setVisible(True)
        
        return dialog.exec_()
        
    @staticmethod
    def edit_function(func, parent=None):
        dialog = FunctionDialog("", "", func=func, parent=parent)
        dialog.setVisible(True)
        
        return dialog.exec_()

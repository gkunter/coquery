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

import sys
import re

from coquery import options
from .pyqt_compat import QtCore, QtGui
from .ui.functionApplyUi import Ui_FunctionDialog

def func_regexp(x, s):
    try:
        start, end = re.search("({})".format(s), x).span()
    except AttributeError:
        return ""
    else:
        return x[start:end]

def func_match(x, s):
    if re.search("{}".format(s), x):
        return "yes"
    else:
        return "no"

class FunctionDialog(QtGui.QDialog):
    def __init__(self, table, feature, parent=None):
        
        super(FunctionDialog, self).__init__(parent)
        self.ui = Ui_FunctionDialog()
        self.ui.setupUi(self)
        try:
            table = str(table)
        except:
            table = "Linked table"
        self.ui.label_description.setText(str(self.ui.label_description.text()).format(str(table), str(feature)))

        self.ui.label_func1.setText(str(self.ui.label_func1.text()).format("{}.{}".format(table, feature)))
        self.ui.label_func2.setText(str(self.ui.label_func2.text()).format("{}.{}".format(table, feature)))
        self.ui.label_func3.setText(str(self.ui.label_func3.text()).format("{}.{}".format(table, feature)))
        self.ui.label_func4.setText(str(self.ui.label_func4.text()).format("{}.{}".format(table, feature)))
        
        try:
            self.resize(options.settings.value("functionapply_size"))
        except TypeError:
            pass

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        options.settings.setValue("functionapply_size", self.size())
        
    @staticmethod
    def display(table, feature, parent=None):
        
        dialog = FunctionDialog(table, feature, parent=parent)        
        dialog.setVisible(True)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            value = dialog.ui.edit_function_value.text()
            escaped = str(value).replace("\\", "\\\\")
            escaped = escaped.replace("'", "\\'")

            if dialog.ui.radio_count.isChecked():
                label = "COUNT('{}', {})".format(escaped, feature)
                FUN = lambda x: x.count(value)
            elif dialog.ui.radio_length.isChecked():
                label = "LENGTH({})".format(feature)
                FUN = lambda x: len(x)
            elif dialog.ui.radio_match.isChecked():
                label = "MATCH('{}', {})".format(escaped, feature)
                FUN = lambda x: func_match(x, value)
            elif dialog.ui.radio_regexp.isChecked():
                label = "REGEXP('{}', {})".format(escaped, feature)
                FUN = lambda x: func_regexp(x, value)
            return label, FUN
        else:
            return None

def main():
    app = QtGui.QApplication(sys.argv)
    viewer = FunctionDialog("Word", "Transcript")
    viewer.exec_()
    
    
if __name__ == "__main__":
    main()
    
from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui

import sys
import re
import functionApplyUi

try:
    import options
except ImportError:
    pass

def func_regexp(x, s):
    match = re.search("({})".format(s), x)
    if match:
        return match.group(1)
    else:
        return ""

def func_match(x, s):
    match = re.search("({})".format(s), x)
    if match:
        return "yes"
    else:
        return "no"

class FunctionDialog(QtGui.QDialog):
    def __init__(self, table, feature, parent=None):
        
        super(FunctionDialog, self).__init__(parent)
        self.omit_tables = ["coquery", "corpus"]
        self.ui = functionApplyUi.Ui_FunctionDialog()
        self.ui.setupUi(self)
        self.ui.label_description.setText(str(self.ui.label_description.text()).format(table, feature))

        self.ui.label_func1.setText(str(self.ui.label_func1.text()).format("{}.{}".format(table, feature)))
        self.ui.label_func2.setText(str(self.ui.label_func2.text()).format("{}.{}".format(table, feature)))
        self.ui.label_func3.setText(str(self.ui.label_func3.text()).format("{}.{}".format(table, feature)))
        self.ui.label_func4.setText(str(self.ui.label_func4.text()).format("{}.{}".format(table, feature)))
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
            
    def closeEvent(self, *args):
        try:
            options.cfg.function_apply_height = self.height()
            options.cfg.function_apply_width = self.width()        
        except NameError:
            pass
        
    @staticmethod
    def display(table, feature, parent=None):
        
        dialog = FunctionDialog(table, feature, parent=parent)        
        dialog.setVisible(True)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            value = dialog.ui.edit_function_value.text()
            if dialog.ui.radio_count.isChecked():
                label = "COUNT('{}', {})".format(value, feature)
                FUN = lambda x: x.count(value)
            elif dialog.ui.radio_length.isChecked():
                label = "LENGTH({})".format(feature)
                FUN = lambda x: len(x)
            elif dialog.ui.radio_match.isChecked():
                label = "MATCH('{}', {})".format(value, feature)
                FUN = lambda x: func_match(x, value)
            elif dialog.ui.radio_regexp.isChecked():
                label = "REGEXP('{}', {})".format(value, feature)
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
    
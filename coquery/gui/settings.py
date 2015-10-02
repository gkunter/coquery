# -*- coding: utf-8 -*-
"""
settings.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from pyqt_compat import QtGui, QtCore
import settingsUi

class Settings(QtGui.QDialog):
    def __init__(self, options, parent=None):
        super(Settings, self).__init__(parent)
        self.options = options
        self.ui = settingsUi.Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.ui.check_ignore_punctuation.setEnabled(False)
        
    def set_ui_options(self):
        try:
            self.ui.check_ignore_case.setChecked(not options.case_sensitive)
        except AttributeError:
            pass
        try:
            self.ui.check_ignore_punctuation.setChecked(options.ignore_punctuation)
        except AttributeError:
            pass
        try:
            self.ui.check_experimental.setChecked(not options.experimental)
        except AttributeError:
            pass
        try:
            self.ui.spin_digits.setValue(not options.digits)
        except AttributeError:
            pass
        try:
            self.ui.edit_installer_path.setText(options.installer_path)
        except AttributeError:
            pass
        try:
            self.ui.edit_visualizer_path.setText(options.visualizer_path)
        except AttributeError:
            pass
        try:
            self.ui.check_ask_on_quit.setChecked(options.ask_on_quit)
        except AttributeError:
            pass
        

    @staticmethod
    def manage(options, parent=None):
        dialog = Settings(options, parent)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            dialog.change_options()
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
def main():
    app = QtGui.QApplication(sys.argv)
    print(Settings.manage(None))
    
if __name__ == "__main__":
    main()
    
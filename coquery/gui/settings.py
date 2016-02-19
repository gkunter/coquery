# -*- coding: utf-8 -*-
"""
settings.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import sys

from pyqt_compat import QtGui, QtCore
from ui.settingsUi import Ui_SettingsDialog

import options

class Settings(QtGui.QDialog):
    def __init__(self, _options, parent=None):
        super(Settings, self).__init__(parent)
        self._options = _options
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        #self.ui.check_ignore_punctuation.setEnabled(False)
        #self.ui.check_experimental.setEnabled(False)
        self.ui.edit_visualizer_path.setEnabled(False)
        self.ui.button_visualizer_path.setEnabled(False)
        
        self.ui.button_installer_path.clicked.connect(self.select_installer_path)                                        
        self.ui.button_visualizer_path.clicked.connect(self.select_visualizer_path)                                        
        
        self.set_ui_options()
        try:
            self.resize(options.settings.value("settings_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("settings_size", self.size())
        
    def select_installer_path(self):
        name = QtGui.QFileDialog.getExistingDirectory(options=QtGui.QFileDialog.ReadOnly|QtGui.QFileDialog.ShowDirsOnly|QtGui.QFileDialog.HideNameFilterDetails)
        if type(name) == tuple:
            name = name[0]
        if name:
            self.options.custom_installer_path = name
            self.ui.edit_installer_path.setText(name)
        
    def select_visualizer_path(self):
        name = QtGui.QFileDialog.getExistingDirectory(options=QtGui.QFileDialog.ReadOnly|QtGui.QFileDialog.ShowDirsOnly|QtGui.QFileDialog.HideNameFilterDetails)
        if type(name) == tuple:
            name = name[0]
        if name:
            self.options.visualizer_path = name
            self.ui.edit_visualizer_path.setText(name)

    def set_ui_options(self):
        try:
            self.ui.check_ignore_case.setChecked(not bool(self.options.case_sensitive))
        except AttributeError:
            pass
        #try:
            #self.ui.check_reaggregate_data.setChecked(bool(self.options.reaggregate_data))
        #except AttributeError:
            #pass
        #try:
            #self.ui.check_server_side.setChecked(bool(self.options.server_side))
        #except AttributeError:
            #pass
        #try:
            #self.ui.check_ignore_punctuation.setChecked(bool(self.options.ignore_punctuation))
        #except AttributeError:
            #pass
        #try:
            #self.ui.check_experimental.setChecked(bool(self.options.experimental))
        #except AttributeError:
            #pass
        try:
            self.ui.check_align_quantified.setChecked(bool(self.options.align_quantified))
        except AttributeError:
            pass
        try:
            self.ui.spin_digits.setValue(int(self.options.digits))
        except AttributeError:
            pass
        try:
            self.ui.edit_installer_path.setText(self.options.custom_installer_path)
        except AttributeError:
            pass
        try:
            self.ui.edit_visualizer_path.setText(self.options.visualizer_path)
        except AttributeError:
            pass
        try:
            self.ui.check_ask_on_quit.setChecked(bool(self.options.ask_on_quit))
        except AttributeError:
            pass
        try:
            self.ui.check_save_query_string.setChecked(bool(self.options.save_query_string))
        except AttributeError:
            pass
        try:
            self.ui.check_save_query_file.setChecked(bool(self.options.save_query_file))
        except AttributeError:
            pass

    def change_options(self):
        self.options.case_sensitive = not bool(self.ui.check_ignore_case.isChecked())
        #self.options.reaggregate_data = bool(self.ui.check_reaggregate_data.isChecked())
        #self.options.server_side= bool(self.ui.check_server_side.isChecked())
        #self.options.ignore_punctuation = bool(self.ui.check_ignore_punctuation.isChecked())
        #self.options.experimental = bool(self.ui.check_experimental.isChecked())
        self.options.align_quantified = bool(self.ui.check_align_quantified.isChecked())
        self.options.ask_on_quit = bool(self.ui.check_ask_on_quit.isChecked())
        self.options.save_query_file = bool(self.ui.check_save_query_file.isChecked())
        self.options.save_query_string = bool(self.ui.check_save_query_string.isChecked())
        self.options.digits = int(self.ui.spin_digits.value())
        self.options.custom_installer_path = str(self.ui.edit_installer_path.text())        

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
    
# -*- coding: utf-8 -*-
"""
createuser.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import sys

from coquery import options
from .pyqt_compat import QtCore, QtGui
from .ui.createUserUi import Ui_CreateUser

class CreateUser(QtGui.QDialog):
    def __init__(self, name=None, password=None, parent=None):
        
        super(CreateUser, self).__init__(parent)
        
        self.ui = Ui_CreateUser()
        self.ui.setupUi(self)

        if name:
            self.ui.new_name.setText(name)
        if password:
            self.ui.new_password.setText(password)
        
        self.ui.new_password.textChanged.connect(self.check_password)
        self.ui.new_password_check.textChanged.connect(self.check_password)

        self.ui.root_name.textChanged.connect(self.check_okay)
        self.ui.root_password.textChanged.connect(self.check_okay)

        self.ui.check_show_passwords.stateChanged.connect(self.toggle_passwords)

        self.check_password()

        try:
            self.resize(options.settings.value("createuser_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("createuser_size", self.size())

    def check_okay(self):
        if not self.ui.root_name.text() or not self.ui.root_password.text() or self.ui.new_password.text() != self.ui.new_password_check.text():
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)

    def check_password(self):
        """
        Check if the two new passwords are identical.
        """
        if self.ui.new_password.text() != self.ui.new_password_check.text():
            self.ui.new_password.setStyleSheet('QLineEdit {background-color: lightyellow; }')
            self.ui.new_password_check.setStyleSheet('QLineEdit {background-color: lightyellow; }')
        else:
            self.ui.new_password.setStyleSheet("")
            self.ui.new_password_check.setStyleSheet("")
        self.check_okay()
    
    def toggle_passwords(self):
        if self.ui.check_show_passwords.checkState():
            self.ui.root_password.setEchoMode(QtGui.QLineEdit.Normal)
            self.ui.new_password.setEchoMode(QtGui.QLineEdit.Normal)
            self.ui.new_password_check.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.ui.root_password.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
            self.ui.new_password.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
            self.ui.new_password_check.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
            
    @staticmethod
    def get(name=None, password=None, parent=None):
        dialog = CreateUser(name, password, parent=parent)
        result = dialog.exec_()
        if result:
            root_name = str(dialog.ui.root_name.text())
            root_password = str(dialog.ui.root_password.text())
            name = str(dialog.ui.new_name.text())
            password = str(dialog.ui.new_password.text())
            return (root_name, root_password, name, password)
        else:
            return None

def main():
    app = QtGui.QApplication(sys.argv)
    credentials = CreateUser.get("coquery", "fun")
    if credentials:
        print(credentials)
if __name__ == "__main__":
    main()
    

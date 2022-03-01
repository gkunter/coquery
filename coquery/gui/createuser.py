# -*- coding: utf-8 -*-
"""
createuser.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from PyQt5 import QtCore, QtWidgets

from coquery import options
from coquery.gui.pyqt_compat import STYLE_WARN
from coquery.gui.ui.createUserUi import Ui_CreateUser


class CreateUser(QtWidgets.QDialog):
    def __init__(self, name=None, password=None, parent=None):
        
        super(CreateUser, self).__init__(parent)
        
        self.ui = Ui_CreateUser()
        self.ui.setupUi(self)

        self.ui.new_password.setFocus(True)

        if name:
            self.ui.new_name.setText(name)
        if password:
            self.ui.new_password.setText(password)
        
        self.toggle_passwords()

        self.ui.new_password.textChanged.connect(self.check_password)
        self.ui.new_password_check.textChanged.connect(self.check_password)

        self.ui.root_name.textChanged.connect(self.check_okay)
        self.ui.root_password.textChanged.connect(self.check_okay)

        self.ui.check_show_passwords.stateChanged.connect(
            self.toggle_passwords)

        self.check_password()

        try:
            self.resize(options.settings.value("createuser_size"))
        except (TypeError, AttributeError):
            pass

    def closeEvent(self, event):
        options.settings.setValue("createuser_size", self.size())

    def check_okay(self):
        new_pwd = self.ui.new_password.text()
        new_pwd_check = self.ui.new_password_check.text()
        check = (self.ui.root_name.text() != "" and new_pwd == new_pwd_check)
        ok_button = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        ok_button.setEnabled(check)

    def check_password(self):
        """
        Check if the two new passwords are identical.
        """
        new_pwd = self.ui.new_password.text()
        new_pwd_check = self.ui.new_password_check.text()
        if new_pwd != new_pwd_check:
            self.ui.new_password.setStyleSheet(STYLE_WARN)
            self.ui.new_password_check.setStyleSheet(STYLE_WARN)
        else:
            self.ui.new_password.setStyleSheet("")
            self.ui.new_password_check.setStyleSheet("")
        self.check_okay()
    
    def toggle_passwords(self):
        if self.ui.check_show_passwords.checkState():
            echo_mode = QtWidgets.QLineEdit.Normal
        else:
            echo_mode = QtWidgets.QLineEdit.PasswordEchoOnEdit

        self.ui.root_password.setEchoMode(echo_mode)
        self.ui.new_password.setEchoMode(echo_mode)
        self.ui.new_password_check.setEchoMode(echo_mode)

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
            return root_name, root_password, name, password
        else:
            return None


def main():
    app = QtWidgets.QApplication(sys.argv)
    credentials = CreateUser.get("coquery", "")
    if credentials:
        print(credentials)


if __name__ == "__main__":
    main()

from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
import argparse
import MySQLOptionsUi
import mysql_guide
import sys
sys.path.append("/home/kunibert/Dev/coquery/coquery")
import sqlwrap
from errors import *
import socket
import re
import string

def check_valid_host(s):
    def is_valid_ipv4_address(address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError: 
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:
            return False
        return True

    def is_valid_ipv6_address(address):
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True

    def is_valid_hostname(s):
        if len(s) > 255:
            return False
        # strings must contain at least one letter, otherwise they should be
        # considered ip addresses
        if not any([x in string.letters for x in s]):
            return
        if s.endswith("."):
            s= s[:-1] # strip exactly one dot from the right, if present
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in s.split("."))

    if is_valid_ipv6_address(s):
        return True
    if is_valid_ipv4_address(s):
        return True
    if is_valid_hostname(s):
        return True
    return False

class MySQLOptions(QtGui.QDialog):
    def __init__(self, host="localhost", port=3306, user="mysql", password="mysql", parent=None):
        
        super(MySQLOptions, self).__init__(parent)
        
        self.ui = MySQLOptionsUi.Ui_Dialog()
        self.ui.setupUi(self)
        if host == "localhost" or host == "127.0.0.1":
            self.ui.radio_local.setChecked(True)
        else:
            self.ui.radio_remote.setChecked(True)
            self.ui.hostname.setText(host)
        self.ui.user.setText(user)
        self.ui.password.setText(password)
        self.ui.port.setValue(port)
        self.check_connection()
        
        self.ui.hostname.textChanged.connect(self.check_connection)
        self.ui.user.textChanged.connect(self.check_connection)
        self.ui.password.textChanged.connect(self.check_connection)
        self.ui.port.valueChanged.connect(self.check_connection)
        self.ui.radio_local.clicked.connect(self.check_connection)
        self.ui.radio_remote.clicked.connect(self.check_connection)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Help).clicked.connect(self.start_mysql_guide)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Help).setText("MySQL server guide...")

    def check_connection(self):
        """ Check if a connection to a MySQL server can be established using
        the settings from the GUI. Return True if a connection can be
        established, or True if not. Also, set up the connection indicator
        accordingly."""
        def indicate_no_connection(self, s):
            self.ui.label_connection.setText("Not connected: {}".format(e))
            self.ui.button_status.setStyleSheet('QPushButton {background-color: red; color: red;}')
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Help).setEnabled(True)
        
        def indicate_connection(self):
            self.ui.button_status.setStyleSheet('QPushButton {background-color: green; color: green;}')
            self.ui.label_connection.setText("Connected ({})".format(x[0]))
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Help).setEnabled(False)
        
        if self.ui.radio_local.isChecked():
            hostname = "localhost"
            self.ui.hostname.setDisabled(True)
        else:
            self.ui.hostname.setDisabled(False)
            hostname = str(self.ui.hostname.text())

        if check_valid_host(hostname):
            try:
                DB = sqlwrap.SqlDB(
                    hostname,
                    self.ui.port.value(),
                    str(self.ui.user.text()),
                    str(self.ui.password.text()))
                DB.Cur.execute("SELECT VERSION()")
                x = DB.Cur.fetchone()
                DB.close()
            except SQLInitializationError as e:
                indicate_no_connection(self, e)
                return False
            else:
                indicate_connection(self)
                return True
        else:
            indicate_no_connection(self, "Invalid hostname or invalid IP address")
            return False
        
    def start_mysql_guide(self):
        mysql_guide.MySqlGuide(self)
        
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()
            
    @staticmethod
    def set(db_host, db_port, db_user, db_password, parent=None):
        dialog = MySQLOptions(db_host, db_port, db_user, db_password, parent=parent)
        result = dialog.exec_()
        if result:
            namespace = argparse.Namespace()
            namespace.db_user = dialog.ui.user.text()
            namespace.db_password = dialog.ui.password.text()
            if dialog.ui.radio_remote.isChecked():
                namespace.db_host = dialog.ui.hostname.text()
            else:
                namespace.db_host = "localhost"
            namespace.db_port = dialog.ui.port.value()
            return namespace
        else:
            return None

def main():
    app = QtGui.QApplication(sys.argv)
    viewer = MySQLOptions()
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    
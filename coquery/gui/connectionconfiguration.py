# -*- coding: utf-8 -*-
"""
Connectionconfiguration.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import argparse
import socket
import re
import string
import sys
import sqlalchemy

from coquery import sqlhelper
from coquery import options
from coquery.errors import *
from coquery.defines import *

from .pyqt_compat import QtCore, QtGui
from . import classes
from .ui.connectionConfigurationUi import Ui_ConnectionConfig

def check_valid_host(s):
    """
    Check if a string is a valid host name or a valid IP address.
    
    The check involves three steps. First, it is checked if the string
    represents a valid IPv6 address by opening a IP6V socket. Then, the 
    same check is performed for IPv4 adresses. Finally, the string is 
    checked for formal appropriateness as a hostname.
    
    Parameters
    ----------
    s : string
        A string representing either an IP address or a host name
    
    Returns
    -------
    b : bool
        True if the string is valid as a host name or IP address, and False
        otherwise.
    """

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
        except (socket.error, AttributeError):  # not a valid address
            return False
        return True

    def is_valid_hostname(s):
        if len(s) > 255:
            return False
        # strings must contain at least one letter, otherwise they should be
        # considered ip addresses
        if not any([x in string.ascii_letters for x in s]):
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

class CoqFileFilter(QtGui.QSortFilterProxyModel):
    def filterAcceptsRow(self, sourceRow, sourceParent):
        index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
        return False
        return self.sourceModel().isDir(index0)

class ConnectionConfiguration(QtGui.QDialog):
    noConnection = QtCore.Signal(Exception)
    accessDenied = QtCore.Signal(Exception)
    configurationError = QtCore.Signal(Exception)
    connected = QtCore.Signal()
    
    def __init__(self, name, config_dict, host="127.0.0.1", port=3306, user="mysql", password="mysql", db_type=SQL_SQLITE, parent=None):
        
        super(ConnectionConfiguration, self).__init__(parent)
        
        self.default_host = host
        self.default_port = port
        self.default_user = user
        self.default_password = password
        self.default_type = db_type

        self.current_server = name
        self.backup_dict = dict(config_dict)
        self.backup_server = name
        self.config_dict = dict(config_dict)
        
        self.ui = Ui_ConnectionConfig()
        self.ui.setupUi(self)
        
        self.ui.frame_sqlite.hide()

        
        #self.ui.checkbox_layout.removeWidget(self.ui.checkBox)
        #self.ui.checkBox.hide()
        #del self.ui.checkBox
        #self.ui.switch_default_path = classes.CoqSwitch(text="Use default directory")
        #self.ui.checkbox_layout.addWidget(self.ui.switch_default_path)
        #self.ui.label_checkbox.buddy = self.ui.switch_default_path
        
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        # set up button signals
        self.ui.button_create_user.clicked.connect(self.create_user)
        self.ui.button_add.clicked.connect(self.add_configuration)
        self.ui.button_replace.clicked.connect(self.replace_configuration)
        self.ui.button_remove.clicked.connect(self.remove_configuration)
        
        # set up connection signals:
        self.noConnection.connect(lambda x: self.update_connection("noConnection", x))
        self.accessDenied.connect(lambda x: self.update_connection("accessDenied", x))
        self.configurationError.connect(lambda x: self.update_connection("configurationError", x))
        self.connected.connect(lambda: self.update_connection("connected"))
        self.state = None
        
        # set the validator for the configuration name QLineEdit so that
        # only an alphanumeric string (including '_') can be entered:
        self.ui.configuration_name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]*")))
        
        # fill tree widget with existing server configurations:
        for x in sorted(self.config_dict):
            current_item = QtGui.QTreeWidgetItem()
            current_item.setText(0, x)
            self.ui.tree_configuration.insertTopLevelItem(0, current_item)
        
        self.set_configuration(self.get_configuration())
        self.update_configuration(False)

        #self.ui.switch_default_path.toggled.connect(self.toggle_default_path)
        self.ui.radio_default_path.clicked.connect(self.toggle_default_path)
        self.ui.radio_custom_path.clicked.connect(self.toggle_default_path)

        self.ui.tree_configuration.itemActivated.connect(self.apply_configuration)
        self.ui.configuration_name.textChanged.connect(lambda: self.update_configuration(False))

        self.ui.hostname.textChanged.connect(lambda: self.update_configuration(True))
        self.ui.user.textChanged.connect(lambda: self.update_configuration(True))
        self.ui.password.textChanged.connect(lambda: self.update_configuration(True))
        self.ui.port.valueChanged.connect(lambda: self.update_configuration(True))
        self.ui.radio_local.clicked.connect(lambda: self.update_configuration(True))
        self.ui.radio_remote.clicked.connect(lambda: self.update_configuration(True))

        self.ui.button_db_path.clicked.connect(self.set_sql_path)
        self.ui.input_db_path.textChanged.connect(lambda: self.update_configuration(True))
        
        self.ui.configuration_name.textEdited.connect(self.set_default_path)
        
        self.ui.radio_mysql.toggled.connect(self.toggle_engine)
        self.ui.radio_sqlite.toggled.connect(self.toggle_engine)
        if not options._use_mysql:
            self.ui.radio_mysql.setDisabled(True)
        self.toggle_engine()
        
        try:
            self.resize(options.settings.value("connectionconfiguration_size"))
        except TypeError:
            pass

    def set_default_path(self):
        if self.ui.radio_default_path.isChecked():
            self.ui.input_db_path.setText(
                    self.get_sql_path(str(self.ui.configuration_name.text())))

    def toggle_default_path(self):
        if str(self.ui.configuration_name.text()) == "Default":
            self.ui.radio_default_path.setChecked(True)
            #self.ui.switch_default_path.setOn()
        if self.ui.radio_default_path.isChecked():
        #if self.ui.switch_default_path.isOn():
            self.ui.button_db_path.setDisabled(True)
            self.ui.input_db_path.setDisabled(True)
        else:
            if str(self.ui.input_db_path.text()) == "":
                self.ui.input_db_path.setText(
                    self.get_sql_path(str(self.ui.configuration_name.text())))
            self.ui.button_db_path.setDisabled(False)
            self.ui.input_db_path.setDisabled(False)
            self.update_configuration(True)

    def closeEvent(self, event):
        options.settings.setValue("connectionconfiguration_size", self.size())

    def update_connection(self, state, exc=None):
        if state == "noConnection":
            match = re.search(r'\"(.*)\"', str(exc))
            if match:
                self.ui.label_connection.setText(match.group(1))
            else:
                self.ui.label_connection.setText(str(exc))
            self.ui.button_status.setStyleSheet('QPushButton {background-color: red; color: red;}')
        elif state == "accessDenied":
            self.ui.label_connection.setText("A MySQL server was found, but access was denied. Check the user name and password, or create a new MySQL user.")
            self.ui.button_status.setStyleSheet('QPushButton {background-color: yellow; color: yellow;}')
        elif state == "configurationError":
            self.ui.label_connection.setText("The current configuration does not appear to be valid. Please check the settings of the dialog.")
            self.ui.button_status.setStyleSheet('QPushButton {background-color: red; color: red;}')
        elif state == "connected": 
            self.ui.button_status.setStyleSheet('QPushButton {background-color: green; color: green;}')
            self.ui.label_connection.setText("Coquery is successfully connected to the MySQL server.")
        self.state = state
        try:
            self.timer.stop()
        except AttributeError: 
            pass
        self.check_buttons()

    def check_buttons(self):
        # disable all buttons by default:
        self.ui.button_add.setEnabled(False)
        self.ui.button_replace.setEnabled(False)
        self.ui.button_remove.setEnabled(False)
        self.ui.radio_sqlite.setEnabled(False)
        self.ui.radio_mysql.setEnabled(False)
        self.ui.label_7.setEnabled(False)
        
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        
        name = str(self.ui.configuration_name.text())

        if name != "Default":
            self.ui.radio_sqlite.setEnabled(True)
            self.ui.radio_mysql.setEnabled(True)
            self.ui.label_7.setEnabled(True)
        else:
            # exit if the configuration name is "Default", because this name 
            # is # reserved:
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            return

        if self.state == "noConnection" or self.state == "configurationError":
            self.ui.group_credentials.setEnabled(False)
        else:
            self.ui.group_credentials.setEnabled(True)            

        # exit if no configuration name has been entered:
        if not name:
            return

        d = self.get_values()

        if d["type"] == SQL_MYSQL and not options._use_mysql:
            return

        # enable either the Add or the Remove button, depending on whether
        # there is already a configuration with the current name:
        if self.state == "connected":
            if name not in self.config_dict:
                self.ui.button_add.setEnabled(True)
                #if d["type"] == SQL_SQLITE:
                    ## Only enable the Add button if the SQLite path exists
                    ## or is empty (in which case the default path will be 
                    ## used):
                    ##if self.ui.switch_default_path.isOn():
                    #if self.ui.radio_default_path.isChecked():
                        #self.ui.button_add.setEnabled(True)
                        #self.ui.input_db_path.setStyleSheet("")
                    #elif os.path.isdir(d["path"]):
                        #self.ui.button_add.setEnabled(True)
                        #self.ui.input_db_path.setStyleSheet("")
                    #else:
                        #self.ui.input_db_path.setStyleSheet("QLineEdit { background: lightyellow; }")
                #else:
                    #self.ui.button_add.setEnabled(True)
            else:
                # only enable Replace button if current values are different
                # from the stored values:
                if d["type"] != self.config_dict[name]["type"]:
                    self.ui.button_replace.setEnabled(True)
                elif d["type"] == SQL_MYSQL:
                    if (d["host"] != self.config_dict[name]["host"] or
                        d["port"] != self.config_dict[name]["port"] or
                        d["user"] != self.config_dict[name]["user"] or
                        d["password"] != self.config_dict[name]["password"]):
                        self.ui.button_replace.setEnabled(True)
                    else:
                        # Enable the Ok button:
                        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
                elif d["type"] == SQL_SQLITE:
                    ## The SQLite db path can be empty (then, the default path 
                    ## will be used). Otherwise, it has to be an existing 
                    ## directory.
                    #if d["path"] == "" or os.path.isdir(d["path"]):
                        ## Enable the Replace button if the path is new:
                        #if (d["path"] != self.config_dict[name]["path"]):
                            #self.ui.button_replace.setEnabled(True)
                        ## Enable the Ok button:
                        #self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
                    
                # Select item in tree:
                self.current_item = self.ui.tree_configuration.findItems(name, QtCore.Qt.MatchExactly, 0)[0]
                self.ui.tree_configuration.insertTopLevelItem(0, self.current_item)
                self.ui.tree_configuration.setCurrentItem(self.current_item)
                self.current_item.setSelected(True)
                
                # Also, enable the Remove button:
                self.ui.button_remove.setEnabled(True)

    def get_sql_path(self, name):
        return os.path.join(options.get_home_dir(), "connections", name, "databases")

    def set_sql_path(self):
        d = self.get_values()
        if d["path"] == "":
            sql_path = os.path.expanduser("~")
        else:
            sql_path = d["path"]

        dialog = QtGui.QFileDialog(directory=sql_path, )
        #dialog.setFileMode(QtGui.QFileDialog.Directory)
        #try:
            #dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
            #dialog.setOption(QtGui.QFileDialog.HideNameFilterDetails, True)
        #except AttributeError:
            #dialog.setFileMode(QtGui.QFileDialog.Directory | QtGui.QFileDialog.DirectoryOnly)
        #dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        name = QtGui.QFileDialog.getExistingDirectory(directory=sql_path, caption="Choose database directory – Coquery")
        if name:
            if type(name) == tuple:
                name = name[0]
            self.ui.input_db_path.setText(name)        

    def apply_configuration(self, item):
        self.current_configuration = self.config_dict[str(item.text(0))]
        self.current_configuration["name"] = str(item.text(0))
        self.set_configuration(self.current_configuration)
        self.update_configuration(True)
            
    def set_configuration(self, d):
        self.ui.configuration_name.setText(d["name"])
        self.old_name = d["name"]

        if d["type"] == SQL_MYSQL:
            self.ui.radio_mysql.setChecked(True)
            self.ui.frame_mysql.show()
            #self.ui.frame_sqlite.hide()

            if d["host"] == "127.0.0.1":
                self.ui.radio_local.setChecked(True)
            else:
                self.ui.radio_remote.setChecked(True)
                self.ui.hostname.setText(d["host"])
            
            self.ui.user.setText(d["user"])
            self.ui.password.setText(d["password"])
            self.ui.port.setValue(int(d["port"]))
        elif d["type"] == SQL_SQLITE:
            self.ui.radio_sqlite.setChecked(True)
            self.ui.frame_mysql.hide()
            #self.ui.frame_sqlite.show()
            self.ui.input_db_path.setText(d["path"])
            if not str(self.ui.input_db_path.text()):
                #self.ui.switch_default_path.setOn()
                self.ui.radio_default_path.setChecked(True)
                self.ui.button_db_path.setDisabled(True)
                self.ui.input_db_path.setDisabled(True)
            else:
                #self.ui.switch_default_path.setOff()
                self.ui.radio_custom_path.setChecked(True)
                self.ui.button_db_path.setDisabled(False)
                self.ui.input_db_path.setDisabled(False)
       
    def get_configuration(self):
        if self.current_server in self.config_dict:
            # Select the current configuration in the tree:
            self.current_item = self.ui.tree_configuration.findItems(self.current_server, QtCore.Qt.MatchExactly, 0)[0]
            self.ui.tree_configuration.setCurrentItem(self.current_item)
            self.current_item.setSelected(True)                
            return self.config_dict[self.current_server]
        else:
            return {
                "name": "Default",
                "host": self.default_host,
                "port": self.default_port,
                "user": self.default_user,
                "type": self.default_type,
                "path": self.get_sql_path("Default"),
                "password": self.default_password}
    
    def get_values(self):
        d = dict()
        d["name"] = str(self.ui.configuration_name.text())
        d["host"] = self.get_hostname()
        d["port"] = int(self.ui.port.text())
        d["user"] = str(self.ui.user.text())
        d["path"] = os.path.expanduser(str(self.ui.input_db_path.text()))
        d["password"] = str(self.ui.password.text())
        if self.ui.radio_mysql.isChecked():
            d["type"] = SQL_MYSQL
        elif self.ui.radio_sqlite.isChecked():
            d["type"] = SQL_SQLITE
        return d
    
    def add_configuration(self):
        name = str(self.ui.configuration_name.text())
        self.config_dict[name] = self.get_values()
        self.current_item = QtGui.QTreeWidgetItem()
        self.current_item.setText(0, name)
        self.ui.tree_configuration.insertTopLevelItem(0, self.current_item)
        self.ui.tree_configuration.setCurrentItem(self.current_item)
        self.current_item.setSelected(True)
        self.check_buttons()
    
    def remove_configuration(self, name=None):
        if not name:
            name = str(self.ui.configuration_name.text())
        current_item = self.ui.tree_configuration.findItems(name, QtCore.Qt.MatchExactly, 0)[0]
        self.ui.tree_configuration.takeTopLevelItem(
            self.ui.tree_configuration.indexOfTopLevelItem(current_item))
        self.config_dict.pop(name)
        self.check_buttons()
    
    def replace_configuration(self):
        name = str(self.ui.configuration_name.text())
        self.config_dict[name] = self.get_values()

    def get_hostname(self):
        if self.ui.radio_local.isChecked():
            hostname = "127.0.0.1"
        else:
            hostname = str(self.ui.hostname.text())
            if hostname == "localhost":
                hostname == "127.0.0.1"
        if hostname == "127.0.0.1":
            self.ui.radio_local.setChecked(True)
            self.ui.hostname.setText("")
            self.ui.hostname.setEnabled(False)
        else:
            self.ui.radio_local.setChecked(False)
            self.ui.hostname.setEnabled(True)
        return hostname

    def create_user(self):
        import createuser
        name = str(self.ui.user.text())
        password = str(self.ui.password.text())
        create_data = createuser.CreateUser.get(name, password, self)

        hostname = self.get_hostname()

        if create_data:
            root_name, root_password, name, password = create_data
            try:
                engine = sqlalchemy.create_engine(sqlhelper.sql_url((
                    hostname, 
                    self.ui.port.value(),
                    SQL_MYSQL,
                    root_name,
                    root_password)))
            except sqlalchemy.exc.SQLAlchemyError as e:
                QtGui.QMessageBox.critical(self, "Access as root failed", "<p>A root access to the MySQL server could not be established.</p><p>Please check the MySQL root name and the MySQL root password, and try again to create a user.") 
                return
            S = """
            CREATE USER '{user}'@'{hostname}' IDENTIFIED BY '{password}';
            GRANT ALL PRIVILEGES ON * . * TO '{user}'@'{hostname}';
            FLUSH PRIVILEGES;""".format(
                user=name, password=password, hostname=hostname)

            with engine.connect() as connection:
                try:
                    connection.execute(S)
                except sqlalchemy.exc.SQLAlchemyError:
                    QtGui.QMessageBox.critical(self, "Error creating user", "Apologies – the user named '{}' could not be created on the MySQL server.".format(name))
                    return
                except Exception as e:
                    print(e)
                    raise e
                else:
                    QtGui.QMessageBox.information(self, "User created", "The user named '{}' has successfully been created on the MySQL server.".format(name))
            engine.dispose()
            self.ui.user.setText(name)
            self.ui.password.setText(password)
            self.check_connection()

    def update_configuration(self, connection_changed):
        self.configuration_changed = connection_changed
        #if not str(self.ui.input_db_path.text()):
            #self.ui.input_db_path.setText(os.path.join(
                #options.cfg.connections_path, self.ui.input_db_path.text(), "databases"))
        if connection_changed or self.state == None:
            self.current_connection = self.check_connection()
        self.check_buttons()
            
    def toggle_engine(self):
        """
        Change the current database engine type.
        """
        self.ui.frame_mysql.hide()
        #self.ui.frame_sqlite.hide()
        if self.ui.radio_mysql.isChecked():
            self.ui.frame_mysql.show()
        elif self.ui.radio_sqlite.isChecked():
            #self.ui.frame_sqlite.show()
            pass
        self.check_buttons()
            
    def check_connection(self):
        """ 
        Check if a connection can be established using the current 
        configuration.
        
        For an SQLite configuration, it is always assumed that a connection 
        can be establised. For MySQL configurations, the settings from the 
        GUI are used to probe the database host.
        
        This method also sets the connection indicator according to the 
        connection state.
        
        Returns
        -------
        b : bool
            True if a connection could be established, or False otherwise.
        """

        if self.ui.radio_sqlite.isChecked():
            self.connected.emit()
            return True

        if self.ui.radio_mysql.isChecked() and not options._use_mysql:
            self.noConnection.emit(Exception("The Python package 'pymysql' is not installed on this system. MySQL connections are not available."))
            return
        
        hostname = self.get_hostname()
        if hostname == "127.0.0.1":
            self.ui.radio_local.setChecked(True)
            self.ui.hostname.setText("")
            self.ui.hostname.setEnabled(False)
        else:
            self.ui.radio_local.setChecked(False)
            self.ui.hostname.setEnabled(True)

        if check_valid_host(hostname):
            self.probe_thread = classes.CoqThread(lambda: self.probe_host(hostname), self)
            self.ui.button_status.setStyleSheet('QPushButton {background-color: grey; color: grey;}')
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_timeout)
            self.timeout_remain = 60
            self.timer.start(1000)
            self.probe_thread.start()
        else:
            self.noConnection.emit(Exception("Invalid hostname or invalid IP address"))
        
    def update_timeout(self):
        try:
            if self.probe_thread.isRunning() and self.timeout_remain >= 0:
                self.timeout_remain = self.timeout_remain - 1
                self.ui.label_connection.setText(
                    "Testing connection (timeout in {} seconds)...".format(self.timeout_remain))
        except AttributeError:
            pass
        
    def probe_host(self, hostname):
        if self.ui.radio_mysql.isChecked():
            db_type = SQL_MYSQL
        else:
            db_type = SQL_SQLITE

        ok, exc = sqlhelper.test_configuration(
                    (hostname, 
                    self.ui.port.value(),
                    db_type,
                    str(self.ui.user.text()),
                    str(self.ui.password.text())))
        if not ok:
            if "access denied" in str(exc.orig).lower():
                self.accessDenied.emit(exc.orig)
            else:
                self.noConnection.emit(exc.orig)
        else:
            self.connected.emit()
    
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def reset_values(self):
        self.config_dict = dict(self.backup_dict)
        self.current_server = self.backup_server

    def accept(self):
        self.current_server = str(self.ui.tree_configuration.currentItem().text(0))
        super(ConnectionConfiguration, self).accept()

    def reject(self):
        self.reset_values()
        super(ConnectionConfiguration, self).reject()

    def exec_(self):
        super(ConnectionConfiguration, self).exec_()
        if self.ui.tree_configuration.currentItem():
            return (self.config_dict, str(self.ui.tree_configuration.currentItem().text(0)))
        else:
            return None
        
    @staticmethod
    def choose(configuration_name, configuration_dict, parent=None):
        dialog = ConnectionConfiguration(configuration_name, configuration_dict, parent=parent)
        return dialog.exec_()

def main():
    app = QtGui.QApplication(sys.argv)
    viewer = ConnectionConfiguration.choose(None, {})
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    
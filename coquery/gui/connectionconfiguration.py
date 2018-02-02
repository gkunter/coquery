# -*- coding: utf-8 -*-
"""
Connectionconfiguration.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import socket
import re
import string
import os
import shutil
import sys
import logging

from coquery.general import (utf8,
                             get_available_space, format_file_size)
from coquery import options
from coquery.defines import (
    DEFAULT_CONFIGURATION, SQL_MYSQL, SQL_SQLITE,
    msg_not_enough_space, msg_completely_remove, msg_invalid_ip,
    msg_mysql_remove, msg_mysql_access_denied, msg_mysql_success,
    msg_mysql_invalid)
from coquery.connections import (get_connection,
                                 MySQLConnection, SQLiteConnection)

from .pyqt_compat import (QtCore, QtWidgets, QtGui, STYLE_WARN)
from . import errorbox
from .classes import CoqProgressDialog, CoqThread
from .ui.connectionConfigurationUi import Ui_ConnectionConfig
from .app import get_icon


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
            # strip exactly one dot from the right, if present
            s = s[:-1]
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in s.split("."))

    if is_valid_ipv6_address(s):
        return True
    if is_valid_ipv4_address(s):
        return True
    if is_valid_hostname(s):
        return True
    return False


class ConnectionConfiguration(QtWidgets.QDialog):
    noConnection = QtCore.Signal(Exception)
    accessDenied = QtCore.Signal(Exception)
    configurationError = QtCore.Signal(Exception)
    connected = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(ConnectionConfiguration, self).__init__(parent)
        self.default_host = "127.0.0.1"
        self.default_port = 3306
        self.default_user = "mysql"
        self.default_password = "mysql"
        self.default_type = SQL_SQLITE
        self._path_edited = False
        self._removed = set()
        self._renamed = {}

        self.ui = Ui_ConnectionConfig()
        self.ui.setupUi(self)
        self.ui.button_add.setIcon(get_icon("Plus"))
        self.ui.button_remove.setIcon(get_icon("Minus"))

        self.ui.ok_button = self.ui.buttonBox.button(self.ui.buttonBox.Ok)
        self.add_new_placeholder()

        # set the validator for the configuration name QLineEdit so that
        # only an alphanumeric string (including '_') can be entered:
        self.ui.connection_name.setValidator(
            QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]*")))

        # Add auto complete to file name edit:
        completer = QtWidgets.QCompleter()
        model = QtWidgets.QFileSystemModel(completer)
        model.setRootPath(os.path.expanduser("~"))
        model.setFilter(QtCore.QDir.Dirs |
                        QtCore.QDir.Drives |
                        QtCore.QDir.NoDotAndDotDot |
                        QtCore.QDir.AllDirs |
                        QtCore.QDir.Hidden)
        completer.setModel(model)
        self.ui.input_db_path.setCompleter(completer)

        self.ui.list_config.currentRowChanged.connect(
            self.new_connection)

        self.ui.radio_mysql.toggled.connect(self.toggle_engine)
        self.ui.radio_sqlite.toggled.connect(self.toggle_engine)
        self.ui.radio_local.toggled.connect(self.toggle_local)
        self.ui.radio_remote.toggled.connect(self.toggle_local)

        self.ui.button_db_path.clicked.connect(self.set_sql_path)
        self.ui.button_create_user.clicked.connect(self.create_user)
        self.ui.button_add.clicked.connect(self.add_new_connection)
        self.ui.button_remove.clicked.connect(self.remove_connection)

        # set up connection signals:
        self.noConnection.connect(
            lambda x: self.update_connection("noConnection", x))
        self.accessDenied.connect(
            lambda x: self.update_connection("accessDenied", x))
        self.configurationError.connect(
            lambda x: self.update_connection("configurationError", x))
        self.connected.connect(
            lambda x: self.update_connection("connected"))

        self._input_widgets = (self.ui.radio_sqlite, self.ui.radio_mysql,
                               self.ui.radio_local, self.ui.radio_remote,
                               self.ui.hostname, self.ui.user,
                               self.ui.connection_name,
                               self.ui.password, self.ui.input_db_path)

        for signal in (self.ui.hostname.textChanged,
                       self.ui.user.textChanged,
                       self.ui.port.valueChanged,
                       self.ui.password.textChanged,
                       self.ui.radio_local.toggled,
                       self.ui.radio_remote.toggled):
            signal.connect(self.check_values)
            signal.connect(self.check_connection)

        self.ui.connection_name.textChanged.connect(self.change_name)
        self.ui.input_db_path.textChanged.connect(self.check_path)
        self.ui.input_db_path.textEdited.connect(self.edit_path)
        try:
            self.resize(
                options.settings.value("connectionconnection_size"))
        except TypeError:
            pass

    def add_new_placeholder(self):
        name = "New connection..."
        connection = SQLiteConnection("", "")
        item = QtWidgets.QListWidgetItem(name)
        item.setData(QtCore.Qt.UserRole, connection)
        self.ui.list_config.insertItem(0, item)

    def get_gui_content(self):
        name = utf8(self.ui.connection_name.text())
        db_type = (SQL_MYSQL if self.ui.radio_mysql.isChecked() else
                   SQL_SQLITE)

        d = dict()
        d["host"] = utf8(self.ui.hostname.text())
        d["port"] = int(self.ui.port.text())
        d["user"] = utf8(self.ui.user.text())
        d["password"] = utf8(self.ui.password.text())
        d["path"] = os.path.abspath(utf8(self.ui.input_db_path.text()))

        return get_connection(name, db_type, **d)

    def add_new_connection(self):
        connection = self.get_gui_content()
        self.add_connection(connection)
        self.select_item(connection.name)

    def is_new_connection(self):
        return (self.ui.list_config.currentRow() ==
                self.ui.list_config.count() - 1)

    def add_connection(self, conf):
        name = utf8(conf.name)
        item = QtWidgets.QListWidgetItem(name)
        item.setData(QtCore.Qt.UserRole, conf)
        item.setData(QtCore.Qt.UserRole + 1, conf)
        self.ui.list_config.insertItem(
            self.ui.list_config.count() - 1, item)

    def remove_connection(self):
        item = self.ui.list_config.currentItem()
        connection = item.data(QtCore.Qt.UserRole)
        name = utf8(item.text())
        confirm_remove = False

        # get confirmation for removal from user, if necessary:
        if connection.db_type() == SQL_MYSQL:
            confirm_remove = True
            resources = options.get_available_resources(name)
            number_of_resources = len(resources)
            if number_of_resources:
                kwargs = dict(name=name,
                              list="<br>".join(list(resources.keys())),
                              number=number_of_resources)
                if number_of_resources > 1:
                    kwargs.update(dict(are="are", corpora="corpora"))
                else:
                    kwargs.update(dict(are="is", corpora="corpus"))
                response = QtWidgets.QMessageBox.warning(
                    self,
                    "Completely remove connection – Coquery",
                    msg_mysql_remove.strip().format(**kwargs),
                    QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.Yes)
                confirm_remove = response == QtWidgets.QMessageBox.Yes

        elif connection.db_type() == SQL_SQLITE:
            db_paths = self.files_from_connection(connection)
            resources = options.get_available_resources(name)
            if not db_paths:
                confirm_remove = True
            else:
                size = sum([os.path.getsize(x) for x in db_paths])
                kwargs = dict(name=name, size=format_file_size(size),
                              list="<br>".join(list(resources.keys())))
                if len(db_paths) > 1:
                    kwargs.update(dict(are="are", number=len(db_paths),
                                       corpora="corpora"))
                else:
                    kwargs.update(dict(are="is", number="one",
                                       corpora="corpus"))
                s = msg_completely_remove.format(**kwargs)
                response = QtWidgets.QMessageBox.warning(
                    self,
                    "Completely remove connection – Coquery",
                    s,
                    QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.Yes)
                confirm_remove = response == QtWidgets.QMessageBox.Yes

        # removal is either confirmed or no confirmation is necessary,
        # proceed:
        if confirm_remove:
            self._removed.add(connection)
            for renamed_connection in self._renamed:
                if self._renamed[renamed_connection] == name:
                    self._renamed.pop(renamed_connection)
            current_row = self.ui.list_config.currentRow()
            self.ui.list_config.takeItem(current_row)
            if current_row == self.ui.list_config.count() - 1:
                self.ui.list_config.setCurrentRow(current_row - 1)

    def select_item(self, name):
        for i in range(self.ui.list_config.count()):
            item = self.ui.list_config.item(i)
            if item.data(QtCore.Qt.UserRole).name == name:
                self.ui.list_config.setCurrentItem(item)
                return item
        self.ui.list_config.setCurrentItem(None)
        return None

    def closeEvent(self, event):
        options.settings.setValue("connectionconnection_size", self.size())

    def new_connection(self, row):
        if row == -1:
            return
        item = self.ui.list_config.item(row)
        data = item.data(QtCore.Qt.UserRole)
        self.set_connection(data)
        self._path_edited = False

    def block_input_signals(self):
        for widget in self._input_widgets:
            widget.blockSignals(True)

    def unblock_input_signals(self):
        for widget in self._input_widgets:
            widget.blockSignals(False)

    def set_connection(self, d):
        self.block_input_signals()

        name = d.name
        self.ui.connection_name.setText(name)

        is_default = (name == DEFAULT_CONFIGURATION)
        self.ui.button_db_path.setHidden(is_default)
        self.ui.input_db_path.setReadOnly(is_default)
        self.ui.connection_name.setReadOnly(is_default)

        is_new = self.is_new_connection()
        self.ui.radio_mysql.setVisible(is_new)
        self.ui.radio_sqlite.setVisible(is_new)
        self.ui.label_mysql_server.setVisible(is_new)

        if isinstance(d, MySQLConnection):
            self.ui.radio_mysql.setChecked(True)
            self.ui.frame_mysql.show()
            self.ui.frame_sqlite.hide()
            if d.host == "127.0.0.1":
                self.ui.radio_local.setChecked(True)
                self.ui.hostname.setDisabled(True)
            else:
                self.ui.radio_remote.setChecked(True)
                self.ui.hostname.setText(d.host)
                self.ui.hostname.setDisabled(False)

            self.ui.user.setText(d.user)
            self.ui.password.setText(d.password)
            self.ui.port.setValue(int(d.port))
        elif isinstance(d, SQLiteConnection):
            self.ui.radio_sqlite.setChecked(True)
            self.ui.frame_sqlite.show()
            self.ui.frame_mysql.hide()

        if is_new:
            path = ""
        elif not is_default:
            path = getattr(d, "path", "")
        else:
            path = os.path.join(
                options.cfg.connections_path, name, "databases")
        self.ui.input_db_path.setText(path)

        self.unblock_input_signals()
        self.check_values()
        self.current_connection = self.check_connection()
        self.ui.connection_name.setFocus()

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
            self.connected.emit("")
            return True

        if self.ui.radio_mysql.isChecked() and not options.use_mysql:
            S = ("The Python package 'pymysql' is not installed on this "
                 "system. MySQL connections are not available.")
            self.noConnection.emit(Exception(S))
            return

        if self.ui.radio_local.isChecked:
            hostname = "127.0.0.1"
        else:
            hostname = utf8(self.ui.hostname.text())

        if check_valid_host(hostname):
            self.probe_thread = CoqThread(
                lambda: self.probe_host(hostname), self)
            self.probe_thread.taskException.connect(self.probe_exception)

            self.ui.button_status.setStyleSheet(
                'QPushButton {background-color: grey; color: grey;}')
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_timeout)
            self.timeout_remain = 60
            self.timer.start(1000)
            self.probe_thread.start()
        else:
            self.noConnection.emit(Exception(msg_invalid_ip))

    def probe_exception(self):
        print(self.exc_info, self.exception)

    def toggle_engine(self):
        """
        Change the current database engine type.
        """
        d = self.ui.list_config.currentItem().data(QtCore.Qt.UserRole)
        name = d.name

        # the default connection cannot be changed:
        if name == DEFAULT_CONFIGURATION:
            self.block_input_signals()
            self.ui.radio_sqlite.setChecked(True)
            self.unblock_input_signals()
        else:
            self.ui.frame_mysql.setVisible(self.ui.radio_mysql.isChecked())
            self.ui.frame_sqlite.setHidden(self.ui.radio_mysql.isChecked())
            self.check_values()

    def toggle_local(self):
        self.block_input_signals()
        self.ui.hostname.setEnabled(self.ui.radio_remote.isChecked())
        self.unblock_input_signals()

    def edit_path(self):
        self._path_edited = True

    def check_path(self, path):
        if not self.is_new_connection():
            path_exists = os.path.isdir(utf8(path))
            self.ui.ok_button.setEnabled(path_exists)
            self.ui.input_db_path.setStyleSheet(
                "" if path_exists else STYLE_WARN)
            if not self.is_new_connection() and path_exists:
                self.update_connection(self.get_gui_content())
        else:
            self.ui.input_db_path.setStyleSheet("")

    def change_name(self, new_name):
        ok_button = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)

        # if the name is empty, the Ok button and the Add button are always
        # disabled:
        if new_name == "":
            self.ui.connection_name.setStyleSheet(STYLE_WARN)
            ok_button.setDisabled(True)
            self.ui.button_add.setDisabled(True)
            return

        # if another configuration exists with the same name, the Ok button
        # and the Add button are always disabled:
        for i in range(self.ui.list_config.count()):
            item = self.ui.list_config.item(i)
            if utf8(item.text()) == utf8(new_name):
                ok_button.setDisabled(True)
                self.ui.button_add.setDisabled(True)
                self.block_input_signals()
                self.ui.connection_name.setStyleSheet(STYLE_WARN)
                self.unblock_input_signals()
                return

        self.ui.connection_name.setStyleSheet("")
        # in the case of a valid name, enable the Add button if this is a
        # new configuration, or the Ok button otherwise
        if self.is_new_connection():
            ok_button.setDisabled(True)
            self.ui.button_add.setEnabled(True)
            if not self._path_edited:
                default_path = os.path.join(
                    options.cfg.connections_path, new_name, "databases")
                self.ui.input_db_path.setText(default_path)
        else:
            item = self.ui.list_config.currentItem()
            connection = item.data(QtCore.Qt.UserRole + 1)
            self._renamed[connection] = new_name
            self.ui.list_config.currentItem().setText(new_name)
            ok_button.setEnabled(True)
            self.ui.button_add.setDisabled(True)
            if not self.is_new_connection():
                self.update_connection(self.get_gui_content())

    def check_values(self):
        name = utf8(self.ui.connection_name.text())
        hostname = utf8(self.ui.hostname.text())

        ok_button = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        ok_button.setDisabled(name == "")

        is_default = (name == DEFAULT_CONFIGURATION)
        is_new = self.is_new_connection()

        if name == "":
            self.ui.button_add.setDisabled(True)
            self.ui.button_add.setStyleSheet(STYLE_WARN)
        else:
            self.ui.button_add.setEnabled(is_new)
            self.ui.button_add.setStyleSheet("")

        self.ui.button_remove.setEnabled(not is_default and not is_new)

        self.block_input_signals()
        if self.ui.radio_remote.isChecked():
            if hostname == "127.0.0.1":
                self.ui.radio_local.setChecked(True)
                self.ui.hostname.setText("")
                self.ui.hostname.setEnabled(False)
            else:
                self.ui.radio_local.setChecked(False)
                self.ui.hostname.setEnabled(True)
        else:
            self.ui.hostname.setDisabled(True)
        self.unblock_input_signals()

        if not is_new:
            self.update_connection(self.get_gui_content())

    def update_timeout(self):
        try:
            if self.probe_thread.isRunning() and self.timeout_remain >= 0:
                self.timeout_remain = self.timeout_remain - 1
                s = "Testing connection (timeout in {} seconds)...".format(
                    self.timeout_remain)
                self.ui.text_status.setText(s)
        except AttributeError:
            pass

    def probe_host(self, hostname):
        if self.ui.radio_mysql.isChecked():
            db_type = SQL_MYSQL
        else:
            db_type = SQL_SQLITE

        kwargs = dict(host=hostname,
                      port=int(self.ui.port.value()),
                      user=utf8(self.ui.user.text()),
                      password=utf8(self.ui.password.text()),
                      path=utf8(self.ui.input_db_path.text()))
        con = get_connection(None, db_type, **kwargs)
        ok, exc = con.test()
        if not ok:
            if "access denied" in str(exc.orig).lower():
                self.accessDenied.emit(exc.orig)
            else:
                self.noConnection.emit(exc.orig)
        else:
            self.connected.emit(exc)

    def update_connection(self, state, exc=None):
        def style_button(color):
            S = 'QPushButton {{ background-color: {col}; color: {col}; }}'
            return S.format(col=color)
        if state == "noConnection":
            match = re.search(r'\"(.*)\"', str(exc))
            if match:
                self.ui.text_status.setText(match.group(1))
            else:
                self.ui.text_status.setText(str(exc))
            self.ui.button_status.setStyleSheet(style_button("yellow"))
            self.ui.ok_button.setDisabled(True)
        elif state == "accessDenied":
            self.ui.text_status.setText(msg_mysql_access_denied.strip())
            self.ui.button_status.setStyleSheet(style_button("yellow"))
            self.ui.ok_button.setDisabled(True)
        elif state == "configurationError":
            self.ui.text_status.setText(msg_mysql_invalid.strip())
            self.ui.button_status.setStyleSheet(style_button("red"))
            self.ui.ok_button.setDisabled(True)
        elif state == "connected":
            self.ui.text_status.setText(msg_mysql_success.strip())
            self.ui.button_status.setStyleSheet(style_button("green"))
        self.state = state
        try:
            self.timer.stop()
        except AttributeError:
            pass

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def exec_(self):
        result = super(ConnectionConfiguration, self).exec_()
        if result == QtWidgets.QDialog.Accepted:
            d = {}

            # move files if necessary:
            new_configs = {}
            old_configs = {}
            try:
                # rename the connections:
                for connection, new_name in self._renamed.items():
                    connection.rename(new_name)

                # move files
                for i in range(self.ui.list_config.count() - 1):
                    item = self.ui.list_config.item(i)
                    data = item.data(QtCore.Qt.UserRole)
                    old = item.data(QtCore.Qt.UserRole + 1)
                    name = utf8(item.text())
                    new_configs[name] = data
                    old_configs[name] = old
                for name in new_configs:
                    new = new_configs[name]
                    old = old_configs.get(name, None)
                    if (isinstance(new, SQLiteConnection) and
                            old and
                            new.path != old.path):
                        try:
                            self.move_connection(
                                name, old.path, new.path)
                        except Exception as e:
                            errorbox.ErrorBox.show(sys.exc_info())
                            data = old
                    d[name] = new

                # *really* remove the files that are slated for removal:
                for connection in self._removed:
                    self.wipe_connection(connection)

            except Exception as e:
                print(e)
                raise e
            return (d, utf8(self.ui.list_config.currentItem().text()))
        else:
            return None

    def files_from_connection(self, connection):
        resources = connection.resources()
        try:
            from_path = connection.path
        except AttributeError:
            db_paths = []
        else:
            db_paths = [os.path.join(from_path,
                                     "{}.db".format(resources[x][0].db_name))
                        for x in resources]
        return db_paths

    @staticmethod
    def choose(connection_name, connections, parent=None):
        result = None
        try:
            dialog = ConnectionConfiguration(parent=parent)
            for connection in connections:
                dialog.add_connection(connections[connection])
            dialog.select_item(connection_name)
            dialog.show()
            result = dialog.exec_()
        except Exception as e:
            print(e)
            raise e
        finally:
            return result

    def create_user(self):
        from . import createuser
        name = str(self.ui.user.text())
        password = str(self.ui.password.text())
        create_data = createuser.CreateUser.get(name, password, self)

        if create_data:
            root_name, root_password, name, password = create_data
            host = utf8(self.ui.hostname.text())
            port = int(self.ui.port.value())
            con = MySQLConnection(name="",
                                  host=host, port=port,
                                  user=root_name, password=root_password)
            try:
                engine = con.get_engine()
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Access as root failed",
                    ("<p>A root access to the MySQL server could not be "
                     "established.</p><p>Please check the MySQL root name "
                     "and the MySQL root password, and try again to create "
                     "a user."))
                return
            S = """
            CREATE USER '{user}'@'{host}' IDENTIFIED BY '{password}';
            GRANT ALL PRIVILEGES ON * . * TO '{user}'@'{host}';
            FLUSH PRIVILEGES;""".format(
                user=name, password=password, host=host)

            with engine.connect() as connection:
                try:
                    connection.execute(S)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Error creating user",
                        ("the user named '{}' could not be "
                         "created on the MySQL server.").format(name))
                    return
                else:
                    QtWidgets.QMessageBox.information(
                        self,
                        "User created",
                        ("The user named '{}' was successfully created on the"
                         "MySQL server.").format(name))
            engine.dispose()
            self.ui.user.setText(name)
            self.ui.password.setText(password)
            self.check_connection()

    def set_sql_path(self):
        path = utf8(self.ui.input_db_path.text())
        if path == "":
            sql_path = os.path.expanduser("~")
        else:
            sql_path = path

        name = utf8(QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select new database directory – Coquery",
            sql_path))
        if name:
            if type(name) == tuple:
                name = name[0]
            self.block_input_signals()
            self.ui.input_db_path.setText(name)
            self.update_connection(self.get_gui_content())
            self.unblock_input_signals()

    def wipe_connection(self, connection):
        name = connection.name
        for file_name in self.files_from_connection(connection):
            try:
                os.remove(file_name)
            except Exception as e:
                errorbox.ErrorBox.show(sys.exc_info(), e)

        connection = os.path.join(options.cfg.connections_path, name)
        try:
            shutil.rmtree(connection)
        except Exception as e:
            errorbox.ErrorBox.show(sys.exc_info(), e)
        logging.info("Completely removed connection '{}'".format(name))
        options.cfg.connections.pop(name)

    def move_connection(self, connection, from_path, to_path):
        db_paths = self.files_from_connection(connection)
        # We add a 20 percent safety margin to the calculated disk usage,
        # just to make sure that there will be enough space on the new
        # target:
        used = sum([os.path.getsize(x) for x in db_paths]) * 1.2

        available = get_available_space(to_path)

        if available < used:
            kwargs = dict(
                name=connection.name,
                from_path=from_path,
                to_path=to_path,
                available=format_file_size(available),
                required=format_file_size(used),
                missing=format_file_size((used - available)))
            QtWidgets.QMessageBox.critical(
                self, "Not enough directory/drive space",
                msg_not_enough_space.format(**kwargs))
        else:
            dialog = CoqProgressDialog("Moving database directory – Coquery")
            dialog.setMaximum(len(db_paths))
            dialog.show()

            copied = []
            for i, source_file in enumerate(db_paths):
                dialog.setValue(i)
                base_name = os.path.basename(source_file)
                target_file = os.path.join(to_path, base_name)
                s = "{} ({} out of {})".format(base_name,
                                               i + 1, len(db_paths))
                dialog.setFormat(s)
                try:
                    shutil.copy(source_file, target_file)
                except Exception as e:
                    for copied_file in copied:
                        os.remove(copied)
                    raise e
                else:
                    copied.append(target_file)
            for source_file in db_paths:
                os.remove(source_file)
        logging.info("Moved databases of '{}' from {} to {}".format(
            connection.name, from_path, to_path))

    def exception_during_move(self, exception):
        errorbox.ErrorBox.show(self.exc_info, self.exception)

# -*- coding: utf-8 -*-
"""
orphanageddatabases.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import os
import glob
import logging
from datetime import datetime

from coquery import options
from coquery.defines import SQL_SQLITE, msg_orphanaged_databases
from coquery.general import format_file_size
from coquery.unicode import utf8

from . import classes

from .pyqt_compat import QtCore, QtWidgets
from .ui.orphanagedDatabasesUi import Ui_OrphanagedDatabases


class OrphanagedDatabasesDialog(QtWidgets.QDialog):
    def __init__(self, orphans=[], parent=None):
        super(OrphanagedDatabasesDialog, self).__init__(parent)
        self._links = {}

        self.ui = Ui_OrphanagedDatabases()
        self.ui.setupUi(self)

        self.ui.box_layout = QtWidgets.QVBoxLayout()
        self.ui.box_text = QtWidgets.QLabel(msg_orphanaged_databases)
        self.ui.box_text.setWordWrap(True)
        self.ui.box_layout.addWidget(self.ui.box_text)

        self.ui.detail_box = classes.CoqDetailBox(
            text="What are orphanaged files?",
            alternative="Hide explanation", parent=self.parent())

        self.ui.detail_box.box.setLayout(self.ui.box_layout)
        self.ui.verticalLayout.insertWidget(2, self.ui.detail_box)

        self.ui.tableWidget.setRowCount(len(orphans))
        for i, tup in enumerate(orphans):
            path, name, date, size, reason = tup
            file_name = os.path.basename(path)
            file_item = QtWidgets.QTableWidgetItem(file_name)
            file_item.setData(QtCore.Qt.UserRole, path)
            name_item = QtWidgets.QTableWidgetItem(name)
            size_item = QtWidgets.QTableWidgetItem(format_file_size(size))
            date_item = QtWidgets.QTableWidgetItem(date)

            reason_item = QtWidgets.QTableWidgetItem(reason)
            reason_label = QtWidgets.QLabel()
            reason_label.setWordWrap(True)
            reason_item.sizeHint = reason_label.sizeHint

            size_item.setData(QtCore.Qt.UserRole, size)

            self.ui.tableWidget.setItem(i, 0, file_item)
            self.ui.tableWidget.setItem(i, 1, name_item)
            self.ui.tableWidget.setItem(i, 2, size_item)
            self.ui.tableWidget.setItem(i, 3, date_item)
            self.ui.tableWidget.setItem(i, 4, reason_item)
            self.ui.tableWidget.setCellWidget(i, 4, reason_label)
            file_item.setCheckState(QtCore.Qt.Unchecked)
        self.ui.tableWidget.resizeRowsToContents()
        self.ui.tableWidget.resizeColumnsToContents()

    @staticmethod
    def remove_orphans(orphans):
        """
        Remove the orphanaged databases in the list.
        """
        count = 0
        total = 0
        for file_path, size in orphans:
            logging.warn("Removed {}".format(file_path))
            print("rm {}".format(file_path))
            os.remove(file_path)
            count += 1
            total += size
        QtWidgets.QMessageBox.information(
            None, "Orphanaged files – Coquery",
            "{} orphanaged file{} deleted ({})".format(
                count, "s" if count > 1 else "", format_file_size(total)))

    @staticmethod
    def display(parent=None):
        selected = []
        try:
            path = options.cfg.current_connection.path
            name = options.cfg.current_connection.name
        except AttributeError:
            l = []
        else:
            l = check_orphans(path)

        if l:
            dialog = OrphanagedDatabasesDialog(orphans=l, parent=None)
            dialog.ui.label.setText(utf8(dialog.ui.label.text()).format(
                path=path, name=name))
            result = dialog.exec_()
            if result == QtWidgets.QDialog.Accepted:
                for x in range(dialog.ui.tableWidget.rowCount()):
                    item = dialog.ui.tableWidget.item(x, 0)
                    size = dialog.ui.tableWidget.item(x, 2)
                    if item.checkState() == QtCore.Qt.Checked:
                        path = item.data(QtCore.Qt.UserRole)
                        size = int(size.data(QtCore.Qt.UserRole))
                        selected.append((path, size))
            if selected:
                OrphanagedDatabasesDialog.remove_orphans(selected)


def check_orphans(path):
    """
    Get a list of orphanaged databases in the database directory for the
    current connetion.
    """
    l = []
    if options.cfg.current_connection.db_type() == SQL_SQLITE:
        databases = glob.glob(os.path.join(path, "*.db"))

        # check for databases that are not linked to one of the existing
        # resources:
        for x in databases:
            timestamp = os.path.getmtime(x)
            date = (datetime.fromtimestamp(timestamp).strftime(
                '%Y-%m-%d, %H:%M:%S'))
            file_name, _ = os.path.splitext(os.path.basename(x))
            resource = options.get_resource_of_database(file_name)
            if not resource:
                size = os.path.getsize(x)
                l.append((x, "?", date, size,
                          "No corpus module found for database"))
            else:
                size = os.path.getsize(x)
                if size == 0:
                    l.append((x, resource.name, date, size,
                          "Database file is empty"))


        # check for resources that have an issue with their databases:
        resources = options.cfg.current_connection.resources()
        for name in resources:
            resource, _, module_path = resources[name]
            db_name = os.path.join(path, "{}.db".format(resource.db_name))
            try:
                db_size = os.path.getsize(db_name)
            except Exception:
                db_size = 0

            if (db_name not in databases or db_size == 0):
                timestamp = os.path.getmtime(db_name)
                date = (datetime.fromtimestamp(timestamp).strftime(
                    '%Y-%m-%d, %H:%M:%S'))
                size = os.path.getsize(module_path)
                if db_name not in databases:
                    reason = "Database file '{}' not found in directory '{}'"
                else:
                    reason = "Database file is empty"
                l.append((module_path,
                          name, date, size,
                          reason.format("{}.db".format(resource.db_name),
                                        path)))

    return sorted(l, key=lambda x: x[1])

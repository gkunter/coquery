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
from datetime import datetime

from coquery import options
from coquery.defines import SQL_SQLITE, msg_orphanaged_databases
from coquery.general import format_file_size
from coquery.unicode import utf8
from coquery.sqlhelper import sqlite_path

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
            text="What are orphanaged databases?",
            alternative="Hide explanation", parent=self.parent())

        self.ui.detail_box.box.setLayout(self.ui.box_layout)
        self.ui.verticalLayout.insertWidget(2, self.ui.detail_box)

        self.ui.tableWidget.setRowCount(len(orphans))
        for i, tup in enumerate(orphans):
            name, date, size = tup
            name_item = QtWidgets.QTableWidgetItem(name)
            size_item = QtWidgets.QTableWidgetItem(format_file_size(size))
            date_item = QtWidgets.QTableWidgetItem(date)
            size_item.setData(QtCore.Qt.UserRole, size)

            self.ui.tableWidget.setItem(i, 0, name_item)
            self.ui.tableWidget.setItem(i, 1, size_item)
            self.ui.tableWidget.setItem(i, 2, date_item)

            name_item.setCheckState(QtCore.Qt.Unchecked)
        self.ui.tableWidget.resizeColumnsToContents()

    @staticmethod
    def remove_orphans(orphans):
        """
        Remove the orphanaged databases in the list.
        """
        try:
            path = sqlite_path(options.cfg.current_server)
        except AttributeError:
            path = ""
        count = 0
        total = 0
        if path:
            for name, size in orphans:
                file_path = os.path.join(path, name)
                os.remove(file_path)
                count += 1
                total += size
        QtWidgets.QMessageBox.information(
            None, "Orphanaged databases – Coquery",
            "{} orphanaged database{} deleted ({})".format(
                count, "s" if count > 1 else "", format_file_size(total)))

    @staticmethod
    def display(parent=None):
        selected = []
        l = check_orphans()
        if l:
            dialog = OrphanagedDatabasesDialog(orphans=l, parent=None)
            result = dialog.exec_()
            if result == QtWidgets.QDialog.Accepted:
                for x in range(dialog.ui.tableWidget.rowCount()):
                    item = dialog.ui.tableWidget.item(x, 0)
                    size = dialog.ui.tableWidget.item(x, 1)
                    if item.checkState() == QtCore.Qt.Checked:
                        selected.append((utf8(item.text()),
                                         int(size.data(QtCore.Qt.UserRole))))
            if selected:
                OrphanagedDatabasesDialog.remove_orphans(selected)


def check_orphans():
    """
    Get a list of orphanaged databases in the database directory for the
    current connetion.
    """
    try:
        path = sqlite_path(options.cfg.current_server)
    except AttributeError:
        path = ""
    l = []
    if options.get_configuration_type() == SQL_SQLITE:
        for x in glob.glob(os.path.join(path, "*.db")):
            file_name, _ = os.path.splitext(os.path.basename(x))
            db_name = options.get_resource_of_database(file_name)
            if not db_name:
                timestamp = os.path.getmtime(x)
                date = (datetime.fromtimestamp(timestamp).strftime(
                    '%Y-%m-%d, %H:%M:%S'))
                size = os.path.getsize(x)
                l.append((os.path.basename(x), date, size))
    return l

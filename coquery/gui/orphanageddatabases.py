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

from coquery import options
from coquery.defines import *
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

        for x in orphans:
            item = QtWidgets.QListWidgetItem(x)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui.listWidget.addItem(item)

    @staticmethod
    def remove_orphans(orphans):
        """
        Remove the orphanaged databases in the list.
        """
        try:
            path = sqlite_path(options.cfg.current_server)
        except AttributeError:
            path = ""
        if path:
            for x in orphans:
                file_path = os.path.join(path, x)
                try:
                    os.remove(file_path)
                except:
                    pass

    @staticmethod
    def display(parent=None):
        selected = []
        l = check_orphans()
        if l:
            dialog = OrphanagedDatabasesDialog(orphans=l, parent=None)
            result = dialog.exec_()
            if result == QtWidgets.QDialog.Accepted:
                for x in range(dialog.ui.listWidget.count()):
                    item = dialog.ui.listWidget.item(x)
                    if item.checkState() == QtCore.Qt.Checked:
                        selected.append(utf8(item.text()))
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
    if path:
        for x in glob.glob(os.path.join(path, "*.db")):
            file_name, _ = os.path.splitext(os.path.basename(x))
            if not options.get_resource_of_database(file_name):
                l.append(os.path.basename(x))
    return l

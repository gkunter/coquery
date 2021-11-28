# -*- coding: utf-8 -*-
"""
logfile.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery import options
from .classes import LogTableModel, LogProxyModel
from .pyqt_compat import QtCore, QtWidgets
from .ui.logfileUi import Ui_logfileDialog

BUTTON_MAP = {"ERROR": "check_errors",
              "WARNING": "check_warnings",
              "INFO": "check_info"}


class LogfileViewer(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LogfileViewer, self).__init__(parent)

        self.ui = Ui_logfileDialog()
        self.ui.setupUi(self)

        self.setWindowIcon(options.cfg.icon)

        self.log_table = LogTableModel(options.cfg.log_messages, self)
        self.log_proxy = LogProxyModel()
        self.log_proxy.setSourceModel(self.log_table)
        self.log_proxy.sortCaseSensitivity = False
        self.ui.log_table.setModel(self.log_proxy)

        for log_type in BUTTON_MAP:
            check_box = getattr(self.ui, BUTTON_MAP[log_type])
            check_box.setChecked(log_type in options.cfg.show_log_messages)
            check_box.stateChanged.connect(self.changeFilters)

        self.ui.log_table.resizeColumnsToContents()
        self.ui.log_table.horizontalHeader().setStretchLastSection(True)

        try:
            self.resize(options.settings.value("logfile_size"))
        except TypeError:
            pass

    def changeFilters(self):
        options.cfg.show_log_messages = []
        for filt, checkbox in BUTTON_MAP.items():
            if getattr(self.ui, checkbox).isChecked():
                options.cfg.show_log_messages.append(filt)
        self.log_proxy.updateFilter()
        self.ui.log_table.resizeColumnsToContents()
        self.ui.log_table.horizontalHeader().setStretchLastSection(True)

    def closeEvent(self, event):
        options.settings.setValue("logfile_size", self.size())

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()

    @staticmethod
    def view(parent=None):
        dialog = LogfileViewer(parent)
        return dialog.exec_()

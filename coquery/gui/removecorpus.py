# -*- coding: utf-8 -*-
"""
removecorpus.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import sys

from coquery import options
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtGui
from .ui.removeCorpusUi import Ui_RemoveCorpus

class RemoveCorpusDialog(QtGui.QDialog):
    def __init__(self, entry, configuration_name, parent=None):
        
        super(RemoveCorpusDialog, self).__init__(parent)

        self.ui = Ui_RemoveCorpus()
        self.ui.setupUi(self)

        self.ui.label.setText(utf8(self.ui.label.text()).format(entry.name, configuration_name))

        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.ui.check_rm_database.toggled.connect(lambda: self.check_boxes(self.ui.check_rm_database))
        self.ui.check_rm_module.toggled.connect(lambda: self.check_boxes(self.ui.check_rm_module))

        try:
            self.resize(options.settings.value("removecorpus_size"))
        except TypeError:
            pass

    def check_boxes(self, box):
        # make sure that if the Remove database box is checked, the 
        # Remove corpus module box is also checked:
        if box == self.ui.check_rm_database:
            if box.isChecked():
                self.ui.check_rm_module.setDisabled(True)
                self.ui.check_rm_module.setChecked(True)
            else:
                self.ui.check_rm_module.setDisabled(False)
                
    def closeEvent(self, event):
        options.settings.setValue("removecorpus_size", self.size())
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
            
    @staticmethod
    def select(entry, configuration_name, parent=None):
        dialog = RemoveCorpusDialog(entry, configuration_name, parent=parent)        
        dialog.setVisible(True)
        dialog.ui.check_rm_module.setChecked(True)
        if entry.adhoc:
            dialog.ui.check_rm_installer.setChecked(True)
            dialog.ui.check_rm_installer.setDisabled(True)
            dialog.ui.check_rm_database.setChecked(True)
            dialog.ui.check_rm_database.setDisabled(True)
        if entry.builtin:
            dialog.ui.check_rm_installer.setChecked(False)
            dialog.ui.check_rm_installer.setDisabled(True)
            
        if entry.name not in options.cfg.current_resources:
            dialog.ui.check_rm_database.setChecked(False)
            dialog.ui.check_rm_database.setDisabled(True)
            dialog.ui.check_rm_module.setChecked(False)
            dialog.ui.check_rm_module.setDisabled(True)
        
            
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            return (
                dialog.ui.check_rm_module.isChecked(),
                dialog.ui.check_rm_database.isChecked(),
                dialog.ui.check_rm_installer.isChecked())
        else:
            return None

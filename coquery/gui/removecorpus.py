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

from pyqt_compat import QtCore, QtGui
from ui.removeCorpusUi import Ui_RemoveCorpus

import options

class RemoveCorpusDialog(QtGui.QDialog):
    def __init__(self, corpus_name, configuration_name, parent=None):
        
        super(RemoveCorpusDialog, self).__init__(parent)

        self.ui = Ui_RemoveCorpus()
        self.ui.setupUi(self)

        self.ui.label.setText(str(self.ui.label.text()).format(corpus_name, configuration_name))

        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.reject)

        try:
            self.resize(options.settings.value("removecorpus_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("removecorpus_size", self.size())
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
            
    @staticmethod
    def select(corpus_name, configuration_name, adhoc_corpus, parent=None):
        
        dialog = RemoveCorpusDialog(corpus_name, configuration_name, parent=parent)        
        dialog.setVisible(True)
        dialog.ui.check_rm_module.setChecked(True)
        if adhoc_corpus:
            dialog.ui.check_rm_installer.setChecked(True)
            dialog.ui.check_rm_installer.setDisabled(True)
            dialog.ui.check_rm_database.setChecked(True)
            dialog.ui.check_rm_database.setDisabled(True)
            
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            return (
                dialog.ui.check_rm_module.isChecked(),
                dialog.ui.check_rm_database.isChecked(),
                dialog.ui.check_rm_installer.isChecked())
        else:
            return None

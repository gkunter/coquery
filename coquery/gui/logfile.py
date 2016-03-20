# -*- coding: utf-8 -*-
"""
logfile.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import sys

from coquery import options
from . import classes
from .pyqt_compat import QtCore, QtGui
from .ui.logfileUi import Ui_logfileDialog

class LogfileViewer(QtGui.QDialog):
    def __init__(self, parent=None):
        
        super(LogfileViewer, self).__init__(parent)
        
        self.ui = Ui_logfileDialog()
        self.ui.setupUi(self)
        
        self.setWindowIcon(options.cfg.icon)
        
        self.log_table = classes.LogTableModel(self)
        self.log_proxy = classes.LogProxyModel()
        self.log_proxy.setSourceModel(self.log_table)
        self.log_proxy.sortCaseSensitivity = False
        self.ui.log_table.setModel(self.log_proxy)
        
        #self.ui.log_table.horizontalHeader().setStretchLastSection(True)        
        #self.log_table.setVisible(False)
        self.ui.log_table.resizeColumnsToContents()
        #self.log_table.setVisible(True)

        try:
            self.resize(options.settings.value("logfile_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("logfile_size", self.size())
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()
            
    @staticmethod
    def view(parent=None):
        dialog = LogfileViewer(parent)
        result = dialog.exec_()
        return None
    
            
def main():
    app = QtGui.QApplication(sys.argv)
    viewer = LogfileViewer("")
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    

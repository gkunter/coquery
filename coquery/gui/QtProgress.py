# -*- coding: utf-8 -*-
"""
QtProgress.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import time
import sys, os

from pyqt_compat import QtCore, QtGui
from errorbox import ErrorBox 

from errors import *

class ProgressIndicator(QtGui.QDialog):
    def __init__(self, FUN, finalize=None, label="", parent=None, *args):
        super(ProgressIndicator, self).__init__(parent)
 
        vbox = QtGui.QVBoxLayout()
        label = QtGui.QLabel(label)
        label.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(label)
 
        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(self.progress_bar)
 
        self.setLayout(vbox) 
        self.setGeometry(300, 300, 300, 50)
        self.progress_bar.setRange(0, 1)
        self.finalize = finalize
        self.show()
        if FUN:
            self.thread = ProgressThread(FUN, self, *args)
            self.thread.taskFinished.connect(self.onFinished)
            self.thread.taskException.connect(self.onException)
            
            self.progress_bar.setRange(0,0)
            self.thread.start()
        
    def onException(self):
        ErrorBox.show(self.exc_info, self.exception)
        
    def onFinished(self):
        # Stop the pulsation
        self.progress_bar.setRange(0,1)
        self.progress_bar.setValue(1)
        self.close()
        if self.finalize:
            self.finalize()
        
    @staticmethod
    def RunThread(FUN, label="", parent=None):
        progress = ProgressIndicator(FUN, label, parent)
        result = progress.exec_()

class ProgressThread(QtCore.QThread):
    taskStarted = QtCore.Signal()
    taskFinished = QtCore.Signal()
    taskException = QtCore.Signal(Exception)
    taskAbort = QtCore.Signal()
    
    def __init__(self, FUN, parent=None, *args, **kwargs):
        super(ProgressThread, self).__init__(parent)
        self.FUN = FUN
        self.exiting = False
        self.args = args
        self.kwargs = kwargs
    
    def __del__(self):
        self.exiting = True
        try:
            self.wait()
        except RuntimeError:
            pass
    
    def setInterrupt(self, fun):
        self.INTERRUPT_FUN = fun
    
    def quit(self):
        self.INTERRUPT_FUN()
        super(ProgressThread, self).quit()
    
    def run(self):
        self.taskStarted.emit()
        self.exiting = False
        try:
            self.FUN(*self.args, **self.kwargs)
        except Exception as e:
            if self.parent:
                self.parent().exc_info = sys.exc_info()
                self.parent().exception = e
            self.taskException.emit(e)
        self.taskFinished.emit()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = ProgressIndicator(time.sleep, None, 10)
    window.resize(200, 100)
    window.show()
    window.onStart()
    value = app.exec_()
    window.close()


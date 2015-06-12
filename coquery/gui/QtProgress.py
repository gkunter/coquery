from pyqt_compat import QtCore, QtGui
import threading
import time
import sys, os
from errors import *
from error_box import ErrorBox 

class ProgressIndicator(QtGui.QDialog):
    def __init__(self, FUN, label="", parent=None):
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
        
        self.thread = ProgressThread(FUN, self)
        self.thread.taskFinished.connect(self.onFinished)
        self.thread.taskException.connect(self.onException)
        
        self.show()
        self.progress_bar.setRange(0,0)
        self.thread.start()
        
    def onException(self):
        ErrorBox.show(self.exc_info)
        
    def onFinished(self):
        # Stop the pulsation
        self.progress_bar.setRange(0,1)
        self.progress_bar.setValue(1)
        self.close()
        
    @staticmethod
    def RunThread(FUN, label="", parent=None):
        progress = ProgressIndicator(FUN, label, parent)
        result = progress.exec_()

class ProgressThread(QtCore.QThread):
    taskFinished = QtCore.Signal()
    taskException = QtCore.Signal()
    
    def __init__(self, FUN, window):
        super(ProgressThread, self).__init__()
        self.parent = window
        self.FUN = FUN
    
    def run(self):
        try:
            self.FUN()
        except Exception as e:
            self.parent.exc_info = sys.exc_info()
            self.parent.exception = e
            self.taskException.emit()
        self.taskFinished.emit()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = ProgressIndicator(time.sleep, None, 10)
    window.resize(200, 100)
    window.show()
    window.onStart()
    value = app.exec_()
    window.close()


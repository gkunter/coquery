from pyqt_compat import QtCore, QtGui
import time
import sys, os

class ProgressIndicator(QtGui.QWidget):

    def __init__(self, FUN, parent=None, *args):
        super(ProgressIndicator, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0,1)
        layout.addWidget(self.progressBar)

        TaskThread.FUN = FUN
        TaskThread.args = args
        self.threaded_task = TaskThread()
        
        button = QtGui.QPushButton("Abort query", self)
        layout.addWidget(button)      

        button.clicked.connect(self.abortQuery)
        
        #self.threaded_task.taskFinished.connect(self.onFinished)

    def onStart(self): 
        self.progressBar.setRange(0,0)
        self.threaded_task.start()
        
    def onFinished(self):
        # Stop the pulsation
        self.progressBar.setRange(0,1)
        self.progressBar.setValue(1)


class TaskThread(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()

    def run(self):
        self.FUN(*self.args)
        self.taskFinished.emit() 

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = ProgressIndicator(time.sleep, None, 10)
    window.resize(200, 100)
    window.show()
    window.onStart()
    value = app.exec_()
    window.close()

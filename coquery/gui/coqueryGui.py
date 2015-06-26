from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
import coqueryUi
import sys

class CoqueryGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        
        super(CoqueryGui, self).__init__(parent)
        
        self.ui = coqueryUi.Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()
            
    @staticmethod
    def view(path, parent=None):
        dialog = LogfileViewer(path, parent)
        result = dialog.exec_()
        return None
    
            
def main():
    app = QtGui.QApplication(sys.argv)
    gui = CoqueryGui()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
    
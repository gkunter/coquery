from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
import options
import logfileUi
import sys

class LogfileViewer(QtGui.QDialog):
    def __init__(self, path, parent=None):
        
        super(LogfileViewer, self).__init__(parent)
        
        self.ui = logfileUi.Ui_logfileDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(options.cfg.icon)
        
        # Fill results view:
        with open(path, "rt") as input_file:
            content = input_file.read()
        self.ui.viewing_area.setPlainText(content)
        self.ui.log_file_path.setText(path)
        
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
    viewer = LogfileViewer()
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    
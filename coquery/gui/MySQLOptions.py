from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
#import options
import MySQLOptionsUi
import sys
sys.path.append("/home/kunibert/Dev/coquery/coquery")
import sqlwrap
from errors import *


class MySQLOptions(QtGui.QDialog):
    def __init__(self, host="localhost", user="coquery", password="coquery", port=3306, parent=None):
        
        super(MySQLOptions, self).__init__(parent)
        
        self.ui = MySQLOptionsUi.Ui_Dialog()
        self.ui.setupUi(self)
        #self.setWindowIcon(options.cfg.icon)
        
        ## Fill results view:
        #with open(path, "rt") as input_file:
            #content = input_file.read()
        #self.ui.viewing_area.setPlainText(content)
        self.ui.hostname.setText(host)
        self.ui.user.setText(user)
        self.ui.password.setText(password)
        self.ui.port.setValue(port)
        self.check_connection()
        
        self.ui.hostname.textChanged.connect(self.check_connection)
        self.ui.user.textChanged.connect(self.check_connection)
        self.ui.password.textChanged.connect(self.check_connection)
        self.ui.port.valueChanged.connect(self.check_connection)
        self.ui.radio_local.clicked.connect(self.check_connection)
        self.ui.radio_remote.clicked.connect(self.check_connection)
        
    def check_connection(self):
        if self.ui.radio_local.isChecked():
            hostname = "localhost"
        else:
            hostname = self.ui.hostname.text()
        try:
            DB = sqlwrap.SqlDB(
                hostname,
                self.ui.port.value(),
                self.ui.user.text(),
                self.ui.password.text())
            #DB.Cur.execute("SELECT VERSION()")
            DB.Cur.execute("SELECT CONNECTION_ID()")
            x = DB.Cur.fetchone()
            DB.close()
        except SQLInitializationError:
            self.ui.label_connection.setText("Not connected")
        else:
            self.ui.label_connection.setText("Connected (MySQL server version {})".format(x[0]))
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()
            
    @staticmethod
    def set(path, parent=None):
        dialog = MySQLOptions(parent)
        result = dialog.exec_()
        return None
    
            
def main():
    app = QtGui.QApplication(sys.argv)
    viewer = MySQLOptions()
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
import mysql_guideUi
import sys

class MySqlGuide(QtGui.QWizard):
    def __init__(self, parent=None):
        
        super(MySqlGuide, self).__init__(parent)
        
        self.ui = mysql_guideUi.Ui_mysql_guide()
        self.ui.setupUi(self)
        logo = QtGui.QPixmap("{}/logo/logo.png".format(sys.path[0]))
        self.ui.logo_label.setPixmap(logo.scaledToHeight(200))
        self.show()
        self.exec_()
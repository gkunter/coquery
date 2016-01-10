# -*- coding: utf-8 -*-
"""
logfile.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
import mysql_guideUi
import sys
import options

class MySqlGuide(QtGui.QWizard):
    def __init__(self, parent=None):
        
        super(MySqlGuide, self).__init__()
        
        self.ui = mysql_guideUi.Ui_mysql_guide()
        self.ui.setupUi(self)
        logo = QtGui.QPixmap("{}/logo/logo.png".format(sys.path[0]))
        self.ui.logo_label.setPixmap(logo.scaledToHeight(200))
        self.show()
        try:
            self.restoreGeometry(options.settings.value("sqlguide_geometry"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("sqlguide_geometry", self.saveGeometry())
        
    @staticmethod
    def display(parent=None):
        guide = MySqlGuide(parent)
        options.cfg.main_window.widget_list.append(guide)

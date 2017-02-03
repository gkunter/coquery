# -*- coding: utf-8 -*-
"""
mysql_guide.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import sys

from coquery import options
from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window
from .ui.mysql_guideUi import Ui_mysql_guide

class MySqlGuide(QtWidgets.QWizard):
    def __init__(self, parent=None):
        
        super(MySqlGuide, self).__init__()
        
        self.ui = Ui_mysql_guide()
        self.ui.setupUi(self)
        logo = QtWidgets.QPixmap("{}/logo/logo.png".format(sys.path[0]))
        self.ui.logo_label.setPixmap(logo.scaledToHeight(200))
        self.show()
        try:
            self.resize(options.settings.value("sqlguide_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("sqlguide_size", self.size())
        
    @staticmethod
    def display(parent=None):
        guide = MySqlGuide(parent)
        get_toplevel_window().widget_list.append(guide)

# -*- coding: utf-8 -*-
"""
about.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import sys

from coquery import options
from coquery.defines import * 
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtGui
from .ui.aboutUi import Ui_AboutDialog

class AboutDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        
        super(AboutDialog, self).__init__(parent)
        def has(module_flag):
            return "yes" if module_flag else "no"
        
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        
        icon = options.cfg.main_window.get_icon("title.png", small_n_flat=False).pixmap(self.size())
        image = QtGui.QImage(icon.toImage())
        painter = QtGui.QPainter(image)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(image.rect(), QtCore.Qt.AlignBottom, "Version {}".format(VERSION))
        painter.end()
        self.ui.label_pixmap.setPixmap(QtGui.QPixmap.fromImage(image))
        self.ui.label_pixmap.setAlignment(QtCore.Qt.AlignCenter)

        s = utf8(self.ui.label_description.text())
        self.ui.label_description.setText(s.format(version=VERSION, date=DATE))

        self.ui.modules.setText("Check optional modules")
        l = []
        for name, flag in (("Seaborn", options._use_seaborn),
                  ("PyMySQL", options._use_mysql),
                  ("NLTK", options._use_nltk),
                  ("tgt", options._use_tgt),
                  ("chardet", options._use_chardet),
                  ("PDFMiner" if sys.version_info < (3, 0) else "pdfminer3k", options._use_pdfminer),
                  ("python-docx", options._use_docx),
                  ("odfpy", options._use_odfpy),
                  ("BeautifulSoup", options._use_bs4)):
            _, _, description, url = MODULE_INFORMATION[name]
            
            l.append("<tr><td><a href='{url}'>{name}</a></td><td>{description}</td><td>{available}</td></tr>".format(
                url=url, name=name, description=description, available=has(flag)))
        self.ui.available_label = QtGui.QLabel("<table cellspacing='3'>{}</table>".format("".join(l)))
        
        self.ui.notes_scroll = QtGui.QScrollArea()                                                                                      
        self.ui.notes_scroll.setWidgetResizable(True)
        self.ui.notes_scroll.setWidget(self.ui.available_label)        

        self.ui.modules.replaceBox(self.ui.notes_scroll)
        self.ui.verticalLayout.insertWidget(2, self.ui.modules)
        
    @staticmethod
    def view(parent=None):
        dialog = AboutDialog(parent=None)
        dialog.exec_()

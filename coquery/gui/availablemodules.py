# -*- coding: utf-8 -*-
"""
availablemodules.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import re
import sys

from coquery import options
from coquery.defines import * 
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window
from .ui.availableModulesUi import Ui_AvailableModules

class AvailableModulesDialog(QtWidgets.QDialog):
    @staticmethod
    def has(module_flag):
        return "yes" if module_flag else "no"

    def __init__(self, parent=None):
        super(AvailableModulesDialog, self).__init__(parent)
        self._links = {}
        
        self.ui = Ui_AvailableModules()
        self.ui.setupUi(self)
        self.ui.table_modules.setHorizontalHeaderLabels(["Module", "Available", "Description"])

        modules = [
                ("cachetools", options.use_cachetools),
                ("PyMySQL", options.use_mysql),
                ("Seaborn", options.use_seaborn),
                ("statsmodels", options.use_statsmodels),
                ("NLTK", options.use_nltk),
                ("tgt", options.use_tgt),
                ("chardet", options.use_chardet),
                ("PDFMiner" if sys.version_info < (3, 0) else "pdfminer3k", options.use_pdfminer),
                ("python-docx", options.use_docx),
                ("odfpy", options.use_odfpy),
                ("BeautifulSoup", options.use_bs4),
                ]
        if sys.platform.startswith("linux"):
            modules.insert(0, ("alsaaudio", options.use_alsaaudio))
        
        self.ui.table_modules.setRowCount(len(modules))
        
        for i, (name, flag) in enumerate(modules):
            _, _, description, url = MODULE_INFORMATION[name]
            
            name_item = QtWidgets.QTableWidgetItem(name)
            status_item = QtWidgets.QTableWidgetItem(self.has(flag))
            desc_item = QtWidgets.QTableWidgetItem(re.sub("<[^<]+?>", "", description))
            self._links[id(name_item)] = url
            
            if flag:
                status_item.setIcon(get_toplevel_window().get_icon("Checked Checkbox"))
            else:
                status_item.setIcon(get_toplevel_window().get_icon("Unchecked Checkbox"))

            
            self.ui.table_modules.setItem(i, 0, name_item)
            self.ui.table_modules.setItem(i, 1, status_item)
            self.ui.table_modules.setItem(i, 2, desc_item)
        
        self.ui.table_modules.setWordWrap(True)
        self.ui.table_modules.resizeRowsToContents()
        self.ui.table_modules.itemClicked.connect(self.open_url)
        
    def open_url(self, item):
        try:
            import webbrowser
            webbrowser.open(self._links[id(item)])
        except AttributeError:
            pass
        
    @staticmethod
    def view(parent=None):
        dialog = AvailableModulesDialog(parent=None)
        dialog.exec_()

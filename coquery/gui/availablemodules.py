# -*- coding: utf-8 -*-
"""
availablemodules.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""


import re
import sys
from PyQt5 import QtWidgets

from coquery import options
from coquery.defines import MODULE_INFORMATION
from .ui.availableModulesUi import Ui_AvailableModules
from .app import get_icon


class AvailableModulesDialog(QtWidgets.QDialog):
    @staticmethod
    def has(module_flag):
        return "yes" if module_flag else "no"

    def __init__(self, parent=None):
        super(AvailableModulesDialog, self).__init__(parent)
        self._links = {}

        self.ui = Ui_AvailableModules()
        self.ui.setupUi(self)
        self.ui.table_modules.setHorizontalHeaderLabels(
            ["Module", "Available", "Description"])

        modules = [
                ("cachetools", options.use_cachetools),
                ("PyMySQL", options.use_mysql),
                ("sqlparse", options.use_sqlparse),
                ("Seaborn", options.use_seaborn),
                ("squarify", options.use_squarify),
                ("statsmodels", options.use_statsmodels),
                ("NLTK", options.use_nltk),
                ("tgt", options.use_tgt),
                ("chardet", options.use_chardet),
                ("pdfminer3k", options.use_pdfminer),
                ("python-docx", options.use_docx),
                ("odfpy", options.use_odfpy),
                ("BeautifulSoup", options.use_bs4),
                ("xlrd", options.use_xlrd),
                ("sphfile", options.use_sphfile),
                ("PyMongo", options.use_pymongo),
                ("pyodbc", options.use_pyodbc),
                ("meza", options.use_meza),
                ]
        if sys.platform.startswith("linux"):
            modules.insert(0, ("alsaaudio", options.use_alsaaudio))

        self.ui.table_modules.setRowCount(len(modules))

        for i, (name, flag) in enumerate(modules):
            _, _, description, url = MODULE_INFORMATION[name]

            name_item = QtWidgets.QTableWidgetItem(name)
            status_item = QtWidgets.QTableWidgetItem(self.has(flag))
            desc_item = QtWidgets.QTableWidgetItem(
                re.sub("<[^<]+?>", "", description))
            self._links[id(name_item)] = url
            self._links[id(desc_item)] = url
            self._links[id(status_item)] = url

            if flag:
                status_item.setIcon(get_icon("Checkmark"))
            else:
                status_item.setIcon(get_icon("Delete"))

            self.ui.table_modules.setItem(i, 0, name_item)
            self.ui.table_modules.setItem(i, 1, status_item)
            self.ui.table_modules.setItem(i, 2, desc_item)

        self.ui.table_modules.setWordWrap(True)
        self.ui.table_modules.resizeColumnsToContents()
        self.ui.table_modules.itemClicked.connect(self.open_url)

    def open_url(self, item):
        try:
            import webbrowser
            webbrowser.open(self._links[id(item)])
        except AttributeError:
            pass

    @staticmethod
    def view(parent=None):
        dialog = AvailableModulesDialog(parent=parent)
        dialog.exec_()

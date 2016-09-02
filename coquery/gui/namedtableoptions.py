# -*- coding: utf-8 -*-
"""
namedtableoptions.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import pandas as pd
import numpy as np

from coquery import options
from coquery.errors import *
from .pyqt_compat import QtGui, QtCore

from .csvoptions import MyTableModel, quote_chars, CSVOptionDialog, CSVOptions
from .ui.namedTableOptionsUi import Ui_NamedTableOptions

class NamedTableOptionsDialog(CSVOptionDialog):
    def __init__(self, filename, fields=[], default=None, parent=None, icon=None):
        """
        Parameters
        ----------
        filename : string
        
        fields : dictionary
        """
        super(NamedTableOptionsDialog, self).__init__(filename, default, parent, 
                                                 icon, ui=Ui_NamedTableOptions)

        self.ui.button_word.clicked.connect(lambda: self.map_query_item_type("word"))
        self.ui.button_lemma.clicked.connect(lambda: self.map_query_item_type("lemma"))
        self.ui.button_pos.clicked.connect(lambda: self.map_query_item_type("pos"))
        self.ui.button_transcript.clicked.connect(lambda: self.map_query_item_type("transcript"))
        self.ui.button_gloss.clicked.connect(lambda: self.map_query_item_type("gloss"))
        
        self._selected = 0
        self.map = default.mapping
        
        # make all widget rows the same height (for cosmetic reasons):
        for key, value in fields:
            button_name = "button_{}".format(value.lower())
            edit_name = "edit_{}".format(value.lower())
            setattr(self.ui, button_name, QtGui.QPushButton(key))
            setattr(self.ui, edit_name, QtGui.QLineEdit())
            
            getattr(self.ui, name).clicked.connect(lambda: self.map_query_item_type(value))
        
        # make all buttons the same size:
        max_height = 0
        for name in [x for x in dir(self.ui) if x.startswith(("button", "label", "edit"))]:
            widget = getattr(self.ui, name)
            max_height = max(max_height, widget.sizeHint().height())
        for name in [x for x in dir(self.ui) if x.startswith(("button", "label", "edit"))]:
            widget = getattr(self.ui, name)
            widget.setMinimumHeight(max_height)

        for x in default.mapping:
            getattr(self.ui, "edit_{}".format(x)).setText(self.map[x])

        try:
            self.resize(options.settings.value("namedtableoptions_size"))
        except TypeError:
            pass

    def update_content(self):
        super(NamedTableOptionsDialog, self).update_content()
        self.map = dict()
        self.ui.edit_word.setText("")
        self.ui.edit_lemma.setText("")
        self.ui.edit_pos.setText("")
        self.ui.edit_transcript.setText("")
        self.ui.edit_gloss.setText("")

    def closeEvent(self, event):
        options.settings.setValue("namedtableoptions_size", self.size())
        
    def map_query_item_type(self, label):
        header = self.file_table.columns[self._col_select]
        for key, value in list(self.map.items()):
            if value == self._col_select:
                line_edit = getattr(self.ui, "edit_{}".format(key))
                line_edit.setText("")
                self.map.pop(key)

        self.map[label] = self._col_select
        line_edit = getattr(self.ui, "edit_{}".format(label))
        line_edit.setText(header)
        
    @staticmethod
    def getOptions(path, fields=[], default=None, parent=None, icon=None):
        dialog = NamedTableOptionsDialog(path, fields, default, parent, icon)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            quote = dict(zip(quote_chars.values(), quote_chars.keys()))[
                str(dialog.ui.quote_char.currentText())]

            return CSVOptions(
                sep=utf8(dialog.ui.separate_char.currentText()),
                selected_column=dialog.ui.query_column.value(),
                header=dialog.ui.file_has_headers.isChecked(),
                skip_lines=dialog.ui.ignore_lines.value(),
                encoding=utf8(dialog.ui.combo_encoding.currentText()),
                quote_char=quote,
                mapping=dialog.map,
                dtypes=dialog.file_table.dtypes)
        else:
            return None
        
    
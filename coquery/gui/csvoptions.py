# -*- coding: utf-8 -*-
"""
csvoptions.py is part of Coquery.

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
from .ui.csvOptionsUi import Ui_FileOptions

class MyTableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent, df, skip, *args):
        super(MyTableModel, self).__init__(parent, *args)
        self.df = df
        self.header = self.df.columns.values.tolist()
        self.skip_lines = skip
        
    def rowCount(self, parent):
        return len(self.df.index)

    def columnCount(self, parent):
        return len(self.df.columns.values)

    def data(self, index, role):
        if role == QtCore.Qt.BackgroundRole and index.row() < self.skip_lines:
            return QtGui.QBrush(QtCore.Qt.lightGray)        
        elif role != QtCore.Qt.DisplayRole:
            return None

        column = self.header[index.column()]
        value = self.df.iloc[index.row()][column]  
        if isinstance(value, np.int64):
            return int(value)
        else:
            return value

    def headerData(self, col, orientation, role):
        if not self.header or col > len(self.header):
            return None
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            try:
                return self.header[col]
            except IndexError:
                return None
        return None

quote_chars = {
    '"': 'Double quote (")',
    "'": "Single quote (')",
    "": "None"}

class CSVOptions(QtGui.QDialog):
    def __init__(self, filename, default=None, parent=None, icon=None):
        super(CSVOptions, self).__init__(parent)
        
        self.filename = filename
        
        self.file_content = None
        
        self.ui = Ui_FileOptions()
        self.ui.setupUi(self)
        
        for x in quote_chars:
            self.ui.quote_char.addItem(quote_chars[x])
        
        self.ui.query_column.setValue(1)

        sep, col, head, skip, quotechar = default
        if sep == "\t":
            sep = "{tab}"
        if sep == " ":
            sep = "{space}"
        index = self.ui.separate_char.findText(sep)
        if index > -1:
            self.ui.separate_char.setCurrentIndex(index)
        else:
            self.ui.separate_char.setEditText(sep)
        self.ui.query_column.setValue(col)
        self.ui.file_has_headers.setChecked(head)
        self.ui.ignore_lines.setValue(skip)
        
        index = self.ui.quote_char.findText(quote_chars[quotechar])
        self.ui.quote_char.setCurrentIndex(index)
            
        self.ui.query_column.valueChanged.connect(self.set_query_column)
        self.ui.ignore_lines.valueChanged.connect(self.update_content)
        self.ui.separate_char.editTextChanged.connect(self.set_new_separator)
        self.ui.file_has_headers.stateChanged.connect(self.update_content)
        self.ui.quote_char.currentIndexChanged.connect(self.update_content)
        self.ui.FilePreviewArea.clicked.connect(self.click_column)

        self.set_new_separator()

        try:
            self.resize(options.settings.value("csvoptions_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("csvoptions_size", self.size())
        
    @staticmethod
    def getOptions(path, default=None, parent=None, icon=None):
        dialog = CSVOptions(path, default, parent, icon)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            quote = dict(zip(quote_chars.values(), quote_chars.keys()))[
                str(dialog.ui.quote_char.currentText())]
            return (str(dialog.ui.separate_char.currentText()),
                 dialog.ui.query_column.value(),
                 dialog.ui.file_has_headers.isChecked(),
                 dialog.ui.ignore_lines.value(),
                 quote)
        else:
            return None
        
    def accept(self):
        super(CSVOptions, self).accept()
        
    def reject(self):
        super(CSVOptions, self).reject()

    #def set_new_skip(self):
        #self.table_model.skip_lines = self.ui.ignore_lines.value()
        #self.ui.FilePreviewArea.reset()
        #self.set_query_column()
        
    def split_file_content(self):
        quote = dict(zip(quote_chars.values(), quote_chars.keys()))[
            str(self.ui.quote_char.currentText())]
        header=0 if self.ui.file_has_headers.isChecked() else None
        try:
            self.file_table = pd.read_table(
                self.filename,
                header=header,
                sep=str(self.separator),
                quoting=3 if not quote else 0,
                quotechar=quote if quote else "#",
                na_filter=False)
        except ValueError as e:
            exception = EmptyInputFileError(self.filename)
            QtGui.QMessageBox.critical(self.parent(), "Query file error", str(exception))
            raise exception
            
    def update_content(self):
        self.split_file_content()
        self.table_model = MyTableModel(self, self.file_table, self.ui.ignore_lines.value())
        self.ui.FilePreviewArea.setModel(self.table_model)
        self.set_query_column()
        self.ui.FilePreviewArea.resizeColumnsToContents()

    def set_new_separator(self):
        sep = str(self.ui.separate_char.currentText())
        if not sep:
            return
        if sep == "{space}":
            self.separator = " "
        elif sep == "{tab}":
            self.separator = "\t"
        elif len(sep) > 1:
            self.separator = self.separator[0]
            self.ui.separate_char.setEditText(sep)
        else:
            self.separator = sep
        self.update_content()

    def set_query_column(self):
        self.ui.FilePreviewArea.selectColumn(self.ui.query_column.value() - 1)

    def click_column(self, index):
        self.ui.query_column.setValue(index.column()+1)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
def main():
    app = QtGui.QApplication(sys.argv)
    print(CSVOptions.getOptions("/home/kunibert/Dev/coquery/coquery/test.csv",
                                default=(",", 1, True, 0, '"')))
    
if __name__ == "__main__":
    main()
    
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import csv
import csvoptionsui
import sys

class MyTableModel(QAbstractTableModel):
    def __init__(self, parent, header, data, skip, *args):
        super(MyTableModel, self).__init__(parent, *args)
        if not data:
            self.content = []
            self.header = []
        else:
            self.content = data
            self.header = header
        self.skip_lines = skip
        
    def rowCount(self, parent):
        return len(self.content)

    def columnCount(self, parent):
        return len(self.content[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.BackgroundRole and index.row() < self.skip_lines:
            return QBrush(Qt.lightGray)        
        elif role != Qt.DisplayRole:
            return None

        row = index.row()
        column = index.column()
        try:
            return self.content[row] [column]
        except IndexError:
            return None

    def headerData(self, col, orientation, role):
        if not self.header or col > len(self.header):
            return QVariant(None)
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return QVariant(self.header[col])
            except IndexError:
                return QVariant(None)
        return QVariant(None)

class CSVOptions(QDialog):
    def __init__(self, filename, default=None, parent=None):
        super(CSVOptions, self).__init__(parent)
        
        self.file_content = None
        
        self.ui = csv_options_ui.Ui_FileOptions()
        self.ui.setupUi(self)
        self.ui.query_column.setValue(1)

        if default:
            sep, col, head, skip = default
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

        self.ui.query_column.valueChanged.connect(self.set_query_column)
        self.ui.ignore_lines.valueChanged.connect(self.set_new_skip)
        self.ui.separate_char.editTextChanged.connect(self.set_new_separator)
        self.ui.file_has_headers.stateChanged.connect(self.toggle_header)
    
        self.ui.FilePreviewArea.clicked.connect(self.click_column)
        self.file_content = open(filename, "rt").readlines()
        if self.ui.file_has_headers.isChecked():
            self.ui.ignore_lines.setMaximum(len(self.file_content) - 1)
        else:
            self.ui.ignore_lines.setMaximum(len(self.file_content))
        self.set_new_separator()
        self.set_query_column()
        
    @staticmethod
    def getOptions(path, default=None, parent=None):
        dialog = CSVOptions(path, default, parent)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            return (str(dialog.ui.separate_char.currentText()),
                 dialog.ui.query_column.value(),
                 dialog.ui.file_has_headers.isChecked(),
                 dialog.ui.ignore_lines.value())
        else:
            return None
        
    def accept(self):
        super(CSVOptions, self).accept()
        
    def reject(self):
        super(CSVOptions, self).reject()

    def set_new_skip(self):
        self.table_model.skip_lines = self.ui.ignore_lines.value()
        self.ui.FilePreviewArea.reset()
        self.set_query_column()
        
    def toggle_header(self):
        if self.ui.file_has_headers.isChecked():
            header = self.file_table[0]
            data = self.file_table[1:]
        else:
            header = []
            data = self.file_table            
        self.table_model = MyTableModel(self, header, data, self.ui.ignore_lines.value())
        self.ui.FilePreviewArea.setModel(self.table_model)
        self.update_tableview()
        if self.ui.file_has_headers.isChecked():
            self.ui.ignore_lines.setMaximum(len(self.file_table) - 1)
        else:
            self.ui.ignore_lines.setMaximum(len(self.file_table))
        self.set_query_column()

    def split_file_content(self):
        self.file_table = []
        self.max_columns = 0
        for x in csv.reader(self.file_content, delimiter=str(self.ui.separate_char.currentText())):
            self.file_table.append(x)
            self.max_columns = max(self.max_columns, len(x))
        for i, x in enumerate(self.file_table):
            if len(x) < self.max_columns:
                x = x + [None] * (self.max_columns - len(x))
                self.file_table[i] = x

    def set_new_separator(self):
        sep = str(self.ui.separate_char.currentText())
        if not sep:
            return
        if sep == "{space}":
            sep = " "
        elif sep == "{tab}":
            sep = "\t"
        if len(sep) > 1:
            sep = sep[0]
            self.ui.separate_char.setEditText(sep)
        self.split_file_content()
        
        if self.ui.file_has_headers.isChecked():
            header = self.file_table[0]
            data = self.file_table[1:]
        else:
            header = []
            data = self.file_table            
        self.table_model = MyTableModel(self, header, data, self.ui.ignore_lines.value())
        self.ui.FilePreviewArea.setModel(self.table_model)
        self.update_tableview()
        self.set_query_column()

    def set_query_column(self):
        self.ui.FilePreviewArea.selectColumn(self.ui.query_column.value() - 1)

    def click_column(self, index):
        self.ui.query_column.setValue(index.column()+1)

    def update_tableview(self):
        if not self.file_table:
            pass
            #self.FilePreviewArea.setColumnCount(0)
            #self.FilePreviewArea.setRowCount(0)
        else:
            #self.FilePreviewArea.setColumnCount(len(self.file_table[0]))
            #self.FilePreviewArea.setRowCount(len(self.file_table))
            
            self.ui.query_column.setMaximum(len(self.file_table[0]))
        
        self.ui.FilePreviewArea.resizeColumnsToContents()
        
    def keyPressEvent(self, e):
        
        if e.key() == Qt.Key_Escape:
            self.close()
            
def main():
    app = QApplication(sys.argv)
    print(CSVOptions.getOptions("~/tmp/tmp2.csv"))
    
if __name__ == "__main__":
    main()
    
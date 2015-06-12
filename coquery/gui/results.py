from __future__ import division

from pyqt_compat import QtCore, QtGui
import os.path
import options
import csv
import resultsUi
import logfile
import sys
import datetime

class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, header, data, *args):
        super(MyTableModel, self).__init__(parent, *args)
        self.content = data
        self.header = header
        self.rownames = range(1, len(data) + 1)
        
    def data(self, index, role):
        if not index.isValid():
            return None
        #elif role == Qt.BackgroundRole and index.row() < self.skip_lines:
            #return QBrush(Qt.lightGray)
        elif role != QtCore.Qt.DisplayRole:
            return None

        row = index.row()
        column = index.column()
        try:
            return self.content[row] [column]
        except IndexError:
            return None

    def rowCount(self, parent):
        return len(self.content)

    def columnCount(self, parent):
        return len(self.header)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.rownames[section])
            else:
                return QtCore.QVariant(None)
            
        if not self.header or section > len(self.header):
            return QtCore.QVariant(None)
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            try:
                return QtCore.QVariant(self.header[section])
            except IndexError:
                return QtCore.QVariant(None)
        return QtCore.QVariant(None)

class ResultsViewer(QtGui.QDialog):
    def __init__(self, Session, parent=None):
        def format_file_size(size):
            if size > 1024**4:
                return "{0:.1f} TiB".format(size/1024**4)
            elif size > 1024**3:
                return "{0:.1f} GiB".format(size/1024**3)
            elif size > 1024**2:
                return "{0:.1f} MiB".format(size/1024**2)
            elif size > 1024:
                return "{0:.1f} KiB".format(size/1024)
            else:
                return "{} bytes".format(size)
        
        super(ResultsViewer, self).__init__(parent)
        
        self.ui = resultsUi.Ui_resultsDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(options.cfg.icon)
        
        # Connect buttons:
        self.ui.button_browse.clicked.connect(self.save_results)
        self.ui.button_quit.clicked.connect(self.accept)
        self.ui.button_restart.clicked.connect(self.reject)
        self.ui.button_logfile.clicked.connect(self.view_logfile)

        # Fill results view:
        self.file_content = [x for x in csv.reader(open(options.cfg.output_path, "rt"))]
        self.table_model = MyTableModel(self, self.file_content[0], self.file_content[1:])
        self.ui.data_preview.setModel(self.table_model)
        self.ui.data_preview.resizeColumnsToContents()
        
        
        diff = (Session.end_time - Session.start_time)
        duration = diff.seconds
        if duration > 3600:
            self.ui.label_time.setText("{} hrs, {}, min, {} s".format(duration // 3600, duration % 3600 // 60, duration % 60))
        elif duration > 60:
            self.ui.label_time.setText("{} min, {}.{} s".format(duration // 60, duration % 60, str(diff.microseconds)[:3]))
        else:
            self.ui.label_time.setText("{}.{} s".format(duration, str(diff.microseconds)[:3]))
        self.ui.row_numbers.setText("{}".format(len(self.file_content) - 1))
        self.ui.file_size.setText(format_file_size(os.path.getsize(options.cfg.output_path)))
        
    def save_results(self):
        name = QtGui.QFileDialog.getSaveFileName(directory="~")
        if type(name) == tuple:
            name = name[0]
        if name:
            with open(name, "wt") as output_file:
                writer = csv.writer(output_file, delimiter=options.cfg.output_separator)
                for x in self.file_content:
                    writer.writerow(x)
                    
    def view_logfile(self):
        logfile.LogfileViewer.view(options.cfg.log_file_path)        

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()
            
def main():
    app = QtGui.QApplication(sys.argv)
    viewer = ResultsViewer()
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    
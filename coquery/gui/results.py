# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

from pyqt_compat import QtCore, QtGui
import os.path
from defines import *
import options
import resultsUi
import logfile
import sys
import copy
import QtProgress
import operator

SORT_NONE = 0
SORT_INC = 1
SORT_DEC = 2
SORT_REV_INC = 3
SORT_REV_DEC = 4

class CoqTableModel(QtCore.QAbstractTableModel):
    """ Define a QAbstractTableModel class that stores the query results so
    that they can be shown in the results view. """
    
    def __init__(self, parent, header, data, *args):
        super(CoqTableModel, self).__init__(parent, *args)
        self.content = data
        self.header = header
        if data:
            self.rownames = range(1, len(data) + 1)
        else:
            self.rownames = None

        self.sort_columns = []
        if self.header:
            self.sort_state = [SORT_NONE] * len(self.header)        
        else:
            self.sort_state = []
        
    def set_header(self, header):
        last_header = self.header
        self.header = header
        if last_header <> self.header:
            self.sort_state = [SORT_NONE] * len(self.header)
            self.sort_columns = []
        
        for i, x in enumerate(header):
            self.setHeaderData(i, QtCore.Qt.Horizontal, x, QtCore.Qt.DecorationRole)
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, len(header))
        
    def set_data(self, data):
        self.content = data
        if data:
            self.rownames = range(1, len(data) + 1)
        else:
            self.rownames = None
        p = self.createIndex(0, 0)
        q = self.createIndex(len(self.content), len(self.content[0]))
        self.dataChanged.emit(p, q)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            try:
                if options.cfg.experimental:
                    return self.content[index.row()][self.header[index.column()]]
                else:
                    return self.content[index.row()] [index.column()]
            except (IndexError, KeyError):
                return None
        elif role == QtCore.Qt.ForegroundRole:
            column = index.column()
            header = self.header[column]
            try:
                col = options.cfg.column_color[header.lower()]
            except KeyError:
                return None
            return QtGui.QColor(col)
        elif role == QtCore.Qt.TextAlignmentRole:
            if self.header[index.column()] == "coq_context_left" or self.sort_state[index.column()] in set([SORT_REV_DEC, SORT_REV_INC]):
                return QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter
        else:
            return None
        
    def headerData(self, index, orientation, role):
        """ Return the header at the given index, taking the sorting settings
        into account. """
        
        # Return row names?
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return self.rownames[index]
            else:
                return None

        # Return column names:
        if not self.header or index > len(self.header):
            return None

        if role == QtCore.Qt.DisplayRole:
            # Get header string?
            column_name = options.cfg.main_window.Session.Corpus.resource.translate_header(self.header[index])
            # Return normal header if not a sort column:
            if index not in self.sort_columns:
                return column_name
            tag_list = []
            
            # Add sorting order number if more than one sorting columns have
            # been selected:
            if len(self.sort_columns) > 1:
                tag_list.append(str(self.sort_columns.index(index)+1))
            
            # Add a "rev" tag if reverse sorting is requested for the column
            if self.sort_state[index] in [SORT_REV_DEC, SORT_REV_INC]:
                tag_list.append("rev")
            
            return "{}{}".format(
                    column_name, 
                    ["", " ({}) ".format(", ".join(tag_list))][bool(tag_list)])

        # Get header decoration (i.e. the sorting arrows)?
        elif role == QtCore.Qt.DecorationRole:
            # add arrows as sorting direction indicators if necessary:
            if self.sort_state[index] in [SORT_DEC, SORT_REV_DEC]:
                return QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_ArrowDown)
            elif self.sort_state[index] in [SORT_INC, SORT_REV_INC]:
                return QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_ArrowUp)
            else:
                return None
        else:
            return None

    def rowCount(self, parent):
        if self.content:
            return len(self.content)
        else:
            return None
        
    def columnCount(self, parent):
        if self.header:
            return len(self.header)
        else:
            return None
        
    def lessThan(self, first, second):
        """ Compare the content of the first row to the content of the
        second. Return True if the first row should be placed above the 
        second row if all sorting columns are considered. """
        
        # if no sorting rows are set, the row with the lower row number
        # should come first:
        if not self.sort_columns:
            return first.row() < second.row()

        # Go through the sorting columns, and compare the two rows in each
        # column. If a comparison already resolves the sorting order, the 
        # following columns are not considered anymore.
        for col in self.sort_columns:
            header = self.header[col]
            state = self.sort_state[col]
            
            # get cell content of first and second row in current column:
            try:
                data_first = self.content[first.row()] [header].lower()
                data_second = self.content[second.row()] [header].lower()
            except AttributeError:
                data_first = self.content[first.row()] [header]
                data_second = self.content[second.row()] [header]

            # reverse the contents if backward sorting is set for the column:
            if state in set([SORT_REV_DEC, SORT_REV_INC]):
                data_first = data_first[::-1]
                data_second = data_second[::-1]

            # compare the rows, and return an appropriate value if one of the
            # two has a lower value than the other:
            if state in set([SORT_DEC, SORT_REV_DEC]):
                if data_first > data_second:
                    return True
                if data_first < data_second:
                    return False
            elif state in set([SORT_INC, SORT_REV_INC]):
                if data_first < data_second:
                    return True
                if data_first > data_second:
                    return False

        # The first row has not been found to have lower values than the
        # second:
        return False
        
    def do_sort(self):
        for col in self.sort_columns[::-1]:
            if self.sort_state[col] in set([SORT_INC, SORT_DEC]):
                key_fun = lambda row: row[self.header[col]]
            elif self.sort_state[col] in set([SORT_REV_INC, SORT_REV_DEC]):
                key_fun = lambda row: row[self.header[col]][::-1]
            else:
                continue
            if self.sort_state[col] in set([SORT_INC, SORT_REV_INC]):
                self.content = sorted(self.content, key=key_fun)
            else:
                self.content = sorted(self.content, key=key_fun, reverse=True)
    
    def sort(self, *args):
        if not self.sort_columns:
            return
        self.layoutAboutToBeChanged.emit()
        options.cfg.main_window.ui.progress_bar.setRange(0, 0)
        self_sort_thread = QtProgress.ProgressThread(
            self.do_sort, self)
        self_sort_thread.taskFinished.connect(self.sort_finished)
        self_sort_thread.taskException.connect(self.exception_during_sort)
        self_sort_thread.start()
        
    def sort_finished(self):
        # Stop the progress indicator:
        options.cfg.main_window.ui.progress_bar.setRange(0, 1)
        self.layoutChanged.emit()

    def exception_during_sort(self):
        options.cfg.main_window.ui.progress_bar.setRange(0, 1)
        options.cfg.main_window.ui.statusbar.showMessage("Error during sorting.")
        error_box.ErrorBox.show(self.exc_info, self.exception)
        
class ResultsViewer(QtGui.QDialog):
    """ Defines a QDialog class that can be used to display the results from
    a query session. """
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
        
        self.Session = Session
        
        self.ui = resultsUi.Ui_resultsDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(options.cfg.icon)
        
        # Connect buttons:
        self.ui.button_browse.clicked.connect(self.save_results)
        self.ui.button_quit.clicked.connect(self.accept)
        self.ui.button_restart.clicked.connect(self.reject)
        self.ui.button_logfile.clicked.connect(self.view_logfile)

        self.table_model = CoqTableModel(self, Session.header, Session.output_storage)

        # make horizontal headers sortable in a special way:
        self.ui.data_preview.horizontalHeader().sectionClicked.connect(self.change_sorting)
        self.ui.data_preview.setModel(self.table_model)
        self.ui.data_preview.setSortingEnabled(False)
        #self.adjust_header_width()

        if not Session.end_time:
            return
        diff = (Session.end_time - Session.start_time)
        duration = diff.seconds
        if duration > 3600:
            self.ui.label_time.setText("{} hrs, {}, min, {} s".format(duration // 3600, duration % 3600 // 60, duration % 60))
        elif duration > 60:
            self.ui.label_time.setText("{} min, {}.{} s".format(duration // 60, duration % 60, str(diff.microseconds)[:3]))
        else:
            self.ui.label_time.setText("{}.{} s".format(duration, str(diff.microseconds)[:3]))
        self.ui.row_numbers.setText("{}".format(len(Session.output_storage)))
        
    def save_results(self):
        name = QtGui.QFileDialog.getSaveFileName(directory="~")
        if type(name) == tuple:
            name = name[0]
        if name:
            with open(name, "wt") as output_file:
                writer = UnicodeWriter(output_file, delimiter=options.cfg.output_separator)
                writer.writerow(self.Session.header)
                for y in range(self.table_model.rowCount()):
                    writer.writerow([QtCore.QString(self.table_model.index(y, x).data()) for x in range(self.table_model.columnCount())])
                    
    def view_logfile(self):
        logfile.LogfileViewer.view(options.cfg.log_file_path)        

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()
            
    def change_sorting(self, index):
        header = self.ui.data_preview.horizontalHeader()

        if not self.table_model.sort_state[index]:
            self.table_model.sort_columns.append(index)
        self.table_model.sort_state[index] += 1
        
        probe_index = self.table_model.createIndex(0, index)
        probe_cell = probe_index.data()
        if type(probe_cell) in [unicode, str, QtCore.QString]:
            max_state = SORT_REV_DEC
        else:
            max_state = SORT_DEC

        if self.table_model.sort_state[index] > max_state:
            self.table_model.sort_state[index] = SORT_NONE
            self.table_model.sort_columns.remove(index)

        self.table_model.sort(0, QtCore.Qt.AscendingOrder)

    def adjust_header_width(self):
        old_sort_state = copy.copy(self.table_model.sort_state)
        old_sort_columns = copy.copy(self.table_model.sort_columns)
        self.table_model.sort_state = [SORT_REV_DEC] * len(self.table_model.header)
        self.table_model.sort_columns = range(len(self.table_model.header))
        self.table_model.sort_state = old_sort_state
        self.table_model.sort_columns = old_sort_columns

        
def main():
    app = QtGui.QApplication(sys.argv)
    viewer = ResultsViewer()
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    
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
import error_box

SORT_NONE = 0
SORT_INC = 1
SORT_DEC = 2
SORT_REV_INC = 3
SORT_REV_DEC = 4

import pandas as pd
import numpy as np

class CoqTableModel(QtCore.QAbstractTableModel):
    """ Define a QAbstractTableModel class that stores the query results in a 
    pandas DataFrame object. It provides the required methods so that they 
    can be shown in the results view. """
    
    def __init__(self, parent, *args):
        super(CoqTableModel, self).__init__(parent, *args)
        self.last_header = None
        self.sort_columns = []
        self.header = []
        self.set_data(pd.DataFrame())

        
    def set_header(self, header): 
        self.header = [x for x in self.content.columns.values if not x.startswith("coquery_invisible")]
        for i, x in enumerate(x):
            self.setHeaderData(i, QtCore.Qt.Horizontal, x, QtCore.Qt.DecorationRole)
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, len(self.header))
        self.sort_state = [SORT_NONE] * len(self.header)
        # remember the current header:
        self.last_header = self.header

    def reorder_data(self, new_order):
        self.content = self.content.reindex(columns=new_order)
        # notify the GUI that the whole data frame has changed:
        self.dataChanged.emit(
            self.createIndex(0, 0), 
            self.createIndex(self.rowCount(), self.columnCount()))

    def set_data(self, data=None):
        """ Set the content of the table model to the given data, using a
        pandas DataFrame object. """
        # create a pandas DataFrame for the provided data:
        if not isinstance(data, pd.DataFrame):
            self.content = pd.DataFrame(data)
        else:
            self.content = data
        
        self.rownames = self.content.index
        # try to set the columns to the output order of the current session
        try:
            self.reorder_data(options.cfg.main_window.Session.output_order)
        except AttributeError:
            # even if that failed, emit a signal that the data has changed:
            self.dataChanged.emit(
                self.createIndex(0, 0), 
                self.createIndex(self.rowCount(), self.columnCount()))

    def column(self, i):
        """ Return the name of the column in the pandas data frame at index 
        position 'i'. """
        return self.header[i]

    def data(self, index, role):
        """ Return a representation of the data cell indexed by 'index', 
        using the specified Qt role. """
        
        if not index.isValid():
            return None
        
        # DisplayRole: return the content of the cell in the data frame:
        if role == QtCore.Qt.DisplayRole:
            try:
                return self.content.iloc[index.row()][self.header[index.column()]]
            except (IndexError, KeyError):
                return None

        # ForegroundRole: return the colour of the column, or the default if
        # no color is specified:
        elif role == QtCore.Qt.ForegroundRole:
            header = self.column(index.column())
            if options.cfg.column_visibility.get(
                self.header[index.column()], True):
                try:
                    col = options.cfg.column_color[header.lower()]
                    return QtGui.QColor(col)
                except KeyError:
                    return None
            else:
                return QtGui.QColor("lightgrey")
                
        # TextAlignmentRole: return the alignment of the column:
        elif role == QtCore.Qt.TextAlignmentRole:
            column = self.column(index.column())
            # integers and floats are always right-aligned:
            if self.content[column].dtype in (np.float64, np.int64):
                return int(QtCore.Qt.AlignRight)|int(QtCore.Qt.AlignVCenter)
            # right-align the left context as well as columns with reverse 
            # sorting enabled:
            if column == "coq_context_left" or self.sort_state[index.column()] in set([SORT_REV_DEC, SORT_REV_INC]):
                return int(QtCore.Qt.AlignRight)|int(QtCore.Qt.AlignVCenter)
        
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

        if role == QtCore.Qt.DisplayRole:
            if not options.cfg.column_visibility.get(
                self.header[index], True):
                return "[hidden]"
            
            # Get header string?
            column = self.column(index)
            
            # do not return a header string for invisible columns:
            if column.startswith("coquery_invisible"):
                return None
            
            display_name = options.cfg.main_window.Session.Corpus.resource.translate_header(column)
            # Return normal header if not a sort column:
            if index not in self.sort_columns:
                return display_name
            tag_list = []
            
            # Add sorting order number if more than one sorting columns have
            # been selected:
            if len(self.sort_columns) > 1:
                tag_list.append(str(self.sort_columns.index(index)+1))
            
            # Add a "rev" tag if reverse sorting is requested for the column
            if self.sort_state[index] in [SORT_REV_DEC, SORT_REV_INC]:
                tag_list.append("rev")
            
            return "{}{}".format(
                    display_name, 
                    ["", " ({}) ".format(", ".join(tag_list))][bool(tag_list)])

        # Get header decoration (i.e. the sorting arrows)?
        elif role == QtCore.Qt.DecorationRole:
            if not options.cfg.column_visibility.get(
            self.header[index], True):
                return None
            # add arrows as sorting direction indicators if necessary:
            if self.sort_state[index] in [SORT_DEC, SORT_REV_DEC]:
                return QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_ArrowUp)
            elif self.sort_state[index] in [SORT_INC, SORT_REV_INC]:
                return QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_ArrowDown)
            else:
                return None
        return None

    def rowCount(self, parent=None):
        """ Return the number of rows. """
        return len(self.content.index)
        
    def columnCount(self, parent=None):
        """ Return the number of columns, ignoring all invisible columns. """
        return len([x for x in self.header if not x.startswith("coquery_invisible")])
        
    def do_sort(self):
        """ Sort the content data frame by taking all sorting columns and 
        their settings into account. """
        
        sort_columns = []
        del_columns = []
        directions = []
        # go through all sort columns:
        for col in self.sort_columns:
            if not options.cfg.column_visibility.get(self.column(col), True):
                continue
            # add a temporary column if reverse sorting is requested:
            if self.sort_state[col] in set([SORT_REV_DEC, SORT_REV_INC]):
                name = "{}_rev".format(self.column(col))
                del_columns.append(name)
                self.content[name] = self.content[self.column(col)].apply(lambda x: x[::-1])
            else:
                name = self.column(col)
            # add the sorting direction
            directions.append(self.sort_state[col] in set([SORT_INC, SORT_REV_INC]))
            sort_columns.append(name)
            
        # sort the data frame:
        self.content.sort(
            columns=sort_columns, ascending=directions,
            axis="index", inplace=True)
        # remove all temporary columns:
        self.content.drop(labels=del_columns, axis="columns", inplace=True)
            
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
        

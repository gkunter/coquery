# -*- coding: utf-8 -*-

"""
results.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division

from pyqt_compat import QtCore, QtGui, pyside
import os.path
from defines import *
import options
import resultsUi
import sys
import copy
import QtProgress
import error_box
import collections

import pandas as pd
import numpy as np

class CoqTableModel(QtCore.QAbstractTableModel):
    """ Define a QAbstractTableModel class that stores the query results in a 
    pandas DataFrame object. It provides the required methods so that they 
    can be shown in the results view. """
    
    def __init__(self, parent, *args):
        super(CoqTableModel, self).__init__(parent, *args)
        self.last_header = None

        # sort_columns is an OrderedDict that stores the sorting information
        # for the table. The keys of sort_columns are the feature names of
        # the sorting columns. The associated values are the sorting modes.
        self.sort_columns = collections.OrderedDict()
        
        self.header = []
        self.set_data(pd.DataFrame())
        
    def set_header(self, header = None): 
        self.header = [x for x in self.content.columns.values if not x.startswith("coquery_invisible")]
        for i, x in enumerate(self.header):
            self.setHeaderData(i, QtCore.Qt.Horizontal, x, QtCore.Qt.DecorationRole)
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, len(self.header))
        
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
        self.content = data
        self.rownames = list(self.content.index.values)
        # try to set the columns to the output order of the current session
        try:
            self.reorder_data(options.cfg.main_window.Session.output_order)
        except AttributeError:
            # even if that failed, emit a signal that the data has changed:
            self.dataChanged.emit(
                self.createIndex(0, 0), 
                self.createIndex(self.rowCount(), self.columnCount()))

    def data(self, index, role):
        """ Return a representation of the data cell indexed by 'index', 
        using the specified Qt role. """
        
        if not index.isValid():
            return None
        
        # DisplayRole: return the content of the cell in the data frame:
        # ToolTipRole: also returns the cell content, but in a form suitable
        # for QHTML:
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.ToolTipRole:
            column = self.header[index.column()]
            value = self.content.iloc[index.row()][column] 
            
            if isinstance(value, (float, np.float64)):
                format_string = "{:.%if}" % options.cfg.digits
            else:
                format_string = "{}"
            
            if role == QtCore.Qt.ToolTipRole:
                return "<div>{}</div>".format(QtCore.Qt.escape(format_string.format(value)))
            else:
                return format_string.format(value)
            
        # ForegroundRole: return the colour of the column, or the default if
        # no color is specified:
        elif role == QtCore.Qt.ForegroundRole:
            header = self.header[index.column()]
            row = self.content.index[index.row()]
            # Check if cell is in a visible row and visible column:
            if options.cfg.column_visibility.get(header, True) and options.cfg.row_visibility.get(row, True):
                # return row color if specified:
                try:
                    col = options.cfg.row_color[row]
                    return QtGui.QColor(col)
                except KeyError:
                    pass
                # return column color if specified:
                try:
                    col = options.cfg.column_color[header]
                    return QtGui.QColor(col)
                except KeyError:
                    # return default color
                    return None
            else:
                # return light grey for hidden cells:
                return QtGui.QColor("lightgrey")
                
        # TextAlignmentRole: return the alignment of the column:
        elif role == QtCore.Qt.TextAlignmentRole:
            column = self.header[index.column()]
            # integers and floats are always right-aligned:
            if self.content[column].dtype in (np.float64, np.int64):
                return int(QtCore.Qt.AlignRight)|int(QtCore.Qt.AlignVCenter)
            # right-align the left context as well as columns with reverse 
            # sorting enabled:
            if column == "coq_context_left" or self.sort_columns.get(column, SORT_NONE) in set([SORT_REV_DEC, SORT_REV_INC]):
                return int(QtCore.Qt.AlignRight)|int(QtCore.Qt.AlignVCenter)
            return int(QtCore.Qt.AlignLeft)|int(QtCore.Qt.AlignVCenter)
        return None
        
    def headerData(self, index, orientation, role):
        """ Return the header at the given index, taking the sorting settings
        into account. """
        
        # Return row names?
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(self.rownames[index])
            else:
                return None

        # Get header string:
        column = self.header[index]

        if role == QtCore.Qt.DisplayRole:
            if not options.cfg.column_visibility.get(column, True):
                return "[hidden]"
            
            # do not return a header string for invisible columns:
            if column.startswith("coquery_invisible"):
                return None

            display_name = options.cfg.main_window.Session.translate_header(column)
            # Return normal header if not a sort column:
            if column not in self.sort_columns:
                return display_name
            
            tag_list = []
            # Add sorting order number if more than one sorting columns have
            # been selected:
            if len(self.sort_columns) > 1:
                sorting_position = list(self.sort_columns.keys()).index(column)
                tag_list.append("{}".format(sorting_position + 1))
            
            # Add a "rev" tag if reverse sorting is requested for the column
            if self.sort_columns[column] in [SORT_REV_DEC, SORT_REV_INC]:
                tag_list.append("rev")
            
            return "{}{}".format(
                    display_name, 
                    ["", " ({}) ".format(", ".join(tag_list))][bool(tag_list)])

        # Get header decoration (i.e. the sorting arrows)?
        elif role == QtCore.Qt.DecorationRole:
            # no decorator for hidden columns:
            if not options.cfg.column_visibility.get(column, True):
                return None
            if column not in self.sort_columns:
                return
            # add arrows as sorting direction indicators if necessary:
            if self.sort_columns[column] in [SORT_DEC, SORT_REV_DEC]:
                return QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_ArrowUp)
            elif self.sort_columns[column] in [SORT_INC, SORT_REV_INC]:
                return QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_ArrowDown)
            else:
                return None
        return None

    def rowCount(self, parent=None):
        """ Return the number of rows. """
        try:
            return len(self.content.index)
        except AttributeError:
            return 0
        
    def columnCount(self, parent=None):
        """ Return the number of columns, ignoring all invisible columns. """
        return len([x for x in self.header if not x.startswith("coquery_invisible")])
        
    def do_sort(self):
        """ Sort the content data frame by taking all sorting columns and 
        their settings into account. """
        
        sort_order = []
        del_columns = []
        directions = []
        # go through all sort columns:
        for col in list(self.sort_columns.keys()):
            if not options.cfg.column_visibility.get(col, True):
                continue
            if not col in self.content.columns.values:
                self.sort_columns.pop(col)
                continue
            # add a temporary column if reverse sorting is requested:
            if self.sort_columns[col] in set([SORT_REV_DEC, SORT_REV_INC]):
                name = "{}_rev".format(col)
                del_columns.append(name)
                self.content[name] = self.content[col].apply(lambda x: x[::-1])
            else:
                name = col
            # add the sorting direction
            directions.append(self.sort_columns[col] in set([SORT_INC, SORT_REV_INC]))
            sort_order.append(name)
            
        if sort_order:
            # sort the data frame:
            self.content.sort(
                columns=sort_order, ascending=directions,
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

def get_background(option, index):
    if option.state & QtGui.QStyle.State_Selected:
        return options.cfg.app.palette().color(QtGui.QPalette().Highlight)
    else:
        return index.data(QtCore.Qt.BackgroundRole)

def get_foreground(option, index):
    if option.state & QtGui.QStyle.State_MouseOver:
        return options.cfg.app.palette().color(QtGui.QPalette().Link)
    elif option.state & QtGui.QStyle.State_Selected:
        return options.cfg.app.palette().color(QtGui.QPalette().HighlightedText)
    else:
        return index.data(QtCore.Qt.ForegroundRole)

class CoqResultCellDelegate(QtGui.QStyledItemDelegate):
    def sizeHint(self, option, index):
        rect = options.cfg.metrics.boundingRect(unicode(index.data(QtCore.Qt.DisplayRole)))
        return rect.adjusted(0, 0, 15, 0).size()
    
    def paint(self, painter, option, index):
        """
        Paint the results cell.
        
        The paint method of the cell delegates takes the representation
        from the table's :func:`data` method, using the DecorationRole role.
        On mouse-over, the cell is rendered like a clickable link.
        """
        content = unicode(index.data(QtCore.Qt.DisplayRole))
        if not content:
            return
        painter.save()

        align = index.data(QtCore.Qt.TextAlignmentRole)
        
        # show content as a link on mouse-over:
        if option.state & QtGui.QStyle.State_MouseOver:
            font = painter.font()
            font.setUnderline(True)
            painter.setFont(font)
        fg = get_foreground(option, index)
        bg = get_background(option, index)
        if bg:
            painter.setBackgroundMode(QtCore.Qt.OpaqueMode)
            painter.setBackground(bg)
            painter.fillRect(option.rect, bg)
        painter.setPen(QtGui.QPen(fg))
        try:
            if align & QtCore.Qt.AlignLeft:
                painter.drawText(option.rect.adjusted(2, 0, 2, 0), index.data(QtCore.Qt.TextAlignmentRole), content)
            else:
                painter.drawText(option.rect.adjusted(-2, 0, -2, 0), index.data(QtCore.Qt.TextAlignmentRole), content)
        finally:
            painter.restore()

class CoqProbabilityDelegate(CoqResultCellDelegate):
    def get_background(self, option, index):
        value = float(index.data(QtCore.Qt.DisplayRole))
        if  value > 1:
            return QtGui.QColor("lightyellow")
        else:
            return super(CoqProbabilityDelegate, self).get_background(option, index)
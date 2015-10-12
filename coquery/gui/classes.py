# -*- coding: utf-8 -*-

"""
classes.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
import collections
import numpy as np
import pandas as pd

import __init__
from pyqt_compat import QtCore, QtGui
import queryfilter
import options
import queries
from defines import *

class CoqTreeItem(QtGui.QTreeWidgetItem):
    """ 
    Define a tree element class that stores the output column options in
    the options tree. 
    """
    def __init__(self, *args, **kwargs):
        super(CoqTreeItem, self).__init__(*args, **kwargs)
        self._objectName = ""
        self._link_by = None
        self._func = None

    def setText(self, column, text, *args):
        super(CoqTreeItem, self).setText(column, text)
        if self.parent():
            parent = self.parent().objectName()
        feature = unicode(self.objectName())
        if feature.endswith("_table"):
            self.setToolTip(column, "Table: {}".format(text))
        elif feature.startswith("coquery_") or feature.startswith("frequency_"):
            self.setToolTip(column, "Special column:\n{}".format(text))
        else:
            self.setToolTip(column, "Data column:\n{}".format(text))

    def setObjectName(self, name):
        """ Store resource variable name as object name. """
        self._objectName = unicode(name)

    def objectName(self):
        """ Retrieve resource variable name from object name. """
        return self._objectName

    def check_children(self, column=0):
        """ 
        Compare the check state of all children.
        
        Parameters
        ----------
        column : int (default=0)
            The column of the tree widget
            
        Returns
        -------
        state : bool
            True if all children have the same check state, False if at least
            one child has a different check state than another.
        """
        child_states = set([])
        for child in [self.child(i) for i in range(self.childCount())]:
            child_states.add(child.checkState(column))
        return len(child_states) == 1

    def update_checkboxes(self, column, expand=False):
        """ 
        Propagate the check state of the item to the other tree items.
        
        This method propagates the check state of the current item to its 
        children (e.g. if the current item is checked, all children are also 
        checked). It also toggles the check state of the parent, but only if
        the current item is a native feature of the parent, and not a linked 
        table. 
        
        If the argument 'expand' is True, the parents of items with checked 
        children will be expanded. 
        
        Parameters
        ----------
        column : int
            The nubmer of the column
        expand : bool
            If True, a parent node will be expanded if the item is checked
        """
        check_state = self.checkState(column)

        if check_state == QtCore.Qt.PartiallyChecked:
            # do not propagate a partially checked state
            return
        
        if str(self._objectName).endswith("_table") and check_state:
            self.setExpanded(True)
        
        # propagate check state to children:
        for child in [self.child(i) for i in range(self.childCount())]:
            child.setCheckState(column, check_state)
        # adjust check state of parent, but not if linked:
        if self.parent() and not self._link_by:
            if not self.parent().check_children():
                self.parent().setCheckState(column, QtCore.Qt.PartiallyChecked)
            else:
                self.parent().setCheckState(column, check_state)
            if expand:
                if self.parent().checkState(column) in (QtCore.Qt.PartiallyChecked, QtCore.Qt.Checked):
                    self.parent().setExpanded(True)

class CoqTreeLinkItem(CoqTreeItem):
    """
    Define a CoqTreeItem class that represents a linked table.
    """
    def setLink(self, from_item, link):
        self._link_by = (from_item, link)
        
    def setText(self, column, text, *args):
        super(CoqTreeLinkItem, self).setText(column, text)
        source, target = text.split(" ► ")
        self.setToolTip(column, "External table:\n{},\nlinked by column:\n{}".format(target, source))

class CoqTreeFuncItem(CoqTreeItem):
    """
    Define a CoqTreeItem class that represents a function column.
    """
    def setFunction(self, func):
        self._func = func
        
    def setText(self, column, label, *args):
        super(CoqTreeFuncItem, self).setText(column, label)

class CoqTreeWidget(QtGui.QTreeWidget):
    """
    Define a tree widget that stores the available output columns in a tree 
    with check boxes for each variable. 
    """
    addLink = QtCore.Signal(CoqTreeItem)
    addFunction = QtCore.Signal(CoqTreeItem)
    removeItem = QtCore.Signal(CoqTreeItem)
    
    def __init__(self, *args):
        super(CoqTreeWidget, self).__init__(*args)
        self.itemChanged.connect(self.update)
        self.setDragEnabled(True)
        self.setAnimated(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

    def update(self, item, column):
        """ Update the checkboxes of parent and child items whenever an
        item has been changed. """
        item.update_checkboxes(column)

    def setCheckState(self, object_name, state, column=0):
        """ Set the checkstate of the item that matches the object_name. If
        the state is Checked, also expand the parent of the item. """
        if type(state) != QtCore.Qt.CheckState:
            if state:
                state = QtCore.Qt.Checked
            else:
                state = QtCore.Qt.Unchecked
        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            if root.objectName() == object_name:
                root.setChecked(column, state)
                self.update(root, column)
            for child in [root.child(i) for i in range(root.childCount())]:
                if child.objectName() == object_name:
                    child.setCheckState(column, state)
                    if state == QtCore.Qt.Checked:
                        root.setExpanded(True)
                    self.update(child, column)
                    return
                
    def mimeData(self, *args):
        """ Add the resource variable name to the MIME data (for drag and 
        drop). """
        value = super(CoqTreeWidget, self).mimeData(*args)
        value.setText(", ".join([x.objectName() for x in args[0]]))
        return value
    
    def get_checked(self, column = 0):
        check_list = []
        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            for child in [root.child(i) for i in range(root.childCount())]:
                if child.checkState(column) == QtCore.Qt.Checked:
                    check_list.append(str(child._objectName))
        return check_list

    def show_menu(self, point):
        item = self.itemAt(point)
        if not item:
            return

        if str(item.objectName()).startswith("coquery") or str(item.objectName()).startswith("frequency_"):
            return

        # show self.menu about the column
        self.menu = QtGui.QMenu("Output column options", self)
        action = QtGui.QWidgetAction(self)
        label = QtGui.QLabel("<b>{}</b>".format(item.text(0)), self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        action.setDefaultWidget(label)
        self.menu.addAction(action)
        
        if not str(item.objectName()).endswith("_table"):
            view_unique = QtGui.QAction("View &unique values", self)
            view_unique.triggered.connect(lambda: self.show_unique_values(item))
            self.menu.addAction(view_unique)
            self.menu.addSeparator()

            add_link = QtGui.QAction("&Link to external table", self)
            add_function = QtGui.QAction("&Add a function", self)
            remove_link = QtGui.QAction("&Remove link", self)
            remove_function = QtGui.QAction("&Remove function", self)
            
            parent = item.parent()
            
            if item._link_by or (parent and parent._link_by):
                self.menu.addAction(remove_link)
            elif item._func:
                self.menu.addAction(remove_function)
            else:
                self.menu.addAction(add_link)
                self.menu.addAction(add_function)
            
            self.menu.popup(self.mapToGlobal(point))
            action = self.menu.exec_()

            if action == add_link:
                self.addLink.emit(item)
            elif action == add_function:
                self.addFunction.emit(item)
            elif action in (remove_link, remove_function):
                self.removeItem.emit(item)
            

    def show_unique_values(self, item):
        import uniqueviewer
        uniqueviewer.UniqueViewer.show(item.objectName(), options.cfg.main_window.resource)

class LogTableModel(QtCore.QAbstractTableModel):
    """
    Define a QAbstractTableModel class that stores logging messages.
    """
    def __init__(self, parent, *args):
        super(LogTableModel, self).__init__(parent, *args)
        self.content = options.cfg.gui_logger.log_data
        self.header = ["Date", "Time", "Level", "Message"]
        
    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()
        
        record = self.content[row]
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return record.asctime.split()[0]
            elif column == 1:
                return record.asctime.split()[1]
            elif column == 2:
                return record.levelname
            elif column == 3:
                return record.message            
        elif role == QtCore.Qt.ForegroundRole:
            if record.levelno in [logging.ERROR, logging.CRITICAL]:
                return QtGui.QBrush(QtCore.Qt.white)
            else:
                return None
        elif role == QtCore.Qt.BackgroundRole:
            if record.levelno == logging.WARNING:
                return QtGui.QBrush(QtCore.Qt.yellow)
            elif record.levelno in [logging.ERROR, logging.CRITICAL]:
                return QtGui.QBrush(QtCore.Qt.red)
        else:
            return None
        
    def rowCount(self, parent):
        return len(self.content)

    def columnCount(self, parent):
        return len(self.header)

class LogProxyModel(QtGui.QSortFilterProxyModel):
    """
    Define a QSortFilterProxyModel that manages access to the logging 
    messages.
    """
    def headerData(self, index, orientation, role):
        # column names:
        if orientation == QtCore.Qt.Vertical:
            return None
        header = self.sourceModel().header
        if not header or index > len(header):
            return None
        
        if role == QtCore.Qt.DisplayRole:
            return header[index]

class CoqTextEdit(QtGui.QTextEdit):
    """
    Defines a QTextEdit class that accepts dragged objects.
    """
    def __init__(self, *args):
        super(CoqTextEdit, self).__init__(*args)
        self.setAcceptDrops(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dragMoveEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        # get the relative position from the mime data
        mime = e.mimeData().text()
        
        if "application/x-qabstractitemmodeldatalist" in e.mimeData().formats():
            label = e.mimeData().text()
            if label == "word_label":
                self.insertPlainText("*")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "word_pos":
                self.insertPlainText(".[*]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "lemma_label":
                self.insertPlainText("[*]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "lemma_transcript":
                self.insertPlainText("[/*/]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "word_transcript":
                self.insertPlainText("/*/")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
        elif e.mimeData().hasText():
            self.insertPlainText(e.mimeData().text())
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
        #x, y = map(int, mime.split(','))

        #if e.keyboardModifiers() & QtCore.Qt.ShiftModifier:
            ## copy
            ## so create a new button
            #button = Button('Button', self)
            ## move it to the position adjusted with the cursor position at drag
            #button.move(e.pos()-QtCore.QPoint(x, y))
            ## show it
            #button.show()
            ## store it
            #self.buttons.append(button)
            ## set the drop action as Copy
            #e.setDropAction(QtCore.Qt.CopyAction)
        #else:
            ## move
            ## so move the dragged button (i.e. event.source())
            #e.source().move(e.pos()-QtCore.QPoint(x, y))
            ## set the drop action as Move
            #e.setDropAction(QtCore.Qt.MoveAction)
        # tell the QDrag we accepted it
        e.accept()

    def setAcceptDrops(self, *args):
        super(CoqTextEdit, self).setAcceptDrops(*args)

class QueryFilterBox(queryfilter.CoqTagBox):
    """
    Define a CoqTagBox that manages query filters.
    """
    def destroyTag(self, tag):
        """
        Remove the tag from the tag cloud as well as the filter from the 
        global filter list. 
        """
        options.cfg.filter_list = [x for x in options.cfg.filter_list if x.text != str(tag.text())]
        super(QueryFilterBox, self).destroyTag(tag)
    
    def addTag(self, *args):
        """ 
        Add the tag to the tag cloud and the global filter list. 
        """
        filt = queries.QueryFilter()
        try:
            filt.resource = self.resource
        except AttributeError:
            return
        try:
            if args:
                filt.text = args[0]
            else:
                filt.text = str(self.edit_tag.text())
        except InvalidFilterError:
            self.edit_tag.setStyleSheet('CoqTagEdit { border-radius: 5px; font: condensed;background-color: rgb(255, 255, 192); }')
        else:
            super(QueryFilterBox, self).addTag(filt.text)
            options.cfg.filter_list.append(filt)



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
    margin = 2
    
    #def sizeHint(self, option, index):
        
        #return QtGui.QFontMetrics().
        
        #options = QtGui.QStyleOptionViewItemV4(option)
        #self.initStyleOption(options,index)

        #content = QtGui.QLabel(unicode(index.data(QtCore.Qt.DisplayRole)))
        #content.setTextWidth(options.rect.width())
        #return QtCore.QSize(content.idealWidth() + self.margin * 2, content.size().height())
    
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
            painter.translate(self.margin, 0)
            painter.drawText(option.rect, index.data(QtCore.Qt.TextAlignmentRole), content)
        finally:
            painter.restore()

class CoqProbabilityDelegate(CoqResultCellDelegate):
    def get_background(self, option, index):
        value = float(index.data(QtCore.Qt.DisplayRole))
        if  value > 1:
            return QtGui.QColor("lightyellow")
        else:
            return super(CoqProbabilityDelegate, self).get_background(option, index)


logger = logging.getLogger(__init__.NAME)

from __future__ import unicode_literals

import logging

from coquery import options
from coquery.defines import *
from coquery.unicode import utf8
from coquery import managers

from .pyqt_compat import QtCore, QtGui, get_toplevel_window
from . import classes

class CoqResourceMenu(QtGui.QMenu):
    viewEntriesRequested = QtCore.Signal(classes.CoqTreeItem)
    viewUniquesRequested = QtCore.Signal(classes.CoqTreeItem)
    addLinkRequested = QtCore.Signal(classes.CoqTreeItem)
    removeItemRequested = QtCore.Signal(classes.CoqTreeItem)
    addGroupRequested = QtCore.Signal(str)
    removeGroupRequested = QtCore.Signal(str)
    
    def __init__(self, item, context=True, title="Output column options", parent=None, *args, **kwargs):
        super(CoqResourceMenu, self).__init__(title, parent)

        rc_feature = utf8(item.objectName())
        label = utf8(item.text(0))
        
        # if shown as context menu, use column name as header:
        if context:
            head = QtGui.QLabel("<b>{}</b>".format(label))
            head.setAlignment(QtCore.Qt.AlignCenter)
            action = QtGui.QWidgetAction(parent)
            action.setDefaultWidget(head)
            self.addAction(action)

        add_link = QtGui.QAction("&Link an external table", parent)
        add_grouping = QtGui.QAction("Add to &group columns", parent)
        remove_link = QtGui.QAction("&Remove linked table", parent)
        remove_grouping = QtGui.QAction("Remove from &group columns", parent)
        view_entries = QtGui.QAction("View all &values", parent)
        view_uniques = QtGui.QAction("View &unique values", parent)

        # linked table:
        if hasattr(item, "link"):
            self.addAction(remove_link)
            remove_link.triggered.connect(lambda: self.removeItemRequested.emit(item))
        elif not (rc_feature.endswith("_table")):
            if not rc_feature.startswith("coquery"):
                self.addAction(view_uniques)
                self.addAction(view_entries)
                view_entries.triggered.connect(lambda: self.viewEntriesRequested.emit(item))
                view_uniques.triggered.connect(lambda: self.viewUniquesRequested.emit(item))

                # Only enable the 'View' entries if the SQL connection is 
                # working:
                view_uniques.setEnabled(options.cfg.gui.test_mysql_connection())
                view_entries.setEnabled(options.cfg.gui.test_mysql_connection())

                self.addSeparator()

                if not hasattr(item.parent(), "link"):
                    self.addAction(add_link)
                    add_link.triggered.connect(lambda: self.addLinkRequested.emit(item))

                if self.parent().ui.list_group_columns.find_resource(rc_feature) is not None:
                    self.addAction(remove_grouping)
                    remove_grouping.triggered.connect(lambda: self.removeGroupRequested.emit(rc_feature))
                else:
                    self.addAction(add_grouping)
                    add_grouping.triggered.connect(lambda: self.addGroupRequested.emit(rc_feature))
        else:
            unavailable = QtGui.QAction(_translate("MainWindow", "No option available for tables.", None), self)
            unavailable.setDisabled(True)
            self.addAction(unavailable)      

class CoqColumnMenu(QtGui.QMenu):
    showColumnRequested = QtCore.Signal(list)
    hideColumnRequested = QtCore.Signal(list)
    renameColumnRequested = QtCore.Signal(str)
    resetColorRequested = QtCore.Signal(list)
    changeColorRequested = QtCore.Signal(list)
    addFunctionRequested = QtCore.Signal(list)
    removeFunctionRequested = QtCore.Signal(list)
    editFunctionRequested = QtCore.Signal(str)
    changeSortingRequested = QtCore.Signal(tuple)
    
    def __init__(self, columns=[], title="", parent=None, *args, **kwargs):
        super(CoqColumnMenu, self).__init__(title, parent, *args, **kwargs)
        self.columns = columns

        session = get_toplevel_window().Session
        manager = managers.get_manager(options.cfg.MODE, session.Resource.name)

        suffix = "s" if len(columns) > 1 else ""
        all_columns_visible = all([x not in manager.hidden_columns for x in columns])
        some_columns_visible = not all([x in manager.hidden_columns for x in columns])

        self.add_header(columns)

        show_column = QtGui.QAction("&Show column{}".format(suffix), parent)
        hide_column = QtGui.QAction("&Hide column{}".format(suffix), parent)
        rename_column = QtGui.QAction("&Rename column...", parent)
        reset_color = QtGui.QAction("&Reset color{}".format(suffix), parent)
        change_color = QtGui.QAction("&Change color{}...".format(suffix), parent)
        add_function = QtGui.QAction("&Add function...", parent)
        #edit_function = QtGui.QAction("&Edit function...", parent)
        remove_function = QtGui.QAction("&Remove function{}".format(suffix), parent)

        show_column.setIcon(parent.get_icon("Expand Arrow"))
        hide_column.setIcon(parent.get_icon("Collapse Arrow"))

        if not all_columns_visible:
            show_column.triggered.connect(lambda: self.showColumnRequested.emit(columns))
            self.addAction(show_column)

        if some_columns_visible:
            hide_column.triggered.connect(lambda: self.hideColumnRequested.emit(columns))
            self.addAction(hide_column)

        # Only show additional options if all columns are visible:
        if all_columns_visible:
            # add rename:
            if len(columns) == 1:
                rename_column.triggered.connect(lambda: self.renameColumnRequested.emit(columns[0]))
                self.addAction(rename_column)
            # add color reset
            if set(columns).intersection(set(options.cfg.column_color.keys())):
                reset_color.triggered.connect(lambda: self.resetColorRequested.emit(columns))
                self.addAction(reset_color)
            # add color change
            change_color.triggered.connect(lambda: self.changeColorRequested.emit(columns))
            self.addAction(change_color)
            
            self.addSeparator()
            
            # add 'add function'
            add_function.triggered.connect(lambda: self.addFunctionRequested.emit(columns))
            self.addAction(add_function)
            
            # add additional function actions, but only if all columns really 
            # are functions:
            if all([x.startswith("func_") for x in columns]):
                #if len(columns) == 1:
                    #edit_function.triggered.connect(lambda: self.editFunctionRequested.emit(columns[0]))
                    #self.addAction(edit_function)
                remove_function.triggered.connect(lambda: self.removeFunctionRequested.emit(columns))
                self.addAction(remove_function)
                
            self.addSeparator()

            # add sorting actions, but only if only one column is selected
            if len(columns) == 1:
                column = columns[0]
                group = QtGui.QActionGroup(self, exclusive=True)
                
                sort_none = group.addAction(QtGui.QAction("Do not sort", self, checkable=True))
                sort_asc = group.addAction(QtGui.QAction("&Ascending", self, checkable=True))
                sort_desc = group.addAction(QtGui.QAction("&Descending", self, checkable=True))

                sort_none.triggered.connect(lambda: self.changeSortingRequested.emit((column, None, None)))
                sort_asc.triggered.connect(lambda: self.changeSortingRequested.emit((column, True, False)))
                sort_desc.triggered.connect(lambda: self.changeSortingRequested.emit((column, False, False)))

                self.addAction(sort_none)
                self.addAction(sort_asc)
                self.addAction(sort_desc)
                
                if parent.table_model.content[[column]].dtypes[0] == "object":
                    sort_asc_rev = group.addAction(QtGui.QAction("&Ascending, reverse", self, checkable=True))
                    sort_desc_rev = group.addAction(QtGui.QAction("&Descending, reverse", self, checkable=True))
                    sort_asc_rev.triggered.connect(lambda: self.changeSortingRequested.emit((column, True, True)))
                    sort_desc_rev.triggered.connect(lambda: self.changeSortingRequested.emit((column, False, True)))
                    self.addAction(sort_asc_rev)
                    self.addAction(sort_desc_rev)
                
                # set currently active sorting mode, if any:
                sorter = manager.get_sorter(columns[0])
                try:
                    if sorter.ascending:
                        if sorter.reverse:
                            sort_asc_rev.setChecked(True)
                        else:
                            sort_asc.setChecked(True)
                    else:
                        if sorter.reverse:
                            sort_desc_rev.setChecked(True)
                        else:
                            sort_desc.setChecked(True)
                except AttributeError:
                    sort_none.setChecked(True)

    def add_header(self, columns):
        # Add menu header:
        session = get_toplevel_window().Session
        display_name = "<br/>".join([session.translate_header(x) for x
                                     in columns])
        action = QtGui.QWidgetAction(self.parent())
        label = QtGui.QLabel("<b>{}</b>".format(display_name), self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        action.setDefaultWidget(label)
        self.addAction(action)
        self.addSeparator()


class CoqHiddenColumnMenu(CoqColumnMenu):
    showColumnRequested = QtCore.Signal(list)

    def __init__(self, columns=[], title="", parent=None, *args, **kwargs):
        super(CoqColumnMenu, self).__init__(title, parent, *args, **kwargs)
        self.columns = columns

        self.add_header(columns)

        suffix = "s" if len(columns) > 1 else ""
        show_column = QtGui.QAction("&Show column{}".format(suffix), parent)
        show_column.setIcon(parent.get_icon("Collapse Arrow"))
        show_column.triggered.connect(lambda: self.showColumnRequested.emit(columns))
        self.addAction(show_column)

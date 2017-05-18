# -*- coding: utf-8 -*-
"""
menus.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import logging
import re

from coquery import options
from coquery.defines import *
from coquery.unicode import utf8
from coquery import managers

from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window
from . import classes

class CoqResourceMenu(QtWidgets.QMenu):
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
            head = QtWidgets.QLabel("<b>{}</b>".format(label))
            head.setAlignment(QtCore.Qt.AlignCenter)
            action = QtWidgets.QWidgetAction(parent)
            action.setDefaultWidget(head)
            self.addAction(action)

        add_link = QtWidgets.QAction("&Link an external table", parent)
        remove_link = QtWidgets.QAction("&Remove linked table", parent)
        view_entries = QtWidgets.QAction("View all &values", parent)
        view_uniques = QtWidgets.QAction("View &unique values", parent)

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

        else:
            unavailable = QtWidgets.QAction(_translate("MainWindow", "No option available for tables.", None), self)
            unavailable.setDisabled(True)
            self.addAction(unavailable)

class CoqColumnMenu(QtWidgets.QMenu):
    hideColumnRequested = QtCore.Signal(list)
    addFunctionRequested = QtCore.Signal(list)
    removeFunctionRequested = QtCore.Signal(list)
    editFunctionRequested = QtCore.Signal(str)
    changeSortingRequested = QtCore.Signal(tuple)
    propertiesRequested = QtCore.Signal(list)
    addGroupRequested = QtCore.Signal(str)
    removeGroupRequested = QtCore.Signal(str)

    def __init__(self, columns=[], title="", parent=None, *args, **kwargs):
        super(CoqColumnMenu, self).__init__(title, parent, *args, **kwargs)
        self.columns = columns

        session = get_toplevel_window().Session
        manager = managers.get_manager(options.cfg.MODE, session.Resource.name)

        suffix = "s" if len(columns) > 1 else ""
        all_columns_visible = all([x not in manager.hidden_columns for x in columns])
        some_columns_visible = not all([x in manager.hidden_columns for x in columns])

        self.add_header(columns)

        column_properties = QtWidgets.QAction("&Properties...", parent)
        column_properties.triggered.connect(lambda: self.propertiesRequested.emit(columns))
        self.addAction(column_properties)

        # add 'add function'
        add_function = QtWidgets.QAction("&Add function...", parent)
        add_function.triggered.connect(lambda: self.addFunctionRequested.emit(columns))
        self.addAction(add_function)

        hide_column = QtWidgets.QAction("&Hide column{}".format(suffix), parent)
        hide_column.setIcon(parent.get_icon("Forward"))
        hide_column.triggered.connect(lambda: self.hideColumnRequested.emit(columns))
        self.addAction(hide_column)

        self.addSeparator()

        # add additional function actions, but only if all columns really
        # are functions (excluding group functions):
        check_is_func = [x.startswith("func_") for x in columns]
        check_is_group_function = [bool(re.match("func_.*_group_", x))
                                   for x in columns]
        check_is_manager_function = [x in [fnc.get_id() for fnc in
                                           manager.manager_functions]
                                     for x in columns]
        if (all(check_is_func) and not any(check_is_group_function) and
            not any(check_is_manager_function)):
            #if len(columns) == 1:
                #edit_function.triggered.connect(lambda: self.editFunctionRequested.emit(columns[0]))
                #self.addAction(edit_function)
            #edit_function = QtWidgets.QAction("&Edit function...", parent)
            remove_function = QtWidgets.QAction("&Remove function{}".format(suffix), parent)
            remove_function.triggered.connect(lambda: self.removeFunctionRequested.emit(columns))
            self.addAction(remove_function)

            self.addSeparator()

        # add sorting actions, but only if only one column is selected
        if len(columns) == 1:
            column = columns[0]
            group = QtWidgets.QActionGroup(self, exclusive=True)

            sort_none = group.addAction(QtWidgets.QAction("Do not sort", self, checkable=True))
            sort_asc = group.addAction(QtWidgets.QAction("&Ascending", self, checkable=True))
            sort_desc = group.addAction(QtWidgets.QAction("&Descending", self, checkable=True))
            sort_asc.setIcon(parent.get_icon("Ascending Sorting"))
            sort_desc.setIcon(parent.get_icon("Descending Sorting"))


            sort_none.triggered.connect(lambda: self.changeSortingRequested.emit((column, None, None)))
            sort_asc.triggered.connect(lambda: self.changeSortingRequested.emit((column, True, False)))
            sort_desc.triggered.connect(lambda: self.changeSortingRequested.emit((column, False, False)))

            self.addAction(sort_none)
            self.addAction(sort_asc)
            self.addAction(sort_desc)

            if parent.table_model.content[[column]].dtypes[0] == "object":
                sort_asc_rev = group.addAction(QtWidgets.QAction("&Ascending, reverse", self, checkable=True))
                sort_desc_rev = group.addAction(QtWidgets.QAction("&Descending, reverse", self, checkable=True))
                sort_asc_rev.setIcon(parent.get_icon("Ascending Reverse Sorting"))
                sort_desc_rev.setIcon(parent.get_icon("Descending Reverse Sorting"))
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
        action = QtWidgets.QWidgetAction(self.parent())
        label = QtWidgets.QLabel("<b>{}</b>".format(display_name), self)
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

        #column_properties = QtWidgets.QAction("&Properties...", parent)
        #column_properties.triggered.connect(lambda: self.propertiesRequested.emit(columns))
        #self.addAction(column_properties)

        ## add 'add function'
        #add_function = QtWidgets.QAction("&Add function...", parent)
        #add_function.triggered.connect(lambda: self.addFunctionRequested.emit(columns))
        #self.addAction(add_function)

        suffix = "s" if len(columns) > 1 else ""
        show_column = QtWidgets.QAction("&Show column{}".format(suffix), parent)
        show_column.setIcon(parent.get_icon("Back"))
        show_column.triggered.connect(lambda: self.showColumnRequested.emit(columns))
        self.addAction(show_column)


def _translate(x, text, y):
    return utf8(options.cfg.app.translate(x, text, y))

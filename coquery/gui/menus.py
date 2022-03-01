# -*- coding: utf-8 -*-
"""
menus.py is part of Coquery.

Copyright (c) 2017-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import re
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal

from coquery import options
from coquery import managers
from coquery.unicode import utf8
from coquery.gui import classes
from coquery.gui.pyqt_compat import get_toplevel_window, tr


class CoqResourceMenu(QtWidgets.QMenu):
    viewEntriesRequested = pyqtSignal(classes.CoqTreeItem)
    viewUniquesRequested = pyqtSignal(classes.CoqTreeItem)
    addLinkRequested = pyqtSignal(classes.CoqTreeItem)
    removeItemRequested = pyqtSignal(classes.CoqTreeItem)
    addGroupRequested = pyqtSignal(str)
    removeGroupRequested = pyqtSignal(str)

    def __init__(self, item, context=True,
                 title="Output column options", parent=None, *args, **kwargs):
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
            remove_link.triggered.connect(
                lambda: self.removeItemRequested.emit(item))
        elif not (rc_feature.endswith("_table")):
            if not rc_feature.startswith("coquery"):
                self.addAction(view_uniques)
                self.addAction(view_entries)
                view_entries.triggered.connect(
                    lambda: self.viewEntriesRequested.emit(item))
                view_uniques.triggered.connect(
                    lambda: self.viewUniquesRequested.emit(item))

                # Only enable the 'View' entries if the SQL connection is
                # working:
                working_mysql = options.cfg.gui.test_mysql_connection()
                view_uniques.setEnabled(working_mysql)
                view_entries.setEnabled(working_mysql)

                self.addSeparator()

                if not hasattr(item.parent(), "link"):
                    self.addAction(add_link)
                    add_link.triggered.connect(
                        lambda: self.addLinkRequested.emit(item))

        else:
            unavailable = QtWidgets.QAction(
                tr("MainWindow", "No option available for tables.", None),
                self)
            unavailable.setDisabled(True)
            self.addAction(unavailable)


class CoqColumnMenu(QtWidgets.QMenu):
    hideColumnRequested = pyqtSignal(list)
    addFunctionRequested = pyqtSignal(list)
    removeUserColumnRequested = pyqtSignal(list)
    removeFunctionRequested = pyqtSignal(list)
    editFunctionRequested = pyqtSignal(str)
    changeSortingRequested = pyqtSignal(tuple)
    propertiesRequested = pyqtSignal(list)
    addGroupRequested = pyqtSignal(str)
    removeGroupRequested = pyqtSignal(str)

    def __init__(self, columns=None, title="", parent=None, *args, **kwargs):
        super(CoqColumnMenu, self).__init__(title, parent, *args, **kwargs)
        columns = columns or []
        self.columns = columns

        session = get_toplevel_window().Session
        manager = managers.get_manager(options.cfg.MODE, session.Resource.name)

        suffix = "s" if len(columns) > 1 else ""
        self.add_header(columns)

        column_properties = QtWidgets.QAction("&Properties...", parent)
        column_properties.triggered.connect(
            lambda: self.propertiesRequested.emit(columns))
        self.addAction(column_properties)

        # add 'add function'
        add_function = QtWidgets.QAction("&Add function...", parent)
        add_function.triggered.connect(
            lambda: self.addFunctionRequested.emit(columns))
        self.addAction(add_function)

        hide_column = QtWidgets.QAction(
            "&Hide column{}".format(suffix), parent)
        hide_column.setIcon(parent.get_icon("Forward"))
        hide_column.triggered.connect(
            lambda: self.hideColumnRequested.emit(columns))
        self.addAction(hide_column)

        self.addSeparator()

        check_is_userdata = [x.startswith("coq_userdata") for x in columns]
        if all(check_is_userdata):
            label = "&Remove user column{}".format(suffix)
            remove_userdata = QtWidgets.QAction(label, parent)
            remove_userdata.triggered.connect(
                lambda: self.removeUserColumnRequested.emit(columns))
            self.addAction(remove_userdata)
            self.addSeparator()

        # add additional function actions, but only if all columns really
        # are functions (excluding group functions):
        check_is_func = [x.startswith("func_") for x in columns]
        check_is_group_function = [bool(re.match("func_.*_group_", x))
                                   for x in columns]
        check_is_manager_function = [x in [fnc.get_id() for fnc in
                                           manager.manager_functions]
                                     for x in columns]
        if (all(check_is_func)
                and not any(check_is_group_function)
                and not any(check_is_manager_function)):
            if len(columns) == 1:
                edit_function = QtWidgets.QAction("&Edit function...", parent)
                edit_function.triggered.connect(
                    lambda: self.editFunctionRequested.emit(columns[0]))
                self.addAction(edit_function)
            remove_function = QtWidgets.QAction(
                "&Remove function{}".format(suffix), parent)
            remove_function.triggered.connect(
                lambda: self.removeFunctionRequested.emit(columns))
            self.addAction(remove_function)

            self.addSeparator()

        # add sorting actions, but only if only one column is selected
        if len(columns) == 1:
            column = columns[0]
            group = QtWidgets.QActionGroup(self)
            group.setExclusive(True)

            sort_none = group.addAction(
                QtWidgets.QAction("Do not sort", self, checkable=True))
            sort_asc = group.addAction(
                QtWidgets.QAction("&Ascending", self, checkable=True))
            sort_desc = group.addAction(
                QtWidgets.QAction("&Descending", self, checkable=True))
            sort_asc.setIcon(parent.get_icon("Ascending Sorting"))
            sort_desc.setIcon(parent.get_icon("Descending Sorting"))

            for action, data in ((sort_none, (column, None, None)),
                                 (sort_asc, (column, True, False)),
                                 (sort_desc, (column, False, False))):
                action.triggered.connect(
                    lambda: self.changeSortingRequested.emit(data))
                self.addAction(action)

            dtype = parent.table_model.content[[column]].dtypes[0]
            if pd.api.types.is_string_dtype(dtype):
                sort_asc_rev = group.addAction(
                    QtWidgets.QAction("&Ascending, reverse",
                                      self, checkable=True))
                sort_desc_rev = group.addAction(
                    QtWidgets.QAction("&Descending, reverse",
                                      self, checkable=True))
                sort_asc_rev.setIcon(
                    parent.get_icon("Ascending Reverse Sorting"))
                sort_desc_rev.setIcon(
                    parent.get_icon("Descending Reverse Sorting"))
                for action, data in ((sort_asc_rev, (column, True, True)),
                                     (sort_desc_rev, (column, False, True))):
                    action.triggered.connect(
                        lambda: self.changeSortingRequested.emit(data))
                    self.addAction(action)

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
    showColumnRequested = pyqtSignal(list)

    def __init__(self, columns=None, title="", parent=None, *args, **kwargs):
        super(CoqColumnMenu, self).__init__(title, parent, *args, **kwargs)
        columns = columns or []
        self.columns = columns

        self.add_header(columns)

        suffix = "s" if len(columns) > 1 else ""
        show_column = QtWidgets.QAction(
            "&Show column{}".format(suffix), parent)
        show_column.setIcon(parent.get_icon("Back"))
        show_column.triggered.connect(
            lambda: self.showColumnRequested.emit(columns))
        self.addAction(show_column)

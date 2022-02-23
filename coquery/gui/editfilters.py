# -*- coding: utf-8 -*-
"""
editfilter.py is part of Coquery.

Copyright (c) 2017-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal

from coquery.defines import (
    FILTER_STAGE_BEFORE_TRANSFORM, FILTER_STAGE_FINAL,
    # The following constants are not explicitly used in the code, but still
    # need to be imported because the CoqEditFilters class uses some black
    # magic to match these constants with elements in the GUI. This is really
    # not nice.
    OP_EQ, OP_NE, OP_GT, OP_GE, OP_LT, OP_LE, OP_MATCH, OP_NMATCH,
    OPERATOR_LABELS,
    )
from coquery.filters import Filter
from coquery.unicode import utf8
from coquery.gui.classes import CoqTableItem
from coquery.gui.pyqt_compat import get_toplevel_window, STYLE_WARN

FeatureRole = QtCore.Qt.UserRole
DtypeRole = QtCore.Qt.UserRole + 1
FilterObjectRole = QtCore.Qt.UserRole + 2


def format_filter(filt):
    """
    Return a string containing a visual representation of the filter.
    """
    col = get_toplevel_window().Session.translate_header(filt.feature)
    value = filt.fix(filt.value)
    op = OPERATOR_LABELS[filt.operator]
    S = "{} {} {}".format(col, op, value)
    if filt.stage == FILTER_STAGE_BEFORE_TRANSFORM:
        S = "{} (before transformation)".format(S)
    return S


class CoqEditFilters(QtWidgets.QWidget):
    listChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        from .ui import coqEditFiltersUi
        super(CoqEditFilters, self).__init__(*args, **kwargs)
        self.ui = coqEditFiltersUi.Ui_CoqEditFilters()
        self.ui.setupUi(self)
        self.ui.check_before_transformation.hide()

        self.columns = []
        self.dtypes = []

        self.ui.button_add.setIcon(
            get_toplevel_window().get_icon("Plus"))
        self.ui.button_remove.setIcon(
            get_toplevel_window().get_icon("Minus"))

        # just make sure that the constants are really imported from defines.py
        assert "OP_GE" in globals()
        operator_dict = {x: globals()[x] for x in globals()
                         if x.startswith("OP_")}
        radio_widgets = [x for x in dir(self.ui)
                         if x.startswith("radio_OP_")]
        self.radio_operators = {
            operator_dict[x.split("_", 1)[1]]: x for x in radio_widgets}

        self.setup_hooks()

    def setData(self, columns, dtypes, filter_list, session):
        assert len(columns) == len(dtypes)

        self.columns = pd.Index(columns)
        self.dtypes = dtypes
        self.session = session
        self.filter_list = filter_list
        self.old_list = {filt.get_hash() for filt in filter_list}

        self.fill_lists()
        self.change_filter()

    def isModified(self):
        current_list = {filt.get_hash() for filt in self.filters()}
        return self.old_list != current_list

    def filters(self):
        l = []
        for i in range(self.ui.table_filters.rowCount() - 1):
            item = self.ui.table_filters.item(i, 0)
            filt = item.data(FilterObjectRole)

            ix = self.columns.tolist().index(filt.feature)
            if self.dtypes[ix] == int:
                try:
                    filt.value = int(filt.value)
                except ValueError:
                    pass

            l.append(filt)
        return l

    def fill_lists(self):
        self.ui.list_columns.blockSignals(True)
        self.ui.list_columns.clear()
        for i, x in enumerate(self.columns):
            item = QtWidgets.QListWidgetItem(self.session.translate_header(x))
            item.setData(FeatureRole, x)
            item.setData(DtypeRole, self.dtypes[i])
            self.ui.list_columns.addItem(item)
        if len(self.columns) > 0:
            self.ui.list_columns.setCurrentRow(0)
        self.ui.list_columns.blockSignals(False)

        self.ui.table_filters.setRowCount(0)
        for filt in self.filter_list:
            item = CoqTableItem(format_filter(filt))
            item.setData(FilterObjectRole, filt)
            i = self.ui.table_filters.rowCount()
            self.ui.table_filters.insertRow(i)
            self.ui.table_filters.setItem(0, i, item)

        new_filter = CoqTableItem("New filter...")
        i = self.ui.table_filters.rowCount()
        self.ui.table_filters.insertRow(i)
        self.ui.table_filters.setItem(0, i, new_filter)

        self.ui.table_filters.selectRow(self.ui.table_filters.rowCount()-1)

    def setup_hooks(self):
        self.ui.button_add.clicked.connect(self.add_filter)
        self.ui.button_remove.clicked.connect(self.remove_filter)
        self.ui.table_filters.clicked.connect(self.change_filter)

        for signal in (self.ui.list_columns.currentRowChanged,
                       self.ui.edit_value.textChanged,
                       self.ui.check_before_transformation.toggled):
            signal.connect(self.update_filter)
        for radio in self.radio_operators.values():
            getattr(self.ui, radio).toggled.connect(self.update_filter)

    def update_buttons(self, item):
        """
        Update dialog buttons to correctly represent the current state of the
        dialog.

        The 'Add' button is only enabled if the 'New filter' row is selected.
        The 'Remove' button is only enabled if a valid filter row is selected.
        The 'Ok' button is only enabled if a change has been made to the
        content of the filter list.

        Parameters:
        -----------
        item : QTableItem
            The currently selected item
        """
        filt = item.data(FilterObjectRole)
        if filt is None:
            self.ui.button_add.setEnabled(True)
            self.ui.button_remove.setDisabled(True)
        else:
            self.ui.button_add.setDisabled(True)
            self.ui.button_remove.setEnabled(True)
            self.ui.check_before_transformation.setChecked(
                filt.stage == FILTER_STAGE_BEFORE_TRANSFORM)

        if self.ui.list_columns.count() == 0:
            self.ui.button_add.setDisabled(True)

        new_list = set()
        for i in range(self.ui.table_filters.rowCount()):
            item = self.ui.table_filters.item(i, 0)
            filt = item.data(FilterObjectRole)
            if filt is not None:
                new_list.add(filt.get_hash())

    def update_filter(self):
        """
        Update the currently selected filter with the current values from the
        dialog.

        This method is called whenever the content of the column list, an
        operator radio button, or the value textedit is changed. It replaces
        the currently selected filter by a new filter initialized with the
        current dialog values.
        """

        feature, dtype, operator, value, stage = self.get_values()
        filt = Filter(feature, dtype, operator, value, stage)

        # make sure that the current filter is legal:
        try:
            if operator not in (OP_MATCH, OP_NMATCH):
                filt.get_filter_string()
        except Exception as e:
            print(e)
            self.ui.edit_value.setStyleSheet(STYLE_WARN)
            return
        else:
            self.listChanged.emit()
            self.ui.edit_value.setStyleSheet(None)

        row = self.ui.table_filters.currentRow()
        if row == self.ui.table_filters.rowCount() - 1:
            return
        selected = self.ui.table_filters.item(row, 0)
        self.blockSignals(True)
        selected.setData(FilterObjectRole, filt)
        selected.setText(format_filter(filt))
        self.blockSignals(False)
        self.update_buttons(selected)


    def change_filter(self):
        """
        Update the values from the dialog with the content of the currently
        selected filter.

        This method is called whenever the selected filter in the filter list
        is changed.
        """
        selected = self.ui.table_filters.currentItem()
        selected_filter = selected.data(FilterObjectRole)

        if selected_filter is not None:
            # get correct operator radio button:
            radio = getattr(self.ui,
                            self.radio_operators[selected_filter.operator])

            row_number = 0
            # get correct feature list entry:
            for i in range(self.ui.list_columns.count()):
                item = self.ui.list_columns.item(i)
                if item.data(FeatureRole) == selected_filter.feature:
                    row_number = i

            self.blockSignals(True)

            # update GUI values:
            radio.setChecked(True)
            self.ui.edit_value.setText(utf8(selected_filter.value))
            self.ui.check_before_transformation.setChecked(
                selected_filter.stage == FILTER_STAGE_BEFORE_TRANSFORM)
            self.ui.list_columns.setCurrentRow(row_number)

            self.blockSignals(False)

        self.update_buttons(selected)

    def get_values(self):
        """
        Retrieve the current values from the dialog.

        Returns:
        --------
        tup : tuple
            A tuple with the elements (column, operator, value, stage).

            'column' a string containing the resource feature name of the
            currently selected column.
            'dtype' the dtype of the column
            'operator' is an integer corresponding to one of the values
            defined in ``defines.py``.
            'value' is a string containing the content of the value textedit.
            'stage' is either FILTER_STAGE_FINAL or
            FILTER_STAGE_BEFORE_TRANSFORM (defined in ``defines.py``)
        """
        feature = utf8(self.ui.list_columns.currentItem().data(FeatureRole))
        dtype = self.ui.list_columns.currentItem().data(DtypeRole)
        value = utf8(self.ui.edit_value.text())

        operator = None
        # determine which operator radio button is checked:
        for radio in self.radio_operators:
            if getattr(self.ui, self.radio_operators[radio]).isChecked():
                operator = globals()[radio]

        if self.ui.check_before_transformation.isChecked():
            stage = FILTER_STAGE_BEFORE_TRANSFORM
        else:
            stage = FILTER_STAGE_FINAL

        return feature, dtype, operator, value, stage

    def add_filter(self):
        """
        Create a new filter entry based on the current dialog values.

        The filter is only added if there is no other filter with the same
        values. If the filter is added, the currently selected filter row is
        set to the 'New filter' row, and the button status is updated.
        """
        new_filt = Filter(*self.get_values())
        hashed = new_filt.get_hash()

        hashed_filters = set()
        rows = self.ui.table_filters.rowCount()
        for i in range(rows - 1):
            item = self.ui.table_filters.item(i, 0)
            existing_filt = item.data(FilterObjectRole)
            hashed_filters.add(existing_filt.get_hash())

        if hashed not in hashed_filters:
            item = CoqTableItem(format_filter(new_filt))
            item.setData(FilterObjectRole, new_filt)
            self.ui.table_filters.insertRow(rows - 1)
            self.ui.table_filters.setItem(rows - 1, 0, item)
            self.ui.table_filters.selectRow(rows)
            self.ui.check_before_transformation.setChecked(False)
            self.update_buttons(self.ui.table_filters.currentItem())
        self.listChanged.emit()

    def remove_filter(self):
        """
        Remove the currently selected filter.

        This also updates the button status."
        """
        current = self.ui.table_filters.currentRow()
        max_row = self.ui.table_filters.rowCount()
        if current < max_row - 1:
            self.ui.table_filters.removeRow(current)
            if current == max_row - 2:
                current = max(0, current - 1)
            self.ui.table_filters.selectRow(current)
            self.update_buttons(self.ui.table_filters.currentItem())
            self.listChanged.emit()

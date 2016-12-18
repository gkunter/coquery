# -*- coding: utf-8 -*-
"""
addfilter.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

from coquery import options
from coquery.defines import *
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtGui
from .ui.addFilterUi import Ui_FiltersDialog
from .classes import CoqTableItem, CoqListItem
from coquery.filters import Filter


class FilterDialog(QtGui.QDialog):
    def __init__(self, filter_list, columns, dtypes, session, parent=None):
        super(FilterDialog, self).__init__(parent)
        self.ui = Ui_FiltersDialog()
        self.ui.setupUi(self)

        self.ui.button_add.setIcon(options.cfg.main_window.get_icon("sign-add"))
        self.ui.button_remove.setIcon(options.cfg.main_window.get_icon("sign-delete"))

        for x in columns:
            item = CoqListItem(session.translate_header(x))
            item.setObjectName(x)
            self.ui.list_columns.addItem(item)

        self.columns = columns
        self.dtypes = dtypes

        self.ui.list_columns.setCurrentRow(0)

        for filt in filter_list:
            item = CoqTableItem(self.format_filter(filt))
            item.setObjectName(filt)
            i = self.ui.table_filters.rowCount()
            self.ui.table_filters.insertRow(i)
            self.ui.table_filters.setItem(0, i, item)

        self.old_list = {filt.get_hash() for filt in filter_list}

        new_filter = CoqTableItem("New filter...")
        new_filter.setObjectName(None)
        i = self.ui.table_filters.rowCount()
        self.ui.table_filters.insertRow(i)
        self.ui.table_filters.setItem(0, i, new_filter)

        self.radio_operators = {
            globals()[x.partition("_")[-1]]: x for x in dir(self.ui) if x.startswith("radio_OP_")}

        self.ui.button_add.clicked.connect(self.add_filter)
        self.ui.button_remove.clicked.connect(self.remove_filter)
        self.ui.table_filters.clicked.connect(self.update_values)
        self.ui.table_filters.currentItemChanged.connect(lambda x, _: self.update_buttons(x))

        self.ui.list_columns.currentRowChanged.connect(self.update_filter)
        self.ui.edit_value.textChanged.connect(self.update_filter)
        for radio in [x for x in dir(self.ui) if x.startswith("radio_OP_")]:
            getattr(self.ui, radio).toggled.connect(self.update_filter)

        #self.ui.table_filters.selectRow(0)
        self.ui.table_filters.selectRow(self.ui.table_filters.rowCount()-1)
        self.update_values()

        try:
            self.resize(options.settings.value("filterdialog_size"))
        except TypeError:
            pass

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

        filt = item.objectName()
        if filt is None:
            self.ui.button_add.setEnabled(True)
            self.ui.button_remove.setDisabled(True)
        else:
            self.ui.button_add.setDisabled(True)
            self.ui.button_remove.setEnabled(True)

        if self.ui.list_columns.count() == 0:
            self.ui.button_add.setDisabled(True)

        new_list = set()
        for i in range(self.ui.table_filters.rowCount()):
            filt = self.ui.table_filters.item(i, 0).objectName()
            if filt is not None:
                new_list.add(filt.get_hash())
        if self.old_list == new_list:
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
        else:
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)

    def update_filter(self):
        """
        Update the currently selected filter with the current values from the
        dialog.

        This method is called whenever the content of the column list, an
        operator radio button, or the value textedit is changed. It replaces
        the currently selected filter by a new filter initialized with the
        current dialog values.
        """
        row = self.ui.table_filters.currentRow()
        if row == self.ui.table_filters.rowCount() - 1:
            return
        self.blockSignals(True)
        selected = self.ui.table_filters.item(row, 0)
        feature, operator, value = self.get_values()
        filt = Filter(feature, operator, value)
        selected.setObjectName(filt)
        selected.setText(self.format_filter(filt))
        self.update_buttons(selected)
        self.blockSignals(False)

    def update_values(self):
        """
        Update the values from the dialog with the content of the currently
        selected filter.

        This method is called whenever the selected filter in the filter list
        is changed.
        """
        selected = self.ui.table_filters.currentItem()
        if selected.objectName() is not None:
            filt = selected.objectName()
            getattr(self.ui,
                    self.radio_operators[filt.operator]).setChecked(True)
            self.ui.edit_value.setText(utf8(filt.value))
            column_label = options.cfg.main_window.Session.translate_header(
                filt.feature)
            for i in range(self.ui.list_columns.count()):
                if utf8(self.ui.list_columns.item(i).text()) == column_label:
                    self.ui.list_columns.setCurrentRow(i)
                    break

    def format_filter(self, filt):
        """
        Return a string containing a visual representation of the filter.
        """
        col = options.cfg.main_window.Session.translate_header(filt.feature)
        value = filt.fix(filt.value)
        op = OPERATOR_LABELS[filt.operator]
        return "{} {} {}".format(col, op, value)

    def get_values(self):
        """
        Retrieve the current values from the dialog.

        Returns:
        --------
        tup : tuple
            A tuple with the three elements column, operator, value.

            'column' a string containing the resource feature name of the
            currently selected column.
            'operator' is an integer corresponding to one of the values
            defined in ``defines.py``.
            'value' is a string containing the content of the value textedit.
        """
        feature = utf8(self.ui.list_columns.currentItem().objectName())
        value = utf8(self.ui.edit_value.text())
        for x in dir(self.ui):
            if x.startswith("radio_OP") and getattr(self.ui, x).isChecked():
                op_label = x.partition("_")[-1]
                operator = globals()[op_label]
        return feature, operator, value

    def add_filter(self):
        """
        Create a new filter entry based on the current dialog values.

        The filter is only added if there is no other filter with the same
        values. If the filter is added, the currently selected filter row is
        set to the 'New filter' row, and the button status is updated.
        """
        feature, operator, value = self.get_values()
        filt = Filter(feature, operator, value)
        hashed = filt.get_hash()
        S = set()
        rows = self.ui.table_filters.rowCount()
        for i in range(rows - 1):
            S.add(self.ui.table_filters.item(0, i).objectName().get_hash())
        if hashed not in S:
            item = CoqTableItem(self.format_filter(filt))
            item.setObjectName(filt)
            self.ui.table_filters.insertRow(rows - 1)
            self.ui.table_filters.setItem(rows - 1, 0, item)
            self.ui.table_filters.selectRow(rows)
            self.update_buttons(self.ui.table_filters.currentItem())

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

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        options.settings.setValue("filterdialog_size", self.size())

    def exec_(self):
        result = super(FilterDialog, self).exec_()
        if result == QtGui.QDialog.Accepted:
            l = []
            for i in range(self.ui.table_filters.rowCount() - 1):
                filt = self.ui.table_filters.item(0, i).objectName()
                ix = self.columns.tolist().index(filt.feature)
                if self.dtypes[ix] == int:
                    filt.value = int(filt.value)
                l.append(filt)
            return l
        else:
            return None

    @staticmethod
    def set_filters(filter_list, **kwargs):
        dialog = FilterDialog(filter_list=filter_list, **kwargs)
        dialog.setVisible(True)

        return dialog.exec_()

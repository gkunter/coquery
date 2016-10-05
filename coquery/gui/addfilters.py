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

        self.ui.list_columns.setCurrentItem(item)

        for filt in filter_list:
            item = CoqTableItem(self.format_filter(filt))
            item.setObjectName(filt)
            i = self.ui.table_filters.rowCount()
            self.ui.table_filters.insertRow(i)
            self.ui.table_filters.setItem(0, i, item)
            
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

        self.ui.table_filters.selectRow(0)
        self.update_values()

        try:
            self.resize(options.settings.value("filterdialog_size"))
        except TypeError:
            pass

    def update_values(self):
        selected = self.ui.table_filters.currentItem()
        if selected.objectName() != None:
            filt = selected.objectName()
            getattr(self.ui, self.radio_operators[filt.operator]).setChecked(True)
            self.ui.edit_value.setText(filt.value)
            column_label = options.cfg.main_window.Session.translate_header(filt.feature)
            for i in range(self.ui.list_columns.count()):
                if utf8(self.ui.list_columns.item(i).text()) == column_label:
                    self.ui.list_columns.setCurrentRow(i)
                    break
    
    def format_filter(self, filt):
        col = options.cfg.main_window.Session.translate_header(filt.feature)
        value = filt.fix(filt.value)
        op = OPERATOR_LABELS[filt.operator]
        return "{} {} {}".format(col, op, value)

    def get_operator(self):
        for x in dir(self.ui):
            if x.startswith("radio_OP") and getattr(self.ui, x).isChecked():
                op_label = x.partition("_")[-1]
                return globals()[op_label]
        return None
        
    def add_filter(self):
        feature = utf8(self.ui.list_columns.currentItem().objectName())
        value = utf8(self.ui.edit_value.text())
        operator = self.get_operator()
        filt = Filter(feature, operator, value)
        hashed = filt.get_hash()
        S = set()
        for i in range(self.ui.table_filters.rowCount() - 1):
            S.add(self.ui.table_filters.item(0, i).objectName().get_hash())
        if hashed not in S:
            item = CoqTableItem(self.format_filter(filt))
            item.setObjectName(filt)
            self.ui.table_filters.insertRow(0)
            self.ui.table_filters.setItem(0, 0, item)
            self.ui.table_filters.selectRow(0)
        
    def remove_filter(self):
        current = self.ui.table_filters.currentRow()
        max_row = self.ui.table_filters.rowCount()
        if current < max_row - 1:
            self.ui.table_filters.removeRow(current)
            if current == max_row - 2:
                current = max(0, current - 1)
            self.ui.table_filters.selectRow(current)
        
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
                ix = self.columns.index(filt.feature)
                if self.dtypes[ix] == int:
                    filt.value = int(filt.value)s
                l.append()
            return l
        else:
            return None

    @staticmethod
    def set_filters(filter_list, **kwargs):
        dialog = FilterDialog(filter_list=filter_list, **kwargs)
        dialog.setVisible(True)
        
        return dialog.exec_()

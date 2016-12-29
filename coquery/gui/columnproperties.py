# -*- coding: utf-8 -*-
"""
columnproperties.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import collections

from coquery import options
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtGui, get_toplevel_window
from .ui.columnPropertiesUi import Ui_ColumnProperties


class ColumnPropertiesDialog(QtGui.QDialog):
    def __init__(self, df, preset, columns, parent=None):
        super(ColumnPropertiesDialog, self).__init__(parent)

        self.ui = Ui_ColumnProperties()
        self.ui.setupUi(self)

        self.df = df
        self.unique_cache = {}
        try:
            self.alias = preset["alias"]
        except:
            self.alias = collections.defaultdict(str)
        try:
            self.substitutions = preset["substitutions"]
        except:
            self.substitutions = collections.defaultdict(dict)
        try:
            self.colors = preset["colors"]
        except:
            self.colors = collections.defaultdict(str)
        try:
            self.hidden = preset["hidden"]
        except:
            self.hidden = collections.defaultdict(str)

        self.setup_data()

        if columns:
            self.ui.widget_selection.setCurrentItem(columns[0])

        try:
            self.resize(options.settings.value("columnproperties_size"))
        except TypeError:
            pass

    def exec_(self, *args, **kwargs):
        session = get_toplevel_window().Session
        result = super(ColumnPropertiesDialog, self).exec_(*args, **kwargs)
        if result == QtGui.QDialog.Accepted:
            d = {}
            d["alias"] = {k: v for k, v in self.alias.items()
                          if session.translate_header(k) != v}
            subst = {}
            for key in self.substitutions:
                tmp = {k: v for k, v in self.substitutions[key].items()
                       if v is not None}
                if tmp:
                    subst[key] = tmp
            d["substitutions"] = subst
            d["colors"] = self.colors
            vis_cols = [x.data(QtCore.Qt.UserRole) for x
                        in self.ui.widget_selection.selectedItems()]
            d["hidden"] = set([x for x in self.df.columns
                               if x not in vis_cols and
                               not x.startswith("coquery_invisible")])
            return d
        else:
            return None

    def closeEvent(self, event):
        options.settings.setValue("columnproperties_size", self.size())

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def setup_data(self):
        columns = [x for x in self.df.columns
                   if not x.startswith("coquery_invisible")]
        vis_cols = [x for x in columns if x not in self.hidden]
        hidden_cols = [x for x in columns if x not in vis_cols]

        session = get_toplevel_window().Session
        self.ui.widget_selection.setSelectedList(vis_cols,
                                                 session.translate_header)
        self.ui.widget_selection.setAvailableList(hidden_cols,
                                                  session.translate_header)
        self.ui.widget_selection.setTrackSelected(True)
        self.ui.widget_selection.setMoveAvailable(False)
        self.ui.widget_selection.setSelectedLabel("Visible columns")
        self.ui.widget_selection.setAvailableLabel("Hidden columns")
        self.show_column(self.ui.widget_selection.currentItem())
        self.ui.widget_selection.currentItemChanged.connect(self.show_column)
        self.ui.edit_column_name.textChanged.connect(self.change_alias)
        self.ui.table_substitutions.cellChanged.connect(
            self.change_substitution)
        button = self.ui.buttonbox_label.button(QtGui.QDialogButtonBox.Reset)
        button.clicked.connect(lambda: self.ui.edit_column_name.setText(""))
        self.ui.button_change_color.clicked.connect(self.set_color)
        button = self.ui.buttonbox_color.button(QtGui.QDialogButtonBox.Reset)
        button.clicked.connect(self.reset_color)

    def reset_color(self):
        current_item = self.ui.widget_selection.currentItem()
        col = current_item.data(QtCore.Qt.UserRole)
        try:
            self.colors.pop(col)
        except KeyError:
            pass
        self.ui.label_example.setStyleSheet("")

    def set_color(self):
        current_item = self.ui.widget_selection.currentItem()
        column = current_item.data(QtCore.Qt.UserRole)
        try:
            color = QtGui.QColorDialog.getColor(self.colors[column])
        except KeyError:
            color = QtGui.QColorDialog.getColor()

        if color.isValid():
            S = "QLabel {{color: {};}}".format(color.name())
            self.ui.label_example.setStyleSheet(S)
            self.colors[column] = color.name()

    def change_substitution(self, i, j):
        current_item = self.ui.widget_selection.currentItem()
        col = current_item.data(QtCore.Qt.UserRole)
        key = utf8(self.ui.table_substitutions.item(i, 0).text())
        value = utf8(self.ui.table_substitutions.item(i, 1).text())
        self.substitutions[col][key] = value

    def change_alias(self):
        current_item = self.ui.widget_selection.currentItem()
        col = current_item.data(QtCore.Qt.UserRole)
        self.alias[col] = utf8(self.ui.edit_column_name.text())

    def show_column(self, current_item):
        col = current_item.data(QtCore.Qt.UserRole)
        try:
            s = self.alias[col]
        except KeyError:
            s = ""
        if not s:
            self.ui.edit_column_name.setText(utf8(current_item.text()))
        else:
            self.ui.edit_column_name.setText(s)

        try:
            s = "QLabel {{ color: {};}}".format(self.colors[col])
        except:
            s = ""
        self.ui.label_example.setStyleSheet(s)

        # set substitution table
        self.ui.table_substitutions.blockSignals(True)
        uniques = self.get_unique_values(col)
        if col not in self.substitutions:
            self.substitutions[col] = {}
        for x in uniques:
            if x not in self.substitutions[col]:
                self.substitutions[col][x] = None
        self.ui.table_substitutions.setRowCount(0)
        self.ui.table_substitutions.setRowCount(len(self.substitutions[col]))
        sorted_items = sorted(self.substitutions[col].items())
        for i, (key, value) in enumerate(sorted_items):
            original = QtGui.QTableWidgetItem(key)
            original.setFlags(original.flags() & ~QtCore.Qt.ItemIsEditable)
            self.ui.table_substitutions.setItem(i, 0, original)

            substitute = QtGui.QTableWidgetItem(value)
            self.ui.table_substitutions.setItem(i, 1, substitute)

        self.ui.table_substitutions.blockSignals(False)

    def get_unique_values(self, column):
        if column in self.unique_cache:
            val = self.unique_cache[column]
        else:
            val = self.df[column].unique()
            self.unique_cache[column] = val
        return val

    @staticmethod
    def manage(df, preset, columns=[], parent=None):
        dialog = ColumnPropertiesDialog(df, preset, columns, parent=parent)
        dialog.setVisible(True)
        return dialog.exec_()

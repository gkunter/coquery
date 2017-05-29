# -*- coding: utf-8 -*-
"""
columnproperties.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import collections

from coquery import options
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtWidgets, QtGui, get_toplevel_window
from .ui.columnPropertiesUi import Ui_ColumnProperties


class ColumnPropertiesDialog(QtWidgets.QDialog):
    _color_map = {QtGui.QColor(name).name().lower(): name for name
                  in QtGui.QColor.colorNames()}
    def __init__(self, df, pre_subst, preset, columns=None, parent=None):
        super(ColumnPropertiesDialog, self).__init__(parent)

        self.ui = Ui_ColumnProperties()
        self.ui.setupUi(self)
        self.ui.widget_selection.setDefocus(False)

        self.df = df
        self.pre_subst = pre_subst
        self.unique_cache = {}
        self.alias = preset.get("alias", {})
        self.substitutions = preset.get("substitutions", {})
        self.colors = preset.get("colors", {})
        self.hidden = preset.get("hidden", {})

        self.setup_data()

        if columns:
            self.ui.widget_selection.setCurrentItem(columns[0])
        else:
            try:
                self.ui.widget_selection.setCurrentItem(
                    options.settings.value("columnproperties_column"))
            except TypeError:
                pass
        try:
            self.ui.tab_widget.setCurrentIndex(
                options.settings.value("columnproperties_index"))
        except TypeError:
            pass

        try:
            self.resize(options.settings.value("columnproperties_size"))
        except TypeError:
            pass

    def _key_dtype(self, key, col):
        if col in self.pre_subst:
            dtype = self.pre_subst[col].dtype
        else:
            dtype = self.df[col].dtype

        # ensure that the keys have the same dtype as the values:
        if dtype == object:
            return key
        elif dtype == float:
            return float(key)
        elif dtype == int:
            return int(key)
        elif dtype == bool:
            if key in ["True", "False"]:
                return key == "True"
            else:
                return bool(key)
        raise TypeError

    def exec_(self, *args, **kwargs):
        session = get_toplevel_window().Session
        result = super(ColumnPropertiesDialog, self).exec_(*args, **kwargs)
        if result == QtWidgets.QDialog.Accepted:
            d = {}

            subst = {}
            for col in [x for x in self.substitutions
                        if x in self.df.columns]:
                # Construct a dict of substitutions. Only those substitutions
                # are valid where the value is not empty and where the value
                # is not also one of the keys:
                tmp = {self._key_dtype(k, col): v for k, v
                       in self.substitutions[col].items()
                       if v not in [None, ""] and
                       v not in self.substitutions[col]}
                if tmp:
                    subst[col] = tmp

            d["alias"] = self.alias
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

    def accept(self, *args):
        super(ColumnPropertiesDialog, self).accept(*args)
        options.settings.setValue("columnproperties_size", self.size())
        current_item = self.ui.widget_selection.currentItem()
        if current_item:
            options.settings.setValue("columnproperties_column",
                                      current_item.data(QtCore.Qt.UserRole))
        options.settings.setValue("columnproperties_index",
                                  self.ui.tab_widget.currentIndex())

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
                                                 session.translate_header,
                                                 ignore_alias=True)
        self.ui.widget_selection.setAvailableList(hidden_cols,
                                                  session.translate_header,
                                                  ignore_alias=True)
        self.ui.widget_selection.setTrackSelected(True)
        self.ui.widget_selection.setMoveAvailable(False)
        self.ui.widget_selection.setSelectedLabel("Visible columns")
        self.ui.widget_selection.setAvailableLabel("Hidden columns")

        if columns:
            current = self.ui.widget_selection.currentItem()
            if current:
                self.show_column(current)
        else:
            self.ui.tab_widget.setEnabled(False)

        self.ui.widget_selection.currentItemChanged.connect(self.show_column)
        self.ui.edit_column_name.textChanged.connect(self.change_alias)
        self.ui.table_substitutions.cellChanged.connect(
            self.change_substitution)
        button = self.ui.buttonbox_label.button(QtWidgets.QDialogButtonBox.Reset)
        button.clicked.connect(self.reset_alias)
        self.ui.button_change_color.clicked.connect(self.set_color)
        self.ui.label_example.clicked.connect(self.set_color)
        button = self.ui.buttonbox_color.button(QtWidgets.QDialogButtonBox.Reset)
        button.clicked.connect(self.reset_color)
        button = self.ui.buttonbox_substitution.button(QtWidgets.QDialogButtonBox.Reset)
        button.clicked.connect(self.reset_substitution)

    def reset_alias(self):
        current_item = self.ui.widget_selection.currentItem()
        val = current_item.data(QtCore.Qt.UserRole)
        session = get_toplevel_window().Session
        text = session.translate_header(val, ignore_alias=True)
        self.ui.edit_column_name.setText(text)

    def reset_substitution(self):
        current_item = self.ui.widget_selection.currentItem()
        column = current_item.data(QtCore.Qt.UserRole)
        for i in range(self.ui.table_substitutions.rowCount()):
            key = self._key_dtype(
                    utf8(self.ui.table_substitutions.item(i, 0).text()),
                    column)
            value = None
            self.ui.table_substitutions.item(i, 1).setText(value)
            self.substitutions[column][key] = value

    def reset_color(self):
        current_item = self.ui.widget_selection.currentItem()
        col = current_item.data(QtCore.Qt.UserRole)
        try:
            self.colors.pop(col)
        except KeyError:
            pass
        self.set_example(None)

    def set_example(self, color):
        if color:
            if color.red() + color.green() + color.blue() > 127 * 3:
                fg = "black"
            else:
                fg = "white"
            S = "QLabel {{background-color: {}; color: {}; }}".format(
                color.name(), fg)
            label = color.name()
            if label.lower() in self._color_map:
                label = "{} ({})".format(label, self._color_map[label])
        else:
            S = ""
            label = "(default color)"
        self.ui.label_example.setText(label)
        self.ui.label_example.setStyleSheet(S)

    def set_color(self):
        current_item = self.ui.widget_selection.currentItem()
        column = current_item.data(QtCore.Qt.UserRole)
        try:
            color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.colors[column]))
        except KeyError:
            color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            self.set_example(color)
            self.colors[column] = color.name()

    def change_substitution(self, i, j):
        current_item = self.ui.widget_selection.currentItem()
        col = current_item.data(QtCore.Qt.UserRole)
        key = utf8(self.ui.table_substitutions.item(i, 0).text())
        value = utf8(self.ui.table_substitutions.item(i, 1).text())
        key = self._key_dtype(key, col)
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

        if col in self.colors:
            self.set_example(QtGui.QColor(self.colors[col]))
        else:
            self.set_example(None)

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
            original = QtWidgets.QTableWidgetItem(utf8(key))
            original.setFlags(original.flags() & ~QtCore.Qt.ItemIsEditable)
            self.ui.table_substitutions.setItem(i, 0, original)

            if value is None:
                substitute = QtWidgets.QTableWidgetItem(None)
            else:
                substitute = QtWidgets.QTableWidgetItem(utf8(value))

            self.ui.table_substitutions.setItem(i, 1, substitute)

        self.ui.table_substitutions.blockSignals(False)

    def get_unique_values(self, column):
        if column in self.unique_cache:
            val = self.unique_cache[column]
        else:
            val = self.pre_subst.get(column,
                                     self.df[column].dropna().unique())
            self.unique_cache[column] = val
        return val

    @staticmethod
    def manage(df, raw, preset, columns=[], parent=None):
        dialog = ColumnPropertiesDialog(df, raw, preset, columns,
                                        parent=parent)
        dialog.setVisible(True)
        return dialog.exec_()

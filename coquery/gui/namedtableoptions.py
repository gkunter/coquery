# -*- coding: utf-8 -*-
"""
namedtableoptions.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import os

from coquery import options
from coquery.unicode import utf8
from .pyqt_compat import QtWidgets

from .csvoptions import quote_chars, CSVOptionDialog, CSVOptions
from .ui.namedTableOptionsUi import Ui_NamedTableOptions


class NamedTableOptionsDialog(CSVOptionDialog):
    def __init__(self, filename, fields=None, default=None, parent=None,
                 icon=None):
        """
        Parameters
        ----------
        filename : string

        fields : dictionary
        """
        self._required = set()
        self._last_header = None
        super(NamedTableOptionsDialog, self).__init__(
            default=default,
            parent=parent,
            icon=icon,
            ui=Ui_NamedTableOptions)
        self.ui.edit_file_name.setText(filename)

        self.ui.button_map_word.clicked.connect(
            lambda: self.map_query_item_type("word"))
        self.ui.button_map_lemma.clicked.connect(
            lambda: self.map_query_item_type("lemma"))
        self.ui.button_map_pos.clicked.connect(
            lambda: self.map_query_item_type("pos"))
        self.ui.button_map_transcript.clicked.connect(
            lambda: self.map_query_item_type("transcript"))
        self.ui.button_map_gloss.clicked.connect(
            lambda: self.map_query_item_type("gloss"))
        self._selected = 0
        self.map = default.mapping

        if fields:
            for key, value in fields:
                button_name = "button_map_{}".format(value.lower())
                edit_name = "edit_map_{}".format(value.lower())
                setattr(self.ui, button_name, QtWidgets.QPushButton(key))
                setattr(self.ui, edit_name, QtWidgets.QLineEdit())

                getattr(self.ui, button_name).clicked.connect(
                    lambda: self.map_query_item_type(value))

        self.resize_widgets()

        for x in default.mapping:
            try:
                getattr(self.ui, "edit_map_{}".format(x)).setText(self.map[x])
            except TypeError:
                # Ignore mappings if there is a type error:
                pass

        try:
            self.resize(options.settings.value("namedtableoptions_size"))
        except TypeError:
            pass

    def resize_widgets(self):
        # make all buttons the same size:
        max_height = 0
        for name in [x for x in dir(self.ui)
                     if x.startswith(("button", "label", "edit"))]:
            widget = getattr(self.ui, name)
            max_height = max(max_height, widget.sizeHint().height())
        for name in [x for x in dir(self.ui)
                     if x.startswith(("button", "label", "edit"))]:
            widget = getattr(self.ui, name)
            widget.setMinimumHeight(max_height)

    def set_mappings(self, tuple_list):
        """
        Set the mappings of the current dialog.

        Each tuple in the tuple list consists of the display name and the
        internal name of the mapping.
        """
        for name in [x for x in dir(self.ui)
                     if x.startswith(("button_map_", "edit_map_"))]:
            widget = getattr(self.ui, name)
            self.ui.layout_name_buttons.removeWidget(widget)
            widget.setParent(None)
            #widget.deleteLater()
            del widget

        for i, (label, name) in enumerate(tuple_list):
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(lambda: self.map_query_item_type(name))
            edit = QtWidgets.QLineEdit()
            button_name = "button_map_{}".format(name.lower())
            edit_name = "edit_map_{}".format(name.lower())
            setattr(self.ui, button_name, button)
            setattr(self.ui, edit_name, edit)
            self.ui.layout_name_buttons.addWidget(button, i, 0, 1, 1)
            self.ui.layout_name_buttons.addWidget(edit, i, 1, 1, 1)
        self.resize_widgets()

    def add_required_mapping(self, required):
        self._required.add(required)

    def validate_dialog(self):
        current_file = utf8(self.ui.edit_file_name.text())
        self.ui.group_mappings.setEnabled(os.path.exists(current_file))

        has_word = True
        for required in self._required:
            if required not in self.map:
                has_word = False
                break

        ok_button = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        ok_button.setEnabled(has_word)

    def select_file(self):
        name = super(NamedTableOptionsDialog, self).select_file()
        if name:
            self.reset_mapping()
            self.validate_dialog()
        return name

    def reset_mapping(self):
        self.map = dict()
        for name in [x for x in dir(self.ui)
                     if x.startswith("edit_map_")]:
            getattr(self.ui, name).setText("")

    def update_content(self):
        super(NamedTableOptionsDialog, self).update_content()
        if self.ui.file_has_headers != self._last_header:
            self.reset_mapping()
        self.validate_dialog()
        self._last_header = self.ui.file_has_headers.isChecked()

    def closeEvent(self, event):
        options.settings.setValue("namedtableoptions_size", self.size())

    def map_query_item_type(self, label):
        header = self.file_table.columns[self._col_select]
        for key, value in list(self.map.items()):
            if value == self._col_select:
                line_edit = getattr(self.ui, "edit_map_{}".format(key))
                line_edit.setText("")
                self.map.pop(key)

        self.map[label] = self._col_select
        line_edit = getattr(self.ui, "edit_map_{}".format(label))
        line_edit.setText(header)
        self.validate_dialog()

    def exec_(self):
        result = super(NamedTableOptionsDialog, self).exec_()
        if isinstance(result, CSVOptions):
            quote = dict(zip(quote_chars.values(), quote_chars.keys()))[
                utf8(self.ui.quote_char.currentText())]

            return CSVOptions(
                file_name=utf8(self.ui.edit_file_name.text()),
                sep=self.separator,
                selected_column=self.ui.query_column.value(),
                header=self.ui.file_has_headers.isChecked(),
                skip_lines=self.ui.ignore_lines.value(),
                encoding=utf8(self.ui.combo_encoding.currentText()),
                quote_char=quote,
                mapping=self.map,
                dtypes=self.file_table.dtypes,
                excel=self._read_from_xls)
        else:
            return None

    @staticmethod
    def getOptions(path, fields=[], default=None, parent=None, icon=None):
        dialog = NamedTableOptionsDialog(path, fields, default, parent, icon)
        return dialog.exec_()

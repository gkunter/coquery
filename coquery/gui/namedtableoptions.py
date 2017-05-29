# -*- coding: utf-8 -*-
"""
namedtableoptions.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

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
        self._last_header = None
        super(NamedTableOptionsDialog, self).__init__(
            default=default,
            parent=parent,
            icon=icon,
            ui=Ui_NamedTableOptions)

        self.ui.button_word.clicked.connect(
            lambda: self.map_query_item_type("word"))
        self.ui.button_lemma.clicked.connect(
            lambda: self.map_query_item_type("lemma"))
        self.ui.button_pos.clicked.connect(
            lambda: self.map_query_item_type("pos"))
        self.ui.button_transcript.clicked.connect(
            lambda: self.map_query_item_type("transcript"))
        self.ui.button_gloss.clicked.connect(
            lambda: self.map_query_item_type("gloss"))

        self._selected = 0
        self.map = default.mapping

        if fields:
            for key, value in fields:
                button_name = "button_{}".format(value.lower())
                edit_name = "edit_{}".format(value.lower())
                setattr(self.ui, button_name, QtWidgets.QPushButton(key))
                setattr(self.ui, edit_name, QtWidgets.QLineEdit())

                getattr(self.ui, button_name).clicked.connect(
                    lambda: self.map_query_item_type(value))

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

        for x in default.mapping:
            try:
                getattr(self.ui, "edit_{}".format(x)).setText(self.map[x])
            except TypeError:
                # Ignore mappings if there is a type error:
                pass

        try:
            self.resize(options.settings.value("namedtableoptions_size"))
        except TypeError:
            pass

    def validate_dialog(self):
        try:
            has_word = "word" in self.map
        except:
            has_word = False
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
        self.ui.edit_word.setText("")
        self.ui.edit_lemma.setText("")
        self.ui.edit_pos.setText("")
        self.ui.edit_transcript.setText("")
        self.ui.edit_gloss.setText("")

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
                line_edit = getattr(self.ui, "edit_{}".format(key))
                line_edit.setText("")
                self.map.pop(key)

        self.map[label] = self._col_select
        line_edit = getattr(self.ui, "edit_{}".format(label))
        line_edit.setText(header)
        self.validate_dialog()

    @staticmethod
    def getOptions(path, fields=[], default=None, parent=None, icon=None):
        dialog = NamedTableOptionsDialog(path, fields, default, parent, icon)
        result = dialog.exec_()
        if isinstance(result, CSVOptions):
            quote = dict(zip(quote_chars.values(), quote_chars.keys()))[
                utf8(dialog.ui.quote_char.currentText())]

            return CSVOptions(
                file_name=utf8(dialog.ui.edit_file_name.text()),
                sep=dialog.separator,
                selected_column=dialog.ui.query_column.value(),
                header=dialog.ui.file_has_headers.isChecked(),
                skip_lines=dialog.ui.ignore_lines.value(),
                encoding=utf8(dialog.ui.combo_encoding.currentText()),
                quote_char=quote,
                mapping=dialog.map,
                dtypes=dialog.file_table.dtypes)
        else:
            return None

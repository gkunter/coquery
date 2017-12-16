# -*- coding: utf-8 -*-
"""
csvoptions.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import codecs
import os
import re
import pandas as pd
import logging

from coquery import options
from coquery.unicode import utf8
from coquery.defines import (msg_csv_encoding_error,
                             msg_csv_file_error,
                             CHARACTER_ENCODINGS)
from .pyqt_compat import QtWidgets, QtGui, QtCore
from .ui.csvOptionsUi import Ui_FileOptions
from .app import get_icon


class CSVOptions(object):
    def __init__(self, file_name="", sep=",", header=True, quote_char='"',
                 skip_lines=0, encoding="utf-8", selected_column=None,
                 mapping=None, dtypes=None, nrows=None, excel=False):
        self.sep = sep
        self.header = header
        self.quote_char = quote_char
        self.skip_lines = skip_lines
        self.encoding = encoding
        self.selected_column = selected_column
        self.mapping = mapping if mapping else {}
        self.dtypes = dtypes
        self.file_name = file_name
        self.nrows = nrows
        self.excel = excel

    def __repr__(self):
        return ("CSVOptions(sep='{}', header={}, quote_char='{}', "
                "skip_lines={}, encoding='{}', selected_column={}, "
                "nrows={}, mapping={}, dtypes={}, excel={})".format(
                    self.sep, self.header, self.quote_char.replace("'", "\'"),
                    self.skip_lines, self.encoding, self.selected_column,
                    self.nrows, self.mapping, self.dtypes, self.excel))

    def read_file(self, path):
        if options.use_xlrd and self.excel:
            df = self.read_excel_file(path)
        else:
            df = self.read_csv_file(path)
        return df

    def read_csv_file(self, path):
        kwargs = {
            "encoding": self.encoding,
            "header": 0 if self.header else None,
            "sep": self.sep,
            "skiprows": self.skip_lines,
            "quotechar": self.quote_char,
            "low_memory": False,
            "error_bad_lines": False}
        try:
            df = pd.read_csv(path, **kwargs)
        except Exception as e:
            print(path)
            from pprint import pprint
            pprint(kwargs)
            logging.error(e)
            print(e)
            raise e
        return df

    def read_excel_file(self, path):
        try:
            df = pd.read_excel(
                path,
                header=0 if self.header else None,
                skiprows=self.skip_lines)
        except Exception as e:
            logging.error(e)
            print(e)
            raise e
        return df


class MyTableModel(QtCore.QAbstractTableModel):
    """
    A table class for the content of a CSV file.
    """
    def __init__(self, parent, df, skip, *args):
        super(MyTableModel, self).__init__(parent, *args)
        self.df = df
        self.header = self.df.columns.values.tolist()
        self.skip_lines = skip

    def rowCount(self, parent):
        return len(self.df.index)

    def columnCount(self, parent):
        return len(self.df.columns.values)

    def data(self, index, role):
        if index.row() < self.skip_lines:
            group = QtGui.QPalette.Disabled
        else:
            group = QtGui.QPalette.Normal

        value = None
        c_role = None
        if role == QtCore.Qt.BackgroundRole:
            c_role = QtGui.QPalette.Base
        elif role == QtCore.Qt.ForegroundRole:
            c_role = QtGui.QPalette.Text
        elif role == QtCore.Qt.DisplayRole:
            value = self.df.iloc[index.row()][index.column()]
            if isinstance(value, pd.np.int64):
                value = int(value)
            elif isinstance(value,
                            (pd.np.float64, pd.np.float, pd.np.float32)):
                value = float(value)

        if c_role:
            return options.cfg.app.palette().brush(group, c_role)
        else:
            return value

    def headerData(self, index, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            group = None
            c_role = None
            value = None

            if index < self.skip_lines:
                group = QtGui.QPalette.Disabled
            else:
                group = QtGui.QPalette.Normal

            if role == QtCore.Qt.DisplayRole:
                value = self.df.index[index]
            elif role == QtCore.Qt.BackgroundRole:
                c_role = QtGui.QPalette.Window
            elif role == QtCore.Qt.ForegroundRole:
                c_role = QtGui.QPalette.WindowText

            if c_role:
                return options.cfg.app.palette().brush(group, c_role)
            else:
                return value

        elif orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                try:
                    return self.header[index]
                except (IndexError, AttributeError):
                    return None

        return None


quote_chars = {
    '"': 'Double quote (")',
    "'": "Single quote (')",
    "": "None"}


class CSVOptionDialog(QtWidgets.QDialog):
    def __init__(self, default=None, parent=None, icon=None, ui=None):
        super(CSVOptionDialog, self).__init__(parent)
        self.file_name = default.file_name
        self.file_content = None

        if ui:
            self.ui = ui()
        else:
            self.ui = Ui_FileOptions()
        self.ui.setupUi(self)
        self.ui.button_browse_file.setIcon(get_icon("Folder"))

        self.ui.edit_file_name.setText(default.file_name)

        for x in quote_chars:
            self.ui.quote_char.addItem(quote_chars[x])

        self.ui.query_column.setValue(1)
        self._col_select = 0
        self._read_from_xls = False

        if default.sep == "\t":
            default.sep = "{tab}"
        if default.sep == " ":
            default.sep = "{space}"
        index = self.ui.separate_char.findText(default.sep)
        if index > -1:
            self.ui.separate_char.setCurrentIndex(index)
        else:
            self.ui.separate_char.setEditText(default.sep)

        if default.selected_column is None:
            self.ui.query_column.hide()
            self.ui.label_query_column.hide()
            self.ui.query_column.setValue(1)
        else:
            self.ui.query_column.setValue(default.selected_column)

        self.ui.spin_nrows.setValue(0 if default.nrows is None else
                                    default.nrows)

        self.ui.file_has_headers.setChecked(default.header)
        self.ui.ignore_lines.setValue(default.skip_lines)

        self.ui.combo_encoding.addItems([x.replace("_", "-")
                                         for x in CHARACTER_ENCODINGS
                                         if x != "ascii"])

        index = self.ui.quote_char.findText(quote_chars[default.quote_char])
        self.ui.quote_char.setCurrentIndex(index)

        self.ui.query_column.valueChanged.connect(self.set_query_column)
        self.ui.query_column.valueChanged.connect(self.validate)

        self.ui.button_browse_file.clicked.connect(self.select_file)
        self.ui.separate_char.editTextChanged.connect(self.set_new_separator)
        self.ui.FilePreviewArea.clicked.connect(self.click_column)
        self.ui.FilePreviewArea.horizontalHeader().sectionClicked.connect(
            self.click_column)

        for signal in (self.ui.ignore_lines.valueChanged,
                       self.ui.file_has_headers.stateChanged,
                       self.ui.quote_char.currentIndexChanged,
                       self.ui.combo_encoding.currentIndexChanged,
                       self.ui.edit_file_name.textChanged,
                       self.ui.spin_nrows.valueChanged):
            signal.connect(self.update_content)

        self.set_encoding_selection(default.encoding)

        self.set_new_separator()

        # Add auto complete to file name edit:
        completer = QtWidgets.QCompleter()
        completer.setModel(QtWidgets.QDirModel(completer))
        self.ui.edit_file_name.setCompleter(completer)

        try:
            self.resize(options.settings.value("csvoptions_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("csvoptions_size", self.size())

    def exec_(self, *args, **kwargs):
        result = super(CSVOptionDialog, self).exec_(*args, **kwargs)
        if result:
            quote = dict(zip(quote_chars.values(), quote_chars.keys()))[
                utf8(self.ui.quote_char.currentText())]
            nrows = self.ui.spin_nrows.value() or None
            return CSVOptions(
                sep=self.separator,
                selected_column=self.ui.query_column.value(),
                header=self.ui.file_has_headers.isChecked(),
                skip_lines=int(self.ui.ignore_lines.value()),
                encoding=utf8(self.ui.combo_encoding.currentText()),
                nrows=nrows,
                quote_char=quote,
                file_name=utf8(self.ui.edit_file_name.text()),
                dtypes=self.file_table.dtypes,
                excel=self._read_from_xls)

    @staticmethod
    def getOptions(default=None, parent=None, icon=None):
        dialog = CSVOptionDialog(default=default, parent=parent, icon=icon)
        return dialog.exec_()

    def set_encoding_selection(self, encoding):
        """
        Disconnect the encoding button box, set the new value, and reconnect.
        """
        encoding = encoding.lower()
        if encoding == "ascii":
            encoding = "utf-8"
        encoding = encoding.replace("iso-", "iso")
        self.ui.combo_encoding.currentIndexChanged.disconnect()
        index = self.ui.combo_encoding.findText(encoding)
        self.ui.combo_encoding.setCurrentIndex(index)
        self.ui.combo_encoding.currentIndexChanged.connect(
            self.update_content)

    def split_file_content(self, file_name):
        """
        Split the content of the file on the basis of the current settings.

        This method also applies the character encoding setting. If there is
        an error with the current character setting, it tries to auto-detect
        a working encoding.
        """
        quote = dict(zip(quote_chars.values(), quote_chars.keys()))[
            utf8(self.ui.quote_char.currentText())]
        if self.ui.file_has_headers.isChecked():
            header = 0
        else:
            header = None
        header = 0 if self.ui.file_has_headers.isChecked() else None
        encoding = utf8(self.ui.combo_encoding.currentText())

        nrows = self.ui.spin_nrows.value() or 99
        if header:
            nrows = nrows + 1

        self._read_from_xls = False
        if options.use_xlrd:
            try:
                df = pd.read_excel(file_name, header=header)
            except Exception as e:
                print(e)
            else:
                self._read_from_xls = True

        if not self._read_from_xls:
            try:
                df = pd.read_table(
                        file_name,
                        header=header,
                        sep=utf8(self.separator),
                        quoting=3 if not quote else 0,
                        quotechar=quote if quote else "#",
                        nrows=nrows,
                        error_bad_lines=False,
                        encoding=encoding)
            except (ValueError, pd.parser.CParserError) as e:
                # this is most likely due to an encoding error.

                if not hasattr(self, "_last_encoding"):
                    # this happened the first time the file content was split.
                    # This is probably due to a wrong encoding setting, so we
                    # try to autodetect the encoding:

                    if options.use_chardet:
                        # detect character encoding using chardet
                        import chardet
                        content = open(file_name, "rb").read()
                        detection = chardet.detect(content[:32000])
                        encoding = detection["encoding"]
                    else:
                        # dumb detection. First try utf-8, then latin-1.
                        try:
                            codecs.open(file_name, "rb",
                                        encoding="utf-8").read()
                        except UnicodeDecodeError:
                            encoding = "latin-1"
                        else:
                            encoding = "utf-8"
                    try:
                        df = pd.read_table(
                                file_name,
                                header=header,
                                sep=utf8(self.separator),
                                quoting=3 if not quote else 0,
                                quotechar=quote if quote else "#",
                                na_filter=False,
                                nrows=100,
                                error_bad_lines=False,
                                encoding=encoding)
                    except (ValueError, pd.parser.CParserError) as e:
                        # the table could still not be read. Raise an error.
                        QtWidgets.QMessageBox.critical(
                            self.parent(), "Query file error",
                            msg_csv_file_error.format(file_name))
                        raise e
                    else:
                        # we have found a working encoding
                        self.set_encoding_selection(encoding)

                elif self._last_encoding != encoding:
                    # we should alert the user that they should use a
                    # different encoding.
                    QtWidgets.QMessageBox.critical(
                        self.parent(), "Query file error",
                        msg_csv_encoding_error.format(file=file_name,
                                                      encoding=encoding))
                    # return to the last encoding, which was hopefully
                    # working:
                    self.set_encoding_selection(self._last_encoding)
                    encoding = self._last_encoding
                else:
                    QtWidgets.QMessageBox.critical(
                        self.parent(), "Query file error",
                        msg_csv_file_error.format(file_name))
                    raise e
        # ascii encoding is always replaced by utf-8
        if encoding == "ascii":
            encoding = "utf-8"
        self._last_encoding = encoding
        if header is None:
            df.columns = ["X{}".format(x) for x in range(len(df.columns))]

        # make column headers SQL-conforming
        df.columns = [re.sub("[^a-zA-Z0-9_]", "_", x) for x in df.columns]

        return df

    def select_file(self):
        """ Call a file selector, and add file name to query file input. """
        name = QtWidgets.QFileDialog.getOpenFileName(
            directory=options.cfg.query_file_path)

        # getOpenFileName() returns different types in PyQt and PySide, fix:
        if type(name) == tuple:
            name = name[0]

        if name:
            self.file_name = utf8(name)
            options.cfg.query_file_path = os.path.dirname(self.file_name)
            self.ui.edit_file_name.setText(self.file_name)
        return name

    def update_content(self):
        current_file = utf8(self.ui.edit_file_name.text())
        if not os.path.exists(current_file):
            self.file_table = pd.DataFrame()
        else:
            self.file_table = self.split_file_content(current_file)

        self.table_model = MyTableModel(self,
                                        self.file_table,
                                        self.ui.ignore_lines.value())
        self.ui.FilePreviewArea.setModel(self.table_model)
        self.set_query_column()
        self.ui.FilePreviewArea.resizeColumnsToContents()

        self.validate()

    def validate(self):
        self.blockSignals(True)
        button_okay = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        S = "QLineEdit {{ background-color: {} }}"
        if not os.path.exists(utf8(self.ui.edit_file_name.text())):
            S = S.format("rgb(255, 255, 192)")
            button_okay.setEnabled(False)
        else:
            pal = options.cfg.app.palette()
            S = S.format(pal.color(QtGui.QPalette.Base).name())
            button_okay.setEnabled(True)

        self.ui.edit_file_name.setStyleSheet(S)
        if self.ui.query_column.value() == 0:
            self.ui.query_column.setValue(1)

        if self.ui.query_column.value() > len(self.file_table.columns):
            button_okay.setEnabled(False)

        self.blockSignals(False)

    def set_new_separator(self):
        sep = utf8(self.ui.separate_char.currentText())
        if not sep:
            return
        if sep == "{space}":
            self.separator = " "
        elif sep == "{tab}":
            self.separator = "\t"
        elif len(sep) > 1:
            self.separator = self.separator[0]
            self.ui.separate_char.setEditText(sep)
        else:
            self.separator = sep
        self.update_content()

    def set_query_column(self):
        self.ui.FilePreviewArea.blockSignals(True)
        self.ui.FilePreviewArea.selectColumn(self.ui.query_column.value() - 1)
        self.ui.FilePreviewArea.blockSignals(False)

    def click_column(self, index):
        if type(index) == int:
            i = index
        else:
            i = index.column()
        if hasattr(self.ui, "query_column"):
            self.ui.query_column.setValue(i+1)
        self._col_select = i

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

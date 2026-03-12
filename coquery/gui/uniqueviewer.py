# -*- coding: utf-8 -*-
"""
uniqueviewer.py is part of Coquery.

Copyright (c) 2016-2026 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import pandas as pd
import os
from PyQt5 import QtCore, QtWidgets

from coquery import options
from coquery.unicode import utf8
from coquery.defines import msg_disk_error, msg_encoding_error
from coquery.gui import errorbox
from coquery.gui import classes
from coquery.gui.threads import CoqThread
from coquery.gui.pyqt_compat import get_toplevel_window
from coquery.gui.ui.uniqueViewerUi import Ui_UniqueViewer


translate = QtWidgets.QApplication.instance().translate


class UniqueViewer(QtWidgets.QDialog):
    def __init__(self, rc_feature=None, db_name=None, uniques=True,
                 parent=None):
        super(UniqueViewer, self).__init__(parent)

        self.ui = Ui_UniqueViewer()
        self.ui.setupUi(self)

        self.ui.button_details = classes.CoqDetailBox(
            str("Corpus: {}   Column: {}"))
        self.ui.verticalLayout.insertWidget(0, self.ui.button_details)

        if uniques:
            label_template = "{label_values}: {{}}"
        else:
            self.setWindowTitle("Entry viewer – Coquery")
            label_template = """
                <table>
                    <tr>
                        <td>{label_values}:</td><td>{{}}</td>
                    </tr>
                    <tr>
                        <td>{label_uniques}:</td><td>{{}}</td>
                    </tr>
                </table>"""
        label = label_template.format(
            label_values=translate(
                "UniqueViewer", "Number of values", None),
            label_uniques=translate(
                "UniqueViewer", "Number of unique values", None))
        self.ui.label = QtWidgets.QLabel(label)
        self.ui.label.setWordWrap(True)
        self.ui.detail_layout = QtWidgets.QHBoxLayout()
        self.ui.detail_layout.addWidget(self.ui.label)
        self.ui.button_details.box.setLayout(self.ui.detail_layout)

        try:
            self.ui.button_details.setExpanded(
                options.settings.value("uniqueviewer_details"))
        except TypeError:
            pass

        self.ui.buttonBox.setDisabled(True)
        self.ui.button_details.setDisabled(True)
        save_button = self.ui.buttonBox.button(self.ui.buttonBox.Save)
        save_button.clicked.connect(self.save_list)

        if uniques:
            self.ui.checkbox_frequency.toggled.connect(self.get_uniques)
        else:
            self.ui.checkbox_frequency.hide()

        self.rc_feature = rc_feature
        self.db_name = db_name
        self.resource = options.get_resource_of_database(db_name)
        self._uniques = uniques

        if self.db_name:
            rc_table = "{}_table".format(rc_feature.partition("_")[0])
            self.table = getattr(self.resource, rc_table)
            self.column = getattr(self.resource, rc_feature)

            self.ui.button_details.setText(
                str(self.ui.button_details.text()).format(
                    self.resource.name,
                    f"{self.table}.{self.column}"))
            self.ui.button_details.setAlternativeText(
                self.ui.button_details.text())
        else:
            self.table = None
            self.column = None

        self.ui.tableWidget.itemClicked.connect(self.entry_clicked)

        try:
            self.resize(options.settings.value("uniqueviewer_size"))
        except TypeError:
            pass
        try:
            self.ui.button_details.setExpanded(
                options.settings.value("uniqueviewer_details"))
        except AttributeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("uniqueviewer_size", self.size())
        options.settings.setValue("uniqueviewer_details",
                                  self.ui.button_details.isExpanded())

    def get_unique(self, frequency: bool = False):
        if not self.db_name:
            return

        engine = options.cfg.current_connection.get_engine(self.db_name)
        if self._uniques:
            if frequency:
                S = (f"SELECT {self.column}, COUNT(*) N FROM {self.table} "
                     f"GROUP BY {self.column}")
            else:
                S = f"SELECT DISTINCT {self.column} FROM {self.table}"
            self.df = pd.read_sql(S, engine)
            self.df = self.df.sort_values(self.column, ascending=True)
        else:
            S = f"SELECT {self.column} FROM {self.table}"
            self.df = pd.read_sql(S, engine)
        engine.dispose()

    def finalize(self):
        self.ui.tableWidget.setSortingEnabled(False)
        self.ui.tableWidget.horizontalHeader().show()
        self.ui.tableWidget.setColumnCount(1)

        # update dialog appearance
        if self._uniques:
            self.ui.label.setText(
                str(self.ui.label.text()).format(len(self.df.index)))
            if not self.ui.checkbox_frequency.isChecked():
                self.ui.tableWidget.horizontalHeader().hide()
            else:
                self.ui.tableWidget.setColumnCount(2)
                self.ui.tableWidget.setHorizontalHeaderLabels(["Value", "N"])
        else:
            self.ui.tableWidget.setHorizontalHeaderLabels(["Click to sort"])

            uniques = sorted(self.df[self.column].dropna().unique())
            value_str = ", ".join([f"'{str(x)}'" for x in uniques[:5]])
            if len(uniques) > 6:
                value_str = f"{value_str}, and {len(uniques) - 5} other values"
            s = f"{len(uniques)} ({value_str})"
            self.ui.label.setText(
                str(self.ui.label.text()).format(len(self.df.index), s))

        self.ui.tableWidget.setRowCount(len(self.df))

        # populate table
        items = (self.df[self.column].apply(utf8)
                                     .apply(QtWidgets.QTableWidgetItem))
        for row, item in enumerate(items):
            self.ui.tableWidget.setItem(row, 0, item)

        if self._uniques and self.ui.checkbox_frequency.isChecked():
            max_freq = max(self.df["N"])
            self.ui.tableWidget.setItemDelegateForColumn(
                1,
                classes.CoqFrequencyBarDelegate(self.ui.tableWidget, max_freq))

            for row, value in enumerate(self.df["N"]):
                item = QtWidgets.QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, int(value))
                item.setTextAlignment(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.ui.tableWidget.setItem(row, 1, item)

        self.ui.tableWidget.setSortingEnabled(True)

        self.ui.progress_bar.setRange(1, 0)
        self.ui.progress_bar.hide()
        self.ui.tableWidget.show()
        self.ui.button_details.show()
        self.ui.label_inform.hide()
        self.ui.label.show()

        self.ui.buttonBox.setEnabled(True)
        self.ui.button_details.setEnabled(True)

    def entry_clicked(self, item, column=None):
        if column:
            text = str(item.text(column))
        else:
            text = str(item.text())
        gui_query_string = get_toplevel_window().ui.edit_query_string
        if self.rc_feature in ("word_label", "corpus_word"):
            gui_query_string.append(text)
        elif self.rc_feature in ("lemma_label", "word_lemma",
                                 "corpus_lemma"):
            gui_query_string.append(f"[{text}]")
        elif self.rc_feature in ("pos_label", "word_pos", "corpus_pos"):
            gui_query_string.append(f"*.[{text}]")
        elif self.rc_feature in ("transcript_label",
                                 "word_transcript",
                                 "corpus_transcript"):
            gui_query_string.append(f"/{text}/")
        elif self.rc_feature in ("lemma_transcript",
                                 "corpus_lemma_transcript"):
            gui_query_string.append(f"[/{text}/]")
        else:
            gui_query_string.append(text)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def onException(self):
        errorbox.ErrorBox.show(self.exc_info, self.exception)

    def save_list(self):
        name = QtWidgets.QFileDialog.getSaveFileName(
            directory=options.cfg.uniques_file_path)
        if isinstance(name, tuple):
            name = name[0]
        if name:
            options.cfg.uniques_file_path = os.path.dirname(name)
            try:
                self.df[self.column].to_csv(
                    name,
                    sep=options.cfg.output_separator,
                    index=False,
                    header=[f"{self.table}.{self.column}"],
                    encoding=options.cfg.output_encoding)
            except IOError:
                QtWidgets.QMessageBox.critical(
                    self, "Disk error", msg_disk_error)
            except (UnicodeEncodeError, UnicodeDecodeError):
                QtWidgets.QMessageBox.critical(
                    self, "Encoding error", msg_encoding_error)

    def get_uniques(self):
        self.ui.progress_bar.setRange(0, 0)
        self.ui.tableWidget.hide()
        self.ui.button_details.hide()
        self.ui.label.hide()

        self.thread = CoqThread(
            self.get_unique,
            self,
            self.ui.checkbox_frequency.isChecked())
        self.thread.taskFinished.connect(self.finalize)
        self.thread.taskException.connect(self.onException)
        self.thread.start()

    @staticmethod
    def show(rc_feature, resource, uniques=True, parent=None):
        dialog = UniqueViewer(rc_feature, resource,
                              uniques=uniques, parent=parent)

        dialog.setVisible(True)
        dialog.get_uniques()
        get_toplevel_window().widget_list.append(dialog)

# -*- coding: utf-8 -*-
"""
uniqueviewer.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import sys
import pandas as pd
import sqlalchemy

from coquery import sqlhelper
from coquery import options
from coquery.unicode import utf8

from . import errorbox
from . import classes
from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window
from .ui.uniqueViewerUi import Ui_UniqueViewer

class UniqueViewer(QtWidgets.QDialog):
    def __init__(self, rc_feature=None, db_name=None, uniques=True, parent=None):
        super(UniqueViewer, self).__init__(parent)

        self.ui = Ui_UniqueViewer()
        self.ui.setupUi(self)

        self.ui.button_details = classes.CoqDetailBox(str("Corpus: {}   Column: {}"))
        self.ui.verticalLayout.insertWidget(0, self.ui.button_details)

        if uniques:
            self.ui.label = QtWidgets.QLabel("Number of values: {}")
        else:
            self.ui.label = QtWidgets.QLabel("<table><tr><td>Number of values:</td><td>{}</td></tr><tr><td>Number of unique values:</td><td>{}</td></tr>")
            self.ui.label.setWordWrap(True)
            self.setWindowTitle("Entry viewer – Coquery")
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
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_list)

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
                    "{}.{}".format(self.table, self.column)))
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

    def get_unique(self):
        if not self.db_name:
            return
        sql = sqlhelper.sql_url(options.cfg.current_server, self.db_name)
        if self._uniques:
            S = "SELECT DISTINCT {} FROM {}".format(self.column, self.table)
            self.df = pd.read_sql(S, sqlalchemy.create_engine(sql))
            self.df = self.df.sort_values(self.column, ascending=True)
        else:
            S = "SELECT {} FROM {}".format(self.column, self.table)
            self.df = pd.read_sql(S, sqlalchemy.create_engine(sql))
        items = (self.df[self.column].apply(utf8)
                                     .apply(QtWidgets.QTableWidgetItem))
        self.ui.tableWidget.setRowCount(len(items))
        self.ui.tableWidget.setColumnCount(1)
        for row, item in enumerate(items):
            self.ui.tableWidget.setItem(row, 0, item)

    def finalize(self):
        #self.ui.progress_spinner.stop()
        self.ui.progress_bar.setRange(1,0)
        self.ui.progress_bar.hide()
        self.ui.tableWidget.show()
        self.ui.button_details.show()
        self.ui.label_inform.hide()
        self.ui.label.show()
        if self._uniques:
            self.ui.label.setText(
                str(self.ui.label.text()).format(len(self.df.index)))
            self.ui.tableWidget.horizontalHeader().hide()
        else:
            self.ui.tableWidget.setHorizontalHeaderLabels(["Click to sort"])
            uniques = sorted(self.df[self.column].unique())
            value_str = ", ".join([str(x) for x in uniques[:5]])
            if len(uniques) > 6:
                value_str = "{}, and {} other values".format(
                    value_str, len(uniques) - 5)
            s = "{} ({})".format(len(uniques), value_str)
            self.ui.label.setText(
                str(self.ui.label.text()).format(len(self.df.index), s))

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
            gui_query_string.append("[{}]".format(text))
        elif self.rc_feature in ("pos_label", "word_pos", "corpus_pos"):
            gui_query_string.append("*.[{}]".format(text))
        elif self.rc_feature in ("transcript_label",
                                 "word_transcript",
                                 "corpus_transcript"):
            gui_query_string.append("/{}/".format(text))
        elif self.rc_feature in ("lemma_transcript",
                                 "corpus_lemma_transcript"):
            gui_query_string.append("[/{}/]".format(text))
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
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.uniques_file_path = os.path.dirname(name)
            try:
                self.df[self.column].to_csv(name,
                           sep=options.cfg.output_separator,
                           index=False,
                           header=["{}.{}".format(self.table, self.column)],
                           encoding=options.cfg.output_encoding)
            except IOError as e:
                QtWidgets.QMessageBox.critical(
                    self, "Disk error", msg_disk_error)
            except (UnicodeEncodeError, UnicodeDecodeError):
                QtWidgets.QMessageBox.critical(
                    self, "Encoding error", msg_encoding_error)

    def get_uniques(self):
        self.ui.progress_bar.setRange(0,0)

        #self.ui.progress_spinner.start()

        self.ui.tableWidget.hide()
        self.ui.button_details.hide()
        self.ui.label.hide()

        self.thread = classes.CoqThread(self.get_unique, self)
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


def main():
    app = QtWidgets.QApplication(sys.argv)
    UniqueViewer.show(None, None)

if __name__ == "__main__":
    main()

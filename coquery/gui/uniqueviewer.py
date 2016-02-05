# -*- coding: utf-8 -*-
"""
uniqueviewer.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import sys
import pandas as pd
import sqlalchemy

from pyqt_compat import QtCore, QtGui
from ui.uniqueViewerUi import Ui_UniqueViewer

import sqlhelper
import options
import errorbox
import QtProgress
import classes

class UniqueViewer(QtGui.QWidget):
    def __init__(self, rc_feature=None, db_name=None, parent=None):
        super(UniqueViewer, self).__init__(parent)
        
        self.ui = Ui_UniqueViewer()
        self.ui.setupUi(self)

        self.ui.button_details = classes.CoqDetailBox(str("Corpus: {}   Column: {}"))
        self.ui.verticalLayout.insertWidget(0, self.ui.button_details)

        self.ui.label = QtGui.QLabel("Number of values: {}")
        self.ui.detail_layout = QtGui.QHBoxLayout()
        self.ui.detail_layout.addWidget(self.ui.label)
        self.ui.button_details.box.setLayout(self.ui.detail_layout)

        try:
            self.ui.button_details.setExpanded(options.settings.value("uniqueviewer_details"))
        except TypeError:
            pass

        self.ui.buttonBox.setDisabled(True)
        self.ui.button_details.setDisabled(True)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.close)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self.save_list)

        self.rc_feature = rc_feature
        self.db_name = db_name
        self.resource = options.get_resource_of_database(db_name)
        
        if self.db_name:
            rc_table = "{}_table".format(rc_feature.partition("_")[0])
            self.table = getattr(self.resource, rc_table)
            self.column = getattr(self.resource, rc_feature)

            self.ui.button_details.setText(
                str(self.ui.button_details.text()).format(
                    self.resource.name, 
                    "{}.{}".format(self.table, self.column)))
        else:
            self.table = None
            self.column = None

        self.ui.treeWidget.itemClicked.connect(self.entry_clicked)
        try:
            self.resize(options.settings.value("uniqueviewer_size"))
        except TypeError:
            pass
        try:
            self.ui.button_details.setExpanded(options.settings.value("uniqueviewer_details"))
        except AttributeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("uniqueviewer_size", self.size())
        options.settings.setValue("uniqueviewer_details", self.ui.button_details.isExpanded())

    def get_unique(self):
        if not self.db_name:
            return

        S = "SELECT DISTINCT {0} FROM {1} ORDER BY {0}".format(self.column, self.table)
        df = pd.read_sql(S, sqlalchemy.create_engine(sqlhelper.sql_url(options.get_mysql_configuration(), self.db_name)))
        self.data = [QtGui.QTreeWidgetItem(self.ui.treeWidget, [x]) for x in df[self.column]]

        for x in self.data:
            x.setToolTip(0, x.text(0))

    def finalize(self):
        self.ui.progress_bar.setRange(1,0)
        self.ui.progress_bar.hide()
        self.ui.treeWidget.show()
        self.ui.label_inform.hide()
        self.ui.label.show()
        self.ui.label.setText(str(self.ui.label.text()).format(len(self.data)))
        self.ui.buttonBox.setEnabled(True)
        self.ui.button_details.setEnabled(True)
        self.data = None
        
    def entry_clicked(self, item, column):
        text = str(item.text(column))
        if self.rc_feature in ("word_label", "corpus_word"):
            options.cfg.main_window.ui.edit_query_string.append(text)
        elif self.rc_feature in ("lemma_label", "word_lemma", "corpus_lemma"):
            options.cfg.main_window.ui.edit_query_string.append("[{}]".format(text))
        elif self.rc_feature in ("pos_label", "word_pos", "corpus_pos"):
            options.cfg.main_window.ui.edit_query_string.append("*.[{}]".format(text))
        elif self.rc_feature in ("transcript_label", "word_transcript", "corpus_transcript"):
            options.cfg.main_window.ui.edit_query_string.append("/{}/".format(text))
        elif self.rc_feature in ("lemma_transcript", "corpus_lemma_transcript"):
            options.cfg.main_window.ui.edit_query_string.append("[/{}/]".format(text))
        else:
            options.cfg.main_window.ui.edit_query_string.append(text)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def onException(self):
        errorbox.ErrorBox.show(self.exc_info, self.exception)

    def save_list(self):
        name = QtGui.QFileDialog.getSaveFileName(directory=options.cfg.uniques_file_path)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.uniques_file_path = os.path.dirname(name)
            try:
                root = self.ui.treeWidget.invisibleRootItem()
                tab = pd.DataFrame.from_records([(str(root.child(i).text(0)),) for i in range(root.childCount())])
                tab.to_csv(name,
                           sep=options.cfg.output_separator,
                           index=False,
                           header=["{}.{}".format(self.table, self.column)],
                           encoding=options.cfg.output_encoding)
            except IOError as e:
                QtGui.QMessageBox.critical(self, "Disk error", msg_disk_error)
            except (UnicodeEncodeError, UnicodeDecodeError):
                QtGui.QMessageBox.critical(self, "Encoding error", msg_encoding_error)
            else:
                self.last_results_saved = True

    @staticmethod
    def show(rc_feature, resource):
        dialog = UniqueViewer(rc_feature, resource)
        dialog.ui.progress_bar.setRange(0,0)
        dialog.ui.treeWidget.hide()
        dialog.ui.label.hide()

        dialog.setVisible(True)
        options.cfg.main_window.widget_list.append(dialog)
        
        dialog.thread = QtProgress.ProgressThread(dialog.get_unique, dialog)
        dialog.thread.taskFinished.connect(dialog.finalize)
        dialog.thread.taskException.connect(dialog.onException)
        dialog.thread.start()
        
def main():
    app = QtGui.QApplication(sys.argv)
    UniqueViewer.show(None, None)
    
if __name__ == "__main__":
    main()
    
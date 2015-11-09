# -*- coding: utf-8 -*-

"""
uniqueviewer.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import pandas as pd

from pyqt_compat import QtCore, QtGui
import uniqueViewerUi
import sys

import options
import error_box
import QtProgress

class UniqueViewer(QtGui.QWidget):
    def __init__(self, rc_feature=None, resource=None, parent=None):
        super(UniqueViewer, self).__init__(parent)
        
        self.ui = uniqueViewerUi.Ui_UniqueViewer()
        self.ui.setupUi(self)
        self.rc_feature = rc_feature
        self.resource = resource

        if self.resource:
            rc_table = "{}_table".format(rc_feature.partition("_")[0])
            self.table = getattr(self.resource, rc_table)
            self.column = getattr(self.resource, rc_feature)
            self.ui.label.setText(str(self.ui.label.text()).format(self.resource.name))
            self.ui.treeWidget.headerItem().setText(0, "{}.{}".format(self.table, self.column))
            
        else:
            self.table = None
            self.column = None
            self.resource = None
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.close)
        self.ui.treeWidget.itemClicked.connect(self.entry_clicked)
            
    def get_unique(self):
        if not self.resource:
            return
        import sqlwrap
        S = "SELECT DISTINCT {0} FROM {1} ORDER BY {0}".format(self.column, self.table)

        self.DB = sqlwrap.SqlDB(
            options.cfg.db_host,
            options.cfg.db_port,
            options.cfg.db_user,
            options.cfg.db_password,
            self.resource.db_name)
        self.DB.execute(S)
        self.data = [QtGui.QTreeWidgetItem(self.ui.treeWidget, [x[0]]) for x in self.DB.Cur]
        for x in self.data:
            x.setToolTip(0, x.text(0))
        self.DB.close()

    def finalize(self):
        self.ui.progress_bar.setRange(1,0)
        self.ui.progress_bar.hide()
        self.ui.treeWidget.show()
        self.data = None
        self.ui.label_2.setText(self.old_label.format(
            self.ui.treeWidget.topLevelItemCount()))
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Save).setEnabled(True)
        
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

    def closeEvent(self, e):
        self.close()

    def onException(self):
        error_box.ErrorBox.show(self.exc_info, self.exception)

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
        dialog.old_label = str(dialog.ui.label_2.text())
        dialog.ui.label_2.setText("Retrieving unique values...")
        dialog.ui.progress_bar.setRange(0,0)
        dialog.ui.treeWidget.hide()
        dialog.setVisible(True)
        options.cfg.main_window.widget_list.append(dialog)
        
        dialog.thread = QtProgress.ProgressThread(dialog.get_unique, dialog)
        dialog.thread.taskFinished.connect(dialog.finalize)
        dialog.thread.taskException.connect(dialog.onException)
        dialog.thread.start()
        
        dialog.ui.buttonBox.button(QtGui.QDialogButtonBox.Save).setEnabled(False)
        dialog.ui.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(dialog.save_list)

def main():
    app = QtGui.QApplication(sys.argv)
    UniqueViewer.show(None, None)
    
if __name__ == "__main__":
    main()
    
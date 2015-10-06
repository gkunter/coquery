from __future__ import division
from __future__ import unicode_literals

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
            self.table = self.resource.__getattribute__(self.resource, rc_table)
            self.column = self.resource.__getattribute__(self.resource, rc_feature)
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
        #QtProgress.ProgressIndicator(dialog.get_unique, finalize=dialog.finalize)

def main():
    app = QtGui.QApplication(sys.argv)
    UniqueViewer.show(None, None)
    
if __name__ == "__main__":
    main()
    
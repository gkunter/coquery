from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
import uniqueViewerUi
import sys

import options

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
        S = "SELECT DISTINCT {} FROM {}".format(self.column, self.table)

        DB = sqlwrap.SqlDB(
            options.cfg.db_host,
            options.cfg.db_port,
            options.cfg.db_user,
            options.cfg.db_password,
            self.resource.db_name)
        DB.execute(S)
        
        for x in DB.Cur:
            item = QtGui.QTreeWidgetItem()
            item.setText(0, x[0])
            item.setToolTip(0, x[0])
            self.ui.treeWidget.addTopLevelItem(item)
        DB.close()
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.treeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        self.ui.label_2.setText(str(self.ui.label_2.text()).format(
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
            
    @staticmethod
    def show(rc_feature, resource):
        dialog = UniqueViewer(rc_feature, resource)
        dialog.get_unique()
        dialog.setVisible(True)
        options.cfg.main_window.widget_list.append(dialog)

def main():
    app = QtGui.QApplication(sys.argv)
    UniqueViewer.show(None, None)
    
if __name__ == "__main__":
    main()
    
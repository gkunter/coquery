# -*- coding: utf-8 -*-
"""
linkselect.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui

import sys
import linkselectUi

import options
from defines import *
from classes import CoqTreeItem

class LinkSelect(QtGui.QDialog):
    def __init__(self, feature, corpus_omit = [], parent=None):
        
        super(LinkSelect, self).__init__(parent)
        self.omit_tables = ["coquery", "corpus"]
        self.corpus_omit = corpus_omit
        self.ui = linkselectUi.Ui_LinkSelect()
        self.ui.setupUi(self)
        self.ui.label.setText(str(self.ui.label.text()).format(resource_feature=feature))
        self.ui.label_2.setText(str(self.ui.label_2.text()).format(resource_feature=feature))
        self.insert_data()
        self.ui.treeWidget.itemActivated.connect(self.selected)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        
    def selected(self):
        item = self.ui.treeWidget.selectedItems()[0]
        if item.childCount():
            item.setExpanded(True)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        
    def insert_data(self):
        resources = options.get_available_resources(options.cfg.current_server)
        for corpus in [x for x in resources if x not in self.corpus_omit]:
            resource = resources[corpus][0]
            table_dict = resource.get_table_dict()
            
            corpusItem =  CoqTreeItem()
            corpusItem.setText(0, corpus.upper())
            corpusItem.setObjectName(corpus)
            for table in [x for x in table_dict if x not in self.omit_tables]:
                table_string = getattr(resource, "{}_table".format(table))
                tableItem = CoqTreeItem()
                tableItem.setText(0, table_string)
                tableItem.setObjectName(table)
                for feature in [x for x in table_dict[table] if not x.rpartition("_")[-1] in ("table", "id")]:
                    featureItem = CoqTreeItem()
                    featureItem.setText(0, getattr(resource, feature))
                    featureItem.setObjectName(feature)
                    tableItem.addChild(featureItem)
                if tableItem.childCount():
                    corpusItem.addChild(tableItem)
            if corpusItem.childCount():
                self.ui.treeWidget.addTopLevelItem(corpusItem)
        self.ui.treeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
            
    def closeEvent(self, *args):
        options.cfg.link_select_view_height = self.height()
        options.cfg.link_select_view_width = self.width()        
        
    @staticmethod
    def display(feature, corpus_omit, parent=None):
        dialog = LinkSelect(feature, corpus_omit, parent=parent)        
        dialog.setVisible(True)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            selected = dialog.ui.treeWidget.selectedItems()[0]
            
            feature = selected.objectName()
            table = selected.parent().objectName()
            corpus = selected.parent().parent().objectName()
            ignore_case = dialog.ui.checkBox.checkState()
            
            return (corpus, table, feature, ignore_case)
        else:
            return None
        

def main():
    app = QtGui.QApplication(sys.argv)
    viewer = LinkSelect()
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    
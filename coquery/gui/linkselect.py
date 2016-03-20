# -*- coding: utf-8 -*-
"""
linkselect.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import sys

from coquery import options
from coquery.defines import *

from .classes import CoqTreeItem
from .pyqt_compat import QtCore, QtGui
from .ui.linkselectUi import Ui_LinkSelect

class Link(object):
    def __init__(self, tree_item, ignore_case=True):
        self.resource = tree_item.parent().parent().objectName()
        resource = options.cfg.current_resources[self.resource][0] 

        self.rc_feature = tree_item.objectName()
        self.table = "{}".format(tree_item.parent().objectName())
        self.db_name = resource.db_name
        self.case = ignore_case
        
        self.table_name = getattr(resource, "{}_table".format(self.table))
        self.feature_name = getattr(resource, self.rc_feature)
        self.label = ".".join([self.resource, self.table_name, self.feature_name])

class LinkSelect(QtGui.QDialog):
    def __init__(self, feature, corpus, corpus_omit = [], parent=None):
        
        super(LinkSelect, self).__init__(parent)
        self.omit_tables = ["coquery", "statistics"]
        self.corpus_omit = corpus_omit
        self.ui = Ui_LinkSelect()
        self.ui.setupUi(self)
        self.ui.label.setText(str(self.ui.label.text()).format(
            resource_feature=feature, corpus=corpus))
        self.insert_data()
        self.ui.treeWidget.itemActivated.connect(self.selected)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        try:
            self.resize(options.settings.value("linkselect_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("linkselect_size", self.size())
        
    def selected(self):
        item = self.ui.treeWidget.selectedItems()[0]
        if item.childCount():
            item.setExpanded(True)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        
    def insert_data(self):
        for corpus in [x for x in options.cfg.current_resources if x not in self.corpus_omit]:
            resource = options.cfg.current_resources[corpus][0]
            tag_list = resource.get_query_item_map()
            table_dict = resource.get_table_dict()

            corpusItem = CoqTreeItem()
            corpusItem.setText(0, corpus)
            corpusItem.setObjectName(corpus)
            corpusItem.setIcon(0, self.parent().get_icon("database"))
            for table in [x for x in table_dict if x not in self.omit_tables]:
                table_string = getattr(resource, "{}_table".format(table))
                tableItem = CoqTreeItem()
                tableItem.setText(0, table_string)
                tableItem.setObjectName(table)
                tableItem.setIcon(0, self.parent().get_icon("table"))
                for feature in [x for x in table_dict[table] if not x.rpartition("_")[-1] in ("table", "id")]:
                    featureItem = CoqTreeItem()
                    featureItem.setText(0, getattr(resource, feature))
                    featureItem.setObjectName(feature)
                    tableItem.addChild(featureItem)
                    if feature in list(tag_list.values()):
                        featureItem.setIcon(0, self.parent().get_icon("tag"))
                    
                if tableItem.childCount():
                    corpusItem.addChild(tableItem)
            if corpusItem.childCount():
                self.ui.treeWidget.addTopLevelItem(corpusItem)
        self.ui.treeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
            
    @staticmethod
    def display(feature, corpus, corpus_omit, parent=None):
        dialog = LinkSelect(feature, corpus, corpus_omit, parent=parent)        
        dialog.setVisible(True)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            selected = dialog.ui.treeWidget.selectedItems()[0]
            return Link(selected, dialog.ui.checkBox.checkState())
        else:
            return None
        

def main():
    app = QtGui.QApplication(sys.argv)
    viewer = LinkSelect()
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    

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
from coquery.corpus import BaseResource
from coquery.defines import *
from coquery.unicode import utf8
from coquery.links import Link

from .classes import CoqTreeItem
from .pyqt_compat import QtCore, QtGui
from .ui.linkselectUi import Ui_LinkSelect

class LinkSelect(QtGui.QDialog):
    def __init__(self, res_from, rc_from, corpus_omit=[], parent=None):
        super(LinkSelect, self).__init__(parent)
        self.corpus_omit = corpus_omit
        self.res_from = res_from
        self.rc_from = rc_from
        
        self.ui = Ui_LinkSelect()
        self.ui.setupUi(self)
        self.ui.label.setText(str(self.ui.label.text()).format(
            resource_feature=getattr(res_from, rc_from), 
            corpus=res_from.name))

        self.insert_data()
        self.ui.treeWidget.itemActivated.connect(self.selected)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        try:
            self.resize(options.settings.value("linkselect_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("linkselect_size", self.size())
        
    @staticmethod
    def pick(res_from, rc_from, corpus_omit, parent=None):
        dialog = LinkSelect(res_from, rc_from, corpus_omit, parent=parent)        
        dialog.setVisible(True)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            selected_column_item = dialog.ui.treeWidget.selectedItems()[0]
            selected_table_item = selected_column_item.parent()
            selected_resource_item = selected_table_item.parent()

            link = Link(res_from=res_from.name, 
                        rc_from=rc_from, 
                        res_to=selected_resource_item.objectName(), 
                        rc_to=selected_column_item.objectName(),
                        case=bool(dialog.ui.checkBox.checkState()))
            return link
        else:
            return None

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
            if self.parent():
                corpusItem.setIcon(0, self.parent().get_icon("database"))
            for table in [x for x in table_dict if x not in self.res_from.special_table_list]:
                table_string = getattr(resource, "{}_table".format(table))
                tableItem = CoqTreeItem()
                tableItem.setText(0, table_string)
                tableItem.setObjectName(table)
                if self.parent():
                    tableItem.setIcon(0, self.parent().get_icon("table"))
                for feature in [x for x in table_dict[table] if not x.rpartition("_")[-1] in ("table", "id")]:
                    featureItem = CoqTreeItem()
                    featureItem.setText(0, getattr(resource, feature))
                    featureItem.setObjectName(feature)
                    tableItem.addChild(featureItem)
                    if feature in list(tag_list.values()) and self.parent():
                        featureItem.setIcon(0, self.parent().get_icon("tag"))
                    
                if tableItem.childCount():
                    corpusItem.addChild(tableItem)
            if corpusItem.childCount():
                self.ui.treeWidget.addTopLevelItem(corpusItem)
        self.ui.treeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

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
from .pyqt_compat import QtCore, QtGui, get_toplevel_window
from .ui.linkselectUi import Ui_LinkSelect

class LinkSelect(QtGui.QDialog):
    def __init__(self, res_from=None, rc_from=None, corpus_omit=[], only_resources=False, parent=None):
        super(LinkSelect, self).__init__(parent)
        self.corpus_omit = corpus_omit
        self.res_from = res_from
        self.rc_from = rc_from
        
        self.ui = Ui_LinkSelect()
        self.ui.setupUi(self)
        self.from_text = utf8(self.ui.label_from.text())
        self.from_corpus_text = utf8(self.ui.label_from_corpus.text())
        self.to_text = utf8(self.ui.label_to.text())
        self.explain_text = utf8(self.ui.label_explain.text())

        self.insert_data(only_resources)
        self.ui.combo_corpus.currentIndexChanged.connect(self.external_changed)
        self.ui.tree_resource.currentItemChanged.connect(self.resource_changed)
        self.ui.tree_external.currentItemChanged.connect(self.external_resource_changed)

        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        try:
            self.resize(options.settings.value("linkselect_size"))
        except TypeError:
            pass

        self.ui.tree_resource.setup_resource(get_toplevel_window().resource,
                                             skip=("coquery", "db"),
                                             checkable=False,
                                             links=False)
        self.ui.tree_resource.allSetExpanded(True)
        self.ui.tree_resource.setCurrentItemByString(self.rc_from)

    def check_dialog(self):
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        self.ui.widget_link_info.hide()
        from_item = self.ui.tree_resource.currentItem()
        to_item = self.ui.tree_external.currentItem()
        if not to_item or not from_item:
            return
        if to_item.childCount() or from_item.childCount():
            return

        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        self.ui.widget_link_info.show()

    def set_to_labels(self, **kwargs):
        self.ui.label_to.setText(self.to_text.format(**kwargs))
        self.ui.label_explain.setText(self.explain_text.format(**kwargs))

    def set_from_labels(self, **kwargs):
        self.ui.label_from.setText(self.from_text.format(**kwargs))
        self.ui.label_from_corpus.setText(self.from_corpus_text.format(**kwargs))

    def closeEvent(self, event):
        options.settings.setValue("linkselect_size", self.size())

    def exec_(self, *args, **kwargs):
        result = super(LinkSelect, self).exec_(*args, **kwargs)
        if result == self.Accepted:
            from_item = self.ui.tree_resource.currentItem()
            to_item = self.ui.tree_external.currentItem()
            return Link(res_from=self.res_from.name,
                        rc_from=utf8(from_item.objectName()),
                        res_to=utf8(self.ui.combo_corpus.currentText()),
                        rc_to=utf8(to_item.objectName()),
                        case=bool(self.ui.checkBox.checkState()))
        else:
            return None

    @staticmethod
    def pick(res_from, rc_from, corpus_omit, parent=None):
        dialog = LinkSelect(res_from, rc_from, corpus_omit, parent=parent)
        dialog.setVisible(True)
        return dialog.exec_()

    @staticmethod
    def get_resource(corpus_omit, parent=None):
        dialog = LinkSelect(res_from=None, rc_from=None, corpus_omit=corpus_omit, only_resources=True, parent=parent)        
        dialog.setVisible(True)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            x = dialog.ui.treeWidget.selectedItems()[0]
            return x.objectName()
        else:
            return None

    def resource_changed(self, current, prev):
        if current.parent():
            from_table = utf8(current.parent().text(0))
            from_resource = utf8(current.text(0))
        else:
            from_table = "<not selected>"
            from_resource = "<not selected>"
        self.set_from_labels(
            from_res=self.res_from.name,
            from_table=from_table,
            from_resource=from_resource)
        self.check_dialog()

    def external_changed(self, index):
        if type(index) == int:
            corpus = utf8(self.ui.combo_corpus.itemText(index))
        else:
            corpus = utf8(index)

        resource, _, _ = options.get_resource(corpus)
        self.ui.tree_external.setup_resource(resource,
                                             skip=("coquery"),
                                             checkable=False,
                                             links=False)
        self.ui.tree_external.allSetExpanded(True)

    def external_resource_changed(self, current, prev):
        to_res = utf8(self.ui.combo_corpus.currentText())
        to_feature = utf8(current.text(0))
        if current.parent():
            to_table = utf8(current.parent().text(0))
        else:
            to_table = "invalid"
        self.set_to_labels(to=to_res, to_resource=to_feature, to_table=to_table)
        self.check_dialog()

    def insert_data(self, only_resources=False):
        corpora = sorted([resource.name for _, (resource, _0, _1, _2)
                   in options.cfg.current_resources.items()
                   if resource.name != self.res_from.name])
        self.ui.combo_corpus.addItems(corpora)
        min_width = self.ui.combo_corpus.sizeHint().width()
        self.ui.label_from_corpus.setMinimumWidth(min_width)
        self.external_changed(self.ui.combo_corpus.itemText(0))
        return

        for corpus in [x for x in options.cfg.current_resources if x not in self.corpus_omit]:
            resource = options.cfg.current_resources[corpus][0]
            tag_list = resource.get_query_item_map()
            table_dict = resource.get_table_dict()

            corpusItem = CoqTreeItem()
            corpusItem.setText(0, corpus)
            corpusItem.setObjectName(corpus)
            if self.parent():
                corpusItem.setIcon(0, self.parent().get_icon("Database"))
            if not only_resources:
                for table in [x for x in table_dict if x not in self.res_from.special_table_list]:
                    table_string = getattr(resource, "{}_table".format(table))
                    tableItem = CoqTreeItem()
                    tableItem.setText(0, table_string)
                    tableItem.setObjectName(table)
                    if self.parent():
                        tableItem.setIcon(0, self.parent().get_icon("Table"))
                    for feature in [x for x in table_dict[table] if not x.rpartition("_")[-1] in ("table", "id")]:
                        featureItem = CoqTreeItem()
                        featureItem.setText(0, getattr(resource, feature))
                        featureItem.setObjectName(feature)
                        tableItem.addChild(featureItem)
                        if feature in list(tag_list.values()) and self.parent():
                            featureItem.setIcon(0, self.parent().get_icon("Price Tag"))
                        
                    if tableItem.childCount():
                        corpusItem.addChild(tableItem)
                if corpusItem.childCount():
                    self.ui.treeWidget.addTopLevelItem(corpusItem)
            else:
                self.ui.treeWidget.addTopLevelItem(corpusItem)
        self.ui.treeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

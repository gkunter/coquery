# -*- coding: utf-8 -*-
"""
resourcetree.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import logging

from coquery import options
from coquery.defines import *
from coquery.unicode import utf8

from .pyqt_compat import QtCore, QtGui
from . import classes

class CoqResourceTree(classes.CoqTreeWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(CoqResourceTree, self).__init__(*args, **kwargs)
        self.selected = []
        self.setParent(parent)

        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
    def setParent(self, parent):
        self.parent = parent
        if self.parent != None:
            self.customContextMenuRequested.connect(self.parent.get_output_column_menu)
            
    def setup_resource(self, resource):
        """ 
        Construct a new output option tree.
        
        The content of the tree depends on the features that are available in
        the current resource. All features that were checked in the old output 
        option tree will also be checked in the new one. In this way, users 
        can easily change between corpora without loosing their output column 
        selections.        
        """
        
        def create_root(table):
            """
            Create a CoqTreeItem object that acts as a table root for the 
            given table.
            """
            if table != "coquery":
                label = getattr(resource, "{}_table".format(table))
            else:
                label = "Query"

            root = classes.CoqTreeItem()
            root.setObjectName("{}_table".format(table))
            root.setFlags(root.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable)
            root.setText(0, label)
            root.setCheckState(0, QtCore.Qt.Unchecked)
            return root            
        
        def create_item(rc_feature):
            """
            Creates a CoqTreeItem object that acts as a table node for the 
            given resource feature. The item contains the appropriate 
            decorations (tags and labels).
            """
            leaf = classes.CoqTreeItem()
            leaf.setObjectName(rc_feature)
            leaf.setCheckState(0, QtCore.Qt.Unchecked)
            label = getattr(resource, rc_feature)
            # Add labels if this feature is mapped to a query item type
            
            if rc_feature == getattr(resource, "query_item_word", None):
                label = "{} [Word]".format(label)
            if rc_feature == getattr(resource, "query_item_lemma", None):
                label = "{} [Lemma]".format(label)
            if rc_feature == getattr(resource, "query_item_transcript", None):
                label = "{} [Transcript]".format(label)
            if rc_feature == getattr(resource, "query_item_pos", None):
                label = "{} [POS]".format(label)
            if rc_feature == getattr(resource, "query_item_gloss", None):
                label = "{} [Gloss]".format(label)

            leaf.setText(0, label)
            if label != getattr(resource, rc_feature):
                leaf.setIcon(0, self.parent.get_icon("tag"))
                root.setIcon(0, self.parent.get_icon("tag"))
            
            return leaf
        
        self.blockSignals(True)
        self.clear()
        
        table_dict = resource.get_table_dict()
        # Ignore denormalized tables:
        tables = [x for x in table_dict.keys() if not x.startswith("corpusngram")]
        # ignore internal  variables of the form {table}_id, {table}_table,
        # {table}_table_{other}
        for table in tables:
            for var in list(table_dict[table]):
                if var == "corpus_id":
                    continue
                if (var.endswith(("_table", "_id")) or 
                    var.startswith(("{}_table".format(table), "corpusngram_"))):
                    table_dict[table].remove(var)
                    
        # Rearrange table names so that they occur in a sensible order:
        for x in reversed(["word", "meta", "lemma", "corpus", "speaker", "source", "file"]):
            if x in tables:
                tables.remove(x)
                tables.insert(0, x)
        tables.remove("coquery")
        tables.append("coquery")
        
        # populate the with a root for each table, and nodes for each 
        # resource in the tables:
        for table in tables:
            if table != "coquery":
                resource_list = sorted(table_dict[table], key=lambda x: getattr(resource, x))
            else:
                resource_list = table_dict[table]
            
            if resource_list:
                root = create_root(table)
                self.addTopLevelItem(root)
                for rc_feature in resource_list:
                    root.addChild(create_item(rc_feature))

        for link in options.cfg.table_links[options.cfg.current_server]:
            if link.res_from == resource.name:
                self.add_external_link(self.getItem(link.rc_from), link)

        for _, group_column in self.parent.ui.list_group_columns.columns:
            if not hasattr(resource, group_column):
                self.parent.ui.list_group_columns.remove_resource(group_column)

        self.blockSignals(False)

    def add_external_link(self, item, link):
        """
        Adds an external link to the given item.
        """
        print("add_external_link({}, {})".format(item, link))
        try:
            ext_res, _, _, _ = options.cfg.current_resources[link.res_to]
        except KeyError:
            # external resource does not exist (anymore), return
            return
        
        _, _, tab, feat = ext_res.split_resource_feature(link.rc_to)
        ext_table = "{}_table".format(tab)
        
        tree = classes.CoqTreeLinkItem()
        tree.setCheckState(0, QtCore.Qt.Unchecked)
        tree.setLink(link)
        tree.setText(0, "{}.{}".format(link.res_to, getattr(ext_res, ext_table)))

        table = ext_res.get_table_dict()[tab]
        table = sorted(table, key=lambda x: getattr(ext_res, x))
        # fill new tree with the features from the linked table (exclude
        # the linking feature):
        for rc_feature in [x for x in table if x != link.rc_to]:
            print("\t", rc_feature)
            _, _, _, feature = ext_res.split_resource_feature(rc_feature)
            # exclude special resource features
            if feature not in ("id", "table") and not feature.endswith("_id"):
                new_item = classes.CoqTreeItem()
                new_item.setText(0, getattr(ext_res, rc_feature))
                new_item.rc_feature = rc_feature
                new_item.setObjectName("{}.{}".format(link.get_hash(), rc_feature))
                new_item.setCheckState(0, QtCore.Qt.Unchecked)
                tree.addChild(new_item)

        ## Insert newly created table as a child of the linked item:
        item.addChild(tree)
        item.setExpanded(True)

    def remove_external_link(self, item):
        """
        Remove either a link from the column tree.        
        
        Parameters
        ----------
        item : CoqTreeItem
            An entry in the output column list representing an external table.
        """
        item.parent().removeChild(item)

    def select(self, selected):
        def traverse(node):
            for child in [node.child(i) for i in range(node.childCount())]:
                if utf8(child.objectName()) in selected:
                    child.setCheckState(0, QtCore.Qt.Checked)
                    child.update_checkboxes(0, expand=True)
                    traverse(child)
        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            traverse(root)

    def selected(self):
        def traverse(node):
            checked = []
            for child in [node.child(i) for i in range(node.childCount())]:
                if child.checkState() != QtCore.Qt.Unchecked:
                    resource = utf8(child.objectName())
                    if not resource.endswith("_table"):
                        checked.append(resource)
                    checked += traverse(child)
            return checked
        
        l = []
        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            l += traverse(root)
        return l
            
logger = logging.getLogger(NAME)
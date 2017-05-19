# -*- coding: utf-8 -*-
"""
resourcetree.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import warnings


from coquery import options
from coquery.defines import *
from coquery.unicode import utf8

from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window
from . import classes


class CoqResourceTree(classes.CoqTreeWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(CoqResourceTree, self).__init__(*args, **kwargs)
        self.setParent(parent)

        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._items_checkable = True
        self.itemChanged.connect(self.on_change)

    def on_change(self, item):
        item.on_change()

    def allSetExpanded(self, b):
        def traverse(node):
            for child in self.nodeItems(node):
                child.setExpanded(b)

        for root in self.rootItems():
            traverse(root)
            root.setExpanded(b)

    def setCurrentItemByString(self, s, **kwargs):
        def traverse(node):
            if utf8(node.objectName()) == s:
                return node
            for child in self.nodeItems(node):
                found = traverse(child)
                if found:
                    return found

        for root in self.rootItems():
            item = traverse(root)
            if item:
                super(CoqResourceTree, self).setCurrentItem(item)

    def rootItems(self):
        return [self.topLevelItem(i) for i in
                range(self.topLevelItemCount())]

    def nodeItems(self, node):
        return [node.child(i) for i in range(node.childCount())]

    def setup_resource(self, resource, skip=(), checkable=True, links=True,
                       view_tables=False):
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
                label = getattr(resource, "{}_table".format(table), table)
            else:
                label = "Query"

            root = classes.CoqTreeItem()
            root.setObjectName("{}_table".format(table))
            root.setText(0, label)
            if checkable:
                root.setFlags(root.flags() |
                            QtCore.Qt.ItemIsUserCheckable |
                            QtCore.Qt.ItemIsSelectable)
                root.setCheckState(0, QtCore.Qt.Unchecked)
            return root

        def create_item(rc_feature, root=None):
            """
            Creates a CoqTreeItem object that acts as a table node for the
            given resource feature. The item contains the appropriate
            decorations (tags and labels).
            """
            leaf = classes.CoqTreeItem()
            leaf.setObjectName(rc_feature)
            if checkable:
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
                leaf.setIcon(0, get_toplevel_window().get_icon("Price Tag"))
                if root:
                    root.setIcon(0, get_toplevel_window().get_icon("Price Tag"))
            return leaf

        def fill_grouped():
            rc_features = [x for x in resource.get_queryable_features()
                           if (not x.endswith(("_id", "_table")) and
                               not x.startswith(("tag_")) and
                               not x.startswith(skip))]

            rc_features.extend(resource.get_exposed_ids())

            segment_features = [x for x in rc_features
                                if x.startswith("segment_")]
            file_features = [x for x in rc_features if x.startswith("file_")]
            lexicon_features = [x for x, _ in resource.get_lexicon_features()
                                if (x not in segment_features and
                                    not x.startswith(("tag_")))]

            lexicon_root = create_root("Tokens")
            source_root = create_root("Texts")
            speaker_root = create_root("Speakers")
            file_root = create_root("Files")
            segment_root = create_root("Segments")
            query_root = create_root("Query string")

            for rc_feature in rc_features:
                leaf = create_item(rc_feature)
                try:
                    target_root = source_root

                    if rc_feature in segment_features:
                        target_root = segment_root
                    elif (rc_feature in lexicon_features or
                        resource.is_tokenized(rc_feature)):
                        target_root = lexicon_root
                    elif rc_feature in file_features:
                        target_root = file_root

                    if rc_feature.startswith("coquery_"):
                        target_root = query_root

                    if rc_feature.startswith("speaker_"):
                        target_root = speaker_root
                    if (hasattr(resource, "speaker_features") and
                        rc_feature in resource.speaker_features):
                        target_root = speaker_root
                except Exception as e:
                    warnings.warn(str(e))
                    print(e)
                finally:
                    target_root.addChild(leaf)

            if lexicon_root.childCount():
                self.addTopLevelItem(lexicon_root)
                lexicon_root.sortChildren(0, QtCore.Qt.AscendingOrder)
            if segment_root.childCount():
                self.addTopLevelItem(segment_root)
                segment_root.sortChildren(0, QtCore.Qt.AscendingOrder)
            if source_root.childCount():
                self.addTopLevelItem(source_root)
                source_root.sortChildren(0, QtCore.Qt.AscendingOrder)
            if speaker_root.childCount():
                self.addTopLevelItem(speaker_root)
                speaker_root.sortChildren(0, QtCore.Qt.AscendingOrder)
            if file_root.childCount():
                self.addTopLevelItem(file_root)
                file_root.sortChildren(0, QtCore.Qt.AscendingOrder)
            if query_root.childCount():
                self.addTopLevelItem(query_root)
                query_root.sortChildren(0, QtCore.Qt.AscendingOrder)

        def fill_tables():
            queryable_features = resource.get_queryable_features()
            table_dict = resource.get_table_dict()
            # Ignore denormalized tables:
            tables = [x for x in table_dict.keys()
                      if not x.startswith("corpusngram") and
                      not x.startswith(skip)]
            # ignore internal  variables of the form {table}_id, {table}_table,
            # {table}_table_{other}
            for table in tables:
                rc_tab = "{}_table".format(table)
                for var in list(table_dict[table]):
                    if var == "corpus_id":
                        continue
                    if (var.endswith(("_table", "_id")) or
                            var.startswith((rc_tab, "corpusngram_"))):
                        table_dict[table].remove(var)

            # Rearrange table names so that they occur in a sensible order:
            for x in reversed(["word", "meta", "lemma", "corpus",
                               "speaker", "source", "file"]):
                if x in tables:
                    tables.remove(x)
                    tables.insert(0, x)
            try:
                tables.remove("coquery")
                tables.append("coquery")
            except ValueError:
                pass

            # populate the tree with a root for each table, and nodes for each
            # resource in the tables:
            for table in tables:
                if table != "coquery":
                    resource_list = sorted(table_dict[table],
                                           key=lambda x: getattr(resource, x))
                else:
                    resource_list = table_dict[table]

                if resource_list:
                    root = create_root(table)
                    self.addTopLevelItem(root)
                    for rc_feature in [x for x in resource_list if
                                       x in queryable_features]:
                        root.addChild(create_item(rc_feature, root))

        self.blockSignals(True)
        self.clear()

        if view_tables:
            fill_tables()
        else:
            view_mode = getattr(resource, "default_view_mode", VIEW_MODE_GROUPED)
            if view_mode == VIEW_MODE_GROUPED:
                fill_grouped()
            elif view_mode == VIEW_MODE_TABLES:
                fill_tables()

        if links:
            # restore external links:
            for link in options.cfg.table_links[options.cfg.current_server]:
                if link.res_from == resource.name:
                    self.add_external_link(link)

        self.blockSignals(False)

    def add_external_link(self, link):
        """
        Adds an external link to the given item.
        """
        try:
            ext_res, _, _, _ = options.cfg.current_resources[link.res_to]
        except KeyError:
            # external resource does not exist (anymore), return
            return

        _, tab, feat = ext_res.split_resource_feature(link.rc_to)
        ext_table = "{}_table".format(tab)

        tree = classes.CoqTreeExternalTable()
        tree.setCheckState(0, QtCore.Qt.Unchecked)
        tree.setLink(link)
        tree.setText(0, "{}.{}".format(link.res_to,
                                       getattr(ext_res, ext_table)))

        table = ext_res.get_table_dict()[tab]
        table = sorted(table, key=lambda x: getattr(ext_res, x))
        # fill new tree with the features from the linked table (exclude
        # the linking feature):
        for rc_feature in [x for x in table]:
            _, _, feature = ext_res.split_resource_feature(rc_feature)
            # exclude special resource features
            if feature not in ("id", "table") and not feature.endswith("_id"):
                new_item = classes.CoqTreeExternalItem()
                new_item.setText(0, getattr(ext_res, rc_feature))
                new_item.rc_feature = rc_feature
                new_item.setObjectName("{}.{}".format(link.get_hash(),
                                                      rc_feature))
                new_item.setCheckState(0, QtCore.Qt.Unchecked)
                tree.addChild(new_item)

        item = self.getItem(link.rc_from)

        # Insert newly created table as a child of the linked item:
        try:
            item.addChild(tree)
            item.setExpanded(True)
        except AttributeError as e:
            print(e)
            pass

    def remove_external_link(self, item):
        """
        Remove either a link from the column tree.

        Parameters
        ----------
        item : CoqTreeItem
            An entry in the output column list representing an external table.
        """
        def traverse(node):
            if node.checkState(0) != QtCore.Qt.Unchecked:
                node.setCheckState(0, QtCore.Qt.Unchecked)
            for child in self.nodeItems(node):
                traverse(child)
        traverse(item)
        item.parent().removeChild(item)

    def select(self, selected):
        def traverse(node):
            for child in self.nodeItems(node):
                if utf8(child.objectName()) in selected:
                    child.setCheckState(0, QtCore.Qt.Checked)
                    child.update_checkboxes(0, expand=True)

        for root in self.rootItems():
            traverse(root)

    def selected(self):
        def traverse(node):
            checked = set()
            for child in [node.child(i) for i in range(node.childCount())]:
                if child.checkState(0) != QtCore.Qt.Unchecked:
                    resource = utf8(child.objectName())
                    if (resource and not resource.endswith("_table") and
                            child.checkState(0) == QtCore.Qt.Checked):
                        checked.add(resource)
                    checked.update(traverse(child))
            return checked

        l = set()
        for root in self.rootItems():
            l.update(traverse(root))
        return l

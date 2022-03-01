# -*- coding: utf-8 -*-
"""
grouptree.py is part of Coquery.

Copyright (c) 2017-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal

from coquery.managers import Group
from coquery.gui.editfilters import format_filter
from coquery.gui.groups import GroupDialog
from coquery.gui.pyqt_compat import get_toplevel_window
from coquery.gui.ui.groupWidgetUi import Ui_GroupWidget


class CoqGroupTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, group):
        super(CoqGroupTreeItem, self).__init__()
        self.change_group(group)

    def add_group_info(self, group):
        self.takeChildren()

        icon_getter = get_toplevel_window().get_icon
        for x in group.columns:
            column = QtWidgets.QTreeWidgetItem()
            name = get_toplevel_window().Session.translate_header(x)
            column.setText(0, name)
            column.setIcon(0, icon_getter("Columns"))
            self.addChild(column)

        if group.get_functions():
            for x in group.get_functions():
                func = QtWidgets.QTreeWidgetItem()
                name = get_toplevel_window().Session.translate_header(x._name)
                func.setText(0, name)
                func.setIcon(0, icon_getter("Percentage"))
                self.addChild(func)

        if group.filters:
            filters = QtWidgets.QTreeWidgetItem()
            filters.setText(0, "Filters")
            for x in group.filters:
                filt = QtWidgets.QTreeWidgetItem()
                filt.setText(0, format_filter(x))
                filters.addChild(filt)
            self.addChild(filters)

        if group.show_distinct:
            distinct = QtWidgets.QTreeWidgetItem()
            distinct.setText(0, "Remove duplicates")
            distinct.setToolTip(0, distinct.text(0))
            distinct.setIcon(0, icon_getter("Cancel"))
            self.addChild(distinct)
        else:
            distinct = QtWidgets.QTreeWidgetItem()
            distinct.setText(0, "Keep duplicates")
            distinct.setToolTip(0, distinct.text(0))
            distinct.setIcon(0, icon_getter("Ok"))
            self.addChild(distinct)

    def change_group(self, group):
        self.setText(0, group.name)
        self.group = group
        self.add_group_info(group)


class CoqGroupTree(QtWidgets.QWidget):
    groupAdded = pyqtSignal(object)
    groupRemoved = pyqtSignal(object)
    groupModified = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        CoqGroupTree.group_label = "{} {{}}".format(
            QtWidgets.QApplication.instance().translate(
                "Main:GroupTree", "Group", ""))

        super(CoqGroupTree, self).__init__(*args, **kwargs)
        self.ui = Ui_GroupWidget()
        self.ui.setupUi(self)

        icon_getter = get_toplevel_window().get_icon
        self.ui.button_group_up.setIcon(icon_getter("Circled Chevron Up"))
        self.ui.button_group_down.setIcon(icon_getter("Circled Chevron Down"))
        self.ui.button_add_group.setIcon(icon_getter("Plus"))
        self.ui.button_remove_group.setIcon(icon_getter("Minus"))
        self.ui.button_edit_group.setIcon(icon_getter("Edit"))

        self.setup_hooks()
        self.check_buttons()
        self._item_number = 0
        self.selected_columns = []

    def selectionChanged(self, new_selection, old_selection):
        """
        This slot can be used to inform the group tree about changes in the
        currently selected columns. This information will be used to set the
        default grouping columns.

        To use it, connect this slot to the selectionChanged signal of the
        table that displays the data.
        """
        self.selected_columns = new_selection

    def add_groups(self, group_list):
        for group in group_list:
            new_item = CoqGroupTreeItem(group)
            self.ui.tree_groups.addTopLevelItem(new_item)

    def clear(self):
        self.ui.tree_groups.clear()

    def groups(self):
        groups = []
        for i in range(self.ui.tree_groups.topLevelItemCount()):
            item = self.ui.tree_groups.topLevelItem(i)
            groups.append(item.group)
        return groups

    def setup_hooks(self):
        self.ui.button_add_group.clicked.connect(self._add_group)
        self.ui.button_remove_group.clicked.connect(self._remove_group)
        self.ui.button_edit_group.clicked.connect(self._edit_group)
        self.ui.tree_groups.itemSelectionChanged.connect(self.check_buttons)
        self.ui.button_group_up.clicked.connect(self.selected_up)
        self.ui.button_group_down.clicked.connect(self.selected_down)

    def selected_up(self):
        self.move_selected(up=True)

    def selected_down(self):
        self.move_selected(up=False)

    def move_selected(self, up):
        indexes = self.ui.tree_groups.selectedIndexes()
        items = self.ui.tree_groups.selectedItems()

        if not items:
            return

        pos_first = indexes[0].row()

        if up:
            new_pos = pos_first - 1
        else:
            new_pos = pos_first + 1

        items = [self.ui.tree_groups.takeTopLevelItem(pos_first)
                 for _ in items]

        self.ui.tree_groups.insertTopLevelItems(new_pos, items)
        for x in items:
            x.setSelected(True)
            self.ui.tree_groups.setCurrentItem(x)
        self.groupModified.emit(x)
        self.check_buttons()

    def get_current_item(self):
        item = self.ui.tree_groups.currentItem()
        while (item is not None and
               not isinstance(item, CoqGroupTreeItem)):
            item = item.parent()
        return item

    def check_buttons(self):
        selected = self.ui.tree_groups.selectedItems()
        selected_count = self.ui.tree_groups.topLevelItemCount()

        self.ui.button_group_up.setDisabled(True)
        self.ui.button_group_down.setDisabled(True)

        # FIXME: replace the exceptions by proper code - the use pattern here
        # takes EAFP far too literally!
        try:
            group_item = self.ui.tree_groups.currentItem().parent()
            selected_row = self.ui.tree_groups.indexFromItem(group_item).row()
            if selected_row > 0:
                self.ui.button_group_up.setEnabled(True)
            if selected_row + 1 < selected_count:
                self.ui.button_group_down.setEnabled(True)
        except (IndexError, AttributeError):
            pass

        try:
            get_toplevel_window().table_model.content
        except AttributeError:
            self.ui.button_add_group.setDisabled(True)
            self.ui.button_edit_group.setDisabled(True)
            self.ui.button_remove_group.setEnabled(bool(selected))
            return
        else:
            self.ui.button_add_group.setEnabled(True)
        self.ui.button_edit_group.setEnabled(bool(selected))
        self.ui.button_remove_group.setEnabled(bool(selected))

    def _add_group(self):
        try:
            vis_cols = get_toplevel_window().table_model.content.columns
            hidden_cols = get_toplevel_window().hidden_model.content.columns
            available_columns = list(vis_cols) + list(hidden_cols)
        except AttributeError:
            available_columns = []

        columns = self.selected_columns or []

        self._item_number += 1
        name = self.group_label.format(self._item_number)
        group = Group(name, list(columns))
        result = GroupDialog.edit(group, available_columns,
                                  parent=get_toplevel_window())
        if result:
            item = CoqGroupTreeItem(result)
            self.ui.tree_groups.addTopLevelItem(item)
            self.groupAdded.emit(item.group)
        else:
            self._item_number -= 1
        self.check_buttons()

    def _remove_group(self):
        index = self.ui.tree_groups.currentIndex()
        item = self.ui.tree_groups.takeTopLevelItem(index.row())
        group = item.group
        self.groupRemoved.emit(group)
        self.check_buttons()

    def _edit_group(self):
        try:
            vis_cols = get_toplevel_window().table_model.content.columns
            hidden_cols = get_toplevel_window().hidden_model.content.columns
            all_columns = list(vis_cols) + list(hidden_cols)
        except AttributeError:
            all_columns = []

        item = self.get_current_item()
        group = item.group
        result = GroupDialog.edit(group, all_columns,
                                  parent=get_toplevel_window())
        if result:
            item.change_group(result)
            self.groupModified.emit(result)

    def headerItem(self, *args, **kwargs):
        return self.ui.tree_groups.headerItem(*args, **kwargs)

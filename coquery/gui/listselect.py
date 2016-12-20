# -*- coding: utf-8 -*-
"""
listselect.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery.unicode import utf8

from .pyqt_compat import QtCore, QtGui, get_toplevel_window
from . import classes


class CoqListSelect(QtGui.QWidget):
    """
    A QWidget that presents two exclusive list (a list of available and a
    list of selected items), with controls to move between the two.
    """
    itemSelectionChanged = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        from .ui import coqListSelectUi
        super(CoqListSelect, self).__init__(*args, **kwargs)
        self.ui = coqListSelectUi.Ui_CoqListSelect()
        self.ui.setupUi(self)

        self.ui.button_add.clicked.connect(self.add_selected)
        self.ui.button_remove.clicked.connect(self.remove_selected)
        self.ui.button_up.clicked.connect(self.selected_up)
        self.ui.button_down.clicked.connect(self.selected_down)

        self.ui.button_up.setIcon(get_toplevel_window().get_icon("Circled Chevron Up"))
        self.ui.button_down.setIcon(get_toplevel_window().get_icon("Circled Chevron Down"))
        self.ui.button_add.setIcon(get_toplevel_window().get_icon("Circled Chevron Left"))
        self.ui.button_remove.setIcon(get_toplevel_window().get_icon("Circled Chevron Right"))

        self.ui.list_selected.itemSelectionChanged.connect(self.check_buttons)
        self.ui.list_available.itemSelectionChanged.connect(self.check_buttons)
        self._minimum = 0
        self._moveAvailable = True

    @staticmethod
    def _fill_list_widget(w, l, translate):
        for x in l:
            if not isinstance(x, QtGui.QListWidgetItem):
                item = QtGui.QListWidgetItem(translate(x))
                item.setData(QtCore.Qt.UserRole, x)
            else:
                item = translate(x)
            w.addItem(item)

    def setMoveAvailable(self, b):
        if b:
            self.ui.button_up.show()
            self.ui.button_down.show()
        else:
            self.ui.button_up.hide()
            self.ui.button_down.hide()
        self._moveAvailable = b

    def _moveAvailable(self):
        return self._moveAvailable

    def minimumItems(self):
        return self._minimum

    def setMinimumItems(self, i):
        self._minimum = i

    def count(self):
        return self.ui.list_selected.count()

    def selectedItems(self):
        return [self.ui.list_selected.item(i) for i
                in range(self.ui.list_selected.count())]

    def setAvailableList(self, l, translate=lambda x: x):
        self._fill_list_widget(self.ui.list_available, l, translate)

    def setSelectedList(self, l, translate=lambda x: x):
        self._fill_list_widget(self.ui.list_selected, l, translate)
        self.ui.list_selected.setCurrentItem(
            self.ui.list_selected.item(0))

    def add_selected(self):
        for x in self.ui.list_available.selectedItems():
            row = self.ui.list_available.row(x)
            item = self.ui.list_available.takeItem(row)
            self.ui.list_selected.addItem(item)
            self.ui.list_selected.setCurrentItem(item)
            self.itemSelectionChanged.emit()

    def remove_selected(self):
        for x in self.ui.list_selected.selectedItems():
            if self.ui.list_selected.count() > self.minimumItems():
                row = self.ui.list_selected.row(x)
                item = self.ui.list_selected.takeItem(row)
                self.ui.list_available.addItem(item)
                self.ui.list_available.setCurrentItem(item)
                self.itemSelectionChanged.emit()

    def selected_up(self):
        self.move_selected(up=True)

    def selected_down(self):
        self.move_selected(up=False)

    def move_selected(self, up):
        pos_first = min([self.ui.list_selected.row(x) for x
                         in self.ui.list_selected.selectedItems()])
        if up:
            new_pos = pos_first - 1
        else:
            new_pos = pos_first + 1
        selected = [self.ui.list_selected.takeItem(pos_first) for _
                    in self.ui.list_selected.selectedItems()]
        for x in selected:
            self.ui.list_selected.insertItem(new_pos, x)
            x.setSelected(True)
            self.ui.list_selected.setCurrentItem(x)
        self.check_buttons()

    def check_buttons(self):
        selected_row = self.ui.list_selected.currentRow()
        selected_count = self.ui.list_selected.count()
        available_count = self.ui.list_available.count()

        self.ui.button_up.setEnabled(selected_row > 0)
        self.ui.button_down.setEnabled(selected_row + 1 < selected_count)
        self.ui.button_remove.setEnabled(selected_count > self.minimumItems())
        self.ui.button_add.setEnabled(available_count > 0)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.add_selected()
        elif event.key() == QtCore.Qt.Key_Right:
            self.remove_selected()
        elif (self.ui.list_selected.hasFocus() and
              event.key() == QtCore.Qt.Key_Up and
              event.modifiers() == QtCore.Qt.ShiftModifier):
            self.selected_up()
        elif (self.ui.list_selected.hasFocus() and
              event.key() == QtCore.Qt.Key_Down and
              event.modifiers() == QtCore.Qt.ShiftModifier):
            self.selected_down()
        else:
            super(CoqListSelect, self).keyPressEvent(event)


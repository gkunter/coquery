# -*- coding: utf-8 -*-
"""
listselect.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery.unicode import utf8

from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window


class CoqListSelect(QtWidgets.QWidget):
    """
    A QWidget that presents two exclusive list (a list of available and a
    list of selected items), with controls to move between the two.
    """
    itemSelectionChanged = QtCore.Signal()
    currentItemChanged = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        from .ui import coqListSelectUi
        super(CoqListSelect, self).__init__(*args, **kwargs)
        self.ui = coqListSelectUi.Ui_CoqListSelect()
        self.ui.setupUi(self)
        self.setDefocus(True)

        self.ui.button_add.clicked.connect(self.add_selected)
        self.ui.button_remove.clicked.connect(self.remove_selected)
        self.ui.button_up.clicked.connect(self.selected_up)
        self.ui.button_down.clicked.connect(self.selected_down)

        icon_getter = get_toplevel_window().get_icon
        self.ui.button_up.setIcon(icon_getter("Circled Chevron Up"))
        self.ui.button_down.setIcon(icon_getter("Circled Chevron Down"))
        self.ui.button_add.setIcon(icon_getter("Circled Chevron Left"))
        self.ui.button_remove.setIcon(icon_getter("Circled Chevron Right"))

        self.ui.list_selected.itemSelectionChanged.connect(self.check_buttons)
        self.ui.list_selected.itemSelectionChanged.connect(
            lambda: self.currentItemChanged.emit(self.currentItem()))
        self.ui.list_available.itemSelectionChanged.connect(self.check_buttons)
        #self.ui.list_available.itemSelectionChanged.connect(
            #lambda: self.currentItemChanged.emit(self.currentItem()))

        self._minimum = 0
        self._move_available = True
        self._track_selected = False
        self._last_selected_row = None
        self._last_available_row = None

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.ui.list_selected.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ui.list_available.setFocusPolicy(QtCore.Qt.NoFocus)

    @staticmethod
    def _fill_list_widget(w, l, translate, *args, **kwargs):
        for x in l:
            if translate is not None:
                if not isinstance(x, QtWidgets.QListWidgetItem):
                    item = QtWidgets.QListWidgetItem(
                                translate(x, *args, **kwargs))
                    item.setData(QtCore.Qt.UserRole, x)
                else:
                    item = translate(x, *args, **kwargs)
            else:
                if not isinstance(x, QtWidgets.QListWidgetItem):
                    item = QtWidgets.QListWidgetItem(x)
                else:
                    item = x
            w.addItem(item)

    def setDefocus(self, b):
        self._defocus = b

    def defocus(self):
        return self._defocus

    def setMoveAvailable(self, b):
        if b:
            self.ui.button_up.show()
            self.ui.button_down.show()
        else:
            self.ui.button_up.hide()
            self.ui.button_down.hide()
        self._move_available = b

    def moveAvailable(self):
        return self._move_available

    def trackSelected(self):
        return self._track_selected

    def setTrackSelected(self, b):
        self._track_selected = b

    def setSelectedLabel(self, s):
        self.ui.label_select_list.setText(s)

    def selectedLabel(self):
        return self.ui.label_select_list.text()

    def setAvailableLabel(self, s):
        self.ui.label_available.setText(s)

    def availableLabel(self):
        return self.ui.label_available.text()

    def minimumItems(self):
        return self._minimum

    def setMinimumItems(self, i):
        self._minimum = i

    def count(self):
        return self.ui.list_selected.count()

    def selectedItems(self):
        return [self.ui.list_selected.item(i) for i
                in range(self.ui.list_selected.count())]

    def setAvailableList(self, l, translate=None, *args, **kwargs):
        self._fill_list_widget(self.ui.list_available, l,
                               translate, *args, **kwargs)

    def setSelectedList(self, l, translate=None, *args, **kwargs):
        self._fill_list_widget(self.ui.list_selected, l,
                               translate, *args, **kwargs)

    def add_selected(self):
        for x in self.ui.list_available.selectedItems():
            row = self.ui.list_available.row(x)
            item = self.ui.list_available.takeItem(row)
            self.ui.list_selected.addItem(item)
            self.ui.list_selected.setCurrentItem(item)
            self.itemSelectionChanged.emit()
        if self.trackSelected():
            self.ui.list_selected.setFocus()
            self.ui.list_available.setCurrentItem(None)

    def remove_selected(self):
        for x in self.ui.list_selected.selectedItems():
            if self.ui.list_selected.count() > self.minimumItems():
                row = self.ui.list_selected.row(x)
                item = self.ui.list_selected.takeItem(row)
                self.ui.list_available.addItem(item)
                self.ui.list_available.setCurrentItem(item)
                self.itemSelectionChanged.emit()
        if self.trackSelected():
            self.ui.list_available.setFocus()
            self.ui.list_selected.setCurrentItem(None)

    def currentItem(self):
        if self.ui.list_selected.selectedItems():
            return self.ui.list_selected.selectedItems()[0]
        if self.ui.list_available.selectedItems():
            return self.ui.list_available.selectedItems()[0]
        else:
            return None

    def setCurrentItem(self, x):
        """
        Set the current item to the item that has 'x' as its data.
        """
        # look in left list:
        for i in range(self.ui.list_selected.count()):
            item = self.ui.list_selected.item(i)
            if utf8(item.data(QtCore.Qt.UserRole)) == x:
                _last_selected_row = item
                self.ui.list_selected.setCurrentItem(item)
                return

        # look in right list:
        for i in range(self.ui.list_available.count()):
            item = self.ui.list_available.item(i)
            if utf8(item.data(QtCore.Qt.UserRole)) == x:
                _last_available_row = item
                self.ui.list_available.setCurrentItem(item)
                return

    def selection_down(self):
        current_row = self.ui.list_selected.currentRow()
        if current_row < self.ui.list_selected.count() - 1:
            self.ui.list_selected.setCurrentItem(
                self.ui.list_selected.item(current_row + 1))

    def selection_up(self):
        current_row = self.ui.list_selected.currentRow()
        if current_row > 0:
            self.ui.list_selected.setCurrentItem(
                self.ui.list_selected.item(current_row - 1))

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
        self.ui.button_remove.setEnabled(
            selected_count > self.minimumItems() and selected_row > -1)
        self.ui.button_add.setEnabled(
            available_count > 0 and self.ui.list_available.currentRow() > -1)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.add_selected()
        elif event.key() == QtCore.Qt.Key_Right:
            self.remove_selected()
        elif event.key() == QtCore.Qt.Key_Up:
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                self.selected_up()
            else:
                self.selection_up()
        elif event.key() == QtCore.Qt.Key_Down:
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                self.selected_down()
            else:
                self.selection_down()
        else:
            super(CoqListSelect, self).keyPressEvent(event)

    def event(self, ev):
        if ev.type() == ev.FocusIn:
            if self.defocus():
                # restore selection bars if focus is regained:
                self.blockSignals(False)

                if self._last_selected_row is None:
                    if self.ui.list_selected.count() > 0:
                        self.ui.list_selected.setCurrentItem(
                            self.ui.list_selected.item(0))
                else:
                    self.ui.list_selected.setCurrentItem(
                        self._last_selected_row)

                if self._last_available_row is None:
                    if self.ui.list_available.count() > 0:
                        self.ui.list_available.setCurrentItem(
                            self.ui.list_available.item(0))
                else:
                    self.ui.list_available.setCurrentItem(
                        self._last_available_row)
        elif ev.type() == ev.FocusOut:
            if self.defocus():
                self.blockSignals(True)
                self._last_selected_row = self.ui.list_selected.currentItem()
                self._last_available_row = self.ui.list_available.currentItem()
                self.ui.list_selected.setCurrentItem(None)
                self.ui.list_available.setCurrentItem(None)

        return super(CoqListSelect, self).event(ev)


class SelectionDialog(QtWidgets.QDialog):
    def __init__(self, title, selected, available, text="", translator=None,
                 *args, **kwargs):
        super(SelectionDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(title)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.list_select = CoqListSelect()
        self.list_select.setAvailableList(available, translator)
        self.list_select.setSelectedList(selected, translator)
        self.main_layout.addWidget(self.list_select)
        self.resize(500, 310)

    def exec_(self):
        super(SelectionDialog, self).exec_()

    @staticmethod
    def show(*args, **kwargs):
        dialog = SelectionDialog(*args, **kwargs)
        dialog.exec_()
        return [x.data(QtCore.Qt.UserRole)
                for x in dialog.list_select.selectedItems()]

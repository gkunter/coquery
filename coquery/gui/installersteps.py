# -*- coding: utf-8 -*-
"""
installersteps.py is part of Coquery.

Copyright (c) 2026 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5 import QtCore, QtWidgets

from coquery.corpusbuilder import InstallerSteps
from coquery.gui import errorbox
from coquery.gui.pyqt_compat import get_toplevel_window
from coquery.gui.ui.installerStepsUi import Ui_InstallerStepSelection

translate = QtWidgets.QApplication.instance().translate


class SelectInstallerSteps(QtWidgets.QDialog):
    def __init__(self, default=None, db_name=None, uniques=True,
                 parent=None):
        super().__init__(parent)

        if not default:
            self.selected = set()
            for key in InstallerSteps:
                self.selected.add(key)
        else:
            self.selected = default

        self.ui = Ui_InstallerStepSelection()
        self.ui.setupUi(self)

        for key in InstallerSteps:
            if hasattr(self.ui, key.value):
                checkbox = getattr(self.ui, key.value)
                checkbox.setChecked(key in self.selected)
                checkbox.toggled.connect(
                    lambda state, name=key.value: self.toggle_step(name, state))

    def toggle_step(self, checkbox_name, state):
        this_step = None
        for key in InstallerSteps:
            if key.value == checkbox_name:
                this_step = key
                break

        if state:
            self.selected.add(this_step)
        else:
            self.selected.remove(this_step)

    def accept(self, *args):
        self.selected = set()
        for key in InstallerSteps:
            checkbox = getattr(self.ui, key.value, None)
            if checkbox and checkbox.isChecked():
                self.selected.add(key)
        super().accept(*args)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def onException(self):
        errorbox.ErrorBox.show(self.exc_info, self.exception)

    def get_uniques(self):
        self.ui.progress_bar.setRange(0, 0)
        self.ui.tableWidget.hide()
        self.ui.button_details.hide()
        self.ui.label.hide()

        self.thread = CoqThread(
            self.get_unique,
            self,
            self.ui.checkbox_frequency.isChecked())
        self.thread.taskFinished.connect(self.finalize)
        self.thread.taskException.connect(self.onException)
        self.thread.start()

    @staticmethod
    def show(rc_feature, resource, uniques=True, parent=None):
        dialog = UniqueViewer(rc_feature, resource,
                              uniques=uniques, parent=parent)

        dialog.setVisible(True)
        dialog.get_uniques()
        get_toplevel_window().widget_list.append(dialog)

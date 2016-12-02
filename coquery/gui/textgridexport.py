# -*- coding: utf-8 -*-
"""
textgridexport.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import os

from coquery import options
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtGui
from .classes import CoqListItem
from .ui.textgridExportUi import Ui_TextgridExport

class TextgridExportDialog(QtGui.QDialog):
    def __init__(self, columns, parent=None):
        super(TextgridExportDialog, self).__init__(parent)
        self.ui = Ui_TextgridExport()
        self.ui.setupUi(self)
        session = options.cfg.main_window.Session
        for col in [x for x in columns if "_endtime_" not in x and
                                          "_starttime_" not in x]:
            item = CoqListItem(session.translate_header(col))
            item.setData(QtCore.Qt.UserRole, col)
            item.setCheckState(QtCore.Qt.Checked)
            self.ui.list_columns.addItem(item)
        self.restore_settings()
        self.ui.button_output_path.clicked.connect(self.set_output_path)
        self.ui.button_sound_path.clicked.connect(self.set_sound_path)
        self.ui.edit_output_path.textChanged.connect(self.check_gui)
        self.ui.edit_sound_path.textChanged.connect(self.check_gui)
        self.ui.list_columns.itemClicked.connect(self.check_gui)
        self.ui.button_output_path.setIcon(parent.get_icon("folder"))
        self.ui.button_sound_path.setIcon(parent.get_icon("folder"))

    def restore_settings(self):
        try:
            self.resize(options.settings.value("textgridexport_size"))
        except TypeError:
            pass
        val = options.settings.value("textgridexport_radio_one_per_match", None)
        self.ui.radio_one_per_match.setChecked(val == None or val == "true" or val == True)
        self.ui.radio_one_per_file.setChecked(not (val == None or val == "true" or val == True))

        val = options.settings.value("textgridexport_check_extract_sound", False)
        if val == "true" or val == True:
            self.ui.check_copy_sounds.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.check_copy_sounds.setCheckState(QtCore.Qt.Unchecked)
        val = options.settings.value("textgridexport_check_remember", False)
        if val == "true" or val == True:
            self.ui.check_remember.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.check_remember.setCheckState(QtCore.Qt.Unchecked)
        self.ui.edit_output_path.setText(options.settings.value("textgridexport_output_path",
                                                                os.path.expanduser("~")))
        self.ui.edit_sound_path.setText(options.settings.value("textgridexport_sound_path", ""))
        self.ui.spin_left_padding.setValue(float(options.settings.value("textgridexport_left_padding", 0)))
        self.ui.spin_right_padding.setValue(float(options.settings.value("textgridexport_right_padding", 0)))

    def check_gui(self, *args, **kwargs):
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        if not os.path.exists(utf8(self.ui.edit_output_path.text())):
            S = "QLineEdit { background-color: rgb(255, 255, 192) }"
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
        else:
            S = "QLineEdit {{ background-color: {} }} ".format(options.cfg.app.palette().color(QtGui.QPalette.Base).name())
        self.ui.edit_output_path.setStyleSheet(S)
        if self.ui.check_copy_sounds.isChecked():
            if not os.path.exists(utf8(self.ui.edit_sound_path.text())):
                S = "QLineEdit { background-color: rgb(255, 255, 192) }"
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
            else:
                S = "QLineEdit {{ background-color: {} }} ".format(options.cfg.app.palette().color(QtGui.QPalette.Base).name())
            self.ui.edit_sound_path.setStyleSheet(S)

        checked = [x for x in range(self.ui.list_columns.count()) if self.ui.list_columns.item(x).checkState()]
        if not checked:
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)

    def set_output_path(self):
        name = self.select_file(self.ui.edit_output_path.text())
        if name:
            self.ui.edit_output_path.setText(name)

    def set_sound_path(self):
        name = self.select_file(self.ui.edit_sound_path.text())
        if name:
            self.ui.edit_sound_path.setText(name)

    def select_file(self, path=""):
        """ Call a file selector, and add file name to query file input. """
        name = QtGui.QFileDialog.getExistingDirectory(directory=path, options=QtGui.QFileDialog.ReadOnly|QtGui.QFileDialog.ShowDirsOnly|QtGui.QFileDialog.HideNameFilterDetails)
        # getOpenFileName() returns different types in PyQt and PySide, fix:
        if type(name) == tuple:
            name = name[0]
        return utf8(name)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def accept(self, *args):
        super(TextgridExportDialog, self).accept(*args)
        options.settings.setValue("textgridexport_size", self.size())
        options.settings.setValue("textgridexport_radio_one_per_match", self.ui.radio_one_per_match.isChecked())
        options.settings.setValue("textgridexport_check_extract_sound", bool(self.ui.check_copy_sounds.checkState()))
        options.settings.setValue("textgridexport_sound_path", utf8(self.ui.edit_sound_path.text()))
        options.settings.setValue("textgridexport_output_path", utf8(self.ui.edit_output_path.text()))
        options.settings.setValue("textgridexport_left_padding", float(self.ui.spin_left_padding.value()))
        options.settings.setValue("textgridexport_right_padding", float(self.ui.spin_right_padding.value()))
        options.settings.setValue("textgridexport_check_remember", bool(self.ui.check_remember.checkState()))

    def exec_(self):
        result = super(TextgridExportDialog, self).exec_()
        if result == QtGui.QDialog.Accepted:
            columns = []
            for col in range(self.ui.list_columns.count()):
                if self.ui.list_columns.item(col).checkState() == QtCore.Qt.Checked:
                    columns.append(utf8(self.ui.list_columns.item(col).data(QtCore.Qt.UserRole)))
            return {"output_path": utf8(self.ui.edit_output_path.text()),
                    "columns": columns,
                    "one_grid_per_match": self.ui.radio_one_per_match.isChecked(),
                    "remember_time": self.ui.check_remember.checkState() != QtCore.Qt.Unchecked,
                    "sound_path": ("" if self.ui.check_copy_sounds.checkState() == QtCore.Qt.Unchecked else
                                   utf8(self.ui.edit_sound_path.text())),
                    "left_padding": float(self.ui.spin_left_padding.value()),
                    "right_padding": float(self.ui.spin_right_padding.value())}
        else:
            return None

    @staticmethod
    def manage(*args, **kwargs):
        dialog = TextgridExportDialog(*args, **kwargs)
        dialog.setVisible(True)

        return dialog.exec_()

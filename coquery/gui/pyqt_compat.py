# -*- coding: utf-8 -*-
"""
pyqt_compat.py is part of Coquery.

Copyright (c) 2016-2021 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import sys
import warnings

from PyQt5 import QtCore, QtGui, QtWidgets

QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot
QtCore.Property = QtCore.pyqtProperty
QtCore.QString = str

pyside = False
pyqt = False


class CoqSettings(QtCore.QSettings):
    def value(self, key, default=None, **kwargs):
        try:
            val = super(CoqSettings, self).value(key, default)
        except Exception as e:
            s = "Exception when requesting setting key '{}': {}".format(
                key, e)
            print(s)
            warnings.warn(s)
            val = default
        return val


if sys.platform == 'win32':
    frameShadow = QtWidgets.QFrame.Raised
    frameShape = QtWidgets.QFrame.Panel
else:
    frameShadow = QtWidgets.QFrame.Raised
    frameShape = QtWidgets.QFrame.StyledPanel


def tr(*args, **kwargs):
    return QtWidgets.QApplication.instance().translate(*args, **kwargs)


def get_toplevel_window():
    """
    Retrieves the top-level widget with the given name. By default, retrieve
    the main window.
    """
    for widget in QtWidgets.qApp.topLevelWidgets():
        if widget.objectName() == "MainWindow":
            return widget
    return None


def close_toplevel_widgets():
    """
    Closes all top-level widgets.
    """
    for widget in QtWidgets.qApp.topLevelWidgets():
        if widget.objectName() != "MainWindow":
            widget.hide()
            widget.close()
            del widget


STYLE_WARN = 'QLineEdit {background-color: lightyellow; }'

COLOR_NAMES = {QtGui.QColor(name).name().lower(): name for name
               in QtGui.QColor.colorNames()}

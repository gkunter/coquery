# -*- coding: utf-8 -*-
"""
pyqt_compat.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import sys

from PyQt5 import QtCore, QtGui, QtWidgets


class CoqSettings(QtCore.QSettings):
    def value(self, key, default=None, *args, **kwargs):
        try:
            val = super().value(key, default, *args, **kwargs)
        except Exception as e:
            s = "Exception when requesting setting key '{}': {}".format(
                key, e)
            print(s)
            logging.warning(s)
            val = default
        return val


if sys.platform == 'win32':
    frameShadow = QtWidgets.QFrame.Raised
    frameShape = QtWidgets.QFrame.Panel
else:
    frameShadow = QtWidgets.QFrame.Raised
    frameShape = QtWidgets.QFrame.StyledPanel


def tr(*args, **kwargs):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app.translate(*args, **kwargs)


def get_toplevel_window(name="MainWindow"):
    """
    Retrieves the top-level widget with the given name. By default, retrieve
    the main window.
    """
    for widget in QtWidgets.qApp.topLevelWidgets():
        if widget.objectName() == name:
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


def clear_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                clear_layout(item.layout())
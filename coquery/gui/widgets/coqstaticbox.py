# -*- coding: utf-8 -*-
"""
coqstaticbox.py is part of Coquery.

Copyright (c) 2018-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5 import QtWidgets, QtCore

from coquery.gui.pyqt_compat import get_toplevel_window


class CoqStaticBox(QtWidgets.QDialog):
    def __init__(self, title, content, *args, **kwargs):
        super(CoqStaticBox, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(title)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel(content)
        self.layout.addWidget(self.label)
        self.setModal(True)
        self.open()
        self.show()
        self.adjustSize()
        self.update()
        self.repaint()
        get_toplevel_window().repaint()
        QtWidgets.QApplication.sendPostedEvents()
        QtWidgets.QApplication.processEvents()
        self.update()
        self.repaint()
        get_toplevel_window().repaint()

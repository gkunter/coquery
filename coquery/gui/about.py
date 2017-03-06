# -*- coding: utf-8 -*-
"""
about.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery import __version__, DATE
from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtWidgets, QtGui, get_toplevel_window
from .ui.aboutUi import Ui_AboutDialog


class AboutDialog(QtWidgets.QDialog):
    """
    Display the About dialog.
    """
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

        main_window = get_toplevel_window()
        icon = (main_window.get_icon("title.png", small_n_flat=False)
                           .pixmap(self.size()))
        image = QtGui.QImage(icon.toImage())
        painter = QtGui.QPainter(image)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(image.rect(),
                         QtCore.Qt.AlignBottom,
                         "Version {}".format(__version__))
        painter.end()
        self.ui.label_pixmap.setPixmap(QtGui.QPixmap.fromImage(image))
        self.ui.label_pixmap.setAlignment(QtCore.Qt.AlignCenter)

        txt = utf8(self.ui.label_description.text())
        self.ui.label_description.setText(txt.format(version=__version__,
                                                     date=DATE))

    @staticmethod
    def view(parent=None):
        dialog = AboutDialog(parent=parent)
        dialog.exec_()

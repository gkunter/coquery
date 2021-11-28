# -*- coding: utf-8 -*-
"""
coqstaticbox.py is part of Coquery.

Copyright (c) 2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from coquery.gui.pyqt_compat import QtCore, QtGui, QtWidgets


class CoqWidgetFader(QtCore.QObject):
    def __init__(self, widget, duration=250):
        def blend(left, right, i, steps):
            x = (steps - i - 1) / steps * left
            y = i / steps * right
            return int(x + y)

        self._widget = widget

        app = QtWidgets.QApplication.instance()
        start = app.palette().color(QtGui.QPalette.Normal,
                                    QtGui.QPalette.Highlight)
        end = widget.palette().color(widget.backgroundRole())
        self._pal = []

        steps = 128

        for i in range(steps):
            blended = (blend(start.red(), end.red(), i, steps),
                       blend(start.green(), end.green(), i, steps),
                       blend(start.blue(), end.blue(), i, steps))
            self._pal.append("#{:02x}{:02x}{:02x}".format(*blended))

        self._delay = duration / steps

    def fade(self):
        self.fade_widget(0)

    def fade_widget(self, step):
        s = "background-color: '{}'".format(self._pal[step])
        self._widget.setStyleSheet(s)
        if step < len(self._pal) - 1:
            QtCore.QTimer.singleShot(self._delay,
                                     lambda: self.fade_widget(step + 1))
        else:
            self._widget.setStyleSheet("")

# -*- coding: utf-8 -*-
"""
cite.py is part of Coquery.

Copyright (c) 2017-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5 import QtCore, QtWidgets

from coquery import __version__, DATE
from coquery.gui.ui.citeUi import Ui_CiteDialog
from coquery.gui.widgets.coqwidgetfader import CoqWidgetFader


class CiteDialog(QtWidgets.QDialog):
    """
    Display the How to Cite dialog.
    """
    def __init__(self, parent=None):
        super(CiteDialog, self).__init__(parent)
        self.ui = Ui_CiteDialog()
        self.ui.setupUi(self)
        self._widget = None
        self.mime = None

        year = DATE.split(",")[-1].strip()

        for widget in (self.ui.edit_unified,
                       self.ui.edit_mla,
                       self.ui.edit_apa,
                       self.ui.edit_bibtex,
                       self.ui.edit_ris,
                       self.ui.edit_endnote):
            if hasattr(widget, "toHtml"):
                html = (widget.toHtml()
                              .replace("{date}", year)
                              .replace("{version}", __version__))
                widget.setHtml(html)
            else:
                text = (widget.toPlainText()
                              .replace("{date}", year)
                              .replace("{version}", __version__))
                widget.setPlainText(text)
            widget.installEventFilter(self)

        self.last_select = None
        self.ui.button_copy.clicked.connect(self.copy_to_clipboard)

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.FocusIn:
            # select text in new widget
            self.last_select = widget
            widget.selectAll()
            widget.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            selected = bytes(widget.toPlainText() + "\n", "utf-8")
            self.mime = QtCore.QMimeData()
            self.mime.setData("text/plain", selected)
            self._widget = widget
            if hasattr(widget, "toHtml"):
                selected = bytes(widget.toHtml(), "utf-8")
                self.mime.setData("text/html", selected)

        elif event.type() == QtCore.QEvent.FocusOut:
            cursor = widget.textCursor()
            cursor.clearSelection()
            widget.setTextCursor(cursor)
            widget.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

        val = super(CiteDialog, self).eventFilter(widget, event)
        return val

    def copy_to_clipboard(self):
        cb = QtWidgets.QApplication.clipboard()
        try:
            cb.setMimeData(self.mime, cb.Clipboard)
            CoqWidgetFader(self._widget).fade()
        except RuntimeError:
            pass

    @staticmethod
    def view(parent=None):
        dialog = CiteDialog(parent=parent)
        dialog.exec_()

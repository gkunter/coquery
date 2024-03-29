# -*- coding: utf-8 -*-
"""
errorbox.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import traceback
from PyQt5 import QtCore, QtWidgets, QtGui

from coquery import options
from coquery.defines import MODULE_INFORMATION, msg_missing_module
from coquery.errors import get_error_repr
from coquery.gui.ui.errorUi import Ui_ErrorDialog


class ErrorBox(QtWidgets.QDialog):
    def __init__(self, exc_info, exception, no_trace=False,
                 message="", parent=None):

        super(ErrorBox, self).__init__(parent)

        self.ui = Ui_ErrorDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(options.cfg.icon)
        self.ui.icon_label.setPixmap(
            QtGui.QIcon.fromTheme("dialog-error").pixmap(32, 32))

        tup = get_error_repr(exc_info)
        exc_type, exc_message, exc_trace, exc_location = tup
        exc_type = type(exception).__name__

        if message:
            exc_message = "<p>{}</p><p>{}</p>".format(exc_message, message)
        if not no_trace:
            trace = exc_trace.replace("\n", "<br>").replace(" ", "&nbsp;")
            error = ("<table><tr><td>Type</td><td><b>{}</b></td></tr>"
                     "<tr><td>Message</td><td><b>{}</b></td></tr>"
                     "</table><p>{}</p>").format(
                         exc_type, exc_message, trace)
        else:
            error = ("<table><tr><td>Type</td><td><b>{}</b></td></tr>"
                     "<tr><td>Message</td><td><b>{}</b></td></tr>"
                     "<tr><td>Location</td><td><b>{}</b></td></tr>"
                     "</table>").format(exc_type, exc_message, exc_location)

        self.ui.trace_area.setText(error)

        try:
            self.resize(options.settings.value("errorbox_size"))
        except TypeError:
            pass

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()

    @staticmethod
    def show(*args, **kwargs):
        dialog = ErrorBox(*args, **kwargs)
        dialog.exec_()

    def closeEvent(self, *args):
        options.settings.setValue("errorbox_size", self.size())


def alert_missing_module(name, parent=None):
    _, _, func, url = MODULE_INFORMATION[name]
    QtWidgets.QMessageBox.critical(
        parent, "Missing Python module – Coquery",
        msg_missing_module.format(name=name, url=url, function=func))


class ExceptionBox(QtWidgets.QDialog):
    def __init__(self, cls, exception, tb, parent=None):
        def get_error_repr(trace):
            trace_strings = []
            indent = ""
            source_line = ""
            for tup in traceback.extract_tb(trace):
                file_name, line_no, func_name, text = tup
                if file_name.startswith(sys.path[0]):
                    s = "{}Function <code>{}()</code> in {}, line {}:"
                    trace_strings.append(
                        s.format(indent,
                                 func_name.replace("<", "&lt;"),
                                 file_name[len(sys.path[0])+1:],
                                 line_no))
                    source_line = text
                    indent += "&nbsp;&nbsp;"
            trace_strings.append(
                "<br>%s>&nbsp;<code>%s</code>" % (indent, source_line))
            return "<br>".join(trace_strings)

        super(ExceptionBox, self).__init__(parent)

        self.ui = Ui_ErrorDialog()
        self.ui.setupUi(self)
        self.ui.icon_label.setPixmap(
            QtGui.QIcon.fromTheme("dialog-error").pixmap(32, 32))

        error = ("<table><tr><td><b>{}&nbsp;</b></td><td>{}<br></td></tr>"
                 "<tr><td><b>Trace&nbsp;</b></td><td>{}</td></tr></table>"
                 .format(type(exception).__name__,
                         exception,
                         get_error_repr(tb)))
        self.ui.trace_area.setText(error)

        try:
            self.resize(options.settings.value("errorbox_size"))
        except TypeError:
            print("couldn't resize")
            pass

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()

    def exec_(self, *args, **kwargs):
        result = super(ExceptionBox, self).exec_(*args, **kwargs)
        options.settings.setValue("errorbox_size", self.size())
        return result


def catch_exceptions(cls, exception, tb):
    ExceptionBox(cls, exception, tb).exec_()


sys.excepthook = catch_exceptions

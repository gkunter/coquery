# -*- coding: utf-8 -*-
"""
sqlqueries.py is part of Coquery.

Copyright (c) 2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import warnings

from coquery import options
from coquery.gui.pyqt_compat import QtCore, QtWidgets, QtGui

try:
    import sqlparse
except ImportError:
    parsing_available = False
else:
    parsing_available = True

try:
    from pygments import highlight
    from pygments.lexers import SqlLexer
    from pygments.formatters import HtmlFormatter
except ImportError:
    warnings.warn("No syntax highlighting available")
    import re

    def highlight(text, *args, **kwargs):
        text = text.split("\n")
        lst = []
        for line in text:
            match = re.match("^(\s+)", line)
            if match:
                line = "{}{}".format(
                    "&nbsp;" * len(match.group(1)),
                    line.strip())
            lst.append(line)
        return "<br>".join(lst)

    class SqlLexer():
        pass

    class HtmlFormatter():
        def get_style_defs(self, s):
            return ""

_translate = QtCore.QCoreApplication.translate


class SQLViewer(QtWidgets.QDialog):
    @classmethod
    def lines_to_html(cls, lines):
        sql_queries = []
        for query_strings in lines:
            if parsing_available:
                lst = [sqlparse.format(s.strip(), reindent=True)
                       for s in query_strings]
            else:
                lst = query_strings
            sql_queries.append(";\n\n".join(lst))
        text = "\n\n-- next query --;\n\n".join(sql_queries)

        return highlight(text,
                         SqlLexer(),
                         HtmlFormatter(prestyles="font-family: monospace;"))

    def __init__(self, text=None, lines=None, parent=None):
        super(SQLViewer, self).__init__(parent)
        self.setObjectName("SQLViewerDialog")
        self.setWindowTitle(_translate("SQLViewerDialog",
                                       "SQL Viewer – Coquery"))

        self.document = QtGui.QTextDocument()
        self.document.setDefaultFont(QtGui.QFont("monospace"))
        self.document.setDefaultStyleSheet(HtmlFormatter().get_style_defs())

        self.viewer = QtWidgets.QTextEdit()
        self.viewer.setReadOnly(True)
        self.viewer.setDocument(self.document)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.viewer)

        self.document.setHtml(text or self.lines_to_html(lines))
        try:
            self.resize(options.settings.value("sqlviewer_size"))
        except TypeError:
            self.resize(640, 480)

    def closeEvent(self, event):
        options.settings.setValue("sqlviewer_size", self.size())

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()

    @staticmethod
    def view(lines, parent=None):
        dialog = SQLViewer(lines, parent)
        dialog.show()

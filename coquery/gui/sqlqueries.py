# -*- coding: utf-8 -*-
"""
logfile.py is part of Coquery.

Copyright (c) 2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from .pyqt_compat import QtCore, QtWidgets, QtGui

import sqlparse

try:
    from pygments import highlight
    from pygments.lexers import SqlLexer
    from pygments.formatters import HtmlFormatter
except ImportError:
    print("byebye")
    def highlight(text, *args, **kwargs):
        return text

    class SqlLexer():
        pass

    class HtmlFormatter():
        def get_style_defs(s):
            return ""

_translate = QtCore.QCoreApplication.translate


class SQLViewer(QtWidgets.QDialog):
    def __init__(self, text=None, lines=None, parent=None):
        super(SQLViewer, self).__init__(parent)
        self.resize(640, 480)
        self.setObjectName("SQLViewerDialog")
        self.setWindowTitle(_translate("SQLViewerDialog",
                                       "SQL Viewer – Coquery"))
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.viewer = QtWidgets.QTextEdit()
        self.viewer.setReadOnly(True)
        self.layout.addWidget(self.viewer)
        self.document = QtGui.QTextDocument()
        self.font = self.document.defaultFont()
        self.font.setFamily("monospace")
        self.document.setDefaultFont(self.font)
        self.viewer.setDocument(self.document)

        if lines:
            sql_queries = []
            for query_strings in lines:
                lst = [sqlparse.format(s.strip(), reindent=True)
                    for s in query_strings]
                sql_queries.append(";\n\n".join(lst))
            text = "\n\n-- next query --\n\n".join(sql_queries)
        print(text)
        css = HtmlFormatter().get_style_defs(".highlight")
        html = highlight(text, SqlLexer(), HtmlFormatter())

        self.document.setDefaultStyleSheet(css)
        self.document.setHtml(html)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()

    @staticmethod
    def view(lines, parent=None):
        dialog = SQLViewer(lines, parent)
        dialog.show()
        #return dialog.exec_()

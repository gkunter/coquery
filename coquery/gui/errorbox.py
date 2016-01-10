# -*- coding: utf-8 -*-

"""
errorbox.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
import options
import errorUi
from errors import *
import sys

class ErrorBox(QtGui.QDialog):
    def __init__(self, exc_info, exception, no_trace=False, message="", parent=None):
        
        super(ErrorBox, self).__init__(parent)
        
        self.ui = errorUi.Ui_ErrorDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(options.cfg.icon)
        self.ui.icon_label.setPixmap(QtGui.QIcon.fromTheme("dialog-error").pixmap(32, 32))
        
        exc_type, exc_message, exc_trace = get_error_repr(exc_info)
        exc_type = type(exception).__name__
        
        if message:
            exc_message = "<p>{}</p><p>{}</p>".format(exc_message, message)
        if not no_trace:
            error_text = "<table><tr><td>Type</td><td><b>{}</b></td></tr><tr><td>Message</td><td><b>{}</b></td></tr></table><p>{}</p>".format(
            exc_type, exc_message, exc_trace.replace("\n", "<br>").replace(" ", "&nbsp;"))
        else:
            error_text = "<table><tr><td>Type</td><td><b>{}</b></td></tr><tr><td>Message</td><td><b>{}</b></td></tr></table>".format(exc_type, exc_message)
            
        self.ui.trace_area.setText(error_text)
        
        try:
            self.resize(options.settings.value("errorbox_size"))
        except TypeError:
            pass
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()
            
    @staticmethod
    def show(exc_info, exception=None, no_trace=False, parent=None):
        dialog = ErrorBox(exc_info, exception, no_trace=no_trace, parent=parent)
        result = dialog.exec_()
        return None

    def closeEvent(self, *args):
        options.settings.setValue("errorbox_size", self.size())

            
def main():
    app = QtGui.QApplication(sys.argv)
    viewer = ErrorBox(Exception())
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    
# -*- coding: utf-8 -*-
"""
nltkdatafiles.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import sys
import os

sys.path.append(os.path.join(sys.path[0], "gui"))

from pyqt_compat import QtCore, QtGui
from ui.nltkDatafilesUi import Ui_NLTKDatafiles

import options
import classes

class NLTKDatafiles(QtGui.QDialog):
    def __init__(self, text, parent=None):
        
        super(NLTKDatafiles, self).__init__(parent)
        
        self.ui = Ui_NLTKDatafiles()
        self.ui.setupUi(self)
        self.ui.textBrowser.setText("<code>{}</code>".format(text.replace("\n", "<br/>")))
        
        try:
            self.resize(options.settings.value("nltkdatafiles_size"))
        except (TypeError, AttributeError):
            pass

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        try:
            options.settings.setValue("nltkdatafiles_size", self.size())
        except AttributeError:
            pass

    def accept(self):
        import nltk
        try:
            exec "nltk.download()" in globals(), locals()
        except Exception as e:
            errorbox.ErrorBox.show(sys.exc_info(), e, no_trace=True)
        finally:
            return super(NLTKDatafiles, self).accept()
        
    @staticmethod
    def ask(text, parent=None):
        
        dialog = NLTKDatafiles(text, parent=parent)        
        dialog.setVisible(True)
        return dialog.exec_() == QtGui.QDialog.Accepted
        
def main():
    app = QtGui.QApplication(sys.argv)
    NLTKDatafiles.ask("""
from pyqt_compat import QtCore, QtGui
from ui.nltkDatafilesUi import Ui_NLTKDatafiles

class NLTKDatafiles(QtGui.QDialog):
    def __init__(self, text, parent=None):
        
        super(NLTKDatafiles, self).__init__(parent)
        
        self.ui = Ui_NLTKDatafiles()
        self.ui.setupUi(self)
        self.ui.textBrowser.setText("<code>{}</code>".format(text))

        try:
            self.resize(options.settings.value("nltkdatafiles_size"))
        except (TypeError, NameError):
            pass

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
""")
    
    
if __name__ == "__main__":
    main()
    
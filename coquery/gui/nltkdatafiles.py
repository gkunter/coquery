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

from coquery import options
import classes
import errorbox
from pyqt_compat import QtCore, QtGui
from ui.nltkDatafilesUi import Ui_NLTKDatafiles

class NLTKDatafiles(QtGui.QDialog):
    updateLabel = QtCore.Signal(str)
    progressTheBar = QtCore.Signal()
    
    def __init__(self, missing, parent=None):
        
        super(NLTKDatafiles, self).__init__(parent)
        
        self.ui = Ui_NLTKDatafiles()
        self.ui.setupUi(self)
        self._missing = missing
        self.ui.textBrowser.setText("<code>{}</code>".format("<br/>".join(missing)))
        self.ui.progressBar.hide()
        
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

    def download_packages(self):
        s = "python -c 'import nltk; nltk.download({})'"
        s = "nltk.download({}, raise_on_error=True)"
        import nltk
        for x in self._missing:
            package = x.split("/")[1]
            self.updateLabel.emit(package)
            exec(s.format('"{}"'.format(package)))
            self.progressTheBar.emit()
    
    def download_finish(self):
        super(NLTKDatafiles, self).accept()

    def download_exception(self):
        errorbox.ErrorBox.show(self.exc_info, self, no_trace=False)

    def update_label(self, s):
        self.ui.label.setText("Installing NLTK component {}...".format(s))

    def next_bar(self):
        self.ui.progressBar.setValue(self.ui.progressBar.value()+1)

    def accept(self):
        self.ui.textBrowser.hide()
        self.ui.label_2.hide()
        self.ui.progressBar.show()
        self.ui.progressBar.setMaximum(len(self._missing))
        self.ui.progressBar.setValue(0)
        self.thread = classes.CoqThread(self.download_packages, self)
        self.thread.taskFinished.connect(self.download_finish)
        self.thread.taskException.connect(self.download_exception)
        self.updateLabel.connect(self.update_label)
        self.progressTheBar.connect(self.next_bar)
        self.thread.start()
        
    @staticmethod
    def ask(missing, parent=None):
        dialog = NLTKDatafiles(missing, parent=parent)        
        return dialog.exec_() == QtGui.QDialog.Accepted
        
def main():
    app = QtGui.QApplication(sys.argv)
    NLTKDatafiles.ask("""
from gui.pyqt_compat import QtCore, QtGui
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
    
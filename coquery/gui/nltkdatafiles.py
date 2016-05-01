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
import zipfile
import shutil

from coquery import options
from coquery.unicode import utf8
from . import classes
from . import errorbox
from .pyqt_compat import QtCore, QtGui
from .ui.nltkDatafilesUi import Ui_NLTKDatafiles

_NLTK_dir = None

class NLTKDatafiles(QtGui.QDialog):
    updateLabel = QtCore.Signal(str)
    progressTheBar = QtCore.Signal()
    
    def __init__(self, missing, parent=None):
        
        super(NLTKDatafiles, self).__init__(parent)
        
        self.ui = Ui_NLTKDatafiles()
        self.ui.setupUi(self)
        self._missing = missing
        self.ui.textBrowser.setText("<code>{}</code>".format("<br/>".join(missing)))
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Open).clicked.disconnect()
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Open).clicked.connect(self.from_directory)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Open).setText("From directory...")
        self.ui.progressBar.hide()
        self.download_dir = None
        
        try:
            self.resize(options.settings.value("nltkdatafiles_size"))
        except (TypeError, AttributeError):
            pass

    def from_directory(self):
        global _NLTK_dir
        name = QtGui.QFileDialog.getExistingDirectory(directory=options.cfg.textgrids_file_path, options=QtGui.QFileDialog.ReadOnly|QtGui.QFileDialog.ShowDirsOnly|QtGui.QFileDialog.HideNameFilterDetails)
        if type(name) == tuple:
            name = name[0]

        if name:
            _NLTK_dir = utf8(name)
            self.accept()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        try:
            options.settings.setValue("nltkdatafiles_size", self.size())
        except AttributeError:
            pass

    def copy_packages(self):
        import nltk.data
        target_path = nltk.data.path[0]
        
        for x in [comp for comp in self._missing if "/" in comp]:
            parts = x.split("/")
            subdir = os.path.join(target_path, parts[0])
            package = parts[1]
            zip_name = "{}.zip".format(package)
            self.updateLabel.emit(package)
            src = os.path.join(_NLTK_dir, zip_name)
            dst = os.path.join(subdir, zip_name)
            if not os.path.exists(subdir):
                os.makedirs(subdir)

            if os.path.exists(src):
                shutil.copyfile(src, dst)
            else:
                raise ValueError("Package file {}.zip not found in {}".format(package, _NLTK_dir))

            with zipfile.ZipFile(dst) as zipped:
                for member in zipped.infolist():
                    zipped.extract(member, subdir)
            
            self.progressTheBar.emit()

    def download_packages(self):
        import nltk
        
        for x in [comp for comp in self._missing if "/" in comp]:
            package = x.split("/")[1]
            self.updateLabel.emit(package)
            nltk.download(package, raise_on_error=True)
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
        if not _NLTK_dir:
            self.thread = classes.CoqThread(self.download_packages, self)
        else:
            self.thread = classes.CoqThread(self.copy_packages, self)
        self.thread.taskFinished.connect(self.download_finish)
        self.thread.taskException.connect(self.download_exception)
        self.updateLabel.connect(self.update_label)
        self.progressTheBar.connect(self.next_bar)
        self.thread.start()
        
    @staticmethod
    def ask(missing, parent=None):
        dialog = NLTKDatafiles(missing, parent=parent)        
        return dialog.exec_() == QtGui.QDialog.Accepted
        


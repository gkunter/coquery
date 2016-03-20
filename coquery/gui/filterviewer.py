# -*- coding: utf-8 -*-
"""
filters.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import codecs
import pandas as pd

from coquery import options
from coquery.defines import *
from . import classes
from .pyqt_compat import QtCore, QtGui
from .ui.stopwordsUi import Ui_Stopwords

class Filters(QtGui.QDialog):
    def __init__(self, word_list, default=None, parent=None, icon=None):
        super(Filters, self).__init__(parent)
        
        self._word_list= word_list
        self.ui = Ui_Stopwords()
        self.ui.setupUi(self)
        self.ui.horizontalLayout.removeWidget(self.ui.stopword_list)
        self.ui.stopword_list.close()
        self.ui.filter_list = classes.CoqTagBox(label="Add corpus filter:")
        self.ui.horizontalLayout.insertWidget(0, self.ui.filter_list)

        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.reset_list)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self.save_list)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Open).clicked.connect(self.open_list)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.close)

        try:
            self.resize(options.settings.value("filters_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("filters_size", self.size())
        self.close()
 
    def reset_list(self):
        response = QtGui.QMessageBox.question(self, "Clear filter list", msg_clear_filters, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if response == QtGui.QMessageBox.Yes:
            self.ui.filter_list.cloud_area.clear()
    
    def save_list(self):
        name = QtGui.QFileDialog.getSaveFileName(directory=options.cfg.filter_file_path)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.filter_file_path = os.path.dirname(name)
            df = pd.DataFrame(self._word_list)
            try:
                df.to_csv(name,
                        index=False, header=False,
                        encoding=options.cfg.output_encoding)
            except IOError as e:
                QtGui.QMessageBox.critical(self, "Disk error", msg_disk_error)
            except (UnicodeEncodeError, UnicodeDecodeError):
                QtGui.QMessageBox.critical(self, "Encoding error", msg_encoding_error)
    
    def open_list(self):
        name = QtGui.QFileDialog.getOpenFileName(directory=options.cfg.filter_file_path)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.filter_file_path = os.path.dirname(name)
            self.ui.buttonBox.setEnabled(False)
            try:
                with codecs.open(name, "r", encoding=options.cfg.output_encoding) as input_file:
                    for word in sorted(set(" ".join(input_file.readlines()).split())):
                        if word and not self.ui.filter_list.hasTag(word):
                            self.ui.filter_list.addTag(str(word))
            except IOError as e:
                QtGui.QMessageBox.critical(self, "Disk error", msg_disk_error)
            except (UnicodeEncodeError, UnicodeDecodeError):
                QtGui.QMessageBox.critical(self, "Encoding error", msg_encoding_error)
            finally:
                self.ui.buttonBox.setEnabled(True)
    
    def exec_(self):
        result = super(Filters, self).exec_()
        if result: 
            return [str(self.ui.filter_list.cloud_area.itemAt(x).widget().text()) for x in range(self.ui.filter_list.cloud_area.count())]
        else:
            return None
    
    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            return
        else:
            super(Filters, self).keyPressEvent(event)
        
    def set_list(self, l):
        for x in l:
            self.ui.filter_list.addTag(str(x))
        
    @staticmethod
    def manage(this_list, parent=None, icon=None):
        dialog = Filters(parent, icon)
        dialog.set_list(this_list)
        return dialog.exec_()

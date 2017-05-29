# -*- coding: utf-8 -*-
"""
settings.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import codecs
import pandas as pd
import os

from coquery import options
from coquery.defines import *
from coquery.general import is_language_code, language_by_code, code_by_language
from coquery.unicode import utf8
from . import classes
from .pyqt_compat import QtCore, QtWidgets, QtGui, get_toplevel_window
from .ui.stopwordsUi import Ui_Stopwords

class CoqStopWord(QtWidgets.QListWidgetItem):
    def __init__(self, *args):
        super(CoqStopWord, self).__init__(*args)
        icon = get_toplevel_window().get_icon("Delete")
        self.setIcon(icon)
        brush = QtGui.QBrush(QtGui.QColor("lightcyan"))
        self.setBackground(brush)
        
class CoqStopwordDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        super(CoqStopwordDelegate, self).__init__(parent, *args)

    def paint(self, painter, option, index):
        painter.save()

        painter.drawPixmap(0, 0, 
                QtWidgets.qApp.style().standardPixmap(QtWidgets.QStyle.SP_DockWidgetCloseButton))
        # set background color
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
        else:
            painter.setBrush(QtGui.QBrush(QtGui.QColor("lightcyan")))
        painter.drawRect(option.rect)

        # set text color
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        value = index.data(QtCore.Qt.DisplayRole)
        painter.drawText(option.rect, QtCore.Qt.AlignLeft, value)

        painter.restore()
        
class CoqAddWord(CoqStopWord):
    def __init__(self, *args):
        super(CoqStopWord, self).__init__(*args)
        self.reset()
    
    def reset(self):
        self.setText("Add...")
        
class CoqStopwordList(QtWidgets.QListWidget):
    def __init__(self, *args):
        super(CoqStopwordList, self).__init__(*args)
        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setFlow(QtWidgets.QListView.TopToBottom)
        self.setProperty("isWrapping", True)
        self.setMovement(QtWidgets.QListView.Static)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSpacing(10)
        self.setFlow(QtWidgets.QListView.LeftToRight)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setWordWrap(True)
        self.setSelectionRectVisible(True)

        self.itemClicked.connect(self.onClick)
        self.add_item = None
 
        self.setItemDelegate(CoqStopwordDelegate(parent=self))

    def onClick(self, item):
        if item == self.add_item:
            #self.add_item.setText("")
            self.openPersistentEditor(self.add_item)
            print("editing")
            self.itemChanged.connect(self.onChange)
            
    def onChange(self, item):
        if item == self.add_item:
            print("change")
            self.itemChanged.disconnect(self.onChange)
            self.closePersistentEditor(self.add_item)
            words = str(self.add_item.text()).split()
            for x in words:
                self.insertItem(self.count() - 1, CoqStopWord(x))
            self.add_item.reset()

    def addAddItem(self, item, *args):
        super(CoqStopwordList, self).addItem(item, *args)
        self.add_item = item

class Stopwords(QtWidgets.QDialog):
    def __init__(self, word_list, default=None, parent=None, icon=None):
        super(Stopwords, self).__init__(parent)
        
        self._word_list= word_list
        self.ui = Ui_Stopwords()
        self.ui.setupUi(self)
        
        lang = []
        for file in os.listdir(options.cfg.stopword_path):
            code, ext = os.path.splitext(file)
            if is_language_code(code) and ext == ".txt":
                lang.append(language_by_code(code).capitalize())

        lang = sorted(lang)
        self.ui.combo_language.addItems(lang)
        self.ui.combo_language.setCurrentIndex(lang.index("English"))
        self.ui.button_add_list.clicked.connect(self.add_stopword_list)

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.close)
        self.ui.buttonbox_io.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_list)
        self.ui.buttonbox_io.button(QtWidgets.QDialogButtonBox.Open).clicked.connect(self.open_list)
        self.ui.buttonbox_io.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect(self.reset_list)

        try:
            self.resize(options.settings.value("stopwords_size"))
        except TypeError:
            pass
        ix = self.ui.combo_language.findText(utf8(options.settings.value("stopword_language")))
        if ix >= 0:
            self.ui.combo_language.setCurrentIndex(ix)

    def closeEvent(self, event):
        options.settings.setValue("stopwords_size", self.size())
        
        options.settings.setValue("stopword_language", utf8(self.ui.combo_language.currentText()))
        self.close()
 
    def reset_list(self):
        response = QtWidgets.QMessageBox.question(self, "Clear stop word list", msg_clear_stopwords, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if response == QtWidgets.QMessageBox.Yes:
            self.ui.stopword_list.cloud_area.clear()
    
    def save_list(self):
        name = QtWidgets.QFileDialog.getSaveFileName(directory=options.cfg.stopwords_file_path)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.stopwords_file_path = os.path.dirname(name)
            df = pd.DataFrame(self._word_list)
            try:
                df.to_csv(name,
                        index=False, header=False,
                        encoding=options.cfg.output_encoding)
            except IOError as e:
                QtWidgets.QMessageBox.critical(self, "Disk error", msg_disk_error)
            except (UnicodeEncodeError, UnicodeDecodeError):
                QtWidgets.QMessageBox.critical(self, "Encoding error", msg_encoding_error)
    
    def open_list(self):
        name = QtWidgets.QFileDialog.getOpenFileName(directory=options.cfg.stopwords_file_path)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.stopwords_file_path = os.path.dirname(name)
            self.ui.buttonBox.setEnabled(False)
            try:
                with codecs.open(name, "r", encoding=options.cfg.output_encoding) as input_file:
                    for word in sorted(set(" ".join(input_file.readlines()).split())):
                        if word and not self.ui.stopword_list.hasTag(word):
                            self.ui.stopword_list.addTag(utf8(word))
            except IOError as e:
                QtWidgets.QMessageBox.critical(self, "Disk error", msg_disk_error)
            except (UnicodeEncodeError, UnicodeDecodeError):
                QtWidgets.QMessageBox.critical(self, "Encoding error", msg_encoding_error)
            finally:
                self.ui.buttonBox.setEnabled(True)
    
    def add_stopword_list(self):
        lang = utf8(self.ui.combo_language.currentText())
        
        stopwords = []
        for line in open(os.path.join(options.cfg.stopword_path, 
                               "{}.txt".format(code_by_language(lang))), "r"):
            if not line.strip().startswith("#"):
                stopwords.append(line.strip())

        for word in sorted(set(stopwords)):
            if not self.ui.stopword_list.hasTag(word):
                self.ui.stopword_list.addTag(utf8(word))
    
    def exec_(self):
        result = super(Stopwords, self).exec_()
        if result: 
            return [str(self.ui.stopword_list.cloud_area.itemAt(x).widget().text()) for x in range(self.ui.stopword_list.cloud_area.count())]
        else:
            return None
    
    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            return
        else:
            super(Stopwords, self).keyPressEvent(event)
        
    def set_list(self, l):
        for x in l:
            self.ui.stopword_list.addTag(str(x))
        
    @staticmethod
    def manage(this_list, parent=None, icon=None):
        dialog = Stopwords(parent, icon)
        dialog.set_list(this_list)
        return dialog.exec_()

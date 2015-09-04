# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'corpusManager.ui'
#
# Created: Fri Sep  4 15:35:32 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui, frameShadow

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_corpusManager(object):
    def setupUi(self, corpusManager):
        corpusManager.setObjectName(_fromUtf8("corpusManager"))
        corpusManager.resize(640, 480)
        self.verticalLayout = QtGui.QVBoxLayout(corpusManager)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scroll_area_corpus = QtGui.QScrollArea(corpusManager)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scroll_area_corpus.sizePolicy().hasHeightForWidth())
        self.scroll_area_corpus.setSizePolicy(sizePolicy)
        self.scroll_area_corpus.setFrameShape(QtGui.QFrame.StyledPanel)
        self.scroll_area_corpus.setFrameShadow(frameShadow)
        self.scroll_area_corpus.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area_corpus.setWidgetResizable(True)
        self.scroll_area_corpus.setObjectName(_fromUtf8("scroll_area_corpus"))
        self.scroll_area_content = QtGui.QWidget()
        self.scroll_area_content.setGeometry(QtCore.QRect(0, 0, 626, 351))
        self.scroll_area_content.setObjectName(_fromUtf8("scroll_area_content"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.scroll_area_content)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.corpus_stack = QtGui.QToolBox(self.scroll_area_content)
        self.corpus_stack.setFrameShape(QtGui.QFrame.NoFrame)
        self.corpus_stack.setFrameShadow(frameShadow)
        self.corpus_stack.setObjectName(_fromUtf8("corpus_stack"))

        self.horizontalLayout_2.addWidget(self.corpus_stack)
        self.scroll_area_corpus.setWidget(self.scroll_area_content)
        self.verticalLayout.addWidget(self.scroll_area_corpus)
        self.frame = QtGui.QFrame(corpusManager)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setMargin(10)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setEnabled(False)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_search_installer = QtGui.QPushButton(self.frame)
        self.button_search_installer.setEnabled(False)
        self.button_search_installer.setObjectName(_fromUtf8("button_search_installer"))
        self.horizontalLayout.addWidget(self.button_search_installer)
        self.verticalLayout.addWidget(self.frame)
        self.buttonBox = QtGui.QDialogButtonBox(corpusManager)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(corpusManager)
        self.corpus_stack.setCurrentIndex(0)
        self.corpus_stack.layout().setSpacing(10)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), corpusManager.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), corpusManager.reject)
        QtCore.QMetaObject.connectSlotsByName(corpusManager)

    def retranslateUi(self, corpusManager):
        corpusManager.setWindowTitle(_translate("corpusManager", "Corpus manager  – Coquery", None))
        self.label.setText(_translate("corpusManager", "Fetch a corpus installer from the internet (feature not available in this version): ", None))
        self.button_search_installer.setText(_translate("corpusManager", "Search...", None))



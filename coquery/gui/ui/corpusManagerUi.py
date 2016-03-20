# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'corpusManager.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from coquery.gui.pyqt_compat import QtCore, QtGui, frameShadow, frameShape

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
        corpusManager.resize(800, 600)
        self.verticalLayout = QtGui.QVBoxLayout(corpusManager)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame_2 = QtGui.QFrame(corpusManager)
        self.frame_2.setFrameShape(frameShape)
        self.frame_2.setFrameShadow(frameShadow)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.list_corpora = QtGui.QScrollArea(self.frame_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_corpora.sizePolicy().hasHeightForWidth())
        self.list_corpora.setSizePolicy(sizePolicy)
        self.list_corpora.setFrameShape(QtGui.QFrame.NoFrame)
        self.list_corpora.setWidgetResizable(True)
        self.list_corpora.setObjectName(_fromUtf8("list_corpora"))
        self.list_content = QtGui.QWidget()
        self.list_content.setGeometry(QtCore.QRect(0, 0, 778, 522))
        self.list_content.setObjectName(_fromUtf8("list_content"))
        self.list_layout = QtGui.QVBoxLayout(self.list_content)
        self.list_layout.setMargin(0)
        self.list_layout.setSpacing(0)
        self.list_layout.setObjectName(_fromUtf8("list_layout"))
        self.list_corpora.setWidget(self.list_content)
        self.verticalLayout_2.addWidget(self.list_corpora)
        self.verticalLayout.addWidget(self.frame_2)
        self.frame = QtGui.QFrame(corpusManager)
        self.frame.setFrameShape(frameShape)
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
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(corpusManager)
        QtCore.QMetaObject.connectSlotsByName(corpusManager)

    def retranslateUi(self, corpusManager):
        corpusManager.setWindowTitle(_translate("corpusManager", "Corpus manager  – Coquery", None))
        self.label.setText(_translate("corpusManager", "Fetch a corpus installer from the internet (feature not available in this version): ", None))
        self.button_search_installer.setText(_translate("corpusManager", "Search...", None))



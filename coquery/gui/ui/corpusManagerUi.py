# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'corpusManager.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_corpusManager(object):
    def setupUi(self, corpusManager):
        corpusManager.setObjectName("corpusManager")
        corpusManager.resize(800, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(corpusManager)
        self.verticalLayout.setObjectName("verticalLayout")
        self.list_corpora = QtWidgets.QScrollArea(corpusManager)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_corpora.sizePolicy().hasHeightForWidth())
        self.list_corpora.setSizePolicy(sizePolicy)
        self.list_corpora.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.list_corpora.setWidgetResizable(True)
        self.list_corpora.setObjectName("list_corpora")
        self.list_content = QtWidgets.QWidget()
        self.list_content.setGeometry(QtCore.QRect(0, 0, 792, 592))
        self.list_content.setObjectName("list_content")
        self.list_layout = QtWidgets.QVBoxLayout(self.list_content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.list_layout.setObjectName("list_layout")
        self.list_corpora.setWidget(self.list_content)
        self.verticalLayout.addWidget(self.list_corpora)

        self.retranslateUi(corpusManager)
        QtCore.QMetaObject.connectSlotsByName(corpusManager)

    def retranslateUi(self, corpusManager):
        _translate = QtCore.QCoreApplication.translate
        corpusManager.setWindowTitle(_translate("corpusManager", "Corpus manager  – Coquery"))



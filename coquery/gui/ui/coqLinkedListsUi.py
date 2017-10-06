# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coqLinkedLists.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CoqLinkedLists(object):
    def setupUi(self, CoqLinkedLists):
        CoqLinkedLists.setObjectName("CoqLinkedLists")
        CoqLinkedLists.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(CoqLinkedLists)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(CoqLinkedLists)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.list_classes = QtWidgets.QListWidget(self.splitter)
        self.list_classes.setObjectName("list_classes")
        self.list_functions = CoqWidgetListView(self.splitter)
        self.list_functions.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.list_functions.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_functions.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_functions.setObjectName("list_functions")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(CoqLinkedLists)
        QtCore.QMetaObject.connectSlotsByName(CoqLinkedLists)

    def retranslateUi(self, CoqLinkedLists):
        _translate = QtCore.QCoreApplication.translate
        CoqLinkedLists.setWindowTitle(_translate("CoqLinkedLists", "Form"))

from ..classes import CoqWidgetListView


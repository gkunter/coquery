# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coqSearchLine.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CoqSearchLine(object):
    def setupUi(self, CoqSearchLine):
        CoqSearchLine.setObjectName("CoqSearchLine")
        CoqSearchLine.resize(640, 23)
        self.horizontalLayout = QtWidgets.QHBoxLayout(CoqSearchLine)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(CoqSearchLine)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.edit_search = QtWidgets.QLineEdit(CoqSearchLine)
        self.edit_search.setObjectName("edit_search")
        self.horizontalLayout.addWidget(self.edit_search)

        self.retranslateUi(CoqSearchLine)
        QtCore.QMetaObject.connectSlotsByName(CoqSearchLine)

    def retranslateUi(self, CoqSearchLine):
        _translate = QtCore.QCoreApplication.translate
        CoqSearchLine.setWindowTitle(_translate("CoqSearchLine", "Form"))
        self.label.setText(_translate("CoqSearchLine", "Search:"))



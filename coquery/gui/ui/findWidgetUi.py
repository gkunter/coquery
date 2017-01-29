# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'findWidget.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FindWidget(object):
    def setupUi(self, FindWidget):
        FindWidget.setObjectName("FindWidget")
        FindWidget.resize(1040, 102)
        self.horizontalLayout = QtWidgets.QHBoxLayout(FindWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_find_close = QtWidgets.QToolButton(FindWidget)
        icon = QtGui.QIcon.fromTheme("window-close")
        self.button_find_close.setIcon(icon)
        self.button_find_close.setObjectName("button_find_close")
        self.horizontalLayout.addWidget(self.button_find_close)
        self.label = QtWidgets.QLabel(FindWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.edit_find = QtWidgets.QLineEdit(FindWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_find.sizePolicy().hasHeightForWidth())
        self.edit_find.setSizePolicy(sizePolicy)
        self.edit_find.setObjectName("edit_find")
        self.horizontalLayout.addWidget(self.edit_find)
        self.button_find_next = QtWidgets.QPushButton(FindWidget)
        icon = QtGui.QIcon.fromTheme("go-down")
        self.button_find_next.setIcon(icon)
        self.button_find_next.setObjectName("button_find_next")
        self.horizontalLayout.addWidget(self.button_find_next)
        self.button_find_prev = QtWidgets.QPushButton(FindWidget)
        icon = QtGui.QIcon.fromTheme("go-up")
        self.button_find_prev.setIcon(icon)
        self.button_find_prev.setObjectName("button_find_prev")
        self.horizontalLayout.addWidget(self.button_find_prev)
        self.horizontalLayout.setStretch(2, 1)

        self.retranslateUi(FindWidget)
        QtCore.QMetaObject.connectSlotsByName(FindWidget)

    def retranslateUi(self, FindWidget):
        _translate = QtCore.QCoreApplication.translate
        FindWidget.setWindowTitle(_translate("FindWidget", "Form"))
        self.button_find_close.setText(_translate("FindWidget", "..."))
        self.label.setText(_translate("FindWidget", "Find:"))
        self.button_find_next.setText(_translate("FindWidget", "Next"))
        self.button_find_prev.setText(_translate("FindWidget", "Previous"))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'buttonList.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ButtonList(object):
    def setupUi(self, ButtonList):
        ButtonList.setObjectName("ButtonList")
        ButtonList.resize(472, 184)
        self.verticalLayout = QtWidgets.QVBoxLayout(ButtonList)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.list_widget = QtWidgets.QListWidget(ButtonList)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_widget.sizePolicy().hasHeightForWidth())
        self.list_widget.setSizePolicy(sizePolicy)
        self.list_widget.setMinimumSize(QtCore.QSize(0, 24))
        self.list_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.list_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.list_widget.setObjectName("list_widget")
        self.verticalLayout.addWidget(self.list_widget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_remove_group = QtWidgets.QPushButton(ButtonList)
        self.button_remove_group.setObjectName("button_remove_group")
        self.horizontalLayout.addWidget(self.button_remove_group)
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_group_up = QtWidgets.QToolButton(ButtonList)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_group_up.sizePolicy().hasHeightForWidth())
        self.button_group_up.setSizePolicy(sizePolicy)
        self.button_group_up.setText("")
        self.button_group_up.setObjectName("button_group_up")
        self.horizontalLayout.addWidget(self.button_group_up)
        self.button_group_down = QtWidgets.QToolButton(ButtonList)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_group_down.sizePolicy().hasHeightForWidth())
        self.button_group_down.setSizePolicy(sizePolicy)
        self.button_group_down.setText("")
        self.button_group_down.setObjectName("button_group_down")
        self.horizontalLayout.addWidget(self.button_group_down)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(ButtonList)
        QtCore.QMetaObject.connectSlotsByName(ButtonList)

    def retranslateUi(self, ButtonList):
        _translate = QtCore.QCoreApplication.translate
        self.button_remove_group.setText(_translate("ButtonList", "Remove"))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'groupcolumns/groupcolumns.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GroupColumns(object):
    def setupUi(self, GroupColumns):
        GroupColumns.setObjectName("GroupColumns")
        self.verticalLayout = QtWidgets.QVBoxLayout(GroupColumns)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.list_widget = CoqListWidget(GroupColumns)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_widget.sizePolicy().hasHeightForWidth())
        self.list_widget.setSizePolicy(sizePolicy)
        self.list_widget.setMinimumSize(QtCore.QSize(0, 24))
        self.list_widget.setObjectName("list_widget")
        self.verticalLayout.addWidget(self.list_widget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_remove_group = QtWidgets.QPushButton(GroupColumns)
        self.button_remove_group.setObjectName("button_remove_group")
        self.horizontalLayout.addWidget(self.button_remove_group)
        spacerItem = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_group_up = QtWidgets.QToolButton(GroupColumns)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_group_up.sizePolicy().hasHeightForWidth())
        self.button_group_up.setSizePolicy(sizePolicy)
        self.button_group_up.setText("")
        self.button_group_up.setObjectName("button_group_up")
        self.horizontalLayout.addWidget(self.button_group_up)
        self.button_group_down = QtWidgets.QToolButton(GroupColumns)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_group_down.sizePolicy().hasHeightForWidth())
        self.button_group_down.setSizePolicy(sizePolicy)
        self.button_group_down.setText("")
        self.button_group_down.setObjectName("button_group_down")
        self.horizontalLayout.addWidget(self.button_group_down)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(GroupColumns)
        QtCore.QMetaObject.connectSlotsByName(GroupColumns)

    def retranslateUi(self, GroupColumns):
        _translate = QtCore.QCoreApplication.translate
        GroupColumns.setWindowTitle(_translate("GroupColumns", "groupcolumns"))
        self.button_remove_group.setText(_translate("GroupColumns", "Remove"))

from ..classes import CoqListWidget


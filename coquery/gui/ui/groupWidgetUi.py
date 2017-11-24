# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'groupWidget.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GroupWidget(object):
    def setupUi(self, GroupWidget):
        GroupWidget.setObjectName("GroupWidget")
        GroupWidget.resize(759, 450)
        self.gridLayout_2 = QtWidgets.QGridLayout(GroupWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tree_groups = QtWidgets.QTreeWidget(GroupWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_groups.sizePolicy().hasHeightForWidth())
        self.tree_groups.setSizePolicy(sizePolicy)
        self.tree_groups.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tree_groups.setRootIsDecorated(True)
        self.tree_groups.setAnimated(True)
        self.tree_groups.setObjectName("tree_groups")
        self.tree_groups.header().setVisible(False)
        self.gridLayout_2.addWidget(self.tree_groups, 0, 0, 4, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 166, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 0, 1, 1, 1)
        self.button_group_up = QtWidgets.QToolButton(GroupWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_group_up.sizePolicy().hasHeightForWidth())
        self.button_group_up.setSizePolicy(sizePolicy)
        self.button_group_up.setText("")
        self.button_group_up.setObjectName("button_group_up")
        self.gridLayout_2.addWidget(self.button_group_up, 1, 1, 1, 1)
        self.button_group_down = QtWidgets.QToolButton(GroupWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_group_down.sizePolicy().hasHeightForWidth())
        self.button_group_down.setSizePolicy(sizePolicy)
        self.button_group_down.setText("")
        self.button_group_down.setObjectName("button_group_down")
        self.gridLayout_2.addWidget(self.button_group_down, 2, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 166, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 3, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.button_add_group = QtWidgets.QPushButton(GroupWidget)
        self.button_add_group.setObjectName("button_add_group")
        self.gridLayout.addWidget(self.button_add_group, 0, 0, 1, 1)
        self.button_edit_group = QtWidgets.QPushButton(GroupWidget)
        self.button_edit_group.setObjectName("button_edit_group")
        self.gridLayout.addWidget(self.button_edit_group, 1, 0, 1, 1)
        self.button_remove_group = QtWidgets.QPushButton(GroupWidget)
        self.button_remove_group.setObjectName("button_remove_group")
        self.gridLayout.addWidget(self.button_remove_group, 1, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        spacerItem3 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 2)
        self.gridLayout_2.setColumnStretch(0, 1)

        self.retranslateUi(GroupWidget)
        QtCore.QMetaObject.connectSlotsByName(GroupWidget)

    def retranslateUi(self, GroupWidget):
        _translate = QtCore.QCoreApplication.translate
        GroupWidget.setWindowTitle(_translate("GroupWidget", "Form"))
        self.tree_groups.headerItem().setText(0, _translate("GroupWidget", "Groups"))
        self.button_add_group.setText(_translate("GroupWidget", "New..."))
        self.button_edit_group.setText(_translate("GroupWidget", "Edit..."))
        self.button_remove_group.setText(_translate("GroupWidget", "Remove"))


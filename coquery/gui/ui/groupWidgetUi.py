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
        GroupWidget.resize(164, 160)
        self.verticalLayout = QtWidgets.QVBoxLayout(GroupWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
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
        self.verticalLayout.addWidget(self.tree_groups)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.button_remove_group = QtWidgets.QPushButton(GroupWidget)
        self.button_remove_group.setObjectName("button_remove_group")
        self.gridLayout.addWidget(self.button_remove_group, 1, 2, 1, 1)
        self.button_add_group = QtWidgets.QPushButton(GroupWidget)
        self.button_add_group.setObjectName("button_add_group")
        self.gridLayout.addWidget(self.button_add_group, 0, 1, 1, 1)
        self.button_edit_group = QtWidgets.QPushButton(GroupWidget)
        self.button_edit_group.setObjectName("button_edit_group")
        self.gridLayout.addWidget(self.button_edit_group, 1, 1, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.button_group_up = QtWidgets.QToolButton(GroupWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_group_up.sizePolicy().hasHeightForWidth())
        self.button_group_up.setSizePolicy(sizePolicy)
        self.button_group_up.setText("")
        self.button_group_up.setObjectName("button_group_up")
        self.horizontalLayout_2.addWidget(self.button_group_up)
        self.button_group_down = QtWidgets.QToolButton(GroupWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_group_down.sizePolicy().hasHeightForWidth())
        self.button_group_down.setSizePolicy(sizePolicy)
        self.button_group_down.setText("")
        self.button_group_down.setObjectName("button_group_down")
        self.horizontalLayout_2.addWidget(self.button_group_down)
        self.horizontalLayout_2.setStretch(0, 1)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 0, 2, 1)
        spacerItem2 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 3, 2, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(3, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(GroupWidget)
        QtCore.QMetaObject.connectSlotsByName(GroupWidget)

    def retranslateUi(self, GroupWidget):
        _translate = QtCore.QCoreApplication.translate
        GroupWidget.setWindowTitle(_translate("GroupWidget", "Form"))
        self.tree_groups.headerItem().setText(0, _translate("GroupWidget", "Groups"))
        self.button_remove_group.setText(_translate("GroupWidget", "Remove"))
        self.button_add_group.setText(_translate("GroupWidget", "New..."))
        self.button_edit_group.setText(_translate("GroupWidget", "Edit..."))


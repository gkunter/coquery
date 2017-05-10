# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'groupWidget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GroupWidget(object):
    def setupUi(self, GroupWidget):
        GroupWidget.setObjectName("GroupWidget")
        GroupWidget.resize(640, 478)
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
        self.gridLayout.setObjectName("gridLayout")
        self.button_add_group = QtWidgets.QPushButton(GroupWidget)
        self.button_add_group.setObjectName("button_add_group")
        self.gridLayout.addWidget(self.button_add_group, 0, 1, 1, 1)
        self.button_remove_group = QtWidgets.QPushButton(GroupWidget)
        self.button_remove_group.setObjectName("button_remove_group")
        self.gridLayout.addWidget(self.button_remove_group, 1, 2, 1, 1)
        self.button_edit_group = QtWidgets.QPushButton(GroupWidget)
        self.button_edit_group.setObjectName("button_edit_group")
        self.gridLayout.addWidget(self.button_edit_group, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(GroupWidget)
        QtCore.QMetaObject.connectSlotsByName(GroupWidget)

    def retranslateUi(self, GroupWidget):
        _translate = QtCore.QCoreApplication.translate
        GroupWidget.setWindowTitle(_translate("GroupWidget", "Form"))
        self.tree_groups.headerItem().setText(0, _translate("GroupWidget", "Groups"))
        self.button_add_group.setText(_translate("GroupWidget", "New..."))
        self.button_remove_group.setText(_translate("GroupWidget", "Remove"))
        self.button_edit_group.setText(_translate("GroupWidget", "Edit..."))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'groupDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GroupDialog(object):
    def setupUi(self, GroupDialog):
        GroupDialog.setObjectName("GroupDialog")
        GroupDialog.resize(640, 480)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(GroupDialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(GroupDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edit_label = QtWidgets.QLineEdit(GroupDialog)
        self.edit_label.setText("")
        self.edit_label.setObjectName("edit_label")
        self.gridLayout.addWidget(self.edit_label, 0, 1, 1, 1)
        self.label_duplicates = QtWidgets.QLabel(GroupDialog)
        self.label_duplicates.setObjectName("label_duplicates")
        self.gridLayout.addWidget(self.label_duplicates, 2, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radio_keep_duplicates = QtWidgets.QRadioButton(GroupDialog)
        self.radio_keep_duplicates.setChecked(True)
        self.radio_keep_duplicates.setObjectName("radio_keep_duplicates")
        self.horizontalLayout.addWidget(self.radio_keep_duplicates)
        self.radio_remove_duplicates = QtWidgets.QRadioButton(GroupDialog)
        self.radio_remove_duplicates.setObjectName("radio_remove_duplicates")
        self.horizontalLayout.addWidget(self.radio_remove_duplicates)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(GroupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.tabWidget = QtWidgets.QTabWidget(GroupDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_selection = CoqListSelect(self.tab)
        self.widget_selection.setObjectName("widget_selection")
        self.verticalLayout_2.addWidget(self.widget_selection)
        self.tabWidget.addTab(self.tab, "")
        self.tab_functions = QtWidgets.QWidget()
        self.tab_functions.setObjectName("tab_functions")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_functions)
        self.horizontalLayout_2.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.linked_functions = CoqLinkedLists(self.tab_functions)
        self.linked_functions.setEditTriggers(QtWidgets.QAbstractItemView.CurrentChanged)
        self.linked_functions.setAlternatingRowColors(True)
        self.linked_functions.setObjectName("linked_functions")
        self.horizontalLayout_2.addWidget(self.linked_functions)
        self.tabWidget.addTab(self.tab_functions, "")
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 2)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.label.setBuddy(self.edit_label)

        self.retranslateUi(GroupDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(GroupDialog.accept)
        self.buttonBox.rejected.connect(GroupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GroupDialog)
        GroupDialog.setTabOrder(self.widget_selection, self.radio_keep_duplicates)
        GroupDialog.setTabOrder(self.radio_keep_duplicates, self.buttonBox)

    def retranslateUi(self, GroupDialog):
        _translate = QtCore.QCoreApplication.translate
        GroupDialog.setWindowTitle(_translate("GroupDialog", "Add a group – Coquery"))
        self.label.setText(_translate("GroupDialog", "&Group name:"))
        self.label_duplicates.setText(_translate("GroupDialog", "Duplicates:"))
        self.radio_keep_duplicates.setText(_translate("GroupDialog", "&Keep"))
        self.radio_remove_duplicates.setText(_translate("GroupDialog", "&Remove"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("GroupDialog", "&Columns"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_functions), _translate("GroupDialog", "&Functions"))

from ..linkedlists import CoqLinkedLists
from ..listselect import CoqListSelect


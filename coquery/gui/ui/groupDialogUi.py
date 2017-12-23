# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'groupDialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GroupDialog(object):
    def setupUi(self, GroupDialog):
        GroupDialog.setObjectName("GroupDialog")
        GroupDialog.resize(640, 480)
        self.gridLayout = QtWidgets.QGridLayout(GroupDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(GroupDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edit_label = QtWidgets.QLineEdit(GroupDialog)
        self.edit_label.setText("")
        self.edit_label.setObjectName("edit_label")
        self.gridLayout.addWidget(self.edit_label, 0, 1, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.radio_keep_duplicates = QtWidgets.QRadioButton(GroupDialog)
        self.radio_keep_duplicates.setChecked(True)
        self.radio_keep_duplicates.setObjectName("radio_keep_duplicates")
        self.verticalLayout_3.addWidget(self.radio_keep_duplicates)
        self.radio_remove_duplicates = QtWidgets.QRadioButton(GroupDialog)
        self.radio_remove_duplicates.setObjectName("radio_remove_duplicates")
        self.verticalLayout_3.addWidget(self.radio_remove_duplicates)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 2, 2, 1)
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
        self.layout_functions = QtWidgets.QVBoxLayout(self.tab_functions)
        self.layout_functions.setContentsMargins(4, 4, 4, 4)
        self.layout_functions.setObjectName("layout_functions")
        self.edit_search_functions = CoqSearchLine(self.tab_functions)
        self.edit_search_functions.setObjectName("edit_search_functions")
        self.layout_functions.addWidget(self.edit_search_functions)
        self.linked_functions = CoqLinkedLists(self.tab_functions)
        self.linked_functions.setEditTriggers(QtWidgets.QAbstractItemView.CurrentChanged)
        self.linked_functions.setAlternatingRowColors(True)
        self.linked_functions.setObjectName("linked_functions")
        self.layout_functions.addWidget(self.linked_functions)
        self.tabWidget.addTab(self.tab_functions, "")
        self.tab_filters = QtWidgets.QWidget()
        self.tab_filters.setObjectName("tab_filters")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_filters)
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_filters = CoqEditFilters(self.tab_filters)
        self.widget_filters.setObjectName("widget_filters")
        self.verticalLayout.addWidget(self.widget_filters)
        self.tabWidget.addTab(self.tab_filters, "")
        self.gridLayout.addWidget(self.tabWidget, 2, 0, 1, 3)
        self.buttonBox = QtWidgets.QDialogButtonBox(GroupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)
        self.label.setBuddy(self.edit_label)

        self.retranslateUi(GroupDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(GroupDialog.accept)
        self.buttonBox.rejected.connect(GroupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GroupDialog)
        GroupDialog.setTabOrder(self.widget_selection, self.buttonBox)

    def retranslateUi(self, GroupDialog):
        _translate = QtCore.QCoreApplication.translate
        GroupDialog.setWindowTitle(_translate("GroupDialog", "Add a group – Coquery"))
        self.label.setText(_translate("GroupDialog", "&Group name:"))
        self.radio_keep_duplicates.setText(_translate("GroupDialog", "&Keep duplicates"))
        self.radio_remove_duplicates.setText(_translate("GroupDialog", "&Remove duplicates"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("GroupDialog", "&Columns"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_functions), _translate("GroupDialog", "&Functions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_filters), _translate("GroupDialog", "Filters"))

from ..editfilters import CoqEditFilters
from ..linkedlists import CoqLinkedLists
from ..listselect import CoqListSelect
from ..searchline import CoqSearchLine

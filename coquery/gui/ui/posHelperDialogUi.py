# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'posHelperDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PosHelperDialog(object):
    def setupUi(self, PosHelperDialog):
        PosHelperDialog.setObjectName("PosHelperDialog")
        PosHelperDialog.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(PosHelperDialog)
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(PosHelperDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.combo_tagset = QtWidgets.QComboBox(PosHelperDialog)
        self.combo_tagset.setObjectName("combo_tagset")
        self.horizontalLayout.addWidget(self.combo_tagset)
        spacerItem = QtWidgets.QSpacerItem(256, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.table_mappings = QtWidgets.QTableWidget(PosHelperDialog)
        self.table_mappings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_mappings.setAlternatingRowColors(True)
        self.table_mappings.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_mappings.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_mappings.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table_mappings.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table_mappings.setShowGrid(False)
        self.table_mappings.setCornerButtonEnabled(False)
        self.table_mappings.setRowCount(0)
        self.table_mappings.setColumnCount(2)
        self.table_mappings.setObjectName("table_mappings")
        item = QtWidgets.QTableWidgetItem()
        self.table_mappings.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_mappings.setHorizontalHeaderItem(1, item)
        self.table_mappings.horizontalHeader().setStretchLastSection(True)
        self.table_mappings.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.table_mappings)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.edit_pos = QtWidgets.QLineEdit(PosHelperDialog)
        self.edit_pos.setReadOnly(True)
        self.edit_pos.setObjectName("edit_pos")
        self.horizontalLayout_2.addWidget(self.edit_pos)
        self.button_insert = QtWidgets.QPushButton(PosHelperDialog)
        self.button_insert.setObjectName("button_insert")
        self.horizontalLayout_2.addWidget(self.button_insert)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(PosHelperDialog)
        QtCore.QMetaObject.connectSlotsByName(PosHelperDialog)

    def retranslateUi(self, PosHelperDialog):
        _translate = QtCore.QCoreApplication.translate
        PosHelperDialog.setWindowTitle(_translate("PosHelperDialog", "POS tag set helper – Coquery"))
        self.label.setText(_translate("PosHelperDialog", "POS tag set:"))
        item = self.table_mappings.horizontalHeaderItem(0)
        item.setText(_translate("PosHelperDialog", "Tag"))
        item = self.table_mappings.horizontalHeaderItem(1)
        item.setText(_translate("PosHelperDialog", "Description"))
        self.button_insert.setText(_translate("PosHelperDialog", "Insert"))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'orphanagedDatabases.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_OrphanagedDatabases(object):
    def setupUi(self, OrphanagedDatabases):
        OrphanagedDatabases.setObjectName("OrphanagedDatabases")
        OrphanagedDatabases.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(OrphanagedDatabases)
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(OrphanagedDatabases)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.tableWidget = QtWidgets.QTableWidget(OrphanagedDatabases)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.tableWidget.horizontalHeader().setHighlightSections(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tableWidget)
        self.label_3 = QtWidgets.QLabel(OrphanagedDatabases)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.buttonBox = QtWidgets.QDialogButtonBox(OrphanagedDatabases)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(OrphanagedDatabases)
        self.buttonBox.accepted.connect(OrphanagedDatabases.accept)
        self.buttonBox.rejected.connect(OrphanagedDatabases.reject)
        QtCore.QMetaObject.connectSlotsByName(OrphanagedDatabases)

    def retranslateUi(self, OrphanagedDatabases):
        _translate = QtCore.QCoreApplication.translate
        OrphanagedDatabases.setWindowTitle(_translate("OrphanagedDatabases", "Orphanaged databases – Coquery"))
        self.label.setText(_translate("OrphanagedDatabases", "There are orphanaged files for the connection \'{name}\':"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("OrphanagedDatabases", "File"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("OrphanagedDatabases", "Corpus"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("OrphanagedDatabases", "Size"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("OrphanagedDatabases", "Last modified"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("OrphanagedDatabases", "Issue"))
        self.label_3.setText(_translate("OrphanagedDatabases", "<html><head/><body><p><span style=\" font-weight:600; color:#ff0000;\">Do you want to delete the selected orphanaged files?</span></p></body></html>"))



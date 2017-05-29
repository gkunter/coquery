# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'availableModules.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AvailableModules(object):
    def setupUi(self, AvailableModules):
        AvailableModules.setObjectName("AvailableModules")
        AvailableModules.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(AvailableModules)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.table_modules = QtWidgets.QTableWidget(AvailableModules)
        self.table_modules.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table_modules.setCornerButtonEnabled(True)
        self.table_modules.setRowCount(0)
        self.table_modules.setColumnCount(3)
        self.table_modules.setObjectName("table_modules")
        self.table_modules.horizontalHeader().setSortIndicatorShown(False)
        self.table_modules.horizontalHeader().setStretchLastSection(True)
        self.table_modules.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.table_modules)

        self.retranslateUi(AvailableModules)
        QtCore.QMetaObject.connectSlotsByName(AvailableModules)

    def retranslateUi(self, AvailableModules):
        _translate = QtCore.QCoreApplication.translate
        AvailableModules.setWindowTitle(_translate("AvailableModules", "Available modules – Coquery"))



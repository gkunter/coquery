# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'availableModules.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from coquery.gui.pyqt_compat import QtCore, QtGui, frameShadow, frameShape

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_AvailableModules(object):
    def setupUi(self, AvailableModules):
        AvailableModules.setObjectName(_fromUtf8("AvailableModules"))
        AvailableModules.resize(640, 480)
        self.verticalLayout = QtGui.QVBoxLayout(AvailableModules)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.table_modules = QtGui.QTableWidget(AvailableModules)
        self.table_modules.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table_modules.setRowCount(0)
        self.table_modules.setColumnCount(3)
        self.table_modules.setObjectName(_fromUtf8("table_modules"))
        self.table_modules.horizontalHeader().setSortIndicatorShown(False)
        self.table_modules.horizontalHeader().setStretchLastSection(True)
        self.table_modules.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.table_modules)

        self.retranslateUi(AvailableModules)
        QtCore.QMetaObject.connectSlotsByName(AvailableModules)

    def retranslateUi(self, AvailableModules):
        AvailableModules.setWindowTitle(_translate("AvailableModules", "Available modules – Coquery", None))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logfile.ui'
#
# Created: Mon Mar  7 10:05:51 2016
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_logfileDialog(object):
    def setupUi(self, logfileDialog):
        logfileDialog.setObjectName(_fromUtf8("logfileDialog"))
        logfileDialog.resize(640, 480)
        self.verticalLayout = QtGui.QVBoxLayout(logfileDialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(logfileDialog)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 640, 480))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.log_table = QtGui.QTableView(self.scrollAreaWidgetContents)
        self.log_table.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.log_table.setObjectName(_fromUtf8("log_table"))
        self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.log_table)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(logfileDialog)
        QtCore.QMetaObject.connectSlotsByName(logfileDialog)

    def retranslateUi(self, logfileDialog):
        logfileDialog.setWindowTitle(_translate("logfileDialog", "Log file – Coquery", None))



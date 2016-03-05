# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logfile.ui'
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

class Ui_logfileDialog(object):
    def setupUi(self, logfileDialog):
        logfileDialog.setObjectName(_fromUtf8("logfileDialog"))
        logfileDialog.resize(640, 480)
        self.verticalLayout = QtGui.QVBoxLayout(logfileDialog)
        self.verticalLayout.setContentsMargins(10, 4, 10, 4)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame = QtGui.QFrame(logfileDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.log_table = QtGui.QTableView(self.frame)
        self.log_table.setObjectName(_fromUtf8("log_table"))
        self.verticalLayout_2.addWidget(self.log_table)
        self.verticalLayout.addWidget(self.frame)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.button_okay = QtGui.QDialogButtonBox(logfileDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_okay.sizePolicy().hasHeightForWidth())
        self.button_okay.setSizePolicy(sizePolicy)
        self.button_okay.setOrientation(QtCore.Qt.Horizontal)
        self.button_okay.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.button_okay.setObjectName(_fromUtf8("button_okay"))
        self.horizontalLayout_2.addWidget(self.button_okay)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(logfileDialog)
        QtCore.QObject.connect(self.button_okay, QtCore.SIGNAL(_fromUtf8("rejected()")), logfileDialog.reject)
        QtCore.QObject.connect(self.button_okay, QtCore.SIGNAL(_fromUtf8("accepted()")), logfileDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(logfileDialog)

    def retranslateUi(self, logfileDialog):
        logfileDialog.setWindowTitle(_translate("logfileDialog", "Log file – Coquery", None))



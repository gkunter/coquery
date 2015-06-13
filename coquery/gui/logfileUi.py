# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logfile.ui'
#
# Created by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui

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
        self.verticalLayout.setContentsMargins(10, 4, 10, 4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.viewing_area = QtGui.QTextBrowser(logfileDialog)
        self.viewing_area.setFrameShadow(QtGui.QFrame.Sunken)
        self.viewing_area.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.viewing_area.setAcceptRichText(False)
        self.viewing_area.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.viewing_area.setObjectName(_fromUtf8("viewing_area"))
        self.verticalLayout.addWidget(self.viewing_area)
        self.line = QtGui.QFrame(logfileDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(30)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(logfileDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.log_file_path = QtGui.QLabel(logfileDialog)
        self.log_file_path.setObjectName(_fromUtf8("log_file_path"))
        self.horizontalLayout.addWidget(self.log_file_path)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
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
        logfileDialog.setWindowTitle(_translate("logfileDialog", "Coquery – Log file", None))
        self.viewing_area.setDocumentTitle(_translate("logfileDialog", "Log file", None))
        self.label.setText(_translate("logfileDialog", "Log file:", None))
        self.log_file_path.setText(_translate("logfileDialog", "TextLabel", None))


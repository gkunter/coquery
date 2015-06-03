# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'results.ui'
#
# Created by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_resultsDialog(object):
    def setupUi(self, resultsDialog):
        resultsDialog.setObjectName(_fromUtf8("resultsDialog"))
        resultsDialog.resize(800, 600)
        self.data_preview = QtGui.QTableView(resultsDialog)
        self.data_preview.setGeometry(QtCore.QRect(10, 10, 781, 491))
        self.data_preview.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.data_preview.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.data_preview.setAlternatingRowColors(True)
        self.data_preview.setSelectionBehavior(QtGui.QAbstractItemView.SelectColumns)
        self.data_preview.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.data_preview.setObjectName(_fromUtf8("data_preview"))
        self.label_12 = QtGui.QLabel(resultsDialog)
        self.label_12.setGeometry(QtCore.QRect(10, 518, 68, 16))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.button_browse = QtGui.QPushButton(resultsDialog)
        self.button_browse.setGeometry(QtCore.QRect(710, 514, 80, 24))
        self.button_browse.setObjectName(_fromUtf8("button_browse"))
        self.file_name = QtGui.QPlainTextEdit(resultsDialog)
        self.file_name.setEnabled(False)
        self.file_name.setGeometry(QtCore.QRect(90, 510, 611, 30))
        self.file_name.setReadOnly(True)
        self.file_name.setObjectName(_fromUtf8("file_name"))
        self.line = QtGui.QFrame(resultsDialog)
        self.line.setGeometry(QtCore.QRect(7, 540, 781, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.button_quit = QtGui.QPushButton(resultsDialog)
        self.button_quit.setGeometry(QtCore.QRect(580, 560, 95, 24))
        self.button_quit.setObjectName(_fromUtf8("button_quit"))
        self.button_restart = QtGui.QPushButton(resultsDialog)
        self.button_restart.setGeometry(QtCore.QRect(690, 560, 95, 24))
        self.button_restart.setObjectName(_fromUtf8("button_restart"))
        self.label = QtGui.QLabel(resultsDialog)
        self.label.setGeometry(QtCore.QRect(10, 563, 101, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_time = QtGui.QLabel(resultsDialog)
        self.label_time.setGeometry(QtCore.QRect(110, 563, 71, 16))
        self.label_time.setObjectName(_fromUtf8("label_time"))

        self.retranslateUi(resultsDialog)
        QtCore.QMetaObject.connectSlotsByName(resultsDialog)

    def retranslateUi(self, resultsDialog):
        resultsDialog.setWindowTitle(_translate("resultsDialog", "Dialog", None))
        self.label_12.setText(_translate("resultsDialog", "Save to file: ", None))
        self.button_browse.setText(_translate("resultsDialog", "Browse...", None))
        self.button_quit.setText(_translate("resultsDialog", "Quit", None))
        self.button_restart.setText(_translate("resultsDialog", "Start again", None))
        self.label.setText(_translate("resultsDialog", "Execution time:", None))
        self.label_time.setText(_translate("resultsDialog", "hh:mm:ss", None))


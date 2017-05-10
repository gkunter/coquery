# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'regexTester.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RegexDialog(object):
    def setupUi(self, RegexDialog):
        RegexDialog.setObjectName("RegexDialog")
        RegexDialog.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(RegexDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.edit_regex = QtWidgets.QLineEdit(RegexDialog)
        self.edit_regex.setObjectName("edit_regex")
        self.gridLayout.addWidget(self.edit_regex, 1, 0, 1, 1)
        self.edit_test_string = QtWidgets.QLineEdit(RegexDialog)
        self.edit_test_string.setObjectName("edit_test_string")
        self.gridLayout.addWidget(self.edit_test_string, 4, 0, 1, 1)
        self.label = QtWidgets.QLabel(RegexDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(RegexDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)
        self.text_cheatsheet = QtWidgets.QTextBrowser(RegexDialog)
        self.text_cheatsheet.setObjectName("text_cheatsheet")
        self.gridLayout.addWidget(self.text_cheatsheet, 6, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(RegexDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.table_groups = QtWidgets.QTableWidget(RegexDialog)
        self.table_groups.setColumnCount(1)
        self.table_groups.setObjectName("table_groups")
        self.table_groups.setRowCount(0)
        self.table_groups.horizontalHeader().setVisible(False)
        self.table_groups.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.table_groups, 1, 1, 5, 1)
        self.label_error = QtWidgets.QLabel(RegexDialog)
        self.label_error.setText("")
        self.label_error.setObjectName("label_error")
        self.gridLayout.addWidget(self.label_error, 2, 0, 1, 1)
        self.gridLayout.setColumnStretch(0, 3)
        self.gridLayout.setColumnStretch(1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        self.label.setBuddy(self.edit_regex)
        self.label_2.setBuddy(self.edit_test_string)

        self.retranslateUi(RegexDialog)
        QtCore.QMetaObject.connectSlotsByName(RegexDialog)

    def retranslateUi(self, RegexDialog):
        _translate = QtCore.QCoreApplication.translate
        RegexDialog.setWindowTitle(_translate("RegexDialog", "Regular expression tester – Coquery"))
        self.label.setText(_translate("RegexDialog", "Regular &expression"))
        self.label_3.setText(_translate("RegexDialog", "Match groups:"))
        self.text_cheatsheet.setHtml(_translate("RegexDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Oxygen-Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label_2.setText(_translate("RegexDialog", "Test string"))



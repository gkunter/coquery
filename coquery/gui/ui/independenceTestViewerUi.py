# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'independenceTestViewer.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IndependenceTestViewer(object):
    def setupUi(self, IndependenceTestViewer):
        IndependenceTestViewer.setObjectName("IndependenceTestViewer")
        IndependenceTestViewer.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(IndependenceTestViewer)
        self.verticalLayout.setContentsMargins(0, -1, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, -1, 4, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(IndependenceTestViewer)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.button_copy_text = QtWidgets.QPushButton(IndependenceTestViewer)
        self.button_copy_text.setObjectName("button_copy_text")
        self.horizontalLayout.addWidget(self.button_copy_text)
        self.button_copy_html = QtWidgets.QPushButton(IndependenceTestViewer)
        self.button_copy_html.setObjectName("button_copy_html")
        self.horizontalLayout.addWidget(self.button_copy_html)
        self.button_copy_latex = QtWidgets.QPushButton(IndependenceTestViewer)
        self.button_copy_latex.setObjectName("button_copy_latex")
        self.horizontalLayout.addWidget(self.button_copy_latex)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.textBrowser = QtWidgets.QTextBrowser(IndependenceTestViewer)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.retranslateUi(IndependenceTestViewer)
        QtCore.QMetaObject.connectSlotsByName(IndependenceTestViewer)

    def retranslateUi(self, IndependenceTestViewer):
        _translate = QtCore.QCoreApplication.translate
        IndependenceTestViewer.setWindowTitle(_translate("IndependenceTestViewer", "Tests of Independence – Coquery"))
        self.label.setText(_translate("IndependenceTestViewer", "Copy to clipboard:"))
        self.button_copy_text.setText(_translate("IndependenceTestViewer", "Plain text"))
        self.button_copy_html.setText(_translate("IndependenceTestViewer", "HTML"))
        self.button_copy_latex.setText(_translate("IndependenceTestViewer", "LaTeX"))
        self.textBrowser.setHtml(_translate("IndependenceTestViewer", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Droid Sans\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Test of independence</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Contingency table</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt; font-weight:600;\"><br /></p>\n"
"<table border=\"0\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;\" cellspacing=\"2\" cellpadding=\"0\">\n"
"<tr>\n"
"<td></td>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">{label_1}</span></p></td>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">{label_2}</span></p></td></tr>\n"
"<tr>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Token frequency</span></p></td>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">{freq_1}</span></p></td>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">{freq_2}</span></p></td></tr>\n"
"<tr>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Normalized frequency</span></p></td>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">{nfreq_1:0.3f}</span></p></td>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">{nfreq_2:0.3f}</span></p></td></tr>\n"
"<tr>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Sub-corpus size</span></p></td>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">{total_1}</span></p></td>\n"
"<td>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">{total_2}</span></p></td></tr></table>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-style:italic;\">G</span><span style=\" font-size:10pt;\">² = {g2:0.3f}, </span><span style=\" font-size:10pt; font-style:italic;\">p</span><span style=\" font-size:10pt;\"> = {p:0.3f}</span></p></body></html>"))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cite.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CiteDialog(object):
    def setupUi(self, CiteDialog):
        CiteDialog.setObjectName("CiteDialog")
        CiteDialog.resize(640, 492)
        self.verticalLayout = QtWidgets.QVBoxLayout(CiteDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(CiteDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.edit_unified = QtWidgets.QTextEdit(CiteDialog)
        self.edit_unified.setReadOnly(True)
        self.edit_unified.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.edit_unified.setObjectName("edit_unified")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.edit_unified)
        self.label_3 = QtWidgets.QLabel(CiteDialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.edit_apa = QtWidgets.QTextEdit(CiteDialog)
        self.edit_apa.setReadOnly(True)
        self.edit_apa.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.edit_apa.setObjectName("edit_apa")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.edit_apa)
        self.label_2 = QtWidgets.QLabel(CiteDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.edit_mla = QtWidgets.QTextEdit(CiteDialog)
        self.edit_mla.setReadOnly(True)
        self.edit_mla.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.edit_mla.setObjectName("edit_mla")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.edit_mla)
        self.label_5 = QtWidgets.QLabel(CiteDialog)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.edit_endnote = QtWidgets.QPlainTextEdit(CiteDialog)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.edit_endnote.setFont(font)
        self.edit_endnote.setReadOnly(True)
        self.edit_endnote.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.edit_endnote.setObjectName("edit_endnote")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.edit_endnote)
        self.label_4 = QtWidgets.QLabel(CiteDialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.edit_bibtex = QtWidgets.QPlainTextEdit(CiteDialog)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.edit_bibtex.setFont(font)
        self.edit_bibtex.setReadOnly(True)
        self.edit_bibtex.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.edit_bibtex.setObjectName("edit_bibtex")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.edit_bibtex)
        self.label_6 = QtWidgets.QLabel(CiteDialog)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.edit_ris = QtWidgets.QPlainTextEdit(CiteDialog)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.edit_ris.setFont(font)
        self.edit_ris.setReadOnly(True)
        self.edit_ris.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.edit_ris.setObjectName("edit_ris")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.edit_ris)
        self.button_copy = QtWidgets.QPushButton(CiteDialog)
        self.button_copy.setObjectName("button_copy")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.button_copy)
        self.verticalLayout.addLayout(self.formLayout)
        self.label.setBuddy(self.edit_unified)
        self.label_3.setBuddy(self.edit_apa)
        self.label_2.setBuddy(self.edit_mla)
        self.label_5.setBuddy(self.edit_endnote)
        self.label_4.setBuddy(self.edit_bibtex)
        self.label_6.setBuddy(self.edit_ris)

        self.retranslateUi(CiteDialog)
        QtCore.QMetaObject.connectSlotsByName(CiteDialog)

    def retranslateUi(self, CiteDialog):
        _translate = QtCore.QCoreApplication.translate
        CiteDialog.setWindowTitle(_translate("CiteDialog", "How to cite – Coquery"))
        self.label.setText(_translate("CiteDialog", "&Unified Stylesheet"))
        self.edit_unified.setHtml(_translate("CiteDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans UI\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Kunter, Gero. {date}. <span style=\" font-style:italic;\">Coquery: a free corpus query tool</span>. Version {version}, http://www.coquery.org. ([INSERT ACCESS DATE].)</p></body></html>"))
        self.label_3.setText(_translate("CiteDialog", "&APA"))
        self.edit_apa.setHtml(_translate("CiteDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans UI\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Kunter, G. ({date}). Coquery: a free corpus query tool (version {version}) [Computer program]. Retrieved from &lt;http://www.coquery.org&gt;</p></body></html>"))
        self.label_2.setText(_translate("CiteDialog", "&MLA"))
        self.edit_mla.setHtml(_translate("CiteDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans UI\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Kunter, Gero. <span style=\" font-style:italic;\">Coquery: a free corpus query tool</span>. Computer Software. Version {version}. {date}. Web. [INSERT ACCESS DATE]. &lt;http://www.coquery.org&gt;.</p></body></html>"))
        self.label_5.setText(_translate("CiteDialog", "E&ndnote"))
        self.edit_endnote.setPlainText(_translate("CiteDialog", "%0 Computer Program\n"
"%A Kunter, Gero\n"
"%D {date}\n"
"%T Coquery: a free corpus query tool\n"
"%U http://www.coquery.org\n"
"%Z Version {version}"))
        self.label_4.setText(_translate("CiteDialog", "BibTe&X"))
        self.edit_bibtex.setPlainText(_translate("CiteDialog", "@misc{Coquery,\n"
"  Title        = {{Coquery: a free corpus query tool}},\n"
"  Author       = {{Kunter, Gero}},\n"
"  Note         = {{Version {version}}},\n"
"  HowPublished = {{http://www.coquery.org}},\n"
"  Year         = {{{year}}}\n"
"}\n"
""))
        self.label_6.setText(_translate("CiteDialog", "&RIS"))
        self.edit_ris.setPlainText(_translate("CiteDialog", "TY  - COMP\n"
"A1  - Kunter, Gero\n"
"TI  - Coquery: a free corpus query tool\n"
"Y1  - {date}\n"
"UR  - http://www.coquery.org\n"
"N1  - Version {version}"))
        self.button_copy.setText(_translate("CiteDialog", "Copy to clipboard"))



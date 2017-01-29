# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nltkDatafiles.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NLTKDatafiles(object):
    def setupUi(self, NLTKDatafiles):
        NLTKDatafiles.setObjectName("NLTKDatafiles")
        NLTKDatafiles.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(NLTKDatafiles)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(NLTKDatafiles)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.textBrowser = QtWidgets.QTextBrowser(NLTKDatafiles)
        self.textBrowser.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.progressBar = QtWidgets.QProgressBar(NLTKDatafiles)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.label = QtWidgets.QLabel(NLTKDatafiles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.buttonBox = QtWidgets.QDialogButtonBox(NLTKDatafiles)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Open|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(NLTKDatafiles)
        self.buttonBox.accepted.connect(NLTKDatafiles.accept)
        self.buttonBox.rejected.connect(NLTKDatafiles.reject)
        QtCore.QMetaObject.connectSlotsByName(NLTKDatafiles)

    def retranslateUi(self, NLTKDatafiles):
        _translate = QtCore.QCoreApplication.translate
        NLTKDatafiles.setWindowTitle(_translate("NLTKDatafiles", "Missing NLTK data files – Coquery"))
        self.label_2.setText(_translate("NLTKDatafiles", "<html><head/><body><p><span style=\" font-weight:600;\">The tagger or tokenizer are not available.</span></p><p>Missing NLTK components:</p></body></html>"))
        self.label.setText(_translate("NLTKDatafiles", "<html><head/><body><p>Do you want to download and install the missing NLTK components?</p></body></html>"))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nltkDatafiles.ui'
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

class Ui_NLTKDatafiles(object):
    def setupUi(self, NLTKDatafiles):
        NLTKDatafiles.setObjectName(_fromUtf8("NLTKDatafiles"))
        NLTKDatafiles.resize(640, 480)
        self.verticalLayout_2 = QtGui.QVBoxLayout(NLTKDatafiles)
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(NLTKDatafiles)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout.setContentsMargins(4, 6, 8, 6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.textBrowser = QtGui.QTextBrowser(self.frame)
        self.textBrowser.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout.addWidget(self.textBrowser)
        self.label = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.progressBar = QtGui.QProgressBar(self.frame)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        self.verticalLayout_2.addWidget(self.frame)
        self.buttonBox = QtGui.QDialogButtonBox(NLTKDatafiles)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.No|QtGui.QDialogButtonBox.Open|QtGui.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(NLTKDatafiles)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NLTKDatafiles.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NLTKDatafiles.reject)
        QtCore.QMetaObject.connectSlotsByName(NLTKDatafiles)

    def retranslateUi(self, NLTKDatafiles):
        NLTKDatafiles.setWindowTitle(_translate("NLTKDatafiles", "Missing NLTK data files – Coquery", None))
        self.label_2.setText(_translate("NLTKDatafiles", "<html><head/><body><p><span style=\" font-weight:600;\">The tagger or tokenizer are not available.</span></p><p>Missing NLTK components:</p></body></html>", None))
        self.label.setText(_translate("NLTKDatafiles", "<html><head/><body><p>Do you want to download and install the missing NLTK components?</p></body></html>", None))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stopwords.ui'
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

class Ui_Stopwords(object):
    def setupUi(self, Stopwords):
        Stopwords.setObjectName(_fromUtf8("Stopwords"))
        Stopwords.resize(640, 480)
        self.verticalLayout_4 = QtGui.QVBoxLayout(Stopwords)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.groupBox = QtGui.QGroupBox(Stopwords)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.stopword_list = CoqTagBox(self.groupBox)
        self.stopword_list.setObjectName(_fromUtf8("stopword_list"))
        self.verticalLayout_3.addWidget(self.stopword_list)
        self.buttonbox_io = QtGui.QDialogButtonBox(self.groupBox)
        self.buttonbox_io.setStandardButtons(QtGui.QDialogButtonBox.Open|QtGui.QDialogButtonBox.Reset|QtGui.QDialogButtonBox.Save)
        self.buttonbox_io.setObjectName(_fromUtf8("buttonbox_io"))
        self.verticalLayout_3.addWidget(self.buttonbox_io)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.groupBox1 = QtGui.QGroupBox(Stopwords)
        self.groupBox1.setObjectName(_fromUtf8("groupBox1"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_2 = QtGui.QLabel(self.groupBox1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_3.addWidget(self.label_2)
        self.combo_language = QtGui.QComboBox(self.groupBox1)
        self.combo_language.setObjectName(_fromUtf8("combo_language"))
        self.horizontalLayout_3.addWidget(self.combo_language)
        self.button_add_list = QtGui.QPushButton(self.groupBox1)
        self.button_add_list.setObjectName(_fromUtf8("button_add_list"))
        self.horizontalLayout_3.addWidget(self.button_add_list)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_4.addWidget(self.groupBox1)
        self.buttonBox = QtGui.QDialogButtonBox(Stopwords)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_4.addWidget(self.buttonBox)
        self.label_2.setBuddy(self.combo_language)

        self.retranslateUi(Stopwords)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Stopwords.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Stopwords.reject)
        QtCore.QMetaObject.connectSlotsByName(Stopwords)

    def retranslateUi(self, Stopwords):
        Stopwords.setWindowTitle(_translate("Stopwords", " Stop words – Coquery", None))
        self.groupBox1.setTitle(_translate("Stopwords", "Preset lists", None))
        self.label_2.setText(_translate("Stopwords", "&Language:", None))
        self.button_add_list.setText(_translate("Stopwords", "A&dd preset list", None))

from ..classes import CoqTagBox


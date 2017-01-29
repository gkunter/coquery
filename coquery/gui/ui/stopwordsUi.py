# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stopwords.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Stopwords(object):
    def setupUi(self, Stopwords):
        Stopwords.setObjectName("Stopwords")
        Stopwords.resize(640, 480)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(Stopwords)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox = QtWidgets.QGroupBox(Stopwords)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.stopword_list = CoqTagBox(self.groupBox)
        self.stopword_list.setObjectName("stopword_list")
        self.verticalLayout_3.addWidget(self.stopword_list)
        self.buttonbox_io = QtWidgets.QDialogButtonBox(self.groupBox)
        self.buttonbox_io.setStandardButtons(QtWidgets.QDialogButtonBox.Open|QtWidgets.QDialogButtonBox.Reset|QtWidgets.QDialogButtonBox.Save)
        self.buttonbox_io.setObjectName("buttonbox_io")
        self.verticalLayout_3.addWidget(self.buttonbox_io)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.groupBox1 = QtWidgets.QGroupBox(Stopwords)
        self.groupBox1.setObjectName("groupBox1")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox1)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.combo_language = QtWidgets.QComboBox(self.groupBox1)
        self.combo_language.setObjectName("combo_language")
        self.horizontalLayout_3.addWidget(self.combo_language)
        self.button_add_list = QtWidgets.QPushButton(self.groupBox1)
        self.button_add_list.setObjectName("button_add_list")
        self.horizontalLayout_3.addWidget(self.button_add_list)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_4.addWidget(self.groupBox1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Stopwords)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_4.addWidget(self.buttonBox)
        self.label_2.setBuddy(self.combo_language)

        self.retranslateUi(Stopwords)
        self.buttonBox.accepted.connect(Stopwords.accept)
        self.buttonBox.rejected.connect(Stopwords.reject)
        QtCore.QMetaObject.connectSlotsByName(Stopwords)

    def retranslateUi(self, Stopwords):
        _translate = QtCore.QCoreApplication.translate
        Stopwords.setWindowTitle(_translate("Stopwords", " Stop words – Coquery"))
        self.groupBox1.setTitle(_translate("Stopwords", "Preset lists"))
        self.label_2.setText(_translate("Stopwords", "&Language:"))
        self.button_add_list.setText(_translate("Stopwords", "A&dd preset list"))

from ..classes import CoqTagBox


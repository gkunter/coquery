# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'corpus_list_entry.ui'
#
# Created: Mon Aug 24 00:07:35 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(640, 480)
        self.corpus_entry = QtGui.QFrame(Form)
        self.corpus_entry.setGeometry(QtCore.QRect(230, 190, 201, 159))
        self.corpus_entry.setObjectName(_fromUtf8("corpus_entry"))
        self.corpus_list_entry = QtGui.QVBoxLayout(self.corpus_entry)
        self.corpus_list_entry.setSpacing(0)
        self.corpus_list_entry.setObjectName(_fromUtf8("corpus_list_entry"))
        self.header_box = QtGui.QFrame(self.corpus_entry)
        self.header_box.setStyleSheet(_fromUtf8("background-color: lightgrey;"))
        self.header_box.setFrameShape(QtGui.QFrame.Box)
        self.header_box.setObjectName(_fromUtf8("header_box"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.header_box)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(10, -1, 10, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.expand_button = QtGui.QLabel(self.header_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.expand_button.sizePolicy().hasHeightForWidth())
        self.expand_button.setSizePolicy(sizePolicy)
        self.expand_button.setAlignment(QtCore.Qt.AlignCenter)
        self.expand_button.setObjectName(_fromUtf8("expand_button"))
        self.horizontalLayout.addWidget(self.expand_button)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.label_title = QtGui.QLabel(self.header_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())
        self.label_title.setSizePolicy(sizePolicy)
        self.label_title.setStyleSheet(_fromUtf8(""))
        self.label_title.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_title.setObjectName(_fromUtf8("label_title"))
        self.horizontalLayout_2.addWidget(self.label_title)
        self.corpus_list_entry.addWidget(self.header_box)
        self.description_area = QtGui.QFrame(self.corpus_entry)
        self.description_area.setStyleSheet(_fromUtf8("QFrame {color: black; background-color: white;}"))
        self.description_area.setFrameShape(QtGui.QFrame.Box)
        self.description_area.setFrameShadow(QtGui.QFrame.Raised)
        self.description_area.setObjectName(_fromUtf8("description_area"))
        self.verticalLayout = QtGui.QVBoxLayout(self.description_area)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(45, 20, 20, 20)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.corpus_description = QtGui.QLabel(self.description_area)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.corpus_description.sizePolicy().hasHeightForWidth())
        self.corpus_description.setSizePolicy(sizePolicy)
        self.corpus_description.setStyleSheet(_fromUtf8(""))
        self.corpus_description.setObjectName(_fromUtf8("corpus_description"))
        self.verticalLayout.addWidget(self.corpus_description)
        self.layout_button = QtGui.QHBoxLayout()
        self.layout_button.setObjectName(_fromUtf8("layout_button"))
        self.button_install = QtGui.QPushButton(self.description_area)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_install.sizePolicy().hasHeightForWidth())
        self.button_install.setSizePolicy(sizePolicy)
        self.button_install.setObjectName(_fromUtf8("button_install"))
        self.layout_button.addWidget(self.button_install)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layout_button.addItem(spacerItem)
        self.verticalLayout.addLayout(self.layout_button)
        self.corpus_list_entry.addWidget(self.description_area)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.expand_button.setText(_translate("Form", "+", None))
        self.label_title.setText(_translate("Form", "Corpus name", None))
        self.corpus_description.setText(_translate("Form", "<font size=\"85%\">Corpus description</font>", None))
        self.button_install.setText(_translate("Form", "Install", None))


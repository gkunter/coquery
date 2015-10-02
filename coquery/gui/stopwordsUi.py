# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stopwords.ui'
#
# Created: Thu Oct  1 23:04:56 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui, frameShadow

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
        self.verticalLayout_4.setSpacing(16)
        self.verticalLayout_4.setContentsMargins(2, 0, 2, 0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.frame = QtGui.QFrame(Stopwords)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(8, 6, 8, 6)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(16)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.stopword_list = QtGui.QListWidget(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stopword_list.sizePolicy().hasHeightForWidth())
        self.stopword_list.setSizePolicy(sizePolicy)
        self.stopword_list.setAlternatingRowColors(True)
        self.stopword_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.stopword_list.setFlow(QtGui.QListView.TopToBottom)
        self.stopword_list.setProperty("isWrapping", True)
        self.stopword_list.setResizeMode(QtGui.QListView.Adjust)
        self.stopword_list.setSpacing(10)
        self.stopword_list.setViewMode(QtGui.QListView.IconMode)
        self.stopword_list.setWordWrap(True)
        self.stopword_list.setSelectionRectVisible(True)
        self.stopword_list.setObjectName(_fromUtf8("stopword_list"))
        self.horizontalLayout.addWidget(self.stopword_list)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.button_stopword_load = QtGui.QPushButton(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_stopword_load.sizePolicy().hasHeightForWidth())
        self.button_stopword_load.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("folder"))
        self.button_stopword_load.setIcon(icon)
        self.button_stopword_load.setObjectName(_fromUtf8("button_stopword_load"))
        self.verticalLayout.addWidget(self.button_stopword_load)
        self.button_stopword_save = QtGui.QPushButton(self.frame)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-save"))
        self.button_stopword_save.setIcon(icon)
        self.button_stopword_save.setObjectName(_fromUtf8("button_stopword_save"))
        self.verticalLayout.addWidget(self.button_stopword_save)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.edit_stopword = QtGui.QLineEdit(self.frame)
        self.edit_stopword.setObjectName(_fromUtf8("edit_stopword"))
        self.verticalLayout_2.addWidget(self.edit_stopword)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.pushButton = QtGui.QPushButton(self.frame)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_4.addWidget(self.frame)
        self.buttonBox = QtGui.QDialogButtonBox(Stopwords)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_4.addWidget(self.buttonBox)

        self.retranslateUi(Stopwords)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Stopwords.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Stopwords.reject)
        QtCore.QMetaObject.connectSlotsByName(Stopwords)

    def retranslateUi(self, Stopwords):
        Stopwords.setWindowTitle(_translate("Stopwords", " Stop words – Coquery", None))
        self.label.setText(_translate("Stopwords", "Stop words:", None))
        self.button_stopword_load.setText(_translate("Stopwords", "Add words from file", None))
        self.button_stopword_load.setShortcut(_translate("Stopwords", "Alt+B", None))
        self.button_stopword_save.setText(_translate("Stopwords", "Save list", None))
        self.label_2.setText(_translate("Stopwords", "Add stop word:", None))
        self.pushButton.setText(_translate("Stopwords", "Remove", None))



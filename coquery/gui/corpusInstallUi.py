# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'corpusInstall.ui'
#
# Created: Tue Aug 25 00:12:08 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui

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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(640, 480)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scroll_area_corpus = QtGui.QScrollArea(Dialog)
        #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.scroll_area_corpus.sizePolicy().hasHeightForWidth())
        #self.scroll_area_corpus.setSizePolicy(sizePolicy)
        self.scroll_area_corpus.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.scroll_area_corpus.setWidgetResizable(True)
        #self.scroll_area_corpus.setObjectName(_fromUtf8("scroll_area_corpus"))
        self.scroll_area_content = QtGui.QWidget()
        self.scroll_area_content.setGeometry(QtCore.QRect(0, 0, 602, 192))
        self.scroll_area_content.setObjectName(_fromUtf8("scroll_area_content"))
        self.list_entry_layout = QtGui.QVBoxLayout(self.scroll_area_content)
        self.list_entry_layout.setObjectName(_fromUtf8("list_entry_layout"))
        self.scroll_area_corpus.setWidget(self.scroll_area_content)
        self.verticalLayout.addWidget(self.scroll_area_corpus)
        self.frame = QtGui.QFrame(Dialog)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setMargin(10)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_search_installer = QtGui.QPushButton(self.frame)
        self.button_search_installer.setObjectName(_fromUtf8("button_search_installer"))
        self.horizontalLayout.addWidget(self.button_search_installer)
        self.verticalLayout.addWidget(self.frame)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Fetch a corpus installer from the internet:", None))
        self.button_search_installer.setText(_translate("Dialog", "Search...", None))


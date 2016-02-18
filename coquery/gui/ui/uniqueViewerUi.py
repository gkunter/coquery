# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uniqueViewer.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui, frameShadow, frameShape

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

class Ui_UniqueViewer(object):
    def setupUi(self, UniqueViewer):
        UniqueViewer.setObjectName(_fromUtf8("UniqueViewer"))
        UniqueViewer.resize(407, 544)
        self.verticalLayout_2 = QtGui.QVBoxLayout(UniqueViewer)
        self.verticalLayout_2.setSpacing(16)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(UniqueViewer)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_inform = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_inform.sizePolicy().hasHeightForWidth())
        self.label_inform.setSizePolicy(sizePolicy)
        self.label_inform.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_inform.setObjectName(_fromUtf8("label_inform"))
        self.verticalLayout.addWidget(self.label_inform)
        self.treeWidget = QtGui.QTreeWidget(self.frame)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setItemsExpandable(False)
        self.treeWidget.setExpandsOnDoubleClick(False)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.treeWidget.header().setVisible(False)
        self.treeWidget.header().setSortIndicatorShown(False)
        self.verticalLayout.addWidget(self.treeWidget)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(16)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.progress_bar = QtGui.QProgressBar(UniqueViewer)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.horizontalLayout.addWidget(self.progress_bar)
        self.buttonBox = QtGui.QDialogButtonBox(UniqueViewer)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(UniqueViewer)
        QtCore.QMetaObject.connectSlotsByName(UniqueViewer)

    def retranslateUi(self, UniqueViewer):
        UniqueViewer.setWindowTitle(_translate("UniqueViewer", "View unique values – Coquery", None))
        self.label_inform.setText(_translate("UniqueViewer", "Retrieving values...", None))



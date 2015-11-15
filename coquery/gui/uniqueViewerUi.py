# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uniqueViewer.ui'
#
# Created: Sun Nov 15 18:22:47 2015
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

class Ui_UniqueViewer(object):
    def setupUi(self, UniqueViewer):
        UniqueViewer.setObjectName(_fromUtf8("UniqueViewer"))
        UniqueViewer.resize(407, 544)
        self.verticalLayout_2 = QtGui.QVBoxLayout(UniqueViewer)
        self.verticalLayout_2.setSpacing(16)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(UniqueViewer)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.button_details = QtGui.QPushButton(self.frame)
        self.button_details.setStyleSheet(_fromUtf8("text-align: left; padding: 4px; padding-left: 1px;"))
        self.button_details.setFlat(False)
        self.button_details.setObjectName(_fromUtf8("button_details"))
        self.verticalLayout_3.addWidget(self.button_details)
        self.frame_details = QtGui.QFrame(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_details.sizePolicy().hasHeightForWidth())
        self.frame_details.setSizePolicy(sizePolicy)
        self.frame_details.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_details.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_details.setObjectName(_fromUtf8("frame_details"))
        self.form_information = QtGui.QFormLayout(self.frame_details)
        self.form_information.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.form_information.setRowWrapPolicy(QtGui.QFormLayout.WrapLongRows)
        self.form_information.setContentsMargins(-1, 0, -1, -1)
        self.form_information.setHorizontalSpacing(10)
        self.form_information.setObjectName(_fromUtf8("form_information"))
        self.label = QtGui.QLabel(self.frame_details)
        self.label.setObjectName(_fromUtf8("label"))
        self.form_information.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.verticalLayout_3.addWidget(self.frame_details)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.label_inform = QtGui.QLabel(self.frame)
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
        self.verticalLayout.setStretch(2, 1)
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
        self.button_details.setText(_translate("UniqueViewer", "Corpus: {}, Column: {}", None))
        self.label.setText(_translate("UniqueViewer", "Number of values: {}", None))
        self.label_inform.setText(_translate("UniqueViewer", "Retrieving values...", None))



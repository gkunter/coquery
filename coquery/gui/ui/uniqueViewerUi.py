# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uniqueViewer.ui'
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

class Ui_UniqueViewer(object):
    def setupUi(self, UniqueViewer):
        UniqueViewer.setObjectName(_fromUtf8("UniqueViewer"))
        UniqueViewer.resize(407, 544)
        self.verticalLayout = QtGui.QVBoxLayout(UniqueViewer)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(4, -1, 4, -1)
        self.verticalLayout_3.setSpacing(1)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_inform = QtGui.QLabel(UniqueViewer)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_inform.sizePolicy().hasHeightForWidth())
        self.label_inform.setSizePolicy(sizePolicy)
        self.label_inform.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_inform.setObjectName(_fromUtf8("label_inform"))
        self.verticalLayout_3.addWidget(self.label_inform)
        self.progress_bar = QtGui.QProgressBar(UniqueViewer)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.verticalLayout_3.addWidget(self.progress_bar)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.tableWidget = QtGui.QTableWidget(UniqueViewer)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setCornerButtonEnabled(False)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_2.addWidget(self.tableWidget)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(UniqueViewer)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(UniqueViewer)
        QtCore.QMetaObject.connectSlotsByName(UniqueViewer)

    def retranslateUi(self, UniqueViewer):
        UniqueViewer.setWindowTitle(_translate("UniqueViewer", "View unique values – Coquery", None))
        self.label_inform.setText(_translate("UniqueViewer", "Retrieving values...", None))
        self.tableWidget.setSortingEnabled(True)



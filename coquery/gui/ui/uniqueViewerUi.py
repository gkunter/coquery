# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uniqueViewer.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_UniqueViewer(object):
    def setupUi(self, UniqueViewer):
        UniqueViewer.setObjectName("UniqueViewer")
        UniqueViewer.resize(407, 544)
        self.verticalLayout = QtWidgets.QVBoxLayout(UniqueViewer)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(4, -1, 4, -1)
        self.verticalLayout_3.setSpacing(1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_inform = QtWidgets.QLabel(UniqueViewer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_inform.sizePolicy().hasHeightForWidth())
        self.label_inform.setSizePolicy(sizePolicy)
        self.label_inform.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_inform.setObjectName("label_inform")
        self.verticalLayout_3.addWidget(self.label_inform)
        self.progress_bar = QtWidgets.QProgressBar(UniqueViewer)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout_3.addWidget(self.progress_bar)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.tableWidget = QtWidgets.QTableWidget(UniqueViewer)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setCornerButtonEnabled(False)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_2.addWidget(self.tableWidget)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(UniqueViewer)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(UniqueViewer)
        QtCore.QMetaObject.connectSlotsByName(UniqueViewer)

    def retranslateUi(self, UniqueViewer):
        _translate = QtCore.QCoreApplication.translate
        UniqueViewer.setWindowTitle(_translate("UniqueViewer", "View unique values – Coquery"))
        self.label_inform.setText(_translate("UniqueViewer", "Retrieving values..."))
        self.tableWidget.setSortingEnabled(True)



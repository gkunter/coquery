# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logfile.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_logfileDialog(object):
    def setupUi(self, logfileDialog):
        logfileDialog.setObjectName("logfileDialog")
        logfileDialog.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(logfileDialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(logfileDialog)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 640, 480))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.check_errors = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.check_errors.setObjectName("check_errors")
        self.horizontalLayout.addWidget(self.check_errors)
        self.check_warnings = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.check_warnings.setObjectName("check_warnings")
        self.horizontalLayout.addWidget(self.check_warnings)
        self.check_info = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.check_info.setObjectName("check_info")
        self.horizontalLayout.addWidget(self.check_info)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.log_table = QtWidgets.QTableView(self.scrollAreaWidgetContents)
        self.log_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.log_table.setObjectName("log_table")
        self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.log_table)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(logfileDialog)
        QtCore.QMetaObject.connectSlotsByName(logfileDialog)

    def retranslateUi(self, logfileDialog):
        _translate = QtCore.QCoreApplication.translate
        logfileDialog.setWindowTitle(_translate("logfileDialog", "Log file – Coquery"))
        self.label.setText(_translate("logfileDialog", "Select messages:"))
        self.check_errors.setText(_translate("logfileDialog", "&Errors"))
        self.check_warnings.setText(_translate("logfileDialog", "&Warnings"))
        self.check_info.setText(_translate("logfileDialog", "&Info"))



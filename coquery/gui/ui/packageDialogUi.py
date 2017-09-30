# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'packageDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PackageDialog(object):
    def setupUi(self, PackageDialog):
        PackageDialog.setObjectName("PackageDialog")
        PackageDialog.resize(640, 107)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PackageDialog.sizePolicy().hasHeightForWidth())
        PackageDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(PackageDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(PackageDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.progress_stage = QtWidgets.QProgressBar(PackageDialog)
        self.progress_stage.setProperty("value", 24)
        self.progress_stage.setObjectName("progress_stage")
        self.verticalLayout.addWidget(self.progress_stage)
        self.progress_chunk = QtWidgets.QProgressBar(PackageDialog)
        self.progress_chunk.setMinimum(0)
        self.progress_chunk.setMaximum(0)
        self.progress_chunk.setProperty("value", -1)
        self.progress_chunk.setFormat("")
        self.progress_chunk.setObjectName("progress_chunk")
        self.verticalLayout.addWidget(self.progress_chunk)

        self.retranslateUi(PackageDialog)
        QtCore.QMetaObject.connectSlotsByName(PackageDialog)

    def retranslateUi(self, PackageDialog):
        _translate = QtCore.QCoreApplication.translate
        PackageDialog.setWindowTitle(_translate("PackageDialog", "Packaging corpus – Coquery"))
        self.label.setText(_translate("PackageDialog", "Packaging corpus {} into file {}..."))



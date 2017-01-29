# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'orphanagedDatabases.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_OrphanagedDatabases(object):
    def setupUi(self, OrphanagedDatabases):
        OrphanagedDatabases.setObjectName("OrphanagedDatabases")
        OrphanagedDatabases.resize(640, 479)
        self.verticalLayout = QtWidgets.QVBoxLayout(OrphanagedDatabases)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(OrphanagedDatabases)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.listWidget = QtWidgets.QListWidget(OrphanagedDatabases)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.label_3 = QtWidgets.QLabel(OrphanagedDatabases)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(OrphanagedDatabases)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(OrphanagedDatabases)
        self.buttonBox.accepted.connect(OrphanagedDatabases.accept)
        self.buttonBox.rejected.connect(OrphanagedDatabases.reject)
        QtCore.QMetaObject.connectSlotsByName(OrphanagedDatabases)

    def retranslateUi(self, OrphanagedDatabases):
        _translate = QtCore.QCoreApplication.translate
        OrphanagedDatabases.setWindowTitle(_translate("OrphanagedDatabases", "Dialog"))
        self.label.setText(_translate("OrphanagedDatabases", "Coquery has detected the following orphanaged databases:"))
        self.label_3.setText(_translate("OrphanagedDatabases", "Do you want to delete these databases?"))



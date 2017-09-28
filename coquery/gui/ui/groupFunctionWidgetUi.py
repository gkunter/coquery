# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'groupFunctionWidget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GroupFunctionWidget(object):
    def setupUi(self, GroupFunctionWidget):
        GroupFunctionWidget.setObjectName("GroupFunctionWidget")
        GroupFunctionWidget.resize(640, 127)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GroupFunctionWidget.sizePolicy().hasHeightForWidth())
        GroupFunctionWidget.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(GroupFunctionWidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setContentsMargins(4, 4, 4, 4)
        self.gridLayout.setObjectName("gridLayout")
        self.label_title = QtWidgets.QLabel(GroupFunctionWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())
        self.label_title.setSizePolicy(sizePolicy)
        self.label_title.setWordWrap(True)
        self.label_title.setObjectName("label_title")
        self.gridLayout.addWidget(self.label_title, 0, 1, 1, 2)
        self.label_columns = QtWidgets.QLabel(GroupFunctionWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_columns.sizePolicy().hasHeightForWidth())
        self.label_columns.setSizePolicy(sizePolicy)
        self.label_columns.setObjectName("label_columns")
        self.gridLayout.addWidget(self.label_columns, 1, 1, 1, 1, QtCore.Qt.AlignTop)
        self.checkbox = QtWidgets.QCheckBox(GroupFunctionWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkbox.sizePolicy().hasHeightForWidth())
        self.checkbox.setSizePolicy(sizePolicy)
        self.checkbox.setText("")
        self.checkbox.setObjectName("checkbox")
        self.gridLayout.addWidget(self.checkbox, 0, 0, 2, 1, QtCore.Qt.AlignVCenter)
        self.button_columns = QtWidgets.QPushButton(GroupFunctionWidget)
        self.button_columns.setObjectName("button_columns")
        self.gridLayout.addWidget(self.button_columns, 1, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)

        self.retranslateUi(GroupFunctionWidget)
        QtCore.QMetaObject.connectSlotsByName(GroupFunctionWidget)

    def retranslateUi(self, GroupFunctionWidget):
        _translate = QtCore.QCoreApplication.translate
        GroupFunctionWidget.setWindowTitle(_translate("GroupFunctionWidget", "Form"))
        self.label_title.setText(_translate("GroupFunctionWidget", "Function name"))
        self.label_columns.setText(_translate("GroupFunctionWidget", "TextLabel"))
        self.button_columns.setText(_translate("GroupFunctionWidget", "Change columns..."))



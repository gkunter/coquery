# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addFunction.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FunctionsDialog(object):
    def setupUi(self, FunctionsDialog):
        FunctionsDialog.setObjectName("FunctionsDialog")
        FunctionsDialog.resize(640, 480)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(FunctionsDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_label = QtWidgets.QWidget(FunctionsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_label.sizePolicy().hasHeightForWidth())
        self.widget_label.setSizePolicy(sizePolicy)
        self.widget_label.setObjectName("widget_label")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_label)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.edit_label = QtWidgets.QLineEdit(self.widget_label)
        self.edit_label.setFocusPolicy(QtCore.Qt.NoFocus)
        self.edit_label.setText("")
        self.edit_label.setReadOnly(True)
        self.edit_label.setObjectName("edit_label")
        self.horizontalLayout_3.addWidget(self.edit_label)
        self.verticalLayout_2.addWidget(self.widget_label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.list_classes = QtWidgets.QListWidget(FunctionsDialog)
        self.list_classes.setObjectName("list_classes")
        self.horizontalLayout.addWidget(self.list_classes)
        self.list_functions = FunctionList(FunctionsDialog)
        self.list_functions.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_functions.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_functions.setObjectName("list_functions")
        self.horizontalLayout.addWidget(self.list_functions)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.widget = QtWidgets.QWidget(FunctionsDialog)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2, 0, QtCore.Qt.AlignVCenter)
        self.label_selected_columns = CoqClickableLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_selected_columns.sizePolicy().hasHeightForWidth())
        self.label_selected_columns.setSizePolicy(sizePolicy)
        self.label_selected_columns.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_selected_columns.setText("")
        self.label_selected_columns.setWordWrap(True)
        self.label_selected_columns.setObjectName("label_selected_columns")
        self.horizontalLayout_2.addWidget(self.label_selected_columns)
        self.button_select_columns = QtWidgets.QPushButton(self.widget)
        self.button_select_columns.setObjectName("button_select_columns")
        self.horizontalLayout_2.addWidget(self.button_select_columns, 0, QtCore.Qt.AlignVCenter)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.addWidget(self.widget)
        self.buttonBox = QtWidgets.QDialogButtonBox(FunctionsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout_2.setStretch(1, 4)

        self.retranslateUi(FunctionsDialog)
        self.buttonBox.accepted.connect(FunctionsDialog.accept)
        self.buttonBox.rejected.connect(FunctionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FunctionsDialog)

    def retranslateUi(self, FunctionsDialog):
        _translate = QtCore.QCoreApplication.translate
        FunctionsDialog.setWindowTitle(_translate("FunctionsDialog", "Add a function – Coquery"))
        self.label_2.setText(_translate("FunctionsDialog", "Selected columns:"))
        self.button_select_columns.setText(_translate("FunctionsDialog", "&Change columns..."))

from ..addfunction import FunctionList
from ..classes import CoqClickableLabel


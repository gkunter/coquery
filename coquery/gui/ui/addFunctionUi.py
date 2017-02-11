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
        self.label = QtWidgets.QLabel(self.widget_label)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.edit_label = QtWidgets.QLineEdit(self.widget_label)
        self.edit_label.setText("")
        self.edit_label.setObjectName("edit_label")
        self.horizontalLayout_3.addWidget(self.edit_label)
        self.verticalLayout_2.addWidget(self.widget_label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.list_classes = QtWidgets.QListWidget(FunctionsDialog)
        self.list_classes.setObjectName("list_classes")
        self.horizontalLayout.addWidget(self.list_classes)
        self.list_functions = QtWidgets.QListWidget(FunctionsDialog)
        self.list_functions.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.list_functions.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_functions.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_functions.setWordWrap(True)
        self.list_functions.setObjectName("list_functions")
        self.horizontalLayout.addWidget(self.list_functions)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.parameter_box = QtWidgets.QWidget(FunctionsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.parameter_box.sizePolicy().hasHeightForWidth())
        self.parameter_box.setSizePolicy(sizePolicy)
        self.parameter_box.setObjectName("parameter_box")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.parameter_box)
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.parameter_box)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.edit_function_value = QtWidgets.QLineEdit(self.parameter_box)
        self.edit_function_value.setObjectName("edit_function_value")
        self.horizontalLayout_2.addWidget(self.edit_function_value)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.setStretch(1, 2)
        self.horizontalLayout_2.setStretch(2, 1)
        self.verticalLayout_2.addWidget(self.parameter_box)
        self.widget_selection = CoqListSelect(FunctionsDialog)
        self.widget_selection.setObjectName("widget_selection")
        self.verticalLayout_2.addWidget(self.widget_selection)
        self.box_combine = QtWidgets.QWidget(FunctionsDialog)
        self.box_combine.setObjectName("box_combine")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.box_combine)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.box_combine)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.combo_combine = QtWidgets.QComboBox(self.box_combine)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.combo_combine.sizePolicy().hasHeightForWidth())
        self.combo_combine.setSizePolicy(sizePolicy)
        self.combo_combine.setObjectName("combo_combine")
        self.horizontalLayout_4.addWidget(self.combo_combine)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.box_combine)
        self.buttonBox = QtWidgets.QDialogButtonBox(FunctionsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(3, 1)
        self.label.setBuddy(self.edit_label)
        self.label_5.setBuddy(self.edit_function_value)
        self.label_4.setBuddy(self.combo_combine)

        self.retranslateUi(FunctionsDialog)
        self.list_functions.setCurrentRow(-1)
        self.buttonBox.accepted.connect(FunctionsDialog.accept)
        self.buttonBox.rejected.connect(FunctionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FunctionsDialog)

    def retranslateUi(self, FunctionsDialog):
        _translate = QtCore.QCoreApplication.translate
        FunctionsDialog.setWindowTitle(_translate("FunctionsDialog", "Add a function – Coquery"))
        self.label.setText(_translate("FunctionsDialog", "&Label:"))
        self.list_functions.setSortingEnabled(True)
        self.label_5.setText(_translate("FunctionsDialog", "Ar&gument:"))
        self.edit_function_value.setPlaceholderText(_translate("FunctionsDialog", "(no value specified)"))
        self.label_4.setText(_translate("FunctionsDialog", "&Combine values:"))

from ..listselect import CoqListSelect


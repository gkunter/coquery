# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addFunction.ui'
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

class Ui_FunctionsDialog(object):
    def setupUi(self, FunctionsDialog):
        FunctionsDialog.setObjectName(_fromUtf8("FunctionsDialog"))
        FunctionsDialog.resize(640, 480)
        self.verticalLayout_2 = QtGui.QVBoxLayout(FunctionsDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.widget_label = QtGui.QWidget(FunctionsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_label.sizePolicy().hasHeightForWidth())
        self.widget_label.setSizePolicy(sizePolicy)
        self.widget_label.setObjectName(_fromUtf8("widget_label"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget_label)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.widget_label)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.edit_label = QtGui.QLineEdit(self.widget_label)
        self.edit_label.setText(_fromUtf8(""))
        self.edit_label.setObjectName(_fromUtf8("edit_label"))
        self.horizontalLayout_3.addWidget(self.edit_label)
        self.verticalLayout_2.addWidget(self.widget_label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.list_classes = QtGui.QListWidget(FunctionsDialog)
        self.list_classes.setObjectName(_fromUtf8("list_classes"))
        self.horizontalLayout.addWidget(self.list_classes)
        self.list_functions = QtGui.QListWidget(FunctionsDialog)
        self.list_functions.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.list_functions.setWordWrap(True)
        self.list_functions.setObjectName(_fromUtf8("list_functions"))
        self.horizontalLayout.addWidget(self.list_functions)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.parameter_box = QtGui.QWidget(FunctionsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.parameter_box.sizePolicy().hasHeightForWidth())
        self.parameter_box.setSizePolicy(sizePolicy)
        self.parameter_box.setObjectName(_fromUtf8("parameter_box"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.parameter_box)
        self.horizontalLayout_2.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_5 = QtGui.QLabel(self.parameter_box)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_2.addWidget(self.label_5)
        self.edit_function_value = QtGui.QLineEdit(self.parameter_box)
        self.edit_function_value.setObjectName(_fromUtf8("edit_function_value"))
        self.horizontalLayout_2.addWidget(self.edit_function_value)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.setStretch(1, 2)
        self.horizontalLayout_2.setStretch(2, 1)
        self.verticalLayout_2.addWidget(self.parameter_box)
        self.widget_selection = CoqListSelect(FunctionsDialog)
        self.widget_selection.setObjectName(_fromUtf8("widget_selection"))
        self.verticalLayout_2.addWidget(self.widget_selection)
        self.box_combine = QtGui.QWidget(FunctionsDialog)
        self.box_combine.setObjectName(_fromUtf8("box_combine"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.box_combine)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_4 = QtGui.QLabel(self.box_combine)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_4.addWidget(self.label_4)
        self.combo_combine = QtGui.QComboBox(self.box_combine)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.combo_combine.sizePolicy().hasHeightForWidth())
        self.combo_combine.setSizePolicy(sizePolicy)
        self.combo_combine.setObjectName(_fromUtf8("combo_combine"))
        self.horizontalLayout_4.addWidget(self.combo_combine)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.box_combine)
        self.buttonBox = QtGui.QDialogButtonBox(FunctionsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(3, 1)
        self.label.setBuddy(self.edit_label)
        self.label_5.setBuddy(self.edit_function_value)
        self.label_4.setBuddy(self.combo_combine)

        self.retranslateUi(FunctionsDialog)
        self.list_functions.setCurrentRow(-1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FunctionsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FunctionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FunctionsDialog)

    def retranslateUi(self, FunctionsDialog):
        FunctionsDialog.setWindowTitle(_translate("FunctionsDialog", "Add a function – Coquery", None))
        self.label.setText(_translate("FunctionsDialog", "&Label:", None))
        self.list_functions.setSortingEnabled(True)
        self.label_5.setText(_translate("FunctionsDialog", "Ar&gument:", None))
        self.edit_function_value.setPlaceholderText(_translate("FunctionsDialog", "(no value specified)", None))
        self.label_4.setText(_translate("FunctionsDialog", "&Combine values:", None))

from ..listselect import CoqListSelect


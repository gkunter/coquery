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
        FunctionsDialog.resize(662, 480)
        self.verticalLayout_2 = QtGui.QVBoxLayout(FunctionsDialog)
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_2.setSpacing(16)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(FunctionsDialog)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout.setContentsMargins(8, 6, 8, 6)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_description = QtGui.QLabel(self.frame)
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.verticalLayout.addWidget(self.label_description)
        self.widget_label = QtGui.QWidget(self.frame)
        self.widget_label.setObjectName(_fromUtf8("widget_label"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget_label)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.widget_label)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.edit_label = QtGui.QLineEdit(self.widget_label)
        self.edit_label.setObjectName(_fromUtf8("edit_label"))
        self.horizontalLayout_3.addWidget(self.edit_label)
        self.verticalLayout.addWidget(self.widget_label)
        self.list_functions = QtGui.QListWidget(self.frame)
        self.list_functions.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.list_functions.setWordWrap(True)
        self.list_functions.setObjectName(_fromUtf8("list_functions"))
        self.verticalLayout.addWidget(self.list_functions)
        self.parameter_box = QtGui.QWidget(self.frame)
        self.parameter_box.setObjectName(_fromUtf8("parameter_box"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.parameter_box)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_5 = QtGui.QLabel(self.parameter_box)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_2.addWidget(self.label_5)
        self.edit_function_value = QtGui.QLineEdit(self.parameter_box)
        self.edit_function_value.setObjectName(_fromUtf8("edit_function_value"))
        self.horizontalLayout_2.addWidget(self.edit_function_value)
        self.verticalLayout.addWidget(self.parameter_box)
        self.box_combine = QtGui.QWidget(self.frame)
        self.box_combine.setObjectName(_fromUtf8("box_combine"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.box_combine)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_4 = QtGui.QLabel(self.box_combine)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.label_4)
        self.combo_combine = QtGui.QComboBox(self.box_combine)
        self.combo_combine.setObjectName(_fromUtf8("combo_combine"))
        self.horizontalLayout.addWidget(self.combo_combine)
        self.label_remark = QtGui.QLabel(self.box_combine)
        self.label_remark.setObjectName(_fromUtf8("label_remark"))
        self.horizontalLayout.addWidget(self.label_remark)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.box_combine)
        self.verticalLayout_2.addWidget(self.frame)
        self.buttonBox = QtGui.QDialogButtonBox(FunctionsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(FunctionsDialog)
        self.list_functions.setCurrentRow(-1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FunctionsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FunctionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FunctionsDialog)

    def retranslateUi(self, FunctionsDialog):
        FunctionsDialog.setWindowTitle(_translate("FunctionsDialog", "Add a function – Coquery", None))
        self.label_description.setText(_translate("FunctionsDialog", "<html><head/><body><p>Add a function to <span style=\" font-weight:600;\">{}</span>:</p></body></html>", None))
        self.label.setText(_translate("FunctionsDialog", "Label:", None))
        self.list_functions.setSortingEnabled(True)
        self.label_5.setText(_translate("FunctionsDialog", "Parameter", None))
        self.edit_function_value.setPlaceholderText(_translate("FunctionsDialog", "(no value specified)", None))
        self.label_4.setText(_translate("FunctionsDialog", "Combine values:", None))
        self.label_remark.setText(_translate("FunctionsDialog", "(not needed for one column)", None))



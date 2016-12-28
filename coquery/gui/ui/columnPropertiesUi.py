# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'columnProperties.ui'
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

class Ui_ColumnProperties(object):
    def setupUi(self, ColumnProperties):
        ColumnProperties.setObjectName(_fromUtf8("ColumnProperties"))
        ColumnProperties.resize(640, 480)
        self.verticalLayout = QtGui.QVBoxLayout(ColumnProperties)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_3 = QtGui.QGroupBox(ColumnProperties)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.widget_selection = CoqListSelect(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_selection.sizePolicy().hasHeightForWidth())
        self.widget_selection.setSizePolicy(sizePolicy)
        self.widget_selection.setObjectName(_fromUtf8("widget_selection"))
        self.verticalLayout_2.addWidget(self.widget_selection)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox = QtGui.QGroupBox(ColumnProperties)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_example = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_example.sizePolicy().hasHeightForWidth())
        self.label_example.setSizePolicy(sizePolicy)
        self.label_example.setFrameShape(frameShape)
        self.label_example.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_example.setObjectName(_fromUtf8("label_example"))
        self.horizontalLayout.addWidget(self.label_example)
        self.button_change_color = QtGui.QPushButton(self.groupBox)
        self.button_change_color.setObjectName(_fromUtf8("button_change_color"))
        self.horizontalLayout.addWidget(self.button_change_color)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        self.edit_column_name = QtGui.QLineEdit(self.groupBox)
        self.edit_column_name.setText(_fromUtf8(""))
        self.edit_column_name.setObjectName(_fromUtf8("edit_column_name"))
        self.gridLayout.addWidget(self.edit_column_name, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.buttonbox_label = QtGui.QDialogButtonBox(self.groupBox)
        self.buttonbox_label.setOrientation(QtCore.Qt.Vertical)
        self.buttonbox_label.setStandardButtons(QtGui.QDialogButtonBox.RestoreDefaults)
        self.buttonbox_label.setCenterButtons(False)
        self.buttonbox_label.setObjectName(_fromUtf8("buttonbox_label"))
        self.gridLayout.addWidget(self.buttonbox_label, 1, 2, 1, 1)
        self.buttonbox_color = QtGui.QDialogButtonBox(self.groupBox)
        self.buttonbox_color.setOrientation(QtCore.Qt.Vertical)
        self.buttonbox_color.setStandardButtons(QtGui.QDialogButtonBox.RestoreDefaults)
        self.buttonbox_color.setObjectName(_fromUtf8("buttonbox_color"))
        self.gridLayout.addWidget(self.buttonbox_color, 2, 2, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(ColumnProperties)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.table_substitutions = QtGui.QTableWidget(self.groupBox_2)
        self.table_substitutions.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.table_substitutions.setObjectName(_fromUtf8("table_substitutions"))
        self.table_substitutions.setColumnCount(2)
        self.table_substitutions.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.table_substitutions.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table_substitutions.setHorizontalHeaderItem(1, item)
        self.gridLayout_2.addWidget(self.table_substitutions, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtGui.QDialogButtonBox(ColumnProperties)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(0, 1)
        self.label_2.setBuddy(self.button_change_color)
        self.label.setBuddy(self.edit_column_name)

        self.retranslateUi(ColumnProperties)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ColumnProperties.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ColumnProperties.reject)
        QtCore.QMetaObject.connectSlotsByName(ColumnProperties)

    def retranslateUi(self, ColumnProperties):
        ColumnProperties.setWindowTitle(_translate("ColumnProperties", "Column properties – Coquery", None))
        self.groupBox_3.setTitle(_translate("ColumnProperties", "Visibility", None))
        self.groupBox.setTitle(_translate("ColumnProperties", "Appearance", None))
        self.label_example.setText(_translate("ColumnProperties", "Example", None))
        self.button_change_color.setText(_translate("ColumnProperties", "Change", None))
        self.label_2.setText(_translate("ColumnProperties", "&Color:", None))
        self.label.setText(_translate("ColumnProperties", "Column &label:", None))
        self.groupBox_2.setTitle(_translate("ColumnProperties", "Value substitution", None))
        item = self.table_substitutions.horizontalHeaderItem(0)
        item.setText(_translate("ColumnProperties", "Value", None))
        item = self.table_substitutions.horizontalHeaderItem(1)
        item.setText(_translate("ColumnProperties", "Substitute", None))

from ..listselect import CoqListSelect


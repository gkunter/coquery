# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'columnProperties.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ColumnProperties(object):
    def setupUi(self, ColumnProperties):
        ColumnProperties.setObjectName("ColumnProperties")
        ColumnProperties.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(ColumnProperties)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_3 = QtWidgets.QGroupBox(ColumnProperties)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_selection = CoqListSelect(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_selection.sizePolicy().hasHeightForWidth())
        self.widget_selection.setSizePolicy(sizePolicy)
        self.widget_selection.setObjectName("widget_selection")
        self.verticalLayout_2.addWidget(self.widget_selection)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.tab_widget = QtWidgets.QTabWidget(ColumnProperties)
        self.tab_widget.setElideMode(QtCore.Qt.ElideMiddle)
        self.tab_widget.setObjectName("tab_widget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_3.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.buttonbox_color = QtWidgets.QDialogButtonBox(self.tab)
        self.buttonbox_color.setOrientation(QtCore.Qt.Vertical)
        self.buttonbox_color.setStandardButtons(QtWidgets.QDialogButtonBox.Reset)
        self.buttonbox_color.setObjectName("buttonbox_color")
        self.gridLayout_3.addWidget(self.buttonbox_color, 1, 2, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_example = CoqClickableLabel(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_example.sizePolicy().hasHeightForWidth())
        self.label_example.setSizePolicy(sizePolicy)
        self.label_example.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_example.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.label_example.setObjectName("label_example")
        self.horizontalLayout.addWidget(self.label_example)
        self.button_change_color = QtWidgets.QPushButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_change_color.sizePolicy().hasHeightForWidth())
        self.button_change_color.setSizePolicy(sizePolicy)
        self.button_change_color.setObjectName("button_change_color")
        self.horizontalLayout.addWidget(self.button_change_color)
        self.gridLayout_3.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.edit_column_name = QtWidgets.QLineEdit(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_column_name.sizePolicy().hasHeightForWidth())
        self.edit_column_name.setSizePolicy(sizePolicy)
        self.edit_column_name.setText("")
        self.edit_column_name.setObjectName("edit_column_name")
        self.gridLayout_3.addWidget(self.edit_column_name, 0, 1, 1, 1)
        self.buttonbox_label = QtWidgets.QDialogButtonBox(self.tab)
        self.buttonbox_label.setOrientation(QtCore.Qt.Vertical)
        self.buttonbox_label.setStandardButtons(QtWidgets.QDialogButtonBox.Reset)
        self.buttonbox_label.setCenterButtons(False)
        self.buttonbox_label.setObjectName("buttonbox_label")
        self.gridLayout_3.addWidget(self.buttonbox_label, 0, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 2, 0, 1, 1)
        self.gridLayout_3.setColumnStretch(1, 1)
        self.gridLayout_3.setRowStretch(2, 1)
        self.tab_widget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.table_substitutions = QtWidgets.QTableWidget(self.tab_2)
        self.table_substitutions.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.table_substitutions.setObjectName("table_substitutions")
        self.table_substitutions.setColumnCount(2)
        self.table_substitutions.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table_substitutions.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_substitutions.setHorizontalHeaderItem(1, item)
        self.table_substitutions.horizontalHeader().setDefaultSectionSize(200)
        self.table_substitutions.horizontalHeader().setMinimumSectionSize(100)
        self.table_substitutions.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_3.addWidget(self.table_substitutions)
        self.buttonbox_substitution = QtWidgets.QDialogButtonBox(self.tab_2)
        self.buttonbox_substitution.setStandardButtons(QtWidgets.QDialogButtonBox.Reset)
        self.buttonbox_substitution.setObjectName("buttonbox_substitution")
        self.verticalLayout_3.addWidget(self.buttonbox_substitution)
        self.tab_widget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tab_widget)
        self.buttonBox = QtWidgets.QDialogButtonBox(ColumnProperties)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(0, 1)
        self.label_2.setBuddy(self.button_change_color)
        self.label.setBuddy(self.edit_column_name)

        self.retranslateUi(ColumnProperties)
        self.tab_widget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(ColumnProperties.accept)
        self.buttonBox.rejected.connect(ColumnProperties.reject)
        QtCore.QMetaObject.connectSlotsByName(ColumnProperties)
        ColumnProperties.setTabOrder(self.widget_selection, self.button_change_color)
        ColumnProperties.setTabOrder(self.button_change_color, self.buttonBox)

    def retranslateUi(self, ColumnProperties):
        _translate = QtCore.QCoreApplication.translate
        ColumnProperties.setWindowTitle(_translate("ColumnProperties", "Column properties – Coquery"))
        self.groupBox_3.setTitle(_translate("ColumnProperties", "&Columns"))
        self.label_example.setText(_translate("ColumnProperties", "Example"))
        self.button_change_color.setText(_translate("ColumnProperties", "Chan&ge"))
        self.label_2.setText(_translate("ColumnProperties", "C&olor:"))
        self.label.setText(_translate("ColumnProperties", "&Label:"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab), _translate("ColumnProperties", "&Appearance"))
        item = self.table_substitutions.horizontalHeaderItem(0)
        item.setText(_translate("ColumnProperties", "Value"))
        item = self.table_substitutions.horizontalHeaderItem(1)
        item.setText(_translate("ColumnProperties", "Substitute"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_2), _translate("ColumnProperties", "Value &substitution"))

from ..classes import CoqClickableLabel
from ..listselect import CoqListSelect


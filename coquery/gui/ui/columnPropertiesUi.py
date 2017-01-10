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
        self.tab_widget = QtGui.QTabWidget(ColumnProperties)
        self.tab_widget.setElideMode(QtCore.Qt.ElideMiddle)
        self.tab_widget.setObjectName(_fromUtf8("tab_widget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.buttonbox_color = QtGui.QDialogButtonBox(self.tab)
        self.buttonbox_color.setOrientation(QtCore.Qt.Vertical)
        self.buttonbox_color.setStandardButtons(QtGui.QDialogButtonBox.Reset)
        self.buttonbox_color.setObjectName(_fromUtf8("buttonbox_color"))
        self.gridLayout_3.addWidget(self.buttonbox_color, 1, 2, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_example = CoqClickableLabel(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_example.sizePolicy().hasHeightForWidth())
        self.label_example.setSizePolicy(sizePolicy)
        self.label_example.setFrameShape(frameShape)
        self.label_example.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_example.setObjectName(_fromUtf8("label_example"))
        self.horizontalLayout.addWidget(self.label_example)
        self.button_change_color = QtGui.QPushButton(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_change_color.sizePolicy().hasHeightForWidth())
        self.button_change_color.setSizePolicy(sizePolicy)
        self.button_change_color.setObjectName(_fromUtf8("button_change_color"))
        self.horizontalLayout.addWidget(self.button_change_color)
        self.gridLayout_3.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.edit_column_name = QtGui.QLineEdit(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_column_name.sizePolicy().hasHeightForWidth())
        self.edit_column_name.setSizePolicy(sizePolicy)
        self.edit_column_name.setText(_fromUtf8(""))
        self.edit_column_name.setObjectName(_fromUtf8("edit_column_name"))
        self.gridLayout_3.addWidget(self.edit_column_name, 0, 1, 1, 1)
        self.buttonbox_label = QtGui.QDialogButtonBox(self.tab)
        self.buttonbox_label.setOrientation(QtCore.Qt.Vertical)
        self.buttonbox_label.setStandardButtons(QtGui.QDialogButtonBox.Reset)
        self.buttonbox_label.setCenterButtons(False)
        self.buttonbox_label.setObjectName(_fromUtf8("buttonbox_label"))
        self.gridLayout_3.addWidget(self.buttonbox_label, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 2, 0, 1, 1)
        self.gridLayout_3.setColumnStretch(1, 1)
        self.gridLayout_3.setRowStretch(2, 1)
        self.tab_widget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.table_substitutions = QtGui.QTableWidget(self.tab_2)
        self.table_substitutions.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.table_substitutions.setObjectName(_fromUtf8("table_substitutions"))
        self.table_substitutions.setColumnCount(2)
        self.table_substitutions.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.table_substitutions.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table_substitutions.setHorizontalHeaderItem(1, item)
        self.table_substitutions.horizontalHeader().setDefaultSectionSize(200)
        self.table_substitutions.horizontalHeader().setMinimumSectionSize(100)
        self.table_substitutions.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_3.addWidget(self.table_substitutions)
        self.buttonbox_substitution = QtGui.QDialogButtonBox(self.tab_2)
        self.buttonbox_substitution.setStandardButtons(QtGui.QDialogButtonBox.Reset)
        self.buttonbox_substitution.setObjectName(_fromUtf8("buttonbox_substitution"))
        self.verticalLayout_3.addWidget(self.buttonbox_substitution)
        self.tab_widget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tab_widget)
        self.buttonBox = QtGui.QDialogButtonBox(ColumnProperties)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(0, 1)
        self.label_2.setBuddy(self.button_change_color)
        self.label.setBuddy(self.edit_column_name)

        self.retranslateUi(ColumnProperties)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ColumnProperties.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ColumnProperties.reject)
        QtCore.QMetaObject.connectSlotsByName(ColumnProperties)
        ColumnProperties.setTabOrder(self.widget_selection, self.button_change_color)
        ColumnProperties.setTabOrder(self.button_change_color, self.buttonBox)

    def retranslateUi(self, ColumnProperties):
        ColumnProperties.setWindowTitle(_translate("ColumnProperties", "Column properties – Coquery", None))
        self.groupBox_3.setTitle(_translate("ColumnProperties", "&Columns", None))
        self.label_example.setText(_translate("ColumnProperties", "Example", None))
        self.button_change_color.setText(_translate("ColumnProperties", "Chan&ge", None))
        self.label_2.setText(_translate("ColumnProperties", "C&olor:", None))
        self.label.setText(_translate("ColumnProperties", "&Label:", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab), _translate("ColumnProperties", "&Appearance", None))
        item = self.table_substitutions.horizontalHeaderItem(0)
        item.setText(_translate("ColumnProperties", "Value", None))
        item = self.table_substitutions.horizontalHeaderItem(1)
        item.setText(_translate("ColumnProperties", "Substitute", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_2), _translate("ColumnProperties", "Value &substitution", None))

from ..classes import CoqClickableLabel
from ..listselect import CoqListSelect


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coqListSelect.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CoqListSelect(object):
    def setupUi(self, CoqListSelect):
        CoqListSelect.setObjectName("CoqListSelect")
        CoqListSelect.resize(652, 230)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(CoqListSelect)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.layout = QtWidgets.QGridLayout()
        self.layout.setObjectName("layout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.button_add = QtWidgets.QToolButton(CoqListSelect)
        self.button_add.setText("")
        self.button_add.setObjectName("button_add")
        self.horizontalLayout_6.addWidget(self.button_add)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.button_up = QtWidgets.QToolButton(CoqListSelect)
        self.button_up.setText("")
        self.button_up.setObjectName("button_up")
        self.verticalLayout.addWidget(self.button_up)
        self.button_down = QtWidgets.QToolButton(CoqListSelect)
        self.button_down.setText("")
        self.button_down.setObjectName("button_down")
        self.verticalLayout.addWidget(self.button_down)
        self.horizontalLayout_6.addLayout(self.verticalLayout)
        self.button_remove = QtWidgets.QToolButton(CoqListSelect)
        self.button_remove.setText("")
        self.button_remove.setObjectName("button_remove")
        self.horizontalLayout_6.addWidget(self.button_remove, 0, QtCore.Qt.AlignVCenter)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.layout.addLayout(self.verticalLayout_5, 1, 1, 1, 1)
        self.list_available = QtWidgets.QListWidget(CoqListSelect)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_available.sizePolicy().hasHeightForWidth())
        self.list_available.setSizePolicy(sizePolicy)
        self.list_available.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.list_available.setObjectName("list_available")
        self.layout.addWidget(self.list_available, 1, 2, 1, 1)
        self.label_available = QtWidgets.QLabel(CoqListSelect)
        self.label_available.setObjectName("label_available")
        self.layout.addWidget(self.label_available, 0, 2, 1, 1)
        self.label_select_list = QtWidgets.QLabel(CoqListSelect)
        self.label_select_list.setObjectName("label_select_list")
        self.layout.addWidget(self.label_select_list, 0, 0, 1, 1)
        self.list_selected = QtWidgets.QListWidget(CoqListSelect)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_selected.sizePolicy().hasHeightForWidth())
        self.list_selected.setSizePolicy(sizePolicy)
        self.list_selected.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.list_selected.setObjectName("list_selected")
        self.layout.addWidget(self.list_selected, 1, 0, 1, 1)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(2, 1)
        self.verticalLayout_2.addLayout(self.layout)
        self.label_available.setBuddy(self.list_available)
        self.label_select_list.setBuddy(self.list_selected)

        self.retranslateUi(CoqListSelect)
        QtCore.QMetaObject.connectSlotsByName(CoqListSelect)
        CoqListSelect.setTabOrder(self.list_selected, self.list_available)
        CoqListSelect.setTabOrder(self.list_available, self.button_up)
        CoqListSelect.setTabOrder(self.button_up, self.button_add)
        CoqListSelect.setTabOrder(self.button_add, self.button_remove)
        CoqListSelect.setTabOrder(self.button_remove, self.button_down)

    def retranslateUi(self, CoqListSelect):
        _translate = QtCore.QCoreApplication.translate
        CoqListSelect.setWindowTitle(_translate("CoqListSelect", "Form"))
        self.label_available.setText(_translate("CoqListSelect", "&Available:"))
        self.label_select_list.setText(_translate("CoqListSelect", "Se&lected:"))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'groupDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GroupDialog(object):
    def setupUi(self, GroupDialog):
        GroupDialog.setObjectName("GroupDialog")
        GroupDialog.resize(640, 480)
        self.verticalLayout = QtWidgets.QGridLayout(GroupDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(GroupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox, 3, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(GroupDialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(GroupDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label, 0, 0, 1, 1)
        self.widget_selection = CoqListSelect(GroupDialog)
        self.widget_selection.setObjectName("widget_selection")
        self.verticalLayout.addWidget(self.widget_selection, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(GroupDialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.edit_label = QtWidgets.QLineEdit(GroupDialog)
        self.edit_label.setText("")
        self.edit_label.setObjectName("edit_label")
        self.verticalLayout.addWidget(self.edit_label, 0, 1, 1, 1)
        self.scroll_area = QtWidgets.QScrollArea(GroupDialog)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_content.setGeometry(QtCore.QRect(0, 0, 535, 265))
        self.scroll_content.setObjectName("scroll_content")
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)
        self.scroll_layout.setObjectName("scroll_layout")
        self.scroll_area.setWidget(self.scroll_content)
        self.verticalLayout.addWidget(self.scroll_area, 2, 1, 1, 1)
        self.verticalLayout.setRowStretch(1, 1)
        self.verticalLayout.setRowStretch(2, 2)
        self.label_3.setBuddy(self.scroll_content)
        self.label.setBuddy(self.edit_label)
        self.label_2.setBuddy(self.widget_selection)

        self.retranslateUi(GroupDialog)
        self.buttonBox.accepted.connect(GroupDialog.accept)
        self.buttonBox.rejected.connect(GroupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GroupDialog)

    def retranslateUi(self, GroupDialog):
        _translate = QtCore.QCoreApplication.translate
        GroupDialog.setWindowTitle(_translate("GroupDialog", "Add a group – Coquery"))
        self.label_3.setText(_translate("GroupDialog", "&Functions:"))
        self.label.setText(_translate("GroupDialog", "&Group name:"))
        self.label_2.setText(_translate("GroupDialog", "&Columns:"))

from ..listselect import CoqListSelect


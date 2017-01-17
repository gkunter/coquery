# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coqListSelect.ui'
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

class Ui_CoqListSelect(object):
    def setupUi(self, CoqListSelect):
        CoqListSelect.setObjectName(_fromUtf8("CoqListSelect"))
        CoqListSelect.resize(652, 230)
        self.verticalLayout_2 = QtGui.QVBoxLayout(CoqListSelect)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.layout = QtGui.QGridLayout()
        self.layout.setObjectName(_fromUtf8("layout"))
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.button_add = QtGui.QToolButton(CoqListSelect)
        self.button_add.setText(_fromUtf8(""))
        self.button_add.setObjectName(_fromUtf8("button_add"))
        self.horizontalLayout_6.addWidget(self.button_add)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.button_up = QtGui.QToolButton(CoqListSelect)
        self.button_up.setText(_fromUtf8(""))
        self.button_up.setObjectName(_fromUtf8("button_up"))
        self.verticalLayout.addWidget(self.button_up)
        self.button_down = QtGui.QToolButton(CoqListSelect)
        self.button_down.setText(_fromUtf8(""))
        self.button_down.setObjectName(_fromUtf8("button_down"))
        self.verticalLayout.addWidget(self.button_down)
        self.horizontalLayout_6.addLayout(self.verticalLayout)
        self.button_remove = QtGui.QToolButton(CoqListSelect)
        self.button_remove.setText(_fromUtf8(""))
        self.button_remove.setObjectName(_fromUtf8("button_remove"))
        self.horizontalLayout_6.addWidget(self.button_remove, QtCore.Qt.AlignVCenter)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.layout.addLayout(self.verticalLayout_5, 1, 1, 1, 1)
        self.list_available = QtGui.QListWidget(CoqListSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_available.sizePolicy().hasHeightForWidth())
        self.list_available.setSizePolicy(sizePolicy)
        self.list_available.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.list_available.setObjectName(_fromUtf8("list_available"))
        self.layout.addWidget(self.list_available, 1, 2, 1, 1)
        self.label_available = QtGui.QLabel(CoqListSelect)
        self.label_available.setObjectName(_fromUtf8("label_available"))
        self.layout.addWidget(self.label_available, 0, 2, 1, 1)
        self.label_select_list = QtGui.QLabel(CoqListSelect)
        self.label_select_list.setObjectName(_fromUtf8("label_select_list"))
        self.layout.addWidget(self.label_select_list, 0, 0, 1, 1)
        self.list_selected = QtGui.QListWidget(CoqListSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_selected.sizePolicy().hasHeightForWidth())
        self.list_selected.setSizePolicy(sizePolicy)
        self.list_selected.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.list_selected.setObjectName(_fromUtf8("list_selected"))
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
        CoqListSelect.setWindowTitle(_translate("CoqListSelect", "Form", None))
        self.label_available.setText(_translate("CoqListSelect", "&Available:", None))
        self.label_select_list.setText(_translate("CoqListSelect", "Se&lected:", None))



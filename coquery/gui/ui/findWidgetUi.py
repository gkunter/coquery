# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'findWidget.ui'
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

class Ui_FindWidget(object):
    def setupUi(self, FindWidget):
        FindWidget.setObjectName(_fromUtf8("FindWidget"))
        FindWidget.resize(1040, 102)
        self.horizontalLayout = QtGui.QHBoxLayout(FindWidget)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.button_find_close = QtGui.QToolButton(FindWidget)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("window-close"))
        self.button_find_close.setIcon(icon)
        self.button_find_close.setObjectName(_fromUtf8("button_find_close"))
        self.horizontalLayout.addWidget(self.button_find_close)
        self.label = QtGui.QLabel(FindWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.edit_find = QtGui.QLineEdit(FindWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_find.sizePolicy().hasHeightForWidth())
        self.edit_find.setSizePolicy(sizePolicy)
        self.edit_find.setObjectName(_fromUtf8("edit_find"))
        self.horizontalLayout.addWidget(self.edit_find)
        self.button_find_next = QtGui.QPushButton(FindWidget)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-down"))
        self.button_find_next.setIcon(icon)
        self.button_find_next.setObjectName(_fromUtf8("button_find_next"))
        self.horizontalLayout.addWidget(self.button_find_next)
        self.button_find_prev = QtGui.QPushButton(FindWidget)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-up"))
        self.button_find_prev.setIcon(icon)
        self.button_find_prev.setObjectName(_fromUtf8("button_find_prev"))
        self.horizontalLayout.addWidget(self.button_find_prev)
        self.horizontalLayout.setStretch(2, 1)

        self.retranslateUi(FindWidget)
        QtCore.QMetaObject.connectSlotsByName(FindWidget)

    def retranslateUi(self, FindWidget):
        FindWidget.setWindowTitle(_translate("FindWidget", "Form", None))
        self.button_find_close.setText(_translate("FindWidget", "...", None))
        self.label.setText(_translate("FindWidget", "Find:", None))
        self.button_find_next.setText(_translate("FindWidget", "Next", None))
        self.button_find_prev.setText(_translate("FindWidget", "Previous", None))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'visualizer.ui'
#
# Created: Tue Aug 18 00:16:39 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui

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

class Ui_Visualizer(object):
    def setupUi(self, Visualizer):
        Visualizer.setObjectName(_fromUtf8("Visualizer"))
        Visualizer.resize(800, 600)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Visualizer)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.box_visualize = QtGui.QFrame(Visualizer)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.box_visualize.sizePolicy().hasHeightForWidth())
        self.box_visualize.setSizePolicy(sizePolicy)
        self.box_visualize.setFrameShape(QtGui.QFrame.StyledPanel)
        self.box_visualize.setFrameShadow(QtGui.QFrame.Raised)
        self.box_visualize.setObjectName(_fromUtf8("box_visualize"))
        self.verticalLayout = QtGui.QVBoxLayout(self.box_visualize)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2.addWidget(self.box_visualize)
        self.frame = QtGui.QFrame(Visualizer)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.check_freeze = QtGui.QCheckBox(self.frame)
        self.check_freeze.setObjectName(_fromUtf8("check_freeze"))
        self.horizontalLayout_3.addWidget(self.check_freeze)
        self.frame_2 = QtGui.QFrame(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.navigation_layout = QtGui.QHBoxLayout(self.frame_2)
        self.navigation_layout.setMargin(0)
        self.navigation_layout.setObjectName(_fromUtf8("navigation_layout"))
        self.horizontalLayout_3.addWidget(self.frame_2)
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.button_close = QtGui.QPushButton(Visualizer)
        self.button_close.setObjectName(_fromUtf8("button_close"))
        self.horizontalLayout_2.addWidget(self.button_close)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Visualizer)
        QtCore.QMetaObject.connectSlotsByName(Visualizer)

    def retranslateUi(self, Visualizer):
        Visualizer.setWindowTitle(_translate("Visualizer", "Data visualization – Coquery", None))
        self.check_freeze.setText(_translate("Visualizer", "&Freeze visualization", None))
        self.button_close.setText(_translate("Visualizer", "&Close", None))


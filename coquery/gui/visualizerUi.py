# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'visualizer.ui'
#
# Created: Tue Jul 21 22:12:59 2015
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

class Ui_visualizer(object):
    def setupUi(self, visualizer):
        visualizer.setObjectName(_fromUtf8("visualizer"))
        visualizer.resize(640, 480)
        self.verticalLayout_2 = QtGui.QVBoxLayout(visualizer)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.box_visualize = QtGui.QFrame(visualizer)
        self.box_visualize.setFrameShape(QtGui.QFrame.StyledPanel)
        self.box_visualize.setFrameShadow(QtGui.QFrame.Raised)
        self.box_visualize.setObjectName(_fromUtf8("box_visualize"))
        self.verticalLayout = QtGui.QVBoxLayout(self.box_visualize)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.graph_area = QtGui.QFrame(self.box_visualize)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graph_area.sizePolicy().hasHeightForWidth())
        self.graph_area.setSizePolicy(sizePolicy)
        self.graph_area.setAutoFillBackground(False)
        self.graph_area.setStyleSheet(_fromUtf8("background: rgb(255, 255, 255)"))
        self.graph_area.setFrameShape(QtGui.QFrame.NoFrame)
        self.graph_area.setFrameShadow(QtGui.QFrame.Plain)
        self.graph_area.setLineWidth(0)
        self.graph_area.setObjectName(_fromUtf8("graph_area"))
        self.visualization_layout = QtGui.QVBoxLayout(self.graph_area)
        self.visualization_layout.setMargin(0)
        self.visualization_layout.setObjectName(_fromUtf8("visualization_layout"))
        self.verticalLayout.addWidget(self.graph_area)
        self.verticalLayout_2.addWidget(self.box_visualize)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.check_freeze = QtGui.QCheckBox(visualizer)
        self.check_freeze.setObjectName(_fromUtf8("check_freeze"))
        self.horizontalLayout.addWidget(self.check_freeze)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(visualizer)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(visualizer)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), visualizer.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), visualizer.reject)
        QtCore.QMetaObject.connectSlotsByName(visualizer)

    def retranslateUi(self, visualizer):
        visualizer.setWindowTitle(_translate("visualizer", "Data visualization – Coquery", None))
        self.check_freeze.setText(_translate("visualizer", "Freeze visualization", None))


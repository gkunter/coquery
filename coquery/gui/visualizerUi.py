# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'visualizer.ui'
#
# Created: Mon Jul 20 23:31:54 2015
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
        self.verticalLayout_2.addWidget(self.box_visualize)
        self.buttonBox = QtGui.QDialogButtonBox(visualizer)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(visualizer)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), visualizer.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), visualizer.reject)
        QtCore.QMetaObject.connectSlotsByName(visualizer)

    def retranslateUi(self, visualizer):
        visualizer.setWindowTitle(_translate("visualizer", "Data visualization – Coquery", None))


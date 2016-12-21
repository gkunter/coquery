# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'textgridView.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(640, 480)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.scrollArea = CoqTextgridScroll(Form)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 640, 456))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.splitter = QtGui.QSplitter(self.scrollAreaWidgetContents)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.frame_waveform = QtGui.QFrame(self.splitter)
        self.frame_waveform.setFrameShape(frameShape)
        self.frame_waveform.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_waveform.setObjectName(_fromUtf8("frame_waveform"))
        self.frame_spectrogram = QtGui.QFrame(self.splitter)
        self.frame_spectrogram.setFrameShape(frameShape)
        self.frame_spectrogram.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_spectrogram.setObjectName(_fromUtf8("frame_spectrogram"))
        self.frame_textgrid = QtGui.QFrame(self.splitter)
        self.frame_textgrid.setFrameShape(frameShape)
        self.frame_textgrid.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_textgrid.setObjectName(_fromUtf8("frame_textgrid"))
        self.horizontalLayout_2.addWidget(self.splitter)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))

from ..textgridscrol import CoqTextgridScroll


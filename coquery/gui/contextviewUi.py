# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'contextview.ui'
#
# Created: Mon Jul 20 23:29:51 2015
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

class Ui_ContextView(object):
    def setupUi(self, ContextView):
        ContextView.setObjectName(_fromUtf8("ContextView"))
        ContextView.resize(578, 412)
        ContextView.setSizeGripEnabled(False)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ContextView)
        self.verticalLayout_2.setContentsMargins(4, 4, 4, -1)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.box_context = QtGui.QFrame(ContextView)
        self.box_context.setFrameShape(QtGui.QFrame.StyledPanel)
        self.box_context.setFrameShadow(QtGui.QFrame.Raised)
        self.box_context.setObjectName(_fromUtf8("box_context"))
        self.verticalLayout = QtGui.QVBoxLayout(self.box_context)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.form_information = QtGui.QFormLayout()
        self.form_information.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.form_information.setHorizontalSpacing(10)
        self.form_information.setObjectName(_fromUtf8("form_information"))
        self.verticalLayout.addLayout(self.form_information)
        self.line = QtGui.QFrame(self.box_context)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.context_area = QtGui.QTextBrowser(self.box_context)
        self.context_area.setAutoFillBackground(False)
        self.context_area.setFrameShape(QtGui.QFrame.StyledPanel)
        self.context_area.setFrameShadow(QtGui.QFrame.Sunken)
        self.context_area.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.context_area.setObjectName(_fromUtf8("context_area"))
        self.verticalLayout.addWidget(self.context_area)
        self.verticalLayout_2.addWidget(self.box_context)
        self.box_context_width = QtGui.QFrame(ContextView)
        self.box_context_width.setFrameShape(QtGui.QFrame.StyledPanel)
        self.box_context_width.setFrameShadow(QtGui.QFrame.Raised)
        self.box_context_width.setObjectName(_fromUtf8("box_context_width"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.box_context_width)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setMargin(10)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_3 = QtGui.QLabel(self.box_context_width)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.spin_context_width = QtGui.QSpinBox(self.box_context_width)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spin_context_width.sizePolicy().hasHeightForWidth())
        self.spin_context_width.setSizePolicy(sizePolicy)
        self.spin_context_width.setFrame(True)
        self.spin_context_width.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.spin_context_width.setMaximum(500)
        self.spin_context_width.setProperty("value", 5)
        self.spin_context_width.setObjectName(_fromUtf8("spin_context_width"))
        self.horizontalLayout.addWidget(self.spin_context_width)
        self.slider_context_width = QtGui.QSlider(self.box_context_width)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slider_context_width.sizePolicy().hasHeightForWidth())
        self.slider_context_width.setSizePolicy(sizePolicy)
        self.slider_context_width.setMinimum(0)
        self.slider_context_width.setMaximum(500)
        self.slider_context_width.setProperty("value", 10)
        self.slider_context_width.setSliderPosition(10)
        self.slider_context_width.setOrientation(QtCore.Qt.Horizontal)
        self.slider_context_width.setInvertedAppearance(False)
        self.slider_context_width.setInvertedControls(False)
        self.slider_context_width.setTickPosition(QtGui.QSlider.TicksAbove)
        self.slider_context_width.setTickInterval(10)
        self.slider_context_width.setObjectName(_fromUtf8("slider_context_width"))
        self.horizontalLayout.addWidget(self.slider_context_width)
        self.verticalLayout_2.addWidget(self.box_context_width)
        self.buttonBox = QtGui.QDialogButtonBox(ContextView)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(ContextView)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ContextView.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ContextView.reject)
        QtCore.QMetaObject.connectSlotsByName(ContextView)

    def retranslateUi(self, ContextView):
        ContextView.setWindowTitle(_translate("ContextView", "Context view – Coquery", None))
        self.label_3.setText(_translate("ContextView", "Context size:", None))
        self.spin_context_width.setSpecialValueText(_translate("ContextView", "none", None))
        self.spin_context_width.setSuffix(_translate("ContextView", " words", None))


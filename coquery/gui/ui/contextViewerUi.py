# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'contextViewer.ui'
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

class Ui_ContextView(object):
    def setupUi(self, ContextView):
        ContextView.setObjectName(_fromUtf8("ContextView"))
        ContextView.resize(640, 480)
        self.verticalLayout_3 = QtGui.QVBoxLayout(ContextView)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, -1, 4, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_4 = QtGui.QLabel(ContextView)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.label_4)
        self.spin_context_width = QtGui.QSpinBox(ContextView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spin_context_width.sizePolicy().hasHeightForWidth())
        self.spin_context_width.setSizePolicy(sizePolicy)
        self.spin_context_width.setFrame(True)
        self.spin_context_width.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.spin_context_width.setMaximum(1000)
        self.spin_context_width.setProperty("value", 10)
        self.spin_context_width.setObjectName(_fromUtf8("spin_context_width"))
        self.horizontalLayout.addWidget(self.spin_context_width)
        self.slider_context_width = QtGui.QSlider(ContextView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slider_context_width.sizePolicy().hasHeightForWidth())
        self.slider_context_width.setSizePolicy(sizePolicy)
        self.slider_context_width.setMinimum(0)
        self.slider_context_width.setMaximum(1000)
        self.slider_context_width.setPageStep(25)
        self.slider_context_width.setProperty("value", 10)
        self.slider_context_width.setSliderPosition(10)
        self.slider_context_width.setOrientation(QtCore.Qt.Horizontal)
        self.slider_context_width.setInvertedAppearance(False)
        self.slider_context_width.setInvertedControls(False)
        self.slider_context_width.setTickPosition(QtGui.QSlider.TicksAbove)
        self.slider_context_width.setTickInterval(10)
        self.slider_context_width.setObjectName(_fromUtf8("slider_context_width"))
        self.horizontalLayout.addWidget(self.slider_context_width)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.tab_widget = QtGui.QTabWidget(ContextView)
        self.tab_widget.setObjectName(_fromUtf8("tab_widget"))
        self.tab_context = QtGui.QWidget()
        self.tab_context.setObjectName(_fromUtf8("tab_context"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.tab_context)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.context_area = QtGui.QTextBrowser(self.tab_context)
        self.context_area.setAutoFillBackground(False)
        self.context_area.setFrameShape(frameShape)
        self.context_area.setFrameShadow(QtGui.QFrame.Sunken)
        self.context_area.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.context_area.setObjectName(_fromUtf8("context_area"))
        self.verticalLayout_4.addWidget(self.context_area)
        self.tab_widget.addTab(self.tab_context, _fromUtf8(""))
        self.tab_textgrid = QtGui.QWidget()
        self.tab_textgrid.setObjectName(_fromUtf8("tab_textgrid"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.tab_textgrid)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.textgrid_area = CoqTextgridView(self.tab_textgrid)
        self.textgrid_area.setObjectName(_fromUtf8("textgrid_area"))
        self.verticalLayout_5.addWidget(self.textgrid_area)
        self.tab_widget.addTab(self.tab_textgrid, _fromUtf8(""))
        self.verticalLayout_3.addWidget(self.tab_widget)
        self.label_4.setBuddy(self.spin_context_width)

        self.retranslateUi(ContextView)
        self.tab_widget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(ContextView)

    def retranslateUi(self, ContextView):
        ContextView.setWindowTitle(_translate("ContextView", "Context view – Coquery", None))
        self.label_4.setText(_translate("ContextView", "&Context size:", None))
        self.spin_context_width.setSpecialValueText(_translate("ContextView", "none", None))
        self.spin_context_width.setSuffix(_translate("ContextView", " words", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_context), _translate("ContextView", "Context", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_textgrid), _translate("ContextView", "Text grid", None))

from ..textgridview import CoqTextgridView


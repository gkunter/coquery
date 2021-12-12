# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'contextViewer.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ContextView(object):
    def setupUi(self, ContextView):
        ContextView.setObjectName("ContextView")
        ContextView.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(ContextView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.button_ids = CoqDetailBox(ContextView)
        self.button_ids.setObjectName("button_ids")
        self.verticalLayout.addWidget(self.button_ids)
        self.context_area = QtWidgets.QTextBrowser(ContextView)
        self.context_area.setAutoFillBackground(False)
        self.context_area.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.context_area.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.context_area.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.context_area.setObjectName("context_area")
        self.verticalLayout.addWidget(self.context_area)
        self.progress_bar = QtWidgets.QProgressBar(ContextView)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setProperty("value", -1)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout.addWidget(self.progress_bar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, -1, 4, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(ContextView)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.spin_context_width = QtWidgets.QSpinBox(ContextView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spin_context_width.sizePolicy().hasHeightForWidth())
        self.spin_context_width.setSizePolicy(sizePolicy)
        self.spin_context_width.setFrame(True)
        self.spin_context_width.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.spin_context_width.setMaximum(1000)
        self.spin_context_width.setProperty("value", 10)
        self.spin_context_width.setObjectName("spin_context_width")
        self.horizontalLayout.addWidget(self.spin_context_width)
        self.slider_context_width = QtWidgets.QSlider(ContextView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
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
        self.slider_context_width.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.slider_context_width.setTickInterval(10)
        self.slider_context_width.setObjectName("slider_context_width")
        self.horizontalLayout.addWidget(self.slider_context_width)
        self.button_prev = QtWidgets.QPushButton(ContextView)
        self.button_prev.setObjectName("button_prev")
        self.horizontalLayout.addWidget(self.button_prev)
        self.button_next = QtWidgets.QPushButton(ContextView)
        self.button_next.setObjectName("button_next")
        self.horizontalLayout.addWidget(self.button_next)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_4.setBuddy(self.spin_context_width)

        self.retranslateUi(ContextView)
        QtCore.QMetaObject.connectSlotsByName(ContextView)

    def retranslateUi(self, ContextView):
        _translate = QtCore.QCoreApplication.translate
        ContextView.setWindowTitle(_translate("ContextView", "Context view – Coquery"))
        self.label_4.setText(_translate("ContextView", "&Context size:"))
        self.spin_context_width.setSpecialValueText(_translate("ContextView", "none"))
        self.spin_context_width.setSuffix(_translate("ContextView", " words"))
        self.button_prev.setToolTip(_translate("ContextView", "Show previous context"))
        self.button_prev.setText(_translate("ContextView", "Previous"))
        self.button_next.setToolTip(_translate("ContextView", "Show next context"))
        self.button_next.setText(_translate("ContextView", "Next"))

from ..classes import CoqDetailBox

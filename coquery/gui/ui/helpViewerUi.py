# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helpViewer.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HelpViewer(object):
    def setupUi(self, HelpViewer):
        HelpViewer.setObjectName("HelpViewer")
        HelpViewer.resize(640, 480)
        self.centralwidget = QtWidgets.QWidget(HelpViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.index = QtWidgets.QTextBrowser(self.splitter)
        self.index.setOpenLinks(False)
        self.index.setObjectName("index")
        self.content = QtWidgets.QTextBrowser(self.splitter)
        self.content.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.content.setFrameShadow(QtWidgets.QFrame.Plain)
        self.content.setObjectName("content")
        self.verticalLayout.addWidget(self.splitter)
        HelpViewer.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(HelpViewer)
        self.toolBar.setObjectName("toolBar")
        HelpViewer.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_next = QtWidgets.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme("go-next")
        self.action_next.setIcon(icon)
        self.action_next.setObjectName("action_next")
        self.action_prev = QtWidgets.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme("go-previous")
        self.action_prev.setIcon(icon)
        self.action_prev.setObjectName("action_prev")
        self.action_home = QtWidgets.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme("go-home")
        self.action_home.setIcon(icon)
        self.action_home.setObjectName("action_home")
        self.action_zoom_in = QtWidgets.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme("zoom-in")
        self.action_zoom_in.setIcon(icon)
        self.action_zoom_in.setObjectName("action_zoom_in")
        self.action_zoom_out = QtWidgets.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme("zoom-out")
        self.action_zoom_out.setIcon(icon)
        self.action_zoom_out.setObjectName("action_zoom_out")
        self.action_reset_zoom = QtWidgets.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme("zoom-original")
        self.action_reset_zoom.setIcon(icon)
        self.action_reset_zoom.setObjectName("action_reset_zoom")
        self.action_print = QtWidgets.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme("document-print")
        self.action_print.setIcon(icon)
        self.action_print.setObjectName("action_print")
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_prev)
        self.toolBar.addAction(self.action_next)
        self.toolBar.addAction(self.action_home)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_print)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_zoom_in)
        self.toolBar.addAction(self.action_zoom_out)
        self.toolBar.addAction(self.action_reset_zoom)

        self.retranslateUi(HelpViewer)
        QtCore.QMetaObject.connectSlotsByName(HelpViewer)

    def retranslateUi(self, HelpViewer):
        _translate = QtCore.QCoreApplication.translate
        HelpViewer.setWindowTitle(_translate("HelpViewer", "Help – Coquery"))
        self.toolBar.setWindowTitle(_translate("HelpViewer", "toolBar"))
        self.action_next.setText(_translate("HelpViewer", "Forward"))
        self.action_prev.setText(_translate("HelpViewer", "Previous"))
        self.action_prev.setToolTip(_translate("HelpViewer", "Previous"))
        self.action_home.setText(_translate("HelpViewer", "Home"))
        self.action_zoom_in.setText(_translate("HelpViewer", "Zoom in"))
        self.action_zoom_in.setToolTip(_translate("HelpViewer", "Zoom in"))
        self.action_zoom_out.setText(_translate("HelpViewer", "Zoom out"))
        self.action_reset_zoom.setText(_translate("HelpViewer", "Reset zoom"))
        self.action_print.setText(_translate("HelpViewer", "Print"))



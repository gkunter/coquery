# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helpViewer.ui'
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

class Ui_HelpViewer(object):
    def setupUi(self, HelpViewer):
        HelpViewer.setObjectName(_fromUtf8("HelpViewer"))
        HelpViewer.resize(640, 480)
        self.centralwidget = QtGui.QWidget(HelpViewer)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.index = QtGui.QTextBrowser(self.splitter)
        self.index.setOpenLinks(False)
        self.index.setObjectName(_fromUtf8("index"))
        self.content = QtGui.QTextBrowser(self.splitter)
        self.content.setFrameShape(QtGui.QFrame.NoFrame)
        self.content.setFrameShadow(QtGui.QFrame.Plain)
        self.content.setObjectName(_fromUtf8("content"))
        self.verticalLayout.addWidget(self.splitter)
        HelpViewer.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(HelpViewer)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        HelpViewer.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_next = QtGui.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-next"))
        self.action_next.setIcon(icon)
        self.action_next.setObjectName(_fromUtf8("action_next"))
        self.action_prev = QtGui.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-previous"))
        self.action_prev.setIcon(icon)
        self.action_prev.setObjectName(_fromUtf8("action_prev"))
        self.action_home = QtGui.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-home"))
        self.action_home.setIcon(icon)
        self.action_home.setObjectName(_fromUtf8("action_home"))
        self.action_zoom_in = QtGui.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("zoom-in"))
        self.action_zoom_in.setIcon(icon)
        self.action_zoom_in.setObjectName(_fromUtf8("action_zoom_in"))
        self.action_zoom_out = QtGui.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("zoom-out"))
        self.action_zoom_out.setIcon(icon)
        self.action_zoom_out.setObjectName(_fromUtf8("action_zoom_out"))
        self.action_reset_zoom = QtGui.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("zoom-original"))
        self.action_reset_zoom.setIcon(icon)
        self.action_reset_zoom.setObjectName(_fromUtf8("action_reset_zoom"))
        self.action_print = QtGui.QAction(HelpViewer)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-print"))
        self.action_print.setIcon(icon)
        self.action_print.setObjectName(_fromUtf8("action_print"))
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
        HelpViewer.setWindowTitle(_translate("HelpViewer", "Help – Coquery", None))
        self.toolBar.setWindowTitle(_translate("HelpViewer", "toolBar", None))
        self.action_next.setText(_translate("HelpViewer", "Forward", None))
        self.action_prev.setText(_translate("HelpViewer", "Previous", None))
        self.action_prev.setToolTip(_translate("HelpViewer", "Previous", None))
        self.action_home.setText(_translate("HelpViewer", "Home", None))
        self.action_zoom_in.setText(_translate("HelpViewer", "Zoom in", None))
        self.action_zoom_in.setToolTip(_translate("HelpViewer", "Zoom in", None))
        self.action_zoom_out.setText(_translate("HelpViewer", "Zoom out", None))
        self.action_reset_zoom.setText(_translate("HelpViewer", "Reset zoom", None))
        self.action_print.setText(_translate("HelpViewer", "Print", None))



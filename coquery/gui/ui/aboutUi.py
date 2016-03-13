# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
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

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName(_fromUtf8("AboutDialog"))
        AboutDialog.resize(610, 640)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtGui.QVBoxLayout(AboutDialog)
        self.verticalLayout_2.setSpacing(16)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(AboutDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(8, 6, 8, 6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame_pixmap = QtGui.QFrame(self.frame)
        self.frame_pixmap.setStyleSheet(_fromUtf8("background-color: #fffdfd"))
        self.frame_pixmap.setObjectName(_fromUtf8("frame_pixmap"))
        self.layout_pixmap = QtGui.QVBoxLayout(self.frame_pixmap)
        self.layout_pixmap.setContentsMargins(4, 3, 4, 3)
        self.layout_pixmap.setSpacing(0)
        self.layout_pixmap.setObjectName(_fromUtf8("layout_pixmap"))
        self.label_pixmap = QtGui.QLabel(self.frame_pixmap)
        self.label_pixmap.setText(_fromUtf8(""))
        self.label_pixmap.setObjectName(_fromUtf8("label_pixmap"))
        self.layout_pixmap.addWidget(self.label_pixmap)
        self.verticalLayout.addWidget(self.frame_pixmap)
        self.label_description = QtGui.QLabel(self.frame)
        self.label_description.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_description.setOpenExternalLinks(True)
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.verticalLayout.addWidget(self.label_description)
        self.verticalLayout_2.addWidget(self.frame)
        self.buttonBox = QtGui.QDialogButtonBox(AboutDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(AboutDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AboutDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AboutDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About – Coquery", None))
        self.label_description.setText(_translate("AboutDialog", "<html><head/><body><p>Coquery is a free corpus query tool.</p><p>Copyright (c) {date} Gero Kunter</p><p>Initial development supported by:<br/>Department of English, Heinrich-Heine Universität Düsseldorf</p><p>Website: <a href=\"http://www.coquery.org\"><span style=\" text-decoration: underline; color:#0057ae;\">http://www.coquery.org</span></a><br/>Follow on Twitter: <a href=\"https://twitter.com/CoqueryTool\"><span style=\" text-decoration: underline; color:#0057ae;\">@CoqueryTool</span></a></p></body></html>", None))



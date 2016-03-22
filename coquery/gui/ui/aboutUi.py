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
        AboutDialog.resize(640, 480)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(AboutDialog)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout.setSpacing(16)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame_pixmap = QtGui.QFrame(AboutDialog)
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
        self.label_description = QtGui.QLabel(AboutDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_description.sizePolicy().hasHeightForWidth())
        self.label_description.setSizePolicy(sizePolicy)
        self.label_description.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_description.setOpenExternalLinks(True)
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.verticalLayout.addWidget(self.label_description)
        self.modules = CoqDetailBox(AboutDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modules.sizePolicy().hasHeightForWidth())
        self.modules.setSizePolicy(sizePolicy)
        self.modules.setObjectName(_fromUtf8("modules"))
        self.verticalLayout.addWidget(self.modules)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About – Coquery", None))
        self.label_description.setText(_translate("AboutDialog", "<html><head/><body><p>Coquery is a free corpus query tool.</p><p>Copyright (c) {date} Gero Kunter</p><p>Initial development supported by:<br/>Department of English, Heinrich-Heine Universität Düsseldorf</p><p>Website: <a href=\"http://www.coquery.org\"><span style=\" text-decoration: underline; color:#0057ae;\">http://www.coquery.org</span></a> – Twitter: <a href=\"https://twitter.com/hashtag/coquery?f=tweets\"><span style=\" text-decoration: underline; color:#0057ae;\">#Coquery</span></a></p><p>Coquery is free software released under the terms of the <a href=\"http://coquery.org/license.html\"><span style=\" text-decoration: underline; color:#0057ae;\">GNU General Public License (version 3)</span></a>. </p><p><br/></p></body></html>", None))

from ..classes import CoqDetailBox


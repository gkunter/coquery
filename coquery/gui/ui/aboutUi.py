# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(640, 480)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout.setSpacing(16)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_pixmap = QtWidgets.QFrame(AboutDialog)
        self.frame_pixmap.setStyleSheet("background-color: #fffdfd")
        self.frame_pixmap.setObjectName("frame_pixmap")
        self.layout_pixmap = QtWidgets.QVBoxLayout(self.frame_pixmap)
        self.layout_pixmap.setContentsMargins(4, 3, 4, 3)
        self.layout_pixmap.setSpacing(0)
        self.layout_pixmap.setObjectName("layout_pixmap")
        self.label_pixmap = QtWidgets.QLabel(self.frame_pixmap)
        self.label_pixmap.setText("")
        self.label_pixmap.setObjectName("label_pixmap")
        self.layout_pixmap.addWidget(self.label_pixmap)
        self.verticalLayout.addWidget(self.frame_pixmap)
        self.label_description = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_description.sizePolicy().hasHeightForWidth())
        self.label_description.setSizePolicy(sizePolicy)
        self.label_description.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_description.setWordWrap(True)
        self.label_description.setOpenExternalLinks(True)
        self.label_description.setObjectName("label_description")
        self.verticalLayout.addWidget(self.label_description)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About – Coquery"))
        self.label_description.setText(_translate("AboutDialog", "<html><head/><body><p>Coquery is a free corpus query tool.</p><p>Copyright (c) {date} Gero Kunter</p><p>Initial development supported by:<br/>Department of English, Heinrich-Heine Universität Düsseldorf</p><p>Website: <a href=\"http://www.coquery.org\"><span style=\" text-decoration: underline; color:#0057ae;\">http://www.coquery.org</span></a> – Twitter: <a href=\"https://twitter.com/hashtag/coquery?f=tweets\"><span style=\" text-decoration: underline; color:#0057ae;\">#Coquery</span></a></p><p>Coquery is free software released under the terms of the <a href=\"http://coquery.org/license.html\"><span style=\" text-decoration: underline; color:#0057ae;\">GNU General Public License (version 3)</span></a>.  Icon set by <a href=\"http://icons8.com\"><span style=\" text-decoration: underline; color:#0057ae;\">icons8.com</span></a>.</p></body></html>"))



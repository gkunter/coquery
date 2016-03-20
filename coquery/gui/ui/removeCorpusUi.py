# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'removeCorpus.ui'
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

class Ui_RemoveCorpus(object):
    def setupUi(self, RemoveCorpus):
        RemoveCorpus.setObjectName(_fromUtf8("RemoveCorpus"))
        RemoveCorpus.resize(480, 365)
        self.verticalLayout_3 = QtGui.QVBoxLayout(RemoveCorpus)
        self.verticalLayout_3.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_3.setContentsMargins(6, 8, 6, 8)
        self.verticalLayout_3.setSpacing(16)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.frame = QtGui.QFrame(RemoveCorpus)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setContentsMargins(6, 8, 6, 8)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.groupBox = QtGui.QGroupBox(self.frame)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.check_rm_module = QtGui.QCheckBox(self.groupBox)
        self.check_rm_module.setObjectName(_fromUtf8("check_rm_module"))
        self.verticalLayout.addWidget(self.check_rm_module)
        self.check_rm_database = QtGui.QCheckBox(self.groupBox)
        self.check_rm_database.setObjectName(_fromUtf8("check_rm_database"))
        self.verticalLayout.addWidget(self.check_rm_database)
        self.check_rm_installer = QtGui.QCheckBox(self.groupBox)
        self.check_rm_installer.setObjectName(_fromUtf8("check_rm_installer"))
        self.verticalLayout.addWidget(self.check_rm_installer)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.verticalLayout_3.addWidget(self.frame)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.frame_2 = QtGui.QFrame(RemoveCorpus)
        self.frame_2.setFrameShape(frameShape)
        self.frame_2.setFrameShadow(frameShadow)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_3 = QtGui.QLabel(self.frame_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_4.addWidget(self.label_3)
        self.verticalLayout_3.addWidget(self.frame_2)
        self.buttonBox = QtGui.QDialogButtonBox(RemoveCorpus)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(RemoveCorpus)
        QtCore.QMetaObject.connectSlotsByName(RemoveCorpus)

    def retranslateUi(self, RemoveCorpus):
        RemoveCorpus.setWindowTitle(_translate("RemoveCorpus", "Remove corpus – Coquery", None))
        self.label.setText(_translate("RemoveCorpus", "<html><head/><body><p><span style=\" font-weight:600;\">Remove corpus</span></p><p>You have chosen to remove the corpus \'{}\' from the database connection \'{}\'.</p></body></html>", None))
        self.label_4.setText(_translate("RemoveCorpus", "Choose the corpus comonents that you wish to remove:", None))
        self.check_rm_module.setText(_translate("RemoveCorpus", "Corpus module", None))
        self.check_rm_database.setText(_translate("RemoveCorpus", "Database", None))
        self.check_rm_installer.setText(_translate("RemoveCorpus", "Installer", None))
        self.label_3.setText(_translate("RemoveCorpus", "Click \'Ok\' to remove the selected components. Click \'Cancel\' to exit without deleting the selected components.", None))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'removeCorpus.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RemoveCorpus(object):
    def setupUi(self, RemoveCorpus):
        RemoveCorpus.setObjectName("RemoveCorpus")
        RemoveCorpus.resize(480, 365)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(RemoveCorpus)
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout_3.setContentsMargins(6, 8, 6, 8)
        self.verticalLayout_3.setSpacing(16)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame = QtWidgets.QFrame(RemoveCorpus)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setContentsMargins(6, 8, 6, 8)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.groupBox = QtWidgets.QGroupBox(self.frame)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.check_rm_module = QtWidgets.QCheckBox(self.groupBox)
        self.check_rm_module.setObjectName("check_rm_module")
        self.verticalLayout.addWidget(self.check_rm_module)
        self.check_rm_database = QtWidgets.QCheckBox(self.groupBox)
        self.check_rm_database.setObjectName("check_rm_database")
        self.verticalLayout.addWidget(self.check_rm_database)
        self.check_rm_installer = QtWidgets.QCheckBox(self.groupBox)
        self.check_rm_installer.setObjectName("check_rm_installer")
        self.verticalLayout.addWidget(self.check_rm_installer)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.verticalLayout_3.addWidget(self.frame)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.frame_2 = QtWidgets.QFrame(RemoveCorpus)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.verticalLayout_3.addWidget(self.frame_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(RemoveCorpus)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(RemoveCorpus)
        QtCore.QMetaObject.connectSlotsByName(RemoveCorpus)

    def retranslateUi(self, RemoveCorpus):
        _translate = QtCore.QCoreApplication.translate
        RemoveCorpus.setWindowTitle(_translate("RemoveCorpus", "Remove corpus – Coquery"))
        self.label.setText(_translate("RemoveCorpus", "<html><head/><body><p><span style=\" font-weight:600;\">Remove corpus</span></p><p>You have chosen to remove the corpus \'{}\' from the database connection \'{}\'.</p></body></html>"))
        self.label_4.setText(_translate("RemoveCorpus", "Choose the corpus comonents that you wish to remove:"))
        self.check_rm_module.setText(_translate("RemoveCorpus", "Corpus module"))
        self.check_rm_database.setText(_translate("RemoveCorpus", "Database"))
        self.check_rm_installer.setText(_translate("RemoveCorpus", "Installer"))
        self.label_3.setText(_translate("RemoveCorpus", "Click \'Ok\' to remove the selected components. Click \'Cancel\' to exit without deleting the selected components."))



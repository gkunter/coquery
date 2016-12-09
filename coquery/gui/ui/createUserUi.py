# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'createUser.ui'
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

class Ui_CreateUser(object):
    def setupUi(self, CreateUser):
        CreateUser.setObjectName(_fromUtf8("CreateUser"))
        CreateUser.resize(640, 480)
        self.verticalLayout_3 = QtGui.QVBoxLayout(CreateUser)
        self.verticalLayout_3.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.groupBox_2 = QtGui.QGroupBox(CreateUser)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.new_password_check = QtGui.QLineEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.new_password_check.sizePolicy().hasHeightForWidth())
        self.new_password_check.setSizePolicy(sizePolicy)
        self.new_password_check.setText(_fromUtf8(""))
        self.new_password_check.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.new_password_check.setObjectName(_fromUtf8("new_password_check"))
        self.gridLayout_2.addWidget(self.new_password_check, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)
        self.new_name = QtGui.QLineEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.new_name.sizePolicy().hasHeightForWidth())
        self.new_name.setSizePolicy(sizePolicy)
        self.new_name.setText(_fromUtf8(""))
        self.new_name.setObjectName(_fromUtf8("new_name"))
        self.gridLayout_2.addWidget(self.new_name, 0, 1, 1, 1)
        self.new_password = QtGui.QLineEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.new_password.sizePolicy().hasHeightForWidth())
        self.new_password.setSizePolicy(sizePolicy)
        self.new_password.setText(_fromUtf8(""))
        self.new_password.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.new_password.setObjectName(_fromUtf8("new_password"))
        self.gridLayout_2.addWidget(self.new_password, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.label_7 = QtGui.QLabel(self.groupBox_2)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_2.addWidget(self.label_7)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(CreateUser)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.root_name = QtGui.QLineEdit(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.root_name.sizePolicy().hasHeightForWidth())
        self.root_name.setSizePolicy(sizePolicy)
        self.root_name.setText(_fromUtf8(""))
        self.root_name.setObjectName(_fromUtf8("root_name"))
        self.gridLayout.addWidget(self.root_name, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_3)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.root_password = QtGui.QLineEdit(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.root_password.sizePolicy().hasHeightForWidth())
        self.root_password.setSizePolicy(sizePolicy)
        self.root_password.setText(_fromUtf8(""))
        self.root_password.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.root_password.setObjectName(_fromUtf8("root_password"))
        self.gridLayout.addWidget(self.root_password, 1, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.groupBox = QtGui.QGroupBox(CreateUser)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.check_show_passwords = QtGui.QCheckBox(self.groupBox)
        self.check_show_passwords.setObjectName(_fromUtf8("check_show_passwords"))
        self.verticalLayout.addWidget(self.check_show_passwords)
        self.verticalLayout_3.addWidget(self.groupBox)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(CreateUser)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.verticalLayout_3.setStretch(4, 1)

        self.retranslateUi(CreateUser)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CreateUser.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CreateUser.reject)
        QtCore.QMetaObject.connectSlotsByName(CreateUser)
        CreateUser.setTabOrder(self.root_name, self.root_password)
        CreateUser.setTabOrder(self.root_password, self.new_name)
        CreateUser.setTabOrder(self.new_name, self.new_password)
        CreateUser.setTabOrder(self.new_password, self.new_password_check)
        CreateUser.setTabOrder(self.new_password_check, self.check_show_passwords)
        CreateUser.setTabOrder(self.check_show_passwords, self.buttonBox)

    def retranslateUi(self, CreateUser):
        CreateUser.setWindowTitle(_translate("CreateUser", "Create a new MySQL user – Coquery", None))
        self.groupBox_2.setTitle(_translate("CreateUser", "New user", None))
        self.label_4.setText(_translate("CreateUser", "Password:", None))
        self.label_6.setText(_translate("CreateUser", "Retype password::", None))
        self.label_5.setText(_translate("CreateUser", "New user name:", None))
        self.label_7.setText(_translate("CreateUser", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">New users will be able to create, query, modify, and delete databases and tables</li>\n"
"<li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">New users will <span style=\" font-weight:600;\">not be able</span> to create or modify the privileges of other users</li></ul></body></html>", None))
        self.groupBox_3.setTitle(_translate("CreateUser", "MySQL root", None))
        self.label_3.setText(_translate("CreateUser", "MySQL root user:", None))
        self.label_2.setText(_translate("CreateUser", "MySQL root password:", None))
        self.check_show_passwords.setText(_translate("CreateUser", "Show passwords", None))



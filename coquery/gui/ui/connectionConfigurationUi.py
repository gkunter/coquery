# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'connectionConfiguration.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui, frameShadow, frameShape

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

class Ui_ConnectionConfig(object):
    def setupUi(self, ConnectionConfig):
        ConnectionConfig.setObjectName(_fromUtf8("ConnectionConfig"))
        ConnectionConfig.resize(532, 570)
        self.verticalLayout_12 = QtGui.QVBoxLayout(ConnectionConfig)
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.label_5 = QtGui.QLabel(ConnectionConfig)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_12.addWidget(self.label_5)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(8)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.tree_configuration = QtGui.QTreeWidget(ConnectionConfig)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_configuration.sizePolicy().hasHeightForWidth())
        self.tree_configuration.setSizePolicy(sizePolicy)
        self.tree_configuration.setRootIsDecorated(False)
        self.tree_configuration.setItemsExpandable(False)
        self.tree_configuration.setHeaderHidden(True)
        self.tree_configuration.setExpandsOnDoubleClick(False)
        self.tree_configuration.setObjectName(_fromUtf8("tree_configuration"))
        self.tree_configuration.headerItem().setText(0, _fromUtf8("1"))
        self.verticalLayout_4.addWidget(self.tree_configuration)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setHorizontalSpacing(8)
        self.gridLayout_3.setVerticalSpacing(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.button_add = QtGui.QPushButton(ConnectionConfig)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_add.sizePolicy().hasHeightForWidth())
        self.button_add.setSizePolicy(sizePolicy)
        self.button_add.setObjectName(_fromUtf8("button_add"))
        self.gridLayout_3.addWidget(self.button_add, 0, 0, 1, 1)
        self.button_replace = QtGui.QPushButton(ConnectionConfig)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_replace.sizePolicy().hasHeightForWidth())
        self.button_replace.setSizePolicy(sizePolicy)
        self.button_replace.setObjectName(_fromUtf8("button_replace"))
        self.gridLayout_3.addWidget(self.button_replace, 0, 1, 1, 1)
        self.button_remove = QtGui.QPushButton(ConnectionConfig)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_remove.sizePolicy().hasHeightForWidth())
        self.button_remove.setSizePolicy(sizePolicy)
        self.button_remove.setObjectName(_fromUtf8("button_remove"))
        self.gridLayout_3.addWidget(self.button_remove, 0, 2, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout_3)
        self.horizontalLayout_5.addLayout(self.verticalLayout_4)
        self.verticalLayout_11 = QtGui.QVBoxLayout()
        self.verticalLayout_11.setSpacing(8)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.groupBox_2 = QtGui.QGroupBox(ConnectionConfig)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_4.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.configuration_name = QtGui.QLineEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.configuration_name.sizePolicy().hasHeightForWidth())
        self.configuration_name.setSizePolicy(sizePolicy)
        self.configuration_name.setObjectName(_fromUtf8("configuration_name"))
        self.gridLayout_4.addWidget(self.configuration_name, 0, 1, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.radio_mysql = QtGui.QRadioButton(self.groupBox_2)
        self.radio_mysql.setObjectName(_fromUtf8("radio_mysql"))
        self.horizontalLayout_2.addWidget(self.radio_mysql)
        self.radio_sqlite = QtGui.QRadioButton(self.groupBox_2)
        self.radio_sqlite.setChecked(True)
        self.radio_sqlite.setObjectName(_fromUtf8("radio_sqlite"))
        self.horizontalLayout_2.addWidget(self.radio_sqlite)
        self.gridLayout_4.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)
        self.label_7 = QtGui.QLabel(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_4.addWidget(self.label_7, 1, 0, 1, 1)
        self.verticalLayout_11.addWidget(self.groupBox_2)
        self.frame_settings = QtGui.QFrame(ConnectionConfig)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_settings.sizePolicy().hasHeightForWidth())
        self.frame_settings.setSizePolicy(sizePolicy)
        self.frame_settings.setObjectName(_fromUtf8("frame_settings"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.frame_settings)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.frame_mysql = QtGui.QWidget(self.frame_settings)
        self.frame_mysql.setObjectName(_fromUtf8("frame_mysql"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame_mysql)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setSpacing(8)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.frame_mysql)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(-1, 10, -1, -1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.radio_local = QtGui.QRadioButton(self.groupBox)
        self.radio_local.setChecked(True)
        self.radio_local.setObjectName(_fromUtf8("radio_local"))
        self.verticalLayout.addWidget(self.radio_local)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.radio_remote = QtGui.QRadioButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radio_remote.sizePolicy().hasHeightForWidth())
        self.radio_remote.setSizePolicy(sizePolicy)
        self.radio_remote.setObjectName(_fromUtf8("radio_remote"))
        self.gridLayout_2.addWidget(self.radio_remote, 0, 0, 1, 1)
        self.hostname = QtGui.QLineEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hostname.sizePolicy().hasHeightForWidth())
        self.hostname.setSizePolicy(sizePolicy)
        self.hostname.setInputMask(_fromUtf8(""))
        self.hostname.setText(_fromUtf8(""))
        self.hostname.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.hostname.setObjectName(_fromUtf8("hostname"))
        self.gridLayout_2.addWidget(self.hostname, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_3.addWidget(self.label_4)
        self.port = QtGui.QSpinBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.port.sizePolicy().hasHeightForWidth())
        self.port.setSizePolicy(sizePolicy)
        self.port.setMinimum(1)
        self.port.setMaximum(65535)
        self.port.setProperty("value", 3306)
        self.port.setObjectName(_fromUtf8("port"))
        self.horizontalLayout_3.addWidget(self.port)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.group_credentials = QtGui.QGroupBox(self.frame_mysql)
        self.group_credentials.setObjectName(_fromUtf8("group_credentials"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.group_credentials)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.password = QtGui.QLineEdit(self.group_credentials)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.password.sizePolicy().hasHeightForWidth())
        self.password.setSizePolicy(sizePolicy)
        self.password.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.password.setObjectName(_fromUtf8("password"))
        self.gridLayout.addWidget(self.password, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.group_credentials)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.button_create_user = QtGui.QPushButton(self.group_credentials)
        self.button_create_user.setObjectName(_fromUtf8("button_create_user"))
        self.gridLayout.addWidget(self.button_create_user, 0, 2, 1, 1)
        self.user = QtGui.QLineEdit(self.group_credentials)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user.sizePolicy().hasHeightForWidth())
        self.user.setSizePolicy(sizePolicy)
        self.user.setObjectName(_fromUtf8("user"))
        self.gridLayout.addWidget(self.user, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.group_credentials)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.verticalLayout_6.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.group_credentials)
        self.connection_indicator = QtGui.QFrame(self.frame_mysql)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connection_indicator.sizePolicy().hasHeightForWidth())
        self.connection_indicator.setSizePolicy(sizePolicy)
        self.connection_indicator.setFrameShape(frameShape)
        self.connection_indicator.setFrameShadow(QtGui.QFrame.Sunken)
        self.connection_indicator.setObjectName(_fromUtf8("connection_indicator"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.connection_indicator)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_6 = QtGui.QLabel(self.connection_indicator)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout.addWidget(self.label_6)
        self.button_status = QtGui.QPushButton(self.connection_indicator)
        self.button_status.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_status.sizePolicy().hasHeightForWidth())
        self.button_status.setSizePolicy(sizePolicy)
        self.button_status.setText(_fromUtf8(""))
        self.button_status.setAutoDefault(False)
        self.button_status.setFlat(False)
        self.button_status.setObjectName(_fromUtf8("button_status"))
        self.horizontalLayout.addWidget(self.button_status)
        self.verticalLayout_7.addLayout(self.horizontalLayout)
        self.scrollArea = QtGui.QScrollArea(self.connection_indicator)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 238, 72))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_8.setMargin(0)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.label_connection = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_connection.sizePolicy().hasHeightForWidth())
        self.label_connection.setSizePolicy(sizePolicy)
        self.label_connection.setText(_fromUtf8(""))
        self.label_connection.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_connection.setWordWrap(True)
        self.label_connection.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_connection.setObjectName(_fromUtf8("label_connection"))
        self.verticalLayout_8.addWidget(self.label_connection)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_7.addWidget(self.scrollArea)
        self.verticalLayout_9.addLayout(self.verticalLayout_7)
        self.verticalLayout_2.addWidget(self.connection_indicator)
        self.verticalLayout_5.addWidget(self.frame_mysql)
        self.frame_sqlite = QtGui.QGroupBox(self.frame_settings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_sqlite.sizePolicy().hasHeightForWidth())
        self.frame_sqlite.setSizePolicy(sizePolicy)
        self.frame_sqlite.setObjectName(_fromUtf8("frame_sqlite"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.frame_sqlite)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.input_db_path = QtGui.QLineEdit(self.frame_sqlite)
        self.input_db_path.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_db_path.sizePolicy().hasHeightForWidth())
        self.input_db_path.setSizePolicy(sizePolicy)
        self.input_db_path.setObjectName(_fromUtf8("input_db_path"))
        self.horizontalLayout_4.addWidget(self.input_db_path)
        self.button_db_path = QtGui.QPushButton(self.frame_sqlite)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_db_path.sizePolicy().hasHeightForWidth())
        self.button_db_path.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("folder"))
        self.button_db_path.setIcon(icon)
        self.button_db_path.setObjectName(_fromUtf8("button_db_path"))
        self.horizontalLayout_4.addWidget(self.button_db_path)
        self.verticalLayout_5.addWidget(self.frame_sqlite)
        self.verticalLayout_11.addWidget(self.frame_settings)
        spacerItem = QtGui.QSpacerItem(40, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.verticalLayout_11.addItem(spacerItem)
        self.verticalLayout_11.setStretch(2, 1)
        self.horizontalLayout_5.addLayout(self.verticalLayout_11)
        self.verticalLayout_12.addLayout(self.horizontalLayout_5)
        self.buttonBox = QtGui.QDialogButtonBox(ConnectionConfig)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_12.addWidget(self.buttonBox)
        self.label_5.setBuddy(self.tree_configuration)
        self.label_3.setBuddy(self.configuration_name)
        self.label_4.setBuddy(self.port)
        self.label.setBuddy(self.user)
        self.label_2.setBuddy(self.password)

        self.retranslateUi(ConnectionConfig)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConnectionConfig.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConnectionConfig.reject)
        QtCore.QMetaObject.connectSlotsByName(ConnectionConfig)
        ConnectionConfig.setTabOrder(self.button_add, self.button_replace)
        ConnectionConfig.setTabOrder(self.button_replace, self.button_remove)
        ConnectionConfig.setTabOrder(self.button_remove, self.buttonBox)
        ConnectionConfig.setTabOrder(self.buttonBox, self.tree_configuration)

    def retranslateUi(self, ConnectionConfig):
        ConnectionConfig.setWindowTitle(_translate("ConnectionConfig", "Database connections – Coquery", None))
        self.label_5.setText(_translate("ConnectionConfig", "<html><head/><body><p><span style=\" font-weight:600;\">Database connections</span></p>", None))
        self.button_add.setText(_translate("ConnectionConfig", "A&dd", None))
        self.button_replace.setText(_translate("ConnectionConfig", "Replace", None))
        self.button_remove.setText(_translate("ConnectionConfig", "Re&move", None))
        self.label_3.setText(_translate("ConnectionConfig", "Connection &name:", None))
        self.configuration_name.setText(_translate("ConnectionConfig", "Default", None))
        self.radio_mysql.setText(_translate("ConnectionConfig", "&Yes", None))
        self.radio_sqlite.setText(_translate("ConnectionConfig", "&No", None))
        self.label_7.setText(_translate("ConnectionConfig", "Use MySQL server:", None))
        self.groupBox.setTitle(_translate("ConnectionConfig", "Server location", None))
        self.radio_local.setText(_translate("ConnectionConfig", "&Local server on this computer", None))
        self.radio_remote.setText(_translate("ConnectionConfig", "URL or IP address:", None))
        self.hostname.setPlaceholderText(_translate("ConnectionConfig", "(URL or IP address)", None))
        self.label_4.setText(_translate("ConnectionConfig", "&Port number:", None))
        self.group_credentials.setTitle(_translate("ConnectionConfig", "User credentials", None))
        self.password.setText(_translate("ConnectionConfig", "coquery", None))
        self.label.setText(_translate("ConnectionConfig", "&User name:", None))
        self.button_create_user.setText(_translate("ConnectionConfig", "&Create user", None))
        self.user.setText(_translate("ConnectionConfig", "coquery", None))
        self.label_2.setText(_translate("ConnectionConfig", "Pass&word:", None))
        self.label_6.setText(_translate("ConnectionConfig", "Connection status:", None))
        self.frame_sqlite.setTitle(_translate("ConnectionConfig", "&Database directory:", None))
        self.input_db_path.setPlaceholderText(_translate("ConnectionConfig", "(use default directory)", None))
        self.button_db_path.setText(_translate("ConnectionConfig", "&Browse", None))
        self.button_db_path.setShortcut(_translate("ConnectionConfig", "Alt+B", None))



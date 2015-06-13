# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'csvOptions.ui'
#
# Created by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui

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

class Ui_FileOptions(object):
    def setupUi(self, FileOptions):
        FileOptions.setObjectName(_fromUtf8("FileOptions"))
        FileOptions.resize(640, 480)
        FileOptions.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout_2 = QtGui.QVBoxLayout(FileOptions)
        self.verticalLayout_2.setContentsMargins(10, -1, 10, -1)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.FilePreviewArea = QtGui.QTableView(FileOptions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FilePreviewArea.sizePolicy().hasHeightForWidth())
        self.FilePreviewArea.setSizePolicy(sizePolicy)
        self.FilePreviewArea.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.FilePreviewArea.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.FilePreviewArea.setAlternatingRowColors(True)
        self.FilePreviewArea.setSelectionBehavior(QtGui.QAbstractItemView.SelectColumns)
        self.FilePreviewArea.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.FilePreviewArea.setObjectName(_fromUtf8("FilePreviewArea"))
        self.verticalLayout_2.addWidget(self.FilePreviewArea)
        self.OptionsBox = QtGui.QFrame(FileOptions)
        self.OptionsBox.setObjectName(_fromUtf8("OptionsBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.OptionsBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.separate_char = QtGui.QComboBox(self.OptionsBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.separate_char.sizePolicy().hasHeightForWidth())
        self.separate_char.setSizePolicy(sizePolicy)
        self.separate_char.setEditable(True)
        self.separate_char.setObjectName(_fromUtf8("separate_char"))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.separate_char, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.OptionsBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_10 = QtGui.QLabel(self.OptionsBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout.addWidget(self.label_10, 0, 0, 1, 1)
        self.ignore_lines = QtGui.QSpinBox(self.OptionsBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ignore_lines.sizePolicy().hasHeightForWidth())
        self.ignore_lines.setSizePolicy(sizePolicy)
        self.ignore_lines.setObjectName(_fromUtf8("ignore_lines"))
        self.gridLayout.addWidget(self.ignore_lines, 3, 1, 1, 1)
        self.file_has_headers = QtGui.QCheckBox(self.OptionsBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.file_has_headers.sizePolicy().hasHeightForWidth())
        self.file_has_headers.setSizePolicy(sizePolicy)
        self.file_has_headers.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.file_has_headers.setText(_fromUtf8(""))
        self.file_has_headers.setObjectName(_fromUtf8("file_has_headers"))
        self.gridLayout.addWidget(self.file_has_headers, 2, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.OptionsBox)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)
        self.query_column = QtGui.QSpinBox(self.OptionsBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.query_column.sizePolicy().hasHeightForWidth())
        self.query_column.setSizePolicy(sizePolicy)
        self.query_column.setMinimum(1)
        self.query_column.setMaximum(999)
        self.query_column.setObjectName(_fromUtf8("query_column"))
        self.gridLayout.addWidget(self.query_column, 1, 1, 1, 1)
        self.label_9 = QtGui.QLabel(self.OptionsBox)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.OptionsBox)
        self.buttonBox = QtGui.QDialogButtonBox(FileOptions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(FileOptions)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FileOptions.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FileOptions.reject)
        QtCore.QMetaObject.connectSlotsByName(FileOptions)

    def retranslateUi(self, FileOptions):
        FileOptions.setWindowTitle(_translate("FileOptions", "Input file options", None))
        self.separate_char.setItemText(0, _translate("FileOptions", ",", None))
        self.separate_char.setItemText(1, _translate("FileOptions", ";", None))
        self.separate_char.setItemText(2, _translate("FileOptions", ":", None))
        self.separate_char.setItemText(3, _translate("FileOptions", "#", None))
        self.separate_char.setItemText(4, _translate("FileOptions", "{tab}", None))
        self.separate_char.setItemText(5, _translate("FileOptions", "{space}", None))
        self.label.setText(_translate("FileOptions", "File contains header:", None))
        self.label_10.setText(_translate("FileOptions", "Character that separates columns:", None))
        self.label_6.setText(_translate("FileOptions", "Text lines to ignore after header:", None))
        self.label_9.setText(_translate("FileOptions", "Read queries from column number:", None))


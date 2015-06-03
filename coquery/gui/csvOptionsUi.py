# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'csv_options.ui'
#
# Created by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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
        self.buttonBox = QtGui.QDialogButtonBox(FileOptions)
        self.buttonBox.setGeometry(QtCore.QRect(10, 440, 621, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.FilePreviewArea = QtGui.QTableView(FileOptions)
        self.FilePreviewArea.setGeometry(QtCore.QRect(10, 5, 620, 260))
        self.FilePreviewArea.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.FilePreviewArea.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.FilePreviewArea.setAlternatingRowColors(True)
        self.FilePreviewArea.setSelectionBehavior(QtGui.QAbstractItemView.SelectColumns)
        self.FilePreviewArea.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.FilePreviewArea.setObjectName(_fromUtf8("FilePreviewArea"))
        self.OptionsBox = QtGui.QGroupBox(FileOptions)
        self.OptionsBox.setGeometry(QtCore.QRect(10, 270, 620, 170))
        self.OptionsBox.setObjectName(_fromUtf8("OptionsBox"))
        self.layoutWidget = QtGui.QWidget(self.OptionsBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 601, 150))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_10 = QtGui.QLabel(self.layoutWidget)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout.addWidget(self.label_10, 0, 0, 1, 1)
        self.separate_char = QtGui.QComboBox(self.layoutWidget)
        self.separate_char.setEditable(True)
        self.separate_char.setObjectName(_fromUtf8("separate_char"))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.separate_char.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.separate_char, 0, 2, 1, 1)
        self.label_9 = QtGui.QLabel(self.layoutWidget)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 1, 0, 1, 1)
        self.query_column = QtGui.QSpinBox(self.layoutWidget)
        self.query_column.setMinimum(1)
        self.query_column.setMaximum(999)
        self.query_column.setObjectName(_fromUtf8("query_column"))
        self.gridLayout.addWidget(self.query_column, 1, 2, 1, 1)
        self.label_6 = QtGui.QLabel(self.layoutWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.ignore_lines = QtGui.QSpinBox(self.layoutWidget)
        self.ignore_lines.setObjectName(_fromUtf8("ignore_lines"))
        self.gridLayout.addWidget(self.ignore_lines, 3, 2, 1, 1)
        self.file_has_headers = QtGui.QCheckBox(self.layoutWidget)
        self.file_has_headers.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.file_has_headers.setText(_fromUtf8(""))
        self.file_has_headers.setObjectName(_fromUtf8("file_has_headers"))
        self.gridLayout.addWidget(self.file_has_headers, 2, 2, 1, 1)
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.layoutWidget1 = QtGui.QWidget(FileOptions)
        self.layoutWidget1.setGeometry(QtCore.QRect(0, 0, 2, 2))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))

        self.retranslateUi(FileOptions)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FileOptions.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FileOptions.reject)
        QtCore.QMetaObject.connectSlotsByName(FileOptions)

    def retranslateUi(self, FileOptions):
        FileOptions.setWindowTitle(_translate("FileOptions", "Input file options", None))
        self.label_10.setText(_translate("FileOptions", "Character that separates columns:", None))
        self.separate_char.setItemText(0, _translate("FileOptions", ",", None))
        self.separate_char.setItemText(1, _translate("FileOptions", ";", None))
        self.separate_char.setItemText(2, _translate("FileOptions", ":", None))
        self.separate_char.setItemText(3, _translate("FileOptions", "#", None))
        self.separate_char.setItemText(4, _translate("FileOptions", "{tab}", None))
        self.separate_char.setItemText(5, _translate("FileOptions", "{space}", None))
        self.label_9.setText(_translate("FileOptions", "Read queries from column number:", None))
        self.label_6.setText(_translate("FileOptions", "Text lines to ignore after header:", None))
        self.label.setText(_translate("FileOptions", "File contains header:", None))


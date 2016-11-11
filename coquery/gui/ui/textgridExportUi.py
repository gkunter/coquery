# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'textgridExport.ui'
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

class Ui_TextgridExport(object):
    def setupUi(self, TextgridExport):
        TextgridExport.setObjectName(_fromUtf8("TextgridExport"))
        TextgridExport.resize(640, 480)
        self.verticalLayout_3 = QtGui.QVBoxLayout(TextgridExport)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(TextgridExport)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.edit_output_path = QtGui.QLineEdit(TextgridExport)
        self.edit_output_path.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_output_path.sizePolicy().hasHeightForWidth())
        self.edit_output_path.setSizePolicy(sizePolicy)
        self.edit_output_path.setAccessibleDescription(_fromUtf8(""))
        self.edit_output_path.setObjectName(_fromUtf8("edit_output_path"))
        self.horizontalLayout.addWidget(self.edit_output_path)
        self.button_output_path = QtGui.QPushButton(TextgridExport)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_output_path.sizePolicy().hasHeightForWidth())
        self.button_output_path.setSizePolicy(sizePolicy)
        self.button_output_path.setObjectName(_fromUtf8("button_output_path"))
        self.horizontalLayout.addWidget(self.button_output_path)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.groupbox = QtGui.QGroupBox(TextgridExport)
        self.groupbox.setObjectName(_fromUtf8("groupbox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupbox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.list_columns = QtGui.QListWidget(self.groupbox)
        self.list_columns.setObjectName(_fromUtf8("list_columns"))
        self.verticalLayout.addWidget(self.list_columns)
        self.groupbox1 = QtGui.QGroupBox(self.groupbox)
        self.groupbox1.setObjectName(_fromUtf8("groupbox1"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupbox1)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.radio_one_per_match = QtGui.QRadioButton(self.groupbox1)
        self.radio_one_per_match.setObjectName(_fromUtf8("radio_one_per_match"))
        self.verticalLayout_2.addWidget(self.radio_one_per_match)
        self.radio_one_per_file = QtGui.QRadioButton(self.groupbox1)
        self.radio_one_per_file.setObjectName(_fromUtf8("radio_one_per_file"))
        self.verticalLayout_2.addWidget(self.radio_one_per_file)
        self.verticalLayout.addWidget(self.groupbox1)
        self.verticalLayout_3.addWidget(self.groupbox)
        self.groupbox2 = QtGui.QGroupBox(TextgridExport)
        self.groupbox2.setObjectName(_fromUtf8("groupbox2"))
        self.gridLayout = QtGui.QGridLayout(self.groupbox2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.check_copy_sounds = QtGui.QCheckBox(self.groupbox2)
        self.check_copy_sounds.setText(_fromUtf8(""))
        self.check_copy_sounds.setObjectName(_fromUtf8("check_copy_sounds"))
        self.gridLayout.addWidget(self.check_copy_sounds, 0, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupbox2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 1, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_3 = QtGui.QLabel(self.groupbox2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.edit_sound_path = QtGui.QLineEdit(self.groupbox2)
        self.edit_sound_path.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_sound_path.sizePolicy().hasHeightForWidth())
        self.edit_sound_path.setSizePolicy(sizePolicy)
        self.edit_sound_path.setAccessibleDescription(_fromUtf8(""))
        self.edit_sound_path.setObjectName(_fromUtf8("edit_sound_path"))
        self.horizontalLayout_2.addWidget(self.edit_sound_path)
        self.button_sound_path = QtGui.QPushButton(self.groupbox2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_sound_path.sizePolicy().hasHeightForWidth())
        self.button_sound_path.setSizePolicy(sizePolicy)
        self.button_sound_path.setObjectName(_fromUtf8("button_sound_path"))
        self.horizontalLayout_2.addWidget(self.button_sound_path)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.groupbox2)
        self.buttonBox = QtGui.QDialogButtonBox(TextgridExport)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.label.setBuddy(self.edit_output_path)
        self.label_3.setBuddy(self.edit_sound_path)

        self.retranslateUi(TextgridExport)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TextgridExport.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TextgridExport.accept)
        QtCore.QMetaObject.connectSlotsByName(TextgridExport)

    def retranslateUi(self, TextgridExport):
        TextgridExport.setWindowTitle(_translate("TextgridExport", "Export to text grids – Coquery", None))
        self.label.setText(_translate("TextgridExport", "&Output path:", None))
        self.edit_output_path.setPlaceholderText(_translate("TextgridExport", "Input path name", None))
        self.button_output_path.setText(_translate("TextgridExport", "&Browse", None))
        self.button_output_path.setShortcut(_translate("TextgridExport", "Alt+B", None))
        self.groupbox.setTitle(_translate("TextgridExport", "Column selection", None))
        self.groupbox1.setTitle(_translate("TextgridExport", "Text grid creation", None))
        self.radio_one_per_match.setText(_translate("TextgridExport", "Create one text grid for each match", None))
        self.radio_one_per_file.setText(_translate("TextgridExport", "Create one text grid for each source file", None))
        self.groupbox2.setTitle(_translate("TextgridExport", "Copy sound files", None))
        self.label_4.setText(_translate("TextgridExport", "Copy matching sound files to output path", None))
        self.label_3.setText(_translate("TextgridExport", "&Sound file path:", None))
        self.edit_sound_path.setPlaceholderText(_translate("TextgridExport", "Input path name", None))
        self.button_sound_path.setText(_translate("TextgridExport", "&Browse", None))
        self.button_sound_path.setShortcut(_translate("TextgridExport", "Alt+B", None))



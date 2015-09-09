# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'functionApply.ui'
#
# Created: Wed Sep  9 11:59:27 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui, frameShadow

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

class Ui_FunctionDialog(object):
    def setupUi(self, FunctionDialog):
        FunctionDialog.setObjectName(_fromUtf8("FunctionDialog"))
        FunctionDialog.resize(640, 480)
        self.verticalLayout_2 = QtGui.QVBoxLayout(FunctionDialog)
        self.verticalLayout_2.setSpacing(16)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(FunctionDialog)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(8, 6, 8, 6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_description = QtGui.QLabel(self.frame)
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.verticalLayout.addWidget(self.label_description)
        self.frame1 = QtGui.QFrame(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame1.sizePolicy().hasHeightForWidth())
        self.frame1.setSizePolicy(sizePolicy)
        self.frame1.setObjectName(_fromUtf8("frame1"))
        self.gridLayout = QtGui.QGridLayout(self.frame1)
        self.gridLayout.setContentsMargins(8, 6, 8, 6)
        self.gridLayout.setHorizontalSpacing(16)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.frame1)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 1, 1, 1)
        self.label = QtGui.QLabel(self.frame1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 1, 1, 1)
        self.radio_length = QtGui.QRadioButton(self.frame1)
        self.radio_length.setChecked(False)
        self.radio_length.setObjectName(_fromUtf8("radio_length"))
        self.gridLayout.addWidget(self.radio_length, 3, 0, 1, 1)
        self.radio_count = QtGui.QRadioButton(self.frame1)
        self.radio_count.setChecked(True)
        self.radio_count.setObjectName(_fromUtf8("radio_count"))
        self.gridLayout.addWidget(self.radio_count, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame1)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 5, 1, 1, 1)
        self.radio_regexp = QtGui.QRadioButton(self.frame1)
        self.radio_regexp.setObjectName(_fromUtf8("radio_regexp"))
        self.gridLayout.addWidget(self.radio_regexp, 5, 0, 1, 1)
        self.radio_match = QtGui.QRadioButton(self.frame1)
        self.radio_match.setObjectName(_fromUtf8("radio_match"))
        self.gridLayout.addWidget(self.radio_match, 4, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.frame1)
        self.label_5.setWordWrap(False)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.label_4)
        self.edit_function_value = QtGui.QLineEdit(self.frame)
        self.edit_function_value.setObjectName(_fromUtf8("edit_function_value"))
        self.horizontalLayout.addWidget(self.edit_function_value)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_2.addWidget(self.frame)
        self.buttonBox = QtGui.QDialogButtonBox(FunctionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(FunctionDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FunctionDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FunctionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FunctionDialog)

    def retranslateUi(self, FunctionDialog):
        FunctionDialog.setWindowTitle(_translate("FunctionDialog", "Apply a function – Coquery", None))
        self.label_description.setText(_translate("FunctionDialog", "<html><head/><body><p>Apply a function to the column <span style=\" font-weight:600;\">{}.{}:</span></p></body></html>", None))
        self.label_2.setText(_translate("FunctionDialog", "Count the number of characters of {}", None))
        self.label.setText(_translate("FunctionDialog", "Count the occurrences of the parameter within {}", None))
        self.radio_length.setText(_translate("FunctionDialog", "&LENGTH", None))
        self.radio_count.setText(_translate("FunctionDialog", "&COUNT", None))
        self.label_3.setText(_translate("FunctionDialog", "<html><head/><body><p>Match {} with the parameter as a <a href=\"https://docs.python.org/2/howto/regex.html\"><span style=\" text-decoration: underline; color:#0057ae;\">regular expression</span></a>, and show the matching string.</p></body></html>", None))
        self.radio_regexp.setText(_translate("FunctionDialog", "&REGEXP", None))
        self.radio_match.setText(_translate("FunctionDialog", "&MATCH", None))
        self.label_5.setText(_translate("FunctionDialog", "Show \'yes\' if the parameter matches {} as a <a href=\"https://docs.python.org/2/howto/regex.html\"><span style=\" text-decoration: underline; color:#0057ae;\">regular expression</span></a>, otherwise \'no\'", None))
        self.label_4.setText(_translate("FunctionDialog", "Parameter", None))



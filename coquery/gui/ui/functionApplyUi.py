# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'functionApply.ui'
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

class Ui_FunctionDialog(object):
    def setupUi(self, FunctionDialog):
        FunctionDialog.setObjectName(_fromUtf8("FunctionDialog"))
        FunctionDialog.resize(520, 480)
        self.verticalLayout_2 = QtGui.QVBoxLayout(FunctionDialog)
        self.verticalLayout_2.setSpacing(16)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(FunctionDialog)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(8, 6, 8, 6)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_description = QtGui.QLabel(self.frame)
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.verticalLayout.addWidget(self.label_description)
        self.frame1 = QtGui.QFrame(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame1.sizePolicy().hasHeightForWidth())
        self.frame1.setSizePolicy(sizePolicy)
        self.frame1.setObjectName(_fromUtf8("frame1"))
        self.gridLayout = QtGui.QGridLayout(self.frame1)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.gridLayout.setContentsMargins(8, 6, 8, 6)
        self.gridLayout.setHorizontalSpacing(16)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_func2 = QtGui.QLabel(self.frame1)
        self.label_func2.setWordWrap(False)
        self.label_func2.setObjectName(_fromUtf8("label_func2"))
        self.gridLayout.addWidget(self.label_func2, 3, 1, 1, 1)
        self.label_func1 = QtGui.QLabel(self.frame1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_func1.sizePolicy().hasHeightForWidth())
        self.label_func1.setSizePolicy(sizePolicy)
        self.label_func1.setWordWrap(True)
        self.label_func1.setObjectName(_fromUtf8("label_func1"))
        self.gridLayout.addWidget(self.label_func1, 2, 1, 1, 1)
        self.radio_length = QtGui.QRadioButton(self.frame1)
        self.radio_length.setChecked(False)
        self.radio_length.setObjectName(_fromUtf8("radio_length"))
        self.gridLayout.addWidget(self.radio_length, 3, 0, 1, 1)
        self.radio_count = QtGui.QRadioButton(self.frame1)
        self.radio_count.setChecked(True)
        self.radio_count.setObjectName(_fromUtf8("radio_count"))
        self.gridLayout.addWidget(self.radio_count, 2, 0, 1, 1)
        self.label_func4 = QtGui.QLabel(self.frame1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_func4.sizePolicy().hasHeightForWidth())
        self.label_func4.setSizePolicy(sizePolicy)
        self.label_func4.setWordWrap(True)
        self.label_func4.setOpenExternalLinks(True)
        self.label_func4.setObjectName(_fromUtf8("label_func4"))
        self.gridLayout.addWidget(self.label_func4, 5, 1, 1, 1)
        self.radio_regexp = QtGui.QRadioButton(self.frame1)
        self.radio_regexp.setObjectName(_fromUtf8("radio_regexp"))
        self.gridLayout.addWidget(self.radio_regexp, 5, 0, 1, 1)
        self.radio_match = QtGui.QRadioButton(self.frame1)
        self.radio_match.setObjectName(_fromUtf8("radio_match"))
        self.gridLayout.addWidget(self.radio_match, 4, 0, 1, 1)
        self.label_func3 = QtGui.QLabel(self.frame1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_func3.sizePolicy().hasHeightForWidth())
        self.label_func3.setSizePolicy(sizePolicy)
        self.label_func3.setWordWrap(True)
        self.label_func3.setOpenExternalLinks(True)
        self.label_func3.setObjectName(_fromUtf8("label_func3"))
        self.gridLayout.addWidget(self.label_func3, 4, 1, 1, 1)
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
        FunctionDialog.setWindowTitle(_translate("FunctionDialog", "Add a function – Coquery", None))
        self.label_description.setText(_translate("FunctionDialog", "<html><head/><body><p>Add a function for the column <span style=\" font-weight:600;\">{}.{}:</span></p></body></html>", None))
        self.label_func2.setText(_translate("FunctionDialog", "Count the number of characters of \'{}\'", None))
        self.label_func1.setText(_translate("FunctionDialog", "Count the occurrences of the parameter within \'{}\'", None))
        self.radio_length.setText(_translate("FunctionDialog", "&LENGTH", None))
        self.radio_count.setText(_translate("FunctionDialog", "&COUNT", None))
        self.label_func4.setText(_translate("FunctionDialog", "<html><head/><body><p>Match \'{}\' with the parameter as a <a href=\"https://docs.python.org/2/howto/regex.html\"><span style=\" text-decoration: underline; color:#0057ae;\">regular expression</span></a>, and show the matching string.</p></body></html>", None))
        self.radio_regexp.setText(_translate("FunctionDialog", "&REGEXP", None))
        self.radio_match.setText(_translate("FunctionDialog", "&MATCH", None))
        self.label_func3.setText(_translate("FunctionDialog", "Show \'yes\' if the parameter matches \'{}\' as a <a href=\"https://docs.python.org/2/howto/regex.html\"><span style=\" text-decoration: underline; color:#0057ae;\">regular expression</span></a>, otherwise \'no\'", None))
        self.label_4.setText(_translate("FunctionDialog", "Parameter", None))



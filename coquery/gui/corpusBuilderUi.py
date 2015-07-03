# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'corpusBuilder.ui'
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

class Ui_CorpusBuilder(object):
    def setupUi(self, CorpusBuilder):
        CorpusBuilder.setObjectName(_fromUtf8("CorpusBuilder"))
        CorpusBuilder.resize(640, 283)
        CorpusBuilder.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(CorpusBuilder)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(CorpusBuilder)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.formFrame = QtGui.QFrame(CorpusBuilder)
        self.formFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.formFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.formFrame.setObjectName(_fromUtf8("formFrame"))
        self.formLayout = QtGui.QFormLayout(self.formFrame)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_2 = QtGui.QLabel(self.formFrame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.corpus_name = QtGui.QLineEdit(self.formFrame)
        self.corpus_name.setMaxLength(32)
        self.corpus_name.setObjectName(_fromUtf8("corpus_name"))
        self.horizontalLayout_3.addWidget(self.corpus_name)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.label_8 = QtGui.QLabel(self.formFrame)
        self.label_8.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_8)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.input_path = QtGui.QLineEdit(self.formFrame)
        self.input_path.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_path.sizePolicy().hasHeightForWidth())
        self.input_path.setSizePolicy(sizePolicy)
        self.input_path.setObjectName(_fromUtf8("input_path"))
        self.horizontalLayout.addWidget(self.input_path)
        self.button_input_path = QtGui.QPushButton(self.formFrame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_input_path.sizePolicy().hasHeightForWidth())
        self.button_input_path.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("folder"))
        self.button_input_path.setIcon(icon)
        self.button_input_path.setObjectName(_fromUtf8("button_input_path"))
        self.horizontalLayout.addWidget(self.button_input_path)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_3 = QtGui.QLabel(self.formFrame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.use_pos_tagging = QtGui.QCheckBox(self.formFrame)
        self.use_pos_tagging.setText(_fromUtf8(""))
        self.use_pos_tagging.setObjectName(_fromUtf8("use_pos_tagging"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.use_pos_tagging)
        self.label_4 = QtGui.QLabel(self.formFrame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_4)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lemma_path = QtGui.QLineEdit(self.formFrame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lemma_path.sizePolicy().hasHeightForWidth())
        self.lemma_path.setSizePolicy(sizePolicy)
        self.lemma_path.setText(_fromUtf8(""))
        self.lemma_path.setObjectName(_fromUtf8("lemma_path"))
        self.horizontalLayout_2.addWidget(self.lemma_path)
        self.button_lemma_path = QtGui.QPushButton(self.formFrame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_lemma_path.sizePolicy().hasHeightForWidth())
        self.button_lemma_path.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document"))
        self.button_lemma_path.setIcon(icon)
        self.button_lemma_path.setObjectName(_fromUtf8("button_lemma_path"))
        self.horizontalLayout_2.addWidget(self.button_lemma_path)
        self.formLayout.setLayout(4, QtGui.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.formFrame)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.progress_bar = QtGui.QProgressBar(CorpusBuilder)
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.verticalLayout.addWidget(self.progress_bar)
        self.buttonBox = QtGui.QDialogButtonBox(CorpusBuilder)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(CorpusBuilder)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CorpusBuilder.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CorpusBuilder.reject)
        QtCore.QMetaObject.connectSlotsByName(CorpusBuilder)

    def retranslateUi(self, CorpusBuilder):
        CorpusBuilder.setWindowTitle(_translate("CorpusBuilder", "Corpus Builder – Coquery", None))
        self.label.setText(_translate("CorpusBuilder", "<html><head/><body><p>This function will create a new corpus from a selection of text files. The corpus will afterwards be available for queries.</p></body></html>", None))
        self.label_2.setText(_translate("CorpusBuilder", "Name of new corpus", None))
        self.label_8.setText(_translate("CorpusBuilder", "Path containing text files", None))
        self.button_input_path.setText(_translate("CorpusBuilder", "Browse", None))
        self.button_input_path.setShortcut(_translate("CorpusBuilder", "Alt+B", None))
        self.label_3.setText(_translate("CorpusBuilder", "Automatic POS tagging", None))
        self.label_4.setText(_translate("CorpusBuilder", "Use lemma dictionary", None))
        self.button_lemma_path.setText(_translate("CorpusBuilder", "Browse", None))
        self.button_lemma_path.setShortcut(_translate("CorpusBuilder", "Alt+B", None))
        self.progress_bar.setFormat(_translate("CorpusBuilder", "Idle.", None))


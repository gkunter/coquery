# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'corpusBuilder.ui'
#
# Created: Sun Jul 12 20:02:47 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_CorpusBuilder(object):
    def setupUi(self, CorpusBuilder):
        CorpusBuilder.setObjectName(_fromUtf8("CorpusBuilder"))
        CorpusBuilder.resize(760, 591)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CorpusBuilder.sizePolicy().hasHeightForWidth())
        CorpusBuilder.setSizePolicy(sizePolicy)
        CorpusBuilder.setModal(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(CorpusBuilder)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(CorpusBuilder)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.frame = QtGui.QFrame(CorpusBuilder)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.corpus_name = QtGui.QLineEdit(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.corpus_name.sizePolicy().hasHeightForWidth())
        self.corpus_name.setSizePolicy(sizePolicy)
        self.corpus_name.setMaxLength(32)
        self.corpus_name.setObjectName(_fromUtf8("corpus_name"))
        self.horizontalLayout.addWidget(self.corpus_name)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.radio_build_corpus = QtGui.QRadioButton(self.frame)
        self.radio_build_corpus.setText(_fromUtf8(""))
        self.radio_build_corpus.setChecked(True)
        self.radio_build_corpus.setObjectName(_fromUtf8("radio_build_corpus"))
        self.gridLayout_2.addWidget(self.radio_build_corpus, 0, 0, 1, 1)
        self.radio_only_module = QtGui.QRadioButton(self.frame)
        self.radio_only_module.setText(_fromUtf8(""))
        self.radio_only_module.setObjectName(_fromUtf8("radio_only_module"))
        self.gridLayout_2.addWidget(self.radio_only_module, 3, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.frame)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 3, 1, 1, 1)
        self.box_build_options = QtGui.QGroupBox(self.frame)
        self.box_build_options.setObjectName(_fromUtf8("box_build_options"))
        self.gridLayout = QtGui.QGridLayout(self.box_build_options)
        self.gridLayout.setMargin(10)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.input_path = QtGui.QLineEdit(self.box_build_options)
        self.input_path.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_path.sizePolicy().hasHeightForWidth())
        self.input_path.setSizePolicy(sizePolicy)
        self.input_path.setObjectName(_fromUtf8("input_path"))
        self.gridLayout.addWidget(self.input_path, 1, 0, 1, 1)
        self.label_8 = QtGui.QLabel(self.box_build_options)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 0, 0, 1, 1)
        self.button_lemma_path = QtGui.QPushButton(self.box_build_options)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_lemma_path.sizePolicy().hasHeightForWidth())
        self.button_lemma_path.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("folder"))
        self.button_lemma_path.setIcon(icon)
        self.button_lemma_path.setObjectName(_fromUtf8("button_lemma_path"))
        self.gridLayout.addWidget(self.button_lemma_path, 5, 1, 1, 1)
        self.button_input_path = QtGui.QPushButton(self.box_build_options)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_input_path.sizePolicy().hasHeightForWidth())
        self.button_input_path.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("folder"))
        self.button_input_path.setIcon(icon)
        self.button_input_path.setObjectName(_fromUtf8("button_input_path"))
        self.gridLayout.addWidget(self.button_input_path, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.box_build_options)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.lemma_path = QtGui.QLineEdit(self.box_build_options)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lemma_path.sizePolicy().hasHeightForWidth())
        self.lemma_path.setSizePolicy(sizePolicy)
        self.lemma_path.setText(_fromUtf8(""))
        self.lemma_path.setObjectName(_fromUtf8("lemma_path"))
        self.gridLayout.addWidget(self.lemma_path, 5, 0, 1, 1)
        self.use_pos_tagging = QtGui.QCheckBox(self.box_build_options)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.use_pos_tagging.sizePolicy().hasHeightForWidth())
        self.use_pos_tagging.setSizePolicy(sizePolicy)
        self.use_pos_tagging.setObjectName(_fromUtf8("use_pos_tagging"))
        self.gridLayout.addWidget(self.use_pos_tagging, 3, 0, 1, 1)
        self.gridLayout_2.addWidget(self.box_build_options, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.verticalLayout_2.addWidget(self.frame)
        self.progress_bar = QtGui.QProgressBar(CorpusBuilder)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.verticalLayout_2.addWidget(self.progress_bar)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(CorpusBuilder)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(CorpusBuilder)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CorpusBuilder.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CorpusBuilder.reject)
        QtCore.QMetaObject.connectSlotsByName(CorpusBuilder)

    def retranslateUi(self, CorpusBuilder):
        CorpusBuilder.setWindowTitle(_translate("CorpusBuilder", "Corpus Builder – Coquery", None))
        self.label.setText(_translate("CorpusBuilder", "<html><head/><body><p>This function will create a new corpus from a selection of text files. The corpus will afterwards be available for queries.</p></body></html>", None))
        self.label_2.setText(_translate("CorpusBuilder", "Name of new corpus:", None))
        self.label_5.setText(_translate("CorpusBuilder", "Build corpus from text files", None))
        self.label_6.setText(_translate("CorpusBuilder", "Only build corpus module (use this if you have a network database server)", None))
        self.label_8.setText(_translate("CorpusBuilder", "Path to text files:", None))
        self.button_lemma_path.setText(_translate("CorpusBuilder", "Browse", None))
        self.button_lemma_path.setShortcut(_translate("CorpusBuilder", "Alt+B", None))
        self.button_input_path.setText(_translate("CorpusBuilder", "Browse", None))
        self.button_input_path.setShortcut(_translate("CorpusBuilder", "Alt+B", None))
        self.label_4.setText(_translate("CorpusBuilder", "<html><head/><body><p>Path to lemma dictionary file (optilnal):</p></body></html>", None))
        self.use_pos_tagging.setText(_translate("CorpusBuilder", "Automatic POS tagging (requires NLTK)", None))
        self.progress_bar.setFormat(_translate("CorpusBuilder", "Idle.", None))


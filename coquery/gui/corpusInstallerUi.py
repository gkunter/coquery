# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'corpusInstaller.ui'
#
# Created: Wed Nov 11 18:52:03 2015
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

class Ui_CorpusInstaller(object):
    def setupUi(self, CorpusInstaller):
        CorpusInstaller.setObjectName(_fromUtf8("CorpusInstaller"))
        CorpusInstaller.resize(797, 591)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CorpusInstaller.sizePolicy().hasHeightForWidth())
        CorpusInstaller.setSizePolicy(sizePolicy)
        CorpusInstaller.setModal(True)
        self.verticalLayout_3 = QtGui.QVBoxLayout(CorpusInstaller)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.frame = QtGui.QFrame(CorpusInstaller)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.corpus_description = QtGui.QLabel(self.frame)
        self.corpus_description.setWordWrap(True)
        self.corpus_description.setObjectName(_fromUtf8("corpus_description"))
        self.verticalLayout.addWidget(self.corpus_description)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setVerticalSpacing(10)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.radio_only_module = QtGui.QRadioButton(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radio_only_module.sizePolicy().hasHeightForWidth())
        self.radio_only_module.setSizePolicy(sizePolicy)
        self.radio_only_module.setText(_fromUtf8(""))
        self.radio_only_module.setObjectName(_fromUtf8("radio_only_module"))
        self.gridLayout_2.addWidget(self.radio_only_module, 2, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.frame)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 2, 1, 1, 1)
        self.box_build_options = QtGui.QGroupBox(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.box_build_options.sizePolicy().hasHeightForWidth())
        self.box_build_options.setSizePolicy(sizePolicy)
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
        self.gridLayout_2.addWidget(self.box_build_options, 1, 1, 1, 1)
        self.radio_install_corpus = QtGui.QRadioButton(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radio_install_corpus.sizePolicy().hasHeightForWidth())
        self.radio_install_corpus.setSizePolicy(sizePolicy)
        self.radio_install_corpus.setText(_fromUtf8(""))
        self.radio_install_corpus.setChecked(True)
        self.radio_install_corpus.setObjectName(_fromUtf8("radio_install_corpus"))
        self.gridLayout_2.addWidget(self.radio_install_corpus, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.verticalLayout_3.addWidget(self.frame)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.progress_box = QtGui.QFrame(CorpusInstaller)
        self.progress_box.setFrameShape(QtGui.QFrame.StyledPanel)
        self.progress_box.setFrameShadow(frameShadow)
        self.progress_box.setObjectName(_fromUtf8("progress_box"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.progress_box)
        self.verticalLayout_2.setMargin(10)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.progress_box)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.progress_general = QtGui.QProgressBar(self.progress_box)
        self.progress_general.setMinimum(0)
        self.progress_general.setMaximum(9)
        self.progress_general.setProperty("value", 0)
        self.progress_general.setObjectName(_fromUtf8("progress_general"))
        self.verticalLayout_2.addWidget(self.progress_general)
        self.progress_bar = QtGui.QProgressBar(self.progress_box)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setFormat(_fromUtf8(""))
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.verticalLayout_2.addWidget(self.progress_bar)
        self.verticalLayout_3.addWidget(self.progress_box)
        self.buttonBox = QtGui.QDialogButtonBox(CorpusInstaller)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(CorpusInstaller)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CorpusInstaller.reject)
        QtCore.QMetaObject.connectSlotsByName(CorpusInstaller)

    def retranslateUi(self, CorpusInstaller):
        CorpusInstaller.setWindowTitle(_translate("CorpusInstaller", "Corpus Installer – Coquery", None))
        self.corpus_description.setText(_translate("CorpusInstaller", "<html><head/><body><p>About to install: <span style=\" font-weight:600;\">{}</span> ({}).</p></body></html>", None))
        self.label_5.setText(_translate("CorpusInstaller", "Install corpus data and corpus module (if you have a local database server)", None))
        self.label_6.setText(_translate("CorpusInstaller", "Only install corpus module (if you have a network database server)", None))
        self.label_8.setText(_translate("CorpusInstaller", "Path to corpus data files:", None))
        self.button_input_path.setText(_translate("CorpusInstaller", "Browse", None))
        self.button_input_path.setShortcut(_translate("CorpusInstaller", "Alt+B", None))
        self.label.setText(_translate("CorpusInstaller", "Installing...", None))
        self.progress_general.setFormat(_translate("CorpusInstaller", "Stage %v of %m", None))



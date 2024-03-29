# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coquery/gui/ui/corpusInstaller.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CorpusInstaller(object):
    def setupUi(self, CorpusInstaller):
        CorpusInstaller.setObjectName("CorpusInstaller")
        CorpusInstaller.resize(768, 604)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CorpusInstaller.sizePolicy().hasHeightForWidth())
        CorpusInstaller.setSizePolicy(sizePolicy)
        CorpusInstaller.setModal(True)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(CorpusInstaller)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.name_label = QtWidgets.QLabel(CorpusInstaller)
        self.name_label.setObjectName("name_label")
        self.horizontalLayout.addWidget(self.name_label)
        self.corpus_name = QtWidgets.QLineEdit(CorpusInstaller)
        self.corpus_name.setMaxLength(32)
        self.corpus_name.setObjectName("corpus_name")
        self.horizontalLayout.addWidget(self.corpus_name)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.widget_options = QtWidgets.QWidget(CorpusInstaller)
        self.widget_options.setObjectName("widget_options")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_options)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_4.addWidget(self.widget_options)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setVerticalSpacing(8)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.radio_only_module = QtWidgets.QRadioButton(CorpusInstaller)
        self.radio_only_module.setText("")
        self.radio_only_module.setObjectName("radio_only_module")
        self.gridLayout_2.addWidget(self.radio_only_module, 2, 0, 1, 1)
        self.label_only_module = CoqClickableLabel(CorpusInstaller)
        self.label_only_module.setObjectName("label_only_module")
        self.gridLayout_2.addWidget(self.label_only_module, 2, 2, 1, 1)
        self.label_read_files = CoqClickableLabel(CorpusInstaller)
        self.label_read_files.setObjectName("label_read_files")
        self.gridLayout_2.addWidget(self.label_read_files, 0, 1, 1, 2)
        self.widget_read_files = QtWidgets.QWidget(CorpusInstaller)
        self.widget_read_files.setObjectName("widget_read_files")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget_read_files)
        self.verticalLayout_5.setContentsMargins(0, -1, 0, -1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_input_path = QtWidgets.QLabel(self.widget_read_files)
        self.label_input_path.setObjectName("label_input_path")
        self.horizontalLayout_3.addWidget(self.label_input_path)
        self.input_path = CoqClickableLabel(self.widget_read_files)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_path.sizePolicy().hasHeightForWidth())
        self.input_path.setSizePolicy(sizePolicy)
        self.input_path.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.input_path.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.input_path.setObjectName("input_path")
        self.horizontalLayout_3.addWidget(self.input_path)
        self.button_input_path = QtWidgets.QPushButton(self.widget_read_files)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_input_path.sizePolicy().hasHeightForWidth())
        self.button_input_path.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon.fromTheme("folder")
        self.button_input_path.setIcon(icon)
        self.button_input_path.setObjectName("button_input_path")
        self.horizontalLayout_3.addWidget(self.button_input_path)
        self.horizontalLayout_3.setStretch(1, 1)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.groupBox = QtWidgets.QGroupBox(self.widget_read_files)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.check_use_metafile = QtWidgets.QCheckBox(self.groupBox)
        self.check_use_metafile.setObjectName("check_use_metafile")
        self.horizontalLayout_2.addWidget(self.check_use_metafile)
        self.label_metafile = CoqClickableLabel(self.groupBox)
        self.label_metafile.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_metafile.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.label_metafile.setText("")
        self.label_metafile.setObjectName("label_metafile")
        self.horizontalLayout_2.addWidget(self.label_metafile)
        self.button_metafile = QtWidgets.QPushButton(self.groupBox)
        icon = QtGui.QIcon.fromTheme("document-open")
        self.button_metafile.setIcon(icon)
        self.button_metafile.setObjectName("button_metafile")
        self.horizontalLayout_2.addWidget(self.button_metafile)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.layout_nltk = QtWidgets.QHBoxLayout()
        self.layout_nltk.setObjectName("layout_nltk")
        self.use_pos_tagging = QtWidgets.QCheckBox(self.groupBox)
        self.use_pos_tagging.setText("")
        self.use_pos_tagging.setObjectName("use_pos_tagging")
        self.layout_nltk.addWidget(self.use_pos_tagging)
        self.label_pos_tagging = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_pos_tagging.sizePolicy().hasHeightForWidth())
        self.label_pos_tagging.setSizePolicy(sizePolicy)
        self.label_pos_tagging.setText("")
        self.label_pos_tagging.setWordWrap(True)
        self.label_pos_tagging.setObjectName("label_pos_tagging")
        self.layout_nltk.addWidget(self.label_pos_tagging)
        self.verticalLayout.addLayout(self.layout_nltk)
        self.widget_n_gram = QtWidgets.QWidget(self.groupBox)
        self.widget_n_gram.setObjectName("widget_n_gram")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_n_gram)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.check_n_gram = QtWidgets.QCheckBox(self.widget_n_gram)
        self.check_n_gram.setObjectName("check_n_gram")
        self.horizontalLayout_4.addWidget(self.check_n_gram)
        self.spin_n = QtWidgets.QSpinBox(self.widget_n_gram)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spin_n.sizePolicy().hasHeightForWidth())
        self.spin_n.setSizePolicy(sizePolicy)
        self.spin_n.setMinimum(2)
        self.spin_n.setProperty("value", 2)
        self.spin_n.setObjectName("spin_n")
        self.horizontalLayout_4.addWidget(self.spin_n)
        spacerItem = QtWidgets.QSpacerItem(37, 23, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout.addWidget(self.widget_n_gram)
        self.verticalLayout_5.addWidget(self.groupBox)
        self.gridLayout_2.addWidget(self.widget_read_files, 1, 2, 1, 1)
        self.radio_read_files = QtWidgets.QRadioButton(CorpusInstaller)
        self.radio_read_files.setText("")
        self.radio_read_files.setObjectName("radio_read_files")
        self.gridLayout_2.addWidget(self.radio_read_files, 0, 0, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout_2)
        self.issue_label = QtWidgets.QLabel(CorpusInstaller)
        self.issue_label.setObjectName("issue_label")
        self.verticalLayout_4.addWidget(self.issue_label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.progress_box = QtWidgets.QFrame(CorpusInstaller)
        self.progress_box.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.progress_box.setFrameShadow(QtWidgets.QFrame.Raised)
        self.progress_box.setObjectName("progress_box")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.progress_box)
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.progress_box)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.progress_general = QtWidgets.QProgressBar(self.progress_box)
        self.progress_general.setMinimum(0)
        self.progress_general.setMaximum(9)
        self.progress_general.setProperty("value", 0)
        self.progress_general.setObjectName("progress_general")
        self.verticalLayout_2.addWidget(self.progress_general)
        self.progress_bar = QtWidgets.QProgressBar(self.progress_box)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setFormat("")
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout_2.addWidget(self.progress_bar)
        self.verticalLayout_4.addWidget(self.progress_box)
        self.buttonBox = QtWidgets.QDialogButtonBox(CorpusInstaller)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_4.addWidget(self.buttonBox)
        self.name_label.setBuddy(self.corpus_name)
        self.label_only_module.setBuddy(self.radio_only_module)
        self.label_read_files.setBuddy(self.radio_read_files)
        self.label_input_path.setBuddy(self.input_path)

        self.retranslateUi(CorpusInstaller)
        self.buttonBox.rejected.connect(CorpusInstaller.reject)
        QtCore.QMetaObject.connectSlotsByName(CorpusInstaller)

    def retranslateUi(self, CorpusInstaller):
        _translate = QtCore.QCoreApplication.translate
        CorpusInstaller.setWindowTitle(_translate("CorpusInstaller", "Corpus Installer – Coquery"))
        self.name_label.setText(_translate("CorpusInstaller", "&Corpus name:"))
        self.label_only_module.setText(_translate("CorpusInstaller", "Only install corpus &module"))
        self.label_read_files.setText(_translate("CorpusInstaller", "Build corpus from &text files"))
        self.label_input_path.setText(_translate("CorpusInstaller", "Directory containg &text files:"))
        self.input_path.setText(_translate("CorpusInstaller", "(no path or file selected)"))
        self.button_input_path.setText(_translate("CorpusInstaller", "&Browse"))
        self.button_input_path.setShortcut(_translate("CorpusInstaller", "Alt+B"))
        self.groupBox.setTitle(_translate("CorpusInstaller", "Options"))
        self.check_use_metafile.setText(_translate("CorpusInstaller", "Use &meta data file:"))
        self.button_metafile.setText(_translate("CorpusInstaller", "&Open"))
        self.check_n_gram.setText(_translate("CorpusInstaller", "&Generate lookup table for multi-item query strings,"))
        self.spin_n.setSuffix(_translate("CorpusInstaller", " items"))
        self.spin_n.setPrefix(_translate("CorpusInstaller", "up to "))
        self.issue_label.setText(_translate("CorpusInstaller", "TextLabel"))
        self.label.setText(_translate("CorpusInstaller", "Installing..."))
        self.progress_general.setFormat(_translate("CorpusInstaller", "Stage %v of %m"))

from ..classes import CoqClickableLabel

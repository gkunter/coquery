# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wizard.ui'
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

class Ui_Wizard(object):
    def setupUi(self, Wizard):
        Wizard.setObjectName(_fromUtf8("Wizard"))
        Wizard.resize(800, 600)
        self.Welcome = QtGui.QWizardPage()
        self.Welcome.setTitle(_fromUtf8(""))
        self.Welcome.setSubTitle(_fromUtf8(""))
        self.Welcome.setObjectName(_fromUtf8("Welcome"))
        self.layoutWidget = QtGui.QWidget(self.Welcome)
        self.layoutWidget.setGeometry(QtCore.QRect(60, 70, 665, 394))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_3 = QtGui.QLabel(self.layoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.Logo = QtGui.QLabel(self.layoutWidget)
        self.Logo.setText(_fromUtf8(""))
        self.Logo.setPixmap(QtGui.QPixmap(_fromUtf8("../../.designer/backup/logo.png")))
        self.Logo.setObjectName(_fromUtf8("Logo"))
        self.horizontalLayout_2.addWidget(self.Logo)
        Wizard.addPage(self.Welcome)
        self.CorpusSelection = QtGui.QWizardPage()
        self.CorpusSelection.setObjectName(_fromUtf8("CorpusSelection"))
        self.frame_2 = QtGui.QFrame(self.CorpusSelection)
        self.frame_2.setGeometry(QtCore.QRect(20, 20, 750, 510))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.groupBox = QtGui.QGroupBox(self.frame_2)
        self.groupBox.setGeometry(QtCore.QRect(40, 40, 650, 91))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.combo_corpus = QtGui.QComboBox(self.groupBox)
        self.combo_corpus.setObjectName(_fromUtf8("combo_corpus"))
        self.horizontalLayout.addWidget(self.combo_corpus)
        self.groupBox1 = QtGui.QGroupBox(self.frame_2)
        self.groupBox1.setGeometry(QtCore.QRect(40, 180, 650, 170))
        self.groupBox1.setObjectName(_fromUtf8("groupBox1"))
        self.layoutWidget1 = QtGui.QWidget(self.groupBox1)
        self.layoutWidget1.setGeometry(QtCore.QRect(21, 47, 169, 94))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.radio_mode_context = QtGui.QRadioButton(self.layoutWidget1)
        self.radio_mode_context.setChecked(True)
        self.radio_mode_context.setObjectName(_fromUtf8("radio_mode_context"))
        self.verticalLayout.addWidget(self.radio_mode_context)
        self.radio_mode_frequency = QtGui.QRadioButton(self.layoutWidget1)
        self.radio_mode_frequency.setObjectName(_fromUtf8("radio_mode_frequency"))
        self.verticalLayout.addWidget(self.radio_mode_frequency)
        self.radio_mode_statistics = QtGui.QRadioButton(self.layoutWidget1)
        self.radio_mode_statistics.setObjectName(_fromUtf8("radio_mode_statistics"))
        self.verticalLayout.addWidget(self.radio_mode_statistics)
        Wizard.addPage(self.CorpusSelection)
        self.InputSelection = QtGui.QWizardPage()
        self.InputSelection.setObjectName(_fromUtf8("InputSelection"))
        self.label_4 = QtGui.QLabel(self.InputSelection)
        self.label_4.setGeometry(QtCore.QRect(70, 130, 401, 28))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.QueryStringBox = QtGui.QGroupBox(self.InputSelection)
        self.QueryStringBox.setGeometry(QtCore.QRect(40, 170, 710, 231))
        self.QueryStringBox.setObjectName(_fromUtf8("QueryStringBox"))
        self.edit_query_string = QtGui.QLineEdit(self.QueryStringBox)
        self.edit_query_string.setGeometry(QtCore.QRect(50, 40, 631, 30))
        self.edit_query_string.setObjectName(_fromUtf8("edit_query_string"))
        self.label_12 = QtGui.QLabel(self.QueryStringBox)
        self.label_12.setGeometry(QtCore.QRect(50, 23, 111, 16))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.radio_query_string = QtGui.QRadioButton(self.QueryStringBox)
        self.radio_query_string.setGeometry(QtCore.QRect(20, 20, 25, 21))
        self.radio_query_string.setText(_fromUtf8(""))
        self.radio_query_string.setChecked(True)
        self.radio_query_string.setObjectName(_fromUtf8("radio_query_string"))
        self.button_file_options = QtGui.QToolButton(self.QueryStringBox)
        self.button_file_options.setEnabled(False)
        self.button_file_options.setGeometry(QtCore.QRect(600, 170, 80, 24))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_file_options.sizePolicy().hasHeightForWidth())
        self.button_file_options.setSizePolicy(sizePolicy)
        self.button_file_options.setCheckable(False)
        self.button_file_options.setObjectName(_fromUtf8("button_file_options"))
        self.label_8 = QtGui.QLabel(self.QueryStringBox)
        self.label_8.setGeometry(QtCore.QRect(50, 113, 139, 24))
        self.label_8.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.radio_query_file = QtGui.QRadioButton(self.QueryStringBox)
        self.radio_query_file.setGeometry(QtCore.QRect(20, 110, 25, 21))
        self.radio_query_file.setText(_fromUtf8(""))
        self.radio_query_file.setObjectName(_fromUtf8("radio_query_file"))
        self.button_browse_file = QtGui.QPushButton(self.QueryStringBox)
        self.button_browse_file.setGeometry(QtCore.QRect(600, 133, 80, 24))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_browse_file.sizePolicy().hasHeightForWidth())
        self.button_browse_file.setSizePolicy(sizePolicy)
        self.button_browse_file.setObjectName(_fromUtf8("button_browse_file"))
        self.line = QtGui.QFrame(self.QueryStringBox)
        self.line.setGeometry(QtCore.QRect(40, 80, 641, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.edit_file_name = QtGui.QLineEdit(self.QueryStringBox)
        self.edit_file_name.setEnabled(False)
        self.edit_file_name.setGeometry(QtCore.QRect(50, 130, 551, 30))
        self.edit_file_name.setObjectName(_fromUtf8("edit_file_name"))
        Wizard.addPage(self.InputSelection)
        self.query_options = QtGui.QWizardPage()
        self.query_options.setObjectName(_fromUtf8("query_options"))
        self.frame_3 = QtGui.QFrame(self.query_options)
        self.frame_3.setGeometry(QtCore.QRect(10, 10, 770, 530))
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.scrollArea = QtGui.QScrollArea(self.frame_3)
        self.scrollArea.setGeometry(QtCore.QRect(10, 39, 750, 471))
        self.scrollArea.setFrameShape(QtGui.QFrame.StyledPanel)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 729, 658))
        self.scrollAreaWidgetContents.setAutoFillBackground(False)
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.selection_layout = QtGui.QGridLayout()
        self.selection_layout.setObjectName(_fromUtf8("selection_layout"))
        self.coquery_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.coquery_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.coquery_label.setObjectName(_fromUtf8("coquery_label"))
        self.selection_layout.addWidget(self.coquery_label, 0, 0, 1, 1)
        self.word_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.word_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.word_label.setObjectName(_fromUtf8("word_label"))
        self.selection_layout.addWidget(self.word_label, 2, 0, 1, 1)
        self.speaker_layout = QtGui.QVBoxLayout()
        self.speaker_layout.setObjectName(_fromUtf8("speaker_layout"))
        self.speaker_data_id = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.speaker_data_id.setObjectName(_fromUtf8("speaker_data_id"))
        self.speaker_layout.addWidget(self.speaker_data_id)
        self.speaker_data_age = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.speaker_data_age.setObjectName(_fromUtf8("speaker_data_age"))
        self.speaker_layout.addWidget(self.speaker_data_age)
        self.speaker_data_sex = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.speaker_data_sex.setObjectName(_fromUtf8("speaker_data_sex"))
        self.speaker_layout.addWidget(self.speaker_data_sex)
        self.selection_layout.addLayout(self.speaker_layout, 10, 1, 1, 1)
        self.source_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.source_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.source_label.setObjectName(_fromUtf8("source_label"))
        self.selection_layout.addWidget(self.source_label, 6, 0, 1, 1)
        self.file_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.file_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.file_label.setObjectName(_fromUtf8("file_label"))
        self.selection_layout.addWidget(self.file_label, 8, 0, 1, 1)
        self.speaker_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.speaker_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.speaker_label.setObjectName(_fromUtf8("speaker_label"))
        self.selection_layout.addWidget(self.speaker_label, 10, 0, 1, 1)
        self.source_layout = QtGui.QVBoxLayout()
        self.source_layout.setObjectName(_fromUtf8("source_layout"))
        self.source_id = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.source_id.setObjectName(_fromUtf8("source_id"))
        self.source_layout.addWidget(self.source_id)
        self.source_data_year = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.source_data_year.setObjectName(_fromUtf8("source_data_year"))
        self.source_layout.addWidget(self.source_data_year)
        self.source_data_genre = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.source_data_genre.setObjectName(_fromUtf8("source_data_genre"))
        self.source_layout.addWidget(self.source_data_genre)
        self.source_data_title = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.source_data_title.setObjectName(_fromUtf8("source_data_title"))
        self.source_layout.addWidget(self.source_data_title)
        self.selection_layout.addLayout(self.source_layout, 6, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.selection_layout.addItem(spacerItem, 17, 0, 1, 1)
        self.time_layout = QtGui.QVBoxLayout()
        self.time_layout.setObjectName(_fromUtf8("time_layout"))
        self.time_data_dur = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.time_data_dur.setObjectName(_fromUtf8("time_data_dur"))
        self.time_layout.addWidget(self.time_data_dur)
        self.time_data_start = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.time_data_start.setObjectName(_fromUtf8("time_data_start"))
        self.time_layout.addWidget(self.time_data_start)
        self.time_data_end = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.time_data_end.setObjectName(_fromUtf8("time_data_end"))
        self.time_layout.addWidget(self.time_data_end)
        self.selection_layout.addLayout(self.time_layout, 12, 1, 1, 1)
        self.lemma_layout = QtGui.QVBoxLayout()
        self.lemma_layout.setObjectName(_fromUtf8("lemma_layout"))
        self.lemma_data_orth = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.lemma_data_orth.setObjectName(_fromUtf8("lemma_data_orth"))
        self.lemma_layout.addWidget(self.lemma_data_orth)
        self.lemma_data_phon = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.lemma_data_phon.setObjectName(_fromUtf8("lemma_data_phon"))
        self.lemma_layout.addWidget(self.lemma_data_phon)
        self.lemma_data_pos = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.lemma_data_pos.setObjectName(_fromUtf8("lemma_data_pos"))
        self.lemma_layout.addWidget(self.lemma_data_pos)
        self.selection_layout.addLayout(self.lemma_layout, 4, 1, 1, 1)
        self.word_layout = QtGui.QVBoxLayout()
        self.word_layout.setObjectName(_fromUtf8("word_layout"))
        self.word_data_orth = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.word_data_orth.setObjectName(_fromUtf8("word_data_orth"))
        self.word_layout.addWidget(self.word_data_orth)
        self.word_data_phon = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.word_data_phon.setObjectName(_fromUtf8("word_data_phon"))
        self.word_layout.addWidget(self.word_data_phon)
        self.word_data_pos = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.word_data_pos.setObjectName(_fromUtf8("word_data_pos"))
        self.word_layout.addWidget(self.word_data_pos)
        self.selection_layout.addLayout(self.word_layout, 2, 1, 1, 1)
        self.context_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.context_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.context_label.setObjectName(_fromUtf8("context_label"))
        self.selection_layout.addWidget(self.context_label, 16, 0, 1, 1)
        self.lemma_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lemma_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lemma_label.setObjectName(_fromUtf8("lemma_label"))
        self.selection_layout.addWidget(self.lemma_label, 4, 0, 1, 1)
        self.time_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.time_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.time_label.setObjectName(_fromUtf8("time_label"))
        self.selection_layout.addWidget(self.time_label, 12, 0, 1, 1)
        self.file_separator = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.file_separator.setFrameShape(QtGui.QFrame.HLine)
        self.file_separator.setFrameShadow(QtGui.QFrame.Sunken)
        self.file_separator.setObjectName(_fromUtf8("file_separator"))
        self.selection_layout.addWidget(self.file_separator, 9, 0, 1, 1)
        self.context_layout = QtGui.QVBoxLayout()
        self.context_layout.setObjectName(_fromUtf8("context_layout"))
        self.context_left_span_layout = QtGui.QHBoxLayout()
        self.context_left_span_layout.setObjectName(_fromUtf8("context_left_span_layout"))
        self.context_left_span = QtGui.QSpinBox(self.scrollAreaWidgetContents)
        self.context_left_span.setObjectName(_fromUtf8("context_left_span"))
        self.context_left_span_layout.addWidget(self.context_left_span)
        self.context_left_span_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.context_left_span_label.sizePolicy().hasHeightForWidth())
        self.context_left_span_label.setSizePolicy(sizePolicy)
        self.context_left_span_label.setObjectName(_fromUtf8("context_left_span_label"))
        self.context_left_span_layout.addWidget(self.context_left_span_label)
        self.context_layout.addLayout(self.context_left_span_layout)
        self.context_right_span_layout = QtGui.QHBoxLayout()
        self.context_right_span_layout.setObjectName(_fromUtf8("context_right_span_layout"))
        self.context_right_span = QtGui.QSpinBox(self.scrollAreaWidgetContents)
        self.context_right_span.setObjectName(_fromUtf8("context_right_span"))
        self.context_right_span_layout.addWidget(self.context_right_span)
        self.context_right_span_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.context_right_span_label.sizePolicy().hasHeightForWidth())
        self.context_right_span_label.setSizePolicy(sizePolicy)
        self.context_right_span_label.setObjectName(_fromUtf8("context_right_span_label"))
        self.context_right_span_layout.addWidget(self.context_right_span_label)
        self.context_layout.addLayout(self.context_right_span_layout)
        self.context_words_as_columns = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.context_words_as_columns.setObjectName(_fromUtf8("context_words_as_columns"))
        self.context_layout.addWidget(self.context_words_as_columns)
        self.selection_layout.addLayout(self.context_layout, 16, 1, 1, 1)
        self.source_separator = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.source_separator.setFrameShape(QtGui.QFrame.HLine)
        self.source_separator.setFrameShadow(QtGui.QFrame.Sunken)
        self.source_separator.setObjectName(_fromUtf8("source_separator"))
        self.selection_layout.addWidget(self.source_separator, 7, 0, 1, 1)
        self.speaker_separator = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.speaker_separator.setFrameShape(QtGui.QFrame.HLine)
        self.speaker_separator.setFrameShadow(QtGui.QFrame.Sunken)
        self.speaker_separator.setObjectName(_fromUtf8("speaker_separator"))
        self.selection_layout.addWidget(self.speaker_separator, 11, 0, 1, 1)
        self.lemma_separator = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.lemma_separator.setFrameShape(QtGui.QFrame.HLine)
        self.lemma_separator.setFrameShadow(QtGui.QFrame.Sunken)
        self.lemma_separator.setObjectName(_fromUtf8("lemma_separator"))
        self.selection_layout.addWidget(self.lemma_separator, 5, 0, 1, 1)
        self.word_separator = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.word_separator.setFrameShape(QtGui.QFrame.HLine)
        self.word_separator.setFrameShadow(QtGui.QFrame.Sunken)
        self.word_separator.setObjectName(_fromUtf8("word_separator"))
        self.selection_layout.addWidget(self.word_separator, 3, 0, 1, 1)
        self.file_layout = QtGui.QVBoxLayout()
        self.file_layout.setObjectName(_fromUtf8("file_layout"))
        self.file_data_name = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.file_data_name.setObjectName(_fromUtf8("file_data_name"))
        self.file_layout.addWidget(self.file_data_name)
        self.file_data_path = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.file_data_path.setObjectName(_fromUtf8("file_data_path"))
        self.file_layout.addWidget(self.file_data_path)
        self.selection_layout.addLayout(self.file_layout, 8, 1, 1, 1)
        self.time_separator = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.time_separator.setFrameShape(QtGui.QFrame.HLine)
        self.time_separator.setFrameShadow(QtGui.QFrame.Sunken)
        self.time_separator.setObjectName(_fromUtf8("time_separator"))
        self.selection_layout.addWidget(self.time_separator, 15, 0, 1, 1)
        self.file_layout_2 = QtGui.QVBoxLayout()
        self.file_layout_2.setObjectName(_fromUtf8("file_layout_2"))
        self.coquery_query_string = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.coquery_query_string.setObjectName(_fromUtf8("coquery_query_string"))
        self.file_layout_2.addWidget(self.coquery_query_string)
        self.coquery_parameters = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.coquery_parameters.setObjectName(_fromUtf8("coquery_parameters"))
        self.file_layout_2.addWidget(self.coquery_parameters)
        self.selection_layout.addLayout(self.file_layout_2, 0, 1, 1, 1)
        self.line_2 = QtGui.QFrame(self.scrollAreaWidgetContents)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.selection_layout.addWidget(self.line_2, 1, 0, 1, 1)
        self.selection_layout.setColumnStretch(0, 1)
        self.verticalLayout_9.addLayout(self.selection_layout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.label_5 = QtGui.QLabel(self.frame_3)
        self.label_5.setGeometry(QtCore.QRect(10, 10, 750, 16))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        Wizard.addPage(self.query_options)

        self.retranslateUi(Wizard)
        QtCore.QMetaObject.connectSlotsByName(Wizard)

    def retranslateUi(self, Wizard):
        Wizard.setWindowTitle(_translate("Wizard", "Wizard", None))
        self.label_3.setText(_translate("Wizard", "<html><head/><body><p><span style=\" font-weight:600;\">Coquery 0.9</span></p><p><span style=\" font-weight:600;\">The corpus query tool</span></p><p>(c) 2015 Gero Kunter</p><p><br/><a href=\"https://bitbucket.org/gkunter/coquery\"><span style=\" text-decoration: underline; color:#0057ae;\">BitBucket page</span></a></p><p>Visit <a href=\"https://twitter.com/CoqueryTool\">@CoqueryTool</a> on Twitter</p></body></html>", None))
        self.label.setText(_translate("Wizard", "Select corpus:", None))
        self.groupBox1.setTitle(_translate("Wizard", "Select query mode", None))
        self.radio_mode_context.setText(_translate("Wizard", "Context (KWIC)", None))
        self.radio_mode_frequency.setText(_translate("Wizard", "Frequency", None))
        self.radio_mode_statistics.setText(_translate("Wizard", "Statistics", None))
        self.label_4.setText(_translate("Wizard", "Select the source of the search queries:", None))
        self.label_12.setText(_translate("Wizard", "Enter query string:", None))
        self.button_file_options.setText(_translate("Wizard", "Options...", None))
        self.button_file_options.setShortcut(_translate("Wizard", "Alt+O", None))
        self.label_8.setText(_translate("Wizard", "Read queries from file...", None))
        self.button_browse_file.setText(_translate("Wizard", "Browse", None))
        self.button_browse_file.setShortcut(_translate("Wizard", "Alt+B", None))
        self.coquery_label.setText(_translate("Wizard", "Coquery features", None))
        self.word_label.setText(_translate("Wizard", "Word features", None))
        self.speaker_data_id.setText(_translate("Wizard", "Identifier", None))
        self.speaker_data_age.setText(_translate("Wizard", "Age", None))
        self.speaker_data_sex.setText(_translate("Wizard", "Sex", None))
        self.source_label.setText(_translate("Wizard", "Source features", None))
        self.file_label.setText(_translate("Wizard", "File features", None))
        self.speaker_label.setText(_translate("Wizard", "Speaker features", None))
        self.source_id.setText(_translate("Wizard", "Identifier", None))
        self.source_data_year.setText(_translate("Wizard", "Year", None))
        self.source_data_genre.setText(_translate("Wizard", "Genre", None))
        self.source_data_title.setText(_translate("Wizard", "Title", None))
        self.time_data_dur.setText(_translate("Wizard", "Duration", None))
        self.time_data_start.setText(_translate("Wizard", "Starting time", None))
        self.time_data_end.setText(_translate("Wizard", "End time", None))
        self.lemma_data_orth.setText(_translate("Wizard", "Orthographic form", None))
        self.lemma_data_phon.setText(_translate("Wizard", "Phonological form", None))
        self.lemma_data_pos.setText(_translate("Wizard", "Part-of-speech", None))
        self.word_data_orth.setText(_translate("Wizard", "Orthographic form", None))
        self.word_data_phon.setText(_translate("Wizard", "Phonological form", None))
        self.word_data_pos.setText(_translate("Wizard", "Part-of-speech", None))
        self.context_label.setText(_translate("Wizard", "Context features", None))
        self.lemma_label.setText(_translate("Wizard", "Lemma features", None))
        self.time_label.setText(_translate("Wizard", "Time features", None))
        self.context_left_span_label.setText(_translate("Wizard", "words in left context", None))
        self.context_right_span_label.setText(_translate("Wizard", "words in right context", None))
        self.context_words_as_columns.setText(_translate("Wizard", "Words as columns", None))
        self.file_data_name.setText(_translate("Wizard", "File name", None))
        self.file_data_path.setText(_translate("Wizard", "File path", None))
        self.coquery_query_string.setText(_translate("Wizard", "Query string", None))
        self.coquery_parameters.setText(_translate("Wizard", "Search parameters", None))
        self.label_5.setText(_translate("Wizard", "Output options", None))


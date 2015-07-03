from __future__ import unicode_literals

from session import *
from defines import *
from pyqt_compat import QtCore, QtGui
import wizardUi
import csvOptions
import QtProgress

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

class focusFilter(QtCore.QObject):
    focus = QtCore.Signal()
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.FocusIn:
            self.focus.emit()
            return super(focusFilter, self).eventFilter(obj, event)
        return super(focusFilter, self).eventFilter(obj, event)

class clickFilter(QtCore.QObject):
    clicked = QtCore.Signal()
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.clicked.emit()
            return super(clickFilter, self).eventFilter(obj, event)
        return super(clickFilter, self).eventFilter(obj, event)

class CoqueryWizard(QtGui.QWizard):
    checked_buttons = set([])

    def get_new_label(self, s, name, parent):
        """ Add a new label to the parent widget. Used for creating the 
        output option list dynamically. """
        new_label = QtGui.QLabel(parent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(new_label.sizePolicy().hasHeightForWidth())
        new_label.setSizePolicy(sizePolicy)
        new_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        new_label.setObjectName(_fromUtf8(name))
        new_label.setText(_translate("Wizard", s, None))
        return new_label

    def get_new_box(self, s, name, parent):
        """ Add a new checkbox to the parent widget. Used for creating the 
        output option list dynamically. """
        new_box = QtGui.QCheckBox(parent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(new_box.sizePolicy().hasHeightForWidth())
        new_box.setTristate(False)
        new_box.setSizePolicy(sizePolicy)
        new_box.setObjectName(_fromUtf8(name))
        new_box.setText(_translate("Wizard", s, None))
        new_box.setChecked(_fromUtf8(name) in self.checked_buttons)
        return new_box

    def get_new_separator(self, name, parent):
        """ Add a new separator to the parent widget. Used for creating the 
        output option list dynamically. """
        new_separator = QtGui.QFrame(parent)
        new_separator.setFrameShape(QtGui.QFrame.HLine)
        new_separator.setFrameShadow(QtGui.QFrame.Sunken)
        new_separator.setObjectName(_fromUtf8(name))
        return new_separator
    
    def clear_layout(self, layout):
        """ Remove all children from the layout. Used for creating the 
        output option list dynamically."""
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if isinstance(item, QtGui.QWidgetItem):
                widget = item.widget()
                if isinstance(widget, QtGui.QCheckBox):
                    if widget.checkState():
                        self.checked_buttons.add(_fromUtf8(widget.objectName()))
                    else:
                        try:
                            self.checked_buttons.remove(_fromUtf8(widget.objectName()))
                        except KeyError:
                            pass
                widget.close()
            elif isinstance(item, QtGui.QSpacerItem):
                pass
            else:
                self.clear_layout(item.layout())
            layout.removeItem(item)   

    def change_corpus(self, *args):
        if self.ui.combo_corpus.isEnabled():
            self.change_corpus_features(str(self.ui.combo_corpus.currentText()).lower())
    
    def change_corpus_features(self, corpus_label, prefix="", suffix=""):
        """ Construct a new output option list depending on the features
        provided by the corpus given in 'corpus_label."""
        
        Resource, Corpus, Lexicon, Path = resource_list.get_available_resources()[corpus_label]
        
        # Find the widget containing the output options and the associated
        # layout:
        options_scroll_content = self.findChild(QtGui.QWidget, "options_scroll_content")
        options_list = self.findChild(QtGui.QGridLayout, "options_list")

        # start with an empty layout for the option list:
        self.clear_layout(options_list)
        
        # get a list of all tables in the resource, except those that contain
        # _denorm_ (these are denormalized tables of existing tables and
        # should be have feature-parity with them)
        table_list = [x[:x.index("_table")] for x in dir(Resource) if x.endswith("_table") and not x.count("_denorm_")]

        # Rearrange table list so that they occur in a sensible order:
        for x in reversed(["word", "lemma", "corpus", "source", "file", "speaker"]):
            if x in table_list:
                table_list.remove(x)
                table_list.insert(0, x)
        
        layout_dict = {}
        block_count = 0       

        # Add options for each content variable in the table description. For 
        # each table, a separate list of checkboxes is added.
        for i, table in enumerate(table_list):
            # create new layout for the table:
            table_layout = QtGui.QVBoxLayout()
            table_layout.setObjectName(_fromUtf8("{}_layout".format(table)))
            layout_dict[table] = table_layout
            
            # look for content variables in the resource:
            for var in dir(Resource):
                # variables of the form x_id, x_y_table, and x_y_id are 
                # internal variables used to link different tables. They
                # do not occur as checkboxes:
                if var.startswith(table) and not var.endswith("_table") and not var.endswith("_id") and not var.startswith("{}_table".format(table)):
                    layout_dict[table].addWidget(
                        self.get_new_box(Resource.__dict__[var], var, options_scroll_content))
            # if there is a list of checkboxes for the current table, add it
            # to the option list:
            if layout_dict[table]:
                options_list.addWidget(
                    self.get_new_label(
                        " ".join([prefix, table, suffix]).strip().capitalize(), 
                        "{}_label".format(table), 
                        options_scroll_content), block_count, 0, 1, 1)
                options_list.addLayout(layout_dict[table], block_count, 1, 1, 1)
                block_count += 1
                # add visual separator:
                options_list.addWidget(self.get_new_separator("{}_separator".format(table), options_scroll_content), block_count, 0, 1, 1)
                block_count += 1

        # Add general output options:
        general_layout = QtGui.QVBoxLayout()
        general_layout.setObjectName(_fromUtf8("coquery_layout"))
        general_layout.addWidget(
            self.get_new_box("Query string", "coquery_query_string", options_scroll_content))
        general_layout.addWidget(
            self.get_new_box("Name of input file     ", "coquery_input_file", options_scroll_content))
        options_list.addWidget(
            self.get_new_label("General", "coquery_label", options_scroll_content), block_count, 0, 1, 1)
        options_list.addLayout(general_layout, block_count, 1, 1, 1)
        block_count += 1
        
        # add a spacer so that the layout is compact:
        options_list.addItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding), block_count, 0, 1, 1)
        
        self.enable_output_option()
    
    #def validateCurrentPage(self):
        #page = self.currentPage()
        ## validate corpus selection and query mode:
        #if self.currentId() == 0:
            #combo = page.findChild(QtGui.QComboBox, "combo_corpus")
            #self.change_corpus_features(str(combo.currentText()).lower(), suffix = "features")
        
            #return True
        ### validate input page:
        ##elif self.currendId() == 2:
            ##if page.field("edit_query_string")
            ##or page.field("edit_file_name")
        #return True

    def setup_hooks(self):
        # hook file browser button:
        self.ui.button_browse_file.clicked.connect(self.select_file)
        # hook file options button:
        self.ui.button_file_options.clicked.connect(self.file_options)

        # set up hooks so that the general option to output the file name
        # is available only if an input file is actually used:
        self.ui.radio_query_string.toggled.connect(self.enable_output_option)
        self.ui.radio_query_file.toggled.connect(self.enable_output_option)

        # hook up events so that the radio buttons are set correctly
        # between either query from file or query from string:
        self.focus_to_file = clickFilter()
        self.ui.edit_file_name.installEventFilter(self.focus_to_file)
        self.focus_to_file.clicked.connect(self.select_file)
        self.ui.edit_file_name.textChanged.connect(self.switch_to_file)
        
        self.focus_to_query = focusFilter()
        self.focus_to_query.focus.connect(self.switch_to_query)
        self.ui.edit_query_string.installEventFilter(self.focus_to_query)

        self.ui.combo_corpus.currentIndexChanged.connect(self.change_corpus)

    def setup_wizard(self):
        logo = QtGui.QPixmap("{}/logo/logo.png".format(sys.path[0]))
        self.ui.Logo.setPixmap(logo.scaledToHeight(200))
        
        self.button(QtGui.QWizard.NextButton).setIcon(QtGui.QIcon.fromTheme("go-next"))
        self.setButtonText(QtGui.QWizard.NextButton, "&Next")
        self.button(QtGui.QWizard.BackButton).setIcon(QtGui.QIcon.fromTheme("go-previous"))
        self.setButtonText(QtGui.QWizard.BackButton, "&Back")
        self.button(QtGui.QWizard.CancelButton).setIcon(QtGui.QIcon.fromTheme("application-exit"))
        self.button(QtGui.QWizard.FinishButton).setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
        self.setButtonText(QtGui.QWizard.FinishButton, "&Run query")
        
        self.fill_combo_corpus()
        
        self.setup_hooks()
        
    def fill_combo_corpus(self):
        print("refill!")
        self.ui.combo_corpus.currentIndexChanged.disconnect()
        last_corpus = self.ui.combo_corpus.currentText()
        self.ui.combo_corpus.clear()
        for x in sorted(resource_list.get_available_resources().keys()):
            self.ui.combo_corpus.addItem(x.upper())
        new_index = self.ui.combo_corpus.findText(last_corpus)
        if new_index == -1:
            new_index = 0
        self.ui.combo_corpus.setCurrentIndex(new_index)
        self.ui.combo_corpus.setEnabled(True)
        self.ui.combo_corpus.currentIndexChanged.connect(self.change_corpus)

    def enable_output_option(self):
        checkbox = self.findChild(QtGui.QCheckBox, "coquery_input_file")
        if checkbox:
            if self.ui.radio_query_file.isChecked():
                checkbox.setDisabled(False)
            else:
                checkbox.setEnabled(False)

    def switch_to_file(self):
        self.ui.radio_query_file.setFocus()
        self.ui.radio_query_file.setChecked(True)

    def switch_to_query(self):
        self.ui.radio_query_string.setChecked(True)

    def set_gui_defaults(self):
        """ evaulates options.cfg, and set the default values of the wizard
        accordingly."""
        pass
    
    def select_file(self):
        name = QtGui.QFileDialog.getOpenFileName(directory="~")
        if type(name) == tuple:
            name = name[0]
        if name:
            self.ui.edit_file_name.setText(name)
            self.ui.button_file_options.setEnabled(True)
            self.switch_to_file()
            
    def file_options(self):
        results = csvOptions.CSVOptions.getOptions(
            self.ui.edit_file_name.text(), 
            self.csv_options, 
            self, icon=options.cfg.icon)
        
        if results:
            self.csv_options = results
            self.switch_to_file()
    
    def __init__(self, parent=None):
        super(CoqueryWizard, self).__init__(parent)
        
        self.file_content = None
        self.ui = wizardUi.Ui_Wizard()
        self.ui.setupUi(self)

        self.setup_wizard()
        self.csv_options = None
        
    def getWizardArguments(self, parent=None):
        """ update the values in options.cfg with those entered in the 
        GUI wizard w."""
        result = self.exec_()
        if result != QtGui.QDialog.Accepted:
            return None
        else:
            self.getGuiValues()
            return True

    def getGuiValues(self):
        if options.cfg:
            options.cfg.corpus = unicode(self.ui.combo_corpus.currentText()).lower()
            if self.ui.radio_mode_context.isChecked():
                options.cfg.MODE = QUERY_MODE_DISTINCT
                
            if self.ui.radio_mode_frequency.isChecked():
                options.cfg.MODE = QUERY_MODE_FREQUENCIES
                
            try:
                if self.ui.radio_mode_statistics.isChecked():
                    options.cfg.MODE = QUERY_MODE_STATISTICS
            except AttributeError:
                pass
                
            if self.ui.radio_mode_tokens.isChecked():
                options.cfg.MODE = QUERY_MODE_TOKENS
                
            if self.ui.radio_query_string.isChecked():
                if type(self.ui.edit_query_string) == QtGui.QLineEdit:
                    options.cfg.query_list = [unicode(self.ui.edit_query_string.text())]
                else:
                    options.cfg.query_list = [unicode(self.ui.edit_query_string.toPlainText())]
            elif self.ui.radio_query_file.isChecked():
                options.cfg.input_path = unicode(self.ui.edit_file_name.text())

            if self.csv_options:
                sep, col, head, skip = self.csv_options
                options.cfg.input_separator = sep
                options.cfg.query_column_number = col
                options.cfg.file_has_headers = head
                options.cfg.skip_lines = skip

            if self.ui.context_words_as_columns.checkState():
                options.cfg.context_columns = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            else:
                options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            
            # new evaluation of check boxes, making use of the 
            # corpus-specific flexible output column selection:
            
            options_list = self.findChild(QtGui.QGridLayout, "options_list")
            options_scroll_content = self.findChild(QtGui.QWidget, "options_scroll_content")

            # remember all clicked checkboxes so that the selection can be 
            # carried over to the new corpus:
            options.cfg.selected_feature_list = []
            for current_box in options_scroll_content.findChildren(QtGui.QCheckBox):
                feature = str(current_box.objectName())
                if current_box.checkState():
                    options.cfg.selected_feature_list.append(feature)
                table, _, variable = feature.partition("_")
                
                if table == "coquery":
                    if variable == "query_string":
                        options.cfg.show_query = current_box.checkState()
                    if variable == "input_file":
                        pass
                        # options.cfg.show_input_file = current_box.checkState()
                if table == "word":
                    if variable == "label":
                        options.cfg.show_orth = current_box.checkState()
                    if variable == "pos":
                        options.cfg.show_pos = current_box.checkState()
                    if variable == "transcript":
                        options.cfg.show_phon = current_box.checkState()
                if table == "lemma":
                    if variable == "label":
                        options.cfg.show_lemma = current_box.checkState()
                    if variable == "pos":
                        pass
                        #options.cfg.show_lemma_pos = current_box.checkState()
                    if variable == "transcript":
                        pass
                        #options.cfg.show_lemma_phon = current_box.checkState()
                if table == "source":
                    options.cfg.source_columns.append(current_box.text())
                if table == "file":
                    if variable == "label":
                        options.cfg.show_filename = current_box.checkState()
                if table == "speaker":
                    options.cfg.show_speaker = options.cfg.show_speaker | current_box.checkState()
                if table == "corpus":
                    if variable == "time":
                        options.cfg.show_time = current_box.checkState()
                
                        
            
            return True
            
                
            # FIXME: the GUI allows more fine-grained selection of 
            # output options than the command line, and this selection
            # is not evaluated fully by write_results().
            options.cfg.show_query = self.ui.coquery_query_string.checkState()
            options.cfg.show_parameters = self.ui.coquery_parameters.checkState()
            options.cfg.show_orth = self.ui.word_data_orth.checkState()
            options.cfg.show_phon = self.ui.word_data_phon.checkState()
            options.cfg.show_pos = self.ui.word_data_pos.checkState()

            options.cfg.show_lemma = self.ui.lemma_data_orth.checkState()
            # unsupported:
            # options.cfg.show_lemma_phon = self.ui.lemma_data_phon.checkState()
            # options.cfg.show_lemma_pos = self.ui.lemma_data_pos.checkState()
            
            if self.ui.source_id.checkState():
                options.cfg.source_columns.append(unicode(self.ui.source_id.text()))
            if self.ui.source_data_year.checkState():
                options.cfg.source_columns.append(unicode(self.ui.source_data_year.text()))
            if self.ui.source_data_genre.checkState():
                options.cfg.source_columns.append(unicode(self.ui.source_data_genre.text()))
            if self.ui.source_data_title.checkState():
                options.cfg.source_columns.append(unicode(self.ui.source_data_title.text()))
            
            options.cfg.show_filename = self.ui.file_data_name.checkState() or self.ui.file_data_path.checkState()
            options.cfg.show_time = self.ui.time_data_dur.checkState() or self.ui.time_data_end.checkState() or self.ui.time_data_start.checkState()
            options.cfg.show_speaker = self.ui.speaker_data_id.checkState() or self.ui.speaker_data_sex.checkState() or self.ui.speaker_data_age.checkState()
            
            if self.ui.context_words_as_columns.checkState():
                options.cfg.context_columns = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            else:
                options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            
        return True

    def setWizardDefaults(self):
        return
        """ update the values in options.cfg with those entered in the 
        GUI wizard w."""

        if options.cfg.corpus:
            self.ui.combo_corpus.setCurrentIndex(
                sorted(resource_list.get_available_resources().keys()).index(options.cfg.corpus))

        if options.cfg.MODE == QUERY_MODE_DISTINCT:
            self.ui.radio_mode_context.setChecked(True)
            
        elif options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            self.ui.radio_mode_frequency.setChecked(True)
            
        elif options.cfg.MODE == QUERY_MODE_STATISTICS:
            self.ui.radio_mode_statistics.setChecked(True)
            
        elif options.cfg.MODE == QUERY_MODE_TOKENS:
            self.ui.radio_mode_tokens.setChecked(True)

        if options.cfg.query_list:
            self.ui.radio_query_string.setChecked(True)
            self.ui.edit_query_string.setText(options.cfg.query_list[0])
        elif options.cfg.input_path:
            self.ui.radio_query_file.setChecked(True)
            self.ui.edit_file_name.setText(options.cfg.input_path)
            
        ## FIXME: the GUI allows more fine-grained selection of 
        ## output options than the command line, and this selection
        ## is not evaluated fully by write_results().
        
        self.ui.coquery_query_string.setChecked(options.cfg.show_query)
        self.ui.coquery_parameters.setChecked(options.cfg.show_parameters)
        self.ui.word_data_orth.setChecked(options.cfg.show_orth)
        self.ui.word_data_phon.setChecked(options.cfg.show_phon)
        self.ui.word_data_pos.setChecked(options.cfg.show_pos)

        #options.cfg.show_lemma = self.ui.lemma_data_orth.checkState()
        ## unsupported:
        ## options.cfg.show_lemma_phon = self.ui.lemma_data_phon.checkState()
        ## options.cfg.show_lemma_pos = self.ui.lemma_data_pos.checkState()
        
        #if self.ui.source_id.checkState():
            #options.cfg.source_columns.append(str(self.ui.source_id.text()))
        #if self.ui.source_data_year.checkState():
            #options.cfg.source_columns.append(str(self.ui.source_data_year.text()))
        #if self.ui.source_data_genre.checkState():
            #options.cfg.source_columns.append(str(self.ui.source_data_genre.text()))
        #if self.ui.source_data_title.checkState():
            #options.cfg.source_columns.append(str(self.ui.source_data_title.text()))
        
        #options.cfg.show_filename = self.ui.file_data_name.checkState() or self.ui.file_data_path.checkState()
        #options.cfg.show_time = self.ui.time_data_dur.checkState() or self.ui.time_data_end.checkState() or self.ui.time_data_start.checkState()
        #options.cfg.show_speaker = self.ui.speaker_data_id.checkState() or self.ui.speaker_data_sex.checkState() or self.ui.speaker_data_age.checkState()
        
        #if self.ui.context_words_as_columns.checkState():
            #options.cfg.context_columns = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
        #else:
            #options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
        
        #if self.csv_options:
            #sep, col, head, skip = self.csv_options
            #options.cfg.input_separator = sep
            #options.cfg.query_column_number = col
            #options.cfg.file_has_headers = head
            #options.cfg.skip_lines = skip
        #return True

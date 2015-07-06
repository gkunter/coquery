from __future__ import unicode_literals

from session import *
from defines import *
from pyqt_compat import QtCore, QtGui
import wizardUi
import csvOptions
import QtProgress
import queryfilter

class focusFilter(QtCore.QObject):
    """ Define an event filter that reacts to focus events. This filter is
    used to toggle the query selection radio buttons. """
    focus = QtCore.Signal()
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.FocusIn:
            self.focus.emit()
            return super(focusFilter, self).eventFilter(obj, event)
        return super(focusFilter, self).eventFilter(obj, event)

class clickFilter(QtCore.QObject):
    """ Define an event filter that reacts to click events. This filter is
    used to toggle the query selection radio buttons. """
    clicked = QtCore.Signal()
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.clicked.emit()
            return super(clickFilter, self).eventFilter(obj, event)
        return super(clickFilter, self).eventFilter(obj, event)

class CoqTreeItem(QtGui.QTreeWidgetItem):
    """ Define a tree element class that stores the output column options in
    the options tree. """
    
    def __init__(self, *args):
        super(CoqTreeItem, self).__init__(*args)
        self._objectName = ""
        
    def setObjectName(self, name):
        """ Store resource variable name as object name. """
        self._objectName = name

    def objectName(self):
        """ Retrieve resource variable name from object name. """
        return self._objectName

    def check_children(self, column=0):
        """ Compare the check state of the item to that of all children.
        Returns True all children have the same check state, False if at 
        # least one child has a different check state than another. """

        child_states = set([])
        for child in [self.child(i) for i in range(self.childCount())]:
            child_states.add(child.checkState(column))
        return len(child_states) == 1

    def update_checkboxes(self, column, expand=False):
        """ Propagate the check state of the item to its children. Also, 
        adjust the check state of the parent accordingly. If the argument 
        'expand' is True, the parents of items with checked children will be 
        expanded. """
        check_state = self.checkState(column)
        if check_state == QtCore.Qt.PartiallyChecked:
            # do not propagate a partially checked state
            return
        
        # propagate check state to children:
        for child in [self.child(i) for i in range(self.childCount())]:
            child.setCheckState(column, check_state)
        # adjust check state of parent:
        if self.parent():
            if not self.parent().check_children():
                self.parent().setCheckState(column, QtCore.Qt.PartiallyChecked)
            else:
                self.parent().setCheckState(column, check_state)
            if expand:
                if self.parent().checkState(column) in (QtCore.Qt.PartiallyChecked, QtCore.Qt.Checked):
                    self.parent().setExpanded(True)

class CoqTreeWidget(QtGui.QTreeWidget):
    """ Define a tree widget that stores the available output columns in a 
    tree with check boxes for each variable. """
    def __init__(self, *args):
        super(CoqTreeWidget, self).__init__(*args)
        self.itemChanged.connect(self.update)
        self.setDragEnabled(True)
            
    def update(self, item, column):
        """ Update the checkboxes of parent and child items whenever an
        item has been changed. """
        item.update_checkboxes(column)
        
    def mimeData(self, *args):
        """ Add the resource variable name to the MIME data (for drag and 
        drop). """
        value = super(CoqTreeWidget, self).mimeData(*args)
        value.setText(", ".join([x.objectName() for x in args[0]]))
        return value
        
class CoqueryWizard(QtGui.QWizard):
    """ Define a QWizard class for Coquery. """
    checked_buttons = set([])
    
    def __init__(self, parent=None):
        super(CoqueryWizard, self).__init__(parent)
        
        self.file_content = None
        self.ui = wizardUi.Ui_Wizard()
        self.ui.setupUi(self)

        self.setup_wizard()
        self.csv_options = None
        
    def setup_hooks(self):
        """ Hook up signals so that the GUI can adequately react to user 
        input. """
        # hook file browser button:
        self.ui.button_browse_file.clicked.connect(self.select_file)
        # hook file options button:
        self.ui.button_file_options.clicked.connect(self.file_options)

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
        
    def switch_to_file(self):
        """ Toggle to query file input. """
        self.ui.radio_query_file.setFocus()
        self.ui.radio_query_file.setChecked(True)

    def switch_to_query(self):
        """ Toggle to query string input. """
        self.ui.radio_query_string.setChecked(True)

    def getWizardArguments(self, parent=None):
        """ Run the wizard. If it is successfully completed, get the values 
        from the GUI and store them in options.cfg.*."""
        result = self.exec_()
        if result != QtGui.QDialog.Accepted:
            return None
        else:
            self.getGuiValues()
            return True

    def change_corpus(self, *args):
        """ Update output option tree whenever the corpus selection has
        changed. """
        if self.ui.combo_corpus.count():
            self.change_corpus_features(str(self.ui.combo_corpus.currentText()).lower())
            try:
                self.filter_variable_model.setStringList(options.cfg.output_variable_names)
            except AttributeError:
                pass
    
    def change_corpus_features(self, corpus_label, prefix="", suffix=""):
        """ Construct a new output option tree depending on the features
        provided by the corpus given in 'corpus_label."""
        
        Resource, Corpus, Lexicon, Path = resource_list.get_available_resources()[corpus_label]
        
        table_dict = Resource().get_table_dict()
        # Ignore denormalized tables:
        tables = [x for x in table_dict.keys() if not "_denorm_" in x]
        
        # ignore internal  variables of the form {table}_id, {table}_table,
        # {table}_table_{other}
        for table in tables:
            for var in list(table_dict[table]):
                if var.endswith("_table") or var.endswith("_id") or var.startswith("{}_table".format(table)):
                    table_dict[table].remove(var)
                    
        # Rearrange table names so that they occur in a sensible order:
        for x in reversed(["word", "lemma", "corpus", "source", "file", "speaker"]):
            if x in tables:
                tables.remove(x)
                tables.insert(0, x)

        # replace old tree widget by a new, still empty tree:
        tree = CoqTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setRootIsDecorated(True)
        self.ui.options_list.removeWidget(tree)
        self.ui.options_tree.close()
        self.ui.options_list.addWidget(tree)
        self.ui.options_tree = tree

        options.cfg.output_variable_names = []

        # populate the tree with a root for each table:
        for table in table_dict:
            root = CoqTreeItem()
            root.setFlags(root.flags() | QtCore.Qt.ItemIsUserCheckable   | QtCore.Qt.ItemIsSelectable)
            root.setText(0, table.capitalize())
            root.setObjectName(wizardUi._fromUtf8("{}_root".format(table)))
            root.setCheckState(0, QtCore.Qt.Unchecked)
            if table_dict[table]:
                tree.addTopLevelItem(root)
            
            # add a leaf for each table variable:
            for var in table_dict[table]:
                leaf = CoqTreeItem()
                root.addChild(leaf)
                label = Resource().__getattribute__(var).capitalize()
                leaf.setText(0, label)
                leaf.setObjectName(wizardUi._fromUtf8(var))
                leaf.setCheckState(0, QtCore.Qt.CheckState(wizardUi._fromUtf8(var) in self.checked_buttons))
                leaf.update_checkboxes(0, expand=True)
                options.cfg.output_variable_names.append(label.lower())
                
    def fill_combo_corpus(self):
        """ Add the available corpus names to the corpus selection combo 
        box. """
        self.ui.combo_corpus.currentIndexChanged.disconnect()

        # remember last corpus name:
        last_corpus = self.ui.combo_corpus.currentText()

        # add corpus names:
        self.ui.combo_corpus.clear()
        self.ui.combo_corpus.addItems([x.upper() for x in resource_list.get_available_resources()])

        # try to return to last corpus name:
        new_index = self.ui.combo_corpus.findText(last_corpus)
        if new_index == -1:
            new_index = 0
            
        self.ui.combo_corpus.setCurrentIndex(new_index)
        self.ui.combo_corpus.setEnabled(True)
        self.ui.combo_corpus.currentIndexChanged.connect(self.change_corpus)

    def select_file(self):
        """ Call a file selector, and add file name to query file input. """
        name = QtGui.QFileDialog.getOpenFileName(directory="~")
        
        # getOpenFileName() returns different types in PyQt and PySide, fix:
        if type(name) == tuple:
            name = name[0]
        
        if name:
            self.ui.edit_file_name.setText(name)
            self.ui.button_file_options.setEnabled(True)
            self.switch_to_file()
            
    def file_options(self):
        """ Get CSV file options for current query input file. """
        results = csvOptions.CSVOptions.getOptions(
            self.ui.edit_file_name.text(), 
            self.csv_options, 
            self, icon=options.cfg.icon)
        
        if results:
            self.csv_options = results
            self.switch_to_file()
    
    def set_gui_defaults(self):
        """ evaulates options.cfg.*, and set the default values of the wizard
        accordingly."""
        pass
    
    def getGuiValues(self):
        """ Set the values in options.cfg.* depending on the current values
        in the GUI. """
        
        if options.cfg:
            options.cfg.corpus = unicode(self.ui.combo_corpus.currentText()).lower()
        
            # determine query mode:
            if self.ui.radio_mode_context.isChecked():
                options.cfg.MODE = QUERY_MODE_DISTINCT
            if self.ui.radio_mode_tokens.isChecked():
                options.cfg.MODE = QUERY_MODE_TOKENS
            if self.ui.radio_mode_frequency.isChecked():
                options.cfg.MODE = QUERY_MODE_FREQUENCIES
            try:
                if self.ui.radio_mode_statistics.isChecked():
                    options.cfg.MODE = QUERY_MODE_STATISTICS
            except AttributeError:
                pass
                
            # either get the query input string or the query file name:
            if self.ui.radio_query_string.isChecked():
                if type(self.ui.edit_query_string) == QtGui.QLineEdit:
                    options.cfg.query_list = [unicode(self.ui.edit_query_string.text())]
                else:
                    options.cfg.query_list = [unicode(self.ui.edit_query_string.toPlainText())]
            elif self.ui.radio_query_file.isChecked():
                options.cfg.input_path = unicode(self.ui.edit_file_name.text())

            # retrieve the CSV options for the current input file:
            if self.csv_options:
                sep, col, head, skip = self.csv_options
                options.cfg.input_separator = sep
                options.cfg.query_column_number = col
                options.cfg.file_has_headers = head
                options.cfg.skip_lines = skip

            # get context options:
            try:
                if self.ui.context_words_as_columns.checkState():
                    options.cfg.context_columns = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
                else:
                    options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            except AttributeError:
                if self.ui.context_mode.currentText() == CONTEXT_KWIC:
                    options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
                elif self.ui.context_mode.currentText() == CONTEXT_COLUMNS:
                   options.cfg.context_columns = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
                else:
                    options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            
            # get text filters:
            #options.cfg.filter_list = []
            #try:
                ## check for valid, but not submitted filters:
                #current_filter_text = self.ui.edit_query_filter.text().strip()
                #if CoqFilterTag.check_valid(current_filter_text, options.cfg.output_variable_names):
                    #options.cfg.filter_list.append(CoqFilterTag.format_content(current_filter_text))
            #except AttributeError:
                #pass
            
            
            options.cfg.selected_features = []
            
            # Go throw options tree widget to get all checked output columns:
            for root in [self.ui.options_tree.topLevelItem(i) for i in range(self.ui.options_tree.topLevelItemCount())]:
                for child in [root.child(i) for i in range(root.childCount())]:
                    if child.checkState(0) == QtCore.Qt.Checked:
                        options.cfg.selected_features.append(child.objectName())
                        
                    table, _, variable = child.objectName().partition("_")
                    
                    if table == "coquery":
                        if variable == "query_string":
                            options.cfg.show_query = True
                        if variable == "input_file":
                            pass
                            # options.cfg.show_input_file = child.checkState(0)
                    if table == "word":
                        if variable == "label":
                            options.cfg.show_orth = child.checkState(0)
                        if variable == "pos":
                            options.cfg.show_pos = child.checkState(0)
                        if variable == "transcript":
                            options.cfg.show_phon = child.checkState(0)
                    if table == "lemma":
                        if variable == "label":
                            options.cfg.show_lemma = child.checkState(0)
                        if variable == "pos":
                            pass
                            #options.cfg.show_lemma_pos = child.checkState(0)
                        if variable == "transcript":
                            pass
                            #options.cfg.show_lemma_phon = child.checkState(0)
                    if table == "source":
                        options.cfg.source_columns.append(child.text())
                    if table == "file":
                        if variable == "label":
                            options.cfg.show_filename = child.checkState(0)
                    if table == "speaker":
                        options.cfg.show_speaker = options.cfg.show_speaker | child.checkState(0)
                    if table == "corpus":
                        if variable == "time":
                            options.cfg.show_time = child.checkState(0)
            return True

    def setWizardDefaults(self):
        """ Set up the gui values based on the values in options.cfg.* """

        # set corpus combo box to current corpus:
        if options.cfg.corpus:
            index = self.ui.combo_corpus.findText(options.cfg.corpus)
            if index > -1:
                self.ui.combo_corpus.setCurrentIndex(index)

        # set query mode:
        if options.cfg.MODE == QUERY_MODE_DISTINCT:
            self.ui.radio_mode_context.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            self.ui.radio_mode_frequency.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_TOKENS:
            self.ui.radio_mode_tokens.setChecked(True)

        # either fill query string or query file input:
        if options.cfg.query_list:
            self.ui.radio_query_string.setChecked(True)
            self.ui.edit_query_string.setText(options.cfg.query_list[0])
        elif options.cfg.input_path:
            self.ui.radio_query_file.setChecked(True)
            self.ui.edit_file_name.setText(options.cfg.input_path)
            
        ## FIXME: the GUI allows more fine-grained selection of 
        ## output options than the command line, and this selection
        ## is not evaluated fully by write_results().
        
        #self.ui.coquery_query_string.setChecked(options.cfg.show_query)
        #self.ui.coquery_parameters.setChecked(options.cfg.show_parameters)
        #self.ui.word_data_orth.setChecked(options.cfg.show_orth)
        #self.ui.word_data_phon.setChecked(options.cfg.show_phon)
        #self.ui.word_data_pos.setChecked(options.cfg.show_pos)

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

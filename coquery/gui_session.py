from __future__ import unicode_literals

from session import *
from defines import *
sys.path.append(os.path.join(sys.path[0], "gui"))
from pyqt_compat import QtCore, QtGui
import wizardUi
import csvOptions
import QtProgress

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
    
    def validateCurrentPage(self):
        if self.currentId() == 1:
            page = self.currentPage()
            combo = page.findChild(QtGui.QComboBox, "combo_corpus")
            Resource, Corpus, Lexicon = available_resources[str(combo.currentText()).lower()]
            
            feature_page = self.page(3)
            
            hide_list = []
            show_list = []
            
            if CORP_FILENAME not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QtGui.QLabel, "file_label"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "file_data_name"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "file_data_path"))
            set_vis_list.append(feature_page.findChild(QtGui.QFrame, "file_separator"))

            if CORP_SPEAKER not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QtGui.QLabel, "speaker_label"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "speaker_data_id"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "speaker_data_age"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "speaker_data_sex"))
            set_vis_list.append(feature_page.findChild(QtGui.QFrame, "speaker_separator"))
            
            if CORP_SOURCE not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QtGui.QLabel, "source_label"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "source_id"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "source_data_year"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "source_data_genre"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "source_data_title"))
            set_vis_list.append(feature_page.findChild(QtGui.QFrame, "source_separator"))
            
            if CORP_TIMING not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QtGui.QLabel, "time_label"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "time_data_dur"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "time_data_start"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "time_data_end"))
            set_vis_list.append(feature_page.findChild(QtGui.QFrame, "time_separator"))
            
            if CORP_CONTEXT not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QtGui.QLabel, "context_label"))
            set_vis_list.append(feature_page.findChild(QtGui.QLabel, "context_left_span_label"))
            set_vis_list.append(feature_page.findChild(QtGui.QSpinBox, "context_left_span"))
            set_vis_list.append(feature_page.findChild(QtGui.QLabel, "context_right_span_label"))
            set_vis_list.append(feature_page.findChild(QtGui.QSpinBox, "context_right_span"))
            set_vis_list.append(feature_page.findChild(QtGui.QCheckBox, "context_words_as_columns"))
            set_vis_list.append(feature_page.findChild(QtGui.QFrame, "context_separator"))
            
            for widget in hide_list:
                if widget:
                    widget.hide()
            for widget in show_list:
                if widget:
                    widget.show()
        return True

    def setup_wizard(self):
        # add available resources to corpus dropdown box:
        corpora = [x.upper() for x in sorted(available_resources.keys())]
        self.ui.combo_corpus.addItems(corpora)
        # add logo:
        self.ui.Logo.setPixmap(QtGui.QPixmap("{}/logo/logo.png".format(sys.path[0])))
        
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
            self)
        
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

        if options.cfg:
            options.cfg.corpus = str(self.ui.combo_corpus.currentText()).lower()
            if self.ui.radio_mode_context.isChecked():
                options.cfg.MODE = QUERY_MODE_DISTINCT
            elif self.ui.radio_mode_frequency.isChecked():
                options.cfg.MODE = QUERY_MODE_FREQUENCIES
            elif self.ui.radio_mode_statistics.isChecked():
                options.cfg.MODE = QUERY_MODE_STATISTICS
            if self.ui.radio_query_string.isChecked():
                options.cfg.query_list = [str(self.ui.edit_query_string.text())]
            elif self.ui.radio_query_file.isChecked():
                options.cfg.input_path = str(self.ui.edit_file_name.text())
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
                options.cfg.source_columns.append(str(self.ui.source_id.text()))
            if self.ui.source_data_year.checkState():
                options.cfg.source_columns.append(str(self.ui.source_data_year.text()))
            if self.ui.source_data_genre.checkState():
                options.cfg.source_columns.append(str(self.ui.source_data_genre.text()))
            if self.ui.source_data_title.checkState():
                options.cfg.source_columns.append(str(self.ui.source_data_title.text()))
            
            options.cfg.show_filename = self.ui.file_data_name.checkState() or self.ui.file_data_path.checkState()
            options.cfg.show_time = self.ui.time_data_dur.checkState() or self.ui.time_data_end.checkState() or self.ui.time_data_start.checkState()
            options.cfg.show_speaker = self.ui.speaker_data_id.checkState() or self.ui.speaker_data_sex.checkState() or self.ui.speaker_data_age.checkState()
            
            if self.ui.context_words_as_columns.checkState():
                options.cfg.context_columns = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            else:
                options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            
            if self.csv_options:
                sep, col, head, skip = self.csv_options
                options.cfg.input_separator = sep
                options.cfg.query_column_number = col
                options.cfg.file_has_headers = head
                options.cfg.skip_lines = skip

class SessionGUI(Session):
    
    def run_queries(self):
        logger.info("Using GUI, %s queries" % len (self.query_list))
        w = QtProgress.ProgressIndicator(super(SessionGUI, self).run_queries)
        w.show()
        w.onStart()
        exit_code = self.app.exec_()
        if exit_code:
            sys.exit(exit_code)


if __name__ == "__main__":
    session = SessionGUI()

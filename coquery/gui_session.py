from PyQt4.QtCore import *
from PyQt4.QtGui import *

from session import *
from defines import *
sys.path.append(os.path.join(sys.path[0], "gui"))
import wizardUi
import csvOptions
import QtProgress

class focusFilter(QObject):
    focus = pyqtSignal()
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.focus.emit()
            return super(focusFilter, self).eventFilter(obj, event)
        return super(focusFilter, self).eventFilter(obj, event)

class clickFilter(QObject):
    clicked = pyqtSignal()
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.clicked.emit()
            return super(clickFilter, self).eventFilter(obj, event)
        return super(clickFilter, self).eventFilter(obj, event)

class CoqueryWizard(QWizard):
    def validateCurrentPage(self):
        if self.currentId() == 1:
            page = self.currentPage()
            combo = page.findChild(QComboBox, "combo_corpus")
            Resource, Corpus, Lexicon = available_resources[str(combo.currentText()).lower()]
            
            feature_page = self.page(3)
            
            hide_list = []
            show_list = []
            
            
            if CORP_FILENAME not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QLabel, "file_label"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "file_data_name"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "file_data_path"))
            set_vis_list.append(feature_page.findChild(QFrame, "file_separator"))

            if CORP_SPEAKER not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QLabel, "speaker_label"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "speaker_data_id"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "speaker_data_age"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "speaker_data_sex"))
            set_vis_list.append(feature_page.findChild(QFrame, "speaker_separator"))
            
            if CORP_SOURCE not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QLabel, "source_label"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "source_id"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "source_data_year"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "source_data_genre"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "source_data_title"))
            set_vis_list.append(feature_page.findChild(QFrame, "source_separator"))
            
            if CORP_TIMING not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QLabel, "time_label"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "time_data_dur"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "time_data_start"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "time_data_end"))
            set_vis_list.append(feature_page.findChild(QFrame, "time_separator"))
            
            if CORP_CONTEXT not in Corpus.provides:
                set_vis_list = hide_list
            else:
                set_vis_list = show_list
            set_vis_list.append(feature_page.findChild(QLabel, "context_label"))
            set_vis_list.append(feature_page.findChild(QLabel, "context_left_span_label"))
            set_vis_list.append(feature_page.findChild(QSpinBox, "context_left_span"))
            set_vis_list.append(feature_page.findChild(QLabel, "context_right_span_label"))
            set_vis_list.append(feature_page.findChild(QSpinBox, "context_right_span"))
            set_vis_list.append(feature_page.findChild(QCheckBox, "context_words_as_columns"))
            set_vis_list.append(feature_page.findChild(QFrame, "context_separator"))
            
            for widget in hide_list:
                if widget:
                    widget.hide()
            for widget in show_list:
                if widget:
                    widget.show()
        return True

class SessionGUI(Session):
    def setup_wizard(self):
        # add available resources to corpus dropdown box:
        corpora = [x.upper() for x in sorted(available_resources.keys())]
        self.ui.combo_corpus.addItems(corpora)
        # add logo:
        self.ui.Logo.setPixmap(QPixmap("{}/logo/logo.png".format(sys.path[0])))
        
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

    def get_arguments_from_gui(self):
        """ update the values in options.cfg with those entered in the 
        GUI wizard w."""
        pass
    
    def select_file(self):
        name = QFileDialog.getOpenFileName(directory="~")
        if name:
            self.ui.edit_file_name.setText(name)
            self.ui.button_file_options.setEnabled(True)
            self.switch_to_file()
            
    def file_options(self):
        results = csvoptions.CSVOptions.getOptions(
            self.ui.edit_file_name.text(), 
            self.csv_options, 
            self.dialog)
        
        if results:
            self.csv_options = results
            self.switch_to_file()
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.dialog = CoqueryWizard()
        self.ui = wizardUi.Ui_Wizard()
        self.ui.setupUi(self.dialog)

        self.setup_wizard()
        self.dialog.show()
        
        self.csv_options = None
        
        exit_code = self.app.exec_()
        if exit_code:
            sys.exit(exit_code)
        self.get_arguments_from_gui()
        
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

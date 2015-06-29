from __future__ import unicode_literals

from session import *
from defines import *
from pyqt_compat import QtCore, QtGui
import coqueryUi
import csvOptions
import QtProgress
import wizard
import results 
import error_box
import codecs

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

class CoqueryApp(QtGui.QMainWindow, wizard.CoqueryWizard):
    """ Coquery as standalone application. """
    def setup_app(self):
        """ initializes all widgets with suitable data """
        # add available resources to corpus dropdown box:
        corpora = [x.upper() for x in sorted(available_resources.keys())]
        self.ui.combo_corpus.addItems(corpora)
        # add logo:
        #logo = QtGui.QPixmap("{}/logo/logo.png".format(sys.path[0]))
        #self.ui.Logo.setPixmap(logo.scaledToHeight(200))
        
        # hook file browser button:
        self.ui.button_browse_file.clicked.connect(self.select_file)
        # hook file options button:
        self.ui.button_file_options.clicked.connect(self.file_options)

        # hook run query button:
        self.ui.button_run_query.clicked.connect(self.run_query)
        
        # hook run query button:
        self.ui.button_show_statistics.clicked.connect(self.run_statistics)
        
        # hook up events so that the radio buttons are set correctly
        # between either query from file or query from string:
        self.focus_to_file = clickFilter()
        self.ui.edit_file_name.installEventFilter(self.focus_to_file)
        self.focus_to_file.clicked.connect(self.select_file)
        self.ui.edit_file_name.textChanged.connect(self.switch_to_file)
        
        self.focus_to_query = focusFilter()
        self.focus_to_query.focus.connect(self.switch_to_query)
        self.ui.edit_query_string.installEventFilter(self.focus_to_query)
        self.ui.log_file_path.setText(options.cfg.log_file_path)
        self.last_logfile_date = None
        
        self.ui.tabbed_views.currentChanged.connect(self.change_tab)
 
    def __init__(self, parent=None):
        super(CoqueryApp, self).__init__(None)
        
        self.file_content = None
        
        self.ui = coqueryUi.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_app()
        self.csv_options = None

    def change_tab(self, i):
        if i == 1:
            if self.last_logfile_date <> os.path.getmtime(options.cfg.log_file_path):
                self.last_logfile_date = os.path.getmtime(options.cfg.log_file_path)
                self.update_logfile()        

    def update_logfile(self):
        with codecs.open(options.cfg.log_file_path, "rt") as input_file:
            content = input_file.read()
        self.ui.viewing_area.setPlainText(content)
        # move to end of log file:
        self.ui.viewing_area.verticalScrollBar().setValue(self.ui.viewing_area.verticalScrollBar().maximum())

    def display_results(self):
        self.table_model = results.MyTableModel(self, self.Session.header, self.Session.output_storage)

        self.proxy_model = results.MySortProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.proxy_model.sortCaseSensitivity = False

        # make horizontal headers sortable in a special way:
        self.ui.data_preview.horizontalHeader().sectionClicked.connect(self.header_sorting)
        self.ui.data_preview.setModel(self.proxy_model)
        self.ui.data_preview.setSortingEnabled(False)

        diff = (self.Session.end_time - self.Session.start_time)
        duration = diff.seconds
        if duration > 3600:
            self.ui.label_time.setText("{} hrs, {}, min, {} s".format(duration // 3600, duration % 3600 // 60, duration % 60))
        elif duration > 60:
            self.ui.label_time.setText("{} min, {}.{} s".format(duration // 60, duration % 60, str(diff.microseconds)[:3]))
        else:
            self.ui.label_time.setText("{}.{} s".format(duration, str(diff.microseconds)[:3]))
        self.ui.row_numbers.setText("{}".format(len(self.Session.output_storage)))

    def exception_during_query(self):
        error_box.ErrorBox.show(self.exc_info)

    def query_finished(self):
        # Stop the progress indicator:
        self.ui.progress_bar.setRange(0,1)
        # show results:
        self.display_results()
        # update the logfile view if currently on display:
        if self.ui.tabbed_views.currentIndex() == 1:
            self.update_logfile()

    def header_sorting(self, index):
        header = self.ui.data_preview.horizontalHeader()

        if not self.proxy_model.sort_state[index]:
            self.proxy_model.sort_columns.append(index)
        self.proxy_model.sort_state[index] += 1
        
        probe_index = self.table_model.createIndex(0, index)
        probe_cell = probe_index.data()
        if type(probe_cell) in [unicode, str]:
            max_state = results.SORT_REV_DEC
        else:
            max_state = results.SORT_DEC

        if self.proxy_model.sort_state[index] > max_state:
            self.proxy_model.sort_state[index] = results.SORT_NONE
            self.proxy_model.sort_columns.remove(index)

        self.proxy_model.sort(0, QtCore.Qt.AscendingOrder)

    def run_query(self):
        self.getGuiValues()
        if self.ui.radio_query_string.isChecked():
            options.cfg.query_list = options.cfg.query_list[0].splitlines()
            self.Session = SessionCommandLine()
        else:
            self.Session = SessionInputFile()
        
        self.ui.progress_bar.setRange(0, 0)

        self.thread = QtProgress.ProgressThread(self.Session.run_queries, self)
        self.thread.taskFinished.connect(self.query_finished)
        self.thread.taskException.connect(self.exception_during_query)
        self.thread.start()
        
    def run_statistics(self):
        return
        self.getGuiValues()
        Session = SessionStatistics()
        ProgressIndicator.RunThread(Session.run_queries, "Querying...")
        finish = ResultsViewer(Session).exec_()
        

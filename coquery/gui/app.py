# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from session import *
from defines import *
from pyqt_compat import QtCore, QtGui
import __init__
import coqueryUi
import csvOptions
import QtProgress
import wizard
import results 
import error_box
import codecs
import logging
import sqlwrap

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class GuiHandler(logging.StreamHandler):
    def __init__(self, *args):
        super(GuiHandler, self).__init__(*args)
        self.log_data = []
        self.app = None
        
    def setGui(self, app):
        self.app = app
        
    def emit(self, record):
        try:
            self.log_data.append(record)
            if len(self.log_data) == 1:
                self.app.ui.log_table.horizontalHeader().setStretchLastSection(True)
                
            self.app.log_table.layoutChanged.emit()
        except:
            self.handleError(record)

class LogTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, *args):
        super(LogTableModel, self).__init__(parent, *args)
        self.content = options.cfg.gui_logger.log_data
        self.header = ["Date", "Time", "Level", "Message"]
        
    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()
        
        record = self.content[row]
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return record.asctime.split()[0]
            elif column == 1:
                return record.asctime.split()[1]
            elif column == 2:
                return record.levelname
            elif column == 3:
                return record.message            
        elif role == QtCore.Qt.ForegroundRole:
            if record.levelno in [logging.ERROR, logging.CRITICAL]:
                return QtGui.QBrush(QtCore.Qt.white)
            else:
                return None
        elif role == QtCore.Qt.BackgroundRole:
            if record.levelno == logging.WARNING:
                return QtGui.QBrush(QtCore.Qt.yellow)
            elif record.levelno in [logging.ERROR, logging.CRITICAL]:
                return QtGui.QBrush(QtCore.Qt.red)
        else:
            return None
        
    def rowCount(self, parent):
        return len(self.content)

    def columnCount(self, parent):
        return len(self.header)

class LogProxyModel(QtGui.QSortFilterProxyModel):
    def headerData(self, index, orientation, role):
        # column names:
        if orientation == QtCore.Qt.Vertical:
            return None
        header = self.sourceModel().header
        if not header or index > len(header):
            return None
        
        if role == QtCore.Qt.DisplayRole:
            return header[index]
        
class CoqueryApp(QtGui.QMainWindow, wizard.CoqueryWizard):
    """ Coquery as standalone application. """
    
    def setup_menu_actions(self):
        self.ui.action_save_results.triggered.connect(self.save_results)
        self.ui.action_quit.triggered.connect(self.save_results)
        self.ui.action_build_corpus.triggered.connect(self.build_corpus)
        self.ui.action_remove_corpus.triggered.connect(self.remove_corpus)
    
    def setup_hooks(self):
        super(CoqueryApp, self).setup_hooks()
        # hook run query button:
        self.ui.button_run_query.clicked.connect(self.run_query)
        # hook run statistics button:
        self.ui.button_show_statistics.clicked.connect(self.run_statistics)
    
    def setup_app(self):
        """ initializes all widgets with suitable data """
        # add available resources to corpus dropdown box:
        corpora = [x.upper() for x in sorted(resource_list.get_available_resources().keys())]
        self.ui.combo_corpus.addItems(corpora)

        self.setup_hooks()
        self.setup_menu_actions()
        
        self.change_corpus()
        self.enable_output_option()

        self.log_table = LogTableModel(self)
        self.log_proxy = LogProxyModel()
        self.log_proxy.setSourceModel(self.log_table)
        self.log_proxy.sortCaseSensitivity = False
        self.ui.log_table.setModel(self.log_proxy)
 
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        
        self.file_content = None
        
        self.ui = coqueryUi.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_app()
        self.csv_options = None
        self.query_thread = None
        self.last_results_saved = True
        
    def display_results(self):
        self.table_model = results.MyTableModel(self, self.Session.header, self.Session.output_storage)

        self.proxy_model = results.MySortProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.proxy_model.sortCaseSensitivity = False

        # make horizontal headers sortable in a special way:
        self.ui.data_preview.horizontalHeader().sectionClicked.connect(self.header_sorting)
        self.ui.data_preview.setModel(self.proxy_model)
        self.ui.data_preview.setSortingEnabled(False)
        self.last_results_saved = False

    def save_results(self):
        name = QtGui.QFileDialog.getSaveFileName(directory="~")
        if type(name) == tuple:
            name = name[0]
        if name:
            try:
                with codecs.open(name, "wt") as output_file:
                    writer = UnicodeWriter(output_file, delimiter=options.cfg.output_separator)
                    writer.writerow(self.Session.header)
                    for y in range(self.proxy_model.rowCount()):
                        writer.writerow([self.proxy_model.index(y, x).data() for x in range(self.proxy_model.columnCount())])
            except IOError as e:
                QtGui.QMessageBox.critical(self, "Disk error", "An error occurred while accessing the disk storage. The results have not been saved.")
            else:
                self.last_results_saved = True
    
    def exception_during_query(self):
        error_box.ErrorBox.show(self.exc_info, self.exception)

    def query_finished(self):
        self.set_query_button()
        # Stop the progress indicator:
        self.ui.progress_bar.setRange(0, 1)
        # show results:
        self.display_results()
        self.query_thread = None
        try:
            diff = (self.Session.end_time - self.Session.start_time)
        except TypeError:
            duration_str = "NA"
        else:
            duration = diff.seconds
            if duration > 3600:
                duration_str = "{} hrs, {}, min, {} s".format(duration // 3600, duration % 3600 // 60, duration % 60)
            elif duration > 60:
                duration_str = "{} min, {}.{} s".format(duration // 60, duration % 60, str(diff.microseconds)[:3])
            else:
                duration_str = "{}.{} s".format(duration, str(diff.microseconds)[:3])
        
        self.ui.statusbar.showMessage("Number of rows: {:<8}      Query duration: {:<10}".format(
            len(self.Session.output_storage), duration_str))        

    def header_sorting(self, index):
        header = self.ui.data_preview.horizontalHeader()

        if not self.proxy_model.sort_state[index]:
            self.proxy_model.sort_columns.append(index)
        self.proxy_model.sort_state[index] += 1
        
        probe_index = self.table_model.createIndex(0, index)
        probe_cell = probe_index.data()
        if type(probe_cell) in [unicode, str, QtCore.QString]:
            max_state = results.SORT_REV_DEC
        else:
            max_state = results.SORT_DEC

        if self.proxy_model.sort_state[index] > max_state:
            self.proxy_model.sort_state[index] = results.SORT_NONE
            self.proxy_model.sort_columns.remove(index)

        self.proxy_model.sort(0, QtCore.Qt.AscendingOrder)

    def set_query_button(self):
        """ Set the action button to start queries. """
        self.ui.button_run_query.clicked.disconnect()
        self.ui.button_run_query.clicked.connect(self.run_query)
        self.ui.button_run_query.setText("Query")
        self.ui.button_run_query.setIcon(QtGui.QIcon.fromTheme(_fromUtf8("media-playback-start")))
        
    def set_stop_button(self):
        """ Set the action button to stop queries. """
        self.ui.button_run_query.clicked.disconnect()
        self.ui.button_run_query.clicked.connect(self.stop_query)
        self.ui.button_run_query.setText("Stop")
        self.ui.button_run_query.setIcon(QtGui.QIcon.fromTheme(_fromUtf8("media-playback-stop")))
    
    def stop_query(self):
        msg_query_running = "<p>The last query has not finished yet. If you interrupt it, the results that have been retrieved so far will be discarded.</p><p>Do you really want to interrupt this query?</p>"
        response = QtGui.QMessageBox.warning(self, "Unfinished query", msg_query_running, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if response == QtGui.QMessageBox.Yes:
            logger.warning("Last query is incomplete.")
            self.ui.button_run_query.setEnabled(False)
            self.ui.button_run_query.setText("Wait...")
            self.ui.statusbar.showMessage("Terminating query...")
            self.query_thread.terminate()
            self.query_thread.wait()
            self.ui.statusbar.showMessage("Last query interrupted.")
            self.Session.Corpus.resource.DB.kill_connection()
            self.ui.button_run_query.setEnabled(True)
            self.ui.progress_bar.setRange(0, 1)
            self.set_query_button()
        
    def run_query(self):
        self.set_stop_button()
        self.ui.statusbar.showMessage("Running query...")
        
        self.getGuiValues()
        if self.ui.radio_query_string.isChecked():
            options.cfg.query_list = options.cfg.query_list[0].splitlines()
            self.Session = SessionCommandLine()
        else:
            self.Session = SessionInputFile()
        
        self.ui.progress_bar.setRange(0, 0)
        self.query_thread = QtProgress.ProgressThread(self.Session.run_queries, self)
        self.query_thread.taskFinished.connect(self.query_finished)
        self.query_thread.taskException.connect(self.exception_during_query)
        self.query_thread.start()
        
    def run_statistics(self):
        self.getGuiValues()
        self.Session = StatisticsSession()
        self.ui.statusbar.showMessage("Gathering corpus statistics...")
        self.ui.progress_bar.setRange(0, 0)
        self.query_thread = QtProgress.ProgressThread(self.Session.run_queries, self)
        self.query_thread.taskFinished.connect(self.query_finished)
        self.query_thread.taskException.connect(self.exception_during_query)
        self.query_thread.start()
        
    def save_configuration(self):
        pass
        
    def remove_corpus(self):
        if self.ui.combo_corpus.isEnabled():
            current_corpus = str(self.ui.combo_corpus.currentText())
            resource, _, _, module = resource_list.get_available_resources()[current_corpus.lower()]
            database = resource.db_name
            msg_corpus_remove = "<p><b>You have requested to remove the corpus '{}'.</b></p><p>This step cannot be reverted. If you proceed, the corpus will not be available for further queries before you install it again.</p><p>Removing this corpus will free approximately {} of disk memory.</p><p><p>Do you really want to remove the corpus?</p>".format(current_corpus, database, "xxx")
            
            response = QtGui.QMessageBox.warning(
                self, "Remove corpus", msg_corpus_remove, QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            
            if response == QtGui.QMessageBox.Yes:
                DB = sqlwrap.SqlDB(Host=options.cfg.db_host, Port=options.cfg.db_port, User=options.cfg.db_user, Password=options.cfg.db_password)
                self.ui.progress_bar.setRange(0, 1)
                self.ui.progress_bar.setFormat("Removing corpus '{}'".format(current_corpus))
                DB.execute("DROP DATABASE {}".format(database))
                os.remove(module)
                
                self.ui.progress_bar.setRange(0, 0)
                self.ui.progress_bar.setFormat("Idle.")
                self.fill_combo_corpus()
                logger.warning("Removed corpus {}.".format(current_corpus))
    
    def build_corpus(self):
        sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../tools")))
        import install_generic
        import corpusbuilder        
        corpusbuilder.BuilderGui(install_generic.GenericCorpusBuilder, self)
        self.fill_combo_corpus()
            
    def closeEvent(self, event):
        if not self.last_results_saved:
            msg_query_running = "<p>The last query results have not been saved. If you quit now, they will be lost.</p><p>Do you really want to quit?</p>"
            response = QtGui.QMessageBox.warning(self, "Unsaved results", msg_query_running, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if response == QtGui.QMessageBox.Yes:
                event.accept()
                self.save_configuration()
            else:
                event.ignore()
        else:
            event.accept()
            self.save_configuration()
            
            
logger = logging.getLogger(__init__.NAME)

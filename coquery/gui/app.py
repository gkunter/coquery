# -*- coding: utf-8 -*-
"""
app.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import sys
import importlib
import os
import codecs
import random
import logging
from collections import defaultdict

import numpy as np
import pandas as pd

from coquery import queries
from coquery import sqlhelper
from coquery.session import *
from coquery.defines import *
from coquery.unicode import utf8

from . import classes
from . import errorbox
from . import contextviewer
from .pyqt_compat import QtCore, QtGui, QtHelp
from .ui import coqueryUi


# add required paths:
sys.path.append(options.cfg.base_path)
sys.path.append(os.path.join(options.cfg.base_path, "visualizer"))
sys.path.append(os.path.join(options.cfg.base_path, "installer"))

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

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

class GuiHandler(logging.StreamHandler):
    def __init__(self, *args):
        super(GuiHandler, self).__init__(*args)
        self.log_data = []
        self.app = None
        
    def setGui(self, app):
        self.app = app
        
    def emit(self, record):
        self.log_data.append(record)

class CoqueryApp(QtGui.QMainWindow):
    """ Coquery as standalone application. """

    corpusListUpdated = QtCore.Signal()

    def __init__(self, parent=None):
        """ Initialize the main window. This sets up any widget that needs
        spetial care, and also sets up some special attributes that relate
        to the GUI, including default appearances of the columns."""
        QtGui.QMainWindow.__init__(self, parent)

        self.file_content = None
        self.csv_options = None
        self.query_thread = None
        self.last_results_saved = True
        self.last_connection = None
        self.last_connection_state = None
        self.last_index = None
        self.corpus_manager = None
        
        self.widget_list = []
        self.Session = None
        
        self._first_corpus = False
        if options.cfg.first_run and not options.cfg.current_resources:
            self._first_corpus = True
        
        size = QtGui.QApplication.desktop().screenGeometry()
        # Retrieve font and metrics for the CoqItemDelegates
        options.cfg.font = options.cfg.app.font()
        options.cfg.metrics = QtGui.QFontMetrics(options.cfg.font)

        self.ui = coqueryUi.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setMenuBar(self.ui.menubar)
        
        self.setup_app()

        # the dictionaries column_width and column_color store default
        # attributes of the columns by display name. This means that problems
        # may arise if several columns have the same name!
        # FIXME: Make sure that the columns are identified correctly.
        self.column_width = {}
        self.column_color = {}
        
        options.cfg.main_window = self
        options.settings = QtCore.QSettings(
            os.path.join(options.get_home_dir(), "coquery.ini"),
             QtCore.QSettings.IniFormat, self)

        try:
            self.restoreGeometry(options.settings.value("main_geometry"))
        except TypeError:
            pass
        try:
            self.restoreState(options.settings.value("main_state"))
        except TypeError:
            pass
        options.cfg.figure_font = options.settings.value("figure_font", QtGui.QLabel().font())
        options.cfg.table_font = options.settings.value("table_font", QtGui.QLabel().font())
        options.cfg.context_font = options.settings.value("context_font", QtGui.QLabel().font())

        # Taskbar icons in Windows require a workaround as described here:
        # https://stackoverflow.com/questions/1551605#1552105
        if sys.platform == "win32":
            import ctypes
            CoqId = 'Coquery.Coquery.{}'.format(VERSION)
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(CoqId)        
        
    def setup_app(self):
        """ Initialize all widgets with suitable data """

        self.ui.options_tree = self.create_output_options_tree()
        self.ui.output_columns.addWidget(self.ui.options_tree)
        
        if options.cfg.current_resources:
            # add available resources to corpus dropdown box:
            corpora = sorted(list(options.cfg.current_resources.keys()))
            self.ui.combo_corpus.addItems(corpora)
        
        index = self.ui.combo_corpus.findText(options.cfg.corpus)
        if index > -1:
            self.ui.combo_corpus.setCurrentIndex(index)
        
        # chamge the default query string edit to the sublassed edit class:
        self.ui.layout_query.removeWidget(self.ui.edit_query_string)
        self.ui.edit_query_string.close()        
        edit_query_string = classes.CoqTextEdit(self)
        edit_query_string.setObjectName("edit_query_string")
        self.ui.layout_query.addWidget(edit_query_string, 0, 1, 1, 2)
        self.ui.edit_query_string = edit_query_string
        
        # fix alignment of radio buttons:
        self.ui.layout_query.setAlignment(self.ui.radio_query_string, QtCore.Qt.AlignTop)
        self.ui.layout_query.setAlignment(self.ui.radio_query_file, QtCore.Qt.AlignTop)
        
        self.ui.verticalLayout_3.setAlignment(self.ui.box_corpus_select, QtCore.Qt.AlignTop)
        self.ui.verticalLayout_3.setAlignment(self.ui.box_context_mode, QtCore.Qt.AlignTop)
        self.ui.verticalLayout_3.setAlignment(self.ui.box_context_mode, QtCore.Qt.AlignTop)

        self.ui.stopword_switch = classes.CoqSwitch(state=options.cfg.use_stopwords)
        self.ui.stopword_layout.addWidget(self.ui.stopword_switch)
        self.ui.stopword_switch.toggled.connect(self.toggle_stopword_switch)
        self.set_stopword_button()
                
        self.ui.filter_switch = classes.CoqSwitch(state=options.cfg.use_corpus_filters)
        self.ui.filter_switch.toggled.connect(self.toggle_filter_switch)
        self.ui.filter_layout.addWidget(self.ui.filter_switch)
        self.set_filter_button()        

        ## set auto-completer for the filter edit:
        #self.filter_variable_model = QtGui.QStringListModel()
        #self.completer = QtGui.QCompleter()
        #self.completer.setModel(self.filter_variable_model)
        #self.completer.setCompletionMode(QtGui.QCompleter.InlineCompletion)
        #self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        #self.ui.filter_box.edit_tag.setCompleter(self.completer)

        # use a file system model for the file name auto-completer::
        self.dirModel = QtGui.QFileSystemModel()
        # make sure that the model is updated on changes to the file system:
        self.dirModel.setRootPath(QtCore.QDir.currentPath())
        self.dirModel.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDotAndDotDot)

        # set auto-completer for the input file edit:
        self.path_completer = QtGui.QCompleter()
        self.path_completer.setModel(self.dirModel)
        self.path_completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.ui.edit_file_name.setCompleter(self.path_completer)

        self.setup_hooks()
        self.setup_menu_actions()
        self.setup_icons()
        
        self.change_corpus()

        self.set_query_button()
        
        self.ui.data_preview.setEnabled(False)
        self.ui.menuAnalyse.setEnabled(False)

        # set splitter stretches:
        self.ui.splitter.setStretchFactor(0, 1)
        self.ui.splitter.setStretchFactor(1, 0)
        self.ui.splitter_2.setStretchFactor(0, 0)
        self.ui.splitter_2.setStretchFactor(1, 1)

        self.table_model = classes.CoqTableModel(self)
        self.table_model.dataChanged.connect(self.table_model.sort)
        self.table_model.columnVisibilityChanged.connect(self.reaggregate)
        self.table_model.rowVisibilityChanged.connect(self.update_row_visibility)

        header = self.ui.data_preview.horizontalHeader()
        header.sectionResized.connect(self.result_column_resize)
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_header_menu)
        header.sectionMoved.connect(self.column_moved)

        header = self.ui.data_preview.verticalHeader()
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_row_header_menu)

        self.ui.data_preview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.ui.data_preview.clicked.connect(self.result_cell_clicked)
        self.ui.data_preview.horizontalHeader().setMovable(True)
        self.ui.data_preview.setSortingEnabled(False)

        self.ui.data_preview.setSelectionBehavior(QtGui.QAbstractItemView.SelectionBehavior(QtGui.QAbstractItemView.SelectRows|QtGui.QAbstractItemView.SelectColumns))


        self.ui.status_message = QtGui.QLabel("{} {}".format(NAME, VERSION))

        self.ui.combo_config = QtGui.QComboBox()

        self.ui.status_progress = QtGui.QProgressBar()
        self.ui.status_progress.hide()

        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout(widget)
        layout.setContentsMargins(4, 0, 0, 0)
        layout.addWidget(self.ui.status_message)
        layout.addWidget(self.ui.status_progress)
        layout.addItem(QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))        
        layout.addWidget(QtGui.QLabel(_translate("MainWindow", "Connection: ", None)))
        layout.addWidget(self.ui.combo_config)

        self.statusBar().layout().setContentsMargins(0, 0, 0, 0)
        self.statusBar().setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        self.statusBar().addWidget(widget, 1)

        self.change_mysql_configuration(options.cfg.current_server)
        self.ui.combo_config.currentIndexChanged.connect(self.switch_configuration)
        
        state = self.test_mysql_connection()
        if not state:
            self.disable_corpus_widgets()
        
        self.connection_timer = QtCore.QTimer()
        self.connection_timer.timeout.connect(self.test_mysql_connection)
        self.connection_timer.start(10000)

    def statusBar(self):
        if hasattr(self.ui, "statusbar"):
            return self.ui.statusbar
        else:
            return super(CoqueryApp, self).statusbar()

    def setup_icons(self):
        self.ui.action_help.setIcon(self.get_icon("life-buoy"))
        self.ui.action_connection_settings.setIcon(self.get_icon("database"))
        self.ui.action_settings.setIcon(self.get_icon("wrench-screwdriver"))
        self.ui.action_build_corpus.setIcon(self.get_icon("sign-add"))
        self.ui.action_manage_corpus.setIcon(self.get_icon("database_2"))
        self.ui.action_corpus_documentation.setIcon(self.get_icon("sign-info"))
        self.ui.action_statistics.setIcon(self.get_icon("monitor"))
        self.ui.action_quit.setIcon(self.get_icon("sign-error"))
        self.ui.action_view_log.setIcon(self.get_icon("calendar-clock"))
        self.ui.action_save_results.setIcon(self.get_icon("floppy"))
        self.ui.action_save_selection.setIcon(self.get_icon("floppy"))
        self.ui.button_browse_file.setIcon(self.get_icon("folder"))
        self.ui.button_file_options.setIcon(self.get_icon("table"))

    def setup_menu_actions(self):
        """ Connect menu actions to their methods."""
        self.ui.action_save_results.triggered.connect(self.save_results)
        self.ui.action_save_selection.triggered.connect(lambda: self.save_results(selection=True))
        self.ui.action_copy_to_clipboard.triggered.connect(lambda: self.save_results(selection=True, clipboard=True))
        self.ui.action_create_textgrid.triggered.connect(self.create_textgrids)
        self.ui.action_quit.triggered.connect(self.close)
        self.ui.action_build_corpus.triggered.connect(self.build_corpus)
        self.ui.action_manage_corpus.triggered.connect(self.manage_corpus)
        self.ui.action_remove_corpus.triggered.connect(self.remove_corpus)
        self.ui.action_settings.triggered.connect(self.settings)
        self.ui.action_connection_settings.triggered.connect(self.connection_settings)
        self.ui.action_statistics.triggered.connect(self.run_statistics)
        self.ui.action_corpus_documentation.triggered.connect(self.open_corpus_help)
        self.ui.action_about_coquery.triggered.connect(self.show_about)
        self.ui.action_help.triggered.connect(self.help)
        self.ui.action_view_log.triggered.connect(self.show_log)
        self.ui.action_mysql_server_help.triggered.connect(self.show_mysql_guide)
        
        self.ui.action_barcode_plot.triggered.connect(lambda: self.visualize_data("barcodeplot"))
        self.ui.action_beeswarm_plot.triggered.connect(lambda: self.visualize_data("beeswarmplot"))

        self.ui.action_tree_map.triggered.connect(lambda: self.visualize_data("treemap"))
        self.ui.action_heat_map.triggered.connect(lambda: self.visualize_data("heatmap"))
        self.ui.action_bubble_chart.triggered.connect(lambda: self.visualize_data("bubbleplot"))
    
        self.ui.menuDensity_plots.setEnabled(False)
        self.ui.action_kde_plot.triggered.connect(lambda: self.visualize_data("densityplot"))
        self.ui.action_ecd_plot.triggered.connect(lambda: self.visualize_data("densityplot", cumulative=True))
            
        self.ui.action_barchart_plot.triggered.connect(lambda: self.visualize_data("barplot"))
        self.ui.action_percentage_bars.triggered.connect(lambda: self.visualize_data("barplot", percentage=True, stacked=True))
        self.ui.action_stacked_bars.triggered.connect(lambda: self.visualize_data("barplot", percentage=False, stacked=True))
        
        self.ui.action_percentage_area_plot.triggered.connect(lambda: self.visualize_data("timeseries", area=True, percentage=True, smooth=True))
        self.ui.action_stacked_area_plot.triggered.connect(lambda: self.visualize_data("timeseries", area=True, percentage=False, smooth=True))
        self.ui.action_line_plot.triggered.connect(lambda: self.visualize_data("timeseries", area=False, percentage=False, smooth=True))
        
        self.ui.action_toggle_filters.triggered.connect(lambda: self.ui.filter_switch.toggle())
        self.ui.action_toggle_stopwords.triggered.connect(lambda: self.ui.stopword_switch.toggle())
        
        self.ui.menu_Results.aboutToShow.connect(self.show_results_menu)
        self.ui.menuCorpus.aboutToShow.connect(self.show_corpus_menu)
        self.ui.menuFile.aboutToShow.connect(self.show_file_menu)
        self.ui.menuSettings.aboutToShow.connect(self.show_settings_menu)

    def help(self):
        from . import helpviewer
        
        self.helpviewer = helpviewer.HelpViewer(parent=self)
        self.helpviewer.show()

    def show_file_menu(self):
        # leave if the results table is empty:
        if len(self.table_model.content.index) == 0:
            # disable the result-related menu entries:
            self.ui.action_save_selection.setDisabled(True)
            self.ui.action_save_results.setDisabled(True)
            self.ui.action_copy_to_clipboard.setDisabled(True)
            self.ui.action_create_textgrid.setDisabled(True)
            return

        # enable "Save results"
        self.ui.action_save_results.setEnabled(True)
        self.ui.action_create_textgrid.setEnabled(True)

        # enable "Save selection" and "Copy selection to clipboard" if there 
        # is a selection:
        if self.ui.data_preview.selectionModel() and self.ui.data_preview.selectionModel().selection():
            self.ui.action_save_selection.setEnabled(True)
            self.ui.action_copy_to_clipboard.setEnabled(True)
            
    def show_corpus_menu(self):
        if self.ui.combo_corpus.count():
            self.ui.action_corpus_documentation.setEnabled(True)
            self.ui.action_statistics.setEnabled(True)
        else:
            self.ui.action_corpus_documentation.setEnabled(False)
            self.ui.action_statistics.setEnabled(False)

    def show_results_menu(self):
        self.ui.menu_Results.clear()

        # Add Output column entry:
        if self.ui.options_tree.selectedItems():
            self.ui.menuOutputOptions = self.get_output_column_menu(selection=self.ui.options_tree.selectedItems())
            self.ui.menu_Results.addMenu(self.ui.menuOutputOptions)
        else:
            self.ui.action_output_options = QtGui.QAction(self.ui.menu_Results)
            self.ui.menu_Results.addAction(self.ui.action_output_options)
            self.ui.action_output_options.setDisabled(True)
            self.ui.action_output_options.setText(_translate("MainWindow", "No output column selected.", None))
            
        self.ui.menu_Results.addSeparator()

        self.ui.menuNoColumns = QtGui.QAction(self.ui.menu_Results)
        self.ui.menuNoColumns.setText(_translate("MainWindow", "No columns selected.", None))
        self.ui.menuNoColumns.setDisabled(True)
        self.ui.menu_Results.addAction(self.ui.menuNoColumns)

        self.ui.menuNoRows = QtGui.QAction(self.ui.menu_Results)
        self.ui.menuNoRows.setText(_translate("MainWindow", "No rows selected.", None))
        self.ui.menuNoRows.setDisabled(True)
        self.ui.menu_Results.addAction(self.ui.menuNoRows)

        select = self.ui.data_preview.selectionModel()

        if select:
            # Check if columns are selected
            if select.selectedColumns():
                # Add column submenu
                selection = []
                for x in self.ui.data_preview.selectionModel().selectedColumns():
                    selection.append(self.table_model.header[x.column()])
                
                self.ui.menuColumns = self.get_column_submenu(selection=selection)
                self.ui.menu_Results.insertMenu(self.ui.menuNoColumns, self.ui.menuColumns)
                self.ui.menu_Results.removeAction(self.ui.menuNoColumns)

            # Check if rows are selected
            if select.selectedRows():
                # Add rows submenu
                selection = []
                for x in self.ui.data_preview.selectionModel().selectedRows():
                    selection.append(self.table_model.content.index[x.row()])
                
                self.ui.menuRows = self.get_row_submenu(selection=selection)
                self.ui.menu_Results.insertMenu(self.ui.menuNoRows, self.ui.menuRows)
                self.ui.menu_Results.removeAction(self.ui.menuNoRows)

    def show_settings_menu(self):
        if options.cfg.stopword_list:
            self.ui.action_toggle_stopwords.setEnabled(True)
            self.ui.action_toggle_stopwords.setCheckable(True)

            if options.cfg.use_stopwords:
                self.ui.action_toggle_stopwords.setText(_translate("MainWindow", "Disable stopwords", None))
                self.ui.action_toggle_stopwords.setChecked(True)
            else:
                self.ui.action_toggle_stopwords.setText(_translate("MainWindow", "Use stopwords", None))
                self.ui.action_toggle_stopwords.setChecked(False)
        else:
            self.ui.action_toggle_stopwords.setEnabled(False)
            self.ui.action_toggle_stopwords.setText(_translate("MainWindow", "No stopwords", None))
            
        if options.cfg.filter_list:
            self.ui.action_toggle_filters.setEnabled(True)
            self.ui.action_toggle_filters.setCheckable(True)
            if options.cfg.use_corpus_filters:
                self.ui.action_toggle_filters.setChecked(True)
                self.ui.action_toggle_filters.setText(_translate("MainWindow", "Switch corpus filters off", None))
            else:
                self.ui.action_toggle_filters.setChecked(False)
                self.ui.action_toggle_filters.setText(_translate("MainWindow", "Switch corpus filters on", None))
        else:
            self.ui.action_toggle_filters.setEnabled(False)
            self.ui.action_toggle_filters.setText(_translate("MainWindow", "No corpus filters", None))

    def setup_hooks(self):
        """ 
        Hook up signals so that the GUI can adequately react to user 
        input.
        """
        # hook file browser button:
        self.ui.button_browse_file.clicked.connect(self.select_file)
        # hook file options button:
        self.ui.button_file_options.clicked.connect(self.file_options)

        # hook up events so that the radio buttons are set correctly
        # between either query from file or query from string:
        self.focus_to_file = focusFilter()
        self.ui.edit_file_name.installEventFilter(self.focus_to_file)

        self.ui.edit_file_name.textChanged.connect(self.switch_to_file)
        self.ui.edit_file_name.textChanged.connect(self.verify_file_name)
        self.focus_to_query = focusFilter()
        self.focus_to_query.focus.connect(self.switch_to_query)
        self.ui.edit_query_string.installEventFilter(self.focus_to_query)

        self.ui.combo_corpus.currentIndexChanged.connect(self.change_corpus)
        # hook run query button:
        self.ui.button_run_query.clicked.connect(self.run_query)

        self.ui.button_stopwords.clicked.connect(self.manage_stopwords)
        self.ui.button_filters.clicked.connect(self.manage_filters)
        
        self.ui.radio_context_none.toggled.connect(self.update_context_widgets)
        self.ui.radio_context_mode_kwic.toggled.connect(self.update_context_widgets)
        self.ui.radio_context_mode_string.toggled.connect(self.update_context_widgets)
        self.ui.radio_context_mode_columns.toggled.connect(self.update_context_widgets)
        
        # set up hooks so that the statistics columns are only available when 
        # the frequency aggregation is active:        
        self.ui.radio_aggregate_collocations.toggled.connect(self.toggle_frequency_columns)
        self.ui.radio_aggregate_frequencies.toggled.connect(self.toggle_frequency_columns)
        self.ui.radio_aggregate_none.toggled.connect(self.toggle_frequency_columns)
        self.ui.radio_aggregate_uniques.toggled.connect(self.toggle_frequency_columns)

        self.ui.radio_aggregate_collocations.clicked.connect(
            lambda: self.reaggregate(
                query_type=queries.CollocationQuery,
                recalculate=False))
        self.ui.radio_aggregate_frequencies.clicked.connect(
            lambda: self.reaggregate(
                query_type=queries.FrequencyQuery,
                recalculate=False))
        self.ui.radio_aggregate_contingency.clicked.connect(
            lambda: self.reaggregate(
                query_type=queries.ContingencyQuery,
                recalculate=False))
        self.ui.radio_aggregate_uniques.clicked.connect(
            lambda: self.reaggregate(
                query_type=queries.DistinctQuery,
                recalculate=False))
        self.ui.radio_aggregate_none.clicked.connect(
            lambda: self.reaggregate(
                query_type=queries.TokenQuery,
                recalculate=False))
            
        self.corpusListUpdated.connect(self.check_corpus_widgets)

    def enable_corpus_widgets(self):
        self.ui.options_area.setEnabled(True)
        self.ui.action_statistics.setEnabled(True)
        self.ui.action_remove_corpus.setEnabled(True)

    def disable_corpus_widgets(self):
        self.ui.options_area.setEnabled(False)
        self.ui.action_statistics.setEnabled(False)
        self.ui.action_remove_corpus.setEnabled(False)

    def check_corpus_widgets(self):
        if options.cfg.current_resources:
            self.enable_corpus_widgets()
        else:
            self.disable_corpus_widgets()

    def column_moved(self):
        if self.Session.query_type == queries.ContingencyQuery:
            self.reaggregate(query_type=queries.ContingencyQuery, recalculate=True)
        
    def result_column_resize(self, index, old, new):
        header = self.table_model.header[index].lower()
        options.cfg.column_width[header.replace(" ", "_").replace(":", "_")] = new

    def result_cell_clicked(self, index=None, token_id=None):
        """
        Launch the context viewer.
        """
        token_width = 1

        if index != None:
            model_index = index
            row = model_index.row()
            data = self.table_model.content.iloc[row]
            if ("coquery_invisible_corpus_id" not in self.Session.output_order or
                "coquery_invisible_number_of_tokens" not in self.Session.output_order or
                pd.isnull(data["coquery_invisible_corpus_id"]) or
                pd.isnull(data["coquery_invisible_number_of_tokens"])):
                if isinstance(self.Session, StatisticsSession):
                    column = data.index[model_index.column()]
                    self.show_unique_values(rc_feature=data["coquery_invisible_rc_feature"],
                                            uniques=column != "coq_statistics_entries")
                else:
                    QtGui.QMessageBox.critical(self, "Context error", msg_no_context_available)
                return
                    
            token_id = data["coquery_invisible_corpus_id"]
            token_width = data["coquery_invisible_number_of_tokens"]
            
        origin_id = options.cfg.main_window.Session.Corpus.get_source_id(token_id)
        
        viewer = contextviewer.ContextView(
            self.Session.Corpus, int(token_id), int(origin_id), int(token_width))
        viewer.show()
        self.widget_list.append(viewer)

    def verify_file_name(self):
        file_name = str(self.ui.edit_file_name.text())
        if not os.path.isfile(file_name):
            self.ui.edit_file_name.setStyleSheet('QLineEdit { background-color: rgb(255, 255, 192) }')
            self.ui.button_file_options.setEnabled(False)
            return False
        else:
            self.ui.edit_file_name.setStyleSheet('QLineEdit { background-color: white } ')
            self.ui.button_file_options.setEnabled(True)
            return True

    def switch_to_file(self):
        """ Toggle to query file input. """
        #self.ui.radio_query_file.setFocus()
        self.ui.radio_query_file.setChecked(True)

    def switch_to_query(self):
        """ Toggle to query string input. """
        self.ui.radio_query_string.setChecked(True)

    def create_output_options_tree(self):
        """ 
        Create and setup a tree widget for the output columns
        """
        tree = classes.CoqTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setRootIsDecorated(True)

        tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.get_output_column_menu)        
        
        tree.addLink.connect(self.add_link)
        tree.addFunction.connect(self.add_function)
        tree.removeItem.connect(self.remove_item)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tree.sizePolicy().hasHeightForWidth())
        tree.setSizePolicy(sizePolicy)

        return tree
    
    def toggle_frequency_columns(self):
        for root in [self.ui.options_tree.topLevelItem(i) for i in range(self.ui.options_tree.topLevelItemCount())]:
            if root.objectName().startswith("statistics"):
                for child in [root.child(i) for i in range(root.childCount())]:
                    if self.ui.radio_aggregate_frequencies.isChecked():
                        child.setDisabled(False)
                        try:
                            options.cfg.disabled_columns.remove(child.objectName())
                        except KeyError:
                            pass
                    else:
                        child.setDisabled(True)
                        options.cfg.disabled_columns.add(child.objectName())
    
    def finish_reaggregation(self):
        self.stop_progress_indicator()
        self.table_model.set_data(self.Session.output_object)
        self.display_results(drop=False)
        self.show_query_status()
        header = self.ui.data_preview.horizontalHeader()
            
    def reaggregate(self, query_type=None, recalculate=True):
        """
        Reaggregate the current data table when changing the visibility of
        the table columns.
        """
        if not self.Session:
            return
        self.unfiltered_tokens = len(self.Session.data_table.index)
        self.thread = classes.CoqThread(self.Session.aggregate_data, parent=self, recalculate=recalculate)
        self.thread.taskFinished.connect(self.finish_reaggregation)
        self.thread.taskException.connect(self.exception_during_query)

        if query_type and query_type != self.Session.query_type:
            self.Session.query_type.remove_output_columns(self.Session)
            self.Session.query_type = query_type
            self.Session.query_type.add_output_columns(self.Session)
        self.start_progress_indicator()
        self.thread.start()

    @staticmethod
    def get_icon(s, small_n_flat=True):
        """
        Return an icon that matches the given string.
        
        Parameters
        ----------
        s : str 
            The name of the icon. In the case of small-n-flat icons, the name 
            does not contain an extension, this is added automatically.
        small_n_flat : bool 
            True if the icon is from the 'small-n-flat' icon set. False if it 
            is artwork provided by Coquery (in the icons/artwork/ 
            subdirectory).
        """
        icon = QtGui.QIcon()
        if small_n_flat:
            path = os.path.join(options.cfg.base_path, "icons", "small-n-flat", "PNG", "{}.png".format(s))
        else:
            path = os.path.join(options.cfg.base_path, "icons", "artwork", s)
        icon.addFile(path)
        assert os.path.exists(path), "Image not found: {}".format(path)
        return icon

    def show_query_status(self):
        if not hasattr(self.Session, "end_time"):
            self.Session.end_time = datetime.datetime.now()
        try:
            diff = (self.Session.end_time - self.Session.start_time)
        except TypeError:
            duration_str = "NA"
        else:
            duration = diff.seconds
            if duration > 3600:
                duration_str = "{} hrs, {} min, {} s".format(duration // 3600, duration % 3600 // 60, duration % 60)
            elif duration > 60:
                duration_str = "{} min, {}.{} s".format(duration // 60, duration % 60, str(diff.microseconds)[:3])
            else:
                duration_str = "{}.{} s".format(duration, str(diff.microseconds)[:3])

        self.showMessage("Tokens: {:<8}   Data rows: {:<8}   Duration of last query: {:<10}".format(
            self.unfiltered_tokens, 
            len(self.table_model.content.index),
            duration_str))

    def change_corpus(self):
        """ 
        Change the output options list depending on the features available
        in the current corpus. If no corpus is avaiable, disable the options
        area and some menu entries. If any corpus is available, these widgets
        are enabled again.
        """
        if not options.cfg.current_resources:
            self.disable_corpus_widgets()
            self.ui.centralwidget.setEnabled(False)
        else:
            self.enable_corpus_widgets()
            self.ui.centralwidget.setEnabled(True)

        if self.ui.combo_corpus.count():
            corpus_name = utf8(self.ui.combo_corpus.currentText())
            self.resource, self.corpus, self.lexicon, self.path = options.cfg.current_resources[corpus_name]

            #self.ui.filter_box.resource = self.resource
            #corpus_variables = [x for _, x in self.resource.get_corpus_features()]
            #corpus_variables.append("Freq")
            #corpus_variables.append("Freq.pmw")
            #try:
                #self.filter_variable_model.setStringList(corpus_variables)
            #except AttributeError:
                #pass
        options.cfg.corpus = utf8(self.ui.combo_corpus.currentText())
        self.change_corpus_features()

    def change_corpus_features(self):
        """ 
        Construct a new output option tree.
        
        The content of the tree depends on the features that are available in
        the current resource. All features that were checked in the old output 
        option tree will also be checked in the new one. In this way, users 
        can easily change between corpora without loosing their output column 
        selections.        
        """
        
        if not options.cfg.current_resources:
            self.ui.options_tree.clear()
            return
        
        table_dict = self.resource.get_table_dict()
        # Ignore denormalized tables:
        tables = [x for x in table_dict.keys() if not "_denorm_" in x]
        # ignore internal  variables of the form {table}_id, {table}_table,
        # {table}_table_{other}
        for table in tables:
            for var in list(table_dict[table]):
                if var == "corpus_id":
                    continue
                if (var.endswith("_table") or var.endswith("_id") or var.startswith("{}_table".format(table))) or "_denorm_" in var:
                    table_dict[table].remove(var)
                    
        # Rearrange table names so that they occur in a sensible order:
        for x in reversed(["word", "lemma", "corpus", "speaker", "source", "file"]):
            if x in tables:
                tables.remove(x)
                tables.insert(0, x)
        tables.remove("coquery")
        tables.remove("statistics")
        tables.append("statistics")
        tables.append("coquery")
        
        last_checked = list(self.ui.options_tree.get_checked())
        
        # After installing the first corpus during the first launch of 
        # Coquery, the word_label column is automatically selected so that 
        # new users unfamiliar with the concept of output columns will get 
        # reasonable defaults:
        if options.cfg.first_run:
            if self._first_corpus:
                last_checked = ["word_label"]
                self._first_corpus = False
        
        self.ui.options_tree.clear()
        
        # populate the self.ui.options_tree with a root for each table:
        for table in tables:
            root = classes.CoqTreeItem()
            root.setObjectName(coqueryUi._fromUtf8("{}_table".format(table)))
            root.setFlags(root.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable)
            try:
                label = getattr(self.resource, str("{}_table".format(table)))
            except AttributeError:
                label = table.capitalize()
                
            root.setText(0, label)
            root.setCheckState(0, QtCore.Qt.Unchecked)
            if table_dict[table]:
                self.ui.options_tree.addTopLevelItem(root)
            
            # add a leaf for each table variable, in alphabetical order:
            for _, var in sorted([(getattr(self.resource, x), x) for x in table_dict[table]]):
                leaf = classes.CoqTreeItem()
                leaf.setObjectName(coqueryUi._fromUtf8(var))
                root.addChild(leaf)
                label = getattr(self.resource, var)
                # Add labels if this feature is mapped to a query item type
                try:
                    if var == self.resource.query_item_word:
                        label = "{} [Word]".format(label)
                except AttributeError:
                    pass
                try:
                    if var == self.resource.query_item_lemma:
                        label = "{} [Lemma]".format(label)
                except AttributeError:
                    pass
                try:
                    if var == self.resource.query_item_transcript:
                        label = "{} [Transcript]".format(label)
                except AttributeError:
                    pass
                try:
                    if var == self.resource.query_item_pos:
                        label = "{} [POS]".format(label)
                except AttributeError:
                    pass
                try:
                    if var == self.resource.query_item_gloss:
                        label = "{} [Gloss]".format(label)
                except AttributeError:
                    pass
                leaf.setText(0, label)
                if label != getattr(self.resource, var):
                    leaf.setIcon(0, self.get_icon("tag"))
                    root.setIcon(0, self.get_icon("tag"))

                if var in last_checked: 
                    leaf.setCheckState(0, QtCore.Qt.Checked)
                else:
                    leaf.setCheckState(0, QtCore.Qt.Unchecked)
                leaf.update_checkboxes(0, expand=True)
        
    def fill_combo_corpus(self):
        """ 
        Add the available corpus names to the corpus selection combo box. 
        """
        try:
            self.ui.combo_corpus.currentIndexChanged.disconnect()
        except TypeError:
            # ignore error if the combo box was not yet connected
            pass

        # remember last corpus name:
        last_corpus = utf8(self.ui.combo_corpus.currentText())

        # add corpus names:
        self.ui.combo_corpus.clear()
        self.ui.combo_corpus.addItems(sorted(list(options.cfg.current_resources.keys())))

        # try to return to last corpus name:
        new_index = self.ui.combo_corpus.findText(last_corpus)
        if new_index == -1:
            new_index = 0
            
        self.ui.combo_corpus.setCurrentIndex(new_index)
        self.ui.combo_corpus.setEnabled(True)
        self.ui.combo_corpus.currentIndexChanged.connect(self.change_corpus)

        self.check_corpus_widgets()
            
    def display_results(self, drop=True):
        self.ui.data_preview.setEnabled(True)
        self.ui.data_preview.setFont(options.cfg.table_font)

        # enable menu entries:
        self.ui.action_save_results.setEnabled(True)
        self.ui.action_copy_to_clipboard.setEnabled(True)

        # Visualizations menu is disabled for corpus statistics:
        if isinstance(self.Session, StatisticsSession):
            self.ui.menuAnalyse.setEnabled(False)
        else:
            self.ui.menuAnalyse.setEnabled(True)

        
        self.table_model.set_header()

        self.ui.data_preview.setModel(self.table_model)

        if drop:
            # drop row colors and row visibility:
            options.cfg.row_visibility = collections.defaultdict(dict)
            options.cfg.row_color = {}

        # set column widths:
        for i, column in enumerate(self.table_model.header):
            if column.lower() in options.cfg.column_width:
                self.ui.data_preview.setColumnWidth(i, options.cfg.column_width[column.lower().replace(" ", "_").replace(":", "_")])
        
        #set delegates:
        header = self.ui.data_preview.horizontalHeader()
        for i in range(header.count()):
            column = self.table_model.header[header.logicalIndex(i)]
            if column in (
                "coq_conditional_probability_left", 
                "coq_conditional_probability_right",  
                "statistics_overall_proportion", 
                "statistics_query_proportion", 
                "coq_statistics_uniquenessratio"):
                deleg = classes.CoqProbabilityDelegate(self.ui.data_preview)
            elif column in ("statistics_column_total"):
                deleg = classes.CoqTotalDelegate(self.ui.data_preview)                
            else:
                deleg = classes.CoqResultCellDelegate(self.ui.data_preview)
            self.ui.data_preview.setItemDelegateForColumn(i, deleg)

        # reset row delegates if an ALL row has previously been set:
        if hasattr(self, "_old_row_delegate"):
            row, delegate = self._old_row_delegate
            self.ui.data_preview.setItemDelegateForRow(row, delegate)
            del self._old_row_delegate

        # set row delegate for ALL row of Contingency aggregates:
        if self.Session.query_type == queries.ContingencyQuery:
            row = len(self.table_model.content.index) - 1
            self._old_row_delegate = (row, self.ui.data_preview.itemDelegateForRow(row))
            self.ui.data_preview.setItemDelegateForRow(row, classes.CoqTotalDelegate(self.ui.data_preview))

        if self.table_model.rowCount():
            self.last_results_saved = False
        
        if options.cfg.memory_dump:
            memory_dump()

    def select_file(self):
        """ Call a file selector, and add file name to query file input. """
        name = QtGui.QFileDialog.getOpenFileName(directory=options.cfg.query_file_path)
        
        # getOpenFileName() returns different types in PyQt and PySide, fix:
        if type(name) == tuple:
            name = name[0]
        
        if name:
            options.cfg.query_file_path = os.path.dirname(utf8(name))
            self.ui.edit_file_name.setText(name)
            self.switch_to_file()
            
    def file_options(self):
        """ Get CSV file options for current query input file. """
        from . import csvoptions
        results = csvoptions.CSVOptions.getOptions(
            utf8(self.ui.edit_file_name.text()), 
            (options.cfg.input_separator,
             options.cfg.query_column_number,
             options.cfg.file_has_headers,
             options.cfg.skip_lines,
             options.cfg.quote_char),
            self, icon=options.cfg.icon)
        
        if results:
            (options.cfg.input_separator,
             options.cfg.query_column_number,
             options.cfg.file_has_headers,
             options.cfg.skip_lines,
             options.cfg.quote_char) = results
            
            if options.cfg.input_separator == "{tab}":
                options.cfg.input_separator = "\t"
            elif options.cfg.input_separator == "{space}":
                options.cfg.input_separator = " "
            self.switch_to_file()


    def set_stopword_button(self):
        if len(options.cfg.stopword_list):
            self.ui.stopword_switch.show()
        else:
            self.ui.stopword_switch.hide()
            self.ui.stopword_switch.setOff()
            options.cfg.use_stopwords = False

    def toggle_stopword_switch(self):
        options.cfg.use_stopwords = self.ui.stopword_switch.isOn()

    def manage_stopwords(self):
        from . import stopwords 
        old_list = options.cfg.stopword_list
        result = stopwords.Stopwords.manage(options.cfg.stopword_list, options.cfg.icon)
        if result != None:
            options.cfg.stopword_list = result
        self.set_stopword_button()
        # activate the filter switch if the filter list was empty before, but 
        # is filled now:
        if not old_list and options.cfg.stopword_list:
            self.ui.stopword_switch.setOn()
    
    def set_filter_button(self):
        if len(options.cfg.filter_list):
            self.ui.filter_switch.show()
        else:
            self.ui.filter_switch.hide()
            self.ui.filter_switch.setOff()
            options.cfg.use_corpus_filters = False

    def toggle_filter_switch(self):
        options.cfg.use_corpus_filters = self.ui.filter_switch.isOn()

    def manage_filters(self):
        from . import filterviewer
        old_list = options.cfg.filter_list
        result = filterviewer.Filters.manage(options.cfg.filter_list, options.cfg.icon)
        if result != None:
            options.cfg.filter_list = result
        self.set_filter_button()
        
        # activate the filter switch if the filter list was empty before, but 
        # is filled now:
        if not old_list and options.cfg.filter_list:
            self.ui.filter_switch.setOn()
            options.cfg.use_corpus_filters = True
    
    def save_results(self, selection=False, clipboard=False):
        if not clipboard:
            if selection:
                caption = "Save selected query results – Coquery"
            else:
                caption = "Save query results – Coquery"
            name = QtGui.QFileDialog.getSaveFileName(
                caption=caption,
                directory=options.cfg.results_file_path)
            if type(name) == tuple:
                name = name[0]
            if not name:
                return
            options.cfg.results_file_path = os.path.dirname(name)
        try:
            header = self.ui.data_preview.horizontalHeader()
            ordered_headers = [self.table_model.header[header.logicalIndex(i)] for i in range(header.count())]
            ordered_headers = [x for x in ordered_headers if options.cfg.column_visibility.get(x, True)]
            tab = self.table_model.content[ordered_headers]

            # exclude invisble rows:
            tab = tab.iloc[~tab.index.isin(pd.Series(
                list(options.cfg.row_visibility[self.Session.query_type].keys())))]
            
            # restrict to selection?
            if selection or clipboard:
                sel = self.ui.data_preview.selectionModel().selection()
                selected_rows = set([])
                selected_columns = set([])
                for x in sel.indexes():
                    selected_rows.add(x.row())
                    selected_columns.add(x.column())
                tab = tab.iloc[list(selected_rows)][list(selected_columns)]
            
            if clipboard:
                cb = QtGui.QApplication.clipboard()
                cb.clear(mode=cb.Clipboard)
                cb.setText(tab.to_csv(
                    sep=str("\t"),
                    index=False,
                    header=[options.cfg.main_window.Session.translate_header(x) for x in tab.columns],
                    encoding=options.cfg.output_encoding), mode=cb.Clipboard)
            else:
                tab.to_csv(name,
                        sep=options.cfg.output_separator,
                        index=False,
                        header=[options.cfg.main_window.Session.translate_header(x) for x in tab.columns],
                        encoding=options.cfg.output_encoding)
        except IOError as e:
            QtGui.QMessageBox.critical(self, "Disk error", msg_disk_error)
        except (UnicodeEncodeError, UnicodeDecodeError):
            QtGui.QMessageBox.critical(self, "Encoding error", msg_encoding_error)
        else:
            if not selection and not clipboard:
                self.last_results_saved = True
    

    def create_textgrids(self):
        if not options._use_tgt:
            errorbox.alert_missing_module("tgt", self)
            return

        name = QtGui.QFileDialog.getExistingDirectory(directory=options.cfg.textgrids_file_path, options=QtGui.QFileDialog.ReadOnly|QtGui.QFileDialog.ShowDirsOnly|QtGui.QFileDialog.HideNameFilterDetails)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.corpus_source_path = name
        else:
            return

        from coquery.textgrids import TextgridWriter

        options.cfg.textgrids_file_path = name

        header = self.ui.data_preview.horizontalHeader()
        ordered_headers = [self.table_model.header[header.logicalIndex(i)] for i in range(header.count())]
        ordered_headers = [x for x in ordered_headers if options.cfg.column_visibility.get(x, True)]
        ordered_headers.append("coquery_invisible_corpus_id")
        tab = self.table_model.content[ordered_headers]

        # exclude invisble rows:
        tab = tab.iloc[~tab.index.isin(pd.Series(
            options.cfg.row_visibility[self.Session.query_type].keys()))]
            
        writer = TextgridWriter(tab, self.Session.Resource)
        n = writer.write_grids(name)
        self.showMessage("Done writing {} text grids to {}.".format(n, name))
    
    def showMessage(self, S):
        self.ui.status_message.setText(S)
        
    def showConnectionStatus(self, S):
        self.ui.status_server.setText(S)
    
    def exception_during_query(self):
        if isinstance(self.exception, UnsupportedQueryItemError):
            QtGui.QMessageBox.critical(self, "Error in query string – Coquery", str(self.exception), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        else:
            errorbox.ErrorBox.show(self.exc_info, self.exception)
        self.showMessage("Query failed.")
        self.set_query_button()
        self.stop_progress_indicator()
        
    def start_progress_indicator(self):
        """ Show the progress indicator, and make it move. """
        self.ui.status_progress.setRange(0, 0)
        self.ui.status_progress.show()
        
    def stop_progress_indicator(self):
        """ Stop the progress indicator from moving, and hide it as well. """
        self.ui.status_progress.setRange(0, 1)
        self.ui.status_progress.hide()
        
    def finalize_query(self):
        self.query_thread = None
        self.showMessage("Preparing results table...")
        self.Session = self.new_session
        del self.new_session
        self.reaggregate()
        self.set_query_button()
        self.stop_progress_indicator()
        
        if isinstance(self.Session, StatisticsSession):
            self.ui.group_aggregation.setEnabled(False)
        else:
            self.ui.group_aggregation.setEnabled(True)
        
        # Create an alert in the system taskbar to indicate that the query has 
        # completed:
        options.cfg.app.alert(self, 0)
        
    def get_output_column_menu(self, point=None, selection=[]):
        if point:
            item = self.ui.options_tree.itemAt(point)
        else:
            item = selection[0]

        if not item:
            return

        # create a context menu:
        menu = QtGui.QMenu("Output column options", self)
        action = QtGui.QWidgetAction(self)

        # if point is set, the menu was called as a context menu: 
        if point:
            # Use column name as header
            label = QtGui.QLabel("<b>{}</b>".format(item.text(0)), self)
            label.setAlignment(QtCore.Qt.AlignCenter)
            action.setDefaultWidget(label)
            menu.addAction(action)
        
        # no options are shown for entries from the special tables and for 
        # linked tables (but for columns from linked tables)
        if not (utf8(item.objectName()).startswith("coquery") or 
                utf8(item.objectName()).startswith("statistics") or
                utf8(item.objectName()).endswith("_table")):
            add_link = QtGui.QAction("&Link to external table", self)
            add_function = QtGui.QAction("&Add a function", self)
            remove_link = QtGui.QAction("&Remove link", self)
            remove_function = QtGui.QAction("&Remove function", self)
            
            parent = item.parent()

            if not item._func:
                view_unique = QtGui.QAction("View &unique values", self)
                view_unique.triggered.connect(lambda: self.show_unique_values(item))
                menu.addAction(view_unique)
                view_entries = QtGui.QAction("View all &values", self)
                view_entries.triggered.connect(lambda: self.show_unique_values(item, uniques=False))
                menu.addAction(view_entries)
                view_unique.setEnabled(options.cfg.gui.test_mysql_connection())
                view_entries.setEnabled(options.cfg.gui.test_mysql_connection())
                menu.addSeparator()

                if item._link_by or (parent and parent._link_by):
                    menu.addAction(remove_link)
                    remove_link.triggered.connect(lambda: self.ui.options_tree.removeItem.emit(item))
                else:
                    menu.addAction(add_link)
                    add_link.triggered.connect(lambda: self.ui.options_tree.addLink.emit(item))
                menu.addAction(add_function)
                add_function.triggered.connect(lambda: self.ui.options_tree.addFunction.emit(item))

            if item._func:
                menu.addAction(remove_function)
                remove_function.triggered.connect(lambda: self.ui.options_tree.removeItem.emit(item))
        else:
            if utf8(item.objectName()).endswith("_table"):
                unavailable = QtGui.QAction(_translate("MainWindow", "No option available for tables.", None), self)
            else:
                 unavailable = QtGui.QAction(_translate("MainWindow", "No option available for special columns.", None), self)
            unavailable.setDisabled(True)
            menu.addAction(unavailable)      
            
        # if point is set, the menu was called as a context menu: 
        if point:
            menu.popup(self.ui.options_tree.mapToGlobal(point))
            menu.exec_()            
        else:
            return menu

    def show_unique_values(self, item=None, rc_feature=None, uniques=True):
        from . import uniqueviewer
        resource = self.resource
        if item is not None:
            rc_feature = item.objectName()
        else:
            rc_feature = rc_feature
        
        _, db_name, table, feature = resource.split_resource_feature(rc_feature)
        if not db_name:
            db_name = resource.db_name
        uniqueviewer.UniqueViewer.show(
            "{}_{}".format(table, feature),
            db_name, uniques=uniques, parent=self)

    def get_column_submenu(self, selection=[], point=None):
        """
        Create a submenu for one or more columns.
        
        Column submenus contain obtions for hiding, showing, renaming, 
        colorizing, and sorting result columns. The set of available options 
        depends on the number of columns selected, the data type of their 
        content, and their current visibility.
        
        Column submenus can either be generated as context menus for the 
        headers in the results table, or from the Output main menu entry. 
        In the former case, the parameter 'point' indicates the screen 
        position of the context menu. In the latter case, point is None.
        
        Parameters
        ----------
        selection : list
            A list of column names 
        point : QPoint
            The screen position for which the context menu is requested
        """
        
        # show menu about the column
        menu = QtGui.QMenu("Column options", self)

        if point:
            header = self.ui.data_preview.horizontalHeader()
            index = header.logicalIndexAt(point.x())
            column = self.table_model.header[index]
            if column not in selection:
                selection = [column]

        display_name = "<br/>".join([options.cfg.main_window.Session.translate_header(x) for x in selection])

        action = QtGui.QWidgetAction(self)
        label = QtGui.QLabel("<b>{}</b>".format(display_name), self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        action.setDefaultWidget(label)
        menu.addAction(action)
        menu.addSeparator()

        if len(selection) > 1:
            suffix = "s"
        else:
            suffix = ""

        if not all([options.cfg.column_visibility.get(x, True) for x in selection]):
            action = QtGui.QAction("&Show column{}".format(suffix), self)
            action.triggered.connect(lambda: self.show_columns(selection))
            action.setIcon(self.get_icon("sign-maximize"))
            menu.addAction(action)

        if not all([not options.cfg.column_visibility.get(x, True) for x in selection]):
            action = QtGui.QAction("&Hide column{}".format(suffix), self)
            action.triggered.connect(lambda: self.hide_columns(selection))
            action.setIcon(self.get_icon("sign-minimize"))
            menu.addAction(action)

        # Only show additional options if all columns are visible:
        if all([options.cfg.column_visibility.get(x, True) for x in selection]):
        
            if len(selection) == 1:
                action = QtGui.QAction("&Rename column...", self)
                action.triggered.connect(lambda: self.rename_column(column))
                menu.addAction(action)

            if set(selection).intersection(set(options.cfg.column_color.keys())):
                action = QtGui.QAction("&Reset color{}".format(suffix), self)
                action.triggered.connect(lambda: self.reset_colors(selection))
                menu.addAction(action)

            action = QtGui.QAction("&Change color{}...".format(suffix), self)
            action.triggered.connect(lambda: self.change_colors(selection))
            menu.addAction(action)
            
            menu.addSeparator()
            if len(selection) == 1:
                column = selection[0]
                group = QtGui.QActionGroup(self, exclusive=True)
                action = group.addAction(QtGui.QAction("Do not sort", self, checkable=True))
                action.triggered.connect(lambda: self.change_sorting_order(column, SORT_NONE))
                if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_NONE:
                    action.setChecked(True)
                menu.addAction(action)
                
                action = group.addAction(QtGui.QAction("&Ascending", self, checkable=True))
                action.triggered.connect(lambda: self.change_sorting_order(column, SORT_INC))
                if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_INC:
                    action.setChecked(True)
                menu.addAction(action)
                action = group.addAction(QtGui.QAction("&Descending", self, checkable=True))
                action.triggered.connect(lambda: self.change_sorting_order(column, SORT_DEC))
                if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_DEC:
                    action.setChecked(True)
                menu.addAction(action)
                                        
                if self.table_model.content[[column]].dtypes[0] == "object":
                    action = group.addAction(QtGui.QAction("&Ascending, reverse", self, checkable=True))
                    action.triggered.connect(lambda: self.change_sorting_order(column, SORT_REV_INC))
                    if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_REV_INC:
                        action.setChecked(True)

                    menu.addAction(action)
                    action = group.addAction(QtGui.QAction("&Descending, reverse", self, checkable=True))
                    action.triggered.connect(lambda: self.change_sorting_order(column, SORT_REV_DEC))
                    if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_REV_DEC:
                        action.setChecked(True)
                    menu.addAction(action)
        return menu

    def get_row_submenu(self, selection=[], point=None):
        """
        Create a submenu for one or more rows.
        
        Column submenus contain obtions for hiding, showing, and colorizing
        result rows. The set of available options depends on the number of 
        rows selected, and their current visibility.
        
        Row submenus can either be generated as context menus for the row 
        names in the results table, or from the Output main menu entry. 
        In the former case, the parameter 'point' indicates the screen 
        position of the context menu. In the latter case, point is None.
        
        Parameters
        ----------
        selection : list
            A list of row indices
        point : QPoint
            The screen position for which the context menu is requested
        """
        
        menu = QtGui.QMenu("Row options", self)

        if not selection:
            if point:
                header = self.ui.data_preview.verticalHeader()
                row = header.logicalIndexAt(point.y())
                selection = [self.table_model.content.index[row]]

        length = len(selection)
        if length > 1:
            display_name = "{} rows selected".format(len(selection))
        elif length == 1:
            display_name = "Row menu"
        else:
            display_name = "(no row selected)"
        action = QtGui.QWidgetAction(self)
        label = QtGui.QLabel("<b>{}</b>".format(display_name), self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        action.setDefaultWidget(label)
        menu.addAction(action)
        
        if length:
            menu.addSeparator()
            # Check if any row is hidden
            if any([not options.cfg.row_visibility[self.Session.query_type].get(x, True) for x in selection]):
                if length > 1:
                    if all([not options.cfg.row_visibility[self.Session.query_type].get(x, True) for x in selection]):
                        action = QtGui.QAction("&Show rows", self)
                    else:
                        action = QtGui.QAction("&Show hidden rows", self)
                else:
                    action = QtGui.QAction("&Show row", self)
                action.triggered.connect(lambda: self.set_row_visibility(selection, True))
                action.setIcon(self.get_icon("sign-maximize"))
                menu.addAction(action)
            # Check if any row is visible
            if any([options.cfg.row_visibility[self.Session.query_type].get(x, True) for x in selection]):
                if length > 1:
                    if all([options.cfg.row_visibility[self.Session.query_type].get(x, True) for x in selection]):
                        action = QtGui.QAction("&Hide rows", self)
                    else:
                        action = QtGui.QAction("&Hide visible rows", self)
                else:
                    action = QtGui.QAction("&Hide row", self)
                action.triggered.connect(lambda: self.set_row_visibility(selection, False))
                action.setIcon(self.get_icon("sign-minimize"))
                menu.addAction(action)
            menu.addSeparator()
            
            # Check if any row has a custom color:
            if any([x in options.cfg.row_color for x in selection]):
                action = QtGui.QAction("&Reset color", self)
                action.triggered.connect(lambda: self.reset_row_color(selection))
                menu.addAction(action)

            action = QtGui.QAction("&Change color...", self)
            action.triggered.connect(lambda: self.change_row_color(selection))
            menu.addAction(action)
        return menu

    def show_header_menu(self, point=None):
        """
        Show a context menu for the current column selection. If no column is
        selected, show a context menu for the column that has been clicked on.
        """
        selection = []
        for x in self.ui.data_preview.selectionModel().selectedColumns():
            selection.append(self.table_model.header[x.column()])
        
        header = self.ui.data_preview.horizontalHeader()
        self.menu = self.get_column_submenu(selection=selection, point=point)
        self.menu.popup(header.mapToGlobal(point))

    def show_row_header_menu(self, point=None):
        """
        Show a context menu for the current row selection. If no row is
        selected, show a context menu for the row that has been clicked on.
        """
        selection = []
        for x in self.ui.data_preview.selectionModel().selectedRows():
            selection.append(self.table_model.content.index[x.row()])
        
        header = self.ui.data_preview.verticalHeader()
        self.menu = self.get_row_submenu(selection=selection, point=point)
        self.menu.popup(header.mapToGlobal(point))

    def rename_column(self, column):
        """
        Open a dialog in which the column name can be changed.
        
        Parameters
        ----------
        column : column index
        """
        from .renamecolumn import RenameColumnDialog
        
        column_name = self.Session.translate_header(column, ignore_alias=True)
        current_name = options.cfg.column_names.get(column, column_name)
        
        name = RenameColumnDialog.get_name(column_name,
                                           current_name)
        options.cfg.column_names[column] = name

    def hide_columns(self, selection):
        """
        Show the columns in the selection.

        Parameters
        ----------
        selection : list
            A list of column names.
        """
        for column in selection:
            options.cfg.column_visibility[column] = False
        self.update_columns()

    def show_columns(self, selection):
        """
        Show the columns in the selection.

        Parameters
        ----------
        selection : list
            A list of column names.
        """
        for column in selection:
            options.cfg.column_visibility[column] = True
        self.update_columns()

    def update_columns(self):
        """
        Update the table by emitting the adequate signals.
        
        This method emits geometriesChanged, layoutChanged and 
        columnVisibilityChanged signals, and also resorts the table if 
        necessary.
        """
        # Resort the data if this is a sorting column:
        self.table_model.sort(0, QtCore.Qt.AscendingOrder)
        self.table_model.layoutChanged.emit()
        self.table_model.columnVisibilityChanged.emit()
        self.ui.data_preview.horizontalHeader().geometriesChanged.emit()

    def update_row_visibility(self):
        """
        Update the aggregations if row visibility has changed.
        """
        self.Session.drop_cached_aggregates()
        self.reaggregate()

    def toggle_visibility(self, column):
        """ 
        Show again a hidden column, or hide a visible column.
        
        Parameters
        ----------
        column : column index
        """
        options.cfg.column_visibility[column] = not options.cfg.column_visibility.get(column, True)
        self.update_columns()

    def set_row_visibility(self, selection, state):
        """ 
        Set the visibility of the selected rows.
        
        Parameters
        ----------
        selection : list
            A list of row indices
        
        state : bool
            True if the rows should be visible, or False to hide the rows
        """
        if state:
            for x in selection:
                try:
                    options.cfg.row_visibility[self.Session.query_type].pop(np.int64(x))
                except KeyError:
                    pass
        else:
            for x in selection:
                options.cfg.row_visibility[self.Session.query_type][np.int64(x)] = False 
        self.ui.data_preview.verticalHeader().geometriesChanged.emit()
        self.table_model.rowVisibilityChanged.emit()
        self.table_model.layoutChanged.emit()

    def reset_colors(self, selection):
        """
        Reset the colors of the columns in the selection.

        Parameters
        ----------
        selection : list
            A list of column names.
        """
        for column in selection:
            try:
                options.cfg.column_color.pop(column)
                self.table_model.layoutChanged.emit()
            except KeyError:
                pass

    def change_colors(self, selection):
        """
        Change the colors of the columns in the selection to one
        selected from a dialog.

        Parameters
        ----------
        selection : list
            A list of column names.
        """
        col = QtGui.QColorDialog.getColor()
        if col.isValid():
            for column in selection:
                options.cfg.column_color[column] = col.name()
        
    def reset_row_color(self, selection):
        for x in selection:
            try:
                options.cfg.row_color.pop(np.int64(x))
            except KeyError:
                pass
        #self.table_model.layoutChanged.emit()

    def change_row_color(self, selection):
        col = QtGui.QColorDialog.getColor()
        if col.isValid():
            for x in selection:
                options.cfg.row_color[np.int64(x)] = col.name()
        
    def change_sorting_order(self, column, mode):
        if mode == SORT_NONE:
            self.table_model.sort_columns.pop(column)
        else:
            self.table_model.sort_columns[column] = mode
        self.table_model.sort(0, QtCore.Qt.AscendingOrder)
        # make sure that the table is updated if there are no sort columns
        # left anymore:
        if not self.table_model.sort_columns:
            self.table_model.layoutChanged.emit()

    def set_query_button(self):
        """ Set the action button to start queries. """
        self.ui.button_run_query.clicked.disconnect()
        self.ui.button_run_query.clicked.connect(self.run_query)
        self.ui.button_run_query.setText(gui_label_query_button)
        self.ui.button_run_query.setIcon(self.get_icon("go"))
        
    def set_stop_button(self):
        """ Set the action button to stop queries. """
        self.ui.button_run_query.clicked.disconnect()
        self.ui.button_run_query.clicked.connect(self.stop_query)
        self.ui.button_run_query.setText(gui_label_stop_button)
        self.ui.button_run_query.setIcon(self.get_icon("stop"))
    
    def stop_query(self):
        response = QtGui.QMessageBox.warning(self, "Unfinished query", msg_query_running, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if response == QtGui.QMessageBox.Yes:
            # FIXME: This isn't working well at all. A possible solution
            # using SQLAlchemy may be found here:
            # http://stackoverflow.com/questions/9437498
            
            logger.warning("Last query is incomplete.")
            self.ui.button_run_query.setEnabled(False)
            self.ui.button_run_query.setText("Wait...")
            self.showMessage("Terminating query...")
            try:
                self.Session.Corpus.resource.DB.kill_connection()
            except Exception as e:
                pass
            if self.query_thread:
                self.query_thread.terminate()
                self.query_thread.wait()
            self.showMessage("Last query interrupted.")
            self.ui.button_run_query.setEnabled(True)
            self.set_query_button()
            self.stop_progress_indicator()
        
    def run_query(self):
        self.getGuiValues()
        self.showMessage("Preparing query...")
        try:
            if self.ui.radio_query_string.isChecked():
                options.cfg.query_list = options.cfg.query_list[0].splitlines()
                self.new_session = SessionCommandLine()
            else:
                if not self.verify_file_name():
                    QtGui.QMessageBox.critical(self, "Invalid file name – Coquery", msg_filename_error, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return
                self.new_session = SessionInputFile()
        except TokenParseError as e:
            QtGui.QMessageBox.critical(self, "Query string parsing error – Coquery", e.par, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except SQLNoConfigurationError:
            QtGui.QMessageBox.critical(self, "Database configuration error – Coquery", msg_sql_no_configuration, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except SQLInitializationError as e:
            QtGui.QMessageBox.critical(self, "Database initialization error – Coquery", msg_initialization_error.format(code=e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except CollocationNoContextError as e:
            QtGui.QMessageBox.critical(self, "Collocation error – Coquery", str(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except RuntimeError as e:
            QtGui.QMessageBox.critical(self, "Runtime error – Coquery", str(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except Exception as e:
            errorbox.ErrorBox.show(sys.exc_info(), e)
        else:
            self.set_stop_button()
            self.showMessage("Running query...")
            self.start_progress_indicator()
            self.query_thread = classes.CoqThread(self.new_session.run_queries, parent=self)
            self.query_thread.taskFinished.connect(self.finalize_query)
            self.query_thread.taskException.connect(self.exception_during_query)
            self.query_thread.start()

    def run_statistics(self):
        if not self.last_results_saved:
            response = QtGui.QMessageBox.warning(
            self, "Discard unsaved data", msg_warning_statistics, QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if response == QtGui.QMessageBox.No:
                return
        
        self.getGuiValues()
        self.new_session = StatisticsSession()
        self.showMessage("Gathering corpus statistics...")
        self.start_progress_indicator()
        self.query_thread = classes.CoqThread(self.new_session.run_queries, parent=self)
        self.query_thread.taskFinished.connect(self.finalize_query)
        self.query_thread.taskException.connect(self.exception_during_query)
        self.query_thread.start()

    def visualize_data(self, name, **kwargs):
        """
        Visualize the current results table using the specified visualization 
        module.
        """
        
        # check if seaborn can be loaded:
        try:
            import seaborn
        except ImportError:
            errorbox.alert_missing_module("Seaborn", self)
            return
        
        from . import visualization
        
        # try to import the specified visualization module:
        name = "visualizer.{}".format(name)
        try:
            module = importlib.import_module(name)
        except Exception as e:
            msg = "<code style='color: darkred'>{type}: {code}</code>".format(
                type=type(e).__name__, code=sys.exc_info()[1])
            logger.error(msg)
            QtGui.QMessageBox.critical(
                self, "Visualization error – Coquery",
                VisualizationModuleError(name, msg).error_message)
            return 
        
        # try to do the visualization:
        try:
            dialog = visualization.VisualizerDialog()
            dialog.Plot(
                self.table_model,
                self.ui.data_preview,
                module.Visualizer,
                parent=self,
                **kwargs)

        except (VisualizationNoDataError, VisualizationInvalidLayout, VisualizationInvalidDataError) as e:
            QtGui.QMessageBox.critical(
                self, "Visualization error – Coquery",
                str(e))
        except Exception as e:
            errorbox.ErrorBox.show(sys.exc_info())
        
    def save_configuration(self):
        self.getGuiValues()
        options.save_configuration()

    def open_corpus_help(self):
        if self.ui.combo_corpus.isEnabled():
            current_corpus = utf8(self.ui.combo_corpus.currentText())
            resource, _, _, module = options.cfg.current_resources[current_corpus]
            try:
                url = resource.url
            except AttributeError:
                QtGui.QMessageBox.critical(None, "Documentation error – Coquery", msg_corpus_no_documentation.format(corpus=current_corpus), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            else:
                import webbrowser
                webbrowser.open(url)
        
    def remove_corpus(self, entry):
        """
        Remove the database and corpus module for 'corpus_name'. If the 
        corpus was created from a text directory, also remove the installer.
        
        Parameters
        ----------
        entry : CoqAccordionEntry
            The entry from the corpus manager that has been selected for 
            removal
        """
        from . import removecorpus

        try:
            resource, _, _, module = options.cfg.current_resources[entry.name]
        except KeyError:
            if entry.adhoc:
                database = "coq_{}".format(entry.name.lower())
            else:
                database = ""
            module = ""
        else:
            database = resource.db_name

        response = removecorpus.RemoveCorpusDialog.select(
            entry, options.cfg.current_server)
        if response and QtGui.QMessageBox.question(
            self,
            "Remove corpus – Coquery",
            "Do you really want to remove the selected corpus components?",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:
            rm_module, rm_database, rm_installer = response
            success = True

            if rm_database and database and sqlhelper.has_database(options.cfg.current_server, database):
                try:
                    sqlhelper.drop_database(options.cfg.current_server, database)
                except Exception as e:
                    raise e
                    QtGui.QMessageBox.critical(
                        self, 
                        "Database error – Coquery", 
                        msg_remove_corpus_error.format(corpus=resource.name, code=e), 
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    success = False

            # Remove the corpus module:
            if rm_module and success and module:
                try:
                    if os.path.exists(module):
                        os.remove(module)
                except IOError:
                    QtGui.QMessageBox.critical(self, "Storage error – Coquery", msg_remove_corpus_disk_error, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    success = False
                else:
                    success = True
                    # also try to remove the compiled python module:
                    try:
                        os.remove("{}c".format(module))
                    except (IOError, OSError):
                        pass
            
            # remove the corpus installer if the corpus was created from 
            # text files:
            if rm_installer and success:
                try:
                    res, _, _, _ = options.cfg.current_resources[entry.name]
                    path = os.path.join(options.cfg.adhoc_path, "coq_install_{}.py".format(res.db_name))
                    os.remove(path)
                except Exception as e:
                    print(e)
                else:
                    success = True

            options.set_current_server(options.cfg.current_server)
            self.fill_combo_corpus()
            if success and (rm_installer or rm_database or rm_module):
                logger.warning("Removed corpus {}.".format(entry.name))
                self.showMessage("Removed corpus {}.".format(entry.name))
                self.corpusListUpdated.emit()
                
            self.change_corpus()

    def build_corpus(self):
        from coquery. installer import coq_install_generic
        from .corpusbuilder_interface import BuilderGui

        builder = BuilderGui(coq_install_generic.BuilderClass, self)
        try:
            result = builder.display()
        except Exception as e:
            errorbox.ErrorBox.show(sys.exc_info())
        if result:
            options.set_current_server(options.cfg.current_server)
        self.fill_combo_corpus()
        self.change_corpus()
        self.corpusListUpdated.emit()
            
    def install_corpus(self, builder_class):
        from .corpusbuilder_interface import InstallerGui

        builder = InstallerGui(builder_class, self)
        try:
            result = builder.display()
        except Exception as e:
            errorbox.ErrorBox.show(sys.exc_info())
        if result:
            options.set_current_server(options.cfg.current_server)
        self.fill_combo_corpus()
        self.change_corpus()
        self.corpusListUpdated.emit()
            
    def manage_corpus(self):
        from . import corpusmanager
        if self.corpus_manager:
            self.corpus_manager.raise_()
            self.corpus_manager.activateWindow()
        else:
            try:
                self.corpus_manager = corpusmanager.CorpusManager(parent=self)        
            except Exception as e:
                raise e
            self.corpus_manager.show()
            self.corpus_manager.installCorpus.connect(self.install_corpus)
            self.corpus_manager.removeCorpus.connect(self.remove_corpus)
            self.corpus_manager.buildCorpus.connect(self.build_corpus)
            self.corpusListUpdated.connect(self.corpus_manager.update)
            
            try:
                result = self.corpus_manager.exec_()
            except Exception as e:
                logger.error(e)
                raise e
            self.corpusListUpdated.disconnect(self.corpus_manager.update)
            
            try:
                self.corpus_manager.close()
            except AttributeError:
                pass

            self.corpus_manager = None
            self.fill_combo_corpus()
            
    def closeEvent(self, event):
        def shutdown():
            options.settings.setValue("main_geometry", self.saveGeometry())
            options.settings.setValue("main_state", self.saveState())
            options.settings.setValue("figure_font", options.cfg.figure_font)
            options.settings.setValue("table_font", options.cfg.table_font)
            options.settings.setValue("context_font", options.cfg.context_font)
            while self.widget_list:
                x = self.widget_list.pop(0)
                x.close()
                del x
            self.save_configuration()
            event.accept()

        if not self.last_results_saved and options.cfg.ask_on_quit:
            response = QtGui.QMessageBox.warning(self, "Unsaved results", msg_unsaved_data, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if response == QtGui.QMessageBox.Yes:
                shutdown()
            else:
                event.ignore()            
        else:
            shutdown()
        
    def settings(self):
        from . import settings
        settings.Settings.manage(options.cfg, self)
        self.ui.data_preview.setFont(options.cfg.table_font)

    def change_current_server(self):
        name = self.ui.combo_config.currentText()
        if name:
            name = utf8(name)
            self.change_mysql_configuration(name)

    def switch_configuration(self, x):
        name = utf8(self.ui.combo_config.itemText(int(x)))
        self.change_mysql_configuration()

    def change_mysql_configuration(self, name=None):
        """
        Change the current connection to the configuration 'name'. If 'name' 
        is empty, take the configuration name from the connection combo box.
        """
        
        if not name:
            name = utf8(self.ui.combo_config.currentText())
            
        try:
            self.ui.combo_config.currentIndexChanged.disconnect()
        except (RuntimeError, TypeError):
            pass
        
        self.ui.combo_config.clear()
        self.ui.combo_config.addItems(sorted(options.cfg.server_configuration))
        if name:
            options.set_current_server(str(name))
            index = self.ui.combo_config.findText(name)
            self.ui.combo_config.setCurrentIndex(index)
            self.test_mysql_connection()

        self.ui.combo_config.currentIndexChanged.connect(self.switch_configuration)

        self.fill_combo_corpus()
        self.change_corpus()

    def test_mysql_connection(self):
        """
        Tests whether a connection to the MySQL host is available, also update 
        the GUI to reflect the status.
        
        This method tests the currently selected MySQL configuration. If a 
        connection can be established using this configuration, the current 
        combo box entry is marked by a tick icon. 
        
        If no connection can be established, the current combo box entry is 
        marked by a warning icon.

        Returns
        -------
        state : bool
            True if a connection is available, or False otherwise.
        """
        if not options.cfg.current_server:
            return False
        else:
            try:
                state, _ = sqlhelper.test_configuration(options.cfg.current_server)
            except ImportError:
                state = False
        # Only do something if the current connection status has changed:
        if state != self.last_connection_state or options.cfg.current_server != self.last_connection:
            # Remember the item that has focus:
            active_widget = options.cfg.app.focusWidget()
            
            # Choose a suitable icon for the connection combo box:
            if state:
                icon = self.get_icon("sign-check")
            else:
                icon = self.get_icon("sign-error")

                
            # Disconnect the currentIndexChanged signal to avoid infinite
            # recursive loop:
            try:
                self.ui.combo_config.currentIndexChanged.disconnect()
            except (TypeError, RuntimeError):
                pass
            # add new entry with suitable icon, remove old icon and reset index:
            index = self.ui.combo_config.findText(options.cfg.current_server)
            self.ui.combo_config.insertItem(index + 1, icon, options.cfg.current_server)
            self.ui.combo_config.setCurrentIndex(index + 1)
            self.ui.combo_config.removeItem(index)
            self.ui.combo_config.setCurrentIndex(index)
            self.last_connection_state = state
            self.last_connection = options.cfg.current_server
            self.last_index = index
            # reconnect currentIndexChanged signal:
            self.ui.combo_config.currentIndexChanged.connect(self.switch_configuration)

            self.ui.options_area.setDisabled(True)
            if state:
                self.fill_combo_corpus()
                if self.ui.combo_corpus.count():
                    self.ui.options_area.setDisabled(False)

            if active_widget:
                active_widget.setFocus()

        return state

    def connection_settings(self):
        from . import connectionconfiguration
        try:
            config_dict, name = connectionconfiguration.ConnectionConfiguration.choose(options.cfg.current_server, options.cfg.server_configuration)
        except TypeError:
            return
        else:
            options.cfg.server_configuration = config_dict
            self.change_mysql_configuration(name)

    def show_mysql_guide(self):
        from . import mysql_guide
        mysql_guide.MySqlGuide.display()

    def getGuiValues(self):
        """ Set the values in options.cfg.* depending on the current values
        in the GUI. """
        
        if options.cfg:
            options.cfg.corpus = utf8(self.ui.combo_corpus.currentText())
        
            # determine query mode:
            if self.ui.radio_aggregate_uniques.isChecked():
                options.cfg.MODE = QUERY_MODE_DISTINCT
            if self.ui.radio_aggregate_none.isChecked():
                options.cfg.MODE = QUERY_MODE_TOKENS
            if self.ui.radio_aggregate_frequencies.isChecked():
                options.cfg.MODE = QUERY_MODE_FREQUENCIES
            if self.ui.radio_aggregate_contingency.isChecked():
                options.cfg.MODE = QUERY_MODE_CONTINGENCY                
            if self.ui.radio_aggregate_collocations.isChecked():
                options.cfg.MODE = QUERY_MODE_COLLOCATIONS
            try:
                if self.ui.radio_mode_statistics.isChecked():
                    options.cfg.MODE = QUERY_MODE_STATISTICS
            except AttributeError:
                pass
                
            # determine context mode:
            if self.ui.radio_context_none.isChecked():
                options.cfg.context_mode = CONTEXT_NONE
            if self.ui.radio_context_mode_kwic.isChecked():
                options.cfg.context_mode = CONTEXT_KWIC
            if self.ui.radio_context_mode_string.isChecked():
                options.cfg.context_mode  = CONTEXT_STRING
            if self.ui.radio_context_mode_columns.isChecked():
                options.cfg.context_mode  = CONTEXT_COLUMNS

            # either get the query input string or the query file name:
            if self.ui.radio_query_string.isChecked():
                if type(self.ui.edit_query_string) == QtGui.QLineEdit:
                    options.cfg.query_list = [utf8(self.ui.edit_query_string.text())]
                else:
                    options.cfg.query_list = [utf8(self.ui.edit_query_string.toPlainText())]
            options.cfg.input_path = utf8(self.ui.edit_file_name.text())

            # get context options:
            options.cfg.context_left = self.ui.context_left_span.value()
            options.cfg.context_right = self.ui.context_right_span.value()
            options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            
            options.cfg.external_links = self.get_external_links()
            options.cfg.selected_features = self.get_selected_features()
            options.cfg.selected_functions = self.get_functions()

            return True

    def get_selected_features(self):
        """
        Traverse through the output columns tree and obtain all features that 
        are checked.

        Returns
        -------
        l : list 
            A list of resource features that were checked in the tree widget.
        """
        def traverse(node):
            checked = []
            for child in [node.child(i) for i in range(node.childCount())]:
                checked += traverse(child)
            if node.checkState(0) == QtCore.Qt.Checked and not node.isDisabled() and not node.objectName().endswith("_table"):
                checked.append(node.objectName())
            return checked

        tree = self.ui.options_tree
        l = []
        for root in [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]:
            l += traverse(root)
        return l
        
    def get_external_links(self):
        """
        Traverse through the output columns tree and obtain all external links 
        that are checked.
        
        Returns
        -------
        l : list 
            A list of tuples. The first element of each tuple is a Link object 
            (defined in linkselect.py), and the second element is a string 
            specifying the resource feature that establishes the link.
        """
        def traverse(node):
            checked = []
            for child in [node.child(i) for i in range(node.childCount())]:
                checked += traverse(child)
            if node.checkState(0) == QtCore.Qt.Checked:
                try:
                    parent = node.parent()
                except AttributeError:
                    print("Warning: Node has no parent")
                    logger.warn("Warning: Node has no parent")
                    return checked
                if parent and parent.isLinked():
                    checked.append((parent.link, node.rc_feature))
            return checked

        tree = self.ui.options_tree
        l = []
        for root in [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]:
            l += traverse(root)
        return l

    def get_functions(self):
        """
        Traverse through the output columns tree and obtain all functions that 
        are checked.
        
        Returns
        -------
        l : list 
            A list of tuples. The first element of each tuple is the resource 
            feature, the second element is the function, and the third element
            is the name of the function as it appears in the tree widget. 
        """
        def traverse(node):
            checked = []
            for child in [node.child(i) for i in range(node.childCount())]:
                checked += traverse(child)
            if node.checkState(0) == QtCore.Qt.Checked and node._func:
                checked.append((node.objectName(), node._func, str(node.text(0))))
            return checked

        tree = self.ui.options_tree
        l = []
        for root in [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]:
            l += traverse(root)
        return l

    def show_log(self):
        from . import logfile
        log_view = logfile.LogfileViewer(parent=self)
        log_view.show()
        self.widget_list.append(log_view)

    def show_about(self):
        from . import about
        about = about.AboutDialog(parent=self)
        about.exec_()
        
    def setGUIDefaults(self):
        """ Set up the gui values based on the values in options.cfg.* """

        # set corpus combo box to current corpus:
        index = self.ui.combo_corpus.findText(options.cfg.corpus)
        if index > -1:
            self.ui.combo_corpus.setCurrentIndex(index)

        # set query mode:
        if options.cfg.MODE == QUERY_MODE_DISTINCT:
            self.ui.radio_aggregate_uniques.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            self.ui.radio_aggregate_frequencies.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_TOKENS:
            self.ui.radio_aggregate_none.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_COLLOCATIONS:
            self.ui.radio_aggregate_collocations.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_CONTINGENCY:
            self.ui.radio_aggregate_contingency.setChecked(True)

        self.ui.edit_file_name.setText(options.cfg.input_path)
        # either fill query string or query file input:
        if options.cfg.query_list:
            self.ui.edit_query_string.setText("\n".join(options.cfg.query_list))
            self.ui.radio_query_string.setChecked(True)
        if options.cfg.input_path_provided:
            self.ui.radio_query_file.setChecked(True)
            
        for rc_feature in options.cfg.selected_features:
            self.ui.options_tree.setCheckState(rc_feature, QtCore.Qt.Checked)
        
        self.ui.context_left_span.setValue(options.cfg.context_left)
        self.ui.context_right_span.setValue(options.cfg.context_right)
        
        if options.cfg.context_mode == CONTEXT_KWIC:
            self.ui.radio_context_mode_kwic.setChecked(True)
        elif options.cfg.context_mode == CONTEXT_STRING:
            self.ui.radio_context_mode_string.setChecked(True)
        elif options.cfg.context_mode == CONTEXT_COLUMNS:
            self.ui.radio_context_mode_columns.setChecked(True)
        else:
            self.ui.radio_context_none.setChecked(True)
        self.update_context_widgets()
            
        #for filt in list(options.cfg.filter_list):
            #self.ui.filter_box.addTag(filt)
            #options.cfg.filter_list.remove(filt)
        
        if options.cfg.use_stopwords:
            self.ui.stopword_switch.setOn()
        if options.cfg.use_corpus_filters:
            self.ui.filter_switch.setOn()
        
        # get table from last session, if possible:
        try:
            self.table_model.set_header(options.cfg.last_header)
            self.table_model.set_data(options.cfg.last_content)
            self.Session = options.cfg.last_session
            self.ui.data_preview.setModel(self.table_model)
        except AttributeError:
            pass
        
        self.toggle_frequency_columns()

    #def select_table(self):
        #"""
        #Open a table select widget.
        
        #The table select widget contains a QTreeWidget with all corpora 
        #except the currently active one as parents, and the respective tables
        #as children.
        
        #The return tuple contains the corpus and the table name. 
        
        #Returns
        #-------
        #(corpus, table) : tuple
            #The name of the corpus and the name of the table from that corpus
            #as feature strings. 
        #"""
        
        
        #corpus, table, feature = linkselect.LinkSelect.display(self)
        
        #corpus = "bnc"
        #table = "word"
        #feature_name = "word_label"
        
        #return (corpus, table, feature_name)

    def update_context_widgets(self):
        if self.ui.radio_context_none.isChecked():
            self.ui.context_left_span.setDisabled(True)
            self.ui.context_right_span.setDisabled(True)
        else:
            self.ui.context_left_span.setDisabled(False)
            self.ui.context_right_span.setDisabled(False)

    def add_link(self, item):
        """
        Link the selected output column to a column from an external table.
        
        The method opens a dialog from which a column in an external table 
        can be selected. Then, a link is added from the argument to that 
        column so that rows from the external table that have the same value
        in the linked table as in the output column from the present corpus
        can be included in the output.
        
        Parameters
        ----------
        item : CoqTreeItem
            An entry in the output column list
        """
        from . import linkselect
        column = 0
        link = linkselect.LinkSelect.display(
            feature=str(item.text(0)),
            corpus=str(self.ui.combo_corpus.currentText()),
            corpus_omit=str(self.ui.combo_corpus.currentText()), 
            parent=self)
        
        if not link:
            return
        else:
            link.key_feature = str(item.objectName())
            item.setExpanded(True)
            
            tree = classes.CoqTreeLinkItem()
            tree.setLink(link)
            tree.setText(column, "{}.{}.{}".format(link.resource, link.table_name, link.feature_name))
            tree.setCheckState(column, QtCore.Qt.Unchecked)
            tree.setObjectName("{}.{}_table".format(link.db_name, link.table))
            
            resource = options.cfg.current_resources[link.resource][0]
            table = resource.get_table_dict()[link.table]

            # fill new tree with the features from the linked table (exclude
            # the linking feature):
            for rc_feature in [x for x in table if x != link.rc_feature]:
                _, _, _, feature = resource.split_resource_feature(rc_feature)
                # exclude special resource features
                if feature not in ("id", "table"):
                    new_item = classes.CoqTreeItem()
                    new_item.setText(0, getattr(resource, rc_feature))
                    new_item.rc_feature = rc_feature
                    new_item.setObjectName("{}.{}".format(link.db_name, rc_feature))
                    new_item.setCheckState(column, QtCore.Qt.Unchecked)
                    tree.addChild(new_item)

            # Insert newly created table as a child of the linked item:
            item.addChild(tree)
            
    def add_function(self, item):
        """
        Add an output column that applies a function to the selected item.
        
        This method opens a dialog that allows to choose a function that 
        may be applied to the selected item. This function is added as an
        additional output column to the list of output columns.
        
        Parameters
        ----------
        item : CoqTreeItem
            An entry in the output column list
        """

        from . import functionapply
        column = 0
        parent = item.parent()
        
        response = functionapply.FunctionDialog.display(
            table=str(parent.text(0)),
            feature=str(item.text(0)), parent=self)
        
        if not response:
            return
        else:
            label, func = response
            
            child_func = classes.CoqTreeFuncItem()
            child_func.setObjectName("func.{}".format(item.objectName()))
            child_func.setFunction(func)
            child_func.rc_feature = item.objectName()
            child_func.setText(column, label)
            child_func.setCheckState(column, QtCore.Qt.Checked)

            item.parent().addChild(child_func)
            item.parent().setExpanded(True)

    def remove_item(self, item):
        """
        Remove either a link or a function from the list of output columns.        
        
        Parameters
        ----------
        item : CoqTreeItem
            An entry in the output column list
        """
        def remove_children(node):
            for child in [node.child(i) for i in range(node.childCount())]:
                remove_children(child)
                node.removeChild(child)
            node.close()

        # remove linked table, but only if the item is not a function:
        if item.parent and item.parent()._link_by and not item._func:
            item = item.parent()
            self.ui.options_tree.takeTopLevelItem(self.ui.options_tree.indexOfTopLevelItem(item))
        else:
            item.parent().removeChild(item)


#try:
    #_encoding = QtGui.QApplication.UnicodeUTF8
    #def _translate(context, text, disambig):
        #return QtGui.QApplication.translate(context, text, disambig, _encoding)
#except AttributeError:
    #def _translate(context, text, disambig):
        #return QtGui.QApplication.translate(context, text, disambig)

def _translate(x, text, y):
    return utf8(text)
    
def memory_dump():
    import gc
    x = 0
    for obj in gc.get_objects():
        i = id(obj)
        size = sys.getsizeof(obj, 0)
        # referrers = [id(o) for o in gc.get_referrers(obj)]
        try:
            cls = str(obj.__class__)
        except:
            cls = "<no class>"
        if size > 1024 * 50:
            referents = set([id(o) for o in gc.get_referents(obj)])
            x += 1
            print(x, {'id': i, 'class': cls, 'size': size, "ref": len(referents)})
            #if len(referents) < 2000:
                #print(obj)

logger = logging.getLogger(NAME)

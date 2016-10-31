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
import numpy as np
import pandas as pd
from collections import defaultdict

from coquery import queries
from coquery import managers
from coquery import functions
from coquery import sqlhelper
from coquery.general import memory_dump
from coquery.session import *
from coquery.defines import *
from coquery.unicode import utf8
from coquery.links import get_by_hash

from . import classes
from . import errorbox
from . import contextviewer
from .pyqt_compat import QtCore, QtGui, QtHelp
from .ui import coqueryUi, coqueryTinyUi
from .resourcetree import CoqResourceTree
from .menus import CoqResourceMenu, CoqColumnMenu

## add path required for visualizers::
if not os.path.join(options.cfg.base_path, "visualizer") in sys.path:
    sys.path.append(os.path.join(options.cfg.base_path, "visualizer"))

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
    columnVisibilityChanged = QtCore.Signal()
    rowVisibilityChanged = QtCore.Signal()
    updateMultiProgress = QtCore.Signal(int)
    abortRequested = QtCore.Signal()

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
        self._group_functions = functions.FunctionList()
        self._column_functions = functions.FunctionList()
        
        self.widget_list = []
        self.Session = None
        
        self.selected_features = set()
        
        self._first_corpus = False
        if options.cfg.first_run and not options.cfg.current_resources:
            self._first_corpus = True
        
        size = QtGui.QApplication.desktop().screenGeometry()
        # Retrieve font and metrics for the CoqItemDelegates
        options.cfg.font = options.cfg.app.font()
        options.cfg.metrics = QtGui.QFontMetrics(options.cfg.font)
        options.cfg.figure_font = options.settings.value("figure_font", QtGui.QLabel().font())
        options.cfg.table_font = options.settings.value("table_font", QtGui.QLabel().font())
        options.cfg.context_font = options.settings.value("context_font", QtGui.QLabel().font())

        if size.width() < 800 or size.height() < 600:
            self.ui = coqueryTinyUi.Ui_MainWindow()
        else:
            self.ui = coqueryUi.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setMenuBar(self.ui.menubar)
        
        self.setup_app()
        
        options.cfg.main_window = self

        try:
            self.restoreState(options.settings.value("main_state"))
        except TypeError:
            pass
        x = options.settings.value("splitter")
        try:
            y = x.toByteArray()
        except (TypeError, AttributeError):
            y = x
        finally:
            if y != None:
                self.ui.splitter.restoreState(y)
        # Taskbar icons in Windows require a workaround as described here:
        # https://stackoverflow.com/questions/1551605#1552105
        if sys.platform == "win32":
            import ctypes
            CoqId = 'Coquery.Coquery.{}'.format(VERSION)
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(CoqId)        

        try:
            self.restoreGeometry(options.settings.value("main_geometry"))
        except TypeError:
            self.ui.centralwidget.adjustSize()
            self.adjustSize()
        
    def setup_app(self):
        """ Initialize all widgets with suitable data """

        self.column_tree = CoqResourceTree(parent=self)

        self.ui.options_tree = self.column_tree
        self.ui.output_columns.insertWidget(1, self.column_tree)
        self.ui.output_columns.setStretch(0, 0)
        self.ui.output_columns.setStretch(1, 1)
        self.ui.output_columns.setStretch(2, 0)
        try:
            self.ui.label_data_columns.setBuddy(self.column_tree)
        except AttributeError:
            pass

        self.ui.aggregate_radio_list = []
        row_pos = self.ui.grid_transform.rowCount()
        for label in SUMMARY_MODES:
            radio = QtGui.QRadioButton(label)
            radio.toggled.connect(self.set_aggregate)
            ix = SUMMARY_MODES.index(label)
            self.ui.grid_transform.addWidget(radio, row_pos + ix, 1)
            self.ui.aggregate_radio_list.append(radio)

        if options.cfg.current_resources:
            # add available resources to corpus dropdown box:
            corpora = sorted(list(options.cfg.current_resources.keys()))
            self.ui.combo_corpus.addItems(corpora)
        
        index = self.ui.combo_corpus.findText(options.cfg.corpus)
        if index > -1:
            self.ui.combo_corpus.setCurrentIndex(index)
            
        height = QtGui.QLabel().sizeHint().height() + 2
        box_height = self.ui.list_toolbox.rowCount() * height + 7
        self.ui.list_toolbox.verticalHeader().setDefaultSectionSize(height)
        self.ui.list_toolbox.setMaximumHeight(box_height)
        self.ui.list_toolbox.setMinimumHeight(box_height)

        self.change_toolbox(options.cfg.last_toolbox)
        self.ui.list_toolbox.resizeColumnsToContents()
        self.ui.list_toolbox.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.ui.list_toolbox.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Interactive)
        self.ui.list_toolbox.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Interactive)

        # use a file system model for the file name auto-completer::
        self.dirModel = QtGui.QFileSystemModel(parent=self)
        # make sure that the model is updated on changes to the file system:
        self.dirModel.setRootPath(QtCore.QDir.currentPath())
        self.dirModel.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDotAndDotDot)

        ## set auto-completer for the input file edit:
        #self.path_completer = QtGui.QCompleter(parent=self)
        #self.path_completer.setModel(self.dirModel)
        #self.path_completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        #self.ui.edit_file_name.setCompleter(self.path_completer)

        # set up group columns
        self.ui.button_remove_group.setDisabled(True)
        self.ui.button_group_up.setDisabled(True)
        self.ui.button_group_down.setDisabled(True)
        #self.ui.list_group_columns.setDragEnabled(True)
        #self.ui.list_group_columns.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.ui.list_group_columns.viewport().setAcceptDrops(True)
        self.ui.list_group_columns.setDropIndicatorShown(False)

        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Apply).setDisabled(True)
        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Apply).setText("&Manage")
        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Cancel).setDisabled(True)
        self.ui.button_box_reaggregate.update()
        #self.ui.button_box_reaggregate.hide()

        self.setup_hooks()
        self.setup_menu_actions()
        self.setup_icons()

        self.change_corpus()

        self.set_query_button()
        self.set_function_button_labels()
        
        self.ui.data_preview.setEnabled(False)
        self.ui.text_no_match.hide()
        self.ui.menuAnalyse.setEnabled(False)

        ## set vertical splitter: top: no stretch, bottom: full stretch
        self.ui.splitter.setStretchFactor(0, 0)
        self.ui.splitter.setStretchFactor(1, 1)

        self.ui.status_message = QtGui.QLabel("{} {}".format(NAME, VERSION))
        self.ui.status_progress = QtGui.QProgressBar()
        self.ui.status_progress.hide()
        
        self.ui.multi_query_progress = QtGui.QProgressBar()
        self.ui.combo_config = QtGui.QComboBox()
        self.ui.multi_query_progress.setFormat("Running query... (%v of %m)")
        self.ui.multi_query_progress.hide()
        self.updateMultiProgress.connect(self.ui.multi_query_progress.setValue)
        self.updateMultiProgress.connect(lambda n: self.ui.status_progress.setValue(0))

        self.statusBar().layout().setContentsMargins(0, 0, 4, 0)
        self.statusBar().setMinimumHeight(QtGui.QProgressBar().sizeHint().height())
        self.statusBar().setMaximumHeight(QtGui.QProgressBar().sizeHint().height())
        self.statusBar().setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.statusBar().layout().addWidget(self.ui.status_message, 1)
        self.statusBar().layout().addWidget(self.ui.multi_query_progress, 1)
        self.statusBar().layout().addWidget(self.ui.status_progress, 1)
        self.statusBar().layout().addItem(QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))        
        self.statusBar().layout().addWidget(QtGui.QLabel(_translate("MainWindow", "Connection: ", None)))
        self.statusBar().layout().addWidget(self.ui.combo_config)
        self.statusBar().layout().setStretchFactor(self.ui.status_message, 1)
        self.statusBar().layout().setStretchFactor(self.ui.status_progress, 1)
        self.statusBar().layout().setStretchFactor(self.ui.multi_query_progress, 1)

        self.change_mysql_configuration(options.cfg.current_server)
        self.ui.combo_config.currentIndexChanged.connect(self.switch_configuration)
        
        state = self.test_mysql_connection()
        if not state:
            self.disable_corpus_widgets()
        
        self.connection_timer = QtCore.QTimer(self)
        self.connection_timer.timeout.connect(self.test_mysql_connection)
        self.connection_timer.start(10000)
        
        # the dictionaries column_width and column_color store default
        # attributes of the columns by display name. This means that problems
        # may arise if several columns have the same name!
        # FIXME: Make sure that the columns are identified correctly.
        self.column_width = {}
        self.column_color = {}
        
        self._resizing_column = False
        
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
        self.ui.button_change_file.setIcon(self.get_icon("folder"))
        self.ui.button_remove_group.setIcon(self.get_icon("sign-delete"))
        #self.ui.button_add_group.setIcon(self.get_icon("sign-add"))
        self.ui.button_group_up.setIcon(self.get_icon("sign-up"))
        self.ui.button_group_down.setIcon(self.get_icon("sign-down"))

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
        self.ui.action_available_modules.triggered.connect(self.show_available_modules)
        self.ui.action_about_coquery.triggered.connect(self.show_about)
        self.ui.action_help.triggered.connect(self.help)
        self.ui.action_view_log.triggered.connect(self.show_log)
        self.ui.action_mysql_server_help.triggered.connect(self.show_mysql_guide)
        
        self.ui.action_barcode_plot.triggered.connect(lambda: self.visualize_data("barcodeplot"))
        self.ui.action_beeswarm_plot.triggered.connect(lambda: self.visualize_data("beeswarmplot"))

        self.ui.action_tree_map.triggered.connect(lambda: self.visualize_data("treemap"))
        self.ui.action_heat_map.triggered.connect(lambda: self.visualize_data("heatmap"))
        self.ui.action_bubble_chart.triggered.connect(lambda: self.visualize_data("bubbleplot"))
    
        self.ui.menuDensity_plots.setEnabled(True)
        self.ui.action_kde_plot.triggered.connect(lambda: self.visualize_data("densityplot"))
        self.ui.action_ecd_plot.triggered.connect(lambda: self.visualize_data("densityplot", cumulative=True))
            
        self.ui.action_barchart_plot.triggered.connect(lambda: self.visualize_data("barplot"))
        self.ui.action_percentage_bars.triggered.connect(lambda: self.visualize_data("barplot_perc", percentage=True, stacked=True))
        self.ui.action_stacked_bars.triggered.connect(lambda: self.visualize_data("barplot", percentage=False, stacked=True))
        
        self.ui.action_percentage_area_plot.triggered.connect(lambda: self.visualize_data("timeseries", area=True, percentage=True, smooth=True))
        self.ui.action_stacked_area_plot.triggered.connect(lambda: self.visualize_data("timeseries", area=True, percentage=False, smooth=True))
        self.ui.action_line_plot.triggered.connect(lambda: self.visualize_data("timeseries", area=False, percentage=False, smooth=True))
        
        self.ui.action_toggle_management.triggered.connect(self.toggle_data_management)
        self.ui.action_toggle_columns.triggered.connect(self.toggle_output_columns)
        self.ui.action_toggle_management.setChecked(options.cfg.show_data_management)
        self.ui.action_toggle_columns.setChecked(options.cfg.show_output_columns)
        
        self.ui.menu_Results.aboutToShow.connect(self.show_results_menu)
        self.ui.menuCorpus.aboutToShow.connect(self.show_corpus_menu)
        self.ui.menuFile.aboutToShow.connect(self.show_file_menu)
        
    def setup_hooks(self):
        """ 
        Hook up signals so that the GUI can adequately react to user 
        input.
        """
        # hook file options button:
        self.ui.button_change_file.clicked.connect(self.file_options)
        self.ui.edit_file_name.clicked.connect(self.file_options)

        # hook up events so that the radio buttons are set correctly
        # between either query from file or query from string:
        self.focus_to_file = focusFilter()
        self.ui.edit_file_name.installEventFilter(self.focus_to_file)

        self.ui.edit_file_name.clicked.connect(self.switch_to_file)
        self.focus_to_query = focusFilter()
        self.focus_to_query.focus.connect(self.switch_to_query)
        self.ui.edit_query_string.installEventFilter(self.focus_to_query)

        self.ui.combo_corpus.currentIndexChanged.connect(self.change_corpus)
        # hook run query button:
        self.ui.button_run_query.clicked.connect(self.run_query)

        self.ui.list_toolbox.currentCellChanged.connect(lambda x, _1, _2, _3: self.change_toolbox(x))
        self.ui.list_toolbox.cellClicked.connect(lambda row, col: self.toggle_toolbox(row, col))

        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(lambda: self.abortRequested.emit())
        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.apply_management)

        # set up hooks for the group column list:
        self.ui.button_remove_group.clicked.connect(self.remove_group_column)
        self.ui.button_group_up.clicked.connect(lambda: self.move_group_column(direction="up"))
        self.ui.button_group_down.clicked.connect(lambda: self.move_group_column(direction="down"))
        self.ui.list_group_columns.itemActivated.connect(self.activate_group_column_buttons)
        self.ui.list_group_columns.itemDropped.connect(lambda x: self.add_group_column(item=x))
        self.ui.list_group_columns.featureRemoved.connect(self.uncheck_grouped_feature)
        self.ui.button_add_summary_function.clicked.connect(lambda: self.add_function(summary=True))
        self.ui.button_add_group_function.clicked.connect(lambda: self.add_function(group=True))
        
        self.ui.check_context.stateChanged.connect(self.change_context)
        self.ui.check_stopwords.stateChanged.connect(self.change_stopwords)
        
        self.ui.check_group_filters.stateChanged.connect(self.change_grouping)
        
        self.ui.check_aggregate.stateChanged.connect(self.change_aggregate)
        self.ui.check_drop_duplicates.stateChanged.connect(self.change_summarize)
        self.ui.check_summarize_filters.stateChanged.connect(self.change_summarize_filters)

        self.ui.button_stopwords.clicked.connect(self.manage_stopwords)
        self.ui.button_filters.clicked.connect(self.manage_filters)
        self.ui.button_group_filters.clicked.connect(self.manage_group_filters)

        self.ui.radio_context_mode_kwic.toggled.connect(self.change_context)
        self.ui.radio_context_mode_string.toggled.connect(self.change_context)
        self.ui.radio_context_mode_columns.toggled.connect(self.change_context)
        self.ui.context_left_span.valueChanged.connect(self.change_context)
        self.ui.context_right_span.valueChanged.connect(self.change_context)

        self.ui.data_preview.horizontalHeader().sectionFinallyResized.connect(self.result_column_resize)
        self.ui.data_preview.horizontalHeader().customContextMenuRequested.connect(self.show_header_menu)
        self.ui.data_preview.horizontalHeader().sectionMoved.connect(self.column_moved)
        self.ui.data_preview.verticalHeader().customContextMenuRequested.connect(self.show_row_header_menu)
        self.ui.data_preview.clicked.connect(self.result_cell_clicked)

        self.corpusListUpdated.connect(self.check_corpus_widgets)
        self.columnVisibilityChanged.connect(lambda: self.reaggregate(recalculate=True, start=True))

        self.column_tree.itemChanged.connect(self.toggle_selected_feature)

        ## FIXME: reimplement row visibility
        #self.rowVisibilityChanged.connect(self.update_row_visibility)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.abortRequested.emit()

    def help(self):
        from . import helpviewer
        
        self.helpviewer = helpviewer.HelpViewer(parent=self)
        self.helpviewer.show()

    def show_file_menu(self):
        """
        Enables or disables entries in the file menu if needed.
        """
        # leave if the results table is empty:
        if not self.ui.data_preview.isEnabled() or len(self.table_model.content) == 0:
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

        # FIXME:
        # The menu should always display the available options so that users
        # can use it to explore the program (cf. Cooper et al. 2014. About 
        # Face. 4th edition. Wiley: ch. 18 'the main justification of [menus'] 
        # existence is to teach us about what is available')

        # Add Output column entry:
        if self.column_tree.selectedItems():
            self.ui.menuOutputOptions = self.get_output_column_menu(selection=self.column_tree.selectedItems())
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
            selection = []
            if select and select.selectedColumns():
                # Add column submenu
                for x in self.ui.data_preview.selectionModel().selectedColumns():
                    selection.append(self.table_model.header[x.column()])
                
            self.ui.menuColumns = self.get_column_submenu(selection=selection)
            self.ui.menu_Results.insertMenu(self.ui.menuNoColumns, self.ui.menuColumns)
            self.ui.menu_Results.removeAction(self.ui.menuNoColumns)

            selection = []
            # Check if rows are selected
            if select and select.selectedRows():
                # Add rows submenu
                selection = self.table_model.content.index[[x.row() for x in self.ui.data_preview.selectionModel().selectedRows()]]
                
            self.ui.menuRows = self.get_row_submenu(selection=selection)
            self.ui.menu_Results.insertMenu(self.ui.menuNoRows, self.ui.menuRows)
            self.ui.menu_Results.removeAction(self.ui.menuNoRows)

    def set_main_screen_appearance(self):
        if options.cfg.show_data_management:
            self.ui.group_management.show()
        else:
            self.ui.group_management.hide()

        if options.cfg.show_output_columns:
            self.column_tree.show()
        else:
            self.column_tree.hide()
            
    def toggle_data_management(self):
        options.cfg.show_data_management = not options.cfg.show_data_management
        self.ui.action_toggle_management.setChecked(options.cfg.show_data_management)
        self.set_main_screen_appearance()

    def toggle_output_columns(self):
        options.cfg.show_output_columns = not options.cfg.show_output_columns
        self.ui.action_toggle_columns.setChecked(options.cfg.show_output_columns)
        self.set_main_screen_appearance()

    def change_toolbox(self, i):
        self.ui.list_toolbox.selectRow(i)
        self.ui.tool_widget.setCurrentIndex(i)
        options.cfg.last_toolbox = i

    def check_group_items(self):
        for item, group_column in self.ui.list_group_columns.columns:
            if group_column not in options.cfg.selected_features:
                item.setIcon(self.get_icon("sign-warning"))
                item.setToolTip(msg_column_not_in_data)
            else:
                item.setIcon(QtGui.QIcon())
                item.setToolTip("")

    def activate_group_column_buttons(self):
        selected = self.ui.list_group_columns.selectedItems()
        self.ui.button_remove_group.setEnabled(selected != [])
        try:
            pos_first = self.ui.list_group_columns.row(selected[0])
            pos_last = self.ui.list_group_columns.row(selected[-1])
        except IndexError:
            pos_first = 0
            pos_last = len(self.ui.list_group_columns.columns)
        self.ui.button_group_up.setEnabled(pos_first > 0)
        self.ui.button_group_down.setEnabled(pos_last < len(self.ui.list_group_columns.columns)-1)

    def move_group_column(self, direction, rc_feature=None):
        if rc_feature:
            selected = [self.ui.list_group_columns.get_item(rc_feature)]
        else:
            selected = self.ui.list_group_columns.selectedItems()
            
        pos_first = self.ui.list_group_columns.row(selected[0])
        pos_last = self.ui.list_group_columns.row(selected[-1])
        
        if direction == "up":
            start = pos_first - 1
        else:
            start = pos_first + 1
            
        features = [self.ui.list_group_columns.get_feature(x) for x in selected]
        
        for i, rc_feature in enumerate(features):
            self.ui.list_group_columns.remove_resource(rc_feature)
            self.ui.list_group_columns.insert_resource(start + i, rc_feature)

        self.activate_group_column_buttons()
        #self.reaggregate(start=True)
        self.enable_apply_button()

    def enable_apply_button(self):
        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
        active = (hasattr(self, "table_model"))
        self.ui.button_box_reaggregate.setEnabled(active)

    def apply_management(self):
        self.reaggregate(start=True)

    def add_group_column(self, rc_feature=None, item=None):
        old_list = set(options.cfg.group_columns)
        if not item:
            if rc_feature:
                selected = [rc_feature]
            else:
                selected = [x.objectName() for x in self.column_tree.selectedItems()]
            for col in selected:
                self.ui.list_group_columns.add_resource(col)

        if self.column_tree.getCheckState(rc_feature) == QtCore.Qt.Unchecked:
            self.column_tree.setCheckState(rc_feature, QtCore.Qt.PartiallyChecked)
        
        options.cfg.group_columns = self.get_group_columns()
        self.activate_group_column_buttons()
        if old_list != set(options.cfg.group_columns):
            #self.reaggregate(start=True)
            self.enable_apply_button()
        self.set_toolbox_appearance(TOOLBOX_GROUPING)

    def uncheck_grouped_feature(self, rc_feature):
        if self.column_tree.getCheckState(rc_feature) == QtCore.Qt.PartiallyChecked:
            self.column_tree.setCheckState(rc_feature, QtCore.Qt.Unchecked)
    
    def remove_group_column(self, rc_feature=None):
        old_list = set(options.cfg.group_columns)
        if rc_feature:
            selected = [self.ui.list_group_columns.get_item(rc_feature)]
        else:
            selected = self.ui.list_group_columns.selectedItems()
        for item in selected:
            self.ui.list_group_columns.remove_item(item)
        options.cfg.group_columns = self.get_group_columns()

        self.activate_group_column_buttons()
        if old_list != set(options.cfg.group_columns):
            #self.reaggregate(start=True)
            self.enable_apply_button()
        
        self.set_toolbox_appearance(TOOLBOX_GROUPING)

    def change_context(self):
        """
        Enable or disable contexts.
        """
        #options.cfg.use_context = self.ui.check_context.isChecked()
        #self.get_context_values()
        #self.reaggregate(start=True)
        self.enable_apply_button()
        self.set_toolbox_appearance(TOOLBOX_CONTEXT)

    def change_stopwords(self):
        """
        Enable or disable stopword filtering.
        """
        options.cfg.use_stopwords = self.ui.check_stopwords.isChecked()
        #self.reaggregate(start=True)
        self.enable_apply_button()
        self.set_toolbox_appearance(TOOLBOX_STOPWORDS)
    
    def change_grouping(self):
        """
        Enable or disable grouping.
        """
        options.cfg.use_group_filters = self.ui.check_group_filters.isChecked()
        #self.reaggregate(start=True)
        self.enable_apply_button()
        self.set_toolbox_appearance(TOOLBOX_GROUPING)

    def change_aggregate(self):
        options.cfg.use_aggregate = self.ui.check_aggregate.isChecked()

        if not options.cfg.use_aggregate:
            options.cfg.MODE = QUERY_MODE_TOKENS
        else:
            for radio in self.ui.aggregate_radio_list:
                if radio.isChecked():
                    options.cfg.MODE = utf8(radio.text())
        #self.reaggregate(start=True)
        self.enable_apply_button()
        self.set_toolbox_appearance(TOOLBOX_AGGREGATE)

    def set_aggregate(self):
        for radio in self.ui.aggregate_radio_list:
            if radio.isChecked():
                options.cfg.MODE = utf8(radio.text())
                self.set_toolbox_appearance(TOOLBOX_AGGREGATE)
                if options.cfg.use_aggregate:
                    #self.reaggregate(start=True)
                    self.enable_apply_button()

    def change_summarize(self):
        options.cfg.drop_duplicates = self.ui.check_drop_duplicates.isChecked()
        self.set_toolbox_appearance(TOOLBOX_SUMMARY)
        #self.reaggregate(start=True)
        self.enable_apply_button()

    def change_summarize_filters(self):
        print("change_summarize_filters")
        options.cfg.use_summarize_filters = self.ui.check_summarize_filters.isChecked()
        self.set_toolbox_appearance(TOOLBOX_SUMMARY)
        #self.reaggregate(start=True)
        self.enable_apply_button()

    def set_context_values(self, mode=None, left_span=None, right_span=None):
        if mode is not None:
            if mode == CONTEXT_STRING:
                self.ui.radio_context_mode_string.setChecked(True)
            elif mode == CONTEXT_COLUMNS:
                self.ui.radio_context_mode_columns.setChecked(True)
            elif mode == CONTEXT_SENTENCE:
                self.ui.radio_context_mode_sentence.setChecked(True)
            elif mode == CONTEXT_KWIC:
                self.ui.radio_context_mode_kwic.setChecked(True)
                
            
        if left_span is not None:
            self.ui.context_left_span.setValue(left_span)
        if right_span is not None:
            self.ui.context_right_span.setValue(right_span)

    def get_context_values(self):
        # determine context mode:
        if not self.ui.check_context.isChecked():
            options.cfg.context_mode = CONTEXT_NONE
            return
        
        if self.ui.radio_context_mode_kwic.isChecked():
            options.cfg.context_mode = CONTEXT_KWIC
        if self.ui.radio_context_mode_string.isChecked():
            options.cfg.context_mode  = CONTEXT_STRING
        if self.ui.radio_context_mode_columns.isChecked():
            options.cfg.context_mode  = CONTEXT_COLUMNS

        # get context options:
        options.cfg.context_left = self.ui.context_left_span.value()
        options.cfg.context_right = self.ui.context_right_span.value()
        options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())

    def manage_stopwords(self):
        from . import stopwords 
        old_list = options.cfg.stopword_list
        result = stopwords.Stopwords.manage(options.cfg.stopword_list, options.cfg.icon)
        if result is not None:
            options.cfg.stopword_list = result

        if (options.cfg.use_stopwords and 
            set(old_list) != set(options.cfg.stopword_list)):
            #self.reaggregate(start=True)
            self.enable_apply_button()
        
        self.set_toolbox_appearance(TOOLBOX_STOPWORDS)

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
        pass
        #self.reaggregate()
        #if self.Session.query_type == queries.ContingencyQuery:
            #self.reaggregate(query_type=queries.ContingencyQuery, recalculate=True)
        
    def result_column_resize(self, index, old, new):
        #header = self.table_model.header[index].lower()
        #options.cfg.column_width[header.replace(" ", "_").replace(":", "_")] = new
        ## notify the GUI that the whole data frame has changed:
        #self.table_model.dataChanged.emit(
            #self.table_model.createIndex(0, 0), 
            #self.table_model.createIndex(self.table_model.rowCount(), self.table_model.columnCount()))

        #self.ui.data_preview.setTextElideMode(QtCore.Qt.ElideMiddle)
        #self.ui.data_preview.setHorizontalScrollMode(self.ui.data_preview.ScrollPerPixel)
        if options.cfg.word_wrap:
            self.resize_rows()

    def result_cell_clicked(self, index=None, token_id=None):
        """
        Launch the context viewer.
        """
        token_width = 1

        if index is not None:
            if self.Session.query_type == queries.ContrastQuery:
                from . import independencetestviewer
                if self.ui.data_preview.model().data(index, QtCore.Qt.DisplayRole):
                    data = self.ui.data_preview.model().data(index, QtCore.Qt.UserRole)
                    viewer = independencetestviewer.IndependenceTestViewer(data, icon=options.cfg.icon)
                    viewer.show()
                    self.widget_list.append(viewer)
                return
            
            model_index = index
            row = model_index.row()
            data = self.table_model.content.iloc[row]
            meta_data = self.table_model.invisible_content.iloc[row]
            
            if isinstance(self.Session, StatisticsSession):
                column = data.index[model_index.column()]
                self.show_unique_values(rc_feature=meta_data["coquery_invisible_rc_feature"],
                                        uniques=column != "coq_statistics_entries")
            else:
                try:
                    token_id = meta_data["coquery_invisible_corpus_id"]
                    token_width = meta_data["coquery_invisible_number_of_tokens"]
                except KeyError:
                    QtGui.QMessageBox.critical(self, "Context error", msg_no_context_available)
                    
        origin_id = options.cfg.main_window.Session.Corpus.get_source_id(token_id)
        
        viewer = contextviewer.ContextView(
            self.Session.Corpus, int(token_id), int(origin_id), int(token_width), 
            icon=options.cfg.icon)
        viewer.show()
        self.widget_list.append(viewer)

    def verify_file_name(self):
        file_name = str(self.ui.edit_file_name.text())
        if not os.path.isfile(file_name):
            self.ui.edit_file_name.setStyleSheet("QLineEdit { background-color: rgb(255, 255, 192) }")
            return False
        else:
            self.ui.edit_file_name.setStyleSheet("QLineEdit {{ background-color: {} }} ".format(
                options.cfg.app.palette().color(QtGui.QPalette.Base).name()))
            return True

    def switch_to_file(self):
        """ Toggle to query file input. """
        #self.ui.radio_query_file.setFocus()
        self.ui.radio_query_file.setChecked(True)

    def switch_to_query(self):
        """ Toggle to query string input. """
        self.ui.radio_query_string.setChecked(True)

    def finalize_reaggregation(self):
        self.display_results(drop=False)
        self.stop_progress_indicator()
        self.resize_rows()
        self.show_query_status()
        self.check_group_items()
        self.ui.group_management.setEnabled(True)
        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Apply).setDisabled(True)
        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Cancel).setDisabled(True)
        #self.ui.button_box_reaggregate.hide()
        print("reaggregation: done")

        manager = managers.get_manager(options.cfg.MODE, self.Session.Resource.name)
        if options.cfg.use_stopwords and manager.stopwords_failed:
            rc_feature = getattr(self.Session.Resource,
                            getattr(self.Session.Resource, QUERY_ITEM_WORD))
            msg = msg_no_word_information.format(rc_feature)
            QtGui.QMessageBox.warning(self, 
                                       "No word information available for stopwords – Coquery", 
                                       msg, 
                                       QtGui.QMessageBox.Ok, 
                                       QtGui.QMessageBox.Ok)

    def kill_reaggregation(self):
        self.aggr_thread.terminate()
        self.finalize_reaggregation()
        self.enable_apply_button()
        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Cancel).setDisabled(True)
        
    def reaggregate(self, recalculate=True, start=False):
        """
        Reaggregate the current data table when changing the visibility of
        the table columns.
        
        Parameters
        ----------
        recalculate : bool
            True if the manager should reevaluate all functions
            
        start : bool
            True if the start timer should be reset when starting the 
            reaggregation
        """
        
        self.getGuiValues()

        if not self.Session:
            return

        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Apply).setDisabled(True)
        self.ui.button_box_reaggregate.button(QtGui.QDialogButtonBox.Cancel).setEnabled(True)
        
        self.Session.group_functions = self._group_functions
        self.Session._column_functions = self._column_functions

        if start:
            self.Session.start_timer()
        self.showMessage("Managing data...")
        self.unfiltered_tokens = len(self.Session.data_table.index)
        self.aggr_thread = classes.CoqThread(lambda: self.Session.aggregate_data(recalculate), parent=self)
        self.aggr_thread.taskException.connect(self.exception_during_query)
        self.aggr_thread.taskFinished.connect(self.finalize_reaggregation)
        self.abortRequested.connect(self.kill_reaggregation)

        if not self.Session.has_cached_data():
            self.start_progress_indicator()
        
        print("reaggregate")
        self.ui.group_management.setDisabled(True)
        #self.ui.button_box_reaggregate.show()
        self.aggr_thread.start()

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
        if not hasattr(self.Session, "start_time"):
            self.Session.start_time = datetime.datetime.now()
        self.Session.stop_timer()

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

        if QtGui.QLabel().palette().window().color().red() > 127:
            col = "#ff0000"
        else:
            col = "#7f0000"

        s = "Number of matches: {num:<8} Unique matches: {uniq:<8} Duration of last operation: {dur}"

        if options.cfg.number_of_tokens and self.unfiltered_tokens != 0:
            s = "<font color='{{col}}'>Note: </font> Match limit ({{lim:<8}}) enabled. {s}".format(s=s)

        self.showMessage(s.format(
            num=self.unfiltered_tokens, 
            uniq=len(self.table_model.content),
            dur=duration_str, col=col,
            lim=options.cfg.number_of_tokens))

    def set_toolbox_appearance(self, row):
        def _set_icon(col, label):
            if label:
                self.ui.list_toolbox.item(row, col).setIcon(self.get_icon(label))
            else:
                self.ui.list_toolbox.item(row, col).setIcon(QtGui.QIcon())
                
        if row == TOOLBOX_CONTEXT:
            check = self.ui.check_context
        elif row == TOOLBOX_AGGREGATE:
            check = self.ui.check_aggregate
        
        if row == TOOLBOX_CONTEXT:
            if not check.isChecked():
                _set_icon(2, None)
            else:
                if options.cfg.context_left != 0 or options.cfg.context_right != 0:
                    _set_icon(2, "lightning")
                else:
                    _set_icon(2, "sign-question")
        elif row == TOOLBOX_STOPWORDS:
            if options.cfg.stopword_list:
                _set_icon(1, "filter" if self.ui.check_stopwords.isChecked() else None)
                _set_icon(2, "lightning" if self.ui.check_stopwords.isChecked() else None)
            else:
                _set_icon(1, "sign-question" if self.ui.check_stopwords.isChecked() else None)
                _set_icon(2, None)
            if self.Session:
                manager = managers.get_manager(options.cfg.MODE, self.Session.Resource.name)
                if manager.stopwords_failed:
                    _set_icon(2, "warning" if check.isChecked() else None)
                    _set_icon(1, None)

        elif row == TOOLBOX_GROUPING:
            _set_icon(2, None)
            if self.ui.check_group_filters.isChecked():
                active = (self.ui.list_group_columns.columns and 
                          options.cfg.group_filter_list)
                _set_icon(1, "filter" if active else "sign-question")
            else:
                _set_icon(1, None)
        
        elif row == TOOLBOX_AGGREGATE:
            _set_icon(2, "lightning" if check.isChecked() else None)
        
        elif row == TOOLBOX_SUMMARY:
            active = (self.ui.check_drop_duplicates.isChecked())
            _set_icon(2, "lightning" if active else None)
            if self.ui.check_summarize_filters.isChecked():
                _set_icon(1, "filter" if options.cfg.filter_list else "sign-question")
            else:
                _set_icon(1, None)

    def toggle_toolbox(self, row, col):
        """
        Toggle the toolbox 'n' from the data management widget.
        """
        if col == 0:
            return

        if row == TOOLBOX_CONTEXT:
            check = self.ui.check_context
        elif row == TOOLBOX_STOPWORDS:
            check = self.ui.check_stopwords
        elif row == TOOLBOX_GROUPING:
            check = None
        elif row == TOOLBOX_AGGREGATE:
            check = self.ui.check_aggregate
        elif row == TOOLBOX_SUMMARY:
            if col == 1:
                check = self.ui.check_summarize_filters
            else:
                check = self.ui.check_drop_duplicates
        
        if row == TOOLBOX_STOPWORDS:
            checked = not self.ui.check_stopwords.isChecked()
            self.ui.check_stopwords.setChecked(checked)
            options.cfg.use_stopwords = checked
            self.set_toolbox_appearance(row)
            return

        # Toggle activation:
        if col == 2:
            if check:
                checked = not check.isChecked()
                check.setChecked(checked)
        elif col == 1:
            if row == TOOLBOX_GROUPING:
                checked = not self.ui.check_group_filters.isChecked()
                self.ui.check_group_filters.setChecked(checked)
                options.cfg.use_group_filters = checked
            elif row == TOOLBOX_SUMMARY:
                checked = not self.ui.check_summarize_filters.isChecked()
                self.ui.check_summarize_filters.setChecked(checked)
                options.cfg.use_summarize_filters = checked
        
        self.set_toolbox_appearance(row)
            
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

        if options.cfg.first_run:
            if self._first_corpus:
                self.selected_features = ["word_label"]
                self._first_corpus = False

        if self.ui.combo_corpus.count():
            corpus_name = utf8(self.ui.combo_corpus.currentText())
            self.resource, self.corpus, self.lexicon, self.path = options.cfg.current_resources[corpus_name]
            self.column_tree.setup_resource(self.resource)
        else:
            self.column_tree.clear()

        self.column_tree.select(self.selected_features)

        options.cfg.corpus = utf8(self.ui.combo_corpus.currentText())

    def toggle_selected_feature(self, item):
        is_checked = (item.checkState(0) == QtCore.Qt.Checked)
        rc_feature = utf8(item.objectName())
        if rc_feature and not rc_feature.endswith("_table"):
            if is_checked:
                self.selected_features.add(rc_feature)
            else:
                self.selected_features.remove(rc_feature)

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
            
    def finalize_resize(self):
        print("resize: done")
            
    def resize_rows(self):
        if not options.cfg.word_wrap:
            return
        self.resize_thread = classes.CoqThread(self.ui.data_preview.resizeRowsToContents, parent=self)
        self.resize_thread.taskFinished.connect(self.finalize_resize)
        self.resize_thread.taskException.connect(self.exception_during_query)
        print("resize: start")
        self.resize_thread.start()
    
    def display_results(self, drop=True):
        if len(self.Session.output_object) == 0:
            self.ui.text_no_match.show()
            # disable menu entries:
            self.ui.action_save_results.setEnabled(False)
            self.ui.action_copy_to_clipboard.setEnabled(False)
        else:
            self.ui.data_preview.setEnabled(True)
            self.ui.text_no_match.hide()
            # enable menu entries:
            self.ui.action_save_results.setEnabled(True)
            self.ui.action_copy_to_clipboard.setEnabled(True)

        # Visualizations menu is disabled for corpus statistics:
        if isinstance(self.Session, StatisticsSession):
            self.ui.menuAnalyse.setEnabled(False)
        else:
            self.ui.menuAnalyse.setEnabled(True)

        self.table_model = classes.CoqTableModel(self.Session.output_object, session=self.Session)
        if self.table_model.rowCount():
            self.last_results_saved = False
        
        self.ui.data_preview.setModel(self.table_model)
        self.ui.data_preview.setDelegates()

        #if drop:
            ## drop row colors and row visibility:

            ### FIXME: reimplement row visibility
            ##self.Session.reset_row_visibility(self.Session.query_type)
            ##options.cfg.row_visibility = collections.defaultdict(dict)
            #options.cfg.row_color = {}
        ## set column widths:
        #for i, column in enumerate(self.table_model.header):
            ## FIXME: reimplement column widths
            #if column in options.cfg.column_width:
                #pass
                ##self.ui.data_preview.setColumnWidth(i, options.cfg.column_width[column])
                ##self.ui.data_preview.setColumnWidth(i, options.cfg.column_width[column.lower().replace(" ", "_").replace(":", "_")])
        
        if options.cfg.memory_dump:
            memory_dump()

    def file_options(self):
        """ Get CSV file options for current query input file. """
        from . import csvoptions
        
        csv_options = csvoptions.CSVOptions(
            sep=options.cfg.input_separator,
            header=options.cfg.file_has_headers,
            quote_char=options.cfg.quote_char,
            skip_lines=options.cfg.skip_lines,
            #encoding=options.cfg.input_encoding,
            encoding="utf-16",
            file_name=utf8(self.ui.edit_file_name.text()),
            selected_column=options.cfg.query_column_number)
        
        results = csvoptions.CSVOptionDialog.getOptions(
            default=csv_options, parent=self, icon=options.cfg.icon)
        
        if results:
            options.cfg.input_separator = results.sep 
            options.cfg.query_column_number = results.selected_column
            options.cfg.file_has_headers = results.header
            options.cfg.skip_lines = results.skip_lines
            options.cfg.quote_char = results.quote_char
            options.cfg.input_encoding = results.encoding
            self.ui.edit_file_name.setText(results.file_name)
            
            if options.cfg.input_separator == "{tab}":
                options.cfg.input_separator = "\t"
            elif options.cfg.input_separator == "{space}":
                options.cfg.input_separator = " "
            self.switch_to_file()

    def manage_filters(self):
        from . import addfilters
        old_list = options.cfg.filter_list
        
        try:
            columns = self.table_model.content.columns
            dtypes = self.table_model.content.dtypes
        except AttributeError:
            columns = []
            dtypes = []
            
        result = addfilters.FilterDialog.set_filters(
            filter_list=options.cfg.filter_list,
            columns=columns, session=self.Session, dtypes=dtypes)

        if result is not None:
            options.cfg.filter_list = result

            s1 = {x.get_hash() for x in old_list} 
            s2 = {x.get_hash() for x in result}

            if (options.cfg.use_summarize_filters and s1 != s2):
                #self.reaggregate()
                self.enable_apply_button()
        
            self.set_toolbox_appearance(TOOLBOX_SUMMARY)

    def manage_group_filters(self):
        from . import addfilters
        old_list = options.cfg.group_filter_list
        
        try:
            columns = self.table_model.content.columns
            dtypes = self.table_model.content.dtypes
        except AttributeError:
            columns = []
            dtypes = []
            
        result = addfilters.FilterDialog.set_filters(
            filter_list=options.cfg.group_filter_list,
            columns=columns, session=self.Session, dtypes=dtypes)
        if result is not None:
            options.cfg.group_filter_list = result

            s1 = {x.get_hash() for x in old_list} 
            s2 = {x.get_hash() for x in result}

            if (options.cfg.use_group_filters and s1 != s2):
                #self.reaggregate()
                self.enable_apply_button()

            self.set_toolbox_appearance(TOOLBOX_GROUPING)        

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
            # FIXME: use manager instead
            #ordered_headers = [x for x in ordered_headers if options.cfg.column_visibility.get(x, True)]
            tab = self.table_model.content[ordered_headers]

            ## restrict to visible rows:
            # FIXME: reimplement row visibility
            #tab = tab[self.Session.row_visibility[self.Session.query_type]]
            
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
        if not options.use_tgt:
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
        # FIXME: use manager instead
        #ordered_headers = [x for x in ordered_headers if options.cfg.column_visibility.get(x, True)]
        ordered_headers.append("coquery_invisible_corpus_id")
        tab = self.table_model.content[ordered_headers]

        ## restrict to visible rows:
        # FIXME: reimplement row visibility
        #tab = tab[self.Session.row_visibility[self.Session.query_type]]
            
        writer = TextgridWriter(tab, self.Session.Resource)
        n = writer.write_grids(name, ordered_headers)
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
        self.ui.group_management.setEnabled(True)
        
    def _display_progress(self, n=None):
        self.ui.status_progress.setRange(0, 0)
        self.ui.status_progress.show()
        if n is None:
            self.ui.multi_query_progress.hide()
        else:
            self.ui.multi_query_progress.setRange(0, n)
            self.ui.multi_query_progress.show()
        
    def start_progress_indicator(self, n=None):
        """ Show the progress indicator, and make it move. """
        self._display_progress(n)
        self._multi_progress = n
        
    def stop_progress_indicator(self):
        """ Stop the progress indicator from moving, and hide it as well. """
        self.ui.status_progress.setRange(0, 1)
        self.ui.status_progress.hide()
        self.ui.multi_query_progress.setRange(0, 1)
        self.ui.multi_query_progress.hide()
        
    def finalize_query(self, to_file=False):
        self.query_thread = None
        if to_file:
            self.showMessage("Query results written to {}.".format(options.cfg.output_path))
            self.set_query_button()
            self.stop_progress_indicator()
        else:
            self.Session = self.new_session
            del self.new_session
            self.reaggregate()
            self.set_query_button()
            self.stop_progress_indicator()
            
            if isinstance(self.Session, StatisticsSession):
                self.ui.tool_widget.widget(TOOLBOX_GROUPING).setDisabled(True)
            else:
                self.ui.tool_widget.widget(TOOLBOX_GROUPING).setEnabled(True)
            
        # Create an alert in the system taskbar to indicate that the query has 
        # completed:
        options.cfg.app.alert(self, 0)
        logger.info("Done")
        print("run_query: done")
        
    def get_output_column_menu(self, point=None, selection=[]):
        if point:
            item = self.ui.options_tree.itemAt(point)
        else:
            item = selection[0]

        if not item:
            return

        menu = CoqResourceMenu(item=item, parent=self)
        menu.viewUniquesRequested.connect(self.show_unique_values)
        menu.viewEntriesRequested.connect(lambda x:self.show_unique_values(x, uniques=False))
        menu.addLinkRequested.connect(self.add_link)
        menu.addGroupRequested.connect(self.add_group_column)
        menu.removeGroupRequested.connect(self.remove_group_column)
        menu.removeItemRequested.connect(self.remove_link)

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
        
        _, hashed, table, feature = resource.split_resource_feature(rc_feature)
        if hashed is None:
            db_name = resource.db_name
        else:
            _, ext_res = get_by_hash(hashed)
            db_name = ext_res.db_name
                
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

        if point:
            header = self.ui.data_preview.horizontalHeader()
            index = header.logicalIndexAt(point.x())
            column = self.table_model.header[index]
            if column not in selection:
                selection = [column]

        menu = CoqColumnMenu(columns=selection, parent=self)
        menu.showColumnRequested.connect(self.show_columns)
        menu.hideColumnRequested.connect(self.hide_columns)
        menu.renameColumnRequested.connect(self.rename_column)
        menu.resetColorRequested.connect(self.reset_colors)
        menu.changeColorRequested.connect(self.change_colors)
        menu.addFunctionRequested.connect(self.add_function)
        menu.removeFunctionRequested.connect(self.remove_functions)
        menu.editFunctionRequested.connect(self.edit_function)
        menu.changeSortingRequested.connect(self.change_sorting_order)

        return menu

    def get_row_submenu(self, selection=pd.Series(), point=None):
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
        if len(selection) == 0:
            if point:
                header = self.ui.data_preview.verticalHeader()
                row = header.logicalIndexAt(point.y())
                selection = self.table_model.content.index[[row]]
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

            ## FIXME: reimplement row visibility
            ## Check if any row is hidden
            #row_vis = self.Session.row_visibility[self.Session.query_type][selection]
            #if not row_vis.all():
                #if length > 1:
                    #if ~row_vis.all():
                        #action = QtGui.QAction("&Show rows", self)
                    #else:
                        #action = QtGui.QAction("&Show hidden rows", self)
                #else:
                    #action = QtGui.QAction("&Show row", self)
                #action.triggered.connect(lambda: self.set_row_visibility(selection, True))
                #action.setIcon(self.get_icon("sign-maximize"))
                #menu.addAction(action)
            ## Check if any row is visible
            #if row_vis.any():
                #if length > 1:
                    #if row_vis.all():
                        #action = QtGui.QAction("&Hide rows", self)
                    #else:
                        #action = QtGui.QAction("&Hide visible rows", self)
                #else:
                    #action = QtGui.QAction("&Hide row", self)
                #action.triggered.connect(lambda: self.set_row_visibility(selection, False))
                #action.setIcon(self.get_icon("sign-minimize"))
                #menu.addAction(action)

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
        
        selection = self.table_model.content.index[[x.row() for x in self.ui.data_preview.selectionModel().selectedRows()]]
        
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
        
        if column.startswith("func_"):
            manager = managers.get_manager(options.cfg.MODE, self.Session.Resource.name)
            fun = manager.get_function(column)
            column_name = fun.get_label(self.Session, manager, unlabel=True)
            current_name = fun.get_label(self.Session, manager, unlabel=False)
            name = RenameColumnDialog.get_name(column_name, current_name)
            fun.set_label(name)
        else:
            column_name = self.Session.translate_header(column, ignore_alias=True)
            current_name = options.cfg.column_names.get(column, column_name)
            name = RenameColumnDialog.get_name(column_name, current_name)
            options.cfg.column_names[column] = name

    def hide_columns(self, selection):
        """
        Show the columns in the selection.

        Parameters
        ----------
        selection : list
            A list of column names.
        """
        manager = managers.get_manager(options.cfg.MODE, 
                                      options.cfg.main_window.Session.Resource.name)
        for column in selection:
            manager.hide_column(column)
        self.update_columns()

    def show_columns(self, selection):
        """
        Show the columns in the selection.

        Parameters
        ----------
        selection : list
            A list of column names.
        """
        manager = managers.get_manager(options.cfg.MODE, 
                                      options.cfg.main_window.Session.Resource.name)
        for column in selection:
            manager.show_column(column)
        self.update_columns()

    def update_columns(self):
        """
        Update the table by emitting the adequate signals.
        
        This method emits geometriesChanged, layoutChanged and 
        columnVisibilityChanged signals, and also resorts the table if 
        necessary.
        """
        self.table_model.layoutChanged.emit()
        self.columnVisibilityChanged.emit()
        self.ui.data_preview.horizontalHeader().geometriesChanged.emit()

    ## FIXME: reimplement row visibility
    #def update_row_visibility(self):
        #"""
        #Update the aggregations if row visibility has changed.
        #"""
        #self.Session.drop_cached_aggregates()
        #self.reaggregate()

    ## FIXME: reimplement row visibility
    #def set_row_visibility(self, selection, state):
        #""" 
        #Set the visibility of the selected rows.
        
        #Parameters
        #----------
        #selection : list
            #A list of row indices
        
        #state : bool
            #True if the rows should be visible, or False to hide the rows
        #"""
        #self.Session.row_visibility[self.Session.query_type][selection] = state

        #self.ui.data_preview.verticalHeader().geometriesChanged.emit()
        #self.table_model.rowVisibilityChanged.emit()
        #self.table_model.layoutChanged.emit()

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
        
    def change_sorting_order(self, tup):
        column, ascending, reverse = tup
        manager = managers.get_manager(options.cfg.MODE, 
                                      options.cfg.main_window.Session.Resource.name)
        if ascending is None:
            manager.remove_sorter(column)
        else:
            manager.add_sorter(column, ascending, reverse)
        # FIXME: Make sure that changing the sorting order does not cause
        # a recalculation!
        self.reaggregate(recalculate=False, start=True)

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
        shift_pressed = options.cfg.app.keyboardModifiers() & QtCore.Qt.ShiftModifier
        options.cfg.to_file = shift_pressed
        if options.cfg.to_file:
            caption = "Choose output file... – Coquery"
            name = QtGui.QFileDialog.getSaveFileName(
                caption=caption,
                directory=options.cfg.output_file_path,
                filter="CSV files (*.csv)")
            if type(name) == tuple:
                name = name[0]
            if not name:
                return
            options.cfg.output_file_path = name
            options.cfg.output_path = name
            
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
            if not options.cfg.to_file:
                if len(self.new_session.query_list) == 1:
                    self.showMessage("Running query...")
                else:
                    self.showMessage("")
            else:
                self.showMessage("Writing to file...")
            
            self.new_session.group_functions = self._group_functions
            self.new_session.column_functions = self._column_functions

            self.start_progress_indicator(n=len(self.new_session.query_list))
            self.query_thread = classes.CoqThread(self.new_session.run_queries, to_file=options.cfg.to_file, parent=self)
            self.query_thread.taskFinished.connect(lambda: self.finalize_query(options.cfg.to_file))
            self.query_thread.taskException.connect(self.exception_during_query)
            print("run_queries: start")
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
        name = "coquery.visualizer.{}".format(name)
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

        builder = BuilderGui(coq_install_generic.BuilderClass, parent=self)
        try:
            result = builder.display()
        except Exception as e:
            errorbox.ErrorBox.show(sys.exc_info())
        if result:
            options.set_current_server(options.cfg.current_server)
        self.fill_combo_corpus()
        self.change_corpus()
        self.corpusListUpdated.emit()
            
    def build_corpus_from_table(self):
        from coquery. installer import coq_install_generic_table
        from .corpusbuilder_interface import BuilderGui
        builder = BuilderGui(coq_install_generic_table.BuilderClass, onefile=True, parent=self)
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
            self.corpus_manager.buildCorpusFromTable.connect(self.build_corpus_from_table)
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
            x = self.ui.splitter.saveState()
            options.settings.setValue("splitter", x)
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
        old_context_font = options.cfg.context_font
        last_wrap = options.cfg.word_wrap
        old_drop_on_na = options.cfg.drop_on_na 

        settings_changed = settings.Settings.manage(options.cfg, self)
        if settings_changed:
            self.ui.data_preview.setFont(options.cfg.table_font)
            self.ui.data_preview.verticalHeader().setDefaultSectionSize(QtGui.QLabel().sizeHint().height() + 2)

            if options.cfg.word_wrap != last_wrap:
                self.ui.data_preview.setWordWrap(options.cfg.word_wrap)
                self.resize_rows()

            try:
                self.table_model.formatted = self.table_model.format_content(
                    self.table_model.content)
            except Exception as e:
                print(e)

            if options.cfg.context_font != old_context_font:
                for widget in self.widget_list:
                    if isinstance(widget, contextviewer.ContextView):
                        widget.update_context()
            
            if (old_drop_on_na != options.cfg.drop_on_na):
                self.reaggregate(start=True)

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

            if not options.cfg.use_aggregate:
                options.cfg.MODE = QUERY_MODE_TOKENS
            for radio in self.ui.aggregate_radio_list:
                if radio.isChecked():
                    options.cfg.selected_aggregate = utf8(radio.text())
                    break

            # either get the query input string or the query file name:
            if self.ui.radio_query_string.isChecked():
                if type(self.ui.edit_query_string) == QtGui.QLineEdit:
                    options.cfg.query_list = [utf8(self.ui.edit_query_string.text())]
                else:
                    options.cfg.query_list = [utf8(self.ui.edit_query_string.toPlainText())]
            options.cfg.input_path = utf8(self.ui.edit_file_name.text())
            options.cfg.select_radio_query_file = bool(self.ui.radio_query_file.isChecked())

            options.cfg.external_links = self.get_external_links()
            # FIXME: eventually, selected_features should be a session variable
            options.cfg.selected_features = self.selected_features
            options.cfg.group_columns = self.get_group_columns()
            self.get_context_values()
            print(options.cfg.context_mode)

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

    def get_group_columns(self):
        """
        Return a list of currently selected group columns
        """
        return [x for _, x in self.ui.list_group_columns.columns]

    def show_log(self):
        from . import logfile
        log_view = logfile.LogfileViewer(parent=self)
        log_view.show()
        self.widget_list.append(log_view)

    def show_about(self):
        from . import about
        about = about.AboutDialog(parent=self)
        about.exec_()
        
    def show_available_modules(self):
        from . import availablemodules
        available = availablemodules.AvailableModulesDialog(parent=self)
        available.show()
        self.widget_list.append(available)
        
    def setGUIDefaults(self):
        """ Set up the gui values based on the values in options.cfg.* """
        self.ui.tool_widget.blockSignals(True)

        for col in [x for x in options.cfg.group_columns if x]:
            self.ui.list_group_columns.add_resource(col)
            options.cfg.group_columns = self.get_group_columns()

        # set corpus combo box to current corpus:
        index = self.ui.combo_corpus.findText(options.cfg.corpus)
        if index > -1:
            self.ui.combo_corpus.setCurrentIndex(index)
        self.ui.check_context.setChecked(options.cfg.use_context)
        self.ui.check_stopwords.setChecked(options.cfg.use_stopwords)
        self.ui.check_group_filters.setChecked(options.cfg.use_group_filters)
        self.ui.check_aggregate.setChecked(options.cfg.use_aggregate)
        self.ui.check_drop_duplicates.setChecked(options.cfg.drop_duplicates)
        self.ui.check_summarize_filters.setChecked(options.cfg.use_summarize_filters)

        for radio in self.ui.aggregate_radio_list:
            if utf8(radio.text()) == options.cfg.selected_aggregate:
                radio.setChecked(True)
                break

        for i in range(self.ui.list_toolbox.rowCount()):
            self.set_toolbox_appearance(i)

        self.ui.edit_file_name.setText(options.cfg.input_path)
        self.ui.edit_query_string.setText("\n".join(options.cfg.query_list))

        self.ui.radio_query_string.setChecked(not options.cfg.select_radio_query_file)
        self.ui.radio_query_file.setChecked(options.cfg.select_radio_query_file)
        
        for rc_feature in options.cfg.selected_features:
            self.ui.options_tree.setCheckState(rc_feature, QtCore.Qt.Checked)


        self.set_context_values(mode=options.cfg.context_mode,
                                left_span=options.cfg.context_left,
                                right_span=options.cfg.context_right)

        # get table from last session, if possible:
        try:
            self.table_model.set_header(options.cfg.last_header)
            self.table_model.set_data(options.cfg.last_content)
            self.Session = options.cfg.last_session
            self.ui.data_preview.setModel(self.table_model)
        except AttributeError:
            pass
        
        self.ui.tool_widget.blockSignals(False)
        
        
        self.set_main_screen_appearance()
        self.activate_group_column_buttons()
        
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

        current_corpus = utf8(self.ui.combo_corpus.currentText())
        resource, _, _ = options.get_resource(current_corpus)

        link = linkselect.LinkSelect.pick(
                                        res_from=resource, 
                                        rc_from=item.objectName(),
                                        corpus_omit=[current_corpus],
                                        parent=self)
        
        if link:
            options.cfg.table_links[options.cfg.current_server].append(link)
            self.column_tree.add_external_link(item, link)

    def remove_link(self, item):
        self.column_tree.remove_external_link(item)
        options.cfg.table_links[options.cfg.current_server].remove(item.link)
          
    def set_function_button_labels(self):
        l = self._group_functions.get_list()
        label = _translate("MainWindow", "Group functions{}...", None)
        
        if len(l) == 0:
            mark = ""
        else:
            mark = " ({})".format(len(l))
        self.ui.button_add_group_function.setText(label.format(mark))

        try:
            session = options.cfg.main_window.Session
            manager = managers.get_manager(options.cfg.MODE, session.Resource.name)
        except:
            manager = managers.get_manager(options.cfg.MODE, utf8(self.ui.combo_corpus.currentText()))
        l = manager.user_summary_functions.get_list()
        label = _translate("MainWindow", "Summary functions{}...", None)
        if len(l) == 0:
            mark = ""
        else:
            mark = " ({})".format(len(l))
        self.ui.button_add_summary_function.setText(label.format(mark))
          
    def add_function(self, columns=[], summary=False, group=False, **kwargs):
        from . import functionapply

        session = options.cfg.main_window.Session
        if session is not None:
            manager = managers.get_manager(options.cfg.MODE, session.Resource.name)
        else:
            manager = managers.get_manager(options.cfg.MODE, utf8(self.ui.combo_corpus.currentText()))

        if group or summary:
            if group:
                types = [
                         functions.FilteredRows, functions.PassingRows,
                         functions.Freq, functions.FreqNorm,
                         functions.FreqPTW, functions.FreqPMW,
                         functions.RowNumber, 
                         functions.Entropy, functions.Percent, 
                         functions.Proportion, functions.Tokens, 
                         functions.Types, functions.TypeTokenRatio]
                checked = [type(x) for x in self._group_functions.get_list()]
  
            else:
                types = [
                         functions.FilteredRows, functions.PassingRows,
                         functions.Entropy, 
                         functions.Freq, functions.FreqNorm,
                         functions.FreqPTW, functions.FreqPMW,
                         functions.RowNumber, 
                         functions.Percent, functions.Proportion, 
                         functions.Tokens, functions.Types, 
                         functions.TypeTokenRatio,
                         functions.CorpusSize, functions.SubcorpusSize]
                checked = [type(x) for x in manager.user_summary_functions.get_list()]
                         
            kwargs.update({
                "function_types": types,
                "max_parameters": 0,
                "checkable": True,
                "checked": checked,
                "edit_label": False,
                "available_columns": []})
        else:
            dtypes = pd.Series([self.table_model.get_dtype(x) for x in columns])
            try:
                if all(dtypes != object):
                    kwargs.update({"function_class": (functions.MathFunction, functions.LogicFunction)})
                else:
                    kwargs.update({"function_class": (functions.StringFunction, functions.LogicFunction)})
            except Exception as e:
                print(e)
                kwargs.update({"function_class": tuple()})
            if not "available_columns" in kwargs:
                kwargs.update({"available_columns": [x for x in self.table_model.content.columns if x not in columns]})
        response = functionapply.FunctionDialog.set_function(parent=self, columns=columns, **kwargs)

        if response is None:
            return

        if group:
            self._group_functions.set_list([x(sweep=True, hidden=True, group=True) for x in response])
            self.set_toolbox_appearance(TOOLBOX_GROUPING)
        elif summary:
            manager.user_summary_functions.set_list([x(sweep=True) for x in response])
            self.set_toolbox_appearance(TOOLBOX_SUMMARY)
        else:
            fun_type, value, aggr, label = response
            fun = fun_type(columns=columns, value=value, aggr=aggr, label=label)
            self._column_functions.add_function(fun)

        self.set_function_button_labels()
        self.enable_apply_button()
            
    def edit_function(self, column):
        from . import functionapply
        session = options.cfg.main_window.Session
        manager = managers.get_manager(options.cfg.MODE, session.Resource.name)
        func = self._column_functions.find_function(column)

        dtypes = pd.Series([self.table_model.get_dtype(x) for x in func.columns(self.table_model.content)])
        try:
            if all(dtypes != object):
                d = {"function_class": (functions.MathFunction, functions.LogicFunction)}
            else:
                d = {"function_class": (functions.StringFunction, functions.LogicFunction)}
        except Exception as e:
            print(e)
            d = {"function_class": tuple()}

        print("----")
        print(func, func.columns(self.table_model.content), d)
        response = functionapply.FunctionDialog.edit_function(func, parent=self, **d)
        if response:
            fun_type, value, aggr, label = response
            new_func = fun_type(columns=func.columns(self.table_model.content), value=value, aggr=aggr, label=label)
            self._column_functions.replace_function(func, new_func)
            self.update_columns()

    def remove_functions(self, columns):
        session = options.cfg.main_window.Session
        manager = managers.get_manager(options.cfg.MODE, session.Resource.name)
        for col in columns:
            func = self._column_functions.find_function(col)
            if func:
                self._column_functions.remove_function(func)
            else:
                # this exception can happen if the function is a summary 
                # or a grouping function:
                summary_func = manager.user_summary_functions.find_function(col)
                group_func = self._group_functions.find_function(col)
                if summary_func:
                    manager.user_summary_functions.remove_function(summary_func)
                else:
                    self._group_functions.remove_function(group_func)
            try:
                options.cfg.column_names.remove(func.get_id())
            except AttributeError:
                pass
                
        self.update_columns()
            
def _translate(x, text, y):
    return utf8(text)
    
logger = logging.getLogger(NAME)

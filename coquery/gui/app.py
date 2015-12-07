# -*- coding: utf-8 -*-

"""
app.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function

import importlib
import os
import codecs
import random
import logging
from collections import defaultdict

import numpy as np
import pandas as pd

import __init__
from session import *
from defines import *
from pyqt_compat import QtCore, QtGui
import QtProgress

import coqueryUi, coqueryCompactUi

import classes
#import results 
import error_box
import sqlwrap
import queries
import contextview

from queryfilter import *

# load visualizations
sys.path.append(os.path.join(sys.path[0], "visualizations"))
sys.path.append(os.path.join(sys.path[0], "installer"))

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

    def __init__(self, parent=None):
        """ Initialize the main window. This sets up any widget that needs
        spetial care, and also sets up some special attributes that relate
        to the GUI, including default appearances of the columns."""
        QtGui.QMainWindow.__init__(self, parent)
        
        self.file_content = None
        self.csv_options = None
        self.query_thread = None
        self.last_results_saved = True
        self.last_connection_state = None
        self.last_index = None
        self.corpus_manager = None
        
        self.widget_list = []
        self.Session = None

        size = QtGui.QApplication.desktop().screenGeometry()
        # Retrieve font and metrics for the CoqItemDelegates
        options.cfg.font = options.cfg.app.font()
        options.cfg.metrics = QtGui.QFontMetrics(options.cfg.font)

        if size.height() < 1024 or size.width() < 1024:
            self.ui = coqueryCompactUi.Ui_MainWindow()
        else:
            self.ui = coqueryUi.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setup_app()
        
        # the dictionaries column_width and column_color store default
        # attributes of the columns by display name. This means that problems
        # may arise if several columns have the same name!
        # FIXME: Make sure that the columns are identified correctly.
        self.column_width = {}
        self.column_color = {}
        
        # A non-modal dialog is shown if no corpus resource is available.
        # The dialog contains some assistance on how to build a new corpus.
        if not options.get_available_resources(options.cfg.current_server):
            self.show_no_corpus_message()
        
        options.cfg.main_window = self
        # Resize the window if a previous size is available
        try:
            if options.cfg.height and options.cfg.width:
                self.resize(options.cfg.width, options.cfg.height)
        except AttributeError:
            pass
        
    def setup_app(self):
        """ Initialize all widgets with suitable data """

        self.create_output_options_tree()
        
        QtGui.QWidget().setLayout(self.ui.tag_cloud.layout())
        self.ui.cloud_flow = FlowLayout(self.ui.tag_cloud, spacing = 1)

        # add available resources to corpus dropdown box:
        corpora = [x for x in sorted(options.get_available_resources(options.cfg.current_server).keys())]

        self.ui.combo_corpus.addItems(corpora)
        
        # chamge the default query string edit to the sublassed edit class:
        self.ui.gridLayout_2.removeWidget(self.ui.edit_query_string)
        self.ui.edit_query_string.close()        
        edit_query_string = classes.CoqTextEdit(self)
        edit_query_string.setObjectName("edit_query_string")
        self.ui.gridLayout_2.addWidget(edit_query_string, 2, 1, 1, 1)
        self.ui.edit_query_string = edit_query_string
        
        self.ui.filter_box = classes.QueryFilterBox(self)
        
        self.ui.verticalLayout_5.removeWidget(self.ui.tag_cloud)
        self.ui.tag_cloud.close()
        self.ui.horizontalLayout.removeWidget(self.ui.edit_query_filter)
        self.ui.horizontalLayout.removeWidget(self.ui.label_4)
        self.ui.edit_query_filter.close()
        self.ui.label_4.close()

        self.ui.verticalLayout_5.addWidget(self.ui.filter_box)

        # set auto-completer for the filter edit:
        self.filter_variable_model = QtGui.QStringListModel()
        self.completer = QtGui.QCompleter()
        self.completer.setModel(self.filter_variable_model)
        self.completer.setCompletionMode(QtGui.QCompleter.InlineCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.ui.filter_box.edit_tag.setCompleter(self.completer)

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
        
        self.change_corpus()

        # Align screen elements:
        self.ui.label_2.setFixedHeight(self.ui.label_5.height())
        self.ui.label.setFixedHeight(self.ui.label_5.height())
        self.ui.label_5.setFixedHeight(self.ui.label_5.height())
        
        self.ui.data_preview.setEnabled(False)
        
        # set splitter stretches:
        self.ui.splitter.setStretchFactor(0,0)
        self.ui.splitter.setStretchFactor(1,1)
        self.ui.splitter_2.setStretchFactor(0,1)
        self.ui.splitter_2.setStretchFactor(1,0)

        self.table_model = classes.CoqTableModel(self)
        self.table_model.dataChanged.connect(self.table_model.sort)
        self.table_model.columnVisibilityChanged.connect(self.reaggregate)
        header = self.ui.data_preview.horizontalHeader()
        header.sectionResized.connect(self.result_column_resize)
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_header_menu)

        header = self.ui.data_preview.verticalHeader()
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_row_header_menu)

        self.ui.data_preview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.data_preview.customContextMenuRequested.connect(self.show_row_header_menu)

        self.ui.data_preview.clicked.connect(self.result_cell_clicked)
        self.ui.data_preview.horizontalHeader().setMovable(True)
        self.ui.data_preview.setSortingEnabled(False)

        self.ui.context_query_syntax.setPixmap(QtGui.qApp.style().standardPixmap(QtGui.QStyle.SP_TitleBarContextHelpButton))
        
        # This is only a template. Alledgedly, OS X does not favour 
        # status bars, so we might use a toolbar instead.
        #if __OS__ == "MAC OS X":
            #self.ui.toolbar = self.addToolBar("Status")
            #self.ui.statusbar = QtGui.QStatusBar()
            #self.ui.toolbar.addWidget(self.ui.statusbar)
            #self.ui.toolbar.setIconSize(QtCore.QSize(16, 16))
            #self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self.ui.status_message = QtGui.QLabel("{} {}".format(__init__.NAME, __init__.__version__))

        self.ui.combo_config = QtGui.QComboBox()
        self.ui.combo_config.addItems(sorted(options.cfg.server_configuration))
        self.ui.combo_config.currentIndexChanged.connect(self.change_current_server)

        self.ui.status_progress = QtGui.QProgressBar()
        self.ui.status_progress.hide()

        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui.status_message)
        layout.addWidget(self.ui.status_progress)
        layout.addItem(QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))        
        layout.addWidget(QtGui.QLabel("Database server: "))
        layout.addWidget(self.ui.combo_config)

        self.statusBar().layout().setContentsMargins(0, 0, 0, 0)
        self.statusBar().setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        self.statusBar().addWidget(widget, 1)

        self.change_mysql_configuration(options.cfg.current_server)
        
        self.connection_timer = QtCore.QTimer()
        self.connection_timer.timeout.connect(self.test_mysql_connection)
        self.connection_timer.start(10000)
        

    def setup_menu_actions(self):
        """ Connect menu actions to their methods."""
        self.ui.action_save_results.triggered.connect(self.save_results)
        self.ui.action_quit.triggered.connect(self.close)
        self.ui.action_build_corpus.triggered.connect(self.build_corpus)
        self.ui.action_manage_corpus.triggered.connect(self.manage_corpus)
        self.ui.action_remove_corpus.triggered.connect(self.remove_corpus)
        self.ui.action_settings.triggered.connect(self.settings)
        self.ui.action_mySQL_settings.triggered.connect(self.mysql_settings)
        self.ui.action_statistics.triggered.connect(self.run_statistics)
        self.ui.action_corpus_documentation.triggered.connect(self.open_corpus_help)
        self.ui.action_about_coquery.triggered.connect(self.show_about)
        self.ui.action_view_log.triggered.connect(self.show_log)
        self.ui.action_mysql_server_help.triggered.connect(self.show_mysql_guide)
        
        self.ui.action_barcode_plot.triggered.connect(
            lambda: self.visualize_data("barcodeplot"))
        self.ui.action_beeswarm_plot.triggered.connect(
            lambda: self.visualize_data("beeswarmplot"))

        self.ui.action_tree_map.triggered.connect(
            lambda: self.visualize_data("treemap"))
        self.ui.action_heat_map.triggered.connect(
            lambda: self.visualize_data("heatmap"))
        
        self.ui.action_barchart_plot.triggered.connect(
            lambda: self.visualize_data("barplot"))
        self.ui.action_stacked_barchart_plot.triggered.connect(
            lambda: self.visualize_data("barplot", percentage=True, stacked=True))
        
        self.ui.action_percentage_area_plot.triggered.connect(
            lambda: self.visualize_data("timeseries", area=True, percentage=True))
        self.ui.action_stacked_area_plot.triggered.connect(
            lambda: self.visualize_data("timeseries", area=True, percentage=False))
        self.ui.action_line_plot.triggered.connect(
            lambda: self.visualize_data("timeseries", area=False, percentage=False))
    
    def setup_hooks(self):
        """ Hook up signals so that the GUI can adequately react to user 
        input. """
        # hook file browser button:
        self.ui.button_browse_file.clicked.connect(self.select_file)
        # hook file options button:
        self.ui.button_file_options.clicked.connect(self.file_options)

        # hook up events so that the radio buttons are set correctly
        # between either query from file or query from string:
        self.focus_to_file = focusFilter()
        self.ui.edit_file_name.installEventFilter(self.focus_to_file)
        #self.focus_to_file.clicked.connect(self.select_file)
        self.ui.edit_file_name.textChanged.connect(self.switch_to_file)
        self.ui.edit_file_name.textChanged.connect(self.verify_file_name)
        self.focus_to_query = focusFilter()
        self.focus_to_query.focus.connect(self.switch_to_query)
        self.ui.edit_query_string.installEventFilter(self.focus_to_query)

        self.ui.combo_corpus.currentIndexChanged.connect(self.change_corpus)
        # hook run query button:
        self.ui.button_run_query.clicked.connect(self.run_query)#self.ui.edit_query_filter.returnPressed.connect(self.add_query_filter)
        #self.ui.edit_query_filter.textEdited.connect(self.edit_query_filter)
        self.ui.button_stopwords.clicked.connect(self.manage_stopwords)
        
        self.ui.radio_aggregate_collocations.toggled.connect(self.toggle_frequency_columns)
        self.ui.radio_aggregate_frequencies.toggled.connect(self.toggle_frequency_columns)
        self.ui.radio_aggregate_none.toggled.connect(self.toggle_frequency_columns)
        self.ui.radio_aggregate_uniques.toggled.connect(self.toggle_frequency_columns)

        self.ui.radio_aggregate_collocations.clicked.connect(
            lambda x: self.reaggregate(query_type=queries.CollocationQuery))
        self.ui.radio_aggregate_frequencies.clicked.connect(
            lambda x: self.reaggregate(query_type=queries.FrequencyQuery))
        self.ui.radio_aggregate_uniques.clicked.connect(
            lambda x: self.reaggregate(query_type=queries.DistinctQuery))
        self.ui.radio_aggregate_none.clicked.connect(
            lambda x: self.reaggregate(query_type=queries.TokenQuery))

        
    def result_column_resize(self, index, old, new):
        header = self.table_model.header[index].lower()
        options.cfg.column_width[header] = new

    def result_cell_clicked(self, index):
        """
        Launch the context viewer.
        """
        
        model_index = index
        row = model_index.row()
        data = self.table_model.content.iloc[row]
        try:
            token_id = data["coquery_invisible_corpus_id"]
            origin_id = options.cfg.main_window.Session.Corpus.get_source_id(token_id)
            token_width = data["coquery_invisible_number_of_tokens"]
        except KeyError:
            QtGui.QMessageBox.critical(self, "Context error", msg_no_context_available)

        contextview.ContextView.display(self.Session.Corpus, int(token_id), int(origin_id), int(token_width), self)

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
        """ Remove any existing tree widget for the output options, create a
        new, empty tree, add it to the layout, and return it. """
        # replace old tree widget by a new, still empty tree:
        tree = classes.CoqTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setRootIsDecorated(True)
        
        tree.addLink.connect(self.add_link)
        tree.addFunction.connect(self.add_function)
        tree.removeItem.connect(self.remove_item)
        
        self.ui.options_list.removeWidget(tree)
        self.ui.options_tree.close()
        self.ui.options_list.addWidget(tree)
        self.ui.options_tree = tree
        return tree
    
    def toggle_frequency_columns(self):
        for root in [self.ui.options_tree.topLevelItem(i) for i in range(self.ui.options_tree.topLevelItemCount())]:
            if root.objectName().startswith("coquery"):
                for child in [root.child(i) for i in range(root.childCount())]:
                    if child.objectName() in ("coquery_relative_frequency", "coquery_per_million_words"):
                        if self.ui.radio_aggregate_frequencies.isChecked():
                            child.setDisabled(False)
                        else:
                            child.setDisabled(True)
    
    def finish_reaggregation(self):
        self.stop_progress_indicator()
        self.table_model.set_data(self.Session.output_object)
        self.table_model.set_header()
    
    def reaggregate(self, query_type=None):
        """
        Reaggregate the current data table when changing the visibility of
        the table columns.
        """
        if not self.Session:
            return
        
        self.query_thread = QtProgress.ProgressThread(self.Session.aggregate_data, self)
        self.query_thread.taskFinished.connect(self.finish_reaggregation)
        self.query_thread.taskException.connect(self.exception_during_query)

        if query_type and query_type != self.Session.query_type:
            self.Session.query_type.remove_output_columns(self.Session)
            self.Session.query_type = query_type
            self.Session.query_type.add_output_columns(self.Session)
        self.start_progress_indicator()
        self.query_thread.start()

    def change_corpus(self):
        """ Change the output options list depending on the features available
        in the current corpus. If no corpus is avaiable, disable the options
        area and some menu entries. If any corpus is available, these widgets
        are enabled again."""
        if not options.get_available_resources(options.cfg.current_server):
            self.disable_corpus_widgets()
        else:
            self.enable_corpus_widgets()
            try:
                self.msg_box_no_corpus.close()
            except AttributeError:
                pass

        if self.ui.combo_corpus.count():
            corpus_name = str(self.ui.combo_corpus.currentText()).lower()
            self.resource, self.corpus, self.lexicon, self.path = options.get_available_resources(options.cfg.current_server)[corpus_name]
            self.ui.filter_box.resource = self.resource
            
            corpus_variables = [x for _, x in self.resource.get_corpus_features()]
            corpus_variables.append("Freq")
            corpus_variables.append("Freq.pmw")
            self.change_corpus_features()
            try:
                self.filter_variable_model.setStringList(corpus_variables)
            except AttributeError:
                pass

    def change_corpus_features(self, prefix="", suffix=""):
        """ Construct a new output option tree depending on the features
        provided by the corpus given in 'corpus_label."""
        
        table_dict = self.resource.get_table_dict()
        # Ignore denormalized tables:
        tables = [x for x in table_dict.keys() if not "_denorm_" in x]
        # ignore internal  variables of the form {table}_id, {table}_table,
        # {table}_table_{other}
        for table in tables:
            for var in list(table_dict[table]):
                if (var.endswith("_table") or var.endswith("_id") or var.startswith("{}_table".format(table))) or "_denorm_" in var:
                    table_dict[table].remove(var)
                    
        # Rearrange table names so that they occur in a sensible order:
        for x in reversed(["word", "lemma", "corpus", "speaker", "source", "file"]):
            if x in tables:
                tables.remove(x)
                tables.insert(0, x)
        tables.remove("coquery")
        tables.append("coquery")


        last_checked = self.ui.options_tree.get_checked()

        tree = self.create_output_options_tree()

        # populate the tree with a root for each table:
        for table in tables:
            root = classes.CoqTreeItem()
            root.setObjectName(coqueryUi._fromUtf8("{}_table".format(table)))
            root.setFlags(root.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable)
            try:
                label = type(self.resource).__getattribute__(self.resource, str("{}_table".format(table)))
            except AttributeError:
                label = table.capitalize()
                
            root.setText(0, label)
            root.setCheckState(0, QtCore.Qt.Unchecked)
            if table_dict[table]:
                tree.addTopLevelItem(root)
            
            # add a leaf for each table variable:
            for var in table_dict[table]:
                leaf = classes.CoqTreeItem()
                leaf.setObjectName(coqueryUi._fromUtf8(var))
                root.addChild(leaf)
                label = type(self.resource).__getattribute__(self.resource, var)
                leaf.setText(0, label)
                if var in last_checked: 
                    leaf.setCheckState(0, QtCore.Qt.Checked)
                else:
                    leaf.setCheckState(0, QtCore.Qt.Unchecked)
                leaf.update_checkboxes(0, expand=True)
                
    def fill_combo_corpus(self):
        """ Add the available corpus names to the corpus selection combo 
        box. """
        try:
            self.ui.combo_corpus.currentIndexChanged.disconnect()
        except TypeError:
            # ignore error if the combo box was not yet connected
            pass

        # remember last corpus name:
        last_corpus = str(self.ui.combo_corpus.currentText())

        l = [x.upper() for x in options.get_available_resources(options.cfg.current_server)]

        # add corpus names:
        self.ui.combo_corpus.clear()
        self.ui.combo_corpus.addItems([x.upper() for x in options.get_available_resources(options.cfg.current_server)])

        # try to return to last corpus name:
        new_index = self.ui.combo_corpus.findText(last_corpus.upper())
        if new_index == -1:
            new_index = 0
            
        self.ui.combo_corpus.setCurrentIndex(new_index)
        self.ui.combo_corpus.setEnabled(True)
        self.ui.combo_corpus.currentIndexChanged.connect(self.change_corpus)

    def enable_corpus_widgets(self):
        """ Enable all widgets that assume that a corpus is available."""
        self.ui.centralwidget.setEnabled(True)
        self.ui.action_statistics.setEnabled(True)
        self.ui.action_remove_corpus.setEnabled(True)
    
    def disable_corpus_widgets(self):
        """ Disable any widget that assumes that a corpus is available."""
        self.ui.centralwidget.setEnabled(False)
        self.ui.action_statistics.setEnabled(False)
        self.ui.action_remove_corpus.setEnabled(False)

    def show_no_corpus_message(self):
        """ Show a non-modal message box informing the user that no corpus
        module is available. This message box will be automatically closed 
        if a corpus resource is available."""
        self.msg_box_no_corpus = QtGui.QMessageBox(self)
        self.msg_box_no_corpus.setWindowTitle("No corpus available – Coquery")
        self.msg_box_no_corpus.setText(msg_no_corpus)
        self.msg_box_no_corpus.setInformativeText(msg_details)
        self.msg_box_no_corpus.setStandardButtons(QtGui.QMessageBox.Ok)
        self.msg_box_no_corpus.setDefaultButton(QtGui.QMessageBox.Ok)
        self.msg_box_no_corpus.setWindowModality(QtCore.Qt.NonModal)
        self.msg_box_no_corpus.setIcon(QtGui.QMessageBox.Warning)
        self.msg_box_no_corpus.show()
        
    def display_results(self):
        self.ui.box_aggregation_mode.show()
        self.ui.data_preview.setEnabled(True)
        
        self.table_model.set_data(self.Session.output_object)
        self.table_model.set_header()

        self.ui.data_preview.setModel(self.table_model)

        # drop row colors and row visibility:
        options.cfg.row_visibility = {}
        options.cfg.row_color = {}

        # set column widths:
        for i, column in enumerate(self.table_model.header):
            if column.lower() in options.cfg.column_width:
                self.ui.data_preview.setColumnWidth(i, options.cfg.column_width[column.lower()])
        
        #set delegates:
        header = self.ui.data_preview.horizontalHeader()
        for i in range(header.count()):
            column = self.table_model.header[header.logicalIndex(i)]

            if column in ("coq_conditional_probability"):
                deleg = classes.CoqProbabilityDelegate(self.ui.data_preview)
            else:
                deleg = classes.CoqResultCellDelegate(self.ui.data_preview)
            self.ui.data_preview.setItemDelegateForColumn(i, deleg)

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
            options.cfg.query_file_path = os.path.dirname(name)
            self.ui.edit_file_name.setText(name)
            self.switch_to_file()
            
    def file_options(self):
        """ Get CSV file options for current query input file. """
        import csvOptions
        results = csvOptions.CSVOptions.getOptions(
            str(self.ui.edit_file_name.text()), 
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

    def manage_stopwords(self):
        import stopwords 
        result = stopwords.Stopwords.manage(self, options.cfg.icon)
    
    def save_results(self):
        name = QtGui.QFileDialog.getSaveFileName(directory=options.cfg.results_file_path)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.results_file_path = os.path.dirname(name)
            try:
                header = self.ui.data_preview.horizontalHeader()
                ordered_headers = [self.table_model.header[header.logicalIndex(i)] for i in range(header.count())]
                ordered_headers = [x for x in ordered_headers if options.cfg.column_visibility.get(x, True)]
                tab = self.table_model.content[ordered_headers]
                # exclude invisble rows:
                tab = tab.iloc[~tab.index.isin(pd.Series(options.cfg.row_visibility.keys()))]
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
                self.last_results_saved = True
    
    def showMessage(self, S):
        self.ui.status_message.setText(S)
        
    def showConnectionStatus(self, S):
        self.ui.status_server.setText(S)
    
    def exception_during_query(self):
        if type(self.exception) == NoLemmaInformationError:
            QtGui.QMessageBox.critical(self, "Disk error", msg_no_lemma_information)
        else:
            error_box.ErrorBox.show(self.exc_info, self.exception)
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
        self.display_results()
        self.set_query_button()
        self.stop_progress_indicator()

        try:
            diff = (datetime.datetime.now() - self.Session.start_time)
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
        self.showMessage("Number of rows: {:<8}      Query duration: {:<10}".format(
            len(self.Session.output_object.index), duration_str))
        options.cfg.app.alert(self, 10)
        
    def show_header_menu(self, point ):
        header = self.ui.data_preview.horizontalHeader()
        header.customContextMenuRequested.disconnect(self.show_header_menu)
        # show self.menu about the column
        self.menu = QtGui.QMenu("Column options", self)

        index = header.logicalIndexAt(point.x())
        column = self.table_model.header[index]

        display_name = options.cfg.main_window.Session.translate_header(column)
        
        action = QtGui.QWidgetAction(self)
        label = QtGui.QLabel("<b>{}</b>".format(display_name), self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        action.setDefaultWidget(label)
        self.menu.addAction(action)
        self.menu.addSeparator()

        if not options.cfg.column_visibility.get(column, True):
            action = QtGui.QAction("&Show column", self)
            action.triggered.connect(lambda: self.toggle_visibility(column))
            action.setIcon(QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_TitleBarShadeButton))
            self.menu.addAction(action)
        else:
            action = QtGui.QAction("&Hide column", self)
            action.triggered.connect(lambda: self.toggle_visibility(column))
            action.setIcon(QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_TitleBarUnshadeButton))
            self.menu.addAction(action)
            self.menu.addSeparator()

            action = QtGui.QAction("&Rename column...", self)
            action.triggered.connect(lambda: self.rename_column(column))
            self.menu.addAction(action)

            if column in options.cfg.column_color:
                action = QtGui.QAction("&Reset color", self)
                action.triggered.connect(lambda: self.reset_color(column))
                self.menu.addAction(action)
    
            action = QtGui.QAction("&Change color...", self)
            action.triggered.connect(lambda: self.change_color(column))
            self.menu.addAction(action)
            self.menu.addSeparator()

            group = QtGui.QActionGroup(self, exclusive=True)
            action = group.addAction(QtGui.QAction("Do not sort", self, checkable=True))
            action.triggered.connect(lambda: self.change_sorting_order(column, SORT_NONE))
            if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_NONE:
                action.setChecked(True)
            self.menu.addAction(action)
            
            action = group.addAction(QtGui.QAction("&Ascending", self, checkable=True))
            action.triggered.connect(lambda: self.change_sorting_order(column, SORT_INC))
            if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_INC:
                action.setChecked(True)
            self.menu.addAction(action)
            action = group.addAction(QtGui.QAction("&Descending", self, checkable=True))
            action.triggered.connect(lambda: self.change_sorting_order(column, SORT_DEC))
            if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_DEC:
                action.setChecked(True)
            self.menu.addAction(action)
                                    
            if self.table_model.content[[column]].dtypes[0] == "object":
                action = group.addAction(QtGui.QAction("&Ascending, reverse", self, checkable=True))
                action.triggered.connect(lambda: self.change_sorting_order(column, SORT_REV_INC))
                if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_REV_INC:
                    action.setChecked(True)

                self.menu.addAction(action)
                action = group.addAction(QtGui.QAction("&Descending, reverse", self, checkable=True))
                action.triggered.connect(lambda: self.change_sorting_order(column, SORT_REV_DEC))
                if self.table_model.sort_columns.get(column, SORT_NONE) == SORT_REV_DEC:
                    action.setChecked(True)
                self.menu.addAction(action)
        
        self.menu.popup(header.mapToGlobal(point))
        header.customContextMenuRequested.connect(self.show_header_menu)

    def show_row_header_menu(self, point):
        self.ui.data_preview.customContextMenuRequested.disconnect(self.show_row_header_menu)
        header = self.ui.data_preview.verticalHeader()
        # show self.menu about the column
        self.menu = QtGui.QMenu("Row options", self)

        index = header.logicalIndexAt(point.y())
        row = self.table_model.content.index[index]
        
        selection = []
        for x in self.ui.data_preview.selectionModel().selectedRows():
            selection.append(self.table_model.content.index[x.row()])

        if not selection:
            selection.append(self.table_model.content.index[row - 1])

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
        self.menu.addAction(action)
        
        if length:
            self.menu.addSeparator()
            # Check if any row is hidden
            if any([not options.cfg.row_visibility.get(x, True) for x in selection]):
                if length > 1:
                    if all([not options.cfg.row_visibility.get(x, True) for x in selection]):
                        action = QtGui.QAction("&Show rows", self)
                    else:
                        action = QtGui.QAction("&Show hidden rows", self)
                else:
                    action = QtGui.QAction("&Show row", self)
                action.triggered.connect(lambda: self.set_row_visibility(selection, True))
                action.setIcon(QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_TitleBarShadeButton))
                self.menu.addAction(action)
            # Check if any row is visible
            if any([options.cfg.row_visibility.get(x, True) for x in selection]):
                if length > 1:
                    if all([options.cfg.row_visibility.get(x, True) for x in selection]):
                        action = QtGui.QAction("&Hide rows", self)
                    else:
                        action = QtGui.QAction("&Hide visible rows", self)
                else:
                    action = QtGui.QAction("&Hide row", self)
                action.triggered.connect(lambda: self.set_row_visibility(selection, False))
                action.setIcon(QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_TitleBarUnshadeButton))
                self.menu.addAction(action)
            self.menu.addSeparator()
            
            # Check if any row has a custom color:
            if any([x in options.cfg.row_color for x in selection]):
                action = QtGui.QAction("&Reset color", self)
                action.triggered.connect(lambda: self.reset_row_color(selection))
                self.menu.addAction(action)

            action = QtGui.QAction("&Change color...", self)
            action.triggered.connect(lambda: self.change_row_color(selection))
            self.menu.addAction(action)
        
        self.menu.popup(header.mapToGlobal(point))
        self.ui.data_preview.customContextMenuRequested.connect(self.show_row_header_menu)

    def rename_column(self, column):
        """
        Open a dialog in which the column name can be changed.
        
        Parameters
        ----------
        column : column index
        """
        from renamecolumn import RenameColumnDialog
        
        column_name = self.Session.translate_header(column, ignore_alias=True)
        current_name = options.cfg.column_names.get(column, column_name)
        
        name = RenameColumnDialog.get_name(column_name,
                                           current_name)
        options.cfg.column_names[column] = name

    def toggle_visibility(self, column):
        """ 
        Show again a hidden column, or hide a visible column.
        
        Parameters
        ----------
        column : column index
        """
        options.cfg.column_visibility[column] = not options.cfg.column_visibility.get(column, True)
        self.ui.data_preview.horizontalHeader().geometriesChanged.emit()
        # Resort the data if this is a sorting column:
        if column in self.table_model.sort_columns:
            self.table_model.sort(0, QtCore.Qt.AscendingOrder)
        self.table_model.layoutChanged.emit()
        self.table_model.columnVisibilityChanged.emit()

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
                    options.cfg.row_visibility.pop(np.int64(x))
                except KeyError:
                    pass
        else:
            for x in selection:
                options.cfg.row_visibility[np.int64(x)] = False 
        self.ui.data_preview.verticalHeader().geometriesChanged.emit()
        self.table_model.layoutChanged.emit()

    def reset_color(self, column):
        try:
            options.cfg.column_color.pop(column)
            self.table_model.layoutChanged.emit()
        except KeyError:
            pass

    def change_color(self, column):
        col = QtGui.QColorDialog.getColor()
        if col.isValid():
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
        self.menu.close()
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
        old_width = self.ui.button_run_query.width()
        self.ui.button_run_query.setText(gui_label_query_button)
        self.ui.button_run_query.setFixedWidth(max(old_width, self.ui.button_run_query.width()))
        self.ui.button_run_query.setIcon(QtGui.QIcon.fromTheme(_fromUtf8("media-playback-start")))
        
    def set_stop_button(self):
        """ Set the action button to stop queries. """
        self.ui.button_run_query.clicked.disconnect()
        self.ui.button_run_query.clicked.connect(self.stop_query)
        old_width = self.ui.button_run_query.width()
        self.ui.button_run_query.setText(gui_label_stop_button)
        self.ui.button_run_query.setFixedWidth(max(old_width, self.ui.button_run_query.width()))
        self.ui.button_run_query.setIcon(QtGui.QIcon.fromTheme(_fromUtf8("media-playback-stop")))
    
    def stop_query(self):
        response = QtGui.QMessageBox.warning(self, "Unfinished query", msg_query_running, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if response == QtGui.QMessageBox.Yes:
            logger.warning("Last query is incomplete.")
            self.ui.button_run_query.setEnabled(False)
            self.ui.button_run_query.setText("Wait...")
            self.showMessage("Terminating query...")
            try:
                self.Session.Corpus.resource.DB.kill_connection()
            except (AttributeError, sqlwrap.mysql.err):
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
        # Lazily close an existing database connection:
        try:
            self.Session.Corpus.resource.DB.close()
        except AttributeError as e:
            pass
        self.showMessage("Preparing query...")
        try:
            if self.ui.radio_query_string.isChecked():
                options.cfg.query_list = options.cfg.query_list[0].splitlines()
                self.Session = SessionCommandLine()
            else:
                if not self.verify_file_name():
                    QtGui.QMessageBox.critical(self, "Invalid file name – Coquery", msg_filename_error, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return
                self.Session = SessionInputFile()
        except SQLNoConfigurationError:
            QtGui.QMessageBox.critical(self, "Database configuration error – Coquery", msg_sql_no_configuration, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except SQLInitializationError as e:
            QtGui.QMessageBox.critical(self, "Database initialization error – Coquery", msg_initialization_error.format(code=e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except CollocationNoContextError as e:
            QtGui.QMessageBox.critical(self, "Collocation error – Coquery", str(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except RuntimeError as e:
            error_box.ErrorBox.show(sys.exc_info(), no_trace=True)
        except Exception as e:
            error_box.ErrorBox.show(sys.exc_info(), e)
        else:
            self.set_stop_button()
            self.showMessage("Running query...")
            self.start_progress_indicator()
            self.query_thread = QtProgress.ProgressThread(self.Session.run_queries, self)
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
        self.Session = StatisticsSession()
        self.showMessage("Gathering corpus statistics...")
        self.start_progress_indicator()
        self.query_thread = QtProgress.ProgressThread(self.Session.run_queries, self)
        self.query_thread.taskFinished.connect(self.finalize_query)
        self.query_thread.taskException.connect(self.exception_during_query)
        self.query_thread.start()

    def visualize_data(self, module, **kwargs):
        try:
            import visualizer
        except RuntimeError:
            QtGui.QMessageBox.critical(
                self, "Missing Python module – Coquery",
                msg_missing_seaborn_module)
        try:
            module = importlib.import_module(module)
        except Exception as e:
            msg = "<code style='color: darkred'>{type}: {code}</code>".format(
                type=type(e).__name__, code=sys.exc_info()[1])
            logger.error(msg)
            QtGui.QMessageBox.critical(
                self, "Visualization error – Coquery",
                VisualizationModuleError(module, msg).error_message)
        else:
            try:
                if "Session" not in dir(self):
                    raise VisualizationNoDataError
                else:
                    dialog = visualizer.VisualizerDialog()
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
                error_box.ErrorBox.show(sys.exc_info())
        
    def save_configuration(self):
        self.getGuiValues()
        options.save_configuration()

    def open_corpus_help(self):
        if self.ui.combo_corpus.isEnabled():
            current_corpus = str(self.ui.combo_corpus.currentText())
            resource, _, _, module = options.get_available_resources(options.cfg.current_server)[current_corpus]
            try:
                url = resource.url
            except AttributeError:
                QtGui.QMessageBox.critical(None, "Documentation error – Coquery", msg_corpus_no_documentation.format(corpus=current_corpus), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            else:
                import webbrowser
                webbrowser.open(url)
        
    def remove_corpus(self, corpus_name):
        resource, _, _, module = options.get_available_resources(options.cfg.current_server)[corpus_name.lower()]
        database = resource.db_name
        db_con = options.cfg.server_configuration[options.cfg.current_server]
        try:
            size = FileSize(sqlwrap.SqlDB(
                db_con["host"], db_con["port"], 
                db_con["user"], db_con["password"]).get_database_size(database))
        except  TypeError:
            size = FileSize(-1)
        response = QtGui.QMessageBox.warning(
            self, "Remove corpus", msg_corpus_remove.format(corpus=corpus_name, size=size), QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        
        if response == QtGui.QMessageBox.Yes:
            try:
                self.Session.Corpus.resource.DB.close()
            except AttributeError as e:
                pass
            DB = sqlwrap.SqlDB(
                db_con["host"], db_con["port"], db_con["user"], db_con["password"])
            self.start_progress_indicator()
            try:
                DB.execute("DROP DATABASE {}".format(database))
            except (sqlwrap.mysql.InternalError, sqlwrap.mysql.OperationalError) as e:
                QtGui.QMessageBox.critical(self, "Database error – Coquery", msg_remove_corpus_error.format(code=e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            finally:
                DB.close()
            try:
                os.remove(module)
            except IOError:
                QtGui.QMessageBox.critical(self, "Storage error – Coquery", msg_remove_corpus_disk_error, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            self.stop_progress_indicator()
            self.fill_combo_corpus()
            logger.warning("Removed corpus {}.".format(corpus_name))
            self.showMessage("Removed corpus {}.".format(corpus_name))

            self.change_corpus()
            try:
                self.corpus_manager.close()
            except AttributeError:
                pass
            self.corpus_manager = None

    def build_corpus(self):
        import coq_install_generic
        import corpusbuilder
        corpusbuilder.BuilderGui(coq_install_generic.GenericCorpusBuilder, parent=self)
        self.fill_combo_corpus()
        self.change_corpus()
        try:
            self.corpus_manager.close()
        except AttributeError:
            pass
        self.corpus_manager = None
            
    def install_corpus(self, builder_class):
        import corpusbuilder
        builder = corpusbuilder.InstallerGui(builder_class, self)
        try:
            result = builder.display()
        except Exception as e:
            error_box.ErrorBox.show(sys.exc_info())
        if result:
            self.fill_combo_corpus()
            self.change_corpus()
            try:
                self.corpus_manager.close()
            except AttributeError:
                pass
            self.corpus_manager = None
            
    def manage_corpus(self):
        import corpusmanager
        
        path = os.path.join(sys.path[0], "installer")
        
        if self.corpus_manager:
            self.corpus_manager.raise_()
            self.corpus_manager.activateWindow()
        else:
            self.corpus_manager = corpusmanager.CorpusManager(parent=self)        
            self.corpus_manager.show()
            self.corpus_manager.read(path)
            self.corpus_manager.installCorpus.connect(self.install_corpus)
            self.corpus_manager.removeCorpus.connect(self.remove_corpus)
            result = self.corpus_manager.exec_()
            try:
                self.corpus_manager.close()
            except AttributeError:
                pass
            self.corpus_manager = None
            
    def shutdown(self):
        """ Shut down the application by removing all open widgets and saving
        the configuration. """
        for x in self.widget_list:
            try:
                x.close()
            except:
                pass
            del x
        self.save_configuration()
            
    def closeEvent(self, event):
        if not self.last_results_saved and options.cfg.ask_on_quit:
            response = QtGui.QMessageBox.warning(self, "Unsaved results", msg_unsaved_data, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if response == QtGui.QMessageBox.Yes:
                self.shutdown()
                event.accept()
            else:
                event.ignore()            
        else:
            self.shutdown()
            event.accept()
        
    def settings(self):
        import settings
        settings.Settings.manage(options.cfg, self)

    def change_current_server(self):
        name = self.ui.combo_config.currentText()
        if name:
            name = str(name)
            self.ui.combo_config.currentIndexChanged.disconnect(self.change_current_server)
            self.change_mysql_configuration(name)
            self.ui.combo_config.currentIndexChanged.connect(self.change_current_server)

    def change_mysql_configuration(self, name):
        self.ui.combo_config.clear()
        self.ui.combo_config.addItems(sorted(options.cfg.server_configuration))
        if name:
            options.cfg.current_server = str(name)
            index = self.ui.combo_config.findText(name)
            self.ui.combo_config.setCurrentIndex(index)
            db_con = options.cfg.server_configuration[name]
            self.test_mysql_connection()
        else:
            options.cfg.current_server = None
        
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
        if options.cfg.current_server == None:
            state = False
        else:
            db_con = options.cfg.server_configuration[options.cfg.current_server]
            state = bool(sqlwrap.SqlDB.test_connection(
                db_con["host"], db_con["port"], 
                db_con["user"], db_con["password"]))

        # Choose a suitable icon:
        if state:
            icon = QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_DialogYesButton)
        else:
            icon = QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_DialogNoButton)

        index = self.ui.combo_config.findText(options.cfg.current_server)
            
        # add new entry with suitable icon, remove old icon and reset index:
        try:
            self.ui.combo_config.currentIndexChanged.disconnect()
        except TypeError:
            pass
        self.ui.combo_config.insertItem(index + 1, icon, options.cfg.current_server)
        self.ui.combo_config.setCurrentIndex(index + 1)
        self.ui.combo_config.removeItem(index)
        self.ui.combo_config.setCurrentIndex(index)
        self.last_connection_state = state
        self.last_index = index
        self.ui.combo_config.currentIndexChanged.connect(self.change_current_server)

        if state:
            self.fill_combo_corpus()
            self.ui.centralwidget.setEnabled(True)
        else:
            self.ui.centralwidget.setEnabled(False)
        
        return state

    def mysql_settings(self):
        import MySQLOptions
        try:
            config_dict, name = MySQLOptions.MySQLOptions.choose(options.cfg.current_server, options.cfg.server_configuration)
        except TypeError:
            return
        else:
            options.cfg.server_configuration = config_dict
            self.change_mysql_configuration(name)

    def show_mysql_guide(self):
        import mysql_guide
        mysql_guide.MySqlGuide.display()

    def getGuiValues(self):
        """ Set the values in options.cfg.* depending on the current values
        in the GUI. """
        
        def traverse_output_columns(node):
            output_features = []
            for child in [node.child(i) for i in range(node.childCount())]:
                output_features += traverse_output_columns(child)
            if node.checkState(0) == QtCore.Qt.Checked and not node.objectName().rpartition("_")[-1] == "table" and not node.isDisabled():
                output_features.append(node.objectName())
            return output_features
        
        def get_external_links(node):
            output_features = {}
            for child in [node.child(i) for i in range(node.childCount())]:
                output_features.update(get_external_links(child))
            if node.checkState(0) == QtCore.Qt.Checked:
                if node.parent() and node.parent()._link_by:
                    link_name = node.objectName().rpartition("func.")[-1]
                    output_features.update({
                        link_name: (
                            "{}.{}".format(node.parent().objectName(),
                            node.parent()._link_by[1]),
                            node.parent()._link_by[0])})

                    #output_features[link_name].append(
                        #("{}.{}".format(node.parent().objectName(),
                        #node.parent()._link_by[1]),
                        #node.parent()._link_by[0]))
            return output_features

        def get_functions(node):
            functions = []
            for child in [node.child(i) for i in range(node.childCount())]:
                functions += get_functions(child)
            if node.checkState(0) == QtCore.Qt.Checked and node._func:
                functions.append((node.objectName(), node._func, str(node.text(0))))
            return functions 

        if options.cfg:
            options.cfg.corpus = str(self.ui.combo_corpus.currentText()).lower()
        
            # determine query mode:
            if self.ui.radio_aggregate_uniques.isChecked():
                options.cfg.MODE = QUERY_MODE_DISTINCT
            if self.ui.radio_aggregate_none.isChecked():
                options.cfg.MODE = QUERY_MODE_TOKENS
            if self.ui.radio_aggregate_frequencies.isChecked():
                options.cfg.MODE = QUERY_MODE_FREQUENCIES
            if self.ui.radio_aggregate_collocations.isChecked():
                options.cfg.MODE = QUERY_MODE_COLLOCATIONS
            try:
                if self.ui.radio_mode_statistics.isChecked():
                    options.cfg.MODE = QUERY_MODE_STATISTICS
            except AttributeError:
                pass
                
            # determine context mode:
            if self.ui.radio_context_mode_kwic.isChecked():
                options.cfg.context_mode = CONTEXT_KWIC
            if self.ui.radio_context_mode_string.isChecked():
                options.cfg.context_mode  = CONTEXT_STRING
            if self.ui.radio_context_mode_columns.isChecked():
                options.cfg.context_mode  = CONTEXT_COLUMNS

            # either get the query input string or the query file name:
            if self.ui.radio_query_string.isChecked():
                if type(self.ui.edit_query_string) == QtGui.QLineEdit:
                    options.cfg.query_list = [str(self.ui.edit_query_string.text())]
                else:
                    options.cfg.query_list = [str(self.ui.edit_query_string.toPlainText())]
            options.cfg.input_path = str(self.ui.edit_file_name.text())

            # get context options:
            try:
                options.cfg.context_left = self.ui.context_left_span.value()
                options.cfg.context_right = self.ui.context_right_span.value()
                if self.ui.context_words_as_columns.checkState():
                    options.cfg.context_columns = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
                else:
                    options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            except AttributeError:
                if options.cfg.context_mode == CONTEXT_KWIC:
                    options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
                elif options.cfg.context_mode == CONTEXT_COLUMNS:
                   options.cfg.context_columns = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
                else:
                    options.cfg.context_span = max(self.ui.context_left_span.value(), self.ui.context_right_span.value())
            
            options.cfg.external_links = {}
            #options.cfg.external_links = defaultdict(list)
            for root in [self.ui.options_tree.topLevelItem(i) for i in range(self.ui.options_tree.topLevelItemCount())]:
                options.cfg.external_links.update(get_external_links(root))
            #print("External links:")
            #for x in options.cfg.external_links:
                #print(x, options.cfg.external_links[x])
            
            # Go throw options tree widget to get all checked output columns:
            options.cfg.selected_features = []
            for root in [self.ui.options_tree.topLevelItem(i) for i in range(self.ui.options_tree.topLevelItemCount())]:
                options.cfg.selected_features += traverse_output_columns(root)

            options.cfg.selected_functions = []
            for root in [self.ui.options_tree.topLevelItem(i) for i in range(self.ui.options_tree.topLevelItemCount())]:
                func = get_functions(root)
                options.cfg.selected_functions += func

            return True

    def show_log(self):
        import logfile
        logfile.LogfileViewer.view()

    def show_about(self):
        import aboutUi
        dialog = QtGui.QDialog(self)
        dialog.ui = aboutUi.Ui_AboutDialog()
        dialog.ui.setupUi(dialog)

        image = QtGui.QImage(self.logo)
        painter = QtGui.QPainter(image)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(image.rect(), QtCore.Qt.AlignBottom, "Version {}".format(__init__.__version__))
        painter.end()
        dialog.ui.label_pixmap.setPixmap(QtGui.QPixmap.fromImage(image))
        dialog.ui.label_pixmap.setAlignment(QtCore.Qt.AlignCenter)

        dialog.ui.label_description.setText(
            str(dialog.ui.label_description.text()).format(version=__init__.__version__, date=__init__.DATE))
        dialog.exec_()

    def setGUIDefaults(self):
        """ Set up the gui values based on the values in options.cfg.* """

        # set corpus combo box to current corpus:
        if options.cfg.corpus:
            index = self.ui.combo_corpus.findText(options.cfg.corpus.upper())
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

        self.ui.edit_file_name.setText(options.cfg.input_path)
        # either fill query string or query file input:
        if options.cfg.query_list:
            self.ui.edit_query_string.setText("\n".join(options.cfg.query_list))
            self.ui.radio_query_string.setChecked(True)
        if options.cfg.input_path_provided:
            self.ui.radio_query_file.setChecked(True)
            
        for rc_feature in options.cfg.selected_features:
            self.ui.options_tree.setCheckState(rc_feature, True)
        
        self.ui.context_left_span.setValue(options.cfg.context_left)
        self.ui.context_right_span.setValue(options.cfg.context_right)
        
        if options.cfg.context_mode == CONTEXT_STRING:
            self.ui.radio_context_mode_string.setChecked(True)
        elif options.cfg.context_mode == CONTEXT_COLUMNS:
            self.ui.radio_context_mode_column.setChecked(True)
        else:
            self.ui.radio_context_mode_kwic.setChecked(True)
            
        for filt in list(options.cfg.filter_list):
            self.ui.filter_box.addTag(filt)
            options.cfg.filter_list.remove(filt)
        
        # get table from last session, if possible:
        try:
            self.table_model.set_header(options.cfg.last_header)
            self.table_model.set_data(options.cfg.last_content)
            self.Session = options.cfg.last_session
            self.ui.data_preview.setModel(self.table_model)
        except AttributeError:
            pass
        
        self.toggle_frequency_columns()

    def select_table(self):
        """
        Open a table select widget.
        
        The table select widget contains a QTreeWidget with all corpora 
        except the currently active one as parents, and the respective tables
        as children.
        
        The return tuple contains the corpus and the table name. 
        
        Returns
        -------
        (corpus, table) : tuple
            The name of the corpus and the name of the table from that corpus
            as feature strings. 
        """
        
        
        corpus, table, feature = linkselect.LinkSelect.display(self)
        
        corpus = "bnc"
        table = "word"
        feature_name = "word_label"
        
        return (corpus, table, feature_name)

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
        import linkselect
        column = 0
        link = linkselect.LinkSelect.display(
            feature=str(item.text(0)),
            corpus_omit=str(self.ui.combo_corpus.currentText()).lower(),
            parent=self)
        
        if not link:
            return
        else:
            corpus, table_name, feature_name, case = link
            item.setExpanded(True)
            
            resource = options.get_available_resources(options.cfg.current_server)[corpus][0]
            table = resource.get_table_dict()[table_name]
            
            new_table = classes.CoqTreeLinkItem()
            new_table.setObjectName("{}.{}_table".format(corpus, table_name))
            
            position = self.ui.options_tree.indexOfTopLevelItem(item.parent()) +1
            self.ui.options_tree.insertTopLevelItem(position, new_table)
            new_table.setLink("{}.{}".format(item.parent().objectName(), item.objectName()), feature_name)
            new_table.setText(column, "{} ► {}.{}".format(str(item.text(0)), corpus.upper(), table_name))
            new_table.setCheckState(column, False)
            
            for rc_feature in table:
                if rc_feature.rpartition("_")[-1] not in ("id", "table") and rc_feature != feature_name:
                    new_item = classes.CoqTreeItem()
                    new_item.setText(0, resource.__getattribute__(resource, rc_feature))
                    new_item.setObjectName("{}.{}".format(corpus, rc_feature))
                    new_item.setCheckState(column, False)
                    new_table.addChild(new_item)
            
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

        import functionapply
        column = 0
        parent = item.parent()
        
        response  = functionapply.FunctionDialog.display(
            table=str(parent.text(0)),
            feature=str(item.text(0)), parent=self)
        
        if not response:
            return
        else:
            label, func = response
            
            child_func = classes.CoqTreeFuncItem()
            child_func.setObjectName("func.{}".format(item.objectName()))
            child_func.setFunction(func)
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
    
logger = logging.getLogger(__init__.NAME)

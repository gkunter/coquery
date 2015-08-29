# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

from session import *
from defines import *
from pyqt_compat import QtCore, QtGui
import __init__
import coqueryUi
import csvOptions
import QtProgress

import results 
import error_box
import codecs
import random
import logging
import sqlwrap
import MySQLOptions
import queries
import contextview
import os

from queryfilter import *

# so, pandas:
import pandas as pd

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
        
        if str(self._objectName).endswith("_root") and check_state:
            self.setExpanded(True)
        
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

    def setCheckState(self, object_name, state, column=0):
        """ Set the checkstate of the item that matches the object_name. If
        the state is Checked, also expand the parent of the item. """
        if type(state) != QtCore.Qt.CheckState:
            if state:
                state = QtCore.Qt.Checked
            else:
                state = QtCore.Qt.Unchecked
        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            if root.objectName() == object_name:
                root.setChecked(column, state)
                self.update(root, column)
            for child in [root.child(i) for i in range(root.childCount())]:
                if child.objectName() == object_name:
                    child.setCheckState(column, state)
                    if state == QtCore.Qt.Checked:
                        root.setExpanded(True)
                    self.update(child, column)
                    return
                
    def mimeData(self, *args):
        """ Add the resource variable name to the MIME data (for drag and 
        drop). """
        value = super(CoqTreeWidget, self).mimeData(*args)
        value.setText(", ".join([x.objectName() for x in args[0]]))
        return value
    
    def get_checked(self, column = 0):
        check_list = []
        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            for child in [root.child(i) for i in range(root.childCount())]:
                if child.checkState(column) == QtCore.Qt.Checked:
                    check_list.append(str(child._objectName))
        return check_list
        

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

class CoqTextEdit(QtGui.QTextEdit):
    def __init__(self, *args):
        super(CoqTextEdit, self).__init__(*args)
        self.setAcceptDrops(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dragMoveEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        # get the relative position from the mime data
        mime = e.mimeData().text()
        
        if "application/x-qabstractitemmodeldatalist" in e.mimeData().formats():
            label = e.mimeData().text()
            if label == "word_label":
                self.insertPlainText("*")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "word_pos":
                self.insertPlainText(".[*]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "lemma_label":
                self.insertPlainText("[*]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "lemma_transcript":
                self.insertPlainText("[/*/]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "word_transcript":
                self.insertPlainText("/*/")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
        elif e.mimeData().hasText():
            self.insertPlainText(e.mimeData().text())
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
        #x, y = map(int, mime.split(','))

        #if e.keyboardModifiers() & QtCore.Qt.ShiftModifier:
            ## copy
            ## so create a new button
            #button = Button('Button', self)
            ## move it to the position adjusted with the cursor position at drag
            #button.move(e.pos()-QtCore.QPoint(x, y))
            ## show it
            #button.show()
            ## store it
            #self.buttons.append(button)
            ## set the drop action as Copy
            #e.setDropAction(QtCore.Qt.CopyAction)
        #else:
            ## move
            ## so move the dragged button (i.e. event.source())
            #e.source().move(e.pos()-QtCore.QPoint(x, y))
            ## set the drop action as Move
            #e.setDropAction(QtCore.Qt.MoveAction)
        # tell the QDrag we accepted it
        e.accept()

    def setAcceptDrops(self, *args):
        super(CoqTextEdit, self).setAcceptDrops(*args)
        
class GuiHandler(logging.StreamHandler):
    def __init__(self, *args):
        super(GuiHandler, self).__init__(*args)
        self.log_data = []
        self.app = None
        
    def setGui(self, app):
        self.app = app
        
    def emit(self, record):
        self.log_data.append(record)
        self.app.log_table.dataChanged.emit(
            self.app.log_table.index(len(self.log_data), 0),
            self.app.log_table.index(len(self.log_data), 3))
        if len(self.log_data) == 1:
            self.app.ui.log_table.horizontalHeader().setStretchLastSection(True)
        self.app.log_table.layoutChanged.emit()

class QueryFilterBox(CoqTagBox):
    def destroyTag(self, tag):
        """ Remove the tag from the tag cloud as well as the filter from 
        the global filter list. """
        options.cfg.filter_list = [x for x in options.cfg.filter_list if x.text != str(tag.text())]
        super(QueryFilterBox, self).destroyTag(tag)
    
    def addTag(self, *args):
        """ Add the tag to the tag cloud and the global filter list. """
        filt = queries.QueryFilter()
        try:
            filt.resource = self.resource
        except AttributeError:
            return
        try:
            if args:
                filt.text = args[0]
            else:
                filt.text = str(self.edit_tag.text())
        except InvalidFilterError:
            self.edit_tag.setStyleSheet('CoqTagEdit { border-radius: 5px; font: condensed;background-color: rgb(255, 255, 192); }')
        else:
            super(QueryFilterBox, self).addTag(filt.text)
            options.cfg.filter_list.append(filt)

#class CoqFileSystemModel(QtGui.QFileSystemModel):
    #def lessThan(self, left, right):
        #print(123)
        #return self.data(left, QtCore.Qt.DisplayRole) < self.data(right, QtCore.Qt.DisplayRole)
    
    #def sort(self, *args):
        #print("sort")
        #super(CoqFileSystemModel, self).sort(*args)
    
    #def data(self, index, role):
        #if role == QtCore.Qt.DisplayRole and index.column() == 0:
            #file_name = self.filePath(index)
            #if self.isDir(index):
                #return super(CoqFileSystemModel, self).data(index, role) + QtCore.QDir.separator()
            #else:
                #return super(CoqFileSystemModel, self).data(index, role).upper()

        #return super(CoqFileSystemModel, self).data(index, role)

class CoqueryApp(QtGui.QMainWindow):
    """ Coquery as standalone application. """
    
    def setup_menu_actions(self):
        """ Connect menu actions to their methods."""
        self.ui.action_save_results.triggered.connect(self.save_results)
        self.ui.action_quit.triggered.connect(self.close)
        self.ui.action_build_corpus.triggered.connect(self.build_corpus)
        self.ui.action_remove_corpus.triggered.connect(self.remove_corpus)
        self.ui.action_mySQL_settings.triggered.connect(self.mysql_settings)
        self.ui.action_statistics.triggered.connect(self.run_statistics)
        self.ui.action_corpus_documentation.triggered.connect(self.open_corpus_help)
        
        self.ui.action_tree_map.triggered.connect(self.show_tree_map)
        self.ui.action_barcode_plot.triggered.connect(self.show_barcode_plot)
        self.ui.action_beeswarm_plot.triggered.connect(self.show_beeswarm_plot)
        self.ui.action_heat_map.triggered.connect(self.show_heatmap_plot)
        self.ui.action_barchart_plot.triggered.connect(self.show_barchart_plot)
        
        self.ui.action_percentage_area_plot.triggered.connect(
            lambda: self.show_time_series_plot(area=True, percentage=True))
        self.ui.action_stacked_area_plot.triggered.connect(
            lambda: self.show_time_series_plot(area=True, percentage=False))
        self.ui.action_line_plot.triggered.connect(
            lambda: self.show_time_series_plot(area=False, percentage=False))
    
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
        
    def setup_app(self):
        """ Initialize all widgets with suitable data """

        self.create_output_options_tree()
        
        QtGui.QWidget().setLayout(self.ui.tag_cloud.layout())
        self.ui.cloud_flow = FlowLayout(self.ui.tag_cloud, spacing = 1)

        # add available resources to corpus dropdown box:
        corpora = [x.upper() for x in sorted(resource_list.get_available_resources().keys())]

        self.ui.combo_corpus.addItems(corpora)
        
        # chamge the default query string edit to the sublassed edit class:
        self.ui.gridLayout_2.removeWidget(self.ui.edit_query_string)
        self.ui.edit_query_string.close()        
        edit_query_string = CoqTextEdit(self)
        edit_query_string.setObjectName(coqueryUi._fromUtf8("edit_query_string"))
        self.ui.gridLayout_2.addWidget(edit_query_string, 2, 1, 1, 1)
        self.ui.edit_query_string = edit_query_string
        
        self.ui.filter_box = QueryFilterBox(self)
        
        
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

        self.stop_progress_indicator()

        self.setup_hooks()
        self.setup_menu_actions()
        
        self.change_corpus()
        
        self.log_table = LogTableModel(self)
        self.log_proxy = LogProxyModel()
        self.log_proxy.setSourceModel(self.log_table)
        self.log_proxy.sortCaseSensitivity = False
        self.ui.log_table.setModel(self.log_proxy)

        self.table_model = results.CoqTableModel(self)
        self.table_model.dataChanged.connect(self.table_model.sort)
        header = self.ui.data_preview.horizontalHeader()
        header.sectionResized.connect(self.result_column_resize)
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_header_menu)

        self.ui.data_preview.setStyleSheet('::item:hover { color: blue; text-decoration: underline }')
        self.ui.data_preview.clicked.connect(self.result_cell_clicked)
        self.ui.data_preview.horizontalHeader().setMovable(True)
        self.ui.data_preview.setSortingEnabled(False)
    
    def result_column_resize(self, index, old, new):
        header = self.table_model.content.columns[index].lower()
        options.cfg.column_width[header] = new

    def result_cell_clicked(self, index):
        model_index = index
        row = model_index.row()
        data = self.table_model.content.iloc[row]
        token_id = data["coquery_invisible_corpus_id"]
        origin_id = data["coquery_invisible_origin_id"]
        token_width = data["coquery_invisible_number_of_tokens"]
        contextview.ContextView.display(self.Session.Corpus, token_id, origin_id, token_width, self)

    def verify_file_name(self):
        file_name = self.ui.edit_file_name.text()
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
        tree = CoqTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setRootIsDecorated(True)
        self.ui.options_list.removeWidget(tree)
        self.ui.options_tree.close()
        self.ui.options_list.addWidget(tree)
        self.ui.options_tree = tree
        return tree
    
    def change_corpus(self):
        """ Change the output options list depending on the features available
        in the current corpus. If no corpus is avaiable, disable the options
        area and some menu entries. If any corpus is available, these widgets
        are enabled again."""
        if not resource_list.get_available_resources():
            self.disable_corpus_widgets()
        else:
            self.enable_corpus_widgets()
            try:
                self.msg_box_no_corpus.close()
            except AttributeError:
                pass

        if self.ui.combo_corpus.count():
            corpus_name = str(self.ui.combo_corpus.currentText()).lower()
            self.resource, self.corpus, self.lexicon, self.path = resource_list.get_available_resources()[corpus_name]
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
            root = CoqTreeItem()
            root.setFlags(root.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable)
            root.setText(0, table.capitalize())
            root.setObjectName(coqueryUi._fromUtf8("{}_root".format(table)))
            root.setCheckState(0, QtCore.Qt.Unchecked)
            if table_dict[table]:
                tree.addTopLevelItem(root)
            
            # add a leaf for each table variable:
            for var in table_dict[table]:
                leaf = CoqTreeItem()
                root.addChild(leaf)
                label = type(self.resource).__getattribute__(self.resource, var).capitalize()
                leaf.setText(0, label)
                leaf.setObjectName(coqueryUi._fromUtf8(var))
                if var in last_checked: 
                    leaf.setCheckState(0, QtCore.Qt.Checked)
                else:
                    leaf.setCheckState(0, QtCore.Qt.Unchecked)
                leaf.update_checkboxes(0, expand=True)
                
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
        msg_no_corpus = "Coquery could not find a corpus module. Without a corpus module, you cannot run any query."
        msg_details = """<p>To build a new corpus module from a selection of text files, select <b>Build corpus...</b> from the Corpus menu.</p>
            <p>To install the corpus module for one of the corpora that are
            supported by Coquery, select <b>Install corpus...</b> from the Corpus menu.</p>"""
        self.msg_box_no_corpus = QtGui.QMessageBox(self)
        self.msg_box_no_corpus.setWindowTitle("No corpus available – Coquery")
        self.msg_box_no_corpus.setText(msg_no_corpus)
        self.msg_box_no_corpus.setInformativeText(msg_details)
        self.msg_box_no_corpus.setStandardButtons(QtGui.QMessageBox.Ok)
        self.msg_box_no_corpus.setDefaultButton(QtGui.QMessageBox.Ok)
        self.msg_box_no_corpus.setWindowModality(QtCore.Qt.NonModal)
        self.msg_box_no_corpus.setIcon(QtGui.QMessageBox.Warning)
        self.msg_box_no_corpus.show()
        
    def __init__(self, parent=None):
        """ Initialize the main window. This sets up any widget that needs
        spetial care, and also sets up some special attributes that relate
        to the GUI, including default appearances of the columns."""
        QtGui.QMainWindow.__init__(self, parent)
        
        self.file_content = None

        self.ui = coqueryUi.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setup_app()
        self.csv_options = None
        self.query_thread = None
        self.last_results_saved = True
        
        self.widget_list = []
        
        # the dictionaries column_width and column_color store default
        # attributes of the columns by display name. This means that problems
        # may arise if several columns have the same name!
        # FIXME: Make sure that the columns are identified correctly.
        self.column_width = {}
        self.column_color = {}
        
        # A non-modal dialog is shown if no corpus resource is available.
        # The dialog contains some assistance on how to build a new corpus.
        if not resource_list.get_available_resources():
            self.show_no_corpus_message()
        
        options.cfg.main_window = self
        # Resize the window if a previous size is available
        try:
            if options.cfg.height and options.cfg.width:
                self.resize(options.cfg.width, options.cfg.height)
        except AttributeError:
            pass
        
    def display_results(self):
        self.table_model.set_data(self.Session.output_object)
        self.table_model.set_header()
        
        self.ui.data_preview.setModel(self.table_model)

        # set column widths:
        for i, column in enumerate(self.table_model.content.columns):
            if column.lower() in options.cfg.column_width:
                self.ui.data_preview.setColumnWidth(i, options.cfg.column_width[column.lower()])
        
        if self.table_model.rowCount():
            self.last_results_saved = False
            
        if options.cfg.memory_dump:
            memory_dump()

    def select_file(self):
        """ Call a file selector, and add file name to query file input. """
        name = QtGui.QFileDialog.getOpenFileName(directory="~")
        
        # getOpenFileName() returns different types in PyQt and PySide, fix:
        if type(name) == tuple:
            name = name[0]
        
        if name:
            self.ui.edit_file_name.setText(name)
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
    
    def save_results(self):
        name = QtGui.QFileDialog.getSaveFileName(directory="~")
        if type(name) == tuple:
            name = name[0]
        if name:
            try:
                columns = [x for x in self.table_model.content.columns if not x.startswith("coquery_invisible")]
                columns = [x for x in columns if options.cfg.column_visibility.get(x, True)]
                tab = self.table_model.content[columns]
                with codecs.open(name, "wt") as output_file:
                    writer = UnicodeWriter(output_file, delimiter=options.cfg.output_separator)
                    writer.writerow([options.cfg.main_window.Session.Corpus.resource.translate_header(x) for x in tab.columns])
                    for i in tab.index:
                        writer.writerow(tab.iloc[i])
            except IOError as e:
                QtGui.QMessageBox.critical(self, "Disk error", "An error occurred while accessing the disk storage. <b>The results have not been saved.</b>")
            except (UnicodeEncodeError, UnicodeDecodeError):
                QtGui.QMessageBox.critical(self, "Encoding error", "<p>Unfortunatenly, there was an error while encoding the characters in the results view. <b>The save file is probably incomplete.</b></p><p>At least one column contains special characters which could not be translated to a format that can be written to a file. You may try to work around this issue by reducing the number of output columns so that the offending character is not in the output anymore.</p><p>We apologize for this inconvenience. Please do not hesitate to contact the authors about it so that the problem may be fixed in a future version.</p>")
            else:
                self.last_results_saved = True
    
    def exception_during_query(self):
        error_box.ErrorBox.show(self.exc_info, self.exception)
        
    def start_progress_indicator(self):
        """ Show the progress indicator, and make it move. """
        self.ui.progress_bar.setRange(0, 0)
        self.ui.progress_bar.show()
        
    def stop_progress_indicator(self):
        """ Stop the progress indicator from moving, and hide it as well. """
        self.ui.progress_bar.setRange(0, 1)
        self.ui.progress_bar.hide()
        
    def finalize_query(self):
        self.query_thread = None
        self.ui.statusbar.showMessage("Preparing results table...")
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
        
        self.ui.statusbar.showMessage("Number of rows: {:<8}      Query duration: {:<10}".format(
            len(self.Session.output_object), duration_str))
        
    def show_header_menu(self, point ):
        header = self.ui.data_preview.horizontalHeader()
        header.customContextMenuRequested.disconnect(self.show_header_menu)
        column = header.logicalIndexAt(point.x())
        # show self.menu about the column
        self.menu = QtGui.QMenu("Column options", self)

        display_name = options.cfg.main_window.Session.Corpus.resource.translate_header(self.table_model.content.columns[column])
        action = QtGui.QWidgetAction(self)
        label = QtGui.QLabel("<b>{}</b>".format(display_name), self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        action.setDefaultWidget(label)
        self.menu.addAction(action)
        self.menu.addSeparator()

        if not options.cfg.column_visibility.get(
            self.table_model.content.columns[column].lower(), True):
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
            
            if self.table_model.content.columns[column].lower() in options.cfg.column_color:
                action = QtGui.QAction("&Reset color", self)
                action.triggered.connect(lambda: self.reset_color(column))
                self.menu.addAction(action)
    
            action = QtGui.QAction("&Change color...", self)
            action.triggered.connect(lambda: self.change_color(column))
            self.menu.addAction(action)
            self.menu.addSeparator()

            group = QtGui.QActionGroup(self, exclusive=True)
            action = group.addAction(QtGui.QAction("Do not sort", self, checkable=True))
            action.triggered.connect(lambda: self.change_sorting_order(column, results.SORT_NONE))
            if self.table_model.sort_state[column] == results.SORT_NONE:
                action.setChecked(True)
            self.menu.addAction(action)
            
            action = group.addAction(QtGui.QAction("&Ascending", self, checkable=True))
            action.triggered.connect(lambda: self.change_sorting_order(column, results.SORT_INC))
            if self.table_model.sort_state[column] == results.SORT_INC:
                action.setChecked(True)
            self.menu.addAction(action)
            action = group.addAction(QtGui.QAction("&Descending", self, checkable=True))
            action.triggered.connect(lambda: self.change_sorting_order(column, results.SORT_DEC))
            if self.table_model.sort_state[column] == results.SORT_DEC:
                action.setChecked(True)
            self.menu.addAction(action)
                                    
            
            probe_index = self.table_model.createIndex(0, column)
            probe_cell = probe_index.data()
            if type(probe_cell) in [unicode, str, QtCore.QString]:
                action = group.addAction(QtGui.QAction("&Ascending, reverse", self, checkable=True))
                action.triggered.connect(lambda: self.change_sorting_order(column, results.SORT_REV_INC))
                if self.table_model.sort_state[column] == results.SORT_REV_INC:
                    action.setChecked(True)

                self.menu.addAction(action)
                action = group.addAction(QtGui.QAction("&Descending, reverse", self, checkable=True))
                action.triggered.connect(lambda: self.change_sorting_order(column, results.SORT_REV_DEC))
                if self.table_model.sort_state[column] == results.SORT_REV_DEC:
                    action.setChecked(True)
                self.menu.addAction(action)
        
        self.menu.popup(header.mapToGlobal(point))
        header.customContextMenuRequested.connect(self.show_header_menu)


    def toggle_visibility(self, index):
        """ Show again a hidden column, or hide a visible column."""
        column = self.table_model.content.columns[index]
        options.cfg.column_visibility[column] = not options.cfg.column_visibility.get(column, True)
        self.ui.data_preview.horizontalHeader().geometriesChanged.emit()
        # Resort the data if this is a sorting column:
        if index in self.table_model.sort_columns:
            self.table_model.sort(0, QtCore.Qt.AscendingOrder)
        self.table_model.layoutChanged.emit()


    def reset_color(self, column):
        header = self.table_model.content.columns[column].lower()
        try:
            options.cfg.column_color.pop(header)
            self.table_model.layoutChanged.emit()
        except KeyError:
            pass

    def change_color(self, column):
        col = QtGui.QColorDialog.getColor()
        header = self.table_model.content.columns[column].lower()
        if col.isValid():
            options.cfg.column_color[header] = col.name()
            #self.table_model.layoutChanged.emit()
        
    def change_sorting_order(self, index, mode):
        self.menu.close()
        if not mode:
            try:
                self.table_model.sort_columns.remove(index)
            except IndexError:
                pass
        elif index not in self.table_model.sort_columns:
            self.table_model.sort_columns.append(index)
        self.table_model.sort_state[index] = mode
        self.table_model.sort(0, QtCore.Qt.AscendingOrder)
        
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
        msg_query_running = "<p>The last query has not finished yet. If you interrupt it, the results that have been retrieved so far will be discarded.</p><p>Do you really want to interrupt this query?</p>"
        response = QtGui.QMessageBox.warning(self, "Unfinished query", msg_query_running, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if response == QtGui.QMessageBox.Yes:
            logger.warning("Last query is incomplete.")
            self.ui.button_run_query.setEnabled(False)
            self.ui.button_run_query.setText("Wait...")
            self.ui.statusbar.showMessage("Terminating query...")
            try:
                self.Session.Corpus.resource.DB.kill_connection()
            except AttributeError:
                pass
            if self.query_thread:
                self.query_thread.terminate()
                self.query_thread.wait()
            self.ui.statusbar.showMessage("Last query interrupted.")
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
        self.ui.statusbar.showMessage("Preparing query...")
        try:
            if self.ui.radio_query_string.isChecked():
                options.cfg.query_list = options.cfg.query_list[0].splitlines()
                self.Session = SessionCommandLine()
            else:
                if not self.verify_file_name():
                    msg_filename_error = """<p><b>File name not valid.</b></p>
                    <p>You have chosen to read the query strings from a file, but
                    the query file name that you have entered is not valid. Please enter a
                    valid query file name, or select a file by pressing the Open
                    button.</p>"""
                    QtGui.QMessageBox.critical(self, "Invalid file name – Coquery", msg_filename_error, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return
                self.Session = SessionInputFile()
        except SQLInitializationError as e:
            msg_initialization_error = """<p>An error occurred while
            initializing the database:</p><p>{}</p>
            <p>Possible reasons include:
            <ul><li>The database server is not running.</li>
            <li>The host name or the server port are incorrect.</li>
            <li>The user name or password are incorrect, or the user has insufficient privileges.</li>
            <li>You are trying to access a local database on a remote server, or vice versa.</li>
            </ul></p>
            <p>Open <b>MySQL settings</b> in the Settings menu to check whether
            the connection to the database server is working, and if the settings are correct.</p>""".format(e)
            QtGui.QMessageBox.critical(self, "Database initialization error – Coquery", msg_initialization_error, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except Exception as e:
            error_box.ErrorBox.show(sys.exc_info())
        else:
            self.set_stop_button()
            self.ui.statusbar.showMessage("Running query...")
            self.start_progress_indicator()
            self.query_thread = QtProgress.ProgressThread(self.Session.run_queries, self)
            self.query_thread.taskFinished.connect(self.finalize_query)
            self.query_thread.taskException.connect(self.exception_during_query)
            self.query_thread.start()

    def run_statistics(self):
        self.getGuiValues()
        self.Session = StatisticsSession()
        self.ui.statusbar.showMessage("Gathering corpus statistics...")
        self.start_progress_indicator()
        self.query_thread = QtProgress.ProgressThread(self.Session.run_queries, self)
        self.query_thread.taskFinished.connect(self.query_finished)
        self.query_thread.taskException.connect(self.exception_during_query)
        self.query_thread.start()
        
    def show_tree_map(self):
        import visualizer
        import treemap
        if not self.table_model.content.empty:
            viz = visualizer.VisualizerDialog()
            viz.Plot(
                self.table_model, 
                self.ui.data_preview, 
                treemap.TreemapVisualizer, self)
        else:
            QtGui.QMessageBox.critical(None, "Visualization error – Coquery", msg_visualization_no_data, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def show_heatmap_plot(self):
        import visualizer
        import heatmap
        if not self.table_model.content.empty:
            viz = visualizer.VisualizerDialog()
            viz.Plot(
                self.table_model, 
                self.ui.data_preview, 
                heatmap.HeatmapVisualizer, self)
        else:
            QtGui.QMessageBox.critical(None, "Visualization error – Coquery", msg_visualization_no_data, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        
    def show_beeswarm_plot(self):
        import visualizer
        import beeswarmplot
        if not self.table_model.content.empty:
            viz = visualizer.VisualizerDialog()
            viz.Plot(
                self.table_model, 
                self.ui.data_preview, 
                beeswarmplot.BeeswarmVisualizer, self)
        else:
            QtGui.QMessageBox.critical(None, "Visualization error – Coquery", msg_visualization_no_data, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def show_barchart_plot(self):
        import visualizer
        import barplot
        if not self.table_model.content.empty:
            viz = visualizer.VisualizerDialog()
            viz.Plot(
                self.table_model, 
                self.ui.data_preview, 
                barplot.BarchartVisualizer, self)
        else:
            QtGui.QMessageBox.critical(None, "Visualization error – Coquery", msg_visualization_no_data, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def show_barcode_plot(self):
        import visualizer
        import barcodeplot
        if not self.table_model.content.empty:
            viz = visualizer.VisualizerDialog()
            viz.Plot(
                self.table_model, 
                self.ui.data_preview, 
                barcodeplot.BarcodeVisualizer, self)
        else:
            QtGui.QMessageBox.critical(None, "Visualization error – Coquery", msg_visualization_no_data, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def show_time_series_plot(self, area, percentage):
        import visualizer
        import time_series
        if not self.table_model.content.empty:
            viz = visualizer.VisualizerDialog()
            viz.Plot(
                self.table_model, 
                self.ui.data_preview, 
                time_series.TimeSeriesVisualizer, 
                self, area=area, percentage=percentage, 
                smooth=True)
        else:
            QtGui.QMessageBox.critical(None, "Visualization error – Coquery", msg_visualization_no_data, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def save_configuration(self):
        self.getGuiValues()
        options.save_configuration()

    def open_corpus_help(self):
        if self.ui.combo_corpus.isEnabled():
            current_corpus = str(self.ui.combo_corpus.currentText())
            resource, _, _, module = resource_list.get_available_resources()[current_corpus.lower()]
            try:
                url = resource.documentation_url
            except AttributeError:
                QtGui.QMessageBox.critical(None, "Documentation error – Coquery", msg_corpus_no_documentation, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            else:
                import webbrowser
                webbrowser.open(url)
        
    def remove_corpus(self):
        if self.ui.combo_corpus.isEnabled():
            current_corpus = str(self.ui.combo_corpus.currentText())
            resource, _, _, module = resource_list.get_available_resources()[current_corpus.lower()]
            database = resource.db_name
            try:
                size = FileSize(sqlwrap.SqlDB(options.cfg.db_host, options.cfg.db_port, options.cfg.db_user, options.cfg.db_password).get_database_size(database))
            except  TypeError:
                size = FileSize(-1)
            msg_corpus_remove = "<p><b>You have requested to remove the corpus '{0}'.</b></p><p>This step cannot be reverted. If you proceed, the corpus will not be available for further queries before you install it again.</p><p>Removing '{0}' will free approximately {1:.1S} of disk memory.</p><p><p>Do you really want to remove the corpus?</p>".format(current_corpus, size)
            
            response = QtGui.QMessageBox.warning(
                self, "Remove corpus", msg_corpus_remove, QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            
            if response == QtGui.QMessageBox.Yes:
                try:
                    self.Session.Corpus.resource.DB.close()
                except AttributeError as e:
                    pass
                DB = sqlwrap.SqlDB(Host=options.cfg.db_host, Port=options.cfg.db_port, User=options.cfg.db_user, Password=options.cfg.db_password)
                self.start_progress_indicator()
                try:
                    DB.execute("DROP DATABASE {}".format(database))
                except sqlwrap.mysql.OperationalError as e:
                    QtGui.QMessageBox.critical(self, "Database error – Coquery", "<p>There was an error while deleting the corpus databases:</p><p>{}</p>".format(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                finally:
                    DB.close()
                try:
                    os.remove(module)
                except IOError:
                    QtGui.QMessageBox.critical(self, "Storage error – Coquery", "<p>There was an error while deleting the corpus module.</p>", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                self.stop_progress_indicator()
                self.fill_combo_corpus()
                logger.warning("Removed corpus {}.".format(current_corpus))
        self.change_corpus()

    def build_corpus(self):
        sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../tools")))
        import coq_generic
        import corpusbuilder
        corpusbuilder.BuilderGui(coq_generic.GenericCorpusBuilder, self)
        self.fill_combo_corpus()
        self.change_corpus()
            
    def shutdown(self):
        """ Shut down the application by removing all open widgets and saving
        the configuration. """
        for x in self.widget_list:
            x.close()
        self.save_configuration()
            
            
    def closeEvent(self, event):
        if not self.last_results_saved:
            msg_query_running = "<p>The last query results have not been saved. If you quit now, they will be lost.</p><p>Do you really want to quit?</p>"
            response = QtGui.QMessageBox.warning(self, "Unsaved results", msg_query_running, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if response == QtGui.QMessageBox.Yes:
                self.shutdown()
                event.accept()
            else:
                event.ignore()            
        else:
            self.shutdown()
            event.accept()
        
    def mysql_settings(self):
        settings = MySQLOptions.MySQLOptions.set(
            options.cfg.db_host, 
            options.cfg.db_port,
            options.cfg.db_user,
            options.cfg.db_password)
        if settings:
            options.cfg.db_host = settings.db_host
            options.cfg.db_port = settings.db_port
            options.cfg.db_user = settings.db_user
            options.cfg.db_password = settings.db_password
        

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
            if self.ui.radio_mode_collocations.isChecked():
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
                    options.cfg.query_list = [unicode(self.ui.edit_query_string.text())]
                else:
                    options.cfg.query_list = [unicode(self.ui.edit_query_string.toPlainText())]
            elif self.ui.radio_query_file.isChecked():
                options.cfg.input_path = unicode(self.ui.edit_file_name.text())

            # retrieve the CSV options for the current input file:
            if self.csv_options:
                sep, col, head, skip = self.csv_options
                if sep == "{tab}":
                    sep = "\t"
                if sep == "{space}":
                    sep = " "
                options.cfg.input_separator = sep
                options.cfg.query_column_number = col
                options.cfg.file_has_headers = head
                options.cfg.skip_lines = skip

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
            options.cfg.selected_features = []
            
            # Go throw options tree widget to get all checked output columns:
            for root in [self.ui.options_tree.topLevelItem(i) for i in range(self.ui.options_tree.topLevelItemCount())]:
                for child in [root.child(i) for i in range(root.childCount())]:
                    if child.checkState(0) == QtCore.Qt.Checked:
                        options.cfg.selected_features.append(str(child.objectName()))
                        
                    table, _, variable = str(child.objectName()).partition("_")
                    
                    if table == "coquery":
                        if variable == "query_string":
                            options.cfg.show_query = bool(child.checkState(0))
                        if variable == "input_file":
                            options.cfg.show_input_file = bool(child.checkState(0))
                    if table == "word":
                        if variable == "label":
                            options.cfg.show_orth = bool(child.checkState(0))
                        if variable == "pos":
                            options.cfg.show_pos = bool(child.checkState(0))
                        if variable == "transcript":
                            options.cfg.show_phon = bool(child.checkState(0))
                    if table == "lemma":
                        if variable == "label":
                            options.cfg.show_lemma = bool(child.checkState(0))
                        if variable == "pos":
                            options.cfg.show_lemma_pos = bool(child.checkState(0))
                        if variable == "transcript":
                            options.cfg.show_lemma_phon = bool(child.checkState(0))
                    try:
                        if table == "source":
                            options.cfg.source_columns.append(str(child.objectName()))
                    except AttributeError:
                        pass
                    if table == "file":
                        if variable == "label":
                            options.cfg.show_filename = bool(child.checkState(0))
                    if table == "speaker":
                        options.cfg.show_speaker = options.cfg.show_speaker | child.checkState(0)
                    if table == "corpus":
                        if variable == "time":
                            options.cfg.show_time = bool(child.checkState(0))
            return True

    def setGUIDefaults(self):
        """ Set up the gui values based on the values in options.cfg.* """

        # set corpus combo box to current corpus:
        if options.cfg.corpus:
            index = self.ui.combo_corpus.findText(options.cfg.corpus.upper())
            if index > -1:
                self.ui.combo_corpus.setCurrentIndex(index)

        # set query mode:
        if options.cfg.MODE == QUERY_MODE_DISTINCT:
            self.ui.radio_mode_context.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            self.ui.radio_mode_frequency.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_TOKENS:
            self.ui.radio_mode_tokens.setChecked(True)
        elif options.cfg.MODE == QUERY_MODE_COLLOCATIONS:
            self.ui.radio_mode_collocations.setChecked(True)

        # either fill query string or query file input:
        if options.cfg.query_list:
            self.ui.radio_query_string.setChecked(True)
            self.ui.edit_query_string.setText(options.cfg.query_list[0])
        elif options.cfg.input_path:
            self.ui.radio_query_file.setChecked(True)
            self.ui.edit_file_name.setText(options.cfg.input_path)
            
        for rc_feature in options.cfg.selected_features:
            self.ui.options_tree.setCheckState(rc_feature, True)
        
        self.ui.context_left_span.setValue(options.cfg.context_left)
        self.ui.context_right_span.setValue(options.cfg.context_right)
        
        if options.cfg.context_mode == CONTEXT_STRING:
            self.ui.radio_context_mode_string.setChecked(True)
        if options.cfg.context_mode == CONTEXT_COLUMNS:
            self.ui.radio_context_mode_column.setChecked(True)
        else:
            self.ui.radio_context_mode_kwic.setChecked(True)
            
        self.csv_options = (options.cfg.input_separator, options.cfg.query_column_number, options.cfg.file_has_headers, options.cfg.skip_lines)
        
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
        return True

    
logger = logging.getLogger(__init__.NAME)

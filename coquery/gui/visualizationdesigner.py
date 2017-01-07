# -*- coding: utf-8 -*-
""" 
visualizationDesigner.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import importlib
import logging
import sys

from coquery import options
from coquery.defines import NAME
from coquery.errors import VisualizationModuleError
from coquery.functions import Freq
from coquery.unicode import utf8

from .pyqt_compat import QtGui, QtCore, get_toplevel_window, pyside

import matplotlib as mpl
import matplotlib.pyplot as plt
if pyside:
    mpl.use("Qt4Agg")
    mpl.rcParams["backend.qt4"] = "PySide"

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import seaborn as sns

from . import classes
from .ui.visualizationDesignerUi import Ui_VisualizationDesigner

app = get_toplevel_window()

visualizer_mapping = (
    ("Barcode plot", "Barcode_plot", "barcodeplot"),
    ("Beeswarm plot", "Beeswarm_plot", "beeswarmplot"),
    #("Barplot", "Barchart", "barplot"),
    #("Stacked bars", "Barchart_stacked", "barplot", "Stacked"),
    #("Percentage bars", "Barchart_percent", "barplot", "Percent"),
    #("Change over time (lines)", "Lines", "timeseries"),
    #("Change over time (stacked)", "Areas_stacked", "timeseries"),
    #("Change over time (percent)", "Areas_percent", "timeseries"),
    #("Heat map", "Heatmap", "heatmap"),
    #("Kernel density", "Normal Distribution Histogram", "densityplot"),
    #("Cumulative distribution", "Positive Dynamic", "densityplot"),
    #("Scatterplot", "Scatter Plot", "scatterplot"),
    )

class VisualizationDesigner(QtGui.QDialog):
    visualizers = {}

    def __init__(self, df, session, parent=None):
        super(VisualizationDesigner, self).__init__(parent)
        self.session = session
        self.df = df

        self.ui = Ui_VisualizationDesigner()
        self.ui.setupUi(self)
        self.finetune_ui()

        self.populate_figure_types()
        self.populate_variable_lists()
        self.check_figure_types()
        self.check_wrapping()
        self.check_layout()
        self.restore_settings()
        self.display_values()

        self.setup_connections()

    def finetune_ui(self):
        """
        Finetune the UI: set widths, set translators, set icons.
        """
        self.ui.list_figures.setDragEnabled(False)
        self.ui.list_figures.setDragDropMode(self.ui.list_figures.NoDragDrop)
        w = app.style().pixelMetric(QtGui.QStyle.PM_ScrollBarExtent)
        self.ui.list_figures.setMinimumWidth(180 + w)
        self.ui.list_figures.setMaximumWidth(180 + w)

        # add canvas layout:
        self.ui.layout_view = QtGui.QVBoxLayout()
        self.ui.layout_view.setMargin(0)
        self.ui.layout_view.setSpacing(0)
        self.ui.tab_view.setLayout(self.ui.layout_view)

        self.ui.button_data_x.setIcon(app.get_icon("X Coordinate"))
        self.ui.button_data_y.setIcon(app.get_icon("Y Coordinate"))
        self.ui.button_columns.setIcon(app.get_icon("Select Column"))
        self.ui.button_rows.setIcon(app.get_icon("Select Row"))

        self.ui.button_clear_x.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_y.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_columns.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_rows.setIcon(app.get_icon("Clear Symbol"))

    def populate_variable_lists(self):
        self.categorical = [col for col in self.df.columns
                       if self.df.dtypes[col] == object and not
                       col.startswith(("coquery_invisible"))]
        self.numerical = [col for col in self.df.columns
                     if self.df.dtypes[col] in (int, float) and not
                     col.startswith(("coquery_invisible"))]

        for col in self.categorical:
            new_item = classes.CoqListItem(self.session.translate_header(col))
            new_item.setData(QtCore.Qt.UserRole, col)
            self.ui.table_categorical.addItem(new_item)

        for col in self.numerical:
            new_item = classes.CoqListItem(self.session.translate_header(col))
            new_item.setData(QtCore.Qt.UserRole, col)
            self.ui.table_numerical.addItem(new_item)

        # add functions
        for func in [Freq]:
            new_item = classes.CoqListItem("{} (generated)".format(
                func.get_name()))
            new_item.setData(QtCore.Qt.UserRole,
                             "func_{}".format(func._name))
            new_item.setData(QtCore.Qt.FontRole,
                             QtGui.QFont(QtGui.QLabel().font().family(),
                                         italic=True))
            self.ui.table_numerical.addItem(new_item)

    def setup_canvas(self, figure):
        if hasattr(self, "canvas"):
            self.ui.layout_view.removeWidget(self.canvas)
            self.canvas.hide()
            del self.canvas
        if hasattr(self, "toolbar"):
            self.ui.layout_view.removeWidget(self.toolbar)
            self.toolbar.hide()
            del self.toolbar
        if hasattr(self, "preview_canvas"):
            self.ui.layout_preview.removeWidget(self.preview_canvas)
            self.preview_canvas.hide()
            del self.preview_canvas

        # figure canvas:
        self.canvas = FigureCanvas(figure)
        self.canvas.setParent(self)
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ui.layout_view.addWidget(self.toolbar)
        self.ui.layout_view.addWidget(self.canvas)

        # preview canvas:
        self.preview_canvas = FigureCanvas(figure)
        self.preview_canvas.setParent(self)
        self.preview_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                          QtGui.QSizePolicy.Expanding)
        self.preview_canvas.updateGeometry()
        self.ui.layout_preview.addWidget(self.preview_canvas)

    def setup_connections(self):
        """
        Connects the GUI signals to the appropriate slots.
        """
        # hook up figure validation:
        self.ui.tray_data_x.featureChanged.connect(self.check_figure_types)
        self.ui.tray_data_y.featureChanged.connect(self.check_figure_types)
        self.ui.tray_data_x.featureCleared.connect(self.check_figure_types)
        self.ui.tray_data_y.featureCleared.connect(self.check_figure_types)

        # hook up layout validation
        self.ui.tray_data_x.featureChanged.connect(self.check_layout)
        self.ui.tray_data_y.featureChanged.connect(self.check_layout)
        self.ui.tray_data_x.featureCleared.connect(self.check_layout)
        self.ui.tray_data_y.featureCleared.connect(self.check_layout)
        self.ui.tray_columns.featureChanged.connect(self.check_layout)
        self.ui.tray_rows.featureChanged.connect(self.check_layout)

        self.ui.tray_columns.featureChanged.connect(self.check_wrapping)
        self.ui.tray_columns.featureCleared.connect(self.check_wrapping)
        self.ui.tray_rows.featureChanged.connect(self.check_wrapping)
        self.ui.tray_rows.featureCleared.connect(self.check_wrapping)

        # hook up clear buttons:
        self.ui.button_clear_x.clicked.connect(
            lambda: self.ui.tray_data_x.clear())
        self.ui.button_clear_y.clicked.connect(
            lambda: self.ui.tray_data_y.clear())
        self.ui.button_clear_rows.clicked.connect(
            lambda: self.ui.tray_rows.clear())
        self.ui.button_clear_columns.clicked.connect(
            lambda: self.ui.tray_columns.clear())

        # hook up to plot_figure():
        self.ui.tray_data_x.featureChanged.connect(self.plot_figure)
        self.ui.tray_data_y.featureChanged.connect(self.plot_figure)
        self.ui.tray_data_x.featureCleared.connect(self.plot_figure)
        self.ui.tray_data_y.featureCleared.connect(self.plot_figure)

        self.ui.tray_columns.featureChanged.connect(self.plot_figure)
        self.ui.tray_columns.featureCleared.connect(self.plot_figure)
        self.ui.tray_rows.featureChanged.connect(self.plot_figure)
        self.ui.tray_rows.featureCleared.connect(self.plot_figure)

        self.ui.list_figures.currentItemChanged.connect(self.plot_figure)
        self.ui.check_wrap_layout.toggled.connect(self.plot_figure)

    def check_wrapping(self):
        columns = self.ui.tray_columns.data()
        rows = self.ui.tray_rows.data()
        if ((columns is None and rows is None) or
            (columns is not None and rows is not None)):
            self._last_wrap_state = self.ui.check_wrap_layout.isChecked()
            self.ui.check_wrap_layout.blockSignals(True)
            self.ui.check_wrap_layout.setChecked(False)
            self.ui.check_wrap_layout.blockSignals(False)
            self.ui.check_wrap_layout.setDisabled(True)

        else:
            self.ui.check_wrap_layout.setDisabled(False)
            if hasattr(self, "_last_wrap_state"):
                self.ui.check_wrap_layout.blockSignals(True)
                self.ui.check_wrap_layout.setChecked(self._last_wrap_state)
                self.ui.check_wrap_layout.blockSignals(False)
                del self._last_wrap_state

    def check_layout(self):
        if self.ui.tray_data_x.text() or self.ui.tray_data_y.text():
            self.ui.group_layout.setEnabled(True)
        else:
            self.ui.group_layout.setEnabled(False)
            if self.ui.tray_columns.text():
                self.ui.tray_columns.clear()
            if self.ui.tray_rows.text():
                self.ui.tray_rows.clear()

    def restore_settings(self):
        try:
            self.resize(options.settings.value("visualizationdesigner_size"))
        except TypeError:
            pass

        self.data_x = options.settings.value("visualizationdesinger_data_x", None)
        self.data_y = options.settings.value("visualizationdesinger_data_y", None)
        self.layout_columns = options.settings.value("visualizationdesinger_layout_columns", None)
        self.layout_rows = options.settings.value("visualizationdesinger_layout_rows", None)
        val = options.settings.value("visualizationdesinger_show_legend", False)
        self.show_legend = (val == "true")
        self.legend_columns = options.settings.value("visualizationdesinger_legend_columns", 1)

    def display_values(self):
        # set up Layout tab:

        # data x
        if self.data_x:
            label = self.session.translate_header(self.data_x)
        else:
            label = None
        #self.ui.receive_data_x.setText(label)

        # data y
        if self.data_y:
            label = self.session.translate_header(self.data_y)
        else:
            label = None
        #self.ui.receive_data_y.setText(label)

        # layout columns
        if self.layout_columns:
            label = self.session.translate_header(self.layout_columns)
        else:
            label = None
        #self.ui.receive_columns.setText(label)

        # layout rows
        if self.layout_rows:
            label = self.session.translate_header(self.layout_rows)
        else:
            label = None
        #self.ui.receive_rows.setText(label)

        self.ui.check_show_legend.setChecked(self.show_legend)
        self.ui.spin_columns.setValue(self.legend_columns)

    def populate_figure_types(self):
        for x in visualizer_mapping:
            if len(x) == 4:
                label, icon, module_name, vis_class = x
            else:
                label, icon, module_name = x
                vis_class = "Visualizer"

            item = QtGui.QListWidgetItem(label)
            try:
                item.setIcon(app.get_icon(icon, small_n_flat=False))
            except Exception as e:
                item.setIcon(app.get_icon(icon, size="64x64"))
            item.setSizeHint(QtCore.QSize(180,
                                          64 + 0 * QtGui.QLabel().sizeHint().height()))
            self.ui.list_figures.addItem(item)

            if label not in VisualizationDesigner.visualizers:
                module = get_visualizer_module(module_name)
                visualizer = getattr(module, vis_class)
                VisualizationDesigner.visualizers[label] = visualizer

    def check_figure_types(self):
        last_item = self.ui.list_figures.currentItem()
        current_item = None

        data_x = self.ui.tray_data_x.data()
        data_y = self.ui.tray_data_y.data()

        self.ui.list_figures.blockSignals(True)
        for i in range(self.ui.list_figures.count()):
            item = self.ui.list_figures.takeItem(i)
            visualizer = VisualizationDesigner.visualizers[item.text()]
            if visualizer.validate_data(data_x, data_y,
                                        self.df, self.session):
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEnabled)
                if item == last_item:
                    current_item = item
            else:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
            self.ui.list_figures.insertItem(i, item)
        if current_item:
            self.ui.list_figures.setCurrentItem(current_item)
        self.ui.list_figures.blockSignals(False)

    def plot_figure(self):
        figure_type = self.ui.list_figures.currentItem()
        if not figure_type:
            return

        visualizer = VisualizationDesigner.visualizers[figure_type.text()]

        self.columns = self.ui.tray_columns.data()
        self.rows = self.ui.tray_rows.data()
        self.data_x = self.ui.tray_data_x.data()
        if self.data_x:
            self.levels_x = list(self.df[self.data_x].unique())
        else:
            self.levels_x = []
        self.data_y = self.ui.tray_data_y.data()
        if self.data_y:
            self.levels_y = list(self.df[self.data_y].unique())
        else:
            self.levels_y = []

        col_wrap = None
        # check column wrapping
        if ((self.columns == self.rows) or
            self.ui.check_wrap_layout.isChecked()):
            if self.columns == self.rows:
                self.rows = None
            if self.rows and not self.columns:
                self.columns = self.rows
                self.rows = None
            if self.columns:
                col_wrap, _= visualizer.get_grid_layout(
                    len(self.df[self.columns].unique()))

        columns = [x for x in [self.data_x, self.data_y,
                               self.columns, self.rows] if x]
        columns.append("coquery_invisible_corpus_id")

        kwargs = {"data": self.df[columns],
                  "col": self.columns,
                  "row": self.rows,
                  "col_wrap": col_wrap,
                  "sharex": True,
                  "sharey": True}

        self.grid = visualizer.get_grid(**kwargs)

        self.grid = self.grid.map_dataframe(visualizer.plot_facet,
                                            x=self.data_x, y=self.data_y,
                                            levels_x=self.levels_x,
                                            levels_y=self.levels_y,
                                            session=self.session)
        self.setup_canvas(self.grid.fig)
        self.grid.fig.tight_layout()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def accept(self, *args):
        super(VisualizationDesigner, self).accept(*args)
        options.settings.setValue("visualizationdesigner_size", self.size())
        options.settings.setValue("visualizationdesinger_data_x", self.data_x)
        options.settings.setValue("visualizationdesinger_data_y", self.data_y)
        options.settings.setValue("visualizationdesinger_layout_columns", self.layout_columns)
        options.settings.setValue("visualizationdesinger_layout_rows", self.layout_rows)
        options.settings.setValue("visualizationdesinger_show_legend", self.show_legend)
        options.settings.setValue("visualizationdesinger_legend_columns", self.legend_columns)

    def exec_(self):
        result = super(VisualizationDesigner, self).exec_()
        if result == QtGui.QDialog.Accepted:
            return result
        else:
            return None


def get_visualizer_module(name):
    # try to import the specified visualization module:
    name = "coquery.visualizer.{}".format(name)
    try:
        return importlib.import_module(name)
    except Exception as e:
        msg = "<code style='color: darkred'>{type}: {code}</code>".format(
            type=type(e).__name__, code=sys.exc_info()[1])
        logger.error(msg)
        QtGui.QMessageBox.critical(
            None, "Visualization error – Coquery",
            VisualizationModuleError(name, msg).error_message)
        return

logger = logging.getLogger(NAME)

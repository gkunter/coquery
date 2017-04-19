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
from coquery.defines import NAME, ROW_NAMES
from coquery.errors import VisualizationModuleError
from coquery.functions import Freq
from coquery.unicode import utf8

from .pyqt_compat import QtWidgets, QtCore, get_toplevel_window, pyside

import matplotlib as mpl
mpl.use("Qt5Agg")
mpl.rcParams["backend"] = "Qt5Agg"
import matplotlib.pyplot as plt


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import seaborn as sns

from . import classes
from ..visualizer.visualizer import get_grid_layout
from .ui.visualizationDesignerUi import Ui_VisualizationDesigner

app = get_toplevel_window()

visualizer_mapping = (
    # Entry order: (Display name, icon name, module, class name)
    ("Beeswarm plot", "Beeswarm_plot", "beeswarmplot", "BeeswarmPlot"),
    ("Barcode plot", "Barcode_plot", "barcodeplot", "BarcodePlot"),
    ("Heatbar plot", "Barcode_plot", "barcodeplot", "HeatbarPlot"),
    ("Barplot", "Barchart", "barplot", "BarPlot"),
    ("Stacked bars", "Barchart_stacked", "barplot", "StackedBars"),
    ("Percentage bars", "Barchart_percent", "barplot", "PercentBars"),
    #("Change over time (lines)", "Lines", "timeseries"),
    #("Change over time (stacked)", "Areas_stacked", "timeseries"),
    #("Change over time (percent)", "Areas_percent", "timeseries"),
    #("Heat map", "Heatmap", "heatmap"),
    ("Box-Whisker plot", "Barchart", "boxplot", "BoxPlot"),
    ("Violin plot", "Normal Distribution Histogram", "boxplot", "ViolinPlot"),
    #("Kernel density", "Normal Distribution Histogram", "densityplot"),
    #("Cumulative distribution", "Positive Dynamic", "densityplot"),
    ("Scatterplot", "Scatter Plot", "scatterplot", "ScatterPlot"),
    ("Regression plot", "Scatter Plot", "scatterplot", "RegressionPlot"),
    )

class VisualizationDesigner(QtWidgets.QDialog):
    moduleLoaded = QtCore.Signal(str, str)
    allLoaded = QtCore.Signal()
    visualizers = {}

    def __init__(self, df, dtypes, session, parent=None):
        super(VisualizationDesigner, self).__init__(parent)
        self.session = session

        # discard special rows such as contingency total:
        self.df = df.loc[[x for x in df.index if x not in ROW_NAMES.values()]]

        self.dtypes = dtypes
        self.vis = None
        self._palette_name = "Paired"

        self.ui = Ui_VisualizationDesigner()
        self.ui.setupUi(self)

        self.populate_figure_types()
        self.populate_variable_lists()

        self.restore_settings()
        self.display_values()

        self.check_figure_types()
        self.check_wrapping()
        self.check_grid_layout()
        self.check_clear_buttons()
        self.check_orientation()
        self.finetune_ui()

        self.setup_connections()

    def finetune_ui(self):
        """
        Finetune the UI: set widths, set translators, set icons.
        """
        self.ui.label_dimensions.setText(
            utf8(self.ui.label_dimensions.text()).format(
                len(self.df),
                len(self.categorical) + len(self.numerical)))

        self.ui.list_figures.setDragEnabled(False)
        self.ui.list_figures.setDragDropMode(self.ui.list_figures.NoDragDrop)
        w = app.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        self.ui.list_figures.setMinimumWidth(180 + w)
        self.ui.list_figures.setMaximumWidth(180 + w)

        # add canvas layout:
        self.ui.layout_view = QtWidgets.QVBoxLayout()
        self.ui.layout_view.setContentsMargins(0, 0, 0, 0)
        self.ui.layout_view.setSpacing(0)
        self.ui.tab_view.setLayout(self.ui.layout_view)

        self.ui.button_columns.setIcon(app.get_icon("Select Column"))
        self.ui.button_rows.setIcon(app.get_icon("Select Row"))

        self.ui.button_clear_x.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_y.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_z.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_columns.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_rows.setIcon(app.get_icon("Clear Symbol"))

        self.resize_previews()

    def add_figure_type(self, label, icon):
        item = QtWidgets.QListWidgetItem(label)
        try:
            item.setIcon(app.get_icon(icon, small_n_flat=False))
        except Exception as e:
            item.setIcon(app.get_icon(icon, size="64x64"))
        item.setSizeHint(QtCore.QSize(180,
                                        64 + 0 * QtWidgets.QLabel().sizeHint().height()))
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
        self.ui.list_figures.addItem(item)

    def load_figure_types(self):
        for x in visualizer_mapping:
            if len(x) == 4:
                label, icon, module_name, vis_class = x
            else:
                label, icon, module_name = x
                vis_class = "Visualizer"

            if label not in VisualizationDesigner.visualizers:
                module = get_visualizer_module(module_name)
                visualizer = getattr(module, vis_class)
                VisualizationDesigner.visualizers[label] = visualizer
            self.moduleLoaded.emit(label, icon)
        self.allLoaded.emit()

    def populate_figure_types(self):
        self.moduleLoaded.connect(self.add_figure_type)
        self.allLoaded.connect(self.check_figure_types)
        self.figure_loader = QtCore.QThread(self)
        self.figure_loader.run = self.load_figure_types
        self.figure_loader.start()

    def populate_variable_lists(self):
        self.categorical = [col for col in self.df.columns
                       if self.dtypes[col] == object and not
                       col.startswith(("coquery_invisible"))]
        self.numerical = [col for col in self.df.columns
                     if self.dtypes[col] in (int, float) and not
                     col.startswith(("coquery_invisible"))]

        for col in self.categorical:
            new_item = classes.CoqListItem(self.session.translate_header(col))
            new_item.setData(QtCore.Qt.UserRole, col)
            self.ui.table_categorical.addItem(new_item)

        for col in self.numerical:
            new_item = classes.CoqListItem(self.session.translate_header(col))
            new_item.setData(QtCore.Qt.UserRole, col)
            self.ui.table_numerical.addItem(new_item)

        ## add functions
        #for func in [Freq]:
            #new_item = classes.CoqListItem("{} (generated)".format(
                #func.get_name()))
            #new_item.setData(QtCore.Qt.UserRole,
                             #"func_{}".format(func._name))
            #new_item.setData(QtCore.Qt.FontRole,
                             #QtWidgets.QFont(QtWidgets.QLabel().font().family(),
                                         #italic=True))
            #self.ui.table_numerical.addItem(new_item)

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
            self.ui.layout_preview_colors.removeWidget(self.preview_canvas2)
            self.preview_canvas2.hide()
            del self.preview_canvas2

        # figure canvas:
        self.canvas = FigureCanvas(figure)
        self.canvas.setParent(self)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ui.layout_view.addWidget(self.toolbar)
        self.ui.layout_view.addWidget(self.canvas)

        # preview canvases:
        self.preview_canvas = FigureCanvas(figure)
        self.preview_canvas.setParent(self)
        self.preview_canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                          QtWidgets.QSizePolicy.Expanding)
        self.preview_canvas.updateGeometry()
        self.ui.layout_preview.addWidget(self.preview_canvas)

        self.preview_canvas2 = FigureCanvas(figure)
        self.preview_canvas2.setParent(self)
        self.preview_canvas2.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                          QtWidgets.QSizePolicy.Expanding)
        self.preview_canvas2.updateGeometry()
        self.ui.layout_preview_colors.addWidget(self.preview_canvas2)

    def setup_connections(self):
        """
        Connects the GUI signals to the appropriate slots.
        """
        # Hook up palette combo boxes:
        self.ui.combo_qualitative.currentIndexChanged.connect(
            lambda x: self.change_palette(utf8(self.ui.combo_qualitative.currentText())))
        self.ui.combo_sequential.currentIndexChanged.connect(
            lambda x: self.change_palette(utf8(self.ui.combo_sequential.currentText())))
        self.ui.combo_diverging.currentIndexChanged.connect(
            lambda x: self.change_palette(utf8(self.ui.combo_diverging.currentText())))

        # Hook up clear buttons.
        self.ui.button_clear_x.clicked.connect(lambda: self.ui.tray_data_x.clear())
        self.ui.button_clear_y.clicked.connect(lambda: self.ui.tray_data_y.clear())
        self.ui.button_clear_z.clicked.connect(lambda: self.ui.tray_data_z.clear())
        self.ui.button_clear_rows.clicked.connect(lambda: self.ui.tray_rows.clear())
        self.ui.button_clear_columns.clicked.connect(lambda: self.ui.tray_columns.clear())

        # Hook up checks for figure type.
        # The list of available figure types can change if a data tray has
        # changed, either because a feature was placed in it or if the tray
        # was cleared.
        self.ui.tray_data_x.featureChanged.connect(self.check_figure_types)
        self.ui.tray_data_y.featureChanged.connect(self.check_figure_types)
        self.ui.tray_data_z.featureChanged.connect(self.check_figure_types)
        self.ui.tray_data_x.featureCleared.connect(self.check_figure_types)
        self.ui.tray_data_y.featureCleared.connect(self.check_figure_types)
        self.ui.tray_data_z.featureCleared.connect(self.check_figure_types)

        # Hook up checks for clear button enable state.
        # The enable state of clear buttons is checked if the feature in the
        # associated tray has changed or cleared.
        self.ui.tray_data_x.featureChanged.connect(self.check_clear_buttons)
        self.ui.tray_data_y.featureChanged.connect(self.check_clear_buttons)
        self.ui.tray_data_z.featureChanged.connect(self.check_clear_buttons)
        self.ui.tray_columns.featureChanged.connect(self.check_clear_buttons)
        self.ui.tray_rows.featureChanged.connect(self.check_clear_buttons)
        self.ui.tray_data_x.featureCleared.connect(self.check_clear_buttons)
        self.ui.tray_data_y.featureCleared.connect(self.check_clear_buttons)
        self.ui.tray_data_z.featureCleared.connect(self.check_clear_buttons)
        self.ui.tray_columns.featureCleared.connect(self.check_clear_buttons)
        self.ui.tray_rows.featureCleared.connect(self.check_clear_buttons)

        # Hook up checks for wrapping checkbox enable state.
        # The enable state of the wrapping checkbox is checked if there are
        # changes to the rows and columns tray.
        self.ui.tray_columns.featureCleared.connect(self.check_wrapping)
        self.ui.tray_columns.featureChanged.connect(self.check_wrapping)
        self.ui.tray_rows.featureCleared.connect(self.check_wrapping)
        self.ui.tray_rows.featureChanged.connect(self.check_wrapping)

        # Hook up checks for grid layout enable state.
        # The enable state of the grid layout box is checked if there are
        # changes to the data trays.
        self.ui.tray_data_x.featureChanged.connect(self.check_grid_layout)
        self.ui.tray_data_y.featureChanged.connect(self.check_grid_layout)
        self.ui.tray_data_z.featureChanged.connect(self.check_grid_layout)
        self.ui.tray_data_x.featureCleared.connect(self.check_grid_layout)
        self.ui.tray_data_y.featureCleared.connect(self.check_grid_layout)
        self.ui.tray_data_z.featureCleared.connect(self.check_grid_layout)

        # Hook up annotation changes:
        self.ui.edit_figure_title.textChanged.connect(self.add_annotations)
        self.ui.edit_x_label.textChanged.connect(self.add_annotations)
        self.ui.edit_y_label.textChanged.connect(self.add_annotations)

        # Hook up figure plotting.
        # The figure will be plot only upon _explicit_ user actions. User
        # actions are:

        # (1) placing a feature in a tray
        self.ui.tray_data_x.featureChanged.connect(self.plot_figure)
        self.ui.tray_data_y.featureChanged.connect(self.plot_figure)
        self.ui.tray_data_z.featureChanged.connect(self.plot_figure)
        self.ui.tray_columns.featureChanged.connect(self.plot_figure)
        self.ui.tray_rows.featureChanged.connect(self.plot_figure)

        # (2) clicking a clear button
        self.ui.button_clear_x.clicked.connect(self.plot_figure)
        self.ui.button_clear_y.clicked.connect(self.plot_figure)
        self.ui.button_clear_z.clicked.connect(self.plot_figure)
        self.ui.button_clear_rows.clicked.connect(self.plot_figure)
        self.ui.button_clear_columns.clicked.connect(self.plot_figure)

        # (3) changing the wrapping checkbox
        self.ui.check_wrap_layout.toggled.connect(self.plot_figure)

        # (4) selecting a different figure type
        self.ui.list_figures.currentItemChanged.connect(self.plot_figure)

        # (5) changing the orientation
        self.ui.radio_horizontal.toggled.connect(self.plot_figure)
        self.ui.radio_vertical.toggled.connect(self.plot_figure)

    def check_orientation(self):
        data_x = self.ui.tray_data_x.data()
        data_y = self.ui.tray_data_y.data()
        data_z = self.ui.tray_data_z.data()

        if data_x is None or data_y is None:
            self.ui.radio_horizontal.setDisabled(True)
            self.ui.radio_vertical.setDisabled(True)
        else:
            self.ui.radio_horizontal.setDisabled(False)
            self.ui.radio_vertical.setDisabled(False)

        if (not self.ui.radio_horizontal.isChecked() and
            not self.ui.radio_vertical.isChecked()):
            self.ui.radio_horizontal.blockSignals(True)
            self.ui.radio_horizontal.setChecked(True)
            self.ui.radio_horizontal.blockSignals(False)

    def check_wrapping(self):
        """
        Activate or deactivate the 'Wrap layout' checkbox. If the checkbox
        is deactivated, also clear the Columns and Rows trays.
        """
        columns = self.ui.tray_columns.data()
        rows = self.ui.tray_rows.data()
        if ((columns is None) or
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

    def check_clear_buttons(self):
        self.ui.button_clear_x.setEnabled(bool(self.ui.tray_data_x.text()))
        self.ui.button_clear_y.setEnabled(bool(self.ui.tray_data_y.text()))
        self.ui.button_clear_z.setEnabled(bool(self.ui.tray_data_z.text()))
        self.ui.button_clear_columns.setEnabled(bool(self.ui.tray_columns.text()))
        self.ui.button_clear_rows.setEnabled(bool(self.ui.tray_rows.text()))
        self.check_orientation()

    def check_grid_layout(self):
        if self.ui.tray_data_x.text() or self.ui.tray_data_y.text():
            self.ui.group_layout.setEnabled(True)
        else:
            self.ui.group_layout.setEnabled(False)
            if self.ui.tray_columns.text():
                self.ui.tray_columns.clear()
            if self.ui.tray_rows.text():
                self.ui.tray_rows.clear()
        self.check_orientation()

    def check_figure_types(self):
        last_item = self.ui.list_figures.currentItem()
        restored_position = None

        data_x = self.ui.tray_data_x.data()
        data_y = self.ui.tray_data_y.data()
        data_z = self.ui.tray_data_z.data()

        self.ui.list_figures.blockSignals(True)
        for i in range(self.ui.list_figures.count()):
            item = self.ui.list_figures.takeItem(i)
            visualizer = VisualizationDesigner.visualizers[item.text()]
            if visualizer.validate_data(data_x, data_y, data_z,
                                        self.df, self.session):
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEnabled)
                if last_item and item.text() == last_item.text():
                    restored_position = i
            else:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
            self.ui.list_figures.insertItem(i, item)
        if restored_position != None:
            self.ui.list_figures.setCurrentItem(
                self.ui.list_figures.item(restored_position))
        else:
            self.ui.list_figures.setCurrentItem(None)
        self.ui.list_figures.blockSignals(False)

    def change_palette(self, x):
        if x != self._palette_name:
            self._palette_name = x
            self.plot_figure()

    def resizeEvent(self, new):
        super(VisualizationDesigner, self).resizeEvent(new)
        self.resize_previews()

    def resize_previews(self):
        size = self.ui.group_preview.size()
        self.ui.group_preview_colors.setMinimumSize(size)
        self.ui.group_preview_colors.setMaximumSize(size)

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

    def get_gui_values(self):
        """
        """
        d = dict(
                data_x=self.ui.tray_data_x.data(),
                data_y=self.ui.tray_data_y.data(),
                data_z=self.ui.tray_data_z.data(),
                columns=self.ui.tray_columns.data(),
                rows=self.ui.tray_rows.data(),
                figure_type=self.ui.list_figures.currentItem(),
                figure_font=None,
                title=utf8(self.ui.edit_figure_title.text()),
                xlab=utf8(self.ui.edit_x_label.text()),
                ylab=utf8(self.ui.edit_y_label.text())
                )
        return d

    def plot_figure(self):
        values = self.get_gui_values()
        figure_type = values["figure_type"]
        if not figure_type:
            return

        columns = self.ui.tray_columns.data()
        rows = self.ui.tray_rows.data()
        data_x = self.ui.tray_data_x.data()
        data_y = self.ui.tray_data_y.data()
        data_z = self.ui.tray_data_z.data()
        if data_x:
           levels_x = sorted(list(self.df[data_x].dropna().unique()))
        else:
            levels_x = []
        if data_y:
            levels_y = sorted(list(self.df[data_y].dropna().unique()))
        else:
            levels_y = []
        if data_z:
            levels_z = sorted(list(self.df[data_z].dropna().unique()))
        else:
            levels_z = []

        if (self.ui.check_wrap_layout.isChecked()):
            col_wrap, _= get_grid_layout(len(self.df[columns].unique()))
        else:
            col_wrap = None

        df_columns = [x for x in [data_x, data_y, data_z, columns, rows] if x]
        df_columns.append("coquery_invisible_corpus_id")

        visualizer_class = VisualizationDesigner.visualizers[figure_type.text()]

        df = self.df[df_columns]
        df.columns = [self.session.translate_header(x) for x in df.columns]

        (data_x, data_y, data_z, columns, rows) = (
            self.session.translate_header(x) for x
            in (data_x, data_y, data_z, columns, rows))

        self.vis = visualizer_class(df, self.session)
        self.grid = self.vis.get_grid(col=columns, row=rows, col_wrap=col_wrap,
                                 sharex=True, sharey=True)

        self.grid = self.grid.map_dataframe(self.vis.plot_facet,
                                            x=data_x, y=data_y, z=data_z,
                                            levels_x=levels_x,
                                            levels_y=levels_y,
                                            levels_z=levels_z,
                                            session=self.session,
                                            palette=self._palette_name)
        self.add_annotations()
        self.setup_canvas(self.grid.fig)
        self.grid.fig.tight_layout()

    def add_annotations(self):
        if self.vis:
            values = self.get_gui_values()
            self.vis.set_annotations(self.grid, values)

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
        if result == QtWidgets.QDialog.Accepted:
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
        QtWidgets.QMessageBox.critical(
            None, "Visualization error – Coquery",
            VisualizationModuleError(name, msg).error_message)
        return

logger = logging.getLogger(NAME)

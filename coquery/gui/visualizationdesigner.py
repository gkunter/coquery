# -*- coding: utf-8 -*-
"""
visualizationDesigner.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import imp
import logging
import sys
import os

from coquery import options, NAME
from coquery.defines import ROW_NAMES
from coquery.errors import VisualizationModuleError
from coquery.unicode import utf8

from .pyqt_compat import QtWidgets, QtCore, QtGui, get_toplevel_window

import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT)
from matplotlib.backends.backend_qt5 import SubplotToolQt

import seaborn as sns

from . import classes
from ..visualizer.visualizer import get_grid_layout
from .ui.visualizationDesignerUi import Ui_VisualizationDesigner

mpl.use("Qt5Agg")
mpl.rcParams["backend"] = "Qt5Agg"

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
    ("Heat map", "Heatmap", "heatmap", "Heatmap"),
    ("Box-Whisker plot", "Boxplot", "boxplot", "BoxPlot"),
    ("Violin plot", "Violinplot", "boxplot", "ViolinPlot"),
    #("Kernel density", "Normal Distribution Histogram", "densityplot"),
    #("Cumulative distribution", "Positive Dynamic", "densityplot"),
    ("Scatterplot", "Scatterplot", "scatterplot", "ScatterPlot"),
    ("Regression plot", "Regressionplot", "scatterplot", "RegressionPlot"),
    )


class MyTool(SubplotToolQt):
    def __init__(self, *args, **kwargs):
        super(MyTool, self).__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.parent.keyPressEvent(event)
        else:
            super(MyTool, self).keyPressEvent(event)

    def functight(self):
        return super(MyTool, self).functight()

class NavigationToolbar(NavigationToolbar2QT):
    """
    See matplotlib/backends/backend_qt5.py for the implementation.
    """
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] not in ("Subplots", "Customize")]

    def __init__(self, canvas, parent, coordinates=True):
        super(NavigationToolbar, self).__init__(canvas, parent, coordinates)

        self._buttons = {}

        for x in self.children():
            if isinstance(x, QtWidgets.QToolButton):
                self._buttons[str(x.text())] = x

        self._buttons["Zoom"].toggled.connect(self.toggle_zoom)
        self._buttons["Pan"].toggled.connect(self.toggle_pan)

        self._zoom = False
        self._pan = False

    def toggle_zoom(self):
        self._zoom = not self._zoom

    def toggle_pan(self):
        self._pan = not self._pan

    def isPanning(self):
        return self._pan

    def isZooming(self):
        return self._zoom


class VisualizationDesigner(QtWidgets.QDialog):
    moduleLoaded = QtCore.Signal(str, str)
    allLoaded = QtCore.Signal()
    visualizers = {}

    def __init__(self, df, session, parent=None):
        super(VisualizationDesigner, self).__init__(parent)
        self.session = session

        # discard special rows such as contingency total:
        self.df = df.loc[[x for x in df.index
                          if x not in ROW_NAMES.values()]]

        self.vis = None
        for i, x in enumerate(df.columns):
            if self.df[x].dtype == bool:
                self.df[x] = self.df[x].astype(str)

        self.ui = Ui_VisualizationDesigner()
        self.ui.setupUi(self)

        # disable unsupported elements:
        self.ui.radio_custom.hide()
        self.ui.combo_custom.hide()
        self.ui.button_remove_custom.hide()
        self.ui.button_reverse_order.hide()
        self.ui.label_38.hide()
        self.ui.spin_number.hide()
        self.ui.label_37.hide()

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

        self.dialog = QtWidgets.QWidget()
        self.dialog_layout = QtWidgets.QVBoxLayout(self.dialog)
        self.dialog.resize(self.viewer_size)
        self.dialog.setWindowTitle("<no figure> – Coquery")
        self.dialog.setWindowIcon(app.get_icon(
            "coquerel_icon.png", small_n_flat=False))
        self.dialog.show()

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

        self.ui.button_columns.setIcon(app.get_icon("Select Column"))
        self.ui.button_rows.setIcon(app.get_icon("Select Row"))

        self.ui.button_clear_x.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_y.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_z.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_columns.setIcon(app.get_icon("Clear Symbol"))
        self.ui.button_clear_rows.setIcon(app.get_icon("Clear Symbol"))

    def add_figure_type(self, label, icon):
        item = QtWidgets.QListWidgetItem(label)
        try:
            item.setIcon(app.get_icon(icon, small_n_flat=False))
        except Exception as e:
            item.setIcon(app.get_icon(icon, size="64x64"))

        size = QtCore.QSize(
            180, 64 + 0 * QtWidgets.QLabel().sizeHint().height())

        item.setSizeHint(size)
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
                if module:
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
                            if self.df.dtypes[col] in (object, bool) and not
                            col.startswith(("coquery_invisible"))]
        self.numerical = [col for col in self.df.columns
                          if self.df.dtypes[col] in (int, float) and not
                          col.startswith(("coquery_invisible"))]

        for col in self.categorical:
            new_item = classes.CoqListItem(self.session.translate_header(col))
            new_item.setData(QtCore.Qt.UserRole, col)
            new_item.setToolTip(new_item.text())
            self.ui.table_categorical.addItem(new_item)

        for col in self.numerical:
            new_item = classes.CoqListItem(self.session.translate_header(col))
            new_item.setData(QtCore.Qt.UserRole, col)
            new_item.setToolTip(new_item.text())
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
            self.dialog_layout.removeWidget(self.canvas)
            self.canvas.hide()
            del self.canvas
        if hasattr(self, "toolbar"):
            self.dialog_layout.removeWidget(self.toolbar)
            self.toolbar.hide()
            del self.toolbar

        # figure canvas:
        self.canvas = FigureCanvas(figure)
        self.canvas.setParent(self)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.dialog_layout.addWidget(self.toolbar)
        self.dialog_layout.addWidget(self.canvas)

        try:
            _w = self.ui.layout_margins.takeAt(0)
            _w.widget().hide()
            self.ui.layout_margins.removeWidget(_w.widget())
            del _w
        except Exception as e:
            print(e)

        self.tool = MyTool(self.canvas.figure, self)
        self.tool.resetbutton.hide()
        self.tool.donebutton.hide()
        self.tool.tightlayout.setText("&Optimize margins")
        self.tool.show()
        self.ui.layout_margins.insertWidget(0, self.tool)

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
        self.ui.combo_qualitative.currentIndexChanged.connect(
            lambda: self.ui.radio_qualitative.setChecked(True))
        self.ui.combo_sequential.currentIndexChanged.connect(
            lambda: self.ui.radio_sequential.setChecked(True))
        self.ui.combo_diverging.currentIndexChanged.connect(
            lambda: self.ui.radio_diverging.setChecked(True))


        # Hook up palette radio buttons:
        self.ui.radio_qualitative.toggled.connect(
            lambda x: self.change_palette(utf8(self.ui.combo_qualitative.currentText())))
        self.ui.radio_sequential.toggled.connect(
            lambda x: self.change_palette(utf8(self.ui.combo_sequential.currentText())))
        self.ui.radio_diverging.toggled.connect(
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
        self.ui.spin_size_title.valueChanged.connect(self.add_annotations)
        self.ui.spin_size_x_label.valueChanged.connect(self.add_annotations)
        self.ui.spin_size_y_label.valueChanged.connect(self.add_annotations)
        self.ui.spin_size_x_ticklabels.valueChanged.connect(self.add_annotations)
        self.ui.spin_size_y_ticklabels.valueChanged.connect(self.add_annotations)
        self.ui.combo_font_figure.currentIndexChanged.connect(self.add_annotations)

        # (6) changing the legend layout
        self.ui.edit_legend_title.editingFinished.connect(self.change_legend)
        self.ui.check_show_legend.toggled.connect(self.change_legend)
        self.ui.spin_columns.valueChanged.connect(self.change_legend)
        self.ui.spin_size_legend.valueChanged.connect(self.change_legend)
        self.ui.spin_size_legend_entries.valueChanged.connect(self.change_legend)

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
        if (columns is None or
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
        if restored_position is not None:
            self.ui.list_figures.setCurrentItem(
                self.ui.list_figures.item(restored_position))
        else:
            self.ui.list_figures.setCurrentItem(None)
        self.ui.list_figures.blockSignals(False)

    def show_palette(self):
        self.ui.color_test_area.clear()
        #test_numbers = self.ui.spin_number.value()
        test_numbers = 12
        test_palette = sns.color_palette(self._palette_name, test_numbers)
        for i, (r, g, b)in enumerate(test_palette):
            item = QtWidgets.QListWidgetItem()
            self.ui.color_test_area.addItem(item)
            brush = QtGui.QBrush(QtGui.QColor(
                        int(r * 255), int(g * 255), int(b * 255)))
            item.setBackground(brush)

    def change_palette(self, x):
        if x != self._palette_name:
            self._palette_name = x
            self.show_palette()
            self.plot_figure()

    def restore_settings(self):
        def get_or_set_size(key, factor=1.0):
            try:
                size = int(options.settings.value(key, None))
            except TypeError:
                size = None
            if size is None:
                size = int(QtWidgets.QLabel().font().pointSize() * factor)
            return size

        self.resize(640, 400)
        try:
            self.resize(options.settings.value("visualizationdesigner_size"))
        except TypeError:
            pass
        self.viewer_size = options.settings.value("visualizationdesigner_viewer_size")
        self.viewer_size = QtCore.QSize(640, 480)

        self.data_x = options.settings.value("visualizationdesinger_data_x", None)
        self.data_y = options.settings.value("visualizationdesigner_data_y", None)
        self.layout_columns = options.settings.value("visualizationdesigner_layout_columns", None)
        self.layout_rows = options.settings.value("visualizationdesigner_layout_rows", None)
        val = options.settings.value("visualizationdesigner_show_legend", "true")
        val = val == "true"
        self.ui.check_show_legend.setChecked(val)


        family = options.settings.value(
            "visualizationdesigner_figure_font", None)
        index = self.ui.combo_font_figure.findText(family)
        if family is None or index == -1:
            family = utf8(QtWidgets.QLabel().font().family())
            index = self.ui.combo_font_figure.findText(family)
        self.ui.combo_font_figure.setCurrentIndex(index)

        self.legend_columns = options.settings.value(
            "visualizationdesigner_legend_columns", 1)

        self.ui.spin_size_title.setValue(
            get_or_set_size("visualizationdesigner_size_title", 1.2))
        self.ui.spin_size_x_label.setValue(
            get_or_set_size("visualizationdesigner_size_x_label"))
        self.ui.spin_size_y_label.setValue(
            get_or_set_size("visualizationdesigner_size_y_label"))
        self.ui.spin_size_legend.setValue(
            get_or_set_size("visualizationdesigner_size_legend"))
        self.ui.spin_size_x_ticklabels.setValue(
            get_or_set_size("visualizationdesigner_size_x_ticklabels", 0.8))
        self.ui.spin_size_y_ticklabels.setValue(
            get_or_set_size("visualizationdesigner_size_y_ticklabels", 0.8))
        self.ui.spin_size_legend_entries.setValue(
            get_or_set_size("visualizationdesigner_size_legend_entries", 0.8))

        palette = options.settings.value("visualizationdesigner_palette", None)
        if palette is None:
            palette = "Paired"
        for box, radio in (
                (self.ui.combo_qualitative, self.ui.radio_qualitative),
                (self.ui.combo_diverging, self.ui.radio_diverging),
                (self.ui.combo_sequential, self.ui.radio_sequential)):
            if box.findText(palette):
                radio.setChecked(True)
                box.setCurrentIndex(box.findText(palette))
                break
        else:
            self.ui.radio_qualitative.setChecked(True)
            self.ui.combo_qualitative.setCurrentIndex(
                self.ui.combo_qualitative.findText("Paired"))
            palette = "Paired"
        self._palette_name = palette

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

        self.ui.spin_columns.setValue(int(self.legend_columns))
        self.show_palette()

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
                figure_font=utf8(self.ui.combo_font_figure.currentText()),
                title=utf8(self.ui.edit_figure_title.text()),
                xlab=utf8(self.ui.edit_x_label.text()),
                ylab=utf8(self.ui.edit_y_label.text()),
                size_title=self.ui.spin_size_title.value(),
                size_xlab=self.ui.spin_size_x_label.value(),
                size_ylab=self.ui.spin_size_y_label.value(),
                size_xticks=self.ui.spin_size_x_ticklabels.value(),
                size_yticks=self.ui.spin_size_y_ticklabels.value(),
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
            col_wrap, _ = get_grid_layout(len(self.df[columns].unique()))
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

        self.grid = self.vis.get_grid(col=columns, row=rows,
                                      col_wrap=col_wrap,
                                      legend_out=True,
                                      sharex=True, sharey=True)

        try:
            self.grid = self.grid.map_dataframe(self.vis.plot_facet,
                                                x=data_x, y=data_y, z=data_z,
                                                levels_x=levels_x,
                                                levels_y=levels_y,
                                                levels_z=levels_z,
                                                session=self.session,
                                                palette=self._palette_name)
            self.setup_canvas(self.grid.fig)
            self.add_annotations()
            self.change_legend()

            self.dialog.setWindowTitle("{} – Coquery".format(figure_type.text()))
            self.dialog.show()
            self.dialog.raise_()

            if hasattr(self.vis, "on_pick"):
                self.grid.fig.canvas.mpl_connect('button_press_event',
                                                self.vis.on_pick)

            self.grid.fig.tight_layout()
            self.tool.functight()
            self.grid.fig.canvas.draw_idle()
        except ValueError as e:
            print(e)

    def add_annotations(self):
        if self.vis:
            values = self.get_gui_values()
            try:
                self.vis.set_annotations(self.grid, values)
            except Exception as e:
                print("ERROR: ", e)
                pass
            else:
                self.canvas.draw()

    def change_legend(self):
        if self.vis:
            if self.ui.check_show_legend.isChecked():
                kwargs = dict(
                    grid=self.grid,
                    title=self.ui.edit_legend_title.text() or None,
                    palette=self._palette_name,
                    ncol=self.ui.spin_columns.value(),
                    fontsize=self.ui.spin_size_legend_entries.value(),
                    titlesize=self.ui.spin_size_legend.value())
                self.vis.add_legend(**kwargs)
            else:
                self.vis.hide_legend(self.grid)
            self.canvas.draw()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            self.reject()

    def close(self, *args):
        options.settings.setValue("visualizationdesigner_size", self.size())
        options.settings.setValue("visualizationdesigner_viewer_size",
                                  self.viewer_size)
        options.settings.setValue("visualizationdesigner_data_x", self.data_x)
        options.settings.setValue("visualizationdesigner_data_y", self.data_y)
        options.settings.setValue("visualizationdesigner_layout_columns", self.layout_columns)
        options.settings.setValue("visualizationdesigner_layout_rows", self.layout_rows)

        options.settings.setValue("visualizationdesigner_figure_font",
            utf8(self.ui.combo_font_figure.currentText()))

        options.settings.setValue("visualizationdesigner_size_title",
                                  self.ui.spin_size_title.value())
        options.settings.setValue("visualizationdesigner_size_x_label",
                                  self.ui.spin_size_x_label.value())
        options.settings.setValue("visualizationdesigner_size_x_ticklabels",
                                  self.ui.spin_size_x_ticklabels.value())
        options.settings.setValue("visualizationdesigner_size_y_label",
                                  self.ui.spin_size_y_label.value())
        options.settings.setValue("visualizationdesigner_size_y_ticklabels",
                                  self.ui.spin_size_y_ticklabels.value())
        options.settings.setValue("visualizationdesigner_size_legend",
                                  self.ui.spin_size_legend.value())
        options.settings.setValue("visualizationdesigner_size_legend_entries",
                                  self.ui.spin_size_legend_entries.value())

        val = "true" if self.ui.check_show_legend.isChecked() else "false"
        options.settings.setValue("visualizationdesigner_show_legend", val)

        options.settings.setValue("visualizationdesigner_legend_columns", self.legend_columns)

        super(VisualizationDesigner, self).close(*args)

        if not hasattr(self, "canvas") and hasattr(self, "dialog"):
            self.dialog.hide()
            self.dialog.close()
            del self.dialog

    def exec_(self):
        result = super(VisualizationDesigner, self).exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.accept()
            return result
        else:
            return None


def get_visualizer_module(name):
    # try to import the specified visualization module:
    visualizer_path = os.path.join(options.cfg.base_path, "visualizer")
    try:
        find = imp.find_module(name, [visualizer_path])
        module = imp.load_module(name, *find)
        return module
    except Exception as e:
        print(e)
        msg = "<code style='color: darkred'>{type}: {code}</code>".format(
            type=type(e).__name__, code=sys.exc_info()[1])
        logger.error(msg)
        QtWidgets.QMessageBox.critical(
            None, "Visualization error – Coquery",
            VisualizationModuleError(name, msg).error_message)
        return None

logger = logging.getLogger(NAME)

# -*- coding: utf-8 -*-
"""
visualizationDesigner.py is part of Coquery.

Copyright (c) 2017-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import importlib.util
import logging
import os
import glob

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QCoreApplication

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg, NavigationToolbar2QT)

import pandas as pd
import seaborn as sns

from coquery import options

from coquery.gui.app import get_icon
from coquery.gui.threads import CoqThread
from coquery.gui.ui.visualizationDesignerUi import Ui_VisualizationDesigner

from coquery.visualizer.visualizer import get_grid_layout
from coquery.visualizer.colorizer import (
    COQ_SINGLE, COQ_CUSTOM,
    Colorizer, ColorizeByFactor, ColorizeByNum)


logging.getLogger("matplotlib.font_manager").disabled = True


def tr(context, text, disambiguation=None):
    return QCoreApplication.instance().translate(context, text, disambiguation)


_MARGIN_LABELS = ["top", "bottom", "left", "right", "wspace", "hspace"]
CONTEXT = "VisualizationDesigner"
PALETTE_BW = "Black and white"

VISUALIZATION_ERROR = tr(
    "VisualizationDesigner",
    """<p><b>An error occurred while plotting.</b></p>
    <p>While plotting the visualization, the following error was 
    encountered:</p>
    <p><span style='color: darkred'><code>{msg}</code></span></p>
    <p>The visualization may be incorrect. Please report this error on the 
    Coquery bug tracker..</p>""",
    None)

MODULE_ERROR = tr(
    "VisualizationDesigner",
    """<p><b>Could not load the visualization module '{module}'</b></p>
    <p>The following error occurred when attempting to open the visualization
    module '{module}':</p>
    <p>
        <span style='color: darkred'>
            <code>{type} in file {file}.py, line {line}:<br>{code}</code>
        </span>
    </p>
    <p>If you have downloaded this module from an external source, you may want to
    see if an updated version is available. Otherwise, either contact the author
    of the module, or report this error on the Coquery bug tracker.</p>""",
    None)


class CoqNavigationToolbar(NavigationToolbar2QT):
    """
    See matplotlib/backends/backend_qt5.py for the implementation of the base
    class.
    """
    def _init_toolbar(self):
        self.toolitems = [
            (tr(CONTEXT, text) or None,
             tr(CONTEXT, tooltip_text) or None,
             image_file,
             callback)
            for text, tooltip_text, image_file, callback in self.toolitems
            if callback not in ["configure_subplots"]]
        return super()._init_toolbar()


class VisualizationDesigner(QtWidgets.QDialog):
    moduleLoaded = pyqtSignal(str, str, object)
    allLoaded = pyqtSignal()
    dataRequested = pyqtSignal()
    paletteUpdated = pyqtSignal()
    updateFigureRequested = pyqtSignal()

    visualizers = {}

    def __init__(self, session, parent=None):
        super(VisualizationDesigner, self).__init__(parent)

        self.session = session
        self.vis = None
        self.df = None
        self._current_color = QtGui.QColor("#55aaff")
        self._dragging = False
        self._plotted = False

        self.ui = Ui_VisualizationDesigner()
        self.ui.setupUi(self)

        self.ui.combo_qualitative.addItem(PALETTE_BW)

        self.populate_figure_types()

        self.restore_settings(options.settings)
        self.display_values()

        self.check_figure_types()
        self.check_wrapping()
        self.check_grid_layout()
        self.check_clear_buttons()
        self._finetune_ui()
        self.change_figure_type()

        self.setup_connections()

        self.figure_widget = QtWidgets.QWidget()
        self.dialog_layout = QtWidgets.QVBoxLayout(self.figure_widget)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)
        self.dialog_layout.setSpacing(0)
        self.figure_widget.resize(self.viewer_size)
        self.figure_widget.setWindowTitle("<no figure> – Coquery")
        self.figure_widget.setWindowIcon(get_icon(
            "coquerel_icon.png", small_n_flat=False))
        self.figure_widget.show()

    def connectDataAvailableSignal(self, signal):
        signal.connect(self.data_available)

    def data_available(self):
        self.ui.button_refresh_data.show()
        new_label = tr(CONTEXT, "<b>New data available</b>", None)
        if len(self.df):
            new_label = "{}<br>{}".format(self.get_label(), new_label)
        self.ui.label_dimensions.setText(new_label)

    def get_label(self):
        if len(self.df):
            label = tr(CONTEXT, "{col} columns, {row} rows", None)
        else:
            label = tr(CONTEXT, "No data available", None)

        label = label.format(col=len(self.categorical) + len(self.numerical),
                             row=len(self.df))
        return label

    def setup_data(self, df, session, alias=None):
        self.blockSignals(True)

        self.ui.table_categorical.clear()
        self.ui.table_numerical.clear()
        self.df = df
        self.session = session
        self.alias = alias or {}
        for i, x in enumerate(df.columns):
            if self.df[x].dtype == bool:
                self.df[x] = self.df[x].astype(str)

        self.populate_variable_lists()
        self.ui.label_dimensions.setText(self.get_label())
        self.check_figure_types()

        if self.vis is not None:
            self.update_figure()

        self.ui.button_refresh_data.hide()

        self.blockSignals(False)

    def _finetune_ui(self):
        """
        Finetune the UI: set widths, set icons.
        """
        self.ui.list_figures.setDragEnabled(False)
        self.ui.list_figures.setDragDropMode(self.ui.list_figures.NoDragDrop)
        app = QtWidgets.QApplication.instance()
        w = app.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        self.ui.list_figures.setMinimumWidth(180 + w)
        self.ui.list_figures.setMaximumWidth(180 + w)

        icon_size = QtCore.QSize(QtWidgets.QLabel().sizeHint().height(),
                                 QtWidgets.QLabel().sizeHint().height())
        pix_col = get_icon("Select Column").pixmap(icon_size)
        pix_row = get_icon("Select Row").pixmap(icon_size)

        self.ui.icon_columns.setPixmap(pix_col)
        self.ui.icon_rows.setPixmap(pix_row)

        self.ui.button_clear_x.setIcon(get_icon("Clear Symbol"))
        self.ui.button_clear_y.setIcon(get_icon("Clear Symbol"))
        self.ui.button_clear_z.setIcon(get_icon("Clear Symbol"))
        self.ui.button_clear_columns.setIcon(get_icon("Clear Symbol"))
        self.ui.button_clear_rows.setIcon(get_icon("Clear Symbol"))

    def add_figure_type(self, label, icon, vis_class):
        self.figure_types.append((label, icon, vis_class))

    def get_figure_item(self, label, icon, vis_class):
        item = QtWidgets.QListWidgetItem(label)
        try:
            item.setIcon(get_icon(icon, small_n_flat=False))
        except Exception as e:
            item.setIcon(get_icon(icon, size="64x64"))

        size = QtCore.QSize(
            180, 64 + 0 * QtWidgets.QLabel().sizeHint().height())

        item.setSizeHint(size)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
        item.setData(QtCore.Qt.UserRole, vis_class)
        return item

    def _load_figure_types(self):
        for module_name in find_visualizer_modules():
            module = get_visualizer_module(module_name)
            visualizations = getattr(module, "provided_visualizations", [])
            # skip visualizers that haven't been updated to the new interface
            # yet:
            if not getattr(module, "updated_to_new_interface", False):
                continue
            for vis_class in visualizations:
                name = getattr(vis_class, "name",
                               "Unnamed ({})".format(module_name))
                icon = getattr(vis_class, "icon", "Grid")
                VisualizationDesigner.visualizers[name] = vis_class
                self.moduleLoaded.emit(name, icon, vis_class)
        self.allLoaded.emit()

    def populate_figure_types(self):
        self.figure_types = []
        self.moduleLoaded.connect(self.add_figure_type)
        self.allLoaded.connect(self.check_figure_types)
        self.figure_loader = CoqThread(self._load_figure_types, parent=self)
        self.figure_loader.taskFinished.connect(self.allLoaded.emit)
        self.figure_loader.taskException.connect(self._loadingError)
        self.figure_loader.start()

    def _loadingError(self, exception, **kwargs):
        exc_type, exc_obj, exc_tb = self.exc_info
        QtWidgets.QMessageBox.critical(
            self,
            tr("VisualizationDesigner",
               "Visualization module error – Coquery",
               None),
            MODULE_ERROR.format(
                module=exception._module_name,
                type=type(exception).__name__,
                file=exception._module_name,
                code=exc_obj,
                line=exc_tb.tb_lineno))

    def populate_variable_lists(self):
        d = self.get_gui_values()
        used = [d[x]
                for x in ["data_x", "data_y", "data_z", "columns", "rows"]
                if x in d and d[x]]

        self.categorical = [col for col in self.df.columns
                            if (pd.api.types.is_bool(self.df[col]) or
                                pd.api.types.is_object_dtype(self.df[col]))
                            and col not in used
                            and not col.startswith("coquery_invisible")]
        self.numerical = [col for col in self.df.columns
                          if pd.api.types.is_numeric_dtype(self.df[col])
                          and col not in used
                          and not col.startswith("coquery_invisible")]

        for col in self.categorical:
            label = self.alias.get(col) or col

            new_item = QtWidgets.QListWidgetItem(label)
            new_item.setData(QtCore.Qt.UserRole, col)
            new_item.setToolTip(new_item.text())
            if label in self.session.Resource.time_features:
                new_item.setIcon(get_icon("Clock"))

            self.ui.table_categorical.addItem(new_item)

        for col in self.numerical:
            label = self.alias.get(col) or col

            new_item = QtWidgets.QListWidgetItem(label)
            new_item.setData(QtCore.Qt.UserRole, col)
            new_item.setToolTip(new_item.text())
            if label in self.session.Resource.time_features:
                new_item.setIcon(get_icon("Clock"))

            self.ui.table_numerical.addItem(new_item)

        if len(self.df):
            # add "row number" variable
            col = "statistics_row_number"
            label = self.alias.get(col) or col

            new_item = QtWidgets.QListWidgetItem(label)
            new_item.setData(QtCore.Qt.UserRole, col)
            new_item.setToolTip(new_item.text())

            self.ui.table_numerical.addItem(new_item)

        ## add functions
        #for func in [Freq]:
            #new_item = QtWidgets.QListWidgetItem("{} (generated)".format(
                #func.get_name()))
            #new_item.setData(QtCore.Qt.UserRole,
                                #"func_{}".format(func._name))
            #new_item.setData(
                #QtCore.Qt.FontRole,
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
        self.canvas = FigureCanvasQTAgg(figure)
        self.canvas.setParent(self)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.toolbar = CoqNavigationToolbar(self.canvas, self)
        self.dialog_layout.addWidget(self.toolbar)
        self.dialog_layout.addWidget(self.canvas)

    def setup_connections(self):
        """
        Connects the GUI signals to the appropriate slots.
        """

        self.ui.button_refresh_data.clicked.connect(
            lambda: self.dataRequested.emit())

        self.ui.combo_qualitative.currentIndexChanged.connect(
            lambda x: self.set_radio(self.ui.radio_qualitative))
        self.ui.combo_sequential.currentIndexChanged.connect(
            lambda x: self.set_radio(self.ui.radio_sequential))
        self.ui.combo_diverging.currentIndexChanged.connect(
            lambda x: self.set_radio(self.ui.radio_diverging))

        # Hook up palette radio buttons:
        self.ui.radio_qualitative.pressed.connect(
            lambda: self.set_radio(self.ui.radio_qualitative))
        self.ui.radio_sequential.pressed.connect(
            lambda: self.set_radio(self.ui.radio_sequential))
        self.ui.radio_diverging.pressed.connect(
            lambda: self.set_radio(self.ui.radio_diverging))
        self.ui.radio_single_color.pressed.connect(
            lambda: self.set_radio(self.ui.radio_single_color))

        # Hook up single color button:
        self.ui.button_change_color.clicked.connect(self.set_color)

        # Hook up reverse checkbox
        self.ui.check_reverse.toggled.connect(
            lambda x: self.change_palette())

        # Hook up number of color spinner
        self.ui.spin_number.valueChanged.connect(
            lambda x: self.change_palette())

        # Hook up clear buttons.
        self.ui.button_clear_x.clicked.connect(self.ui.tray_data_x.clear)
        self.ui.button_clear_y.clicked.connect(self.ui.tray_data_y.clear)
        self.ui.button_clear_z.clicked.connect(self.ui.tray_data_z.clear)
        self.ui.button_clear_rows.clicked.connect(self.ui.tray_rows.clear)
        self.ui.button_clear_columns.clicked.connect(
            self.ui.tray_columns.clear)

        # Change custom figure widgets if necessary:
        self.ui.list_figures.currentItemChanged.connect(
            self.change_figure_type)

        self.ui.check_hide_unavailable.toggled.connect(self.check_figure_types)

        for widget in [self.ui.tray_data_x,
                       self.ui.tray_data_y,
                       self.ui.tray_data_z]:
            # Hook up checks for figure type.
            # The list of available figure types can change if a data tray has
            # changed, either because a feature was placed in it or if the tray
            # was cleared.
            widget.featureChanged.connect(self.check_figure_types)
            widget.featureCleared.connect(self.check_figure_types)

            # Hook up checks for grid layout enable state.
            # The enable state of the grid layout box is checked if there are
            # changes to the data trays.
            widget.featureChanged.connect(self.check_grid_layout)
            widget.featureCleared.connect(self.check_grid_layout)

        for widget in [self.ui.tray_rows, self.ui.tray_columns]:
            # Hook up checks for column and row trays so that they can't
            # contain duplicates of either the x or the y feature tray:
            widget.featureChanged.connect(self.check_duplicates)

            # Hook up checks for wrapping checkbox enable state.
            # The enable state of the wrapping checkbox is checked if there are
            # changes to the rows and columns tray.
            widget.featureChanged.connect(self.check_wrapping)
            widget.featureCleared.connect(self.check_wrapping)

        for widget in [self.ui.tray_data_x,
                       self.ui.tray_data_y,
                       self.ui.tray_data_z,
                       self.ui.tray_columns,
                       self.ui.tray_rows]:
            # Hook up checks for clear button enable state.
            # The enable state of clear buttons is checked if the feature in the
            # associated tray has changed or cleared.
            widget.featureChanged.connect(self.check_clear_buttons)
            widget.featureCleared.connect(self.check_clear_buttons)

        # Hook up annotation changes:
        for signal in (self.ui.edit_figure_title.textChanged,
                       self.ui.edit_x_label.textChanged,
                       self.ui.edit_y_label.textChanged,
                       self.ui.spin_size_title.valueChanged,
                       self.ui.spin_size_x_label.valueChanged,
                       self.ui.spin_size_y_label.valueChanged,
                       self.ui.spin_size_x_ticklabels.valueChanged,
                       self.ui.spin_size_y_ticklabels.valueChanged,
                       self.ui.combo_font_figure.currentIndexChanged):
            signal.connect(self.update_annotations)

        # changing the legend layout
        for signal in (self.ui.check_show_legend.toggled,
                       self.ui.spin_columns.valueChanged):
            signal.connect(self.change_legend)

        for signal in (self.ui.spin_size_legend.valueChanged,
                       self.ui.spin_size_legend_entries.valueChanged,
                       self.ui.edit_legend_title.textChanged,
                       self.ui.combo_font_figure.currentIndexChanged):
            signal.connect(self.change_legend_appearance)

        # Hook up figure plotting:
        for signal in (
                       # (1) placing a feature in a tray
                       self.ui.tray_data_x.featureChanged,
                       self.ui.tray_data_y.featureChanged,
                       self.ui.tray_data_z.featureChanged,
                       self.ui.tray_columns.featureChanged,
                       self.ui.tray_rows.featureChanged,

                       # (2) clicking a clear button
                       self.ui.button_clear_x.clicked,
                       self.ui.button_clear_y.clicked,
                       self.ui.button_clear_z.clicked,
                       self.ui.button_clear_rows.clicked,
                       self.ui.button_clear_columns.clicked,

                       # (3) changing the wrapping checkbox
                       self.ui.check_wrap_layout.toggled,

                       # (4) selecting a different figure type
                       self.ui.list_figures.currentItemChanged):

            signal.connect(self.plot_figure)

        self.ui.color_test_area.itemPressed.connect(self.switch_stylesheet)
        self.ui.color_test_area.currentItemChanged.connect(
            self.reset_stylesheet)
        self.ui.color_test_area.model().dataChanged.connect(
            self.set_custom_palette)

        # Note: The signals for the "Margins" tab are already set up in the
        # .ui file - this is probably the preferred option for the other
        # signals as well.

    def update_slider_margins(self):
        """
        Change the figure margins according to the settings of the sliders in
        the Margins tab, and also update the spinner values to match.
        
        This method is called whenever a slider emits a valueChanged signal.

        Returns
        -------
        None
        """
        old_margins = {var: getattr(self.grid.fig.subplotpars, var)
                       for var in _MARGIN_LABELS}

        margins = dict(
            zip(_MARGIN_LABELS,
            [self.ui.slide_top.value() / 100,
             self.ui.slide_bottom.value() / 100,
             self.ui.slide_left.value() / 100,
             self.ui.slide_right.value() / 100,
             self.ui.slide_horizontal.value() / 100,
             self.ui.slide_vertical.value() / 100]))

        if margins["left"] > old_margins["right"]:
            margins["right"] = 1 - margins["left"] - 0.00001
        elif 1 - margins["right"] < old_margins["left"]:
            margins["left"] = 1 - margins["right"] - 0.00001

        self.set_margins(margins)
        self.update_figure_margins(margins)

    def update_spin_margins(self):
        """
        Change the figure margins according to the settings of the spinners in
        the Margins tab, and also update the slider values to match. 
        
        This method is called whenever a spinner emits a valueChanged signal.

        Returns
        -------
        None
        """
        margins = dict(zip(
            _MARGIN_LABELS,
            [self.ui.spin_top.value(),
             self.ui.spin_bottom.value(),
             self.ui.spin_left.value(),
             self.ui.spin_right.value(),
             self.ui.spin_horizontal.value(),
             self.ui.spin_vertical.value()]))
        self.set_margins(margins)
        self.update_figure_margins(margins)

    def update_figure_margins(self, margins):
        """
        Changes the figure margins according to the provided margins.

        Returns
        -------
        None
        """
        margins["right"] = 1 - margins["right"]
        margins["top"] = 1 - margins ["top"]
        try:
            self.grid.fig.subplots_adjust(**margins)
        except ValueError as e:
            pass
        else:
            self.canvas.draw_idle()

    def set_tight_layout(self):
        self.grid.fig.tight_layout()
        margins = {var: getattr(self.grid.fig.subplotpars, var)
                   for var in _MARGIN_LABELS}
        margins["right"] = 1 - margins["right"]
        margins["top"] = 1 - margins["top"]
        self.set_margins(margins)

    def use_tight_layout(self):
        """
        Calls tight_layout() for the current figure, and updates the widgets
        in the Margins tab with the new values.

        This method is evoked if the Optimize button is pressed.
        The canvas will be redrawn.

        Returns
        -------
        None
        """
        self.set_tight_layout()
        self.canvas.draw_idle()

    def set_margins(self, margins):
        """
        Update the widgets in the Margin tab with the provided values.

        All signals are blocked while setting the values.

        Parameters
        ----------
        margins : dict of str
            The values for the top, bottom, left, right, horizontal, and
            vertical widgets.

        Returns
        -------
        None
        """
        if margins["left"] >= (1 - margins["right"]):
            margins["left"], margins["right"] = (1 - margins["right"],
                                                 1 - margins["left"])
        if margins["bottom"] >= (1 - margins["top"]):
            margins["top"], margins["bottom"] = (1 - margins["bottom"],
                                                 1 - margins["top"])

        for var, (spinner, slider) in zip(
                _MARGIN_LABELS,
                ((self.ui.spin_top, self.ui.slide_top),
                 (self.ui.spin_bottom, self.ui.slide_bottom),
                 (self.ui.spin_left, self.ui.slide_left),
                 (self.ui.spin_right, self.ui.slide_right),
                 (self.ui.spin_horizontal, self.ui.slide_horizontal),
                 (self.ui.spin_vertical, self.ui.slide_vertical))):
            spinner.blockSignals(True)
            slider.blockSignals(True)
            spinner.setValue(margins[var])
            slider.setValue(margins[var] * 100)
            spinner.blockSignals(False)
            slider.blockSignals(False)

    def change_figure_type(self):
        self.ui.group_custom.hide()

        figure_type = self.ui.list_figures.currentItem()
        if figure_type is None:
            return

        if self.df is None:
            return

        vis_class = VisualizationDesigner.visualizers[
            figure_type.text()]

        self.vis = vis_class(self.df, self.session,
                             id_column="coquery_invisible_corpus_id",
                             limiter_fnc=self.session.limiter)
        self.add_custom_widgets(self.vis)

    def add_custom_widgets(self, vis):
        clear_layout(self.ui.layout_custom)

        tup = vis.get_custom_widgets(**self.get_gui_values())
        items, apply_signals, update_signals = tup

        if items:
            self.ui.group_custom.show()
            for item in items:
                if isinstance(item, QtWidgets.QLayout):
                    self.ui.layout_custom.addLayout(item)
                else:
                    self.ui.layout_custom.addWidget(item)
            self.ui.button_apply = self.create_apply_button(vis, apply_signals)
            apply_layout = QtWidgets.QHBoxLayout()
            apply_layout.addItem(
                QtWidgets.QSpacerItem(0, 0,
                                      QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Minimum))
            apply_layout.addWidget(self.ui.button_apply)
            apply_layout.addItem(
                QtWidgets.QSpacerItem(0, 0,
                                      QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Minimum))
            self.ui.layout_custom.addLayout(apply_layout)
            for signal in update_signals:
                signal.connect(vis.update_widgets)

        else:
            self.ui.group_custom.hide()

    def create_apply_button(self, vis, signals):
        label = tr("Visualizer", "Apply", None)

        button = QtWidgets.QPushButton(label)
        button.setDisabled(True)
        button.clicked.connect(self.update_figure)

        for signal in signals:
            signal.connect(self.enable_apply_button)
        return button

    def enable_apply_button(self):
        """
        Enable the 'Apply' custom button, if present.
        """
        try:
            self.ui.button_apply.setEnabled(True)
        except AttributeError:
            pass

    def update_figure(self):
        logging.info("VIS: update_figure()")
        self.vis.update_values()
        self.plot_figure()
        logging.info("VIS: update_figure() done")

    def recolorize(self):
        if not self._plotted:
            self.update_figure()
        else:
            values = self.get_gui_values()
            self.colorizer.palette = values["palette"]
            self.vis.colorize()
            self.update_legend()
            plt.gcf().canvas.draw_idle()

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

    def check_duplicates(self):
        columns = self.ui.tray_columns.data()
        rows = self.ui.tray_rows.data()
        x = self.ui.tray_data_x.data()
        y = self.ui.tray_data_y.data()

        if columns and (columns in [x, y]):
            self.ui.tray_columns.clear()
        if rows and (rows in [x, y]):
            self.ui.tray_rows.clear()

    def check_clear_buttons(self):
        for button, tray in (
                (self.ui.button_clear_x, self.ui.tray_data_x),
                (self.ui.button_clear_y, self.ui.tray_data_y),
                (self.ui.button_clear_z, self.ui.tray_data_z),
                (self.ui.button_clear_columns, self.ui.tray_columns),
                (self.ui.button_clear_rows, self.ui.tray_rows)):
            button.setEnabled(bool(tray.text()))

    def check_grid_layout(self):
        if self.ui.tray_data_x.text() or self.ui.tray_data_y.text():
            self.ui.group_layout.setEnabled(True)
        else:
            self.ui.group_layout.setEnabled(False)
            if self.ui.tray_columns.text():
                self.ui.tray_columns.clear()
            if self.ui.tray_rows.text():
                self.ui.tray_rows.clear()

    def check_figure_types(self):
        if self.df is None:
            return

        current_item = self.ui.list_figures.currentItem()
        if current_item:
            last_class = current_item.data(QtCore.Qt.UserRole)
        else:
            last_class = None

        data_x = self.ui.tray_data_x.data()
        data_y = self.ui.tray_data_y.data()

        hide_unavailable = self.ui.check_hide_unavailable.isChecked()

        self.ui.list_figures.blockSignals(True)

        self.ui.list_figures.clear()

        for label, icon, vis_class in self.figure_types:
            item = self.get_figure_item(label, icon, vis_class)
            visualizer = VisualizationDesigner.visualizers[item.text()]
            if (visualizer.validate_data(data_x, data_y,
                                         self.df, self.session) and
                    not ((data_x or data_y) and (data_x == data_y))):
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEnabled)
                self.ui.list_figures.addItem(item)
            else:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                if not hide_unavailable:
                    self.ui.list_figures.addItem(item)

        # try to restore last position:
        for i in range(self.ui.list_figures.count()):
            current_item = self.ui.list_figures.item(i)
            vis_class = current_item.data(QtCore.Qt.UserRole)
            if vis_class == last_class:
                self.ui.list_figures.setCurrentItem(current_item)
                break

        self.ui.list_figures.blockSignals(False)

    # PALETTE METHODS

    """
    Update palette...

    * different index from current combo box is selected
    * current radio button is deselected
    * the reverse button is clicked
    * a different custom color is selected
    --> each of these emits an paletteUpdated signal that
        should be connected to show_palette()

    The figure will be repainted if...

    * the palette has been updated
    * the palette order has been changed
    * a palette color has been modified
    """

    def get_palette_name(self):
        for ptype in ("qualitative", "sequential", "diverging",
                      "single_color", "custom"):
            widget_name = "radio_{}".format(ptype)
            widget = getattr(self.ui, widget_name)
            if widget.isChecked():
                if ptype == "single_color":
                    return "{}_{}".format(
                        COQ_SINGLE, self._current_color.name())
                elif ptype == "custom":
                    pal_name = COQ_CUSTOM
                    break
                else:
                    combo_name = "combo_{}".format(ptype)
                    combo = getattr(self.ui, combo_name)
                    pal_name = combo.currentText()
                    break

        if self.ui.check_reverse.isChecked():
            pal_name = "{}_r".format(pal_name)
        return pal_name or "Paired"

    def get_current_palette(self):
        self._palette_name = self.get_palette_name()
        self._color_number = self.ui.spin_number.value()

        name, _, rev = self._palette_name.partition("_")

        if not name:
            name = "Paired"

        if name == COQ_SINGLE:
            rgb = self._current_color.getRgb()[:-1]
            palette = [tuple(x / 255 for x in rgb)] * self._color_number
        elif name == PALETTE_BW:
            palette = [(0, 0, 0), (1, 1, 1)]
        elif name == COQ_CUSTOM:
            palette = []
            self.ui.color_test_area.blockSignals(True)
            for i in range(self.ui.color_test_area.count()):
                item = self.ui.color_test_area.item(i)
                rgb = item.background().color().getRgb()[:-1]
                palette.append(tuple(x / 255 for x in rgb))
            self.ui.color_test_area.blockSignals(False)
        else:
            palette = sns.color_palette(name, self._color_number)

        if rev == "r":
            palette = palette[::-1]
        return palette

    def show_palette(self):
        palette = self.get_current_palette()

        self.ui.color_test_area.blockSignals(True)
        self.ui.color_test_area.clear()
        for i, (r, g, b) in enumerate(palette):
            item = QtWidgets.QListWidgetItem()
            self.ui.color_test_area.addItem(item)
            brush = QtGui.QBrush(QtGui.QColor(
                        int(r * 255), int(g * 255), int(b * 255)))
            item.setBackground(brush)
        self.ui.color_test_area.blockSignals(False)
        self.updateFigureRequested.emit()

    def set_custom_palette(self):
        if not self._dragging:
            return

        self._dragging = False
        current_palette = self.get_palette_name()
        if current_palette != COQ_SINGLE:
            self._custom_palette = self.get_current_palette()
            self.ui.radio_custom.setChecked(True)
            self._palette_name = None
            self.recolorize()

    def change_palette(self):
        self.show_palette()
        self.recolorize()

    def set_color(self):
        if self._current_color:
            color = QtWidgets.QColorDialog.getColor(self._current_color)
        else:
            color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self._current_color = color
            self.change_palette()

    def switch_stylesheet(self, item):
        if item:
            color = item.background().color()
            template = """QListWidget::item:selected {{
                            background: rgb({r}, {g}, {b}); }}"""
            self.ui.color_test_area.setStyleSheet(
                template.format(r=color.red(),
                                g=color.green(),
                                b=color.blue()))
            self._dragging = True
        else:
            self.ui.color_test_area.setStyleSheet(None)

    def reset_stylesheet(self, item1, item2):
        self.ui.color_test_area.setStyleSheet(None)
        self.ui.color_test_area.setCurrentItem(None)

    def set_radio(self, radio):
        radio.blockSignals(True)
        if not radio.isChecked():
            radio.setChecked(True)
        self.change_palette()
        radio.blockSignals(False)

    def display_values(self):
        # set up Layout tab:
        # data x
        if self.data_x:
            label = self.alias.get(self.data_x) or self.data_x
        else:
            label = None
        if label:
            self.ui.receive_data_x.setData(label)

        # data y
        if self.data_y:
            label = self.alias.get(self.data_y) or self.data_y
        else:
            label = None
        #self.ui.receive_data_y.setText(label)

        # layout columns
        if self.layout_columns:
            label = self.alias.get(self.layout_columns) or self.layout_columns
        else:
            label = None
        #self.ui.receive_columns.setText(label)

        # layout rows
        if self.layout_rows:
            label = self.alias.get(self.layout_rows) or self.layout_rows
        else:
            label = None
        #self.ui.receive_rows.setText(label)

        self.ui.spin_columns.setValue(int(self.legend_columns))
        self.show_palette()

    def get_gui_values(self):
        """
        """
        x = self.ui.tray_data_x.data()
        y = self.ui.tray_data_y.data()
        z = self.ui.tray_data_z.data()

        d = dict(x=x, y=y, z=z,
                 columns=self.ui.tray_columns.data(),
                 rows=self.ui.tray_rows.data(),
                 figure_type=self.ui.list_figures.currentItem(),
                 figure_font=self.ui.combo_font_figure.currentText(),
                 title=self.ui.edit_figure_title.text(),
                 xlab=self.ui.edit_x_label.text(),
                 ylab=self.ui.edit_y_label.text(),
                 size_title=self.ui.spin_size_title.value(),
                 size_xlab=self.ui.spin_size_x_label.value(),
                 size_ylab=self.ui.spin_size_y_label.value(),
                 size_xticks=self.ui.spin_size_x_ticklabels.value(),
                 size_yticks=self.ui.spin_size_y_ticklabels.value(),
                 session=self.session,
                 palette=self.get_current_palette(),
                 color_number=self.ui.spin_number.value())

        d["levels_x"] = []
        d["levels_y"] = []
        d["levels_z"] = []
        d["range_x"] = None
        d["range_y"] = None
        d["range_z"] = None

        if x:
            try:
                d["levels_x"] = uniques(self.df[x])
            except KeyError:
                self.ui.tray_data_x.clear(no_return=True)
            else:
                d["range_x"] = (self.df[x].dropna().min(),
                                self.df[x].dropna().max())

        if y:
            try:
                d["levels_y"] = uniques(self.df[y])
            except KeyError:
                self.ui.tray_data_y.clear(no_return=True)
            else:
                d["range_y"] = (self.df[y].dropna().min(),
                                self.df[y].dropna().max())

        if z:
            try:
                d["levels_z"] = uniques(self.df[z])
            except KeyError:
                self.ui.tray_data_z.clear(no_return=True)
            else:
                d["range_z"] = (self.df[z].dropna().min(),
                                self.df[z].dropna().max())

        return d

    def get_colorizer(self, x, y, z, df, palette, vis, **kwargs):
        z = z or vis.get_subordinated(x=x, y=y)
        if z:
            if df[z].dtype == object:
                levels = uniques(df[z])
                colorizer = ColorizeByFactor(palette, levels)
                if z not in [x, y]:
                    colorizer.set_title_frm(vis.get_factor_frm())
            else:
                colorizer = ColorizeByNum(palette, kwargs["range_z"])
                colorizer.set_title_frm(vis.get_num_frm())
        else:
            colorizer = Colorizer(palette)
            colorizer.set_title_frm("{z}")
        return colorizer

    def plot_figure(self):
        logging.info("VIS: plot_figure()")
        values = self.get_gui_values()

        if not values["figure_type"]:
            return

        if (self.ui.check_wrap_layout.isChecked()):
            col_wrap, _ = get_grid_layout(
                len(self.df[values["columns"]].unique()))
        else:
            col_wrap = None

        data_columns = [values[x] for x in ["x", "y", "z", "columns", "rows"]
                        if values[x]]

        # remove duplicates:
        data_columns = list(set(data_columns))
        data_columns.append("coquery_invisible_corpus_id")
        aliased_columns = [self.alias.get(x, x) for x in data_columns]

        for x in ["x", "y", "z", "columns", "rows"]:
            values[x] = self.alias.get(values[x], values[x])

        df = self.df[data_columns]
        df.columns = aliased_columns

        logging.info("VIS: Data initialized")
        self.vis.df = df
        self.vis.frm_str = options.cfg.float_format
        self.vis.experimental = options.cfg.experimental
        self.colorizer = self.get_colorizer(df=df, vis=self.vis, **values)

        logging.info("VIS: Visualizer initialized")
        self.grid = self.vis.get_grid(col=values["columns"],
                                      row=values["rows"],
                                      col_wrap=col_wrap,
                                      legend_out=True,
                                      sharex=True, sharey=True,
                                      values=values)
        logging.info("VIS: Grid initialized")

        self.setup_canvas(self.grid.fig)
        logging.info("VIS: canvas initialized")

        w, h = self.figure_widget.size().width(), self.figure_widget.size().height()
        dpi = self.grid.fig.dpi
        self.grid.fig.set_size_inches(w / dpi, h / dpi)

        logging.info("VIS: Grid size {}, {} inches".format(
            w / dpi, h / dpi))

        self.start_plot()
        try:
            self.run_plot(**values)
        except Exception as e:
            raise e
            self.exception_plot(e)
            self._plotted = False
        else:
            self._plotted = True
        self.finalize_plot()

        #if options.cfg.experimental:
            #self.plot_thread = CoqThread(
                #self.run_plot, parent=self, **values)
            #self.plot_thread.taskStarted.connect(self.start_plot)
            #self.plot_thread.taskFinished.connect(self.finalize_plot)
            #self.plot_thread.taskException.connect(self.exception_plot)
            ##self.vis.moveToThread(self.plot_thread)
            #self.plot_thread.start()
        #else:
            #self.start_plot()
            #self.run_plot(**values)
            #self.finalize_plot()
        logging.info("VIS: plot_figure() done")

    def start_plot(self):
        logging.info("VIS: start_plot()")
        try:
            self.progress_bar = QtWidgets.QProgressBar()
            self.progress_bar.setRange(0, 0)
            self.progress_bar.show()
            self.dialog_layout.addWidget(self.progress_bar)
        except Exception as e:
            logging.error(f"VIS: start_plot(), exception {str(e)}")
            raise e
        logging.info("VIS: start_plot() done")

    def run_plot(self, **kwargs):
        logging.info("VIS: run_plot()")
        try:
            self.grid.map_dataframe(self.vis.draw,
                                    colorizer=self.colorizer,
                                    **kwargs)
        except Exception as e:
            logging.error("VIS: run_plot(), exception {}".format(str(e)))
            raise e
        self.grid.set_titles(row_template="{row_name}", col_template="{col_name}")
        logging.info("VIS: run_plot() done")

    def finalize_plot(self):
        logging.info("VIS: finalize_plot()")
        try:
            values = self.get_gui_values()
            figure_title = values["figure_type"].text()

            try:
                self.dialog_layout.removeWidget(self.progress_bar)
                self.progress_bar.hide()
                del self.progress_bar
            except AttributeError:
                pass

            self.add_annotations()
            self.set_limits()
            self.update_legend()

            self.set_tight_layout()
            self.canvas.draw_idle()

            self.figure_widget.setWindowTitle("{} – Coquery".format(figure_title))
            self.figure_widget.show()
            self.figure_widget.raise_()

            self.ui.widget_margins.setEnabled(True)
            self.ui.group_spacing.setEnabled(
                bool(self.ui.tray_columns.data() or self.ui.tray_rows.data()))

            # Try to connect on_pick() method of visualizer to Matplot press
            # events:
            try:
                self.grid.fig.canvas.mpl_connect("button_press_event",
                                                 self.vis.on_pick)
            except AttributeError:
                pass

            # Disable the Apply button (if existing):
            try:
                self.ui.button_apply.setDisabled(True)
            except AttributeError:
                pass

        except Exception as e:
            logging.error("VIS: finalize_plot(), exception {}".format(str(e)))
            raise e
        logging.info("VIS: finalize_plot() done")

    def exception_plot(self, e):
        logging.error(e)
        QtWidgets.QMessageBox.critical(
            self,
            "Error while plotting – Coquery",
            VISUALIZATION_ERROR.format(msg=str(e)),
            QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def update_annotations(self):
        self.add_annotations()
        self.canvas.draw_idle()

    def add_annotations(self):
        if self.vis:
            values = self.get_gui_values()
            try:
                self.vis.set_annotations(self.grid, values)
            except Exception as e:
                print("ERROR: ", e)
                logging.error(str(e))

    def set_limits(self):
        if self.vis:
            values = self.get_gui_values()
            try:
                self.vis.set_limits(self.grid, values)
            except Exception as e:
                print("ERROR: ", e)
                logging.error(str(e))

    def update_legend(self):
        if self.ui.check_show_legend.isChecked():
            kwargs = dict(
                grid=self.grid,
                title=self.ui.edit_legend_title.text() or None,
                palette=self._palette_name,
                ncol=self.ui.spin_columns.value(),
                fontsize=self.ui.spin_size_legend_entries.value(),
                titlesize=self.ui.spin_size_legend.value())
            self.vis.hide_legend(self.grid)
            self.vis.add_legend(**kwargs)
        else:
            self.vis.hide_legend(self.grid)

    def change_legend_appearance(self):
        try:
            legend = self.grid.fig.legends[-1]
        except (AttributeError, IndexError):
            return

        if legend:
            font = self.ui.combo_font_figure.currentText()

            title_text = self.ui.edit_legend_title.text()
            if title_text:
                legend.set_title(title_text)
            title = legend.get_title()
            title.set_size(self.ui.spin_size_legend.value())
            title.set_fontname(font)
            entry_size = self.ui.spin_size_legend_entries.value()
            for entry in legend.get_texts():
                entry.set_size(entry_size)
                entry.set_fontname(font)

            self.canvas.draw_idle()

    def change_legend(self):
        if self.vis:
            self.update_legend()
            plt.gcf().canvas.draw_idle()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            self.reject()

    def store_settings(self, settings):
        return
        gui = self.get_gui_values()
        reverse_palette = ["false", "true"][self.ui.check_reverse.isChecked()]
        show_legend = ["false", "true"][self.ui.check_show_legend.isChecked()]
        hide_unavailable = ["false", "true"][
            self.ui.check_hide_unavailable.isChecked()]

        for name, value in (
                ("size", self.size()),
                ("viewer_size", self.viewer_size),
                ("data_x", gui["x"]),
                ("data_y", gui["y"]),
                ("data_z", gui["z"]),
                ("layout_columns", gui["columns"]),
                ("layout_rows", gui["rows"]),
                ("figure_type", gui["figure_type"]),  # CHECK
                ("figure_font", gui["figure_font"]),
                ("size_title", gui["size_title"]),
                ("size_x_label", gui["size_xlab"]),
                ("size_x_ticklabels", gui["size_xticks"]),
                ("size_y_label", gui["size_ylab"]),
                ("size_y_ticklabels", gui["size_yticks"]),
                ("color_number", gui["color_number"]),
                ("palette", gui["palette"]),


                ("size_legend", self.ui.spin_size_legend.value()),
                ("size_legend_entries",
                 self.ui.spin_size_legend_entries.value()),
                ("legend_columns", self.legend_columns),
                ("show_legend", show_legend),
                ("hide_unavailable", hide_unavailable)):

            settings.setValue("visualizationdesigner_{}".format(name), value)

    def restore_settings(self, settings):
        def get_or_set_size(key, factor=1.0):
            try:
                size = int(settings.value(key, None))
            except TypeError:
                size = None
            if size is None:
                size = int(QtWidgets.QLabel().font().pointSize() * factor)
            return size

        self.resize(640, 400)
        try:
            self.resize(settings.value("visualizationdesigner_size"))
        except TypeError:
            pass
        self.viewer_size = settings.value(
            "visualizationdesigner_viewer_size")
        self.viewer_size = QtCore.QSize(640, 480)

        self.data_x = settings.value("visualizationdesinger_data_x", None)
        self.data_y = settings.value("visualizationdesigner_data_y", None)
        self.layout_columns = settings.value(
            "visualizationdesigner_layout_columns", None)
        self.layout_rows = settings.value(
            "visualizationdesigner_layout_rows", None)
        val = settings.value("visualizationdesigner_show_legend", "true")
        self.ui.check_show_legend.setChecked(val == "true")

        val = settings.value("visualizationdesigner_hide_unavailable", "true")
        self.ui.check_hide_unavailable.setChecked(val == "true")

        family = settings.value("visualizationdesigner_figure_font", None)
        index = self.ui.combo_font_figure.findText(family)
        if family is None or index == -1:
            family = QtWidgets.QLabel().font().family()
            index = self.ui.combo_font_figure.findText(family)
        self.ui.combo_font_figure.setCurrentIndex(index)

        self.legend_columns = settings.value(
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

        val = settings.value("visualizationdesigner_reverse_palette", "true")
        self._reversed = (val == "true")
        self.ui.check_reverse.setChecked(self._reversed)
        val = settings.value("visualizationdesigner_color_number", 12)
        self._color_number = int(val)
        self.ui.spin_number.setValue(self._color_number)

        palette = settings.value("visualizationdesigner_palette", "Paired")
        if not palette:
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

        if self._reversed:
            palette = "{}_r".format(palette)
        self._palette_name = palette

    def closeEvent(self, ev):
        self.store_settings(options.settings)
        if not hasattr(self, "canvas") and hasattr(self, "dialog"):
            self.figure_widget.hide()
            self.figure_widget.close()
            del self.figure_widget
        return super(VisualizationDesigner, self).closeEvent(ev)


def get_visualizer_module(name):
    # try to import the specified visualization module:
    visualizer_path = os.path.join(options.cfg.base_path, "visualizer")
    try:
        spec = importlib.util.find_spec(name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        e._module_name = name
        raise e
    return module


def find_visualizer_modules():
    """
    Finds the list of potential visualization modules.
    """
    visualizer_path = os.path.join(options.cfg.base_path, "visualizer")

    lst = [os.path.splitext(os.path.basename(file_name))[0]
           for file_name in glob.glob(os.path.join(visualizer_path, "*.py"))]
    return lst


def uniques(S):
    """
    Get unique levels of Series by discarding NAs and then sorting
    the unique values.

    This function is much more efficient (but less transparent) than
    the equivalent sorted(S.dropna().unique().values()).

    Parameters
    ----------
    S : Series
        A Series with either numeric or non-numeric values

    Returns
    -------
    unique_values : list
        A list with the sorted unique values in the input Series
    """
    return sorted(set(S.values[~pd.isnull(S.values)]))


def clear_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                clear_layout(item.layout())

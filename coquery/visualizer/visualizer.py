# -*- coding: utf-8 -*-
"""
visualizer.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math

import pandas as pd
import matplotlib as mpl
mpl.use("Qt5Agg")
mpl.rcParams["backend"] = "Qt5Agg"
import matplotlib.pyplot as plt
import seaborn as sns

from coquery.gui.pyqt_compat import QtCore, QtGui, QtWidgets
from coquery import options
from coquery import managers
from coquery.general import CoqObject
from coquery.errors import (VisualizationInvalidLayout,
                            VisualizationNoDataError)
from coquery.unicode import utf8
from coquery.gui.classes import CoqTableModel


class BaseVisualizer(QtCore.QObject):
    """
    Define a class that contains the code to visualize data in several
    ways.

    The data to be visualized is passed to the visualizer by calling
    :func:`set_data_source`. :func:`update_data` contains the code that is
    required to translate the data from the data source into a format that
    is usable for the visualizer. This method is also called whenever the
    layout or content of the data source changes. The visualization routines
    are specified in :func:`draw`. This method is usually called externally
    by :func:`VisualizerDialog.Plot`.
    """
    numerical_axes = 0
    default_func = None
    function_list = []

    def __init__(self, data_model, data_view, parent=None):
        super(BaseVisualizer, self).__init__(parent=parent)
        self._model = None
        self._view = None
        self.options = {}
        self.set_data_source(data_model, data_view)
        self.set_defaults()
        self.setup_figure()

        self.function = self.draw
        mpl.rcParams["axes.formatter.useoffset"] = "False"

    def set_defaults(self):
        if self.numerical_axes and False:
            if not self.options.get("color_number"):
                self.options["color_number"] = 1
            if not self.options.get("label_legend_columns"):
                self.options["label_legend_columns"] = 1
            if not self.options.get("color_palette"):
                self.options["color_palette"] = "Paired"
                self.options["color_number"] = 1
        else:
            if not self.options.get("color_number"):
                self.options["color_number"] = len(self._levels[-1])
            if not self.options.get("label_legend_columns"):
                self.options["label_legend_columns"] = 1
            if not self.options.get("color_palette"):
                if len(self._levels) == 0:
                    self.options["color_palette"] = "Paired"
                    self.options["color_number"] = 1
                elif len(self._levels[-1]) in (2, 4, 6):
                    self.options["color_palette"] = "Paired"
                elif len(self._groupby) == 2:
                    self.options["color_palette"] = "Paired"
                else:
                    self.options["color_palette"] = "RdPu"

        self.options["figure_font"] = (
            QtWidgets.QApplication.instance().font())

        if not self.options.get("color_palette_values"):
            self.set_palette_values(self.options["color_number"])

    def format_coord(self, x, y, title):
        pass

    def set_tooltip(self, s):
        try:
            self.g.fig.canvas.setToolTip(s)
        except Exception as e:
            print(e)

    def set_hover(self, fun=None):
        if fun is None:
            fun = self.format_coord

        if not fun:
            return

        for ax in self.g.fig.axes:
            ax.format_coord = lambda x, y: fun(x, y, ax.get_title())

    def onclick(self, event):
        pass

    def set_palette_values(self, n=None):
        """
        Set the color palette values to the specified number.
        """
        if not n:
            n = self.options["color_number"]
        else:
            self.options["color_number"] = n

        if self.options["color_palette"] != "custom":
            self.options["color_palette_values"] = sns.color_palette(
                self.options["color_palette"], n)

    def _validate_layout(func):
        def func_wrapper(self):
            if self._col_wrap:
                if self._col_wrap > 16:
                    raise VisualizationInvalidLayout
                else:
                    return func(self)
            if self._col_factor and len(pd.unique(self._table[self._col_factor].values.ravel())) > 16:
                raise VisualizationInvalidLayout
            if self._row_factor and len(pd.unique(self._table[self._row_factor].values.ravel())) > 16:
                raise VisualizationInvalidLayout
            return func(self)
        return func_wrapper

    @_validate_layout
    def setup_figure(self):
        """
        Prepare the matplotlib figure for plotting.

        This method sets the default font, and the overall apearance of the
        figure.
        """

        if options.cfg.xkcd:
            fonts = QtGui.QFontDatabase().families()
            for x in ["Humor Sans", "DigitalStrip", "Comic Sans MS"]:
                if x in fonts:
                    self.options["figure_font"] = QtGui.QFont(x, pointSize=self.options["figure_font"].pointSize())
                    break
            else:
                for x in ["comic", "cartoon"]:
                    for y in fonts:
                        if x.lower() in y.lower():
                            self.options["figure_font"] = QtGui.QFont(x, pointSize=self.options["figure_font"].pointSize())
                            break
            plt.xkcd()

        with sns.plotting_context("paper"):
            self.g = sns.FacetGrid(self._table,
                                   col=self._col_factor,
                                   col_wrap=self._col_wrap,
                                   row=self._row_factor,
                                   sharex=True,
                                   sharey=True)

    def map_data(self, func):
        """
        Map the dataframe using :func:`func`.

        This method wraps the function :func:`func` so that a facet is
        plotted for the grouping variables. In order for this to work,
        :func:`func` has to take two values: `data`, which is a sub-
        dataframe after grouping, and `color`, which is currently not
        used, but which must be handled by `func` anyway.

        Technically, it calls :func:`FacetGrid.map_dataframe` from
        `seaborn` with `func` as a parameter if more than one plot
        is required. Otherwise, it calls `func` directly, as `FacetGrid`
        can have problems if only one plot is drawn.

        Parameters
        ----------
        func : function
            The plotting function.
        """
        if self._col_factor:
            self.g.map_dataframe(func)
        else:
            func(self._table, None)

    def get_grid_layout(self, n):
        """ Return a tuple containing a nrows, ncols pair that can be used to
        utilize the screen space more or less nicely for the number of grids
        n. This function doesn't take the window ratio into account yet, but
        always assumes a rectangular screen.

        This function is an adaption of the R function n2mfrow. """

        if n <= 3:
            return (n, 1)
        elif n <= 6:
            return ((n + 1) // 2, 2)
        elif n <= 12:
            return ((n + 2) // 3, 3)
        else:
            nrows = int(math.sqrt(n)) + 1
            ncols = int(n / nrows) + 1
            return (nrows, ncols)

    def draw(self, func=None, number_column=None):
        """ Do the visualization."""
        pass

    def set_data_source(self, model, view):
        """ Set the data for the the visualizer. Currently, the method takes
        two parameters, 'model' and 'view', which are expected to be instances
        of QAbstractDataModel and QTableView classes, respectively. """
        self._model = model
        self._view = view
        self.update_data()

    def get_palette(self):
        """
        Return a palette that is suitable for the data.
        """
        # choose the "Paired" palette if the number of grouping factor
        # levels is even and below 13, or the "Set3" palette otherwise:
        if len(self._levels) == 0:
            if len(self._groupby) == 1:
                return sns.color_palette("Paired")[0]
            else:
                palette_name = "Paired"
        elif len(self._levels[-1]) in (2, 4, 6):
            palette_name = "Paired"
        else:
            # use 'Set3', a quantitative palette, if there are two grouping
            # factors, or a palette diverging from Red to Purple otherwise:
            palette_name = "Paired" if len(self._groupby) == 2 else "RdPu"
        return sns.color_palette(palette_name)

    def update_data(self):
        """
        Update the internal representation of the model content so that
        it is usable by the visualizer.
        """

        if not options.cfg.main_window.Session:
            raise VisualizationNoDataError

        session = options.cfg.main_window.Session
        manager = managers.get_manager(options.cfg.MODE, session.Resource.name)

        header = self._view.horizontalHeader()
        view_columns = [self._model.header[header.logicalIndex(i)] for i in range(header.count())]
        view_columns = [x for x in view_columns if (
            x in options.cfg.main_window.Session.output_object.columns and
            x not in manager.hidden_columns)]

        column_order = view_columns
        column_order.append("coquery_invisible_corpus_id")

        view_columns = [session.translate_header(x) for x in view_columns]

        try:
            self._time_columns = session.Corpus.resource.time_features
        except NameError:
            self._time_columns = []

            # FIXME: reimplement row visibility
            #self._table = session.data_table[session.row_visibility[queries.TokenQuery]]
        dtypes = session.output_object[column_order].dropna().dtypes
        self._table = CoqTableModel.format_content(
            source=session.output_object[column_order].dropna(),
            num_to_str=False)
        self._table.columns = [session.translate_header(x) for x in self._table.columns]
        dtypes.index = self._table.columns.values

        # in order to prepare the layout of the figure, first determine
        # how many dimensions the data table has.
        self._factor_columns = [x for x in self._table.columns if (
            dtypes[x] in (bool, object) and
            x in view_columns and
            x not in self._time_columns and
            not x.startswith("func_DECAT"))]
        if options.cfg.verbose:
            print("DTYPES")
            print("output_object ", dtypes)
            print("_table        ", self._table.dtypes)
        self._number_columns = [x for x in self._table.columns if (
            dtypes[x] in (int, float) and
            x in view_columns and
            x not in self._time_columns and
            not x.startswith("coquery_invisible"))]
        if self.dimensionality:
            self._groupby = self._factor_columns[-self.dimensionality:]
        else:
            self._groupby = []

        self._levels = [sorted([utf8(y) for y in pd.unique(self._table[x].ravel())]) for x in self._groupby]

        if len(self._factor_columns) > self.dimensionality:
            self._col_factor = self._factor_columns[-self.dimensionality - 1]
        else:
            self._col_factor = None

        if len(self._factor_columns) > self.dimensionality + 1:
            self._row_factor = self._factor_columns[-self.dimensionality - 2]
            self._col_wrap = None
        else:
            self._row_factor = None
            if self._col_factor:
                self._col_wrap, _ = self.get_grid_layout(
                    len(pd.unique(self._table[self._col_factor].ravel())))
            else:
                self._col_wrap = None

        if options.cfg.verbose:
            print("factors:        ", self._factor_columns)
            print("grouping:       ", self._groupby)
            print("levels:         ", self._levels)
            print("col_wrap:       ", self._col_wrap)
            print("col_factor:     ", self._col_factor)
            print("row_factor:     ", self._row_factor)
            print("time_columns:   ", self._time_columns)
            print("number_columns: ", self._number_columns)

    def add_legend(self, levels=None, loc="lower left"):
        """
        Add a legend to the figure, using the current option settings.
        """
        if levels:
            legend_bar = [
                plt.Rectangle(
                    (0, 0), 1, 1,
                    fc=self.options["color_palette_values"][i],
                    edgecolor="none") for i, _ in enumerate(levels)
                ]
            self.g.fig.get_axes()[-1].legend(
                legend_bar, levels,
                ncol=self.options.get("label_legend_columns", 1),
                title=utf8(self.options.get("label_legend", "")),
                frameon=True,
                framealpha=0.7,
                loc=loc).draggable()
        else:
            self.g.fig.get_axes()[-1].legend(
                ncol=self.options.get("label_legend_columns", 1),
                title=utf8(self.options.get("label_legend", "")),
                frameon=True,
                framealpha=0.7,
                loc=loc).draggable()

    def adjust_fonts(self):
        """
        Adjust the fonts of the figure.

        The font sizes are either retrieved from the 'options' dictionary of
        this instance, or from the system default. If the default is used,
        the font size of axis tick labels and legend entries is scaled by
        the factor 0.833.
        """
        # Set font sizes of axis labels and ticks, separately for each axis:
        for ax in self.g.fig.axes:
            for element, font in [(ax.xaxis.label, "font_x_axis"),
                                  (ax.yaxis.label, "font_y_axis")]:
                self.options[font] = self.options.get(font, QtGui.QFont(self.options["figure_font"].family()))
                element.set_fontsize(self.options[font].pointSize())

            if not self.options.get("font_x_ticks"):
                self.options["font_x_ticks"] = QtGui.QFont(
                    self.options["font_x_axis"].family(), round(self.options["font_x_axis"].pointSize() / 1.2))
            for element in ax.get_xticklabels():
                element.set_fontsize(self.options["font_x_ticks"].pointSize())

            if not self.options.get("font_y_ticks"):
                self.options["font_y_ticks"] = QtGui.QFont(
                    self.options["font_y_axis"].family(), round(self.options["font_y_axis"].pointSize() / 1.2))
            for element in ax.get_yticklabels():
                element.set_fontsize(self.options["font_y_ticks"].pointSize())

        # Set font size of main title:
        if not self.options.get("font_main"):
            self.options["font_main"] = QtGui.QFont(
                    self.options["figure_font"].family(), round(self.options["figure_font"].pointSize() * 1.2))
        if "label_main" in self.options:
            plt.suptitle(utf8(self.options["label_main"]), size=self.options["font_main"].pointSize())

        if not self.options.get("font_legend"):
            self.options["font_legend"] = QtGui.QFont(self.options["figure_font"].family())
        if not self.options.get("font_legend_entries"):
            self.options["font_legend_entries"] = QtGui.QFont(
                self.options["font_legend"].family(), round(self.options["font_legend"].pointSize() / 1.2))

        # set font size of legend:
        legend = plt.gca().get_legend()
        if legend:
            legend.get_title().set_fontsize(self.options["font_legend"].pointSize())
            legend.get_title().set_fontname(self.options["font_legend"].family())
            for x in legend.get_texts():
                x.set_fontsize(self.options["font_legend_entries"].pointSize())
                x.set_fontname(self.options["font_legend_entries"].family())

    def get_levels(self, name):
        """
        Return a set containing all distinct values in the column 'name'.

        The values are returned in alphabetical order.

        Parameters
        ----------
        name : string
            The column name for which the unique values are requested

        Returns
        -------
        levels : list
            A unique list of all values that are contained in the specified
            data column.
        """
        return pd.unique(self._table[name].values.ravel())

    def get_ordered_row(self, index):
        """
        Return a list containing the values of the dictionary 'row', in
        the order of the columns in the table view.

        Parameters
        ----------
        index : int
            The row number

        Returns
        -------
        row : a list of values from the data table
        """
        return self._table.iloc[index]

    def adjust_axes(self):
        """
        Try to make the axis labels as readable as possible.

        This method tries to make both axis labels horizontal. If overlaps
        are created, the axis labels are rotated by 45 degrees. If there are
        still overlaps after this rotation, the labels are set to be vertical.
        """

        def _axis_ticklabels_overlap(labels, fig):
            """Return a boolean for whether the list of ticklabels have overlaps.

            Parameters
            ----------
            labels : list of ticklabels

            Returns
            -------
            overlap : boolean
                True if any of the labels overlap.

            """
            if not labels:
                return False

            # get a renderer even on backends where they are normally
            # unavailable, using method by "Stretch" (CC-BY-AS)
            # http://stackoverflow.com/a/22689498/5215507
            if hasattr(fig.canvas, "get_renderer"):
                renderer = fig.canvas.get_renderer()
            else:
                import io
                fig.canvas.print_pdf(io.BytesIO())
                renderer = fig._cachedRenderer

            try:
                bboxes = [l.get_window_extent(renderer) for l in labels]
                overlaps = [b.count_overlaps(bboxes) for b in bboxes]
                return max(overlaps) > 1
            except RuntimeError as e:
                print("RT", e)
                # Issue on macosx backend raises an error in the code above
                return False

        x_overlap = False

        for ax in self.g.fig.axes:
            #ax.get_xaxis().get_major_formatter().set_scientific(False)

            xtl = ax.get_xticklabels()
            ytl = ax.get_yticklabels()
            plt.setp(xtl, rotation="horizontal")
            plt.setp(ytl, rotation="horizontal")

            sns_overlap = sns.utils.axis_ticklabels_overlap(xtl)
            coq_overlap = _axis_ticklabels_overlap(xtl, self.g.fig)

            if sns_overlap != coq_overlap:
                S = "Incongruent overlap detection: sns: {}, coq: {}"
                print(S.format(sns_overlap, coq_overlap))

            if sns_overlap or coq_overlap:
                x_overlap = True

        if x_overlap:
            self.g.fig.autofmt_xdate()

    def get_plot_context(self):
        """
        Return one of the Seaborn contexts.

        The :mod:`Seaborn` library, which handles the overall layout of the
        :mod:`matplotlib` canvas that is used for drawing, provides different
        plotting contexts that manage font sizes, margins, and so on. The
        available contexts are: `paper`, `notebook`, `talk`, and `poster`,
        in increasing context size order.

        This method selects a suitable context based on the current font
        scaling that is determined by calling :func:`get_font_scale`. For
        larger font sizes, larger context sizes are chosen. This should
        adjust spacing for displays with different resolutions.

        Returns
        -------
        context : string
            A Seaborn context, either `paper`, `notebook`, `talk`, or `poster`
        """
        default = 12

        font_scale = options.cfg.app.font().pointSize() / default

        if font_scale <= 0.7:
            return "paper"
        if font_scale <= 1.2:
            return "notebook"
        if font_scale <= 1.5:
            return "talk"
        return "poster"


class Visualizer(CoqObject):
    axes_style = None
    plotting_context = "notebook"

    DEFAULT_TITLE = "(no title)"
    DEFAULT_XLABEL = "X"
    DEFAULT_YLABEL = "Y"

    def __init__(self, df, session):
        super(Visualizer, self).__init__()
        self.df = df
        self.session = session
        self.legend_levels = None
        self.legend_title = None
        self._last_legend_pos = None
        self._xlab = "X"
        self._ylab = "Y"

    def get_grid(self, **kwargs):
        kwargs["data"] = self.df
        with sns.axes_style(self.axes_style):
            with sns.plotting_context(self.plotting_context):
                grid = sns.FacetGrid(**kwargs)
        return grid

    def add_legend(self, grid, title=None, palette=None, levels=None, loc="lower left",
                   **kwargs):
        """
        Add a legend to the figure, using the current option settings.
        """
        #if levels:
            #legend_bar = [
                #plt.Rectangle(
                    #(0, 0), 1, 1,
                    #fc=self.options["color_palette_values"][i],
                    #edgecolor="none") for i, _ in enumerate(levels)
                #]
            #self.g.fig.get_axes()[-1].legend(
                #legend_bar, levels,
                #ncol=self.options.get("label_legend_columns", 1),
                #title=utf8(self.options.get("label_legend", "")),
                #frameon=True,
                #framealpha=0.7,
                #loc=loc).draggable()
        #else:
        grid.fig.legends = []
        if (title or self.legend_title) and self.legend_levels:
            col = sns.color_palette(palette,
                                    n_colors=len(self.legend_levels))

            legend_bar = [plt.Rectangle((0, 0), 1, 1,
                                        fc=col[i], edgecolor="none")
                        for i, _ in enumerate(self.legend_levels)]
            titlesize = kwargs.pop("titlesize")
            grid.fig.legend(legend_bar,
                    self.legend_levels,
                    title=title or self.legend_title,
                    frameon=True,
                    framealpha=0.7,
                    loc=loc, **kwargs).draggable()

            legend = grid.fig.legends[-1]
            legend.get_title().set_fontsize(titlesize)
            #if self._last_legend_pos:
                #grid.fig.legends[-1].set_bbox_to_anchor(
                    #self._last_legend_pos)
                #self._last_legend_pos = None


        #grid.fig.get_axes()[-1].legend(
            #ncol=self.options.get("label_legend_columns", 1),
            #title=utf8(self.options.get("label_legend", "")),
            #title="Legendary",
            #frameon=True,
            #framealpha=0.7,
            #loc=loc).draggable()

    def hide_legend(self, grid):
        try:
            legend = grid.fig.legends[-1]
        except IndexError:
            # no legend available, pass
            pass
        else:
            self._last_legend_pos = legend.get_bbox_to_anchor()
            legend.set_visible(False)
            grid.fig.legends = []

    def plot_facet(self, data, color,
                   x=None, y=None, levels_x=None, levels_y=None,
                   palette=None, **kwargs):
        pass

    def rotate_annotations(self, grid):
        for ax in grid.fig.axes:
            #ax.get_xaxis().get_major_formatter().set_scientific(False)

            xtl = ax.get_xticklabels()
            ytl = ax.get_yticklabels()
            plt.setp(xtl, rotation="horizontal")
            plt.setp(ytl, rotation="horizontal")

            sns_overlap = sns.utils.axis_ticklabels_overlap(xtl)

        if sns_overlap:
            grid.fig.autofmt_xdate()

    def set_annotations(self, grid, values):
        if values.get("title"):
            plt.suptitle(values.get("title"),
                         fontsize=values["size_title"],
                         fontname=values["figure_font"])

        if grid.col_names:
            for ax, title in zip(grid.axes.flat, grid.col_names):
                ax.set_title(title,
                             fontsize=int(values["size_title"]/1.2),
                             fontname=values["figure_font"])

        xlab = values.get("xlab") or self._xlab
        ylab = values.get("ylab") or self._ylab
        grid.set_xlabels(xlab,
                         fontsize=values["size_xlab"],
                         fontname=values["figure_font"])
        grid.set_ylabels(ylab,
                         fontsize=values["size_ylab"],
                         fontname=values["figure_font"])

        for ax in grid.fig.axes:
            for tick in (
                    ax.xaxis.get_major_ticks() + ax.xaxis.get_minor_ticks()):
                tick.label.set_fontsize(values["size_xticks"])
                tick.label.set_fontname(values["figure_font"])
            for tick in (
                    ax.yaxis.get_major_ticks() + ax.yaxis.get_minor_ticks()):
                tick.label.set_fontsize(values["size_yticks"])
                tick.label.set_fontname(values["figure_font"])

        self.rotate_annotations(grid)

    @staticmethod
    def dtype(feature, df):
        if feature:
            if feature.startswith("func_"):
                # FIXME: not all functions will return numerical data. For
                # the time being, only a few functions are included by the
                # designer, and all of them are in fact numerical, but this
                # might change at some point.
                return pd.np.float64
            try:
                return df.dtypes[feature]
            except KeyError:
                return None
        else:
            return None

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        """
        Validate the data types.

        The method returns True if the visualizer can handle an X and a Y
        variable of the given type. For example, a bar chart can handle
        two categorical variables, so a call validate_dtypes(object, object)
        will return True.

        Either argument can be None, which means that the corresponding
        dimension is not used.

        By default, the data is valid if at least one column name is not
        empty and both are distinct.

        Parameters
        ----------
        data_x, data_y : str
            A column name in the data frame, or None if the dimension is not
            used.

        df : DataFrame
            The data frame that the column names refer to

        session : Session
            The session in which the data frame was produced.

        Returns
        -------
        valid : bool
            True if the visualizer can handle these data types, or False
            otherwise.
        """
        return ((data_x or data_y) and (data_x != data_y) and
                len(df) > 0)

    @staticmethod
    def count_parameters(data_x, data_y, data_z, df, session):
        num_cols = df.select_dtypes(include=[pd.np.number]).columns
        cat_cols = df.select_dtypes(exclude=[pd.np.number]).columns
        categorical = [x for x in (data_x, data_y, data_z) if x in cat_cols]
        numeric = [x for x in (data_x, data_y, data_z) if x in num_cols]
        empty = [x for x in (data_x, data_y, data_z) if x is None]
        return categorical, numeric, empty


def get_grid_layout(n):
    """ Return a tuple containing a nrows, ncols pair that can be used to
    utilize the screen space more or less nicely for the number of grids
    n. This function doesn't take the window ratio into account yet, but
    always assumes a rectangular screen.

    This function is an adaption of the R function n2mfrow. """

    if n <= 3:
        return (n, 1)
    elif n <= 6:
        return ((n + 1) // 2, 2)
    elif n <= 12:
        return ((n + 2) // 3, 3)
    else:
        nrows = int(math.sqrt(n)) + 1
        ncols = int(n / nrows) + 1
        return (nrows, ncols)



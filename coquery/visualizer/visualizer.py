# -*- coding: utf-8 -*-
"""
visualizer.py is part of Coquery.

Copyright (c) 2016-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import collections

import scipy.stats as st
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from coquery.gui.pyqt_compat import QtCore
from coquery.defines import PALETTE_BW

from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum)

mpl.use("Qt5Agg")
mpl.rcParams["backend"] = "Qt5Agg"


class Aggregator(QtCore.QObject):
    def __init__(self, id_column=None):
        super(Aggregator, self).__init__()
        self.reset()
        self._id_column = id_column or "coquery_invisible_corpus_id"

    def reset(self):
        self._aggs_dict = collections.defaultdict(list)
        self._names_dict = collections.defaultdict(list)

    def add(self, column, fnc, name=None):
        if fnc == "mode":
            fnc = self._get_most_frequent
        elif fnc == "ci":
            fnc = self._get_interval
        self._aggs_dict[column].append(fnc)
        self._names_dict[column].append(name or column)

    def process(self, df, grouping):

        # if there is an id column in the data frame, make sure that the
        # aggregation samples the first ID
        if self._id_column not in df.columns:
            if self._id_column in self._aggs_dict:
                self._aggs_dict.remove(self._id_column)
            if self._id_column in self._names_dict:
                self._names_dict.remove(self._id_column)
        else:
            self.add(self._id_column, "first")

        df = df.groupby(grouping).agg(self._aggs_dict)
        agg_columns = []
        for names in [self._names_dict[x] for x in df.columns.levels[0]]:
            agg_columns += names
        df.columns = agg_columns
        df = df.reset_index()
        return df

    @staticmethod
    def _get_most_frequent(x):
        counts = x.value_counts()
        val = counts[counts == counts.max()].sort_index().index[0]
        return val

    @staticmethod
    def _get_interval(x):
        return x.sem() * st.t.ppf(1 - 0.025, len(x))


class Visualizer(QtCore.QObject):
    """
    Define a Visualizer class that can be used by the visualization designer.

    In order to be used by the visualization designer, Visualization classes
    have to implement the following methods:

    prepare_arguments()
    plot_facet()
    set_titles()
    colorize_elements()

    Other frequently used methods are:
    set_annotations()
    set_limits()
    """

    axes_style = None
    plotting_context = "notebook"

    DEFAULT_TITLE = "(no title)"
    DEFAULT_XLABEL = "X"
    DEFAULT_YLABEL = "Y"

    def __init__(self, df, session, id_column=None, limiter_fnc=None):
        super(Visualizer, self).__init__()
        self.df = df
        self.session = session
        self.legend_levels = None
        self.legend_title = None
        self.legend_palette = []
        self._last_legend_pos = None
        self.aggregator = Aggregator()
        self.colorizer = None
        self._xlab, self._ylab = self.DEFAULT_XLABEL, self.DEFAULT_YLABEL
        self._id_column = id_column
        self.frm_str = "{}"
        self._limiter_fnc = limiter_fnc
        self.experimental = False

    def get_default_index(self):
        return self._id_column

    def get_id_values(self, data):
        if self._id_column:
            values = data[self._id_column]
        else:
            values = pd.Series(data.index)
        return values

    def get_custom_widgets(self, *args, **kwargs):
        """
        Return a tuple containing a description of the custom widgets for
        this visualizer.

        The tuple contains three lists:
        (1) a list of widgets or layouts that will be added to the custom
            widget layout of the visualization designer
        (2) a list of signals that will activate the Apply button by calling
            enable_apply_button()
        (3) a list of signals that will update the widgets by calling
            update_widgets()
        """
        return ([], [], [])

    def update_values(self):
        """
        Update the visualizer-specific variables with values obtained from
        custom widgets.
        """

    def update_widgets(self):
        """
        Update the custom widgets in response to a change of a visualizer-
        specifc widget.
        """

    def get_grid(self, **kwargs):
        """
        This method is used to set up a FacetGrid object with the appropriate
        context settings.
        """
        kwargs["data"] = self.df
        with sns.axes_style(self.axes_style):
            with sns.plotting_context(self.plotting_context):
                grid = sns.FacetGrid(**kwargs)
        return grid

    def get_factor_frm(self):
        return "Most frequent {z}"

    def get_num_frm(self):
        return "Mean {z}"

    def get_default_frm(self):
        return "{z}"

    def suggest_legend(self):
        """
        Return True if a legend should be drawn, or False otherwise.

        The default behavior is to only draw a legend if both `x` and `y` are
        specified as data columns.

        Visualizers that need legends to be drawn under other condtions will
        have to override this method.
        """
        return (self.x and self.y)

    def get_legend(self, z):
        if not self.suggest_legend():
            return (None, [], None)

        if z:
            legend_title = self.colorizer.legend_title(z)
        else:
            legend_title = self.colorizer.legend_title(
                self.get_subordinated(self.x, self.y))

        legend_levels = self.colorizer.legend_levels()
        legend_palette = self.colorizer.get_palette(
            n=len(legend_levels or []))

        return (legend_title, legend_levels, legend_palette)

    def add_legend(self, grid, title=None, palette=None, levels=None,
                   loc="lower left", **kwargs):
        """
        Add a legend to the figure, using the current option settings.
        """
        grid.fig.legends = []

        (legend_title,
         legend_levels,
         legend_palette) = self.get_legend(self.z)

        if (title or legend_title) and legend_levels:
            col = legend_palette
            legend_bar = [plt.Rectangle((0, 0), 1, 1,
                                        fc=col[i], edgecolor="none")
                          for i, _ in enumerate(legend_levels)]
            titlesize = kwargs.pop("titlesize")
            grid.fig.legend(
                legend_bar,
                legend_levels,
                title=title or legend_title,
                frameon=True,
                framealpha=0.7,
                loc=loc, **kwargs).draggable()

            legend = grid.fig.legends[-1]
            legend.get_title().set_fontsize(titlesize)

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

    def prepare_arguments(self, data, x, y, z, levels_x, levels_y, **kwargs):
        return {}

    def plot_facet(self, **kwargs):
        """
        Plot the facet using the provided arguments.

        Returns
        -------
        lst : list
            A list of elements that can be colorized.
        """
        return []

    def get_colors(self, colorizer, elements, **kwargs):
        """
        Determine the color of each element.

        Arguments
        ---------
        colorizer : Colorizer
        elements : list
            A list of elements created by plot_facet()

        Returns
        -------
        lst : list
            A list of tuples representing Matplotlib color values.
        """
        return []

    def colorize_elements(self, elements, colors):
        """
        Colorize the elements created previously using the appropriate
        palette values.
        """
        pass

    def set_titles(self, **kwargs):
        self._xlab = self.DEFAULT_XLABEL
        self._ylab = self.DEFAULT_YLABEL

    def colorize(self):
        self.colors = self.get_colors(self.colorizer,
                                      self.elements,
                                      **self.params)
        self.colorize_elements(self.elements, self.colors)

    def draw(self, data, color, **kwargs):
        self.x = kwargs.get("x")
        self.y = kwargs.get("y")
        self.z = kwargs.get("z")
        self.levels_x = kwargs.get("levels_x")
        self.levels_y = kwargs.get("levels_y")
        self.levels_z = kwargs.get("levels_z")
        self.colorizer = kwargs.get("colorizer")

        self.params = self.prepare_arguments(data, **kwargs)
        self.elements = self.plot_facet(**self.params)
        if not isinstance(self.elements, list):
            raise ValueError("plot_facet() needs to return a list")
        self.set_titles(**self.params)
        self.colorize()

    def rotate_annotations(self, grid):
        x_overlap = False
        y_overlap = False

        for ax in grid.fig.axes:
            xtl = ax.get_xticklabels()
            ytl = ax.get_yticklabels()
            plt.setp(xtl, rotation="horizontal")
            plt.setp(ytl, rotation="horizontal")

            if sns.utils.axis_ticklabels_overlap(xtl):
                x_overlap = True
            if sns.utils.axis_ticklabels_overlap(ytl):
                y_overlap = True

        if x_overlap:
            grid.fig.autofmt_xdate()
        if y_overlap:
            grid.fig.autofmt_ydate()

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

    def set_limits(self, grid, values):
        pass

    @staticmethod
    def get_figure_size():
        fig = plt.gcf()
        bbox = fig.get_window_extent().transformed(
                    fig.dpi_scale_trans.inverted())
        return bbox.width * fig.dpi, bbox.height * fig.dpi

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
    def validate_data(data_x, data_y, df, session):
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
    def count_parameters(data_x, data_y, df, session):
        num_cols = df.select_dtypes(include=[pd.np.number]).columns
        cat_cols = df.select_dtypes(exclude=[pd.np.number]).columns
        categorical = [x for x in (data_x, data_y) if x in cat_cols]
        numeric = [x for x in (data_x, data_y) if x in num_cols]
        empty = [x for x in (data_x, data_y) if x is None]

        return categorical, numeric, empty

    @staticmethod
    def get_colorizer(data, palette, color_number,
                      z, levels_z=None, range_z=None):
        if z:
            if data[z].dtype == object:
                c = ColorizeByFactor(palette, color_number, levels_z)
            else:
                c = ColorizeByNum(palette, color_number, data[z],
                                  vrange=range_z)
        else:
            c = Colorizer(palette, color_number)
        return c

    def get_subordinated(self, x, y):
        """
        Determine whether the X or the Y variable is to be treated as the
        subordinate variable if both are specified.

        This method is used by the VisualizationDesigner to select the correct
        colorizer class.

        The default behavior is to return either X or Y if only one is
        specified, and to return Y if both are specified.

        This default behavior can be changed by descendant classes. The
        method can also return None as a value. In this case, the
        visualization designer will select a colorizer class that ignores the
        data variables. Normally, this will result in a colorizer that cycles
        through the palette values.

        Parameters
        ----------
        x, y : str or None
            The names of columns that may be considered when determining which
            element receives which color.

        Returns
        -------
        z : str or None
            The column name that should be used to determine the colorizers.
            Can be None.
        """
        if x and y:
            return y
        else:
            return x or y


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

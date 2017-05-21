# -*- coding: utf-8 -*-
"""
barplot.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections

from coquery.visualizer import visualizer as vis
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from seaborn.palettes import cubehelix_palette

from coquery.gui.pyqt_compat import QtCore
from coquery.functions import *
from coquery.managers import *


class Visualizer(vis.BaseVisualizer):
    dimensionality = 2
    numerical_axes = 1

    function_list = [Freq, FreqPMW, FreqNorm, Proportion, Percent]
    default_func = Freq

    def __init__(self, *args, **kwargs):
        try:
            self.percentage = kwargs.pop("percentage")
        except KeyError:
            self.percentage = False
        try:
            self.stacked = kwargs.pop("stacked")
        except KeyError:
            self.stacked = False

        super(Visualizer, self).__init__(*args, **kwargs)

        # The dictionary _rectangles manages the boxes for mouse-over lookup.

        # The keys are strings, and represent the grouping level of the plot.
        # The values are themselves dictionaries. The keys of these
        # dictionaries are tuples and coorrespond to the horizontal
        # coordinates of the respective box, i.e. (x0, x1). The associated
        # value is a tuple (label, count), where label is the factor level
        # of the box, and the count is either the frequency or the
        # percentage of that level.
        self._rectangles = dict()

    def set_defaults(self):
        """
        Set the plot defaults.
        """
        # choose the "Paired" palette if the number of grouping factor
        # levels is even and below 13, or the "Set3" palette otherwise:
        if len(self._levels[1 if len(self._groupby) == 2 else 0]) in (2, 4, 6, 8, 12):
            self.options["color_palette"] = "Paired"
        else:
            # use 'Set3', a quantitative palette, if there are two grouping
            # factors, or a palette diverging from Red to Purple otherwise:
            if len(self._groupby) == 2:
                self.options["color_palette"] = "Set3"
            else:
                self.options["color_palette"] = "RdPu"
        super(Visualizer, self).set_defaults()

        if self.percentage:
            self.options["label_x_axis"] = "Percentage"
        else:
            self.options["label_x_axis"] = "Frequency"

        session = options.cfg.main_window.Session

        if len(self._groupby) == 2:
            self.options["label_y_axis"] = session.translate_header(self._groupby[0])
            self.options["label_legend"] = session.translate_header(self._groupby[1])
        else:
            self.options["label_legend"] = session.translate_header(self._groupby[0])
            if self.percentage:
                self.options["label_y_axis"] = ""
            else:
                self.options["label_y_axis"] = session.translate_header(self._groupby[0])

    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(Visualizer, self).setup_figure()

    def format_coord(self, x, y, ax):
        """
        Get the box information at the given position.

        This method checks if the mouse is currently inside of a box. If so,
        return a string containing the grouping labels and the size of the
        box.

        As a side effect, this method also sets the tooltip for the widget so
        that the string is shown as the tooltip.

        Parameters
        ----------
        x, y : float
            The grid coordinates of the mouse cursor

        ax : Axis
            The axis that the mouse is currently located in

        Returns
        -------
        s : string
            A formatted string with the grouping levels and the size of the
            box.
        """
        y = y + 0.5

        row = self._rectangles[ax][int(y)]
        for rect in row:
            (x0, x1), (y0, y1) = rect
            if (x0 <= x <= x1) and (y0 <= y <= y1):
                label, value = row[rect]
                break
        else:
            self.set_tooltip("")
            return ""

        if len(self._groupby) > 1:
            prefix = "{} – ".format(self._levels[0][int(y)])
        else:
            prefix = ""

        if self.percentage:
            S = "{}{}: {:.1f}%".format(prefix, label, value)
        else:
            S = "{}{}: {}".format(prefix, label, int(value))

        self.set_tooltip(S)
        return S

    def set_hover(self):
        pass

    def add_rectangles(self, df, ax, stacked):
        """
        Add the information stored in the data frame as rectangles to
        the rectangle list for the axis.
        """
        if stacked:
            for row in df.index:
                offset = len(self._groupby) - 1
                edges = [0] + list(df.iloc[row].values.ravel())[offset:]
                last_content = 0
                for i in range(len(edges) - 1):
                    content = df.iloc[row][i+offset]
                    if content != last_content:
                        key = ((edges[i] + 0.0000001, edges[i+1]),
                               (row + 0.1, row + 0.91))
                        val = (df.columns[i+offset], content - last_content)
                        if ax not in self._rectangles:
                            self._rectangles[ax] = collections.defaultdict(dict)
                        self._rectangles[ax][row][key] = val
                        last_content = content
        else:
            # no stacks:
            if len(self._groupby) == 2:
                # two grouping factors:
                for row in df.index:
                    offset = len(self._groupby) - 1
                    height = 0.8 / len(self._levels[-1])
                    for i, col in enumerate(df.columns[offset:]):
                        content = df.iloc[row][i+offset]
                        if content:
                            y_pos = row + 0.1
                            key = (
                                (0, df.iloc[row][col]),
                                (y_pos + i * height, y_pos + (i+1) * height))
                            val = (col, df.iloc[row][col])
                            if ax not in self._rectangles:
                                self._rectangles[ax] = collections.defaultdict(dict)
                            self._rectangles[ax][row][key] = val
            else:
                # one grouping factor
                for i, col in enumerate(df.columns):
                    content = df.iloc[0][col]
                    if content:
                        key = (0, content), (i + 0.1, i + 0.9)
                        val = (col, content)
                        if ax not in self._rectangles:
                            self._rectangles[ax] = collections.defaultdict(dict)
                        self._rectangles[ax][i][key] = val

    def draw(self, func_x=default_func, column_x=None):
        """ Plot bar charts. """
        def plot_facet(data, color):
            session = options.cfg.main_window.Session
            if self.stacked:
                ax = plt.gca()

                if len(self._groupby) == 2:
                    data["COQ_FUNC"] = fun.evaluate(data, session=session)

                    df = data.pivot_table(index=self._groupby[0],
                                          columns=[self._groupby[-1]],
                                          values="COQ_FUNC",
                                          fill_value=0,
                                          dropna=False)
                    df = df.reset_index().fillna(0)
                    for x in self._levels[0]:
                        if x not in df[self._groupby[0]].values:
                            row = pd.Series(index=df.columns)
                            row[self._groupby[0]] = x
                            df = df.append(row.fillna(0), ignore_index=True)
                    # supply empty factor levels
                    for x in self._levels[-1]:
                        if x not in df.columns:
                            df[x] = 0
                    if self.percentage:
                        df[self._levels[-1]] = df[self._levels[-1]].apply(lambda x: 100 * x / x.sum(), axis=1).cumsum(axis=1)
                    else:
                        df[self._levels[-1]] = df[self._levels[-1]].cumsum(axis=1)

                    for i, stack in enumerate(self._levels[-1][::-1]):
                        tmp = sns.barplot(
                            x=stack,
                            y=self._groupby[0],
                            data=df,
                            color=self.options["color_palette_values"][::-1][i],
                            ax=plt.gca())
                else:
                    # one stacked bar (so, this is basically a spine chart)
                    #self.ct = data[self._groupby[0]].value_counts()[self._levels[-1]]
                    data["COQ_FUNC"] = fun.evaluate(data, session=session)
                    df = data[self._groupby + ["COQ_FUNC"]].drop_duplicates()
                    df["COQ_FUNC"] = df["COQ_FUNC"].cumsum()
                    df = df.reset_index(drop=True)
                    for n, i in enumerate(df.index[::-1]):
                        tmp = sns.barplot(
                            x="COQ_FUNC",
                            data=df.iloc[i],
                            color=self.options["color_palette_values"][::-1][n],
                            ax=plt.gca())

                # FIXME: reimplement mouse-over
                #self.add_rectangles(df, ax, stacked=True)
                #ax.format_coord = lambda x, y: self.format_coord(x, y, ax)
            else:
                ax = plt.gca()
                if self._value_column:
                    df = data
                    values = self._value_column
                else:
                    values = "COQ_FUNC"
                    df = data.assign(COQ_FUNC=lambda d: fun.evaluate(d,
                                                                     session=options.cfg.main_window.Session))

                df = df[self._groupby + [values]].drop_duplicates().fillna(0)

                kwargs = {"x": values,
                          "y": self._groupby[0],
                          "order": self._levels[0],
                          "palette": self.options["color_palette_values"],
                          "data": df}

                try:
                    kwargs.update({"hue": df[self._groupby[1]], "hue_order": self._levels[1]})
                except IndexError:
                    # use only one grouping variable
                    pass

                ax = sns.barplot(**kwargs)

                # FIXME: reimplement mouse-over
                #self.add_rectangles(df, ax, stacked=False)
                #ax.format_coord = lambda x, y: self.format_coord(x, y, ax)

        session = options.cfg.main_window.Session
        manager = get_manager(options.cfg.MODE, session.Resource.name)

        if self.percentage:
            self._levels[-1] = sorted(self._levels[-1])

        sns.despine(self.g.fig,
                    left=False, right=False, top=False, bottom=False)

        self._value_column = column_x

        if column_x is None:
            fun = func_x(columns=self._groupby, session=session)
            value_label = fun.get_label(manager=manager, session=session)
            self.options["label_x_axis"] = value_label
        else:
            self.options["label_x_axis"] = "mean({})".format(column_x)

        self.map_data(plot_facet)

        self.g.set_axis_labels(self.options["label_x_axis"],
                               self.options["label_y_axis"])

        if self.percentage:
            self.g.set(xlim=(0, 100))

        # Add axis labels:
        if self.stacked:
            # Stacked bars always show a legend
            if len(self._groupby) == 2:
                self.add_legend(self._levels[1], loc="lower right")
            else:
                self.add_legend(self._levels[0], loc="lower right")
        elif len(self._groupby) == 2:
            # Otherwise, only show a legend if there are grouped bars
            try:
                self.add_legend(self._levels[1], loc="lower right")
            except IndexError:
                pass


class BarPlot(vis.Visualizer):
    axes_style = "whitegrid"
    _default = "Frequency"

    def get_parameters(self, **kwargs):
        session = kwargs.get("session")
        self._ax = kwargs.get("ax", plt.gca())
        self._x = kwargs.get("x")
        self._y = kwargs.get("y")
        self._z = kwargs.get("z")
        self._levels_x = kwargs.get("levels_x")
        self._levels_y = kwargs.get("levels_y")
        self._hue = kwargs.get("hue")
        self._hue_order = kwargs.get("hue_order")
        self._palette = kwargs.get("palette", None)

        df = kwargs.get("data")
        params = {"palette": self._palette, "ax": self._ax}

        cat, num, _ = self.count_parameters(self._x, self._y, self._z,
                                            df, session)
        if num:
            numeric = num[0]
            if len(cat) < 2:
                if cat[0] == self._y:
                    self._x = None
                    self._levels_x = None
                else:
                    self._y = None
                    self._levels_x = None
            else:
                if self._x == numeric:
                    self._x = self._z
                    self._levels_x = self._hue_order
                    self._z = None
                    self._hue_order = None
                elif self._y == numeric:
                    self._y = self._z
                    self._levels_y = self._hue_order
                    self._z = None
                    self._hue_order = None

        else:
        ## check if one of the columns is a numeric column:
        #if self._x and self.dtype(self._x, df) != object:
            #numeric = self._x
            #self._x = None
            #self._levels_x = None
        #elif self._y and self.dtype(self._y, df) != object:
            #numeric = self._y
            #self._y = None
            #self._levels_y = None
        #else:
            #if self._z and self.dtype(self._z, df) != object:
                #numeric = self._z
            #else:
                # if there is no numeric column, use the provided function,
                #  or Freq() as the default function:
                numeric = self._default
                data_columns = [col for col in (self._x, self._y) if col]
                func = kwargs.get("func", Freq)
                fun = func(columns=data_columns, session=session)
                df[numeric] = fun.evaluate(df, session)
                df = (df.drop("coquery_invisible_corpus_id", axis=1)
                        .drop_duplicates().fillna(0).reset_index(drop=True))

        params.update({"data": df,
                       "x": self._x, "y": self._y, "order": None,
                       "hue": None, "hue_order": None})

        if self._x and not self._y:
            # show vertical bars
            params.update({"y": numeric, "order": self._levels_x})
            self._xlab = self._x
            self._ylab = numeric
        elif self._y and not self._x:
            # show horizontal bars
            params.update({"x": numeric, "order": self._levels_y})
            self._xlab = numeric
            self._ylab = self._y
        else:
            # show horizontal, hued bars
            params.update({"x": numeric, "y": self._y,
                           "order": self._levels_y,
                           "hue": self._x, "hue_order": self._levels_x})
            self._xlab = numeric
            self._ylab = self._y

        return params

    def plot_facet(self, **kwargs):
        params = self.get_parameters(**kwargs)
        ax = sns.barplot(**params)

        if self._x and self._y:
            self.legend_title = params["hue"]
            self.legend_levels = params["hue_order"]

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 1 or len(cat) == 0:
            return False
        return True


class StackedBars(BarPlot):
    """
    Stacked bar chart
    """

    def transform(self, series):
        return series.values.cumsum()

    def group_transform(self, grp, numeric):
        return grp[numeric].cumsum()

    def plot_facet(self, **kwargs):
        params = self.get_parameters(**kwargs)
        data = params["data"]
        x = params["x"]
        y = params["y"]
        levels_x = params.get("levels_x")
        levels_y = params.get("levels_y")
        hue = params["hue"]
        numeric = self._default

        if data.dtypes[x] != object:
            numeric = x
            axis = y
        else:
            numeric = y
            axis = x

        if hue and sum([bool(x), bool(y)]) == 1:
            order = hue
            hue = None

        if hue:
            data = data.sort_values([y, hue]).reset_index(drop=True)
            data[numeric] = (data.groupby(y)
                                 .apply(self.group_transform, numeric)
                                 .reset_index(0)[numeric])

            levels = params["hue_order"][::-1]
            kwargs = {"x": numeric, "y": axis}
            if x and y and hue:
                self._xlab = self._default
            elif x:
                self._xlab = x
                self._ylab = numeric
            else:
                self._xlab = numeric
                self._ylab = y
            split = hue
        else:
            data = data.sort_values(axis)
            data[numeric] = self.transform(data[numeric])
            levels = params["order"][::-1]
            if x == numeric:
                kwargs = {"x": x, "y": None}
                self._xlab = self._default
                self._ylab = y
            else:
                kwargs = {"y": y, "x": None}
                self._xlab = x
                self._ylab = self._default
            split = axis

        col = sns.color_palette(params["palette"],
                                n_colors=len(levels))[::-1]

        for n, val in enumerate(levels):
            if split != axis:
                d = {axis: params["order"], split: val}
                df = (pd.merge(data[data[split] == val],
                            pd.DataFrame(d),
                            how="right")
                        .fillna(0)
                        .sort_values(by=axis)
                        .reset_index(drop=True))
            else:
                df = data[data[split] == val]
            sns.barplot(data=df,
                        color=col[n], ax=params["ax"], **kwargs)

        if split == axis:
            self.legend_title = split
            self.legend_levels = params["order"]
        else:
            self.legend_title = hue
            self.legend_levels = params["hue_order"]

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 1 or len(cat) == 0:
            return False
        if len(num) == 1 and len(cat) == 1:
            return False
        return True

class PercentBars(StackedBars):
    """
    Stacked bar chart showing percentages
    """
    _default = "Percentage"

    def transform(self, series):
        return (series * 100 / series.sum()).cumsum()

    def group_transform(self, grp, numeric):
        return (grp[numeric] * 100 / grp[numeric].sum()).cumsum()

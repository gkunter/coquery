# -*- coding: utf-8 -*-
"""
densityplot.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from coquery.visualizer import visualizer as vis
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

from coquery.errors import *
from coquery import options
from coquery.functions import *

sequential_palettes = ["Blues", "Reds", "Greens", "Oranges", "Purples",
                       "BuGn", "BuPu", "RdPu", "OrRd", "YlGn",
                       "BrBG", "PiYG", "PRGn", "PuOr", "RdBu", "RdGy"]

class Visualizer(vis.BaseVisualizer):
    dimensionality = 1
    numerical_axes = 2
    function_list = [Freq, FreqPMW, FreqNorm, Proportion, Percent]
    default_func = Freq

    def __init__(self, *args, **kwargs):
        try:
            self.cumulative = kwargs.pop("cumulative")
        except KeyError:
            self.cumulative = False
        self._plot_frequency = True
        super(Visualizer, self).__init__(*args, **kwargs)
        self.set_data_table(options.cfg.main_window.Session.output_object)

    def set_defaults(self):
        self.options["color_palette"] = "Paired"
        if self._levels:
            self.options["color_number"] = len(self._levels[-1])
        else:
            self.options["color_number"] = 1

        if len(self._number_columns) == 0:
            raise VisualizationInvalidDataError

        if len(self._number_columns) == 1:
            if self.cumulative:
                self.options["label_y_axis"] = "Cumulative probability"
            else:
                self.options["label_y_axis"] = "Density"
        else:
            self.options["label_y_axis"] = self._number_columns[-2]
        self.options["label_x_axis"] = self._number_columns[-1]

        if len(self._groupby) == 1:
            self.options["label_legend"] = self._groupby[-1]

        super(Visualizer, self).set_defaults()

    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(Visualizer, self).setup_figure()

    def draw(self, func_x=default_func, column_x=None, **kwargs):

        def plot_facet(data, color, **kwargs):
            if self._value_column or True:
                df = data.dropna(subset=self._number_columns[-2:])
                x_values = self._value_column
            else:
                x_values = "COQ_FUNC"
                df = data.dropna(subset=self._number_columns[-2:]).assign(COQ_FUNC=lambda d: fun.evaluate(d))

            if self._levels != []:
                colors = dict(zip(
                    self._levels[0],
                    self.options["color_palette_values"]))
            else:
                colors = self.options["color_palette_values"]
            try:
                if len(self._number_columns) > 1:
                    if len(self._groupby) > 0:
                        for i, x in enumerate(self._levels[-1]):
                            sns.kdeplot(
                                data=df[df[self._groupby[-1]] == x][self._number_columns[-2]],
                                data2=df[df[self._groupby[-1]] == x][self._number_columns[-1]],
                                shade=True,
                                cmap=sequential_palettes[i % len(sequential_palettes)],
                                shade_lowest=False,
                                alpha=0.5,
                                ax=plt.gca())

                    else:
                        sns.kdeplot(
                            data=df[self._number_columns[-2]],
                            data2=df[self._number_columns[-1]],
                            shade=True,
                            cmap=self.options["color_palette"],
                            shade_lowest=False,
                            ax=plt.gca())
                else:
                    if len(self._groupby) > 0:
                        for x in self._levels[-1]:
                            sns.kdeplot(
                                data=df[df[self._groupby[-1]] == x][x_values],
                                color=colors[x],
                                shade=True,
                                cumulative=self.cumulative,
                                label=x,
                                ax=plt.gca())
                    else:
                        sns.kdeplot(data=df[x_values],
                                    color=colors[-1],
                                    shade=True,
                                    cumulative=self.cumulative,
                                    ax=plt.gca())

            except Exception as e:
                print(e)

        self._value_column = self._number_columns[-1]
        #print(2)
        #if column_x is None:
            #fun = func_x(columns=self._groupby, session=options.cfg.main_window.Session)
            #value_label = fun.get_label(session=options.cfg.main_window.Session)
        #else:
            #value_label = column_x
        #print(3)
        self.map_data(plot_facet)
        self.g.set_axis_labels(self.options["label_x_axis"], self.options["label_y_axis"])

        if self._levels:

            category_levels = self._levels[-1]

            if len(self._number_columns) > 1:
                legend_bar = [
                    plt.Rectangle(
                        (0, 0), 1, 1,
                        fc=sns.color_palette(sequential_palettes[i], 1)[0],
                        edgecolor="none") for i, _ in enumerate(category_levels)]

            else:
                legend_bar = [
                    plt.Rectangle(
                        (0, 0), 1, 1,
                        fc=self.options["color_palette_values"][i],
                        edgecolor="none") for i, _ in enumerate(category_levels)]

            try:
                self.g.fig.get_axes()[-1].legend(
                    legend_bar, category_levels,
                    ncol=self.options["label_legend_columns"],
                    title=self.options["label_legend"],
                    frameon=True,
                    framealpha=0.7,
                    loc="lower left").draggable()
            except Exception as e:
                print(e)
                raise e

class DensityPlot(vis.Visualizer):
    cumulative = False
    axes_style = "whitegrid"
    _default = "Density estimate"

    def plot_facet(self, data, color, **kwargs):
        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        levels_x = kwargs.get("levels_x")
        levels_y = kwargs.get("levels_y")
        levels_z = kwargs.get("levels_z")

        num = []
        category = None
        levels = None
        self._xlab = self._default
        self._ylab = self._default
        if x and self.dtype(x, data) != object:
            num.append(x)
            self.flip = False
            self._xlab = x
        else:
            category = x
            levels = levels_x
        if y and self.dtype(y, data) != object:
            num.append(y)
            self.flip = True
            self._ylab = y
        else:
            category = y
            levels = levels_y
        if z and self.dtype(z, data) == object:
            category = z
            levels = levels_z

        if not category:
            col = self.get_palette(kwargs["palette"], kwargs["color_number"])
            if len(num) == 1:
                sns.kdeplot(data[num[0]], vertical=self.flip,
                            color=col[0],
                            cumulative=self.cumulative)
            else:
                sns.kdeplot(data[num[0]], data[num[1]],
                            #cmap=kwargs["palette"],
                            colors=col,
                            cmap=None,
                            shade=True, shade_lowest=False,
                            alpha=0.5)
        else:
            for i, level in enumerate(levels):
                df = data[data[category] == level]
                if len(num) == 1:
                    col = self.get_palette(kwargs["palette"], len(levels))
                    sns.kdeplot(df[num[0]], vertical=self.flip,
                                color=col[i],
                                cumulative=self.cumulative)
                else:
                    pal = sequential_palettes[i % len(sequential_palettes)]
                    sns.kdeplot(df[num[0]], df[num[1]],
                                cmap=pal,
                                shade=True, shade_lowest=False, alpha=0.5)
                    self.legend_palette += sns.color_palette(pal, 1)

        if levels:
            self.legend_title = category
            self.legend_levels = levels

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) in [1, 2]:
            return True
        else:
            return False

        if len(num) > 2 or len(num) == 0 or len(cat) > 1:
            return False
        else:
            return True


class CumulativePlot(DensityPlot):
    cumulative = True
    _default = "Cumulative probability"

    def plot_facet(self, data, color, **kwargs):
        super(CumulativePlot, self).plot_facet(data, color, **kwargs)
        ax = plt.gca()
        if self.flip:
            ax.set_ylim(0, 1)
        else:
            ax.set_xlim(0, 1)

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) != 1:
            return False
        if len(cat) > 1:
            return False
        else:
            return True


logger = logging.getLogger(NAME)

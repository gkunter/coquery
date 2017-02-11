# -*- coding: utf-8 -*-
""" 
scatterplot.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

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

    def __init__(self, *args, **kwargs):
        super(Visualizer, self).__init__(*args, **kwargs)
        #self.set_data_table(options.cfg.main_window.Session.output_object)

    def set_defaults(self):
        self.options["color_palette"] = "Paired"
        if self._levels:
            self.options["color_number"] = len(self._levels[-1])
        else:
            self.options["color_number"] = 1

        if len(self._number_columns) == 0:
            raise VisualizationInvalidDataError

        if len(self._number_columns) == 1:
            self.options["label_x_axis"] = "Index"
        else:
            self.options["label_x_axis"] = self._number_columns[-2]
        self.options["label_y_axis"] = self._number_columns[-1]
        
        if len(self._groupby) == 1:
            self.options["label_legend"] = self._groupby[-1]
            
        super(Visualizer, self).set_defaults()

    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(Visualizer, self).setup_figure()

    def draw(self, column_x=None, **kwargs):
        
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
                            sns.regplot(
                                x=df[df[self._groupby[-1]] == x][self._number_columns[-2]],
                                y=df[df[self._groupby[-1]] == x][self._number_columns[-1]],
                                ax=plt.gca())

                    else:
                        sns.regplot(
                            x=df[self._number_columns[-2]],
                            y=df[self._number_columns[-1]],
                            ax=plt.gca())
                else:
                    if len(self._groupby) > 0:
                        for x in self._levels[-1]:
                            y = df[df[self._groupby[-1]] == x][x_values]
                            sns.regplot(
                                x=range(len(y)),
                                y=y,
                                ax=plt.gca())
                    else:
                        y = df[x_values]
                        sns.kdeplot(x=range(len(y)),
                                    y=df[x_values],
                                    ax=plt.gca())
                                    
            except Exception as e:
                print(e)
            
        self._value_column = self._number_columns[-1]
        self.map_data(plot_facet)
        #self.g.set_axis_labels(self.options["label_x_axis"], self.options["label_y_axis"])

        #if self._levels:

            #category_levels = self._levels[-1]

            #if len(self._number_columns) > 1:
                #legend_bar = [
                    #plt.Rectangle(
                        #(0, 0), 1, 1,
                        #fc=sns.color_palette(sequential_palettes[i], 1)[0],
                        #edgecolor="none") for i, _ in enumerate(category_levels)]

            #else:
                #legend_bar = [
                    #plt.Rectangle(
                        #(0, 0), 1, 1,
                        #fc=self.options["color_palette_values"][i],
                        #edgecolor="none") for i, _ in enumerate(category_levels)]

            #try:
                #self.g.fig.get_axes()[-1].legend(
                    #legend_bar, category_levels,
                    #ncol=self.options["label_legend_columns"],
                    #title=self.options["label_legend"],
                    #frameon=True,
                    #framealpha=0.7,
                    #loc="lower left").draggable()
            #except Exception as e:
                #print(e)
                #raise e


class ScatterPlot(vis.Visualizer):
    fit_reg = False

    def plot_facet(self, data, color, **kwargs):
        x = kwargs.get("x")
        y = kwargs.get("y")
        levels_x = kwargs.get("levels_x")
        levels_y = kwargs.get("levels_y")

        if self.dtype(x, data) == object or self.dtype(y, data) == object:
            if self.dtype(y, data) == object:
                category = y
                numeric = x
                levels = levels_y
            else:
                category = x
                numeric = y
                levels = levels_x
            cols = sns.color_palette(kwargs["palette"], n_colors=len(levels))
            for i, val in enumerate(levels):
                df = data[data[category] == val]
                if category == x:
                    ax = sns.regplot(x=df.index.values, y=df[numeric],
                                     color=cols[i],
                                     fit_reg=self.fit_reg,
                                     ax=kwargs.get("ax", plt.gca()))
                else:
                    ax = sns.regplot(x=df[numeric], y=df.index.values,
                                     color=cols[i],
                                     fit_reg=self.fit_reg,
                                     ax=kwargs.get("ax", plt.gca()))
        else:
            if x is None:
                val_x = pd.Series(range(len(data)), name=x)
                val_y = data[y]
            elif y is None:
                val_x = data[x]
                val_y = pd.Series(range(len(data)), name=y)
            else:
                val_x = data[x]
                val_y = data[y]
            col = sns.color_palette(kwargs["palette"], n_colors=1)
            ax = sns.regplot(val_x, val_y,
                             fit_reg=self.fit_reg,
                             ax=kwargs.get("ax", plt.gca()))

    def get_grid(self, **kwargs):
        with sns.axes_style("whitegrid"):
            grid = super(ScatterPlot, self).get_grid(**kwargs)
        return grid

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 2 or len(num) == 0 or len(cat) > 1:
            return False
        else:
            return True

class RegressionPlot(ScatterPlot):
    fit_reg = True

logger = logging.getLogger(NAME)

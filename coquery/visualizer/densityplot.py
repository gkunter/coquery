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

class Visualizer(vis.BaseVisualizer):
    dimensionality = 1
    _plot_frequency = True
    vmax = 0

    def __init__(self, *args, **kwargs):
        try:
            self.cumulative = kwargs.pop("cumulative")
        except KeyError:
            self.cumulative = False
        self.set_data_table(options.cfg.main_window.Session.output_object)
        self._plot_frequency = True
        super(Visualizer, self).__init__(*args, **kwargs)

    def set_defaults(self):
        self.options["color_palette"] = "Paired"
        if self._levels:
            self.options["color_number"] = len(self._levels[-1])
        else:
            self.options["color_number"] = 1

        if len(self._number_columns) == 1:
            if self.cumulative:
                self.options["label_y_axis"] = "Cumulative probability"
            else:
                self.options["label_y_axis"] = "Density"
            self.options["label_x_axis"] = self._number_columns[-1]
            if len(self._groupby) == 1:
                self.options["label_legend"] = self._groupby[-1]
            
        super(Visualizer, self).set_defaults()


    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(Visualizer, self).setup_figure()

    def draw(self, **kwargs):
        
        def plot_facet(data, color, **kwargs):
            colors = dict(zip(
                self._levels[0],
                self.options["color_palette_values"]))
            try:
                if len(self._number_columns) > 1:
                    sns.kdeplot(
                        data[self._number_columns[-2]],
                        data[self._number_columns[-1]],
                        shade=True,
                        shade_lowest=False,
                        color=color,
                        cumulative=self.cumulative,
                        ax=plt.gca())
                elif len(self._number_columns) == 1:
                    if len(self._groupby) == 1:
                        for x in self._levels[-1]:
                            sns.kdeplot(data[data[self._groupby[-1]] == x][self._number_columns[-1]],
                                color=colors[x],
                                shade=True,
                                cumulative=self.cumulative,
                                ax=plt.gca())
            except Exception as e:
                print(e)
            #ct.plot(kind="area", ax=plt.gca(), stacked=True, color=self.get_palette(), **kwargs)
            
        self.map_data(plot_facet)
        
        self.g.set_axis_labels(self.options["label_x_axis"], self.options["label_y_axis"])

        category_levels = self._levels[-1]
        legend_bar = [
            plt.Rectangle(
                (0, 0), 1, 1,
                fc=self.options["color_palette_values"][i], 
                edgecolor="none") for i, _ in enumerate(category_levels)
            ]
        try:
            print(legend_bar)
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
        
logger = logging.getLogger(NAME)

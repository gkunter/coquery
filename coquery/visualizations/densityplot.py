# -*- coding: utf-8 -*-
""" 
densityplot.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import visualizer as vis
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from errors import *
import options
import logging
import __init__

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

    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(Visualizer, self).setup_figure()

    def draw(self, **kwargs):
        
        def plot_facet(data, color, **kwargs):
            try:
                if len(self._number_columns) > 1:
                    sns.kdeplot(
                        data[self._number_columns[-2]],
                        data[self._number_columns[-1]],
                        shade=True,
                        color=color,
                        cumulative=self.cumulative,
                        ax=plt.gca())
                elif len(self._number_columns) == 1:
                    sns.kdeplot(data[self._number_columns[-1]],
                             color=color,
                             shade=True,
                             cumulative=self.cumulative,
                             ax=plt.gca())
            except Exception as e:
                print(e)
            #ct.plot(kind="area", ax=plt.gca(), stacked=True, color=self.get_palette(), **kwargs)
            
        self.map_data(plot_facet)
        
        self.g.set_axis_labels(self.options["label_x_axis"], self.options["label_y_axis"])
        
logger = logging.getLogger(__init__.NAME)

# -*- coding: utf-8 -*-
""" 
barcodeplot.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from coquery import options
from coquery.defines import *
from coquery.unicode import utf8

from coquery.visualizer import visualizer as vis

import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def lineplot(x=None, y=None, data=None, order=None, palette=None,
             linewidth=0, ax=None, orient="v", **kwargs):
    if ax is None:
        ax = plt.gca()
    if not order:
        order = y.unique()
    order = list(sorted(order))
    func = plt.vlines if orient=="v" else plt.hlines
    for i, lev in enumerate(order):
        func(x[y == lev], i + 0.025, i + 0.975, colors=palette[i], linewidth=1)

    if len(order) < 2:
        ax.set(yticks=[])
    else:
        ax.set(yticks=[0.5 + n for n in range(len(order))])
        ax.set(yticklabels=order)
    ax.set(xlim=(0, max(x)))
    ax.set(ylim=(len(order), 0))
    return ax

class Visualizer(vis.BaseVisualizer):
    dimensionality = 1
    
    def format_coord(self, x, y, title):
        return "{}: <b>{}</b>, Corpus position: {}".format(
            self._groupby[-1], sorted(self._levels[-1])[int(y)], int(x))
    
    def onclick(self, event):
        try:
            options.cfg.main_window.result_cell_clicked(token_id=int(event.xdata))
        except TypeError:
            pass
    
    def set_defaults(self):
        self.options["color_palette"] = "Paired"
        self.options["color_number"] = len(self._levels[0])
        super(Visualizer, self).set_defaults()
        self.options["label_x_axis"] = "Corpus position"
        if not self._levels or len(self._levels[0]) < 2:
            self.options["label_y_axis"] = ""
        else:
            self.options["label_y_axis"] = self._groupby[0]

    def setup_figure(self):
        with sns.axes_style("white"):
            super(Visualizer, self).setup_figure()
    
    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in a subplot matching the factor level 
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        def plot_facet(data, color):
            lineplot(
                x=data["coquery_invisible_corpus_id"],
                y=data[self._groupby[-1]],
                order=self._levels[-1],
                palette=self.options["color_palette_values"],
                data=data)

        #sns.despine(self.g.fig, 
                    #left=False, right=False, top=False, bottom=False)

        self.map_data(plot_facet)
        self.g.set_axis_labels(utf8(self.options["label_x_axis"]), utf8(self.options["label_y_axis"]))
        self.g.set(xlim=(0, options.cfg.main_window.Session.Corpus.get_corpus_size()))

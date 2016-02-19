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

import unittest
import options
from defines import *

import visualizer as vis
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def lineplot(a, level=0, start=0, end=1, axis="x", color="black", ax=None, **kwargs):
    """Plot datapoints in an array as sticks on an axis.

    Parameters
    ----------
    a : vector
        1D array of observations.
    height : scalar, optional
        Height of ticks as proportion of the axis.
    axis : {'x' | 'y'}, optional
        Axis to draw rugplot on.
    ax : matplotlib axes
        Axes to draw plot into; otherwise grabs current axes.
    kwargs : key, value mappings
        Other keyword arguments are passed to ``axvline`` or ``axhline``.

    Returns
    -------
    ax : matplotlib axes
        The Axes object with the plot on it.

    """
    if ax is None:
        ax = plt.gca()
    vertical = kwargs.pop("vertical", axis == "y")
    func = ax.axhline if vertical else ax.axvline
    kwargs.setdefault("linewidth", 1)
    a.reset_index(drop=True, inplace=True)
    level.reset_index(drop=True, inplace=True)
    for i in a.index:
        func(a[i], start[level[i]], end[level[i]], color=color[level[i]], **kwargs)
    return ax

class Visualizer(vis.BaseVisualizer):
    dimensionality = 1
    
    def format_coord(self, x, y, title):
        return "Corpus position: {}".format(int(x))
    
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
            offset = 0.025 * (1 / len(self._levels[0]))
            starts = dict(zip(
                self._levels[0],
                [offset + x / len(self._levels[0]) for x in range(len(self._levels[0]))]))
            ends = dict(zip(
                self._levels[0],
                [(x+1) / len(self._levels[0]) - offset for x in range(len(self._levels[0]))]))
                #sns.color_palette("Paired", len(self._levels[0]))))
            colors = dict(zip(
                self._levels[0],
                self.options["color_palette_values"]))
            lineplot(data.coquery_invisible_corpus_id,
                     level=data[self._groupby[-1]],
                     start=starts, end=ends, color=colors, ax=plt.gca())

        sns.despine(self.g.fig, 
                    left=False, right=False, top=False, bottom=False)

        self._ticks = [(x+0.5) / len(self._levels[0]) for x in range(len(self._levels[0]))]

        self.map_data(plot_facet)

        if not self._levels or len(self._levels[0]) < 2:
            self.g.set(yticks=[])
        else:
            self.g.set(yticks=self._ticks)
            self.g.set(yticklabels=self._levels[0])
        self.g.set_axis_labels(self.options["label_x_axis"], self.options["label_y_axis"])
        self.g.set(xlim=(0, options.cfg.main_window.Session.Corpus.get_corpus_size()))

""" Barcode plot visualization """

from __future__ import division
from __future__ import print_function

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
    #a = np.asarray(a)
    vertical = kwargs.pop("vertical", axis == "y")
    func = ax.axhline if vertical else ax.axvline
    kwargs.setdefault("linewidth", 1)
    for i, pt in enumerate(a):
        print(i, level[i], pt, start[i], end[i])
        func(pt, start[i], end[i], color="black", **kwargs)
    return ax

class BarcodeVisualizer(vis.Visualizer):
    visualize_frequency = False
    dimensionality = 0

    def setup_figure(self):
        with sns.axes_style("white"):
            super(BarcodeVisualizer, self).setup_figure()
        #self._starts = [x / len(self._levels[0]) for x in range(len(self._levels[0]))]
        #self._ends = [0.95 * (x+1) / len(self._levels[0]) for x in range(len(self._levels[0]))]
        #self._ticks = [(x+0.5) / len(self._levels[0]) for x in range(len(self._levels[0]))]
        #self._colors = sns.color_palette("Paired", len(self._levels[0]))
    
    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in a subplot matching the factor level 
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        #self._starts = [x / len(self._levels[0]) for x in range(len(self._levels[0]))]
        #self._ends = [0.95 * (x+1) / len(self._levels[0]) for x in range(len(self._levels[0]))]
        #self._ticks = [(x+0.5) / len(self._levels[0]) for x in range(len(self._levels[0]))]
        #self._colors = sns.color_palette("Paired", len(self._levels[0]))


        
        sns.despine(self.g.fig, 
                    left=False, right=False, top=False, bottom=False)
        #print(
            #self._table[self._groupby[0]], 
            #self._table[self._groupby[0]].apply(lambda x: self._levels[0].index(x)))
        #levels = self._table[self._groupby[0]].apply(lambda x: self._levels[0].index(x))
        #self.g.map(lineplot, 
                   #"coquery_invisible_corpus_id", 
                   #level=levels,
                   #start=self._table[self._groupby[0]].apply(
                       #lambda x: self._starts[self._levels[0].index(x)]),
                   #end=self._table[self._groupby[0]].apply(
                       #lambda x: self._ends[self._levels[0].index(x)]),
                   #color=self._table[self._groupby[0]].apply(
                       #lambda x: self._colors[self._levels[0].index(x)]))
        self.g.map(sns.rugplot, "coquery_invisible_corpus_id", height=1)

        if not self._levels or len(self._levels[0]) < 2:
            self.g.set(yticks=[])
            self.g.set_axis_labels("Corpus position", "")
        else:
            self.g.set(yticks=self._ticks)
            self.g.set(yticklabels=self._levels[0])
            self.g.set_axis_labels("Corpus position", self._groupby[0])
        self.g.set_titles(fontweight="bold", size=options.cfg.app.font().pointSize() * self.get_font_scale())
        #self.figure.tight_layout()

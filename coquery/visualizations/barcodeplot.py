""" Barcode plot visualization """

from __future__ import division
from __future__ import print_function

import unittest
import options
from defines import *

import visualizer as vis
import seaborn as sns
import pandas as pd
import matplotlib as mpl

class BarcodeVisualizer(vis.Visualizer):
    visualize_frequency = False

    def setup_figure(self):
        super(BarcodeVisualizer, self).setup_figure()

        # get the last factor in the current table. 
        try:
            col_factor = [x for x in self._table.columns if not x.startswith("coquery_invisible")][-1]
        except IndexError:
            col_factor = None
        # get the penultimate factor in the current table. 
        try:
            row_factor = [x for x in self._table.columns if not x.startswith("coquery_invisible")][-2]
            col_wrap=None
        except IndexError:
            # only a single factor in the table, use column wrapping:
            row_factor=None
            _, col_wrap = self.get_grid_layout(len(pd.unique(self._table[col_factor])))

        mpl.rc("font",
               {"family": "normal", "weight": "bold", "size": 22})

        self.g = sns.FacetGrid(self._table, 
                               xlim=(0, options.cfg.main_window.Session.Corpus.get_corpus_size()),
                               ylim=(0, 1),
                               col_wrap=col_wrap,
                               #row=row_factor,
                               col=col_factor, sharex=True, sharey=True)
        self.figure = self.g.fig

    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in a subplot matching the factor level 
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        
        sns.despine(self.g.fig, left=True, right=True)
        with sns.axes_style("white"):
            self.g.map(sns.rugplot, "coquery_invisible_corpus_id", height=1, color=sns.color_palette("Paired", 1)[0])

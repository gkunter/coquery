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
import matplotlib.pyplot as plt

class HeatmapVisualizer(vis.Visualizer):
    visualize_frequency = True

    def setup_figure(self):
        with sns.plotting_context(self.get_plot_context(), font_scale=self.get_font_scale()):
            super(HeatmapVisualizer, self).setup_figure()
        print(self.figure)
        print(dir(self.figure))

    def update_data(self):
        super(HeatmapVisualizer, self).update_data()
        # get the last factor in the current table. 
        columns = [x for x in self._table.columns if not x.startswith("coquery_invisible")]
        if len(columns) == 1:
            self.col_factor = columns[0]
            self.row_factor = None
            self.col_wrap = True
        elif len(columns) >= 2:
            self.col_factor = columns[-2]
            self.row_factor = columns[-1]
            self.col_wrap = False
        else:
            self.col_factor = None
            self.row_factor = None

    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in a subplot matching the factor level 
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        
        #self.setup_axis("Y")
        sns.heatmap(pd.crosstab(
            self._table[self.row_factor], 
            self._table[self.col_factor]), ax=self.subplot)
        self.setup_axis("Y")
        self.setup_axis("X")
        #self.figure.autofmt_xdate()
        self.figure.tight_layout()

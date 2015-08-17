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
    dimensionality=2
    
    def setup_figure(self):
        with sns.axes_style("white"):
            super(HeatmapVisualizer, self).setup_figure()

    #def update_data(self):
        #super(HeatmapVisualizer, self).update_data()
        ## get the last factor in the current table. 
        #columns = [x for x in self._table.columns if not x.startswith("coquery_invisible")]
        #if len(columns) == 1:
            #self.col_factor = columns[0]
            #self.row_factor = None
            #self.col_wrap = True
        #elif len(columns) >= 2:
            #self.col_factor = columns[-2]
            #self.row_factor = columns[-1]
            #self.col_wrap = False
        #else:
            #self.col_factor = None
            #self.row_factor = None

    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in a subplot matching the factor level 
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        
        def get_crosstab(data, row_fact,col_fact, row_names, col_names):
            ct = pd.crosstab(data[row_fact], data[col_fact])
            ct = ct.reindex_axis(row_names, axis=0).fillna(0)
            ct = ct.reindex_axis(col_names, axis=1).fillna(0)
            return ct
        
        if len(self._groupby) < 2:
            tmp = pd.Series([""] * len(self._table[self._groupby[0]]), name="")
            tab = pd.crosstab(tmp, self._table[self._groupby[0]])
        else:
            FUN = lambda data, color: sns.heatmap(
                get_crosstab(
                    data, 
                    self._groupby[0], 
                    self._groupby[1], 
                    self._levels[0], 
                    self._levels[1]),
                robust=True,
                annot=True,
                cbar=False,
                vmax=vmax,
                linewidths=1)

        vmax = pd.crosstab(
            [self._table[x] for x in [self._row_factor, self._groupby[0]] if x <> None],
            [self._table[x] for x in [self._col_factor, self._groupby[1]] if x <> None]).values.max()

        self.g.map_dataframe(FUN)

        self.setup_axis("Y")
        self.setup_axis("X")
        
        self.g.fig.tight_layout()

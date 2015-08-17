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

class BarchartVisualizer(vis.Visualizer):
    visualize_frequency = False
    dimensionality = 2

    #def setup_figure(self):
        #with sns.axes_style("white"):
            #super(BarchartVisualizer, self).setup_figure()
    
    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in a subplot matching the factor level 
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        
        sns.despine(self.g.fig, 
                    left=False, right=False, top=False, bottom=False)

        if len(self._groupby) == 2:
            self.g.map(sns.countplot, 
                       y=self._table[self._groupby[0]], 
                       data=self._table, 
                       hue=self._table[self._groupby[1]], 
                       palette="Greens_d") 
        else:
            self.g.map_dataframe(sns.countplot, 
                        y=self._groupby[0],
                        palette="Greens_d",
                        data=self._table,) 


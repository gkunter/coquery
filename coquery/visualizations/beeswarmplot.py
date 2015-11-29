""" Beeswarm visualization """

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

from beeswarm import *

class Visualizer(vis.BaseVisualizer):
    dimensionality = 1

    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(Visualizer, self).setup_figure()
 
    def draw(self):
        def plot_facet(data, color):
            #col = self.get_colors_for_factor(self.col_factor, rgb_string=True)
            
            values = [data[data[self._groupby[-1]] == x]["coquery_invisible_corpus_id"].values for x in self._levels[-1]]
            
            beeswarm(
                values=values,
                positions=range(len(self._levels[-1])),
                ax=plt.gca())
        
        self.g.map_dataframe(plot_facet)
        self.g.set_axis_labels(self._groupby[-1], "Corpus position")
        self.g.set_titles(fontweight="bold", size=options.cfg.app.font().pointSize() * self.get_font_scale())
        self.g.set(xticklabels=self._levels[-1])
        #self.setup_axis("X", self.col_factor)
        #self.subplot.set_xlabel(self.col_factor)
        #self.subplot.set_ylabel("Corpus position")
        #self.figure.tight_layout()

        
        #sns.despine(self.g.fig, left=False, right=False, top=False, bottom=False)
        #self.g.map(beeswarm,
            #values=[self._table["coquery_invisible_corpus_id"]],
                   ##positions=self._table["coquery_invisible_corpus_id"],
                   #col=["blue"], method="square")
        #self.g.set(yticks=[])
        #self.g.set_axis_labels("Corpus position", "")
        #self.g.set_titles(fontweight="bold", size=options.cfg.app.font().pointSize() * self.get_font_scale())

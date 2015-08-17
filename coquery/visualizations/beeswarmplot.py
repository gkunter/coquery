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

class BeeswarmVisualizer(vis.Visualizer):
    visualize_frequency = True

    def setup_figure(self):
        with sns.plotting_context(self.get_plot_context(), font_scale=self.get_font_scale()):
            super(BeeswarmVisualizer, self).setup_figure()
        # get the last factor in the current table. 
        try:
            self.col_factor = [x for x in self._table.columns if not x.startswith("coquery_invisible")][-1]
        except IndexError:
            self.col_factor = None
        # get the penultimate factor in the current table. 
        try:
            self.row_factor = [x for x in self._table.columns if not x.startswith("coquery_invisible")][-2]
            col_wrap=None
        except IndexError:
            # only a single factor in the table, use column wrapping:
            self.row_factor=None
            _, col_wrap = self.get_grid_layout(len(pd.unique(self._table[self.col_factor])))

        #mpl.rc("font",
               #{"family": "normal", "weight": "bold", "size": 22})

        #with sns.plotting_context(self.get_plot_context(), font_scale=self.get_font_scale()):
            #with sns.axes_style("white"):
                #self.g = sns.FacetGrid(self._table, 
                                    ##xlim=(0, options.cfg.main_window.Session.Corpus.get_corpus_size()),
                                    ##ylim=(0, 1),
                                    #col_wrap=col_wrap,
                                    ##row=row_factor,
                                    #col=self.col_factor, sharex=True, sharey=True)
        #self.figure = self.g.fig

    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in a subplot matching the factor level 
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        
        grouped = self._table.groupby(self.col_factor)
        val=[self._table.iloc[grouped.groups[x]]["coquery_invisible_corpus_id"] for x in grouped.groups]
        
        col = self.get_colors_for_factor(self.col_factor, rgb_string=True)
        beeswarm(
            values=val,
            #positions=self._table["coquery_invisible_corpus_id"],
            col=col.values(), method="hex", labels=col.keys(), ax = self.subplot)
        
        self.setup_axis("X", self.col_factor)
        self.subplot.set_xlabel(self.col_factor)
        self.subplot.set_ylabel("Corpus position")
        self.figure.tight_layout()

        
        #sns.despine(self.g.fig, left=False, right=False, top=False, bottom=False)
        #self.g.map(beeswarm,
            #values=[self._table["coquery_invisible_corpus_id"]],
                   ##positions=self._table["coquery_invisible_corpus_id"],
                   #col=["blue"], method="square")
        #self.g.set(yticks=[])
        #self.g.set_axis_labels("Corpus position", "")
        #self.g.set_titles(fontweight="bold", size=options.cfg.app.font().pointSize() * self.get_font_scale())

""" Barcode plot visualization """

from __future__ import division
from __future__ import print_function

import unittest
import options
from defines import *

from visualizer import Visualizer

class BarcodeVisualizer(Visualizer):
    visualize_frequency = False

    def setup_figure(self):
        #super(BarcodeVisualizer, self).setup_figure()
        #self.subplot = self.figure.add_subplot(111)
        #self.subplot.set_ylim(0, 1)
        #self.subplot.set_xlim(0, options.cfg.main_window.Session.Corpus.get_corpus_size())

        self.figure = self.get_default_figure()
        
        self.subplot_dict = {}
        
        self.table_structure = self.get_table_levels()

        # prod contains a list of lists, where each inner list represents one
        # possible combination of factor levels from the current table
        # structure.
        prod = [self.get_ordered_row(x) for x in dict_product(self.table_structure)]

        # Try to choose a suitable grid layout for the figure. If there are
        # more than just a single factor, there is one column for each factor 
        # level of the last column in the data table. If there is only one 
        # factor, the levels are layed out so that there is an appropriate
        # number of rows and columns.
        
        if len(self.table_structure) > 1:
            # Get the number of the factor levels in the last column of the
            # data table:
            ncols = len(self.table_structure[self.table_structure.keys()[-1]])
            nrows = len(prod) // ncols
        else:
            nrows, ncols = self.get_grid_layout(len(prod))

        # Create a subplot for each factor level combination in the table
        # structure. The subplots are accessible by tuples of factor levels.
        for i, row in enumerate(prod):
            key = tuple(row)
            self.subplot_dict[key] = self.figure.add_subplot(
                nrows, ncols, i + 1)
            self.subplot_dict[key].set_ylim(0, 1)
            self.subplot_dict[key].set_xlim(0, options.cfg.main_window.Session.Corpus.get_corpus_size())
            self.subplot_dict[key].set_xlabel(", ".join(key))

    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in the subplot matching the factor level 
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        
        #bins = collections.Counter()
        #for x in self._content:
            #bins[x["coquery_invisible_corpus_id"] // 10000] += 1
        #largest_bin = max(bins.values())
        #for x in bins:
            #self.subplot.bar([x * 10000 for x in bins.keys()], bins.values(), width=9500)
            
        for row in self._model.content:
            l = tuple(self.get_ordered_row(row))
            self.subplot_dict[l].vlines(row["coquery_invisible_corpus_id"], 0, 1, colors=[(0, 0, 0, 0.25)])
            
        self.figure.tight_layout()

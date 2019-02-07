# -*- coding: utf-8 -*-
"""
beeswarmplot.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function

import seaborn as sns
import matplotlib.pyplot as plt

from coquery.visualizer import barcodeplot


class BeeswarmPlot(barcodeplot.BarcodePlot):
    axes_style = "whitegrid"
    name = "Beeswarm plot"
    icon = "Beeswarm_plot"

    NUM_COLUMN = "coquery_invisible_corpus_id"

    def prepare_arguments(self, data, x, y, z,
                          levels_x, levels_y):
        if not x and not y:
            if not self.force_horizontal:
                X = [""] * len(data)
                Y = data[self.NUM_COLUMN]
                self.horizontal = True
            else:
                X = data[self.NUM_COLUMN]
                Y = [""] * len(data)
                self.horizontal = False
            O = None
        elif x:
            X = data[x]
            Y = data[self.NUM_COLUMN]
            O = levels_x
            self.horizontal = True
        else:
            X = data[self.NUM_COLUMN]
            Y = data[y]
            O = levels_y
            self.horizontal = False

        if self.z:
            self.colorizer.set_reversed(True)
            hue = self.colorizer.mpt_to_hex(
                self.colorizer.get_hues(data[z]))
            self.colorizer.set_reversed(False)
        else:
            hue = self.colorizer.mpt_to_hex(
                self.colorizer.get_palette(n=len(data)))
        self.colors = hue

        return {"x": X, "y": Y, "order": O}

    def set_titles(self):
        if not self.x and not self.y:
            if not self.force_horizontal:
                self._xlab = ""
            else:
                self._ylab = ""
        elif self.x:
            self._xlab = self.x
        else:
            self._ylab = self.y

        if not self.horizontal:
            self._xlab = self.DEFAULT_LABEL
        else:
            self._ylab = self.DEFAULT_LABEL

    def colorize_artists(self):
        self.artists.set_color(self.colors)

    def plot_facet(self, data, color, **kwargs):
        self.args = self.prepare_arguments(data, self.x, self.y, self.z,
                                           self.levels_x, self.levels_y)

        ax = sns.swarmplot(**self.args)
        self.artists = ax.collections[0]


provided_visualizations = [BeeswarmPlot]

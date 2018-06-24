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

from coquery import options

from coquery.visualizer import visualizer as vis
from coquery.visualizer import barcodeplot


class BeeswarmPlot(barcodeplot.BarcodePlot):
    axes_style = "whitegrid"
    name = "Beeswarm plot"
    icon = "Beeswarm_plot"

    def plot_facet(self, data, color,
                   x=None, y=None, z=None,
                   levels_x=None, levels_y=None,
                   levels_z=None, range_z=None,
                   palette="", color_number=None, **kwargs):

        if not x and not y:
            if not self.force_horizontal:
                X = [""] * len(data)
                Y = data["coquery_invisible_corpus_id"]
                self._xlab = ""
                self.horizontal = True
            else:
                X = data["coquery_invisible_corpus_id"]
                Y = [""] * len(data)
                self._ylab = ""
                self.horizontal = False
            O = None
        elif x:
            X = data[x]
            Y = data["coquery_invisible_corpus_id"]
            O = levels_x
            self._xlab = x
            self.horizontal = True
        else:
            X = data["coquery_invisible_corpus_id"]
            Y = data[y]
            O = levels_y
            self._ylab = y
            self.horizontal = False

        if not self.horizontal:
            self._xlab = self.DEFAULT_LABEL
        else:
            self._ylab = self.DEFAULT_LABEL

        self._colorizer = self.get_colorizer(data, palette, color_number,
                                                z, levels_z, range_z)

        if z:
            palette = self._colorizer.get_palette(n=len(levels_z))
            self._colorizer.set_reversed(True)
            hue = self._colorizer.mpt_to_hex(
                self.get_colors(data, self._colorizer, z))
            self._colorizer.set_reversed(False)

        else:
            palette = self._colorizer.get_palette()
            hue = self._colorizer.mpt_to_hex(
                self.get_colors(data, self._colorizer, z))


        self.legend_title = self._colorizer.legend_title(z)
        self.legend_palette = palette[::-1]
        if not (z == x or z == y):
            self.legend_levels = self._colorizer.legend_levels()
        else:
            self.legend_levels = []

        sns.swarmplot(x=X, y=Y, order=O, hue=hue, palette=palette)
        return kwargs.get("ax", plt.gca())


provided_visualizations = [BeeswarmPlot]

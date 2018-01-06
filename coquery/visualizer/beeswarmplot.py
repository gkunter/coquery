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
                   levels_x=None, levels_y=None, levels_z=None,
                   palette="", **kwargs):
        params = {"data": data}
        corpus_id = "coquery_invisible_corpus_id"

        if not x and not y:
            self._xlab = self.DEFAULT_LABEL
            self._ylab = ""
            params.update({"x": corpus_id,
                           "y": [""] * len(data),
                           "palette": self.get_palette(palette, 1)})
        elif y:
            self._xlab = self.DEFAULT_LABEL
            self._ylab = y
            params.update({"x": corpus_id,
                           "y": y,
                           "order": levels_y})
            if not x:
                params.update({"palette": self.get_palette(palette,
                                                           len(levels_y))})
            else:
                self.legend_title = x
                self.legend_levels = levels_x
                params.update({"hue": x,
                               "hue_order": levels_x,
                               "palette": self.get_palette(palette,
                                                           len(levels_x))})
        else:
            self.horizontal = False
            self._xlab = x
            self._ylab = self.DEFAULT_LABEL
            params.update({"x": x,
                           "y": corpus_id,
                           "order": levels_x,
                           "palette": self.get_palette(palette,
                                                       len(levels_x))})

        if z and not (x and y):
            self.legend_title = z
            self.legend_levels = levels_z
            params.update({"hue": z,
                           "hue_order": levels_z,
                           "palette": self.get_palette(palette,
                                                       len(levels_z))})

        sns.swarmplot(**params)
        return kwargs.get("ax", plt.gca())

provided_visualizations = [BeeswarmPlot]

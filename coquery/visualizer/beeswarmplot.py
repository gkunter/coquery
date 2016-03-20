# -*- coding: utf-8 -*-
""" 
beeswarmplot.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from coquery import options
from coquery.defines import *
from coquery.gui.pyqt_compat import QtGui

from coquery.visualizer import visualizer as vis

class Visualizer(vis.BaseVisualizer):
    dimensionality = 1

    def format_coord(self, x, y, title):
        return "{}: <b>{}</b>, corpus position: {}".format(
            self._groupby[-1], sorted(self._levels[-1])[int(round(x))], int(y))
    
    def setup_figure(self):
        with sns.axes_style("ticks"):
            super(Visualizer, self).setup_figure()
 
    def set_defaults(self):
        self.options["color_palette"] = "Paired"
        self.options["color_number"] = len(self._levels[0])
        super(Visualizer, self).set_defaults()
        self.options["label_y_axis"] = "Corpus position"
        if not self._levels or len(self._levels[0]) < 2:
            self.options["label_x_axis"] = ""
        else:
            self.options["label_x_axis"] = self._groupby[0]

    def onclick(self, event):
        try:
            options.cfg.main_window.result_cell_clicked(token_id=int(event.ydata))
        except TypeError:
            pass
 
    def draw(self):
        def plot_facet(data, color):
            if hasattr(sns, "swarmplot"):
                ax = sns.swarmplot(
                    x=data[self._groupby[-1]],
                    y=data["coquery_invisible_corpus_id"],
                    order=sorted(self._levels[-1]),
                    palette=self.options["color_palette_values"],
                    data=data)
            else:
                # If the current Seaborn version doesn't provide swarmplots
                # yet (they were introduced in 0.7.0), use an alternative 
                # swarm package (see https://github.com/mgymrek/pybeeswarm)
                import beeswarm
                values = [data[data[self._groupby[-1]] == x]["coquery_invisible_corpus_id"].values for x in sorted(self._levels[-1])]
                col = ["#{:02X}{:02X}{:02X}".format(int(255*r), int(255*g), int(255*b)) for r, g, b in self.options["color_palette_values"]][:len(values)]
                beeswarm.beeswarm(
                    values=values,
                    method="center",
                    s=5,
                    positions=range(len(self._levels[-1])),
                    col=col, 
                    ax=plt.gca())
        
        self.g.map_dataframe(plot_facet)

        self.g.set(ylim=(0, options.cfg.main_window.Session.Corpus.get_corpus_size()))
        self.g.set_axis_labels(self.options["label_x_axis"], self.options["label_y_axis"])
        if not hasattr(sns, "swarmplot"):
            self.g.set(xticklabels=self._levels[-1])

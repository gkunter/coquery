# -*- coding: utf-8 -*-
"""
beeswarmplot.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

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


class Visualizer(vis.BaseVisualizer):
    dimensionality = 1
    function_list = []

    def format_coord(self, x, y, title):
        return "{}: <b>{}</b>, corpus position: {}".format(
            self._groupby[-1],
            sorted(self._levels[-1])[int(round(x))], int(y))

    def setup_figure(self):
        with sns.axes_style("ticks"):
            super(Visualizer, self).setup_figure()

    def set_defaults(self):
        session = options.cfg.main_window.Session

        self.options["color_palette"] = "Paired"
        self.options["color_number"] = len(self._levels[0])
        super(Visualizer, self).set_defaults()
        self.options["label_y_axis"] = "Corpus position"
        if not self._levels or len(self._levels[0]) < 2:
            self.options["label_x_axis"] = ""
        else:
            self.options["label_x_axis"] = session.translate_header(
                self._groupby[0])

    def onclick(self, event):
        try:
            # FIXME: instead of using event.ydata, the closest token id
            # should be used for lookup. The discussion at
            # http://stackoverflow.com/questions/12141150/ may help to
            # do this efficiently
            options.cfg.main_window.result_cell_clicked(
                token_id=int(event.ydata))
        except TypeError:
            pass

    def draw(self):
        def plot_facet(data, color):
            sns.swarmplot(
                x=data[self._groupby[-1]],
                y=data["coquery_invisible_corpus_id"],
                order=sorted(self._levels[-1]),
                palette=self.options["color_palette_values"],
                data=data)

        self.g.map_dataframe(plot_facet)

        ymax = options.cfg.main_window.Session.Corpus.get_corpus_size()
        self.g.set(ylim=(0, ymax))
        self.g.set_axis_labels(self.options["label_x_axis"],
                               self.options["label_y_axis"])


class BeeswarmPlot(barcodeplot.BarcodePlot):
    axes_style = "whitegrid"

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

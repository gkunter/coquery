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
                   x=None, y=None, levels_x=None, levels_y=None,
                   palette=None, **kwargs):
        ax = kwargs.get("ax", plt.gca())
        corpus_id = "coquery_invisible_corpus_id"

        params = {"data": data, "palette": palette}
        self.horizontal = True
        if not x and not y:
            params.update({"x": corpus_id}),
            self._xlab = x
            self._ylab = ""
        elif x and not y:
            params.update({"x": x, "y": corpus_id, "order": levels_x})
            self.horizontal = False
            self._xlab = x
            self._ylab = "Corpus position"
        elif y and not x:
            params.update({"y": y, "x": corpus_id, "order": levels_y})
            self._xlab = "Corpus position"
            self._ylab = y
        elif x and y:
            params.update({"x": corpus_id, "y": y, "hue": x,
                           "order": levels_y, "hue_order": levels_x})
            self._xlab = "Corpus position"
            self._ylab = y

        sns.swarmplot(**params)
        return ax

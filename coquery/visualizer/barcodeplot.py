# -*- coding: utf-8 -*-
"""
barcodeplot.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from coquery import options
from coquery.unicode import utf8

from coquery.visualizer import visualizer as vis

import seaborn as sns
import matplotlib.pyplot as plt


class Visualizer(vis.BaseVisualizer):
    dimensionality = 1
    function_list = []

    def format_coord(self, x, y, title):
        return "{}: <b>{}</b>, Corpus position: {}".format(
            self._groupby[-1], sorted(self._levels[-1])[int(y)], int(x))

    def onclick(self, event):
        try:
            # FIXME: instead of using event.xdata, the closest token id
            # should be used for lookup. The discussion at
            # http://stackoverflow.com/questions/12141150/ may help to
            # do this efficiently
            options.cfg.main_window.result_cell_clicked(
                token_id=int(event.xdata))
        except TypeError:
            pass

    def set_defaults(self):
        session = options.cfg.main_window.Session
        self.options["color_palette"] = "Paired"
        self.options["color_number"] = len(self._levels[0])
        super(Visualizer, self).set_defaults()
        self.options["label_x_axis"] = "Corpus position"
        if not self._levels or len(self._levels[0]) < 2:
            self.options["label_y_axis"] = ""
        else:
            self.options["label_y_axis"] = session.translate_header(
                self._groupby[0])

    def setup_figure(self):
        with sns.axes_style("white"):
            super(Visualizer, self).setup_figure()

    def draw(self):
        self.map_data(self.plot_facet,
                      x=self._groupby[-1],
                      levels_x=self._levels[-1])
        self.g.set_axis_labels(utf8(self.options["label_x_axis"]),
                               utf8(self.options["label_y_axis"]))
        xmax = options.cfg.main_window.Session.Corpus.get_corpus_size()
        self.g.set(xlim=(0, xmax))

    @staticmethod
    def plot_facet(data, color, **kwargs):
        """
        Plot a barcode plot.

        In a barcode plot, each token is represented by a line drawn at the
        location of the corresponding corpus id.
        """

        ax = kwargs.get("ax", plt.gca())
        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        levels_x = kwargs.get("levels_x", None)
        levels_y = kwargs.get("levels_y", None)
        palette = kwargs.get("palette", None)

        if x is None and y is None:
            order = [1]
            orient = "v"
        else:
            if y:
                x = y
                y = None
                orient = "h"
                order = levels_y
            else:
                orient = "v"
                order = levels_x

        order = list(sorted(order))
        if len(order) == 1:
            ticks = []
            labels = []
        else:
            ticks = [0.5 + n for n in range(len(order))]
            labels = order

        if orient == "h":
            ylim = 0, data["coquery_invisible_corpus_id"].max()
            xlim = len(order), 0
            line_func = plt.hlines
            ax.set(xticks=ticks, xticklabels=labels)
        else:
            xlim = 0, data["coquery_invisible_corpus_id"].max()
            ylim = len(order), 0
            line_func = plt.vlines
            ax.set(yticks=ticks, yticklabels=labels)
        ax.set(xlim=xlim, ylim=ylim)

        if palette is None:
            palette = [color] * len(order)

        if x:
            for i, lev in enumerate(order):
                line_func(
                    data["coquery_invisible_corpus_id"][data[x] == lev],
                    i + 0.025, i + 0.975, colors=palette[i], linewidth=1)
        else:
            line_func(data["coquery_invisible_corpus_id"],
                      0.025, 0.975, colors=palette[0], linewidth=1)

        return ax

    @staticmethod
    def get_grid(**kwargs):
        with sns.axes_style("white"):
            grid = vis.BaseVisualizer.get_grid(**kwargs)
        return grid

    @staticmethod
    def validate_data(data_x, data_y, df, session):
        if data_x is not None and data_y is not None:
            return False
        if data_x is None and data_y is None:
            return True

        dtype_x = Visualizer.dtype(data_x, df)
        dtype_y = Visualizer.dtype(data_y, df)

        return ((dtype_x == object and dtype_y is None) or
                (dtype_y == object and dtype_x is None))

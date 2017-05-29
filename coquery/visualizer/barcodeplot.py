# -*- coding: utf-8 -*-
"""
barcodeplot.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from __future__ import unicode_literals

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


from coquery import options
from coquery.unicode import utf8

from coquery.visualizer import visualizer as vis


def lineplot(x=None, y=None, data=None, order=None, palette=None,
             linewidth=0, ax=None, orient="v", **kwargs):
    if ax is None:
        ax = plt.gca()
    if not order:
        order = y.unique()
    order = list(sorted(order))
    func = plt.vlines if orient=="v" else plt.hlines
    for i, lev in enumerate(order):
        func(x[y == lev], i + 0.025, i + 0.975, colors=palette[i], linewidth=1)

    if len(order) < 2:
        ax.set(yticks=[])
    else:
        ax.set(yticks=[0.5 + n for n in range(len(order))])
        ax.set(yticklabels=order)
    ax.set(xlim=(0, max(x)))
    ax.set(ylim=(len(order), 0))
    return ax

class Visualizer(vis.BaseVisualizer):
    dimensionality = 1

    def format_coord(self, x, y, title):
        return "{}: <b>{}</b>, Corpus position: {}".format(
            self._groupby[-1], sorted(self._levels[-1])[int(y)], int(x))

    def onclick(self, event):
        try:
            options.cfg.main_window.result_cell_clicked(token_id=int(event.xdata))
        except TypeError:
            pass

    def set_defaults(self):
        self.options["color_palette"] = "Paired"
        self.options["color_number"] = len(self._levels[0])
        super(Visualizer, self).set_defaults()
        self.options["label_x_axis"] = "Corpus position"
        if not self._levels or len(self._levels[0]) < 2:
            self.options["label_y_axis"] = ""
        else:
            self.options["label_y_axis"] = self._groupby[0]

    def setup_figure(self):
        with sns.axes_style("white"):
            super(Visualizer, self).setup_figure()

    def draw(self):
        """ Plot a vertical line for each token in the current data table.
        The line is drawn in a subplot matching the factor level
        combination in that row. The horizontal position corresponds to the
        token id so that tokens that occur in the same part of the corpus
        will also have lines that are placed close to each other. """
        def plot_facet(data, color):
            lineplot(
                x=data["coquery_invisible_corpus_id"],
                y=data[self._groupby[-1]],
                order=self._levels[-1],
                palette=self.options["color_palette_values"],
                data=data)

        #sns.despine(self.g.fig,
                    #left=False, right=False, top=False, bottom=False)

        self.map_data(plot_facet)
        self.g.set_axis_labels(utf8(self.options["label_x_axis"]), utf8(self.options["label_y_axis"]))
        self.g.set(xlim=(0, options.cfg.main_window.Session.Corpus.get_corpus_size(filters=[])))

class BarcodePlot(vis.Visualizer):
    axes_style = "white"
    TOP = 0.975
    BOTTOM = 0.025
    COLOR = None

    def plot_facet(self,
                   data, color, x=None, y=None, levels_x=None, levels_y=None,
                   palette=None, rug=None, rug_color="Black",
                   **kwargs):
        """
        Plot a barcode plot.

        In a barcode plot, each token is represented by a line drawn at the
        location of the corresponding corpus id.
        """
        def get_colors(palette, levels):
            return sns.color_palette(palette, n_colors=len(levels))

        corpus_id = data["coquery_invisible_corpus_id"]

        if x and not y:
            self.horizontal = False
            ax_kwargs = {"xticks": 0.5 + pd.np.arange(len(levels_x)),
                         "xticklabels": levels_x}
            if levels_x:
                ax_kwargs["xlim"] = (0, len(levels_x))

            xval = data[x].apply(lambda x: levels_x.index(x))
            colors = get_colors(palette, levels_x)
            cols = xval.apply(lambda x: colors[x])
            if rug:
                if "top" in rug:
                    plt.hlines(corpus_id, xval + 0.9, xval + 1, cols)
                if "bottom" in rug:
                    plt.hlines(corpus_id, xval, xval + 0.1, cols)
            else:
                plt.hlines(corpus_id, xval + self.BOTTOM, xval + self.TOP, cols)
            self._ylab = "Corpus position"
            if levels_x:
                self._xlab = x
            else:
                self._xlab = ""
        else:
            self.horizontal = True
            levels_y = levels_y[::-1]
            ax_kwargs = {"yticks": 0.5 + pd.np.arange(len(levels_y)),
                         "yticklabels": levels_y}
            if levels_y:
                ax_kwargs["ylim"] = (0, len(levels_y))

            if not x and not y:
                cols = [get_colors(palette, [0])[0]] * len(data)
                yval = 0
            elif y and not x:
                yval = data[y].apply(lambda y: levels_y.index(y))
                colors = get_colors(palette, levels_y)[::-1]
                cols = yval.apply(lambda y: colors[y])
            elif x and y:
                yval = data[y].apply(lambda y: levels_y.index(y))
                colors = get_colors(palette, levels_x)
                cols = data[x].apply(lambda x: colors[levels_x.index(x)])
            if rug:
                if "top" in rug:
                    plt.vlines(corpus_id, yval + 0.9, yval + 1, cols)
                if "bottom" in rug:
                    plt.vlines(corpus_id, yval, yval + 0.1, cols)
            else:
                plt.vlines(corpus_id,
                           yval + self.BOTTOM, yval + self.TOP,
                           cols)
            self._xlab = "Corpus position"
            if levels_y:
                self._ylab = y
            else:
                self._ylab = ""


        ax = kwargs.get("ax", plt.gca())
        ax.set(**ax_kwargs)

    def set_annotations(self, grid, values):
        lim = (0, self.session.Corpus.get_corpus_size())
        if self.horizontal:
            grid.set(xlim=lim)
        else:
            grid.set(ylim=lim)
        vis.Visualizer.set_annotations(self, grid, values)

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(df) == 0:
            return False

        if len(num) > 0 or len(cat) > 2:
            return False
        return True

class HeatbarPlot(BarcodePlot):
    """
    Produce a heat bar instead of single bars.

    Assuming that 'matches' is an array containing the corpus ids of the
    tokens in the match, this code produces a heat bar:

    import numpy as np
    from matplotlib import pyplot as plt
    import statsmodels

    corpus_size = 50000
    matches = np.unique(
                np.concatenate(
                    (np.random.normal(1000, 250, 10).astype(int),
                     np.random.normal(32500, 2000, 20).astype(int),
                     np.random.uniform(0, corpus_size, 20).astype(int))))

    # KDE from statsmodels:
    from statsmodels.nonparametric.kde import KDEUnivariate
    kde = KDEUnivariate(matches.astype(float))
    kde.fit(bw="scott")

    # alternative KDE from scipy.stats:
    # from scipy.stats import gaussian_kde
    # kde = scipy.stats.gaussian_kde(matches, "silverman")

    values = kde.evaluate(range(corpus_size))
    #values =kde.density

    plt.pcolormesh([values], cmap="Blues_r")
    plt.vlines(matches, 0, 1)

    """

    TOP = 0.05
    BOTTOM = 0.0
    COLOR = "Black"

    def __init__(self, *args, **kwargs):
        from statsmodels.nonparametric.kde import KDEUnivariate
        HeatbarPlot.kde = KDEUnivariate
        super(HeatbarPlot, self).__init__(*args, **kwargs)

    def plot_facet(self, data, color, **kwargs):
        """
        Plot a HeatBar plot.

        A heatbar plot is like a barcode plot, only that there is also a
        heat map plotted under the lines.
        """

        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        levels_x = kwargs.get("levels_x", None)
        levels_y = kwargs.get("levels_y", None)

        corpus_size = self.session.Corpus.get_corpus_size()
        M = []
        if x:
            for current_x in levels_x:
                dsub = data[data[x] == current_x]
                matches = dsub.coquery_invisible_corpus_id
                density = self.kde(matches.astype(float))
                density.fit(bw="scott")
                values = density.evaluate(range(corpus_size))[::-1]
                #M.append(len(matches) * values / values.max())
                M.append(len(matches) * values)
            plt.imshow(pd.np.array(M).T,
                       aspect="auto", cmap="Greys",
                       extent=(0, len(levels_x), 0, corpus_size))
        elif y:
            for current_y in levels_y:
                dsub = data[data[y] == current_y]
                matches = dsub.coquery_invisible_corpus_id
                density = self.kde(matches.astype(float))
                try:
                    density.fit(bw="scott")
                except:
                    values = pd.np.array([0] * corpus_size)
                else:
                    values = density.evaluate(range(corpus_size))
                    values = values / values.max()
                M.append(len(matches) * values)
            plt.imshow(pd.np.array(M),
                       aspect="auto", cmap="Greys",
                       extent=(0, corpus_size, 0, len(levels_y)))
        else:
            matches = data["coquery_invisible_corpus_id"]
            density = self.kde(matches.astype(float))
            density.fit(bw="scott")
            M = [density.evaluate(range(corpus_size))]
            plt.imshow(M,
                       aspect="auto", cmap="Greys",
                       extent=(0, corpus_size, 0, 1))
        super(HeatbarPlot, self).plot_facet(data, color,
                                            rug=["top", "bottom"],
                                            **kwargs)

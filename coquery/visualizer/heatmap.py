# -*- coding: utf-8 -*-
"""
heatmap.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from coquery.visualizer import visualizer as vis
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def _annotate_heatmap(self, ax, mesh):
    import numpy as np
    import colorsys
    """Add textual labels with the value in each cell."""
    try:
        mesh.update_scalarmappable()
        xpos, ypos = np.meshgrid(ax.get_xticks(), ax.get_yticks())
        for x, y, val, color in zip(xpos.flat, ypos.flat,
                                    mesh.get_array(), mesh.get_facecolors()):
            if val is not np.ma.masked:
                _, l, _ = colorsys.rgb_to_hls(*color[:3])
                text_color = ".15" if l > .5 else "w"
                val = ("{:" + self.fmt + "}").format(val)
                ax.text(x, y, val, color=text_color,
                        ha="center", va="center", **self.annot_kws)
    except Exception as e:
        print(e)
        raise e

if sns.__version__ < "0.7.0":
    sns.matrix._HeatMapper._annotate_heatmap = _annotate_heatmap

class Visualizer(vis.BaseVisualizer):
    dimensionality=2

    def setup_figure(self):
        with sns.axes_style("white"):
            super(Visualizer, self).setup_figure()

    def set_defaults(self):
        self.options["color_palette"] = "RdPu"
        super(Visualizer, self).set_defaults()

        if len(self._groupby) == 2:
            self.options["label_y_axis"] = self._groupby[0]
            self.options["label_legend"] = self._groupby[1]
        else:
            self.options["label_legend"] = self._groupby[0]



    def draw(self):
        """ Draw a heat map. """

        def get_crosstab(data, row_fact,col_fact, row_names, col_names):
            ct = pd.crosstab(data[row_fact], data[col_fact])
            ct = ct.reindex_axis(row_names, axis=0).fillna(0)
            ct = ct.reindex_axis(col_names, axis=1).fillna(0)
            return ct

        def plot(data, color):
            ct = get_crosstab(
                    data,
                    self._groupby[0],
                    self._groupby[1],
                    self._levels[0],
                    self._levels[1])

            sns.heatmap(ct,
                robust=True,
                annot=True,
                cbar=False,
                cmap=cmap,
                fmt="g",
                vmax=vmax,
                #ax=plt.gca(),
                linewidths=1)

        if len(self._groupby) < 2:
            # create a dummy cross tab with one dimension containing empty
            # values:
            data_column = self._table[self._groupby[0]].reset_index(drop=True)
            tab = pd.crosstab(
                pd.Series([""] * len(data_column), name=""),
                data_column)
            plot_facet = lambda data, color: sns.heatmap(
                tab,
                robust=True,
                annot=True,
                cbar=False,
                cmap=cmap,
                fmt="g",
                linewidths=1)
        else:
            plot_facet = plot
            vmax = pd.crosstab(
                [self._table[x] for x in [self._row_factor, self._groupby[0]] if x != None],
                [self._table[x] for x in [self._col_factor, self._groupby[1]] if x != None]).values.max()

        cmap = ListedColormap(self.options["color_palette_values"])
        self.map_data(plot_facet)

class Heatmap(vis.Visualizer):
    def plot_facet(self, data, color, **kwargs):

        def get_crosstab(data, row_fact, col_fact, row_names, col_names):
            ct = pd.crosstab(data[row_fact], data[col_fact])
            ct = ct.reindex_axis(row_names, axis=0).fillna(0)
            ct = ct.reindex_axis(col_names, axis=1).fillna(0)
            return ct

        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        levels_x = kwargs.get("levels_x")
        levels_y = kwargs.get("levels_y")
        levels_z = kwargs.get("levels_z")

        cmap = (kwargs.get("palette", "Blues"))
        param_count = sum([bool(x), bool(y), bool(z)])

        if param_count == 3:
            if data[x].dtype in (int, float):
                numeric = x
                x = z
                levels_x = levels_z
            elif data[y].dtype in (int, float):
                numeric = y
                y = z
                levels_y = levels_z
            else:
                numeric = z
            ct = (data[[x, y, numeric]].groupby([x, y])
                                       .agg("mean")
                                       .reset_index()
                                       .pivot(x, y, numeric)
                                       .T)
            ct = ct.reindex_axis(levels_y, axis=0)
            ct = ct.reindex_axis(levels_x, axis=1)
            self._xlab = x
            self._ylab = y

        elif param_count == 2:
            numeric = None
            cat = []
            if x:
                if data[x].dtype in (int, float):
                    numeric = x
                    x = None
            if y:
                if data[y].dtype in (int, float):
                    numeric = y
                    y = None
            if z:
                if data[z].dtype in (int, float):
                    numeric = z
                    z = None
            if numeric:
                cat = [fact for fact in [x, y, z] if fact][0]
                ct = (data[[cat, numeric]].groupby(cat)
                                          .agg("mean"))
                if cat == x or cat == z:
                    ct = ct.reindex_axis(levels_x).T
                else:
                    ct = ct.reindex_axis(levels_y)
            else:
                ct = get_crosstab(data, x, y, levels_x, levels_y).T
            self._xlab = x
            self._ylab = y
        elif x:
            ct = pd.crosstab(pd.Series([""] * len(data[x]), name=""),
                             data[x])
            ct = ct.reindex_axis(levels_x, axis=1)
            self._xlab = x
            self._ylab = "Frequency"
        elif y:
            ct = pd.crosstab(pd.Series([""] * len(data[y]), name=""),
                             data[y]).T
            ct = ct.reindex_axis(levels_y, axis=0)
            self._ylab = y
            self._xlab = "Frequency"

        sns.heatmap(ct.fillna(0),
            robust=True,
            annot=True,
            cbar=False,
            cmap=cmap,
            fmt="g",
            #vmax=vmax,
            linewidths=1)

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 1 or len(cat) > 2 or len(cat) == 0:
            return False
        else:
            return True

# -*- coding: utf-8 -*-
""" 
heatmap.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import visualizer as vis
import seaborn as sns
import pandas as pd

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
sns.matrix._HeatMapper._annotate_heatmap = _annotate_heatmap


class Visualizer(vis.BaseVisualizer):
    dimensionality=2
    
    def setup_figure(self):
        with sns.axes_style("white"):
            super(Visualizer, self).setup_figure()

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
                fmt="g",
                vmax=vmax,
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
                fmt="g",
                linewidths=1)
        else:
            plot_facet = plot
            #plot_facet = lambda data, color: sns.heatmap(
                #get_crosstab(
                    #data, 
                    #self._groupby[0], 
                    #self._groupby[1], 
                    #self._levels[0], 
                    #self._levels[1]),
                #robust=True,
                #annot=True,
                #cbar=False,
                #fmt="g",
                #vmax=vmax,
                #linewidths=1)

            vmax = pd.crosstab(
                [self._table[x] for x in [self._row_factor, self._groupby[0]] if x != None],
                [self._table[x] for x in [self._col_factor, self._groupby[1]] if x != None]).values.max()

        self.map_data(plot_facet)

        self.setup_axis("Y")
        self.setup_axis("X")

        self.adjust_fonts(16)

        try:
            self.g.fig.tight_layout()
        except ValueError:
            # A ValueError sometimes occurs with long labels. We ignore it:
            pass
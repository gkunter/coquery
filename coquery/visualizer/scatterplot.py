# -*- coding: utf-8 -*-
"""
scatterplot.py is part of Coquery.

Copyright (c) 2016-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from coquery.visualizer import visualizer as vis
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt


sequential_palettes = ["Blues", "Reds", "Greens", "Oranges", "Purples",
                       "BuGn", "BuPu", "RdPu", "OrRd", "YlGn",
                       "BrBG", "PiYG", "PRGn", "PuOr", "RdBu", "RdGy"]


class ScatterPlot(vis.Visualizer):
    name = "Scatterplot"
    icon = "Scatterplot"

    fit_reg = False
    axes_style = "whitegrid"
    _default = "Index"

    def plot_facet(self, data, color, **kwargs):
        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        levels_x = kwargs.get("levels_x")
        levels_y = kwargs.get("levels_y")
        levels_z = kwargs.get("levels_z")

        levels = None

        if (x and y and z):
            if self.dtype(x, data) == object:
                category = x
                levels = levels_x
                num_x = z
                num_y = y
            elif self.dtype(y, data) == object:
                category = y
                levels = levels_y
                num_x = x
                num_y = z
            elif self.dtype(z, data) == object:
                category = z
                levels = levels_z
                num_x = x
                num_y = y
            else:
                raise RuntimeError("Wrong data types for scatter plots")

            cols = sns.color_palette(kwargs["palette"], n_colors=len(levels))
            for i, val in enumerate(levels):
                df = data[data[category] == val]
                self._xlab = num_x
                self._ylab = num_y
                sns.regplot(x=df[num_x], y=df[num_y],
                            color=cols[i],
                            fit_reg=self.fit_reg,
                            ax=kwargs.get("ax", plt.gca()))

        elif sum([bool(x), bool(y), bool(z)]) == 2:
            if sum([self.dtype(x, data) == object,
                    self.dtype(y, data) == object,
                    self.dtype(z, data) == object]) == 1:
                if self.dtype(x, data) == object:
                    category = x
                    levels = levels_x
                    if y:
                        num_x = None
                        num_y = y
                    else:
                        num_x = z
                        num_y = None
                elif self.dtype(y, data) == object:
                    category = y
                    levels = levels_y
                    if x:
                        num_x = x
                        num_y = None
                    else:
                        num_x = None
                        num_y = z
                elif self.dtype(z, data) == object:
                    category = z
                    levels = levels_z
                    if x:
                        num_x = x
                        num_y = None
                    else:
                        num_x = None
                        num_y = y
                cols = sns.color_palette(kwargs["palette"],
                                         n_colors=len(levels))
                for i, val in enumerate(levels):
                    df = data[data[category] == val]
                    if num_x:
                        sns.regplot(x=df[num_x],
                                    y=pd.Series(range(len(df))),
                                    color=cols[i],
                                    fit_reg=self.fit_reg)
                        self._xlab = num_x
                        self._ylab = self._default
                    else:
                        sns.regplot(x=pd.Series(range(len(df))),
                                    y=df[num_y],
                                    color=cols[i],
                                    fit_reg=self.fit_reg)
                        self._xlab = self._default
                        self._ylab = num_y
            else:
                if x is None:
                    val_x = pd.Series(range(len(data)))
                    val_y = data[y]
                    self._xlab = self._default
                    self._ylab = y
                elif y is None:
                    val_x = data[x]
                    val_y = pd.Series(range(len(data)))
                    self._xlab = x
                    self._ylab = self._default
                else:
                    val_x = data[x]
                    val_y = data[y]
                    self._xlab = x
                    self._ylab = y
                col = sns.color_palette(kwargs["palette"], n_colors=1)
                sns.regplot(val_x, val_y,
                            color=col[0],
                            fit_reg=self.fit_reg)
        else:
            if x is not None:
                val_x = data[x]
                self._xlab = x
            elif z is not None:
                val_x = data[z]
                self._xlab = z
            else:
                val_x = pd.Series(range(len(data)))
                self.x_label = self._default
            if y is not None:
                val_y = data[y]
                self._ylab = y
            else:
                val_y = pd.Series(range(len(data)))
                self._ylab = self._default
            col = sns.color_palette(kwargs["palette"], n_colors=1)
            sns.regplot(val_x, val_y,
                        color=col[0], fit_reg=self.fit_reg)

        if levels:
            self.legend_title = category
            self.legend_levels = levels

    #def on_pick(self, event):
        #try:
            #x_pos = event.xdata
            #y_pos = event.ydata

            #if self.x_dim and not self.y_dim:
                #_df = self.df[["coquery_invisible_corpus_id",
                               #self.x_dim]]
                #_df = _df.append(pd.Series([0, x_pos], index=_df.columns),
                                 #ignore_index=True)
            #elif self.y_dim and not self.x_dim:
                #_df = self.df[["coquery_invisible_corpus_id",
                               #self.y_dim]]
                #_df = _df.append(pd.Series([0, y_pos], index=_df.columns),
                                 #ignore_index=True)
            #else:
                #_df = self.df[["coquery_invisible_corpus_id"] +
                              #[self.x_dim, self.y_dim]]
                #_df = _df.append(pd.Series([0, x_pos, y_pos],
                                           #index=_df.columns),
                                 #ignore_index=True)
            #dist = squareform(pdist(_df[_df.columns[1:]]))
            #neighbor = (_df.iloc[dist[-1][:-1].argmin()]
                        #["coquery_invisible_corpus_id"])
            #print(self.df.iloc[neighbor][_df.columns])
            #print(x_pos, y_pos)
        #except Exception as e:
            #print(e)

    @staticmethod
    def validate_data(data_x, data_y, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, df, session)

        if len(num) > 2 or len(num) == 0 or len(cat) > 1:
            return False
        else:
            return True


class RegressionPlot(ScatterPlot):
    name = "Regression plot"
    icon = "Regressionplot"

    fit_reg = True


provided_visualizations = [ScatterPlot, RegressionPlot]

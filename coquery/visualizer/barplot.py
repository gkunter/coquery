# -*- coding: utf-8 -*-
""" 
barplot.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections

from coquery.visualizer import visualizer as vis
import seaborn as sns
from seaborn.palettes import cubehelix_palette
import pandas as pd
import matplotlib.pyplot as plt

from coquery.gui.pyqt_compat import QtCore

class Visualizer(vis.BaseVisualizer):
    dimensionality = 2

    def __init__(self, *args, **kwargs):
        try:
            self.percentage = kwargs.pop("percentage")
        except KeyError:
            self.percentage = False
        try:
            self.stacked = kwargs.pop("stacked")
        except KeyError:
            self.stacked = False
        super(Visualizer, self).__init__(*args, **kwargs)

        # The dictionary _rectangles manages the boxes for mouse-over lookup.
        
        # The keys are strings, and represent the grouping level of the plot.
        # The values are themselves dictionaries. The keys of these 
        # dictionaries are tuples and coorrespond to the horizontal 
        # coordinates of the respective box, i.e. (x0, x1). The associated 
        # value is a tuple (label, count), where label is the factor level 
        # of the box, and the count is either the frequency or the 
        # percentage of that level.
        self._rectangles = dict()

    def set_defaults(self):
        """
        Set the plot defaults.
        """
        # choose the "Paired" palette if the number of grouping factor
        # levels is even and below 13, or the "Set3" palette otherwise:
        if len(self._levels[1 if len(self._groupby) == 2 else 0]) in (2, 4, 6, 8, 12):
            self.options["color_palette"] = "Paired"
        else:
            # use 'Set3', a quantitative palette, if there are two grouping
            # factors, or a palette diverging from Red to Purple otherwise:
            if len(self._groupby) == 2:
                self.options["color_palette"] = "Set3"
            else:
                self.options["color_palette"] = "RdPu"
        super(Visualizer, self).set_defaults()

        if self.percentage:
            self.options["label_x_axis"] = "Percentage"
        else:
            self.options["label_x_axis"] = "Frequency"
            
        if len(self._groupby) == 2:
            self.options["label_y_axis"] = self._groupby[0]
            self.options["label_legend"] = self._groupby[1]
        else:
            self.options["label_legend"] = self._groupby[0]
            if self.percentage:
                self.options["label_y_axis"] = ""
            else:
                self.options["label_y_axis"] = self._groupby[0]

    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(Visualizer, self).setup_figure()

    def format_coord(self, x, y, ax):
        """
        Get the box information at the given position.
        
        This method checks if the mouse is currently inside of a box. If so, 
        return a string containing the grouping labels and the size of the 
        box.
        
        As a side effect, this method also sets the tooltip for the widget so 
        that the string is shown as the tooltip.
        
        Parameters
        ----------
        x, y : float 
            The grid coordinates of the mouse cursor
        
        ax : Axis 
            The axis that the mouse is currently located in
            
        Returns
        -------
        s : string 
            A formatted string with the grouping levels and the size of the 
            box.
        """
        y = y + 0.5

        row = self._rectangles[ax][int(y)]
        for rect in row:
            (x0, x1), (y0, y1) = rect
            if (x0 <= x <= x1) and (y0 <= y <= y1):
                label, value = row[rect]
                break
        else:
            self.set_tooltip("")
            return ""

        if len(self._groupby) > 1:
            prefix = "{} – ".format(self._levels[0][int(y)])
        else:
            prefix = ""

        if self.percentage:
            S = "{}{}: {:.1f}%".format(prefix, label, value)
        else:
            S = "{}{}: {}".format(prefix, label, int(value))

        self.set_tooltip(S)
        return S

    def set_hover(self):
        pass

    def add_rectangles(self, df, ax, stacked):
        """
        Add the information stored in the data frame as rectangles to 
        the rectangle list for the axis.
        """
        if stacked:
            for row in df.index:
                offset = len(self._groupby) - 1
                edges = [0] + list(df.iloc[row].values.ravel())[offset:]
                last_content = 0
                for i in range(len(edges) - 1):
                    content = df.iloc[row][i+offset]
                    if content != last_content:
                        key = ((edges[i] + 0.0000001, edges[i+1]),
                               (row + 0.1, row + 0.91))
                        val = (df.columns[i+offset], content - last_content)
                        if ax not in self._rectangles:
                            self._rectangles[ax] = collections.defaultdict(dict)
                        self._rectangles[ax][row][key] = val
                        last_content = content
        else:
            # no stacks:
            if len(self._groupby) == 2:
                # two grouping factors:
                for row in df.index:
                    offset = len(self._groupby) - 1
                    height = 0.8 / len(self._levels[-1])
                    for i, col in enumerate(df.columns[offset:]):
                        content = df.iloc[row][i+offset]
                        if content:
                            y_pos = row + 0.1
                            key = (
                                (0, df.iloc[row][col]),
                                (y_pos + i * height, y_pos + (i+1) * height))
                            val = (col, df.iloc[row][col])
                            if ax not in self._rectangles:
                                self._rectangles[ax] = collections.defaultdict(dict)
                            self._rectangles[ax][row][key] = val
            else:
                # one grouping factor
                for i, col in enumerate(df.columns):
                    content = df.iloc[0][col]
                    if content:
                        key = (0, content), (i + 0.1, i + 0.9)
                        val = (col, content)
                        if ax not in self._rectangles:
                            self._rectangles[ax] = collections.defaultdict(dict)
                        self._rectangles[ax][i][key] = val

    def draw(self):
        """ Plot bar charts. """
        def plot_facet(data, color):
            if self.stacked:
                ax=plt.gca()
                if len(self._groupby) == 2:
                    # seperate stacked bars for each grouping
                    # variable
                    self.ct = pd.crosstab(data[self._groupby[0]], data[self._groupby[-1]])
                    df = pd.DataFrame(self.ct)
                    df = df.reindex_axis(self._levels[1], axis=1).fillna(0)
                    
                    if self.percentage:
                        df = df[self._levels[-1]].apply(lambda x: 100 * x / x.sum(), axis=1).cumsum(axis=1)
                    else:
                        df = df[self._levels[-1]].cumsum(axis=1)
                        
                    df = df.reindex_axis(self._levels[0], axis=0).fillna(0)
                    order = df.columns
                    df = df.reset_index()
                    ax=plt.gca()
                    for i, stack in enumerate(order[::-1]):
                        tmp = sns.barplot(
                            x=stack,
                            y=self._groupby[0],
                            data = df, 
                            color=self.options["color_palette_values"][::-1][i], 
                            ax=plt.gca())
                else:
                    # one stacked bar (so, this is basically a spine chart)
                    self.ct = data[self._groupby[0]].value_counts()[self._levels[-1]]
                    df = pd.DataFrame(self.ct)
                    df = df.transpose()
                    if self.percentage:
                        df = df.apply(lambda x: 100 * x / x.sum(), axis=1).cumsum(axis=1)
                    else:
                        df = df.cumsum(axis=1)
                    order = df.columns
                    for i, stack in enumerate(order[::-1]):
                        tmp = sns.barplot(
                            x=stack,
                            data = df[self._levels[-1]], 
                            color=self.options["color_palette_values"][::-1][i], 
                            ax=plt.gca())
                self.add_rectangles(df, ax, stacked=True)
                ax.format_coord = lambda x, y: self.format_coord(x, y, ax)
            else:
                if len(self._groupby) == 2:
                    self.ct = pd.crosstab(data[self._groupby[0]], data[self._groupby[-1]])
                    df = pd.DataFrame(self.ct)
                    df = df.reindex_axis(self._levels[1], axis=1).fillna(0)
                    df = df[self._levels[-1]]
                    df = df.reindex_axis(self._levels[0], axis=0).fillna(0)
                    order = df.columns
                    df = df.reset_index()
                    
                    ax = sns.countplot(
                        y=data[self._groupby[0]],
                        order=self._levels[0],
                        hue=data[self._groupby[1]],
                        hue_order=self._levels[1],
                        palette=self.options["color_palette_values"],
                        data=data)
                else:
                    # Don't use the 'hue' argument if there is only a single 
                    # grouping factor:
                    self.ct = data[self._groupby[0]].value_counts()[self._levels[-1]]
                    df = pd.DataFrame(self.ct)
                    df = df.transpose()

                    ax = sns.countplot(
                        y=data[self._groupby[0]],
                        order=self._levels[0],
                        palette=self.options["color_palette_values"],
                        data=data)
                self.add_rectangles(df, ax, stacked=False)
                ax.format_coord = lambda x, y: self.format_coord(x, y, ax)
        if self.percentage:
            self._levels[-1] = sorted(self._levels[-1])
                
        sns.despine(self.g.fig,
                    left=False, right=False, top=False, bottom=False)

        self.map_data(plot_facet)
        self.g.set_axis_labels(self.options["label_x_axis"], self.options["label_y_axis"])

        if self.percentage:
            self.g.set(xlim=(0, 100))
            
        # Add axis labels:
        if self.stacked:
            # Stacked bars always show a legend
            if len(self._groupby) == 2:
                self.add_legend(self._levels[1], loc="lower right")
            else:
                self.add_legend(self._levels[0], loc="lower right")
        elif len(self._groupby) == 2:
            # Otherwise, only show a legend if there are grouped bars
            self.add_legend(loc="lower right")

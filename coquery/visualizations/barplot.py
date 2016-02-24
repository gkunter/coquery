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

import visualizer as vis
import seaborn as sns
from seaborn.palettes import cubehelix_palette
import pandas as pd
import matplotlib.pyplot as plt

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

    def set_defaults(self):
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

    def format_coord(self, x, y, title):
        y = y + 0.5
        offset = y - int(y)
        # Check if mouse is outside the bar area:
        if not 0.1 < offset < 0.91:
            return ""
        else:
            y_cat = self._levels[0][int(y)]
            if len(self._groupby) == 2:
                try:
                    # calculate the factor level number from the y
                    # coordinate. The vaules used here seem to work, but
                    # are only derived empirically:
                    sub_cat = sorted(self._levels[1])[int(((offset - 0.1) / 0.8) * len(self._levels[1]))]                    
                except IndexError:
                    sub_cat = sorted(self._levels[1])[-1]
            else:
                sub_cat = None
                
            if title:
                # obtain the grid row and column from the axes title:
                if self._row_factor:
                    row_spec, col_spec = title.split(" | ")
                    _, row_value = row_spec.split(" = ")
                    assert _ == self._row_factor
                else:
                    col_spec = title
                    row_value = None
                _, col_value = col_spec.split(" = ")
                assert _ == self._col_factor
            else:
                row_value = None
                col_value = None
        
        
        if not hasattr(self, "ct"):
            return ""
        
        # this is a rather klunky way of getting the frequency from the
        # cross table:
        if self._row_factor:
            try:
                freq = self.ct[col_value]
                freq = freq[sub_cat]
                freq = freq[row_value]
                freq = freq[y_cat]
            except KeyError:
                return ""
            else:
                return "{} = {} | {} = {} | {} = {} | {} = {}, Freq: {}".format(
                    self._row_factor, row_value,
                    self._col_factor, col_value,
                    self._groupby[0], y_cat,
                    self._groupby[1], sub_cat,
                    freq)
        elif self._col_factor:
            try:
                freq = self.ct[col_value]
                freq = freq[sub_cat]
                freq = freq[y_cat]
            except KeyError:
                return ""
            else:
                return "{} = {} | {} = {} | {} = {}, Freq: {}".format(
                    self._col_factor, col_value,
                    self._groupby[0], y_cat,
                    self._groupby[1], sub_cat,
                    freq)
        elif len(self._groupby) == 2:
            try:
                freq = self.ct[sub_cat]
                freq = freq[y_cat]
            except KeyError:
                return ""
            else:
                return "{} = {} | {} = {}, Freq: {}".format(
                    self._groupby[0], y_cat,
                    self._groupby[1], sub_cat,
                    freq)
        else:
            try:
                freq = self.ct[y_cat]
            except KeyError:
                return ""
            else:
                return "{} = {}, Freq: {}".format(
                    self._groupby[0], y_cat,
                    freq)
        return ""

    def draw(self):
        """ Plot bar charts. """
        def plot_facet(data, color):
            if self.stacked:
                ax=plt.gca()
                if len(self._groupby) == 2:
                    # seperate stacked percentage bars for each grouping
                    # variable
                    self.ct = pd.crosstab(data[self._groupby[0]], data[self._groupby[-1]])
                    df = pd.DataFrame(self.ct)
                    df = df.reindex_axis(self._levels[1], axis=1).fillna(0)
                    if self.percentage:
                        df = df[self._levels[1]].apply(lambda x: 100 * x / x.sum(), axis=1).cumsum(axis=1)
                    else:
                        df = df[self._levels[1]].cumsum(axis=1)
                        
                    df = df.reindex_axis(self._levels[0], axis=0).fillna(0)
                    order = df.columns
                    df = df.reset_index()
                    ax=plt.gca()
                    for i, stack in enumerate(order[::-1]):
                        sns.barplot(
                            x=stack,
                            y=self._groupby[0],
                            data = df, 
                            color=self.options["color_palette_values"][::-1][i], 
                            ax=plt.gca())
                else:
                    # one stacked percentage bar (so, this is basically a 
                    # spine chart)
                    self.ct = data[self._groupby[0]].value_counts()[self._levels[-1]]
                    df = pd.DataFrame(self.ct)
                    if self.percentage:
                        df = df.apply(lambda x: 100 * x / x.sum(), axis=0).cumsum(axis=0)
                    else:
                        df = df.cumsum(axis=0)
                    df = df.transpose()
                    for i, stack in enumerate(df.columns[::-1]):
                        sns.barplot(
                            x=stack,
                            data = df, 
                            color=self.options["color_palette_values"][::-1][i], 
                            ax=plt.gca())
            else:
                if len(self._groupby) == 2:
                    ax = sns.countplot(
                        y=data[self._groupby[0]],
                        order=self._levels[0],
                        hue=data[self._groupby[1]],
                        hue_order=sorted(self._levels[1]),
                        palette=self.options["color_palette_values"],
                        data=data)
                else:
                    # Don't use the 'hue' argument if there is only a single 
                    # grouping factor:
                    ax = sns.countplot(
                        y=data[self._groupby[0]],
                        order=self._levels[0],
                        palette=self.options["color_palette_values"],
                        data=data)
            #ax.format_coord = lambda x, y: my_format_coord(x, y, ax.get_title())
            return
                
            #if len(self._groupby) == 1:
                ## Don't use the 'hue' argument if there is only a single 
                ## grouping factor:
                #ax = sns.countplot(
                    #y=data[self._groupby[0]],
                    #order=self._levels[0],
                    #palette=self.options["color_palette_values"],
                    #data=data)
            #else:
                ## Use the 'hue' argument if there are two grouping factors:
                #ax = sns.countplot(
                    #y=data[self._groupby[0]],
                    #order=self._levels[0],
                    #hue=data[self._groupby[1]],
                    #hue_order=sorted(self._levels[1]),
                    #palette=palette_name,
                    #data=data)
            ## add a custom annotator for this axes:
            #return ax

        #if self._row_factor:
            #self.ct = pd.crosstab(
                #[self._table[self._row_factor], self._table[self._groupby[0]]],
                #[self._table[self._col_factor], self._table[self._groupby[1]]])
        #elif self._col_factor:
            #self.ct = pd.crosstab(
                #self._table[self._groupby[0]],
                #[self._table[self._col_factor], self._table[self._groupby[1]]])
        #elif len(self._groupby) == 2:
            #self.ct = pd.crosstab(
                #self._table[self._groupby[0]],
                #self._table[self._groupby[1]])
        #else:
            #self.ct = self._table[self._groupby[0]].value_counts()
                
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

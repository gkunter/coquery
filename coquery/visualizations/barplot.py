""" Bar chart visualization """

from __future__ import division
from __future__ import print_function

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
        super(BarchartVisualizer, self).__init__(*args, **kwargs)

    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(BarchartVisualizer, self).setup_figure()

    def draw(self):
        """ Plot bar charts. """
        def my_format_coord(x, y, title):
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

        def plot_facet(data, color):

            if len(self._groupby) == 2:
                if self.percentage:
                    ct = pd.crosstab(
                        data[self._groupby[0]], data[self._groupby[1]])
                    df = pd.DataFrame(ct)
                    df = df.reindex_axis(self._levels[1], axis=1).fillna(0)
                    df = df[self._levels[1]].apply(lambda x: 100 * x / x.sum(), axis=1).cumsum(axis=1)
                    df = df.reindex_axis(self._levels[0], axis=0).fillna(0)
                    df = df.reset_index()
                    pal = sns.color_palette(palette_name, n_colors=len(self._levels[1]))[::-1]
                    for i, stack in enumerate(self._levels[1][::-1]):
                        sns.barplot(
                            x=stack,
                            y=self._groupby[0],
                            data = df, color=pal[i], ax=plt.gca())
                else:
                    ax = sns.countplot(
                        y=data[self._groupby[0]],
                        order=self._levels[0],
                        hue=data[self._groupby[1]],
                        hue_order=sorted(self._levels[1]),
                        palette=palette_name,
                        data=data)

            else:
                if self.percentage:
                    ct = data[self._groupby[0]].value_counts()
                    df = pd.DataFrame(ct)
                    df = df.apply(lambda x: 100 * x / x.sum(), axis=0).cumsum(axis=0)
                    #df = df.reset_index()
                    df.columns = [self._groupby[0], "Percent"]
                    df = df.transpose()
                    df["YCat"] = self._groupby[0]
                    pal = sns.color_palette(palette_name, n_colors=len(self._levels[0]))[::-1]
                    for i, stack in enumerate(self._levels[0][::-1]):
                        sns.barplot(
                            x=stack,
                            y="YCat",
                            data = df, color=pal[i], ax=plt.gca())
                else:
                    # Don't use the 'hue' argument if there is only a single 
                    # grouping factor:
                    ax = sns.countplot(
                        y=data[self._groupby[0]],
                        order=self._levels[0],
                        palette=palette_name,
                        data=data)
            return
                
                
                
                
            if len(self._groupby) == 1:
                # Don't use the 'hue' argument if there is only a single 
                # grouping factor:
                ax = sns.countplot(
                    y=data[self._groupby[0]],
                    order=self._levels[0],
                    palette=palette_name,
                    data=data)
            else:
                # Use the 'hue' argument if there are two grouping factors:
                ax = sns.countplot(
                    y=data[self._groupby[0]],
                    order=self._levels[0],
                    hue=data[self._groupby[1]],
                    hue_order=sorted(self._levels[1]),
                    palette=palette_name,
                    data=data)
            # add a custom annotator for this axes:
            ax.format_coord = lambda x, y: my_format_coord(x, y, ax.get_title())
            return ax

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

        # choose the "Paired" palette if the number of grouping factor
        # levels is even and below 13, or the "Set3" palette otherwise:
        if len(self._levels[1 if len(self._groupby) == 2 else 0]) in (2, 4, 6, 8, 12):
            palette_name = "Paired"
        else:
            # use 'Set3', a quantitative palette, if there are two grouping
            # factors, or a palette diverging from Red to Purple otherwise:
            palette_name = "Set3" if len(self._groupby) == 2 else "RdPu"

        self.map_data(plot_facet)
            
        # Add axis labels:
        if self.percentage:
            self.g.set(xlim=(0, 100))
            self.g.set_axis_labels("Percentage", self._groupby[0])
        else:
            self.g.set_axis_labels("Frequency", self._groupby[0])
        
        # Add a legend if there are two grouping factors:
        if len(self._groupby) == 2:
            if self.percentage:
                pal = sns.color_palette(palette_name, n_colors=len(self._levels[1]))
                legend_bar = [
                    plt.Rectangle(
                        (0, 0), 1, 1,
                        fc=pal[i], 
                        edgecolor="none") for i, _ in enumerate(self._levels[1])
                    ]
                self.g.fig.get_axes()[-1].legend(
                    legend_bar, self._levels[1],
                    ncol=1,
                    title=self._groupby[1], 
                    frameon=True, 
                    framealpha=0.7, 
                    loc="lower left").draggable()
            else:
                self.g.fig.get_axes()[-1].legend(title=self._groupby[1], frameon=True, framealpha=0.7, loc="lower left").draggable()
        # Try to make the figure fit into the area nicely:
        #self.g.fig.tight_layout()

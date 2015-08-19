""" Bar chart visualization """

import visualizer as vis
import seaborn as sns
from seaborn.palettes import cubehelix_palette
import pandas as pd

class BarchartVisualizer(vis.Visualizer):
    dimensionality = 2

    def draw(self):
        """ Plot bar charts. """
        if self._row_factor:
            self.ct = pd.crosstab(
                [self._table[self._row_factor], self._table[self._groupby[0]]],
                [self._table[self._col_factor], self._table[self._groupby[1]]])
        elif self._col_factor:
            self.ct = pd.crosstab(
                self._table[self._groupby[0]],
                [self._table[self._col_factor], self._table[self._groupby[1]]])
        elif len(self._groupby) == 2:
            self.ct = pd.crosstab(
                self._table[self._groupby[0]],
                self._table[self._groupby[1]])
        else:
            self.ct = self._table[self._groupby[0]].value_counts()
                
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
                        sub_cat = sorted(self._levels[1])[int(((offset - 0.1) / 0.8) * len(self._levels[1]))]                    
                    except IndexError:
                        sub_cat = sorted(self._levels[1])[-1]
                else:
                    sub_cat = None
                if title:
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
                    print(1)
                    return ""
                else:
                    return "{} = {}, Freq: {}".format(
                        self._groupby[0], y_cat,
                        freq)
            return ""

        def sub_data(data, color):
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
            ax.format_coord = lambda x, y: my_format_coord(x, y, ax.get_title())
            return ax

        sns.despine(self.g.fig)
                    #left=False, right=False, top=False, bottom=False)

        # choose the "Paired" palette if the number of grouping factor
        # levels is even and below 13, or the "Set3" palette otherwise:
        if len(self._levels[1 if len(self._groupby) == 2 else 0]) in (2, 4, 6, 8, 12):
            palette_name = "Paired"
        else:
            palette_name = "Set3" if len(self._groupby) == 2 else "RdPu"
            

        # plot FacetGrid:
        self.g.map_dataframe(sub_data) 
        # Add axis labels:
        self.g.set_axis_labels("Frequency", self._groupby[0])
        # Add a legend if there are two grouping factors:
        if len(self._groupby) == 2:
            self.g.add_legend(title=self._groupby[1], frameon=True)
        # Try to make the figure fit into the area nicely:
        self.g.fig.tight_layout()

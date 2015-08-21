""" Time series visualization """

import visualizer as vis
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

class TimeSeriesVisualizer(vis.Visualizer):
    visualize_frequency = True
    dimensionality=2
    vmax = 0
    
    def __init__(self, *args, **kwargs):
        try:
            self.area = kwargs.pop("area")
        except KeyError:
            self.area = False
        try:
            self.percentage = kwargs.pop("percentage")
        except KeyError:
            self.percentage = False
            
        super(TimeSeriesVisualizer, self).__init__(*args, **kwargs)
    
    def update_data(self):
        super(TimeSeriesVisualizer, self).update_data()
        year = self._table.columns[self._table.columns == "Year"]
        age = self._table.columns[self._table.columns == "Age"]
        date = self._table.columns[self._table.columns == "Date"]
        if len(year):
            self._time_column = year[0]
        elif len(date):
            self._time_column = date[0]
        elif len(age):
            self._time_column = age[0]
        else:
            self._time_column = ""

        if self._time_column:
            self._table[self._time_column] = pd.to_datetime([str(x) for x in self._table[self._time_column]], 
                                errors="ignore", exact=False)
            if len(self._groupby) == 2:
                if self._col_factor:
                    self._row_factor = self._col_factor
                self._col_factor = self._groupby[0]
                
                self._groupby[0] = self._groupby[1]
                self._levels = [self._levels[1]]
                self._groupby[1] = self._time_column
            else:
                self._groupby.append(self._time_column)
    
    def setup_figure(self):
        with sns.axes_style("white"):
            super(TimeSeriesVisualizer, self).setup_figure()

    def draw(self, **kwargs):
        """ Draw a heat map. """
        
        def plot_facet(data, color, **kwargs):
            
            if len(self._groupby) == 2:
                ct = pd.crosstab(data[self._groupby[1]], data[self._groupby[0]])
                if len(self._levels) == 2:
                    ct = ct.reindex_axis(self._levels[1], axis=0).fillna(0)
                ct = ct.reindex_axis(self._levels[0], axis=1).fillna(0)
                ct.index = pd.to_datetime(ct.index, coerce=True)
                ct = ct[pd.notnull(ct.index)]
            else:
                ct = pd.crosstab(
                    data[self._groupby[0]],
                    pd.Series([""] * len(self._table[self._groupby[0]]), name="")                    )
            
            if self.percentage:
                ct = ct.apply(lambda x: x / sum(x), axis=1)
                ct = ct.resample("AS")
                return ct.plot(kind="area", ax=plt.gca(), stacked=True, color=self.get_palette(), **kwargs)
            else:
                if self.area:
                    if len(self._groupby) == 2:
                        self.vmax = max(self.vmax, ct.apply(sum, axis=1).max())
                    return ct.plot(ax=plt.gca(), kind="area", stacked=True, color=self.get_palette(), **kwargs)
                else:
                    self.vmax = max(self.vmax, ct.values.max())
                    ct.plot(ax=plt.gca(), stacked=False, color=self.get_palette(), **kwargs)
            
        self.g.map_dataframe(plot_facet, 
                             )
        
        self.g.add_legend(title=self._groupby[0])
        if self.percentage:
            self.g.set(ylim=(0, 1))
        else:
            self.g.set(ylim=(0, self.vmax))
        if self.percentage:
            self.g.set_axis_labels(self._groupby[-1], "Percentage")
        else:
            if self.area:
                self.g.set_axis_labels(self._groupby[-1], "Cummulative frequency")                
            else:
                self.g.set_axis_labels(self._groupby[-1], "Frequency")                
        
        self.setup_axis("Y")
        self.setup_axis("X")
        
        self.g.fig.tight_layout()

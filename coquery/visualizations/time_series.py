""" Time series visualization """

import visualizer as vis
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

class TimeSeriesVisualizer(vis.Visualizer):
    visualize_frequency = True
    dimensionality=2
    vmax = 0
    
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
            self._table[self._time_column] = pd.to_datetime(self._table[self._time_column], 
                                errors="ignore", exact=False)
    
    def setup_figure(self):
        with sns.axes_style("white"):
            super(TimeSeriesVisualizer, self).setup_figure()

    def draw(self):
        """ Draw a heat map. """
        
        def plot_facet(data, color, **kwargs):
            try:
                percentage = kwargs.pop("percentage")
            except KeyError:
                percentage = False
            stacked = kwargs.get("stacked", True)
            
            ct = pd.crosstab(data[self._groupby[1]], data[self._groupby[0]])
            ct = ct.reindex_axis(self._levels[1], axis=0).fillna(0)
            ct = ct.reindex_axis(self._levels[0], axis=1).fillna(0)
            ct.index = pd.to_datetime(ct.index)
            if percentage:
                return ct.apply(lambda x: x / sum(x), axis=1).plot(ax=plt.gca(), **kwargs)
            else:
                if stacked:
                    self.vmax = max(self.vmax, ct.apply(sum, axis=1).max())
                else:
                    self.vmax = max(self.vmax, ct.values.max())
                return ct.plot(ax=plt.gca(), **kwargs)
            
        self.g.map_dataframe(plot_facet, percentage=False, stacked=False)
        
        self.g.add_legend(title=self._groupby[0])
        self.g.set(ylim=(0, self.vmax))
        
        self.setup_axis("Y")
        self.setup_axis("X")
        
        self.g.fig.tight_layout()

""" Time series visualization """

import visualizer as vis
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TimeSeriesVisualizer(vis.Visualizer):
    visualize_frequency = True
    dimensionality = 1
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
        try:
            self.smooth = kwargs.pop("smooth")
        except KeyError:
            self.smooth = False
            
        super(TimeSeriesVisualizer, self).__init__(*args, **kwargs)
    
    def update_data(self, bandwidth=1):
        super(TimeSeriesVisualizer, self).update_data()
        
        for x in self._table.columns[::-1]:
            if x in self._time_columns:
                self._time_column = x
                break
        else:
            self._time_column = ""

        self.bandwidth = bandwidth

        if self._time_column:
            if  self._time_column in self._groupby:
                if self._groupby[-1] != self._time_column:
                    self._groupby = self._groupby[::-1]
                    self._levels = self._levels[::-1]
            else:
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
        with sns.axes_style("whitegrid"):
            super(TimeSeriesVisualizer, self).setup_figure()

    def draw(self, **kwargs):
        """ Draw a heat map. """
        
        def plot_facet(data, color, **kwargs):
            
            if len(self._groupby) == 2:
                num = []
                date = []
                time = data[self._time_column]
                for x in time:
                    # try to convert the time column to a useful time object
                    try:
                        num.append(pd.datetime((int(x) // self.bandwidth) * self.bandwidth, 1, 1))
                    except ValueError:
                        num.append(np.NaN)
                    try:
                        date.append(pd.Timestamp("{}".format(
                            (pd.Timestamp(x).year // self.bandwidth) * self.bandwidth)))
                    except ValueError:
                        date.append(pd.NaT)
                if pd.isnull(num).sum() <= pd.isnull(date).sum():
                    data[self._time_column] = num
                    time_range = [pd.datetime((int(x) // self.bandwidth) * self.bandwidth, 1, 1) for x in (self._table[self._time_column].min(), self._table[self._time_column].max())]
                else:
                    data[self._time_column] = date
                    time_range = [pd.Timestamp("{}".format(
                        (pd.Timestamp(x).year // self.bandwidth) * self.bandwidth)) for x in (self._table[self._time_column].min(), self._table[self._time_column].max())]

                ct = pd.crosstab(data[self._time_column], data[self._groupby[0]])
                ct = ct.reindex_axis(self._levels[0], axis=1).fillna(0)
                ct = ct[pd.notnull(ct.index)]
            else:
                ct = pd.crosstab(
                    data[self._time_column],
                    pd.Series([""] * len(self._table[self._time_column]), name="")                    )
            # percentage area plot:
            if self.percentage:
                ct = ct.apply(lambda x: (100 * x) / sum(x), axis=1)
                ct.plot(kind="area", ax=plt.gca(), stacked=True, color=self.get_palette(), **kwargs)
            else:
                if self.area:
                    # Stacked area plot:
                    if len(self._groupby) == 2:
                        self.vmax = max(self.vmax, ct.apply(sum, axis=1).max())
                    ct.plot(ax=plt.gca(), kind="area", stacked=True, color=self.get_palette(), **kwargs)
                else:
                    # Line plot:
                    self.vmax = max(self.vmax, ct.values.max())
                    print(ct)
                    ct.plot(ax=plt.gca())
                    #ct.plot(ax=plt.gca(), stacked=False, color=self.get_palette(), **kwargs)
            
        self.g.map_dataframe(plot_facet)
        
        if self.percentage:
            self.g.set(ylim=(0, 100))
        else:
            self.g.set(ylim=(0, self.vmax))
        if self.percentage:
            self.g.set_axis_labels(self._groupby[-1], "Percentage")
        else:
            if self.area:
                self.g.set_axis_labels(self._groupby[-1], "Cummulative frequency")                
            else:
                self.g.set_axis_labels(self._groupby[-1], "Frequency")                
        
        #self.setup_axis("Y")
        #self.setup_axis("X")
        
        self.g.fig.get_axes()[-1].legend(title=self._groupby[0], framealpha=0.7, frameon=True, loc="lower left").draggable()
        self.g.fig.tight_layout()
""" Time series visualization """

import visualizer as vis
import seaborn as sns
import pandas as pd

class TimeSeriesVisualizer(vis.Visualizer):
    visualize_frequency = True
    dimensionality=2
    
    def update_data(self):
        super(TimeSeriesVisualizer, self).update_data()
        year = self._table.columns[self._table.columns == "Year"]
        age = self._table.columns[self._table.columns == "Age"]
        date = self._table.columns[self._table.columns == "Date"]
        print(year)
        if len(year):
            self._time_column = year[0]
        elif len(date):
            self._time_column = date[0]
        elif len(age):
            self._time_column = age[0]
        else:
            self._time_column = ""
        print(self._time_column)
        if self._time_column:
            print(self._time_column)
            self._table[self._time_column] = pd.to_datetime(self._table[self._time_column], 
                                errors="ignore", exact=False)
            print(self._table.head())
    
    def setup_figure(self):
        with sns.axes_style("white"):
            super(TimeSeriesVisualizer, self).setup_figure()

    def draw(self):
        """ Draw a heat map. """
        
        def plot_facet(data, color):
            ct = pd.crosstab(data[self._groupby[1]], data[self._groupby[0]])
            ct = ct.reindex_axis(self._levels[1], axis=0).fillna(0)
            ct = ct.reindex_axis(self._levels[0], axis=1).fillna(0)
            ct.index = pd.to_datetime(ct.index)
            print(ct[ct.index < "1995"])
            return ct.plot(kind="area")
            
            #print(ct[ct.index < "1995"].to_dict())

            return pd.DataFrame(ct.to_dict()).plot()
            
            
            print(type(ct))
            print(ct.index.dtype)
            ax = ct.plot()
            print(ax)
            return ax
            
            #time_count = data[self._time_column].value_counts()
            #time_count = time_count.reindex(
                #pd.unique(self._table[self._time_column].values.ravel()))
            #tmp = tmp.
            
            #ax = 
            
            pd.DataFrame([tmp.get_group(x)["BOLD signal"] for x in tmp.groups]).transpose().plot()
            
            
            ax = sns.tsplot(
                data=data,
                time=data[self._time_column],
                condition=data[self._groupby[1]])
            return ax

        
        self.g.map_dataframe(plot_facet)
        
        
        #FUN = lambda data, color: sns.tsplot(
            #data[self._time_column].value_counts())
            #vmax = pd.crosstab(
                #[self._table[x] for x in [self._row_factor, self._groupby[0]] if x <> None],
                #[self._table[x] for x in [self._col_factor, self._groupby[1]] if x <> None]).values.max()

        #self.g.map_dataframe(FUN)

        #self.setup_axis("Y")
        #self.setup_axis("X")
        
        self.g.fig.tight_layout()

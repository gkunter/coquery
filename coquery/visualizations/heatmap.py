""" Heatmap visualization """

import visualizer as vis
import seaborn as sns
import pandas as pd

class Visualizer(vis.BaseVisualizer):
    visualize_frequency = True
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
        
        if len(self._groupby) < 2:
            # create a dummy cross tab with one dimension containing empty
            # values:
            tab = pd.crosstab(
                pd.Series([""] * len(self._table[self._groupby[0]]), name=""), 
                self._table[self._groupby[0]])
            plot_facet = lambda data, color: sns.heatmap(
                tab,
                robust=True,
                annot=True,
                cbar=False,
                fmt="g",
                linewidths=1)
        else:
            plot_facet = lambda data, color: sns.heatmap(
                get_crosstab(
                    data, 
                    self._groupby[0], 
                    self._groupby[1], 
                    self._levels[0], 
                    self._levels[1]),
                robust=True,
                annot=True,
                cbar=False,
                fmt="g",
                vmax=vmax,
                linewidths=1)

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
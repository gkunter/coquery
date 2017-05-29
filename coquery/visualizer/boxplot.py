# -*- coding: utf-8 -*-
"""
boxplot.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from coquery.visualizer import visualizer as vis
import seaborn as sns

class BoxPlot(vis.Visualizer):
    axes_style = "whitegrid"

    def plot_fnc(self, *args, **kwargs):
        sns.boxplot(*args, **kwargs)

    def plot_facet(self, data, color, **kwargs):
        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        palette = kwargs.get("palette")

        # case 1: one category in x, one numeric elsewhere
        if (self.dtype(x, data) == object and
            (self.dtype(y, data) != object and z is None) or
            (y is None and self.dtype(z, data) != object)):
            if z is None:
                numeric = y
            else:
                numeric = z
            self.plot_fnc(x=x, y=numeric, data=data, palette=palette)
            self._xlab = x
            self._ylab = numeric
        # case 2: one category in y, one numeric elsewhere
        elif (self.dtype(y, data) == object and
              (self.dtype(x, data) != object and z is None) or
              (x is None and self.dtype(z, data) != object)):
            if z is None:
                numeric = x
            else:
                numeric = z
            self.plot_fnc(x=numeric, y=y, data=data, palette=palette)
            self._xlab = numeric
            self._ylab = y
        # case 3: one category in x and z, a numeric in y:
        elif (self.dtype(x, data) == object and
              self.dtype(z, data) == object and
              self.dtype(y, data) in (float, int)):
            self.plot_fnc(x=x, y=y, hue=z, data=data, palette=palette)

            self.legend_title = kwargs["z"]
            self.legend_levels = kwargs["levels_z"]
            self._xlab = x
            self._ylab = y

        # case 4: one category in y and z, a numeric in x:
        elif (self.dtype(y, data) == object and
              self.dtype(z, data) == object and
              self.dtype(x, data) in (float, int)):
            self.plot_fnc(x=x, y=y, hue=z, data=data, palette=palette)

            self.legend_title = kwargs["z"]
            self.legend_levels = kwargs["levels_z"]
            self._xlab = x
            self._ylab = y

        # case 5: one category in x and y, a numeric in z:
        else:
            self.plot_fnc(x=z, y=y, hue=x, data=data, palette=palette)

            self.legend_title = kwargs["x"]
            self.legend_levels = kwargs["levels_x"]
            self._xlab = z
            self._ylab = y

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) != 1:
            return False
        if len(cat) == 0:
            return False
        if len(cat) == 1 and vis.Visualizer.dtype(data_z, df) == object:
            return False
        return True

class ViolinPlot(BoxPlot):
    def plot_fnc(self, *args, **kwargs):
        sns.violinplot(*args, **kwargs)

# -*- coding: utf-8 -*-
"""
timeseries.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from coquery.visualizer import visualizer as vis
import math
import pandas as pd
import matplotlib.pyplot as plt

from coquery.gui.pyqt_compat import QtWidgets, tr


class TimeSeries(vis.Visualizer):
    name = "Change over time (lines)"
    icon = "Lines"

    axes_style = "whitegrid"
    _default = "Frequency"
    _unit = " units"
    bandwidth = 1

    kind = "line"
    stacked = False

    def get_custom_widgets(self, *args, **kwargs):
        label = tr("TimeSeries", "Bandwidth", None)
        unit = tr("TimeSeries", " units", None)

        layout = QtWidgets.QHBoxLayout()
        self.label_bandwidth = QtWidgets.QLabel(label)
        self.spin_bandwidth = QtWidgets.QSpinBox()
        self.spin_bandwidth.setValue(self.bandwidth)
        self.spin_bandwidth.setSuffix(unit)
        self.spin_bandwidth.setMinimum(1)
        self.spin_bandwidth.setMaximum(9999)
        self.spin_bandwidth.setValue(self.bandwidth)

        layout.addWidget(self.label_bandwidth)
        layout.addWidget(self.spin_bandwidth)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        return ([layout],
                [self.spin_bandwidth.valueChanged],
                [])

    def update_values(self):
        self.bandwidth = int(self.spin_bandwidth.value())

    def plot_facet(self, data, color,
                   x=None, y=None, z=None,
                   levels_x=None, levels_y=None, levels_z=None,
                   palette=None, **kwargs):

        def to_num(x):
            bw = TimeSeries.bandwidth
            val = pd.to_numeric(x, errors="coerce")
            val = val.apply(
                lambda x: x if pd.isnull(x) else (int(x) // bw) * bw)
            return val

        def to_year(x):
            bw = TimeSeries.bandwidth
            val = pd.to_datetime(x.astype(str), errors="coerce")
            val = val.apply(
                lambda x: x if pd.isnull(x) else (int(x.year) // bw) * bw)
            return val

        category = None
        levels = None
        numeric = None

        self._xlab = self._default
        self._ylab = self._default
        if x:
            as_time = to_year(data[x].head(1000))
            as_num = to_num(data[x].head(1000))
            if len(as_time.dropna()) > len(as_num.dropna()):
                numeric = x
                fun = to_year
                self._xlab = x
            elif len(as_num.dropna()):
                numeric = x
                fun = to_num
                self._xlab = x
            else:
                category = x
                levels = levels_x
        if y:
            if numeric is None:
                as_time = to_year(data[y].head(1000))
                as_num = to_num(data[y].head(1000))
                if len(as_time.dropna()) > len(as_num.dropna()):
                    numeric = y
                    fun = to_year
                    self._ylab = y
                elif len(as_num.dropna()):
                    numeric = y
                    fun = to_num
                    self._ylab = y
                else:
                    category = y
                    levels = levels_y
            else:
                category = y
                levels = levels_y

        if z and self.dtype(z, data) == object:
            category = z
            levels = levels_z
        val = fun(data[numeric])
        if not category:
            col = self.get_palette(palette, kwargs["color_number"])[0]
            tab = val.value_counts().sort_index()

            self.plot_func(S=tab, color=col, ax=plt.gca())
            min_x = val.min()
            max_x = val.max()

            x_range = list(range(math.floor(min_x),
                                 math.ceil(max_x + 1), TimeSeries.bandwidth))
            if TimeSeries.bandwidth > 1:
                labels = ["{}–{}".format(x, x + TimeSeries.bandwidth - 1)
                          for x in x_range]
            else:
                labels = x_range
            plt.xticks(x_range, labels)
        else:
            col = self.get_palette(palette, len(levels))[::-1]
            index = (val.dropna()
                        .drop_duplicates()
                        .sort_values())
            tmp = {}

            for i, level in enumerate(levels):
                df = data[data[category] == level]
                val = fun(df[numeric])
                tab = val.value_counts().sort_index()
                tab = tab.reindex_axis(index).fillna(0)
                tmp[level] = tab
            df = pd.DataFrame(tmp)
            self.plot_func(df=df, color=col, ax=plt.gca())
        if levels:
            self.legend_title = category
            self.legend_levels = levels

    def plot_func(self, S=None, df=None, *args, **kwargs):
        if S is not None:
            pd.Series(S).plot.line(*args, **kwargs)
        else:
            df.plot.line(*args, **kwargs)

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        """
        Validate the parameters.

        For TimeSeries visualizations, the parameters are valid if either x or
        y is either a time feature or a numeric variable.
        """
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        try:
            time_features = session.Resource.time_features
            time = [x for x in [data_x, data_y] if
                    session.translate_header(x) in time_features]
        except AttributeError:
            time = []

        if ((len(time) == 1 and len(num) == 1) or
                (len(time) == 1 and len(num) == 0 and len(cat) == 1)):
            return True

        if len(num) == 1 and len(time) == 0:
            return True

        return False


class StackedArea(TimeSeries):
    name = "Change over time (stacked)"
    icon = "Areas_stacked"

    kind = "area"
    stacked = True

    def plot_func(self, S=None, df=None, *args, **kwargs):
        if S is not None:
            self._transform(S=S).plot.area(stacked=True, *args, **kwargs)
        else:
            self._transform(df=df).plot.area(stacked=True, *args, **kwargs)

    def _transform(self, S=None, df=None):
        if S is not None:
            return S
        else:
            return df


class PercentageArea(StackedArea):
    name = "Change over time (percent)"
    icon = "Areas_percent"

    _default = "Percentage"

    def _transform(self, S=None, df=None):
        if S is not None:
            return pd.Series(data=[100] * len(S), index=S.index)
        else:
            return df.apply(lambda x: x * 100 / sum(x), axis=1)

    def set_annotations(self, grid, values):
        super(PercentageArea, self).set_annotations(grid, values)
        grid.set(ylim=(0, 100))


provided_visualizations = [TimeSeries, StackedArea, PercentageArea]

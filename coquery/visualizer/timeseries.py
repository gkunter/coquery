# -*- coding: utf-8 -*-
"""
timeseries.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from coquery.visualizer import visualizer as vis
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

from coquery.errors import *
from coquery.gui.pyqt_compat import QtWidgets

class Visualizer(vis.BaseVisualizer):
    dimensionality = 2
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

        super(Visualizer, self).__init__(*args, **kwargs)

    def set_defaults(self):
        if self.percentage:
            self.options["label_y_axis"] = "Percentage"
        else:
            if self.area:
                self.options["label_y_axis"] = "Cummulative frequency"
            else:
                self.options["label_y_axis"] = "Frequency"
        self.options["label_x_axis"] = self._groupby[-1]
        self.options["label_legend"] = self._groupby[0]
        super(Visualizer, self).set_defaults()

    def update_data(self, bandwidth=1):
        super(Visualizer, self).update_data()
        for x in self._table.columns[::-1]:
            if x in self._time_columns:
                self._time_column = x
                break
        else:
            self._time_column = ""

        self.bandwidth = bandwidth

        # Found column with temporal data?
        if self._time_column:
            if  self._time_column in self._groupby:
                # make sure that column is last in the internal data frame
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
        else:
            raise VisualizationInvalidDataError

    def setup_figure(self):
        with sns.axes_style("whitegrid"):
            super(Visualizer, self).setup_figure()

    def convert_to_datetime(self, x):
        try:
            return (int(x) // self.bandwidth) * self.bandwidth
        except ValueError:
            return np.NaN

    def convert_to_timeseries(self, x):
        # FIXME:
        # pandas >= 0.17.0 has changed the Timestamp API. Check that this
        # is still working!
        version = [int(x) for x in pd.__version__.split(".")]
        try:
             return pd.Timestamp("{}".format(
                (pd.Timestamp("{}".format(x)).year // self.bandwidth) * self.bandwidth)).year
        except ValueError:
            return pd.NaT

    def draw(self, **kwargs):
        """ Draw time series. """

        def plot_facet(data, color, **kwargs):
            num = []
            date = []
            time = data[self._time_column]
            num = data[self._time_column].apply(self.convert_to_datetime)
            date = data[self._time_column].apply(self.convert_to_timeseries)
            if pd.isnull(num).sum() <= pd.isnull(date).sum():
                data[self._time_column] = num
            else:
                data[self._time_column] = date

            data.dropna(inplace=True)
            if len(self._groupby) == 2:
                ct = pd.crosstab(data[self._time_column], data[self._groupby[0]])
                ct = ct.reindex_axis(self._levels[0], axis=1).fillna(0)
                ct = ct[pd.notnull(ct.index)]
            else:
                ct = pd.crosstab(
                    data[self._time_column],
                    pd.Series([""] * len(self._table[self._time_column]), name=""))

            # percentage area plot:
            if self.percentage:
                # if there is only one grouping variable (the time column),
                # the cross table produces a Series, not a data frame. It
                # isn't really very informative to plot it, but we provide
                # for this special case anyway_
                if type(ct) == pd.Series:
                    ct = ct.apply(lambda x: 100)
                else:
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
                    ct.plot(ax=plt.gca(), color=self.get_palette())

        self.map_data(plot_facet)

        if self.percentage:
            self.g.set(ylim=(0, 100))
        else:
            self.g.set(ylim=(0, self.vmax))
        self.g.set_axis_labels(self.options["label_x_axis"], self.options["label_y_axis"])

        if len(self._groupby) == 2:
            self.add_legend()

class TimeSeries(vis.Visualizer):
    axes_style = "whitegrid"
    _default = "Frequency"
    bandwidth = 1

    def get_custom_widgets(self):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QApplication.instance().translate(
                    "TimeSeries", "Bandwidth", None)
        unit = QtWidgets.QApplication.instance().translate(
                    "TimeSeries", " years", None)
        button = QtWidgets.QApplication.instance().translate(
                    "TimeSeries", "Apply", None)

        TimeSeries.label_bandwidth = QtWidgets.QLabel(label)
        TimeSeries.spin_bandwidth = QtWidgets.QSpinBox()
        TimeSeries.spin_bandwidth.setValue(TimeSeries.bandwidth)
        TimeSeries.spin_bandwidth.setSuffix(unit)
        TimeSeries.spin_bandwidth.setMinimum(1)
        TimeSeries.button_apply = QtWidgets.QPushButton(button)
        TimeSeries.button_apply.setDisabled(True)
        TimeSeries.button_apply.clicked.connect(
            lambda: TimeSeries.update_figure(
                self, TimeSeries.spin_bandwidth.value()))
        TimeSeries.spin_bandwidth.valueChanged.connect(
            lambda x: TimeSeries.button_apply.setEnabled(True))
        layout.addWidget(TimeSeries.label_bandwidth)
        layout.addWidget(TimeSeries.spin_bandwidth)
        layout.addWidget(TimeSeries.button_apply)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        layout.setStretch(2, 0)
        return [layout]

    @classmethod
    def update_figure(cls, self, i):
        cls.bandwidth = i
        TimeSeries.button_apply.setDisabled(True)
        self.updateRequested.emit()

    def plot_facet(self, data, color, **kwargs):

        def to_num(x):
            bw = TimeSeries.bandwidth
            val = pd.to_numeric(x, errors="coerce")
            val = val.apply(lambda x: x if pd.isnull(x)
                                      else
                                      (int(x) // bw) * bw)
            return val

        def to_year(x):
            bw = TimeSeries.bandwidth
            val = pd.to_datetime(x.astype(str), errors="coerce")
            val = val.apply(lambda x: x if pd.isnull(x)
                                      else
                                      (int(x.year) // bw) * bw)
            return val

        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        levels_x = kwargs.get("levels_x")
        levels_y = kwargs.get("levels_y")
        levels_z = kwargs.get("levels_z")

        category = None
        levels = None
        value = None
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
            if Numeric is None:
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
            tab = val.value_counts().sort_index()
            tab.plot(ax=plt.gca())
        else:
            index = (val.dropna()
                        .drop_duplicates()
                        .sort_values())
            for i, level in enumerate(levels):
                df = data[data[category] == level]
                val = fun(df[numeric])
                tab = val.value_counts().sort_index()
                tab = tab.reindex_axis(index).fillna(0)
                tab.plot()

        if levels:
            self.legend_title = category
            self.legend_levels = levels

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        # check if any of the data columns is a time column:
        if ((session.translate_header(data_x) not
             in session.Resource.time_features) and
            (session.translate_header(data_x) not
             in session.Resource.time_features)):
            return False

        return True

        # check if either column is a categorical column:
        if (TimeSeries.dtype(data_x, df) != object and
            TimeSeries.dtype(data_y, df) != object):
            return False

        return True

class StackedArea(TimeSeries):
    pass

class PercentageArea(TimeSeries):
    def set_annotations(self, grid):
        super(PercentageArea, self).set_annotations(grid)
        grid.set(ylim=(0, 100))




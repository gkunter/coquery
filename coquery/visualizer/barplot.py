# -*- coding: utf-8 -*-
"""
barplot.py is part of Coquery.

Copyright (c) 2016–2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets, QtCore

from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum)


class BarPlot(vis.Visualizer):
    name = "Barplot"
    icon = "Barchart"

    axes_style = "whitegrid"
    DEFAULT_LABEL = "Frequency"

    horizontal = True

    def plt_func(self, *args, **kwargs):
        sns.barplot(*args, **kwargs)

    def get_custom_widgets(self, *args, **kwargs):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QApplication.instance().translate(
                    "BarPlot", "Favor Y category over X category", None)
        button = QtWidgets.QApplication.instance().translate(
                    "Visualizer", "Apply", None)

        BarPlot.check_horizontal = QtWidgets.QCheckBox(label)
        BarPlot.check_horizontal.setCheckState(
            QtCore.Qt.Checked if BarPlot.horizontal else
            QtCore.Qt.Unchecked)

        BarPlot.button_apply = QtWidgets.QPushButton(button)
        BarPlot.button_apply.setDisabled(True)
        BarPlot.button_apply.clicked.connect(
            lambda: BarPlot.update_figure(
                self, BarPlot.check_horizontal.checkState()))

        BarPlot.check_horizontal.stateChanged.connect(
            lambda x: BarPlot.button_apply.setEnabled(True))

        layout.addWidget(BarPlot.check_horizontal)
        layout.addWidget(BarPlot.button_apply)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        return [layout]

    @classmethod
    def update_figure(cls, self, i):
        cls.horizontal = bool(i)
        BarPlot.button_apply.setDisabled(True)
        self.updateRequested.emit()

    def plot_facet(self,
                   data, color,
                   x=None, y=None, z=None,
                   levels_x=None, levels_y=None, levels_z=None,
                   range_x=None, range_y=None, range_z=None,
                   palette=None, color_number=None,
                   **kwargs):

        self.aggregator.reset()

        numeric = "COQ_FREQ"
        self._xlab = self.DEFAULT_LABEL
        self._ylab = self.DEFAULT_LABEL

        if (x and y and (data[x].dtype != object or data[y].dtype != object)):
            # one of the two given variable is numeric, let seaborn do most
            # of the magic
            self._xlab = x
            self._ylab = y
            args = {"x": data[x], "y": data[y],
                    "order": (levels_x if data[x].dtype == object else
                              levels_y)}
        else:
            if (x and not y) or (x and y and not BarPlot.horizontal):
                # set up for vertical bars
                self._xlab = x
                args = {"x": x, "order": levels_x,
                        "y": numeric,
                        "hue": y, "hue_order": levels_y}
                self.aggregator.add(x, "count", name=numeric)
            else:
                # set up for horizontal bars
                self._ylab = y
                args = {"y": y, "order": levels_y,
                        "x": numeric,
                        "hue": x, "hue_order": levels_x}
                self.aggregator.add(y, "count", name=numeric)

            # Add hue variable to aggregation:
            if z:
                hues = "COQ_HUE"
                if data[z].dtype == object:
                    self.aggregator.add(z, "mode", name=hues)
                else:
                    self.aggregator.add(z, "mean", name=hues)

            df = self.aggregator.process(data, list(filter(None, [x, y])))
            args["data"] = df

            # Take care of a hue variable:
            if z:
                if data[z].dtype == object:
                    self._colorizer = ColorizeByFactor(
                        palette, color_number, levels_z)
                    self._colorizer.set_title_frm("Most frequent {z}")
                else:
                    self._colorizer = ColorizeByNum(
                        palette, color_number, df[hues])
                    self._colorizer.set_title_frm("Mean {z}")
                cols = self._colorizer.get_hues(data=df[hues])

        if not z:
            self._colorizer = Colorizer(palette, color_number, args["order"])
            cols = self._colorizer.get_hues(data=df[x if x else y])
            self.legend_title = args["hue"]
            self.legend_levels = args["hue_order"]
        else:
            self.legend_title = self._colorizer.legend_title(z)
            self.legend_levels = self._colorizer.legend_levels()

        self.legend_palette = self._colorizer.get_palette(
            n=len(self.legend_levels))
        self.plt_func(**args, palette=cols, ax=plt.gca())

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 1 or len(cat) == 0:
            return False

        return True


class StackedBars(BarPlot):
    """
    Stacked bar chart

    The stacked bars are produced by overplotting several bar plots on the
    same axes using sns.barplot().
    """
    name = "Stacked bars"
    icon = "Barchart_stacked"

    focus = 0
    sort = 0

    #def get_custom_widgets(self, **kwargs):
        #x = kwargs.get("x", None)
        #y = kwargs.get("y", None)
        #hue = kwargs.get("z", None)

        #levels_x = kwargs.get("levels_x", None)
        #levels_y = kwargs.get("levels_y", None)
        #levels_z = kwargs.get("levels_z", None)

        #layout = QtWidgets.QGridLayout()
        #tr = QtWidgets.QApplication.instance().translate

        #focus_label = QtWidgets.QLabel(tr("StackedBars", "Set focus:", None))
        #sort_label = QtWidgets.QLabel(tr("StackedBars", "Sort by:", None))
        #button = tr("StackedBars", "Apply", None)

        #StackedBars.combo_focus = QtWidgets.QComboBox()
        #StackedBars.combo_sort = QtWidgets.QComboBox()
        #StackedBars.button_apply = QtWidgets.QPushButton(button)
        #StackedBars.button_apply.setDisabled(True)

        #if levels_x and not levels_y:
            #entries = levels_x
        #else:
            #entries = levels_y

        #entries.insert(0, tr("StackedBars", "(none)", None))

        #StackedBars.combo_focus.addItems(entries)
        #StackedBars.combo_sort.addItems(entries)

        #StackedBars.button_apply.clicked.connect(
            #lambda: StackedBars.update_figure(
                #self,
                #StackedBars.combo_focus.currentIndex(),
                #StackedBars.combo_sort.currentIndex()))
        #StackedBars.combo_focus.currentIndexChanged.connect(
            #lambda x: StackedBars.button_apply.setEnabled(True))
        #StackedBars.combo_sort.currentIndexChanged.connect(
            #lambda x: StackedBars.button_apply.setEnabled(True))

        #self.focus = 0
        #self.sort = 0

        #layout.addWidget(focus_label, 0, 0)
        #layout.addWidget(sort_label, 1, 0)
        #layout.addWidget(StackedBars.combo_focus, 0, 1)
        #layout.addWidget(StackedBars.combo_sort, 1, 1)

        #h_layout = QtWidgets.QHBoxLayout()
        #h_layout.addWidget(QtWidgets.QLabel())
        #h_layout.addWidget(StackedBars.button_apply)
        #h_layout.addWidget(QtWidgets.QLabel())
        #h_layout.setStretch(0, 1)
        #h_layout.setStretch(2, 1)

        #layout.addLayout(h_layout, 2, 0, 1, 3)

        #layout.setColumnStretch(0, 1)
        #layout.setColumnStretch(1, 3)

        #return [layout]

    @staticmethod
    def transform(series):
        return series.values.cumsum()

    @staticmethod
    def group_transform(grp, numeric):
        return grp[numeric].cumsum()

    def plt_func(self, x, y, hue, order, hue_order, data, palette, ax,
                 *args, **kwargs):
        """
        Plot the stacked bars.

        The method uses the aggregated tables produced by the normal bar plot.
        Either 'x' or 'y' is numeric and contains the count data, while the
        other variable is the main grouping variable. The 'hue' variable
        contains the subordinate category (if applicable).
        """

        if data[x].dtype == object:
            num = "y"
            cat = "x"
            category = x
            numeric = y
        else:
            num = "x"
            cat = "y"
            category = y
            numeric = x

        if hue:
            # If a subordinate category is given as the 'hue' argument,
            # the data is split into groups defined by the main category.
            # Within each group, the numeric variable is transformed using
            # the group_transform() method, which calculates the cumulative
            # sum within each group.
            data = data.sort_values([category, hue])
            data = data.reset_index(drop=True)
            data[numeric] = (data.groupby(category)
                                 .apply(self.group_transform, numeric)
                                 .reset_index(0)[numeric])
            values = hue_order

        else:
            # If no subordinate category is given, the numeric variable is
            # just the cumulative sum.
            values = self.transform(data[numeric])

        for val, col in reversed(list(zip(values, palette))):
            if hue:
                # Create a data frame that merges the counts for the current
                # hue value with all expected subordinate category values.
                # This data frame is then used to plot the bars of the current
                # hue value.
                df = (pd.merge(data[data[hue] == val],
                               pd.DataFrame({category: order, hue: val}),
                               how="right")
                        .fillna(pd.np.nan)
                        .sort_values(by=category)
                        .reset_index(drop=True))

                kwargs = {num: numeric, cat: category, "data": df}
            else:
                kwargs = {num: val}

            sns.barplot(**kwargs, color=col, ax=ax)

    @classmethod
    def update_figure(cls, self, focus, sort):
        cls.focus = focus
        cls.sort = sort
        cls.button_apply.setDisabled(True)
        self.updateRequested.emit()


class PercentBars(StackedBars):
    """
    Stacked bar chart showing percentages

    This class redefines the transform() and the group_transform() methods
    from the StackedBars parent class so that they represent percentages.
    """
    name = "Percentage bars"
    icon = "Barchart_percent"

    DEFAULT_LABEL = "Percentage"

    @staticmethod
    def transform(series):
        return (series * 100 / series.sum()).cumsum()

    @staticmethod
    def group_transform(grp, numeric):
        return (grp[numeric] * 100 / grp[numeric].sum()).cumsum()


provided_visualizations = [BarPlot, StackedBars, PercentBars]

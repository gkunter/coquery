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
    COL_COLUMN = "COQ_HUE"
    NUM_COLUMN = "COQ_NUM"
    RGB_COLUMN = "COQ_RGB"
    SEM_COLUMN = "COQ_SEM"
    vertical = True

    def plt_func(self, **kwargs):
        #def _errorbar(mean, sem):
            #upper = mean + sem
            #lower = mean - sem
        data = kwargs.get("data")
        ax = sns.barplot(**kwargs)

        if self.SEM_COLUMN in data.columns:
            if kwargs.get("y") == self.NUM_COLUMN:
                ax.errorbar(x=list(range(len(data))),
                            y=data[self.NUM_COLUMN],
                            yerr=data[self.SEM_COLUMN],
                            linestyle="")
            elif kwargs.get("x") == self.NUM_COLUMN:
                ax.errorbar(y=list(range(len(data))),
                            x=data[self.NUM_COLUMN],
                            xerr=data[self.SEM_COLUMN],
                            linestyle="")
        return ax

    def get_custom_widgets(self, *args, **kwargs):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QApplication.instance().translate(
                    "BarPlot", "Prefer vertical bars where possible", None)
        button = QtWidgets.QApplication.instance().translate(
                    "Visualizer", "Apply", None)

        BarPlot.check_direction = QtWidgets.QCheckBox(label)
        BarPlot.check_direction.setCheckState(
            QtCore.Qt.Checked if BarPlot.vertical else
            QtCore.Qt.Unchecked)

        BarPlot.button_apply = QtWidgets.QPushButton(button)
        BarPlot.button_apply.setDisabled(True)
        BarPlot.button_apply.clicked.connect(
            lambda: BarPlot.update_figure(
                self, BarPlot.check_direction.checkState()))

        BarPlot.check_direction.stateChanged.connect(
            lambda x: BarPlot.button_apply.setEnabled(True))

        layout.addWidget(BarPlot.check_direction)
        layout.addWidget(BarPlot.button_apply)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        return [layout]

    @classmethod
    def update_figure(cls, self, i):
        cls.vertical = bool(i)
        BarPlot.button_apply.setDisabled(True)
        self.updateRequested.emit()

    def prepare_arguments(self, data, x, y, z,
                          levels_x, levels_y, z_statistic=None,
                          colorizer=None):
        """
        Return a dictionary representing the arguments that will be passed on
        to plt_func().
        """
        aggregator = vis.Aggregator()

        if (x and y and (data[x].dtype != object or data[y].dtype != object)):
            # one of the two given variable is numeric, let seaborn do most
            # of the magic
            if data[x].dtype == object:
                ax_cat, ax_num = "x", "y"
                grouping, target = x, y
                order = levels_x
            else:
                ax_cat, ax_num = "y", "x"
                grouping, target = y, x
                order = levels_y
            numeric = self.NUM_COLUMN
            hue, hue_order = None, None
            data[self.COL_COLUMN] = data[grouping]
            aggregator.add(target, "mean", name=numeric)
            aggregator.add(target, "ci", name=self.SEM_COLUMN)
            data = aggregator.process(data, [grouping])
            data[self.COL_COLUMN] = data[grouping]
        else:
            if x:
                if not y:
                    ax_cat, ax_num = "x", "y"
                else:
                    ax_cat, ax_num = (("x", "y") if self.vertical else
                                      ("y", "x"))
                grouping, hue = x, y
                order, hue_order = levels_x, levels_y
            else:
                ax_cat, ax_num = "y", "x"
                grouping, hue = y, x
                order, hue_order = levels_y, levels_x

            numeric = self.NUM_COLUMN

            if hue:
                aggregator.add(hue, "count", name=numeric)
            else:
                aggregator.add(grouping, "count", name=numeric)

            # Add hue variable to aggregation:
            if z:
                if z_statistic is None:
                    z_statistic = ("mode" if data[z].dtype == object else
                                   "mean")
                aggregator.add(z, z_statistic, name=self.COL_COLUMN)

            data = aggregator.process(data, list(filter(None, [x, y])))

            if z:
                if z == x:
                    data[self.COL_COLUMN] = data[x]
                elif z == y:
                    data[self.COL_COLUMN] = data[y]
            else:
                if x and not y:
                    data[self.COL_COLUMN] = data[x]
                elif y and not x:
                    data[self.COL_COLUMN] = data[y]
                else:
                    data[self.COL_COLUMN] = data[hue]

        if colorizer:
            data[self.RGB_COLUMN] = colorizer.get_hues(data[self.COL_COLUMN])

        args = {ax_cat: grouping, "order": order,
                ax_num: numeric,
                "hue": hue, "hue_order": hue_order,
                "data": data}

        return args

    def plot_facet(self,
                   data, color,
                   x=None, y=None, z=None,
                   levels_x=None, levels_y=None, levels_z=None,
                   range_x=None, range_y=None, range_z=None,
                   palette=None, color_number=None,
                   **kwargs):

        self._xlab = self.DEFAULT_LABEL
        self._ylab = self.DEFAULT_LABEL

        if (x and y and (data[x].dtype != object or data[y].dtype != object)):
            # one of the two given variable is numeric, let seaborn do most
            # of the magic
            self._xlab = x
            self._ylab = y
        else:
            if (x and not y) or (x and y and not BarPlot.vertical):
                self._xlab = x
            else:
                self._ylab = y

        args = self.prepare_arguments(data, x, y, z, levels_x, levels_y)

        # Take care of a hue variable:
        if z:
            if args["data"][self.COL_COLUMN].dtype == object:
                self._colorizer = ColorizeByFactor(
                    palette, color_number, levels_z)
                self._colorizer.set_title_frm("Most frequent {z}")
            else:
                self._colorizer = ColorizeByNum(
                    palette, color_number, args["data"][self.COL_COLUMN])
                self._colorizer.set_title_frm("Mean {z}")
            cols = self._colorizer.get_hues(args["data"][self.COL_COLUMN])
            self.legend_title = self._colorizer.legend_title(z)
            self.legend_levels = self._colorizer.legend_levels()
        else:
            self._colorizer = Colorizer(palette, color_number, args["order"])
            cols = self._colorizer.get_hues(args["data"][x if x else y])
            self.legend_title = args["hue"]
            self.legend_levels = args["hue_order"]

        #self.legend_palette = self._colorizer.get_palette(
            #n=len(self.legend_levels))

        print(args)
        ax = self.plt_func(**args, palette=cols, ax=plt.gca())

        # add fix for cases where the bar color is specified by teh same
        # column as either the first or the second data column:
        if z and x and y:
            for i, cont in enumerate(ax.containers):
                for j, art in enumerate(cont):
                    if z == y:
                        art.set_facecolor(self.legend_palette[j])
                    elif z == x:
                        art.set_facecolor(self.legend_palette[i])

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
        print(x, y, hue)

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

        if hue or len(order) == 1:
            # If a subordinate category is given as the 'hue' argument,
            # the data is split into groups defined by the main category.
            # Within each group, the numeric variable is transformed using
            # the group_transform() method, which calculates the cumulative
            # sum within each group.
            data = data.sort_values([category, hue])
            data = data.reset_index(drop=True)

            if len(order) > 1:
                data[numeric] = (data.groupby(category)
                                        .apply(self.group_transform, numeric)
                                        .reset_index(0)[numeric])

            values = hue_order

        else:
            # If no subordinate category is given, or if the subordinate
            # category has just one value, the numeric variable is just the
            # cumulative sum:
            values = self.transform(data[numeric])

        for val, col in reversed(list(zip(values, palette))):
            if hue:
                # Create a data frame that merges the counts for the current
                # hue value with all expected subordinate category values.
                # This data frame is then used to plot the bars of the current
                # hue value.
                df = pd.merge(data[data[hue] == val],
                              pd.DataFrame({category: order, hue: val}),
                              how="right")
                df = df.fillna(pd.np.nan)
                df = df.sort_values(by=category)
                df = df.reset_index(drop=True)

                kwargs = {num: numeric, cat: category, "data": df}
            else:
                kwargs = {num: val}

            _ax = sns.barplot(**kwargs, color=col, ax=ax)

        # add fix for cases where the bar color is specified by teh same
        # column as either the first or the second data column:
        print(hue, x, y, category)
        if hue and x and y:
            rev = self.legend_palette
            for i, cont in enumerate(_ax.containers):
                for j, art in enumerate(cont):
                    if hue == y:
                        art.set_facecolor((self.legend_palette)[j])
                    else:
                        print(i, rev[i])
                        art.set_facecolor(rev[1])


        self._category = category
        self._values = values

        return _ax

    def plot_facet(self, data, color, **kwargs):
        super(StackedBars, self).plot_facet(data, color, **kwargs)

        if not self.legend_levels:
            if self._category == kwargs.get("x"):
                self.legend_levels = kwargs.get("levels_x")
            else:
                self.legend_levels = kwargs.get("levels_x")
            self.legend_title = self._category
            self.legend_palette = self._colorizer.get_palette(
                len(self.legend_levels))

        #if not(kwargs.get("x") and kwargs.get("y")):
            #if self._category == kwargs.get("x"):
                #levels = kwargs.get("levels_x")
            #else:
                #levels = kwargs.get("levels_y")

            #if self.legend_levels:
                #self.legend_levels = ["{}: {}".format(x, y)
                                #for x, y in zip(levels, self.legend_levels)]
                ##self.legend_title = "{}: {}".format(
                    ##self._category, self.legend_title)

            #else:
                #self.legend_levels = levels
                #self.legend_title = self._category

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

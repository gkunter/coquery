# -*- coding: utf-8 -*-
"""
barplot.py is part of Coquery.

Copyright (c) 2016–2021 Gero Kunter (gero.kunter@coquery.org)

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
import itertools

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets, QtCore, tr


class BarPlot(vis.Visualizer):
    name = "Barplot"
    icon = "Barchart"

    axes_style = "whitegrid"
    DEFAULT_LABEL = "Frequency"
    COL_COLUMN = "COQ_HUE"
    NUM_COLUMN = "COQ_NUM"
    RGB_COLUMN = "COQ_RGB"
    SEM_COLUMN = "COQ_SEM"   # this column contains the standard error
    vertical = True

    def plt_func(self, **kwargs):
        ax = sns.barplot(**kwargs)

        data = kwargs.get("data")
        style = {"linestyle": "", "ecolor": "black"}
        # add error bars if there is a standard error column in the data set
        if self.SEM_COLUMN in data.columns:
            if kwargs.get("y") == self.NUM_COLUMN:
                ax.errorbar(x=list(range(len(data))),
                            y=data[self.NUM_COLUMN],
                            yerr=data[self.SEM_COLUMN],
                            **style)
            elif kwargs.get("x") == self.NUM_COLUMN:
                ax.errorbar(y=list(range(len(data))),
                            x=data[self.NUM_COLUMN],
                            xerr=data[self.SEM_COLUMN],
                            **style)
        return ax

    def get_custom_widgets(self, *args, **kwargs):
        label = tr("BarPlot", "Prefer vertical bars where possible", None)

        self.check_direction = QtWidgets.QCheckBox(label)
        self.check_direction.setCheckState(
            QtCore.Qt.Checked if self.vertical else QtCore.Qt.Unchecked)

        return ([self.check_direction],
                [self.check_direction.stateChanged],
                [])

    def update_values(self):
        self.vertical = self.check_direction.isChecked()

    def prepare_arguments(self, data, x, y, z,
                          levels_x, levels_y, z_statistic=None):
        """
        Return a dictionary representing the arguments that will be passed on
        to plt_func().
        """
        aggregator = vis.Aggregator()

        if x and y and (data[x].dtype != object or data[y].dtype != object):
            # one of the two given variable is numeric
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

            # Add color variable to aggregation:
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
                    data[self.COL_COLUMN] = data[y]

        args = {ax_cat: grouping, "order": order,
                ax_num: numeric,
                "hue": hue, "hue_order": hue_order,
                "data": data}

        return args

    def plot_facet(self, data, color, **kwargs):
        self.args = self.prepare_arguments(data, self.x, self.y, self.z,
                                           self.levels_x, self.levels_y)
        self.plt_func(ax=plt.gca(), **self.args)

    def colorize_artists(self, ax=None):
        if ax is None:
            ax = plt.gca()

        if ((self.x and not self.y) or (self.y and not self.x) or
                (self.df[self.x].dtype != object) or
                (self.df[self.y].dtype != object)):
            # colorize one categorical series (either with or without a
            # numeric series):
            if not self.z:
                if self.x and self.df[self.x].dtype == object:
                    levels = self.levels_x
                else:
                    levels = self.levels_y

                rgb = self.colorizer.get_hues(levels)
            else:
                df = self.args["data"]
                rgb = self.colorizer.get_hues(df[:, self.COL_COLUMN])

            assert len(ax.containers[0]) == len(rgb)

            for i, art in enumerate(ax.containers[0]):
                art.set_facecolor(rgb[i])
        else:
            # colorize two categorical series
            data = self.args["data"]
            rgb = self.colorizer.get_hues(data[:, self.COL_COLUMN])
            data[self.RGB_COLUMN] = rgb

            for i, cont in enumerate(ax.containers):
                val_y = self.levels_y[i]
                for j, art in enumerate(cont):
                    val_x = self.levels_x[j]
                    row = data[(data[self.x] == val_x) &
                               (data[self.y] == val_y)]
                    if len(row):
                        color = row[:, self.RGB_COLUMN].tolist()[0]
                        art.set_facecolor(color)

    def set_titles(self):
        self._xlab, self._ylab = BarPlot.DEFAULT_LABEL, BarPlot.DEFAULT_LABEL
        if self.args["x"] != self.NUM_COLUMN:
            self._xlab = self.x
        else:
            self._ylab = self.y

    def get_subordinated(self, x, y):
        if x and y:
            if self.df[y].dtype == object:
                return y
            else:
                return x
        else:
            return x or y

    def suggest_legend(self):
        return (self.z or
                not ((self.x and not self.y) or
                     (self.y and not self.x) or
                     (self.df[self.x].dtype != self.df[self.y].dtype)))

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

    #def update_figure(cls, self, focus, sort):
        #cls.focus = focus
        #cls.sort = sort
        #cls.button_apply.setDisabled(True)

    @staticmethod
    def transform(series):
        return series.cumsum()

    @staticmethod
    def group_transform(grp, numeric):
        return grp[numeric].cumsum()

    def suggest_legend(self):
        """
        Stacked bars will always suggest a legend.
        """
        return True

    def colorize_artists(self, ax=None):
        if ax is None:
            ax = plt.gca()

        if self.x and not self.y:
            cols = self.colorizer.get_palette(len(self.levels_x))
        elif self.y and not self.x:
            cols = self.colorizer.get_palette(len(self.levels_y))
        else:
            cols = self.colorizer.get_palette(len(self.levels_y))

        for col, cont in zip(cols, ax.containers[::-1]):
            for act in cont:
                act.set_facecolor(col)

    def set_titles(self):
        self._xlab, self._ylab = BarPlot.DEFAULT_LABEL, BarPlot.DEFAULT_LABEL
        if self.x and not self.y:
            self._xlab = self.x
        elif self.y and not self.x:
            self._ylab = self.y
        else:
            if self.df[self.y].dtype == object:
                if self.df[self.x].dtype == object:
                    if self.vertical:
                        self._xlab = self.x
                    else:
                        self._ylab = self.y
                else:
                    self._ylab = self.y
            else:
                self._xlab = self.x

    def prepare_arguments(self, data, x, y, z,
                          levels_x, levels_y, z_statistic=None):
        args = super(StackedBars, self).prepare_arguments(
            data, x, y, z, levels_x, levels_y, z_statistic)

        if args["x"] != self.NUM_COLUMN:
            num = "y"
            cat = "x"
            category = args["x"]
        else:
            num = "x"
            cat = "y"
            category = args["y"]

        if args["hue"] or len(args["order"]) == 1:
            # If a subordinate category is given as the 'z' argument,
            # the data is split into groups defined by the main category.
            # Within each group, the numeric variable is transformed using
            # the group_transform() method, which calculates the cumulative
            # sum within each group.

            # FIXME: I'm pretty sure that the code used below to calculate the
            # cumulative sums can be streamlined!

            if args["hue"]:
                levels = args["hue_order"]
                data = args["data"].sort_values([category, args["hue"]])
            else:
                levels = args["order"]
                data = args["data"].sort_values([category])

            data = data.reset_index(drop=True)

            if len(data[category].unique()) > 1:
                df = (data.groupby(category, dropna=False)
                          .apply(self.group_transform, self.NUM_COLUMN)
                          .reset_index(0))
                data[self.NUM_COLUMN] = df[self.NUM_COLUMN]
            else:
                data[self.NUM_COLUMN] = self.transform(data[self.NUM_COLUMN])

            if args["hue_order"]:
                expand = pd.DataFrame(
                    data=list(itertools.product(args["order"],
                                                args["hue_order"])),
                    columns=[category, self.COL_COLUMN])

                df = (data.merge(expand, how="right")
                          .sort_values(by=[category]))
            else:
                df = data
        else:
            # If no subordinate category is given, or if the subordinate
            # category has just one value, the numeric variable is just the
            # cumulative sum:

            if cat == "x":
                levels = levels_x
            else:
                levels = levels_y
            df = pd.DataFrame({category: levels})
            df = df.merge(args["data"], how="left")
            df[self.NUM_COLUMN] = self.transform(df[self.NUM_COLUMN])
            df[self.COL_COLUMN] = df[category]

        args = {num: self.NUM_COLUMN, cat: category,
                "levels": levels, "data": df}
        return args

    def plt_func(self, **kwargs):
        levels = kwargs.pop("levels")
        df = kwargs.pop("data")
        for val in levels[::-1]:
            _ax = sns.barplot(data=df[df[self.COL_COLUMN] == val], **kwargs)
        else:
            _ax = plt.gca()

        if not (self.x and self.y):
            if kwargs["x"] != self.NUM_COLUMN:
                _ax.set_xticklabels([])
            else:
                _ax.set_yticklabels([])
        return _ax


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

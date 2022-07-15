# -*- coding: utf-8 -*-
"""
stackedbarplot.py is part of Coquery.

Copyright (c) 2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import itertools

import pandas as pd
import seaborn as sns

from coquery.visualizer.visualizer import VisualizerStatus
from coquery.visualizer.barplot import BarPlot


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

    def set_titles(self, **kwargs):
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
                          levels_x, levels_y, z_statistic=None, **kwargs):
        args = super(StackedBars, self).prepare_arguments(
            data, x, y, z, levels_x, levels_y, z_statistic, **kwargs)

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

        containers = []

        for val in levels[::-1]:
            ax = sns.barplot(data=df[df[self.COL_COLUMN] == val],
                             edgecolor="black", **kwargs)
            containers.append(ax.containers)
        return containers

    def get_colors(self, colorizer, elements, **kwargs):

        # if (bool(self.x) != bool(self.y) or
        #         any([dtype != object for dtype in
        #              self.df[[self.x, self.y]]])):
        #     # only one categorical (either with or without a numeric
        #     # variable):
        #     if not self.z:
        #         levels = self.levels_x if self.x else self.levels_y
        #         hues = self.colorizer.get_hues(levels)
        #         rgb = [[hue] for hue in hues][::-1]
        #     else:
        #         df = pd.merge(
        #             pd.DataFrame({
        #                 self.x: self.levels_x * len(self.levels_y),
        #                 self.y: pd.np.repeat(self.levels_y,
        #                                      len(self.levels_x))}),
        #             kwargs["data"],
        #             on=[self.x, self.y], how="left")
        #         hues = self.colorizer.get_hues(df[self.COL_COLUMN])
        #         rgb = pd.np.split(pd.np.array(hues), len(self.levels_y))[::-1]
        #
        # return rgb or ["green"] * len(elements)
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
                hues = [self.colorizer.get_hues(levels)[0]] * len(levels)
            else:
                df = kwargs["data"]
                hues = self.colorizer.get_hues(df[self.COL_COLUMN])
            rgb = [hues]
        else:
            # colorize two categorical series
            if not self.z:
                hues = self.colorizer.get_hues(self.levels_y)
                rgb = [[col] * len(self.levels_x) for col in hues]
            else:
                df = pd.merge(
                    pd.DataFrame({
                        self.x: self.levels_x * len(self.levels_y),
                        self.y: pd.np.repeat(self.levels_y,
                                             len(self.levels_x))}),
                    kwargs["data"],
                    on=[self.x, self.y], how="left")
                hues = self.colorizer.get_hues(df[self.COL_COLUMN])
                rgb = pd.np.split(pd.np.array(hues), len(self.levels_y))
        return rgb

    def colorize_elements(self, elements, colors):
        for container, color_list in zip(elements, colors):
            for artist, color in zip(container, color_list):
                artist.set_facecolor(color)


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


updated_to_new_interface = VisualizerStatus.Incomplete
provided_visualizations = [StackedBars, PercentBars]

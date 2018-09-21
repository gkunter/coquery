# -*- coding: utf-8 -*-
"""
This module tests the beeswarm plot visualizer module.

Run it like so:

coquery$ python -m test.vis.test_beeswarmplot

"""

import unittest
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from test.testcase import CoqTestCase
from coquery.visualizer.beeswarmplot import BeeswarmPlot

from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum)


class TestBeeswarmPlot(CoqTestCase):
    ID_COLUMN = "ID"

    def setUp(self):
        self.vis = BeeswarmPlot(None, None, id_column=self.ID_COLUMN)
        self.df = CoqTestCase.get_default_df()
        plt.gca().clear()

    def test_horizontal_no_subgroup(self):
        """
        Basic test: only a single numerical variable along the `X` axis
        """
        values = self.vis.get_id_values(self.df)
        dummy_grouping = pd.Series([""] * len(self.df))
        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=None, z=None,
                                          levels_x=None, levels_y=None)

        target = {"x": values,
                  "y": dummy_grouping,
                  "z": None,
                  "order": None,
                  "horizontal": True}

        self.assertDictEqual(args, target)

    def test_vertical_no_subgroup(self):
        """
        Basic test: force a vertical plot
        """
        self.vis.force_horizontal = False

        values = self.vis.get_id_values(self.df)
        dummy_grouping = pd.Series([""] * len(self.df))
        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=None, z=None,
                                          levels_x=None, levels_y=None)

        target = {"x": dummy_grouping,
                  "y": values,
                  "z": None,
                  "order": None,
                  "horizontal": False}

        self.assertDictEqual(args, target)

    def test_horizontal_subgroup(self):
        """
        Horizontal plot with grouping variable `Y`
        """
        values = self.vis.get_id_values(self.df)
        category = "Y"
        grouping = self.df[category]
        levels = sorted(grouping.unique())
        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=category, z=None,
                                          levels_x=None, levels_y=levels)

        target = {"x": values,
                  "y": grouping,
                  "z": None,
                  "order": levels,
                  "horizontal": True}

        self.assertDictEqual(args, target)

    def test_vertical_subgroup(self):
        """
        Vertical plot with grouping variable `X`
        """
        self.vis.force_horizontal = False
        values = self.vis.get_id_values(self.df)
        category = "X"
        grouping = self.df[category]
        levels = sorted(grouping.unique())
        args = self.vis.prepare_arguments(data=self.df,
                                          x=category, y=None, z=None,
                                          levels_x=levels, levels_y=None)

        target = {"x": grouping,
                  "y": values,
                  "z": None,
                  "order": levels,
                  "horizontal": False}

        self.assertDictEqual(args, target)

    def test_colorizer_default(self):
        """
        Use default colorization.

        The default behavior is to use the first color of the palette.
        Alternatively, this might be changed so that the dot colors cicle
        through the palette.
        """
        params = self.vis.prepare_arguments(data=self.df,
                                            x=None, y=None, z=None,
                                            levels_x=None, levels_y=None)
        palette = sns.color_palette("Paired", 6)
        colorizer = Colorizer(palette, len(palette))

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)
        target = [colorizer.mpt_to_hex([palette[0]] * len(self.df))]

        pd.np.testing.assert_array_equal(colors, target)

    def test_colorizer_factor(self):
        """
        Use a factor as colorizer variable
        """
        factor = "Z"
        fact_levels = sorted(self.df[factor].unique())
        params = self.vis.prepare_arguments(data=self.df,
                                            x=None, y=None, z=factor,
                                            levels_x=None, levels_y=None)
        palette = sns.color_palette("Paired", 6)
        colorizer = ColorizeByFactor(palette, 6, fact_levels)

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)
        self.df["COQ_COLOR"] = colorizer.mpt_to_hex(
            [palette[fact_levels.index(val)] for val in params["z"]])

        target = [self.df
                      .sort_values(by=self.vis._id_column)
                      .get("COQ_COLOR")]

        pd.np.testing.assert_array_equal(colors, target)

    def test_colorizer_factor_subgroups_1(self):
        """
        Use grouping variable as colorizer factor
        """
        category = "Y"
        grouping = self.df[category]
        levels = sorted(grouping.unique())
        factor = "Y"
        fact_levels = sorted(self.df[factor].unique())
        params = self.vis.prepare_arguments(data=self.df,
                                            x=None, y=category, z=factor,
                                            levels_x=None, levels_y=levels)
        palette = sns.color_palette("Paired", 6)
        colorizer = ColorizeByFactor(palette, 6, fact_levels)

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)

        self.df["COQ_COLOR"] = colorizer.mpt_to_hex(
            [palette[fact_levels.index(val)] for val in params["z"]])

        target = [self.df["COQ_COLOR"][self.df[category] == level]
                  for level in levels]

        pd.np.testing.assert_array_equal(colors, target)

    def test_colorizer_factor_subgroups_2(self):
        """
        Use a distinct colorizer factor
        """
        category = "Y"
        grouping = self.df[category]
        levels = sorted(grouping.unique())
        factor = "Z"
        fact_levels = sorted(self.df[factor].unique())
        params = self.vis.prepare_arguments(data=self.df,
                                            x=None, y=category, z=factor,
                                            levels_x=None, levels_y=levels)
        palette = sns.color_palette("Paired", 6)
        colorizer = ColorizeByFactor(palette, 6, fact_levels)

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)

        self.df["COQ_COLOR"] = colorizer.mpt_to_hex(
            [palette[fact_levels.index(val)] for val in params["z"]])

        target = [(self.df[self.df[category] == level]
                       .sort_values(by=self.vis._id_column)
                       .get("COQ_COLOR"))
                  for level in levels]

        pd.np.testing.assert_array_equal(colors, target)

    def test_colorizer_num(self):
        """
        Use a numeric variable for colorization
        """
        numeric = "NUM"

        params = self.vis.prepare_arguments(data=self.df,
                                            x=None, y=None, z=numeric,
                                            levels_x=None, levels_y=None)
        palette = sns.color_palette("Paired", 5)
        colorizer = ColorizeByNum(palette, len(palette), self.df[numeric],
                                  vrange=(0, 100))

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)
        target = [colorizer.mpt_to_hex(
            [palette[4 - (val // 20)] for val
             in self.df.sort_values(by=self.vis._id_column)[numeric]])]

        pd.np.testing.assert_array_equal(colors, target)


class TestBeeswarmPlotRandomized(TestBeeswarmPlot):
    def setUp(self):
        super(TestBeeswarmPlotRandomized, self).setUp()
        self.df = self.df.sample(frac=1)

provided_tests = (
    TestBeeswarmPlot,
    TestBeeswarmPlotRandomized,
    )


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

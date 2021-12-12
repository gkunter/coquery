# -*- coding: utf-8 -*-
"""
This module tests the boxplot visualizer module.

Run it like so:

coquery$ python -m test.vis.test_boxplot

"""

import unittest
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from coquery.visualizer.boxplot import BoxPlot
from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum)

from test.testcase import CoqTestCase


class TestBoxPlot(CoqTestCase):
    ID_COLUMN = "ID"

    def setUp(self):
        self.vis = BoxPlot(None, None, id_column=self.ID_COLUMN)
        self.vis.draw_boxen = False
        self.df = self.get_default_df()
        plt.gca().clear()

    def test_horizontal_no_subgroup(self):
        """
        Basic test: only a single numerical variable along the `X` axis
        """
        numerical = "NUM"
        args = self.vis.prepare_arguments(data=self.df,
                                          x=numerical, y=None, z=None,
                                          levels_x=None, levels_y=None)
        values = self.df[numerical]
        target = {"x": values,
                  "y": None,
                  "order": None}
        self.assertDictEqual(args, target)

    def test_vertical_no_subgroup(self):
        """
        Basic test: only a single numerical variable along the `Y` axis
        """
        numerical = "NUM"
        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=numerical, z=None,
                                          levels_x=None, levels_y=None)
        values = self.df[numerical]
        target = {"x": None,
                  "y": values,
                  "order": None}
        self.assertDictEqual(args, target)

    def test_horizontal_subgroup(self):
        """
        Basic test: only a single numerical variable along the `X` axis
        """
        numerical = "NUM"
        category = "X"
        levels = sorted(self.df[category].unique())
        args = self.vis.prepare_arguments(data=self.df,
                                          x=numerical, y=category, z=None,
                                          levels_x=None, levels_y=levels)
        target = {"x": self.df[numerical],
                  "y": self.df[category],
                  "order": levels}
        self.assertDictEqual(args, target)

    def test_vertical_subgroup(self):
        """
        Basic test: only a single numerical variable along the `X` axis
        """
        numerical = "NUM"
        category = "X"
        levels = sorted(self.df[category].unique())
        args = self.vis.prepare_arguments(data=self.df,
                                          x=category, y=numerical, z=None,
                                          levels_x=levels, levels_y=None)
        target = {"x": self.df[category],
                  "y": self.df[numerical],
                  "order": levels}
        self.assertDictEqual(args, target)

    def test_horizontal_no_subgroup_get_colors(self):
        numerical = "NUM"
        args = self.vis.prepare_arguments(data=self.df,
                                          x=numerical, y=None, z=None,
                                          levels_x=None, levels_y=None)
        palette = sns.color_palette("Paired", 6)
        colorizer = Colorizer(palette)
        elements = self.vis.plot_facet(**args)
        colors = self.vis.get_colors(colorizer, elements, **args)
        target = [colorizer.mpt_to_hex(palette[:1])]
        np.testing.assert_array_equal(colors, target)

    def test_horizontal_subgroup_get_colors(self):
        numerical = "NUM"
        category = "X"
        levels = sorted(self.df[category].unique())
        args = self.vis.prepare_arguments(data=self.df,
                                          x=numerical, y=category, z=None,
                                          levels_x=None, levels_y=levels)
        palette = sns.color_palette("Paired", 6)
        colorizer = Colorizer(palette)
        elements = self.vis.plot_facet(**args)
        colors = self.vis.get_colors(colorizer, elements, **args)
        target = [colorizer.mpt_to_hex([col]) for col in palette[:2]]
        np.testing.assert_array_equal(colors, target)

    def test_horizontal_no_subgroup_colorize_elements(self):
        numerical = "NUM"
        args = self.vis.prepare_arguments(data=self.df,
                                          x=numerical, y=None, z=None,
                                          levels_x=None, levels_y=None)
        palette = sns.color_palette("Paired", 6)
        colorizer = Colorizer(palette)
        elements = self.vis.plot_facet(**args)
        colors = self.vis.get_colors(colorizer, elements, **args)
        self.vis.colorize_elements(elements, colors)
        self.assertEqual(elements[0].get_facecolor()[:3],
                         palette[0][:3])

    def test_horizontal_subgroup_colorize_elements(self):
        numerical = "NUM"
        category = "X"
        levels = sorted(self.df[category].unique())
        args = self.vis.prepare_arguments(data=self.df,
                                          x=numerical, y=category, z=None,
                                          levels_x=None, levels_y=levels)
        palette = sns.color_palette("Paired", 6)
        colorizer = Colorizer(palette)
        elements = self.vis.plot_facet(**args)
        colors = self.vis.get_colors(colorizer, elements, **args)
        self.vis.colorize_elements(elements, colors)
        np.testing.assert_almost_equal(
            elements[0].get_facecolor()[:3],
            palette[0][:3])


class TestBoxenPlot(TestBoxPlot):
    def setUp(self):
        if not hasattr(sns, "boxenplot"):
            raise unittest.SkipTest
        super(TestBoxenPlot, self).setUp()
        self.vis.draw_boxen = True


provided_tests = (
    TestBoxPlot,
    TestBoxenPlot,
    )


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
This module tests the barcodeplot visualizer module.

Run it like so:

coquery$ python -m test.vis.test_barcodeplot

"""

import unittest
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from coquery.gui.pyqt_compat import QtWidgets
from coquery.visualizer.barcodeplot import BarcodePlot
from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum)

from test.testcase import CoqTestCase, CoqQtTestCase


class _MetaTestCase(CoqTestCase):
    ID_COLUMN = "ID"

    def setUp(self):
        self.vis = BarcodePlot(None, None, id_column=self.ID_COLUMN)
        self.df = self.get_default_df()
        plt.gca().clear()


class TestBarcodePlot(_MetaTestCase):
    def test_horizontal_no_subgroup(self):
        """
        Basic test: only a single numerical variable along the `X` axis
        """
        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=None, z=None,
                                          levels_x=None, levels_y=None)

        self.df = (self.df.sort_values(by=self.vis._id_column)
                          .reset_index(drop=True))
        values = self.df[self.vis._id_column]
        dummy_grouping = pd.Series([""] * len(self.df))
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

        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=None, z=None,
                                          levels_x=None, levels_y=None)

        self.df = (self.df.sort_values(by=self.vis._id_column)
                          .reset_index(drop=True))
        values = self.df[self.vis._id_column]
        dummy_grouping = pd.Series([""] * len(self.df))
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
        category = "Y"
        levels = sorted(self.df[category].unique())
        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=category, z=None,
                                          levels_x=None, levels_y=levels)

        self.df = (self.df.sort_values(by=self.vis._id_column)
                          .reset_index(drop=True))
        values = self.df[self.vis._id_column]
        grouping = self.df[category]
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
        category = "X"
        levels = sorted(self.df[category].unique())
        args = self.vis.prepare_arguments(data=self.df,
                                          x=category, y=None, z=None,
                                          levels_x=levels, levels_y=None)

        self.df = (self.df.sort_values(by=self.vis._id_column)
                          .reset_index(drop=True))
        values = self.df[self.vis._id_column]
        grouping = self.df[category]
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
        colorizer = Colorizer(palette)

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)
        target = [colorizer.mpt_to_hex([palette[0]] * len(self.df))]

        np.testing.assert_array_equal(colors, target)

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
        colorizer = ColorizeByFactor(palette, fact_levels)

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)

        self.df = self.df.sort_values(by=self.vis._id_column)
        self.df["COQ_COLOR"] = colorizer.mpt_to_hex(
            [palette[fact_levels.index(val)] for val in params["z"]])

        target = [self.df.get("COQ_COLOR")]

        self.df["COLORS"] = target[0]
        self.df["MATCH"] = self.df["COLORS"] == self.df["COQ_COLOR"]

        np.testing.assert_array_equal(colors, target)

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
        colorizer = ColorizeByFactor(palette, fact_levels)

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)

        self.df = self.df.sort_values(by=self.vis._id_column)
        self.df["COQ_COLOR"] = colorizer.mpt_to_hex(
            [palette[fact_levels.index(val)] for val in params["z"]])

        target = [self.df["COQ_COLOR"][self.df[category] == level]
                  for level in levels]

        np.testing.assert_array_equal(colors, target)

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
        colorizer = ColorizeByFactor(palette, fact_levels)

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)

        self.df = self.df.sort_values(by=self.vis._id_column)
        self.df["COQ_COLOR"] = colorizer.mpt_to_hex(
            [palette[fact_levels.index(val)] for val in params["z"]])

        target = [self.df[self.df[category] == level]["COQ_COLOR"]
                  for level in levels]

        np.testing.assert_array_equal(colors, target)

    def test_colorizer_num(self):
        """
        Use a numeric variable for colorization
        """
        numeric = "NUM"

        params = self.vis.prepare_arguments(data=self.df,
                                            x=None, y=None, z=numeric,
                                            levels_x=None, levels_y=None)
        palette = sns.color_palette("Paired", 5)
        colorizer = ColorizeByNum(palette, vrange=(0, 100))

        elements = self.vis.plot_facet(**params)
        colors = self.vis.get_colors(colorizer, elements, **params)

        target = [colorizer.mpt_to_hex(
            [palette[val // 20] for val
             in self.df.sort_values(by=self.vis._id_column)[numeric]])]
        np.testing.assert_array_equal(colors, target)

    def test_validate_data(self):
        valid1 = self.vis.validate_data(None, None, self.df, None)
        valid2 = self.vis.validate_data("X", None, self.df, None)
        valid3 = self.vis.validate_data(None, "X", self.df, None)

        self.assertTrue(valid1)
        self.assertTrue(valid2)
        self.assertTrue(valid3)

        invalid1 = self.vis.validate_data("NUM", None, self.df, None)
        invalid2 = self.vis.validate_data(None, "NUM", self.df, None)
        invalid3 = self.vis.validate_data("X", "NUM", self.df, None)
        invalid4 = self.vis.validate_data("NUM", "X", self.df, None)
        invalid5 = self.vis.validate_data("X", "Y", self.df, None)
        invalid6 = self.vis.validate_data("NUM", "NUM", self.df, None)

        self.assertFalse(invalid1)
        self.assertFalse(invalid2)
        self.assertFalse(invalid3)
        self.assertFalse(invalid4)
        self.assertFalse(invalid5)
        self.assertFalse(invalid6)


class TestBarcodePlotWidgets(CoqQtTestCase):
    def setUp(self):
        super().setUp()
        self.vis = BarcodePlot(None, None)
        self.df = self.get_default_df()

    def test_custom_widgets(self):
        tup = self.vis.get_custom_widgets()
        widgets, activate_signals, update_signals = tup
        expected_classes = [QtWidgets.QCheckBox, QtWidgets.QCheckBox]

        self.assertListEqual([type(x) for x in widgets],
                             expected_classes)

        self.assertTrue(len(activate_signals) == 2)
        self.assertListEqual(update_signals, [])


class TestBarcodePlotRandomized(TestBarcodePlot):
    """
    Run the same tests as TestBarcodePlot but with a randomized dataframe.
    """
    def setUp(self):
        super().setUp()
        self.df = self.df.sample(frac=1).reset_index(drop=True)


provided_tests = (
    TestBarcodePlot,
    TestBarcodePlotRandomized,
    TestBarcodePlotWidgets,
    )


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

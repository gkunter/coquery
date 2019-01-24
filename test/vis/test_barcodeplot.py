# -*- coding: utf-8 -*-
"""
This module tests the barcodeplot visualizer module.

Run it like so:

coquery$ python -m test.vis.test_barcodeplot

"""

import unittest
import pandas as pd
import seaborn as sns
import scipy.stats as st
import itertools
import argparse
import matplotlib.pyplot as plt

from coquery.coquery import options
from coquery.visualizer.barcodeplot import BarcodePlot
from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum)

from test.testcase import CoqTestCase


class TestBarcodePlot(CoqTestCase):
    ID_COLUMN = "ID"

    def setUp(self):
        self.vis = BarcodePlot(None, None, id_column=self.ID_COLUMN)
        self.df = self.get_default_df()
        plt.gca().clear()

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

        self.df = self.df.sort_values(by=self.vis._id_column)
        self.df["COQ_COLOR"] = colorizer.mpt_to_hex(
            [palette[fact_levels.index(val)] for val in params["z"]])

        target = [self.df.get("COQ_COLOR")]

        self.df["COLORS"] = target[0]
        self.df["MATCH"] = self.df["COLORS"] == self.df["COQ_COLOR"]

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

        self.df = self.df.sort_values(by=self.vis._id_column)
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

        self.df = self.df.sort_values(by=self.vis._id_column)
        self.df["COQ_COLOR"] = colorizer.mpt_to_hex(
            [palette[fact_levels.index(val)] for val in params["z"]])

        target = [self.df[self.df[category] == level]["COQ_COLOR"]
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


class TestBarcodePlotRandomized(TestBarcodePlot):
    def setUp(self):
        super(TestBarcodePlotRandomized, self).setUp()
        self.df = self.df.sample(frac=1).reset_index(drop=True)




    #NUM_COLUMN = "NUM"

    #def setUp(self):
        #self.vis = BarcodePlot(None, None, self.NUM_COLUMN)
        #self.df = CoqTestCase.get_default_df()

    #def test_horizontal_no_subgroup(self):
        #"""
        #Basic test: only a single numerical variable along the `X` axis
        #"""
        #args = self.vis.prepare_arguments(data=self.df,
                                          #x=None, y=None, z=None,
                                          #levels_x=None, levels_y=None)

        #target = {"values": self.df[self.NUM_COLUMN],
                  #"pos": pd.Series([0] * len(self.df),
                                   #index=self.df.index),
                  #"func": plt.vlines,
                  #"horizontal": False}

        #self.assertDictEqual(args, target)

    #def test_vertical_no_subgroup(self):
        #"""
        #Basic test: only a single numerical variable along the `Y` axis
        #"""
        #self.vis.force_horizontal = False

        #args = self.vis.prepare_arguments(data=self.df,
                                          #x=None, y=None, z=None,
                                          #levels_x=None, levels_y=None)

        #target = {"values": self.df[self.NUM_COLUMN],
                  #"pos": pd.Series([0] * len(self.df),
                                   #index=self.df.index),
                  #"func": plt.hlines,
                  #"horizontal": True}

        #self.assertDictEqual(args, target)

    #def test_horizontal_subgroup(self):
        #"""
        #Numerical variable along `Y` with grouping variable along `X`
        #"""

        #category = "X"
        #levels = sorted(self.df[category].unique())

        #args = self.vis.prepare_arguments(data=self.df,
                                          #x=category, y=None, z=None,
                                          #levels_x=levels, levels_y=None)

        #target = {"values": self.df[self.NUM_COLUMN],
                  #"pos": self.df[category].apply(
                      #lambda val: 0 if val == levels[0] else 1),
                  #"func": plt.hlines,
                  #"horizontal": True}

        #self.assertDictEqual(args, target)

    #def test_vertical_subgroup(self):
        #"""
        #Numerical variable along `X` with grouping variable along `Y`
        #"""

        #category = "X"
        #levels = sorted(self.df[category].unique())

        #args = self.vis.prepare_arguments(data=self.df,
                                          #x=None, y=category, z=None,
                                          #levels_x=None, levels_y=levels)

        #target = {"values": self.df[self.NUM_COLUMN],
                  #"pos": self.df[category].apply(
                      #lambda val: 1 if val == levels[0] else 0),
                  #"func": plt.vlines,
                  #"horizontal": False}

        #self.assertDictEqual(args, target)


class TestBarcodePlotAxisArguments(TestBarcodePlot):
    def test_horizontal_no_subgroup(self):
        """
        Basic test: only a single numerical variable along the `X` axis
        """
        ax_args = self.vis.prepare_ax_kwargs(data=self.df,
                                              x=None, y=None, z=None,
                                              levels_x=None, levels_y=None)
        target = {"yticklabels": []}
        self.assertDictEqual(ax_args, target)

    def test_vertical_no_subgroup(self):
        """
        Basic test: only a single numerical variable along the `Y` axis
        """
        self.vis.force_horizontal = False

        ax_args = self.vis.prepare_ax_kwargs(data=self.df,
                                              x=None, y=None, z=None,
                                              levels_x=None, levels_y=None)
        target = {"xticklabels": []}
        self.assertDictEqual(ax_args, target)

    def test_horizontal_subgroup(self):
        """
        Numerical variable along `Y` with grouping variable along `X`
        """

        category = "X"
        levels = sorted(self.df[category].unique())

        ax_args = self.vis.prepare_ax_kwargs(data=self.df,
                                              x=category, y=None, z=None,
                                              levels_x=levels, levels_y=None)
        target = {"xticklabels": levels,
                  "xticks": pd.np.array([0.5, 1.5]),
                  "xlim": (0, 2)}

        self.assertDictEqual(ax_args, target)

    def test_vertical_subgroup(self):
        """
        Numerical variable along `X` with grouping variable along `Y`
        """

        category = "X"
        levels = sorted(self.df[category].unique())

        ax_args = self.vis.prepare_ax_kwargs(data=self.df,
                                              x=None, y=category, z=None,
                                              levels_x=None, levels_y=levels)
        target = {"yticklabels": levels[::-1],
                  "yticks": pd.np.array([0.5, 1.5]),
                  "ylim": (0, 2)}

        self.assertDictEqual(ax_args, target)


class TestHeatbarPlotArguments(CoqTestCase):
    NUM_COLUMN = "NUM"

    def setUp(self):
        from coquery.visualizer.barcodeplot import HeatbarPlot

        # TEST DATA:
        #
        #            0         1         2         3         4
        # ID:        01234567890123456789012345678901234567890123456789
        # Tokens:      A A A A A         BBB       A    A    A     BBB

        N = [2, 4, 6, 8, 10, 20, 21, 22, 30, 35, 40, 46, 47, 48]
        X = list("AAAAA") + list("BBB") + list("AAA") + list("BBB")
        self.df = pd.DataFrame({self.NUM_COLUMN: N, "X": X})
        self.vis = HeatbarPlot(None, None, self.NUM_COLUMN)

    def test_increment_bins(self):
        """
        Test the increment_bins() method, which is responsible for
        distributing a token presence across one or two bins depending on
        whether the location of the token relative to the bin margins.

        The following table summarizes the expected behavior for different
        values of `p`, the relative position of a token id to the beginning
        of a bin. A value of p=0.0 indicates that the token is located at the
        left edge of the target bin, and a value of p=1.0 indicates that the
        token is located at the right edge of the target bin.

        The columns B(-1), B(0), B(+1) give the increments for the target bin
        B(0), the bin preceding the target bin B(-1) and the bin folloowing
        the target bin B(+1).

        The largest increment is added when p=0.5, i.e. when the token is
        located at the center of the bin. In this case, the whole increment is
        given to the target bin, and no spread to a neighboring bin takes
        place. If the token is located at the edge of a bin (p=0.0), the
        increment is spread equally across the preceding bin and the target
        bin.

        ------------------------
          P  B(-1)   B(0)  B(+1)
        ------------------------
        0.0   +0.5   +0.5
        0.1   +0.4   +0.6
        0.2   +0.3   +0.7
        0.3   +0.2   +0.8
        0.4   +0.1   +0.9
        0.5          +1.0
        0.6          +0.9  +0.1
        0.7          +0.8  +0.2
        0.8          +0.7  +0.3
        0.9          +0.6  +0.4
        ------------------------

        """

        increments = [[0.5, 0.5, 0.0],
                      [0.4, 0.6, 0.0],
                      [0.3, 0.7, 0.0],
                      [0.2, 0.8, 0.0],
                      [0.1, 0.9, 0.0],
                      [0.0, 1.0, 0.0],
                      [0.0, 0.9, 0.1],
                      [0.0, 0.8, 0.2],
                      [0.0, 0.7, 0.3],
                      [0.0, 0.6, 0.4]]

        for i, p in enumerate(pd.np.arange(0, 1, 0.1)):
            bins = [0, 0, 0]
            pd.np.testing.assert_array_almost_equal(
                increments[i],
                self.vis.increment_bins(bins, 5 + p * 5, 5))

    def test_horizontal_no_subgroup(self):
        binned = pd.np.zeros(10)

        for i in self.df[self.NUM_COLUMN]:
            binned = self.vis.increment_bins(binned, i, 5)

        args = self.vis.prepare_im_arguments(
            data=self.df,
            x=None, y=None, z=None, levels_x=None, levels_y=None,
            size=49, bw=5)

        target = {"aspect": "auto",
                  "interpolation": "gaussian",
                  "extent": (0, 49, None, None),
                  "M": pd.np.array([binned])}

        self.assertDictEqual(args, target)

    def test_vertical_no_subgroup(self):
        self.vis.force_horizontal = False

        binned = pd.np.zeros(10)

        for i in self.df[self.NUM_COLUMN]:
            binned = self.vis.increment_bins(binned, i, 5)

        args = self.vis.prepare_im_arguments(
            data=self.df,
            x=None, y=None, z=None, levels_x=None, levels_y=None,
            size=49, bw=5)

        target = {"aspect": "auto",
                  "interpolation": "gaussian",
                  "extent": (None, None, 0, 49),
                  "M": pd.np.array([binned])}

        self.assertDictEqual(args, target)

    def test_horizontal_subgroup(self):
        M = pd.np.array(pd.np.zeros((2, 10)))

        for ix in self.df.index:
            row = 0 if self.df.iloc[ix]["X"] == "A" else 1
            val = self.df.iloc[ix][self.NUM_COLUMN]
            M[row] = self.vis.increment_bins(M[row], val, 5)

        args = self.vis.prepare_im_arguments(
            data=self.df,
            x=None, y="X", z=None, levels_x=None, levels_y=["A", "B"],
            size=49, bw=5)

        target = {"aspect": "auto",
                  "interpolation": "gaussian",
                  "extent": (0, 49, None, None),
                  "M": M}

        self.assertDictEqual(args, target)

    def test_vertical_subgroup(self):
        """
        Test vertical subgroups. Group counts are the same as in
        test_horizontal_subgroup(), but the `extent` argument differs.
        """
        M = pd.np.array(pd.np.zeros((2, 10)))

        for ix in self.df.index:
            row = 0 if self.df.iloc[ix]["X"] == "A" else 1
            val = self.df.iloc[ix][self.NUM_COLUMN]
            M[row] = self.vis.increment_bins(M[row], val, 5)

        args = self.vis.prepare_im_arguments(
            data=self.df,
            x="X", y=None, z=None, levels_x=["A", "B"], levels_y=None,
            size=49, bw=5)

        target = {"aspect": "auto",
                  "interpolation": "gaussian",
                  "extent": (None, None, 0, 49, ),
                  "M": M}

        self.assertDictEqual(args, target)


provided_tests = (
    TestBarcodePlot,
    TestBarcodePlotRandomized,
    #TestBarcodePlotAxisArguments,
    #TestHeatbarPlotArguments,
    )


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

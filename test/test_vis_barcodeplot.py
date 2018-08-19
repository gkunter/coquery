# -*- coding: utf-8 -*-
"""
This module tests the barplot visualizer module.

Run it like so:

coquery$ python -m test.test_vis_barcodeplot

"""

import unittest
import pandas as pd
import seaborn as sns
import scipy.stats as st
import itertools
import argparse
import matplotlib.pyplot as plt

from coquery.coquery import options

from .testcase import CoqTestCase


class TestBarcodePlotArguments(CoqTestCase):
    NUM_COLUMN = "coquery_invisible_corpus_id"

    def setUp(self):
        options.cfg = argparse.Namespace()
        options.cfg.experimental = False

        from coquery.visualizer.barcodeplot import BarcodePlot

        pd.np.random.seed(123)
        self.df = pd.DataFrame(
            {"X": list("AAAAAAAAAAAAAAAAAAABBBBBBBBBBB"),
             "Y": list("xxxxxxxxyyyyyyyyyyyxxxxxxxyyyy"),
             "Z": list("111122221111222211221122112222"),
             self.NUM_COLUMN: pd.np.random.randint(0, 100, 30)})

        self.vis = BarcodePlot(None, None)

    def test_horizontal_no_subgroup(self):
        """
        Basic test: only a single numerical variable along the `X` axis
        """
        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=None, z=None,
                                          levels_x=None, levels_y=None)

        target = {"values": self.df[self.NUM_COLUMN],
                  "pos": pd.Series([0] * len(self.df),
                                   index=self.df.index),
                  "func": plt.vlines,
                  "horizontal": False}

        self.assertDictEqual(args, target)

    def test_vertical_no_subgroup(self):
        """
        Basic test: only a single numerical variable along the `Y` axis
        """
        self.vis.force_horizontal = False

        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=None, z=None,
                                          levels_x=None, levels_y=None)

        target = {"values": self.df[self.NUM_COLUMN],
                  "pos": pd.Series([0] * len(self.df),
                                   index=self.df.index),
                  "func": plt.hlines,
                  "horizontal": True}

        self.assertDictEqual(args, target)

    def test_horizontal_subgroup(self):
        """
        Numerical variable along `Y` with grouping variable along `X`
        """

        category = "X"
        levels = sorted(self.df[category].unique())

        args = self.vis.prepare_arguments(data=self.df,
                                          x=category, y=None, z=None,
                                          levels_x=levels, levels_y=None)

        target = {"values": self.df[self.NUM_COLUMN],
                  "pos": self.df[category].apply(
                      lambda val: 0 if val == levels[0] else 1),
                  "func": plt.hlines,
                  "horizontal": True}

        self.assertDictEqual(args, target)

    def test_vertical_subgroup(self):
        """
        Numerical variable along `X` with grouping variable along `Y`
        """

        category = "X"
        levels = sorted(self.df[category].unique())

        args = self.vis.prepare_arguments(data=self.df,
                                          x=None, y=category, z=None,
                                          levels_x=None, levels_y=levels)

        target = {"values": self.df[self.NUM_COLUMN],
                  "pos": self.df[category].apply(
                      lambda val: 1 if val == levels[0] else 0),
                  "func": plt.vlines,
                  "horizontal": False}

        self.assertDictEqual(args, target)


class TestBarcodePlotAxisArguments(TestBarcodePlotArguments):
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
    NUM_COLUMN = "coquery_invisible_corpus_id"

    def setUp(self):
        options.cfg = argparse.Namespace()
        options.cfg.experimental = False

        from coquery.visualizer.barcodeplot import HeatbarPlot

        # TEST DATA:
        #
        #            0         1         2         3         4
        # ID:        01234567890123456789012345678901234567890123456789
        # Tokens:      A A A A A         BBB       A    A    A     BBB

        N = [2, 4, 6, 8, 10, 20, 21, 22, 30, 35, 40, 46, 47, 48]
        X = list("AAAAA") + list("BBB") + list("AAA") + list("BBB")
        self.df = pd.DataFrame({self.NUM_COLUMN: N, "X": X})
        self.vis = HeatbarPlot(None, None)


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
    TestBarcodePlotArguments,
    TestBarcodePlotAxisArguments,
    TestHeatbarPlotArguments,
    )


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

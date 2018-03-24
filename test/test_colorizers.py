# -*- coding: utf-8 -*-
"""
This module tests the colorizer module.

Run it like so:

coquery$ python -m test.test_colorizers

"""

from __future__ import unicode_literals

import unittest
import os

import pandas as pd
import seaborn as sns

from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum, ColorizeByFreq,
    COQ_SINGLE)
from coquery.defines import PALETTE_BW


class TestColorizer(unittest.TestCase):
    def test_get_palette(self):
        colorizer = Colorizer("Paired", 5)
        pal = colorizer.get_palette()
        sns_pal = sns.color_palette("Paired", 5)
        self.assertListEqual(pal, sns_pal)

    def test_get_palette_rev(self):
        colorizer = Colorizer("Paired_r", 5)
        pal = colorizer.get_palette()
        sns_pal = sns.color_palette("Paired", 5)
        self.assertListEqual(pal, sns_pal[::-1])

    def test_get_palette_bw(self):
        colorizer = Colorizer(PALETTE_BW, 5)
        pal = colorizer.get_palette()
        bw_pal = [(0, 0, 0),
                  (1, 1, 1),
                  (0, 0, 0),
                  (1, 1, 1),
                  (0, 0, 0)]
        self.assertListEqual(pal, bw_pal)

    def test_get_palette_bw_rev(self):
        colorizer = Colorizer("{}_r".format(PALETTE_BW), 5)
        pal = colorizer.get_palette()
        bw_pal = [(0, 0, 0),
                  (1, 1, 1),
                  (0, 0, 0),
                  (1, 1, 1),
                  (0, 0, 0)][::-1]
        self.assertListEqual(pal, bw_pal)

    def test_get_palette_single(self):
        colorizer = Colorizer("{}_#ff0000".format(COQ_SINGLE), 5)
        pal = colorizer.get_palette()
        single_pal = [(1, 0, 0)] * 5
        self.assertListEqual(pal, single_pal)

    def test_get_hues_by_n_1(self):
        colorizer = Colorizer("Paired", 5)
        hues = colorizer.get_hues(n=13)
        sns_hues = (sns.color_palette("Paired", 5) * 2 +
                    sns.color_palette("Paired", 5)[:3])
        self.assertListEqual(hues, sns_hues)

    def test_get_hues_by_n_2(self):
        colorizer = Colorizer("Paired", 5)
        hues = colorizer.get_hues(n=3)
        sns_hues = sns.color_palette("Paired", 5)[:3]
        self.assertListEqual(hues, sns_hues)

    def test_get_hues_by_data_1(self):
        colorizer = Colorizer("Paired", 5)
        hues = colorizer.get_hues(data=range(13))
        sns_hues = (sns.color_palette("Paired", 5) * 2 +
                    sns.color_palette("Paired", 5)[:3])
        self.assertListEqual(hues, sns_hues)

    def test_get_hues_by_data_2(self):
        colorizer = Colorizer("Paired", 5)
        hues = colorizer.get_hues(data=range(3))
        sns_hues = sns.color_palette("Paired", 5)[:3]
        self.assertListEqual(hues, sns_hues)

    def test_legend_title(self):
        colorizer = Colorizer("Paired", 5)
        legend_title = colorizer.legend_title("coq_word")
        self.assertEqual(legend_title, "")

    def test_legend_palette(self):
        colorizer = Colorizer("Paired", 5)
        legend_palette = colorizer.legend_palette()
        self.assertEqual(legend_palette, [])

    def test_legend_levels(self):
        colorizer = Colorizer("Paired", 5)
        legend_levels = colorizer.legend_levels()
        self.assertListEqual(legend_levels, [])

    def test_set_title_frm(self):
        colorizer = Colorizer("Paired", 5)
        colorizer.set_title_frm("{z}")
        z = "coq_word"
        legend_title = colorizer.legend_title(z)
        self.assertEqual(legend_title, z)


class TestColorizeByFactor(unittest.TestCase):
    def test_get_hues_by_data_1(self):
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor("Paired", 5, values=["A", "B"])
        hues = colorizer.get_hues(data=list("AABBABA"))
        expected = [sns_pal[0],
                    sns_pal[0],
                    sns_pal[1],
                    sns_pal[1],
                    sns_pal[0],
                    sns_pal[1],
                    sns_pal[0]]
        self.assertListEqual(hues, expected)

    def test_get_hues_by_data_2(self):
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor("Paired", 5, values=list("ABCDEF"))
        hues = colorizer.get_hues(data=list("ABCDEFABCDEF"))
        expected = [sns_pal[0],
                    sns_pal[1],
                    sns_pal[2],
                    sns_pal[3],
                    sns_pal[4],
                    sns_pal[0],

                    sns_pal[0],
                    sns_pal[1],
                    sns_pal[2],
                    sns_pal[3],
                    sns_pal[4],
                    sns_pal[0]]

        self.assertListEqual(hues, expected)

    def test_get_hues_by_data_3(self):
        data = list("BBB")

        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor("Paired", 5, values=["A", "B"])
        hues = colorizer.get_hues(data=data)
        expected = [sns_pal[1],
                    sns_pal[1],
                    sns_pal[1]]

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_get_hues_by_data_3a(self):
        data = list("B")

        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor("Paired", 5, values=["A", "B"])
        hues = colorizer.get_hues(data=data)
        expected = [sns_pal[1]]

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_get_hues_by_data_4(self):
        data = list("AAA")

        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor("Paired", 5, values=["A", "B"])
        hues = colorizer.get_hues(data=data)
        expected = [sns_pal[0],
                    sns_pal[0],
                    sns_pal[0]]

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_get_hues_by_data_4a(self):
        data = list("A")

        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor("Paired", 5, values=["A", "B"])
        hues = colorizer.get_hues(data=data)
        expected = [sns_pal[0]]

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_legend_title(self):
        factor_column = "coq_word"
        colorizer = ColorizeByFactor("Paired", 5, values=["A", "B"])
        title = colorizer.legend_title(z=factor_column)
        self.assertEqual(title, factor_column)

    def test_legend_palette_1(self):
        colorizer = ColorizeByFactor("Paired", 5, values=["A", "B"])
        sns_pal = sns.color_palette("Paired", 5)
        pal = sns_pal[:2]
        self.assertListEqual(colorizer.legend_palette(), pal)

    def test_legend_palette_2(self):
        colorizer = ColorizeByFactor("Paired", 5, values=list("ABCDEFGHI"))
        sns_pal = sns.color_palette("Paired", 5)
        pal = sns_pal + sns_pal[:-1]
        self.assertListEqual(colorizer.legend_palette(), pal)

    def test_legend_levels(self):
        levels = list("ABCDEFGHI")
        colorizer = ColorizeByFactor("Paired", 5, values=levels)
        self.assertListEqual(colorizer.legend_levels(), levels)


class TestColorizeByNum(unittest.TestCase):
    #def test_bins_1(self):
        #vrange = (0, 100)
        #colorizer = ColorizeByNum("Paired", 5, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [0, 20, 40, 60, 80])

    #def test_bins_1a(self):
        #vrange = (5, 95)
        #colorizer = ColorizeByNum("Paired", 5, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [0, 20, 40, 60, 80])

    #def test_bins_2(self):
        #vrange = (0, 100)
        #colorizer = ColorizeByNum("Paired", 4, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [0, 25, 50, 75])

    #def test_bins_2a(self):
        #vrange = (5, 95)
        #colorizer = ColorizeByNum("Paired", 4, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [0, 25, 50, 75])

    #def test_bins_3(self):
        #vrange = (0, 1000)
        #colorizer = ColorizeByNum("Paired", 10, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [0, 100, 200, 300, 400,
                                    #500, 600, 700, 800, 900])

    #def test_bins_3a(self):
        #vrange = (5, 995)
        #colorizer = ColorizeByNum("Paired", 10, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [0, 100, 200, 300, 400,
                                    #500, 600, 700, 800, 900])

    #def test_bins_3b(self):
        #vrange = (50, 950)
        #colorizer = ColorizeByNum("Paired", 10, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [0, 100, 200, 300, 400,
                                    #500, 600, 700, 800, 900])

    #def test_bins_4(self):
        #vrange = (-200, 200)
        #colorizer = ColorizeByNum("Paired", 4, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [-200, -100, 0, 100])

    #def test_bins_4a(self):
        #vrange = (-195, 195)
        #colorizer = ColorizeByNum("Paired", 4, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [-200, -100, 0, 100])

    #def test_bins_5(self):
        #vrange = (-200, -100)
        #colorizer = ColorizeByNum("Paired", 4, vrange, int)
        #bins = list(colorizer.bins)
        #self.assertListEqual(bins, [-200, -175, -150, -125])

    def test_bins_6(self):
        vrange = (100, 200)
        colorizer = ColorizeByNum("Paired", 4, vrange, int)
        bins = list(colorizer.bins)
        self.assertListEqual(bins, [100, 125, 150, 175])

    #def __init__(self, palette, ncol, vmin, vmax, dtype):
        #super(ColorizeByNum, self).__init__(palette, ncol)
        #self.vmin = vmin
        #self.vmax = vmax
        #self.dtype = dtype
        #self.bins = pd.np.linspace(self.vmin, self.vmax,
                                   #self.ncol,
                                   #endpoint=False)
        #self.set_title_frm("{z}")

    #def get_hues(self, data):
        #hues = super(ColorizeByNum, self).get_hues(n=self.ncol)[::-1]
        #binned = pd.np.digitize(data, self.bins, right=False) - 1
        #return [hues[val] for val in binned]

    #def legend_levels(self):
        #if self.dtype == int:
            #frm_str = "{:.0f}"
        #else:
            #frm_str = options.cfg.float_format
        #return ["≥ {}".format(frm_str.format(x)) for x in self.bins][::-1]


class TestColorizeByFreq(unittest.TestCase):
    pass


provided_tests = (TestColorizer,
                  TestColorizeByFactor,
                  TestColorizeByNum,
                  TestColorizeByFreq)


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

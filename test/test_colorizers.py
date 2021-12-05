# -*- coding: utf-8 -*-
"""
This module tests the colorizer module.

Run it like so:

coquery$ python -m test.test_colorizers

"""

from __future__ import unicode_literals
from __future__ import division


import matplotlib as mpl

mpl.use("Qt5Agg")
mpl.rcParams["backend"] = "Qt5Agg"

import pandas as pd
import seaborn as sns

from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum,
    COQ_SINGLE)
from coquery.defines import PALETTE_BW
from test.testcase import CoqTestCase, run_tests


class TestColorizer(CoqTestCase):
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
        colorizer = Colorizer(f"{PALETTE_BW}_r", 5)
        pal = colorizer.get_palette()
        bw_pal = [(0, 0, 0),
                  (1, 1, 1),
                  (0, 0, 0),
                  (1, 1, 1),
                  (0, 0, 0)][::-1]
        self.assertListEqual(pal, bw_pal)

    def test_get_palette_single(self):
        colorizer = Colorizer(f"{COQ_SINGLE}_#ff0000", 5)
        pal = colorizer.get_palette()
        single_pal = [(1, 0, 0)] * 5
        self.assertListEqual(pal, single_pal)

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


class TestColorizeByFactor(CoqTestCase):
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


class TestColorizeByNum(CoqTestCase):
    def test_get_hues_1(self):
        data = [500, 500, 4500, 4500, 2500]

        colorizer = ColorizeByNum("Greys", 5,
                                  pd.Series(data), vrange=(0, 5000))
        sns_pal = sns.color_palette("Greys", 5)[::-1]

        expected = [sns_pal[0],
                    sns_pal[0],
                    sns_pal[4],
                    sns_pal[4],
                    sns_pal[2]]
        hues = colorizer.get_hues(data=data)

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_legend_levels_1(self):
        data = [500, 500, 4500, 4500, 2500]

        colorizer = ColorizeByNum("Paired", 5,
                                  pd.Series(range(5000)),
                                  vrange=(0, 5000))

        expected = ["≥ 4000",
                    "≥ 3000",
                    "≥ 2000",
                    "≥ 1000",
                    "≥ 0"]

        levels = colorizer.legend_levels()

        self.assertEqual(len(levels), len(data))
        self.assertListEqual(levels, expected)


class TestColorizeByFreq(CoqTestCase):
    pass


class TestColorizeTransform(CoqTestCase):
    def setUp(self):
        self.rgb = [(0, 0, 0),
                    (127, 0, 0), (0, 127, 0), (0, 0, 127),
                    (127, 127, 0), (127, 0, 127), (0, 127, 127),
                    (127, 127, 127),
                    (255, 0, 0), (0, 255, 0), (0, 0, 255),
                    (255, 255, 0), (255, 0, 255), (0, 255, 255),
                    (255, 255, 255)]
        self.hex = ["#000000",
                    "#7f0000", "#007f00", "#00007f",
                    "#7f7f00", "#7f007f", "#007f7f",
                    "#7f7f7f",
                    "#ff0000", "#00ff00", "#0000ff",
                    "#ffff00", "#ff00ff", "#00ffff",
                    "#ffffff"]
        self.mpt = [(0.0, 0.0, 0.0),
                    (127 / 255, 0.0, 0.0),
                    (0.0, 127 / 255, 0.0),
                    (0.0, 0.0, 127 / 255),
                    (127 / 255, 127 / 255, 0.0),
                    (127 / 255, 0.0, 127 / 255),
                    (0.0, 127 / 255, 127 / 255),
                    (127 / 255, 127 / 255, 127 / 255),
                    (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0),
                    (1.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0),
                    (1.0, 1.0, 1.0)]

    def test_hex_to_rgb(self):
        self.assertListEqual(self.rgb, Colorizer.hex_to_rgb(self.hex))

    def test_hex_to_mpt(self):
        self.assertListEqual(self.mpt, Colorizer.hex_to_mpt(self.hex))

    def test_rgb_to_hex(self):
        self.assertListEqual(self.hex, Colorizer.rgb_to_hex(self.rgb))

    def test_rgb_to_mpt(self):
        self.assertListEqual(self.mpt, Colorizer.rgb_to_mpt(self.rgb))

    def test_mpt_to_rgb(self):
        self.assertListEqual(self.rgb, Colorizer.mpt_to_rgb(self.mpt))

    def test_mpt_to_hex(self):
        self.assertListEqual(self.hex, Colorizer.mpt_to_hex(self.mpt))


provided_tests = (TestColorizer,
                  TestColorizeByFactor,
                  TestColorizeByNum,
                  TestColorizeByFreq,
                  TestColorizeTransform)


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

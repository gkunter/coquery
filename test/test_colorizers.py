# -*- coding: utf-8 -*-
"""
This module tests the colorizer module.

Run it like so:

coquery$ python -m test.test_colorizers

"""

import pandas as pd
import seaborn as sns

from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByNum)
from test.testcase import CoqTestCase, run_tests


class TestColorizer(CoqTestCase):
    def test_get_palette(self):
        colorizer = Colorizer("Paired", 5)
        pal = colorizer.get_palette()

        sns_pal = sns.color_palette("Paired", 5)
        colorizer = Colorizer(sns_pal)
        pal = colorizer.get_palette()
        self.assertListEqual(pal, sns_pal)

    def test_get_palette_2(self):
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = Colorizer(sns_pal)
        pal = colorizer.get_palette(n=7)
        self.assertListEqual(pal, sns_pal + sns_pal[0:2])

    def test_get_palette_3(self):
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = Colorizer(sns_pal)
        pal = colorizer.get_palette(n=14)
        self.assertListEqual(pal, (sns_pal * 3)[:-1])

    def test_get_hues_1(self):
        """
        Test if hues are correctly assigned for a data set smaller than the
        number of colors in the current palette.
        """
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = Colorizer(sns_pal)
        data = range(4)
        hues = colorizer.get_hues(data=data)
        self.assertListEqual(hues, sns_pal[:4])

    def test_get_hues_2(self):
        """
        Test if hues are correctly recycled if there is more data than colors
        in the current palette.
        """
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = Colorizer(sns_pal)
        data = range(10)
        hues = colorizer.get_hues(data=data)
        self.assertListEqual(hues, sns_pal * 2)

    def test_get_hues_ncol_1(self):
        """
        Test if the number of colors used from the current palette can be
        limited to one.
        """
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = Colorizer(sns_pal)
        data = range(10)
        hues = colorizer.get_hues(data=data, ncol=1)
        self.assertListEqual(hues, [sns_pal[0]] * 10)

    def test_get_hues_ncol_2(self):
        """
        Test if the number of colors used from the current palette can be
        limited to two.
        """
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = Colorizer(sns_pal)
        data = range(10)
        hues = colorizer.get_hues(data=data, ncol=2)
        self.assertListEqual(hues, sns_pal[:2] * 5)

    def test_legend_title(self):
        colorizer = Colorizer([])
        legend_title = colorizer.legend_title("coq_word")
        self.assertEqual(legend_title, "")

    def test_legend_palette(self):
        colorizer = Colorizer([])
        legend_palette = colorizer.legend_palette()
        self.assertEqual(legend_palette, [])

    def test_legend_levels(self):
        colorizer = Colorizer([])
        legend_levels = colorizer.legend_levels()
        self.assertListEqual(legend_levels, [])

    def test_set_title_frm(self):
        colorizer = Colorizer([])
        colorizer.set_title_frm("{z}")
        z = "coq_word"
        legend_title = colorizer.legend_title(z)
        self.assertEqual(legend_title, z)


class TestColorizeByFactor(CoqTestCase):
    def test_get_hues_by_data_1(self):
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor(sns_pal, values=["A", "B"])
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
        colorizer = ColorizeByFactor(sns_pal, values=list("ABCDEF"))
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
        colorizer = ColorizeByFactor(sns_pal, values=["A", "B"])
        hues = colorizer.get_hues(data=data)
        expected = [sns_pal[1],
                    sns_pal[1],
                    sns_pal[1]]

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_get_hues_by_data_3a(self):
        data = list("B")

        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor(sns_pal, values=["A", "B"])
        hues = colorizer.get_hues(data=data)
        expected = [sns_pal[1]]

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_get_hues_by_data_4(self):
        data = list("AAA")

        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor(sns_pal, values=["A", "B"])
        hues = colorizer.get_hues(data=data)
        expected = [sns_pal[0],
                    sns_pal[0],
                    sns_pal[0]]

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_get_hues_by_data_4a(self):
        data = list("A")
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor(sns_pal, values=["A", "B"])
        hues = colorizer.get_hues(data=data)
        expected = [sns_pal[0]]

        self.assertEqual(len(hues), len(data))
        self.assertListEqual(hues, expected)

    def test_legend_title(self):
        factor_column = "coq_word"
        colorizer = ColorizeByFactor([], values=["A", "B"])
        title = colorizer.legend_title(z=factor_column)
        self.assertEqual(title, factor_column)

    def test_legend_palette_1(self):
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor(sns_pal, values=["A", "B"])
        pal = sns_pal[:2]
        self.assertListEqual(colorizer.legend_palette(), pal)

    def test_legend_palette_2(self):
        sns_pal = sns.color_palette("Paired", 5)
        colorizer = ColorizeByFactor(sns_pal, values=list("ABCDEFGHI"))
        pal = sns_pal + sns_pal[:-1]
        self.assertListEqual(colorizer.legend_palette(), pal)

    def test_legend_levels(self):
        levels = list("ABCDEFGHI")
        colorizer = ColorizeByFactor([], values=levels)
        self.assertListEqual(colorizer.legend_levels(), levels)


class TestColorizeByNum(CoqTestCase):
    def test_get_hues_1(self):
        data = pd.Series([500, 500, 4500, 4500, 2500])

        pal = list("ABCDE")
        colorizer = ColorizeByNum(pal, vrange=(0, 5000))

        target = list("AAEEC")
        values = colorizer.get_hues(data=data, ncol=len(pal))
        self.assertEqual(len(values), len(data))
        self.assertListEqual(target, values)

    def test_legend_levels_1(self):
        data = pd.Series([500, 500, 4500, 4500, 2500])

        pal = list("ABCDE")
        colorizer = ColorizeByNum(pal, vrange=(0, 5000))
        colorizer.get_hues(data=data)

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


provided_tests = (
    TestColorizer,
    TestColorizeByFactor,
    TestColorizeByNum,
    TestColorizeTransform,
    )


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
This module tests the bubble plot visualizer module.

Run it like so:

coquery$ python -m test.vis.test_bubbleplot

"""

import unittest
import pandas as pd
import numpy as np
import math

from test.testcase import CoqTestCase


def r(x):
    return np.sqrt(x / np.pi)


class TestBubblePlotMethods(CoqTestCase):
    NUM_COLUMN = "NUM"

    def setUp(self):
        from coquery.visualizer.bubbleplot import BubblePlot
        self.vis = BubblePlot(None, None, self.NUM_COLUMN)

    def test_intersect1(self):
        pos1 = (0, 0)
        r1 = 1
        tup1 = (pos1, r1)

        test_range = [
            ((0, 2), 1),    # no intersection
            ((0, 1), 1),    # intersection
            ((2, 0), 1),    # no intersection
            ((1, 0), 1),    # intersection
            ((0, -2), 1),   # no intersection
            ((0, -1), 1),   # intersection
            ((-2, 0), 1),   # no intersection
            ((-1, 0), 1),   # intersection
            ((math.sqrt(2), math.sqrt(2)), 1),      # no intersection
            ]

        test_results = [self.vis.intersecting(tup1, tup2)
                        for tup2 in test_range]
        self.assertListEqual(
            test_results,
            [False, True, False, True, False, True, False, True, False])

    def test_intersect2(self):
        """
        Test for intersections with shifted centers
        """
        pos1 = (0, 0)
        r1 = 1

        test_range = [
            ((0, 2), 1),    # no intersection
            ((0, 1), 1),    # intersection
            ((2, 0), 1),    # no intersection
            ((1, 0), 1),    # intersection
            ((0, -2), 1),   # no intersection
            ((0, -1), 1),   # intersection
            ((-2, 0), 1),   # no intersection
            ((-1, 0), 1),   # intersection
            ((np.sqrt(2), np.sqrt(2)), 1),    # no intersection
            ]

        test_results = [self.vis.intersecting((np.array(pos1) + 1, r1),
                                              (np.array(pos2) + 1, r2))
                        for pos2, r2 in test_range]
        self.assertListEqual(
            test_results,
            [False, True, False, True, False, True, False, True, False])

    def test_rotate_vector(self):
        """
        Test vector rotation method
        """
        test_range = [
            (1, 0.00 * np.pi, (1, 0)),
            (1, 0.25 * np.pi, (np.sqrt(2) / 2, np.sqrt(2) / 2)),
            (1, 0.50 * np.pi, (0, 1)),
            (1, 0.75 * np.pi, (-np.sqrt(2) / 2, np.sqrt(2) / 2)),
            (1, 1.00 * np.pi, (-1, 0)),
            (1, 1.25 * np.pi, (-np.sqrt(2) / 2, -np.sqrt(2) / 2)),
            (1, 1.50 * np.pi, (0, -1)),
            (1, 1.75 * np.pi, (np.sqrt(2) / 2, -np.sqrt(2) / 2)),

            (2, 0.00 * np.pi, (2, 0)),
            (2, 0.25 * np.pi, (np.sqrt(2), np.sqrt(2))),
            (2, 0.50 * np.pi, (0, 2)),
            (2, 0.75 * np.pi, (-np.sqrt(2), np.sqrt(2))),
            (2, 1.00 * np.pi, (-2, 0)),
            (2, 1.25 * np.pi, (-np.sqrt(2), -np.sqrt(2))),
            (2, 1.50 * np.pi, (0, -2)),
            (2, 1.75 * np.pi, (np.sqrt(2), -np.sqrt(2))),
            ]

        test_results = [self.vis.rotate_vector(x, theta)
                        for x, theta, _ in test_range]
        expected = [result for _, _, result in test_range]
        np.testing.assert_almost_equal(test_results, expected)

    def test_get_angle1(self):
        test_range = [
            ((np.sqrt(2), 1, 1), 0.5 * np.pi),
            ((1, 1, 1), np.pi / 3),
            ((5**2, 3**2, 4**2), np.pi),
            ]

        test_results = [self.vis.get_angle(*tup) for tup, _ in test_range]
        expected = [result for _, result in test_range]
        np.testing.assert_almost_equal(test_results, expected)


class TestBubblePlotAlgorithm(TestBubblePlotMethods):
    def setUp(self):
        super().setUp()
        from coquery.visualizer.bubbleplot import BubblePlot

        np.random.seed(123)
        self.df = pd.DataFrame(
            {"X": list("AAAAAAAAAAAAAAAAAAABBBBBBBBBBB"),
             "Y": list("xxxxxxxxyyyyyyyyyyyxxxxxxxyyyy"),
             "Z": list("111122221111222211221122112222"),
             "NUM": np.random.randint(0, 100, 30)})

        self.df2 = pd.DataFrame(
            {"X": ["A"] * 5 + ["B"] * 3 + ["C"] * 1,
             "NUM": np.arange(9)})
        self.vis = BubblePlot(None, None, "NUM")
        self.vis.box_padding = False

    def test_get_dataframe1(self):
        target = pd.DataFrame(
            {"X": ["A", "B"],
             "COQ_NUMERIC": (self.df["X"]
                                 .value_counts()
                                 .reset_index(drop=True))})
        value = self.vis.get_dataframe(self.df, "X", None, None)
        pd.testing.assert_index_equal(target.columns.sort_values(),
                                      value.columns.sort_values())
        pd.testing.assert_frame_equal(target[value.columns], value)

    def test_get_dataframe2(self):
        target = (self.df.groupby(["X", "Y"])
                         .size()
                         .reset_index()
                         .rename(columns={0: "COQ_NUMERIC"})
                         .sort_index())

        value = (self.vis.get_dataframe(self.df, "X", "Y", None)
                         .sort_index())
        pd.testing.assert_index_equal(target.columns.sort_values(),
                                      value.columns.sort_values())
        pd.testing.assert_frame_equal(target[value.columns], value)

    def test_get_dataframe3(self):
        target = (self.df.groupby(["X"])
                         .agg({"NUM": "mean"})
                         .reset_index()
                         .rename(columns={"NUM": "COQ_NUMERIC"}))

        value = (self.vis.get_dataframe(self.df, "X", "NUM", None)
                         .sort_index())
        pd.testing.assert_index_equal(target.columns.sort_values(),
                                      value.columns.sort_values())
        pd.testing.assert_frame_equal(target[value.columns], value)

    def test_get_position(self):
        """
        Test a bubble configuration like this:
         --- ---
        | A | B |
         ---C---
            -
        where A, B, and C are bubbles with raddii representing frequencies of
        5, 3, and 1, respectively.
        """
        aggr = pd.DataFrame({"X": self.df2["X"].unique(),
                             "COQ_NUMERIC": (self.df2["X"]
                                                 .value_counts()
                                                 .reset_index(drop=True))})

        r_n, r_a, r_x = (aggr.sort_values(by=["COQ_NUMERIC"])["COQ_NUMERIC"]
                             .values)

        pos_a = (0, 0)
        pos_n = (r_a + r_n, 0)

        pos = self.vis.get_position(r_x, (pos_a, r_a, ""), (pos_n, r_n, ""))

        (x_a, y_a) = pos_a
        (x_n, y_n) = pos_n

        l_a = r_n + r_x
        l_b = r_a + r_x
        l_c = r_a + r_n

        # theta is the angle C given the three lengths. Here, it expresses
        # the angle that is needed to rotate a vector of length l_c so that
        # it connects (0, 0) and (x_n, y_n).
        theta = -self.vis.get_angle(l_a, l_b, l_c)

        target = (x_a + l_b * np.cos(theta),
                  y_a + l_b * np.sin(theta))
        np.testing.assert_almost_equal(pos, target)

    def test_get_label1(self):
        aggr = pd.DataFrame({"X": ["A", "B"],
                             "COQ_NUMERIC": (self.df["X"]
                                                 .value_counts()
                                                 .reset_index(drop=True))})
        for i in range(len(aggr)):
            row = aggr.iloc[i]
            label = self.vis.get_label(row, ["X"], "COQ_NUMERIC")
            self.assertEqual(label, f'{row["X"]} ({row["COQ_NUMERIC"]})')

    def test_get_label2(self):
        aggr = (self.df.groupby(["X", "Y"])
                       .size()
                       .reset_index()
                       .rename(columns={0: "COQ_NUMERIC"})
                       .sort_index())

        for i in range(len(aggr)):
            row = aggr.iloc[i]
            label = self.vis.get_label(row, ["X", "Y"], "COQ_NUMERIC")
            self.assertEqual(
                label, f'{row["X"]} | {row["Y"]} ({row["COQ_NUMERIC"]})')

    def test_get_label3(self):
        aggr = (self.df.groupby(["X"])
                       .agg({"NUM": "mean"})
                       .reset_index())

        for i in range(len(aggr)):
            row = aggr.iloc[i]
            label = self.vis.get_label(row, ["X"], "NUM")
            self.assertEqual(label, f"{row['X']}: M={row['NUM']}")

    def test_prepare_argument(self):
        value = self.vis.prepare_arguments(self.df2, "X", None, None,
                                           self.df2["X"].unique(), None)

        aggr = pd.DataFrame({"X": self.df2["X"].unique(),
                             "COQ_NUMERIC": (self.df2["X"]
                                                 .value_counts()
                                                 .reset_index(drop=True))})

        row0 = aggr[aggr["X"] == "A"].iloc[0]
        row1 = aggr[aggr["X"] == "B"].iloc[0]
        row2 = aggr[aggr["X"] == "C"].iloc[0]
        f0 = row0["COQ_NUMERIC"]
        f1 = row1["COQ_NUMERIC"]
        f2 = row2["COQ_NUMERIC"]
        l0 = self.vis.get_label(row0, ["X"], "COQ_NUMERIC")
        l1 = self.vis.get_label(row1, ["X"], "COQ_NUMERIC")
        l2 = self.vis.get_label(row2, ["X"], "COQ_NUMERIC")

        r0, r1, r2 = r(f0), r(f1), r(f2)
        p0 = (0, 0)
        p1 = (r0 + r1, 0)
        p2 = self.vis.get_position(r2, (p0, r0, ""), (p1, r1, ""))
        target = {"data": [(p0, r0, l0),
                           (p1, r1, l1),
                           (p2, r2, l2)],
                  "cix": aggr.index}

        self.assertDictEqual(target, value, )

    def test_place_circles1(self):
        self.vis.x = "X"
        self.vis.y = None

        df = pd.DataFrame(data=[("A", 1),
                                ("B", 10),
                                ("C", 1000),
                                ("D", 500),
                                ("E", 5),
                                ("F", 5),
                                ("G", 2),
                                ("H", 2),
                                ("I", 5000),
                                ("J", 50),
                                ("K", 50),
                                ],
                          columns=[self.vis.x, self.vis.NUM_COLUMN])

        circles = self.vis.place_circles(df)

        for (x, y), rad, label in circles:
            self.assertFalse(pd.isnull(x))
            self.assertFalse(pd.isnull(y))

    def test_place_circles2(self):
        """
        Assert that the algorithm produces valid circle positions even in the
        face of very distorted data.
        """
        self.vis.x = "X"
        self.vis.y = None

        n = 500
        num = np.concatenate(
            (np.random.randint(5000, 100000, n // 5),
             np.random.randint(500, 1000, n // 5),
             np.random.randint(1, 100, 3 * n // 5)))

        df = pd.DataFrame({"X": np.arange(n), self.vis.NUM_COLUMN: num})
        df = df.sample(frac=1).reset_index(drop=True)

        circles = self.vis.place_circles(df)
        for (x, y), rad, label in circles:
            self.assertFalse(pd.isnull(x))
            self.assertFalse(pd.isnull(y))
        # self._plot_circles(circles)

    def _plot_circles(self, circles):
        from matplotlib import pyplot as plt

        ax = plt.gca()
        for i, ((x, y), rad, label) in enumerate(circles):
            circ = plt.Circle((x, y), rad)
            ax.add_patch(circ)
            ax.text(x, y, i, va="center", ha="center")
        ax.set_aspect(1)
        ax.autoscale(enable=True, axis="both")
        plt.show()


provided_tests = (
    TestBubblePlotMethods,
    TestBubblePlotAlgorithm,
    )


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
This module tests the barplot visualizer module.

Run it like so:

coquery$ python -m test.test_vis_barplot

"""

import unittest
import pandas as pd
import seaborn as sns
import scipy.stats as st
import itertools

from coquery.visualizer.barplot import BarPlot, StackedBars


NUM_COLUMN = BarPlot.NUM_COLUMN
COL_COLUMN = BarPlot.COL_COLUMN
SEM_COLUMN = BarPlot.SEM_COLUMN


# helper functions that simulate code used in the visualization aggregator:
def count(df, grouping):
    return (df.groupby(grouping)
              .size()
              .reset_index()
              .rename(columns={0: NUM_COLUMN}))


def most_frequent(df, grouping, target):
    columns = grouping + [target]
    return (count(df, columns).sort_values(NUM_COLUMN, ascending=False)
                              .drop_duplicates(grouping)
                              .reset_index(drop=True)
                              .drop(NUM_COLUMN, axis=1)
                              .rename(columns={target: COL_COLUMN}))


def means(df, grouping, target, name=None):
    name = name or COL_COLUMN
    return (df.groupby(grouping)
              .agg({target: "mean"})
              .reset_index()
              .rename(columns={target: name}))


def ci(df, grouping, target, name=None):
    def _get_interval(x):
        return x.sem() * st.t.ppf(1 - 0.025, len(x))

    name = name or SEM_COLUMN
    return (df.groupby(grouping)
              .agg({target: _get_interval})
              .reset_index()
              .rename(columns={target: name}))


# helper function that maps a categorical value onto RGB values
def map_to_pal(palette, levels, data):
    palette = sns.color_palette("Paired", n_colors=len(levels))
    return [palette[levels.index(val)] for val in data]


class CoqTestCase1(unittest.TestCase):
    def setUp(self):
        pd.np.random.seed(123)
        self.df = pd.DataFrame({"X": list("AAAAAAAAAAAAAAAAAAABBBBBBBBBBB"),
                                "Y": list("xxxxxxxxyyyyyyyyyyyxxxxxxxyyyy"),
                                "Z": list("111122221111222211221122112222"),
                                "NUM": pd.np.random.randint(0, 100, 30)
                                })

    def assertDictEqual(self, d1, d2):
        """
        This overrides assertDictEqual so that any DataFrame value of the
        dictionaries is transformed to a dictionary before comparing.
        """

        D1 = d1.copy()
        D2 = d2.copy()

        d_df1 = {}
        d_df2 = {}

        for key, val in d1.items():
            if isinstance(val, pd.DataFrame):
                d_df1[key] = D1.pop(key)
        for key, val in d2.items():
            if isinstance(val, pd.DataFrame):
                d_df2[key] = D2.pop(key)

        super(CoqTestCase1, self).assertDictEqual(D1, D2)

        for key in d_df1.keys():
            pd.testing.assert_frame_equal(d_df1[key], d_df2[key])


class CoqTestCase2(CoqTestCase1):
    def setUp(self):
        pd.np.random.seed(123)
        self.df = pd.DataFrame({"X": list("AAAAAAAAAAAAAAAAAAABBBB"),
                                "Y": list("xxxxxxxxyyyyyyyyyyyyyyy"),
                                "Z": list("11112222111122221122222"),
                                "NUM": pd.np.random.randint(0, 100, 23)
                                })


class TestBarPlotSimple(CoqTestCase1):
    """
    Test barplots when only a single categorical variable is provided.
    """
    def test_prepare_argument_X_only(self):
        """
        Basic test: only a single categorical variable on the `X` axis
        """
        vis = BarPlot(None, None)

        category = "X"
        numeric = NUM_COLUMN
        levels = sorted(self.df[category].unique())
        data = count(self.df, [category])
        data[COL_COLUMN] = data[category]

        target = {"x": category, "order": levels,
                  "y": numeric,
                  "hue": None, "hue_order": None,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=None, z=None,
                                     levels_x=levels, levels_y=None)

        self.assertDictEqual(args, target)

    def test_prepare_argument_Y_only(self):
        """
        Basic test: only a single categorical variable on the `Y` axis
        """
        vis = BarPlot(None, None)

        category = "Y"
        numeric = NUM_COLUMN
        levels = sorted(self.df[category].unique())
        data = count(self.df, [category])
        data[COL_COLUMN] = data[category]

        target = {"x": numeric,
                  "y": category, "order": levels,
                  "hue": None, "hue_order": None,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=None, y=category, z=None,
                                     levels_x=None, levels_y=levels)
        self.assertDictEqual(args, target)

    def test_prepare_argument_X_no_horiz(self):
        """
        Barplots with only `X` specified as a categorical variable should
        ignore the `vertical` attribute.
        """
        category = "X"
        levels = sorted(self.df[category].unique())

        vis1 = BarPlot(None, None)
        vis1.vertical = False
        args1 = vis1.prepare_arguments(data=self.df,
                                       x=category, y=None, z=None,
                                       levels_x=levels, levels_y=None)

        vis2 = BarPlot(None, None)
        vis2.vertical = True
        args2 = vis2.prepare_arguments(data=self.df,
                                       x=category, y=None, z=None,
                                       levels_x=levels, levels_y=None)

        self.assertDictEqual(args1, args2)

    def test_prepare_argument_Y_no_horiz(self):
        """
        Barplots with only `Y` specified as a categorical variable should
        ignore the `vertical` attribute.
        """

        category = "Y"
        levels = sorted(self.df[category].unique())

        vis1 = BarPlot(None, None)
        vis1.vertical = False
        args1 = vis1.prepare_arguments(data=self.df,
                                       x=None, y=category, z=None,
                                       levels_x=None, levels_y=levels)

        vis2 = BarPlot(None, None)
        vis2.vertical = True
        args2 = vis2.prepare_arguments(data=self.df,
                                       x=None, y=category, z=None,
                                       levels_x=None, levels_y=levels)

        self.assertDictEqual(args1, args2)


class TestBarPlotComplex(CoqTestCase1):
    """
    Test barplots that use two categorical variables.
    """
    def test_prepare_argument_XY_vert(self):
        """
        Default case: `X` and `Y` categorical variables and vertical bars
        """
        vis = BarPlot(None, None)

        category = "X"
        hue = "Y"
        order = sorted(self.df[category].unique())
        hue_order = sorted(self.df[hue].unique())
        numeric = NUM_COLUMN
        data = count(self.df, [category, hue])
        data[COL_COLUMN] = data[hue]

        target = {"x": category, "order": order,
                  "y": numeric,
                  "hue": hue, "hue_order": hue_order,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=hue, z=None,
                                     levels_x=order, levels_y=hue_order)

        self.assertDictEqual(args, target)

    def test_prepare_argument_XY_horiz(self):
        """
        Special case: `X` and `Y` categorical variables and horizontal bars
        """
        vis = BarPlot(None, None)
        vis.vertical = False

        category = "X"
        hue = "Y"
        order = sorted(self.df[category].unique())
        hue_order = sorted(self.df[hue].unique())
        numeric = NUM_COLUMN
        data = count(self.df, [category, hue])
        data[COL_COLUMN] = data[hue]

        target = {"x": numeric,
                  "y": category, "order": order,
                  "hue": hue, "hue_order": hue_order,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=hue, z=None,
                                     levels_x=order, levels_y=hue_order)

        self.assertDictEqual(args, target)


class TestBarPlotNum(CoqTestCase1):
    """
    Test barplots that use one categorical and one numerical variables.
    """
    def test_prepare_argument_X_num(self):
        vis = BarPlot(None, None)

        category = "X"
        numeric = "NUM"
        order = sorted(self.df[category].unique())

        data = pd.merge(
            means(self.df, [category], target=numeric, name=NUM_COLUMN),
            ci(self.df, [category], target=numeric, name=SEM_COLUMN),
            on=[category])
        data[COL_COLUMN] = data[category]

        target = {"x": category, "y": NUM_COLUMN,
                  "order": order,
                  "hue": None, "hue_order": None,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=numeric, z=None,
                                     levels_x=order, levels_y=None)

        self.assertDictEqual(args, target)

    def test_prepare_argument_Y_num(self):
        vis = BarPlot(None, None)

        category = "Y"
        numeric = "NUM"
        order = sorted(self.df[category].unique())

        data = pd.merge(
            means(self.df, [category], target=numeric, name=NUM_COLUMN),
            ci(self.df, [category], target=numeric, name=SEM_COLUMN),
            on=[category])
        data[COL_COLUMN] = data[category]

        target = {"x": category, "y": NUM_COLUMN,
                  "order": order,
                  "hue": None, "hue_order": None,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=numeric, z=None,
                                     levels_x=order, levels_y=None)

        self.assertDictEqual(args, target)


class TestBarPlotColorCat(CoqTestCase1):
    """
    Test simple and complex bar plots with a categorical variable providing
    the color semantics.
    """
    def test_prepare_argument_X(self):
        vis = BarPlot(None, None)

        category = "X"
        semantics = "Z"
        numeric = NUM_COLUMN
        levels_x = sorted(self.df[category].unique())
        data = pd.merge(
            count(self.df, [category]),
            most_frequent(self.df, [category], semantics))

        target = {"x": category, "order": levels_x,
                  "y": numeric,
                  "hue": None, "hue_order": None,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=None, z=semantics,
                                     levels_x=levels_x, levels_y=None)

        self.assertDictEqual(args, target)

    def test_prepare_argument_XY(self):
        vis = BarPlot(None, None)

        category = "X"
        hue = "Y"
        semantics = "Z"
        order = sorted(self.df[category].unique())
        hue_order = sorted(self.df[hue].unique())
        numeric = NUM_COLUMN
        data = pd.merge(
            count(self.df, [category, hue]),
            most_frequent(self.df, [category, hue], semantics))

        target = {"x": category, "order": order,
                  "y": numeric,
                  "hue": hue, "hue_order": hue_order,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=hue, z=semantics,
                                     levels_x=order, levels_y=hue_order)

        self.assertDictEqual(args, target)


class TestBarPlotColorNum(CoqTestCase1):
    """
    Test simple and complex bar plots with a numerical variable providing the
    color semantics.
    """
    def test_prepare_argument_X(self):
        vis = BarPlot(None, None)

        category = "X"
        semantics = "NUM"
        numeric = NUM_COLUMN
        levels = sorted(self.df[category].unique())
        data = pd.merge(
            count(self.df, [category]),
            means(self.df, [category], semantics))

        target = {"x": category, "order": levels,
                  "y": numeric,
                  "hue": None, "hue_order": None,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=None, z=semantics,
                                     levels_x=levels, levels_y=None)

        self.assertDictEqual(args, target)

    def test_prepare_argument_XY(self):
        vis = BarPlot(None, None)

        category = "X"
        hue = "Y"
        semantics = "NUM"
        order = sorted(self.df[category].unique())
        hue_order = sorted(self.df[hue].unique())
        numeric = NUM_COLUMN
        data = pd.merge(
            count(self.df, [category, hue]),
            means(self.df, [category, hue], semantics))

        target = {"x": category, "order": order,
                  "y": numeric,
                  "hue": hue, "hue_order": hue_order,
                  "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=hue, z=semantics,
                                     levels_x=order, levels_y=hue_order)

        self.assertDictEqual(args, target)


class TestBarPlotSimpleDefective(TestBarPlotSimple, CoqTestCase2):
    """
    Run the TestBarPlotSimple tests with a data frame that lacks some
    combinations
    """


class TestBarPlotComplexDefective(TestBarPlotComplex, CoqTestCase2):
    """
    Run the TestBarPlotComplex tests with a data frame that lacks some
    combinations
    """


class TestBarPlotNumDefective(TestBarPlotNum, CoqTestCase2):
    """
    Run the TestBarPlotNum tests with a data frame that lacks some
    combinations
    """


class TestBarPlotColorCatDefective(TestBarPlotColorCat, CoqTestCase2):
    """
    Run the TestBarPlotColorCat tests with a data frame that lacks some
    combinations
    """


class TestBarPlotColorNumDefective(TestBarPlotColorNum, CoqTestCase2):
    """
    Run the TestBarPlotColorNum tests with a data frame that lacks some
    combinations
    """


# STACKED BAR PLOT TESTS
class TestStackedPlotSimple(CoqTestCase1):
    def test_prepare_argument_X_only(self):
        """
        Basic test: only a single categorical variable on the `X` axis
        """
        vis = StackedBars(None, None)

        category = "X"
        numeric = NUM_COLUMN
        levels = sorted(self.df[category].unique())
        data = (self.df.groupby(category)
                       .size()
                       .cumsum()
                       .reset_index()
                       .rename(columns={0: "COQ_NUM"}))
        data[COL_COLUMN] = data[category]

        target = {"x": category, "y": numeric,
                  "levels": levels, "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=None, z=None,
                                     levels_x=levels, levels_y=None)

        self.assertDictEqual(args, target)

    def test_prepare_argument_Y_only(self):
        """
        Basic test: only a single categorical variable on the `Y` axis
        """
        vis = StackedBars(None, None)

        category = "Y"
        numeric = NUM_COLUMN
        levels = sorted(self.df[category].unique())
        data = (self.df.groupby(category)
                       .size()
                       .cumsum()
                       .reset_index()
                       .rename(columns={0: "COQ_NUM"}))
        data[COL_COLUMN] = data[category]

        target = {"x": numeric, "y": category,
                  "levels": levels, "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=None, y=category, z=None,
                                     levels_x=None, levels_y=levels)

        self.assertDictEqual(args, target)

    def test_prepare_argument_X_incomplete(self):
        """
        A single categorical variable on a data frame where not all factor
        levels are attested
        """
        vis = StackedBars(None, None)

        category = "X"
        numeric = NUM_COLUMN
        levels = sorted(self.df[category].unique()) + ["C"]
        data = (self.df.groupby(category)
                       .size()
                       .cumsum()
                       .reset_index()
                       .rename(columns={0: "COQ_NUM"}))
        data.loc[len(data)] = {category: "C", numeric: pd.np.nan}

        data[COL_COLUMN] = data[category]

        target = {"x": category, "y": numeric,
                  "levels": levels, "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=None, z=None,
                                     levels_x=levels, levels_y=None)
        self.assertDictEqual(args, target)


class TestStackedPlotComplex(CoqTestCase1):

    def test_prepare_argument_XY(self):
        """
        Basic test: only a single categorical variable on the `Y` axis
        """
        vis = StackedBars(None, None)

        category = "X"
        hue = "Y"
        order = sorted(self.df[category].unique())
        hue_order = sorted(self.df[hue].unique())
        numeric = NUM_COLUMN
        data = (self.df.groupby([category, hue])
                       .size()
                       .groupby([category])
                       .cumsum()
                       .reset_index()
                       .rename(columns={0: "COQ_NUM"}))
        data[COL_COLUMN] = data[hue]

        # ensure that all variable combinations are attested in the target
        # frame:
        expand = pd.DataFrame(data=list(itertools.product(order, hue_order)),
                              columns=[category, COL_COLUMN])
        data = data.merge(expand, how="right")

        target = {"x": category, "y": numeric,
                  "levels": hue_order, "data": data}

        args = vis.prepare_arguments(data=self.df,
                                     x=category, y=hue, z=None,
                                     levels_x=order, levels_y=hue_order)

        self.assertDictEqual(args, target)


class TestStackedPlotSimpleDefective(TestStackedPlotSimple, CoqTestCase2):
    """
    Run the TestStackedPlotSimple test with a data frame that lacks some
    combinations
    """


class TestStackedPlotComplexDefective(TestStackedPlotComplex, CoqTestCase2):
    """
    Run the TestStackedPlotComplex test with a data frame that lacks some
    combinations
    """


provided_tests = (
    TestBarPlotSimple,
    TestBarPlotComplex,
    TestBarPlotNum,
    TestBarPlotColorCat,
    TestBarPlotColorNum,

    TestBarPlotSimpleDefective,
    TestBarPlotComplexDefective,
    TestBarPlotNumDefective,
    TestBarPlotColorCatDefective,
    TestBarPlotColorNumDefective,

    TestStackedPlotSimple,
    TestStackedPlotComplex,

    TestStackedPlotSimpleDefective,
    TestStackedPlotComplexDefective,

    )


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
This module tests the filters module.

Run it like so:

coquery$ python -m test.test_filters

"""

from __future__ import unicode_literals

import unittest
import os.path
import sys
import pandas as pd
import re

from coquery.filters import *
from coquery.defines import *

STRING_COLUMN = "coq_word_label_1"
INT_COLUMN = "coq_corpus_id_1"
FLOAT_COLUMN = "coq_fraction_1"
BOOL_COLUMN = "coq_truth_1"

class TestFilterString(unittest.TestCase):
    df = pd.DataFrame({
            STRING_COLUMN: ['abc', "Peter's", 'xxx', None],
            INT_COLUMN: [1, 2, 3, 7],
            FLOAT_COLUMN: [-1.2345, 0, 1.2345, pd.np.nan],
            BOOL_COLUMN: [True, True, False, False]})

    def test_string_values(self):
        filt1 = Filter(STRING_COLUMN, str, OP_EQ, "abc")
        filt2 = Filter(STRING_COLUMN, str, OP_EQ, "Peter's")
        self.assertEqual(filt1.get_filter_string(),
                         "coq_word_label_1 == 'abc'")
        self.assertEqual(filt2.get_filter_string(),
                         "coq_word_label_1 == 'Peter\\'s'")

    def test_int_values(self):
        filt1 = Filter(INT_COLUMN, int, OP_EQ, 0)
        filt2 = Filter(INT_COLUMN, int, OP_EQ, 5)
        filt3 = Filter(INT_COLUMN, int, OP_EQ, -5)
        self.assertEqual(filt1.get_filter_string(),
                         "coq_corpus_id_1 == 0")
        self.assertEqual(filt2.get_filter_string(),
                         "coq_corpus_id_1 == 5")
        self.assertEqual(filt3.get_filter_string(),
                         "coq_corpus_id_1 == -5")

    def test_float_values(self):
        filt1 = Filter(FLOAT_COLUMN, float, OP_EQ, float(1.2345))
        filt2 = Filter(FLOAT_COLUMN, float, OP_EQ, 0.0)
        filt3 = Filter(FLOAT_COLUMN, float, OP_EQ, float(-1.2345))
        self.assertEqual(filt1.get_filter_string(),
                         "coq_fraction_1 == 1.2345")
        self.assertEqual(filt2.get_filter_string(),
                         "coq_fraction_1 == 0.0")
        self.assertEqual(filt3.get_filter_string(),
                         "coq_fraction_1 == -1.2345")

    def test_bool_values(self):
        filt1 = Filter(BOOL_COLUMN, bool, OP_EQ, True)
        filt2 = Filter(BOOL_COLUMN, bool, OP_NE, True)
        filt3 = Filter(BOOL_COLUMN, bool, OP_EQ, False)

        filt1a = Filter(BOOL_COLUMN, bool, OP_EQ, "yes")
        filt1b = Filter(BOOL_COLUMN, bool, OP_EQ, "1")
        filt1c = Filter(BOOL_COLUMN, bool, OP_EQ, 1)
        filt1d = Filter(BOOL_COLUMN, bool, OP_EQ, "y")
        filt1e = Filter(BOOL_COLUMN, bool, OP_EQ, "True")
        filt1f = Filter(BOOL_COLUMN, bool, OP_EQ, "true")

        filt3a = Filter(BOOL_COLUMN, bool, OP_EQ, "no")
        filt3b = Filter(BOOL_COLUMN, bool, OP_EQ, "0")
        filt3c = Filter(BOOL_COLUMN, bool, OP_EQ, 0)
        filt3d = Filter(BOOL_COLUMN, bool, OP_EQ, "n")
        filt3e = Filter(BOOL_COLUMN, bool, OP_EQ, "False")
        filt3f = Filter(BOOL_COLUMN, bool, OP_EQ, "false")

        self.assertEqual(filt1.get_filter_string(),
                         "coq_truth_1 == True")
        self.assertEqual(filt2.get_filter_string(),
                         "coq_truth_1 != True")
        self.assertEqual(filt3.get_filter_string(),
                         "coq_truth_1 == False")

        self.assertEqual(filt1.get_filter_string(),
                         filt1a.get_filter_string())
        self.assertEqual(filt1.get_filter_string(),
                         filt1b.get_filter_string())
        self.assertEqual(filt1.get_filter_string(),
                         filt1c.get_filter_string())
        self.assertEqual(filt1.get_filter_string(),
                         filt1d.get_filter_string())
        self.assertEqual(filt1.get_filter_string(),
                         filt1e.get_filter_string())
        self.assertEqual(filt1.get_filter_string(),
                         filt1f.get_filter_string())

        self.assertEqual(filt3.get_filter_string(),
                         filt3a.get_filter_string())
        self.assertEqual(filt3.get_filter_string(),
                         filt3b.get_filter_string())
        self.assertEqual(filt3.get_filter_string(),
                         filt3c.get_filter_string())
        self.assertEqual(filt3.get_filter_string(),
                         filt3d.get_filter_string())
        self.assertEqual(filt3.get_filter_string(),
                         filt3e.get_filter_string())
        self.assertEqual(filt3.get_filter_string(),
                         filt3f.get_filter_string())

    def test_operator_values(self):
        filt1 = Filter(STRING_COLUMN, str, OP_EQ, "abc")
        filt2 = Filter(STRING_COLUMN, str, OP_NE, "abc")
        filt3 = Filter(STRING_COLUMN, str, OP_LT, "abc")
        filt4 = Filter(STRING_COLUMN, str, OP_LE, "abc")
        filt5 = Filter(STRING_COLUMN, str, OP_GT, "abc")
        filt6 = Filter(STRING_COLUMN, str, OP_GE, "abc")
        self.assertEqual(filt1.get_filter_string(),
                         "coq_word_label_1 == 'abc'")
        self.assertEqual(filt2.get_filter_string(),
                         "coq_word_label_1 != 'abc'")
        self.assertEqual(filt3.get_filter_string(),
                         "coq_word_label_1 < 'abc'")
        self.assertEqual(filt4.get_filter_string(),
                         "coq_word_label_1 <= 'abc'")
        self.assertEqual(filt5.get_filter_string(),
                         "coq_word_label_1 > 'abc'")
        self.assertEqual(filt6.get_filter_string(),
                         "coq_word_label_1 >= 'abc'")

    def test_list_values(self):
        filt1 = Filter(STRING_COLUMN, str, OP_IN, ["abc", "Peter's"])
        filt2 = Filter(INT_COLUMN, int, OP_IN, [1, 2, 3])
        filt3 = Filter(FLOAT_COLUMN, float, OP_IN, [1.2345, 0.0, -1.2345])
        self.assertEqual(filt1.get_filter_string(),
                         "coq_word_label_1 in ['abc', 'Peter\\'s']")
        self.assertEqual(filt2.get_filter_string(),
                         "coq_corpus_id_1 in [1, 2, 3]")
        self.assertEqual(filt3.get_filter_string(),
                         "coq_fraction_1 in [1.2345, 0.0, -1.2345]")

    def test_range_values(self):
        filt1 = Filter(STRING_COLUMN, str, OP_RANGE, ["abc", "Peter's"])
        filt2 = Filter(STRING_COLUMN, str, OP_RANGE, ["abc", "Peter's", "XYZ"])
        filt3 = Filter(STRING_COLUMN, str, OP_RANGE, ["abc", "xxx"])
        filt4 = Filter(INT_COLUMN, int, OP_RANGE, [1, 2, 3])
        filt5 = Filter(FLOAT_COLUMN, float, OP_RANGE, [1.2345, 0.0, -1.2345])
        self.assertEqual(filt1.get_filter_string(),
                         "'Peter\\'s' <= coq_word_label_1 < 'abc'")
        self.assertEqual(filt2.get_filter_string(),
                         "'Peter\\'s' <= coq_word_label_1 < 'abc'")
        self.assertEqual(filt3.get_filter_string(),
                         "'abc' <= coq_word_label_1 < 'xxx'")
        self.assertEqual(filt4.get_filter_string(),
                         "1 <= coq_corpus_id_1 < 3")
        self.assertEqual(filt5.get_filter_string(),
                         "-1.2345 <= coq_fraction_1 < 1.2345")

    def test_nan_values(self):
        filt1 = Filter(STRING_COLUMN, str, OP_EQ, "")
        filt2 = Filter(STRING_COLUMN, str, OP_EQ, None)
        filt3 = Filter(STRING_COLUMN, str, OP_NE, None)
        filt4 = Filter(STRING_COLUMN, str, OP_GT, None)
        filt5 = Filter(INT_COLUMN, int, OP_EQ, pd.np.nan)
        filt6 = Filter(INT_COLUMN, int, OP_NE, pd.np.nan)

        filt7 = Filter(FLOAT_COLUMN, float, OP_EQ, "")
        filt8 = Filter(FLOAT_COLUMN, float, OP_EQ, None)
        filt9 = Filter(FLOAT_COLUMN, float, OP_NE, None)
        filt10 = Filter(FLOAT_COLUMN, float, OP_EQ, pd.np.nan)
        filt11 = Filter(FLOAT_COLUMN, float, OP_NE, pd.np.nan)

        self.assertEqual(filt1.get_filter_string(),
                         "coq_word_label_1 == ''")
        self.assertEqual(filt2.get_filter_string(),
                         "coq_word_label_1 != coq_word_label_1")
        self.assertEqual(filt3.get_filter_string(),
                         "coq_word_label_1 == coq_word_label_1")
        with self.assertRaises(ValueError):
            filt4.get_filter_string()
        self.assertEqual(filt5.get_filter_string(),
                         "coq_corpus_id_1 != coq_corpus_id_1")
        self.assertEqual(filt6.get_filter_string(),
                         "coq_corpus_id_1 == coq_corpus_id_1")

        self.assertEqual(filt7.get_filter_string(),
                         "coq_fraction_1 != coq_fraction_1")
        self.assertEqual(filt8.get_filter_string(),
                         "coq_fraction_1 != coq_fraction_1")
        self.assertEqual(filt9.get_filter_string(),
                         "coq_fraction_1 == coq_fraction_1")
        self.assertEqual(filt10.get_filter_string(),
                         "coq_fraction_1 != coq_fraction_1")
        self.assertEqual(filt11.get_filter_string(),
                         "coq_fraction_1 == coq_fraction_1")

    def test_illegal_bool_filter(self):
        filt1 = Filter(BOOL_COLUMN, bool, OP_EQ, "xxx")
        with self.assertRaises(ValueError):
            filt1.get_filter_string()

    def test_match_filter(self):
        filt1 = Filter(STRING_COLUMN, str, OP_MATCH, ".b.")
        with self.assertRaises(ValueError):
            filt1.get_filter_string()

    def test_broken_ranges(self):
        filt1 = Filter(STRING_COLUMN, str, OP_RANGE, [])
        filt2 = Filter(STRING_COLUMN, str, OP_RANGE, ["abc"])
        filt3 = Filter(STRING_COLUMN, str, OP_RANGE, ["abc", 0])
        filt4 = Filter(STRING_COLUMN, str, OP_RANGE, ["xxx", "abc"])
        filt5 = Filter(INT_COLUMN, int, OP_RANGE, [3, 2, 1])

        with self.assertRaises(ValueError):
            filt1.get_filter_string()
        self.assertEqual(filt2.get_filter_string(),
                         "'abc' <= coq_word_label_1 < 'abc'")
        with self.assertRaises(TypeError):
            filt3.get_filter_string()
        self.assertEqual(filt4.get_filter_string(),
                         "'abc' <= coq_word_label_1 < 'xxx'")
        self.assertEqual(filt5.get_filter_string(),
                         "1 <= coq_corpus_id_1 < 3")

class TestApply(unittest.TestCase):
    df = pd.DataFrame({
            STRING_COLUMN: ['abc', "Peter's", 'xxx', None],
            INT_COLUMN: [1, 2, 3, 7],
            FLOAT_COLUMN: [-1.2345, 0, 1.2345, pd.np.nan],
            BOOL_COLUMN: [True, True, False, False]})

    def assert_index_equal(self, df1, df2):
        self.assertListEqual(df1.index.tolist(), df2.index.tolist())

    def test_bool_filter(self):
        filt1 = Filter(BOOL_COLUMN, bool, OP_EQ, True)
        filt2 = Filter(BOOL_COLUMN, bool, OP_NE, True)

        self.assert_index_equal(filt1.apply(self.df),
                                self.df[self.df[BOOL_COLUMN] == True])
        self.assert_index_equal(filt2.apply(self.df),
                                self.df[self.df[BOOL_COLUMN] != True])

    def test_string_filter(self):
        filt1 = Filter(STRING_COLUMN, str, OP_EQ, "xxx")
        filt2 = Filter(STRING_COLUMN, str, OP_NE, "xxx")
        filt3 = Filter(STRING_COLUMN, str, OP_LT, "xxx")
        filt4 = Filter(STRING_COLUMN, str, OP_LE, "xxx")
        filt5 = Filter(STRING_COLUMN, str, OP_GT, "xxx")
        filt6 = Filter(STRING_COLUMN, str, OP_GE, "xxx")
        filt7 = Filter(STRING_COLUMN, str, OP_IN, ["abc", "xxx"])
        filt8 = Filter(STRING_COLUMN, str, OP_RANGE, ["abc", "xxx"])
        filt9 = Filter(STRING_COLUMN, str, OP_MATCH, ".b")
        filt10 = Filter(STRING_COLUMN, str, OP_NMATCH, ".b")
        filt11 = Filter(STRING_COLUMN, str, OP_EQ, "")
        filt12 = Filter(STRING_COLUMN, str, OP_EQ, None)
        filt13 = Filter(STRING_COLUMN, str, OP_NE, None)

        self.assert_index_equal(
            filt1.apply(self.df), self.df[self.df[STRING_COLUMN] == "xxx"])
        self.assert_index_equal(
            filt2.apply(self.df), self.df[self.df[STRING_COLUMN] != "xxx"])
        self.assert_index_equal(
            filt3.apply(self.df), self.df[self.df[STRING_COLUMN] < "xxx"])
        self.assert_index_equal(
            filt4.apply(self.df), self.df[self.df[STRING_COLUMN] <= "xxx"])
        self.assert_index_equal(
            filt5.apply(self.df), self.df[self.df[STRING_COLUMN] > "xxx"])
        self.assert_index_equal(
            filt6.apply(self.df), self.df[self.df[STRING_COLUMN] >= "xxx"])
        self.assert_index_equal(
            filt7.apply(self.df), self.df[self.df[STRING_COLUMN].isin(["abc", "xxx"])])
        self.assert_index_equal(
            filt8.apply(self.df),
            self.df[("abc" <= self.df[STRING_COLUMN]) &
                    (self.df[STRING_COLUMN] < "xxx")])
        self.assert_index_equal(
            filt9.apply(self.df),
            self.df.dropna()[
                self.df[STRING_COLUMN].dropna().apply(
                    lambda x: bool(re.search(".b", x)))])
        self.assert_index_equal(
            filt10.apply(self.df),
            self.df.dropna()[
                self.df[STRING_COLUMN].dropna().apply(
                    lambda x: not bool(re.search(".b", x)))])
        self.assertEqual(filt11.apply(self.df).index.tolist(), [])
        self.assert_index_equal(
            filt12.apply(self.df), self.df[self.df[STRING_COLUMN].isnull()])
        self.assert_index_equal(
            filt13.apply(self.df), self.df[~self.df[STRING_COLUMN].isnull()])

    def test_numeric_filter(self):
        filt1 = Filter(FLOAT_COLUMN, float, OP_EQ, 1.2345)
        filt2 = Filter(FLOAT_COLUMN, float, OP_NE, 1.2345)
        filt3 = Filter(FLOAT_COLUMN, float, OP_LT, 1.2345)
        filt4 = Filter(FLOAT_COLUMN, float, OP_LE, 1.2345)
        filt5 = Filter(FLOAT_COLUMN, float, OP_GT, 1.2345)
        filt6 = Filter(FLOAT_COLUMN, float, OP_GE, 1.2345)
        filt7 = Filter(FLOAT_COLUMN, float, OP_IN, [-1.2345, 1.2345])
        filt8 = Filter(FLOAT_COLUMN, float, OP_RANGE, [-1.2345, 1.2345])
        filt9 = Filter(FLOAT_COLUMN, float, OP_MATCH, "\.\d\d\d5")
        filt10 = Filter(FLOAT_COLUMN, float, OP_EQ, "")
        filt11 = Filter(FLOAT_COLUMN, float, OP_EQ, None)
        filt12 = Filter(FLOAT_COLUMN, float, OP_NE, None)
        filt13 = Filter(FLOAT_COLUMN, float, OP_EQ, "1.2345")

        self.assert_index_equal(
            filt1.apply(self.df), self.df[self.df[FLOAT_COLUMN] == 1.2345])
        self.assert_index_equal(
            filt2.apply(self.df), self.df[self.df[FLOAT_COLUMN] != 1.2345])
        self.assert_index_equal(
            filt3.apply(self.df), self.df[self.df[FLOAT_COLUMN] < 1.2345])
        self.assert_index_equal(
            filt4.apply(self.df), self.df[self.df[FLOAT_COLUMN] <= 1.2345])
        self.assert_index_equal(
            filt5.apply(self.df), self.df[self.df[FLOAT_COLUMN] > 1.2345])
        self.assert_index_equal(
            filt6.apply(self.df), self.df[self.df[FLOAT_COLUMN] >= 1.2345])
        self.assert_index_equal(
            filt7.apply(self.df),
            self.df[self.df[FLOAT_COLUMN].isin([-1.2345, 1.2345])])
        self.assert_index_equal(
            filt8.apply(self.df),
            self.df[(-1.2345 <= self.df[FLOAT_COLUMN]) &
                    (self.df[FLOAT_COLUMN] < 1.2345)])
        self.assert_index_equal(
            filt9.apply(self.df),
            self.df[self.df[FLOAT_COLUMN].isin([-1.2345, 1.2345])])

        self.assert_index_equal(
            filt10.apply(self.df), self.df[self.df[FLOAT_COLUMN].isnull()])
        self.assert_index_equal(
            filt11.apply(self.df), self.df[self.df[FLOAT_COLUMN].isnull()])
        self.assert_index_equal(
            filt12.apply(self.df), self.df[~self.df[FLOAT_COLUMN].isnull()])
        self.assert_index_equal(
            filt13.apply(self.df), self.df[self.df[FLOAT_COLUMN] == 1.2345])

def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestFilterString),
        unittest.TestLoader().loadTestsFromTestCase(TestApply),
        ])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
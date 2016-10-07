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

df = pd.DataFrame({
        STRING_COLUMN: ['abc', "Peter's", 'xxx', None],
        INT_COLUMN: [1, 2, 3, 7],
        FLOAT_COLUMN: [-1.2345, 0, 1.2345, pd.np.nan]})

class TestFilterString(unittest.TestCase):
    def test_string_values(self):
        filt1 = Filter(STRING_COLUMN, OP_EQ, "abc")
        filt2 = Filter(STRING_COLUMN, OP_EQ, "Peter's")
        self.assertEqual(filt1.get_filter_string(), "coq_word_label_1 == 'abc'")
        self.assertEqual(filt2.get_filter_string(), "coq_word_label_1 == 'Peter\\'s'")

    def test_int_values(self):
        filt1 = Filter(INT_COLUMN, OP_EQ, 0)
        filt2 = Filter(INT_COLUMN, OP_EQ, 5)
        filt3 = Filter(INT_COLUMN, OP_EQ, -5)
        self.assertEqual(filt1.get_filter_string(), "coq_corpus_id_1 == 0")
        self.assertEqual(filt2.get_filter_string(), "coq_corpus_id_1 == 5")
        self.assertEqual(filt3.get_filter_string(), "coq_corpus_id_1 == -5")

    def test_float_values(self):
        filt1 = Filter(FLOAT_COLUMN, OP_EQ, float(1.2345))
        filt2 = Filter(FLOAT_COLUMN, OP_EQ, 0.0)
        filt3 = Filter(FLOAT_COLUMN, OP_EQ, float(-1.2345))
        self.assertEqual(filt1.get_filter_string(), "coq_fraction_1 == 1.2345")
        self.assertEqual(filt2.get_filter_string(), "coq_fraction_1 == 0.0")
        self.assertEqual(filt3.get_filter_string(), "coq_fraction_1 == -1.2345")

    def test_operator_values(self):
        filt1 = Filter(STRING_COLUMN, OP_EQ, "abc")
        filt2 = Filter(STRING_COLUMN, OP_NE, "abc")
        filt3 = Filter(STRING_COLUMN, OP_LT, "abc")
        filt4 = Filter(STRING_COLUMN, OP_LE, "abc")
        filt5 = Filter(STRING_COLUMN, OP_GT, "abc")
        filt6 = Filter(STRING_COLUMN, OP_GE, "abc")
        self.assertEqual(filt1.get_filter_string(), "coq_word_label_1 == 'abc'")
        self.assertEqual(filt2.get_filter_string(), "coq_word_label_1 != 'abc'")
        self.assertEqual(filt3.get_filter_string(), "coq_word_label_1 < 'abc'")
        self.assertEqual(filt4.get_filter_string(), "coq_word_label_1 <= 'abc'")
        self.assertEqual(filt5.get_filter_string(), "coq_word_label_1 > 'abc'")
        self.assertEqual(filt6.get_filter_string(), "coq_word_label_1 >= 'abc'")
        
    def test_list_values(self):
        filt1 = Filter(STRING_COLUMN, OP_IN, ["abc", "Peter's"])
        filt2 = Filter(INT_COLUMN, OP_IN, [1, 2, 3])
        filt3 = Filter(FLOAT_COLUMN, OP_IN, [1.2345, 0.0, -1.2345])
        self.assertEqual(filt1.get_filter_string(), "coq_word_label_1 in ['abc', 'Peter\\'s']")
        self.assertEqual(filt2.get_filter_string(), "coq_corpus_id_1 in [1, 2, 3]")
        self.assertEqual(filt3.get_filter_string(), "coq_fraction_1 in [1.2345, 0.0, -1.2345]")

    def test_range_values(self):
        filt1 = Filter(STRING_COLUMN, OP_RANGE, ["abc", "Peter's"])
        filt2 = Filter(STRING_COLUMN, OP_RANGE, ["abc", "Peter's", "XYZ"])
        filt3 = Filter(STRING_COLUMN, OP_RANGE, ["abc", "xxx"])
        filt4 = Filter(INT_COLUMN, OP_RANGE, [1, 2, 3])
        filt5 = Filter(FLOAT_COLUMN, OP_RANGE, [1.2345, 0.0, -1.2345])
        self.assertEqual(filt1.get_filter_string(), "'Peter\\'s' <= coq_word_label_1 < 'abc'")
        self.assertEqual(filt2.get_filter_string(), "'Peter\\'s' <= coq_word_label_1 < 'abc'")
        self.assertEqual(filt3.get_filter_string(), "'abc' <= coq_word_label_1 < 'xxx'")
        self.assertEqual(filt4.get_filter_string(), "1 <= coq_corpus_id_1 < 3")
        self.assertEqual(filt5.get_filter_string(), "-1.2345 <= coq_fraction_1 < 1.2345")
        
    def test_nan_values(self):
        filt1 = Filter(STRING_COLUMN, OP_EQ, "")
        filt2 = Filter(STRING_COLUMN, OP_EQ, None)
        filt3 = Filter(STRING_COLUMN, OP_NE, None)
        filt4 = Filter(STRING_COLUMN, OP_GT, None)
        filt5 = Filter(INT_COLUMN, OP_EQ, pd.np.nan)
        filt6 = Filter(INT_COLUMN, OP_NE, pd.np.nan)
        self.assertEqual(filt1.get_filter_string(), "coq_word_label_1 == ''")
        self.assertEqual(filt2.get_filter_string(), "coq_word_label_1 != coq_word_label_1")
        self.assertEqual(filt3.get_filter_string(), "coq_word_label_1 == coq_word_label_1")
        with self.assertRaises(ValueError):
            filt4.get_filter_string()
        self.assertEqual(filt5.get_filter_string(), "coq_corpus_id_1 != coq_corpus_id_1")
        self.assertEqual(filt6.get_filter_string(), "coq_corpus_id_1 == coq_corpus_id_1")
        
    def test_match_filter(self):
        filt1 = Filter(STRING_COLUMN, OP_MATCH, ".b.")
        with self.assertRaises(ValueError):
            filt1.get_filter_string()
        
    def test_broken_ranges(self):
        filt1 = Filter(STRING_COLUMN, OP_RANGE, [])
        filt2 = Filter(STRING_COLUMN, OP_RANGE, ["abc"])
        filt3 = Filter(STRING_COLUMN, OP_RANGE, ["abc", 0])
        filt4 = Filter(STRING_COLUMN, OP_RANGE, ["xxx", "abc"])
        filt5 = Filter(INT_COLUMN, OP_RANGE, [3, 2, 1])
        
        with self.assertRaises(ValueError):
            filt1.get_filter_string()
        self.assertEqual(filt2.get_filter_string(), "'abc' <= coq_word_label_1 < 'abc'")
        with self.assertRaises(TypeError):
            filt3.get_filter_string()
        self.assertEqual(filt4.get_filter_string(), "'abc' <= coq_word_label_1 < 'xxx'")
        self.assertEqual(filt5.get_filter_string(), "1 <= coq_corpus_id_1 < 3")

class TestApply(unittest.TestCase):
    def test_string_filter(self):
        filt1 = Filter(STRING_COLUMN, OP_EQ, "xxx")
        filt2 = Filter(STRING_COLUMN, OP_NE, "xxx")
        filt3 = Filter(STRING_COLUMN, OP_LT, "xxx")
        filt4 = Filter(STRING_COLUMN, OP_LE, "xxx")
        filt5 = Filter(STRING_COLUMN, OP_GT, "xxx")
        filt6 = Filter(STRING_COLUMN, OP_GE, "xxx")
        filt7 = Filter(STRING_COLUMN, OP_IN, ["abc", "xxx"])
        filt8 = Filter(STRING_COLUMN, OP_RANGE, ["abc", "xxx"])
        filt9 = Filter(STRING_COLUMN, OP_MATCH, ".b")
        filt10 = Filter(STRING_COLUMN, OP_NMATCH, ".b")
        filt11 = Filter(STRING_COLUMN, OP_EQ, "")
        filt12 = Filter(STRING_COLUMN, OP_EQ, None)
        filt13 = Filter(STRING_COLUMN, OP_NE, None)
        
        self.assertListEqual(filt1.apply(df).index.tolist(), 
                             df[df[STRING_COLUMN] == "xxx"].index.tolist())
        self.assertListEqual(filt2.apply(df).index.tolist(), 
                             df[df[STRING_COLUMN] != "xxx"].index.tolist())
        self.assertListEqual(filt3.apply(df).index.tolist(), 
                             df[df[STRING_COLUMN] < "xxx"].index.tolist())
        self.assertListEqual(filt4.apply(df).index.tolist(), 
                             df[df[STRING_COLUMN] <= "xxx"].index.tolist())
        self.assertListEqual(filt5.apply(df).index.tolist(), 
                             df[df[STRING_COLUMN] > "xxx"].index.tolist())
        self.assertListEqual(filt6.apply(df).index.tolist(), 
                             df[df[STRING_COLUMN] >= "xxx"].index.tolist())
        self.assertListEqual(filt7.apply(df).index.tolist(), 
                             df[df[STRING_COLUMN].isin(["abc", "xxx"])].index.tolist())
        self.assertListEqual(filt8.apply(df).index.tolist(), 
                             df[("abc" <= df[STRING_COLUMN]) & (df[STRING_COLUMN] < "xxx")].index.tolist())
        self.assertListEqual(filt9.apply(df).index.tolist(), 
                             df.dropna()[df[STRING_COLUMN].dropna().apply(lambda x: bool(re.search(".b", x)))].index.tolist())
        self.assertListEqual(filt10.apply(df).index.tolist(), 
                             df.dropna()[df[STRING_COLUMN].dropna().apply(lambda x: not bool(re.search(".b", x)))].index.tolist())
        self.assertListEqual(filt11.apply(df).index.tolist(), [])
        self.assertListEqual(filt12.apply(df).index.tolist(), 
                             df[df[STRING_COLUMN].isnull()].index.tolist())
        self.assertListEqual(filt13.apply(df).index.tolist(), 
                             df[~df[STRING_COLUMN].isnull()].index.tolist())

    def test_numeric_filter(self):
        filt1 = Filter(FLOAT_COLUMN, OP_EQ, 1.2345)
        filt2 = Filter(FLOAT_COLUMN, OP_NE, 1.2345)
        filt3 = Filter(FLOAT_COLUMN, OP_LT, 1.2345)
        filt4 = Filter(FLOAT_COLUMN, OP_LE, 1.2345)
        filt5 = Filter(FLOAT_COLUMN, OP_GT, 1.2345)
        filt6 = Filter(FLOAT_COLUMN, OP_GE, 1.2345)
        filt7 = Filter(FLOAT_COLUMN, OP_IN, [-1.2345, 1.2345])
        filt8 = Filter(FLOAT_COLUMN, OP_RANGE, [-1.2345, 1.2345])
        filt9 = Filter(FLOAT_COLUMN, OP_MATCH, "\.\d\d\d5")
        filt10 = Filter(FLOAT_COLUMN, OP_EQ, "")
        filt11 = Filter(FLOAT_COLUMN, OP_EQ, None)
        filt12 = Filter(FLOAT_COLUMN, OP_NE, None)
        
        self.assertListEqual(filt1.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN] == 1.2345].index.tolist())
        self.assertListEqual(filt2.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN] != 1.2345].index.tolist())
        self.assertListEqual(filt3.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN] < 1.2345].index.tolist())
        self.assertListEqual(filt4.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN] <= 1.2345].index.tolist())
        self.assertListEqual(filt5.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN] > 1.2345].index.tolist())
        self.assertListEqual(filt6.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN] >= 1.2345].index.tolist())
        self.assertListEqual(filt7.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN].isin([-1.2345, 1.2345])].index.tolist())
        self.assertListEqual(filt8.apply(df).index.tolist(), 
                             df[(-1.2345 <= df[FLOAT_COLUMN]) & (df[FLOAT_COLUMN] < 1.2345)].index.tolist())
        self.assertListEqual(filt9.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN].isin([-1.2345, 1.2345])].index.tolist())
        self.assertListEqual(filt10.apply(df).index.tolist(), [])
        self.assertListEqual(filt11.apply(df).index.tolist(), 
                             df[df[FLOAT_COLUMN].isnull()].index.tolist())
        self.assertListEqual(filt12.apply(df).index.tolist(), 
                             df[~df[FLOAT_COLUMN].isnull()].index.tolist())

if __name__ == '__main__':
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestFilterString),
        unittest.TestLoader().loadTestsFromTestCase(TestApply),
        ])
    unittest.TextTestRunner().run(suite)

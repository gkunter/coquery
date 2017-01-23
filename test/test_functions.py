# -*- coding: utf-8 -*-
""" 
This module tests the functions module.

Run it like so:

coquery$ python -m test.test_functions

"""

from __future__ import unicode_literals

import unittest
import os.path
import sys
import pandas as pd
import re

from .mockmodule import MockOptions, MockSettings

from coquery.defines import *
from coquery.functions import *
from coquery.functionlist import FunctionList
from coquery import options

options.cfg = MockOptions()
options.settings = MockSettings()

options.cfg.verbose = False
options.cfg.drop_on_na = False
options.cfg.column_properties = {}
options.cfg.corpus = "Test"

df1 = pd.DataFrame({'coquery_invisible_number_of_tokens': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1, 23: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 1, 29: 1, 30: 1, 31: 1, 32: 1, 33: 1, 34: 1, 35: 1, 36: 1, 37: 1, 38: 1, 39: 1, 40: 1, 41: 1, 42: 1, 43: 1, 44: 1, 45: 1, 46: 1, 47: 1, 48: 1, 49: 1, 50: 1, 51: 1, 52: 1, 53: 1, 54: 1},
                   'db_celex_coq_phonoword_phoncvbr_1': {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: None, 19: None, 20: None, 21: None, 22: None, 23: '[CVC][VC][CCVVC]', 24: '[CVC][VC][CCVVC]', 25: '[CVC][VC][CCVVC]', 26: '[CVC][VC][CCVVC]', 27: '[CVC][VC][CCVVC]', 28: '[CVC][VC][CCVVC]', 29: '[CVC][VC][CCVVC]', 30: '[CVC][VC][CCVVC]', 31: '[CVC][VC][CCVVC]', 32: '[CVC][VC][CCVVC]', 33: '[CVC][VC][CCVVC]', 34: '[CVC][VC][CCVVC]', 35: '[CVC][VC][CCVVC]', 36: '[CVC][VC][CCVVC]', 37: '[CVC][VC][CCVVC]', 38: '[CVC][VC][CCVVC]', 39: '[CVC][VC][CCVVC]', 40: '[CVC][VC][CCVVC]', 41: '[CVC][VC][CCVVC]', 42: '[CVC][VC][CCVVC]', 43: '[CVC][VC][CCVVC]', 44: '[CVC][VC][CCVVC]', 45: '[CVC][VC][CCVVC]', 46: '[CVC][VC][CCVVC]', 47: '[CVC][VC][CCVVC]', 48: '[CVC][VC][CCVVC]', 49: '[CVC][VC][CCVVC]', 50: '[CVC][VC][CCVVC]', 51: '[CVC][VC][CCVVC]', 52: '[CVC][VC][CCVVC]', 53: '[CVC][VC][CCVVC]', 54: '[CVC][VC][CCVVC]'}, 'coq_word_lemma_1': {0: 'DISINVEST', 1: 'DISINVEST', 2: 'DISINVEST', 3: 'DISINVEST', 4: 'DISINVEST', 5: 'DISINVEST', 6: 'DISINVEST', 7: 'DISINVEST', 8: 'DISINVEST', 9: 'DISINVEST', 10: 'DISINVEST', 11: 'DISINVEST', 12: 'DISINVEST', 13: 'DISINVEST', 14: 'DISINVEST', 15: 'DISINVEST', 16: 'DISINVEST', 17: 'DISINVEST', 18: 'DISINVEST', 19: 'DISINVEST', 20: 'DISINVEST', 21: 'DISINFORM', 22: 'DISINFORM', 23: 'DISINCLINE', 24: 'DISINCLINE', 25: 'DISINCLINE', 26: 'DISINCLINE', 27: 'DISINCLINE', 28: 'DISINCLINE', 29: 'DISINCLINE', 30: 'DISINCLINE', 31: 'DISINCLINE', 32: 'DISINCLINE', 33: 'DISINCLINE', 34: 'DISINCLINE', 35: 'DISINCLINE', 36: 'DISINCLINE', 37: 'DISINCLINE', 38: 'DISINCLINE', 39: 'DISINCLINE', 40: 'DISINCLINE', 41: 'DISINCLINE', 42: 'DISINCLINE', 43: 'DISINCLINE', 44: 'DISINCLINE', 45: 'DISINCLINE', 46: 'DISINCLINE', 47: 'DISINCLINE', 48: 'DISINCLINE', 49: 'DISINCLINE', 50: 'DISINCLINE', 51: 'DISINCLINE', 52: 'DISINCLINE', 53: 'DISINCLINE', 54: 'DISINCLINE'}, 
                   'coquery_invisible_corpus_id': {0: 209958039, 1: 222147309, 2: 270672183, 3: 273669329, 4: 338252544, 5: 502550702, 6: 674478400, 7: 679851596, 8: 248429324, 9: 297611776, 10: 473032852, 11: 473034740, 12: 571814551, 13: 597679391, 14: 679683583, 15: 681286004, 16: 429535765, 17: 571814444, 18: 571814457, 19: 571814459, 20: 571814461, 21: 284683786, 22: 433840744, 23: 278745314, 24: 278745314, 25: 278745314, 26: 278745314, 27: 278745314, 28: 278745314, 29: 278745314, 30: 278745314, 31: 278745314, 32: 278745314, 33: 278745314, 34: 278745314, 35: 278745314, 36: 278745314, 37: 278745314, 38: 278745314, 39: 519017348, 40: 519017348, 41: 519017348, 42: 519017348, 43: 519017348, 44: 519017348, 45: 519017348, 46: 519017348, 47: 519017348, 48: 519017348, 49: 519017348, 50: 519017348, 51: 519017348, 52: 519017348, 53: 519017348, 54: 519017348}, 
                   'coquery_dummy': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0}, 
                   'db_celex_coq_phonoword_phonstrsdisc_1': {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: None, 19: None, 20: None, 21: None, 22: None, 23: '"dIs-In-\'kl2n', 24: '"dIs-In-\'kl2n', 25: '"dIs-In-\'kl2n', 26: '"dIs-In-\'kl2n', 27: '"dIs-In-\'kl2n', 28: '"dIs-In-\'kl2n', 29: '"dIs-In-\'kl2n', 30: '"dIs-In-\'kl2n', 31: '"dIs-In-\'kl2n', 32: '"dIs-In-\'kl2n', 33: '"dIs-In-\'kl2n', 34: '"dIs-In-\'kl2n', 35: '"dIs-In-\'kl2n', 36: '"dIs-In-\'kl2n', 37: '"dIs-In-\'kl2n', 38: '"dIs-In-\'kl2n', 39: '"dIs-In-\'kl2n', 40: '"dIs-In-\'kl2n', 41: '"dIs-In-\'kl2n', 42: '"dIs-In-\'kl2n', 43: '"dIs-In-\'kl2n', 44: '"dIs-In-\'kl2n', 45: '"dIs-In-\'kl2n', 46: '"dIs-In-\'kl2n', 47: '"dIs-In-\'kl2n', 48: '"dIs-In-\'kl2n', 49: '"dIs-In-\'kl2n', 50: '"dIs-In-\'kl2n', 51: '"dIs-In-\'kl2n', 52: '"dIs-In-\'kl2n', 53: '"dIs-In-\'kl2n', 54: '"dIs-In-\'kl2n'}, 
                   'db_celex_coq_corpus_cob_1': {0: pd.np.nan, 1: pd.np.nan, 2: pd.np.nan, 3: pd.np.nan, 4: pd.np.nan, 5: pd.np.nan, 6: pd.np.nan, 7: pd.np.nan, 8: pd.np.nan, 9: pd.np.nan, 10: pd.np.nan, 11: pd.np.nan, 12: pd.np.nan, 13: pd.np.nan, 14: pd.np.nan, 15: pd.np.nan, 16: pd.np.nan, 17: pd.np.nan, 18: pd.np.nan, 19: pd.np.nan, 20: pd.np.nan, 21: pd.np.nan, 22: pd.np.nan, 23: 0.0, 24: 0.0, 25: 0.0, 26: 0.0, 27: 0.0, 28: 0.0, 29: 0.0, 30: 0.0, 31: 0.0, 32: 0.0, 33: 0.0, 34: 0.0, 35: 0.0, 36: 0.0, 37: 0.0, 38: 0.0, 39: 0.0, 40: 0.0, 41: 0.0, 42: 0.0, 43: 0.0, 44: 0.0, 45: 0.0, 46: 0.0, 47: 0.0, 48: 0.0, 49: 0.0, 50: 0.0, 51: 0.0, 52: 0.0, 53: 0.0, 54: 0.0}, 
                   'coq_word_label_1': {0: 'DISINVESTING', 1: 'DISINVESTING', 2: 'DISINVESTING', 3: 'DISINVESTING', 4: 'DISINVESTING', 5: 'DISINVESTING', 6: 'DISINVESTING', 7: 'DISINVESTING', 8: 'DISINVEST', 9: 'DISINVEST', 10: 'DISINVEST', 11: 'DISINVEST', 12: 'DISINVEST', 13: 'DISINVEST', 14: 'DISINVEST', 15: 'DISINVEST', 16: 'DISINVESTING', 17: 'DISINVEST', 18: 'DISINVEST', 19: 'DISINVEST', 20: 'DISINVEST', 21: 'DISINFORM', 22: 'DISINFORM', 23: 'DISINCLINE', 24: 'DISINCLINE', 25: 'DISINCLINE', 26: 'DISINCLINE', 27: 'DISINCLINE', 28: 'DISINCLINE', 29: 'DISINCLINE', 30: 'DISINCLINE', 31: 'DISINCLINE', 32: 'DISINCLINE', 33: 'DISINCLINE', 34: 'DISINCLINE', 35: 'DISINCLINE', 36: 'DISINCLINE', 37: 'DISINCLINE', 38: 'DISINCLINE', 39: 'DISINCLINE', 40: 'DISINCLINE', 41: 'DISINCLINE', 42: 'DISINCLINE', 43: 'DISINCLINE', 44: 'DISINCLINE', 45: 'DISINCLINE', 46: 'DISINCLINE', 47: 'DISINCLINE', 48: 'DISINCLINE', 49: 'DISINCLINE', 50: 'DISINCLINE', 51: 'DISINCLINE', 52: 'DISINCLINE', 53: 'DISINCLINE', 54: 'DISINCLINE'},
                   'coquery_invisible_origin_id': {0: 3007917, 1: 3070300, 2: 3036553, 3: 4003221, 4: 4001564, 5: 4060924, 6: 4112423, 7: 4114852, 8: 3049412, 9: 4008118, 10: 4028862, 11: 4028862, 12: 220882, 13: 232557, 14: 4114423, 15: 4119065, 16: 1050494, 17: 220882, 18: 220882, 19: 220882, 20: 220882, 21: 4001783, 22: 1051016, 23: 4004373, 24: 4004373, 25: 4004373, 26: 4004373, 27: 4004373, 28: 4004373, 29: 4004373, 30: 4004373, 31: 4004373, 32: 4004373, 33: 4004373, 34: 4004373, 35: 4004373, 36: 4004373, 37: 4004373, 38: 4004373, 39: 4076097, 40: 4076097, 41: 4076097, 42: 4076097, 43: 4076097, 44: 4076097, 45: 4076097, 46: 4076097, 47: 4076097, 48: 4076097, 49: 4076097, 50: 4076097, 51: 4076097, 52: 4076097, 53: 4076097, 54: 4076097}, 
                   'coq_source_genre_1': {0: 'NEWS', 1: 'NEWS', 2: 'NEWS', 3: 'ACAD', 4: 'ACAD', 5: 'NEWS', 6: 'MAG', 7: 'NEWS', 8: 'NEWS', 9: 'ACAD', 10: 'ACAD', 11: 'ACAD', 12: 'SPOK', 13: 'SPOK', 14: 'NEWS', 15: 'ACAD', 16: 'FIC', 17: 'SPOK', 18: 'SPOK', 19: 'SPOK', 20: 'SPOK', 21: 'ACAD', 22: 'FIC', 23: 'ACAD', 24: 'ACAD', 25: 'ACAD', 26: 'ACAD', 27: 'ACAD', 28: 'ACAD', 29: 'ACAD', 30: 'ACAD', 31: 'ACAD', 32: 'ACAD', 33: 'ACAD', 34: 'ACAD', 35: 'ACAD', 36: 'ACAD', 37: 'ACAD', 38: 'ACAD', 39: 'FIC', 40: 'FIC', 41: 'FIC', 42: 'FIC', 43: 'FIC', 44: 'FIC', 45: 'FIC', 46: 'FIC', 47: 'FIC', 48: 'FIC', 49: 'FIC', 50: 'FIC', 51: 'FIC', 52: 'FIC', 53: 'FIC', 54: 'FIC'}})

df0 = {"coq_word_label_1": ["abc"] * 3 + ["xxx"] * 2,
       "coq_source_genre_1": ["SPOK", "NEWS", "NEWS", "SPOK", "NEWS"],
       "coquery_invisible_corpus_id": range(5)}

STRING_COLUMN = "coq_word_label_1"
INT_COLUMN = "coq_corpus_id_1"
FLOAT_COLUMN = "coq_fraction_1"

df2 = pd.DataFrame({
        STRING_COLUMN: ['abc', "Peter's", 'xxx', None],
        INT_COLUMN: [1, 2, 3, 7],
        FLOAT_COLUMN: [-1.2345, 0, 1.2345, pd.np.nan]})

class TestFrequencyFunctions(unittest.TestCase):
    #def test_freq(self):
        #df = pd.DataFrame(df0)
        #func = Freq(columns=[x for x in df.columns if not x.startswith("coquery_invisible")])
        #val = FunctionList([func]).apply(df, session=None)[func.get_id()]
        #self.assertListEqual(val.tolist(), [1, 2, 2, 1, 1])

    #def test_freq_with_none(self):
        #df = pd.DataFrame(df0)
        #df["coq_test_label_1"] = [None, "A", None, "B", None]
        #func = Freq(columns=[x for x in df.columns if not x.startswith("coquery_invisible")])
        #val = FunctionList([func]).apply(df, session=None)[func.get_id()]
        #self.assertListEqual(val.tolist(), [1, 2, 2, 1, 1])

    #def test_freq_with_nan1(self):
        #df = pd.DataFrame(df0)
        #df["coq_test_label_1"] = [pd.np.nan, "A", pd.np.nan, "B", pd.np.nan]
        #columns = [x for x in df.columns
                   #if not x.startswith("coquery_invisible")]
        #func = Freq(columns=columns)
        #val = FunctionList([func]).apply(df, session=None)[func.get_id()]
        #self.assertListEqual(val.tolist(), [1, 2, 2, 1, 1])

    #def test_freq_with_nan2(self):
        #df = pd.DataFrame(df0)
        #df["coq_test_label_1"] = [pd.np.nan, 1.0, pd.np.nan, 2.0, pd.np.nan]
        #func = Freq(columns=[x for x in df.columns if not x.startswith("coquery_invisible")])
        #val = FunctionList([func]).apply(df, session=None)[func.get_id()]
        #self.assertListEqual(val.tolist(), [1, 2, 2, 1, 1])

    #def test_freq_with_count1(self):
        #df = pd.DataFrame(df0)
        #df["coq_test_label_1"] = [pd.np.nan, "aaa", pd.np.nan, "abc", pd.np.nan]
        #func1 = Freq(columns=[x for x in df.columns if not x.startswith("coquery_invisible")])
        #func2 = StringCount(columns=["coq_test_label_1"], value="a")
        #val = FunctionList([func1, func2]).apply(df, session=None)[func1.get_id()]
        #self.assertListEqual(val.tolist(), [1, 2, 2, 1, 1])

    #def test_count_with_nan(self):
        #df = pd.DataFrame(df1)
        #func = StringCount(columns=["db_celex_coq_phonoword_phoncvbr_1"], value="[")
        #df = FunctionList([func]).apply(df, session=None)
        #func = Freq(columns=[x for x in df.columns if not x.startswith("coquery_invisible")])
        #func_list = FunctionList([func])
        #val_a = func_list.apply(df, session=None)[func.get_id()]
        ##print(df)

        #df = pd.DataFrame(df1)
        #df = df[[x for x in df if x.startswith("coq_")]]
        #func = Freq(columns=df.columns)
        #func_list = FunctionList([func])
        #val_b = func_list.apply(df, session=None)[func.get_id()]
        
        #self.assertListEqual(val_a.tolist(), val_b.tolist())

class TestStringFunctions(unittest.TestCase):
    def test_count(self):
        func = StringCount(columns=["coq_word_label_1"], value="x")
        val = FunctionList([func]).apply(df0, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [0, 0, 0, 3, 3])

def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestFrequencyFunctions),
        unittest.TestLoader().loadTestsFromTestCase(TestStringFunctions),
        ])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
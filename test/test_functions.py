# -*- coding: utf-8 -*-
"""
This module tests the functions module.

Run it like so:

coquery$ python -m test.test_functions

"""

from __future__ import unicode_literals
from __future__ import division

import warnings
import argparse
import pandas as pd
import numpy as np


from coquery.functions import (
    get_base_func,
    Function,
    BaseProportion, TypeTokenRatio,
    BaseReferenceCorpus, ReferenceCorpusFrequencyPTW,
    Freq,
    StringCount, StringLength, StringChain, StringMatch, StringExtract,
    StringUpper, StringLower, StringReplace,
    Add, Sub, Mul, Div, Log,
    Min, Max, Mean, Median, StandardDeviation, InterquartileRange,
    Percentile,
    Equal, NotEqual, GreaterThan, GreaterEqual, LessThan, LessEqual,
    And, Or, Xor, If, Empty, Missing,
    MutualInformation,
    ToNumeric, ToCategory,
    )

from coquery import options
from coquery.defines import DEFAULT_CONFIGURATION
from coquery.connections import SQLiteConnection
from coquery.corpus import CorpusClass, BaseResource
from coquery.functionlist import FunctionList
from coquery.session import Session

from test.testcase import CoqTestCase, run_tests

df0 = pd.DataFrame({
    'coq_word_label_1': ['abc'] * 3 + ['x'] * 2,
    'coq_word_label_2': ['a'] * 4 + [pd.NA],
    'coq_source_genre_1': ['SPOK', 'NEWS', 'NEWS', 'SPOK', 'NEWS'],
    'coquery_invisible_corpus_id': range(5),
    })

df1 = pd.DataFrame({
    'coquery_invisible_number_of_tokens': {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1,
        15: 1,
        16: 1,
        17: 1,
        18: 1,
        19: 1,
        20: 1,
        21: 1,
        22: 1,
        23: 1,
        24: 1,
        25: 1,
        26: 1,
        27: 1,
        28: 1,
        29: 1,
        30: 1,
        31: 1,
        32: 1,
        33: 1,
        34: 1,
        35: 1,
        36: 1,
        37: 1,
        38: 1,
        39: 1,
        40: 1,
        41: 1,
        42: 1,
        43: 1,
        44: 1,
        45: 1,
        46: 1,
        47: 1,
        48: 1,
        49: 1,
        50: 1,
        51: 1,
        52: 1,
        53: 1,
        54: 1,
        },
    'db_celex_coq_phonoword_phoncvbr_1': {
        0: None,
        1: None,
        2: None,
        3: None,
        4: None,
        5: None,
        6: None,
        7: None,
        8: None,
        9: None,
        10: None,
        11: None,
        12: None,
        13: None,
        14: None,
        15: None,
        16: None,
        17: None,
        18: None,
        19: None,
        20: None,
        21: None,
        22: None,
        23: '[CVC][VC][CCVVC]',
        24: '[CVC][VC][CCVVC]',
        25: '[CVC][VC][CCVVC]',
        26: '[CVC][VC][CCVVC]',
        27: '[CVC][VC][CCVVC]',
        28: '[CVC][VC][CCVVC]',
        29: '[CVC][VC][CCVVC]',
        30: '[CVC][VC][CCVVC]',
        31: '[CVC][VC][CCVVC]',
        32: '[CVC][VC][CCVVC]',
        33: '[CVC][VC][CCVVC]',
        34: '[CVC][VC][CCVVC]',
        35: '[CVC][VC][CCVVC]',
        36: '[CVC][VC][CCVVC]',
        37: '[CVC][VC][CCVVC]',
        38: '[CVC][VC][CCVVC]',
        39: '[CVC][VC][CCVVC]',
        40: '[CVC][VC][CCVVC]',
        41: '[CVC][VC][CCVVC]',
        42: '[CVC][VC][CCVVC]',
        43: '[CVC][VC][CCVVC]',
        44: '[CVC][VC][CCVVC]',
        45: '[CVC][VC][CCVVC]',
        46: '[CVC][VC][CCVVC]',
        47: '[CVC][VC][CCVVC]',
        48: '[CVC][VC][CCVVC]',
        49: '[CVC][VC][CCVVC]',
        50: '[CVC][VC][CCVVC]',
        51: '[CVC][VC][CCVVC]',
        52: '[CVC][VC][CCVVC]',
        53: '[CVC][VC][CCVVC]',
        54: '[CVC][VC][CCVVC]',
        },
    'coq_word_lemma_1': {
        0: 'DISINVEST',
        1: 'DISINVEST',
        2: 'DISINVEST',
        3: 'DISINVEST',
        4: 'DISINVEST',
        5: 'DISINVEST',
        6: 'DISINVEST',
        7: 'DISINVEST',
        8: 'DISINVEST',
        9: 'DISINVEST',
        10: 'DISINVEST',
        11: 'DISINVEST',
        12: 'DISINVEST',
        13: 'DISINVEST',
        14: 'DISINVEST',
        15: 'DISINVEST',
        16: 'DISINVEST',
        17: 'DISINVEST',
        18: 'DISINVEST',
        19: 'DISINVEST',
        20: 'DISINVEST',
        21: 'DISINFORM',
        22: 'DISINFORM',
        23: 'DISINCLINE',
        24: 'DISINCLINE',
        25: 'DISINCLINE',
        26: 'DISINCLINE',
        27: 'DISINCLINE',
        28: 'DISINCLINE',
        29: 'DISINCLINE',
        30: 'DISINCLINE',
        31: 'DISINCLINE',
        32: 'DISINCLINE',
        33: 'DISINCLINE',
        34: 'DISINCLINE',
        35: 'DISINCLINE',
        36: 'DISINCLINE',
        37: 'DISINCLINE',
        38: 'DISINCLINE',
        39: 'DISINCLINE',
        40: 'DISINCLINE',
        41: 'DISINCLINE',
        42: 'DISINCLINE',
        43: 'DISINCLINE',
        44: 'DISINCLINE',
        45: 'DISINCLINE',
        46: 'DISINCLINE',
        47: 'DISINCLINE',
        48: 'DISINCLINE',
        49: 'DISINCLINE',
        50: 'DISINCLINE',
        51: 'DISINCLINE',
        52: 'DISINCLINE',
        53: 'DISINCLINE',
        54: 'DISINCLINE',
        },
    'coquery_invisible_corpus_id': {
        0: 209958039,
        1: 222147309,
        2: 270672183,
        3: 273669329,
        4: 338252544,
        5: 502550702,
        6: 674478400,
        7: 679851596,
        8: 248429324,
        9: 297611776,
        10: 473032852,
        11: 473034740,
        12: 571814551,
        13: 597679391,
        14: 679683583,
        15: 681286004,
        16: 429535765,
        17: 571814444,
        18: 571814457,
        19: 571814459,
        20: 571814461,
        21: 284683786,
        22: 433840744,
        23: 278745314,
        24: 278745314,
        25: 278745314,
        26: 278745314,
        27: 278745314,
        28: 278745314,
        29: 278745314,
        30: 278745314,
        31: 278745314,
        32: 278745314,
        33: 278745314,
        34: 278745314,
        35: 278745314,
        36: 278745314,
        37: 278745314,
        38: 278745314,
        39: 519017348,
        40: 519017348,
        41: 519017348,
        42: 519017348,
        43: 519017348,
        44: 519017348,
        45: 519017348,
        46: 519017348,
        47: 519017348,
        48: 519017348,
        49: 519017348,
        50: 519017348,
        51: 519017348,
        52: 519017348,
        53: 519017348,
        54: 519017348,
        },
    'coquery_dummy': {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: 0,
        13: 0,
        14: 0,
        15: 0,
        16: 0,
        17: 0,
        18: 0,
        19: 0,
        20: 0,
        21: 0,
        22: 0,
        23: 0,
        24: 0,
        25: 0,
        26: 0,
        27: 0,
        28: 0,
        29: 0,
        30: 0,
        31: 0,
        32: 0,
        33: 0,
        34: 0,
        35: 0,
        36: 0,
        37: 0,
        38: 0,
        39: 0,
        40: 0,
        41: 0,
        42: 0,
        43: 0,
        44: 0,
        45: 0,
        46: 0,
        47: 0,
        48: 0,
        49: 0,
        50: 0,
        51: 0,
        52: 0,
        53: 0,
        54: 0,
        },
    'db_celex_coq_phonoword_phonstrsdisc_1': {
        0: None,
        1: None,
        2: None,
        3: None,
        4: None,
        5: None,
        6: None,
        7: None,
        8: None,
        9: None,
        10: None,
        11: None,
        12: None,
        13: None,
        14: None,
        15: None,
        16: None,
        17: None,
        18: None,
        19: None,
        20: None,
        21: None,
        22: None,
        23: '"dIs-In-\'kl2n',
        24: '"dIs-In-\'kl2n',
        25: '"dIs-In-\'kl2n',
        26: '"dIs-In-\'kl2n',
        27: '"dIs-In-\'kl2n',
        28: '"dIs-In-\'kl2n',
        29: '"dIs-In-\'kl2n',
        30: '"dIs-In-\'kl2n',
        31: '"dIs-In-\'kl2n',
        32: '"dIs-In-\'kl2n',
        33: '"dIs-In-\'kl2n',
        34: '"dIs-In-\'kl2n',
        35: '"dIs-In-\'kl2n',
        36: '"dIs-In-\'kl2n',
        37: '"dIs-In-\'kl2n',
        38: '"dIs-In-\'kl2n',
        39: '"dIs-In-\'kl2n',
        40: '"dIs-In-\'kl2n',
        41: '"dIs-In-\'kl2n',
        42: '"dIs-In-\'kl2n',
        43: '"dIs-In-\'kl2n',
        44: '"dIs-In-\'kl2n',
        45: '"dIs-In-\'kl2n',
        46: '"dIs-In-\'kl2n',
        47: '"dIs-In-\'kl2n',
        48: '"dIs-In-\'kl2n',
        49: '"dIs-In-\'kl2n',
        50: '"dIs-In-\'kl2n',
        51: '"dIs-In-\'kl2n',
        52: '"dIs-In-\'kl2n',
        53: '"dIs-In-\'kl2n',
        54: '"dIs-In-\'kl2n',
        },
    'db_celex_coq_corpus_cob_1': {
        0: np.nan,
        1: np.nan,
        2: np.nan,
        3: np.nan,
        4: np.nan,
        5: np.nan,
        6: np.nan,
        7: np.nan,
        8: np.nan,
        9: np.nan,
        10: np.nan,
        11: np.nan,
        12: np.nan,
        13: np.nan,
        14: np.nan,
        15: np.nan,
        16: np.nan,
        17: np.nan,
        18: np.nan,
        19: np.nan,
        20: np.nan,
        21: np.nan,
        22: np.nan,
        23: 0.0,
        24: 0.0,
        25: 0.0,
        26: 0.0,
        27: 0.0,
        28: 0.0,
        29: 0.0,
        30: 0.0,
        31: 0.0,
        32: 0.0,
        33: 0.0,
        34: 0.0,
        35: 0.0,
        36: 0.0,
        37: 0.0,
        38: 0.0,
        39: 0.0,
        40: 0.0,
        41: 0.0,
        42: 0.0,
        43: 0.0,
        44: 0.0,
        45: 0.0,
        46: 0.0,
        47: 0.0,
        48: 0.0,
        49: 0.0,
        50: 0.0,
        51: 0.0,
        52: 0.0,
        53: 0.0,
        54: 0.0,
        },
    'coq_word_label_1': {
        0: 'DISINVESTING',
        1: 'DISINVESTING',
        2: 'DISINVESTING',
        3: 'DISINVESTING',
        4: 'DISINVESTING',
        5: 'DISINVESTING',
        6: 'DISINVESTING',
        7: 'DISINVESTING',
        8: 'DISINVEST',
        9: 'DISINVEST',
        10: 'DISINVEST',
        11: 'DISINVEST',
        12: 'DISINVEST',
        13: 'DISINVEST',
        14: 'DISINVEST',
        15: 'DISINVEST',
        16: 'DISINVESTING',
        17: 'DISINVEST',
        18: 'DISINVEST',
        19: 'DISINVEST',
        20: 'DISINVEST',
        21: 'DISINFORM',
        22: 'DISINFORM',
        23: 'DISINCLINE',
        24: 'DISINCLINE',
        25: 'DISINCLINE',
        26: 'DISINCLINE',
        27: 'DISINCLINE',
        28: 'DISINCLINE',
        29: 'DISINCLINE',
        30: 'DISINCLINE',
        31: 'DISINCLINE',
        32: 'DISINCLINE',
        33: 'DISINCLINE',
        34: 'DISINCLINE',
        35: 'DISINCLINE',
        36: 'DISINCLINE',
        37: 'DISINCLINE',
        38: 'DISINCLINE',
        39: 'DISINCLINE',
        40: 'DISINCLINE',
        41: 'DISINCLINE',
        42: 'DISINCLINE',
        43: 'DISINCLINE',
        44: 'DISINCLINE',
        45: 'DISINCLINE',
        46: 'DISINCLINE',
        47: 'DISINCLINE',
        48: 'DISINCLINE',
        49: 'DISINCLINE',
        50: 'DISINCLINE',
        51: 'DISINCLINE',
        52: 'DISINCLINE',
        53: 'DISINCLINE',
        54: 'DISINCLINE',
        },
    'coquery_invisible_origin_id': {
        0: 3007917,
        1: 3070300,
        2: 3036553,
        3: 4003221,
        4: 4001564,
        5: 4060924,
        6: 4112423,
        7: 4114852,
        8: 3049412,
        9: 4008118,
        10: 4028862,
        11: 4028862,
        12: 220882,
        13: 232557,
        14: 4114423,
        15: 4119065,
        16: 1050494,
        17: 220882,
        18: 220882,
        19: 220882,
        20: 220882,
        21: 4001783,
        22: 1051016,
        23: 4004373,
        24: 4004373,
        25: 4004373,
        26: 4004373,
        27: 4004373,
        28: 4004373,
        29: 4004373,
        30: 4004373,
        31: 4004373,
        32: 4004373,
        33: 4004373,
        34: 4004373,
        35: 4004373,
        36: 4004373,
        37: 4004373,
        38: 4004373,
        39: 4076097,
        40: 4076097,
        41: 4076097,
        42: 4076097,
        43: 4076097,
        44: 4076097,
        45: 4076097,
        46: 4076097,
        47: 4076097,
        48: 4076097,
        49: 4076097,
        50: 4076097,
        51: 4076097,
        52: 4076097,
        53: 4076097,
        54: 4076097,
        },
    'coq_source_genre_1': {
        0: 'NEWS',
        1: 'NEWS',
        2: 'NEWS',
        3: 'ACAD',
        4: 'ACAD',
        5: 'NEWS',
        6: 'MAG',
        7: 'NEWS',
        8: 'NEWS',
        9: 'ACAD',
        10: 'ACAD',
        11: 'ACAD',
        12: 'SPOK',
        13: 'SPOK',
        14: 'NEWS',
        15: 'ACAD',
        16: 'FIC',
        17: 'SPOK',
        18: 'SPOK',
        19: 'SPOK',
        20: 'SPOK',
        21: 'ACAD',
        22: 'FIC',
        23: 'ACAD',
        24: 'ACAD',
        25: 'ACAD',
        26: 'ACAD',
        27: 'ACAD',
        28: 'ACAD',
        29: 'ACAD',
        30: 'ACAD',
        31: 'ACAD',
        32: 'ACAD',
        33: 'ACAD',
        34: 'ACAD',
        35: 'ACAD',
        36: 'ACAD',
        37: 'ACAD',
        38: 'ACAD',
        39: 'FIC',
        40: 'FIC',
        41: 'FIC',
        42: 'FIC',
        43: 'FIC',
        44: 'FIC',
        45: 'FIC',
        46: 'FIC',
        47: 'FIC',
        48: 'FIC',
        49: 'FIC',
        50: 'FIC',
        51: 'FIC',
        52: 'FIC',
        53: 'FIC',
        54: 'FIC',
        },
    })

STRING_COLUMN = "coq_word_label_1"
INT_COLUMN = "coq_corpus_id_1"
FLOAT_COLUMN = "coq_fraction_1"

df2 = pd.DataFrame({
        STRING_COLUMN: ['abc', "Peter's", 'xxx', pd.NA],
        INT_COLUMN: [1, 2, 3, 7],
        FLOAT_COLUMN: [-1.2345, 0, 1.2345, np.nan]})


class FncTestCase(CoqTestCase):
    def setUp(self):
        options.cfg = argparse.Namespace()

        options.cfg.verbose = False
        options.cfg.drop_on_na = False
        options.cfg.benchmark = False

        self.df = df0.copy()


class TestModuleFunctions(FncTestCase):
    def test_get_base_func_1(self):
        func = Function()
        self.assertEqual(Function, get_base_func(func))
        self.assertEqual(Function, get_base_func(Function))

    def test_get_base_func_2(self):
        self.assertEqual(BaseProportion, get_base_func(TypeTokenRatio))

    def test_get_base_func_3(self):
        self.assertEqual(BaseReferenceCorpus,
                         get_base_func(ReferenceCorpusFrequencyPTW))


class TestFrequencyFunctions(FncTestCase):
    def test_freq(self):
        df = df0.copy()
        func = Freq(columns=[x for x in df.columns
                             if not x.startswith("coquery_invisible")])
        val = FunctionList([func]).lapply(df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [1, 2, 2, 1, 1])

    def test_freq_with_none(self):
        df = df0.copy()
        df["coq_test_label_1"] = [pd.NA, "A", pd.NA, "B", pd.NA]
        func = Freq(columns=["coq_word_label_1", "coq_test_label_1"])
        val = FunctionList([func]).lapply(df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [2, 1, 2, 1, 1])

    def test_freq_with_nan1(self):
        df = df0.copy()
        df["coq_test_label_1"] = [np.nan, "A", np.nan, "B", np.nan]
        func = Freq(columns=["coq_word_label_1", "coq_test_label_1"])
        val = FunctionList([func]).lapply(df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [2, 1, 2, 1, 1])


class TestStringFunctions(FncTestCase):
    def test_count_1(self):
        func = StringCount(columns=["coq_word_label_1"], pat="x")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [0, 0, 0, 1, 1])

    def test_count_2(self):
        func = StringCount(columns=["coq_word_label_1"], pat="X")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [0, 0, 0, 1, 1])

    def test_count_case_1(self):
        func = StringCount(columns=["coq_word_label_1"], pat="x", case=True)
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [0, 0, 0, 1, 1])

    def test_count_case_2(self):
        func = StringCount(columns=["coq_word_label_1"], pat="X", case=True)
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [0, 0, 0, 0, 0])

    def test_count_null(self):
        func = StringCount(columns=["coq_word_label_2"], pat="a")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [1, 1, 1, 1, 0])

    def test_length(self):
        func = StringLength(columns=["coq_word_label_1"])
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [3, 3, 3, 1, 1])

    def test_length_null(self):
        func = StringLength(columns=["coq_word_label_2"])
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(val.tolist(), [1, 1, 1, 1, 0])

    def test_chain(self):
        func = StringChain(
            columns=["coq_word_label_1", "coq_source_genre_1"],
            sep=" ")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(
            val.tolist(),
            ["abc SPOK", "abc NEWS", "abc NEWS", "x SPOK", "x NEWS"])

    def test_chain_na(self):
        func = StringChain(
            columns=["coq_word_label_1", "coq_word_label_2"],
            sep=" ")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(
            val.tolist(),
            ["abc a", "abc a", "abc a", "x a", "x"])

    def test_chain_num(self):
        func = StringChain(
            columns=["coq_word_label_1", "coquery_invisible_corpus_id"],
            sep=" ")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(
            val.tolist(),
            ["abc 0", "abc 1", "abc 2", "x 3", "x 4"])

    def test_match_1(self):
        func = StringMatch(columns=["coq_word_label_1"], pat="[a]")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(
            val.tolist(), [True, True, True, False, False])

    def test_match_2(self):
        func = StringMatch(columns=["coq_word_label_1"], pat="[A]")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(
            val.tolist(), [True, True, True, False, False])

    def test_match_case_1(self):
        func = StringMatch(columns=["coq_word_label_1"], pat="[A]", case=True)
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(
            val.tolist(), [False, False, False, False, False])

    def test_match_case_2(self):
        func = StringMatch(columns=["coq_word_label_1"], pat="[a]", case=True)
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(
            val.tolist(), [True, True, True, False, False])

    def test_match_null(self):
        func = StringMatch(columns=["coq_word_label_2"], pat="[a]")
        val = FunctionList([func]).lapply(self.df, session=None)[func.get_id()]
        self.assertListEqual(
            val.tolist(), [True, True, True, True, False])

    def test_extract_1(self):
        func = StringExtract(columns=["coq_word_label_1"], pat="[ABX]*")
        val = FunctionList([func]).lapply(self.df, session=None)
        self.assertListEqual(
            val.iloc[:, -1].values.ravel().tolist(),
            ["ab", "ab", "ab", "x", "x"])

    def test_extract_2(self):
        func = StringExtract(columns=["coq_word_label_1"], pat="[abx]*")
        val = FunctionList([func]).lapply(self.df, session=None)
        self.assertListEqual(
            val.iloc[:, -1].values.ravel().tolist(),
            ["ab", "ab", "ab", "x", "x"])

    def test_extract_case_1(self):
        func = StringExtract(columns=["coq_word_label_1"],
                             pat="[ABX]*", case=True)
        val = FunctionList([func]).lapply(self.df, session=None)
        self.assertListEqual(
            val.iloc[:, -1].values.ravel().tolist(),
            ["", "", "", "", ""])

    def test_extract_case_2(self):
        func = StringExtract(columns=["coq_word_label_1"],
                             pat="[abx]*", case=True)
        val = FunctionList([func]).lapply(self.df, session=None)
        self.assertListEqual(
            val.iloc[:, -1].values.ravel().tolist(),
            ["ab", "ab", "ab", "x", "x"])

    def test_extract_groups(self):
        """
        Tests issue #255
        """
        df = pd.DataFrame({"a": ["abx"] * 5 + ["a"] * 5 + ["bx"] * 5,
                           "b": [""] * 10 + ["yyannxzzz"] * 5})
        func = StringExtract(columns=["a"], pat="(a).*(x)")
        val = FunctionList([func]).lapply(df, session=None)

        result = val.iloc[:, -2]
        target = pd.Series(["a"] * 5 + [pd.NA] * 10)
        self.assertEqual(len(val.iloc[:, -2].compare(target)), 0)

        target = pd.Series(["x"] * 5 + [pd.NA] * 10)
        self.assertEqual(len(val.iloc[:, -1].compare(target)), 0)

    def test_extract_groups_and_compare(self):
        df = pd.DataFrame({"word": ["win-win",
                                    "lose-win",
                                    "self-destruct",
                                    "abcde"]})

        func1 = StringExtract(columns=["word"], pat="(.*)-(.*)")
        df = FunctionList([func1]).lapply(df, session=None)
        func2 = Equal(columns=df.columns[-2:])
        val = FunctionList([func2]).lapply(df, session=None)
        pd.testing.assert_series_equal(
            val[func2.get_id()],
            pd.Series([True, False, False, False]),
            check_names=False,
            check_dtype=False)

    def test_extract_with_illegal_regexp(self):
        """
        Test issue #297.

        If a regular expression is faulty and raises a RegularExpressionError,
        the function containing the expression should return a column
        consisting only of NAs.
        """

        df = pd.DataFrame({"Query string": ["/? ??? ?/"] * 5})

        func = StringExtract(columns=["Query string"], pat="^? ???")

        df = FunctionList([func]).lapply(df, session=None)
        pd.testing.assert_series_equal(
            df[func.get_id()],
            pd.Series([pd.NA] * len(df)),
            check_names=False)

    def test_upper(self):
        df = pd.DataFrame({"a": ["abx"] * 5 + ["a"] * 5 + ["bx"] * 5,
                           "b": [""] * 10 + ["yyannxzzz"] * 5})
        func = StringUpper(columns=["a"])
        val = FunctionList([func]).lapply(df, session=None).iloc[:, -1]
        self.assertListEqual(
            val.values.ravel().tolist(),
            ["ABX"] * 5 + ["A"] * 5 + ["BX"] * 5)

    def test_upper_multi(self):
        df = pd.DataFrame({"a": ["abx"] * 5 + ["a"] * 5 + ["bx"] * 5,
                           "b": [""] * 10 + ["yyannxzzz"] * 5})
        func = StringUpper(columns=["a", "b"])
        val = FunctionList([func]).lapply(df, session=None)
        self.assertListEqual(
            val.iloc[:, -2].values.ravel().tolist(),
            ["ABX"] * 5 + ["A"] * 5 + ["BX"] * 5)
        self.assertListEqual(
            val.iloc[:, -1].values.ravel().tolist(),
            [""] * 10 + ["YYANNXZZZ"] * 5)

    def test_lower(self):
        df = pd.DataFrame({"a": list("ABCDEFGHIJ"),
                           "b": list("ABABABABAB")})
        func = StringLower(columns=["a"])
        val = FunctionList([func]).lapply(df, session=None).iloc[:, -1]
        self.assertListEqual(
            val.values.ravel().tolist(), list("abcdefghij"))

    def test_lower_multi(self):
        df = pd.DataFrame({"a": list("ABCDEFGHIJ"),
                           "b": list("ABABABABAB")})
        func = StringLower(columns=["a", "b"])
        val = FunctionList([func]).lapply(df, session=None)
        self.assertListEqual(
            val.iloc[:, -2].values.ravel().tolist(), list("abcdefghij"))
        self.assertListEqual(
            val.iloc[:, -1].values.ravel().tolist(), list("ababababab"))

    def test_replace_1(self):
        func = StringReplace(columns=["coq_source_genre_1"],
                             pat="S", repl="s")
        val = FunctionList([func]).lapply(self.df, session=None).iloc[:, -1]
        self.assertListEqual(
            val.values.ravel().tolist(),
            ["sPOK", "NEWs", "NEWs", "sPOK", "NEWs"])

    def test_replace_2(self):
        func = StringReplace(columns=["coq_source_genre_1"],
                             pat="s", repl="s")
        val = FunctionList([func]).lapply(self.df, session=None).iloc[:, -1]
        self.assertListEqual(
            val.values.ravel().tolist(),
            ["sPOK", "NEWs", "NEWs", "sPOK", "NEWs"])

    def test_replace_multi(self):
        func = StringReplace(columns=["coq_word_label_1", "coq_word_label_2"],
                             pat="a", repl="A")
        val = FunctionList([func]).lapply(self.df, session=None)
        self.assertListEqual(
            val.iloc[:, -2].values.ravel().tolist(),
            ["Abc"] * 3 + ["x"] * 2)
        self.assertListEqual(
            val.iloc[:, -1].values.ravel().tolist(),
            ["A"] * 4 + [pd.NA])


class TestProportionFunctions(FncTestCase):
    def _get_frequency(_, s, _engine, *args, **kwargs):
        return {
            "a": 100,
            "x": 20,
            "abc": 1000,
            "abc a": 5,
            "x a": 10,
            }.get(s, pd.NA)

    def _get_corpus_size(_, *args, **kwargs):
        return 100000

    def setUp(self):
        super().setUp()
        default = SQLiteConnection(DEFAULT_CONFIGURATION)
        options.cfg.current_connection = default
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.Session = Session()
        self.Session.Resource = BaseResource
        self.Session.Resource.db_name = "db_test"
        self.Session.Resource.corpus = CorpusClass()
        self.Session.Resource.corpus.resource = self.Session.Resource
        self.Session.Resource.corpus.get_frequency = self._get_frequency
        self.Session.Resource.corpus.get_corpus_size = self._get_corpus_size

    def _get_dummy_frequency(self, *args, **kwargs):
        return self.Session.resource

    def test_mutual_information_1(self):
        columns = ["coq_word_label_1", "coq_word_label_2"]
        func = MutualInformation(columns)
        func_list = FunctionList([func])
        val = func_list.lapply(self.df, session=self.Session)[func.get_id()]
        _f_abc_a = self.Session.Resource.corpus.get_frequency("abc a", pd.NA)
        _f_x_a = self.Session.Resource.corpus.get_frequency("x a", pd.NA)
        _f_abc = self.Session.Resource.corpus.get_frequency("abc", pd.NA)
        _f_x = self.Session.Resource.corpus.get_frequency("x", pd.NA)
        _f_a = self.Session.Resource.corpus.get_frequency("a", pd.NA)
        _n = self.Session.Resource.corpus.get_corpus_size()

        target = pd.Series([np.log2((_f_abc_a * _n) / (_f_abc * _f_a)),
                            np.log2((_f_abc_a * _n) / (_f_abc * _f_a)),
                            np.log2((_f_abc_a * _n) / (_f_abc * _f_a)),
                            np.log2((_f_x_a * _n) / (_f_x * _f_a)),
                            pd.NA])

        pd.testing.assert_series_equal(val, target, check_names=False)


class TestMathFunctions(FncTestCase):
    def setUp(self):
        super(TestMathFunctions, self).setUp()

        self.df = pd.DataFrame(
                    {"column_1": [2, 5, 7, 9],
                     "column_2": [3, 3, 3, 3],
                     "column_3": [2, np.nan, np.nan, 0],
                     "column_4": [2.1, 2.2, 2.3, 2.4],
                     "column_5": list("abcd"),
                     "column_6": [0, 1, 0, 1]})

    def assert_result(self, func_class, df, columns, expected,
                      value=None, **kwargs):
        func = func_class(columns=columns, value=value, **kwargs)
        result = FunctionList([func]).lapply(df, session=None)

        pd.testing.assert_series_equal(
            result[func.get_id()],
            pd.Series(expected),
            check_names=False,
            check_dtype=False)

    def test_coerce_value_int_1(self):
        columns = ["column_1", "column_2"]
        value = "2"
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), 2)
        self.assertEqual(type(
            func.coerce_value(self.df, value)), float)

    def test_coerce_value_int_2(self):
        columns = ["column_1", "column_2"]
        value = "2.0"
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), 2)
        self.assertEqual(type(
            func.coerce_value(self.df, value)), float)

    def test_coerce_value_int_3(self):
        columns = ["column_1", "column_2"]
        value = 2.0
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), 2)
        self.assertEqual(type(
            func.coerce_value(self.df, value)), float)

    def test_coerce_value_int_4(self):
        columns = ["column_1", "column_2"]
        value = 2
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), 2)
        self.assertEqual(type(
            func.coerce_value(self.df, value)), float)

    def test_coerce_value_float_1(self):
        columns = ["column_3", "column_4"]
        value = "2"
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), 2)
        self.assertEqual(type(
            func.coerce_value(self.df, value)), float)

    def test_coerce_value_float_2(self):
        columns = ["column_3", "column_4"]
        value = "2.0"
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), 2)
        self.assertEqual(type(
            func.coerce_value(self.df, value)), float)

    def test_coerce_value_float_3(self):
        columns = ["column_3", "column_4"]
        value = 2.0
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), 2)
        self.assertEqual(type(
            func.coerce_value(self.df, value)), float)

    def test_coerce_value_float_4(self):
        columns = ["column_3", "column_4"]
        value = 2
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), 2)
        self.assertEqual(type(
            func.coerce_value(self.df, value)), float)

    def test_coerce_value_string_1(self):
        columns = ["column_1", "column_5"]
        value = "2"
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), "2")
        self.assertEqual(
            type(func.coerce_value(self.df, value)), str)

    def test_coerce_value_string_2(self):
        columns = ["column_1", "column_5"]
        value = "2.0"
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), "2.0")
        self.assertEqual(
            type(func.coerce_value(self.df, value)), str)

    def test_coerce_value_string_3(self):
        columns = ["column_1", "column_5"]
        value = 2.0
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), "2.0")
        self.assertEqual(
            type(func.coerce_value(self.df, value)), str)

    def test_coerce_value_string_4(self):
        columns = ["column_1", "column_5"]
        value = 2
        func = Add(columns=columns, value=value)
        self.assertEqual(func.coerce_value(self.df, value), "2")
        self.assertEqual(
            type(func.coerce_value(self.df, value)), str)

    def test_add(self):
        columns = ["column_1", "column_2"]
        expected = [5, 8, 10, 12]
        func = Add
        self.assert_result(func, self.df, columns, expected)

    def test_add_nan(self):
        columns = ["column_1", "column_3"]
        expected = [4, pd.NA, pd.NA, 9]
        func = Add
        self.assert_result(func, self.df, columns, expected)

    def test_add_fixed_1(self):
        columns = ["column_1"]
        expected = [3, 6, 8, 10]
        func = Add
        value = 1
        self.assert_result(func, self.df, columns, expected, value=value)

    def test_add_fixed_2(self):
        columns = ["column_1"]
        expected = [3, 6, 8, 10]
        func = Add
        value = "1"
        self.assert_result(func, self.df, columns, expected, value=value)

    def test_add_columnwise(self):
        """
        Test #277
        "Mathematics function should optionally operate column-wise"
        """
        columns = ["column_1"]
        expected = [2 + 5 + 7 + 9] * len(self.df)
        func = Add
        self.assert_result(func, self.df, columns, expected)

    def test_sub(self):
        columns = ["column_1", "column_2"]
        expected = [-1, 2, 4, 6]
        func = Sub
        self.assert_result(func, self.df, columns, expected)

    def test_sub_fixed(self):
        columns = ["column_1"]
        expected = [1, 4, 6, 8]
        func = Sub
        value = 1
        self.assert_result(func, self.df, columns, expected, value=value)

    def test_mul(self):
        columns = ["column_1", "column_2"]
        expected = [6, 15, 21, 27]
        func = Mul
        self.assert_result(func, self.df, columns, expected)

    def test_mul_fixed(self):
        columns = ["column_1"]
        expected = [4, 10, 14, 18]
        func = Mul
        value = 2
        self.assert_result(func, self.df, columns, expected, value=value)

    def test_div_zero(self):
        columns = ["column_1", "column_3"]
        expected = [1, pd.NA, pd.NA, np.inf]
        func = Div
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assert_result(func, self.df, columns, expected)

    def test_log2(self):
        columns = ["column_1", "column_2"]
        expected = [[np.log2(x) for x in self.df[columns[0]]],
                    [np.log2(x) for x in self.df[columns[1]]]]
        base = "Log2"
        func = Log(columns=columns, base=base)
        val = FunctionList([func]).lapply(self.df, session=None)
        self.assertListEqual(
            val.iloc[:, -2].values.ravel().tolist(), expected[0])
        self.assertListEqual(
            val.iloc[:, -1].values.ravel().tolist(), expected[1])

    def test_log2_columnwise(self):
        columns = ["column_1"]
        expected = [np.log2(x) for x in self.df.column_1]
        func = Log
        base = "Log2"
        self.assert_result(func, self.df, columns, expected, base=base)

    def test_log10_columnwise(self):
        columns = ["column_1"]
        expected = [np.log10(x) for x in self.df.column_1]
        func = Log
        base = "Log10"
        self.assert_result(func, self.df, columns, expected, base=base)

    def test_logN_columnwise(self):
        columns = ["column_1"]
        expected = [np.log(x) for x in self.df.column_1]
        func = Log
        base = "LogN"
        self.assert_result(func, self.df, columns, expected, base=base)

    def test_max(self):
        columns = ["column_1", "column_2"]
        expected = [3, 5, 7, 9]
        func = Max
        self.assert_result(func, self.df, columns, expected)

    def test_max_columnwise(self):
        """
        Test #277
        "Mathematics function should optionally operate column-wise"
        """
        columns = ["column_1"]
        expected = [9, 9, 9, 9]
        func = Max
        self.assert_result(func, self.df, columns, expected)

    def test_min(self):
        columns = ["column_1", "column_2"]
        expected = [2, 3, 3, 3]
        func = Min
        self.assert_result(func, self.df, columns, expected)

    def test_min_columnwise(self):
        """
        Test #277
        "Mathematics function should optionally operate column-wise"
        """
        columns = ["column_1"]
        expected = [2, 2, 2, 2]
        func = Min
        self.assert_result(func, self.df, columns, expected)

    def test_mean(self):
        columns = ["column_1", "column_2"]
        expected = [np.mean((2, 3)),
                    np.mean((5, 3)),
                    np.mean((7, 3)),
                    np.mean((9, 3))]
        func = Mean
        self.assert_result(func, self.df, columns, expected)

    def test_mean_columnwise(self):
        """
        Test #277
        "Mathematics function should optionally operate column-wise"
        """
        columns = ["column_1"]
        expected = [(2 + 5 + 7 + 9) / 4] * len(self.df)
        func = Mean
        self.assert_result(func, self.df, columns, expected)

    def test_median(self):
        columns = ["column_1", "column_2"]
        expected = [np.median((2, 3)),
                    np.median((5, 3)),
                    np.median((7, 3)),
                    np.median((9, 3))]
        func = Median
        self.assert_result(func, self.df, columns, expected)

    def test_median_columnwise(self):
        """
        Test #277
        "Mathematics function should optionally operate column-wise"
        """
        columns = ["column_1"]
        expected = [6] * len(self.df)
        func = Median
        self.assert_result(func, self.df, columns, expected)

    def test_sd(self):
        columns = ["column_1", "column_2"]
        expected = [np.std((2, 3)),
                    np.std((5, 3)),
                    np.std((7, 3)),
                    np.std((9, 3))]
        func = StandardDeviation
        self.assert_result(func, self.df, columns, expected)

    def test_sd_columnwise(self):
        """
        Test #277
        "Mathematics function should optionally operate column-wise"
        """
        columns = ["column_1"]
        expected = [np.std((2, 5, 7, 9))] * len(self.df)
        func = StandardDeviation
        self.assert_result(func, self.df, columns, expected)

    def test_iqr(self):
        columns = ["column_1", "column_2"]
        expected = [0.5, 1, 2, 3]
        func = InterquartileRange
        self.assert_result(func, self.df, columns, expected)

    def test_iqr_columnwise(self):
        """
        Test #277
        "Mathematics function should optionally operate column-wise"
        """
        columns = ["column_1"]
        expected = [3.25] * 4
        func = InterquartileRange
        self.assert_result(func, self.df, columns, expected)

    def test_percentile(self):
        columns = ["column_1", "column_2"]
        expected = [2.5, 4, 5, 6]
        func = Percentile
        value = 50
        self.assert_result(func, self.df, columns, expected, value=value)

    def test_percentile_columnwise(self):
        columns = ["column_1"]
        expected = [6] * 4
        func = Percentile
        value = 50
        self.assert_result(func, self.df, columns, expected, value=value)


class TestLogicalFunctions(FncTestCase):
    def setUp(self):
        super(TestLogicalFunctions, self).setUp()

        self.df = pd.DataFrame(
            {"column_1": [1, 1, 2, 2, 5, 5],
             "column_2": [1, 1, 3, 3, 3, 3],
             "column_3": [1, pd.NA, 2, pd.NA, 3, pd.NA],
             "column_4": [0, 1, 0, 1, 0, 1],
             "column_5": [2, 2, 2, 2, 0, 0],
             "column_6": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
             "str_1": ["aaa", "bbb", "ccc", "ddd", "eee", "fff"],
             "str_2": ["ccc", "ccc", "ccc", "ddd", "ddd", "ddd"],
             "str_3": ["aaa", pd.NA, "ccc", pd.NA, "eee", pd.NA],
             "str_4": ["", "X"] * 3,
             })

    def assert_result(self, func_class, df, columns, expected, value=None,
                      **kwargs):
        func = func_class(columns=columns, value=value, **kwargs)
        result = FunctionList([func]).lapply(df, session=None)
        val = result[func.get_id()]
        pd.testing.assert_series_equal(
            result[func.get_id()],
            pd.Series(expected),
            check_names=False,
            check_dtype=False)

    def test_equal(self):
        columns = ["column_1", "column_2"]
        expected = [True, True, False, False, False, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected)

    def test_equal_value(self):
        columns = ["column_1"]
        expected = [False, False, True, True, False, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected, value=2)

    def test_equal_one_has_na(self):
        columns = ["column_1", "column_3"]
        expected = [True, False, True, False, False, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected)

    def test_equal_both_have_na1(self):
        columns = ["column_3", "column_3"]
        expected = [True, False, True, False, True, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected)

    def test_equal_both_have_na2(self):
        columns = ["column_6", "column_3"]
        expected = [False, False, False, False, False, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected)

    def test_equal_str(self):
        columns = ["str_1", "str_2"]
        expected = [False, False, True, True, False, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected)

    def test_equal_str_value(self):
        columns = ["str_1"]
        expected = [False, False, True, False, False, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected, value="ccc")

    def test_equal_str_none(self):
        columns = ["str_1", "str_3"]
        expected = [True, False, True, False, True, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected)

    def test_value_conversion_1(self):
        columns = ["column_1"]
        expected = [False, False, True, True, False, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected, value="2")

    def test_value_conversion_2(self):
        columns = ["column_1"]
        expected = [False, False, True, True, False, False]
        func = Equal
        self.assert_result(func, self.df, columns, expected, value="2.0")

    def test_notqual(self):
        columns = ["column_1", "column_2"]
        expected = [False, False, True, True, True, True]
        func = NotEqual
        self.assert_result(func, self.df, columns, expected)

    def test_notequal_value(self):
        columns = ["column_1"]
        expected = [True, True, False, False, True, True]
        func = NotEqual
        self.assert_result(func, self.df, columns, expected, value=2)

    def test_notequal_none(self):
        columns = ["column_1", "column_3"]
        expected = [False, True, False, True, True, True]
        func = NotEqual
        self.assert_result(func, self.df, columns, expected)

    def test_notequal_str(self):
        columns = ["str_1", "str_2"]
        expected = [True, True, False, False, True, True]
        func = NotEqual
        self.assert_result(func, self.df, columns, expected)

    def test_notequal_str_value(self):
        columns = ["str_1"]
        expected = [True, True, False, True, True, True]
        func = NotEqual
        self.assert_result(func, self.df, columns, expected, value="ccc")

    def test_notequal_str_none(self):
        columns = ["str_1", "str_3"]
        expected = [False, True, False, True, False, True]
        func = NotEqual
        self.assert_result(func, self.df, columns, expected)

    def test_greaterthan(self):
        columns = ["column_1", "column_2"]
        expected = [False, False, False, False, True, True]
        func = GreaterThan
        self.assert_result(func, self.df, columns, expected)

    def test_greaterthan_value(self):
        columns = ["column_1"]
        expected = [False, False, False, False, True, True]
        func = GreaterThan
        self.assert_result(func, self.df, columns, expected, value=2)

    def test_greaterthan_str(self):
        columns = ["str_1", "str_2"]
        expected = [False, False, False, False, True, True]
        func = GreaterThan
        self.assert_result(func, self.df, columns, expected)

    def test_greaterthan_str_value(self):
        columns = ["str_1"]
        expected = [False, False, True, True, True, True]
        func = GreaterThan
        self.assert_result(func, self.df, columns, expected, value="bbb")

    def test_greaterequal(self):
        columns = ["column_1", "column_2"]
        expected = [True, True, False, False, True, True]
        func = GreaterEqual
        self.assert_result(func, self.df, columns, expected)

    def test_greaterequal_value(self):
        columns = ["column_1"]
        expected = [False, False, True, True, True, True]
        func = GreaterEqual
        self.assert_result(func, self.df, columns, expected, value=2)

    def test_greaterequal_str(self):
        columns = ["str_1", "str_2"]
        expected = [False, False, True, True, True, True]
        func = GreaterEqual
        self.assert_result(func, self.df, columns, expected)

    def test_greaterequal_str_value(self):
        columns = ["str_1"]
        expected = [False, True, True, True, True, True]
        func = GreaterEqual
        self.assert_result(func, self.df, columns, expected, value="bbb")

    def test_lessthan(self):
        columns = ["column_1", "column_2"]
        expected = [False, False, True, True, False, False]
        func = LessThan
        self.assert_result(func, self.df, columns, expected)

    def test_lessthan_value(self):
        columns = ["column_1"]
        expected = [True, True, False, False, False, False]
        func = LessThan
        self.assert_result(func, self.df, columns, expected, value=2)

    def test_lessthan_str(self):
        columns = ["str_1", "str_2"]
        expected = [True, True, False, False, False, False]
        func = LessThan
        self.assert_result(func, self.df, columns, expected)

    def test_lessthan_str_value(self):
        columns = ["str_1"]
        expected = [True, False, False, False, False, False]
        func = LessThan
        self.assert_result(func, self.df, columns, expected, value="bbb")

    def test_lessequal(self):
        columns = ["column_1", "column_2"]
        expected = [True, True, True, True, False, False]
        func = LessEqual
        self.assert_result(func, self.df, columns, expected)

    def test_lessequal_value(self):
        columns = ["column_1"]
        expected = [True, True, True, True, False, False]
        func = LessEqual
        self.assert_result(func, self.df, columns, expected, value=2)

    def test_lessequal_str(self):
        columns = ["str_1", "str_2"]
        expected = [True, True, True, True, False, False]
        func = LessEqual
        self.assert_result(func, self.df, columns, expected)

    def test_lessequal_str_value(self):
        columns = ["str_1"]
        expected = [True, True, False, False, False, False]
        func = LessEqual
        self.assert_result(func, self.df, columns, expected, value="bbb")

    def test_and(self):
        columns = ["column_1", "column_4"]
        expected = [False, True, False, True, False, True]
        func = And
        self.assert_result(func, self.df, columns, expected)

    def test_and_value_with_NA(self):
        columns = ["column_3"]
        expected = [True, pd.NA, True, pd.NA, True, pd.NA]
        func = And
        self.assert_result(func, self.df, columns, expected, value=True)

    def test_or(self):
        columns = ["column_4", "column_5"]
        expected = [True, True, True, True, False, True]
        func = Or
        self.assert_result(func, self.df, columns, expected)

    def test_xor(self):
        columns = ["column_4", "column_5"]
        expected = [True, False, True, False, False, True]
        func = Xor
        self.assert_result(func, self.df, columns, expected)

    def test_if(self):
        columns = ["column_4"]
        expected = ["zero", "one", "zero", "one", "zero", "one"]
        func = If
        self.assert_result(func, self.df, columns, expected,
                           value1="one", value2="zero")

    def test_if_with_NA(self):
        columns = ["column_3"]
        expected = ["one", pd.NA, "one", pd.NA, "one", pd.NA]
        func = If
        self.assert_result(func, self.df, columns, expected,
                           value1="one", value2="zero")

    def test_missing(self):
        columns = ["str_3", "str_4"]
        val = Missing(columns=columns).evaluate(self.df)
        pd.testing.assert_series_equal(
            val["str_3"],
            pd.Series([False, True] * 3),
            check_names=False)
        pd.testing.assert_series_equal(
            val["str_4"],
            pd.Series([False, False] * 3),
            check_names=False)

    def test_empty(self):
        columns = ["str_3", "str_4"]
        val = Empty(columns=columns).evaluate(self.df)
        pd.testing.assert_series_equal(
            val["str_3"],
            pd.Series([False, True] * 3),
            check_names=False)
        pd.testing.assert_series_equal(
            val["str_4"],
            pd.Series([True, False] * 3),
            check_names=False)


class TestConversionFunctions(FncTestCase):
    def assert_result(self, func_class, df, columns, expected, value=None,
                      **kwargs):
        func = func_class(columns=columns, value=value, **kwargs)
        result = FunctionList([func]).lapply(df, session=None)
        pd.testing.assert_series_equal(result[func.get_id()],
                                       expected,
                                       check_names=False,
                                       check_dtype=False)

    def test_str_to_num(self):
        df = pd.DataFrame({"str1": list("123"),
                           "str2": list("abc"),
                           "str3": list("1bc")})

        expected1 = pd.Series([1, 2, 3])
        expected2 = pd.Series([pd.NA, pd.NA, pd.NA])
        expected3 = pd.Series([1, pd.NA, pd.NA])

        self.assert_result(ToNumeric, df, ["str1"], expected1)
        self.assert_result(ToNumeric, df, ["str2"], expected2)
        self.assert_result(ToNumeric, df, ["str3"], expected3)

    def test_num_to_str(self):
        df = pd.DataFrame({"num1": [1, 2, 3],
                           "num2": [1, 2, pd.NA],
                           "num3": [1.5, 2.5, 3.5]})

        expected1 = pd.Series(["1", "2", "3"])
        expected2 = pd.Series(["1", "2", pd.NA])
        expected3 = pd.Series(["1.5", "2.5", "3.5"])

        self.assert_result(ToCategory, df, ["num1"], expected1)
        self.assert_result(ToCategory, df, ["num2"], expected2)
        self.assert_result(ToCategory, df, ["num3"], expected3)


provided_tests = [
    TestFrequencyFunctions,
    TestStringFunctions,
    TestMathFunctions,
    TestLogicalFunctions,
    TestModuleFunctions,
    TestConversionFunctions,
    TestProportionFunctions,
]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

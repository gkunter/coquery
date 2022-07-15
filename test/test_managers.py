# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import warnings

import pandas as pd
import pandas.testing as pdt
import numpy as np

from coquery.coquery import options
from coquery.session import Session
from coquery.defines import (QUERY_MODE_TOKENS, CONTEXT_NONE,
                             DEFAULT_CONFIGURATION, ROW_NAMES)
from coquery.connections import SQLiteConnection
from coquery.corpus import BaseResource
from coquery.managers import Manager, ContingencyTable, Group, Summary
from coquery.functions import Freq, Tokens
from test.testcase import CoqTestCase, run_tests


class ManagerResource(BaseResource):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    db_name = "MockCorpus"
    query_item_word = "word_label"


class TestMeta(CoqTestCase):
    df = pd.DataFrame(
        {"coq_word_label_1": list("aaaaaabbbb"),
         "coq_word_label_2": list("yyyyxxxxxx"),
         "coq_word_label_3": list("ababababab"),
         "coquery_invisible_corpus_id": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
         "coquery_invisible_number_of_tokens": [1] * 10})

    resource = ManagerResource()

    def setUp(self):
        options.cfg = argparse.Namespace()
        options.cfg.corpus = None
        options.cfg.MODE = QUERY_MODE_TOKENS
        options.cfg.stopword_list = []
        options.cfg.context_mode = CONTEXT_NONE
        options.cfg.drop_on_na = True
        options.cfg.drop_duplicates = True
        options.cfg.benchmark = False
        options.cfg.verbose = False
        options.cfg.summary_group = [Summary("summary")]
        default = SQLiteConnection(DEFAULT_CONFIGURATION)
        options.cfg.current_connection = default
        options.cfg.sample_matches = False

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.Session = Session()

        self.Session.Resource = ManagerResource()


class TestManager(TestMeta):
    def setUp(self):
        super().setUp()
        self.manager = Manager()

    def test_manager_basic_1(self):
        df = self.manager.process(self.df, session=self.Session)
        np.testing.assert_array_equal(df.values, self.df.values)

    def test_manager_arrange_groups_1(self):
        group = Group("Test", ["coq_word_label_2"])
        self.manager.set_groups([group])
        df = self.manager.process(self.df, session=self.Session)

        self.assertListEqual(
            list(df["coq_word_label_2"].values), list("xxxxxxyyyy"))
        self.assertListEqual(
            list(df["coquery_invisible_corpus_id"].values),
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_manager_arrange_groups_2(self):
        group = Group("Test", ["coq_word_label_1"])
        self.manager.set_groups([group])
        df = self.manager.process(self.df, session=self.Session)

        self.assertListEqual(
            list(df["coq_word_label_1"].values), list("aaaaaabbbb"))
        self.assertListEqual(
            list(df["coquery_invisible_corpus_id"].values),
            [5, 6, 7, 8, 9, 10, 1, 2, 3, 4])

    def test_manager_arrange_groups_3(self):
        sorted_df = pd.DataFrame(
            {"a": list("aabbbbaaaa"),
             "b": list("xxxxxxyyyy"),
             "c": list("bababababa"),
             "d": [5, 6, 1, 2, 3, 4, 7, 8, 9, 10],
             "e": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]})
        group = Group("Test", ["coq_word_label_2", "coq_word_label_1"])
        self.manager.set_groups([group])
        df = self.manager.process(self.df, session=self.Session)

        np.testing.assert_array_equal(df.values, sorted_df.values)

    def test_manager_mutate_groups_tokens_1(self):
        group = Group("Test",
                      ["coq_word_label_1"],
                      functions=[(Tokens, [])])
        func = group.get_functions()[0]
        self.manager.set_groups([group])
        df = self.manager.process(self.df, session=self.Session)

        self.assertListEqual(
            list(df[func.get_id()].values),
            [6] * 6 + [4] * 4)

    def test_manager_mutate_groups_freq_2(self):
        group = Group("Test",
                      ["coq_word_label_1", "coq_word_label_2"],
                      functions=[(Freq,
                                  ["coq_word_label_1", "coq_word_label_2"])])
        func = group.get_functions()[0]
        self.manager.set_groups([group])

        df = self.manager.process(self.df, session=self.Session)
        self.assertListEqual(
            list(df[func.get_id()].values),
            [2] * 2 + [4] * 4 + [4] * 4)

    def test_manager_mutate_groups_freq_3(self):
        group = Group("Test",
                      ["coq_word_label_1"],
                      functions=[(Freq,
                                  ["coq_word_label_2", "coq_word_label_3"])])
        func = group.get_functions()[0]
        self.manager.set_groups([group])

        df = self.manager.process(self.df, session=self.Session)
        self.assertListEqual(
            list(df[func.get_id()].values),
            [1] + [1] + [2] * 2 + [2] * 2 + [2] * 2 + [2] * 2)


class TestContingency(TestMeta):
    def setUp(self):
        def _get_manager(*args, **kwargs):
            return self
        super().setUp()
        self.df["coquery_invisible_origin_id"] = [1, 1, 1, 2, 2, 2, 3, 3, 3, 3]
        self.manager = ContingencyTable()
        options.cfg.column_names = []
        self.Session.get_manager = _get_manager
        self.Session.translate_header = lambda x: x

    # def test_get_cat_cols(self):
    #     val = self.manager._get_cat_cols(self.df, self.Session)
    #     target = ["coq_word_label_1", "coq_word_label_2", "coq_word_label_3"]
    #     self.assertCountEqual(val, target)
    #
    # def test_get_num_cols(self):
    #     val = self.manager._get_num_cols(self.df, self.Session)
    #     target = ["coquery_invisible_corpus_id",
    #               "coquery_invisible_number_of_tokens",
    #               "coquery_invisible_origin_id"]
    #     self.assertCountEqual(val, target)
    #
    # def test_get_agg_fnc(self):
    #     val = self.manager._get_agg_fnc(self.df, self.Session)
    #     target = {k: self.manager._get_first
    #               for k in self.manager._get_num_cols(self.df, self.Session)}
    #     self.assertDictEqual(val, target)

    # def test_get_pivot_table(self):
    #     val = self.manager._get_pivot_table(self.df, self.Session)
    #     print(val)

    def test_process_1(self):
        val = self.manager.process(self.df, session=self.Session)
        row_total = pd.Series([ROW_NAMES["row_total"], "", 5, 5, 10])
        col_total = pd.Series([2, 4, 4, 10])
        pdt.assert_series_equal(val.iloc[-1].reset_index(drop=True),
                                row_total.reset_index(drop=True),
                                check_names=False,
                                check_series_type=False)
        pdt.assert_series_equal(val.iloc[:, -1],
                                col_total,
                                check_names=False,
                                check_series_type=False)

    def test_process_2(self):
        columns = ["coq_word_label_1", "coq_word_label_2"]
        val = self.manager.process(self.df[columns], session=self.Session)
        row_total = pd.Series([ROW_NAMES["row_total"], 6, 4, 10])
        col_total = pd.Series([6, 4, 10])
        pdt.assert_series_equal(val.iloc[-1].reset_index(drop=True),
                                row_total.reset_index(drop=True),
                                check_names=False)
        pdt.assert_series_equal(val.iloc[:, -1], col_total,
                                check_names=False)

    def test_process_3(self):
        columns = ["coq_word_label_1"]
        val = self.manager.process(self.df[columns], session=self.Session)
        row_total = pd.Series([ROW_NAMES["row_total"], 10])
        col_total = pd.Series([6, 4, 10])
        pdt.assert_series_equal(val.iloc[-1].reset_index(drop=True),
                                row_total.reset_index(drop=True),
                                check_names=False)
        pdt.assert_series_equal(val.iloc[:, -1], col_total,
                                check_names=False)

    def test_process_4(self):
        columns = []
        val = self.manager.process(self.df[columns], session=self.Session)
        row_total = pd.Series([10])
        col_total = pd.Series([10])
        pdt.assert_series_equal(val.iloc[-1].reset_index(drop=True),
                                row_total.reset_index(drop=True),
                                check_names=False)
        pdt.assert_series_equal(val.iloc[:, -1], col_total,
                                check_names=False)




provided_tests = [
    TestManager,
    TestContingency,
    ]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

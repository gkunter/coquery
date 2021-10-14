# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import warnings

import pandas as pd

from coquery.coquery import options
from coquery.session import Session
from coquery.defines import (QUERY_MODE_TOKENS, CONTEXT_NONE,
                             DEFAULT_CONFIGURATION)
from coquery.connections import SQLiteConnection
from coquery.corpus import BaseResource
from coquery.managers import Manager, Group, Summary
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


class TestManager(CoqTestCase):
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

        self.manager = Manager()

    def test_manager_basic_1(self):
        df = self.manager.process(self.df, session=self.Session)
        pd.np.testing.assert_array_equal(df.values, self.df.values)

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

        pd.np.testing.assert_array_equal(df.values, sorted_df.values)

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


provided_tests = [TestManager]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

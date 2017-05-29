# -*- coding: utf-8 -*-

from __future__ import print_function
import unittest
import argparse

import pandas as pd

from coquery.coquery import options
from coquery.queries import TokenQuery
from coquery.session import Session
from coquery.defines import QUERY_MODE_TOKENS

class TestQueries(unittest.TestCase):
    def setUp(self):
        options.cfg = argparse.Namespace()
        options.cfg.corpus = None
        options.cfg.MODE = QUERY_MODE_TOKENS
        options.cfg.current_server = "MockConnection"
        options.cfg.align_quantified = True
        options.cfg.selected_features = ["word_label"]

        self.session = Session()
        self.df = pd.DataFrame(
            {"coq_word_label_1": list("aaaaaabbbb"),
             "coq_word_label_2": list("aaaaaabbbb"),
             "coq_word_label_3": list("aaaaaabbbb"),
             "coquery_invisible_corpus_id": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]})

    def test_max_tokens_1(self):
        query = TokenQuery("item1 item2 item3", self.session)
        self.assertEqual(query.get_max_tokens(), 3)

    def test_max_tokens_2(self):
        query = TokenQuery("item1{0,3} item2{1,3} item3{2,3}", self.session)
        self.assertEqual(query.get_max_tokens(), 9)

    def test_get_token_numbering_1(self):
        query = TokenQuery("item1 item2 item3", self.session)
        self.assertEqual(query.get_token_numbering(0), "1")
        self.assertEqual(query.get_token_numbering(1), "2")
        self.assertEqual(query.get_token_numbering(2), "3")

    def test_get_token_numbering_2(self):
        query = TokenQuery("item1{0,3} item2{1,3} item3{2,3}", self.session)
        self.assertEqual(query.get_token_numbering(0), "1.1")
        self.assertEqual(query.get_token_numbering(1), "1.2")
        self.assertEqual(query.get_token_numbering(2), "1.3")
        self.assertEqual(query.get_token_numbering(3), "2.1")
        self.assertEqual(query.get_token_numbering(4), "2.2")
        self.assertEqual(query.get_token_numbering(5), "2.3")
        self.assertEqual(query.get_token_numbering(6), "3.1")
        self.assertEqual(query.get_token_numbering(7), "3.2")
        self.assertEqual(query.get_token_numbering(8), "3.3")

    def test_insert_static_data_1(self):
        query = TokenQuery("item1{0,3} item2{1,3} item3{2,3}", self.session)
        query._query_id = 999

        df = query.insert_static_data(self.df)
        self.assertListEqual(
            df.columns.tolist(),
            ["coq_word_label_1", "coq_word_label_2", "coq_word_label_3",
             "coquery_invisible_corpus_id",
             "coquery_dummy",
             "coquery_invisible_query_id"])
        self.assertListEqual(
            df.coquery_invisible_query_id.tolist(),
            [999] * len(df))
        self.assertListEqual(
            df.coquery_dummy.tolist(),
            [0] * len(df))

    def test_insert_static_data_2(self):
        query = TokenQuery("item1{0,3} item2{1,3} item3{2,3}", self.session)
        query._query_id = 999

        df = query.insert_static_data(self.df)
        self.assertListEqual(
            df.columns.tolist(),
            ["coq_word_label_1", "coq_word_label_2", "coq_word_label_3",
             "coquery_invisible_corpus_id",
             "coquery_dummy",
             "coquery_invisible_query_id"])

    def test_insert_static_data_3(self):
        query_string = "item1 item2 item3"
        query = TokenQuery(query_string, self.session)
        query._query_id = 999

        options.cfg.selected_features = ["word_label", "coquery_query_string"]

        df = query.insert_static_data(self.df)
        self.assertListEqual(
            sorted(df.columns.tolist()),
            sorted(["coq_word_label_1", "coq_word_label_2", "coq_word_label_3",
                    "coquery_invisible_corpus_id",
                    "coquery_dummy", "coquery_invisible_query_id",
                    "coquery_query_string"]))

        self.assertListEqual(
            df.coquery_query_string.tolist(),
            [query_string] * len(df))

    def test_insert_static_data_4(self):
        query_string = "item1 item2 item3"
        query = TokenQuery(query_string, self.session)
        query._query_id = 999

        options.cfg.selected_features = ["coquery_query_token"]

        df = query.insert_static_data(self.df)

        self.assertListEqual(
            sorted(df.columns.tolist()),
            sorted(["coq_word_label_1", "coq_word_label_2", "coq_word_label_3",
                    "coquery_invisible_corpus_id",
                    "coquery_dummy", "coquery_invisible_query_id",
                    "coquery_query_token_1", "coquery_query_token_2", "coquery_query_token_3"]))

        self.assertListEqual(
            df.coquery_query_token_1.tolist(), ["item1"] * len(df))

        self.assertListEqual(
            df.coquery_query_token_2.tolist(), ["item2"] * len(df))

        self.assertListEqual(
            df.coquery_query_token_3.tolist(), ["item3"] * len(df))


def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestQueries)])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

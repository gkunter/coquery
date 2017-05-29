# -*- coding: utf-8 -*-

from __future__ import print_function
import unittest
import sys

from .mockmodule import setup_module, MockOptions

setup_module("sqlalchemy")

from coquery.corpus import LexiconClass, SQLResource
from coquery.coquery import options
from coquery.defines import *
from coquery.queries import TokenQuery
from coquery.tokens import COCAToken
import coquery.links

import argparse

class Resource(SQLResource):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "FileId"
    corpus_starttime = "Start"
    corpus_endtime = "End"
    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_pos = "POS"
    word_lemma_id = "LemmaId"
    word_transcript = "Transcript"
    lemma_table = "Lemmas"
    lemma_id = "LemmaId"
    lemma_label = "Lemma"
    lemma_deep_id = "DeepId"
    deep_table = "Deep"
    deep_id = "DeepId"
    source_table = "Files"
    source_id = "FileId"
    source_label = "Title"
    segment_id = "SegmentId"
    segment_table = "Segments"
    segment_starttime = "SegStart"
    segment_endtime = "SegEnd"
    segment_origin_id = "SegmentOrigin"

    db_name = "MockCorpus"
    name = "Corp"
    query_item_word = "word_label"
    query_item_pos = "word_pos"
    query_item_lemma = "lemma_label"
    query_item_transcript = "word_transcript"

    annotations = {"segment": "word"}


class MockBuckeye(SQLResource):
    """
    MockBuckeye simulates a super-flat corpus, i.e. one in which there is not
    even a Lexicon table.
    """
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word = "Word"
    corpus_file_id = "FileId"
    file_table = "Files"
    file_id = "FileId",
    file_path = "Path"
    name = "SuperFlat"

    query_item_word = "corpus_word"


class FlatResource(SQLResource):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "FileId"
    corpus_starttime = "Start"
    corpus_endtime = "End"
    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_pos = "POS"
    word_lemma = "Lemma"

    db_name = "MockFlat"
    name = "Flat"
    query_item_word = "word_label"
    query_item_lemma = "word_lemma"
    query_item_pos = "word_pos"


class ExternalCorpus(SQLResource):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_data = "ExtData"
    db_name = "extcorp"
    name = "ExternalCorpus"


class TestCorpus(unittest.TestCase):
    resource = Resource
    flat_resource = FlatResource

    @staticmethod
    def pos_check_function(l):
        return [x.lower().startswith(("n", "v")) for x in l]

    def setUp(self):
        self.maxDiff = None
        options.cfg = argparse.Namespace()
        options.cfg.number_of_tokens = 0
        options.cfg.limit_matches = False
        options.cfg.regexp = False
        options.cfg.query_case_sensitive = False
        options.get_configuration_type = lambda: SQL_MYSQL
        self.Session = MockOptions()
        self.Session.Resource = self.resource
        self.Session.Lexicon = None
        self.Session.Corpus = None

        COCAToken.set_pos_check_function(self.pos_check_function)

        #options.cfg.external_links = [(Link(), "word_label")]

    # TEST TABLE PATH

    #def test_table_path_deep(self):
        #l = ["word", "deep"]
        #path = self.resource.get_table_path(*l)
        #self.assertListEqual(path, ["word", "lemma", "deep"])

    #def test_table_path_non_existing(self):
        #l = ["lemma", "source"]
        #path = self.resource.get_table_path(*l)
        #self.assertEqual(path, None)

    @staticmethod
    def simple(s):
        s = s.replace("\n", " ")
        while "  " in s:
            s = s.replace("  ", " ")
        return s.strip()

    def test_get_required_tables_1(self):
        x = self.resource.get_required_tables("corpus", [], {})
        root, l = x
        self.assertEqual(root, "corpus")
        self.assertListEqual(l, [])

    def test_get_required_tables_2(self):
        x = self.resource.get_required_tables("corpus", ["word_label"], {})
        root, l = x
        self.assertEqual(root, "corpus")
        self.assertListEqual(l, [("word", [])])

    def test_get_required_tables_3(self):
        root, l = self.resource.get_required_tables("corpus", ["word_label", "source_label"], {})
        self.assertEqual(root, "corpus")
        self.assertListEqual(l, [("source", []), ("word", [])])

    def test_get_required_tables_3a(self):
        root, l = self.resource.get_required_tables("corpus", ["source_label", "word_label"], {})
        self.assertEqual(root, "corpus")
        self.assertListEqual(l, [("source", []), ("word", [])])

    def test_get_required_tables_4(self):
        root, l = self.resource.get_required_tables("corpus", ["lemma_label", "word_label", "source_label"], {})
        self.assertListEqual(l, [("source", []), ("word", [("lemma", [])])])

    def test_get_required_tables_5(self):
        root, l = self.resource.get_required_tables("corpus", ["word_label", "lemma_label"], {})
        self.assertEqual(l, [("word", [("lemma", [])])])

    def test_get_required_tables_6(self):
        root, l = self.resource.get_required_tables("corpus", ["lemma_label"], {})
        self.assertEqual(l, [("word", [("lemma", [])])])

    # TEST CORPUS JOINS

    def test_corpus_joins_one_item(self):
        query = TokenQuery("*", self.Session)
        l = self.resource.get_corpus_joins(query.query_list[0])
        self.assertListEqual(l, ["FROM       Corpus AS COQ_CORPUS_1"])

    def test_corpus_joins_three_items(self):
        query = TokenQuery("* * *", self.Session)
        l = self.resource.get_corpus_joins(query.query_list[0])
        self.assertListEqual(l, ["FROM       Corpus AS COQ_CORPUS_1",
                                 "INNER JOIN Corpus AS COQ_CORPUS_2 ON COQ_CORPUS_2.ID = COQ_CORPUS_1.ID + 1",
                                 "INNER JOIN Corpus AS COQ_CORPUS_3 ON COQ_CORPUS_3.ID = COQ_CORPUS_1.ID + 2"])

    def test_corpus_joins_optimized_order_1(self):
        """
        Three query items, join order optimized by query item complexity.
        """
        query = TokenQuery("* *ier [n*]", self.Session)
        l = self.resource.get_corpus_joins(query.query_list[0])
        self.maxDiff = None
        self.assertListEqual(l, ["FROM       Corpus AS COQ_CORPUS_2",
                                 "INNER JOIN Corpus AS COQ_CORPUS_3 ON COQ_CORPUS_3.ID = COQ_CORPUS_2.ID + 1",
                                 "INNER JOIN Corpus AS COQ_CORPUS_1 ON COQ_CORPUS_1.ID = COQ_CORPUS_2.ID - 1"])

    def test_corpus_joins_optimized_order_2(self):
        """
        Three query items, join order optimized by query item complexity.
        POS tags are penalized.
        """
        query = TokenQuery("* d* [n*]", self.Session)
        l = self.resource.get_corpus_joins(query.query_list[0])
        self.maxDiff = None
        self.assertListEqual(l, ["FROM       Corpus AS COQ_CORPUS_2",
                                 "INNER JOIN Corpus AS COQ_CORPUS_3 ON COQ_CORPUS_3.ID = COQ_CORPUS_2.ID + 1",
                                 "INNER JOIN Corpus AS COQ_CORPUS_1 ON COQ_CORPUS_1.ID = COQ_CORPUS_2.ID - 1"])

    def test_quantified_query_string_1(self):
        query = TokenQuery("* b*{1,2} *", self.Session)
        self.assertTrue(len(query.query_list) == 2)

        l = self.resource.get_corpus_joins(query.query_list[0])
        self.assertListEqual(l,
            ["FROM       Corpus AS COQ_CORPUS_2",
             "INNER JOIN Corpus AS COQ_CORPUS_1 ON COQ_CORPUS_1.ID = COQ_CORPUS_2.ID - 1",
             "INNER JOIN Corpus AS COQ_CORPUS_4 ON COQ_CORPUS_4.ID = COQ_CORPUS_2.ID + 1"])

        l = self.resource.get_corpus_joins(query.query_list[1])
        self.assertListEqual(l,
            ["FROM       Corpus AS COQ_CORPUS_2",
             "INNER JOIN Corpus AS COQ_CORPUS_3 ON COQ_CORPUS_3.ID = COQ_CORPUS_2.ID + 1",
             "INNER JOIN Corpus AS COQ_CORPUS_1 ON COQ_CORPUS_1.ID = COQ_CORPUS_2.ID - 1",
             "INNER JOIN Corpus AS COQ_CORPUS_4 ON COQ_CORPUS_4.ID = COQ_CORPUS_2.ID + 2"])

    def test_lemmatized_corpus_joins_1(self):
        S = "#abc.[n*]"
        query = TokenQuery(S, self.Session)
        l = self.resource.get_corpus_joins(query.query_list[0])
        self.assertListEqual(l, ["FROM       Corpus AS COQ_CORPUS_1"])

    ### FEATURE JOINS

    def test_feature_joins_1(self):
        l1, l2 = self.resource.get_feature_joins(0, ["word_label"])
        self.assertListEqual(l1, ["INNER JOIN Lexicon AS COQ_WORD_1 ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId"])
        self.assertListEqual(l2, [])

    def test_feature_joins_2(self):
        l1, l2 = self.resource.get_feature_joins(1, ["word_label"])
        self.assertListEqual(l1, ["INNER JOIN Lexicon AS COQ_WORD_2 ON COQ_WORD_2.WordId = COQ_CORPUS_2.WordId"])
        self.assertListEqual(l2, [])

    def test_feature_joins_3(self):
        l1, l2 = self.resource.get_feature_joins(0, ["word_label", "word_pos"])
        self.assertListEqual(l1, ["INNER JOIN Lexicon AS COQ_WORD_1 ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId"])
        self.assertListEqual(l2, [])

    def test_feature_joins_4(self):
        # direct and dependent selection
        l1, l2 = self.resource.get_feature_joins(0, ["word_label", "lemma_label"])
        self.assertListEqual(l1, ["INNER JOIN Lexicon AS COQ_WORD_1 ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId",
                                  "INNER JOIN Lemmas AS COQ_LEMMA_1 ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId"])
        self.assertListEqual(l2, [])

    def test_feature_joins_4a(self):
        # direct and dependent selection, inverse order
        l1a, l2a = self.resource.get_feature_joins(0, ["lemma_label", "word_label"])
        l1b, l2b = self.resource.get_feature_joins(0, ["word_label", "lemma_label"])
        self.assertListEqual(l1a, l1b)
        self.assertListEqual(l2a, l2b)

    def test_feature_joins_5(self):
        # dependent selection only; feature joins should be like
        # a join where all in-between tables are directly selected:
        l1a, l2a = self.resource.get_feature_joins(0, ["lemma_label"])
        l1b, l2b = self.resource.get_feature_joins(0, ["word_label", "lemma_label"])
        self.assertListEqual(l1a, l1b)
        self.assertListEqual(l2a, l2b)

    def test_feature_joins_6(self):
        # dependent selection, second order
        l1, l2 = self.resource.get_feature_joins(0, ["deep_label"])
        self.assertListEqual(l1, ["INNER JOIN Lexicon AS COQ_WORD_1 ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId",
                                  "INNER JOIN Lemmas AS COQ_LEMMA_1 ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId",
                                  "INNER JOIN Deep AS COQ_DEEP_1 ON COQ_DEEP_1.DeepId = COQ_LEMMA_1.DeepId"])
        self.assertListEqual(l2, [])

    def test_feature_joins_7a(self):
        # get a source feature (first query item)
        l1, l2 = self.resource.get_feature_joins(0, ["source_label"])
        self.assertListEqual(l1, ["INNER JOIN Files AS COQ_SOURCE_1 ON COQ_SOURCE_1.FileId = COQ_CORPUS_1.FileId"])
        self.assertListEqual(l2, [])

    def test_feature_joins_7b(self):
        # get a source feature (second query item)
        l1, l2 = self.resource.get_feature_joins(1, ["source_label"])
        self.assertListEqual(l1, [])
        self.assertListEqual(l2, [])

    #def test_feature_joins_8(self):
        ## words and segments
        #l1, l2 = self.resource.get_feature_joins(0, ["word_label", "segment_label"])
        #print(l1, l2)

    def test_get_token_conditions_1(self):
        token = COCAToken("a*")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d, {"word": ["COQ_WORD_1.Word LIKE 'a%'"]})

    def test_get_token_conditions_2(self):
        token = COCAToken("a*|b*.[n*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d, {"word": ["COQ_WORD_1.Word LIKE 'a%' OR COQ_WORD_1.Word LIKE 'b%'",
                                          "COQ_WORD_1.POS LIKE 'n%'"]})

    def test_get_token_conditions_3(self):
        token = COCAToken("[a*|b*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d, {"lemma": ["COQ_LEMMA_1.Lemma LIKE 'a%' OR COQ_LEMMA_1.Lemma LIKE 'b%'"]})

    def test_get_token_conditions_4(self):
        token = COCAToken("a*.[n*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d,
             {"word": ["COQ_WORD_1.Word LIKE 'a%'",
                       "COQ_WORD_1.POS LIKE 'n%'"]})

    def test_get_token_conditions_5(self):
        token = COCAToken("*'ll")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d,
             {"word": ["COQ_WORD_1.Word LIKE '%''ll'"]})

    def test_get_token_conditions_quote_char_1(self):
        token = COCAToken("'ll")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d,
             {"word": ["COQ_WORD_1.Word = '''ll'"]})

    def test_get_token_conditions_quote_char_2(self):
        token = COCAToken("'ll|ll")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d,
             {"word": ["COQ_WORD_1.Word IN ('''ll', 'll')"]})

    def test_token_condition_empty_1(self):
        token = COCAToken("*")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d, {})

    def test_token_condition_empty_2(self):
        token = COCAToken("*.[*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d, {})

    def test_token_condition_empty_3(self):
        token = COCAToken("*.[n*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d,
             {"word": ["COQ_WORD_1.POS LIKE 'n%'"]})

    def test_token_condition_empty_4(self):
        token = COCAToken("a*.[*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d,
             {"word": ["COQ_WORD_1.Word LIKE 'a%'"]})

    def test_token_conditions_lemmatized_flat_1(self):
        self.Session.Resource = self.flat_resource
        S = "#abc"
        token = COCAToken(S, self.Session)
        d = self.flat_resource.get_token_conditions(0, token)
        self.assertEqual(
            self.simple(d["word"][0]),
            self.simple("""
                COQ_WORD_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     WHERE (COQ_WORD_1.Word = 'abc'))"""))
        self.Session.Resource = self.resource

    def test_token_conditions_lemmatized_flat_pos(self):
        self.Session.Resource = self.flat_resource
        S = "#a*.[n*]"
        token = COCAToken(S, self.Session)
        d = self.flat_resource.get_token_conditions(0, token)
        self.assertEqual(
            self.simple(d["word"][0]),
            self.simple("""
                COQ_WORD_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     WHERE (COQ_WORD_1.Word LIKE 'a%') AND
                           (COQ_WORD_1.POS LIKE 'n%'))"""))
        self.Session.Resource = self.resource

    def test_token_conditions_lemmatized_deep_1(self):
        S = "#abc"
        token = COCAToken(S, self.Session)
        d = self.resource.get_token_conditions(0, token)
        self.assertEqual(
            self.simple(d["word"][0]),
            self.simple("""
                COQ_LEMMA_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     INNER JOIN Lemmas AS COQ_LEMMA_1
                             ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId
                     WHERE (COQ_WORD_1.Word = 'abc'))"""))

    def test_token_conditions_lemmatized_deep_2(self):
        S = "#/a*/"
        token = COCAToken(S, self.Session)
        d = self.resource.get_token_conditions(0, token)
        self.assertEqual(
            self.simple(d["word"][0]),
            self.simple("""
                COQ_LEMMA_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     INNER JOIN Lemmas AS COQ_LEMMA_1
                             ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId
                     WHERE (COQ_WORD_1.Transcript LIKE 'a%'))"""))

    ### SELECT COLUMNS

    def test_get_required_columns_1(self):
        query = TokenQuery("*", self.Session)
        s = self.resource.get_required_columns(query.query_list[0],
                                               ["word_label"])
        self.assertListEqual(s, ["COQ_WORD_1.Word AS coq_word_label_1",
                                 "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
                                 "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])

    def test_get_required_columns_2(self):
        query = TokenQuery("* *", self.Session)
        s = self.resource.get_required_columns(query.query_list[0],
                                               ["word_label"])
        self.assertListEqual(s, ["COQ_WORD_1.Word AS coq_word_label_1",
                                 "COQ_WORD_2.Word AS coq_word_label_2",
                                 "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
                                 "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])

    def test_get_required_columns_3(self):
        query = TokenQuery("* *", self.Session)
        l = self.resource.get_required_columns(query.query_list[0],
                                               ["source_label", "word_label", "word_pos"])
        self.assertListEqual(l, ["COQ_WORD_1.Word AS coq_word_label_1",
                                 "COQ_WORD_2.Word AS coq_word_label_2",
                                 "COQ_WORD_1.POS AS coq_word_pos_1",
                                 "COQ_WORD_2.POS AS coq_word_pos_2",
                                 "COQ_SOURCE_1.Title AS coq_source_label_1",
                                 "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
                                 "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])

    def test_get_required_columns_4(self):
        query = TokenQuery("*", self.Session)
        l = self.resource.get_required_columns(query.query_list[0],
                                               ["lemma_label"])
        self.assertListEqual(l, ["COQ_LEMMA_1.Lemma AS coq_lemma_label_1",
                                 "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
                                 "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])

    def test_get_required_columns_quantified(self):
        s = "more * than [dt]{0,1} [jj]{0,3} [nn*]{1,2}"
        query = TokenQuery(s, self.Session)

        self.assertTrue(len(query.query_list) == 16)
        l = self.resource.get_corpus_joins(query.query_list[0])
        # 1    2 3     4      5    6    7      8     9
        # more * than {NONE} {NONE NONE NONE} {[nn*] NONE}

        l = self.resource.get_required_columns(query.query_list[0],
            ["word_label"])
        self.assertListEqual(l,
            ["COQ_WORD_1.Word AS coq_word_label_1",
             "COQ_WORD_2.Word AS coq_word_label_2",
             "COQ_WORD_3.Word AS coq_word_label_3",
             "NULL AS coq_word_label_4",
             "NULL AS coq_word_label_5",
             "NULL AS coq_word_label_6",
             "NULL AS coq_word_label_7",
             "COQ_WORD_8.Word AS coq_word_label_8",
             "NULL AS coq_word_label_9",
             "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
             "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])

    def test_get_required_columns_NULL_1(self):
        # tests issue #256
        query = TokenQuery("_NULL *", self.Session)
        l = self.resource.get_required_columns(query.query_list[0],
                                               ["word_label"])
        self.assertListEqual(l,
             ["NULL AS coq_word_label_1",
              "COQ_WORD_2.Word AS coq_word_label_2",
              "COQ_CORPUS_2.ID AS coquery_invisible_corpus_id",
              "COQ_CORPUS_2.FileId AS coquery_invisible_origin_id"])

    def test_get_required_columns_NULL_2(self):
        # tests issue #256
        query = TokenQuery("_NULL *", self.Session)
        l = self.resource.get_required_columns(query.query_list[0],
                                               ["word_label", "source_label"])
        self.assertListEqual(l,
             ["NULL AS coq_word_label_1",
              "COQ_WORD_2.Word AS coq_word_label_2",
              "COQ_SOURCE_2.Title AS coq_source_label_1",
              "COQ_CORPUS_2.ID AS coquery_invisible_corpus_id",
              "COQ_CORPUS_2.FileId AS coquery_invisible_origin_id"])

    def test_feature_joins_NULL_1(self):
        # tests issue #256
        l1, l2 = self.resource.get_feature_joins(
            0, ["source_label"], first_item=2)
        self.assertListEqual(
            l1,
            [self.simple("""
             INNER JOIN Files AS COQ_SOURCE_2
             ON COQ_SOURCE_2.FileId = COQ_CORPUS_2.FileId""")])
        self.assertListEqual(l2, [])


    ## QUERY STRINGS

    def test_query_string_blank(self):
        query = TokenQuery("*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_CORPUS_1.ID AS coquery_invisible_corpus_id,
                   COQ_CORPUS_1.FileId AS coquery_invisible_origin_id
            FROM Corpus AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId"""

        self.assertEqual(self.simple(query_string),
                         self.simple(target_string))

    def test_query_string_ortho(self):
        query = TokenQuery("a*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_CORPUS_1.ID AS coquery_invisible_corpus_id,
                   COQ_CORPUS_1.FileId AS coquery_invisible_origin_id
            FROM Corpus AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId
            WHERE (COQ_WORD_1.Word LIKE 'a%')"""

        self.assertEqual(self.simple(query_string),
                         self.simple(target_string))

    def test_query_string_ortho_or(self):
        query = TokenQuery("a*|b*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_CORPUS_1.ID AS coquery_invisible_corpus_id,
                   COQ_CORPUS_1.FileId AS coquery_invisible_origin_id
            FROM Corpus AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId
            WHERE (COQ_WORD_1.Word LIKE 'a%' OR COQ_WORD_1.Word LIKE 'b%')"""

        self.assertEqual(self.simple(query_string),
                         self.simple(target_string))

    def test_query_string_ortho_or_with_pos(self):
        query = TokenQuery("a*|b*.[n*]", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_CORPUS_1.ID AS coquery_invisible_corpus_id,
                   COQ_CORPUS_1.FileId AS coquery_invisible_origin_id
            FROM Corpus AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId
            WHERE (COQ_WORD_1.Word LIKE 'a%' OR
                   COQ_WORD_1.Word LIKE 'b%') AND
                  (COQ_WORD_1.POS LIKE 'n%')"""

        self.assertEqual(self.simple(query_string),
                         self.simple(target_string))

    def test_query_string_two_items(self):
        query = TokenQuery("a* b*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_WORD_2.Word AS coq_word_label_2,
                   COQ_CORPUS_1.ID AS coquery_invisible_corpus_id,
                   COQ_CORPUS_1.FileId AS coquery_invisible_origin_id

            FROM Corpus AS COQ_CORPUS_1
            INNER JOIN Corpus AS COQ_CORPUS_2
                    ON COQ_CORPUS_2.ID = COQ_CORPUS_1.ID + 1

            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId
            INNER JOIN Lexicon AS COQ_WORD_2
                    ON COQ_WORD_2.WordId = COQ_CORPUS_2.WordId

            WHERE (COQ_WORD_1.Word LIKE 'a%') AND
                  (COQ_WORD_2.Word LIKE 'b%')"""

        self.assertEqual(self.simple(query_string),
                         self.simple(target_string))

    def test_query_string_apostrophe(self):
        query = TokenQuery("*'ll", self.Session)
        query_string = self.resource.get_query_string(
            query.query_list[0], ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_CORPUS_1.ID AS coquery_invisible_corpus_id,
                   COQ_CORPUS_1.FileId AS coquery_invisible_origin_id
            FROM Corpus AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId
            WHERE (COQ_WORD_1.Word LIKE '%''ll')"""
        self.assertEqual(self.simple(query_string),
                         self.simple(target_string))

    def test_query_string_NULL_1(self):
        # tests issue #256
        query = TokenQuery("_NULL *", self.Session)
        query_string = self.resource.get_query_string(
            query.query_list[0], ["word_label", "source_label"])
        target_string = """
            SELECT NULL AS coq_word_label_1,
                   COQ_WORD_2.Word AS coq_word_label_2,
                   COQ_SOURCE_2.Title AS coq_source_label_1,
                   COQ_CORPUS_2.ID AS coquery_invisible_corpus_id,
                   COQ_CORPUS_2.FileId AS coquery_invisible_origin_id

            FROM Corpus AS COQ_CORPUS_2

            INNER JOIN Files AS COQ_SOURCE_2
                    ON COQ_SOURCE_2.FileId = COQ_CORPUS_2.FileId

            INNER JOIN Lexicon AS COQ_WORD_2
                    ON COQ_WORD_2.WordId = COQ_CORPUS_2.WordId"""

        self.assertEqual(self.simple(query_string),
                         self.simple(target_string))


    ### WHERE get_token_conditions

    def test_where_conditions_1(self):
        query = TokenQuery("a* b*", self.Session)
        join_list = self.resource.get_corpus_joins(query.query_list[0])
        l = self.resource.get_condition_list(query.query_list[0],
                                             join_list,
                                             ["word_label"])
        self.assertListEqual(l,
            ["(COQ_WORD_1.Word LIKE 'a%')",
             "(COQ_WORD_2.Word LIKE 'b%')"])

    def test_where_conditions_2(self):
        query = TokenQuery("*'ll", self.Session)
        join_list = self.resource.get_corpus_joins(query.query_list[0])
        l = self.resource.get_condition_list(query.query_list[0],
                                             join_list,
                                             ["word_label"])
        self.assertListEqual(l,
            ["(COQ_WORD_1.Word LIKE '%''ll')"])

    def test_where_conditions_quantified(self):
        s = "more * than [dt]{0,1} [jj]{0,3} [nn*]{1,2}"
        # 1    2 3     4      5    6    7      8     9
        # more * than {NONE} {NONE NONE NONE} {[nn*] NONE}
        query = TokenQuery(s, self.Session)
        join_list = self.resource.get_corpus_joins(query.query_list[0])
        l = self.resource.get_condition_list(query.query_list[0],
                                             join_list,
                                             ["word_label"])
        self.assertListEqual(l,
            ["(COQ_WORD_1.Word = 'more')",
             "(COQ_WORD_3.Word = 'than')",
             "(COQ_WORD_8.POS LIKE 'nn%')"])


def _monkeypatch_get_resource(name):
    return TestCorpusWithExternal.external, None, None


class TestSuperFlat(unittest.TestCase):
    """
    This TestCase tests issues with a corpus that doesn't have a Lexicon
    table, but in which the words (and other lexical features) are stored
    directly in the corpus table:

    Issue #271

    """
    resource = MockBuckeye
    external = ExternalCorpus

    def setUp(self):
        self.maxDiff = None
        options.cfg = argparse.Namespace()
        options.cfg.number_of_tokens = 0
        options.cfg.limit_matches = False
        options.cfg.regexp = False
        options.cfg.query_case_sensitive = False
        options.get_configuration_type = lambda: SQL_MYSQL
        options.get_resource = _monkeypatch_get_resource
        self.Session = MockOptions()
        self.Session.Resource = self.resource
        self.Session.Lexicon = None
        self.Session.Corpus = None

        self.link = coquery.links.Link(
                        self.resource.name, "corpus_word",
                        self.external.name, "word_label",
                        join="LEFT JOIN")
        options.cfg.current_server = "Default"
        options.cfg.table_links = {}
        options.cfg.table_links[options.cfg.current_server] = [self.link]

    def test_linked_feature_join(self):
        ext_feature = "{}.word_data".format(self.link.get_hash())
        l1, l2 = self.resource.get_feature_joins(0, [ext_feature])

        self.assertListEqual(l1, [
            ("LEFT JOIN extcorp.Lexicon AS EXTCORP_LEXICON_1 "
             "ON EXTCORP_LEXICON_1.Word = COQ_CORPUS_1.Word")])
        self.assertListEqual(l2, [])

    def test_linked_required_columns(self):
        query = TokenQuery("*", self.Session)
        ext_feature = "{}.word_data".format(self.link.get_hash())
        l = self.resource.get_required_columns(query.query_list[0],
                                               [ext_feature])
        self.assertListEqual(l,
            ["EXTCORP_LEXICON_1.ExtData AS db_extcorp_coq_word_data_1",
             "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
             "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])


class TestCorpusWithExternal(unittest.TestCase):
    external = ExternalCorpus
    resource = Resource

    def setUp(self):
        self.maxDiff = None
        options.cfg = argparse.Namespace()
        options.cfg.number_of_tokens = 0
        options.cfg.limit_matches = False
        options.cfg.regexp = False
        options.cfg.query_case_sensitive = False
        options.get_configuration_type = lambda: SQL_MYSQL
        options.get_resource = _monkeypatch_get_resource
        self.Session = MockOptions()
        self.Session.Resource = self.resource
        self.Session.Lexicon = None
        self.Session.Corpus = None

        self.link = coquery.links.Link(
                        self.resource.name, "word_label",
                        self.external.name, "word_label",
                        join="LEFT JOIN")
        options.cfg.current_server = "Default"
        options.cfg.table_links = {}
        options.cfg.table_links[options.cfg.current_server] = [self.link]

    def test_linked_feature_join(self):
        ext_feature = "{}.word_data".format(self.link.get_hash())
        l1, l2 = self.resource.get_feature_joins(0, [ext_feature])
        self.assertListEqual(l1, [
            "INNER JOIN Lexicon AS COQ_WORD_1 ON COQ_WORD_1.WordId = COQ_CORPUS_1.WordId",
            "LEFT JOIN extcorp.Lexicon AS EXTCORP_LEXICON_1 ON EXTCORP_LEXICON_1.Word = COQ_WORD_1.Word"])
        self.assertListEqual(l2, [])

    def test_linked_required_columns(self):
        query = TokenQuery("*", self.Session)
        ext_feature = "{}.word_data".format(self.link.get_hash())
        l = self.resource.get_required_columns(query.query_list[0],
                                               [ext_feature])
        self.assertListEqual(l,
            ["EXTCORP_LEXICON_1.ExtData AS db_extcorp_coq_word_data_1",
             "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
             "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])

    def test_quantified_required_columns(self):
        ext_feature = "{}.word_data".format(self.link.get_hash())
        s = "happy to{0,1} [n*]"

        query = TokenQuery(s, self.Session)
        self.assertTrue(len(query.query_list) == 2)

        l = self.resource.get_corpus_joins(query.query_list[0])
        # 1     2    3
        # happy {to} [n*]

        l = self.resource.get_required_columns(query.query_list[0],
            ["word_label", ext_feature])
        self.assertListEqual(l,
            ["COQ_WORD_1.Word AS coq_word_label_1",
             "NULL AS coq_word_label_2",
             "COQ_WORD_3.Word AS coq_word_label_3",
             "EXTCORP_LEXICON_1.ExtData AS db_extcorp_coq_word_data_1",
             "NULL AS db_extcorp_coq_word_data_2",
             "EXTCORP_LEXICON_3.ExtData AS db_extcorp_coq_word_data_3",
             "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
             "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])

        l = self.resource.get_required_columns(query.query_list[1],
            ["word_label", ext_feature])
        self.assertListEqual(l,
            ["COQ_WORD_1.Word AS coq_word_label_1",
             "COQ_WORD_2.Word AS coq_word_label_2",
             "COQ_WORD_3.Word AS coq_word_label_3",
             "EXTCORP_LEXICON_1.ExtData AS db_extcorp_coq_word_data_1",
             "EXTCORP_LEXICON_2.ExtData AS db_extcorp_coq_word_data_2",
             "EXTCORP_LEXICON_3.ExtData AS db_extcorp_coq_word_data_3",
             "COQ_CORPUS_1.ID AS coquery_invisible_corpus_id",
             "COQ_CORPUS_1.FileId AS coquery_invisible_origin_id"])

def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestCorpus),
        unittest.TestLoader().loadTestsFromTestCase(TestSuperFlat),
        unittest.TestLoader().loadTestsFromTestCase(TestCorpusWithExternal)
        ])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

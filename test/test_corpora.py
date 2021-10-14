# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import os
import pandas as pd

from coquery.defines import DEFAULT_CONFIGURATION
from coquery.connections import MySQLConnection
from coquery.corpus import SQLResource, CorpusClass, BaseResource
from coquery.coquery import options
from coquery.defines import SQL_MYSQL, CONTEXT_NONE
from coquery.queries import TokenQuery
from coquery.tokens import COCAToken
import coquery.links
from test.testcase import CoqTestCase, run_tests


class MockConnection(MySQLConnection):
    def resources(self):
        return self._resources


default_connection = MockConnection(name=DEFAULT_CONFIGURATION,
                                    host="127.0.0.1",
                                    port=3306,
                                    user="coquery", password="coquery")


class CorpusResource(SQLResource):
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

    def dump_table(self, path, rc_table):
        with open(path, "w") as dump_file:
            dump_file.write(rc_table)


def simple(s):
    s = s.replace("\n", " ")
    s = s.replace("\t", " ")
    while "  " in s:
        s = s.replace("  ", " ")
    return s.strip()


class NGramResource(CorpusResource):
    corpusngram_table = "CorpusNgram"
    corpusngram_width = 3


class BiGramResource(CorpusResource):
    corpusngram_table = "CorpusNgram"
    corpusngram_width = 2


class MockBuckeye(SQLResource):
    """
    MockBuckeye simulates a super-flat corpus, i.e. one in which there is not
    even a Lexicon table.
    """
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word = "Word"
    corpus_pos = "POS"
    corpus_lemma = "Lemma"
    corpus_starttime = "Start"
    corpus_endtime = "End"
    corpus_file_id = "FileId"
    file_table = "Files"
    file_id = "FileId",
    file_path = "Path"
    name = "SuperFlat"

    lexical_features = ["corpus_word", "corpus_pos",
                        "corpus_starttime", "corpus_endtime"]

    query_item_word = "corpus_word"
    query_item_pos = "corpus_pos"
    query_item_lemma = "corpus_lemma"


class FlatResource(SQLResource):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "FileId"
    corpus_starttime = "Start"
    corpus_endtime = "End"
    corpus_sentence = "Sentence"
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


class TestCorpus(CoqTestCase):
    flat_resource = FlatResource

    @classmethod
    def pos_check_function(cls, l):
        return [x.lower().startswith(("n", "v")) for x in l]

    def setUp(self):
        self.resource = CorpusResource(None, None)
        self.maxDiff = None
        options.cfg = argparse.Namespace()
        options.cfg.number_of_tokens = 0
        options.cfg.limit_matches = False
        options.cfg.regexp = False
        options.cfg.query_case_sensitive = False
        options.get_configuration_type = lambda: SQL_MYSQL
        options.cfg.context_mode = CONTEXT_NONE
        options.cfg.context_left = None
        options.cfg.context_right = None
        self.Session = argparse.Namespace()
        self.Session.Resource = self.resource
        self.Session.Corpus = None

        options.cfg.current_connection = default_connection

        COCAToken.set_pos_check_function(self.pos_check_function)

    # TEST TABLE PATH

    def test_table_path_deep(self):
        lst = ["word", "deep"]
        path = self.resource.get_table_path(*lst)
        self.assertListEqual(path, ["word", "lemma", "deep"])

    def test_table_path_non_existing(self):
        lst = ["lemma", "source"]
        path = self.resource.get_table_path(*lst)
        self.assertEqual(path, None)

    def test_get_required_tables_1(self):
        x = self.resource.get_required_tables("corpus", [], {})
        root, lst = x
        self.assertEqual(root, "corpus")
        self.assertListEqual(lst, [])

    def test_get_required_tables_2(self):
        x = self.resource.get_required_tables("corpus", ["word_label"], {})
        root, lst = x
        self.assertEqual(root, "corpus")
        self.assertListEqual(lst, [("word", [])])

    def test_get_required_tables_3(self):
        root, lst = self.resource.get_required_tables(
            "corpus", ["word_label", "source_label"], {})
        self.assertEqual(root, "corpus")
        self.assertListEqual(lst, [("source", []), ("word", [])])

    def test_get_required_tables_3a(self):
        root, lst = self.resource.get_required_tables(
            "corpus", ["source_label", "word_label"], {})
        self.assertEqual(root, "corpus")
        self.assertListEqual(lst,
                             [("source", []), ("word", [])])

    def test_get_required_tables_4(self):
        root, lst = self.resource.get_required_tables(
            "corpus", ["lemma_label", "word_label", "source_label"], {})
        self.assertListEqual(lst,
                             [("source", []), ("word", [("lemma", [])])])

    def test_get_required_tables_5(self):
        root, lst = self.resource.get_required_tables(
            "corpus", ["word_label", "lemma_label"], {})
        self.assertEqual(lst,
                         [("word", [("lemma", [])])])

    def test_get_required_tables_6(self):
        root, lst = self.resource.get_required_tables(
            "corpus", ["lemma_label"], {})
        self.assertEqual(lst, [("word", [("lemma", [])])])

    # TEST QUERY ORDER HEURISTICS

    def assertTListEqual(self, l1, l2):
        for x1, x2 in zip(l1, l2):
            self.assertEqual(x1, x2)

    def test_string_entropy_0(self):
        strings = ["*", "?*", "*?"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertTListEqual(entropies, [entropies[0]] * len(entropies))
        strings = ["a", "b"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertTListEqual(entropies, [entropies[0]] * len(entropies))

    def test_string_entropy_1(self):
        strings = ["*", "?", "a"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_string_entropy_2(self):
        strings = ["a*", "a?", "a", "aa"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_string_entropy_3(self):
        strings = ["a?", "a", "aa"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_string_entropy_4(self):
        strings = ["a*", "a?*", "aa*"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_string_entropy_5(self):
        strings = ["*a", "*aa", "a*", "aa*"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_string_entropy_6(self):
        strings = ["~a*", "a*"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_string_entropy_7(self):
        strings = ["[n*]", "a*"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_string_entropy_8(self):
        strings = ["*", "[n*]", "a*", "[nn*]", "aa*"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_string_entropy_9(self):
        strings = ["*", "[n*]", "*a"]
        entropies = [self.resource.string_entropy(s) for s in strings]
        self.assertListEqual(entropies, sorted(entropies, reverse=True))

    def test_get_token_order_1(self):
        i1 = (0, (1, '*'))
        i2 = (1, (2, '*'))
        self.assertListEqual(
            self.resource.get_token_order([i1, i2]),
            [i1, i2])
        self.assertListEqual(
            self.resource.get_token_order([i2, i1]),
            [i2, i1])

    def test_get_token_order_2(self):
        i1 = (0, (1, '*'))
        i2 = (1, (2, 'the'))
        self.assertListEqual(
            self.resource.get_token_order([i1, i2]),
            [i2, i1])
        self.assertListEqual(
            self.resource.get_token_order([i2, i1]),
            [i2, i1])

    def test_get_token_order_3(self):
        i1 = (0, (1, '*'))
        i2 = (1, (2, '.'))
        self.assertListEqual(
            self.resource.get_token_order([i1, i2]),
            [i2, i1])
        self.assertListEqual(
            self.resource.get_token_order([i2, i1]),
            [i2, i1])

    def test_get_token_order_4(self):
        """
        Test penalization of POS tags (1)
        """
        i1 = (0, (1, 'a*'))
        i2 = (1, (2, '[n*]'))
        self.assertListEqual(
            self.resource.get_token_order([i1, i2]),
            [i1, i2])
        self.assertListEqual(
            self.resource.get_token_order([i2, i1]),
            [i1, i2])

    def test_get_token_order_5(self):
        """
        Test penalization of POS tags (2)
        """
        i1 = (0, (1, 'a*'))
        i2 = (1, (2, '[nn*]'))
        self.assertListEqual(
            self.resource.get_token_order([i1, i2]),
            [i2, i1])
        self.assertListEqual(
            self.resource.get_token_order([i2, i1]),
            [i2, i1])

    def test_get_token_order_6(self):
        """
        Test penalization of negation
        """
        i1 = (0, (1, 'a*'))
        i2 = (1, (2, '~a*'))
        self.assertListEqual(
            self.resource.get_token_order([i1, i2]),
            [i1, i2])
        self.assertListEqual(
            self.resource.get_token_order([i2, i1]),
            [i1, i2])

    def test_is_lexical_1(self):
        self.assertTrue(self.resource.is_lexical("word_label"))
        self.assertTrue(self.resource.is_lexical("lemma_label"))
        self.assertTrue(self.resource.is_lexical("word_id"))
        self.assertFalse(self.resource.is_lexical("source_label"))
        self.assertFalse(self.resource.is_lexical("segment_label"))

    def test_is_lexical_2(self):
        self.assertTrue(self.resource.is_lexical("corpus_id"))
        self.assertTrue(self.resource.is_lexical("corpus_word_id"))
        self.assertFalse(self.resource.is_lexical("corpus_source_id"))

    def test_get_origin_rc(self):
        self.assertEqual(self.resource.get_origin_rc(), "corpus_source_id")

    # TEST get_subselect_corpus():

    #def test_get_subselect_corpus_1(self):
        #query = TokenQuery("*", self.Session)
        #l = [simple(s) for s
             #in self.resource.get_subselect_corpus(query.query_list[0])]

        #self.assertListEqual(
            #l,
            #[simple(

    ## TEST CORPUS JOINS

    def test_corpus_joins_one_item(self):
        query = TokenQuery("*", self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(
            lst,
            [simple("""FROM  (SELECT End AS End1,
                                     FileId AS FileId1,
                                     ID AS ID1,
                                     Start AS Start1,
                                     WordId AS WordId1
                              FROM   Corpus) AS COQ_CORPUS_1""")])

    def test_corpus_joins_three_items(self):
        query = TokenQuery("* * *", self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]

        self.assertListEqual(
            lst,
            [simple("""FROM  (SELECT End AS End1,
                                     FileId AS FileId1,
                                     ID AS ID1,
                                     Start AS Start1,
                                     WordId AS WordId1
                              FROM   Corpus) AS COQ_CORPUS_1"""),
             simple("""INNER JOIN (SELECT End AS End2,
                                          FileId AS FileId2,
                                          ID AS ID2,
                                          Start AS Start2,
                                          WordId AS WordId2
                                   FROM   Corpus) AS COQ_CORPUS_2
                        ON    ID2 = ID1 + 1"""),
             simple("""INNER JOIN (SELECT End AS End3,
                                          FileId AS FileId3,
                                          ID AS ID3,
                                          Start AS Start3,
                                          WordId AS WordId3
                                   FROM   Corpus) AS COQ_CORPUS_3
                       ON     ID3 = ID1 + 2""")])

    def test_corpus_joins_optimized_order_1(self):
        """
        Three query items, join order optimized by query item complexity.
        """
        query = TokenQuery("* *ier [n*]", self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.maxDiff = None

        self.assertListEqual(
            lst,
            [simple("""FROM  (SELECT End AS End2,
                                     FileId AS FileId2,
                                     ID AS ID2,
                                     Start AS Start2,
                                     WordId AS WordId2
                              FROM   Corpus) AS COQ_CORPUS_2"""),
             simple("""INNER JOIN (SELECT End AS End3,
                                          FileId AS FileId3,
                                          ID AS ID3,
                                          Start AS Start3,
                                          WordId AS WordId3
                                   FROM   Corpus) AS COQ_CORPUS_3
                       ON     ID3 = ID2 + 1"""),
             simple("""INNER JOIN (SELECT End AS End1,
                                          FileId AS FileId1,
                                          ID AS ID1,
                                          Start AS Start1,
                                          WordId AS WordId1
                                   FROM   Corpus) AS COQ_CORPUS_1
                       ON     ID1 = ID2 - 1""")])

    def test_corpus_joins_optimized_order_2(self):
        """
        Three query items, join order optimized by query item complexity.
        POS tags are penalized.
        """
        query = TokenQuery("* d* [n*]", self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.maxDiff = None
        self.assertListEqual(
            lst,
            [simple("""FROM  (SELECT End AS End2,
                                     FileId AS FileId2,
                                     ID AS ID2,
                                     Start AS Start2,
                                     WordId AS WordId2
                              FROM   Corpus) AS COQ_CORPUS_2"""),
             simple("""INNER JOIN (SELECT End AS End3,
                                          FileId AS FileId3,
                                          ID AS ID3,
                                          Start AS Start3,
                                          WordId AS WordId3
                                   FROM   Corpus) AS COQ_CORPUS_3
                       ON     ID3 = ID2 + 1"""),
             simple("""INNER JOIN (SELECT End AS End1,
                                          FileId AS FileId1,
                                          ID AS ID1,
                                          Start AS Start1,
                                          WordId AS WordId1
                                   FROM   Corpus) AS COQ_CORPUS_1
                       ON     ID1 = ID2 - 1""")])

    def test_quantified_query_string_1(self):
        query = TokenQuery("* b*{1,2} *", self.Session)
        self.assertTrue(len(query.query_list) == 2)

        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]

        self.assertListEqual(
            lst,
            [simple("""FROM  (SELECT End AS End2,
                                     FileId AS FileId2,
                                     ID AS ID2,
                                     Start AS Start2,
                                     WordId AS WordId2
                              FROM   Corpus) AS COQ_CORPUS_2"""),
             simple("""INNER JOIN (SELECT End AS End1,
                                          FileId AS FileId1,
                                          ID AS ID1,
                                          Start AS Start1,
                                          WordId AS WordId1
                                   FROM   Corpus) AS COQ_CORPUS_1
                       ON     ID1 = ID2 - 1"""),
             simple("""INNER JOIN (SELECT End AS End4,
                                          FileId AS FileId4,
                                          ID AS ID4,
                                          Start AS Start4,
                                          WordId AS WordId4
                                   FROM   Corpus) AS COQ_CORPUS_4
                       ON     ID4 = ID2 + 1""")])

        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[1])]
        self.assertListEqual(
            lst,
            [simple("""FROM  (SELECT End AS End2,
                                     FileId AS FileId2,
                                     ID AS ID2,
                                     Start AS Start2,
                                     WordId AS WordId2
                              FROM   Corpus) AS COQ_CORPUS_2"""),
             simple("""INNER JOIN (SELECT End AS End3,
                                          FileId AS FileId3,
                                          ID AS ID3,
                                          Start AS Start3,
                                          WordId AS WordId3
                                   FROM   Corpus) AS COQ_CORPUS_3
                       ON     ID3 = ID2 + 1"""),
             simple("""INNER JOIN (SELECT End AS End1,
                                          FileId AS FileId1,
                                          ID AS ID1,
                                          Start AS Start1,
                                          WordId AS WordId1
                                   FROM   Corpus) AS COQ_CORPUS_1
                       ON ID1 = ID2 - 1"""),
             simple("""INNER JOIN (SELECT End AS End4,
                                          FileId AS FileId4,
                                          ID AS ID4,
                                          Start AS Start4,
                                          WordId AS WordId4
                                   FROM   Corpus) AS COQ_CORPUS_4
                       ON ID4 = ID2 + 2""")])

    def test_lemmatized_corpus_joins_1(self):
        S = "#abc.[n*]"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(
            lst,
            [simple("""
                FROM  (SELECT End AS End1,
                              FileId AS FileId1,
                              ID AS ID1,
                              Start AS Start1,
                              WordId AS WordId1
                       FROM   Corpus) AS COQ_CORPUS_1""")])

    ### FEATURE JOINS

    def test_feature_joins_1(self):
        l1, l2 = self.resource.get_feature_joins(0, ["word_label"])
        self.assertListEqual(l1, [simple("""
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1""")])

    def test_feature_joins_2(self):
        l1, l2 = self.resource.get_feature_joins(1, ["word_label"])
        self.assertListEqual(l1, [simple("""
            INNER JOIN Lexicon AS COQ_WORD_2
                    ON COQ_WORD_2.WordId = WordId2""")])

    def test_feature_joins_3(self):
        l1, l2 = self.resource.get_feature_joins(0, ["word_label", "word_pos"])
        self.assertListEqual(l1, [simple("""
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1""")])
        self.assertListEqual(l2, [])

    def test_feature_joins_4(self):
        # direct and dependent selection
        l1, l2 = self.resource.get_feature_joins(
            0, ["word_label", "lemma_label"])
        self.assertListEqual(
            l1,
            [("INNER JOIN Lexicon AS COQ_WORD_1 "
              "ON COQ_WORD_1.WordId = WordId1"),
             ("INNER JOIN Lemmas AS COQ_LEMMA_1 "
              "ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId")])
        self.assertListEqual(l2, [])

    def test_feature_joins_4a(self):
        # direct and dependent selection, inverse order
        l1a, l2a = self.resource.get_feature_joins(
            0, ["lemma_label", "word_label"])
        l1b, l2b = self.resource.get_feature_joins(
            0, ["word_label", "lemma_label"])
        self.assertListEqual(l1a, l1b)
        self.assertListEqual(l2a, l2b)

    def test_feature_joins_5(self):
        # dependent selection only; feature joins should be like
        # a join where all in-between tables are directly selected:
        l1a, l2a = self.resource.get_feature_joins(0, ["lemma_label"])
        l1b, l2b = self.resource.get_feature_joins(
            0, ["word_label", "lemma_label"])
        self.assertListEqual(l1a, l1b)
        self.assertListEqual(l2a, l2b)

    def test_feature_joins_6(self):
        # dependent selection, second order
        l1, l2 = self.resource.get_feature_joins(0, ["deep_label"])
        self.assertListEqual(
            l1,
            [("INNER JOIN Lexicon AS COQ_WORD_1 "
              "ON COQ_WORD_1.WordId = WordId1"),
             ("INNER JOIN Lemmas AS COQ_LEMMA_1 "
              "ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId"),
             ("INNER JOIN Deep AS COQ_DEEP_1 ON "
              "COQ_DEEP_1.DeepId = COQ_LEMMA_1.DeepId")])
        self.assertListEqual(l2, [])

    def test_feature_joins_7a(self):
        # get a source feature (first query item)
        l1, l2 = self.resource.get_feature_joins(0, ["source_label"])
        self.assertListEqual(
            l1,
            ["INNER JOIN Files AS COQ_SOURCE_1 "
             "ON COQ_SOURCE_1.FileId = FileId1"])
        self.assertListEqual(l2, [])

    def test_feature_joins_7b(self):
        # get a source feature (second query item)
        l1, l2 = self.resource.get_feature_joins(1, ["source_label"])
        self.assertListEqual(l1, [])
        self.assertListEqual(l2, [])

    #def test_feature_joins_8(self):
        ## words and segments
        ## this test is still not operational
        #l1, l2 = self.resource.get_feature_joins(
        #   0, ["word_label", "segment_label"])
        #print(l1, l2)

    def test_get_token_conditions_1(self):
        token = COCAToken("a*")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d, {"word": ["COQ_WORD_1.Word LIKE 'a%'"]})

    def test_get_token_conditions_2(self):
        token = COCAToken("a*|b*.[n*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d,
            {"word": [("COQ_WORD_1.Word LIKE 'a%' OR "
                       "COQ_WORD_1.Word LIKE 'b%'"),
                      "COQ_WORD_1.POS LIKE 'n%'"]})

    def test_get_token_conditions_3(self):
        token = COCAToken("[a*|b*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d,
            {"lemma": ["COQ_LEMMA_1.Lemma LIKE 'a%' OR "
                       "COQ_LEMMA_1.Lemma LIKE 'b%'"]})

    def test_get_token_conditions_4(self):
        token = COCAToken("a*.[n*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d,
            {"word": ["COQ_WORD_1.Word LIKE 'a%'",
                      "COQ_WORD_1.POS LIKE 'n%'"]})

    def test_get_token_conditions_5(self):
        token = COCAToken("*'ll")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d, {"word": ["COQ_WORD_1.Word LIKE '%''ll'"]})

    def test_get_token_conditions_negated_1(self):
        token = COCAToken("~a*")
        d = self.resource.get_token_conditions(0, token)
        self.assertTrue(token.negated)
        self.assertDictEqual(
            d, {"word": ["COQ_WORD_1.Word LIKE 'a%'"]})

    def test_get_token_conditions_negated_2(self):
        token = COCAToken("~*.[n*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertTrue(token.negated)
        self.assertDictEqual(
            d, {"word": ["COQ_WORD_1.POS LIKE 'n%'"]})

    def test_get_token_conditions_negated_3(self):
        token = COCAToken("~a*.[n*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertTrue(token.negated)
        self.assertDictEqual(
            d,
            {"word": ["COQ_WORD_1.Word LIKE 'a%'",
                      "COQ_WORD_1.POS LIKE 'n%'"]})

    def test_get_token_conditions_quote_char_1(self):
        token = COCAToken("'ll")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d, {"word": ["COQ_WORD_1.Word = '''ll'"]})

    def test_get_token_conditions_quote_char_2(self):
        token = COCAToken("'ll|ll")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d, {"word": ["COQ_WORD_1.Word IN ('''ll', 'll')"]})

    #def test_get_token_conditions_initial_wildcard_rev(self):
        #token = COCAToken("*ing")
        #d = self.resource.get_token_conditions(0, token)
        #self.assertDictEqual(
            #d, {"word": ["COQ_WORD_1.Word_rev"]})

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
        self.assertDictEqual(
            d, {"word": ["COQ_WORD_1.POS LIKE 'n%'"]})

    def test_token_condition_empty_4(self):
        token = COCAToken("a*.[*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d, {"word": ["COQ_WORD_1.Word LIKE 'a%'"]})

    def test_token_conditions_lemmatized_flat_1(self):
        self.Session.Resource = self.flat_resource
        S = "#abc"
        token = COCAToken(S)
        d = self.flat_resource.get_token_conditions(0, token)
        self.assertEqual(
            simple(d["word"][0]),
            simple("""
                COQ_WORD_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     WHERE (COQ_WORD_1.Word = 'abc'))"""))
        self.Session.Resource = self.resource

    def test_token_conditions_lemmatized_flat_pos(self):
        self.Session.Resource = self.flat_resource
        S = "#a*.[n*]"
        token = COCAToken(S)
        d = self.flat_resource.get_token_conditions(0, token)
        self.assertEqual(
            simple(d["word"][0]),
            simple("""
                COQ_WORD_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     WHERE (COQ_WORD_1.Word LIKE 'a%') AND
                           (COQ_WORD_1.POS LIKE 'n%'))"""))
        self.assertEqual(
            simple(d["word"][1]),
            simple("COQ_WORD_1.POS LIKE 'n%'"))
        self.Session.Resource = self.resource

    def test_token_conditions_lemmatized_deep_1(self):
        S = "#abc"
        token = COCAToken(S)
        d = self.resource.get_token_conditions(0, token)
        self.assertEqual(
            simple(d["word"][0]),
            simple("""
                COQ_LEMMA_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     INNER JOIN Lemmas AS COQ_LEMMA_1
                             ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId
                     WHERE (COQ_WORD_1.Word = 'abc'))"""))

    def test_token_conditions_lemmatized_deep_2(self):
        S = "#/a*/"
        token = COCAToken(S)
        d = self.resource.get_token_conditions(0, token)
        self.assertEqual(
            simple(d["word"][0]),
            simple("""
                COQ_LEMMA_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     INNER JOIN Lemmas AS COQ_LEMMA_1
                             ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId
                     WHERE (COQ_WORD_1.Transcript LIKE 'a%'))"""))

    def test_token_conditions_lemmatized_deep_3(self):
        S = "#a*.[n*]"
        token = COCAToken(S)
        d = self.resource.get_token_conditions(0, token)
        self.assertEqual(
            simple(d["word"][0]),
            simple("""
                COQ_LEMMA_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     INNER JOIN Lemmas AS COQ_LEMMA_1
                             ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId
                     WHERE (COQ_WORD_1.Word LIKE 'a%') AND
                           (COQ_WORD_1.POS LIKE 'n%'))"""))
        self.assertEqual(
            simple(d["word"][1]),
            simple("COQ_WORD_1.POS LIKE 'n%'"))

    def test_token_conditions_lemmatized_deep_4(self):
        """
        Tests issue #296.
        """
        token = COCAToken("#?ome")
        d = self.resource.get_token_conditions(0, token)
        self.assertEqual(
            simple(d["word"][0]),
            simple("""
                COQ_LEMMA_1.Lemma IN
                    (SELECT DISTINCT Lemma
                     FROM       Lexicon AS COQ_WORD_1
                     INNER JOIN Lemmas AS COQ_LEMMA_1
                             ON COQ_LEMMA_1.LemmaId = COQ_WORD_1.LemmaId
                     WHERE (COQ_WORD_1.Word LIKE '_ome'))"""))

    def test_token_conditions_id_query_1(self):
        S = "=123"
        token = COCAToken(S)
        d = self.resource.get_token_conditions(0, token)
        print(d)
        self.assertEqual(
            simple(d["corpus"][0]),
            simple("""ID1 = '123'"""))

    ### SELECT COLUMNS

    def test_get_required_columns_1(self):
        query = TokenQuery("*", self.Session)
        s = self.resource.get_required_columns(query.query_list[0],
                                               ["word_label"])
        self.assertListEqual(s, ["COQ_WORD_1.Word AS coq_word_label_1",
                                 "ID1 AS coquery_invisible_corpus_id",
                                 "FileId1 AS coquery_invisible_origin_id"])

    def test_get_required_columns_2(self):
        query = TokenQuery("* *", self.Session)
        s = self.resource.get_required_columns(query.query_list[0],
                                               ["word_label"])
        self.assertListEqual(s, ["COQ_WORD_1.Word AS coq_word_label_1",
                                 "COQ_WORD_2.Word AS coq_word_label_2",
                                 "ID1 AS coquery_invisible_corpus_id",
                                 "FileId1 AS coquery_invisible_origin_id"])

    def test_get_required_columns_3(self):
        query = TokenQuery("* *", self.Session)
        lst = self.resource.get_required_columns(
            query.query_list[0],
            ["source_label", "word_label", "word_pos"])
        self.assertListEqual(lst,
                             ["COQ_WORD_1.Word AS coq_word_label_1",
                              "COQ_WORD_2.Word AS coq_word_label_2",
                              "COQ_WORD_1.POS AS coq_word_pos_1",
                              "COQ_WORD_2.POS AS coq_word_pos_2",
                              "COQ_SOURCE_1.Title AS coq_source_label_1",
                              "ID1 AS coquery_invisible_corpus_id",
                              "FileId1 AS coquery_invisible_origin_id"])

    def test_get_required_columns_4(self):
        query = TokenQuery("*", self.Session)
        lst = self.resource.get_required_columns(
            query.query_list[0], ["lemma_label"])
        self.assertListEqual(lst, ["COQ_LEMMA_1.Lemma AS coq_lemma_label_1",
                                   "ID1 AS coquery_invisible_corpus_id",
                                   "FileId1 AS coquery_invisible_origin_id"])

    def test_get_required_columns_quantified(self):
        s = "more * than [dt]{0,1} [jj]{0,3} [nn*]{1,2}"
        query = TokenQuery(s, self.Session)

        self.assertTrue(len(query.query_list) == 16)
        # 1    2 3     4      5    6    7      8     9
        # more * than {NONE} {NONE NONE NONE} {[nn*] NONE}

        lst = self.resource.get_required_columns(
            query.query_list[0], ["word_label"])
        self.assertListEqual(
            lst,
            ["COQ_WORD_1.Word AS coq_word_label_1",
             "COQ_WORD_2.Word AS coq_word_label_2",
             "COQ_WORD_3.Word AS coq_word_label_3",
             "NULL AS coq_word_label_4",
             "NULL AS coq_word_label_5",
             "NULL AS coq_word_label_6",
             "NULL AS coq_word_label_7",
             "COQ_WORD_8.Word AS coq_word_label_8",
             "NULL AS coq_word_label_9",
             "ID1 AS coquery_invisible_corpus_id",
             "FileId1 AS coquery_invisible_origin_id"])

    def test_get_token_offset_1(self):
        S = "a*"
        query = TokenQuery(S, self.Session)
        self.assertEqual(
            self.resource.get_token_offset(query.query_list[0]),
            0)

    def test_get_token_offset_2(self):
        S = "_NULL a*"
        query = TokenQuery(S, self.Session)
        self.assertEqual(
            self.resource.get_token_offset(query.query_list[0]),
            1)

    def test_get_required_columns_NULL_1(self):
        # tests issue #256
        query = TokenQuery("_NULL *", self.Session)
        lst = self.resource.get_required_columns(
            query.query_list[0], ["word_label"])
        self.assertListEqual(
            lst,
            ["NULL AS coq_word_label_1",
             "COQ_WORD_2.Word AS coq_word_label_2",
             "ID2 AS coquery_invisible_corpus_id",
             "FileId2 AS coquery_invisible_origin_id"])

    def test_get_required_columns_NULL_2(self):
        # tests issue #256
        query = TokenQuery("_NULL *", self.Session)
        lst = self.resource.get_required_columns(
            query.query_list[0], ["word_label", "source_label"])
        self.assertListEqual(
            lst,
            ["NULL AS coq_word_label_1",
             "COQ_WORD_2.Word AS coq_word_label_2",
             "COQ_SOURCE_2.Title AS coq_source_label_1",
             "ID2 AS coquery_invisible_corpus_id",
             "FileId2 AS coquery_invisible_origin_id"])

    def test_feature_joins_NULL_1(self):
        # tests issue #256
        l1, l2 = self.resource.get_feature_joins(
            0, ["source_label"], first_item=2)
        self.assertListEqual(
            l1,
            [simple("""
             INNER JOIN Files AS COQ_SOURCE_2
             ON COQ_SOURCE_2.FileId = FileId2""")])
        self.assertListEqual(l2, [])

    ### QUERY STRINGS

    def test_query_string_blank(self):
        query = TokenQuery("*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_combined(self):
        query = TokenQuery("a*.[n*]", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE (COQ_WORD_1.Word LIKE 'a%') AND
                  (COQ_WORD_1.POS LIKE 'n%')"""
        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_combined_negated_1(self):
        query = TokenQuery("~a*.[n*]", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE NOT ((COQ_WORD_1.Word LIKE 'a%') AND
                       (COQ_WORD_1.POS LIKE 'n%'))"""
        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_ortho(self):
        query = TokenQuery("a*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE (COQ_WORD_1.Word LIKE 'a%')"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_initial_wildcard(self):
        query = TokenQuery("*ing", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE (COQ_WORD_1.Word LIKE '%ing')"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_ortho_or(self):
        query = TokenQuery("a*|b*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE (COQ_WORD_1.Word LIKE 'a%' OR COQ_WORD_1.Word LIKE 'b%')"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_ortho_or_with_pos(self):
        query = TokenQuery("a*|b*.[n*]", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE (COQ_WORD_1.Word LIKE 'a%' OR
                   COQ_WORD_1.Word LIKE 'b%') AND
                  (COQ_WORD_1.POS LIKE 'n%')"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_two_items(self):
        query = TokenQuery("a* b*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_WORD_2.Word AS coq_word_label_2,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id

            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN (SELECT End AS End2,
                         FileId AS FileId2,
                         ID AS ID2,
                         Start AS Start2,
                         WordId AS WordId2 FROM Corpus) AS COQ_CORPUS_2
                    ON ID2 = ID1 + 1

            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            INNER JOIN Lexicon AS COQ_WORD_2
                    ON COQ_WORD_2.WordId = WordId2

            WHERE (COQ_WORD_1.Word LIKE 'a%') AND
                  (COQ_WORD_2.Word LIKE 'b%')"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_two_items_negated(self):
        query = TokenQuery("~a*|b* ~b*", self.Session)
        query_string = self.resource.get_query_string(query.query_list[0],
                                                      ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_WORD_2.Word AS coq_word_label_2,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id

            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN (SELECT End AS End2,
                         FileId AS FileId2,
                         ID AS ID2,
                         Start AS Start2,
                         WordId AS WordId2 FROM Corpus) AS COQ_CORPUS_2
                    ON ID2 = ID1 + 1

            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            INNER JOIN Lexicon AS COQ_WORD_2
                    ON COQ_WORD_2.WordId = WordId2

            WHERE NOT ((COQ_WORD_1.Word LIKE 'a%' OR
                        COQ_WORD_1.Word LIKE 'b%'))
                  AND
                  NOT ((COQ_WORD_2.Word LIKE 'b%'))"""
        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_apostrophe(self):
        query = TokenQuery("*'ll", self.Session)
        query_string = self.resource.get_query_string(
            query.query_list[0], ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1
            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE (COQ_WORD_1.Word LIKE '%''ll')"""
        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_NULL_1(self):
        # tests issue #256
        query = TokenQuery("_NULL *", self.Session)
        query_string = self.resource.get_query_string(
            query.query_list[0], ["word_label", "source_label"])
        target_string = """
            SELECT NULL AS coq_word_label_1,
                   COQ_WORD_2.Word AS coq_word_label_2,
                   COQ_SOURCE_2.Title AS coq_source_label_1,
                   ID2 AS coquery_invisible_corpus_id,
                   FileId2 AS coquery_invisible_origin_id

            FROM (SELECT End AS End2,
                         FileId AS FileId2,
                         ID AS ID2,
                         Start AS Start2,
                         WordId AS WordId2 FROM Corpus) AS COQ_CORPUS_2

            INNER JOIN Files AS COQ_SOURCE_2
                    ON COQ_SOURCE_2.FileId = FileId2

            INNER JOIN Lexicon AS COQ_WORD_2
                    ON COQ_WORD_2.WordId = WordId2"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_to_file(self):
        query = TokenQuery("*", self.Session)
        query_string = self.resource.get_query_string(
            query.query_list[0], ["word_label", "source_label"], to_file=True)
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   COQ_SOURCE_1.Title AS coq_source_label_1

            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1

            INNER JOIN Files AS COQ_SOURCE_1
                    ON COQ_SOURCE_1.FileId = FileId1

            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_to_file_no_column(self):
        query = TokenQuery("*", self.Session)
        query_string = self.resource.get_query_string(
            query.query_list[0], [], to_file=True)
        target_string = """
            SELECT ID1 AS coquery_invisible_corpus_id
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1 FROM Corpus) AS COQ_CORPUS_1"""

        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_get_context_string(self):
        target_string = """
            SELECT     COQ_WORD_1.Word AS Context,
                       (CASE
                           WHEN ID1 < 100 THEN 0
                           WHEN ID1 >= 100 + 1 THEN 2
                           ELSE 1
                       END) AS Position
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Start AS Start1,
                         WordId AS WordId1
                  FROM   Corpus) AS COQ_CORPUS_1

            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE      (COQ_CORPUS_1.ID1 BETWEEN 95 AND 105) AND
                       (COQ_CORPUS_1.FileId1 = 1) LIMIT 11"""
        context_string = self.resource.get_context_string(
            token_id=100,
            width=1,
            left=5,
            right=5,
            origin_id=1)
        self.assertEqual(simple(context_string),
                         simple(target_string))

    def test_get_context_string_sentence(self):
        target_string = """
            SELECT     COQ_WORD_1.Word AS Context,
                       (CASE
                           WHEN ID1 < 100 THEN 0
                           WHEN ID1 >= 100 + 1 THEN 2
                           ELSE 1
                       END) AS Position
            FROM (SELECT End AS End1,
                         FileId AS FileId1,
                         ID AS ID1,
                         Sentence AS Sentence1,
                         Start AS Start1,
                         WordId AS WordId1
                  FROM   Corpus) AS COQ_CORPUS_1

            INNER JOIN Lexicon AS COQ_WORD_1
                    ON COQ_WORD_1.WordId = WordId1
            WHERE      (COQ_CORPUS_1.ID1 BETWEEN 95 AND 105) AND
                       (COQ_CORPUS_1.FileId1 = 1) AND
                       (COQ_CORPUS_1.Sentence1 = '99') LIMIT 11"""
        context_string = self.flat_resource.get_context_string(
            self.flat_resource,
            token_id=100,
            width=1,
            left=5,
            right=5,
            origin_id=1,
            sentence_id=99)
        self.assertEqual(simple(context_string),
                         simple(target_string))

    def test_get_context_NA(self):
        """
        Test whether the get_context() method reacts appropriately to empty
        data.
        """
        value = self.resource.get_context(
            pd.np.nan,
            pd.np.nan,
            pd.np.nan,
            options.cfg.current_connection,
            left=7, right=7,
            sentence_id=pd.np.nan)
        target = ([None] * 7, [], [None] * 7)
        self.assertEqual(target, value)


class TestSuperFlat(CoqTestCase):
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
        self.Session = argparse.Namespace()
        self.Session.Resource = self.resource
        self.Session.Corpus = None

        self.link = coquery.links.Link(
                        self.resource.name, "corpus_word",
                        self.external.name, "word_label",
                        join="LEFT JOIN")
        options.cfg.table_links = {DEFAULT_CONFIGURATION: [self.link]}

        default = MockConnection(name=DEFAULT_CONFIGURATION,
                                 host="127.0.0.1",
                                 port=3306,
                                 user="coquery", password="coquery")
        default.add_resource(self.resource, None)
        default.add_resource(self.external, None)
        options.cfg.connections = [default]
        options.cfg.current_connection = default

    def test_is_lexical_1(self):
        self.assertFalse(self.resource.is_lexical("file_path"))
        self.assertFalse(self.resource.is_lexical("file_id"))

    def test_is_lexical_2(self):
        self.assertTrue(self.resource.is_lexical("corpus_id"))
        self.assertTrue(self.resource.is_lexical("corpus_word"))
        self.assertTrue(self.resource.is_lexical("corpus_lemma"))

    def test_get_origin_rc(self):
        self.assertEqual(self.resource.get_origin_rc(), "corpus_file_id")

    def test_get_required_columns(self):
        query = TokenQuery("*", self.Session)
        lst = self.resource.get_required_columns(query.query_list[0],
                                                 ["corpus_word"])
        self.assertListEqual(lst, ["Word1 AS coq_corpus_word_1",
                                   "ID1 AS coquery_invisible_corpus_id",
                                   "FileId1 AS coquery_invisible_origin_id"])

    def test_linked_feature_join(self):
        ext_feature = "{}.word_data".format(self.link.get_hash())
        lst1, lst2 = self.resource.get_feature_joins(0, [ext_feature])

        self.assertListEqual(
            lst1,
            [("LEFT JOIN extcorp.Lexicon AS EXTCORP_LEXICON_1 "
              "ON EXTCORP_LEXICON_1.Word = COQ_CORPUS_1.Word1")])
        self.assertListEqual(lst2, [])

    def test_linked_required_columns(self):
        query = TokenQuery("*", self.Session)
        ext_feature = "{}.word_data".format(self.link.get_hash())
        lst = self.resource.get_required_columns(query.query_list[0],
                                                 [ext_feature])
        self.assertListEqual(
            lst,
            ["EXTCORP_LEXICON_1.ExtData AS db_extcorp_coq_word_data_1",
             "ID1 AS coquery_invisible_corpus_id",
             "FileId1 AS coquery_invisible_origin_id"])

    def test_get_token_conditions_1(self):
        token = COCAToken("a*")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(d, {"corpus": ["Word1 LIKE 'a%'"]})

    def test_get_token_conditions_2(self):
        token = COCAToken("a*|b*.[n*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d,
            {"corpus": ["Word1 LIKE 'a%' OR Word1 LIKE 'b%'",
                        "POS1 LIKE 'n%'"]})

    def test_get_token_conditions_3(self):
        token = COCAToken("[a*|b*]")
        d = self.resource.get_token_conditions(0, token)
        self.assertDictEqual(
            d, {"corpus": ["Lemma1 LIKE 'a%' OR Lemma1 LIKE 'b%'"]})

    def test_where_conditions_1(self):
        query = TokenQuery("a* b*", self.Session)
        join_list = self.resource.get_corpus_joins(query.query_list[0])
        lst = self.resource.get_condition_list(
            query.query_list[0], join_list, ["corpus_word"])
        self.assertListEqual(
            lst, ["(Word1 LIKE 'a%')", "(Word2 LIKE 'b%')"])

    def test_where_conditions_2(self):
        query = TokenQuery("a* bcd*", self.Session)
        join_list = self.resource.get_corpus_joins(query.query_list[0])
        lst = self.resource.get_condition_list(
            query.query_list[0], join_list, ["corpus_word"])
        self.assertListEqual(
            lst, ["(Word1 LIKE 'a%')", "(Word2 LIKE 'bcd%')", "ID2 > 0"])

    def test_get_external_join(self):
        ext_feature = "{}.word_data".format(self.link.get_hash())
        s = self.resource.get_external_join(0, ext_feature)
        self.assertEqual(
            s,
            simple("""
                   LEFT JOIN extcorp.Lexicon AS EXTCORP_LEXICON_1
                   ON EXTCORP_LEXICON_1.Word = COQ_CORPUS_1.Word1"""))

    def test_get_required_columns_NULL_1(self):
        # tests issues related to #256
        query = TokenQuery("_NULL *", self.Session)
        lst = self.resource.get_required_columns(
            query.query_list[0], ["corpus_word"])
        self.assertListEqual(
            lst,
            ["NULL AS coq_corpus_word_1",
             "Word2 AS coq_corpus_word_2",
             "ID2 AS coquery_invisible_corpus_id",
             "FileId2 AS coquery_invisible_origin_id"])

    def test_get_required_columns_NULL_2(self):
        # tests issues related to #256
        query = TokenQuery("_NULL *", self.Session)
        lst = self.resource.get_required_columns(
            query.query_list[0], ["corpus_word", "file_path"])
        self.assertListEqual(
            lst,
            ["NULL AS coq_corpus_word_1",
             "Word2 AS coq_corpus_word_2",
             "COQ_FILE_2.Path AS coq_file_path_1",
             "ID2 AS coquery_invisible_corpus_id",
             "FileId2 AS coquery_invisible_origin_id"])

    def test_leading_null(self):
        """
        Test behavior with leading _NULL query items (in response to issue
        #282).
        """
        query = TokenQuery("_NULL o*", self.Session)
        lst = self.resource.get_required_columns(
            query.query_list[0], ["corpus_word", "corpus_starttime"])
        self.assertListEqual(
            lst,
            ["NULL AS coq_corpus_word_1",
             "Word2 AS coq_corpus_word_2",
             "NULL AS coq_corpus_starttime_1",
             "Start2 AS coq_corpus_starttime_2",
             "ID2 AS coquery_invisible_corpus_id",
             "FileId2 AS coquery_invisible_origin_id"])


class TestCorpusWithExternal(CoqTestCase):
    external = ExternalCorpus
    resource = CorpusResource

    def setUp(self):
        self.maxDiff = None
        options.cfg = argparse.Namespace()
        options.cfg.number_of_tokens = 0
        options.cfg.limit_matches = False
        options.cfg.regexp = False
        options.cfg.experimental = True
        options.cfg.query_case_sensitive = False
        self.Session = argparse.Namespace()
        self.Session.Resource = self.resource
        self.Session.Corpus = None
        default = MockConnection(name=DEFAULT_CONFIGURATION,
                                 host="127.0.0.1",
                                 port=3306,
                                 user="coquery", password="coquery")
        default.add_resource(self.resource, None)
        default.add_resource(self.external, None)
        options.cfg.connections = [default]
        options.cfg.current_connection = default

        self.link = coquery.links.Link(
                        self.resource.name, "word_label",
                        self.external.name, "word_label",
                        join="LEFT JOIN")
        self.inner_link = coquery.links.Link(
                        self.resource.name, "word_label",
                        self.external.name, "word_label",
                        join="INNER JOIN")

        options.cfg.table_links = {
            DEFAULT_CONFIGURATION: [self.link, self.inner_link]}

    def test_is_lexical(self):
        self.assertTrue(self.resource.is_lexical("word_label"))
        col = "{}.word_data".format(self.link.get_hash())
        self.assertTrue(self.resource.is_lexical(col))

    def test_get_external_join(self):
        ext_feature = "{}.word_data".format(self.link.get_hash())
        s = self.resource.get_external_join(0, ext_feature)
        self.assertEqual(s,
                         simple("""
                             LEFT JOIN extcorp.Lexicon AS EXTCORP_LEXICON_1
                             ON EXTCORP_LEXICON_1.Word = COQ_WORD_1.Word"""))

    def test_get_external_inner_join(self):
        ext_feature = "{}.word_data".format(self.inner_link.get_hash())
        s = self.resource.get_external_join(0, ext_feature)
        self.assertEqual(s,
                         simple("""
                             INNER JOIN extcorp.Lexicon AS EXTCORP_LEXICON_1
                             ON EXTCORP_LEXICON_1.Word = COQ_WORD_1.Word"""))

    def test_linked_feature_join(self):
        ext_feature = "{}.word_data".format(self.link.get_hash())
        lst1, lst2 = self.resource.get_feature_joins(0, [ext_feature])
        self.assertListEqual(
            lst1,
            [simple("INNER JOIN Lexicon AS COQ_WORD_1 "
                    "ON COQ_WORD_1.WordId = WordId1"),
             simple("LEFT JOIN extcorp.Lexicon AS EXTCORP_LEXICON_1 "
                    "ON EXTCORP_LEXICON_1.Word = COQ_WORD_1.Word")])
        self.assertListEqual(lst2, [])

    def test_linked_required_columns(self):
        query = TokenQuery("*", self.Session)
        ext_feature = "{}.word_data".format(self.link.get_hash())
        lst = self.resource.get_required_columns(query.query_list[0],
                                                 [ext_feature])
        self.assertListEqual(
            lst,
            ["EXTCORP_LEXICON_1.ExtData AS db_extcorp_coq_word_data_1",
             "ID1 AS coquery_invisible_corpus_id",
             "FileId1 AS coquery_invisible_origin_id"])

    def test_quantified_required_columns(self):
        ext_feature = "{}.word_data".format(self.link.get_hash())
        s = "happy to{0,1} [n*]"

        query = TokenQuery(s, self.Session)
        self.assertTrue(len(query.query_list) == 2)

        lst = self.resource.get_corpus_joins(query.query_list[0])
        # 1     2    3
        # happy {to} [n*]

        lst = self.resource.get_required_columns(
            query.query_list[0], ["word_label", ext_feature])
        self.assertListEqual(
            lst,
            ["COQ_WORD_1.Word AS coq_word_label_1",
             "NULL AS coq_word_label_2",
             "COQ_WORD_3.Word AS coq_word_label_3",
             "EXTCORP_LEXICON_1.ExtData AS db_extcorp_coq_word_data_1",
             "NULL AS db_extcorp_coq_word_data_2",
             "EXTCORP_LEXICON_3.ExtData AS db_extcorp_coq_word_data_3",
             "ID1 AS coquery_invisible_corpus_id",
             "FileId1 AS coquery_invisible_origin_id"])

        lst = self.resource.get_required_columns(
            query.query_list[1], ["word_label", ext_feature])
        self.assertListEqual(
            lst,
            ["COQ_WORD_1.Word AS coq_word_label_1",
             "COQ_WORD_2.Word AS coq_word_label_2",
             "COQ_WORD_3.Word AS coq_word_label_3",
             "EXTCORP_LEXICON_1.ExtData AS db_extcorp_coq_word_data_1",
             "EXTCORP_LEXICON_2.ExtData AS db_extcorp_coq_word_data_2",
             "EXTCORP_LEXICON_3.ExtData AS db_extcorp_coq_word_data_3",
             "ID1 AS coquery_invisible_corpus_id",
             "FileId1 AS coquery_invisible_origin_id"])


class TestNGramCorpus(CoqTestCase):
    resource = NGramResource

    def setUp(self):
        self.maxDiff = None
        options.cfg = argparse.Namespace()
        options.cfg.number_of_tokens = 0
        options.cfg.limit_matches = False
        options.cfg.regexp = False
        options.cfg.query_case_sensitive = False
        options.cfg.experimental = True
        options.get_configuration_type = lambda: SQL_MYSQL
        options.cfg.no_ngram = False
        self.Session = argparse.Namespace()
        self.Session.Resource = self.resource
        self.Session.Corpus = None

        options.cfg.current_connection = default_connection

    def test_get_origin_rc(self):
        self.assertEqual(self.resource.get_origin_rc(), "corpus_source_id")

    def test_corpus_joins_one_item(self):
        S = "*"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(lst,
                             [simple("FROM (SELECT End AS End1,"
                                     "             FileId AS FileId1,"
                                     "             ID AS ID1,"
                                     "             Start AS Start1,"
                                     "             WordId AS WordId1"
                                     "      FROM   Corpus) AS COQ_CORPUS_1")])

    def test_corpus_joins_three_items(self):
        S = "* * *"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(lst, ["FROM CorpusNgram"])

    def test_corpus_joins_four_items(self):
        S = "* * * *"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(
            lst,
            ["FROM CorpusNgram",
             simple("INNER JOIN (SELECT "
                    "              End AS End4,"
                    "              FileId AS FileId4,"
                    "              ID AS ID4,"
                    "              Start AS Start4,"
                    "              WordId AS WordId4"
                    "       FROM   Corpus) AS COQ_CORPUS_4"
                    "       ON     ID4 = ID1 + 3")])

    def test_corpus_joins_four_items_ref(self):
        S = ". the end *"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(
            lst,
            ["FROM CorpusNgram",
             simple("INNER JOIN (SELECT "
                    "              End AS End4,"
                    "              FileId AS FileId4,"
                    "              ID AS ID4,"
                    "              Start AS Start4,"
                    "              WordId AS WordId4"
                    "       FROM   Corpus) AS COQ_CORPUS_4"
                    "       ON     ID4 = ID1 + 3")])

    def test_corpus_joins_ref_outside_1(self):
        S = ". . . the"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(
            lst,
            [simple("FROM (SELECT "
                    "              End AS End4,"
                    "              FileId AS FileId4,"
                    "              ID AS ID4,"
                    "              Start AS Start4,"
                    "              WordId AS WordId4"
                    "       FROM   Corpus) AS COQ_CORPUS_4"),
             simple("INNER JOIN CorpusNgram ON ID1 = ID4 - 3")])

    def test_corpus_joins_ref_outside_2(self):
        S = ". . . the ."
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(
            lst,
            [simple("FROM (SELECT "
                    "              End AS End4,"
                    "              FileId AS FileId4,"
                    "              ID AS ID4,"
                    "              Start AS Start4,"
                    "              WordId AS WordId4"
                    "       FROM   Corpus) AS COQ_CORPUS_4"),
             simple("INNER JOIN CorpusNgram ON ID1 = ID4 - 3"),
             simple("INNER JOIN (SELECT "
                    "               End AS End5, "
                    "               FileId AS FileId5, "
                    "               ID AS ID5, "
                    "               Start AS Start5, "
                    "               WordId AS WordId5 "
                    "       FROM Corpus) AS COQ_CORPUS_5 "
                    "       ON ID5 = ID4 + 1")])

    def test_corpus_joins_ref_outside_3(self):
        S = ". . . the great"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]
        self.assertListEqual(
            lst,
            [simple("FROM (SELECT "
                    "              End AS End5,"
                    "              FileId AS FileId5,"
                    "              ID AS ID5,"
                    "              Start AS Start5,"
                    "              WordId AS WordId5"
                    "       FROM   Corpus) AS COQ_CORPUS_5"),
             simple("INNER JOIN (SELECT "
                    "              End AS End4, "
                    "              FileId AS FileId4, "
                    "              ID AS ID4, "
                    "              Start AS Start4, "
                    "              WordId AS WordId4 "
                    "       FROM Corpus) AS COQ_CORPUS_4 "
                    "       ON ID4 = ID5 - 1"),
             simple("INNER JOIN CorpusNgram ON ID1 = ID5 - 4")])

    def test_get_token_offset(self):
        S = "_NULL a*"
        query = TokenQuery(S, self.Session)
        self.assertEqual(
            self.resource.get_token_offset(query.query_list[0]),
            0)

    def test_corpus_required_columns_initial_null_placeholder(self):
        S = "_NULL a*"
        query = TokenQuery(S, self.Session)
        lst = self.resource.get_required_columns(query.query_list[0],
                                                 ["word_label"])
        self.assertListEqual(
            lst,
            ["NULL AS coq_word_label_1",
             "COQ_WORD_2.Word AS coq_word_label_2",
             "ID1 AS coquery_invisible_corpus_id",
             "FileId1 AS coquery_invisible_origin_id"])

    def test_feature_joins_initial_null_placeholder(self):
        l1, l2 = self.resource.get_feature_joins(0, ["word_label"],
                                                 first_item=2)
        self.assertListEqual(l1, [simple("""
            INNER JOIN Lexicon AS COQ_WORD_2
                    ON COQ_WORD_2.WordId = WordId1""")])

    def test_query_string_initial_null_placeholder(self):
        query = TokenQuery("_NULL a* b*", self.Session)
        query_string = self.resource.get_query_string(
            query.query_list[0], ["word_label"])
        target_string = """
            SELECT NULL AS coq_word_label_1,
                   COQ_WORD_2.Word AS coq_word_label_2,
                   COQ_WORD_3.Word AS coq_word_label_3,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM CorpusNgram
            INNER JOIN Lexicon AS COQ_WORD_2 ON COQ_WORD_2.WordId = WordId1
            INNER JOIN Lexicon AS COQ_WORD_3 ON COQ_WORD_3.WordId = WordId2
            WHERE (COQ_WORD_2.Word LIKE 'a%')
              AND (COQ_WORD_3.Word LIKE 'b%')
            """
        self.assertEqual(simple(query_string),
                         simple(target_string))

    def test_query_string_medial_null_placeholder(self):
        """
        Tests issue #292
        """
        query = TokenQuery("a* _NULL b*", self.Session)
        query_string = self.resource.get_query_string(
            query.query_list[0], ["word_label"])
        target_string = """
            SELECT COQ_WORD_1.Word AS coq_word_label_1,
                   NULL AS coq_word_label_2,
                   COQ_WORD_3.Word AS coq_word_label_3,
                   ID1 AS coquery_invisible_corpus_id,
                   FileId1 AS coquery_invisible_origin_id
            FROM CorpusNgram
            INNER JOIN Lexicon AS COQ_WORD_1 ON COQ_WORD_1.WordId = WordId1
            INNER JOIN Lexicon AS COQ_WORD_3 ON COQ_WORD_3.WordId = WordId2
            WHERE (COQ_WORD_1.Word LIKE 'a%')
              AND (COQ_WORD_3.Word LIKE 'b%')
            """
        self.assertEqual(simple(query_string),
                         simple(target_string))


class TestBigramCorpus(CoqTestCase):
    """
    This test case addresses an issue that occured with look-up tables
    consisting of bigrams.

    Apparently, query strings like '* * xxx' or '* xxx yyy' produce the
    correct query strings, but the query string '* *.[x*] yyy' uses incorrect
    ids for the different word columns.

    Thus may be caused by determining the token orders incorrectly.
    """

    resource = BiGramResource

    def setUp(self):
        self.maxDiff = None
        options.cfg = argparse.Namespace()
        options.cfg.number_of_tokens = 0
        options.cfg.limit_matches = False
        options.cfg.regexp = False
        options.cfg.query_case_sensitive = False
        options.cfg.experimental = True
        options.get_configuration_type = lambda: SQL_MYSQL
        options.cfg.no_ngram = False
        self.Session = argparse.Namespace()
        self.Session.Resource = self.resource
        self.Session.Corpus = None

        options.cfg.current_connection = default_connection

    def test_working_1(self):
        S = "* * xxx"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]

        target = [
            simple("FROM (SELECT "
                   "              End AS End3,"
                   "              FileId AS FileId3,"
                   "              ID AS ID3,"
                   "              Start AS Start3,"
                   "              WordId AS WordId3"
                   "       FROM   Corpus) AS COQ_CORPUS_3"),
            simple("INNER JOIN CorpusNgram "
                   "ON ID1 = ID3 - 2")]

        self.assertListEqual(lst, target)

    def test_working_2(self):
        S = "* xxx xxx"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]

        target = [
            simple("FROM CorpusNgram"),
            simple("INNER JOIN (SELECT "
                   "              End AS End3,"
                   "              FileId AS FileId3,"
                   "              ID AS ID3,"
                   "              Start AS Start3,"
                   "              WordId AS WordId3"
                   "       FROM   Corpus) AS COQ_CORPUS_3 "
                   "ON ID3 = ID1 + 2")]

        self.assertListEqual(lst, target)

    def test_issue(self):
        S = "* *.[v*] xxx"
        query = TokenQuery(S, self.Session)
        lst = [simple(s) for s
               in self.resource.get_corpus_joins(query.query_list[0])]

        target = [
            simple("FROM CorpusNgram"),
            simple("INNER JOIN (SELECT "
                   "              End AS End3,"
                   "              FileId AS FileId3,"
                   "              ID AS ID3,"
                   "              Start AS Start3,"
                   "              WordId AS WordId3"
                   "       FROM   Corpus) AS COQ_CORPUS_3 "
                   "ON ID3 = ID1 + 2")]

        print("\n".join(lst))
        print("\n".join(target))

        self.assertListEqual(lst, target)


class TestRenderedContext(CoqTestCase):
    """
    This test case addresses the way contexts are rendered.
    """

    resource = BaseResource

    def setUp(self):
        self.corpus = CorpusClass()
        self.corpus.resource = self.resource

    def test_parse_row1(self):
        """
        Produce a word token for a row that does not contain a query match.

        Expected behavior: the orthographic string without any embellishment
        """
        row = pd.Series(
            {'coquery_invisible_corpus_id': 1882,
             'coq_word_label_1': 'it',
             'COQ_TAG_TAG': None,
             'COQ_TAG_TYPE': None,
             'COQ_ATTRIBUTE': None,
             'COQ_TAG_ID': None})
        tags = pd.DataFrame(
            data={'COQ_TAG_TAG': {},
                  'COQ_TAG_TYPE': {},
                  'COQ_ATTRIBUTE': {},
                  'COQ_ID': {}}, dtype="object")

        self.corpus.id_list = [1878, 1879]

        target = ["it"]
        val = self.corpus.parse_row(row, tags, 1878, 1)
        self.assertListEqual(val, target)

    def test_parse_row2(self):
        """
        Produce a word token for a row that contains a query match, but which
        is not the target token.

        Expected behavior: the orthographic string wrapped into a styled <span>
        """
        row = pd.Series(
            {'coquery_invisible_corpus_id': 1882,
             'coq_word_label_1': 'it',
             'COQ_TAG_TAG': None,
             'COQ_TAG_TYPE': None,
             'COQ_ATTRIBUTE': None,
             'COQ_TAG_ID': None})
        tags = pd.DataFrame(
            data={'COQ_TAG_TAG': {},
                  'COQ_TAG_TYPE': {},
                  'COQ_ATTRIBUTE': {},
                  'COQ_ID': {}}, dtype="object")

        self.corpus.id_list = [1878, 1882]

        target = [
            "<span style='{};'>".format(
                self.corpus.resource.render_token_style),
            "it",
            "</span>"]
        val = self.corpus.parse_row(row, tags, 1878, 1)
        self.assertListEqual(val, target)

    def test_parse_row2a(self):
        """
        Produce a word token for a row that contains the second word of a
        two-word query match, but which is not the target token.

        Expected behavior: the orthographic string wrapped into a styled <span>
        """
        row = pd.Series(
            {'coquery_invisible_corpus_id': 1883,
             'coq_word_label_1': 'it',
             'COQ_TAG_TAG': None,
             'COQ_TAG_TYPE': None,
             'COQ_ATTRIBUTE': None,
             'COQ_TAG_ID': None})
        tags = pd.DataFrame(
            data={'COQ_TAG_TAG': {},
                  'COQ_TAG_TYPE': {},
                  'COQ_ATTRIBUTE': {},
                  'COQ_ID': {}}, dtype="object")

        self.corpus.id_list = [1878, 1879, 1882, 1883]

        target = [
            "<span style='{};'>".format(
                self.corpus.resource.render_token_style),
            "it",
            "</span>"]
        val = self.corpus.parse_row(row, tags, 1878, 2)
        self.assertListEqual(val, target)

    def test_parse_row3(self):
        """
        Produce a word token for a row that contains the target token.

        Expected behavior: the orthographic string wrapped into a styled <span>
        and a <b> tag
        """
        row = pd.Series(
            {'coquery_invisible_corpus_id': 1878,
             'coq_word_label_1': 'it',
             'COQ_TAG_TAG': None,
             'COQ_TAG_TYPE': None,
             'COQ_ATTRIBUTE': None,
             'COQ_TAG_ID': None})
        tags = pd.DataFrame(
            data={'COQ_TAG_TAG': {},
                  'COQ_TAG_TYPE': {},
                  'COQ_ATTRIBUTE': {},
                  'COQ_ID': {}}, dtype="object")

        self.corpus.id_list = [1878, 1882]

        target = [
            "<span style='{};'>".format(
                self.corpus.resource.render_token_style),
            "<b>", "it", "</b>",
            "</span>"]
        val = self.corpus.parse_row(row, tags, 1878, 1)
        self.assertListEqual(val, target)

    def test_parse_row3a(self):
        """
        Produce a word token for a row that is the second word of the target
        token.

        Expected behavior: the orthographic string wrapped into a styled <span>
        and a <b> tag
        """
        row = pd.Series(
            {'coquery_invisible_corpus_id': 1879,
             'coq_word_label_1': 'it',
             'COQ_TAG_TAG': None,
             'COQ_TAG_TYPE': None,
             'COQ_ATTRIBUTE': None,
             'COQ_TAG_ID': None})
        tags = pd.DataFrame(
            data={'COQ_TAG_TAG': {},
                  'COQ_TAG_TYPE': {},
                  'COQ_ATTRIBUTE': {},
                  'COQ_ID': {}}, dtype="object")

        self.corpus.id_list = [1878, 1879, 1882, 1883]

        target = ["<span style='{};'>".format(
                    self.corpus.resource.render_token_style),
                  "<b>",
                  "it",
                  "</b>",
                  "</span>"]
        val = self.corpus.parse_row(row, tags, 1878, 2)
        pd.np.testing.assert_array_equal(val, target)

    def test_parse_df_1(self):
        df = pd.DataFrame(
            {'coquery_invisible_corpus_id': {998: 2023,
                                             999: 2024,
                                             1000: 2025,
                                             1001: 2026,
                                             1002: 2027},
             'coq_word_label_1': {998: "'",
                                  999: 'said',
                                  1000: 'Alice',
                                  1001: 'to',
                                  1002: 'herself'},
             'COQ_TAG_TAG': {998: None,
                             999: None,
                             1000: None,
                             1001: None,
                             1002: None},
             'COQ_TAG_TYPE': {998: None,
                              999: None,
                              1000: None,
                              1001: None,
                              1002: None},
             'COQ_ATTRIBUTE': {998: None,
                               999: None,
                               1000: None,
                               1001: None,
                               1002: None},
             'COQ_TAG_ID': {998: None,
                            999: None,
                            1000: None,
                            1001: None,
                            1002: None}})
        tags = pd.DataFrame(
            data={'COQ_TAG_TAG': {},
                  'COQ_TAG_TYPE': {},
                  'COQ_ATTRIBUTE': {},
                  'COQ_ID': {}}, dtype="object")
        self.corpus.id_list = pd.np.array([2025])
        target = ["'",
                  "said",
                  "<span style='background: lightyellow;'>",
                  "<b>",
                  "Alice",
                  "</b>",
                  "</span>",
                  "to",
                  'herself']

        val = self.corpus.parse_df(df, tags, token_id=2025, token_width=1)
        pd.np.testing.assert_array_equal(val, target)

    def test_parse_df_2(self):
        df = pd.DataFrame(
            {'coquery_invisible_corpus_id': {998: 2023,
                                             999: 2024,
                                             1000: 2025,
                                             1001: 2026,
                                             1002: 2027},
             'coq_word_label_1': {998: "'",
                                  999: 'said',
                                  1000: 'Alice',
                                  1001: 'to',
                                  1002: 'herself'},
             'COQ_TAG_TAG': {998: None,
                             999: None,
                             1000: None,
                             1001: None,
                             1002: None},
             'COQ_TAG_TYPE': {998: None,
                              999: None,
                              1000: None,
                              1001: None,
                              1002: None},
             'COQ_ATTRIBUTE': {998: None,
                               999: None,
                               1000: None,
                               1001: None,
                               1002: None},
             'COQ_TAG_ID': {998: None,
                            999: None,
                            1000: None,
                            1001: None,
                            1002: None}})
        tags = pd.DataFrame(
            data={'COQ_TAG_TAG': {},
                  'COQ_TAG_TYPE': {},
                  'COQ_ATTRIBUTE': {},
                  'COQ_ID': {}}, dtype="object")
        self.corpus.id_list = pd.np.array([2025])
        target = ["'",
                  "said",
                  "<span style='background: lightyellow;'>",
                  "<b>",
                  "Alice",
                  "to",
                  "</b>",
                  "</span>",
                  'herself']

        val = self.corpus.parse_df(df, tags, token_id=2025, token_width=2)
        pd.np.testing.assert_array_equal(val, target)


def mock_get_available_resources(configuration):
    path = os.path.join(os.path.expanduser("~"),
                        "{}.py".format(CorpusResource.db_name))
    return {CorpusResource.name: [SQLResource,
                                  CorpusClass,
                                  path]}


provided_tests = [
                  TestCorpus, TestSuperFlat, TestCorpusWithExternal,
                  TestNGramCorpus, TestBigramCorpus,
                  TestRenderedContext,
                  ]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

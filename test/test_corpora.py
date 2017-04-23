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
from coquery.gui.linkselect import Link

import argparse

class TestCorpus(unittest.TestCase):

    resource = SQLResource
    # mock corpus module:
    resource.corpus_table = "Corpus"
    resource.corpus_id = "ID"
    resource.corpus_word_id = "WordId"
    resource.corpus_source_id = "FileId"
    resource.corpus_starttime = "Start"
    resource.corpus_endtime = "End"
    resource.word_table = "Lexicon"
    resource.word_id = "WordId"
    resource.word_label = "Word"
    resource.word_pos = "POS"
    resource.word_lemma_id = "LemmaId"
    resource.lemma_table = "Lemmas"
    resource.lemma_id = "LemmaId"
    resource.lemma_label = "Lemma"
    resource.lemma_deep_id = "DeepId"
    resource.deep_table = "Deep"
    resource.deep_id = "DeepId"
    resource.source_table = "Files"
    resource.source_id = "FileId"
    resource.source_label = "Title"
    resource.segment_id = "SegmentId"
    resource.segment_table = "Segments"
    resource.segment_starttime = "SegStart"
    resource.segment_endtime = "SegEnd"
    resource.segment_origin_id = "SegmentOrigin"

    resource.db_name = "MockCorpus"
    resource.query_item_word = "word_label"

    resource.query_item_pos = "word_pos"
    resource.query_item_lemma = "lemma_label"

    resource.annotations = {"segment": "word"}

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
    
    #def test_is_lexical(self):
        #self.assertTrue(self.resource.is_lexical("word_label"))
        #self.assertTrue(self.resource.is_lexical("cmudict.word_transcript"))
        #self.assertFalse(self.resource.is_lexical("source_label"))
        
    #def test_no_link(self):
        #table_structure = ice_ng.Resource.get_table_structure("word_table", ["word_label"])
        #self.assertEqual(table_structure["rc_features"], ['word_label', 'word_lemma_id', 'word_pos', 'word_transcript'])
        #self.assertEqual(table_structure["rc_requested_features"], ["word_label"])
        #self.assertEqual(table_structure["alias"], "COQ_WORD_TABLE")
        #self.assertEqual(table_structure["parent"], "corpus_table")

    #def test_linked(self):
        #rc_features = [x for x, _ in ice_ng.Resource.get_lexicon_variables()]
        #table_structure = buckeye.Resource.get_table_structure("word_table", rc_features)
        #self.assertEqual(table_structure["rc_features"], sorted(["word_label", "word_pos", "word_transcript", "word_lemma_id"]))
        #self.assertEqual(table_structure["alias"], "COQ_WORD_TABLE")
        #self.assertEqual(table_structure["parent"], "corpus_table")

    #def test_full_tree(self):
        #rc_features = ice_ng.Resource.get_resource_features()
        #table_structure = buckeye.Resource.get_table_structure("corpus_table", [])
        #print(table_structure)
        #self.assertEqual(table_structure["rc_features"], sorted(['corpus_source_id', 'corpus_time', 'corpus_word_id']))
        #self.assertEqual(table_structure["alias"], "COQ_CORPUS_TABLE")
        #self.assertEqual(table_structure["parent"], None)

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

    ### CORPUS JOINS

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

    @staticmethod
    def simple(s):
        s = s.replace("\n", " ")
        while "  " in s:
            s = s.replace("  ", " ")
        return s.strip()

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



def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestCorpus)])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
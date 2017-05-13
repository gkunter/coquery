# -*- coding: utf-8 -*-

from __future__ import print_function
import unittest
import sys

from .mockmodule import setup_module

setup_module("sqlalchemy")
setup_module("options")

from coquery.corpus import LexiconClass, BaseResource
from coquery.coquery import options
from coquery.defines import *
from coquery.queries import TokenQuery
from coquery.session import Session

from coquery.gui.linkselect import Link

import argparse

# mock corpus module:
BaseResource.corpus_table = "Corpus"
BaseResource.corpus_id = "ID"
BaseResource.corpus_word_id = "WordId"
BaseResource.word_table = "Lexicon"
BaseResource.word_id = "WordId"
BaseResource.word_label = "Word"
BaseResource.db_name = "MockCorpus"
BaseResource.query_item_word = "word_label"

class TestCorpus(unittest.TestCase):
    resource = BaseResource()

    def setUp(self):
        options.cfg = argparse.Namespace()
        #options.cfg.external_links = [(Link(), "word_label")]

    def test_is_lexical(self):
        self.assertTrue(self.resource.is_lexical("word_label"))
        self.assertTrue(self.resource.is_lexical("func.word_label"))
        #self.assertTrue(self.resource.is_lexical("cmudict.word_transcript"))
        #self.assertTrue(self.resource.is_lexical("func.cmudict.word_transcript"))
        self.assertFalse(self.resource.is_lexical("source_label"))
        self.assertFalse(self.resource.is_lexical("func.source_label"))

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

    def test_get_select_list(self):
        options.cfg.corpus = ""
        options.cfg.current_server = "MockConnection"
        options.cfg.MODE = QUERY_MODE_TOKENS
        options.cfg.context_mode = CONTEXT_NONE
        options.cfg.selected_features = ["word_label"]
        session = Session()

        query = TokenQuery("this is a query", session)
        session.get_max_token_count = lambda: 4
        self.assertListEqual(
            sorted(self.resource.get_select_list(query)),
            sorted(["coq_word_label_1", "coq_word_label_2",
                    "coq_word_label_3", "coq_word_label_4",
                    "coquery_invisible_corpus_id",
                    "coquery_invisible_number_of_tokens"]))

def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestCorpus)])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
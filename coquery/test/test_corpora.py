from __future__ import print_function
import unittest
import os.path
import sys

sys.path.append(os.path.normpath(os.path.join(sys.path[0], "..")))
sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../gui")))
sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../installer")))
import defines
import corpus
import options
import ICE_NG as ice_ng
import argparse

class TestCorpus(unittest.TestCase):
    resource = ice_ng.Resource
    
    def setUp(self):
        options.cfg = argparse.Namespace()
        options.cfg.external_links = {
            u'cmudict.word_transcript': (
                u'cmudict.word_table.word_label', u'word_table.word_label')}    
    
    def test_is_lexical(self):
        self.assertTrue(self.resource.is_lexical("word_label"))
        self.assertTrue(self.resource.is_lexical("func.word_label"))
        self.assertTrue(self.resource.is_lexical("cmudict.word_transcript"))
        self.assertTrue(self.resource.is_lexical("func.cmudict.word_transcript"))
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


if __name__ == '__main__':
    import timeit
    
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestCorpus)])
    unittest.TextTestRunner().run(suite)

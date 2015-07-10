from __future__ import print_function
import unittest
import os.path
import sys

sys.path.append(os.path.normpath(os.path.join(sys.path[0], "..")))
sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../corpora")))
import defines
import corpus
import buckeye


class TestBuckeyeTables(unittest.TestCase):
    def runTest(self):
        super(TestQueryToken, self).runTest()
    
    def test_no_link(self):
        table_structure = buckeye.Resource.get_table_structure("word_table", ["word_label"])
        self.assertEqual(table_structure["rc_features"], ['word_label', 'word_lemma_id', 'word_pos', 'word_transcript'])
        self.assertEqual(table_structure["rc_requested_features"], ["word_label"])
        self.assertEqual(table_structure["alias"], "COQ_WORD_TABLE")
        self.assertEqual(table_structure["parent"], "corpus_table")

    def test_linked(self):
        rc_features = [x for x, _ in buckeye.Resource.get_lexicon_variables()]
        table_structure = buckeye.Resource.get_table_structure("word_table", rc_features)
        self.assertEqual(table_structure["rc_features"], sorted(["word_label", "word_pos", "word_transcript", "word_lemma_id"]))
        self.assertEqual(table_structure["alias"], "COQ_WORD_TABLE")
        self.assertEqual(table_structure["parent"], "corpus_table")

    def test_full_tree(self):
        rc_features = buckeye.Resource.get_resource_features()
        table_structure = buckeye.Resource.get_table_structure("corpus_table", [])
        print(table_structure)
        self.assertEqual(table_structure["rc_features"], sorted(['corpus_source_id', 'corpus_time', 'corpus_word_id']))
        self.assertEqual(table_structure["alias"], "COQ_CORPUS_TABLE")
        self.assertEqual(table_structure["parent"], None)


if __name__ == '__main__':
    import timeit
    
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestBuckeyeTables)])
    unittest.TextTestRunner().run(suite)

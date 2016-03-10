# -*- coding: utf-8 -*-

""" This model tests the Coquery module textgrids."""

from __future__ import print_function

import pandas as pd
from pandas.util.testing import assert_frame_equal

import unittest
import os.path
import sys
import argparse

sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../coquery")))

# Mock module requirements:
class mock_module(object):
    pass

sys.modules["sqlalchemy"] = mock_module
sys.modules["options"] = mock_module
from corpus import CorpusClass, LexiconClass, BaseResource

import textgrids
import options

def _get_source_id(token_id):
    return [1, 1, 2, 2, 2][token_id-1]

def _get_file_data(token_id, features):
    df = pd.DataFrame({
        "Files.Filename": {0: "File1.txt", 1: "File1.txt", 2: "File2.txt", 3: "File2.txt", 4: "File2.txt"},
        "Files.Duration": {0: 10, 1: 10, 2: 20, 3: 20, 4:20},
        "Corpus.ID": {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}})
    return df

# Mock a corpus module:
BaseResource.corpus_table = "Corpus"
BaseResource.corpus_id = "ID"
BaseResource.corpus_word_id = "WordId"
BaseResource.corpus_source_id = "SourceId"
BaseResource.corpus_file_id = "FileId"
BaseResource.corpus_starttime = "Start"
BaseResource.corpus_endtime = "End"

BaseResource.word_table = "Lexicon"
BaseResource.word_id = "WordId"
BaseResource.word_label = "Word"

BaseResource.source_table = "Source"
BaseResource.source_id = "SourceId"
BaseResource.source_title = "Title"

BaseResource.file_table = "Files"
BaseResource.file_id = "FileId"
BaseResource.file_name = "Filename"
BaseResource.file_duration = "Duration"

BaseResource.db_name = "Test"


class TestModuleMethods(unittest.TestCase):
    
    def setUp(self):
        self.resource1 = BaseResource()
        lexicon = LexiconClass()
        corpus = CorpusClass()

        corpus.lexicon = lexicon

        lexicon.corpus = corpus
        lexicon.resource = self.resource1

        corpus.resource = self.resource1
        corpus.get_source_id = _get_source_id
        corpus.get_file_data = _get_file_data

        self.resource1.corpus = corpus
        self.resource1.lexicon = lexicon
        
        options.cfg = argparse.Namespace()
        self.selected_features1 = ["corpus_starttime", "corpus_endtime"]
        self.selected_features2 = ["corpus_starttime", "corpus_endtime", "word_label"]
        
        self.df1 = pd.DataFrame({
            "coquery_invisible_corpus_id": [1, 2, 3, 4, 5],
            "coq_corpus_starttime_1": [4, 5, 4, 5, 8],
            "coq_corpus_endtime_1": [4.5, 5.5, 4.5, 6, 8.5]})

        self.df2 = pd.DataFrame({
            "coquery_invisible_corpus_id": [1, 2, 3, 4, 5],
            "coq_corpus_starttime_1": [4, 5, 4, 5, 8],
            "coq_corpus_endtime_1": [4.5, 5.5, 4.5, 6, 8.5],
            "coq_word_label_1": ["this", "tree", "a", "tiny", "boat"]})

    def test_get_file_data(self):
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.resource1)
        df = _get_file_data([1, 2, 3, 4, 5], [self.resource1.corpus_id, self.resource1.file_name, self.resource1.file_duration])
        assert_frame_equal(writer.get_file_data(), df)

    def test_prepare_textgrids_number_of_grids(self):
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.resource1)
        grids = writer.prepare_textgrids()
        self.assertEqual(len(grids), len(writer.get_file_data()["Files.Filename"].unique()))
            
    def test_prepare_textgrids_feature_timing1(self):
        """
        Test the textgrid for a query that has only corpus timings, but no 
        additional lexical features.
        
        In this case, at one tier should be created that will contain 
        the corpus IDs of the tokens.
        """
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.resource1)
        grids = writer.prepare_textgrids()

        self.assertEqual(list(writer.feature_timing.keys()), ["corpus_id"])
        self.assertEqual(writer.feature_timing["corpus_id"], ("corpus_starttime", "corpus_endtime"))
        
    def test_prepare_textgrids_feature_timing2(self):
        """
        Test the textgrid for a query that has a lexical feature in addition 
        to the corpus timings (word_label).
        
        In this case, at one tier should be created that will contain 
        the word_labels of the tokens.
        """
        options.cfg.selected_features = self.selected_features2
        writer = textgrids.TextgridWriter(self.df2, self.resource1)
        grids = writer.prepare_textgrids()

        self.assertEqual(list(writer.feature_timing.keys()), ["corpus_id", "word_label"])
        self.assertEqual(writer.feature_timing["word_label"], ("corpus_starttime", "corpus_endtime"))
        self.assertEqual(writer.feature_timing["corpus_id"], ("corpus_starttime", "corpus_endtime"))

    def test_fill_grids1(self):
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.resource1)
        grids = writer.fill_grids()
        
        grid = grids["File1.txt"]
        # only one tier expected:
        self.assertEqual(len(grid.tiers), 1)
        tier = grid.tiers[0]
        # expected tiername: corpus_id
        self.assertEqual(tier.name, "corpus_id")
        # two expected intervals:
        self.assertEqual(len(tier.intervals), 2)
        interval1 = tier.intervals[0]
        self.assertEqual(interval1.start_time, 4)
        self.assertEqual(interval1.end_time, 4.5)
        self.assertEqual(interval1.text, "1")
        interval2 = tier.intervals[1]
        self.assertEqual(interval2.start_time, 5)
        self.assertEqual(interval2.end_time, 5.5)
        self.assertEqual(interval2.text, "2")

        grid = grids["File2.txt"]
        
        # only one tier expected:
        self.assertEqual(len(grid.tiers), 1)
        tier = grid.tiers[0]
        
        # expected tiername: word_label
        self.assertEqual(tier.name, "corpus_id")
        
        # three expected intervals:
        self.assertEqual(len(tier.intervals), 3)
        interval1 = tier.intervals[0]
        self.assertEqual(interval1.start_time, 4)
        self.assertEqual(interval1.end_time, 4.5)
        self.assertEqual(interval1.text, "3")
        interval2 = tier.intervals[1]
        self.assertEqual(interval2.start_time, 5)
        self.assertEqual(interval2.end_time, 6)
        self.assertEqual(interval2.text, "4")
        interval3 = tier.intervals[2]
        self.assertEqual(interval3.start_time, 8)
        self.assertEqual(interval3.end_time, 8.5)
        self.assertEqual(interval3.text, "5")
        
    def test_fill_grids2(self):
        options.cfg.selected_features = self.selected_features2
        writer = textgrids.TextgridWriter(self.df2, self.resource1)
        grids = writer.fill_grids()
        
        grid = grids["File1.txt"]
        # only one tier expected:
        self.assertEqual(len(grid.tiers), 1)
        tier = grid.tiers[0]
        # expected tiername: word_label
        self.assertEqual(tier.name, "word_label")
        # two expected intervals:
        self.assertEqual(len(tier.intervals), 2)
        interval1 = tier.intervals[0]
        self.assertEqual(interval1.start_time, 4)
        self.assertEqual(interval1.end_time, 4.5)
        self.assertEqual(interval1.text, "this")
        interval2 = tier.intervals[1]
        self.assertEqual(interval2.start_time, 5)
        self.assertEqual(interval2.end_time, 5.5)
        self.assertEqual(interval2.text, "tree")

        grid = grids["File2.txt"]
        
        # only one tier expected:
        self.assertEqual(len(grid.tiers), 1)
        tier = grid.tiers[0]
        
        # expected tiername: word_label
        self.assertEqual(tier.name, "word_label")
        
        # three expected intervals:
        self.assertEqual(len(tier.intervals), 3)
        interval1 = tier.intervals[0]
        self.assertEqual(interval1.start_time, 4)
        self.assertEqual(interval1.end_time, 4.5)
        self.assertEqual(interval1.text, "a")
        interval2 = tier.intervals[1]
        self.assertEqual(interval2.start_time, 5)
        self.assertEqual(interval2.end_time, 6)
        self.assertEqual(interval2.text, "tiny")
        interval3 = tier.intervals[2]
        self.assertEqual(interval3.start_time, 8)
        self.assertEqual(interval3.end_time, 8.5)
        self.assertEqual(interval3.text, "boat")
        
        
if __name__ == '__main__':
    import timeit
    
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestModuleMethods),
        ])
    
    print()
    print(" ----- START ----- ")
    print()
    unittest.TextTestRunner().run(suite)

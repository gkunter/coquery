# -*- coding: utf-8 -*-

""" This model tests the Coquery module textgrids."""

from __future__ import print_function

import pandas as pd
from pandas.util.testing import assert_frame_equal

import unittest
import os.path
import sys
import argparse
import collections

from .mockmodule import setup_module, MockOptions

setup_module("sqlalchemy")

from coquery.corpus import CorpusClass, LexiconClass, BaseResource
from coquery import textgrids
from coquery import options

options.cfg = MockOptions()

options.cfg.current_resources = collections.defaultdict(
    lambda: (None, None, None, None))


class MockSession(object):
    def __init__(self, resource):
        self.lexicon = LexiconClass()
        self.corpus = CorpusClass()
        self.Resource = resource

        self.corpus.lexicon = self.lexicon
        self.corpus.resource = resource
        self.lexicon.corpus = self.corpus
        self.lexicon.resource = resource

        resource.corpus = self.corpus
        resource.lexicon = self.lexicon


def _get_file_data(_, token_id, features):
    df = pd.DataFrame({
        "Filename": {0: "File1.txt", 1: "File1.txt",
                     2: "File2.txt", 3: "File2.txt", 4: "File2.txt"},
        "Duration": {0: 10, 1: 10, 2: 20, 3: 20, 4:20},
        "ID": {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}})
    return df

CorpusClass.get_file_data = _get_file_data

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


class TestTextGridModuleMethods(unittest.TestCase):
    def setUp(self):
        self.resource = BaseResource()
        self.session = MockSession(self.resource)

        self.selected_features1 = [
            "corpus_starttime", "corpus_endtime"]
        self.selected_features2 = [
            "corpus_starttime", "corpus_endtime", "word_label"]

        self.df1 = pd.DataFrame({
            "coquery_invisible_corpus_id": [1, 2, 3, 4, 5],
            "coq_corpus_starttime_1": [4, 5, 4, 5, 8],
            "coq_corpus_endtime_1": [4.5, 5.5, 4.5, 6, 8.5],
            "coquery_invisible_origin_id": [1, 1, 2, 2, 2]})

        self.df2 = pd.DataFrame({
            "coquery_invisible_corpus_id": [1, 2, 3, 4, 5],
            "coq_corpus_starttime_1": [4, 5, 4, 5, 8],
            "coq_corpus_endtime_1": [4.5, 5.5, 4.5, 6, 8.5],
            "coq_word_label_1": ["this", "tree", "a", "tiny", "boat"],
            "coquery_invisible_origin_id": [1, 1, 2, 2, 2]})

    def test_get_file_data(self):
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.session)
        df = _get_file_data(None, [1, 2, 3, 4, 5], [self.resource.corpus_id,
                                              self.resource.file_name,
                                              self.resource.file_duration])
        assert_frame_equal(writer.get_file_data(), df)

    def test_prepare_textgrids_number_of_grids(self):
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.session)
        grids = writer.prepare_textgrids()
        self.assertEqual(
            len(grids),
            len(writer.get_file_data()["Filename"].unique()))

    def test_prepare_textgrids_feature_timing1(self):
        """
        Test the textgrid for a query that has only corpus timings, but no
        additional lexical features.

        In this case, at one tier should be created that will contain
        the corpus IDs of the tokens.
        """
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.session)
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
        writer = textgrids.TextgridWriter(self.df2, self.session)
        grids = writer.prepare_textgrids()

        self.assertCountEqual(
            list(writer.feature_timing.keys()),
            ["corpus_id", "word_label"])
        self.assertEqual(
            writer.feature_timing["word_label"],
            ("corpus_starttime", "corpus_endtime"))
        self.assertEqual(
            writer.feature_timing["corpus_id"],
            ("corpus_starttime", "corpus_endtime"))

    def test_fill_grids_file1_no_labels(self):
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.session)
        grids = writer.fill_grids()

        grid = grids[("File1.txt",)]
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

    def test_fill_grids_file2_no_labels(self):
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.session)

        grids = writer.fill_grids()

        grid = grids[("File2.txt",)]

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

    def test_fill_grids_file1_labels(self):
        options.cfg.selected_features = self.selected_features2
        writer = textgrids.TextgridWriter(self.df2, self.session)
        grids = writer.fill_grids()

        grid = grids[("File1.txt", )]
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

    def test_fill_grids_file2_labels(self):
        options.cfg.selected_features = self.selected_features2
        writer = textgrids.TextgridWriter(self.df2, self.session)
        grids = writer.fill_grids()

        grid = grids[("File2.txt", )]

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


def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestTextGridModuleMethods),
        ])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    if not hasattr(TestTextGridModuleMethods, "assertCountEqual"):
        setattr(TestTextGridModuleMethods, "assertCountEqual",
                TestTextGridModuleMethods.assertItemsEqual)
    main()

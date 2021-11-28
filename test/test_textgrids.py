# -*- coding: utf-8 -*-

""" This model tests the Coquery module textgrids."""

from __future__ import print_function

import argparse
import tempfile
import pandas as pd

from coquery import options
from coquery.corpus import CorpusClass, SQLResource
from coquery.general import has_module
from coquery.connections import SQLiteConnection
from coquery.defines import QUERY_MODE_TOKENS

if has_module("tgt"):
    from coquery import textgrids

from test.testcase import CoqTestCase, run_tests


class TextgridResource(SQLResource):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "SourceId"
    corpus_file_id = "FileId"
    corpus_starttime = "Start"
    corpus_endtime = "End"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"

    source_table = "Source"
    source_id = "SourceId"
    source_title = "Title"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_duration = "Duration"

    db_name = "Test"
    query_item_word = "word_label"

    def get_file_data(self, token_id, features):
        df = pd.DataFrame({
            "Filename": {0: "File1.txt", 1: "File1.txt",
                        2: "File2.txt", 3: "File2.txt", 4: "File2.txt"},
            "Duration": {0: 10, 1: 10, 2: 20, 3: 20, 4:20},
            "ID": {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}})
        return df


class MockSession(object):
    def __init__(self):
        self.corpus = CorpusClass()
        self.Resource = TextgridResource(None, self.corpus)

        self.corpus.resource = self.Resource
        self.Resource.corpus = self.corpus


class TestTextGridModuleMethods(CoqTestCase):
    def setUp(self):
        if not has_module("tgt"):
            self.skipTest("Module 'tgt' not available.")

        options.cfg = argparse.Namespace()
        options.cfg.corpus = None
        options.cfg.MODE = QUERY_MODE_TOKENS
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.temp_path = tmp_dir
        default = SQLiteConnection("temporary", self.temp_path)
        options.cfg.current_connection = default
        options.cfg.input_separator = ","
        options.cfg.quote_char = '"'
        options.cfg.input_encoding = "utf-8"
        options.cfg.csv_restrict = None

        self.session = MockSession()
        self.resource = self.session.Resource

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

    def test_prepare_textgrids_number_of_grids(self):
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.session)
        grids = writer.prepare_textgrids()
        self.assertEqual(
            len(grids),
            len(writer.file_data["Filename"].unique()))

    def test_prepare_textgrids_feature_timing1(self):
        """
        Test the textgrid for a query that has only corpus timings, but no
        additional lexical features.

        In this case, at one tier should be created that will contain
        the corpus IDs of the tokens.
        """
        options.cfg.selected_features = self.selected_features1
        writer = textgrids.TextgridWriter(self.df1, self.session)
        writer.prepare_textgrids()

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
        writer.prepare_textgrids()

        self.assertListEqual(
            list(writer.feature_timing.keys()), ["corpus_id", "word_label"])
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


provided_tests = [TestTextGridModuleMethods]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

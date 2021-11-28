# -*- coding: utf-8 -*-

import pandas as pd
import os

from coquery.corpus import SQLResource
from coquery.connections import SQLiteConnection
from coquery.defines import SQL_SQLITE
from coquery.queries import TokenQuery

from test.testcase import tmp_path


class MockResource(SQLResource):
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
    name = "Mock Corpus"
    query_item_word = "word_label"
    query_item_pos = "word_pos"
    query_item_lemma = "lemma_label"
    query_item_transcript = "word_transcript"

    annotations = {"segment": "word"}


class MockConnection(SQLiteConnection):
    def __init__(self):
        self.path = tmp_path()
        os.makedirs(self.path)
        super().__init__("MOCK", self.path)

    def resources(self):
        return [MockResource]

    def close(self):
        os.rmdir(self.path)

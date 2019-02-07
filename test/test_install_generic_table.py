# -*- coding: utf-8 -*-
"""
This module tests the table installer module.

Run it like so:

coquery$ python -m test.test_generic_table

"""

from __future__ import unicode_literals

import os
import warnings
import tempfile
import argparse
import pandas as pd
from importlib.machinery import SourceFileLoader

from coquery.coquery import options
from coquery.options import CSVOptions
from coquery.connections import SQLiteConnection
from coquery.installer.coq_install_generic_table import BuilderClass
from test.testcase import CoqTestCase, run_tests

class TestGenericTable(CoqTestCase):
    def setUp(self):
        self.temp_name = "test_db"
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.temp_path = tmp_dir
        os.mkdir(self.temp_path)
        self.module_path = os.path.join(self.temp_path,
                                        "{}.py".format(self.temp_name))

        with tempfile.NamedTemporaryFile() as tmp:
            self.temp_file = tmp.name

        self.df = pd.DataFrame(
            data=[("tree", 4, 3.632),
                  ("apple", 5, 5.362),
                  ("man", 3, 7.169)],
            columns=["Word", "Length", "LogFreq"])

        self.df.to_csv(self.temp_file, index_label=False)

        options.cfg = argparse.Namespace()
        default = SQLiteConnection("temporary", self.temp_path)
        options.cfg.current_connection = default
        options.cfg.corpora_path = self.temp_path
        options.cfg.verbose = False

        self.dtypes = pd.Series(data=[pd.np.dtype("O"),
                                      pd.np.dtype("int64"),
                                      pd.np.dtype("float64")],
                                index=["Word", "Length", "LogFreq"])
        self.mapping = {'word': 0}

        csvoptions = CSVOptions(sep=',', header=True, quote_char='"',
                                skip_lines=0, encoding='utf-8',
                                selected_column=1, mapping=self.mapping,
                                dtypes=self.dtypes)

        self.installer = BuilderClass(dtypes=self.dtypes,
                                      mapping=self.mapping,
                                      table_options=csvoptions)

        self.installer.arguments = argparse.Namespace()
        self.installer.arguments.name = "Test"
        self.installer.arguments.metadata = None
        self.installer.arguments.lookup_ngram = None
        self.installer.arguments.only_module = False

        self.installer.arguments.path = self.temp_file
        self.installer.arguments.db_name = self.temp_name

        self.installer.setup_db(keep_db=False)
        self.installer.DB.use_database(self.installer.arguments.db_name)

    def tearDown(self):
        os.remove(self.installer.arguments.path)
        try:
            os.remove(options.cfg.current_connection.db_path(self.temp_name))
        except IOError:
            pass
        try:
            os.remove(self.module_path)
        except IOError:
            pass
        try:
            cache_path = os.path.join(self.temp_path, "__pycache__")
            for file_name in os.listdir(cache_path):
                os.remove(os.path.join(cache_path, file_name))
            os.rmdir(cache_path)
        except IOError:
            pass

        os.rmdir(self.temp_path)
        del options.cfg.current_connection

    def test_suggest_sql_types(self):
        value = self.installer.suggest_sql_types(self.dtypes, self.mapping)
        target = [("corpus_word", "Word", "VARCHAR(255)"),
                  ("corpus_x1", "Length", "INTEGER"),
                  ("corpus_x2", "LogFreq", "REAL")]

        self.assertListEqual(value, target)

    def test_module(self):
        self.installer.build()
        loader = SourceFileLoader(self.installer.arguments.db_name,
                                  self.module_path)
        res = loader.load_module().Resource

        self.assertEqual(getattr(res, "corpus_table"), "Corpus")
        self.assertEqual(getattr(res, "corpus_id"), "ID")
        self.assertEqual(getattr(res, "corpus_word"), "Word")
        self.assertEqual(getattr(res, "corpus_x1"), "Length")
        self.assertEqual(getattr(res, "corpus_x2"), "LogFreq")
        self.assertEqual(getattr(res, "corpus_file_id"), "FileId")

        self.assertEqual(getattr(res, "file_table"), "Files")
        self.assertEqual(getattr(res, "file_id"), "FileId")
        self.assertEqual(getattr(res, "file_name"), "Filename")
        self.assertEqual(getattr(res, "file_path"), "Path")

        self.assertEqual(getattr(res, "query_item_word"), "corpus_word")
        self.assertEqual(getattr(res, "name"), self.installer.arguments.name)

    def test_database(self):
        self.installer.build()

        tg_corpus = self.df
        tg_corpus["ID"] = pd.Series(range(len(tg_corpus))) + 1
        tg_corpus["FileId"] = [1] * len(tg_corpus)

        path, file_name = os.path.split(self.temp_file)
        tg_files = pd.read_csv(self.installer.arguments.path)
        tg_files = pd.DataFrame(
            {"FileId": [1],
             "Filename": [file_name],
             "Path": [path]})

        uri = options.cfg.current_connection.url(self.temp_name)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rd_corpus = pd.read_sql_table("Corpus", uri)
            rd_files = pd.read_sql_table("Files", uri)

        pd.testing.assert_frame_equal(tg_corpus.sort_index(axis="columns"),
                                      rd_corpus.sort_index(axis="columns"))
        pd.testing.assert_frame_equal(tg_files.sort_index(axis="columns"),
                                      rd_files.sort_index(axis="columns"))


provided_tests = [TestGenericTable]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

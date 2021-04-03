# -*- coding: utf-8 -*-
""" This model tests the Coquery session classes."""

from __future__ import print_function

import argparse
import os
import warnings
import pandas as pd

from coquery.coquery import options
from coquery.session import SessionInputFile, SessionCommandLine
from coquery.defines import QUERY_MODE_TOKENS, CONTEXT_NONE
from coquery.queries import TokenQuery
from coquery.errors import TokenParseError
from coquery.functions import StringExtract
from coquery.functionlist import FunctionList
from coquery.managers import Manager

from test.testcase import CoqTestCase, run_tests, tmp_filename
from test.mockclasses import MockConnection, MockResource


class TestSessionInputFile(CoqTestCase):
    def setUp(self):
        options.cfg = argparse.Namespace()
        options.cfg.corpus = None
        options.cfg.input_separator = ","
        options.cfg.quote_char = '"'
        options.cfg.input_encoding = "utf-8"
        options.cfg.csv_restrict = None
        options.cfg.current_connection = MockConnection()
        options.cfg.input_path = tmp_filename()

    def tearDown(self):
        os.remove(options.cfg.input_path)
        options.cfg.current_connection.close()

    def write_to_temp_file(self, d):
        with open(options.cfg.input_path, "w") as temp_file:
            lst = []
            if d.get("header", None):
                lst.append("{}\n".format(
                    options.cfg.input_separator.join(d["header"])))
            if d.get("queries", None):
                lst.append("{}\n".format("\n".join(d["queries"])))
            S = "".join(lst)
            temp_file.write(S)

    def test_input_file_session_init_header_only(self):
        options.cfg.file_has_headers = True
        options.cfg.query_column_number = 0
        options.cfg.skip_lines = 0

        d = {"header": ["HEADER"]}

        self.write_to_temp_file(d)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            session = SessionInputFile()

        session.prepare_queries()

        self.assertListEqual(session.header, [])
        self.assertEqual(options.cfg.query_label,
                         d["header"][options.cfg.query_column_number])
        self.assertListEqual(session.query_list, [])

    def test_input_file_session_init_simple_file(self):
        options.cfg.file_has_headers = True
        options.cfg.query_column_number = 1
        options.cfg.skip_lines = 0

        d = {"header": ["HEADER"],
             "queries": ["QUERY"]}

        self.write_to_temp_file(d)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            session = SessionInputFile()

        session.prepare_queries()

        self.assertListEqual(session.header, [])
        self.assertEqual(options.cfg.query_label,
                         d["header"][options.cfg.query_column_number - 1])

        self.assertEqual(len(session.query_list),
                         len(d.get("queries", [])))
        self.assertListEqual(
            [x.query_string for x in session.query_list],
            d.get("queries", []))

    def test_input_file_session_init_query_space(self):
        options.cfg.file_has_headers = True
        options.cfg.query_column_number = 1
        options.cfg.skip_lines = 0

        d = {"header": ["HEADER"],
             "queries": ["QUERY ", "QUERY"]}

        self.write_to_temp_file(d)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            session = SessionInputFile()

        session.prepare_queries()

        self.assertListEqual(session.header, [])
        self.assertEqual(options.cfg.query_label,
                         d["header"][options.cfg.query_column_number - 1])

        self.assertEqual(len(session.query_list),
                         len(d.get("queries", [])))
        self.assertListEqual(
            [x.query_string for x in session.query_list],
            d.get("queries", []))

    def test_input_file_session_init_header_and_content(self):
        options.cfg.file_has_headers = True
        options.cfg.query_column_number = 1
        options.cfg.skip_lines = 0

        queries = ["QUERY1", "QUERY2"]

        d = {"header": ["HEADER"],
             "queries": queries}

        self.write_to_temp_file(d)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            session = SessionInputFile()

        session.prepare_queries()

        self.assertListEqual(session.header, [])
        self.assertEqual(options.cfg.query_label,
                         d["header"][options.cfg.query_column_number - 1])
        self.assertEqual(len(session.query_list), len(queries))
        self.assertListEqual(
            [x.query_string for x in session.query_list], queries)

    def test_input_file_session_init_complex_file(self):
        options.cfg.file_has_headers = True
        options.cfg.query_column_number = 2
        options.cfg.skip_lines = 0

        queries = ["QUERY1", "QUERY2"]
        d = {"header": ["DATA1", "QUERY", "DATA2"],
             "queries": ["tmp,{},tmp".format(s) for s in queries]}

        self.write_to_temp_file(d)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            session = SessionInputFile()

        session.prepare_queries()

        self.assertListEqual(session.header, ["DATA1", "DATA2"])
        self.assertEqual(options.cfg.query_label,
                         d["header"][options.cfg.query_column_number - 1])
        self.assertEqual(len(session.query_list), len(queries))
        self.assertListEqual(
            [x.query_string for x in session.query_list], queries)

    def test_issue249(self):
        options.cfg.file_has_headers = True
        options.cfg.query_column_number = 2
        options.cfg.skip_lines = 0

        d = {"header": ["DATA1", "QUERY", "DATA2"],
             "queries": ['tmp,\"#constitute .[v*]\",tmp']}

        self.write_to_temp_file(d)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            session = SessionInputFile()

        session.prepare_queries()
        with self.assertRaises(TokenParseError):
            session.prepare_queries()


class TestSessionMethods(CoqTestCase):
    def setUp(self):
        options.cfg = argparse.Namespace()
        options.cfg.corpus = None
        options.cfg.MODE = QUERY_MODE_TOKENS
        options.cfg.current_connection = MockConnection()
        options.cfg.input_separator = ","
        options.cfg.quote_char = '"'
        options.cfg.input_encoding = "utf-8"
        options.cfg.drop_on_na = True
        options.cfg.benchmark = False
        options.cfg.query_list = []
        options.cfg.column_names = {}
        options.cfg.verbose = True
        options.cfg.stopword_list = []
        options.cfg.context_mode = CONTEXT_NONE
        options.cfg.context_left = 3
        options.cfg.context_right = 5
        options.cfg.sample_matches = False

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.session = SessionCommandLine([])

        self.session.Resource = MockResource
        self.manager = Manager()
        options.cfg.managers = {
            MockResource.name: {QUERY_MODE_TOKENS: self.manager}}

    def test_translate_header_multicolumn_functions(self):
        val = ["abx"] * 5 + ["a"] * 5 + ["bx"] * 5
        df = pd.DataFrame({"coq_word_label_1": val})
        func = StringExtract(columns=["coq_word_label_1"], pat="(a).*(x)")
        self.session.column_functions = FunctionList([func])
        self.manager.set_column_order(df.columns)
        df = self.manager.process(df, self.session)
        self.assertListEqual(
            [self.session.translate_header(x) for x in df.columns],
            ["Word",
             "{} (match 1)".format(
                 func.get_label(self.session, self.manager)),
             "{} (match 2)".format(
                 func.get_label(self.session, self.manager))])

    def test_translate_header_context_labels(self):
        df = pd.DataFrame({"coq_context_left": ["A A A"] * 5,
                           "coq_context_right": ["B B B B B"] * 5})
        self.assertListEqual(
            [self.session.translate_header(x) for x in df.columns],
            ["Left context(3)", "Right context(5)"])


class MockQuery1(TokenQuery):
    """
    This query mocks a search for the search string ABACK|ABARINGE in a
    dictionary-like resource. Calling run() and insert_static_data()
    yields the following data frame:

                                            0         1
    coq_corpus_word_1                   ABACK  ABARINGE
    coquery_invisible_corpus_id         78928       373
    coq_corpus_x32_1                        4      <NA>
    coquery_invisible_dummy                 0         0
    coquery_invisible_number_of_tokens      1         1
    coquery_invisible_origin_id             1         1
    coquery_invisible_query_id              1         1

    """

    def __init__(self, session):
        super().__init__("ABACK|ABARINGE", session)

    @staticmethod
    def run(*args, **kwargs):
        df = pd.DataFrame(
            {'coq_corpus_word_1': {0: 'ABACK', 1: 'ABARINGE'},
             'coquery_invisible_corpus_id': {0: 78928, 1: 373}})
        df["coq_corpus_x32_1"] = pd.Series({0: 4, 1: pd.NA})
        return df

    @staticmethod
    def insert_static_data(df):
        df['coquery_invisible_dummy'] = pd.Series({0: 0, 1: 0})
        df['coquery_invisible_number_of_tokens'] = pd.Series({0: 1, 1: 1})
        df['coquery_invisible_origin_id'] = pd.Series({0: 1, 1: 1})
        df['coquery_invisible_query_id'] = pd.Series({0: 1, 1: 1})
        return df


class MockQuery2a(TokenQuery):
    """
    This query mocks a search for the search string ABACK in a
    dictionary-like resource. Calling run() and insert_static_data()
    yields the following data frame:

                                            0
    coq_corpus_word_1                   ABACK
    coquery_invisible_corpus_id         78928
    coq_corpus_x32_1                        4
    coquery_invisible_dummy                 0
    coquery_invisible_number_of_tokens      1
    coquery_invisible_origin_id             1
    coquery_invisible_query_id              1

    """

    def __init__(self, session):
        super().__init__("ABACK", session)

    @staticmethod
    def run(*args, **kwargs):
        df = pd.DataFrame(
            {'coq_corpus_word_1': {0: 'ABACK'},
             'coquery_invisible_corpus_id': {0: 78928}})
        df["coq_corpus_x32_1"] = pd.Series({0: 4})
        return df

    @staticmethod
    def insert_static_data(df):
        df['coquery_invisible_dummy'] = pd.Series({0: 0})
        df['coquery_invisible_number_of_tokens'] = pd.Series({0: 1})
        df['coquery_invisible_origin_id'] = pd.Series({0: 1})
        df['coquery_invisible_query_id'] = pd.Series({0: 1, 1: 1})
        return df


class MockQuery2b(TokenQuery):
    """
    This query mocks a search for the search string ABARINGE in a
    dictionary-like resource. Calling run() and insert_static_data()
    yields the following data frame:

                                               0
    coq_corpus_word_1                   ABARINGE
    coquery_invisible_corpus_id              373
    coq_corpus_x32_1                        <NA>
    coquery_invisible_dummy                    0
    coquery_invisible_number_of_tokens         1
    coquery_invisible_origin_id                1
    coquery_invisible_query_id                 1

    """

    def __init__(self, session):
        super().__init__("ABARINGE", session)

    @staticmethod
    def run(*args, **kwargs):
        df = pd.DataFrame(
            {'coq_corpus_word_1': {0: 'ABARINGE'},
             'coquery_invisible_corpus_id': {0: 373}})
        df["coq_corpus_x32_1"] = pd.Series({0: pd.NA})
        return df

    @staticmethod
    def insert_static_data(df):
        df['coquery_invisible_dummy'] = pd.Series({0: 0})
        df['coquery_invisible_number_of_tokens'] = pd.Series({0: 1})
        df['coquery_invisible_origin_id'] = pd.Series({0: 1})
        df['coquery_invisible_query_id'] = pd.Series({0: 1})
        return df


class TestSessionQueries(CoqTestCase):
    def setUp(self):

        options.cfg = argparse.Namespace()
        options.cfg.current_connection = MockConnection()
        options.cfg.query_list = []
        options.cfg.MODE = QUERY_MODE_TOKENS
        options.cfg.managers = {}
        options.cfg.filter_list = []
        options.cfg.column_order = []
        options.cfg.gui = False
        options.cfg.corpus = None
        options.cfg.verbose = False
        options.cfg.stopword_list = []
        options.cfg.drop_on_na = False
        options.cfg.sample_matches = False
        options.cfg.output_path = None
        options.cfg.output_separator = ","
        options.cfg.digits = 3
        options.cfg.align_quantified = False
        options.cfg.selected_features = ["coq_corpus_word", "coq_corpus_x32"]
        options.cfg.drop_duplicates = False
        options.cfg.context_mode = CONTEXT_NONE
        options.cfg.column_names = []

    def test_run_queries1(self):
        """
        This test asserts that a simple word-alternative query (e.g.
        ABACK|ABARINGE) produces the same results as two separate single-word
        queries ABACK and ABARINGE, respectively.
        """

        session = SessionCommandLine()
        session.db_engine = options.cfg.current_connection.get_engine("dummy")
        session.Resource = MockResource

        session.query_list = [MockQuery1(session)]
        session.run_queries()
        df1 = session.data_table

        session.query_list = [MockQuery2a(session), MockQuery2b(session)]
        session.run_queries()
        df2 = session.data_table.reset_index(drop=True)

        pd.testing.assert_frame_equal(df1, df2)


provided_tests = [
                  TestSessionInputFile,
                  TestSessionMethods,
                  TestSessionQueries]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

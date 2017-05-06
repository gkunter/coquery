# -*- coding: utf-8 -*-
""" This model tests the Coquery session classes."""

from __future__ import print_function

import unittest
import argparse
import tempfile
import os

from coquery.coquery import options
from coquery.session import SessionInputFile
from coquery.defines import QUERY_MODE_TOKENS
from coquery.errors import TokenParseError

class TestSessionInputFile(unittest.TestCase):
    def setUp(self):
        options.cfg = argparse.Namespace()
        options.cfg.corpus = None
        options.cfg.MODE = QUERY_MODE_TOKENS
        options.cfg.current_server = "MockConnection"
        options.cfg.input_separator = ","
        options.cfg.quote_char = '"'
        options.cfg.input_encoding = "utf-8"

        self.temp_file = tempfile.NamedTemporaryFile("w")
        options.cfg.input_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        os.remove(options.cfg.input_path)

    def write_to_temp_file(self, d):
        with open(options.cfg.input_path, "w") as temp_file:
            l = []
            if d.get("header", None):
                l.append("{}\n".format(
                    options.cfg.input_separator.join(d["header"])))
            if d.get("queries", None):
                l.append("{}\n".format("\n".join(d["queries"])))
            S = "".join(l)
            temp_file.write(S)

    def test_input_file_session_init_header_only(self):
        options.cfg.file_has_headers = True
        options.cfg.query_column_number = 0
        options.cfg.skip_lines = 0

        d = {"header": ["HEADER"]}

        self.write_to_temp_file(d)

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
             "queries": ["QUERY ","QUERY"]}

        self.write_to_temp_file(d)

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

    def test_input_file_session_init_simple_file(self):
        options.cfg.file_has_headers = True
        options.cfg.query_column_number = 1
        options.cfg.skip_lines = 0

        queries = ["QUERY1", "QUERY2"]

        d = {"header": ["HEADER"],
             "queries": queries}

        self.write_to_temp_file(d)

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

        queries = ["QUERY1", "QUERY2"]
        d = {"header": ["DATA1", "QUERY", "DATA2"],
             "queries": ['tmp,\"#constitute .[v*]\",tmp']}

        self.write_to_temp_file(d)

        session = SessionInputFile()
        with self.assertRaises(TokenParseError):
            session.prepare_queries()

def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestSessionInputFile),
        ])

    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

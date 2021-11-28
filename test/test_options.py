# -*- coding: utf-8 -*-
"""
This module tests the the options module.

Run it like so:

coquery$ python -m test.test_options

"""

from __future__ import print_function

from coquery.options import decode_query_string, encode_query_string
from test.testcase import CoqTestCase, run_tests


class TestQueryStringParse(CoqTestCase):
    """
    Run tests for encoding and decoding query strings for the configuration
    file.

    The content of the query string field is stored in the configuration
    file as a comma-separated list. In order to correctly handle query
    strings that contain themselves commas, the content of that field needs
    to be encoded correctly (i.e. quotation marks need to be added.

    These tests check whether encoding and decoding works correctly.
    """
    def runTest(self):
        super(TestQueryStringParse, self).runTest()

    def test_parse(self):
        self.assertEqual(decode_query_string("abc,def"), "abc\ndef")
        self.assertEqual(decode_query_string('"abc,def"'), "abc,def")
        self.assertEqual(decode_query_string('\\"abc'), '"abc')
        self.assertEqual(decode_query_string('"*{1,2}"'), "*{1,2}")
        self.assertEqual(decode_query_string('"*{1,2}",abc'), "*{1,2}\nabc")

    def test_encode(self):
        self.assertEqual(encode_query_string("abc"), '"abc"')
        self.assertEqual(encode_query_string("abc\ndef"), '"abc","def"')
        self.assertEqual(encode_query_string("abc,def"), '"abc,def"')

    def test_bidirect(self):
        for S in ["abc", '"abc"', "abc\ndef", "[v*] *{1,2} [n*]",
                  "abc,def", '""', ",,,", "\\?\n\\*"]:
            self.assertEqual(decode_query_string(encode_query_string(S)), S)


provided_tests = [TestQueryStringParse]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

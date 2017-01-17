""" This model tests the Coquery token parsers."""

from __future__ import print_function

import unittest

from coquery.options import decode_query_string, encode_query_string

class TestQueryStringParse(unittest.TestCase):
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
        for S in ["abc", '"abc"', "abc\ndef","[v*] *{1,2} [n*]",
                  "abc,def", '""', ",,,", "\\?\n\\*"]:
            self.assertEqual(decode_query_string(encode_query_string(S)), S)

def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestQueryStringParse)])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
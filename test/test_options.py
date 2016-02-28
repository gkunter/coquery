""" This model tests the Coquery token parsers."""

from __future__ import print_function

import unittest
import os.path
import sys

sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../coquery")))

from options import decode_query_string, encode_query_string

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
        self.assertItemsEqual(decode_query_string("abc,def"), "abc\ndef")
        self.assertItemsEqual(decode_query_string('"abc,def"'), "abc,def")
        self.assertItemsEqual(decode_query_string('\\"abc'), '"abc')
        self.assertItemsEqual(decode_query_string('"*{1,2}"'), "*{1,2}")
        self.assertItemsEqual(decode_query_string('"*{1,2}",abc'), "*{1,2}\nabc")

    def test_encode(self):
        self.assertEqual(encode_query_string("abc"), '"abc"')
        self.assertEqual(encode_query_string("abc\ndef"), '"abc","def"')
        self.assertEqual(encode_query_string("abc,def"), '"abc,def"')
        
    def test_bidirect(self):
        for S in ["abc", '"abc"', "abc\ndef","[v*] *{1,2} [n*]",
                  "abc,def", '""', ",,,", "\\?\n\\*"]:
            self.assertEqual(decode_query_string(encode_query_string(S)), S)

if __name__ == '__main__':
    import timeit
    
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestQueryStringParse)])
    
    print()
    print(" ----- START ----- ")
    print()
    unittest.TextTestRunner().run(suite)

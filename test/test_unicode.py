# -*- coding: utf-8 -*-
""" This model tests the Coquery module unicode.py."""

from __future__ import print_function

from coquery.unicode import utf8
from test.testcase import CoqTestCase, run_tests


class TestUnicodeModuleMethods(CoqTestCase):
    def test_namespace_conflict(self):
        """
        Test whether the module name 'unicode' interferes with the built-in
        type 'unicode' in Python 2.7.
        """
        if hasattr(__builtins__, "unicode"):
            self.assertEqual(getattr(__builtins__, "unicode")("test"),
                             u"test")

    def test_utf8_type(self):
        s1 = b'unaccented text for testing'
        s2 = 'unaccented text for testing'
        s3 = u'unaccented text for testing'
        s4 = 'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        s5 = u'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        # test types:
        self.assertEqual(type(utf8(s1)), type(u""))
        self.assertEqual(type(utf8(s2)), type(u""))
        self.assertEqual(type(utf8(s3)), type(u""))
        self.assertEqual(type(utf8(s4)), type(u""))
        self.assertEqual(type(utf8(s5)), type(u""))

    def test_utf8_content(self):
        s1a = 'unaccented text for testing'
        s1b = b'unaccented text for testing'
        s1u = u'unaccented text for testing'

        s2a = 'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        s2u = u'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'

        # test content:
        self.assertEqual(utf8(s1a), s1u)
        self.assertEqual(utf8(s1b), s1u)
        self.assertEqual(utf8(s2a), s2u)


provided_tests = [TestUnicodeModuleMethods]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

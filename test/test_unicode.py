# -*- coding: utf-8 -*-
""" This model tests the Coquery module unicode.py."""

from __future__ import print_function

import unittest
import sys
import os

sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../coquery")))
sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../coquery/gui")))

from unicode import utf8
from gui.pyqt_compat import QtCore

class TestModuleMethods(unittest.TestCase):
    def test_namespace_conflict(self):
        """
        Test whether the module name 'unicode' interferes with the built-in 
        type 'unicode' in Python 2.7.
        
        There are two tests. For Python 2.7, the return value of 
        unicode("test") is tested against the explicit unicode string u"test".
        For Python 3.x, a call to unicode() is expected to raise a NameError,
        as this type is not defined.
        """
        if sys.version_info < (3, 0):
            self.assertEqual(unicode("test"), u"test")
        else:
            self.assertRaises(NameError, lambda: unicode())
        
    def test_utf8_type(self):
        s1 = b'unaccented text for testing'
        s2 = 'unaccented text for testing'
        s3 = u'unaccented text for testing'
        s4 = 'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        s5 = u'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        s6 = QtCore.QString(s2)
        s7 = QtCore.QString(s4)
        
        # test types:
        self.assertEqual(type(utf8(s1)), type(u""))
        self.assertEqual(type(utf8(s2)), type(u""))
        self.assertEqual(type(utf8(s3)), type(u""))
        self.assertEqual(type(utf8(s4)), type(u""))
        self.assertEqual(type(utf8(s5)), type(u""))
        self.assertEqual(type(utf8(s6)), type(u""))
        self.assertEqual(type(utf8(s7)), type(u""))
        
    def test_utf8_content(self):
        s1a = 'unaccented text for testing'
        s1b = QtCore.QString(s1a)
        s1c = b'unaccented text for testing'
        s1u = u'unaccented text for testing'

        s2a = 'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        s2b = QtCore.QString(s2a)
        s2u  = u'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        
        # test content:
        self.assertEqual(utf8(s1a), s1u)
        self.assertEqual(utf8(s1b), s1u)
        self.assertEqual(utf8(s1c), s1u)
        self.assertEqual(utf8(s2a), s2u)
        self.assertEqual(utf8(s2b), s2u)
        
if __name__ == '__main__':
    import timeit
    
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestModuleMethods),
        ])
    
    print()
    print(" ----- START ----- ")
    print()
    unittest.TextTestRunner().run(suite)

# -*- coding: utf-8 -*-

"""
This module tests the string replacement used in the ICE-NG installer to
fix the faulty character encodings.
"""

from __future__ import unicode_literals

import unittest
import sys, os

sys.path.append(os.path.join(sys.path[0], "../installer"))
from coq_install_ice_ng import *

class TestReplace(unittest.TestCase):
    def test_replace(self):
        replace_func = ICENigeriaBuilder.replace_encoding_errors
        
        pairs = [
            ("YarâAdua", "Yar’Adua"),
            ("-âEkidâ", "-‘Ekid’"),
            ("ĕkíd", "ÄkÃ­d"),
            ]
        
        for mangled, correct in pairs:
            self.assertEqual(replace_func(mangled), correct)

if __name__ == '__main__':
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestReplace),
        ])
    unittest.TextTestRunner().run(suite)

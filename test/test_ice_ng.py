# -*- coding: utf-8 -*-

"""
test_ice_ng.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import unittest
import sys, os

sys.path.append(os.path.join(sys.path[0], "../coquery/installer"))
sys.path.append(os.path.join(sys.path[0], "../coquery"))
from coq_install_ice_ng import *

class TestReplace(unittest.TestCase):
    def test_replace(self):
        replace_func = BuilderClass._replace_encoding_errors
        
        pairs = [
            ("YarâAdua", "Yar’Adua"),
            ("-âEkidâ", "-‘Ekid’"),
            ("ĕkíd", "ÄkÃ­d"),
            ]
        
        for mangled, correct in pairs:
            self.assertEqual(replace_func(mangled), correct)

    def test_count_frequency(self):
        builder = BuilderClass()
        print(builder.get_corpus_features())
        print(builder.get_lexicon_features())
        
if __name__ == '__main__':
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestReplace),
        ])
    unittest.TextTestRunner().run(suite)

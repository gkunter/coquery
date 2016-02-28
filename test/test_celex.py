# -*- coding: utf-8 -*-

"""
test_celex.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import unittest
import sys, os

sys.path.append(os.path.join(sys.path[0], "../coquery"))
sys.path.append(os.path.join(sys.path[0], "../coquery/installer"))
from coq_install_celex import *

class TestCELEX(unittest.TestCase):
    def test_dia_to_unicode(self):
        self.assertEqual(dia_to_unicode("cause c#el`ebre"), "cause célèbre")
        self.assertEqual(dia_to_unicode("#eclat"), "éclat")
        self.assertEqual(dia_to_unicode("`a la"), "à la")
        self.assertEqual(dia_to_unicode('k"ummel'), "kümmel")
        self.assertEqual(dia_to_unicode('d#eb^acle'), "débâcle")
        self.assertEqual(dia_to_unicode('fa,cade'), "façade")
        self.assertEqual(dia_to_unicode('sm@aland'), "småland")
        
if __name__ == '__main__':
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestCELEX),
        ])
    unittest.TextTestRunner().run(suite)

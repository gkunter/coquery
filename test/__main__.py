# -*- coding: utf-8 -*-

"""
__main__.py is part of Coquery.

Copyright (c) 2016-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function

import unittest
import sys
from pprint import pprint


def main():
    test_list = []
    args = sys.argv[1:]
    if args:
        print("Running tests for these modules:")
        print()
        pprint(sorted(args), indent=4)
        print()
    else:
        print("Running complete tests")

    if not args or "bibliography" in args:
        from test.test_bibliography import provided_tests
        test_list += provided_tests

    if not args or "colorizers" in args:
        from test.test_colorizers import provided_tests
        test_list += provided_tests

    if not args or "connections" in args:
        from test.test_connections import provided_tests
        test_list += provided_tests

    if not args or "corpus" in args:
        from test.test_corpora import provided_tests
        test_list += provided_tests

    if not args or "corpusbuilder" in args:
        from test.test_corpusbuilder import provided_tests
        test_list += provided_tests

    if not args or "filters" in args:
        from test.test_filters import provided_tests
        test_list += provided_tests

    if not args or "functionlist" in args:
        from test.test_functionlist import provided_tests
        test_list += provided_tests

    if not args or "functions" in args:
        from test.test_functions import provided_tests
        test_list += provided_tests

    if not args or "general" in args:
        from test.test_general import provided_tests
        test_list += provided_tests

    if not args or "installer" in args:
        from test.test_install_generic import provided_tests
        test_list += provided_tests
        from test.test_install_generic_table import provided_tests
        test_list += provided_tests
        from test.test_install_generic_package import provided_tests
        test_list += provided_tests

        from test.test_celex import provided_tests
        test_list += provided_tests
        from test.test_ice_ng import provided_tests
        test_list += provided_tests
        from test.test_obc2 import provided_tests
        test_list += provided_tests
        from test.test_switchboard import provided_tests
        test_list += provided_tests

    if not args or "managers" in args:
        from test.test_managers import provided_tests
        test_list += provided_tests

    if not args or "options" in args:
        from test.test_options import provided_tests
        test_list += provided_tests

    if not args or "queries" in args:
        from test.test_queries import provided_tests
        test_list += provided_tests

    if not args or "sessions" in args:
        from test.test_sessions import provided_tests
        test_list += provided_tests

    if not args or "tables" in args:
        from test.test_tables import provided_tests
        test_list += provided_tests

    if not args or "textgrids" in args:
        from test.test_textgrids import provided_tests
        test_list += provided_tests

    if not args or "tokens" in args:
        from test.test_tokens import provided_tests
        test_list += provided_tests

    if not args or "unicode" in args:
        from test.test_unicode import provided_tests
        test_list += provided_tests

    if not args or "visualizer" in args:
        from test.vis.barcodeplot import provided_tests
        test_list += provided_tests
        from test.vis.test_barplot import provided_tests
        test_list += provided_tests
        from test.vis.test_beeswarmplot import provided_tests
        test_list += provided_tests
        from test.vis.test_boxplot import provided_tests
        test_list += provided_tests
        from test.vis.test_bubbleplot import provided_tests
        test_list += provided_tests
        from test.vis.heatbarplot import provided_tests

    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in test_list])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

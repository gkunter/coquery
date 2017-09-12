# -*- coding: utf-8 -*-
"""
This module tests the general.py module.

Run it like so:

coquery$ python -m test.test_general

"""


from __future__ import print_function
import unittest
import sys
import tempfile
import os

from coquery.general import check_fs_case_sensitive


class TestGeneral(unittest.TestCase):

    def test_check_fs_case_sensitive(self):
        if sys.platform == "linux":
            self.assertTrue(check_fs_case_sensitive(os.path.expanduser("~")))
        elif sys.platform in ("win32", "darwin"):
            self.assertFalse(check_fs_case_sensitive(os.path.expanduser("~")))
        else:
            raise NotImplementedError


provided_tests = [TestGeneral]


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

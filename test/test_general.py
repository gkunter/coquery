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
import numpy as np

from coquery.general import check_fs_case_sensitive, pretty


class TestGeneral(unittest.TestCase):

    def test_check_fs_case_sensitive(self):
        if sys.platform == "linux":
            self.assertTrue(check_fs_case_sensitive(os.path.expanduser("~")))
        elif sys.platform in ("win32", "darwin"):
            self.assertFalse(check_fs_case_sensitive(os.path.expanduser("~")))
        else:
            raise NotImplementedError

class TestPretty(unittest.TestCase):
    def assertListEqual(self, l1, l2):
        if (any([type(x) == object for x in l1]) or
                any([type(x) == object for x in l2])):
            return super(TestPretty, self).assertListEqual(l1, l2)
        else:
            if not np.allclose(l1, l2):
                raise self.failureException(
                    "Lists not equal enough:\n\t{}\n\t{}".format(l1, l2))
            return all(np.equal(l1, l2))

    def test_pretty_1(self):
        vrange = (0, 100)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [0, 20, 40, 60, 80])

    def test_pretty_1a(self):
        vrange = (5, 95)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [0, 20, 40, 60, 80])

    def test_pretty_2(self):
        vrange = (0, 100)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0, 25, 50, 75])

    def test_pretty_2a(self):
        vrange = (5, 95)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0, 25, 50, 75])

    def test_pretty_3(self):
        vrange = (0, 1000)
        bins = pretty(vrange, 10)
        self.assertListEqual(list(bins),
                             [0, 100, 200, 300, 400, 500, 600, 700, 800, 900])

    def test_pretty_3a(self):
        vrange = (5, 995)
        bins = pretty(vrange, 10)
        self.assertListEqual(list(bins),
                             [0, 100, 200, 300, 400, 500, 600, 700, 800, 900])

    def test_pretty_3b(self):
        vrange = (50, 950)
        bins = pretty(vrange, 10)
        self.assertListEqual(list(bins),
                             [0, 100, 200, 300, 400, 500, 600, 700, 800, 900])

    def test_pretty_4(self):
        vrange = (-200, 200)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [-200, -100, 0, 100])

    def test_pretty_4a(self):
        vrange = (-195, 195)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [-200, -100, 0, 100])

    def test_pretty_5(self):
        vrange = (-200, -100)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [-200, -175, -150, -125])

    def test_pretty_6(self):
        vrange = (100, 200)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [100, 125, 150, 175])

    def test_pretty_7(self):
        vrange = (0, 10)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [0, 2, 4, 6, 8])

    def test_pretty_8(self):
        vrange = (0, 10)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0, 2.5, 5, 7.5])

    def test_pretty_9(self):
        vrange = (0, 1)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0, 0.25, 0.5, 0.75])

    def test_pretty_10(self):
        vrange = (0.5, 1)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0.5, 0.625, 0.75, 0.875])

    def test_pretty_10a(self):
        vrange = (0.05, 0.10)
        bins = pretty(vrange, 4)
        self.assertListEqual(bins,
                             [0.0, 0.025, 0.05, 0.075])

    def test_pretty_11(self):
        vrange = (0, 136)
        bins = pretty(vrange, 2)
        self.assertListEqual(list(bins),
                             [0, 75])

    def test_pretty_12(self):
        vrange = (13452, 32787)
        bins = pretty(vrange, 2)
        self.assertListEqual(list(bins),
                             [13400, 23400])

    def test_pretty_12a(self):
        vrange = (13452, 32787)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [13400, 18400, 23400, 28400])

    def test_pretty_13(self):
        vrange = (13452, 33061)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [13400, 17400, 21400, 25400, 29400])

    def test_pretty_14(self):
        vrange = (134528, 330612)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [134000, 174000, 214000, 254000, 294000])

    def test_pretty_15(self):
        vrange = (20033, 32399)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [20000, 23000, 26000, 29000, 32000])

    def test_pretty_16(self):
        vrange = (75, 136)
        bins = pretty(vrange, 7)
        self.assertListEqual(list(bins),
                             [70, 80, 90, 100, 110, 120, 130])




provided_tests = [TestGeneral, TestPretty]


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
This module tests the general.py module.

Run it like so:

coquery$ python -m test.test_visualizationdesigner

"""
import pandas as pd

from test.testcase import CoqTestCase
from visualizationdesigner import uniques


class TestUniques(CoqTestCase):
    """
    Test the uniques() module function from visualizationdesigner.py
    """
    def test_uniques_1(self):
        val = pd.Series(["C", "B", "A", "C", "A"])
        target = ["A", "B", "C"]
        self.assertEqual(uniques(val), target)

    def test_uniques_2(self):
        val = pd.Series([7, 3, 5, 1, 7, 3, 5])
        target = [1, 3, 5, 7]
        self.assertEqual(uniques(val), target)

    def test_uniques_na_1(self):
        val = pd.Series(["B", "A", pd.NA, "B", pd.NA])
        target = ["A", "B"]
        self.assertEqual(uniques(val), target)

    def test_uniques_na_2(self):
        val = pd.Series([7, 3, pd.NA, 1, 7, 3, pd.NA])
        target = [1, 3, 7]
        self.assertEqual(uniques(val), target)


provided_tests = [
    TestUniques,
]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

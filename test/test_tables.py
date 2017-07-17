# -*- coding: utf-8 -*-
"""
This module tests the tables module.

Run it like so:

coquery$ python -m test.test_tables

"""

from __future__ import print_function

import unittest

from coquery import tables


class TestColumns(unittest.TestCase):
    def test_init(self):
        name = "Label"
        dtype = "VARCHAR(30)"
        col = tables.Column(name, dtype)
        self.assertEqual(col.name, name)
        self.assertEqual(col.data_type, dtype)

    def test_set_properties(self):
        name = "Label"
        dtype = "VARCHAR(30)"
        col = tables.Column(name, dtype)
        col.name = name[::-1]
        col.data_type = dtype[::-1]
        self.assertEqual(col.name, name[::-1])
        self.assertEqual(col.data_type, dtype[::-1])

    def test_defaults(self):
        col = tables.Column("", "")
        self.assertFalse(col.is_identifier)
        self.assertFalse(col.key)

    def test_base_type_1(self):
        name = "Label"
        dtype = "VARCHAR(30)"
        col = tables.Column(name, dtype)
        self.assertEqual(col.base_type, "VARCHAR")

    def test_base_type_2(self):
        name = "Value"
        dtype = "LONGINT(32) UNSIGNED NOT NULL"
        col = tables.Column(name, dtype)
        self.assertEqual(col.base_type, "LONGINT")

    def test_is_numeric_1(self):
        name = "Label"
        dtype = "VARCHAR(30)"
        col = tables.Column(name, dtype)
        self.assertFalse(col.is_numeric())

    def test_is_numeric_2(self):
        name = "Value"
        dtype = "LONGINT(32) UNSIGNED NOT NULL"
        col = tables.Column(name, dtype)
        self.assertTrue(col.is_numeric())


class TestIdentifier(TestColumns):
    def test_defaults(self):
        col = tables.Identifier("", "")
        self.assertTrue(col.is_identifier)
        self.assertFalse(col.key)


class TestLinks(TestColumns):
    def test_defaults(self):
        col = tables.Link("", "")
        self.assertFalse(col.is_identifier)
        self.assertTrue(col.key)


class TestTables(unittest.TestCase):
    def test_init(self):
        name = "Lexicon"
        tab = tables.Table(name)
        self.assertEqual(tab.name, name)
        self.assertListEqual(tab.columns, [])
        self.assertEqual(tab.primary, None)

    def test_add(self):
        raise NotImplementedError

    def test_get_or_insert(self):
        raise NotImplementedError

    def test_find(self):
        raise NotImplementedError

    def test_add_column(self):
        raise NotImplementedError

    def test_get_column(self):
        raise NotImplementedError

    def test_suggest_data_type(self):
        raise NotImplementedError

    def test_get_create_string(self):
        raise NotImplementedError


provided_tests = TestColumns, TestIdentifier, TestLinks, TestTables


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(case)
         for case in provided_tests])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

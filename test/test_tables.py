# -*- coding: utf-8 -*-
"""
This module tests the tables module.

Run it like so:

coquery$ python -m test.test_tables

"""

from __future__ import print_function

from coquery import tables
from coquery.defines import SQL_MYSQL, SQL_SQLITE
from test.testcase import CoqTestCase, run_tests


def simple(s):
    s = s.replace("\n", " ")
    s = s.replace("\t", " ")
    while "  " in s:
        s = s.replace("  ", " ")
    return s.strip()


class TestColumns(CoqTestCase):
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
        dtype = "INT(32) UNSIGNED NOT NULL"
        col = tables.Column(name, dtype)
        self.assertEqual(col.base_type, "INT")

    def test_is_numeric_1(self):
        name = "Label"
        dtype = "VARCHAR(30)"
        col = tables.Column(name, dtype)
        self.assertFalse(col.is_numeric())

    def test_is_numeric_2(self):
        name = "Value"
        dtype = "INT(32) UNSIGNED NOT NULL"
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

    def test_get_dtype(self):
        linked_tab = tables.Table("LinkedTable")
        linked_tab.add_column(tables.Identifier("LinkId", "MEDIUMINT"))

        col = tables.Link("LinkID", linked_tab.name)
        dtype = col.get_dtype([linked_tab])

        self.assertEqual(dtype, "MEDIUMINT")


class TestTables(CoqTestCase):
    def setUp(self):
        self.name = "Table"
        self.table = tables.Table(self.name)

        # default linked table:
        self.linked_tab = tables.Table("LinkedTable")
        self.linked_tab.add_column(tables.Identifier("LinkId", "MEDIUMINT"))
        self.existing_tables = [self, self.linked_tab]

        # default columns:
        self.identifier = tables.Identifier("ID", "INT UNSIGNED NOT NULL")
        self.col1 = tables.Column("Label", "VARCHAR(30)")
        self.col2 = tables.Column("Value", "INT UNSIGNED NOT NULL")
        self.col3 = tables.Column("Category",
                                  "ENUM('val1','val2','val3') NOT NULL")
        self.link = tables.Link("LinkId", self.linked_tab.name)

        # default values:
        self.val1 = {"Label": "test1", "Value": 1,
                     "Category": "val1", "LinkId": 100}
        self.val2 = {"Label": "test2", "Value": 2,
                     "Category": "val2", "LinkId": 101}
        self.val3 = {"Label": "test3", "Value": 3,
                     "Category": "val3", "LinkId": 102}

    def test_init(self):
        name = "Table"
        self.assertEqual(self.table.name, name)
        self.assertListEqual(self.table.columns, [])
        self.assertEqual(self.table.primary, None)

    def _add_all_test_columns(self):
        self.table.add_column(self.identifier)
        self.table.add_column(self.col1)
        self.table.add_column(self.col2)
        self.table.add_column(self.col3)
        self.table.add_column(self.link)

    def _add_default_values(self):
        self.table.add(self.val1)
        self.table.add(self.val2)
        self.table.add(self.val3)

    def test_get_column_order(self):
        self.table.add_column(self.identifier)
        self.table.add_column(self.col1)
        self.table.add_column(self.col2)

        self.assertListEqual(self.table.get_column_order(),
                             [self.col1.name, self.col2.name])

    def test_add_column(self):
        self._add_all_test_columns()

        self.assertEqual(len(self.table.get_column_order()), 4)
        self.assertEqual(self.table.get_column_order()[0], self.col1.name)
        self.assertEqual(self.table.get_column_order()[1], self.col2.name)
        self.assertEqual(self.table.get_column_order()[2], self.col3.name)
        self.assertEqual(self.table.get_column_order()[3], self.link.name)

        # duplicate columns raise ValueError:
        self.assertRaises(ValueError, self.table.add_column, self.col1)
        self.assertRaises(ValueError, self.table.add_column, self.col2)
        self.assertRaises(ValueError, self.table.add_column, self.col3)

        # No exceptions raised:
        self.table.add_column(self.identifier)
        self.table.add_column(self.link)

    def test_get_column(self):
        self._add_all_test_columns()

        self.assertEqual(self.table.get_column(self.identifier.name),
                         self.identifier)
        self.assertEqual(self.table.get_column(self.col1.name), self.col1)
        self.assertEqual(self.table.get_column(self.col2.name), self.col2)
        self.assertEqual(self.table.get_column(self.col3.name), self.col3)
        self.assertEqual(self.table.get_column(self.link.name), self.link)

    def test_get_create_string_SQLite(self):
        self._add_all_test_columns()

        s = self.table.get_create_string(SQL_SQLITE, self.existing_tables)
        self.assertEqual(simple(s),
                         simple("""
            ID INT NOT NULL PRIMARY KEY,
            Label VARCHAR(30) COLLATE NOCASE,
            Value INT NOT NULL,
            Category VARCHAR(4) NOT NULL COLLATE NOCASE,
            LinkId {}
            """.format(self.linked_tab.primary.data_type)))

    def test_get_create_string_MySQL(self):
        self._add_all_test_columns()

        s = self.table.get_create_string(SQL_MYSQL, self.existing_tables)
        self.assertEqual(simple(s),
                         simple("""
            `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
            `Label` VARCHAR(30),
            `Value` INT UNSIGNED NOT NULL,
            `Category` ENUM('val1','val2','val3') NOT NULL,
            `LinkId` {},
            PRIMARY KEY (`ID`)
            """.format(self.linked_tab.primary.data_type)))

    def test_get_create_string_SQLite_nonunique_id(self):
        tab = tables.Table("Table")
        tab.add_column(
            tables.Identifier("ID", "MEDIUMINT NOT NULL", unique=False))

        s = tab.get_create_string(SQL_SQLITE, [])
        self.assertEqual(simple(s),
                         simple("""
            ID_primary INT NOT NULL PRIMARY KEY,
            ID MEDIUMINT NOT NULL
            """))

    def test_get_create_string_MySQL_nonunique_id(self):
        tab = tables.Table("Table")
        tab.add_column(
            tables.Identifier("ID", "MEDIUMINT NOT NULL", unique=False))

        s = tab.get_create_string(SQL_MYSQL, [])
        self.assertEqual(simple(s),
                         simple("""
            `ID_primary` INT NOT NULL AUTO_INCREMENT,
            `ID` MEDIUMINT NOT NULL,
            PRIMARY KEY (`ID_primary`)
            """))

    def test_get_create_string_duplicate_ids(self):
        tab = tables.Table("Table")
        tab.add_column(tables.Identifier("ID", "MEDIUMINT"))
        tab.add_column(tables.Link("ID", "MEDIUMINT", create=False))

        s = tab.get_create_string(SQL_SQLITE, [])
        self.assertEqual(simple(s),
                         simple("ID MEDIUMINT PRIMARY KEY"))

    def test_add(self):
        self._add_all_test_columns()
        self._add_default_values()

        self.assertEqual(self.table._current_id, 3)
        self.assertEqual(len(self.table._add_cache), 3)
        self.assertEqual(len(self.table._add_lookup), 3)
        self.assertEqual(self.table._add_cache[0],
                         (1, "test1", 1, "val1", 100))
        self.assertEqual(self.table._add_cache[1],
                         (2, "test2", 2, "val2", 101))
        self.assertEqual(self.table._add_cache[2],
                         (3, "test3", 3, "val3", 102))
        self.assertEqual(self.table._add_lookup[("test1", 1, "val1", 100)], 1)
        self.assertEqual(self.table._add_lookup[("test2", 2, "val2", 101)], 2)
        self.assertEqual(self.table._add_lookup[("test3", 3, "val3", 102)], 3)

    def test_add_with_id(self):
        self._add_all_test_columns()
        val_with_id1 = dict(self.val1)
        val_with_id1.update({"ID": 10})
        val_with_id2 = dict(self.val2)
        val_with_id2.update({"ID": 11})
        val_with_id3 = dict(self.val3)
        val_with_id3.update({"ID": 12})

        self.table.add_with_id(val_with_id1)
        self.table.add_with_id(val_with_id2)
        self.table.add_with_id(val_with_id3)

        self.assertEqual(self.table._current_id, 12)
        self.assertEqual(len(self.table._add_cache), 3)
        self.assertEqual(len(self.table._add_lookup), 3)
        self.assertEqual(self.table._add_cache[0],
                         (10, "test1", 1, "val1", 100))
        self.assertEqual(self.table._add_cache[1],
                         (11, "test2", 2, "val2", 101))
        self.assertEqual(self.table._add_cache[2],
                         (12, "test3", 3, "val3", 102))

    def test_get_or_insert(self):
        self._add_all_test_columns()
        self._add_default_values()

        new1 = {"Label": "new1", "Value": 1,
                "Category": "val1", "LinkId": 100}
        new2 = {"Label": "new2", "Value": 1,
                "Category": "val2", "LinkId": 100}
        new3 = {"Label": "new3", "Value": 1,
                "Category": "val3", "LinkId": 100}

        id_val1_before = self.table.get_or_insert(self.val1)
        id_val2_before = self.table.get_or_insert(self.val2)
        id_val3_before = self.table.get_or_insert(self.val3)
        id_new1 = self.table.get_or_insert(new1)
        id_new2 = self.table.get_or_insert(new2)
        id_new3 = self.table.get_or_insert(new3)
        id_val1_after = self.table.get_or_insert(self.val1)
        id_val2_after = self.table.get_or_insert(self.val2)
        id_val3_after = self.table.get_or_insert(self.val3)

        self.assertEqual(id_val1_before, 1)
        self.assertEqual(id_val2_before, 2)
        self.assertEqual(id_val3_before, 3)
        self.assertEqual(id_val1_after, 1)
        self.assertEqual(id_val2_after, 2)
        self.assertEqual(id_val3_after, 3)
        self.assertEqual(id_new1, 4)
        self.assertEqual(id_new2, 5)
        self.assertEqual(id_new3, 6)
        self.assertEqual(len(self.table._add_lookup), 6)

    def test_suggest_data_type(self):
        self.skipTest("Test not implemeneted.")

    def test_find(self):
        self.skipTest("Test not implemeneted.")


provided_tests = [TestColumns, TestIdentifier, TestLinks, TestTables]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

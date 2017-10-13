# -*- coding: utf-8 -*-
"""
This module tests the connections module.

Run it like so:

coquery$ python -m test.test_connections

"""

from __future__ import unicode_literals

import unittest
import os

from coquery.connections import (Connection,
                                 MySQLConnection,
                                 SQLiteConnection)
from coquery.defines import SQL_MYSQL, SQL_SQLITE, DEFAULT_CONFIGURATION
from coquery.corpus import BaseResource, CorpusClass
from coquery.general import get_home_dir


class TestConnection(unittest.TestCase):
    def setUp(self):
        self.name = "test_virtual"
        self._db_type = "TEST"

    def test_init(self):
        con1 = Connection(self.name)
        self.assertEqual(con1.name, self.name)
        self.assertEqual(con1._db_type, None)

        con2 = Connection(self.name, self._db_type)
        self.assertEqual(con2.name, self.name)
        self.assertEqual(con2._db_type, self._db_type)

    def test_add_resource(self):
        res_name1 = "Corpus1"
        res1 = BaseResource()
        res1.name = res_name1
        cor1 = CorpusClass()

        res_name2 = "Corpus2"
        res2 = BaseResource()
        res2.name = res_name2
        cor2 = CorpusClass()

        con = Connection(self.name)

        con.add_resource(res1, cor1)
        con.add_resource(res2, cor2)

        self.assertEqual(con.get_resource(res_name1), (res1, cor1))
        self.assertEqual(con.get_resource(res_name2), (res2, cor2))

    def test_count_resources(self):
        res_name1 = "Corpus1"
        res1 = BaseResource()
        res1.name = res_name1
        cor1 = CorpusClass()

        res_name2 = "Corpus2"
        res2 = BaseResource()
        res2.name = res_name2
        cor2 = CorpusClass()

        con = Connection(self.name)

        con.add_resource(res1, cor1)
        self.assertEqual(con.count_resources(), 1)
        con.add_resource(res1, cor1)
        self.assertEqual(con.count_resources(), 1)
        con.add_resource(res2, cor2)
        self.assertEqual(con.count_resources(), 2)

    def test_remove_resource(self):
        res_name = "Corpus1"
        res = BaseResource()
        res.name = res_name
        cor = CorpusClass()
        con = Connection(self.name)

        con.add_resource(res, cor)
        self.assertEqual(con.count_resources(), 1)
        con.remove_resource(res_name)
        self.assertEqual(con.count_resources(), 0)



class TestMySQLConnection(unittest.TestCase):
    def setUp(self):
        self.name = "test_mysql"
        self.host = "127.0.0.1"
        self.port = 3306
        self.user = "mysql"
        self.password = "abcde" # just because I can
        self.db_name = "coq_corpus"

    def test_init(self):
        con = MySQLConnection(
            self.name, self.host, self.port, self.user, self.password)

        self.assertEqual(con._db_type, SQL_MYSQL)
        self.assertEqual(con.name, self.name)
        self.assertEqual(con.host, self.host)
        self.assertEqual(con.port, self.port)
        self.assertEqual(con.user, self.user)
        self.assertEqual(con.password, self.password)

    def test_url_1(self):
        con = MySQLConnection(
            self.name, self.host, self.port, self.user, self.password)

        template = ("mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
                    "?charset=utf8mb4&local_infile=1")
        url = template.format(user=self.user,
                              password=self.password,
                              host=self.host,
                              port=self.port,
                              dbname=self.db_name)

        self.assertEqual(url, con.url(self.db_name))

    def test_url_2(self):
        con = MySQLConnection(
            self.name, self.host, self.port, self.user, self.password,
            params=[])

        template = "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
        url = template.format(user=self.user,
                              password=self.password,
                              host=self.host,
                              port=self.port,
                              dbname=self.db_name)

        self.assertEqual(url, con.url(self.db_name))


class TestSQLiteConnection(unittest.TestCase):
    def setUp(self):
        self.name = "test_sqlite"
        self.db_path = os.path.expanduser("~/tmp")
        self.db_name = "coq_corpus"

    def test_init(self):
        con = SQLiteConnection(self.name, self.db_path)
        self.assertEqual(con._db_type, SQL_SQLITE)
        self.assertEqual(con.name, self.name)
        self.assertEqual(con.path, self.db_path)

    def test_default(self):
        con = SQLiteConnection(DEFAULT_CONFIGURATION)

        self.assertEqual(con.path,
                         os.path.join(get_home_dir(),
                                      "connections",
                                      DEFAULT_CONFIGURATION))

    def test_url(self):
        con = SQLiteConnection(self.name, self.db_path)

        path = os.path.join(self.db_path, "{}.db".format(self.db_name))
        url = "sqlite+pysqlite:///{path}".format(path=path)

        self.assertEqual(url, con.url(self.db_name))


provided_tests = (TestConnection, TestMySQLConnection, TestSQLiteConnection)


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

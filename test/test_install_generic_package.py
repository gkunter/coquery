# -*- coding: utf-8 -*-
"""
This module tests the package installer module.

Run it like so:

coquery$ python -m test.test_install_generic_package

"""

from __future__ import unicode_literals

import unittest
import os
import argparse

from coquery.defines import SQL_SQLITE, SQL_MYSQL, DEFAULT_CONFIGURATIION
from coquery.sqlwrap import SqlDB
from coquery.coquery import options
from coquery.installer.coq_install_generic_package import BuilderClass
from coquery.tables import Table
from coquery.connections import SQLiteConnection, MySQLConnection

from .mockmodule import MockOptions


class MockTable(Table):
    def __init__(self, *args, **kwargs):
        self.content = {}

    def get_or_insert(self, d):
        word = d["Word"]
        if word not in self.content:
            self.content[word] = (len(self.content) + 1, d)
        return self.content[word][0]


class TestGenericPackage(unittest.TestCase):
    def setUp(self):
        options.cfg = MockOptions()
        db_type = SQL_SQLITE

        options.cfg.verbose = False
        default = SQLiteConnection(DEFAULT_CONFIGURATIION)
        mysql = MySQLConnection(name=SQL_MYSQL,
                                host="127.0.0.1",
                                port=3306,
                                user="coquery", password="coquery")
        options.cfg.connections = {DEFAULT_CONFIGURATIION: default,
                                   SQL_MYSQL: mysql}

        options.cfg.database_path = os.path.expanduser("~/tmp")
        options.cfg.corpora_path = os.path.expanduser("~/tmp")
        options.cfg.adhoc_path = os.path.expanduser("~/tmp")

        self.installer = BuilderClass(
            package=os.path.expanduser("~/ALICE.coq"))
        self.installer.arguments = argparse.Namespace()
        self.installer.arguments.name = "ALICE2"
        self.installer.arguments.db_name = "coq_alice2"
        self.installer.arguments.db_type = db_type

        if db_type == SQL_SQLITE:
            self.installer.arguments.db_host = ""
            self.installer.arguments.db_port = ""
            self.installer.arguments.db_user = ""
            self.installer.arguments.db_password = ""
        else:
            self.installer.arguments.db_host = "127.0.0.1"
            self.installer.arguments.db_port = 3306
            self.installer.arguments.db_user = "coquery"
            self.installer.arguments.db_password = "coquery"

        self.installer.arguments.only_module = False
        self.installer.arguments.metadata = None
        self.installer.arguments.lookup_ngram = None
        self.installer.arguments.path = os.path.expanduser("~/ALICE.coq")

        db = SqlDB(
            self.installer.arguments.db_host,
            self.installer.arguments.db_port,
            self.installer.arguments.db_type,
            self.installer.arguments.db_user,
            self.installer.arguments.db_password,
            self.installer.arguments.db_name)
        db.use_database(self.installer.arguments.db_name)
        self.installer.DB = db

    def test_build(self):
        self.installer.build()


def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestGenericPackage),
        ])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

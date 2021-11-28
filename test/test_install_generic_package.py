# -*- coding: utf-8 -*-
"""
This module tests the package installer module.

Run it like so:

coquery$ python -m test.test_install_generic_package

"""

from __future__ import unicode_literals

import unittest
import os
import sys
import argparse
import tempfile
import zipfile
import json
from pathlib import Path

from coquery.coquery import options
from coquery.installer.coq_install_generic_package import BuilderClass
from coquery.connections import SQLiteConnection, MySQLConnection
from coquery.corpus import SQLResource
from test.testcase import CoqTestCase, run_tests


class CorpusResource(SQLResource):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word = "Word"


class TestGenericPackage(CoqTestCase):
    def create_package(self, name):
        raise NotImplementedError


    def setUp(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.temp_path = tmp_dir

        Path(self.temp_path).mkdir(parents=True, exist_ok=True)

        self.temp_name = "test_db"
        self.file_name = f"{self.temp_name}.coq"
        self.package_path = os.path.join(self.temp_path, self.file_name)

        options.cfg = argparse.Namespace()
        default = SQLiteConnection("temporary", self.temp_path)
        options.cfg.current_connection = default
        options.cfg.corpora_path = self.temp_path
        options.cfg.verbose = False

        options.cfg.database_path = self.temp_path
        options.cfg.corpora_path = self.temp_path
        options.cfg.adhoc_path = self.temp_path

        self.create_package(self.temp_name)

        self.installer = BuilderClass(package=self.package_path)
        self.installer.arguments = argparse.Namespace()
        self.installer.arguments.name = "TEST"
        self.installer.arguments.db_name = "test_db"

        self.installer.arguments.only_module = False
        self.installer.arguments.metadata = None
        self.installer.arguments.lookup_ngram = None
        self.installer.arguments.path = self.package_path

    def tearDown(self):
        for file_name in os.listdir(self.temp_path):
            os.remove(os.path.join(self.temp_path, file_name))
        os.rmdir(self.temp_path)

    def test_build(self):
        self.installer.build()


provided_tests = [
    TestGenericPackage,
    ]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

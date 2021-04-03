# -*- coding: utf-8 -*-
"""
This module tests the corpus builder module.

Run it like so:

coquery$ python -m test.test_install_generic

"""

from __future__ import unicode_literals

import os
import argparse

from coquery.coquery import options
from coquery.installer.coq_install_generic import BuilderClass
from coquery.tables import Table
from coquery.options import CSVOptions
from test.testcase import CoqTestCase, run_tests, tmp_filename, tmp_path


class MockTable(Table):
    def __init__(self, *args, **kwargs):
        self.content = {}

    def get_or_insert(self, d):
        word = d["Word"]
        if word not in self.content:
            self.content[word] = (len(self.content) + 1, d)
        return self.content[word][0]


DATA_FILES = ["file1.txt", "file2.txt", "file3.txt", "file999.txt"]


class TestGeneric(CoqTestCase):

    def setUp(self):
        options.cfg = argparse.Namespace()

        self.installer = BuilderClass()

        self.installer.arguments = argparse.Namespace()
        self.installer.arguments.name = "MOCK_BUILD"

        self.installer.arguments.metaoptions = CSVOptions(
            sep=",", header=True, quote_char='"', skip_lines=None,
            encoding="utf-8")

        self.installer.arguments.metadata = tmp_filename()

        with open(self.installer.arguments.metadata, "w") as meta_file:
            meta_file.write("Filename,Time,Code\n")
            meta_file.write("file1.txt,2017,A\n")
            meta_file.write("file2.txt,2018,B\n")
            meta_file.write("file3.txt,2019,C\n")
            meta_file.write("file4.txt,2019,D\n")

        self.installer.arguments.path = tmp_path()

        os.mkdir(self.installer.arguments.path)
        for file_name in DATA_FILES:
            open(os.path.join(self.installer.arguments.path,
                              file_name), "a").close()

    def tearDown(self):
        for file_name in DATA_FILES:
            os.remove(os.path.join(self.installer.arguments.path, file_name))
        os.rmdir(self.installer.arguments.path)

    def test_add_metadata(self):
        self.installer.add_metadata(self.installer.arguments.path, 0)

    def test_has_metadata(self):
        self.installer.add_metadata(self.installer.arguments.path, 0)

        self.assertTrue(self.installer.has_metadata("file3.txt"))

        # even though file4.txt is in the meta data file, there is no
        # corresponding source data file, so the file should be discarded:
        self.assertFalse(self.installer.has_metadata("file4.txt"))
        self.assertFalse(self.installer.has_metadata("file5.txt"))


provided_tests = [TestGeneric]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

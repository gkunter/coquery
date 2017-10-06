# -*- coding: utf-8 -*-

"""
coq_install_generic_package.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import time
import re
import logging
import zipfile
import json
import os
import codecs
import tempfile

from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.corpusbuilder import (Column, Identifier)
from coquery.general import utf8
from coquery.defines import SQL_SQLITE
from coquery import options

function_str = """
    @staticmethod
    def get_name():
        return "{name}"

    @staticmethod
    def get_db_name():
        return "{db_name}"

    @staticmethod
    def get_title():
        return "{name}: imported from {package}"

    _is_adhoc = True

    @staticmethod
    def get_description():
        return ['''{description}''']
    """


class BuilderClass(BaseCorpusBuilder):
    def __init__(self, gui=False, package=None):
        self._package = package
        self._widget = gui
        self._chunk_signal = None
        self._file_signal = None

        db_type = (options.cfg.server_configuration[
                    options.cfg.current_server]["type"])

        # reconstruct the resource features from the tables.json file.
        zf = zipfile.ZipFile(package)
        tables = json.loads(utf8(zf.read("tables.json")))

        # first pass: create all corpus features:
        for tab in tables:
            features = tables[tab]["Fields"]
            primary = tables[tab]["Primary"]
            name = tables[tab]["Name"]
            setattr(self, "{}_table".format(tab), name)
            for rc_feature in features:
                setattr(self, rc_feature, features[rc_feature]["Name"])

        # second pass: create all columns:
        for tab in tables:
            features = tables[tab]["Fields"]
            primary = getattr(self, tables[tab]["Primary"])
            columns = []

            for rc_feature in features:
                feature = features[rc_feature]
                name = feature["Name"]
                dtype = "{} {}".format(feature["Type"], feature["Null"])
                if db_type == SQL_SQLITE:
                    dtype = dtype.replace("unsigned ", "")
                if name == primary:
                    columns.append(Identifier(name, dtype))
                else:
                    columns.append(Column(name, dtype))

            setattr(self, "{}_columns".format(tab), columns)
            self.auto_create.append(tab)

        super(BuilderClass, self).__init__(gui)

    def chunkSignal(self):
        return self._chunk_signal

    def setChunkSignal(self, signal):
        self._chunk_signal = signal

    def fileSignal(self):
        return self._file_signal

    def setFileSignal(self, signal):
        self._file_signal = signal

    def build_write_module(self):
        path = self.get_module_path(self.arguments.db_name)

        desc_template = """<p>The corpus '{name}' was installed on {date}.
            It was imported from the package file <code>{package}</code>.</p>
            """
        self._description = desc_template.format(
            name=self.arguments.name,
            date=utf8(time.strftime("%c")),
            package=self._package)

        zf = zipfile.ZipFile(self._package)
        for x in zf.namelist():
            if x.endswith(".py"):
                module_name = x
                break
        content = utf8(zf.read(module_name))
        zf.close()

        content = re.sub("(from coquery.corpus import \*)",
                         r"\1\nfrom coquery.corpusbuilder import *",
                         content)
        content = re.sub(
            "(    name = )'.*'",
            r"\1'{}'".format(self.arguments.name), content)
        content = re.sub(
            "(    display_name = )'.*'",
            r"\1'{}'".format(self.arguments.name), content)
        content = re.sub(
            "(    db_name = )'.*'",
            r"\1'{}'".format(self.arguments.db_name.lower()),
            content)
        self.module_content = content
        with codecs.open(path, "w", encoding="utf-8") as output_file:
            output_file.write(self.module_content)
            logging.info("Corpus module %s written." % path)

    def build_load_files(self):
        zf = zipfile.ZipFile(self._package)
        try:
            temp_dir = tempfile.mkdtemp()
            for file_name in [x for x in zf.namelist()
                              if x.endswith(".csv")]:
                try:
                    temp_name = zf.extract(file_name, temp_dir)
                    self.process_file(temp_name)
                finally:
                    os.remove(temp_name)
        finally:
            os.rmdir(temp_dir)

    def process_file(self, path):
        table = getattr(self,
                        "{}_table".format(
                            os.path.splitext(os.path.basename(path))[0]))
        if self.fileSignal():
            self.fileSignal().emit(table, "Reading table ")
        self.DB.load_file(path,
                          encoding="utf-8",
                          table=table,
                          index=None,
                          header="infer",
                          chunksize=250000,
                          chunksignal=self.chunkSignal())
        self.commit_data()

    @classmethod
    def get_file_list(cls, path, file_filter, sort=True):
        return []

    def create_installer_module(self):
        """
        """
        functions = function_str.format(
            name=self.arguments.name, db_name=self.arguments.db_name,
            package=self._package, description=self._description)
        file_name = self.get_module_path(self.arguments.db_name)

        with codecs.open(file_name, "r") as input_file:
            source = input_file.readlines()
        in_docstring = False
        for x in source:
            x = re.sub("(class )Resource\(.*\):",
                       r"\1BuilderClass(BaseCorpusBuilder):{}\n{}".format(
                           functions,
                           "    description = ['''{}''']\n".format(
                               self._description)),
                       x)

            if x.startswith('"""'):
                if not in_docstring:
                    in_docstring = True
                    yield '"""'
                else:
                    in_docstring = False
            if in_docstring:
                continue

            yield x

# -*- coding: utf-8 -*-

"""
coq_install_generic.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import os
import re
import numpy as np
import logging
import time

from coquery.corpusbuilder import BaseCorpusBuilder, disambiguate_label
from coquery.corpusbuilder import (Column, Link, Identifier)
from coquery.capturer import Capturer
from coquery.general import utf8


class BuilderClass(BaseCorpusBuilder):
    file_name = None
    MAX_VARCHAR_LENGTH = 255

    def suggest_sql_types(self, dtypes, mapping):
        """
        Create a list with of tuples representing the SQL data types for the
        data table.

        The tuples are in order of the columns in the data table, and each
        tuple consists of four elements: (1) the resource feature name
        assigned to that data table column, (2) the display name (either based
        on the data table headers or generated on the fly, (3) the suggested
        SQL data type based on the Numpy data type of the column.
        """
        lst = []
        for i, label in enumerate(dtypes.index.values):
            if i in mapping.values():
                query_type = dict(zip(mapping.values(), mapping.keys()))[i]
                rc_feature = f"corpus_{query_type}"
            else:
                rc_feature = f"corpus_x{i}"
            if dtypes[i] == object:
                # It would be nice to be able to determine the maximum length
                # if string data columns from the data frame, like so:
                #
                # max_length = df[i].map(len).max()
                #
                # But at this stage, the data frame is not available yet, so
                # we have to use a fixed maximum string length:
                dtype = f"VARCHAR({self.MAX_VARCHAR_LENGTH})"
            elif dtypes[i] == np.float64:
                dtype = "REAL"
            elif dtypes[i] == np.int64:
                dtype = "INTEGER"
            lst.append((rc_feature, label, dtype))
        return lst

    def __init__(self,
                 gui=False, mapping=None, dtypes=None, table_options=None):
        # all corpus builders have to call the inherited __init__ method:
        super(BuilderClass, self).__init__(gui)
        self._table_options = table_options
        self._is_tagged_label = "table-based corpus"

        _columns = []

        feature_map = dict(zip(mapping.values(), mapping.keys()))
        for i, label in enumerate(dtypes.index.values):
            if i in mapping.values():
                query_type = feature_map[i]
                rc_feature = f"corpus_{query_type}"
            else:
                rc_feature = f"corpus_x{i}"
            if dtypes[i] == object:
                # It would be nice to be able to determine the maximum length
                # if string data columns from the data frame, like so:
                #
                # max_length = df[i].map(len).max()
                #
                # But at this stage, the data frame is not available yet, so
                # we have to use a fixed maximum string length:
                max_length = 128
                dtype = f"VARCHAR({max_length})"
            elif dtypes[i] == np.float64:
                dtype = "REAL"
            elif dtypes[i] == np.int64:
                dtype = "INTEGER"
            _columns.append((i, rc_feature, label, dtype))
            setattr(self, rc_feature, label)

        self.corpus_table = "Corpus"
        # ensure that the internal labels don't interfere with labels that
        # exist as column headers:
        self.corpus_id = disambiguate_label("ID", dtypes.index.values)
        self.corpus_file_id = disambiguate_label("FileId", dtypes.index.values)

        self.file_table = "Files"
        self.file_id = "FileId"
        self.file_name = "Filename"
        self.file_path = "Path"

        self.create_table_description(
            self.file_table,
            [Identifier(self.file_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.file_name, "VARCHAR(2048) NOT NULL"),
             Column(self.file_path, "VARCHAR(2048) NOT NULL")])

        lst = [Identifier(self.corpus_id, "BIGINT(20) UNSIGNED NOT NULL"),
               Link(self.corpus_file_id, self.file_table)]

        for _, _, label, dtype in _columns:
            lst.append(Column(label, dtype))

        self.create_table_description(self.corpus_table, lst)

    def create_description_text(self):
        desc_template = """<p>The table-based corpus '{name}' was created on
            {date}. It contains {tokens} text tokens.</p>
            <p>Directory:<br/> <code>{path}</code></p>
            <p>File:<br/><code>{file}</code></p>"""

        path, filename = os.path.split(self.arguments.path)
        description = [desc_template.format(
            name=utf8(self.arguments.name),
            date=utf8(time.strftime("%c")),
            tokens=self._corpus_id,
            path=path,
            file=filename)]
        return description

    def validate_path(self, path):
        return path == self.arguments.path

    @classmethod
    def validate_files(cls, file_list):
        return True

    def build_load_files(self):
        capt = Capturer(stderr=True)
        with capt:
            df = self._table_options.read_file(self.arguments.path)
        for x in capt:
            s = f"File {self.arguments.path} – {x}"
            logging.warning(s)
            print(s)

        if not self._table_options.header:
            df.columns = [f"X{num}" for num in df.columns]
        else:
            df.columns = [re.sub("[^a-zA-Z0-9_]", "_", x) for x in df.columns]
        df[self.corpus_file_id] = 1
        self.DB.load_dataframe(df, self.corpus_table, self.corpus_id)
        self.store_filename(self.arguments.path)
        self._corpus_id = len(df)

    @classmethod
    def get_file_list(cls, path, file_filter, sort=True):
        return []


def main():
    BuilderClass().build()


if __name__ == "__main__":
    main()

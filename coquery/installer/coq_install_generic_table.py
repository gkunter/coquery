# -*- coding: utf-8 -*-

"""
coq_install_generic.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import re
import pandas as pd
import logging

from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.corpusbuilder import (Column, Link, Identifier)
from coquery.capturer import Capturer


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
                rc_feature = "corpus_{}".format(query_type)
            else:
                rc_feature = "corpus_x{}".format(i)
            if dtypes[i] == object:
                # It would be nice to be able to determine the maximum length
                # if string data columns from the data frame, like so:
                #
                # max_length = df[i].map(len).max()
                #
                # But at this stage, the data frame is not available yet, so
                # we have to use a fixed maximum string length:
                dtype = "VARCHAR({})".format(self.MAX_VARCHAR_LENGTH)
            elif dtypes[i] == pd.np.float64:
                dtype = "REAL"
            elif dtypes[i] == pd.np.int64:
                dtype = "INTEGER"
            lst.append((rc_feature, label, dtype))
        return lst

    def __init__(self,
                 gui=False, mapping=None, dtypes=None, table_options=None):
        # all corpus builders have to call the inherited __init__ method:
        super(BuilderClass, self).__init__(gui)
        self._table_options = table_options
        _columns = []

        for i, label in enumerate(dtypes.index.values):
            if i in mapping.values():
                query_type = dict(zip(mapping.values(), mapping.keys()))[i]
                rc_feature = "corpus_{}".format(query_type)
            else:
                rc_feature = "corpus_x{}".format(i)
            if dtypes[i] == object:
                # It would be nice to be able to determine the maximum length
                # if string data columns from the data frame, like so:
                #
                # max_length = df[i].map(len).max()
                #
                # But at this stage, the data frame is not available yet, so
                # we have to use a fixed maximum string length:
                max_length = 128
                dtype = "VARCHAR({})".format(max_length)
            elif dtypes[i] == pd.np.float64:
                dtype = "REAL"
            elif dtypes[i] == pd.np.int64:
                dtype = "INTEGER"
            _columns.append((i, rc_feature, label, dtype))
            setattr(self, rc_feature, label)

        self.corpus_table = "Corpus"
        self.corpus_id = "ID"
        self.corpus_file_id = "FileId"

        self.file_table = "Files"
        self.file_id = "FileId"
        self.file_name = "Filename"
        self.file_path = "Path"

        self.create_table_description(
            self.file_table,
            [Identifier(self.file_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.file_name, "VARCHAR(2048) NOT NULL"),
             Column(self.file_path, "VARCHAR(2048) NOT NULL")])

        l = [Identifier(self.corpus_id, "BIGINT(20) UNSIGNED NOT NULL"),
             Link(self.corpus_file_id, self.file_table)]

        for _, _, label, dtype in _columns:
            l.append(Column(label, dtype))

        self.create_table_description(self.corpus_table, l)

    def validate_path(self, path):
        return path == self.arguments.path

    @staticmethod
    def validate_files(l):
        return True

    def build_load_files(self):
        capt = Capturer(stderr=True)
        with capt:
            df = self._table_options.read_file(self.arguments.path)
        for x in capt:
            s = "File {} – {}".format(self.arguments.path, x)
            logging.warning(s)
            print(s)

        if not self._table_options.header:
            df.columns = ["X{}".format(x) for x in df.columns]
        else:
            df.columns = [re.sub("[^a-zA-Z0-9_]", "_", x) for x in df.columns]
        df[self.corpus_file_id] = 1
        self.DB.load_dataframe(df, self.corpus_table, self.corpus_id)
        self.store_filename(self.arguments.path)

    @classmethod
    def get_file_list(cls, path, file_filter, sort=True):
        return []


def main():
    BuilderClass().build()

if __name__ == "__main__":
    main()

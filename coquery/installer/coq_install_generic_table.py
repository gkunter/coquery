# -*- coding: utf-8 -*-

"""
coq_install_generic.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import string
import re
import pandas as pd

from coquery.corpusbuilder import BaseCorpusBuilder, logger
from coquery.corpusbuilder import (Column, Link, Identifier)
from coquery.capturer import Capturer


class BuilderClass(BaseCorpusBuilder):
    file_name = None

    def __init__(self,
                 gui=False, mapping=None, dtypes=None, table_options=None):
        # all corpus builders have to call the inherited __init__ function:
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

        # Add the main lexicon table. Each row in this table represents a
        # word-form that occurs in the corpus. It has the following columns:
        #
        # WordId (Identifier)
        # An int value containing the unique identifier of this word-form.
        #
        # LemmaId
        # An int value containing the unique identifier of the lemma that
        # is associated with this word-form.
        #
        # Text
        # A text value containing the orthographic representation of this
        # word-form.
        #
        # Additionally, if NLTK is used to tag part-of-speech:
        #
        # Pos
        # A text value containing the part-of-speech label of this
        # word-form.

        # Add the file table. Each row in this table represents a data file
        # that has been incorporated into the corpus. Each token from the
        # corpus table is linked to exactly one file from this table, and
        # more than one token may be linked to each file in this table.
        # The table contains the following columns:
        #
        # FileId (Identifier)
        # An int value containing the unique identifier of this file.
        #
        # File
        # A text value containing the base file name of this data file.
        #
        # Path
        # A text value containing the path that points to this data file.

        self.create_table_description(
            self.file_table,
            [Identifier(self.file_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.file_name, "VARCHAR(2048) NOT NULL"),
             Column(self.file_path, "VARCHAR(2048) NOT NULL")])

        # Add the main corpus table. Each row in this table represents a
        # token in the corpus. It has the following columns:
        #
        # TokenId (Identifier)
        # An int value containing the unique identifier of the token
        #
        # WordId
        # An int value containing the unique identifier of the lexicon
        # entry associated with this token.
        #
        # FileId
        # An int value containing the unique identifier of the data file
        # that contains this token.

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
        if self._table_options is not None:
            kwargs = {
                "encoding": self._table_options.encoding,
                "header": 0 if self._table_options.header else None,
                "sep": self._table_options.sep,
                "skiprows": self._table_options.skip_lines,
                "quotechar": self._table_options.quote_char}
        else:
            kwargs = {"encoding": "utf-8"}

        kwargs.update({"low_memory": False, "error_bad_lines": False})

        capt = Capturer(stderr=True)
        with capt:
            try:
                df = pd.read_csv(self.arguments.path, **kwargs)
            except Exception as e:
                logger.error(e)
                print(e)
                raise e
        for x in capt:
            s = "File {} – {}".format(self.arguments.path, x)
            logger.warn(s)
            print(s)

        if not self._table_options.header:
            df.columns = ["X{}".format(x) for x in df.columns]
        else:
            df.columns = [re.sub("[^a-zA-Z0-9_]", "_", x) for x in df.columns]

        df[self.corpus_file_id] = 1
        self.DB.load_dataframe(df, self.corpus_table, self.corpus_id)

    @classmethod
    def get_file_list(cls, path, file_filter, sort=True):
        return []


def main():
    BuilderClass().build()

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

"""
coq_install_coha.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import pandas as pd
import logging
import codecs
import sys
import os

from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.tables import Column, Identifier, Link
from coquery.defines import SQL_MYSQL
from coquery import options


class BuilderClass(BaseCorpusBuilder):
    file_filter = "????.txt"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    file_columns = [
        Identifier(file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
        Column(file_name, "CHAR(8) NOT NULL"),
        Column(file_path, "TINYTEXT NOT NULL")]

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_labelcs = "WordCS"
    word_lemma = "Lemma"
    word_pos = "POS"
    word_columns = [
        Identifier(word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
        Column(word_label, "VARCHAR(26) NOT NULL"),
        Column(word_labelcs, "VARCHAR(48) NOT NULL"),
        Column(word_lemma, "VARCHAR(24) NOT NULL"),
        Column(word_pos, "VARCHAR(24) NOT NULL")]

    source_table = "Sources"
    source_id = "SourceId"
    source_label = "Title"
    source_author = "Author"
    source_year = "Year"
    source_genre = "Genre"
    source_words = "Words"
    source_publisher = "Publisher"
    source_columns = [
        Identifier(source_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
        Column(source_words, "MEDIUMINT(6) UNSIGNED NOT NULL"),
        Column(source_genre, "ENUM('FIC','MAG','NEWS','NF') NOT NULL"),
        Column(source_year, "SMALLINT(4) NOT NULL"),
        Column(source_label, "VARCHAR(150) NOT NULL"),
        Column(source_author, "VARCHAR(100) NOT NULL"),
        Column(source_publisher, "VARCHAR(114) NOT NULL")]

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "SourceId"
    corpus_columns = [
        Identifier(corpus_id, "INT(9) UNSIGNED NOT NULL"),
        Link(corpus_word_id, word_table),
        Link(corpus_source_id, source_table)]

    auto_create = ["file", "word", "source", "corpus"]

    expected_files = ["sources_coha.xlsx", "lexicon.txt",
                      "1810.txt", "1820.txt", "1830.txt", "1840.txt",
                      "1850.txt", "1860.txt", "1870.txt", "1880.txt",
                      "1890.txt", "1900.txt", "1910.txt", "1920.txt",
                      "1930.txt", "1940.txt", "1950.txt", "1960.txt",
                      "1970.txt", "1980.txt", "1990.txt", "2000.txt"]

    def __init__(self, gui=False, *args):
        # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)
        self.add_time_feature(self.source_year)

    @staticmethod
    def get_name():
        return "COHA"

    @staticmethod
    def get_db_name():
        return "coq_coha"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en-US"

    @staticmethod
    def get_title():
        return "Corpus of Historical American English"

    @staticmethod
    def get_description():
        return [
            "The Corpus of Historical American English (COHA) is the largest "
            "structured corpus of historical English. The corpus was created "
            "by Mark Davies of Brigham Young University, with funding from "
            "the US National Endowment for the Humanities.",
            "COHA allows you search more than 400 million words of text of "
            "American English from 1810 to 2009."]

    @staticmethod
    def get_references():
        return ["Davies, Mark. (2010-) <i>The Corpus of Historical American "
                "English: 400 million words, 1810-2009</i>. Available online "
                "at http://corpus.byu.edu/coha/."]

    @staticmethod
    def get_url():
        return "http://corpus.byu.edu/coha/"

    @staticmethod
    def get_license():
        return "COHA is available under the terms of a commercial license."

    @staticmethod
    def get_installation_note():
        _, _, db_type, _, _ = options.get_con_configuration()

        if db_type == SQL_MYSQL:
            return """
            <p><b>MySQL installation note</b><p>
            <p>The COHA installer uses a special feature of MySQL servers
            which allows to load large chunks of data into the database in a
            single step.</p>
            <p>This feature notably speeds up the installation of the COHA
            corpus. However, it may be disabled on your MySQL servers. In that
            case, the installation will fail with an error message similar to
            the following: </p>
            <p><code>The used command is not allowed with this MySQL version
            </code></p>
            <p>Should the installation fail, please ask your MySQL server
            administrator to enable loading of local in-files by setting the
            option <code>local-infile</code> in the MySQL configuration file.
            </p>
            """
        else:
            return None

    def build_load_files(self):
        files = sorted(self.get_file_list(self.arguments.path,
                                          self.file_filter))

        self._widget.progressSet.emit(len(files), "")

        for count, file_name in enumerate(files):
            if self.interrupted:
                return

            base_name = os.path.basename(file_name)

            s = "Reading '{}' (file %v out of %m)".format(base_name)
            self._widget.labelSet.emit(s)
            logging.info("Reading {}".format(file_name))

            # set up default arguments for the load_file() method:
            kwargs = {"sep": "\t", "quoting": 3, "encoding": "latin-1"}

            # handle the different files:
            if base_name == "sources_coha.xlsx":
                # load the sources from an excel file
                names = [self.source_id, self.source_words, self.source_genre,
                         self.source_year, self.source_label,
                         self.source_author, self.source_publisher]
                df = pd.read_excel(file_name, skiprows=0, names=names,
                                   engine=None)

                for col in (self.source_label, self.source_author,
                            self.source_publisher):
                    df[col] = df[col].fillna("")

                self.DB.load_dataframe(
                    df, self.source_table, index_label=None)
            elif base_name == "lexicon.txt":
                # load the lexicon file
                names = (self.word_id, self.word_labelcs, self.word_label,
                         self.word_lemma, self.word_pos)
                self.DB.load_file(
                    file_name=file_name,
                    table=self.word_table,
                    index=None,
                    skiprows=2,
                    header=None,
                    names=names,
                    error_bad_lines=False,
                    na_filter=False,
                    drop_duplicate=self.word_id,
                    **kwargs)
            else:
                # load a corpus file
                names = (self.corpus_source_id, self.corpus_id,
                         self.corpus_word_id)
                lines = self.DB.load_file(
                            file_name=file_name,
                            table=self.corpus_table,
                            index=None,
                            header=None,
                            names=names,
                            **kwargs)
                self._corpus_id += lines
                self.store_filename(base_name)

            self._widget.progressUpdate.emit(count + 1)

if __name__ == "__main__":
    BuilderClass().build()

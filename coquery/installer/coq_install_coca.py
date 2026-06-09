# -*- coding: utf-8 -*-

"""
coq_install_coca.py is part of Coquery.

Copyright (c) 2016-2026 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import logging
import zipfile
import tarfile
import os
import io
import pandas as pd
import csv

from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.tables import Identifier, Column, Link
from coquery import options
from coquery.defines import SQL_MYSQL


_FILENAME_SOURCES: str = "coca-sources.zip"
_FILENAME_SUBGENRES: str = "coca-subgenres.txt"
_FILENAME_LEXICON: str = "coca-lexicon.zip"
_FILENAME_DB: str = "coca-db.tar"
_CHUNKSIZE: int = 100000
# For some weird reason, the COCA engineers decided to introduce some kind of
# dummy entry into the lexicon with the word ID 14000000. This dummy entry has
# no real orthographic representation (lexicon.txt has "@zq" as value for this
# entry). The really crazy decision is that they use this dummy entry in the
# DB dumps for the BLOG section with non-unique token IDs: the token ID value
# 1 occurs more than 2400 times in db_blog_01.txt, which of course introduces
# database inconsistencies if the token ID is set to be unique.
#
# This is really a puzzling decision, and I couldn't find any documentation for
# this dummy entry. It's also weird that they chose a relatively low number for
# this ID: the highest genuine word ID is 13602391, which leaves something like
# 400,000 IDs until the dummy entry ID is reached. That's not too much given
# the poor quality of the blog and web-based tokenization process.
#
# Be it as it may, that leaves me with two options:
# (1) Keep the token ID column from the DB files, but create a new column that
#     will serve as the truly unique token ID that the SQL database requires
# (2) Remove all occurrences of this dummy entry to keep the SQL database
#     consistent

# Since there is no obvious advantage of retaining the dummy item, I opt for
# option (2) since option (1) will inflate the size of the database for no
# good reason.
_COCA_MAGIC_WORD_ID: int = 14000000

class BuilderClass(BaseCorpusBuilder):
    file_filter = "db_*_*.txt"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    file_columns = [
        Identifier(file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
        Column(file_name, "CHAR(16) NOT NULL"),
        Column(file_path, "TINYTEXT NOT NULL")]

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_lemma = "Lemma"
    word_pos = "POS"
    word_columns = [
        Identifier(word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
        Column(word_label, "VARCHAR(64) NOT NULL"),
        Column(word_lemma, "VARCHAR(64) NOT NULL"),
        Column(word_pos, "VARCHAR(32) NOT NULL")]

    subgenre_table = "Subgenres"
    subgenre_id = "SubgenreId"
    subgenre_label = "Subgenre"
    subgenre_columns = [
        Identifier(subgenre_id, "SMALLINT UNSIGNED"),
        Column(subgenre_label, "VARCHAR(32) NOT NULL")]

    source_table = "Sources"
    source_id = "SourceId"
    source_label = "Source"
    source_title = "Title"
    source_genre = "Genre"
    source_year = "Year"
    source_subgenre_id = "SubgenreId"
    source_columns = [
        Identifier(source_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
        Column(source_year,  "SMALLINT(4) NOT NULL"),
        Column(source_genre, "CHAR(6) NOT NULL"),
        Link(source_subgenre_id, subgenre_table),
        Column(source_label, "VARCHAR(256)"),
        Column(source_title, "VARCHAR(512)")]

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "SourceId"
    corpus_columns = [
        Identifier(corpus_id, "INT(9) UNSIGNED NOT NULL"),
        Link(corpus_word_id, word_table),
        Link(corpus_source_id, source_table)]

    auto_create = ["word", "file", "subgenre", "source", "corpus"]

    expected_files = [
        _FILENAME_SOURCES, _FILENAME_SUBGENRES,
        _FILENAME_LEXICON,
        _FILENAME_DB,
        ]

    def __init__(self, gui=False, *args):
        # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)
        self.add_time_feature(self.source_year)

    @staticmethod
    def get_name():
        return "COCA"

    @staticmethod
    def get_db_name():
        return "coq_coca"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en-US"

    @staticmethod
    def get_title():
        return "Corpus of Contemporary American English"

    @staticmethod
    def get_description():
        return [
            "From the website:",
            "\"The Corpus of Contemporary American English (COCA) was created "
            "by Mark Davies, and it is the only large and 'balanced' corpus "
            "of American English. COCA is probably the most widely-used "
            "corpus of English, and it is related to other corpora from "
            "English-Corpora.org, which offer unparalleled insight into "
            "variation in English.",
            "The corpus contains more than one billion words of text (25+ "
            "million words each year 1990-2019) from eight genres: spoken, "
            "fiction, popular magazines, newspapers, academic texts, TV and "
            "movies subtitles, blogs, and other web pages.\""]

    @staticmethod
    def get_references():
        return ["Davies, Mark. (2008-) "
                "<i>The Corpus of Contemporary American English (COCA)</i>. "
                "Available online at https://www.english-corpora.org/coca/"]

    @staticmethod
    def get_url():
        return "https://www.english-corpora.org"

    @staticmethod
    def get_license():
        return "COCA is available under the terms of a commercial license."

    @classmethod
    def get_installation_note(cls):
        return (
            "<p>The installer expects the following files in the selected "
            "directory:</p><ul>"
            f"<li>{_FILENAME_DB}</li>"
            f"<li>{_FILENAME_LEXICON}</li>"
            f"<li>{_FILENAME_SOURCES}</li>"
            f"<li>{_FILENAME_SUBGENRES}</li>"
            "</ul>")


    def build_load_files(self):
        file_list = self.get_file_list(self.arguments.path, self.file_filter)

        _process_mappings = {
            _FILENAME_SOURCES:      self._process_sources,
            _FILENAME_SUBGENRES:    self._process_subgenres,
            _FILENAME_DB:           self._process_db,
            _FILENAME_LEXICON:      self._process_lexicon}

        for count, file_name in enumerate(file_list):
            if self.interrupted:
                return

            base_name = os.path.basename(file_name)
            _process_mappings[base_name](file_name)


    def _process_sources(self, file_name: str) -> None:
        base_name: str = os.path.basename(file_name)

        msg: str = f"Reading sources from {base_name}"
        self._widget.labelSet.emit(msg)
        logging.info(msg)

        # The dictionary 'kwargs' stores the arguments that are needed to
        # correctly load the specified file into an SQL table using the
        # `load_file()` method of the current database object.

        kwargs = {
            "sep": "\t",
            "quoting": 3,
            "encoding": "iso8859_15",
            "header": None,
            "na_values": "",
            "names": (self.source_id, self.source_year, self.source_genre,
                      self.source_subgenre_id, self.source_label,
                      self.source_title)}

        with zipfile.ZipFile(file_name) as zip_file:
            for source_filename in zip_file.namelist():
                if self.interrupted:
                    return

                with zip_file.open(source_filename) as archived_file:
                    df = pd.read_csv(archived_file, **kwargs)
                    n_lines = self.DB.load_dataframe(
                        df,
                        table_name=self.source_table,
                        index_label=False)

    def _process_subgenres(self, file_name: str) -> None:
        base_name: str = os.path.basename(file_name)

        msg: str = f"Reading subgenres from {base_name}"
        self._widget.labelSet.emit(msg)
        logging.info(msg)

        kwargs = {
            "sep": "\t",
            "quoting": 3,
            "encoding": "utf-8",
            "header": None,
            "na_values": "",
            "names": (self.subgenre_id, self.subgenre_label)}

        df = pd.read_csv(file_name, **kwargs)
        n_lines = self.DB.load_dataframe(
            df,
            table_name=self.subgenre_table,
            index_label=False)

    def _process_lexicon(self, file_name: str) -> None:
        base_name: str = os.path.basename(file_name)

        msg: str = f"Reading lexicon from {base_name}"
        self._widget.labelSet.emit(msg)
        logging.info(msg)

        # The dictionary 'kwargs' stores the arguments that are needed to
        # correctly load the specified file into an SQL table using the
        # `load_file()` method of the current database object.

        column_names = (self.word_id, self.word_label, self.word_lemma,
                        self.word_pos)
        dtypes = ("Int64", "str", "str", "str")

        kwargs = {
            "sep": "\t",
            "quoting": csv.QUOTE_NONE,
            "encoding": "iso8859_15",
            "header": None,
            "na_values": "",
            "names": column_names,
            "dtype": dict(zip(column_names, dtypes)),
            "chunksize": _CHUNKSIZE
            }

        with zipfile.ZipFile(file_name) as zip_file:
            for source_filename in zip_file.namelist():
                if self.interrupted:
                    return

                msg: str = f"Determining number of entries in {source_filename}"
                self._widget.progressSet.emit(0, msg)


                with zip_file.open(source_filename) as archived_file:
                    n_lines = sum(1 for _ in archived_file)
                    n_chunks = 1 + n_lines // _CHUNKSIZE
                    self._widget.progressSet.emit(
                        n_chunks,
                        "Inserting lexicon chunks... (%v of %m)")

                with zip_file.open(source_filename) as archived_file:
                    reader = pd.read_csv(archived_file, **kwargs)

                    for i, chunk in enumerate(reader):
                        if self.interrupted:
                            return
                        self._widget.progressUpdate.emit(i)
                        chunk = chunk[~chunk.duplicated(self.word_id)]
                        self.DB.load_dataframe(
                            chunk.fillna(""),
                            table_name=self.word_table,
                            index_label=False,
                        )

    def _process_db(self, file_name: str) -> None:
        base_name: str = os.path.basename(file_name)
        column_names=(self.corpus_source_id,
                      self.corpus_id,
                      self.corpus_word_id)
        dtypes = ("Int64", "Int64", "Int64")
        kwargs = {
                "sep": "\t",
                "quoting": csv.QUOTE_NONE,
                "encoding": "iso8859_15",
                "header": None,
                "na_values": "",
                "names": column_names,
                "dtype": dict(zip(column_names, dtypes)),
                "chunksize": _CHUNKSIZE
                }


        n_files: int = 0
        files_processed: int = 0

        msg: str = f"Determining number of files in {base_name}"
        self._widget.progressSet.emit(0, msg)
        with tarfile.open(file_name, mode="r|*") as tar_file:
            for member in tar_file:
                src = (tar_file
                        .extractfile(member)
                        .read())
                zip_buffer = io.BytesIO(src)

                with zipfile.ZipFile(zip_buffer) as zip_file:
                    n_files += len(zip_file.namelist())

        msg: str = f"Extracting archives from {base_name}"
        self._widget.progressSet.emit(n_files, msg)
        logging.info(msg)

        with tarfile.open(file_name, mode="r|*") as tar_file:
            for member in tar_file:
                if self.interrupted:
                    return

                src = (tar_file
                        .extractfile(member)
                        .read())
                zip_buffer = io.BytesIO(src)

                with zipfile.ZipFile(zip_buffer) as zip_file:
                    for zip_name in zip_file.namelist():
                        if self.interrupted:
                            return
                        files_processed += 1
                        logging.info(f"Inserting from {zip_name}")
                        with zip_file.open(zip_name) as input_file:
                            reader = pd.read_csv(input_file,
                                                    **kwargs)
                            for i, chunk in enumerate(reader):
                                if self.interrupted:
                                    return

                                msg = f"Inserting chunk {i} from {zip_name}"
                                self._widget.labelSet.emit(
                                    f"{msg} (file %v of %m)")
                                self._widget.progressUpdate.emit(
                                    files_processed)

                                chunk = chunk[
                                    chunk[
                                        self.word_id] != _COCA_MAGIC_WORD_ID]
                                chunk = chunk.fillna("")
                                self.DB.load_dataframe(
                                    chunk,
                                    table_name=self.corpus_table,
                                    index_label=False)

                            self.commit_data()

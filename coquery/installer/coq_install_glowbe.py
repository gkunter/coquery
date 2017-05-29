# -*- coding: utf-8 -*-

"""
coq_install_glowbe.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import zipfile
import os.path
import logging
import pandas as pd

try:
    from cStringIO import BytesIO
except ImportError:
    from io import BytesIO

from coquery.corpusbuilder import BaseCorpusBuilder, Column, Identifier, Link
from coquery import NAME

class BuilderClass(BaseCorpusBuilder):
    file_filter = "db_*_*.zip"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "SourceId"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_lemma = "Lemma"
    word_pos = "POS"

    source_table = "Sources"
    source_id = "TextId"
    source_nwords = "NWords"
    source_country = "Country"
    source_genre = "Genre"
    source_url = "URL"
    source_title = "Title"

    special_files = ["sources.zip", "lexicon.zip"]
    expected_files = special_files + [
        "db_au_kso.zip", "db_bd_lws.zip", "db_ca_usi.zip",
        "db_gb_blog_akq.zip", "db_gb_genl_lsp.zip", "db_gh_msk.zip",
        "db_hk_wjj.zip", "db_ie_ksu.zip", "db_in_ksi.zip", "db_jm_bsh.zip",
        "db_ke_aua.zip", "db_lk_ssy.zip", "db_my_wme.zip", "db_ng_kdt.zip",
        "db_nz_poj.zip", "db_ph_jop.zip", "db_pk_jww.zip", "db_sg_jsu.zip",
        "db_tz_niy.zip", "db_us_blog_lks.zip", "db_us_genl_ksl.zip",
        "db_za_asl.zip"]

    def __init__(self, gui=False, *args):
        # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "INT UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(24) NOT NULL"),
             Column(self.word_lemma, "VARCHAR(24) NOT NULL"),
             Column(self.word_pos, "VARCHAR(24) NOT NULL")])

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "SMALLINT UNSIGNED NOT NULL"),
             Column(self.file_name, "TINYTEXT NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])

        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "MEDIUMINT UNSIGNED NOT NULL"),
             Column(self.source_nwords, "TINYINT UNSIGNED NOT NULL"),
             Column(self.source_country, "VARCHAR(2) NOT NULL"),
             Column(self.source_genre, "CHAR(1)NOT NULL"),
             Column(self.source_url, "TINYTEXT NOT NULL"),
             Column(self.source_title, "TINYTEXT NOT NULL")])

        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "INT UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_source_id, self.source_table)])

    @staticmethod
    def get_name():
        return "GloWbE"

    @staticmethod
    def get_db_name():
        return "glowbe"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en-various"

    @staticmethod
    def get_title():
        return "Corpus of Global Web-Based English"

    @staticmethod
    def get_modules():
        return [("odo", "Odo", "http://odo.pydata.org/en/latest/project-info.html")]

    @staticmethod
    def get_description():
        return [
            "The corpus of Global Web-based English (GloWbE; pronounced 'globe') is unique in the way that it allows you to carry out comparisons between different varieties of English.",
            "GloWbE contains about 1.9 billion words of text from twenty different countries. This makes it about 100 times as large as other corpora like the International Corpus of English, and it allows for many types of searches that would not be possible otherwise."]

    @staticmethod
    def get_references():
        return ["Davies, Mark. (2012) <i>The corpus of Global Web-based English (GloWbE)</i>. Available online at http://corpus.byu.edu/glowbe/"]

    @staticmethod
    def get_url():
        return "http://corpus.byu.edu/glowbe/"

    @staticmethod
    def get_license():
        return "GloWbE is available under the terms of a commercial license."

    def build_load_files(self):
        from odo import odo
        import datashape
        datashape.coretypes._canonical_string_encodings.update({"utf8mb4_unicode_ci": "U8"})

        files = sorted(self.get_file_list(self.arguments.path, self.file_filter))

        if self._widget:
            self._widget.progressSet.emit(len(files), "")

        for count, file_name in enumerate(files):
            if self.interrupted:
                return

            base_name = os.path.basename(file_name)
            zip_file = zipfile.ZipFile(file_name)
            for text_name in zip_file.namelist():

                if self._widget:
                    self._widget.labelSet.emit("Extracting '{}' from '{}' (file %v out of %m)".format(text_name, base_name))
                logger.info("Extracting '{}' from '{}'".format(text_name, base_name))

                if self._interrupted:
                    return

                if base_name == "lexicon.zip":
                    table = self.word_table
                    target = (self.word_id,
                                self.word_label,
                                self.word_lemma,
                                self.word_pos)
                    dtypes = dict(zip(target,
                                      (pd.np.int64, object, object, object)))
                elif base_name == "sources.zip":
                    table = self.source_table
                    target = (self.source_id,
                                self.source_nwords,
                                self.source_country,
                                self.source_url,
                                self.source_title)
                    dtypes = dict(zip(target,
                                      (pd.np.int64, pd.np.int64, object, object, object)))
                else:
                    table = self.corpus_table
                    target = (self.corpus_source_id,
                                self.corpus_id,
                                self.corpus_word_id)
                    dtypes = dict(zip(target,
                                      (pd.np.int64, pd.np.int64, pd.np.int64)))

                # Read the complete zip file into a pandas data frame. This
                # might be tweaked so that smaller chunks are processed so
                # that the corpus can be installed on systems that do not have
                # enough RAM to fit the largest source files (probably
                # lexicon.txt). # get_chunk() is provided in general.py.

                # the file "db_us_b03.txt" contains an EOF character \x1a in
                # the last line (row number 23302766), which breaks the
                # installation. To fix this, this line will be skipped when
                # reading that file (adjusted for 0-indexing):
                skiprows = [23302765] if text_name == "db_us_b03.txt" else []

                df = pd.read_csv(BytesIO(zip_file.read(text_name)),
                                 sep="\t",
                                 names=target,
                                 dtype=dtypes,
                                 quoting=3,
                                 header=(2 if base_name in self.special_files
                                         else None),
                                 error_bad_lines=False,
                                 encoding="latin-1",
                                 skiprows=skiprows,
                                 engine="c")
                # Strangely, the lexicon can have empty cells in Word, Lemma,
                # and POS. They are filled by empty strings:
                df = df.fillna("")

                # In sources.txt, the country and the genre column are stored
                # in a single column, but we want to store them as two:
                if base_name == "sources.zip":
                    df[self.source_genre] = df[self.source_country].apply(lambda x: x.strip()[-1])
                    df[self.source_country] = df[self.source_country].apply(lambda x: x[:2])
                    df = df[[self.source_id,
                             self.source_nwords,
                             self.source_country,
                             self.source_genre,
                             self.source_url,
                             self.source_title]]

                if self._widget:
                    self._widget.labelSet.emit("Writing '{}' to database".format(text_name))

                # use odo to write the data frame to the database:
                odo(df, "{}::{}".format(self.DB.sql_url, table), encoding="utf-8")

            if self._widget:
                self._widget.progressUpdate.emit(count + 1)

if __name__ == "__main__":
    BuilderClass().build()


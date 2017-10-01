# -*- coding: utf-8 -*-

"""
coq_install_malti.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import codecs
import re
import os

from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.tables import Column, Identifier, Link
from coquery.defines import QUERY_ITEM_TRANSCRIPT

section_map = {"academic": "Academic",
                "culture": "Culture",
                "european": "European",
                "law": "Maltese Law",
                "literature": "Literature",
                "news": "News",
                "opinion": "Opinion",
                "parl": "Parliament",
                "religion": "Religion",
                "sport": "Sport"}

re_text = re.compile('\<text id="(.*)">')
re_p = re.compile('\<p id="(.*)">')
re_s = re.compile('\<s id="(.*)">')


class BuilderClass(BaseCorpusBuilder):
    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_pos = "POS"
    word_lemma = "Lemma"
    word_root = "Root"
    word_columns = [
        Identifier(word_id, "MEDIUMINT(5) UNSIGNED NOT NULL"),
        Column(word_label, "VARCHAR(33) NOT NULL"),
        Column(word_pos, "VARCHAR(7) NOT NULL"),
        Column(word_lemma, "VARCHAR(33) NOT NULL"),
        Column(word_root, "VARCHAR(33) NOT NULL")]

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    file_columns = [
        Identifier(file_id, "SMALLINT(5) UNSIGNED NOT NULL"),
        Column(file_name, "VARCHAR(21) NOT NULL"),
        Column(file_path, "VARCHAR(2048) NOT NULL")]

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    corpus_section = "Section"
    corpus_text = "Text"
    corpus_sentence = "Sentence"
    corpus_paragraph = "Paragraph"

    corpus_columns = [
        Identifier(corpus_id, "INT(7) UNSIGNED NOT NULL"),
        Link(corpus_file_id, file_table),
        Link(corpus_word_id, word_table),
        Column(corpus_section, "VARCHAR(20) NOT NULL"),
        Column(corpus_text, "VARCHAR(20) NOT NULL"),
        Column(corpus_sentence, "INT UNSIGNED NOT NULL"),
        Column(corpus_paragraph, "INT UNSIGNED NOT NULL"),
        ]

    auto_create = ["word", "file", "corpus"]

    expected_files = ["malti03.academic.1.txt",
                      "malti03.academic.2.txt",
                      "malti03.culture.1.txt",
                      "malti03.culture.2.txt",
                      "malti03.european.txt",
                      "malti03.law.txt",
                      "malti03.literature.1.txt",
                      "malti03.literature.2.txt",
                      "malti03.news.1.txt",
                      "malti03.news.2-1.txt",
                      "malti03.news.2-10.txt",
                      "malti03.news.2-2.txt",
                      "malti03.news.2-3.txt",
                      "malti03.news.2-4.txt",
                      "malti03.news.2-5.txt",
                      "malti03.news.2-6.txt",
                      "malti03.news.2-7.txt",
                      "malti03.news.2-8.txt",
                      "malti03.news.2-9.txt",
                      "malti03.opinion.1.txt",
                      "malti03.opinion.2.txt",
                      "malti03.parl.1.txt",
                      "malti03.parl.2.txt",
                      "malti03.parl.3.txt",
                      "malti03.parl.4.txt",
                      "malti03.parl.5.txt",
                      "malti03.religion.1.txt",
                      "malti03.religion.2.txt",
                      "malti03.sport.1.txt",
                      "malti03.sport.2.txt"]

    @staticmethod
    def get_name():
        return "Korpus Malti"

    @staticmethod
    def get_db_name():
        return "coq_malti"

    @staticmethod
    def get_title():
        return "Korpus Malti: A generic corpus of Maltese"

    @staticmethod
    def get_language():
        return "Maltese"

    @staticmethod
    def get_language_code():
        return "mt"

    @staticmethod
    def get_description():
        return ["Korpus Malti: A generic corpus of Maltese"]

    @staticmethod
    def get_references():
        return [
            "Gatt, A., & Čéplö, S. (2013). Digital corpora and other "
            "electronic resources for Maltese. In <i>Proceedings of the "
            "International Conference on Corpus Linguistics</i>. Lancaster, "
            "UK: University of Lancaster."]

    @staticmethod
    def get_url():
        s = "http://mlrs.research.um.edu.mt/index.php?page=downloads"
        return s

    @staticmethod
    def get_license():
        return ("Korpus Malti is free for academic research (unknown "
                "license).")

    def __init__(self, *args, **kwargs):
        super(BuilderClass, self).__init__(*args, **kwargs)
        self.map_query_item(QUERY_ITEM_TRANSCRIPT, "word_root")

    def _process_text(self, current_text):
        word_table = self.table(self.word_table)
        for line in current_text:
            if self._interrupted:
                return

            line = line.strip()
            if not line:
                continue

            if '<text id ="' in line:
                match = re_text.match(line)
                self._text_label = match.group(1)
                continue
            if '<p id="' in line:
                match = re_p.match(line)
                self._paragraph_id = match.group(1)
                continue
            if '<s id="' in line:
                match = re_s.match(line)
                self._sentence_id = match.group(1)
                continue

            fields = line.split("\t")
            if len(fields) == 4:
                d = dict(zip([self.word_label, self.word_pos,
                              self.word_lemma, self.word_root],
                             fields))
                self._word_id = word_table.get_or_insert(d)
                self.add_token_to_corpus(
                    {self.corpus_word_id: self._word_id,
                     self.corpus_file_id: self._file_id,
                     self.corpus_section: self._section_name,
                     self.corpus_text: self._text_label,
                     self.corpus_sentence: self._sentence_id,
                     self.corpus_paragraph: self._paragraph_id})
            else:
                self._check.add(line)

    def process_file(self, filename):
        if self._interrupted:
            return

        base_name = os.path.basename(filename)
        match = re.match("malti03\.(\w*)\.", base_name)
        self._section_name = section_map[match.group(1)]

        with codecs.open(filename, "r", encoding="utf-8") as input_file:
            self._check = set([])
            self._process_text(input_file.read())
            print(self._check)
        self.commit_data()

# -*- coding: utf-8 -*-

"""
coq_install_cmudict.py is part of Coquery.

Copyright (c) 2016-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""


from __future__ import unicode_literals
from __future__ import print_function

import codecs

from coquery.corpusbuilder import Identifier, Column, BaseCorpusBuilder
from coquery import transpose


class BuilderClass(BaseCorpusBuilder):
    encoding = "latin-1"
    file_filter = "cmudict*"

    corpus_table = "Dictionary"
    corpus_id = "ID"
    corpus_word = "Word"
    corpus_transcript = "Transcript"
    corpus_ipa = "IPA"

    corpus_columns = [
        Identifier(corpus_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
        Column(corpus_word, "VARCHAR(50) NOT NULL"),
        Column(corpus_transcript, "VARCHAR(100) NOT NULL"),
        Column(corpus_ipa, "VARCHAR(100) NOT NULL")]

    auto_create = ["corpus"]

    @staticmethod
    def validate_files(file_lst):
        if len(file_lst) > 1:
            msg_template = ("<p>More than one file has a name that starts "
                            "with <code>cmudict</code>' in the selected "
                            "directory:</p><p>{}</p>.")
            msg_str = msg_template.format("<br/>".join(file_lst))
            raise RuntimeError(msg_str)
        elif len(file_lst) == 0:
            msg_str = ("<p>No dictionary file could be found in the selected "
                       "directory. The file name of the dictionary file has "
                       "to start with the sequence <code>cmudict</code>.</p>")
            raise RuntimeError(msg_str)

    def build_load_files(self):
        files = BuilderClass.get_file_list(self.arguments.path,
                                           self.file_filter)
        with codecs.open(files[0], "r",
                         encoding=self.arguments.encoding) as input_file:
            content = input_file.readlines()
        if self._widget:
            self._widget.progressSet.emit(len(content) // 100,
                                          "Reading dictionary file...")
            self._widget.progressUpdate.emit(0)

        for i, current_line in enumerate(content):
            current_line = current_line.strip()
            if current_line and not current_line.startswith(";;;"):
                word, transcript = current_line.split("  ")
                ipa = transpose.arpa_to_ipa(transcript.strip())
                self.add_token_to_corpus(
                    {self.corpus_id: i+1,
                     self.corpus_word: word,
                     self.corpus_transcript: transcript,
                     self.corpus_ipa: ipa})
            if self._widget and not i % 100:
                self._widget.progressUpdate.emit(i // 100)
        self.commit_data()

    @staticmethod
    def get_title():
        return "Carnegie Mellon Pronouncing Dictionary"

    @staticmethod
    def get_url():
        return 'http://www.speech.cs.cmu.edu/cgi-bin/cmudict'

    @staticmethod
    def get_name():
        return "CMUdict"

    @staticmethod
    def get_db_name():
        return "cmudict"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en-US"

    @staticmethod
    def get_license():
        return ("CMUdict is available under the terms of a modified FreeBSD "
                "license.")

    @staticmethod
    def get_description():
        return [
            "The Carnegie Mellon Pronouncing Dictionary (CMUdict) is a "
            "dictionary containing approximately 135.000 English word-forms "
            "and their phonemic transcriptions, using a variant of the "
            "RPAbet transcription system."]


if __name__ == "__main__":
    BuilderClass().build()

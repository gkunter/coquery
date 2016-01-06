# -*- coding: utf-8 -*-

"""
coq_install_gapra.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import codecs
import csv

from corpusbuilder import *

class BuilderClass(BaseCorpusBuilder):
    file_filter = "s*.words.tagged"

    root_table = "Roots"
    root_id = "RootId"
    root_radicals = "Radicals"
    root_type = "Type"
    root_variant = "Variant"
    
    lemma_table = "Lexemes"
    lemma_id = "LemmaId"
    lemma_label = "Lemma"
    lemma_derived_form = "Derived_form"
    lemma_gloss = "Gloss"
    lemma_intransitive = "Intransitive"
    lemma_modified = "Modified"
    lemma_pos = "POS"
    lemma_root_id = "RootId"

    source_table = "Sources"
    source_label = "Title"
    source_year = "Year"
    source_author = "Author"
    source_key = "Key"
    source_note = "Note"
    
    word_table = "Wordforms"
    word_id = "WordId"
    word_label = "Surface_form"
    word_transcript = "Phonetic"
    word_gender = "Gender"
    word_number = "Number"
    word_pattern = "Pattern"
    word_source_id = "SourceId"
    word_lemma_id = "LemmaId"
    word_modified = "Modified"
       
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    corpus_table = "Wordforms"
    corpus_id = "WordId"

    expected_files = [
        "lexemes.bson", "roots.bson", "sources.bson", "wordforms.bson"]

    def __init__(self, gui=False, *args):
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.root_table,
            [Primary(self.root_id, "INT(4) UNSIGNED NOT NULL"),
            Column(self.root_radicals, "VARCHAR(9) NOT NULL"),
            Column(self.root_type, "VARCHAR(12) NOT NULL"),
            Column(self.root_variant, "TINYINT(1) UNSIGNED"),
            Link(self.root_source_id, self.source_table)])
        
        self.add_time_feature(self.source_year)
    
    @staticmethod
    def get_modules():
        return [("bson", "PyMongo", "http://api.mongodb.org/python/current/index.html")]
    
    @staticmethod
    def get_name():
        return "Ġabra"

    @staticmethod
    def get_db_name():
        return "gabra"
    
    @staticmethod
    def get_title():
        return "Ġabra: an open lexicon for Maltese"
        
    @staticmethod
    def get_description():
        return [
            "Ġabra is a free, open lexicon for Maltese, built by collecting various different lexical resources into one common database. While it is not yet a complete dictionary for Maltese, it already contains 16,291 entries and 4,520,596 inflectional word forms. Many of these are linked by root, include translations in English, and are marked for various morphological features."]

    @staticmethod
    def get_references():
        return ['John J. Camilleri. "<i>A Computational Grammar and Lexicon for Maltese</i>", M.Sc. Thesis. Chalmers University of Technology. Gothenburg, Sweden, September 2013. ']

    @staticmethod
    def get_url():
        return "http://mlrs.research.um.edu.mt/resources/gabra/"

    @staticmethod
    def get_license():
        return '<a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>'

    def process_file(self, filename):

        with open("lexemes.bson", "rb") as f:
            for data in bson.decode_file_iter(f):
                # add data

                try:
                    (self._value_word_label, 
                    self._value_word_lemmatranscript, 
                    self._value_word_transcript, 
                    self._value_word_pos) = value.split("; ")
                except ValueError:
                    continue

                self._word_id = self.table(self.word_table).get_or_insert(
                    {self.word_label: self._value_word_label, 
                        self.word_pos: self._value_word_pos,
                        self.word_transcript: self._value_word_transcript,
                        self.word_lemmatranscript: self._value_word_lemmatranscript})
                
                self.add_token_to_corpus(
                    {self.corpus_word_id: self._word_id, 
                    self.corpus_file_id: self._file_id,
                    self.corpus_time: self._value_corpus_time})

if __name__ == "__main__":
    BuilderClass().build()

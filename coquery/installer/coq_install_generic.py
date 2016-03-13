# -*- coding: utf-8 -*-

"""
coq_install_generic.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery.corpusbuilder import *
from coquery import options

if options._use_chardet:
    import chardet

class BuilderClass(BaseCorpusBuilder):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    word_table = "Lexicon"
    word_id = "WordId"
    word_lemma = "Lemma"
    word_label = "Word"
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    def __init__(self, gui=False, pos=True):
        # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui)

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
        
        if pos:
            self.word_pos = "POS"
            self.create_table_description(self.word_table,
                [Identifier(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
                Column(self.word_lemma, "VARCHAR(40) NOT NULL"),
                Column(self.word_pos, "VARCHAR(12) NOT NULL"),
                Column(self.word_label, "VARCHAR(40) NOT NULL")])
        else:
            self.create_table_description(self.word_table,
                [Identifier(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
                Column(self.word_lemma, "VARCHAR(40) NOT NULL"),
                Column(self.word_label, "VARCHAR(40) NOT NULL")])

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

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
            Column(self.file_name, "TINYTEXT NOT NULL"),
            Column(self.file_path, "TINYTEXT NOT NULL")])

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
        
        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "BIGINT(20) UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_file_id, self.file_table)])

    @staticmethod
    def validate_files(l):
        if len(l) == 0:
            raise RuntimeError("<p>No file could be found in the selected directory.</p> ")

def main():
    BuilderClass().build()
    
if __name__ == "__main__":
    main()
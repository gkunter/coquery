# -*- coding: utf-8 -*-

"""
coq_install_cmudict.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function

import codecs

from coquery.corpusbuilder import *
from coquery import transpose

class BuilderClass(BaseCorpusBuilder):
    encoding = "latin-1"
    file_filter = "cmudict*"
    
    def __init__(self, gui=False, *args):
        # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)
        
        # Add table descriptions for the table used in this database.
        #
        # Every table has a primary key that uniquely identifies each entry
        # in the table. This primary key is used to link an entry from one
        # table to an entry from another table. The name of the primary key
        # stored in a string is given as the second argument to the function
        # add_table_description().
        #
        # A table description is a dictionary with at least a 'CREATE' key
        # which takes a list of strings as its value. Each of these strings
        # represents a MySQL instruction that is used to create the table.
        # Typically, this instruction is a column specification, but you can
        # also add other table options for this table. Note that the primary
        # key cannot be set manually.
        # 
        # Add the dictionary table. Each row in this table represents a 
        # dictionary entry. Internally, it double-functions both as the
        # corpus table (which is required to run queries in the first place)
        # and the lexicon table (which is required for word look-up). It
        # has the following columns:
        # 
        # ID
        # An int value containing the unique identifier of the lexicon
        # entry associated with this token.
        #
        # Text
        # A string value containing the orthographic form of the token.
        # Transcript
        # A string value containing the phonological transcription using
        # ARPAbet.
        
        self.corpus_table = "Dictionary"
        self.corpus_id = "ID"
        self.corpus_word = "Word"
        self.corpus_transcript = "Transcript"
        self.corpus_ipa = "IPA"
        
        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.corpus_word, "VARCHAR(50) NOT NULL"),
             Column(self.corpus_transcript, "VARCHAR(100) NOT NULL"),
             Column(self.corpus_ipa, "VARCHAR(100) NOT NULL")])

    @staticmethod
    def validate_files(l):
        if len(l) > 1:
            raise RuntimeError("<p>More than one file has a name that starts with <code>cmudict</code>' in the selected directory:</p><p>{}</p>.".format("<br/>".join(files)))
        if len(l) == 0:
            raise RuntimeError("<p>No dictionary file could be found in the selected directory. The file name of the dictionary file has to start with the sequence <code>cmudict</code>.</p> ")

    def build_load_files(self):
        files = BuilderClass.get_file_list(self.arguments.path, self.file_filter)
        with codecs.open(files[0], "r", encoding = self.arguments.encoding) as input_file:
            content = input_file.readlines()
        if self._widget:
            self._widget.progressSet.emit(len(content) // 100, "Reading dictionary file...")
            self._widget.progressUpdate.emit(0)

        for i, current_line in enumerate(content):
            current_line = current_line.strip()
            if current_line and not current_line.startswith (";;;"):
                word, transcript = current_line.split ("  ")
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
        return "CMUdict is available under the terms of a modified FreeBSD license."
    
    @staticmethod
    def get_description():
        return ["The Carnegie Mellon Pronouncing Dictionary (CMUdict) is a dictionary containing approximately 135.000 English word-forms and their phonemic transcriptions, using a variant of the ARPAbet transcription system."]

if __name__ == "__main__":
    BuilderClass().build()
    
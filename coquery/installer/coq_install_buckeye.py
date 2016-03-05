# -*- coding: utf-8 -*-

"""
coq_install_buckeye.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import codecs
import csv

from coquery.corpusbuilder import *

# The class corpus_code contains the Python source code that will be
# embedded into the corpus library. It provides the Python code that will
# override the default class methods of CorpusClass by methods that are
# tailored for the Buckeye corpus.
#
class corpus_code():
    def sql_string_get_time_info(self, token_id):
        return "SELECT {} FROM {} WHERE {} = {}".format(
                self.resource.corpus_time,
                self.resource.corpus_table,
                self.resource.corpus_id,
                token_id)

    def get_time_info_header(self):
        return ["Time"]

class BuilderClass(BaseCorpusBuilder):
    file_filter = "s*.words.tagged"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Wprd"
    word_pos = "POS"
    word_transcript = "Transcript"
    word_lemmatranscript = "Lemma_Transcript"
    
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    corpus_time = "Time"

    expected_files = [
        's2901b.words.tagged', 's1304a.words.tagged', 's2503b.words.tagged', 
        's1101a.words.tagged', 's1803b.words.tagged', 's2702b.words.tagged', 
        's0402b.words.tagged', 's2402a.words.tagged', 's1104a.words.tagged', 
        's0201a.words.tagged', 's3302b.words.tagged', 's2902b.words.tagged', 
        's0501a.words.tagged', 's1602b.words.tagged', 's3802a.words.tagged', 
        's0504a.words.tagged', 's1303a.words.tagged', 's3102b.words.tagged', 
        's3801b.words.tagged', 's0102b.words.tagged', 's0802b.words.tagged', 
        's0204b.words.tagged', 's2901a.words.tagged', 's1801b.words.tagged', 
        's2802b.words.tagged', 's1102a.words.tagged', 's1603a.words.tagged', 
        's0302a.words.tagged', 's3701a.words.tagged', 's0404a.words.tagged', 
        's3401b.words.tagged', 's3602b.words.tagged', 's2101a.words.tagged', 
        's3403a.words.tagged', 's0305b.words.tagged', 's2503a.words.tagged', 
        's2203b.words.tagged', 's0704a.words.tagged', 's2502b.words.tagged', 
        's0204a.words.tagged', 's1903a.words.tagged', 's3601b.words.tagged', 
        's0203a.words.tagged', 's1503a.words.tagged', 's1002b.words.tagged', 
        's0101b.words.tagged', 's3001a.words.tagged', 's0502a.words.tagged', 
        's3602a.words.tagged', 's2003a.words.tagged', 's0803a.words.tagged', 
        's3202a.words.tagged', 's2703b.words.tagged', 's0205b.words.tagged', 
        's1403a.words.tagged', 's1001a.words.tagged', 's1901b.words.tagged', 
        's2001a.words.tagged', 's1103a.words.tagged', 's3304a.words.tagged', 
        's3701b.words.tagged', 's2102a.words.tagged', 's1301a.words.tagged', 
        's3401a.words.tagged', 's2301b.words.tagged', 's2002a.words.tagged', 
        's0306a.words.tagged', 's0202b.words.tagged', 's3603b.words.tagged', 
        's1702a.words.tagged', 's2102b.words.tagged', 's2001b.words.tagged', 
        's0901a.words.tagged', 's2902a.words.tagged', 's1203a.words.tagged', 
        's2403a.words.tagged', 's0601a.words.tagged', 's1403b.words.tagged', 
        's1101b.words.tagged', 's2201a.words.tagged', 's2903b.words.tagged', 
        's1904a.words.tagged', 's3402a.words.tagged', 's1804a.words.tagged', 
        's4002a.words.tagged', 's2401a.words.tagged', 's0901b.words.tagged', 
        's3503b.words.tagged', 's0703a.words.tagged', 's3101b.words.tagged', 
        's0601b.words.tagged', 's0701b.words.tagged', 's2701a.words.tagged', 
        's3302a.words.tagged', 's0301b.words.tagged', 's1102b.words.tagged', 
        's1803a.words.tagged', 's2701b.words.tagged', 's3703a.words.tagged', 
        's3901a.words.tagged', 's1702b.words.tagged', 's2704a.words.tagged', 
        's2202a.words.tagged', 's1003a.words.tagged', 's0205a.words.tagged', 
        's2703a.words.tagged', 's3702a.words.tagged', 's0403a.words.tagged', 
        's1201b.words.tagged', 's3502a.words.tagged', 's2501b.words.tagged', 
        's4003a.words.tagged', 's2501a.words.tagged', 's0201b.words.tagged', 
        's1203b.words.tagged', 's3703b.words.tagged', 's0102a.words.tagged', 
        's1602a.words.tagged', 's3901b.words.tagged', 's0703b.words.tagged', 
        's1303b.words.tagged', 's4001b.words.tagged', 's0202a.words.tagged', 
        's2302a.words.tagged', 's1502a.words.tagged', 's2502a.words.tagged', 
        's1802a.words.tagged', 's0503b.words.tagged', 's3403b.words.tagged', 
        's1801a.words.tagged', 's0503a.words.tagged', 's3301b.words.tagged', 
        's1202b.words.tagged', 's0303b.words.tagged', 's2401b.words.tagged', 
        's2302b.words.tagged', 's3803a.words.tagged', 's2202b.words.tagged', 
        's3003a.words.tagged', 's0702b.words.tagged', 's2601a.words.tagged', 
        's0902a.words.tagged', 's0903b.words.tagged', 's2101b.words.tagged', 
        's0403b.words.tagged', 's2002b.words.tagged', 's2803a.words.tagged', 
        's1902b.words.tagged', 's0801b.words.tagged', 's3902b.words.tagged', 
        's2402b.words.tagged', 's3002a.words.tagged', 's2802a.words.tagged', 
        's2201b.words.tagged', 's1903b.words.tagged', 's2303b.words.tagged', 
        's1201a.words.tagged', 's2903a.words.tagged', 's2004a.words.tagged', 
        's1601a.words.tagged', 's3402b.words.tagged', 's0803b.words.tagged', 
        's3201b.words.tagged', 's0305a.words.tagged', 's1802b.words.tagged', 
        's1402b.words.tagged', 's1501a.words.tagged', 's3002b.words.tagged', 
        's3501b.words.tagged', 's3101a.words.tagged', 's1904b.words.tagged', 
        's1001b.words.tagged', 's0804a.words.tagged', 's0502b.words.tagged', 
        's0602a.words.tagged', 's1401b.words.tagged', 's3501a.words.tagged', 
        's2203a.words.tagged', 's2601b.words.tagged', 's0702a.words.tagged', 
        's4001a.words.tagged', 's1301b.words.tagged', 's0603a.words.tagged', 
        's1703b.words.tagged', 's1701b.words.tagged', 's3001b.words.tagged', 
        's2403b.words.tagged', 's0206a.words.tagged', 's3303a.words.tagged', 
        's0902b.words.tagged', 's3802b.words.tagged', 's1003b.words.tagged', 
        's3201a.words.tagged', 's2303a.words.tagged', 's0203b.words.tagged', 
        's3702b.words.tagged', 's1703a.words.tagged', 's3801a.words.tagged', 
        's3902a.words.tagged', 's3103a.words.tagged', 's2003b.words.tagged', 
        's2603b.words.tagged', 's1603b.words.tagged', 's1601b.words.tagged', 
        's3903b.words.tagged', 's1202a.words.tagged', 's4004a.words.tagged', 
        's2603a.words.tagged', 's0101a.words.tagged', 's1701a.words.tagged', 
        's0402a.words.tagged', 's3102a.words.tagged', 's0802a.words.tagged', 
        's0903a.words.tagged', 's1302a.words.tagged', 's1002a.words.tagged', 
        's4002b.words.tagged', 's0304b.words.tagged', 's0103a.words.tagged', 
        's3303b.words.tagged', 's3903a.words.tagged', 's3504a.words.tagged', 
        's1502b.words.tagged', 's1004a.words.tagged', 's0304a.words.tagged', 
        's3301a.words.tagged', 's1501b.words.tagged', 's1901a.words.tagged', 
        's0301a.words.tagged', 's2801a.words.tagged', 's2702a.words.tagged', 
        's3502b.words.tagged', 's1104b.words.tagged', 's3503a.words.tagged', 
        's0602b.words.tagged', 's1302b.words.tagged', 's0501b.words.tagged', 
        's4003b.words.tagged', 's0303a.words.tagged', 's3601a.words.tagged', 
        's2602a.words.tagged', 's3202b.words.tagged', 's0401a.words.tagged', 
        's2602b.words.tagged', 's1902a.words.tagged', 's2801b.words.tagged', 
        's2301a.words.tagged', 's3603a.words.tagged', 's0302b.words.tagged', 
        's1401a.words.tagged', 's1604a.words.tagged', 's1103b.words.tagged', 
        's1204a.words.tagged', 's0801a.words.tagged', 's1402a.words.tagged']

    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        # add table descriptions for the tables used in this database.
        #
        # A table description is a dictionary with at least a 'CREATE' key
        # which takes a list of strings as its value. Each of these strings
        # represents a MySQL instruction that is used to create the table.
        # Typically, this instruction is a column specification, but you can
        # also add other table options such as the primary key for this 
        # table.
        #
        # Additionaly, the table description can have an 'INDEX' key which
        # takes a list of tuples as its value. Each tuple has three 
        # elements. The first element is a list of strings containing the
        # column names that are to be indexed. The second element is an
        # integer value specifying the index length for columns of Text
        # types. The third element specifies the index type (e.g. 'HASH' or
        # 'BTREE'). Note that not all MySQL storage engines support all 
        # index types.
        
        # Add the main lexicon table. Each row in this table represents a
        # word-form that occurs in the corpus. It has the following columns:
        #
        # WordId
        # An int value containing the unique identifier of this word-form.
        #
        # Text
        # A text value containing the orthographic representation of this
        # word-form.
        #
        # LemmaId
        # An int value containing the unique identifier of the lemma that
        # is associated with this word-form.
        # 
        # Pos
        # A text value containing the part-of-speech label of this 
        # word-form.
        #
        # Transcript
        # A text value containing the phonological transcription of this
        # word-form.

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "TEXT NOT NULL", index_length=13),
             Column(self.word_pos, "ENUM('CC','CD','DT','DT_VBZ','EX','EX_VBZ','FW','IN','JJ','JJR','JJS','LS','MD','MD_RB','NN','NNP','NNPS','NNS','null','PDT','PRP','PRP_MD','PRP_VBP','PRP_VBZ','PRP$','RB','RBR','RBS','RP','SYM','TO','UH','VB','VBD','VBG','VBG_TO','VBN','VBP','VBP_RB','VBP_TO','VBZ','VBZ_RB','WDT','WP','WP_VBZ','WP$','WRB') NOT NULL"),
             Column(self.word_transcript, "TINYTEXT NOT NULL", index_length=16),
             Column(self.word_lemmatranscript, "VARCHAR(41) NOT NULL")])
                    
        # Add the file table. Each row in this table represents a data file
        # that has been incorporated into the corpus. Each token from the
        # corpus table is linked to exactly one file from this table, and
        # more than one token may be linked to each file in this table.
        # The table contains the following columns:
        #
        # FileId
        # An int value containing the unique identifier of this file.
        # 
        # Path
        # A text value containing the path that points to this data file.

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "TINYINT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "ENUM('s0101a.words.tagged','s0101b.words.tagged','s0102a.words.tagged','s0102b.words.tagged','s0103a.words.tagged','s0201a.words.tagged','s0201b.words.tagged','s0202a.words.tagged','s0202b.words.tagged','s0203a.words.tagged','s0203b.words.tagged','s0204a.words.tagged','s0204b.words.tagged','s0205a.words.tagged','s0205b.words.tagged','s0206a.words.tagged','s0301a.words.tagged','s0301b.words.tagged','s0302a.words.tagged','s0302b.words.tagged','s0303a.words.tagged','s0303b.words.tagged','s0304a.words.tagged','s0304b.words.tagged','s0305a.words.tagged','s0305b.words.tagged','s0306a.words.tagged','s0401a.words.tagged','s0401b.words.tagged','s0402a.words.tagged','s0402b.words.tagged','s0403a.words.tagged','s0403b.words.tagged','s0404a.words.tagged','s0501a.words.tagged','s0501b.words.tagged','s0502a.words.tagged','s0502b.words.tagged','s0503a.words.tagged','s0503b.words.tagged','s0504a.words.tagged','s0601a.words.tagged','s0601b.words.tagged','s0602a.words.tagged','s0602b.words.tagged','s0603a.words.tagged','s0701a.words.tagged','s0701b.words.tagged','s0702a.words.tagged','s0702b.words.tagged','s0703a.words.tagged','s0703b.words.tagged','s0704a.words.tagged','s0801a.words.tagged','s0801b.words.tagged','s0802a.words.tagged','s0802b.words.tagged','s0803a.words.tagged','s0803b.words.tagged','s0804a.words.tagged','s0901a.words.tagged','s0901b.words.tagged','s0902a.words.tagged','s0902b.words.tagged','s0903a.words.tagged','s0903b.words.tagged','s1001a.words.tagged','s1001b.words.tagged','s1002a.words.tagged','s1002b.words.tagged','s1003a.words.tagged','s1003b.words.tagged','s1004a.words.tagged','s1101a.words.tagged','s1101b.words.tagged','s1102a.words.tagged','s1102b.words.tagged','s1103a.words.tagged','s1103b.words.tagged','s1104a.words.tagged','s1104b.words.tagged','s1201a.words.tagged','s1201b.words.tagged','s1202a.words.tagged','s1202b.words.tagged','s1203a.words.tagged','s1203b.words.tagged','s1204a.words.tagged','s1301a.words.tagged','s1301b.words.tagged','s1302a.words.tagged','s1302b.words.tagged','s1303a.words.tagged','s1303b.words.tagged','s1304a.words.tagged','s1401a.words.tagged','s1401b.words.tagged','s1402a.words.tagged','s1402b.words.tagged','s1403a.words.tagged','s1403b.words.tagged','s1501a.words.tagged','s1501b.words.tagged','s1502a.words.tagged','s1502b.words.tagged','s1503a.words.tagged','s1601a.words.tagged','s1601b.words.tagged','s1602a.words.tagged','s1602b.words.tagged','s1603a.words.tagged','s1603b.words.tagged','s1604a.words.tagged','s1701a.words.tagged','s1701b.words.tagged','s1702a.words.tagged','s1702b.words.tagged','s1703a.words.tagged','s1703b.words.tagged','s1801a.words.tagged','s1801b.words.tagged','s1802a.words.tagged','s1802b.words.tagged','s1803a.words.tagged','s1803b.words.tagged','s1804a.words.tagged','s1901a.words.tagged','s1901b.words.tagged','s1902a.words.tagged','s1902b.words.tagged','s1903a.words.tagged','s1903b.words.tagged','s1904a.words.tagged','s1904b.words.tagged','s2001a.words.tagged','s2001b.words.tagged','s2002a.words.tagged','s2002b.words.tagged','s2003a.words.tagged','s2003b.words.tagged','s2004a.words.tagged','s2101a.words.tagged','s2101b.words.tagged','s2102a.words.tagged','s2102b.words.tagged','s2201a.words.tagged','s2201b.words.tagged','s2202a.words.tagged','s2202b.words.tagged','s2203a.words.tagged','s2203b.words.tagged','s2301a.words.tagged','s2301b.words.tagged','s2302a.words.tagged','s2302b.words.tagged','s2303a.words.tagged','s2303b.words.tagged','s2401a.words.tagged','s2401b.words.tagged','s2402a.words.tagged','s2402b.words.tagged','s2403a.words.tagged','s2403b.words.tagged','s2501a.words.tagged','s2501b.words.tagged','s2502a.words.tagged','s2502b.words.tagged','s2503a.words.tagged','s2503b.words.tagged','s2601a.words.tagged','s2601b.words.tagged','s2602a.words.tagged','s2602b.words.tagged','s2603a.words.tagged','s2603b.words.tagged','s2701a.words.tagged','s2701b.words.tagged','s2702a.words.tagged','s2702b.words.tagged','s2703a.words.tagged','s2703b.words.tagged','s2704a.words.tagged','s2801a.words.tagged','s2801b.words.tagged','s2802a.words.tagged','s2802b.words.tagged','s2803a.words.tagged','s2901a.words.tagged','s2901b.words.tagged','s2902a.words.tagged','s2902b.words.tagged','s2903a.words.tagged','s2903b.words.tagged','s3001a.words.tagged','s3001b.words.tagged','s3002a.words.tagged','s3002b.words.tagged','s3003a.words.tagged','s3101a.words.tagged','s3101b.words.tagged','s3102a.words.tagged','s3102b.words.tagged','s3103a.words.tagged','s3201a.words.tagged','s3201b.words.tagged','s3202a.words.tagged','s3202b.words.tagged','s3301a.words.tagged','s3301b.words.tagged','s3302a.words.tagged','s3302b.words.tagged','s3303a.words.tagged','s3303b.words.tagged','s3304a.words.tagged','s3401a.words.tagged','s3401b.words.tagged','s3402a.words.tagged','s3402b.words.tagged','s3403a.words.tagged','s3403b.words.tagged','s3501a.words.tagged','s3501b.words.tagged','s3502a.words.tagged','s3502b.words.tagged','s3503a.words.tagged','s3503b.words.tagged','s3504a.words.tagged','s3601a.words.tagged','s3601b.words.tagged','s3602a.words.tagged','s3602b.words.tagged','s3603a.words.tagged','s3603b.words.tagged','s3701a.words.tagged','s3701b.words.tagged','s3702a.words.tagged','s3702b.words.tagged','s3703a.words.tagged','s3703b.words.tagged','s3801a.words.tagged','s3801b.words.tagged','s3802a.words.tagged','s3802b.words.tagged','s3803a.words.tagged','s3901a.words.tagged','s3901b.words.tagged','s3902a.words.tagged','s3902b.words.tagged','s3903a.words.tagged','s3903b.words.tagged','s4001a.words.tagged','s4001b.words.tagged','s4002a.words.tagged','s4002b.words.tagged','s4003a.words.tagged','s4003b.words.tagged','s4004a.words.tagged') NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])

        # Add the main corpus table. Each row in this table represents a 
        # token in the corpus. It has the following columns:
        # 
        # TokenId
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
            [Identifier(self.corpus_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_word_id, self.word_table),
             Column(self.corpus_time, "DECIMAL(17,6) NOT NULL")])

        
        # Specify that the corpus-specific code is contained in the dummy
        # class 'corpus_code' defined above:
        self._corpus_code = corpus_code
        
        self.add_time_feature(self.corpus_time)
    
    @staticmethod
    def get_name():
        return "Buckeye"

    @staticmethod
    def get_db_name():
        return "buckeye"
    
    @staticmethod
    def get_title():
        return "Buckeye Speech Corpus"
        
    @staticmethod
    def get_language():
        return "English"
    
    @staticmethod
    def get_language_code():
        return "en-US"
        
    @staticmethod
    def get_description():
        return [
            "The Buckeye Corpus of conversational speech contains high-quality recordings from 40 speakers in Columbus OH conversing freely with an interviewer. The speech has been orthographically transcribed and phonetically labeled."]

    @staticmethod
    def get_references():
        return ["Pitt, M.A., Dilley, L., Johnson, K., Kiesling, S., Raymond, W., Hume, E. and Fosler-Lussier, E. (2007) Buckeye Corpus of Conversational Speech (2nd release) [www.buckeyecorpus.osu.edu] Columbus, OH: Department of Psychology, Ohio State University (Distributor)"]

    @staticmethod
    def get_url():
        return "http://buckeyecorpus.osu.edu/"

    @staticmethod
    def get_license():
        return "Buckeye Corpus Content License"

    # Redefine the process_file method so that the .words files provided
    # by the Buckeye corpus are handled correctly:
    def process_file(self, filename):
        file_body = False
        # read file using the specified encoding (default is 'utf-8), and 
        # retry using 'ISO-8859-1'/'latin-1' in case of an error:
        try:
            with codecs.open(filename, "r", encoding=self.arguments.encoding) as input_file:
                input_data = input_file.read()
        except UnicodeDecodeError:
            with codecs.open(filename, "r", encoding="ISO-8859-1") as input_file:
                input_data = input_file.read()
                
        input_data = [x.strip() for x in input_data.splitlines() if x.strip()]
        for row in input_data:
            while "  " in row:
                row = row.replace("  ", " ")
            # only process the lines after the hash mark:
            if row == "#":
                file_body = True
            elif file_body:
                try:
                    self._value_corpus_time, _, remain = row.partition(" ")
                    _, _, value = remain.partition(" ")
                except ValueError:
                    continue

                try:
                    (self._value_word_label, 
                    self._value_word_lemmatranscript, 
                    self._value_word_transcript, 
                    self._value_word_pos) = value.split("; ")
                except ValueError:
                    continue

                if float(self._value_corpus_time) >= 0:
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

from __future__ import unicode_literals
import codecs
import csv

import corpusbuilder

# The class corpus_code contains the Python source code that will be
# embedded into the corpus library. It provides the Python code that will
# override the default class methods of SQLCorpus by methods that are
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

class BuckeyeBuilder(corpusbuilder.BaseCorpusBuilder):
    def __init__(self):
       # all corpus builders have to call the inherited __init__ function:
        super(BuckeyeBuilder, self).__init__()
        
        # Read only .words files from the corpus path:
        self.file_filter = "*.words"
        
        # specify which features are provided by this corpus and lexicon:
        self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_PHON", "LEX_POS"]
        self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_TIMING"]
        
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
        
        self.corpus_table = "corpus"
        self.corpus_id = "TokenId"
        self.corpus_word_id = "WordId"
        self.corpus_source_id = "FileId"
        self.corpus_time = "Time"

        self.add_table_description(self.corpus_table, self.corpus_id,
            {"CREATE": [
                "`{}` BIGINT(20) UNSIGNED NOT NULL".format(self.corpus_id),
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.corpus_word_id),
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.corpus_source_id),
                "`{}` DECIMAL(11,6) UNSIGNED".format(self.corpus_time)],
            "INDEX": [
                ([self.corpus_word_id], 0, "HASH"),
                ([self.corpus_source_id], 0, "HASH")]})
        
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

        self.word_table = "word"
        self.word_id = "WordId"
        self.word_label = "Text"
        self.word_lemma_id = "LemmaId"
        self.word_pos = "Pos"
        self.word_transcript = "Transcript"
        
        self.add_table_description(self.word_table, self.word_id,
            {"CREATE": [
                "`{}` SMALLINT(5) UNSIGNED NOT NULL".format(self.word_id),
                "`{}` TEXT NOT NULL".format(self.word_label),
                "`{}` SMALLINT(5) UNSIGNED NOT NULL".format(self.word_lemma_id),
                "`{}` VARCHAR(7) NOT NULL".format(self.word_pos),
                "`{}` TINYTEXT NOT NULL".format(self.word_transcript)],
            "INDEX": [
                ([self.word_lemma_id], 0, "HASH"),
                ([self.word_pos], 0, "BTREE"),
                ([self.word_label], 4, "BTREE"),
                ([self.word_transcript], 4, "BTREE")]})

        # Add the lemma table. Each row in this table represents a lemma in
        # the lexicon. Each word-form from the lexicon table is linked to
        # exactly one lemma from this table, and more than one word-form
        # may be linked to each lemma in this table. The table has the 
        # following columns:
        #
        # LemmaId
        # An int value containing the unique identifier of this lemma.
        #
        # Text
        # A text value containing the orthographic representation of this
        # lemma.
        # 
        # Transcript
        # A text value containing the phonological transcription of this 
        # lemma.

        self.lemma_table = "lemma"
        self.lemma_id = "LemmaId"
        self.lemma_label = "Text"
        self.lemma_transcript = "Transcript"
        
        self.add_table_description(self.lemma_table, self.lemma_id,
            {"CREATE": [
                "`{}` SMALLINT(5) UNSIGNED NOT NULL".format(self.lemma_id),
                "`{}` TEXT NOT NULL".format(self.lemma_label),
                "`{}` VARCHAR(41) NOT NULL".format(self.lemma_transcript)],
            "INDEX": [
                ([self.lemma_label], 4, "BTREE")]})

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
        
        self.file_table = "file"
        self.file_id = "FileId"
        self.file_label = "Path"

        self.add_table_description(self.file_table, self.file_id,
            {"CREATE": [
                "`{}` SMALLINT(3) UNSIGNED NOT NULL".format(self.file_id),
                "`{}` TINYTEXT NOT NULL".format(self.file_label)]})

        # Any corpus that provides either CORP_CONTEXT, CORP_SOURCE or
        # CORP_FILENAME also needs to specify a source table. Each row in
        # this source table represents a corpus source, and it has to 
        # contain at least the following column:
        #
        # SourceId
        # An int value containing the unique identifier of this source.
        # 
        # Additional columns may also store further information such as 
        # year or genre.
        # 
        # In this generic corpus, detailed information on the source texts
        # is not available, so no separate source table is required. 
        # Instead, the corpus uses the file table as the source table:
        
        self.source_table = "file"
        self.source_id = "FileId"
        
        # Specify that the corpus-specific code is contained in the dummy
        # class 'corpus_code' defined above:
        self._corpus_code = corpus_code
        
    def get_description(self):
        return "This script makes the Buckeye corpus available to Coquery by reading the corpus data files from {} into the MySQL database '{}'.".format(self.arguments.path, self.arguments.db_name)

    # Redefine the process_file method so that the .words files provided
    # by the Buckeye corpus are handled correctly:
    def process_file(self, filename):
        with codecs.open(filename, "rt", encoding="utf8") as input_file:
            for current_line in csv.reader(input_file, delimiter=str("\t")):
                if len(current_line) == 5:
                    time, word, lemma_trans, trans, pos = current_line
        
                    if float(time) >= 0:
                        lemma_id = self.table_get(self.lemma_table, 
                            {self.lemma_label: word.lower(), 
                             self.lemma_transcript: lemma_trans})[self.lemma_id]
                        word_id = self.table_get(self.word_table, 
                            {self.word_label: word, 
                             self.word_lemma_id: lemma_id, 
                             self.word_pos: pos,
                             self.word_transcript: trans})[self.word_id]
                        self.table_add(self.corpus_table, 
                            {self.corpus_word_id: word_id, 
                             self.corpus_source_id: self._file_id,
                             self.corpus_time: time})

if __name__ == "__main__":
    BuckeyeBuilder().build()

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import corpusbuilder

class GenericCorpusBuilder(corpusbuilder.BaseCorpusBuilder):
    def __init__(self, gui=False):
        # all corpus builders have to call the inherited __init__ function:
        super(GenericCorpusBuilder, self).__init__(gui)
        
        # specify which features are provided by this corpus and lexicon:
        self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_POS"]
        self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS"]

        # add table descriptions for the tables used in this database.
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
        self.corpus_file_id = "FileId"
        
        self.add_table_description(self.corpus_table, self.corpus_id,
            {"CREATE": [
                "`{}` BIGINT(20) UNSIGNED NOT NULL".format(self.corpus_id),
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.corpus_word_id),
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.corpus_file_id)],
            "INDEX": [
                ([self.corpus_word_id], 0, "HASH"),
                ([self.corpus_file_id], 0, "HASH")]})
        
        # Add the main lexicon table. Each row in this table represents a
        # word-form that occurs in the corpus. It has the following columns:
        #
        # WordId
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
        
        self.word_table = "word"
        self.word_id = "WordId"
        self.word_lemma_id = "LemmaId"
        self.word_label = "Text"
        self.word_pos = "Pos"
        
        create_columns = ["`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.word_id),
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.word_lemma_id),
                "`{}` VARCHAR(12) NOT NULL".format(self.word_pos),
                "`{}` VARCHAR(40) NOT NULL".format(self.word_label)]
        index_columns = [([self.word_lemma_id], 0, "HASH"),
                ([self.word_pos], 0, "BTREE"),
                ([self.word_label], 0, "BTREE")]

        self.add_table_description(self.word_table, self.word_id,
            {"CREATE": create_columns,
            "INDEX": index_columns})
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
        
        self.lemma_table = "lemma"
        self.lemma_id = "LemmaId"
        self.lemma_label = "Text"
        
        self.add_table_description(self.lemma_table, self.lemma_id,
            {"CREATE": [
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.lemma_id),
                "`{}` TINYTEXT NOT NULL".format(self.lemma_label)],
            "INDEX": [
                ([self.lemma_label], 0, "BTREE")]})

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
        self.file_name = "File"
        self.file_path = "Path"
        
        self.add_table_description(self.file_table, self.file_id,
            {"CREATE": [
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.file_id),
                "`{}` TINYTEXT NOT NULL".format(self.file_name),
                "`{}` TINYTEXT NOT NULL".format(self.file_path)]})

        # The following is obsolete for the experimental query method.
        ## Any corpus that provides either CORP_CONTEXT, CORP_SOURCE or
        ## CORP_FILENAME also needs to specify a source table. Each row in
        ## this source table represents a corpus source, and it has to 
        ## contain at least the following column:
        ##
        ## SourceId
        ## An int value containing the unique identifier of this source.
        ## 
        ## Additional columns may also store further information such as 
        ## year or genre.
        ## 
        ## In this generic corpus, detailed information on the source texts
        ## is not available, so no separate source table is required. 
        ## Instead, the corpus uses the file table as the source table:
        
        #self.source_table = "file"
        #self.source_id = "FileId"

    def get_description(self):
        return "This script creates the corpus '{}' by reading data from the files in {} to populate the MySQL database '{}' so that the database can be queried by Coquery.".format(self.name, self.arguments.path, self.arguments.db_name)

def main():
    GenericCorpusBuilder().build()
    
if __name__ == "__main__":
    main()
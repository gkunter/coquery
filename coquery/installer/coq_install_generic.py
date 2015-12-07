# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from corpusbuilder import *

class GenericCorpusBuilder(BaseCorpusBuilder):
    corpus_table = "Corpus"
    corpus_id = "TokenId"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    word_table = "Lexicon"
    word_id = "WordId"
    word_lemma = "Lemma"
    word_label = "Word"
    word_pos = "POS"
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    def __init__(self, gui=False):
        # all corpus builders have to call the inherited __init__ function:
        super(GenericCorpusBuilder, self).__init__(gui)
        
        # specify which features are provided by this corpus and lexicon:
        #self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_POS"]
        #self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS"]
        
        #self.documentation_url = "(no URL availabe)"

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
        
        self.create_table_description(self.word_table,
            [Primary(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
            Column(self.word_lemma, "VARCHAR(40) NOT NULL"),
            Column(self.word_pos, "VARCHAR(12) NOT NULL"),
            Column(self.word_label, "VARCHAR(40) NOT NULL")])

        # Add the file table. Each row in this table represents a data file
        # that has been incorporated into the corpus. Each token from the
        # corpus table is linked to exactly one file from this table, and
        # more than one token may be linked to each file in this table.
        # The table contains the following columns:
        #
        # FileId
        # An int value containing the unique identifier of this file.
        # 
        # File 
        # A text value containing the base file name of this data file.
        # 
        # Path
        # A text value containing the path that points to this data file.
        

        self.create_table_description(self.file_table,
            [Primary(self.file_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
            Column(self.file_name, "TINYTEXT NOT NULL"),
            Column(self.file_path, "TINYTEXT NOT NULL")])

        self.create_table_description(self.corpus_table,
            [Primary(self.corpus_id, "BIGINT(20) UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_file_id, self.file_table)])

    def get_description(self):
        return "This script creates the corpus '{}' by reading data from the files in {} to populate the MySQL database '{}' so that the database can be queried by Coquery.".format(self.name, self.arguments.path, self.arguments.db_name)

def main():
    GenericCorpusBuilder().build()
    
if __name__ == "__main__":
    main()
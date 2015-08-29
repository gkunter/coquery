from __future__ import unicode_literals

from corpusbuilder import *
import codecs

class CMUdictBuilder(BaseCorpusBuilder):
    def __init__(self):
        # all corpus builders have to call the inherited __init__ function:
        super(CMUdictBuilder, self).__init__()
        
        # specify which features are provided by this corpus and lexicon:
        self.lexicon_features = ["LEX_WORDID", "LEX_ORTH", "LEX_PHON"]
        self.corpus_features = ["CORP_STATISTICS"]
        self.documentation_url = 'http://www.speech.cs.cmu.edu/cgi-bin/cmudict'
        
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
        # Additionaly, the table description can have an 'INDEX' key which
        # takes a list of tuples as its value. Each tuple has three 
        # elements. The first element is a list of strings containing the
        # column names that are to be indexed. The second element is an
        # integer value specifying the index length for columns of Text
        # types. The third element specifies the index type (e.g. 'HASH' or
        # 'BTREE'). Note that not all MySQL storage engines support all 
        # index types.
        
        # Add the dictionary table. Each row in this table represents a 
        # dictionary entry. Internally, it double-functions both as the
        # corpus table (which is required to run queries in the first place)
        # and the lexicon table (which is required for word look-up). It
        # has the following columns:
        # 
        # TokenId
        # An int value containing the unique identifier of the token
        #
        # WordId
        # An int value containing the unique identifier of the lexicon
        # entry associated with this token.
        #
        # Transcript
        # A string value containing the phonological transcription using
        # SAMPA (I guess).

        
        self.corpus_table = "dict"
        self.corpus_id = "WordId"
        self.corpus_word_id = "WordId"
        self.word_table = "dict"
        self.word_id = "WordId"
        self.word_label = "Text"
        self.word_transcript = "Transcript"
        
        
        self.add_table_description(self.word_table, self.word_id,
            {"CREATE": [
                "`{}` MEDIUMINT(6) UNSIGNED NOT NULL".format(self.word_id),
                "`{}` VARCHAR(33) NOT NULL".format(self.word_label),
                "`{}` VARCHAR(93) NOT NULL".format(self.word_transcript)],
            "INDEX": [
                ([self.word_label], 0, "HASH"),
                ([self.word_transcript], 0, "HASH")]})
        
        self.add_new_table_description(self.word_table,
            [Primary(self.corpus_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(33) NOT NULL"),
             Column(self.word_transcript, "VARCHAR(93) NOT NULL")])


    def create_tables(self):
        for i, current_table in enumerate(self.table_description):
            if self.Con.has_table(current_table):
                self.Con.drop_table(current_table)
        super(CMUdictBuilder, self).create_tables()

    def load_files(self):
        with codecs.open(self.arguments.path, "r", encoding = self.arguments.encoding) as input_file:
            for word_id, current_line in enumerate(input_file):
                current_line = current_line.strip()
                if current_line and not current_line.startswith (";;;"):
                    word, transcript = current_line.split ("  ")
                    self.table_add(self.word_table, 
                        {self.word_id: word_id,
                         self.word_label: word, 
                         self.word_transcript: transcript})
        self.Con.commit()
                    
    def get_description(self):
        return "This script creates the corpus '{}' by reading data from the files in {} to populate the MySQL database '{}' so that the database can be queried by Coquery.".format(self.name, self.arguments.path, self.arguments.db_name)

if __name__ == "__main__":
    CMUdictBuilder().build()
    
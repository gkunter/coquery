# -*- coding: utf-8 -*-

"""
coq_install_coha.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import codecs
import csv
import itertools
import tempfile

from coquery.corpusbuilder import *
from coquery.defines import *
from coquery import options

class BuilderClass(BaseCorpusBuilder):
    file_filter = "????.txt"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "SourceId"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_labelcs = "WordCS"
    word_lemma = "Lemma"
    word_pos = "POS"

    source_table = "Sources"
    source_id = "SourceId"
    source_label = "Title"
    source_author = "Author"
    source_year = "Year"
    source_genre = "Genre"
    source_words = "Words"

    expected_files = ["sources_coha.csv", "lexicon.txt",
        "1810.txt", "1820.txt", "1830.txt", "1840.txt", "1850.txt", 
        "1860.txt", "1870.txt", "1880.txt", "1890.txt", "1900.txt", 
        "1910.txt", "1920.txt", "1930.txt", "1940.txt", "1950.txt", 
        "1960.txt", "1970.txt", "1980.txt", "1990.txt", "2000.txt"]

    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(26) NOT NULL"),
             Column(self.word_labelcs, "VARCHAR(48) NOT NULL"),
             Column(self.word_lemma, "VARCHAR(24) NOT NULL"),
             Column(self.word_pos, "VARCHAR(24) NOT NULL")])

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "CHAR(8) NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])

        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.source_words, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.source_genre, "ENUM('FIC','MAG','NEWS','NF') NOT NULL"),
             Column(self.source_year, "SMALLINT(4) NOT NULL"),
             Column(self.source_label, "VARCHAR(155) NOT NULL"),
             Column(self.source_author, "VARCHAR(100) NOT NULL")])
            
        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "INT(9) UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_source_id, self.source_table)])

        self.add_time_feature(self.source_year)
    
    @staticmethod
    def get_name():
        return "COHA"

    @staticmethod
    def get_db_name():
        return "coha"

    @staticmethod
    def get_language():
        return "English"
    
    @staticmethod
    def get_language_code():
        return "en-US"
        
    @staticmethod
    def get_title():
        return "Corpus of Historical American English"
        
    @staticmethod
    def get_description():
        return [
            "The Corpus of Historical American English (COHA) is the largest structured corpus of historical English. The corpus was created by Mark Davies of Brigham Young University, with generous funding from the US National Endowment for the Humanities.",
            "COHA allows you search more than 400 million words of text of American English from 1810 to 2009."]

    @staticmethod
    def get_references():
        return ["Davies, Mark. (2010-) <i>The Corpus of Historical American English: 400 million words, 1810-2009</i>. Available online at http://corpus.byu.edu/coha/."]

    @staticmethod
    def get_url():
        return "http://corpus.byu.edu/coha/"

    @staticmethod
    def get_license():
        return "COHA is available under the terms of a commercial license."

    @staticmethod
    def get_installation_note():
        _, _, db_type, _, _ = options.get_con_configuration()
        
        if db_type == SQL_MYSQL:
            return """
            <p><b>MySQL installation note</b><p>
            <p>The COHA installer uses a special feature of MySQL servers 
            which allows to load large chunks of data into the database in a 
            single step.</p>
            <p>This feature notably speeds up the installation of the COHA 
            corpus. However, it may be disabled on your MySQL servers. In that 
            case, the installation will fail with an error message similar to 
            the following: </p>
            <p><code>The used command is not allowed with this MySQL version</code></p>
            <p>Should the installation fail, please ask your MySQL server 
            administrator to enable loading of local in-files by setting the 
            option <code>local-infile</code> in the MySQL configuration file.
            </p>                
            """
        else:
            return None

    def build_load_files(self):
        chunk_size = 250000
        def get_chunk(iterable):
            """
            Yield a chunk from the big file given as 'iterable'.
            
            This function is based on a rather elegant solution posted on 
            Stack Overflow: http://stackoverflow.com/a/24862655
            """
            iterable = iter(iterable)
            while True:
                yield itertools.chain(
                    [next(iterable)], 
                    itertools.islice(iterable, chunk_size - 1))
        
        files = sorted(self.get_file_list(self.arguments.path, self.file_filter))

        if self._widget:
            self._widget.progressSet.emit(len(files), "")

        # Unfortunately, the connection to the MySQL server may break 
        # with larger files. It is as yet unclear whether this can be 
        # fixed on the server side by a suitable configuration. For 
        # the time being, we will break the text files into smaller 
        # chunks of currently 250000 lines. These chunks are written 
        # into temporary files, which are in turn read by the MySQL 
        # server using the LOAD DATA LOCAL INLINE command.
        # Sadly, this is not very fast.

        for count, file_name in enumerate(files):
            base_name = os.path.basename(file_name)
            
            if self._widget:
                self._widget.labelSet.emit("Reading '{}' (file %v out of %m)".format(os.path.basename(file_name)))

            if base_name == "lexicon.txt":
                with codecs.open(file_name, "r", encoding="latin-1") as big_file:
                    # Iterate the chunks:
                    for i, lines in enumerate(get_chunk(big_file)):
                        if self.interrupted:
                            return
                        if i == 0:
                            arguments = "LINES TERMINATED BY '\\n' IGNORE 3 LINES"
                        else:
                            arguments = "LINES TERMINATED BY '\\n'"
                        
                        # create and fill temporary file:
                        temp_file = tempfile.NamedTemporaryFile("w", delete=False)
                        if sys.version_info < (3, 0):
                            temp_file.write(u"\n".join([x.strip() for x in lines]).encode("utf-8"))
                        else:
                            temp_file.write("\n".join([x.strip() for x in lines]))
                        temp_file.close()
                        self.DB.load_infile(temp_file.name, self.word_table, arguments)
                        os.remove(temp_file.name)
            elif base_name == "sources_coha.csv":
                with codecs.open(file_name, "r", encoding="latin-1") as big_file:
                    # Iterate the chunks:
                    for i, lines in enumerate(get_chunk(big_file)):
                        if self.interrupted:
                            return
                        if i == 0:
                            arguments = "FIELDS TERMINATED BY '\\t' LINES TERMINATED BY '\\n' IGNORE 1 LINES"
                        else:
                            arguments = "FIELDS TERMINATED BY '\\t' LINES TERMINATED BY '\\n'"
                        
                        # create and fill temporary file:
                        temp_file = tempfile.NamedTemporaryFile("w", delete=False)
                        if sys.version_info < (3, 0):
                            temp_file.write(u"\n".join([x.strip() for x in lines]).encode("utf-8"))
                        else:
                            temp_file.write("\n".join([x.strip() for x in lines]))
                        temp_file.close()
                        self.DB.load_infile(temp_file.name, self.source_table, arguments)
                        os.remove(temp_file.name)
            else:
                arguments = "LINES TERMINATED BY '\\n' ({}, {}, {}) ".format(
                    self.corpus_source_id,
                    self.corpus_id,
                    self.corpus_word_id)
                with codecs.open(file_name, "r", encoding="latin-1") as big_file:
                    
                    # Iterate the chunks:
                    for i, lines in enumerate(get_chunk(big_file)):
                        if self.interrupted:
                            return

                        content = list(lines)
                        self._corpus_id += len(content)
                        
                        # create and fill temporary file:
                        temp_file = tempfile.NamedTemporaryFile("w", delete=False)
                        temp_file.write("\n".join([x.strip() for x in content]))
                        temp_file.close()
                        self.DB.load_infile(temp_file.name, self.corpus_table, arguments)
                        os.remove(temp_file.name)

                self.store_filename(base_name)

            if self._widget:
                self._widget.progressUpdate.emit(count + 1)

if __name__ == "__main__":
    BuilderClass().build()

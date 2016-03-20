from __future__ import unicode_literals
from __future__ import print_function
import codecs
import csv
import os
import collections, difflib, string

from coquery import corpusbuilder

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

class BURSCBuilder(corpusbuilder.BaseCorpusBuilder):
    def __init__(self):
       # all corpus builders have to call the inherited __init__ function:
        super(BURSCBuilder, self).__init__()
        
        # Read only .txt files from the corpus path:
        self.file_filter = "*.txt"
        
        # specify which features are provided by this corpus and lexicon:
        self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_PHON", "LEX_POS"]
        self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_TIMING"]
        self.documentation_url = "https://catalog.ldc.upenn.edu/LDC96S36"
        
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
                "`{}` TEXT NOT NULL".format(self.word_lemma_id),
                "`{}` VARCHAR(10) NOT NULL".format(self.word_pos),
                "`{}` TINYTEXT NOT NULL".format(self.word_transcript)],
            "INDEX": [
                ([self.word_lemma_id], 0, "BTREE"),
                ([self.word_pos], 0, "BTREE"),
                ([self.word_label], 0, "BTREE"),
                ([self.word_transcript], 0, "BTREE")]})

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
        return "This script makes the Boston University Radio Speech Corpus available to Coquery by reading the corpus data files from {} into the MySQL database '{}'.".format(self.arguments.path, self.arguments.db_name)

    def get_transcript(self, word):
        try:
            i = self._transcript_index
            while True:
                _, transcript = self._transcript_list[i]
                i += 1
                if word == _:
                    self._transcript_index = i
                    return transcript
        except IndexError as e:
            print(self._file_name)
            print(i, word, self._transcript_index)
            print("\n".join(["{:<3} {:<30} {}".format(i, word, transcript) for i, (word, transcript) in enumerate(self._transcript_list)]))
            raise e
        
    def get_pos(self, word):
        i = self._pos_index
        # Sometimes, words start with (undocumented) braces. They may mess
        # up POS retrieval, and are stripped.
        word = word.strip("}").strip("{")
        while True:
            try:
                _, pos = self._pos_list[i]
            except IndexError as e:
                print(self._file_name)
                print(i, self._pos_index)
                print(word)
                #print(self._pos_list)
                #print(self._pos_list[i:])
                return "<NA>"
            # check if word matches the next word in the pos list:
            if word.lower()[:min(len(word), len(_))] != _.lower()[:min(len(word), len(_))]:
                i += 1
                if i >= len(self._pos_list):
                    pos = "<NA>"
                    break
            else:
                self._pos_index = i + 1
                break
        return pos

    def process_wrd_file(self, filename):
        root, ext = os.path.splitext(filename)
        self._wrd_list = []
        try:
            with codecs.open("{}.wrd".format(root), "r", encoding="latin-1") as wrd_file:
                in_body = False
                for row in wrd_file:
                    row = row.strip()
                    if row == "#":
                        in_body = True
                    elif in_body:
                        try:
                            time, _, label = row.split()
                        except ValueError:
                            if len(row.split()) > 3:
                                print("[{}]".format(row))
                                asd
                            pass
                        else:
                            if label.rfind("/") > -1:
                                label = label[:label.rfind("/")]
                            if not label.startswith(">"):
                                self._wrd_list.append([label, time])
            self._wrd_index = 0
        except IOError:
            pass

    def process_pos_file(self, filename):
        # try to read the .pos file for the .wrd file:
        self._pos_list = collections.OrderedDict()
        root, ext = os.path.splitext(filename)
        try:
            with codecs.open("{}.pos".format(root), "r") as pos_file:
                for row in pos_file:
                    row = row.strip()
                    if row.strip():
                        word, pos = row.split()
                        self._pos_list[word] = pos
            self._pos_index = 0
        except IOError:
            pass

    def process_transcript_file(self, filename):
        self._transcript_list = collections.OrderedDict()
        root, ext = os.path.splitext(filename)
        # try to read the .aln file:
        transcript_file = "{}.alb".format(root)
        if not os.path.exists(transcript_file):
            transcript_file = "{}.ala".format(root)
        if os.path.exists(transcript_file):
            with codecs.open(transcript_file, "r") as transcript_file:
                transcript = []
                for row in transcript_file:
                    if row.strip():
                        if row.startswith(">"):
                            word = row[1:].strip()
                            if word.lower() not in ["endsil", "sil"]:
                                self._transcript_list[word] = " ".join(transcript)
                            transcript = []
                        else:
                            if row.count("\t") == 2:
                                phone, start, dur = row.split("\t")
                                if phone.lower() not in ["brth", "pau", "sil", "h#"]:
                                    transcript.append(phone)
                            else:
                                print(row)
        self._transcript_index = 0
        
    def process_txt_file(self, filename):
        try:
            with codecs.open(filename, "r", encoding=self.arguments.encoding) as input_file:
                raw_text = input_file.read()
        except UnicodeDecodeError:
            with codecs.open(filename, "r", encoding="ISO-8859-1") as input_file:
                raw_text = input_file.read()
        self._word_list = []
        for word in raw_text.split():
            word = word.strip()
            if word.lower() != "brth":
                self._word_list.append(word)

    def normalize(self, word):
        for p in string.punctuation:
            word = word.replace(p, '')
        return word.lower().strip()
    
    def store_filename(self, *args):
        pass

    # Redefine the process_file method so that the .words files provided
    # by the Buckeye corpus are handled correctly:
    def process_file(self, filename):
        self.process_wrd_file(filename)
        self.process_pos_file(filename)
        self.process_transcript_file(filename)
        self.process_txt_file(filename)
        #print("Words in .wrd:", len(self._wrd_list))
        #print("Words in .txt: ", len(self._word_list))
        wrds = [self.normalize(x) for x, time in self._wrd_list]
        txt = [self.normalize(x) for x in self._word_list]
        
        diff = list(difflib.ndiff(wrds, txt))
        wrds_counter = 0
        txt_counter = 0
        diff = [x for x in diff if not(x.startswith("?")) and x.strip()]
        if len(diff) <> len(txt):
            print(filename)
            for i, x in enumerate(diff):
                fields = x.split()
                if len(fields) == 1:
                    code = " "
                    word = fields[0]
                else:
                    code = fields[0]
                    word = fields[1]

                if diff[i].startswith("-"):
                    if not diff[i+1].startswith("+"):
                        print("Insert '{}' at {}".format(self._wrd_list[wrds_counter][0], txt_counter))
                        self._word_list.insert(txt_counter, self._wrd_list[wrds_counter][0])
                        txt_counter += 1
                        wrds_counter += 1
                    else:
                        print("Change from '{}' to '{}'".format(self._word_list[txt_counter],
                                                        self._wrd_list[wrds_counter][0]))
                        self._word_list[txt_counter] = self._wrd_list[wrds_counter][0]
                else:
                    txt_counter += 1
                    wrds_counter += 1

        wrds = [self.normalize(x) for x, time in self._wrd_list]
        txt = [self.normalize(x) for x in self._word_list]
        
        diff = list(difflib.ndiff(wrds, txt))
        if len(diff) <> len(txt):
            print(filename)
            for i, x in enumerate(diff):
                print(x)

            asd
    
if __name__ == "__main__":
    BURSCBuilder().build()

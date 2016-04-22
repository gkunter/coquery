# -*- coding: utf-8 -*-

"""
coq_install_icle.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import re
import string
import pandas as pd

from coquery.corpusbuilder import *
from coquery.unicode import utf8
from coquery.bibliography import *

class BuilderClass(BaseCorpusBuilder):
    file_filter = "*.*"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_lemma = "Lemma"
    word_pos = "POS"
    word_claws = "CLAWS"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "TextId"
    corpus_file_id = "FileId"
    corpus_speaker_id = "SpeakerId"
    
    source_table = "Texts"
    source_id = "TextId"
    source_batch = "Batch"
    source_title = "Title"
    source_type = "Type"
    source_condition = "Conditions"
    source_reftool = "Reference_tools"
    source_exam = "Examination"
    source_status = "Status"
    source_institute = "Institute"
    source_comment = "Comments"
    
    speaker_table = "Speakers"
    speaker_id = "SpeakerId"
    speaker_age = "Age"
    speaker_sex = "Gender"
    speaker_country = "Country"
    speaker_language = "Native_language"
    speaker_schoolenglish = "Years_English_at_school"
    speaker_unienglish = "Years_English_at_university"
    speaker_abroadenglish = "Months_English_speaking_country"
    speaker_otherlang1 = "Other_language_1"
    speaker_otherlang2 = "Other_language_2"
    speaker_otherlang3 = "Other_language_3"
    
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    special_files = ["source_info.csv", "tokens.txt"]
    expected_files = special_files + ["BGSU1003.txt", "CNHK1052.txt"]
    
    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)
        
        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
            Column(self.file_name, "TINYTEXT NOT NULL"),
            Column(self.file_path, "TINYTEXT NOT NULL")])

        self.create_table_description(self.speaker_table,
            [Identifier(self.speaker_id, "MEDIUMINT(4) UNSIGNED NOT NULL"),
            Column(self.speaker_age, "TINYINT(2) UNSIGNED"),
            Column(self.speaker_sex, "ENUM('Female','Male','Unknown') NOT NULL"),
            Column(self.speaker_country, "VARCHAR(15) NOT NULL"),
            Column(self.speaker_language, "VARCHAR(17) NOT NULL"),
            Column(self.speaker_schoolenglish, "TINYINT(2) UNSIGNED"),
            Column(self.speaker_unienglish, "DECIMAL(1,1) UNSIGNED"),
            Column(self.speaker_abroadenglish, "DECIMAL(3,2) UNSIGNED"),
            Column(self.speaker_otherlang1, "VARCHAR(16)"),
            Column(self.speaker_otherlang2, "VARCHAR(16)"),
            Column(self.speaker_otherlang3, "VARCHAR(9)"),
                ])

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "MEDIUMINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(60) NOT NULL"),
             Column(self.word_lemma, "VARCHAR(30) NOT NULL"),
             Column(self.word_pos, "VARCHAR(10) NOT NULL"),
             Column(self.word_claws, "VARCHAR(10) NOT NULL")])

        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "MEDIUMINT(4) UNSIGNED NOT NULL"),
             Column(self.source_batch, "CHAR(19) NOT NULL"),
             Column(self.source_title, "VARCHAR(434) NOT NULL"),
             Column(self.source_type, "ENUM('Argumentative','Literary','Other') NOT NULL"),
             Column(self.source_condition, "ENUM('No Timing','Timed','Unknown') NOT NULL"),
             Column(self.source_reftool, "ENUM('Yes','No','Unknown') NOT NULL"),
             Column(self.source_exam, "ENUM('Yes','No','Unknown') NOT NULL"),
             Column(self.source_status, "ENUM('Complete','Incomplete') NOT NULL"),
             Column(self.source_institute, "VARCHAR(88) NOT NULL"),
             Column(self.source_comment, "VARCHAR(141) NOT NULL"),
                ])
    
        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_source_id, self.source_table),
             Link(self.corpus_speaker_id, self.speaker_table)])
            
        self._sources = {}
        self._speakers = {}
        self._words = {}

    @staticmethod
    def get_name():
        return "ICLE"

    @staticmethod
    def get_db_name():
        return "coq_icle"
    
    @staticmethod
    def get_title():
        return "The International Corpus of Learner English"
        
    @staticmethod
    def get_language():
        return "English"
    
    @staticmethod
    def get_language_code():
        return "en-L2"
        
    @staticmethod
    def get_description():
        return [
            "The International Corpus of Learner English contains argumentative essays written by higher intermediate to advanced learners of English from several mother tongue backgrounds (Bulgarian, Chinese, Czech, Dutch, Finnish, French, German, Italian, Japanese, Norwegian, Polish, Russian, Spanish, Swedish, Tswana, Turkish). The corpus is the result of collaboration with a wide range of partner universities internationally. The first version was published on CD-ROM in 2002, and an expanded version, ICLEv2, was published in 2009. The corpus is highly homogeneous as all partners have adopted the same corpus collection guidelines."]

    @staticmethod
    def get_references():
        return [InCollection(
            authors=PersonList(Person(first="Sylviane", last="Granger")),
            year=2008,
            contributiontitle="Learner corpora",
            editors=PersonList(
                Person(first="Anke", last="Lüdeling"),
                Person(first="Merja", last="Kytö")),
            title="Handbook on corpus linguistics",
            publisher="Mouton de Gruyter",
            address="Berlin")]

    @staticmethod
    def get_url():
        return "https://www.uclouvain.be/en-cecl-icle.html"
    
    @staticmethod
    def get_license():
        return "The ICLE is available under the terms of a commercial license.</a>."

    @classmethod
    def get_file_list(cls, *args, **kwargs):
        """
        Make sure that source_info.csv file appears first in the file list.
        """
        l = super(BuilderClass, cls).get_file_list(*args, **kwargs)
        for x in list(l):
            if os.path.basename(x) in cls.special_files:
                l.remove(x)
                l.insert(0, x)
        return l

    @staticmethod
    def _filename_to_batch(filename):
        """
        This method should return a string that matches the 'batch' label.
        """
        #{"BGSU": "ICLE-BG-SUN",
         #"CNHK": "ICLE-CN-HKU",
         #"CNUK": "ICLE-CN-UK",
         #"CZKR": "ICLE-CZ-KRAL",
         #"DBAN": "ICLE-DB-KVH",
         #"CZKR": "ICLE-CZ-PRAG",
        
        #if filename.startswith("BGSU"):
            #id_str = 
        #elif filename.startswith("CNHK"):
            #id_str = 
        #elif filename.startswith("CNUK"):
            #id_str = "ICLE-CN-UK"
        #return "ICLE
        return filename

    def process_file(self, filename):
        base_name = os.path.basename(filename)
        print(base_name)
        if base_name == "source_info.csv":
            df = pd.read_csv(filename)
            for i in df.index:
                row = df.loc[i]
                if i == 1:
                    print(row)
                    print(row.dtypes)
                if row.schooleng == -1:
                    row.schooleng = None
                if row.unieng == -1:
                    row.unieng = None
                if row.monthseng == -1:
                    row.monthseng = None
                if row.age == -1:
                    row.age = None
                    
                self._sources[utf8(row.file)] = self.table(self.source_table).add(
                    {self.source_batch: self._filename_to_batch(row.file),
                    self.source_title: utf8(row.title),
                    self.source_type: row.type,
                    self.source_condition: row.conditions,
                    self.source_reftool: row.reftools,
                    self.source_exam: row.exam,
                    self.source_status: row.status,
                    self.source_institute: utf8(row.instit2),
                    self.source_comment: utf8(row.comments)})
                self._speakers[utf8(row.file)] = self.table(self.speaker_table).add(
                    {self.speaker_age: row.age,
                     self.speaker_sex: row.sex,
                     self.speaker_country: row.country,
                     self.speaker_language: row.llanguage,
                     self.speaker_schoolenglish: row.schooleng,
                     self.speaker_unienglish: row.unieng,
                     self.speaker_abroadenglish: row.monthseng,
                     self.speaker_otherlang1: row.olang1,
                     self.speaker_otherlang2: row.olang2,
                     self.speaker_otherlang3: row.olang3})
        elif base_name == "tokens.txt":
            hold_back = []
            with codecs.open(filename, "r", encoding="utf-16") as input_file:
                _ = input_file.read()
                for row in input_file:
                    #match = re.match("{(.+),(.+)\.(\w+)\+(.+)}", row)
                    match = re.match("{(.+),(.+)\.(.+)}", row)
                    if match:
                        label = match.group(1)
                        pos = match.group(3)
                        if "+" in pos:
                            pos, _, claws = pos.partition("+")
                        else:
                            claws = pos
                        d = {
                            self.word_label: label,
                            self.word_lemma: match.group(2),
                            self.word_pos: pos,
                            self.word_claws: claws}
                        if label not in self._words:
                            self._words[label] = self.table(self.word_table).add(d)
                    else:
                        hold_back.append(row.strip())

                for row in hold_back:
                    if row not in self._words:
                        if row in string.punctuation:
                            d = {
                                self.word_label: row,
                                self.word_lemma: row,
                                self.word_pos: "PUNCT",
                                self.word_claws: "PUNCT"}
                        else:
                            d = {self.word_label: row,
                                    self.word_lemma: row.lower(),
                                    self.word_pos: "UNKNOWN",
                                    self.word_claws: "UNKNOWN"}
                        self._words[row] = self.table(self.word_table).add(d)
                
        elif base_name in self.expected_files:
            self._source_id = self._sources[base_name.partition(".")[0]]
            self._speaker_id = self._speakers[base_name.partition(".")[0]]
            
            d = {self.corpus_file_id: self._file_id,
                self.corpus_source_id: self._source_id,
                self.corpus_speaker_id: self._speaker_id}
            
            with codecs.open(filename, "r") as input_file:
                batch = None
                for row in input_file:
                    if batch == None:
                        """
                        process batch name
                        """
                        batch = row
                    else:
                        words = row.split()
                        for word in [x.strip() for x in words]:
                            # handle any word-initial punctuation:
                            while word and word[0] in string.punctuation:
                                d[self.corpus_word_id] = self.table(self.word_table).get_or_insert(
                                    {self.word_label: word[0],
                                    self.word_lemma: word[0],
                                    self.word_pos: "PUNCT",
                                    self.word_claws: "PUNCT"}, case=True)

                                self.add_token_to_corpus(dict(d))
                                word = word[1:]
                            
                            # construct word, taking punctuation and escaped 
                            # punctuation into account:
                            l = []
                            escaped = True
                            for ch in word:
                                # add escaped characters to the word:
                                if escaped:
                                    l.append(ch)
                                    escaped = False
                                    continue
                                # take note of escaping:
                                if ch == "\\":
                                    escaped = True
                                    continue
                                # add any non-punctuation character to word:
                                if ch not in string.punctuation:
                                    l.append(ch)
                                    continue
                                # current character is a punctuation mark.
                                # store the current word:
                                if l:
                                    w = "".join(l)
                                    d[self.corpus_word_id] = self.table(self.word_table).get_or_insert(
                                        {self.word_label: w,
                                         self.word_lemma: w.lower(),
                                         self.word_pos: "UNKNOWN",
                                         self.word_claws: "UNKNOWN"}, case=True)
                                    self.add_token_to_corpus(dict(d))
                                    l = []
                                # add any following punctuation marks as 
                                # punctuation tokens:
                                d[self.corpus_word_id] = self.table(self.word_table).get_or_insert(
                                    {self.word_label: ch,
                                    self.word_lemma: ch,
                                    self.word_pos: "PUNCT",
                                    self.word_claws: "PUNCT"}, case=True)
                                self.add_token_to_corpus(dict(d))
                            # make sure that the current word is added:
                            if l:
                                w = "".join(l)
                                d[self.corpus_word_id] = self.table(self.word_table).get_or_insert(
                                    {self.word_label: w,
                                    self.word_lemma: w.lower(),
                                    self.word_pos: "UNKNOWN",
                                    self.word_claws: "UNKNOWN"}, case=True)
                                self.add_token_to_corpus(dict(d))
    
    def store_filename(self, file_name):
        if os.path.basename(file_name) not in self.special_files:
            super(BuilderClass, self).store_filename(file_name)
                    
if __name__ == "__main__":
    BuilderClass().build()

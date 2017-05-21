# -*- coding: utf-8 -*-

"""
coq_install_lob.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from unicodedata import lookup

from coquery.corpusbuilder import *
from coquery.unicode import utf8
from coquery.bibliography import *

REPLACE_TABLE = {
    }

SOURCE_CATEGORY = {
    "A": "PRESS: REPORTAGE",
    "B": "PRESS: EDITORIAL",
    "C": "PRESS: REVIEWS",
    "D": "RELIGION",
    "E": "SKILL AND HOBBIES",
    "F": "POPULAR LORE",
    "G": "BELLES-LETTRES",
    "H": "MISCELLANEOUS",
    "J": "LEARNED",
    "K": "FICTION: GENERAL",
    "L": "FICTION: MYSTERY",
    "M": "FICTION: SCIENCE",
    "N": "FICTION: ADVENTURE",
    "P": "FICTION: ROMANCE",
    "R": "HUMOR"}

SOURCE_TITLE = dict()

CATEGORY_NUMBERS = {"a": 44, "b": 27, "c": 17, "d": 17, "e": 38, "f": 44,
                    "g": 77, "h": 30, "j": 80, "k": 29, "l": 24, "m": 6,
                    "n": 29, "p": 29, "r": 9}

class BuilderClass(BaseCorpusBuilder):
    file_filter = "*.*"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_orth = "Word_orth"
    word_pos = "POS"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "SourceId"
    corpus_file_id = "FileId"

    source_table = "Sources"
    source_id = "SourceId"
    source_label = "Label"
    source_title = "Title"
    source_category = "Category"

    expected_files = ["lobth_{}.txt".format(x) for x in CATEGORY_NUMBERS.keys()]


    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "MEDIUMINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(33) NOT NULL"),
             Column(self.word_label, "VARCHAR(33) NOT NULL"),
             Column(self.word_pos, "VARCHAR(20) NOT NULL")])

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "ENUM({}) NOT NULL".format(
                 ",".join(["'{}'".format(x) for x in expected_files]))),
             Column(self.file_path, "TINYTEXT NOT NULL")])

        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "SMALLINT(3) UNSIGNED NOT NULL"),
             Column(self.source_label, "ENUM('A01','A02','A03','A04','A05','A06','A07','A08','A09','A10','A11','A12','A13','A14','A15','A16','A17','A18','A19','A20','A21','A22','A23','A24','A25','A26','A27','A28','A29','A30','A31','A32','A33','A34','A35','A36','A37','A38','A39','A40','A41','A42','A43','A44','B01','B02','B03','B04','B05','B06','B07','B08','B09','B10','B11','B12','B13','B14','B15','B16','B17','B18','B19','B20','B21','B22','B23','B24','B25','B26','B27','C01','C02','C03','C04','C05','C06','C07','C08','C09','C10','C11','C12','C13','C14','C15','C16','C17','D01','D02','D03','D04','D05','D06','D07','D08','D09','D10','D11','D12','D13','D14','D15','D16','D17','E01','E02','E03','E04','E05','E06','E07','E08','E09','E10','E11','E12','E13','E14','E15','E16','E17','E18','E19','E20','E21','E22','E23','E24','E25','E26','E27','E28','E29','E30','E31','E32','E33','E34','E35','E36','F01','F02','F03','F04','F05','F06','F07','F08','F09','F10','F11','F12','F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24','F25','F26','F27','F28','F29','F30','F31','F32','F33','F34','F35','F36','F37','F38','F39','F40','F41','F42','F43','F44','F45','F46','F47','F48','G01','G02','G03','G04','G05','G06','G07','G08','G09','G10','G11','G12','G13','G14','G15','G16','G17','G18','G19','G20','G21','G22','G23','G24','G25','G26','G27','G28','G29','G30','G31','G32','G33','G34','G35','G36','G37','G38','G39','G40','G41','G42','G43','G44','G45','G46','G47','G48','G49','G50','G51','G52','G53','G54','G55','G56','G57','G58','G59','G60','G61','G62','G63','G64','G65','G66','G67','G68','G69','G70','G71','G72','G73','G74','G75','H01','H02','H03','H04','H05','H06','H07','H08','H09','H10','H11','H12','H13','H14','H15','H16','H17','H18','H19','H20','H21','H22','H23','H24','H25','H26','H27','H28','H29','H30','J01','J02','J03','J04','J05','J06','J07','J08','J09','J10','J11','J12','J13','J14','J15','J16','J17','J18','J19','J20','J21','J22','J23','J24','J25','J26','J27','J28','J29','J30','J31','J32','J33','J34','J35','J36','J37','J38','J39','J40','J41','J42','J43','J44','J45','J46','J47','J48','J49','J50','J51','J52','J53','J54','J55','J56','J57','J58','J59','J60','J61','J62','J63','J64','J65','J66','J67','J68','J69','J70','J71','J72','J73','J74','J75','J76','J77','J78','J79','J80','K01','K02','K03','K04','K05','K06','K07','K08','K09','K10','K11','K12','K13','K14','K15','K16','K17','K18','K19','K20','K21','K22','K23','K24','K25','K26','K27','K28','K29','L01','L02','L03','L04','L05','L06','L07','L08','L09','L10','L11','L12','L13','L14','L15','L16','L17','L18','L19','L20','L21','L22','L23','L24','M01','M02','M03','M04','M05','M06','N01','N02','N03','N04','N05','N06','N07','N08','N09','N10','N11','N12','N13','N14','N15','N16','N17','N18','N19','N20','N21','N22','N23','N24','N25','N26','N27','N28','N29','P01','P02','P03','P04','P05','P06','P07','P08','P09','P10','P11','P12','P13','P14','P15','P16','P17','P18','P19','P20','P21','P22','P23','P24','P25','P26','P27','P28','P29','R01','R02','R03','R04','R05','R06','R07','R08','R09') NOT NULL"),
             Column(self.source_title, "VARCHAR(100) NOT NULL"),
             Column(self.source_category, "ENUM('BELLES-LETTRES','FICTION: ADVENTURE','FICTION: GENERAL','FICTION: MYSTERY','FICTION: ROMANCE','FICTION: SCIENCE','HUMOR','LEARNED','MISCELLANEOUS: GOVERNMENT & HOUSE ORGANS','POPULAR LORE','PRESS: EDITORIAL','PRESS: REPORTAGE','PRESS: REVIEWS','RELIGION','SKILL AND HOBBIES') NOT NULL")])

        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_source_id, self.source_table)])

    @staticmethod
    def get_name():
        return "LOB"

    @staticmethod
    def get_db_name():
        return "coq_lob"

    @staticmethod
    def get_title():
        return "The Lancaster-Oslo/Bergen Corpus of British English"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en-UK"

    @staticmethod
    def get_description():
        return ["The Lancaster-Oslo/Bergen Corpus (often abbreviated as LOB Corpus) is a million-word collection of British English texts which was compiled in the 1970s in collaboration between the University of Lancaster, the University of Oslo, and the Norwegian Computing Centre for the Humanities, Bergen, to provide a British counterpart to the Brown Corpus compiled by Henry Kučera and W. Nelson Francis for American English in the 1960s.",
            "Its composition was designed to match the original Brown corpus in terms of its size and genres as closely as possible using documents published in the UK by British authors. Both corpora consist of 500 samples each comprising about 2000 words in 15 different genres. (Source: Wikipedia, <a href='https://en.wikipedia.org/wiki/Lancaster-Oslo-Bergen_Corpus'>Lancaster-Oslo-Bergen Corpus</a>)"]

    @classmethod
    def get_file_list(cls, *args, **kwargs):
        """
        Make sure that the CONTENTS file appears first in the file list.
        """
        l = super(BuilderClass, cls).get_file_list(*args, **kwargs)
        for x in list(l):
            if os.path.basename(x) == "CONTENTS":
                l.remove(x)
                l.insert(0, x)
                break
        return l

    def process_file(self, filename):
        base_name = os.path.basename(filename)
        if base_name == "CONTENTS":
            for line in open(filename, "r").readlines():
                match = re.match("([A-R]\d\d)\.\s+(.*)", line.strip())
                if match:
                    SOURCE_TITLE["c{}".format(match.group(1).lower())] = match.group(2).strip()

        elif base_name in self.expected_files:
            d = {self.source_label: base_name[1:].upper(),
                self.source_title: SOURCE_TITLE[base_name],
                self.source_category: SOURCE_CATEGORY[base_name[1].upper()]}
            self._source_id = self.table(self.source_table).add(d)

            with open(filename, "r") as input_file:
                in_headline = False
                in_title = False
                in_italics = False
                in_foreign = False
                for content in input_file:
                    if self._interrupted:
                        return
                    if content.strip():
                        self.tag_token(self._corpus_id + 1, "p", {}, op=True)
                        for token in content.strip().split():
                            word, _, pos = token.partition("/")

                            if not in_foreign:
                                if pos.startswith("fw-"):
                                    in_foreign = True
                                    self.tag_token(self._corpus_id + 1, "span", {"style": "color='#aa0000'"}, op=True)
                                    _, _, pos = pos.partition("-")
                            else:
                                if not pos.startswith("fw-"):
                                    in_foreign = False
                                    self.tag_token(self._corpus_id, "span", {}, cl=True)
                                    _, _, pos = pos.partition("-")

                            if not in_headline:
                                if pos.endswith("-hl"):
                                    in_headline = True
                                    self.tag_token(self._corpus_id + 1, "head", {}, op=True)
                                    pos, _, _ = pos.rpartition("-")
                            else:
                                if not pos.endswith("-hl"):
                                    in_headline = False
                                    self.tag_token(self._corpus_id, "head", {}, cl=True)
                                    pos, _, _ = pos.rpartition("-")

                            if not in_italics:
                                if pos.endswith("-nc"):
                                    in_italics = True
                                    self.tag_token(self._corpus_id + 1, "hi", {"rend": "it"}, op=True)
                                    pos, _, _ = pos.rpartition("-")
                            else:
                                if not pos.endswith("-nc"):
                                    in_italics = False
                                    self.tag_token(self._corpus_id, "hi", {}, cl=True)
                                    pos, _, _ = pos.rpartition("-")

                            if not in_title:
                                if pos.endswith("-tl"):
                                    in_title = True
                                    self.tag_token(self._corpus_id + 1, "b", {}, op=True)
                                    pos, _, _ = pos.rpartition("-")
                            else:
                                if not pos.endswith("-tl"):
                                    in_title = False
                                    self.tag_token(self._corpus_id, "b", {}, cl=True)
                                    pos, _, _ = pos.rpartition("-")

                            self._word_id = self.table(self.word_table).get_or_insert(
                                {self.word_label: word, self.word_pos: pos})
                            self.add_token_to_corpus(
                                {self.corpus_word_id: self._word_id,
                                self.corpus_file_id: self._file_id,
                                self.corpus_source_id: self._source_id})

                        self.tag_token(self._corpus_id, "p", {}, cl=True)


if __name__ == "__main__":
    BuilderClass().build()

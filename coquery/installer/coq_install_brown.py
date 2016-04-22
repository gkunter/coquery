# -*- coding: utf-8 -*-

"""
coq_install_brown.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

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
    "**ya": lookup("GREEK SMALL LETTER ALPHA"),
    "**yb": lookup("GREEK SMALL LETTER BETA"),
    "**yc": lookup("GREEK SMALL LETTER CHI"),
    "**yd": lookup("GREEK SMALL LETTER DELTA"),
    "**ye": lookup("GREEK SMALL LETTER EPSILON"),
    "**yf": lookup("GREEK SMALL LETTER PHI"),
    "**yg": lookup("GREEK SMALL LETTER GAMMA"),
    "**yh": lookup("GREEK SMALL LETTER ETA"),
    "**yi": lookup("GREEK SMALL LETTER IOTA"),
    "**yj": lookup("GREEK SMALL LETTER THETA"),
    "**yk": lookup("GREEK SMALL LETTER KAPPA"),
    "**yl": lookup("GREEK SMALL LETTER LAMDA"),
    "**ym": lookup("GREEK SMALL LETTER MU"),
    "**yn": lookup("GREEK SMALL LETTER NU"),
    "**yo": lookup("GREEK SMALL LETTER OMICRON"),
    "**yp": lookup("GREEK SMALL LETTER PI"),
    "**yq": lookup("GREEK SMALL LETTER OMEGA"),
    "**yr": lookup("GREEK SMALL LETTER RHO"),
    "**ys": lookup("GREEK SMALL LETTER SIGMA"),
    "**yt": lookup("GREEK SMALL LETTER TAU"),
    "**yu": lookup("GREEK SMALL LETTER UPSILON"),
    "**yx": lookup("GREEK SMALL LETTER XI"),
    "**yy": lookup("GREEK SMALL LETTER PSI"),
    "**yz": lookup("GREEK SMALL LETTER ZETA"),
    
    "**za": lookup("GREEK CAPITAL LETTER ALPHA"),
    "**zb": lookup("GREEK CAPITAL LETTER BETA"),
    "**zc": lookup("GREEK CAPITAL LETTER CHI"),
    "**zd": lookup("GREEK CAPITAL LETTER DELTA"),
    "**ze": lookup("GREEK CAPITAL LETTER EPSILON"),
    "**zf": lookup("GREEK CAPITAL LETTER PHI"),
    "**zg": lookup("GREEK CAPITAL LETTER GAMMA"),
    "**zh": lookup("GREEK CAPITAL LETTER ETA"),
    "**zi": lookup("GREEK CAPITAL LETTER IOTA"),
    "**zj": lookup("GREEK CAPITAL LETTER THETA"),
    "**zk": lookup("GREEK CAPITAL LETTER KAPPA"),
    "**zl": lookup("GREEK CAPITAL LETTER LAMDA"),
    "**zm": lookup("GREEK CAPITAL LETTER MU"),
    "**zn": lookup("GREEK CAPITAL LETTER NU"),
    "**zo": lookup("GREEK CAPITAL LETTER OMICRON"),
    "**zp": lookup("GREEK CAPITAL LETTER PI"),
    "**zq": lookup("GREEK CAPITAL LETTER OMEGA"),
    "**zr": lookup("GREEK CAPITAL LETTER RHO"),
    "**zs": lookup("GREEK CAPITAL LETTER SIGMA"),
    "**zt": lookup("GREEK CAPITAL LETTER TAU"),
    "**zu": lookup("GREEK CAPITAL LETTER UPSILON"),
    "**zx": lookup("GREEK CAPITAL LETTER XI"),
    "**zy": lookup("GREEK CAPITAL LETTER PSI"),
    "**zz": lookup("GREEK CAPITAL LETTER ZETA"), 
    
    "**b": lookup("REPLACEMENT CHARACTER")
    }

SOURCE_CATEGORY = {
    "A": "PRESS: REPORTAGE", 
    "B": "PRESS: EDITORIAL", 
    "C": "PRESS: REVIEWS", 
    "D": "RELIGION", 
    "E": "SKILL AND HOBBIES", 
    "F": "POPULAR LORE", 
    "G": "BELLES-LETTRES", 
    "H": "MISCELLANEOUS: GOVERNMENT & HOUSE ORGANS", 
    "J": "LEARNED", 
    "K": "FICTION: GENERAL", 
    "L": "FICTION: MYSTERY", 
    "M": "FICTION: SCIENCE", 
    "N": "FICTION: ADVENTURE", 
    "P": "FICTION: ROMANCE", 
    "R": "HUMOR"}

SOURCE_TITLE = dict()

CATEGORY_NUMBERS = {"a": 44, "b": 27, "c": 17, "d": 17, "e": 36, "f": 48, 
                    "g": 75, "h": 30, "j": 80, "k": 29, "l": 24, "m": 6,
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

    expected_files = ["brown.zip"]
    special_files = ["CONTENTS"]
    expected_files = special_files + []
    
    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        for _ch in CATEGORY_NUMBERS:
            _format_str = "c{}{{:02}}".format(_ch)
            self.expected_files += [_format_str.format(i+1) for i in range(CATEGORY_NUMBERS[_ch])]

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "MEDIUMINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(33) NOT NULL"),
             Column(self.word_pos, "VARCHAR(20) NOT NULL")])

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "ENUM('ca01','ca02','ca03','ca04','ca05','ca06','ca07','ca08','ca09','ca10','ca11','ca12','ca13','ca14','ca15','ca16','ca17','ca18','ca19','ca20','ca21','ca22','ca23','ca24','ca25','ca26','ca27','ca28','ca29','ca30','ca31','ca32','ca33','ca34','ca35','ca36','ca37','ca38','ca39','ca40','ca41','ca42','ca43','ca44','cb01','cb02','cb03','cb04','cb05','cb06','cb07','cb08','cb09','cb10','cb11','cb12','cb13','cb14','cb15','cb16','cb17','cb18','cb19','cb20','cb21','cb22','cb23','cb24','cb25','cb26','cb27','cc01','cc02','cc03','cc04','cc05','cc06','cc07','cc08','cc09','cc10','cc11','cc12','cc13','cc14','cc15','cc16','cc17','cd01','cd02','cd03','cd04','cd05','cd06','cd07','cd08','cd09','cd10','cd11','cd12','cd13','cd14','cd15','cd16','cd17','ce01','ce02','ce03','ce04','ce05','ce06','ce07','ce08','ce09','ce10','ce11','ce12','ce13','ce14','ce15','ce16','ce17','ce18','ce19','ce20','ce21','ce22','ce23','ce24','ce25','ce26','ce27','ce28','ce29','ce30','ce31','ce32','ce33','ce34','ce35','ce36','cf01','cf02','cf03','cf04','cf05','cf06','cf07','cf08','cf09','cf10','cf11','cf12','cf13','cf14','cf15','cf16','cf17','cf18','cf19','cf20','cf21','cf22','cf23','cf24','cf25','cf26','cf27','cf28','cf29','cf30','cf31','cf32','cf33','cf34','cf35','cf36','cf37','cf38','cf39','cf40','cf41','cf42','cf43','cf44','cf45','cf46','cf47','cf48','cg01','cg02','cg03','cg04','cg05','cg06','cg07','cg08','cg09','cg10','cg11','cg12','cg13','cg14','cg15','cg16','cg17','cg18','cg19','cg20','cg21','cg22','cg23','cg24','cg25','cg26','cg27','cg28','cg29','cg30','cg31','cg32','cg33','cg34','cg35','cg36','cg37','cg38','cg39','cg40','cg41','cg42','cg43','cg44','cg45','cg46','cg47','cg48','cg49','cg50','cg51','cg52','cg53','cg54','cg55','cg56','cg57','cg58','cg59','cg60','cg61','cg62','cg63','cg64','cg65','cg66','cg67','cg68','cg69','cg70','cg71','cg72','cg73','cg74','cg75','ch01','ch02','ch03','ch04','ch05','ch06','ch07','ch08','ch09','ch10','ch11','ch12','ch13','ch14','ch15','ch16','ch17','ch18','ch19','ch20','ch21','ch22','ch23','ch24','ch25','ch26','ch27','ch28','ch29','ch30','cj01','cj02','cj03','cj04','cj05','cj06','cj07','cj08','cj09','cj10','cj11','cj12','cj13','cj14','cj15','cj16','cj17','cj18','cj19','cj20','cj21','cj22','cj23','cj24','cj25','cj26','cj27','cj28','cj29','cj30','cj31','cj32','cj33','cj34','cj35','cj36','cj37','cj38','cj39','cj40','cj41','cj42','cj43','cj44','cj45','cj46','cj47','cj48','cj49','cj50','cj51','cj52','cj53','cj54','cj55','cj56','cj57','cj58','cj59','cj60','cj61','cj62','cj63','cj64','cj65','cj66','cj67','cj68','cj69','cj70','cj71','cj72','cj73','cj74','cj75','cj76','cj77','cj78','cj79','cj80','ck01','ck02','ck03','ck04','ck05','ck06','ck07','ck08','ck09','ck10','ck11','ck12','ck13','ck14','ck15','ck16','ck17','ck18','ck19','ck20','ck21','ck22','ck23','ck24','ck25','ck26','ck27','ck28','ck29','cl01','cl02','cl03','cl04','cl05','cl06','cl07','cl08','cl09','cl10','cl11','cl12','cl13','cl14','cl15','cl16','cl17','cl18','cl19','cl20','cl21','cl22','cl23','cl24','cm01','cm02','cm03','cm04','cm05','cm06','cn01','cn02','cn03','cn04','cn05','cn06','cn07','cn08','cn09','cn10','cn11','cn12','cn13','cn14','cn15','cn16','cn17','cn18','cn19','cn20','cn21','cn22','cn23','cn24','cn25','cn26','cn27','cn28','cn29','CONT','cp01','cp02','cp03','cp04','cp05','cp06','cp07','cp08','cp09','cp10','cp11','cp12','cp13','cp14','cp15','cp16','cp17','cp18','cp19','cp20','cp21','cp22','cp23','cp24','cp25','cp26','cp27','cp28','cp29','cr01','cr02','cr03','cr04','cr05','cr06','cr07','cr08','cr09') NOT NULL"),
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
        return "BROWN"

    @staticmethod
    def get_db_name():
        return "coq_brown"
    
    @staticmethod
    def get_title():
        return "The Brown University Standard Corpus of Present-Day English"
        
    @staticmethod
    def get_language():
        return "English"
    
    @staticmethod
    def get_language_code():
        return "en-US"
        
    @staticmethod
    def get_description():
        return [
            "The Brown University Standard Corpus of Present-Day American English (or just Brown Corpus) was compiled in the 1960s by Henry Kučera and W. Nelson Francis at Brown University, Providence, Rhode Island as a general corpus (text collection) in the field of corpus linguistics. It contains 500 samples of English-language text, totaling roughly one million words, compiled from works published in the United States in 1961. (Source: Wikipedia, <a href='https://en.wikipedia.org/wiki/Brown_Corpus'>Brown Corpus</a>)"]

    @staticmethod
    def get_references():
        return [Book(
            authors=PersonList(
                Person(first="Henry", last="Kučera"), 
                Person(first="Nelson", middle="W.", last="Francis")),
            year=1979,
            title="A standard corpus of present-day edited American English, for use with digital computers",
            publisher="Brown University Press",
            address="Providendce, RI")]

    @staticmethod
    def get_url():
        return "https://http://clu.uni.no/icame/manuals/BROWN/INDEX.HTM"
    
    @staticmethod
    def get_installation_note():
        return "<p>This installer expects the files from the ZIP file <code>brown.zip</code>. This file has been released on <a href='https://archive.org/'>https://archive.org</a> under a Creative Commons license. Please download the ZIP file from <a href='https://archive.org/download/BrownCorpus/brown.zip'>https://archive.org/download/BrownCorpus/brown.zip</a>, and extract the content to a directory.</p><p>Other releases such as the version distributed as part of the <a href='http://clu.uni.no/icame/newcd.htm'>ICAME Corpus Collection on CD-ROM</a>, use a different structure for the file directories, and cannot be used with this installer.</p>"

    @staticmethod
    def get_license():
        return "The Brown corpus is available under the terms of the <a href='http://creativecommons.org/licenses/by-nc/3.0/'>Creative Commons Attribution-Noncommercial 3.0 License</a>."

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

# -*- coding: utf-8 -*-

"""
coq_install_celex_de.py is part of Coquery.

Copyright (c) 2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals
from __future__ import print_function

from coquery.tables import (Column, Link, Identifier,
                            varchar, smallint, mediumint, enum)
from coquery.defines import (
    QUERY_ITEM_POS, QUERY_ITEM_TRANSCRIPT, QUERY_ITEM_WORD, VIEW_MODE_TABLES)

from coquery.installer.coq_install_celex import CELEXBuilderClass
from coquery.installer.coq_install_celex import dia_to_unicode, _tr


class BuilderClass(CELEXBuilderClass):
    default_view_mode = VIEW_MODE_TABLES
    file_filter = "g??.cd"

    _ORTH_WORDS = "gow"
    _ORTH_LEMMAS = "gol"
    _MORPH_WORDS = "gmw"

    lemma_table = "Ortho_Lemma"
    lemma_id = "ID"
    lemma_label = "Head"
    lemma_mann = "LemmaMann"
    lemma_headsyldia = "HeadSylDia"
    lemma_headsylchg = "HeadSylChg"
    lemma_stem = "Stem"
    lemma_stemsyldia = "StemSylDia"
    lemma_stemsylchg = "StemSylChg"

    lemma_columns = [
        Identifier(lemma_id, mediumint(5)),
        Column(lemma_label, varchar(31)),
        Column(lemma_mann, mediumint(5)),
        Column(lemma_headsyldia, varchar(40)),
        Column(lemma_headsylchg, enum("N", "Y")),
        Column(lemma_stem, varchar(31)),
        Column(lemma_stemsyldia, varchar(40)),
        Column(lemma_stemsylchg, enum("N", "Y"))]

    flecttype_table = "FlectType"
    flecttype_id = "ID"
    flecttype_label = "FlectType"
    flecttype_number = "Number"
    flecttype_case = "Case"
    flecttype_degree = "Degree"
    flecttype_separate = "SeparateWF"
    flecttype_nonfinite = "NonfiniteWF"
    flecttype_tense = "Tense"
    flecttype_person = "Person"
    flecttype_mood = "Mood"
    flecttype_adjsuffix = "AdjSuffix"
    flecttype_gender = "Gender"
    flecttype_columns = [
        Identifier(flecttype_id, smallint(3)),
        Column(flecttype_label, varchar(23)),
        Column(flecttype_number, enum("Sg", "Pl", "")),
        Column(flecttype_case, enum("Nom", "Gen", "Dat", "Acc", "")),
        Column(flecttype_degree, enum("Pos", "Comp", "Sup", "")),
        Column(flecttype_separate, enum("N", "Y")),
        Column(flecttype_nonfinite, enum("Inf", "ZuInf", "Part", "")),
        Column(flecttype_tense, enum("Pres", "Past", "")),
        Column(flecttype_person, enum("1", "2", "3", "")),
        Column(flecttype_mood, enum("Ind", "Sub", "Imp", "")),
        Column(flecttype_adjsuffix,
               enum("e", "en", "er", "em", "es", "s", "")),
        Column(flecttype_gender, enum("m", "w", "n", ""))]

    morphword_table = "Morph_Word"
    morphword_id = "ID"
    morphword_flecttype_id = "FlectTypeId"
    morphword_columns = [
        Identifier(morphword_id, mediumint(6)),
        Link(morphword_flecttype_id, flecttype_table)]

    corpus_table = "Ortho_Words"
    corpus_id = "ID"
    corpus_morphword_id = "ID"
    corpus_lemma_id = "LemmaId"
    corpus_word = "Word"
    corpus_mann = "WordMann"
    corpus_wordsyldia = "WordSyl"
    corpus_wordsylchg = "WordSylChg"
    corpus_columns = [
        Identifier(corpus_id, mediumint(6)),
        Link(corpus_lemma_id, lemma_table),
        Link(corpus_morphword_id, morphword_table, create=False),
        Column(corpus_word, varchar(33)),
        Column(corpus_mann, mediumint(6)),
        Column(corpus_wordsyldia, varchar(43)),
        Column(corpus_wordsylchg, enum("N", "Y"))]

    auto_create = ["lemma", "flecttype", "morphword", "corpus"]
    expected_files = ["gow.cd", "gmw.cd", "gol.cd"]

    _flect_dict = {}

    @classmethod
    def component_to_label(cls, component):
        _MAP = {cls._ORTH_WORDS: _tr("Orthography word forms"),
                cls._ORTH_LEMMAS: _tr("Orthography lemmas"),
                cls._MORPH_WORDS: _tr("Morphology word forms")}

        return _MAP.get(component, None)

    def set_fnc_map(self):
        self._FNC_MAP = {self._ORTH_WORDS: self.process_orth_word,
                         self._ORTH_LEMMAS: self.process_orth_lemma,
                         self._MORPH_WORDS: self.process_morph_word}

    def process_orth_word(self, columns):
        (wid, worddia, mann, lemma_id, wordsyldia, wordsylchg) = columns

        self.table(self.corpus_table).add(
            {self.corpus_id: wid,
             self.corpus_lemma_id: lemma_id,
             self.corpus_word: dia_to_unicode(worddia),
             self.corpus_mann: mann,
             self.corpus_wordsyldia: wordsyldia,
             self.corpus_wordsylchg: wordsylchg})

    def process_orth_lemma(self, columns):
        (lid, head, mann, headsyldia, headsylchg,
         stem, stemsyldia, stemsylchg) = columns

        self.table(self.lemma_table).add(
            {self.lemma_id: lid,
             self.lemma_label: dia_to_unicode(head),
             self.lemma_mann: mann,
             self.lemma_headsyldia: headsyldia,
             self.lemma_headsylchg: headsylchg,
             self.lemma_stem: stem,
             self.lemma_stemsyldia: stemsyldia,
             self.lemma_stemsylchg: stemsylchg})

    def process_morph_word(self, columns):
        wid, _, _, _, flecttypes = columns

        ft_table = self.table(self.flecttype_table)
        mw_table = self.table(self.morphword_table)

        for flecttype in flecttypes.split(","):
            if flecttype not in self._flect_dict:
                number = ("Sg" if "S" in flecttype else
                          "Pl" if "P" in flecttype else
                          None)
                case = ("Nom" if "n" in flecttype else
                        "Gen" if "g" in flecttype else
                        "Dat" if "d" in flecttype else
                        "Acc" if "a" in flecttype else
                        None)
                degree = ("Pos" if "o" in flecttype else
                          "Comp" if "c" in flecttype else
                          "Sup" if "u" in flecttype else
                          None)
                separate = "Y" if "/" in flecttype else "N"
                nonfinite = ("Inf" if "i" in flecttype else
                             "ZuInf" if "z" in flecttype else
                             "Part" if "p" in flecttype else
                             None)
                tense = ("Pres" if "E" in flecttype else
                         "Past" if "A" in flecttype else
                         None)
                person = ("1" if "1" in flecttype else
                          "2" if "2" in flecttype else
                          "3" if "3" in flecttype else
                          None)
                mood = ("Ind" if "I" in flecttype else
                        "Sub" if "K" in flecttype else
                        "Imp" if "r" in flecttype else
                        None)
                adjsuffix = ("e" if "4" in flecttype else
                             "en" if "5" in flecttype else
                             "er" if "6" in flecttype else
                             "em" if "7" in flecttype else
                             "es" if "8" in flecttype else
                             "s" if "9" in flecttype
                             else None)
                gender = ("m" if "m" in flecttype else
                          "w" if "w" in flecttype else
                          "n" if "s" in flecttype else
                          None)

                d = {self.flecttype_id: wid,
                     self.flecttype_label: flecttype,
                     self.flecttype_number: number,
                     self.flecttype_case: case,
                     self.flecttype_degree: degree,
                     self.flecttype_separate: separate,
                     self.flecttype_nonfinite: nonfinite,
                     self.flecttype_tense: tense,
                     self.flecttype_person: person,
                     self.flecttype_mood: mood,
                     self.flecttype_adjsuffix: adjsuffix,
                     self.flecttype_gender: gender}
                flecttype_id = ft_table.get_or_insert(d)
                self._flect_dict[flecttype] = flecttype_id
            else:
                flecttype_id = self._flect_dict[flecttype]

            mw_table.add(
                {self.morphword_id: wid,
                 self.morphword_flecttype_id: flecttype_id})

    def map_query_items(self):
        self.map_query_item(QUERY_ITEM_WORD, "corpus_word")

    @staticmethod
    def get_title():
        return "CELEX2 Lexical Database (German)"

    @staticmethod
    def get_url():
        return 'https://catalog.ldc.upenn.edu/LDC96L14'

    @staticmethod
    def get_name():
        return "CELEX2 (DE)"

    @staticmethod
    def get_db_name():
        return "coq_celexde"

    @staticmethod
    def get_language():
        return "German"

    @staticmethod
    def get_language_code():
        return "de"


if __name__ == "__main__":
    BuilderClass().build()

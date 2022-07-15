# -*- coding: utf-8 -*-

"""
coq_install_gabra.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import os
import bson

from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.tables import Column, Identifier, Link
from coquery.bibliography import Reference, PersonList, Person
from coquery.defines import VIEW_MODE_TABLES


def yn(s) -> str:
    """
    Return 'Y' if int(s) is True, or 'N' otherwise. Return an empty
    string if s is None.
    """
    if s:
        if int(s):
            return "Y"
        else:
            return "N"
    return ""


class BuilderClass(BaseCorpusBuilder):
    default_view_mode = VIEW_MODE_TABLES
    file_filter = "*.bson"
    expected_files = [
        "roots.bson", "lexemes.bson", "sources.bson", "wordforms.bson"]

    root_table = "Roots"
    root_id = "RootId"
    root_radicals = "Radicals"
    root_type = "Type"
    root_variant = "Variant"
    root_alternatives = "Alternatives"
    _root_dict = {}

    join_type = "LEFT"

    lemma_table = "Lexemes"

    lemma_id = "LemmaId"
    lemma_label = "Lemma"
    lemma_adjectival = "Adjectival"
    lemma_adverbial = "Adverbial"
    lemma_alternatives = "Alternatives"
    lemma_apertiumparadigm = "Apertium_paradigm"
    lemma_archaic = "Archaic"
    lemma_created = "Created"
    lemma_derived_form = "Derived_form"
    lemma_ditransitive = "Ditransitive"
    lemma_features = "Features"
    lemma_feedback = "Feedback"
    lemma_form = "Form"
    lemma_frequency = "Frequency"
    lemma_norm_freq = "NormFreq"
    lemma_gender = "Gender"
    lemma_gloss = "Gloss"
    lemma_headword = "Headword"
    lemma_hypothetical = "Hypothetical"
    lemma_intransitive = "Intransitive"
    lemma_modified = "Modified"
    lemma_notduplicate = "Not_duplicate"
    lemma_number = "Number"
    lemma_onomastictype = "Onomastic_type"
    lemma_participle = "Participle"
    lemma_pending = "Pending"
    lemma_pos = "POS"
    lemma_root_id = "RootId"
    lemma_transcript = "Phonetic"
    lemma_verbalnoun = "Verbal_noun"

    source_id = "SourceId"
    source_key = "Identifier"
    source_table = "Sources"
    source_label = "Title"
    source_year = "Year"
    source_author = "Author"
    source_note = "Note"

    corpus_table = "Wordforms"
    corpus_id = "ID"
    corpus_word = "Surface_form"

    corpus_adverbial = "Adverbial"
    corpus_alternatives = "Alternatives"
    corpus_archaic = "Archaic"
    corpus_aspect = "Aspect"
    corpus_created = "Created"
    corpus_dir_obj = "Dir_obj"
    corpus_form = "Form"
    corpus_full = "Full"
    corpus_gender = "Gender"
    corpus_generated = "Generated"
    corpus_gloss = "Gloss"
    corpus_hypothetical = "Hypothetical"
    corpus_ind_obj = "Ind_obj"
    corpus_lemma_id = "LemmaId"
    corpus_modified = "Modified"
    corpus_number = "Number"
    corpus_pattern = "Pattern"
    corpus_transcript = "Phonetic"
    corpus_plural_form = "Plural_form"
    corpus_polarity = "Polarity"
    corpus_possessor = "Possessor"
    corpus_source_id = "Source"
    corpus_subject = "Subject"

    @staticmethod
    def get_modules():
        return [("bson",
                 "PyMongo",
                 "http://api.mongodb.org/python/current/index.html")]

    @staticmethod
    def get_name():
        return "Ġabra"

    @staticmethod
    def get_db_name():
        return "gabra"

    @staticmethod
    def get_title():
        return "Ġabra: an open lexicon for Maltese"

    @staticmethod
    def get_language():
        return "Maltese"

    @staticmethod
    def get_language_code():
        return "mt"

    @staticmethod
    def get_description():
        return [
            "Ġabra is a free, open lexicon for Maltese, built by collecting "
            "various different lexical resources into one common database. "
            "While it is not yet a complete dictionary for Maltese, it "
            "already contains 16,291 entries and 4,520,596 inflectional word "
            "forms. Many of these are linked by root, include translations "
            "in English, and are marked for various morphological features."]

    @staticmethod
    def get_references():
        return [Reference(
            authors=PersonList(Person(
                first="John", middle="J.", last="Camilleri")),
            title="A Computational Grammar and Lexicon for Maltese",
            other=("M.Sc. Thesis. Chalmers University of Technology. "
                   "Gothenburg, Sweden, September 2013."))]

    @staticmethod
    def get_url():
        return "http://mlrs.research.um.edu.mt/resources/gabra/"

    @staticmethod
    def get_license():
        return (
            'Ġabra is available under the terms of the <a href="http://'
            'creativecommons.org/licenses/by/4.0/">Creative Commons '
            'Attribution 4.0 International License</a>.')

    def __init__(self, gui=False, *args):
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(
            self.root_table,
            [Identifier(self.root_id, "INT(6) UNSIGNED"),
             Column(self.root_radicals, "VARCHAR(128)"),
             Column(self.root_type, "VARCHAR(128)"),
             Column(self.root_alternatives, "VARCHAR(128)"),
             Column(self.root_variant, "TINYINT")])

        self.create_table_description(
            self.source_table,
            [Identifier(self.source_id, "TINYINT"),
             Column(self.source_key, "VARCHAR(1024)"),
             Column(self.source_label, "VARCHAR(1024)"),
             Column(self.source_year, "INT"),
             Column(self.source_author, "VARCHAR(1024)"),
             Column(self.source_note, "VARCHAR(1024)")])

        lst = [Identifier(self.lemma_id, "SMALLINT(5) UNSIGNED"),
               Column(self.lemma_label, "VARCHAR(512)"),
               Column(self.lemma_adjectival, "VARCHAR(1)"),
               Column(self.lemma_adverbial, "VARCHAR(1)"),
               Column(self.lemma_alternatives, "VARCHAR(128)"),
               Column(self.lemma_apertiumparadigm, "VARCHAR(128)"),
               Column(self.lemma_archaic, "VARCHAR(1)"),
               Column(self.lemma_created, "VARCHAR(128)"),
               Column(self.lemma_derived_form, "TINYINT"),
               Column(self.lemma_ditransitive, "VARCHAR(1)"),
               Column(self.lemma_features, "VARCHAR(128)"),
               Column(self.lemma_feedback, "VARCHAR(128)"),
               Column(self.lemma_form, "VARCHAR(128)"),
               Column(self.lemma_frequency, "VARCHAR(128)"),
               Column(self.lemma_norm_freq, "REAL"),
               Column(self.lemma_gender, "VARCHAR(1)"),
               Column(self.lemma_gloss, "VARCHAR(1024)"),
               Column(self.lemma_headword, "VARCHAR(128)"),
               Column(self.lemma_hypothetical, "VARCHAR(1)"),
               Column(self.lemma_intransitive, "VARCHAR(1)"),
               Column(self.lemma_modified, "VARCHAR(128)"),
               Column(self.lemma_notduplicate, "VARCHAR(1)"),
               Column(self.lemma_number, "VARCHAR(128)"),
               Column(self.lemma_onomastictype, "VARCHAR(128)"),
               Column(self.lemma_participle, "VARCHAR(1)"),
               Column(self.lemma_pending, "VARCHAR(1)"),
               Column(self.lemma_pos, "VARCHAR(8)"),
               Link(self.lemma_root_id, self.root_table),
               Column(self.lemma_transcript, "VARCHAR(128)"),
               Column(self.lemma_verbalnoun, "VARCHAR(1)")]

        self.create_table_description(
            self.lemma_table, lst)

        self.create_table_description(
            self.corpus_table,
            [Identifier(self.corpus_id,         "MEDIUMINT(7) UNSIGNED"),
             Column(self.corpus_word,           "VARCHAR( 512)"),
             Column(self.corpus_adverbial,      "VARCHAR(   1)"),
             Column(self.corpus_alternatives,   "VARCHAR( 128)"),
             Column(self.corpus_archaic,        "VARCHAR(   1)"),
             Column(self.corpus_aspect,         "VARCHAR(   8)"),
             Column(self.corpus_created,        "VARCHAR( 128)"),
             Column(self.corpus_dir_obj,        "VARCHAR( 128)"),
             Column(self.corpus_form,           "VARCHAR( 128)"),
             Column(self.corpus_full,           "VARCHAR( 128)"),
             Column(self.corpus_gender,         "VARCHAR(   8)"),
             Column(self.corpus_generated,      "VARCHAR(   1)"),
             Column(self.corpus_gloss,          "VARCHAR( 124)"),
             Column(self.corpus_hypothetical,   "VARCHAR(   1)"),
             Column(self.corpus_ind_obj,        "VARCHAR( 128)"),
             Link(self.corpus_lemma_id, self.lemma_table),
             Column(self.corpus_modified,       "VARCHAR( 128)"),
             Column(self.corpus_number,         "VARCHAR( 128)"),
             Column(self.corpus_pattern,        "VARCHAR( 128)"),
             Column(self.corpus_transcript,     "VARCHAR( 128)"),
             Column(self.corpus_plural_form,    "VARCHAR( 128)"),
             Column(self.corpus_polarity,       "VARCHAR(   8)"),
             Column(self.corpus_possessor,      "VARCHAR(  16)"),
             Link(self.corpus_source_id, self.source_table),
             Column(self.corpus_subject,        "VARCHAR(  16)")])

        self.add_time_feature(self.source_year)

        self._source_id_dict = {}
        self._lemma_id_dict = {}
        self._radicals_dict = {}

        self._source_id = None
        self._root_id = None
        self._lemma_id = None

    @staticmethod
    def _parse_noun_spec(dct: dict) -> str:
        if not dct:
            return ""
        else:
            lst = [dct.get(feature)
                   for feature in ["person", "number", "gender"]
                   if dct.get(feature)]
            return "_".join([x for x in lst if x])

    def _parse_lexemes_entry(self, entry) -> dict:
        # Fix some spelling mistakes in the key names:
        for x, correct in [("achaic", "archaic"),
                           ("archaic ", "archaic"),
                           ("adverbial ", "adverbial"),
                           ("instransitive", "intransitive")]:
            if x in entry.keys():
                entry[correct] = entry[x]

        # get root id if possible:
        root = entry.get("root")
        if root:
            radicals = root.get("radicals", "").strip()
            root_id = self._radicals_dict.get(radicals, 0)
        else:
            root_id = 0

        lst = []
        for ngloss, meaning in enumerate(
                entry.get("glosses", [])):
            gls = meaning["gloss"]
            if len(entry.get("glosses", [])) > 1:
                lst.append(f"({ngloss + 1}) {gls}")
            else:
                lst.append(gls)
        gloss = "; ".join(lst)

        # look up headword:
        try:
            headword = entry.get("headword").get("lemma")
        except AttributeError:
            headword = ""

        # fix 'verbalnoun':
        verbal_noun = entry.get("verbalnoun", "")
        if verbal_noun == "verbalnoun" or verbal_noun == "1":
            verbal_noun = "N"

        # FIXME: Some entries contain comments in square brackets in the
        # FIXME: lemma field. These comments should be removed.
        # lemma = re.match(r"(.*)(?:\s[[])?", entry.get("lemma")).groups()[0]

        d = {self.lemma_id: self._lemma_id,
             self.lemma_label: entry.get("lemma"),
             self.lemma_adjectival: yn(entry.get("adjectival")),
             self.lemma_adverbial: yn(entry.get("adverbial")),
             self.lemma_alternatives: ";".join(entry.get("alternatives", [])),
             self.lemma_apertiumparadigm: entry.get("apertium_paradigm", ""),
             self.lemma_archaic: yn(entry.get("archaic")),
             self.lemma_created: entry.get("created", ""),
             self.lemma_derived_form: entry.get("derived_form", 0),
             self.lemma_ditransitive: yn(entry.get("ditransitive")),
             self.lemma_features: entry.get("features"),
             self.lemma_feedback: entry.get("feedback", ''),
             self.lemma_form: entry.get("form", ''),
             self.lemma_frequency: entry.get("frequency", None),
             self.lemma_norm_freq: entry.get("norm_freq", 0),
             self.lemma_gender: entry.get("gender", ""),
             self.lemma_gloss: gloss,
             self.lemma_headword: headword,
             self.lemma_hypothetical: yn(entry.get("hypothetical")),
             self.lemma_intransitive: yn(entry.get("intransitive")),
             self.lemma_modified: entry.get("modified", ""),
             self.lemma_notduplicate: yn(entry.get("not_duplicate")),
             self.lemma_number: entry.get("number", ""),
             self.lemma_onomastictype: entry.get("onomastic_type", ""),
             self.lemma_participle: yn(entry.get("participle")),
             self.lemma_pending: yn(entry.get("pending")),
             self.lemma_pos: entry.get("pos", ''),
             self.lemma_root_id: root_id,
             self.lemma_transcript: entry.get("phonetic", ""),
             self.lemma_verbalnoun: verbal_noun}
        return d

    def _parse_wordforms_entry(self, entry) -> dict:
        # try to get source id at all costs:
        source_id = 0
        source_list = entry.get("sources")
        if source_list:
            try:
                source_id = self._source_id_dict[source_list[0]]
            except KeyError:
                for x in self._source_id_dict:
                    if self._source_id_dict[x] in source_list:
                        source_id = self._source_id_dict[x]
                        break
                else:
                    source_id = 0

        # collapse the dictionaries behind subject,
        # ind_obj, dir_obj, and possessor:
        subject_str = self._parse_noun_spec(entry.get("subject"))
        dir_obj_str = self._parse_noun_spec(entry.get("dir_obj"))
        ind_obj_str = self._parse_noun_spec(entry.get("ind_obj"))
        possessor_str = self._parse_noun_spec(entry.get("possessor"))

        alternatives_str = ";".join(entry.get("alternatives", []))

        lexeme_id = entry.get("lexeme_id")
        lemma_id = self._lemma_id_dict.get(str(lexeme_id), 0)

        d = {self.corpus_id: self._corpus_id,
             self.corpus_adverbial: yn(entry.get("adverbial")),
             self.corpus_alternatives: alternatives_str,
             self.corpus_archaic: yn(entry.get("archaic")),
             self.corpus_aspect: entry.get("aspect", ""),
             self.corpus_created: entry.get("created", ""),
             self.corpus_dir_obj: dir_obj_str,
             self.corpus_form: entry.get("form", ""),
             self.corpus_full: entry.get("full", ""),
             self.corpus_gender: entry.get("gender", ""),
             self.corpus_generated: yn(entry.get("generated")),
             self.corpus_gloss: entry.get("gloss", ""),
             self.corpus_hypothetical: yn(entry.get("hypothetical")),
             self.corpus_ind_obj: ind_obj_str,
             self.corpus_lemma_id: lemma_id,
             self.corpus_modified: entry.get("modified", ""),
             self.corpus_number: entry.get("number", ""),
             self.corpus_pattern: entry.get("pattern", ""),
             self.corpus_transcript: entry.get("phonetic", ""),
             self.corpus_plural_form: entry.get("plural_form", ""),
             self.corpus_polarity: entry.get("polarity", ""),
             self.corpus_possessor: possessor_str,
             self.corpus_source_id: source_id,
             self.corpus_subject: subject_str,
             self.corpus_word: entry.get("surface_form", "")}
        return d

    def build_load_files(self):
        file_list = self.get_file_list(self.arguments.path, self.file_filter)
        files = []
        for expected_file in self.expected_files:
            for fn in file_list:
                if os.path.basename(fn) == expected_file:
                    files.append(fn)
                    continue
        if len(files) != len(self.expected_files):
            raise RuntimeError(
                "Not all expected files were found in the selected path.")

        if self._widget:
            self._widget.progressSet.emit(len(self.expected_files), "")
            self._widget.progressUpdate.emit(0)

        self._corpus_id = 0

        max_cache = 20000
        for i, filepath in enumerate(files):
            filename = os.path.basename(filepath)

            if filename == "wordforms.bson":
                self.table(self.corpus_table).set_max_cache(max_cache)
                self._widget.progressSet.emit(4520596 // max_cache,
                                              "Loading {}".format(filename))
                self._widget.progressUpdate.emit(0)
            else:
                self._widget.labelSet.emit("Loading {}".format(filename))

            if filename == "sources.bson":
                with open(filepath, "rb") as input_file:
                    for entry in bson.decode_file_iter(input_file):
                        self._source_id = len(self._source_id_dict) + 1
                        key = str(entry["key"])
                        self._source_id_dict[key] = self._source_id
                        d = {self.source_id: self._source_id,
                             self.source_label: entry.get("title", ""),
                             self.source_year: entry.get("year", ""),
                             self.source_author: entry.get("author", ""),
                             self.source_key: entry.get("key", ""),
                             self.source_note: entry.get("note", "")}
                        self.table(self.source_table).add(d)

            elif filename == "roots.bson":
                with open(filepath, "rb") as input_file:
                    for entry in bson.decode_file_iter(input_file):
                        self._root_id = len(self._root_dict) + 1
                        self._root_dict[str(entry["_id"])] = self._root_id
                        radicals = entry.get("radicals", "").strip()
                        d = {self.root_id: self._root_id,
                             self.root_radicals: radicals,
                             self.root_type: entry.get("type", ""),
                             self.root_variant: entry.get("variant", 0),
                             self.root_alternatives:
                                 entry.get("alternatives", "")}
                        self.table(self.root_table).add(d)
                        self._radicals_dict[radicals] = self._root_id

            elif filename == "lexemes.bson":
                with open(filepath, "rb") as input_file:
                    for entry in bson.decode_file_iter(input_file):
                        self._lemma_id = len(self._lemma_id_dict) + 1
                        self._lemma_id_dict[str(entry["_id"])] = self._lemma_id
                        d = self._parse_lexemes_entry(entry)
                        self.table(self.lemma_table).add(d)

            elif filename == "wordforms.bson":
                with open(filepath, "rb") as input_file:
                    for entry in bson.decode_file_iter(input_file):
                        self._corpus_id += 1
                        d = self._parse_wordforms_entry(entry)
                        self.table(self.corpus_table).add(d)

                        if self._widget and not self._corpus_id % max_cache:
                            self._widget.progressUpdate.emit(
                                self._corpus_id // max_cache)
            self.commit_data()

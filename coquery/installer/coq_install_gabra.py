# -*- coding: utf-8 -*-

"""
coq_install_gapra.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import codecs
import csv

from corpusbuilder import *
from errors import *

class BuilderClass(BaseCorpusBuilder):
    file_filter = "s*.words.tagged"

    root_table = "Roots"
    root_id = "RootId"
    root_radicals = "Radicals"
    root_type = "Type"
    root_variant = "Variant"
    root_alternatives = "Alternatives"
    root_gabraid = "ĠabraId"
    _root_dict = {}
    
    lemma_table = "Lexemes"
    lemma_id = "LemmaId"
    lemma_label = "Lemma"
    lemma_gabraid = "ĠabraId"
    _lemma_dict = {}
    
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
    
    source_table = "Sources"
    source_label = "Title"
    source_year = "Year"
    source_author = "Author"
    source_key = "Key"
    source_note = "Note"
    source_gabraid = "ĠabraId"
    _source_dict = {}
    
    word_table = "Wordforms"
    word_gabraid = "ĠabraId"
    word_id = "WordId"
    _word_dict = {}
     
    word_adverbial = "Adverbial"
    word_alternatives = "Alternatives"
    word_archaic = "Archaic"
    word_aspect = "Aspect"
    word_created = "Created"
    word_dir_obj = "Dir_obj"
    word_form = "Form"
    word_full = "Full"
    word_gender = "Gender"
    word_generated = "Generated"
    word_gloss = "Gloss"
    word_hypothetical = "Hypothetical"
    word_ind_obj = "Ind_obj"
    word_lexeme_id = "LemmaId"
    word_modified = "Modified"
    word_number = "Number"
    word_pattern = "Pattern"
    word_phonetic = "Phonetic"
    word_plural_form = "Plural_form"
    word_polarity = "Polarity"
    word_possessor = "Possessor"
    word_source_id = "SourceId"
    word_subject = "Subject"
    word_surfaceform = "Surface_form"
     
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    corpus_table = "Wordforms"
    corpus_id = "WordId"

    expected_files = [
        "lexemes.bson", "roots.bson", "sources.bson", "wordforms.bson"]

    def __init__(self, gui=False, *args):
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.root_table,
            [Primary(self.root_id, "INT(4) UNSIGNED NOT NULL"),
            Column(self.root_radicals, "VARCHAR(9) NOT NULL"),
            Column(self.root_type, "VARCHAR(12) NOT NULL"),
            Column(self.root_alternatives, "VARCHAR(40) NOT NULL"),
            Column(self.root_variant, "TINYINT(1) UNSIGNED"),
            Link(self.root_source_id, self.source_table)])
        
        self.add_time_feature(self.source_year)
    
    @staticmethod
    def get_modules():
        return [("bson", "PyMongo", "http://api.mongodb.org/python/current/index.html")]
    
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
    def get_description():
        return [
            "Ġabra is a free, open lexicon for Maltese, built by collecting various different lexical resources into one common database. While it is not yet a complete dictionary for Maltese, it already contains 16,291 entries and 4,520,596 inflectional word forms. Many of these are linked by root, include translations in English, and are marked for various morphological features."]

    @staticmethod
    def get_references():
        return ['John J. Camilleri. "<i>A Computational Grammar and Lexicon for Maltese</i>", M.Sc. Thesis. Chalmers University of Technology. Gothenburg, Sweden, September 2013. ']

    @staticmethod
    def get_url():
        return "http://mlrs.research.um.edu.mt/resources/gabra/"

    @staticmethod
    def get_license():
        return '<a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>'

    #def build_load_files(self):
        #files = [x for x in sorted(self.get_file_list(self.arguments.path, self.file_filter)) if os.path.basename(x).lower() in BuilderClass.expected_files]
        #if self._widget:
            #self._widget.progressSet.emit(len(BuilderClass.expected_files), "")
            #self._widget.progressUpdate.emit(0)

        #for i, filename in ["sources.bson", "roots.bson", "lexemes.bson", "wordforms.bson"]:
            #with open(filename, "rb") as input_file:
                #for entry in bson.decode_file_iter(input_file):
                    #if filename == "sources.bson":
                        #d = {self.source_label: entry.get("title"),
                            #self.source_year: entry.get("year"),
                            #self.source_author: entry.get("author"),
                            #self.source_key: entry.get("key"),
                            #self.source_gabraid: entry.get("_id"),
                            #self.source_note: entry.get("note")}
                        #self._source_id = self.table(self.source_table).get_or_insert(d)
                        #self._source_dict[entry["_id"]] = self._source_id
                    #elif filename == "roots.bson":
                        #d = {self.root_radicals: entry.get("radicals"),
                             #self.root_type: entry.get("type"),
                             #self.root_variant: entry.get("variant"),
                             #self.root_alternatives: entry.get("alternatives"),
                             #self.root_gabraid: entry.get("_id")}
                        #self._root_id = self.table(self.root_table).get_or_insert(d)
                        #self._root_dict[entry["_id"]] = self._root_id
                    #elif filename == "lexemes.bson":
                        ## Fix some spelling mistakes in the key names:
                        #for x, correct in [("achaic", "archaic"), 
                                           #("archaic ", "archaic"),
                                           #("adverbial ", "adverbial"),
                                           #("instransitive", "intransitive")]:
                            #if x in entry.keys():
                                #entry[correct] = entry[x]
                        #d = {self.lemma_label: entry.get("lemma"),
                            #self.lemma_gabraid: entry.get("_id"),
                            #self.lemma_adjectival: entry.get("adjectival"),
                            #self.lemma_adverbial: entry.get("adverbial"),
                            #self.lemma_alternatives: entry.get("alternatives"),
                            #self.lemma_apertiumparadigm: entry.get("apertium_paradigm"),
                            #self.lemma_archaic: entry.get("archaic"),
                            #self.lemma_created: entry.get("created"),
                            #self.lemma_derived_form: entry.get("derived_form"),
                            #self.lemma_ditransitive: entry.get("ditransitive"),
                            #self.lemma_features: entry.get("features"),
                            #self.lemma_feedback: entry.get("feedback"),
                            #self.lemma_form: entry.get("form"),
                            #self.lemma_frequency: entry.get("frequency"),
                            #self.lemma_gender: entry.get("gender"),
                            #self.lemma_gloss: entry.get("gloss"),
                            #self.lemma_headword: entry.get("headword"),
                            #self.lemma_hypothetical: entry.get("hypothetical"),
                            #self.lemma_intransitive: entry.get("intransitive"),
                            #self.lemma_modified: entry.get("modified"),
                            #self.lemma_notduplicate: entry.get("not_duplicate"),
                            #self.lemma_number: entry.get("number"),
                            #self.lemma_onomastictype: entry.get("onomastic_type"),
                            #self.lemma_participle: entry.get("participle"),
                            #self.lemma_pending: entry.get("pending"),
                            #self.lemma_pos: entry.get("pos"),
                            #self.lemma_root_id: self._root_dict.get(entry.get("root")),
                            #self.lemma_transcript: entry.get("phonetic"),
                            #self.lemma_verbalnoun: entry.get("verbalnoun"),}
                        #self._lemma_id = self.table(self.lemma_table).get_or_insert(d)
                        #self._lemma_dict[entry["_id"]] = self._lemma_id
                    #elif filename == "wordforms.bson":
                        #d = {self.word_gabraid: entry.get("_id"),
                            #self.word_adverbial: entry.get("Adverbial"),
                            #self.word_alternatives: entry.get("Alternatives"),
                            #self.word_archaic: entry.get("Archaic"),
                            #self.word_aspect: entry.get("Aspect"),
                            #self.word_created: entry.get("Created"),
                            #self.word_dir_obj: entry.get("Dir_obj"),
                            #self.word_form: entry.get("Form"),
                            #self.word_full: entry.get("Full"),
                            #self.word_gender: entry.get("Gender"),
                            #self.word_generated: entry.get("Generated"),
                            #self.word_gloss: entry.get("Gloss"),
                            #self.word_hypothetical: entry.get("Hypothetical"),
                            #self.word_ind_obj: entry.get("Ind_obj"),
                            #self.word_lexeme_id: self._lemma_dict.get(entry.get("lexeme_id")),
                            #self.word_modified: entry.get("Modified"),
                            #self.word_number: entry.get("Number"),
                            #self.word_pattern: entry.get("Pattern"),
                            #self.word_phonetic: entry.get("Phonetic"),
                            #self.word_plural_form: entry.get("Plural_form"),
                            #self.word_polarity: entry.get("Polarity"),
                            #self.word_possessor: entry.get("Possessor"),
                            #self.word_source_id: self._source_dict.get(entry.get("sources")),
                            #self.word_subject: entry.get("Subject"),
                            #self.word_surfaceform: entry.get("Surface_form")}
                        #self._word_id = self.table(self.word_table).get_or_insert(d)
                        #self._word_dict[entry["_id"]] = self._word_id

if __name__ == "__main__":
    BuilderClass().build()

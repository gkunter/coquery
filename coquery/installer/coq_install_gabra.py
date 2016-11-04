# -*- coding: utf-8 -*-

"""
coq_install_gapra.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery.corpusbuilder import *
from coquery.errors import *
from coquery.bibliography import *

class BuilderClass(BaseCorpusBuilder):
    file_filter = "*.bson"
    expected_files = [
        "lexemes.bson", "roots.bson", "sources.bson", "wordforms.bson"]

    root_table = "Roots"
    root_id = "RootId"
    root_radicals = "Radicals"
    root_type = "Type"
    root_variant = "Variant"
    root_alternatives = "Alternatives"
    _root_dict = {}
    
    _lemma_dict = {}
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
    lemma_radicals = "Radicals"
    lemma_root_id = "RootId"
    lemma_transcript = "Phonetic"
    lemma_verbalnoun = "Verbal_noun"
    
    _source_dict = {}
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
    def get_language():
        return "Maltese"
    
    @staticmethod
    def get_language_code():
        return "mt"
        
    @staticmethod
    def get_description():
        return [
            "Ġabra is a free, open lexicon for Maltese, built by collecting various different lexical resources into one common database. While it is not yet a complete dictionary for Maltese, it already contains 16,291 entries and 4,520,596 inflectional word forms. Many of these are linked by root, include translations in English, and are marked for various morphological features."]

    @staticmethod
    def get_references():
        return [Reference(
            authors=PersonList(Person(
                first="John", middle="J.", last="Camilleri")),
            title="A Computational Grammar and Lexicon for Maltese", 
            other="M.Sc. Thesis. Chalmers University of Technology. Gothenburg, Sweden, September 2013.")]

    @staticmethod
    def get_url():
        return "http://mlrs.research.um.edu.mt/resources/gabra/"

    @staticmethod
    def get_license():
        return 'Ġabra is available under the terms of the <a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.'

    def __init__(self, gui=False, *args):
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.root_table,
            [Identifier(self.root_id, "SMALLINT(4) UNSIGNED"),
            Column(self.root_radicals, "VARCHAR(9)"),
            Column(self.root_type, "ENUM('geminated','irregular','strong','weak-final','weak-initial','weak-medial')"),
            Column(self.root_alternatives, "ENUM('','?-g?-b-r','?-j-j','?-k-l-m','?-l-?-q','?-m-j²','?-n-?-l','?-n-?-r','?-w-?','?-w-f','b-d-j','b-h-r-?','b-s-b-s','d-?-d-?','d-?-q','f-r-q-n','f-s-j','g-b-x','g-z-z','h-j-d-r','h-n-d-b','h-r-h-r','k-?-b-r','l-m-b-b','l-n-b-t','n-?-g?','n-w-n-m','p-s-d-j','q-?-d-r','q-l-q-l','q-w-w','s-r-d-k','s-r-w-n','see h-?-?','see h-?-h-?','see p-n-n','see p-n-p-n','see p-x-p-x','see p-x-x','t-b-t-b','z-p-z-p')"),
            Column(self.root_variant, "ENUM('0', '1','2','3','4','5')")])
            
        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "ENUM('1','2','3','4','5','6','7','8','9','10')"),
             Column(self.source_key, "ENUM('Apertium2014','Camilleri2013','DM2015','Ellul2013','Falzon2013','KelmaKelma','KelmetilMalti','Mayer2013','Spagnol2011','UserFeedback')"),
             Column(self.source_label, "ENUM('A computational grammar and lexicon for Maltese','A Tale of Two Morphologies. Verb structure and argument alternations in Maltese','Anonymous feedback suggestions from users','Apertium: A free/open-source machine translation platform','Basic English-Maltese Dictionary','Deverbal nouns in Maltese','Dizzjunarju Malti','Fixing the broken plural in Maltese','Kelma Kelma Facebook Page','Kelmet il-Malti Facebook Group')"),
             Column(self.source_year, "ENUM('','2011','2013','2014','2015')"),
             Column(self.source_author, "ENUM('Apertium','Grazio Falzon','John J. Camilleri','Leanne Ellul','Michael Spagnol','Thomas Mayer, Michael Spagnol & Florian Schönhuber','Various')"),
             Column(self.source_note, "ENUM('','(in print)','Contributions by research assistants funded by the DM project','Germany: University of Konstanz dissertation','http://www.apertium.org/','https://www.facebook.com/groups/246657308743181/','https://www.facebook.com/kelmakelma.mt','Malta: University of Malta dissertation','Sweden: Chalmers University of Technology, M.Sc. thesis')")])
            
        self.create_table_description(self.lemma_table,
            [Identifier(self.lemma_id, "SMALLINT(5) UNSIGNED"),
             Column(self.lemma_label, "VARCHAR(50)", index_length=8),
             Column(self.lemma_adjectival, "ENUM('','Y')"),
             Column(self.lemma_adverbial, "ENUM('','Y')"),
             Column(self.lemma_alternatives, "VARCHAR(35)"),
             Column(self.lemma_apertiumparadigm, "VARCHAR(50)"),
             Column(self.lemma_archaic, "ENUM('','Y')"),
             Column(self.lemma_created, "VARCHAR(26)"),
             Column(self.lemma_derived_form, "ENUM('0','1','2','3','5','6','7','8','9','10')"),
             Column(self.lemma_ditransitive, "ENUM('','N','Y')"),
             Column(self.lemma_features, "ENUM('','toponym')"),
             Column(self.lemma_feedback, "VARCHAR(50)"),
             Column(self.lemma_form, "ENUM('','accretive','comparative','diminutive','mimated','participle','verablnoun','verbalnoun')"),             
             Column(self.lemma_frequency, "INT"),
             Column(self.lemma_gender, "ENUM('','f','m')"),
             Column(self.lemma_gloss, "VARCHAR(50)", index_length=12), 
             Column(self.lemma_headword, "VARCHAR(50)"),             
             Column(self.lemma_hypothetical, "ENUM('','N','Y')"),
             Column(self.lemma_intransitive, "ENUM('','N','Y')"),
             Column(self.lemma_modified, "VARCHAR(26)"),             
             Column(self.lemma_notduplicate, "ENUM('','N','Y')"),
             Column(self.lemma_number, "ENUM('','s')"),
             Column(self.lemma_onomastictype, "ENUM('','anthroponym','other','toponym')"),
             Column(self.lemma_participle, "ENUM('','N','Y')"),
             Column(self.lemma_pending, "ENUM('','N','Y')"),
             Column(self.lemma_pos, "ENUM('','ADJ','ADP','ADV','CONJ','DET','INTJ','NOUN','NUM','PART','PRON','PROPN','VERB','X')"),
             Column(self.lemma_radicals, "VARCHAR(50)", index_length=7),
             Link(self.lemma_root_id, self.root_table),             
             Column(self.lemma_transcript, "VARCHAR(29)"),             
             Column(self.lemma_verbalnoun, "ENUM('','Y')")])           

        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(7) UNSIGNED"),
             Column(self.corpus_word, "VARCHAR(50)", index_length=15),
             Column(self.corpus_adverbial, "ENUM('','N','Y')"),
             Column(self.corpus_alternatives, "VARCHAR(26)"),
             Column(self.corpus_archaic, "ENUM('','N','Y')"),
             Column(self.corpus_aspect, "ENUM('','imp','impf','pastpart','perf')"),
             Column(self.corpus_created, "VARCHAR(26)"),
             Column(self.corpus_dir_obj, "ENUM('','p1_pl','p1_pl_mf','p1_sg','p1_sg_mf','p2_pl','p2_pl_mf','p2_sg','p2_sg_mf','p3_pl','p3_pl_mf','p3_sg_f','p3_sg_m')"),
             Column(self.corpus_form, "ENUM('','comparative','diminutive','interrogative','mimated','superlative','verbalnoun')"),
             Column(self.corpus_full, "CHAR(50)"),
             Column(self.corpus_gender, "ENUM('','f','m','mf','pl','u')"),
             Column(self.corpus_generated, "ENUM('','N','Y')"),
             Column(self.corpus_gloss, "ENUM('','(obsolete) Harder, more compact or solid','A bray','A chiselling. Nuance','A confession','A flirtatious person. Girl-flirt','A lazy worker who stops frequently from work','A piercing','A short rest from work','A stripping, undressing','a swim','A weeding','a young man','a young woman','Balder','boy, child, son','Breathing. Enabling something to breathe','Causing someone to incur expenses','children, offspring','Closer, nearer','Expenditure','Fatter, stouter','Fiercer, harsher','Flirting, making love','flushes: rushes of blood wo the face during menopause or pregnancy','Frequent/repeated stone-dressing','girl, child, daughter','great grandfather','great grandmother','great grandparents','Growth/spread of dog-grass','Growth/spreading of Bermuda grass','Gust of wind; a blowin, a swelling; inflation','Holier; superlative l-eqdes/l-aqdes, the holiest','Hotter, warmer','Inflation. Swelling of face, whitlow, etc.','Migration of birds','Migrations of birds','More ancient, older','More beautiful','More nauseating','Nose','Nostrils','nun','Outbreak of flu, epidemic','Part of a crumbled wall of a field','Penetration','Penetrations','Piercing, communicating (room with another)','Piercings','Purer, more purified','Self-conceit','Short for aktar mis?ut, naughtier, more troublesome; more perverse','Shorter','Shying, skittishness (of horses)','Small bellows','Smaller/younger','Sourer','Spending, expenses, expenditure','Spending, incurring expenses','Stone-dressing','Taking umbrage at something. Shying','Taller/longer','trifles','Wider, broader','witch','young women')"),
             Column(self.corpus_hypothetical, "ENUM('','N','Y')"),
             Column(self.corpus_ind_obj, "ENUM('','p1_pl','p1_pl_mf','p1_sg','p1_sg_mf','p2_pl','p2_pl_mf','p2_sg','p2_sg_mf','p3_pl','p3_pl_mf','p3_sg_f','p3_sg_m')"),
             Link(self.corpus_lemma_id, self.lemma_table),
             Column(self.corpus_modified, "VARCHAR(26)"),
             Column(self.corpus_number, "ENUM('','coll','dl','pl','pl_ind','pl_pl','sg','sgv','sp')"),
             Column(self.corpus_pattern, "ENUM('','CCCVCCVC','CCCVCVC','CCCVVCVC','CCVCCV','CCVCCVC','CCVCVC','CCVVC','CCVVCCVC','CCVVCV','CCVVCVC','CVCCCVCCVC','CVCCV','CVCCVC','CVCCVCV','CVCCVCVCCVC','CVCVC','CVCVCCCVCVC','CVCVCV','CVCVCVCCVC','CVVC','CVVCCVC','CVVCVC','VCCCV','VCCCVCVC','VCCCVCVCCVC','VCCVCCVVCVC','VCCVCVC','VCCVCVCCVC','VCCVVC','VCCVVCV','VCVCCVC','VCVVC','VCVVCV','VCVVCVC','VCVVCVCVC','VVCCV','VVCVC')"),
             Column(self.corpus_transcript, "VARCHAR(13)"),
             Column(self.corpus_plural_form, "ENUM('','counted')"),
             Column(self.corpus_polarity, "ENUM('','neg','pos')"),
             Column(self.corpus_possessor, "ENUM('','1 Pl','1 Sg','2 Pl','2 Sg','3 Pl','3 Sg F','3 Sg M')"),
             Link(self.corpus_source_id, self.source_table),
             Column(self.corpus_subject, "ENUM('','_pl_mf','_sg_f','_sg_m','p1_pl','p1_pl_mf','p1_sg','p1_sg_mf','p2_pl','p2_pl_mf','p2_sg','p2_sg_mf','p3_pl','p3_pl_mf','p3_sg_f','p3_sg_m')")])
                
        self.add_time_feature(self.source_year)
    
    def build_load_files(self):
        import bson

        def yn(s):
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
        
        files = [x for x in sorted(self.get_file_list(self.arguments.path, self.file_filter)) if os.path.basename(x).lower() in BuilderClass.expected_files]
        if self._widget:
            self._widget.progressSet.emit(len(BuilderClass.expected_files), "")
            self._widget.progressUpdate.emit(0)
    
        self._corpus_id = 0

        for i, filepath in enumerate(files):
            filename = os.path.basename(filepath)
            
            if filename == "wordforms.bson":
                max_cache = 20000
                self.table(self.corpus_table)._max_cache = max_cache
                self._widget.progressSet.emit(4520596 // max_cache, "Loading {}".format(filename))
                self._widget.progressUpdate.emit(0)
            else:
                self._widget.labelSet.emit("Loading {}".format(filename))
            
            with open(filepath, "rb") as input_file:
                for entry in bson.decode_file_iter(input_file):
                    self._entry = entry
                    if filename == "sources.bson":
                        self._source_id = len(self._source_dict) + 1
                        self._source_dict[str(entry["key"])] = self._source_id
                        d = {
                            self.source_id: self._source_id,
                            self.source_label: entry.get("title", ""),
                            self.source_year: entry.get("year", ""),
                            self.source_author: entry.get("author", ""),
                            self.source_key: entry.get("key", ""),
                            self.source_note: entry.get("note", "")}
                        self.table(self.source_table).add(d)
                    
                    elif filename == "roots.bson":
                        self._root_id = len(self._root_dict) + 1
                        self._root_dict[str(entry["_id"])] = self._root_id
                        d = {self.root_id: self._root_id,
                             self.root_radicals: entry.get("radicals", ""),
                             self.root_type: entry.get("type", ""),
                             self.root_variant: entry.get("variant", 0),
                             self.root_alternatives: entry.get("alternatives", "")}
                        self.table(self.root_table).add(d)
                    
                    elif filename == "lexemes.bson":
                        # Fix some spelling mistakes in the key names:
                        for x, correct in [("achaic", "archaic"), 
                                           ("archaic ", "archaic"),
                                           ("adverbial ", "adverbial"),
                                           ("instransitive", "intransitive")]:
                            if x in entry.keys():
                                entry[correct] = entry[x]
                        self._lemma_id = len(self._lemma_dict) + 1
                        self._lemma_dict[str(entry["_id"])] = self._lemma_id

                        # get root id if possible, and also root radicals:
                        root_id = None
                        root = entry.get("root", "")
                        if root:
                            root_id = str(root.get("_id"))
                            root_radicals = root.get("radicals", "")
                        root_link = self._root_dict.get(root_id, 0)

                        # look up headword:
                        headword = None
                        headword_dict = entry.get("headword", "")
                        if headword_dict:
                            headword = headword_dict.get("lemma")

                        # fix 'verbalnoun':
                        verbal_noun = entry.get("verbalnoun", "")
                        if verbal_noun == "verbalnoun" or verbal_noun == "1":
                            verbal_noun = "N"

                        d = {
                            self.lemma_id: self._lemma_id,
                            self.lemma_label: entry.get("lemma", ""),
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
                            self.lemma_frequency: entry.get("frequency", 0),
                            self.lemma_gender: entry.get("gender", ""),
                            self.lemma_gloss: entry.get("gloss", ""),
                            self.lemma_headword: headword,
                            self.lemma_hypothetical: yn(entry.get("hypothetical")),
                            self.lemma_intransitive: yn(entry.get("intransitive")),
                            self.lemma_modified: entry.get("modified", ""),
                            self.lemma_notduplicate: yn(entry.get("not_duplicate")),
                            self.lemma_number: entry.get("number", ""),
                            self.lemma_onomastictype: entry.get("onomastic_type", ""),
                            self.lemma_participle: yn(entry.get("participle")),
                            self.lemma_pending: yn(entry.get("pending")),
                            self.lemma_pos: entry.get("pos",''),
                            self.lemma_radicals: root_radicals,
                            self.lemma_root_id: root_link,
                            self.lemma_transcript: entry.get("phonetic", ""),
                            self.lemma_verbalnoun: entry.get("verbalnoun")}
                        self.table(self.lemma_table).add(d)
                    
                    elif filename == "wordforms.bson":
                        self._corpus_id += 1

                        # try to get source id at all costs:
                        source_id = None
                        source_list = entry.get("sources")
                        if source_list:
                            try:
                                source_id = self._source_dict[source_list[0]]
                            except KeyError:
                                for x in self._source_dict:
                                    if self._source_dict[x] == source_list[0]:
                                        source_id = self._source_dict[x]
                                        break
                                else:
                                    source_id = 0
                        
                        # collapse the dictionaries behind subject, 
                        # ind_obj, and dir_obj:
                        subj_dict = entry.get("subject")
                        l = []
                        if subj_dict:
                            l = [subj_dict["person"], subj_dict["number"]]
                            if "gender" in subj_dict:
                                l.append(subj_dict["gender"])
                        subj = "_".join(l)

                        ind_obj_dict = entry.get("ind_obj")
                        l = []
                        if ind_obj_dict:
                            l = [ind_obj_dict["person"], ind_obj_dict["number"]]
                            if "gender" in ind_obj_dict:
                                l.append(ind_obj_dict["gender"])
                        ind_obj = "_".join(l)

                        dir_obj_dict = entry.get("dir_obj")
                        l = []
                        if dir_obj_dict:
                            l = [dir_obj_dict["person"], dir_obj_dict["number"]]
                            if "gender" in dir_obj_dict:
                                l.append(dir_obj_dict["gender"])
                        dir_obj = "_".join(l)

                        d = {self.corpus_id: self._corpus_id, 
                            self.corpus_adverbial: yn(entry.get("adverbial")),
                            self.corpus_alternatives: ";".join(entry.get("alternatives", [])),
                            self.corpus_archaic: yn(entry.get("archaic")),
                            self.corpus_aspect: entry.get("aspect", ""),
                            self.corpus_created: entry.get("created", ""),
                            self.corpus_dir_obj: dir_obj,
                            self.corpus_form: entry.get("form", ""),
                            self.corpus_full: entry.get("full", ""),
                            self.corpus_gender: entry.get("gender", ""),
                            self.corpus_generated: yn(entry.get("generated")),
                            self.corpus_gloss: entry.get("gloss", ""),
                            self.corpus_hypothetical: yn(entry.get("hypothetical")),
                            self.corpus_ind_obj: ind_obj,
                            self.corpus_lemma_id: self._lemma_dict.get(str(entry.get("lexeme_id"))),
                            self.corpus_modified: entry.get("modified", ""),
                            self.corpus_number: entry.get("number", ""),
                            self.corpus_pattern: entry.get("pattern", ""),
                            self.corpus_transcript: entry.get("phonetic", ""),
                            self.corpus_plural_form: entry.get("plural_form", ""),
                            self.corpus_polarity: entry.get("polarity", ""),
                            self.corpus_possessor: entry.get("possessor", ""),
                            self.corpus_source_id: source_id,
                            self.corpus_subject: subj,
                            self.corpus_word: entry.get("surface_form", "")}
                        self.table(self.corpus_table).add(d)
                        phon = entry.get("phonetic")

                        if self._widget and not self._corpus_id % max_cache:
                            self._widget.progressUpdate.emit(self._corpus_id // max_cache)
                self.commit_data()    

if __name__ == "__main__":
    BuilderClass().build()


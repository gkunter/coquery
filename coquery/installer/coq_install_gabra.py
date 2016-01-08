# -*- coding: utf-8 -*-

"""
coq_install_gapra.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License. A 
Coquery exception applies under GNU GPL version 3 section 7.

For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>. For the Coquery 
exception, see <http://www.coquery.org/license/>.
"""

from __future__ import unicode_literals
import codecs
import csv

from corpusbuilder import *
from errors import *

class BuilderClass(BaseCorpusBuilder):
    file_filter = "*.bson"

    root_table = "Roots"
    root_id = "RootId"
    root_radicals = "Radicals"
    root_type = "Type"
    root_variant = "Variant"
    root_alternatives = "Alternatives"
    root_gabraid = "GabraId"
    _root_dict = {}
    
    _lemma_dict = {}
    lemma_table = "Lexemes"

    lemma_id = "LemmaId"
    lemma_label = "Lemma"
    lemma_gabraid = "GabraId"
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
    source_gabraid = "GabraId"
    
    word_table = "Wordforms"
    word_id = "WordId"
     
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
    word_lemma_id = "LemmaId"
    word_modified = "Modified"
    word_number = "Number"
    word_pattern = "Pattern"
    word_transcript = "Phonetic"
    word_plural_form = "Plural_form"
    word_polarity = "Polarity"
    word_possessor = "Possessor"
    word_source_id = "Source"
    word_subject = "Subject"
    word_surfaceform = "Surface_form"
     
    #file_table = "Files"
    #file_id = "FileId"
    #file_name = "Filename"
    #file_path = "Path"

    corpus_table = "Wordforms"
    corpus_id = "WordId"

    expected_files = [
        "lexemes.bson", "roots.bson", "sources.bson", "wordforms.bson"]
        #"sources.bson", "roots.bson", "lexemes.bson"]

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
        return 'Ġabra is available under the terms of the <a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.'

    def __init__(self, gui=False, *args):
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.root_table,
            [Primary(self.root_id, "SMALLINT(4) UNSIGNED NOT NULL"),
            Column(self.root_radicals, "VARCHAR(9) NOT NULL"),
            Column(self.root_type, "ENUM('geminated','irregular','strong','weak-final','weak-initial','weak-medial')"),
            Column(self.root_alternatives, "ENUM('','?-g?-b-r','?-j-j','?-k-l-m','?-l-?-q','?-m-j²','?-n-?-l','?-n-?-r','?-w-?','?-w-f','b-d-j','b-h-r-?','b-s-b-s','d-?-d-?','d-?-q','f-r-q-n','f-s-j','g-b-x','g-z-z','h-j-d-r','h-n-d-b','h-r-h-r','k-?-b-r','l-m-b-b','l-n-b-t','n-?-g?','n-w-n-m','p-s-d-j','q-?-d-r','q-l-q-l','q-w-w','s-r-d-k','s-r-w-n','see h-?-?','see h-?-h-?','see p-n-n','see p-n-p-n','see p-x-p-x','see p-x-x','t-b-t-b','z-p-z-p')"),
            Column(self.root_variant, "ENUM('1','2','3','4','5')")])
            
        self.create_table_description(self.source_table,
            [Primary(self.source_id, "ENUM('1','2','3','4','5','6','7','8','9','10') NOT NULL"),
             Column(self.source_key, "ENUM('Apertium2014','Camilleri2013','DM2015','Ellul2013','Falzon2013','KelmaKelma','KelmetilMalti','Mayer2013','Spagnol2011','UserFeedback') NOT NULL"),
             Column(self.source_label, "ENUM('A computational grammar and lexicon for Maltese','A Tale of Two Morphologies. Verb structure and argument alternations in Maltese','Anonymous feedback suggestions from users','Apertium: A free/open-source machine translation platform','Basic English-Maltese Dictionary','Deverbal nouns in Maltese','Dizzjunarju Malti','Fixing the broken plural in Maltese','Kelma Kelma Facebook Page','Kelmet il-Malti Facebook Group') NOT NULL"),
             Column(self.source_year, "ENUM('2011','2013','2014','2015') NOT NULL"),
             Column(self.source_author, "ENUM('Apertium','Grazio Falzon','John J. Camilleri','Leanne Ellul','Michael Spagnol','Thomas Mayer, Michael Spagnol & Florian Schönhuber','Various') NOT NULL"),
             Column(self.source_note, "ENUM('','(in print)','Contributions by research assistants funded by the DM project','Germany: University of Konstanz dissertation','http://metashare.metanet4u.eu/repository/browse/basic-english-maltese-dictionary/13fc5802abc511e1a40','http://www.apertium.org/','https://www.facebook.com/groups/246657308743181/','https://www.facebook.com/kelmakelma.mt','Malta: University of Malta dissertation','Sweden: Chalmers University of Technology, M.Sc. thesis') NOT NULL")])
            
        self.create_table_description(self.lemma_table,
            [Primary(self.lemma_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.lemma_label, "TINYTEXT"),
             Column(self.lemma_adjectival, "ENUM('0','1') NOT NULL"),
             Column(self.lemma_adverbial, "ENUM('0','1') NOT NULL"),
             Column(self.lemma_alternatives, "VARCHAR(35) NOT NULL"),
             Column(self.lemma_apertiumparadigm, "TEXT"),
             #Column(self.lemma_apertiumparadigm, """ENUM('?/abib__n','?/arbuna__n_f','?/armug__n_m','?/obla__adj_f','?/u?__adj','?at/i__adj','?l/iqa__n_f','?omb__n_m','/belt__n_f','/iblaq__adj','/ilbiera?__adv','/imbag?ad__adv','/ma__adv','/wild__n_m','att/ri?i__n_f','b/niedem__n_m','ba?ri__n_m','barrani__adj','bg?/id__adj','bojkot/t__n_m','bsa??it/u__adj','buff/u__n_m','differenti__adj','dixx__n_m','double_cons','eminent__adj','ener?ija__n_f','entit/à__n_f','epi/ku__adj','ewl/ieni__adj','Ewrope/w__adj','f/artas__adj','first_cons','first_vowel','g?/ama__n_GD','g?/ibien__n_GD','g?ar/bi__n_m','G?awdxi__n','gowl__n_m','gri?__adj','haddiem__n','hemm__adv','i-/erbg?a__n','il-/biera?__adv','immedjatament__adv','imxarr/ab__adj','is-/Sibt__n','ispettur__n_mf','it-/Tnejn__n','Kattoli/ku__n','kif__adv','kwadr/u__adj','lab/ra__n_f','Lhud__n','m/ewta__n_f','ma?mu?__adj','Malta__np','Malti__adj','maz/za__n_f','mg?a??/el__adj','miel/a?__adj','mis/lem__n_m','mistied/en__adj','mniss/el__adj','molestja__n_f','moviment__n_m','nativ__adj','ohxon__adj','Olimpjadi__np','p/asta?__n_m','parti__n_m','pjanet/a__n_m','Portugi?__n','profet/a__n_m','propost/a__n_f','q/arn__n_m','q/ormi__n_m','qarrej__n_m','qot/na__n_f','rebbie?__n_m','rebbieg?a__n_f','rettili__n_m','ri?/el__n_m','rq/iq__adj','s?ubij/a__n_f','s/alva??__n_m','San__np','se__adv','stampa__n_f','stazzjon__n_f','Taljan__n','teknolo?i/ku__adj','tib/na__n_f','Tibet__np','tik/ka__n_f','tni??is__n_m','tor/k__n_m','trib/ù__n_m','two_cons','unjoni__n_f','wer/?__n_m','wies/a\'__adj','xal/la__n_f','xir/ja__n_f')"""),
             Column(self.lemma_archaic, "ENUM('0','1')"),
             Column(self.lemma_created, "TEXT"),
             Column(self.lemma_derived_form, "TEXT"),
             Column(self.lemma_ditransitive, "TEXT"),
             Column(self.lemma_features, "TEXT"),
             #Column(self.lemma_feedback, """ENUM('','"o" minflok "a" f\'diversi verbi.','dfinnieu --> dfinnieh','Dictionnaries have : ti?ti?bor in Dictionaries (Vassalli, Aquilina, Serracino-Inglott) and in Standard Maltese','First vowel a is missing in verb inflections','G?-D-W','Hi Michael!  The perfect conjugation looks wrong.  Thanks!','I think the imperfect negative should be e.g. nitkellimx','I think you\'ve put a g instead of g?','imperf. = a - e,  mhux o - o','impf. =  i - a  --> jitlaq .....','Impf. = a - i ','incorrect Vowels in Impf and Imp. nibda, nibdew, ...','incorrectThe meaning is incorrect','J-W-M ?','jin?g?u mhux jin?u   P3 Pl','Maybe "xitla"/"xtieli"  should be added...','Na?seb hemm ?ball: l-"O??ett dirett" P2 Pl u P3 Pl iridu jinqalbu. Grazzi a-a,   mhux i-o.  ','naqra?','nfidthux','nifhemx = nifhimx ....  e??.','niftiehmu, mhux niftehmu .........','nilg?ob -> nilg?abtilg?ob -> tilg?ab ; jilg?ab ; nilag?bu ; jilag?bu : http://www.illum.com.mt/sports/intervista/39186/ilbasketball_huwa_ajjitha#.VeGSsZe68a1','Please can the conjugations be added?','rkibthux','s?antu <-> s?anuimperf. =  i - o','sej?et mhux sej?iet P3, Sg. Fem.','Should P3 Pl Perfect tense be urew, not urejna','sraqthux should be sraqtux. There must be something wrong with all Perfective P1 Sg P3 Sg Masc Negative','t?ajjartu <-> t?ajru;   P2 Pl <-> P3 Pl','Trid ti?i: kkalzrat')"""),
             Column(self.lemma_feedback, "TEXT"),
             Column(self.lemma_form, "ENUM('accretive','comparative','diminutive','mimated','participle','verablnoun','verbalnoun')"),             
             Column(self.lemma_frequency, "INT NOT NULL"),             
             Column(self.lemma_gender, "TEXT"),             
             Column(self.lemma_gloss, "TEXT"),             
             Column(self.lemma_headword, "TEXT"),             
             Column(self.lemma_hypothetical, "ENUM('0','1')"),             
             Column(self.lemma_intransitive, "ENUM('0','1')"),             
             Column(self.lemma_modified, "TEXT"),             
             Column(self.lemma_notduplicate, "ENUM('','1')"),             
             Column(self.lemma_number, "TEXT"),             
             Column(self.lemma_onomastictype, "TEXT"),             
             Column(self.lemma_participle, "ENUM('0','1')"),             
             Column(self.lemma_pending, "ENUM('','1')"),             
             Column(self.lemma_pos, "TEXT"),             
             Column(self.lemma_radicals, "TEXT"), 
             Link(self.lemma_root_id, self.root_table),             
             Column(self.lemma_transcript, "VARCHAR(29)"),             
             Column(self.lemma_verbalnoun, "TEXT")])           

        self.create_table_description(self.word_table,
            [Primary(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.word_adverbial, "ENUM('0','1') NOT NULL"),
             Column(self.word_alternatives, "VARCHAR(26) NOT NULL"),
             Column(self.word_archaic, "ENUM('0','1') NOT NULL"),
             Column(self.word_aspect, "ENUM('imp','impf','pastpart','perf')"),
             Column(self.word_created, "CHAR(26)"),
             Column(self.word_dir_obj, "ENUM('gender:f_number:sg_person:p3','gender:m_number:sg_person:p3','gender:mf_number:pl_person:p1','gender:mf_number:pl_person:p2','gender:mf_number:pl_person:p3','gender:mf_number:sg_person:p1','gender:mf_number:sg_person:p2','number:pl_person:p1','number:pl_person:p2','number:pl_person:p3','number:sg_person:p1','number:sg_person:p2')"),
             Column(self.word_form, "ENUM('','comparative','diminutive','interrogative','mimated','superlative','verbalnoun')"),
             Column(self.word_full, "CHAR(50)"),
             Column(self.word_gender, "ENUM('','f','m','mf','pl','u')"),
             Column(self.word_generated, "ENUM('0','1') NOT NULL"),
             Column(self.word_gloss, "TEXT"),
             Column(self.word_hypothetical, "TEXT"),
             Column(self.word_ind_obj, "TEXT"),
             Link(self.word_lemma_id, self.lemma_table),
             Column(self.word_modified, "TEXT"),
             Column(self.word_number, "TEXT"),
             Column(self.word_pattern, "TEXT"),
             Column(self.word_transcript, "TEXT"),
             Column(self.word_plural_form, "TEXT"),
             Column(self.word_polarity, "TEXT"),
             Column(self.word_possessor, "TEXT"),
             Link(self.word_source_id, self.source_table),
             Column(self.word_subject, "TEXT"),
             Column(self.word_surfaceform, "TEXT")])
                
        self.add_time_feature(self.source_year)
    
    def build_load_files(self):
        import bson
        import json
        
        files = [x for x in sorted(self.get_file_list(self.arguments.path, self.file_filter)) if os.path.basename(x).lower() in BuilderClass.expected_files]
        if self._widget:
            self._widget.progressSet.emit(len(BuilderClass.expected_files), "")
            self._widget.progressUpdate.emit(0)
    
        self._word_id = 0

        for i, filepath in enumerate(files):
            filename = os.path.basename(filepath)
            
            if filename == "wordforms.bson":
                max_cache = 10000
                self.table(self.word_table)._max_cache = max_cache
                self.table(self.word_table)._connection = self.Con
                self._widget.progressSet.emit(4520596 // max_cache, "Loading {}".format(filename))
                self._widget.progressUpdate.emit(0)
            else:
                self._widget.labelSet.emit("Loading {}".format(filename))
            
            with open(filepath, "rb") as input_file:
                for entry in bson.decode_file_iter(input_file):
                    
                    if filename == "sources.bson":
                        self._source_id = len(self._source_dict) + 1
                        self._source_dict[str(entry["_id"])] = self._source_id
                        d = {
                            self.source_id: self._source_id,
                            self.source_label: entry.get("title"),
                            self.source_year: entry.get("year"),
                            self.source_author: entry.get("author"),
                            self.source_key: entry.get("key"),
                            self.source_note: entry.get("note")}
                        self.table(self.source_table).add(d)
                    
                    elif filename == "roots.bson":
                        self._root_id = len(self._root_dict) + 1
                        self._root_dict[str(entry["_id"])] = self._root_id
                        d = {self.root_id: self._root_id,
                             self.root_radicals: entry.get("radicals"),
                             self.root_type: entry.get("type"),
                             self.root_variant: entry.get("variant"),
                             self.root_alternatives: entry.get("alternatives")}
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
                        root = entry.get("root")
                        if root:
                            root_id = str(root.get("_id"))
                            root_radicals = root.get("radicals")
                        root_link = self._root_dict.get(root_id)

                        # look up headword:
                        headword = None
                        headword_dict = entry.get("headword")
                        if headword_dict:
                            headword = headword_dict.get("lemma")

                        d = {
                            self.lemma_id: self._lemma_id,
                            self.lemma_label: entry.get("lemma"),
                            self.lemma_adjectival: entry.get("adjectival", 0),
                            self.lemma_adverbial: entry.get("adverbial", 0),
                            self.lemma_alternatives: ";".join(entry.get("alternatives", [])),
                            self.lemma_apertiumparadigm: entry.get("apertium_paradigm"),
                            self.lemma_archaic: entry.get("archaic", 0),
                            self.lemma_created: entry.get("created"),
                            self.lemma_derived_form: entry.get("derived_form"),
                            self.lemma_ditransitive: entry.get("ditransitive"),
                            self.lemma_features: entry.get("features"),
                            self.lemma_feedback: entry.get("feedback"),
                            self.lemma_form: entry.get("form"),
                            self.lemma_frequency: entry.get("frequency"),
                            self.lemma_gender: entry.get("gender"),
                            self.lemma_gloss: entry.get("gloss"),
                            self.lemma_headword: headword,
                            self.lemma_hypothetical: entry.get("hypothetical", 0),
                            self.lemma_intransitive: entry.get("intransitive", 0),
                            self.lemma_modified: entry.get("modified"),
                            self.lemma_notduplicate: entry.get("not_duplicate"),
                            self.lemma_number: entry.get("number"),
                            self.lemma_onomastictype: entry.get("onomastic_type"),
                            self.lemma_participle: entry.get("participle", 0),
                            self.lemma_pending: entry.get("pending"),
                            self.lemma_pos: entry.get("pos"),
                            self.lemma_radicals: root_radicals,
                            self.lemma_root_id: root_link,
                            self.lemma_transcript: entry.get("phonetic"),
                            self.lemma_verbalnoun: entry.get("verbalnoun"),}
                        self.table(self.lemma_table).add(d)
                    
                    elif filename == "wordforms.bson":
                        self._word_id += 1

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
                        subj = None
                        subj_dict = entry.get("subject")
                        if subj_dict:
                            subj = "_".join(["{}:{}".format(x, subj_dict[x]) for x in sorted(subj_dict.keys())])

                        ind_obj = None
                        ind_dict = entry.get("ind_obj")
                        if ind_dict:
                            ind_obj = "_".join(["{}:{}".format(x, ind_dict[x]) for x in sorted(ind_dict.keys())])

                        dir_obj = None
                        dir_dict = entry.get("dir_obj")
                        if dir_dict:
                            dir_obj = "_".join(["{}:{}".format(x, dir_dict[x]) for x in sorted(dir_dict.keys())])
                        
                        d = {self.word_id: self._word_id, 
                            self.word_adverbial: entry.get("adverbial", 0),
                            self.word_alternatives: ";".join(entry.get("alternatives", [])),
                            self.word_archaic: entry.get("archaic", 0),
                            self.word_aspect: entry.get("aspect"),
                            self.word_created: entry.get("created"),
                            self.word_dir_obj: dir_obj,
                            self.word_form: entry.get("form"),
                            self.word_full: entry.get("full"),
                            self.word_gender: entry.get("gender"),
                            self.word_generated: entry.get("generated", 0),
                            self.word_gloss: entry.get("gloss"),
                            self.word_hypothetical: entry.get("hypothetical", 0),
                            self.word_ind_obj: ind_obj,
                            self.word_lemma_id: self._lemma_dict.get(str(entry.get("lexeme_id"))),
                            self.word_modified: entry.get("modified"),
                            self.word_number: entry.get("number"),
                            self.word_pattern: entry.get("pattern"),
                            self.word_transcript: entry.get("phonetic"),
                            self.word_plural_form: entry.get("plural_form"),
                            self.word_polarity: entry.get("polarity"),
                            self.word_possessor: entry.get("possessor"),
                            self.word_source_id: source_id,
                            self.word_subject: subj,
                            self.word_surfaceform: entry.get("surface_form")}
                        self.table(self.word_table).add(d)

                        if self._widget and not self._word_id % max_cache:
                            self._widget.progressUpdate.emit(self._word_id // max_cache)
                self.commit_data()    

if __name__ == "__main__":
    BuilderClass().build()

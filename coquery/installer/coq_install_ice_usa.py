# -*- coding: utf-8 -*-
"""
coq_install_ice_usa.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function
import os.path


#try:
    #from cStringIO import StringIO
#except ImportError:
    #from io import StringIO
    
from coquery.corpusbuilder import *
from coquery.bibliography import *


ICE_CORPUS_DESIGN = {
    "Non-printed": {
        "Student Writing": {
            "Label": "W1A",
            "Student Essays": 10,
            "Exam Scripts": 10
            },
        "Letters": {
            "Label": "W1B",
            "Social Letters": 15,
            "Business Letters": 15
            }
        },
    "Printed": {
        "Academic Writing": {
            "Label": "W2A",
            "Humanities": 10,
            "Social Sciences": 10,
            "Natural Sciences": 10,
            "Technology": 10
            },
        "Non-Academic Writing": {
            "Label": "W2B",
            "Humanities": 10,
            "Social Sciences": 10,
            "Natural Sciences": 10,
            "Technology": 10
            },
        "Reportage": {
            "Label": "W2C",
            "Press News Reports": 20
        },
        "Instructional Writing": {
            "Label": "W2D",
            "Administrative Writing": 10,
            "Skills/hobbies": 10
            },
        "Persuasive writing": {
            "Label": "W2E",
            "Press editorials": 10
            },
        "Creative writing": {
            "Label": "W2F",
            "Novels & short stories": 20
            }
        }
    }



class corpus_code():

    def get_tag_translate(self, tag):
        translate_dict = {
            "i": "html",
            "p": "p",
            "h": "h1",
            "bold": "b",
            "it": "i",
            "ul": "u",
            "smallcaps": "span style='font-variant: small-caps;'",
            "quote": "span style='font-style: italic; color: darkgrey; '",
            "foreign": "span style='font-style: italic;'",
            "indig": "span style='font-style: italic; color: darkblue; '",
            "-": "s",
            "o": "hr",
            }
        
        if tag in translate_dict:
            return translate_dict[tag]
        else:
            print("unsupported tag: ", tag)
            return tag

    def renderer_open_element(self, tag, attributes):
        context = super(Corpus, self).renderer_open_element(tag, attributes)
        if tag == "@":
            context.append(' <span style="color: lightgrey; background: black;">')
        return context

    def renderer_close_element(self, tag, attributes):
        context = super(Corpus, self).renderer_close_element(tag, attributes)
        if tag == "error":
            try:
                context.append('<span style="color: darkgreen;">{}</span>'.format(attributes["corrected"]))
            except KeyError:
                pass
        if tag == "@":
            context.append("</span>")
        return context

class BuilderClass(BaseCorpusBuilder):
    encoding = "latin-1"
    file_filter = "W??-???.TXT"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word = "Word"
    corpus_file_id = "FileId"
    corpus_source_id = "SourceId"
    corpus_textunit_id = "TextUnitId"
    corpus_subtext = "Subtext"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    
    textunit_table = "Text_units"
    textunit_id = "TextUnitId"
    
    source_table = "Sources"
    source_id = "SourceId"
    source_mode = "Mode"
    source_age = "Age"
    source_gender = "Gender"
    source_ethnicity = "Ethnicity"
    source_date = "Date"
    source_icetext = "ICE_text_category"
    source_icetextcode = "ICE_text_code"
    source_place = "Place"
    
    speaker_table = "Speakers"
    speaker_id = "SpeakerId"
    speaker_forename = "Forename"
    speaker_surname = "Surname"
    speaker_age = "Age"
    speaker_gender = "Gender"
    speaker_nationality = "Nationality"
    speaker_ethnicity = "Ethnicity"
    speaker_birthplace = "Birthplace"
    speaker_education = "Education"
    speaker_educationlevel = "Education_level"
    speaker_occupation = "Occupation"
    speaker_affiliation = "Affiliation"
    speaker_l1 = "Mother_tongue"
    speaker_l2 = "Other_languages"

    


    #expected_files = [
        #W1A-001.TXT  W1A-017.TXT  W1B-013.TXT  W1B-029.TXT  W2A-015.TXT  W2A-031.TXT  W2B-007.TXT  W2B-023.TXT  W2B-039.TXT  W2C-015.TXT  W2D-011.TXT  W2E-007.TXT  W2F-013.TXT
        #W1A-002.TXT  W1A-018.TXT  W1B-014.TXT  W1B-030.TXT  W2A-016.TXT  W2A-032.TXT  W2B-008.TXT  W2B-024.TXT  W2B-040.TXT  W2C-016.TXT  W2D-012.TXT  W2E-008.TXT  W2F-014.TXT
        #W1A-003.TXT  W1A-019.TXT  W1B-015.TXT  W2A-001.TXT  W2A-017.TXT  W2A-033.TXT  W2B-009.TXT  W2B-025.TXT  W2C-001.TXT  W2C-017.TXT  W2D-013.TXT  W2E-009.TXT  W2F-015.TXT
        #W1A-004.TXT  W1A-020.TXT  W1B-016.TXT  W2A-002.TXT  W2A-018.TXT  W2A-034.TXT  W2B-010.TXT  W2B-026.TXT  W2C-002.TXT  W2C-018.TXT  W2D-014.TXT  W2E-010.TXT  W2F-016.TXT
        #W1A-005.TXT  W1B-001.TXT  W1B-017.TXT  W2A-003.TXT  W2A-019.TXT  W2A-035.TXT  W2B-011.TXT  W2B-027.TXT  W2C-003.TXT  W2C-019.TXT  W2D-015.TXT  W2F-001.TXT  W2F-017.TXT
        #W1A-006.TXT  W1B-002.TXT  W1B-018.TXT  W2A-004.TXT  W2A-020.TXT  W2A-036.TXT  W2B-012.TXT  W2B-028.TXT  W2C-004.TXT  W2C-020.TXT  W2D-016.TXT  W2F-002.TXT  W2F-018.TXT
        #W1A-007.TXT  W1B-003.TXT  W1B-019.TXT  W2A-005.TXT  W2A-021.TXT  W2A-037.TXT  W2B-013.TXT  W2B-029.TXT  W2C-005.TXT  W2D-001.TXT  W2D-017.TXT  W2F-003.TXT  W2F-019.TXT
        #W1A-008.TXT  W1B-004.TXT  W1B-020.TXT  W2A-006.TXT  W2A-022.TXT  W2A-038.TXT  W2B-014.TXT  W2B-030.TXT  W2C-006.TXT  W2D-002.TXT  W2D-018.TXT  W2F-004.TXT  W2F-020.TXT
        #W1A-009.TXT  W1B-005.TXT  W1B-021.TXT  W2A-007.TXT  W2A-023.TXT  W2A-039.TXT  W2B-015.TXT  W2B-031.TXT  W2C-007.TXT  W2D-003.TXT  W2D-019.TXT  W2F-005.TXT
        #W1A-010.TXT  W1B-006.TXT  W1B-022.TXT  W2A-008.TXT  W2A-024.TXT  W2A-040.TXT  W2B-016.TXT  W2B-032.TXT  W2C-008.TXT  W2D-004.TXT  W2D-020.TXT  W2F-006.TXT
        #W1A-011.TXT  W1B-007.TXT  W1B-023.TXT  W2A-009.TXT  W2A-025.TXT  W2B-001.TXT  W2B-017.TXT  W2B-033.TXT  W2C-009.TXT  W2D-005.TXT  W2E-001.TXT  W2F-007.TXT
        #W1A-012.TXT  W1B-008.TXT  W1B-024.TXT  W2A-010.TXT  W2A-026.TXT  W2B-002.TXT  W2B-018.TXT  W2B-034.TXT  W2C-010.TXT  W2D-006.TXT  W2E-002.TXT  W2F-008.TXT
        #W1A-013.TXT  W1B-009.TXT  W1B-025.TXT  W2A-011.TXT  W2A-027.TXT  W2B-003.TXT  W2B-019.TXT  W2B-035.TXT  W2C-011.TXT  W2D-007.TXT  W2E-003.TXT  W2F-009.TXT
        #W1A-014.TXT  W1B-010.TXT  W1B-026.TXT  W2A-012.TXT  W2A-028.TXT  W2B-004.TXT  W2B-020.TXT  W2B-036.TXT  W2C-012.TXT  W2D-008.TXT  W2E-004.TXT  W2F-010.TXT
        #W1A-015.TXT  W1B-011.TXT  W1B-027.TXT  W2A-013.TXT  W2A-029.TXT  W2B-005.TXT  W2B-021.TXT  W2B-037.TXT  W2C-013.TXT  W2D-009.TXT  W2E-005.TXT  W2F-011.TXT
        #W1A-016.TXT  W1B-012.TXT  W1B-028.TXT  W2A-014.TXT  W2A-030.TXT  W2B-006.TXT  W2B-022.TXT  W2B-038.TXT  W2C-014.TXT  W2D-010.TXT  W2E-006.TXT  W2F-012.TXT



        #] 

    def __init__(self, gui=False, *args):
        """
        Initialize the corpus builder.
        
        During initialization, the database table structure is defined.
        
        All corpus installers have to call the inherited initializer
        :func:`BaseCorpusBuilder.__init__`.
        
        Parameters
        ----------
        gui : bool
            True if the graphical installer is used, and False if the 
            installer runs on the console.
        """
        super(BuilderClass, self).__init__(gui, *args)

        # specify which features are provided by this corpus and lexicon:
        #self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_POS"]
        #self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_SOURCE"]

        self.check_arguments()
        
        # add table descriptions for the tables used in this database.
        #
        # Every table has a primary key that uniquely identifies each entry
        # in the table. This primary key is used to link an entry from one
        # table to an entry from another table. The name of the primary key
        # stored in a string is given as the second argument to the function
        # add_table_description().
        #
        # A table description is a dictionary with at least a 'CREATE' key
        # which takes a list of strings as its value. Each of these strings
        # represents a MySQL instruction that is used to create the table.
        # Typically, this instruction is a column specification, but you can
        # also add other table options for this table. Note that the primary
        # key cannot be set manually.
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
        
        #self.corpus_table = "corpus"
        #self.corpus_id = "TokenId"
        #self.corpus_word_id = "WordId"
        #self.corpus_file_id = "FileId"
        #self.corpus_source_id = "SourceId"
        
        # Add the main lexicon table. Each row in this table represents a
        # word-form that occurs in the corpus. It has the following columns:
        #
        # WordId
        # An int value containing the unique identifier of this word-form.
        #
        # LemmaId
        # An int value containing the unique identifier of the lemma that
        # is associated with this word-form.
        # 
        # Text
        # A text value containing the orthographic representation of this
        # word-form.
        #
        # Additionally, if NLTK is used to tag part-of-speech:
        #
        # Pos
        # A text value containing the part-of-speech label of this 
        # word-form.
        
        #self.word_table = "word"
        #self.word_id = "WordId"
        #self.word_lemma = "Lemma"
        #self.word_label = "Text"
        #self.word_pos = "Pos"
        
        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(36) NOT NULL"),
             Column(self.word_lemma, "VARCHAR(36) NOT NULL"),
             Column(self.word_pos, "ENUM('CC','CD','DT','EX','FW','IN','JJ','JJR','JJS','LS','MD','NN','NNS','NP','NPS','PDT','POS','PP','PP$','PUNCT','RB','RBR','RBS','RP','SYM','TO','UH','VB','VBD','VBG','VBN','VBP','VBZ','WDT','WP','WP$','WRB') NOT NULL")])
             

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
        
        #self.file_table = "file"
        #self.file_id = "FileId"
        #self.file_name = "Filename"
        #self.file_path = "Path"
        
        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "TINYTEXT NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])
            
        #self.sentence_table = "sentence"
        #self.sentence_id = "SentenceId"
        
        #self.add_table_description(self.sentence_table, self.sentence_id,
            #{"CREATE" : [
                #"`{}` MEDIUMINT(5) UNSIGNED NOT NULL".format(self.sentence_id)]})
        
        #self.source_table = "source"
        #self.source_id = "SourceId"
        #self.source_mode = "Mode"
        #self.source_age = "Age"
        #self.source_gender = "Gender"
        #self.source_ethnicity = "Ethnicity"
        #self.source_date = "Date"
        #self.source_icetext = "ICE_text_category"
        #self.source_icetextcode = "ICE_text_code"
        #self.source_place = "Place"
        
        self.add_time_feature(self.source_date)
        self.add_time_feature(self.source_age)

        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "SMALLINT(3) UNSIGNED NOT NULL"),
            Column(self.source_mode, "TINYTEXT NOT NULL"),
            Column(self.source_date, "VARCHAR(10) NOT NULL"), 
            Column(self.source_icetext, "ENUM('Academic writing humanities','Academic writing natural sciences','Academic writing social sciences','Academic writing technical','Administrative/instructive writing','Business letters','Editorials','Exams','Instructive writing/skills and hobbies','Novels','Popular writing humanities','Popular writing natural sciences','Popular writing social sciences','Popular writing technology','Press reportage','Social letters','Students essays') NOT NULL"), 
            Column(self.source_icetextcode, "ENUM('W1A','W1B','W2A','W2B','W2C','W2D','W2E','W2F') NOT NULL"), 
            Column(self.source_place, "VARCHAR(30) NOT NULL"), 
            Column(self.source_age, "VARCHAR(5) NOT NULL"),  
            Column(self.source_gender, "VARCHAR(1) NOT NULL"),  
            Column(self.source_ethnicity, "VARCHAR(15) NOT NULL")])

        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_source_id, self.source_table)])
                
        self._corpus_id = 0
        self._corpus_code = corpus_code
        

    def xml_preprocess_tag(self, element):
        #self.tag_token(self._corpus_id, element.tag, element.attrib, op=True)
        self.tag_next_token(element.tag, element.attrib)
        #if element.text or list(element):
            #self.tag_next_token(element.tag, element.attrib)
        #else:
            #self.add_empty_tag(element.tag, element.attrib)
            #if element.tag == "x-anonym-x":
                ## ICE-NG contains anonymized labels for names, placenames,
                ## and other nouns. Insert a special label in that case:
                #self._word_id = self.table_get(self.word_table, 
                        #{self.word_label: "ANONYMIZED", 
                        #self.word_lemma: "ANONYMIZED", 
                        #self.word_pos: "np"}, case=True)

    def xml_postprocess_tag(self, element):
        self.tag_token(self._corpus_id, element.tag, element.attrib, cl=True)
        # mon-empty tag
        #if element.text or list(element):
            #self.tag_last_token(element.tag, element.attrib)

    def process_text(self, text):
        for row in text.splitlines():
            try:
                self._value_word_label, self._value_word_pos, self._value_word_lemma = [x.strip() for x in row.split("\t")]
            except ValueError:
                pass
            else:
                self._value_word_label = self._replace_encoding_errors(self._value_word_label)
                self._value_word_lemma = self._replace_encoding_errors(self._value_word_lemma)
                new_sentence = False
                
                if self._value_word_pos == "CD":
                    self._value_word_lemma = self._value_word_label
                if self._value_word_pos in string.punctuation or self._value_word_pos == "''":
                    self._value_word_pos = "PUNCT"
                if self._value_word_pos == "SENT":
                    new_sentence = True
                    self._value_word_pos = "PUNCT"
                    
                if self._value_word_label and self._value_word_lemma:
                    self._word_id = self.table(self.word_table).get_or_insert(
                        {self.word_label: self._value_word_label, 
                        self.word_lemma: self._value_word_lemma, 
                        self.word_pos: self._value_word_pos}, case=True)
                        
                    self.add_token_to_corpus(
                        {self.corpus_word_id: self._word_id,
                        self.corpus_file_id: self._file_id,
                        self.corpus_source_id: self._source_id})

                #if new_sentence:
                    #self._sentence_id = self.table_get(self.sentence_table,
                        #{self.sentence_source_id: self._source_id})

    def xml_process_content(self, element_text):
        """ In ICE-NG, the XML elements contain rows of words. This method 
        processes these rows, and creates token entries in the corpus table. 
        It also creates new entries in the word table if necessary."""
        if element_text:
            self.process_text(element_text)

    def xml_process_tail(self, element_tail_text):
        if element_tail_text:
            self.process_text(element_tail_text)
        
    def xml_get_meta_information(self, root):
        meta = root.find("meta")

        try:
            self._value_source_date = meta.find("date").text.strip().split("\t")[0]
        except AttributeError:
            self._value_source_date = ""
        self._value_source_date = self._value_source_date.strip().strip("-")
        
        if self._value_source_date in ["TODO"]:
            self._value_source_date = ""

        try:
            self._value_source_place = meta.find("place").text.strip().split("\t")[0]
        except AttributeError:
            self._value_source_place = ""
            
        author = meta.find("author")

        try:
            self._value_source_gender = author.find("gender").text.strip().split("\t")[0]
        except AttributeError:
            self._value_source_gender = ""
        try:
            self._value_source_age = author.find("age").text.strip().split("\t")[0]
        except AttributeError:
            self._value_source_gage = ""
        try:
            self._value_source_ethnicity = author.find("ethnic-group").text.strip().split("\t")[0]
            self._value_source_ethnicity = self._value_source_ethnicity.strip("/")
            
        except AttributeError:
            self._value_source_ethnicity = ""

        # get text category, based on filename (see ICE-NG documentation):
        self._value_source_icetext, self._value_source_icetextcode = self._get_ice_text_category(self._current_file)
        
        # currently, only the written component is used:
        self._value_source_mode = "written"

        # all meta data gathered, store it:
        self._source_id = self.table(self.source_table).get_or_insert(
            {self.source_age: self._value_source_age,
             self.source_gender: self._value_source_gender,
             self.source_ethnicity: self._value_source_ethnicity,
             self.source_date: self._value_source_date,
             self.source_mode: self._value_source_mode,
             self.source_icetext: self._value_source_icetext,
             self.source_icetextcode: self._value_source_icetextcode,
             self.source_place: self._value_source_place})
                
    def _get_ice_text_category(self, file_name):
        """
        Retrieve the ICE text category for the file.
        
        The ICE-Nigeria documentation contains a list that maps the file
        names used in the corpus to ICE text categories. This list is used
        here to return a tuple with the description and the code as values.
        
        Parameters
        ----------
        file_name : string
            The name of the file
            
        Returns
        -------
        tup : tuple
            A tuple containing two strings: first, the description of the 
            category, second, the ICEtext category code.
        """
        
        mapping = {
            "ahum": ("Academic writing humanities", "W2A"),
            "ansc": ("Academic writing natural sciences", "W2A"),
            "assc": ("Academic writing social sciences", "W2A"),
            "atec": ("Academic writing technical", "W2A"),
            "adm":  ("Administrative/instructive writing", "W2D"),
            "bl":   ("Business letters", "W1B"),
            "ed":   ("Editorials", "W2E"),
            "ex":   ("Exams", "W1A"),
            "nov":  ("Novels", "W2F"),
            "phum": ("Popular writing humanities", "W2B"),
            "pnsc": ("Popular writing natural sciences", "W2B"),
            "pssc": ("Popular writing social sciences", "W2B"),
            "ptec": ("Popular writing technology", "W2B"),
            "pr":   ("Press reportage", "W2C"),
            "skho": ("Instructive writing/skills and hobbies", "W2D"),
            "sl":   ("Social letters", "W1B"),
            "ess":  ("Students essays", "W1A")}
        
        name = os.path.split(file_name)[1].lower()
        desc, code = mapping[name.partition("_")[0]]
        return desc, code
    
    def process_xml_file(self, current_file):
        """ Reads an XML file."""

        # There are a few errors in the XML files that are fixed in this 
        # method.
        #
        # First, if the lemma of the word is unknown, the non-conforming XML
        # tag '<unknown>' is used in the files. The fix is that in such a
        # case, the value of the first column (i.e. the orhtographic word) 
        # is copied to the last column (i.e. the lemma).
        #
        # Second, HTML entities (e.g. &quot;) are malformed. They are placed
        # in two lines, the first starting with the ampersand plus the name,
        # teh second line containing the closing semicolon.
        #
        # Third, sometimes the opening XML tag is fed into the POS tagger,
        # with disastrous results, e.g. from Pr_54.xml.pos, line 235:
        #
        #    <error  NN  <unknown>
        #    corrected=  NN  <unknown>
        #    "   ''  "
        #    &quot   NN  <unknown>
        #    ;   :   ;
        #    ."> JJ  <unknown>
        #    &quot   NN  <unknown>
        #    ;   :   ;
        #    </error>
        #
        # This is fixed by a hack: a line that contains more '<' than '>'
        # is considered malformed. The first column of every following line
        # is concatenated to the content of the first column of the 
        # malformed line, up to the point where a line is encountered that
        # contains more '>' than '<'. After that line, the file is processed
        # normally. This hack transforms the malformed lines above into
        # a well-formed XML segment that corresponds to the content of 
        # Pr_54.xml:
        #
        #     <error corrected="&quot;.">
        #     &quot;   PUNCT   &quot;
        #     </error>

        
        self._current_file = current_file

        file_buffer = StringIO()
        with codecs.open(current_file, "r", encoding = self.arguments.encoding) as input_file:
            skip = False
            fix_split_token = ""
            for i, line in enumerate(input_file):
                line = line.strip()
                if line.count("\t") == 2:
                    word, pos, lemma = line.split("\t")
                else:
                    word = line
                    pos = ""
                    lemma = ""
                
                # Some lines with only a semicolon in the word column are
                # left-overs from malformed HTML entities. Skip them if 
                # necessary:
                if word.strip() == ";" and skip:
                    skip = False
                else:                    
                    # HTML entities don't seem to be correctly encoded in 
                    # the POS files. Fix that:
                    if word.startswith("&") and not word.endswith(";"):
                        word = "{};".format(word)
                        pos = "PUNCT"
                        line = "{}\t{}\t{}".format(word, pos, lemma)
                        
                        # the next line will be skipped if it contains the
                        # trailing semicolon:
                        skip = True
                        
                    if not fix_split_token:
                        # if there are more opening brackets than closing
                        # brackets in a line, we may be dealing with a split
                        # XML token:
                        if line.count("<") != line.count(">") and line.find("\t") > -1:
                            fix_split_token = word + " "
                            
                        # '<unknown>' is not a valid XML tag:
                        if lemma == "<unknown>":
                            line = "{}\t{}\t{}".format(word, pos, word)
                    else:
                        # Fix split tokens by looking for a line with more
                        # closing brackets than opening brackets:
                        if line.count(">") > line.count("<"):
                            if fix_split_token.endswith('"'):
                                if (fix_split_token.count('"') % 2):
                                    line = "".join([fix_split_token, word])
                                else:
                                    line = " ".join([fix_split_token, word])
                            else:
                                line = "".join([fix_split_token, word])
                            fix_split_token = ""
                        else:
                            if word.startswith("'") > 0:
                                if fix_split_token.count("'") % 2:
                                    fix_split_token = "".join([fix_split_token, word])
                                else:
                                    fix_split_token = " ".join([fix_split_token, word])
                            elif word.startswith('"') > 0:
                                if fix_split_token.count('"') % 2:
                                    fix_split_token = "".join([fix_split_token, word])
                                else:
                                    fix_split_token = " ".join([fix_split_token, word])
                            else:
                                if fix_split_token.endswith('"'):
                                    
                                    if (fix_split_token.count('"') % 2):
                                        fix_split_token = "".join([fix_split_token, word])
                                    else:
                                        fix_split_token = " ".join([fix_split_token, word])
                                else:
                                    fix_split_token = "".join([fix_split_token, word])
                    if fix_split_token:
                        pass
                    else:
                        # The file buffer uses byte-strings, not unicode 
                        # strings. Therefore, encode the string first:
                        #file_buffer.write(line.encode("utf-8"))
                        #file_buffer.write("\n")
                        try:
                            file_buffer.write(line)
                        except UnicodeEncodeError:
                            file_buffer.write(line.encode("utf-8"))
                            
                        file_buffer.write("\n")
                        last = line

        S = file_buffer.getvalue()

        e = self.xml_parse_file(StringIO(S))
        self.xml_get_meta_information(e)
        self.xml_process_element(self.xml_get_body(e))
        
    def xml_get_body(self, root):
        return root.find("text")
        
    def process_file(self, current_file):
        # Process every file except for bl_18a.xml.pos. This file only 
        # contains unimportant meta information:
        if current_file.lower().find("bl_18a.xml.pos") == -1:
            self.process_xml_file(current_file)

    def get_file_identifier(self, path):
        _, base = os.path.split(path)
        while "." in base:
            base, _= os.path.splitext(base)
        return base.lower()

    @staticmethod
    def _replace_encoding_errors(s):
        """
        Replace erroneous character sequences by the correct character
        
        Unfortunately, some data files in ICE-NG have corrput character 
        encodings, which can limit the usefulness of the corpus data. This
        function attempts to reverse the faulty encoding by replacing any
        character sequence that appears to be the result of an encdoing 
        error by the character that was probably intended.
        
        Parameters
        ----------
        s : string
            The character string
            
        Returns
        -------
        s : string
            The input string with known encoding errors fixed.
        """
        
        # apparently, the character sequence â marks any faulty encoding,
        # and the next character is the actual encoding error. The problem
        # is that in ICE_NG, this three-character sequence can be split up
        # into two 'words', e.g. for the dash in Pr_13.txt, line 36 
        # ('hereas others – notably top officials'). In Pr_13.xml.pos, this
        # dash is represented in two separate rows in lines 381-382.
        
        # My solution is to find the two-character marker and replace it by
        # an empty string. Then, the next character is replaced, using the
        # lookup table.
        # The installer has to check, then, if the string is empty after
        # replacement. If so, it should discard the current line.
        
        # CHECK CHARACTERS after 'i' in ATec_01.xml.pos, ATec_06.xml.pos
        
        replace_list = [
            ("â", "‘"),
            ("â", "’"),

            ("â", "“"),
            ("â", "”"),

            ("â", "–"),
            
            ("Â°", "°"),
            ("Â·", "·"),

            ("Ã ", "à"),
            ("Ãš", "è"),
            ("Ã¬", "ì"),
            ("Ã²", "ò"),
            
            ("Ä", "ĕ"),

            ("Ã©", "é"),
            ("Ã­", "í"),
            ("Ãº", "ú"),

            ("Ã€", "ä"),
            
            ("Ã", "Ì"),
            
            ("Ã±", "ñ"),

            ("Ê€", "ʤ"),
            
            ("Î¼", "μ"),
            ("â", "∆"),
            ]
        corrupt_replace_list = [
            ("", "’"),
            ("", "–"),
        ]
        for old, new in replace_list:
            s = s.replace(old, new)

        for old, new in corrupt_replace_list:
            s = s.replace(old.replace("â", ""), new)
            
        return s

    @staticmethod
    def get_name():
        return "ICE_US"

    @staticmethod
    def get_db_name():
        return "ice_us"

    @staticmethod
    def get_language():
        return "English"
    
    @staticmethod
    def get_language_code():
        return "en-US"
        
    @staticmethod
    def get_title():
        return "International Corpus of English – USA"

    @staticmethod
    def get_description():
        return [
            "The International Corpus of English – USA is a member of the ICE family of English corpora. It contains approximately 460.000 tokens of spoken US-American English."]

    @staticmethod
    def get_license():
        return "ICE USA is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike license (<a href='https://creativecommons.org/licenses/by-nc-sa/3.0/'>CC BY-NC-SA 3.0</a> DE)."
        
    @staticmethod
    def get_references():
        return [str(Article(
                authors=PersonList(
                    Person(first = "Eva-Maria", last = "Wunder"), 
                    Person(first = "Holger", last = "Voormann"), 
                    Person(first = "Ulrike", last = "Gut")), 
                title = "The ICE Nigeria corpus project: Creating an open, rich and accurate corpus",
                year = 2009,
                journal = "ICAME Journal",
                volume = 34,
                pages = "78-88"))]

    @staticmethod
    def get_url():
        return "http://ice-corpora.net/ice/index.htm"
    
if __name__ == "__main__":
    BuilderClass().build()

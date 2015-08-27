from __future__ import unicode_literals 

import cProfile
from corpusbuilder import *
import xml.etree
import re

class BNCBuilder(BaseCorpusBuilder):
    def __init__(self):
       # all corpus builders have to call the inherited __init__ function:
        super(BNCBuilder, self).__init__()
        
        # Read only .words files from the corpus path:
        self.file_filter = "*.xml"
        
        # specify which features are provided by this corpus and lexicon:
        self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_POS"]
        self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_SOURCE"]
        self.documentation_url = 'http://www.natcorp.ox.ac.uk/'
        
        
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
        # id
        # An int value containing the unique identifier of the token
        #
        # Entity_id
        # An int value containing the unique identifier of the lexicon
        # entry associated with this token.
        #
        # Source_id
        # An int value containing the unique identifier of the source that
        # contains this token.
        #
        # Speaker_id
        # An int value containing the unique identifier of the speaker who
        # produced this token. It is zero for written texts.
        #
        # Sentence_id
        # An int value containing the unique identifier of the sentence 
        # that contains this token.
        
        self.corpus_table = "corpus"
        self.corpus_id = "Token_id"
        self.corpus_word_id = "Word_id"
        self.corpus_source_id = "Source_id"
        self.corpus_speaker_id = "Speaker_id"
        self.corpus_sentence_id = "Sentence_id"

        self.add_table_description(self.corpus_table, self.corpus_id,
            {"CREATE": [
                "`{}` INT(9) UNSIGNED NOT NULL".format(self.corpus_id),
                "`{}` INT(9) UNSIGNED NOT NULL".format(self.corpus_sentence_id),
                "`{}` MEDIUMINT(7) UNSIGNED DEFAULT 0".format(self.corpus_speaker_id),
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.corpus_word_id),
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.corpus_source_id)],
            "INDEX": [  
                ([self.corpus_word_id], 0, "HASH"),
                ([self.corpus_speaker_id], 0, "HASH"),
                ([self.corpus_sentence_id], 0, "HASH"),
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
        # Lemma
        # A text value containing the unique identifier of the lemma that
        # is associated with this word-form.
        # 
        # C5
        # A text value containing the part-of-speech label of this 
        # word-form.
        #
        # Type
        # An enum containing the type of the token.

        self.word_table = "words"
        self.word_id = "Word_id"
        self.word_label = "Word"
        self.word_lemma = "Lemma"
        self.word_pos = "C5_POS"
        self.word_lemma_pos = "Lemma_POS"
        self.word_type = "Type"

        self.add_table_description(self.word_table, self.word_id,
            {"CREATE": [
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.word_id),
                "`{}` VARCHAR(133) NOT NULL".format(self.word_label),
                "`{}` ENUM('AJ0','AJ0-AV0','AJ0-NN1','AJ0-VVD','AJ0-VVG','AJ0-VVN','AJC','AJS','AT0','AV0','AV0-AJ0','AVP','AVP-PRP','AVQ','AVQ-CJS','CJC','CJS','CJS-AVQ','CJS-PRP','CJT','CJT-DT0','CRD','CRD-PNI','DPS','DT0','DT0-CJT','DTQ','EX0','ITJ','NN0','NN1','NN1-AJ0','NN1-NP0','NN1-VVB','NN1-VVG','NN2','NN2-VVZ','None','NP0','NP0-NN1','ORD','PNI','PNI-CRD','PNP','PNQ','PNX','POS','PRF','PRP','PRP-AVP','PRP-CJS','PUL','PUN','PUQ','PUR','TO0','UNC','VBB','VBD','VBG','VBI','VBN','VBZ','VDB','VDD','VDG','VDI','VDN','VDZ','VHB','VHD','VHG','VHI','VHN','VHZ','VM0','VVB','VVB-NN1','VVD','VVD-AJ0','VVD-VVN','VVG','VVG-AJ0','VVG-NN1','VVI','VVN','VVN-AJ0','VVN-VVD','VVZ','VVZ-NN2','XX0','ZZ0')".format(self.word_pos),
                "`{}` ENUM('c','gap','pause','vocal','w')".format(self.word_type),
                "`{}` VARCHAR(131) NOT NULL".format(self.word_lemma),
                "`{}` ENUM('ADJ','ADV','ART','CONJ','INTERJ','PREP','PRON','SUBST','UNC','VERB', 'PUNCT')".format(self.word_lemma_pos)],
             "INDEX": [
                ([self.word_lemma], 0, "HASH"),
                ([self.word_label], 0, "BTREE"),
                ([self.word_lemma_pos], 0, "HASH"),
                ([self.word_pos], 0, "BTREE")]})

        self.add_new_table_description(self.word_table,
            [Primary(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(133) NOT NULL"),
             Column(self.word_lemma, "VARCHAR(133) NOT NULL"),
             Column(self.word_pos, "ENUM('AJ0','AJ0-AV0','AJ0-NN1','AJ0-VVD','AJ0-VVG','AJ0-VVN','AJC','AJS','AT0','AV0','AV0-AJ0','AVP','AVP-PRP','AVQ','AVQ-CJS','CJC','CJS','CJS-AVQ','CJS-PRP','CJT','CJT-DT0','CRD','CRD-PNI','DPS','DT0','DT0-CJT','DTQ','EX0','ITJ','NN0','NN1','NN1-AJ0','NN1-NP0','NN1-VVB','NN1-VVG','NN2','NN2-VVZ','None','NP0','NP0-NN1','ORD','PNI','PNI-CRD','PNP','PNQ','PNX','POS','PRF','PRP','PRP-AVP','PRP-CJS','PUL','PUN','PUQ','PUR','TO0','UNC','VBB','VBD','VBG','VBI','VBN','VBZ','VDB','VDD','VDG','VDI','VDN','VDZ','VHB','VHD','VHG','VHI','VHN','VHZ','VM0','VVB','VVB-NN1','VVD','VVD-AJ0','VVD-VVN','VVG','VVG-AJ0','VVG-NN1','VVI','VVN','VVN-AJ0','VVN-VVD','VVZ','VVZ-NN2','XX0','ZZ0')"),
             Column(self.word_lemma_pos, "ENUM('ADJ','ADV','ART','CONJ','INTERJ','PREP','PRON','SUBST','UNC','VERB', 'PUNCT')"),
             Column(self.word_type, "ENUM('c','gap','pause','vocal','w')")])

        # Add the file table. Each row in this table represents an XML file
        # that has been incorporated into the corpus. Each token from the
        # corpus table is linked to exactly one file from this table, and
        # more than one token may be linked to each file in this table.
        # The table contains the following columns:
        #
        # id
        # An int value containing the unique identifier of this file.
        # 
        # Filename
        # A text value containing the path that points to this XML file.
        
        self.file_table = "files"
        self.file_id = "File_id"
        self.file_name = "Filename"
        self.file_path = "Path"

        self.add_table_description(self.file_table, self.file_id,
            {"CREATE": [
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.file_id),
                "`{}` TINYTEXT NOT NULL".format(self.file_path),
                "`{}` TINYTEXT NOT NULL".format(self.file_name)]})

        self.add_new_table_description(self.file_table,
            [Primary(self.file_id, "SMALLINT(4) UNSIGNED NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL"),
             Column(self.file_name, "TINYTEXT NOT NULL")])

        # Add the speaker table. Each row in this table represents a speaker
        # who has contributed to the recordings in the BNC. Each sentence
        # from a spoken text is linked to exactly one speaker from this
        # table, and more than one sentence may be linked to each speaker.
        # The table contains the following columns:
        #
        # id
        # A string value containing the label used in the BNC to refer to 
        # this speaker. It is used in the who attributes of the XML <u> 
        # elements as well as the xml:id attribute of the <person> element 
        # in the the profile description statement.
        #
        # Age
        # An string value containing the age of the speaker, taken from the 
        # <age> element within the <person> element if present, otherwise
        # from the age attribute of the <person> element if present, or 
        # empty otherwise.
        # 
        # Sex
        # A string value containing the sex of the speaker, taken from the 
        # sex attribute of the <person> element if present, or empty 
        # otherwise.
        
        self.speaker_table = "speaker"
        self.speaker_id = "Speaker_id"
        self.speaker_label = "Speaker"
        self.speaker_age = "Age"
        self.speaker_sex = "Sex"
        
        self.add_table_description(self.speaker_table, self.speaker_id,
            {"CREATE": [
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.speaker_id),
                "`{}` TINYTEXT NOT NULL".format(self.speaker_label),
                "`{}` ENUM('-82+','0','1','10','10+','11','12','13','13+','14','14+','15','16','17','17+','18','19','2','20','20+','21','21+','22','23','24','25','25+','26','27','28','29','3','3+','30','30+','31','32','33','34','35','35+','36','37','38','39','4','40','40+','41','42','43','44','45','45+','46','46+','47','48','48+','49','5','50','50+','51','52','53','54','55','55+','56','57','58','59','6','60','60+','61','62','63','64','65','65+','66','67','68','69','7','70','70+','71','72','73','74','75','75+','76','77','78','79','8','80','80+','81','82','84','86','87','89','9','92','93','95','unknown')".format(self.speaker_age),
                "`{}` ENUM('f','m','u')".format(self.speaker_sex)],
            "INDEX": [
                ([self.speaker_age], 0, "HASH"),
                ([self.speaker_label], 0, "HASH"),
                ([self.speaker_sex], 0, "HASH")]})
        
        self.add_time_feature(self.speaker_age)
        
        self.add_new_table_description(self.speaker_table,
            [Primary(self.speaker_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.speaker_label, "TINYTEXT NOT NULL"),
             Column(self.speaker_age, "ENUM('-82+','0','1','10','10+','11','12','13','13+','14','14+','15','16','17','17+','18','19','2','20','20+','21','21+','22','23','24','25','25+','26','27','28','29','3','3+','30','30+','31','32','33','34','35','35+','36','37','38','39','4','40','40+','41','42','43','44','45','45+','46','46+','47','48','48+','49','5','50','50+','51','52','53','54','55','55+','56','57','58','59','6','60','60+','61','62','63','64','65','65+','66','67','68','69','7','70','70+','71','72','73','74','75','75+','76','77','78','79','8','80','80+','81','82','84','86','87','89','9','92','93','95','unknown')"),
             Column(self.speaker_sex, "ENUM('f','m','u')")])
       
        # Add the sentence table. Each row in this table represents a 
        # sentence from the XML file. Each token in the corpus table is 
        # linked to exactly one sentence from this table, and more than one
        # tokens may be linked to each sentence. The table contains the 
        # following columns:
        #
        # id
        # An int value containing the unique identifier of this file.

        self.sentence_table = "sentence"
        self.sentence_id = "Sentence_id"

        self.add_table_description(self.sentence_table, self.sentence_id,
            {"CREATE": [
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.sentence_id)]})

        self.add_new_table_description(self.sentence_table,
            [Primary(self.sentence_id, "SMALLINT(4) UNSIGNED NOT NULL")])

        # Add the source table. Each row in this table represents a BNC 
        # source. Each sentence from the sentence table is linked to exactly
        # one source from this table, and more than one sentences may be
        # linked to each source. The table contains the following columns:
        #
        # id
        # An int value containing the unique identifier of this source.
        # 
        # XMLName
        # A string value that contains the three-letter identifier
        # of the XML file (e.g. F00). This value is taken from the <idno>
        # element with type "bnc" from the publication statement in the XML
        # file description component.
        # 
        # OldName
        # A string value that contains the label used in early BNC releases
        # to identify the source. This value is taken from the <idno>
        # element with type "old" from the publication statement in the XML
        # file description component.
        #
        # Type
        # An enum value that contains the text type, taken from the type 
        # attribute of the <wtext> and <stext> elements in the XML file.
        #
        # Class
        # A text value that contains the genre classification code, taken
        # from the <classCode scheme="DLEE"> element in the <textClass>
        # section of the XML profile description component.
        #
        # Date
        # A text value that contains the year in which the text was created,
        # taken from the date attribute of the <creation> element in the XML
        # profile description component, or from a <date> element within
        # this <creation> element.
        #
        # File_id
        # An int value containing the unique identifier of the file that 
        # this source is read from.
        
        self.source_table = "texts"
        self.source_id = "Source_id"
        self.source_xmlname = "XMLName"
        self.source_oldname = "OldName"
        self.source_genre = "Type"
        self.source_class = "Class"        
        self.source_year = "Date"
        self.source_file_id = "File_id"
        
        self.add_table_description(self.source_table, self.source_id,
            {"CREATE": [
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.source_id),
                "`{}` CHAR(3) NOT NULL".format(self.source_xmlname),
                "`{}` CHAR(6) NOT NULL".format(self.source_oldname),
                "`{}` ENUM('ACPROSE','CONVRSN','FICTION','NEWS','NONAC','OTHERPUB','OTHERSP','UNPUB') NOT NULL".format(self.source_genre),
                "`{}` ENUM('S brdcast discussn','S brdcast documentary','S brdcast news','S classroom','S consult','S conv','S courtroom','S demonstratn','S interview','S interview oral history','S lect commerce','S lect humanities arts','S lect nat science','S lect polit law edu','S lect soc science','S meeting','S parliament','S pub debate','S sermon','S speech scripted','S speech unscripted','S sportslive','S tutorial','S unclassified','W ac:humanities arts','W ac:medicine','W ac:nat science','W ac:polit law edu','W ac:soc science','W ac:tech engin','W admin','W advert','W biography','W commerce','W email','W essay school','W essay univ','W fict drama','W fict poetry','W fict prose','W hansard','W institut doc','W instructional','W letters personal','W letters prof','W misc','W news script','W newsp brdsht nat: arts','W newsp brdsht nat: commerce','W newsp brdsht nat: editorial','W newsp brdsht nat: misc','W newsp brdsht nat: report','W newsp brdsht nat: science','W newsp brdsht nat: social','W newsp brdsht nat: sports','W newsp other: arts','W newsp other: commerce','W newsp other: report','W newsp other: science','W newsp other: social','W newsp other: sports','W newsp tabloid','W nonAc: humanities arts','W nonAc: medicine','W nonAc: nat science','W nonAc: polit law edu','W nonAc: soc science','W nonAc: tech engin','W pop lore','W religion') NOT NULL".format(self.source_class),
                "`{}` VARCHAR(21) NOT NULL".format(self.source_year),
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.source_file_id)],
            "INDEX": [
                ([self.source_genre], 0, "HASH"),
                ([self.source_xmlname], 0, "HASH"),
                ([self.source_oldname], 0, "HASH"),
                ([self.source_class], 0, "HASH"),
                ([self.source_file_id], 0, "HASH"),
                ([self.source_year], 0, "BTREE")]})

        self.add_time_feature(self.source_year)
            
        self.add_new_table_description(self.source_table,
            [Primary(self.source_id, "SMALLINT(4) UNSIGNED NOT NULL"),
             Column(self.source_xmlname, "CHAR(3) NOT NULL"),
             Column(self.source_oldname, "CHAR(6) NOT NULL"),
             Column(self.source_genre, "ENUM('ACPROSE','CONVRSN','FICTION','NEWS','NONAC','OTHERPUB','OTHERSP','UNPUB') NOT NULL"),
             Column(self.source_class, "ENUM('S brdcast discussn','S brdcast documentary','S brdcast news','S classroom','S consult','S conv','S courtroom','S demonstratn','S interview','S interview oral history','S lect commerce','S lect humanities arts','S lect nat science','S lect polit law edu','S lect soc science','S meeting','S parliament','S pub debate','S sermon','S speech scripted','S speech unscripted','S sportslive','S tutorial','S unclassified','W ac:humanities arts','W ac:medicine','W ac:nat science','W ac:polit law edu','W ac:soc science','W ac:tech engin','W admin','W advert','W biography','W commerce','W email','W essay school','W essay univ','W fict drama','W fict poetry','W fict prose','W hansard','W institut doc','W instructional','W letters personal','W letters prof','W misc','W news script','W newsp brdsht nat: arts','W newsp brdsht nat: commerce','W newsp brdsht nat: editorial','W newsp brdsht nat: misc','W newsp brdsht nat: report','W newsp brdsht nat: science','W newsp brdsht nat: social','W newsp brdsht nat: sports','W newsp other: arts','W newsp other: commerce','W newsp other: report','W newsp other: science','W newsp other: social','W newsp other: sports','W newsp tabloid','W nonAc: humanities arts','W nonAc: medicine','W nonAc: nat science','W nonAc: polit law edu','W nonAc: soc science','W nonAc: tech engin','W pop lore','W religion') NOT NULL"),
             Column(self.source_year, "VARCHAR(21) NOT NULL"),
             Link(self.source_file_id, self.file_table)])

        self.add_new_table_description(self.corpus_table, 
            [Primary(self.corpus_id, "INT(9) UNSIGNED NOT NULL"),
             Link(self.corpus_sentence_id, self.sentence_table),
             Link(self.corpus_speaker_id, self.speaker_table),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_source_id, self.source_table)])


    
    def get_node_value(self, node):
        """ Retrieve the text stored in the node. Some element types store
        the text as an attribute, and are otherwise empty. This method will
        return that text anyway."""
        
        # words <w> and punctuations <c> have their value stored in their 
        # text:
        if node.tag in ("w", "c"):
            try:
                return node.text.strip()
            except AttributeError:
                return ""
            
        # vocal nodes <vocal> and text gap nodes <gap> have their value 
        # in the desc attribute:
        if node.tag in ("vocal", "gap"):
            return node.attrib.get("desc", "").strip()
        
        # pause nodes <pause> have their duration in the dur attribute:
        if node.tag == "pause":
            return node.attrib.get("dur", "").strip()
    
    def xml_preprocess_tag(self, element):
        element._tagged = False
        tag = element.tag
        # <u> is an utterance. This element has a who attribute that 
        # specifies the speaker of the utterance.
        if tag == "u":
            lookup = self.table_find(
                self.speaker_table, 
                {self.speaker_label: element.attrib["who"].strip()})
            if lookup:
                self._speaker_id = lookup[self.speaker_id]
            else:
                self._speaker_id = self.table_get(
                    self.speaker_table,
                    {self.speaker_label: element.attrib["who"].strip()})
        # <s> is a sentence:
        elif tag == "s":
            self._sentence_id = self.table_get(self.sentence_table, {})
        
        #other supported elements:
        elif tag in ("w", "vocal", "c", "gap", "pause"):
            word_text = self.get_node_value(element)
            lemma_text = ""
            lemma_pos = "UNC"
            
            if tag == "w":
                lemma_text = element.attrib.get("hw", "").strip()
                lemma_pos = element.attrib.get("pos", "").strip()
            if tag == "c":
                lemma_text = word_text
                lemma_pos = "PUNCT"
            word_pos = element.attrib.get("c5", "").strip()
            
            if tag not in ("w", "c"):
                word_pos = "UNC"
                
            # get word_id that matches current token (a new one is created
            # if necessary:
            self._word_id = self.table_get(self.word_table, 
                {self.word_label: word_text, 
                 self.word_lemma: lemma_text, 
                 self.word_lemma_pos: lemma_pos,
                 self.word_pos: word_pos, 
                 self.word_type: tag}, case=True)
            
            # store the new token with all needed information:
            self.add_token_to_corpus({self.corpus_word_id: self._word_id,
                         self.corpus_speaker_id: self._speaker_id,
                         self.corpus_sentence_id: self._sentence_id,
                         self.corpus_source_id: self._source_id})
            #self._corpus_id = self.table_add(self.corpus_table,
                        #{self.corpus_word_id: self._word_id,
                         #self.corpus_speaker_id: self._speaker_id,
                         #self.corpus_sentence_id: self._sentence_id,
                         #self.corpus_source_id: self._source_id})
        else:
            if element.text or list(element):
                self.tag_next_token(element.tag, element.attrib)
                element._tagged = True
            else:
                self.add_empty_tag(element.tag, element.attrib)
                
    def xml_postprocess_tag(self, element):
        if element._tagged:
            self.tag_last_token(element.tag, element.attrib)
    
    def get_speaker_data(self, *args):
        person = args[0]
        if person.tag == "person":
            sex = person.attrib.get("sex", "unknown")
            if person.find("age") != None:
                age = person.find("age").text.strip()
            else:
                age = person.attrib.get("age", "unknown")
            
            # During parsing of the XML tree, the attribute "xml:id" is
            # interpreted as a qualified name (which it probably isn't).
            # Thus, the 'xml' part is replaced by the namespace, which for
            # XML files like those in the BNC is apparently
            # http://www.w3.org/XML/1998/namespace
            # Thus, in order to get the speaker identifier, we have to look
            # for {http://www.w3.org/XML/1998/namespace}id instead.
            xml_id = person.attrib.get("{http://www.w3.org/XML/1998/namespace}id", "unknown")
        return [xml_id, age, sex]

    def xml_get_meta_info(self, root):
        """ Parse XML root so that any meta information that should be 
        retrieved from the XML tree is stored adequately in the corpus
        tables.
        
        This method should evaluate the content of 
        
        <teiHeader>
            <fileDesc>
                <extent>6688 tokens; 6708 w-units; 423 s-units</extent>
            </fileDesc>
        </teiHeader> 
        
        to ensure that the whole file is correctly processed.
        
        Alternatively, it should use the detailed usage information from 
        <teiHeader><
            encodingDesc>
                <tagsDecl>
                    <namespace name="">
                        <tagUsage gi="c" occurs="810" />
                        ...

        """
        def get_year(S):
            match = re.match("(\d\d\d\d)", S)
            if match:
                return match.group(1)
            else:
                return S
        
        header = root.find("teiHeader")
        file_desc = header.find("fileDesc")
        encoding_desc = header.find("encodingDesc")
        profile_desc = header.find("profileDesc")
        revision_desc = header.find("revisionDesc")
        
        # Get the date:
        creation = profile_desc.find("creation")
        date_element = creation.find("date")
        if date_element != None:
            source_date = get_year(date_element.text.strip())
        else:
            source_date = get_year(creation.attrib.get("date", "0000"))
                
        # Get XMLName and OldName:
        for idno in file_desc.find("publicationStmt").findall("idno"):
            if idno.attrib["type"] == "bnc":
                source_xmlname = idno.text.strip()
            else:
                source_oldname = idno.text.strip()
        
        body = self.xml_get_body(root)
        
        # Get the text classification string:
        source_type = body.attrib.get("type")
        for class_code in profile_desc.find("textClass").findall("classCode"):
            if class_code.attrib.get("scheme") == "DLEE":
                source_class = class_code.text.strip()

        # Find all speakers, and if there are some, make sure that they are
        # stored in the speaker table:
        participant_desc = profile_desc.find("particDesc")
        if participant_desc != None:
            for person in participant_desc.findall("person"):
                speaker_label, speaker_age, speaker_sex = self.get_speaker_data(person)
                self.table_get(self.speaker_table,
                    {self.speaker_label: speaker_label,
                        self.speaker_age: speaker_age,
                        self.speaker_sex: speaker_sex})
        # Initially, there is no speaker. It is set for each <u> element. In
        # written texts, no <u> elements occur, so the variable remains 
        # empty.
        self._speaker_id = 0
        
        # Get a valid source id for this text. If it isn't in the source 
        # table yet, store it as a new entry:
        self._source_id = self.table_get(self.source_table, 
            {self.source_xmlname: source_xmlname, 
             self.source_oldname: source_oldname, 
             self.source_genre: source_type, 
             self.source_class: source_class, 
             self.source_year: source_date, 
             self.source_file_id: self._file_id})
        
    def xml_get_body(self, root):
        """ Obtain either the <wtext> element for written or the <stext> 
        element for spoken texts from the root."""
        
        body = root.find("wtext")
        if body == None:
            body = root.find("stext")
        if body == None:
            logger.warning("Neither <wtext> nor <stext> found in file, not processed.")
        return body

    def process_file(self, current_file):
        """ Process an XML file, and insert all relevant information into
        the corpus."""
        e = self.xml_parse_file(current_file)
        self.xml_get_meta_info(e)
        self.xml_process_element(self.xml_get_body(e))

def main():
    BNCBuilder().build()

if __name__ == "__main__":
    main()
    #cProfile.run("main()", sort=1)
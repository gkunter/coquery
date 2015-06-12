from __future__ import unicode_literals 

import corpusbuilder
import xml.etree
import re

class corpus_code():
    def get_source_info_header(self):
        return [
            self.resource.source_genre,
            self.resource.source_year,
            self.resource.source_oldname]
    
    def sql_string_get_file_info(self, source_id):
        return "SELECT {text_table}.{text} AS XMLName, {file_table}.{file_name} AS Filename FROM {sentence_table}, {text_table}, {file_table} WHERE {sentence_table}.{sentence_id} = {this_id} AND {sentence_table}.{sentence_text} = {text_table}.{text_id} AND {text_table}.{text_file_id} = {file_table}.{file_id}".format(
            text_table=self.resource.source_table_name,
            text=self.resource.source_label,
            file_table=self.resource.file_table,
            file_name=self.resource.file_label,
            sentence_table=self.resource.sentence_table,
            sentence_id=self.resource.sentence_id,
            this_id=source_id,
            sentence_text=self.resource.sentence_text_id,
            text_id=self.resource.source_id,
            text_file_id=self.resource.source_file_id,
            file_id=self.resource.file_id)
        
    def get_file_info_header(self):
        return [
            self.resource.source_label,
            self.resource.file_label]
 
class BNCBuilder(corpusbuilder.BaseCorpusBuilder):
    def __init__(self):
       # all corpus builders have to call the inherited __init__ function:
        super(BNCBuilder, self).__init__()
        
        # Read only .words files from the corpus path:
        self.file_filter = "*.xml"
        
        # specify which features are provided by this corpus and lexicon:
        self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_POS"]
        self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_SOURCE"]
        
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
        # Sentence_id
        # An int value containing the unique identifier of the sentence 
        # that contains this token.
        
        self.corpus_table = "element"
        self.corpus_token_id = "id"
        self.corpus_word_id = "Entity_id"
        self.corpus_source_id = "Sentence_id"

        self.add_table_description(self.corpus_table, self.corpus_token_id,
            {"CREATE": [
                "`{}` int(9) UNSIGNED NOT NULL".format(self.corpus_token_id),
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.corpus_word_id),
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.corpus_source_id)],
            "INDEX": [  
                ([self.corpus_word_id], 0, "HASH"),
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
        # Lemma_id
        # An int value containing the unique identifier of the lemma that
        # is associated with this word-form.
        # 
        # C5
        # A text value containing the part-of-speech label of this 
        # word-form.
        #
        # Type
        # An enum containing the type of the token.

        self.word_table = "entity"
        self.word_id = "id"
        self.word_label = "Text"
        self.word_lemma_id = "Lemma_id"
        self.word_pos_id = "C5"
        self.word_type = "Type"

        self.add_table_description(self.word_table, self.word_id,
            {"CREATE": [
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.word_id),
                "`{}` VARCHAR(133) NOT NULL".format(self.word_label),
                "`{}` MEDIUMINT(6) UNSIGNED".format(self.word_lemma_id),
                "`{}` ENUM('AJ0','AJ0-AV0','AJ0-NN1','AJ0-VVD','AJ0-VVG','AJ0-VVN','AJC','AJS','AT0','AV0','AV0-AJ0','AVP','AVP-PRP','AVQ','AVQ-CJS','CJC','CJS','CJS-AVQ','CJS-PRP','CJT','CJT-DT0','CRD','CRD-PNI','DPS','DT0','DT0-CJT','DTQ','EX0','ITJ','NN0','NN1','NN1-AJ0','NN1-NP0','NN1-VVB','NN1-VVG','NN2','NN2-VVZ','None','NP0','NP0-NN1','ORD','PNI','PNI-CRD','PNP','PNQ','PNX','POS','PRF','PRP','PRP-AVP','PRP-CJS','PUL','PUN','PUQ','PUR','TO0','UNC','VBB','VBD','VBG','VBI','VBN','VBZ','VDB','VDD','VDG','VDI','VDN','VDZ','VHB','VHD','VHG','VHI','VHN','VHZ','VM0','VVB','VVB-NN1','VVD','VVD-AJ0','VVD-VVN','VVG','VVG-AJ0','VVG-NN1','VVI','VVN','VVN-AJ0','VVN-VVD','VVZ','VVZ-NN2','XX0','ZZ0')".format(self.word_pos_id),
                "`{}` ENUM('c','gap','pause','vocal','w')".format(self.word_type)],
             "INDEX": [
                ([self.word_lemma_id], 0, "HASH"),
                ([self.word_label], 0, "BTREE"),
                ([self.word_pos_id], 0, "BTREE")]})

        # Add the lemma table. Each row in this table represents a lemma in
        # the lexicon. Each word-form from the lexicon table is linked to
        # exactly one lemma from this table, and more than one word-form
        # may be linked to each lemma in this table. The table has the 
        # following columns:
        #
        # id
        # An int value containing the unique identifier of this lemma.
        #
        # Text
        # A text value containing the orthographic representation of this
        # lemma.
        # 
        # Pos
        # A text value containing the word class of this lemma. Note that 
        # this value is not used in queries involving part-of-speech tags.
        # These queries use the POS label from the word-form table.

        self.lemma_table = "lemma"
        self.lemma_id = "id"
        self.lemma_label = "Text"
        self.lemma_pos_id = "Pos"
        
        self.add_table_description(self.lemma_table, self.lemma_id,
            {"CREATE": [
                "`{}` MEDIUMINT(6) UNSIGNED NOT NULL".format(self.lemma_id),
                "`{}` VARCHAR(131) NOT NULL".format(self.lemma_label),
                "`{}` ENUM('ADJ','ADV','ART','CONJ','INTERJ','PREP','PRON','SUBST','UNC','VERB', 'PUNCT')".format(self.lemma_pos_id)],
            "INDEX": [
                ([self.lemma_label], 0, "BTREE")]})

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
        
        self.file_table = "file"
        self.file_id = "id"
        self.file_label = "Filename"

        self.add_table_description(self.file_table, self.file_id,
            {"CREATE": [
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.file_id),
                "`{}` TINYTEXT NOT NULL".format(self.file_label)]})

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
        self.speaker_id = "id"
        self.speaker_age = "Age"
        self.speaker_sex = "Sex"
        
        self.add_table_description(self.speaker_table, self.speaker_id,
            {"CREATE": [
                "`{}` VARCHAR(8) NOT NULL".format(self.speaker_id),
                "`{}` ENUM('-82+','0','1','10','10+','11','12','13','13+','14','14+','15','16','17','17+','18','19','2','20','20+','21','21+','22','23','24','25','25+','26','27','28','29','3','3+','30','30+','31','32','33','34','35','35+','36','37','38','39','4','40','40+','41','42','43','44','45','45+','46','46+','47','48','48+','49','5','50','50+','51','52','53','54','55','55+','56','57','58','59','6','60','60+','61','62','63','64','65','65+','66','67','68','69','7','70','70+','71','72','73','74','75','75+','76','77','78','79','8','80','80+','81','82','84','86','87','89','9','92','93','95','unknown')".format(self.speaker_age),
                "`{}` ENUM('f','m','u')".format(self.speaker_sex)],
            "INDEX": [
                ([self.speaker_age], 0, "HASH"),
                ([self.speaker_sex], 0, "HASH")]})
       
        # Add the sentence table. Each row in this table represents a 
        # sentence from the XML file. Each token in the corpus table is 
        # linked to exactly one sentence from this table, and more than one
        # tokens may be linked to each sentence. The table contains the 
        # following columns:
        #
        # id
        # An int value containing the unique identifier of this file.
        #
        # Source_id
        # An int value containing the unique identifier of the text that
        # this sentence is linked to.
        #
        # Speaker_id
        # An text value containing the unique identifier of the speaker that
        # this sentence is linked to, taken from the who attribute of the
        # XML <u> element surrounding this sentence.

        self.sentence_table = "sentence"
        self.sentence_id = "id"
        self.sentence_source_id = "Source_id"
        self.sentence_speaker_id = "Speaker_id"

        self.add_table_description(self.sentence_table, self.sentence_id,
            {"CREATE": [
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.sentence_id),
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.sentence_source_id),
                "`{}` VARCHAR(8)".format(self.sentence_speaker_id)],
            "INDEX": [
                ([self.sentence_speaker_id], 0, "HASH")]})

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
        
        self.source_table = "text"
        self.source_table_alias = "SOURCETABLE"
        self.source_id = "id"
        self.source_info_label = "XMLName"
        self.source_info_oldname = "OldName"
        self.source_info_genre = "Type"
        self.source_info_class = "Class"        
        self.source_info_year = "Date"
        self.source_file_id = "File_id"
        
        # The corpus tokens do not store direct links to the source table,
        # but are linked indirectly via the column Sentence_id. In order to
        # be able to join the corpus table with the source table in the 
        # queries, we need to construct a temporary table that uses 
        # Sentence_id as the main key, but which includes also the source
        # information. This tabled is constructed by using the following
        # MySQL table query instruction:
        self.source_table_construct = "(SELECT {sentence_table}.{sentence_id}, {source_table}.{genre}, {source_table}.{date}, {source_table}.{old_name}, {source_table}.{xml_name}, {source_table}.{source_class} FROM {sentence_table}, {source_table} WHERE {sentence_table}.{sentence_text} = {source_table}.{source_id}) AS {source_name}".format(
            sentence_table=self.sentence_table,
            sentence_id=self.sentence_id,
            sentence_text=self.sentence_source_id,
            source_id=self.source_id,
            source_table=self.source_table,
            genre=self.source_info_genre,
            source_class=self.source_info_class,
            date=self.source_info_year,
            old_name=self.source_info_oldname,
            xml_name=self.source_info_label,
            source_name=self.source_table_alias)
        
        self.add_table_description(self.source_table, self.source_id,
            {"CREATE": [
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.source_id),
                "`{}` CHAR(3) NOT NULL".format(self.source_info_label),
                "`{}` CHAR(6) NOT NULL".format(self.source_info_oldname),
                "`{}` ENUM('ACPROSE','CONVRSN','FICTION','NEWS','NONAC','OTHERPUB','OTHERSP','UNPUB') NOT NULL".format(self.source_info_genre),
                "`{}` ENUM('S brdcast discussn','S brdcast documentary','S brdcast news','S classroom','S consult','S conv','S courtroom','S demonstratn','S interview','S interview oral history','S lect commerce','S lect humanities arts','S lect nat science','S lect polit law edu','S lect soc science','S meeting','S parliament','S pub debate','S sermon','S speech scripted','S speech unscripted','S sportslive','S tutorial','S unclassified','W ac:humanities arts','W ac:medicine','W ac:nat science','W ac:polit law edu','W ac:soc science','W ac:tech engin','W admin','W advert','W biography','W commerce','W email','W essay school','W essay univ','W fict drama','W fict poetry','W fict prose','W hansard','W institut doc','W instructional','W letters personal','W letters prof','W misc','W news script','W newsp brdsht nat: arts','W newsp brdsht nat: commerce','W newsp brdsht nat: editorial','W newsp brdsht nat: misc','W newsp brdsht nat: report','W newsp brdsht nat: science','W newsp brdsht nat: social','W newsp brdsht nat: sports','W newsp other: arts','W newsp other: commerce','W newsp other: report','W newsp other: science','W newsp other: social','W newsp other: sports','W newsp tabloid','W nonAc: humanities arts','W nonAc: medicine','W nonAc: nat science','W nonAc: polit law edu','W nonAc: soc science','W nonAc: tech engin','W pop lore','W religion') NOT NULL".format(self.source_info_class),
                "`{}` VARCHAR(21) NOT NULL".format(self.source_info_year),
                "`{}` SMALLINT(4) UNSIGNED NOT NULL".format(self.source_file_id)],
            "INDEX": [
                ([self.source_info_genre], 0, "HASH"),
                ([self.source_info_year], 0, "BTREE")]})
    
        # Specify that the corpus-specific code is contained in the dummy
        # class 'corpus_code' defined above:
        self._corpus_code = corpus_code
        
    def get_node_value(self, node):
        # words <w> and punctuations <c> have their value stored in their 
        # text:
        if node.tag in ("w", "c"):
            try:
                return node.text.strip ()
            except AttributeError:
                return ""
        # vocal nodes <vocal> and text gap nodes <gap> have their value 
        # in the desc attribute:
        if node.tag in ("vocal", "gap"):
            return node.attrib.get("desc", "").strip()
        
        # pause nodes <pause> have their duration in the dur attribute:
        if node.tag == "pause":
            return node.attrib.get("dur", "").strip()
    
    def process_child(self, child):
        tag = child.tag
        # <u> is an utterance. This element has a who attribute that 
        # specifies the speaker of the utterance.
        if tag == "u":
            self._speaker_id = child.attrib["who"].strip()
            if self._speaker_id not in self._tables[self.speaker_table]:
                self.logger.warning("Speaker %s found in body, but not in the speaker table" % self._speaker_id)
        # <s> is a sentence:
        elif tag == "s":
            self._sentence_id = self.table_get(self.sentence_table,
                {self.sentence_source_id: self._source_id, 
                 self.sentence_speaker_id: self._speaker_id})
        # other supported elements:
        elif tag in ("w", "vocal", "c", "gap", "pause"):
            word_text = self.get_node_value(child)
            if tag == "w":
                lemma_text = child.attrib.get("hw", "").strip()
                lemma_pos = child.attrib.get("pos", "").strip()
            if tag == "c":
                lemma_text = word_text
                lemma_pos = "PUNCT"
            word_pos = child.attrib.get("c5", "").strip()
            
            if tag in ("w", "c"):
                lemma_id = self.table_get(self.lemma_table, 
                    {self.lemma_label: lemma_text, 
                     self.lemma_pos_id: lemma_pos})
            else:
                lemma_id = 0
                word_pos = "UNC"
            word_id = self.table_get(self.word_table, 
                {self.word_label: word_text, 
                 self.word_lemma_id: lemma_id, 
                 self.word_pos_id: word_pos, 
                 self.word_type: tag})
                
            
            self.table_add(self.corpus_table, [word_id, self._sentence_id])

        # Recursively descend the tree:
        for grandchild in child:
            self.process_child(grandchild)

    def get_speaker_data(self, *args):
        person = args[0]
        if person.tag == "person":
            sex = person.attrib.get("sex", "unknown")
            if person.find("age") is not None:
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

    def process_file(self, current_file):
        
        # This should evaluate the content of
        #<teiHeader><fileDesc><extent> 6688 tokens; 6708 w-units; 423 s-units </extent</fileDesc></teiHeader> 
        # to ensure that the whole file is correctly processed.
        #
        # Or, it should use the detailed usage information from 
        # <teiHeader><encodingDesc><tagsDecl><namespace name="">
        #   <tagUsage gi="c" occurs="810" />...
        def get_year(S):
            match = re.match("(\d\d\d\d)", S)
            if match:
                return match.group(1)
            else:
                return S
            
           
        e = xml.etree.ElementTree.parse(current_file).getroot()
        header = e.find("teiHeader")
        file_desc = header.find("fileDesc")
        encoding_desc = header.find("encodingDesc")
        profile_desc = header.find("profileDesc")
        revision_desc = header.find("revisionDesc")
        
        # Get the date:
        creation = profile_desc.find("creation")
        date_element = creation.find("date")
        if date_element is not None:
            source_date = get_year(date_element.text.strip())
        else:
            source_date = get_year(creation.attrib.get("date", "0000"))
                
        # Get XMLName and OldName:
        for idno in file_desc.find("publicationStmt").findall("idno"):
            if idno.attrib["type"] == "bnc":
                source_xmlname = idno.text.strip()
            else:
                source_oldname = idno.text.strip()
        
        # Get the body:
        body = e.find("wtext")
        if body is None:
            body = e.find("stext")
        if body is None:
            logger.warning("Neither <wtext> nor <stext> found in file, not processed.")
            return
        
        # Get the text classification string:
        source_type = body.attrib.get("type")
        for class_code in profile_desc.find("textClass").findall("classCode"):
            if class_code.attrib.get("scheme") == "DLEE":
                source_class = class_code.text.strip()
        
        # Get a valid source id for this text. If it isn't in the source 
        # table yet, store it as a new entry:
        self._source_id = self.table_get(self.source_table, 
            {self.source_xmlname: source_xmlname, 
             self.source_oldname: source_oldname, 
             self.source_type: source_type, 
             self.source_info_class: source_class, 
             self.source_info_year: source_date, 
             self.source_file_id: self._id_count[self.file_table]})
        
        # Find all speakers, and if there are some, make sure that they are
        # stored in the speaker table:
        participant_desc = profile_desc.find("particDesc")
        if participant_desc is not None:
            for person in participant_desc.findall("person"):
                speaker = self.get_speaker_data(person)
                if speaker[0] not in self._tables[self.speaker_table]:
                    self.Con.insert(self.speaker_table, speaker)
                    self._tables[self.speaker_table][speaker[0]] = speaker
        
        
        # Now, parse the body of the XML file.
        
        # Initially, there is no speaker. It is set for each <u> element. In
        # written texts, no <u> elements occur, so the variable remains 
        # empty.
        self._speaker_id = ""
        
        for child in body:
            self.process_child(child)

if __name__ == "__main__":
    BNCBuilder().build()
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import xml.etree
import os.path, re
import csv, cStringIO, codecs, string

import corpusbuilder

class ICENigeriaBuilder(corpusbuilder.BaseCorpusBuilder):
    #def read_speaker_data(self, path):
        #e = xml.etree.ElementTree.parse(current_file).getroot()
        #header = e.find("teiHeader")
        #file_desc = header.find("fileDesc")
        #encoding_desc = header.find("encodingDesc")
        #profile_desc = header.find("profileDesc")
        #revision_desc = header.find("revisionDesc")
        
        ## Get the date:
        #creation = profile_desc.find("creation")
        #date_element = creation.find("date")
        #if date_element != None:
            #source_date = get_year(date_element.text.strip())
        #else:
            #source_date = get_year(creation.attrib.get("date", "0000"))
                
        ## Get XMLName and OldName:
        #for idno in file_desc.find("publicationStmt").findall("idno"):
            #if idno.attrib["type"] == "bnc":
                #source_xmlname = idno.text.strip()
            #else:
                #source_oldname = idno.text.strip()

                #pass
    
    
    def __init__(self):
        """ Initialize the corpus builder. The initialization includes a 
        definition of the database schema. """
        
        # all corpus builders have to call the inherited __init__ function:
        super(ICENigeriaBuilder, self).__init__()

        # specify which features are provided by this corpus and lexicon:
        self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_POS"]
        self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_SOURCE"]

        self.check_arguments()
        if not self.arguments.summary_path:
            self.arguments.summary_path = os.path.join(self.arguments.path, "../../summary.xml")
        
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
        
        self.corpus_table = "corpus"
        self.corpus_id = "TokenId"
        self.corpus_word_id = "WordId"
        self.corpus_source_id = "FileId"
        self.corpus_sentence_id = "SentenceId"
        
        self.add_table_description(self.corpus_table, self.corpus_id,
            {"CREATE": [
                "`{}` MEDIUMINT(6) UNSIGNED NOT NULL".format(self.corpus_id),
                "`{}` SMALLINT(5) UNSIGNED NOT NULL".format(self.corpus_word_id),
                "`{}` SMALLINT(5) UNSIGNED NOT NULL".format(self.corpus_sentence_id),                
                "`{}` SMALLINT(3) UNSIGNED NOT NULL".format(self.corpus_source_id)],
            "INDEX": [
                ([self.corpus_word_id], 0, "HASH"),
                ([self.corpus_sentence_id], 0, "HASH"),
                ([self.corpus_source_id], 0, "HASH")]})
        
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
        
        self.word_table = "word"
        self.word_id = "WordId"
        self.word_lemma = "Lemma"
        self.word_label = "Text"
        self.word_pos = "Pos"
        
        create_columns = ["`{}` SMALLINT(5) UNSIGNED NOT NULL".format(self.word_id),
                "`{}` VARCHAR(32) NOT NULL".format(self.word_label),
                "`{}` VARCHAR(32) NOT NULL".format(self.word_lemma),
                "`{}` VARCHAR(12) NOT NULL".format(self.word_pos)]
        index_columns = [([self.word_lemma], 0, "HASH"),
                ([self.word_pos], 0, "BTREE"),
                ([self.word_label], 0, "BTREE")]

        self.add_table_description(self.word_table, self.word_id,
            {"CREATE": create_columns,
            "INDEX": index_columns})

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
        
        self.file_table = "file"
        self.file_id = "FileId"
        self.file_label = "Path"
        
        self.add_table_description(self.file_table, self.file_id,
            {"CREATE": [
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.file_id),
                "`{}` TINYTEXT NOT NULL".format(self.file_label)]})

        # Any corpus that provides either CORP_CONTEXT, CORP_SOURCE or
        # CORP_FILENAME also needs to specify a source table. Each row in
        # this source table represents a corpus source, and it has to 
        # contain at least the following column:
        #
        # SourceId
        # An int value containing the unique identifier of this source.
        # 
        # Additional columns may also store further information such as 
        # year or genre.
        
        #self.speaker_table = "file"
        #self.speaker_id = "FileId"
        
        self.sentence_table = "sentence"
        self.sentence_id = "SentenceId"
        self.sentence_source_id = "SourceId"
        
        self.add_table_description(self.sentence_table, self.sentence_id,
            {"CREATE" : [
                "`{}` MEDIUMINT(5) UNSIGNED NOT NULL".format(self.sentence_id),
                "`{}` SMALLINT(3) UNSIGNED NOT NULL".format(self.sentence_source_id)],
            "INDEX": [
                ([self.sentence_source_id], 0, "HASH")]})
        
        self.source_table = "source"
        self.source_id = "SourceId"
        self.source_info_source = "Source"
        self.source_info_mode = "Mode"
        self.source_info_age = "Age"
        self.source_info_gender = "Gender"
        self.source_info_ethnicity = "Ethnicity"
        self.source_info_date = "Date"
        self.source_info_register = "Register"
        self.source_info_place = "Place"
        
        self.add_table_description(self.source_table, self.source_id,
            {"CREATE": [
                "`{}` SMALLINT(3) UNSIGNED NOT NULL".format(self.source_id),
                "`{}` VARCHAR(12) NOT NULL".format(self.source_info_source),
                "`{}` TINYTEXT NOT NULL".format(self.source_info_mode),
                "`{}` VARCHAR(15) NOT NULL".format(self.source_info_date),
                "`{}` VARCHAR(30) NOT NULL".format(self.source_info_register),
                "`{}` VARCHAR(30) NOT NULL".format(self.source_info_place),
                "`{}` VARCHAR(5) NOT NULL".format(self.source_info_age),
                "`{}` VARCHAR(1) NOT NULL".format(self.source_info_gender),
                "`{}` VARCHAR(15) NOT NULL".format(self.source_info_ethnicity)],
            "INDEX": [
                ([self.source_info_mode], 0, "BTREE"),
                ([self.source_info_register], 0, "BTREE"),
                ([self.source_info_date], 0, "BTREE"),
                ([self.source_info_place], 0, "BTREE"),
                ([self.source_info_gender], 0, "BTREE"),
                ([self.source_info_ethnicity], 0, "BTREE"),
                ([self.source_info_ethnicity], 0, "BTREE")]})
                
        self._source_info = {}
        self._sentence_id = None
        
        #self.file_filter = "*Pr_18_tmp*"
        
    def additional_arguments(self):
        self.parser.add_argument("--summary-path", help="Path to the summary.xml file containing speaker data (default: relative to input file path)", type=str)
        
    def process_child(self, child):
        def process_content(content):
            for row in content.splitlines():
                try:
                    word_text, word_pos, lemma_text = [x.strip() for x in row.split("\t")]
                except ValueError:
                    pass
                else:
                    new_sentence = False
                    
                    if word_pos == "CD":
                        lemma_text = word_text
                    if word_pos in string.punctuation:
                        word_pos = "PUNCT"
                    if word_pos == "SENT":
                        new_sentence = True
                        word_pos = "PUNCT"
                        
                    self._word_id = self.table_get(self.word_table, 
                        {self.word_label: word_text, 
                        self.word_lemma: lemma_text, 
                        self.word_pos: word_pos})[self.word_id]
                        
                    self.table_add(self.corpus_table,
                        {self.corpus_word_id: self._word_id,
                        self.corpus_source_id: self._source_id,
                        self.corpus_sentence_id: self._sentence_id})

                    if new_sentence:
                        self._sentence_id = self.table_get(self.sentence_table,
                            {self.sentence_source_id: self._source_id})[self.sentence_id]

        content = child.text
        if content:
            process_content(content)
        for grandchild in child:
            self.process_child(grandchild)
        content = child.tail
        if content:
            process_content(content)
        
        
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
        
        file_buffer = cStringIO.StringIO()
        with codecs.open(current_file, "rt", encoding = self.arguments.encoding) as input_file:
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
                        try:
                            file_buffer.write(line.encode("utf-8"))
                        except (UnicodeEncodeError, UnicodeDecodeError) as e:
                            print(line.decode("utf-8"))
                            print(line)
                            raise e
                        file_buffer.write("\n")
                        last = line

        S = file_buffer.getvalue()
        try:
            e = xml.etree.ElementTree.parse(cStringIO.StringIO(S)).getroot()
        except xml.etree.ElementTree.ParseError as e:
            m = re.search(r"line (\d*), column (\d*)", str(e))
            if m:
                line = int(m.group(1))
                column = int(m.group(2))
                start_line = max(0, line - 5)
                end_line = line + 5
            else:
                start_line = 0
                end_line = 999999
            S = S.splitlines()
            self.logger.error(e)
            print(current_file)
            for i, x in enumerate(S):                
                if i > start_line:
                    print("{:<3}: {}".format(i, x.decode("utf8")))
                if i == line - 1:
                    print("      " + " " * (column - 1) + "^")
                if i > end_line:
                    break
            raise e
        
        meta_info_keys = ["date", "place"]
        meta_info = {}        
        meta_xml = e.find("meta")
        for x in meta_info_keys:
            try:
                meta_info[x] = meta_xml.find(x).text.strip().split("\t")[0]
            except AttributeError:
                meta_info[x] = "?"
        meta_xml = meta_xml.find("author")
        meta_info_keys = ["gender", "age", "ethnic-group"]
        for x in meta_info_keys:
            try:
                meta_info[x] = meta_xml.find(x).text.strip().split("\t")[0]
            except AttributeError:
                meta_info[x] = "?"
                
        meta_info["register"] = os.path.basename(os.path.dirname(current_file))
        meta_info["mode"] = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(current_file), "..")))
        #genre = source_info["xml"].split("/")[1]

                
        base = self.get_file_identifier(current_file)
        self._source_info[base] = meta_info
        
        self._source_id = self.table_get(self.source_table,
            {self.source_info_source: base,
             self.source_info_age: meta_info["age"],
             self.source_info_gender: meta_info["gender"],
             self.source_info_ethnicity: meta_info["ethnic-group"],
             self.source_info_date: meta_info["date"],
             self.source_info_mode: meta_info["mode"],
             self.source_info_register: meta_info["register"],
             self.source_info_place: meta_info["place"]})[self.source_id]
            
        self._sentence_id = self.table_get(self.sentence_table,
                {self.sentence_source_id: self._source_id})[self.sentence_id]
        
        for x in e.find("text"):
            self.process_child(x)
        
    def process_file(self, current_file):
        if current_file.find("bl_18a.xml.pos") == -1:
            self.process_xml_file(current_file)

    def get_file_identifier(self, path):
        _, base = os.path.split(path)
        while "." in base:
            base, _= os.path.splitext(base)
        return base.lower()

    def read_source_data(self):
        #e = xml.etree.ElementTree.parse(self.arguments.summary_path).getroot()
        
        #for desc in e.findall("file"):
            #meta = desc.find("meta")
            #base = self.get_file_identifier(meta.attrib["raw"])
            #self._source_info[base] = meta.attrib
        pass

    def get_description(self):
        return "This script makes ICE Nigeria available to Coquery by reading the corpus data files from {} into the MySQL database '{}' so that the database can be queried by Coquery.".format(self.arguments.path, self.arguments.db_name)

def main():
    ICENigeriaBuilder().build()
    
if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
import xml.etree
import os.path, re
import csv, cStringIO, codecs, string
from collections import defaultdict
from corpusbuilder import *

class corpus_code():
    def tag_to_qhtml(self, s):
        translate_dict = {
            "p": "p",
            "punctuation": "",
            "heading": "h1",
            "boldface": "b",
            "italics": "i",
            "underline": "u",
            "superscript": "sup",
            "subscript": "sup",
            "text": "html", 
            "deleted": "s",
            "other-language": "span style='font-style: italic;'",
            "quote": "span style='font-style: italic; color: darkgrey; '",
            "error": "s"}
        if s in translate_dict:
            return translate_dict[s]
        else:
            print("unsupported tag: ", s)
            return s
    
    def render_context(self, token_id, source_id, token_width, context_width, widget):
        start = max(0, token_id - context_width)
        end = token_id + token_width + context_width - 1
    
        S = "SELECT {corpus}.{corpus_id}, {word}, {tag}, {tag_type}, {attribute}, {tag_id} FROM {corpus} INNER JOIN {word_table} ON {corpus}.{corpus_word_id} = {word_table}.{word_id} LEFT JOIN {tag_table} ON {corpus}.{corpus_id} = {tag_table}.{tag_corpus_id} WHERE {corpus}.{corpus_id} BETWEEN {start} AND {end} AND {corpus}.{source_id} = {current_source_id}".format(
            corpus=self.resource.corpus_table,
            corpus_id=self.resource.corpus_id,
            corpus_word_id=self.resource.corpus_word_id,
            source_id=self.resource.corpus_source_id,
            
            word=self.resource.word_label,
            word_table=self.resource.word_table,
            word_id=self.resource.word_id,
            
            tag_table=self.resource.tag_table,
            tag=self.resource.tag_label,
            tag_id=self.resource.tag_id,
            tag_corpus_id=self.resource.tag_corpus_id,
            tag_type=self.resource.tag_type,
            attribute=self.resource.tag_attribute,
            
            current_source_id=source_id,
            start=start, end=end)
        cur = self.resource.DB.execute_cursor(S)
        entities = {}

        for row in cur:
            #row = [x.decode("utf-8", errors="replace") if isinstance(x, str) else x for x in row]
            if row[self.resource.corpus_id] not in entities:
                entities[row[self.resource.corpus_id]] = []
            entities[row[self.resource.corpus_id]].append(row)

        context = []
        # we need to keep track of any opening and closing tag that does not
        # have its matching tag in the selected context:
        opened_tags = []
        closed_tags = []
        correct_word = ""
        for token in sorted(entities):
            entity_list = sorted(entities[token], key=lambda x:x[self.resource.tag_id])
            text_output = False
            word = entity_list[0][self.resource.word_label]
            for row in entity_list:
                tag = row[self.resource.tag_label]
                
                # special treatment for tags:
                if tag:
                    attributes = row[self.resource.tag_attribute]
                    tag_type = row[self.resource.tag_type]

                    if tag_type == "empty":
                        if tag == "object":
                            # add placeholder images for <object> tags
                            if "type=table" in attributes:
                                context.append("<br/><img src='../logo/placeholder_table.png'/><br/>")
                            if "type=graphic" in attributes:
                                context.append("<br/><img src='../logo/placeholder.png'/><br/>")
                            if "type=formula" in attributes:
                                context.append("<br/><img src='../logo/formula.png'/><br/>")
                        elif tag == "error":
                            if attributes.startswith("corrected="):
                                correct_word = attributes[len("corrected="):]
                                context.append('<span style="color: darkgreen;">{}</span>'.format(correct_word))
                            correct_word  = ""
                        elif tag == "break":
                            context.append("<br/>")
                        elif tag == "x-anonym-x":
                            context.append('<span style="color: lightgrey; background: black;">&nbsp;&nbsp;&nbsp;{}&nbsp;&nbsp;&nbsp;</span>'.format(attributes[len("type="):]))
                        else:
                            print(tag)
                
                    elif tag_type == "open":
                        if tag == "error":
                            if attributes.startswith("corrected="):
                                correct_word = attributes[len("corrected="):]
                            attributes = 'style="color: darkgrey;"'
                        #elif tag == "other-language":
                            #context.append('<span style="font-style: italic;">')
                        tag = self.tag_to_qhtml(tag)
                        if attributes:
                            context.append("<{} {}>".format(tag, attributes))
                        else:
                            context.append("<{}>".format(tag))
                        opened_tags.append(row[self.resource.tag_label])

                    elif tag_type == "close":
                        # if there is still a dangling correction from an 
                        # open <error> tag, add the correct word now:
                        if correct_word:
                            context.append('<span style="color: darkgreen;">{}</span>'.format(correct_word))
                            correct_word = ""
                        # add the current token before processing any other
                        # closing tag:
                        if not text_output:
                            text_output = True
                            if token == token_id:
                                context.append('<span style="font-weight: bold; background-color: lightyellow; border-style: outset;" >')
                            context.append(word)
                        
                        if attributes:
                            context.append("</{} {}>".format(self.tag_to_qhtml(tag), attributes))
                        else:
                            context.append("</{}>".format(self.tag_to_qhtml(tag)))
                        # if the current tag closes an earlier opening tag,
                        # remove that tag from the list of open environments:
                        try:
                            if opened_tags[-1] == row[self.resource.tag_label]:
                                opened_tags.pop(len(opened_tags)-1)
                        except IndexError:
                            closed_tags.append(tag)
                            pass
                        if tag == "other-language":
                            context.append('</span>')
            if not text_output:
                if token == token_id:
                    context.append('<span style="font-weight: bold; background-color: lightyellow; border-style: outset;" >')
                context.append(word)
            if token == token_id + token_width - 1:
                context.append('</span>')
        for x in opened_tags[::-1]:
            context.append("</{}>".format(self.tag_to_qhtml(x)))
        for x in closed_tags:
            context.insert(0, ("<{}>".format(self.tag_to_qhtml(x))))

        widget.ui.context_area.setText(collapse_words(context))

class ICENigeriaBuilder(BaseCorpusBuilder):
    def __init__(self):
        """ Initialize the corpus builder. The initialization includes a 
        definition of the database schema. """
        
        # all corpus builders have to call the inherited __init__ function:
        super(ICENigeriaBuilder, self).__init__()

        # specify which features are provided by this corpus and lexicon:
        self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_POS"]
        self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_SOURCE"]

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
        
        self.corpus_table = "corpus"
        self.corpus_id = "TokenId"
        self.corpus_word_id = "WordId"
        self.corpus_file_id = "FileId"
        self.corpus_source_id = "SourceId"
        
        self.add_table_description(self.corpus_table, self.corpus_id,
            {"CREATE": [
                "`{}` MEDIUMINT(6) UNSIGNED NOT NULL".format(self.corpus_id),
                "`{}` SMALLINT(5) UNSIGNED NOT NULL".format(self.corpus_word_id),
                #"`{}` SMALLINT(5) UNSIGNED NOT NULL".format(self.corpus_sentence_id),                
                "`{}` SMALLINT(3) UNSIGNED NOT NULL".format(self.corpus_file_id),
                "`{}` SMALLINT(3) UNSIGNED NOT NULL".format(self.corpus_source_id)],
            "INDEX": [
                ([self.corpus_word_id], 0, "HASH"),
                #([self.corpus_sentence_id], 0, "HASH"),
                ([self.corpus_file_id], 0, "HASH"),
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
            
        self.add_new_table_description(self.word_table,
            [Primary(self.word_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(32) NOT NULL"),
             Column(self.word_lemma, "VARCHAR(32) NOT NULL"),
             Column(self.word_pos, "VARCHAR(12) NOT NULL")])
             
            
                                       

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
        self.file_name = "Filename"
        self.file_path = "Path"
        
        self.add_table_description(self.file_table, self.file_id,
            {"CREATE": [
                "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(self.file_id),
                "`{}` TINYTEXT NOT NULL".format(self.file_name),
                "`{}` TINYTEXT NOT NULL".format(self.file_path)]})
        
        self.add_new_table_description(self.file_table,
            [Primary(self.file_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.file_name, "TINYTEXT NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])
        
        #self.sentence_table = "sentence"
        #self.sentence_id = "SentenceId"
        
        #self.add_table_description(self.sentence_table, self.sentence_id,
            #{"CREATE" : [
                #"`{}` MEDIUMINT(5) UNSIGNED NOT NULL".format(self.sentence_id)]})
        
        self.source_table = "source"
        self.source_id = "SourceId"
        self.source_mode = "Mode"
        self.source_age = "Age"
        self.source_gender = "Gender"
        self.source_ethnicity = "Ethnicity"
        self.source_date = "Date"
        self.source_register = "Register"
        self.source_place = "Place"
        
        self.add_table_description(self.source_table, self.source_id,
            {"CREATE": [
                "`{}` SMALLINT(3) UNSIGNED NOT NULL".format(self.source_id),
                "`{}` TINYTEXT NOT NULL".format(self.source_mode),
                "`{}` VARCHAR(15) NOT NULL".format(self.source_date),
                "`{}` VARCHAR(30) NOT NULL".format(self.source_register),
                "`{}` VARCHAR(30) NOT NULL".format(self.source_place),
                "`{}` VARCHAR(5) NOT NULL".format(self.source_age),
                "`{}` VARCHAR(1) NOT NULL".format(self.source_gender),
                "`{}` VARCHAR(15) NOT NULL".format(self.source_ethnicity)],
            "INDEX": [
                ([self.source_mode], 0, "BTREE"),
                ([self.source_register], 0, "BTREE"),
                ([self.source_date], 0, "BTREE"),
                ([self.source_place], 0, "BTREE"),
                ([self.source_gender], 0, "BTREE"),
                ([self.source_ethnicity], 0, "BTREE"),
                ([self.source_ethnicity], 0, "BTREE")]})

        self.add_new_table_description(self.source_table,
            [Primary(self.source_id, "SMALLINT(3) UNSIGNED NOT NULL"),
             Column(self.source_mode, "TINYTEXT NOT NULL"),
             Column(self.source_date, "VARCHAR(15) NOT NULL"),
             Column(self.source_register, "VARCHAR(30) NOT NULL"),
             Column(self.source_place, "VARCHAR(30) NOT NULL"),
             Column(self.source_age, "VARCHAR(5) NOT NULL"),
             Column(self.source_gender, "VARCHAR(1) NOT NULL"),
             Column(self.source_ethnicity, "VARCHAR(15) NOT NULL")])

        self.add_new_table_description(self.corpus_table,
            [Primary(self.corpus_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_source_id, self.source_table)])

                
        self._corpus_id = 0
        self._corpus_code = corpus_code
        

    def xml_preprocess_tag(self, element):
        if element.text or list(element):
            self.tag_next_token(element.tag, element.attrib)
        else:
            self.add_empty_tag(element.tag, element.attrib)

    def xml_postprocess_tag(self, element):
        if element.text or list(element):
            self.tag_last_token(element.tag, element.attrib)
        else:
            if element.tag == "x-anonym-x":
                # ICE-NG contains anonymized labels for names, placenames,
                # and other nouns. Insert a special label in that case:
                self._word_id = self.table_get(self.word_table, 
                        {self.word_label: "ANONYMIZED", 
                        self.word_lemma: "ANONYMIZED", 
                        self.word_pos: "np"}, case=True)

    def process_text(self, text):
        for row in text.splitlines():
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
                    self.word_pos: word_pos}, case=True)
                    
                self._corpus_id = self.table_add(self.corpus_table,
                    {self.corpus_word_id: self._word_id,
                    self.corpus_file_id: self._file_id,
                    self.corpus_source_id: self._source_id})

                #if new_sentence:
                    #self._sentence_id = self.table_get(self.sentence_table,
                        #{self.sentence_source_id: self._source_id})
        

    def xml_process_content(self, element):
        """ In ICE-NG, the XML elements contain rows of words. This method 
        processes these rows, and creates token entries in the corpus table. 
        It also creates new entries in the word table if necessary."""
        if element.text:
            self.process_text(element.text)

    def xml_process_tail(self, element):
        if element.tail:
            self.process_text(element.tail)
        
    def xml_get_meta_information(self, root):
        meta_info_keys = ["date", "place"]
        meta_info = {}        
        meta_xml = root.find("meta")
        for x in meta_info_keys:
            try:
                meta_info[x] = meta_xml.find(x).text.strip().split("\t")[0]
            except AttributeError:
                meta_info[x] = "?"
                
        # get speaker/author information, enclosed in <author> tags:
        meta_xml = meta_xml.find("author")
        meta_info_keys = ["gender", "age", "ethnic-group"]
        for x in meta_info_keys:
            try:
                meta_info[x] = meta_xml.find(x).text.strip().split("\t")[0]
            except AttributeError:
                meta_info[x] = "?"
                
        meta_info["register"] = os.path.basename(os.path.dirname(self._current_file))
        meta_info["mode"] = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(self._current_file), "..")))

        # all meta data gathered, store it:
        self._source_id = self.table_get(self.source_table,
            {self.source_age: meta_info["age"],
             self.source_gender: meta_info["gender"],
             self.source_ethnicity: meta_info["ethnic-group"],
             self.source_date: meta_info["date"],
             self.source_mode: meta_info["mode"],
             self.source_register: meta_info["register"],
             self.source_place: meta_info["place"]})
                
        
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
                        # The file buffer uses byte-strings, not unicode 
                        # strings. Therefore, encode the string first:
                        file_buffer.write(line.encode("utf-8"))
                        file_buffer.write("\n")
                        last = line

        S = file_buffer.getvalue()
        
        e = self.xml_parse_file(cStringIO.StringIO(S))
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

    def get_description(self):
        return "This script makes ICE Nigeria available to Coquery by reading the corpus data files from {}/POS-Tagged into the MySQL database '{}' so that the database can be queried by Coquery.The required data file 'ICE-Nigeria-written-pos-tagged.zip' can be downloaded from http://sourceforge.net/projects/ice-nigeria/files/.".format(self.arguments.path, self.arguments.db_name)

    def get_citation(self):
        return "(no citation)"
    
def main():
    ICENigeriaBuilder().build()
    
if __name__ == "__main__":
    main()
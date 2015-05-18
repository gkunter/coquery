# -*- coding: utf-8 -*-
"""
FILENAME: bnc.py -- corpus module for the Coquery corpus query tool

This module contains the classes required to make BNC queries.

LICENSE:
Copyright (c) 2015 Gero Kunter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from corpus import *
import tokens

class Resource(SQLResource):
    pos_table = "entity"
    pos_label = "C5"
    pos_id = "C5"

    word_table = "entity"
    word_id = "id"
    word_label = "Text"
    word_pos_id = "C5"
    word_lemma_id = "Lemma_id"
    word_transcript_id = "Text"
    
    lemma_table = "lemma"
    lemma_id = "id"
    lemma_label = "Text"

    corpus_table = "element"
    corpus_word_id = "Entity_id"
    corpus_token_id = "id"
    corpus_source_id = "Sentence_id"

    sentence_table = "sentence"
    sentence_id = "id"
    sentence_text_id = "Text_id"

    source_table_name = "text"
    source_table_alias = "SOURCETABLE"
    source_id = "id"
    source_label = "XMLName"
    source_year = "Date"
    source_genre = "Type"
    source_oldname = "OldName"
    source_file_id = "File_id"
    source_table = "(SELECT {sentence_table}.{sentence_id}, {text_table}.{genre}, {text_table}.{date}, {text_table}.{old_name}, {text_table}.{xml_name} FROM {sentence_table}, {text_table} WHERE {sentence_table}.{sentence_text} = {text_table}.{source_id}) AS {source_name}".format(
        sentence_table=sentence_table,
        sentence_id=sentence_id,
        sentence_text=sentence_text_id,
        source_id=source_id,
        text_table=source_table_name,
        genre=source_genre,
        date=source_year,
        old_name=source_oldname,
        xml_name=source_label,
        source_name=source_table_alias)
    
    speaker_table = "speaker"
    speaker_id = "id"
    
    file_table = "file"
    file_id = "id"
    file_label = "Filename"
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_ORTH, LEX_LEMMA, LEX_POS]

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_SOURCE, CORP_FILENAME, CORP_STATISTICS]

    def get_source_info_headers(self):
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
        
    def get_file_info_headers(self):
        return [
            self.resource.source_label,
            self.resource.file_label]
 

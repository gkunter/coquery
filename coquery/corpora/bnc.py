# -*- coding: utf-8 -*-
#
# FILENAME: bnc.py -- a corpus module for the Coquery corpus query tool
# 
# This module was automatically created by corpusbuilder.py.
#

from corpus import *

class Resource(SQLResource):
    db_name = 'bnc'
    name = 'bnc'
    corpus_source_id = 'Sentence_id'
    corpus_table = 'element'
    corpus_token_id = 'id'
    corpus_word_id = 'Entity_id'
    file_id = 'id'
    file_label = 'Filename'
    file_table = 'file'
    lemma_id = 'id'
    lemma_label = 'Text'
    lemma_pos_id = 'Pos'
    lemma_table = 'lemma'
    sentence_id = 'id'
    sentence_source_id = 'Source_id'
    sentence_speaker_id = 'Speaker_id'
    sentence_table = 'sentence'
    source_class = 'Class'
    source_file_id = 'File_id'
    source_genre = 'Type'
    source_id = 'id'
    source_info_label = 'XMLName'
    source_info_oldname = 'OldName'
    source_table = 'text'
    source_table_alias = 'SOURCETABLE'
    source_table_construct = '(SELECT sentence.id, text.Type, text.Date, text.OldName, text.XMLName, text.Class FROM sentence, text WHERE sentence.Source_id = text.id) AS SOURCETABLE'
    source_info_year = 'Date'
    speaker_age = 'Age'
    speaker_id = 'id'
    speaker_sex = 'Sex'
    speaker_table = 'speaker'
    word_id = 'id'
    word_label = 'Text'
    word_lemma_id = 'Lemma_id'
    word_pos_id = 'C5'
    word_table = 'entity'
    word_type = 'Type'
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_POS]
    

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_FILENAME, CORP_SOURCE, CORP_STATISTICS]
    
    #def get_source_info_headers(self):
        #return [
            #self.resource.source_genre,
            #self.resource.source_year,
            #self.resource.source_oldname]
    
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


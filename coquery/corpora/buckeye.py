# -*- coding: utf-8 -*-
#
# FILENAME: buckeye.py -- a corpus module for the Coquery corpus query tool
# 
# This module was automatically created by corpusbuilder.py.
#

from corpus import *

class Resource(SQLResource):
    name = 'buckeye'
    db_name = 'buckeye_maria'
    corpus_code = '__main__.corpus_code'
    corpus_source_id = 'FileId'
    corpus_table = 'corpus'
    corpus_time = 'Time'
    corpus_token_id = 'TokenId'
    corpus_word_id = 'WordId'
    file_id = 'FileId'
    file_label = 'Path'
    file_table = 'file'
    lemma_id = 'LemmaId'
    lemma_label = 'Text'
    lemma_table = 'lemma'
    lemma_transcript_id = 'Transcript'
    source_id = 'FileId'
    source_table = 'file'
    word_id = 'WordId'
    word_label = 'Text'
    word_lemma_id = 'LemmaId'
    word_pos_id = 'Pos'
    word_table = 'word'
    word_transcript_id = 'Transcript'
    

    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_PHON, LEX_POS]
    


class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_FILENAME, CORP_STATISTICS, CORP_TIMING]
    
    def sql_string_get_time_info(self, token_id):
        return "SELECT {} FROM {} WHERE {} = {}".format(
                self.resource.corpus_time,
                self.resource.corpus_table,
                self.resource.corpus_token_id,
                token_id)

    def get_time_info_headers(self):
        return ["Time"]


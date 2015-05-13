# -*- coding: utf-8 -*-
#
# FILENAME: shakespeare.py -- a corpus module for the Coquery corpus query tool
# 
# This module was automatically created by create_mysql_corpus.py.
#

from corpus import *

class Resource(SQLResource):
    db_name = "shakespeare"

    word_table = "word"
    word_id_column = "WordId"
    word_label_column = "Text"
    word_pos_id_column = "Pos"
    word_lemma_id_column = "LemmaId"

    lemma_table = "lemma"
    lemma_id_column = "LemmaId"
    lemma_label_column = "Text"

    pos_table = "word"
    pos_id_column = "Pos"
    pos_label_column = "Pos"
    
    corpus_table = "corpus"
    corpus_word_id_column = "WordId"
    corpus_token_id_column = "TokenId"
    corpus_source_id_column = "SourceId"
    
    file_table = "source"
    file_id_column = "SourceId"
    file_label_column = "Text"
    
    source_table = "source"
    source_table_alias = "source"
    source_id_column = "SourceId"
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_POS]

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_FILENAME, CORP_STATISTICS, CORP_SENTENCE]

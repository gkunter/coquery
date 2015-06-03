# -*- coding: utf-8 -*-
#
# FILENAME: shakespeare.py -- a corpus module for the Coquery corpus query tool
# 
# This module was automatically created by create_mysql_corpus.py.
#

from corpus import *

class Resource(SQLResource):
    name = 'shakespeare'
    db_name = "shakespeare"

    word_table = "word"
    word_id = "WordId"
    word_label = "Text"
    word_pos_id = "Pos"
    word_lemma_id = "LemmaId"

    lemma_table = "lemma"
    lemma_id = "LemmaId"
    lemma_label = "Text"

    pos_table = "word"
    pos_id = "Pos"
    pos_label = "Pos"
    
    corpus_table = "corpus"
    corpus_word_id = "WordId"
    corpus_token_id = "TokenId"
    corpus_source_id = "SourceId"
    
    file_table = "source"
    file_id = "SourceId"
    file_label = "Text"

    source_table = "source"
    source_table_alias = "source"
    source_id = "SourceId"

    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_POS]

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_FILENAME, CORP_STATISTICS]

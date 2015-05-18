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

class Resource(SQLResource):
    word_table = "lexicon"
    word_id = "WordId"
    word_label = "WordCS"
    word_transcript_id = "Word"
    word_pos_id = "PoS"
    word_lemma_id = "Lemma"

    lemma_table = "lexicon"
    lemma_id = "Lemma"
    lemma_label = "Lemma"

    pos_table = "lexicon"
    pos_id = "PoS"
    pos_label = "PoS"

    #transcript_table = "cmudict.dict"
    #transcript_id = "Text"
    #transcript_label = "Transcript"
    
    corpus_table = "corpus"
    corpus_word_id = "WordId"
    corpus_token_id = "TokenId"
    corpus_source_id = "TextId"
    
    source_table = "sources"
    source_id = "TextId"
    source_label = "Title"
    source_table_alias = "sources"
    source_year = "Year"
    source_genre = "Genre"
    
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_POS]

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_SOURCE, CORP_STATISTICS]
 
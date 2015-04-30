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
    word_id_column = "WordId"
    word_label_column = "Word"
    word_transcript_id_column = "Word"
    word_pos_id_column = "PoS"
    word_lemma_id_column = "Lemma"

    lemma_table = "lexicon"
    lemma_id_column = "Lemma"
    lemma_label_column = "Lemma"

    pos_table = "lexicon"
    pos_id_column = "PoS"
    pos_label_column = "PoS"

    #transcript_table = "cmudict.dict"
    #transcript_id_column = "Text"
    #transcript_label_column = "Transcript"
    
    corpus_table = "corpus"
    corpus_word_id_column = "WordId"
    corpus_token_id_column = "TokenId"
    corpus_source_id_column = "TextId"
    
    source_table = "sources"
    source_id_column = "TextId"
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_POS]

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_STATISTICS]
 
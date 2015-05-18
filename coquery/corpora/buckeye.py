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
    word_table = "word"
    word_id = "WordId"
    word_label = "Text"
    word_pos_id = "Pos"
    word_lemma_id = "LemmaId"
    word_transcript_id = "Transcript"
    
    lemma_table = "lemma"
    lemma_id = "LemmaId"
    lemma_label = "Text"

    pos_table = "word"
    pos_id = "Pos"
    pos_label = "Pos"
    
    transcript_table = "word"
    transcript_id = "Text"
    transcript_label = "Transcript"

    corpus_table = "corpus"
    corpus_word_id = "WordId"
    corpus_token_id = "TokenId"
    corpus_source_id = "SourceId"
    corpus_time = "Time"
    
    file_table = "source"
    file_id = "SourceId"
    file_label = "Text"
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_POS, LEX_PHON]

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_FILENAME, CORP_STATISTICS, CORP_TIMING]

    def sql_string_get_time_info(self, token_id):
        return "SELECT Time FROM {} WHERE {} = {}".format(
                self.resource.corpus_table,
                self.resource.corpus_token_id,
                token_id)

    def get_time_info_headers(self):
        return ["Time"]
    

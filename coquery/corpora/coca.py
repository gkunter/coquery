# -*- coding: utf-8 -*-
"""
FILENAME: coca.py -- corpus module for the Coquery corpus query tool

This module contains the classes required to make COCA queries.

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
import options
import tokens

class Resource(SQLResource):
    pos_table = "pos"
    pos_label_column = "PoS"
    pos_clean_label_column = "PosClean"
    pos_id_column = "PosId"

    word_table = "lexicon"
    word_id_column = "WordId"
    word_label_column = "Word"
    word_pos_id_column = "PosId"
    word_lemma_id_column = "Lemma"
    
    lemma_table = "lexicon"
    lemma_id_column = "Lemma"
    lemma_label_column = "Lemma"

    #transcript_table = "cmudict.dict"
    #transcript_id_column = "Text"
    #transcript_label_column = "Transcript"

    corpus_table = "corpus"
    corpus_word_id_column = "WordId"
    corpus_token_id_column = "TokenId"
    corpus_source_id_column = "TextId"

    source_table = "sources"
    source_table_alias = "sources"
    source_id_column = "TextId"
    source_year_column = "Year"
    source_genre_column = "Genre"
    source_label_column = "Source"
    source_title_column = "Title"
    
    self_join_corpus = "corpusBig"
    self_join_source_table = "sources"

class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_ORTH, LEX_LEMMA, LEX_POS]

    def __init__(self, resource):
        super(Lexicon, self).__init__(resource)
        if options.cfg.ignore_pos_chars:
            query_string = "SELECT {} AS ID, {} AS POS FROM {}".format(
                self.resource.pos_id_column,
                self.resource.pos_clean_label_column, 
                self.resource.pos_table)
        else:
            query_string = "SELECT {} AS ID, {} AS POS FROM {}".format(
                self.resource.pos_id_column,
                self.resource.pos_label_column, 
                self.resource.pos_table)
        for current_pos in self.resource.DB.execute_cursor(query_string):
            self.pos_dict[current_pos["ID"]] = current_pos["POS"]

    def sql_string_get_posid_list(self, token):
        where_string = self.sql_string_get_posid_list_where(token)
        return "SELECT DISTINCT {word_table}.{word_pos} FROM {word_table} INNER JOIN {pos_table} ON {pos_table}.{pos_id} = {word_table}.{word_pos} WHERE {where_string}".format(
            word_pos=self.resource.word_pos_id_column,
            word_table=self.resource.word_table,
            pos_table=self.resource.pos_table,
            pos_id=self.resource.pos_id_column,
            where_string=where_string)

class Corpus(SQLCorpus):
    provides = [CORP_SOURCE, CORP_CONTEXT, CORP_STATISTICS]
    
    def yield_query_results(self, Query, self_join=True):
        if Query.number_of_tokens == 1 or Query.number_of_tokens > 7:
            return super(Corpus, self).yield_query_results(Query, False)
        else: 
            return super(Corpus, self).yield_query_results(Query, self_join)
 
    def sql_string_get_source_info(self, source_id):
        return "SELECT {} AS Year, {} AS Genre, {} AS Source, {} AS Title FROM {} WHERE {} = {}".format(
            self.resource.source_year_column,
            self.resource.source_genre_column,
            self.resource.source_label_column,
            self.resource.source_title_column,
            self.resource.source_table,
            self.resource.source_id_column,
            source_id)
    
    def get_source_info_headers(self):
        return ["Year", "Genre", "Source", "Title"]

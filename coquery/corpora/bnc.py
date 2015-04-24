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
from __future__ import print_function
import sys

import __init__

import logging

from corpus import *
import options

import sqlwrap
import tokens


class BNCResource(SQLResource):
    DB = sqlwrap.SqlDB (Host=options.cfg.db_host, Port=options.cfg.db_port, User=options.cfg.db_user, Password=options.cfg.db_password, Database=options.cfg.db_name)

    pos_table = "entity"
    pos_label_column = "C5"
    pos_id_column = "C5"

    word_table = "entity"
    word_id_column = "id"
    word_label_column = "Text"
    word_pos_id_column = "C5"
    word_lemma_id_column = "Lemma_id"
    word_transcript_id_column = "Text"
    
    lemma_table = "lemma"
    lemma_id_column = "id"
    lemma_label_column = "Text"

    corpus_table = "element"
    corpus_word_id_column = "Entity_id"
    corpus_token_id_column = "id"

    source_table = "text"
    source_id_column = "XMLName"
    source_label_column = "XMLName"
    
    corpus_source_id_column = "Sentence_id"
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_ORTH, LEX_LEMMA, LEX_POS]

    def __init__(self, resource):
        super(Lexicon, self).__init__(resource)
        self.resource = resource

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_SOURCE, CORP_FILENAME, CORP_STATISTICS]

    def get_context(self, token_id, number_of_tokens):
        if options.cfg.context_span > token_id:
            left_span = token_id - 1
        else:
            left_span = options.cfg.context_span
        start = token_id - left_span
        end = token_id + number_of_tokens + options.cfg.context_span - 1
        QueryString = "SELECT entity_id FROM element WHERE id BETWEEN %s AND %s" % (start, end)
        Resource.DB.execute(QueryString)
        ContextList = []
        for i, CurrentResult in enumerate(Resource.DB.Cur):
            entry = self.lexicon.get_entry(CurrentResult[0])
            # if the query is not case sensitive, capitalize the words that
            # match the query string:
            if not options.cfg.case_sensitive and i in range(options.cfg.context_span, options.cfg.context_span + number_of_tokens):
                ContextList.append (entry.orth.upper())
            else:
                ContextList.append (entry.orth)
        return ContextList
 
    def get_text_wherelist(self, text_filter):
        token = tokens.COCATextToken(text_filter, self.lexicon)
        Genres, Years, Negated = token.get_parse()
        query_string = "SELECT sentence.id FROM sentence INNER JOIN text ON (sentence.Text_id = text.id)"
        where_list = []
        if Genres:
            where_list += ['text.Type LIKE "%s"' % x for x in Genres]
        if where_list:
            where_string = " OR ".join(where_list)
        
        query_string = "%s WHERE %s" % (query_string, where_string)
        Resource.DB.execute(query_string)
        Results = Resource.DB.fetch_all()
        if not Results:
            raise TextfilterError
        return [str(x) for x in Results]
 
    def get_source_info(self, source_id):
        source_info_headers = self.get_source_info_headers()
        ErrorValue = ["<na>"] * len(source_info_headers)
        if not source_id:
            return ErrorValue
        try:
            cursor = Resource.DB.execute_cursor("SELECT * FROM sentence INNER JOIN text where sentence.Text_id = text.id AND sentence.id = {}".format(source_id))
            Result = cursor.fetchone()
        except SQLOperationalError: 
            return ErrorValue
        return [Result[x] for x in source_info_headers]
    
    def get_source_info_headers(self):
        return ["Type", "Date", "OldName"]
    
    def get_file_info(self, file_id):
        file_info_headers = self.get_file_info_headers()
        ErrorValue = ["<na>"] * len(file_info_headers)
        if not file_id:
            return ErrorValue
        try:
            cursor = Resource.DB.execute_cursor("SELECT * FROM text, file WHERE text.file_id = file.id AND file.id = %s" % file_id)
            Result = cursor.fetchone()
        except (SQLOperationalError, IndexError):
            return ErrorValue
        return [Result[x] for x in file_info_headers]
    
    def get_file_info_headers(self):
        return ["XMLName", "Filename"]
 
if __name__ == "__main__":
    print("""This module is part of the Coquery corpus query tool and cannot be run on its own.""", file=sys.stderr)
    sys.exit(1)
else:
    logger = logging.getLogger(__init__.NAME)
    Resource = BNCResource()

    logger.info("Connected to database %s@%s:%s."  % (options.cfg.db_name, options.cfg.db_host, options.cfg.db_port))
    logger.info("User=%s, password=%s" % (options.cfg.db_user, options.cfg.db_password))            

    if options.cfg.no_cache:
        logger.info("Resetting query cache.")
        Resource.DB.execute("RESET QUERY CACHE")
        Resource.DB.execute("SET SESSION query_cache_type = OFF")

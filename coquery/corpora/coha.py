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
import options
import sqlwrap
from corpus import *

class COHAResource(SQLResource):
    DB = sqlwrap.SqlDB (Host=options.cfg.db_host, Port=options.cfg.db_port, User=options.cfg.db_user, Password=options.cfg.db_password, Database=options.cfg.db_name)

    pos_table = "lexicon"
    pos_id_column = "PoS"
    pos_label_column = "PoS"
    
    word_table = "lexicon"
    word_id_column = "WordId"
    word_label_column = "Word"
    word_transcript_id_column = "Word"
    word_pos_id_column = "PoS"
    word_pos_column = "PoS"
    word_lemma_id_column = "Lemma"

    transcript_table = "cmudict.dict"
    transcript_id_column = "Text"
    transcript_label_column = "Transcript"
    
    lemma_table = "lexicon"
    lemma_id_column = "Lemma"
    lemma_label_column = "Lemma"

    corpus_table = "corpus"
    corpus_word_id_column = "WordId"
    corpus_token_id_column = "TokenId"
    corpus_source_id_column = "TextId"
    
    source_table = "sources"
    source_id_column = "TextId"
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_POS, LEX_PHON]

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_SOURCE, CORP_STATISTICS]

    def get_context(self, token_id, number_of_tokens):
        if options.cfg.context_span > token_id:
            left_span = token_id - 1
        else:
            left_span = options.cfg.context_span
        start = token_id - left_span
        end = token_id + number_of_tokens + options.cfg.context_span - 1
        QueryString = "SELECT {word_id} AS W1 FROM {corpus_table} WHERE {token_id} BETWEEN {start} AND {end}".format(
            word_id=self.resource.corpus_word_id_column,
            corpus_table=self.resource.corpus_table,
            token_id=self.resource.corpus_token_id_column,
            start=start, end=end)
        Resource.DB.execute(QueryString)
        ContextList = []
        i = start
        for i, CurrentResult in enumerate(Resource.DB.Cur):
            entry = self.lexicon.get_entry(CurrentResult[0])
            # if the query is not case sensitive, capitalize the words that
            # match the query string:
            if not options.cfg.case_sensitive and i in range(left_span, left_span + number_of_tokens):
                ContextList.append (entry.orth.upper())
            else:
                ContextList.append (entry.orth)
        return ContextList
 
if __name__ == "__main__":
    print("""This module is part of the Coquery corpus query tool and cannot be run on its own.""", file=sys.stderr)
    sys.exit(1)
else:
    logger = logging.getLogger(__init__.NAME)
    Resource = COHAResource()
    
    logger.info("Connected to database %s@%s:%s."  % (options.cfg.db_name, options.cfg.db_host, options.cfg.db_port))
    logger.info("User=%s, password=%s" % (options.cfg.db_user, options.cfg.db_password))            

    if options.cfg.no_cache:
        logger.info("Resetting query cache.")
        Resource.DB.execute("RESET QUERY CACHE")
        Resource.DB.execute("SET SESSION query_cache_type = OFF")

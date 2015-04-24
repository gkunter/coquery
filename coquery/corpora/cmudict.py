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

class CMUDictResource(SQLResource):

    db_name = "cmudict"

    DB = sqlwrap.SqlDB (Host=options.cfg.db_host, Port=options.cfg.db_port, User=options.cfg.db_user, Password=options.cfg.db_password, Database=db_name)

    word_table = "dict"
    word_id_column = "WordId"
    word_transcript_id_column = "Transcript"

    transcript_table = "dict"
    transcript_id_column = "Transcript"
    transcript_label_column = "Transcript"
    
    #corpus_table = "dict"
    #corpus_word_id_column = "WordId"
    #corpus_token_id_column = "WordId"
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_ORTH, LEX_PHON]

class Corpus(SQLCorpus):
    provides = [CORP_STATISTICS]
 
if __name__ == "__main__":
    print("""This module is part of the Coquery corpus query tool and cannot be run on its own.""", file=sys.stderr)
    sys.exit(1)    
else:
    logger = logging.getLogger(__init__.NAME)
    Resource = CMUDictResource()
    
    logger.info("Connected to database %s@%s:%s."  % (Resource.db_name, options.cfg.db_host, options.cfg.db_port))
    logger.info("User=%s, password=%s" % (options.cfg.db_user, options.cfg.db_password))            

    if options.cfg.no_cache:
        logger.info("Resetting query cache.")
        Resource.DB.execute("RESET QUERY CACHE")
        Resource.DB.execute("SET SESSION query_cache_type = OFF")

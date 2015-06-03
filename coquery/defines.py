# -*- coding: utf-8 -*-
"""
FILENAME: defines.py -- part of Coquery corpus query tool

This module defines several constants used in different other modules.

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
import glob
import os.path
import imp
import sys
import warnings

# The following flags are used to indicate which fields are provided by the 
# lexicon of a corpus, and also to access the fields of the value of 
# BaseLexicon.get_entry(WordId):

LEX_WORDID = "word_id"  # Lexicon entries provide a WordId (obligatory)
LEX_ORTH = "orth"       # Lexicon entries provide an orthographic 
                        # representation of word-forms (obligatory)
LEX_LEMMA = "lemma"     # Lexicon entries provide a lemma identifier
LEX_POS = "pos"         # Lexicon entries provide a part-of-speech identifier
LEX_PHON = "phon"       # Lexicon entries provide a phonological 
                        # representation
LEX_FREQ = "freq"       # Lexicon entries provide a frequency measure

CORP_SOURCE = "source"
CORP_SPEAKER = "speaker"
CORP_CONTEXT = "context"
CORP_FILENAME = "filename"
CORP_TIMING = "time"
CORP_STATISTICS = "statistics"
CORP_SENTENCE = "sentence"

QUERY_MODE_TOKENS = "TOKEN"
QUERY_MODE_FREQUENCIES = "FREQ"
QUERY_MODE_DISTINCT = "DISTINCT"
QUERY_MODE_STATISTICS = "STATS"

def get_available_resources():
    resources = {}
    for corpus in glob.glob(os.path.join(sys.path[0], "corpora/*.py")):
        corpus_name, ext = os.path.splitext(os.path.basename(corpus))
        module = imp.load_source(corpus_name, corpus)
        try:
            resource = module.Resource
            resources[resource.name.lower()] = (module.Resource, module.Corpus, module.Lexicon)
        except AttributeError:
            warnings.warn("{} does not appear to be a valid resource.".format(corpus_name))
    return resources

available_resources = get_available_resources()
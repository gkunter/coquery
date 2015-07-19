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
import csv, codecs

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

TABLE_CORPUS = "corpus"
TABLE_WORD = "word"
TABLE_LEMMA = "lemma"
TABLE_SOURCE = "source"
TABLE_FILE = "file"
TABLE_SPEAKER = "speaker"

CONTEXT_KWIC = "KWIC"
CONTEXT_STRINGS = "Strings"
CONTEXT_COLUMNS = "Columns"

# from https://docs.python.org/2.7/library/csv.html#csv-examples
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, encoding="utf-8", types=None, **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, **kwds)
        self.types = types
        self.encoding = encoding

    def next(self):
        row = self.reader.next()
        if not self.types:
            return [unicode(s, self.encoding) for s in row]
        else:
            try:
                return [unicode(x, self.encoding) if var_type == unicode else var_type(x) for x, var_type in zip(row, self.types)]
            except ValueError:
                return [unicode(s, self.encoding) for s in row]
    def __iter__(self):
        return self

class UnicodeWriter(object):
    """ Define a class that substitutes the csv writer object in order to
    be friendly to Unicode strings."""
    
    def __init__(self, f, encoding="utf-8", **kwds):
        self.writer = csv.writer(f, **kwds)
        self.encoding = encoding

    def writerow(self, row):
        def encode_string(s):
            if isinstance(s, unicode):
                return s.encode(self.encoding)
            elif isinstance(s, (int, float, long, complex)):
                return s
            elif not isinstance(s, str):
                return str(s)
            return s
        return self.writer.writerow([encode_string(x) for x in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class ResourceList(object):
    def __init__(self):
        self.available_resources = self.get_available_resources()
        
    @property
    def available(self):
        """ Return a list that represents all available corpus modules. Each
        entry in the list is a tuple containing the Resource() class, 
        Corpus() class, Lexicon() class, and the corpus module filename as
        a string."""
        return self.get_available_resources()

    def get_available_resources(self):
        self.available_resources = {}
        corpus_path = os.path.join(sys.path[0], "corpora")
        if not os.path.exists(corpus_path):
            os.makedirs(corpus_path)
        for corpus in glob.glob(os.path.join(corpus_path, "*.py")):
            corpus_name, ext = os.path.splitext(os.path.basename(corpus))
            try:
                module = imp.load_source(corpus_name, corpus)
                resource = module.Resource
                self.available_resources[resource.name.lower()] = (module.Resource, module.Corpus, module.Lexicon, corpus)
            except AttributeError, ImportError:
                warnings.warn("{} does not appear to be a valid corpus module.".format(corpus_name))
        return self.available_resources

def collapse_words(word_list):
    """ Concatenate the words in the word list, taking clitics, punctuation
    and some other stop words into account."""
    stop_words = ["<p>", "<P>"]
    conflate_words = ["n't", "'s", "'ve"]
    token_list = []
    punct = '!\'),-./:;?^_`}’'
    quote_list = ['"', "'"]
    context_list = [x.strip() for x in word_list]
    open_quote = {}
    open_quote ['"'] = False
    open_quote ["'"] = False
    for i, current_token in enumerate(context_list):
        try:
            if '""""' in current_token:
                current_token = '"'
            if current_token not in stop_words:
                if current_token not in punct and current_token not in conflate_words:
                    if i > 0 and context_list[i-1] not in '([{‘':
                        token_list.append(" ")
                token_list.append(current_token)
        except (UnicodeEncodeError, UnicodeDecodeError):
            token_list.append(unicode(current_token.decode("utf-8")))
    return "".join(token_list)
resource_list = ResourceList()


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

#from __future__ import unicode_literals

import glob
import os.path
import imp
import sys
import warnings
import csv, cStringIO, codecs

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

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, **kwds)
        self.stream = f
        self.encoding = encoding
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        try:
            self.writer.writerow([s.encode("utf-8") if type(s) in (unicode, str) else s for s in row])
        except UnicodeDecodeError:
            self.writer.writerow([s for s in row])

        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class ResourceList(object):
    def __init__(self):
        self.available_resources = self.get_available_resources()

    def get_available_resources(self):
        self.available_resources = {}
        for corpus in glob.glob(os.path.join(sys.path[0], "corpora/*.py")):
            corpus_name, ext = os.path.splitext(os.path.basename(corpus))
            try:
                module = imp.load_source(corpus_name, corpus)
                resource = module.Resource
                self.available_resources[resource.name.lower()] = (module.Resource, module.Corpus, module.Lexicon, corpus)
            except AttributeError, ImportError:
                warnings.warn("{} does not appear to be a valid corpus library.".format(corpus_name))
        return self.available_resources

resource_list = ResourceList()


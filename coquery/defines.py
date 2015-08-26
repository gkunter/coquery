# -*- coding: utf-8 -*-
"""
FILENAME: defines.py -- part of Coquery corpus query tool

This module defines several constants used in different other modules.

"""

import glob
import os.path
import imp
import sys
import warnings
import csv, codecs
import math
import itertools

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
QUERY_MODE_COLLOCATIONS = "COLLOCATE"

TABLE_CORPUS = "corpus"
TABLE_WORD = "word"
TABLE_LEMMA = "lemma"
TABLE_SOURCE = "source"
TABLE_FILE = "file"
TABLE_SPEAKER = "speaker"

CONTEXT_KWIC = "KWIC"
CONTEXT_STRING = "String"
CONTEXT_COLUMNS = "Columns"
CONTEXT_SENTENCE = "Sentence"

COLUMN_NAMES = {
    "coq_frequency": "Frequency", 
    "coq_freq_per_milion": "Frequency (pmw)",
    "coq_context_left": "Left context",
    "coq_context_right": "Right context",
    "coq_context_string": "Context",
    "coq_collocate_word_label": "Collocate word",
    "coq_collocate_lemma_label": "Collocate lemma",
    "coq_collocate_pos_label": "Collocate POS",
    "coq_collocate_transcript_label": "Collocate transcript",
    "coq_collocate_frequency": "Collocate frequency",
    "coq_collocate_frequency_left": "Left context frequency",
    "coq_collocate_frequency_right": "Right context frequency",
    "coq_mutual_information": "Mutual information",
    "coq_conditional_probability": "Pcond",

    "coquery_query_string": "Query string"}

# for Python 3 compatibility:
try:
    unicode()
except NameError:
    unicode = str
    long = int

# Error messages used by the GUI:
msg_visualization_no_data = """<p>The 'Query results' view is empty, hence there is nothing to visualize.</p>
<p>You have either not run a query in this session yet, or there are no tokens in the corpus that match your last query.</p>
<p>Try to run a visualization again once the Query results view is not empty anymore.</p>"""
msg_visualization_no_frequency = """<p>No frequency data available.</p>
<p>The visualization that you chose only works with query results from Frequency queries.</p>
<p>Try to change the query mode to 'Frequency', re-run the query, and call the
visualization again.</p>"""
msg_corpus_no_documentation = """<p>No corpus documentation available.</p>
<p>The current corpus module does not provide a link to the corpus
documentation. You may find help on how the corpus is structured by using an
internet search engine.</p>"""


gui_label_query_button = "&Query"
gui_label_stop_button = "&Stop"

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
        if "delimiter" in kwds:
            kwds["delimiter"] = str(kwds["delimiter"])
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
                try:
                    return str(s)
                except UnicodeEncodeError as e:
                    raise e
            return s
        return self.writer.writerow([encode_string(x) for x in row])

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
            except Exception as e:
                warnings.warn("{} could not be loaded.".format(corpus_name))
                warnings.warn("Exception: {}".format(e))
                continue
            resource = module.Resource
            try:
                self.available_resources[resource.name.lower()] = (module.Resource, module.Corpus, module.Lexicon, corpus)
            except (AttributeError, ImportError):
                warnings.warn("{} does not appear to be a valid corpus module.".format(corpus_name))
        return self.available_resources

class FileSize(long):
    """ Define a long class that can store file sizes, and which allows
    custom formatting by using the format specifier S, which displays a 
    human-readable file size with suffixes b, kb, Mb etc.
    Adapted from http://code.activestate.com/recipes/578321-human-readable-filememory-sizes/
    """
    def __format__(self, fmt):
        if self < 0:
            return "(unknown)"
        if fmt == "" or fmt[-1] != "S":
            if fmt[-1].tolower() in ['b','c','d','o','x','n','e','f','g','%']:
                # Numeric format.
                return long(self).__format__(fmt)
            else:
                return str(self).__format__(fmt)

        val, suffixes = float(self), ["b ","Kb","Mb","Gb","Tb","Pb"]
        if val < 1:
            # Can't take log(0) in any base.
            i, v = 0, 0
        else:
            exp = int(math.log(val,1024))+1
            v = val / math.pow(1024, exp)
            # Move to the next bigger suffix when the value is large enough:
            v, exp = (v, exp) if v > 0.5 else (v * 1024, exp - 1)
        return ("{0:{1}f}" + suffixes[exp]).format(v, fmt[:-1])

def dict_product(d):
    """ Create a Cartesian product of the lists stored as values in the
    dictionary 'd'.
    
    This product is useful for example to create a table of all factor level
    combinations. The factor levels can be accessed by the column names. """
    
    cart_product = itertools.product(*d.itervalues())
    
    return (dict(itertools.izip(d, x)) for x in cart_product)


resource_list = ResourceList()


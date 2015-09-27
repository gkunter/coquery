# -*- coding: utf-8 -*-
"""
FILENAME: defines.py -- part of Coquery corpus query tool

This module defines several constants used in different other modules.

"""

from __future__ import unicode_literals

import glob
import os, inspect
import importlib
import sys
import warnings
import csv, codecs
import math
import itertools

import gc
import sys

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

SORT_NONE = 0
SORT_INC = 1
SORT_DEC = 2
SORT_REV_INC = 3
SORT_REV_DEC = 4

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

    "coquery_query_token": "Query token",
    "coquery_expanded_query_string": "Expanded query string",
    "coquery_query_string": "Query string"}

# for Python 3 compatibility:
try:
    unicode()
except NameError:
    # Python 3 does not have unicode and long, so define them here:
    unicode = str
    long = int
    
# Error messages used by the GUI:
msg_corpus_no_documentation = """<p>No corpus documentation available.</p>
<p>The current corpus module does not provide a link to the corpus
documentation. You may find help on how the corpus is structured by using an
internet search engine.</p>"""
msg_install_abort = """<p>You have requested to abort the installation.</p>
<p>The installation has not been completed yet. If you abort now, the data 
installed so far will be discarded, and the corpus will still not be available
for queries.</p>"""
msg_corpus_broken = """Error reading the installer '{name}'

The corpus installer stored in the file {name} could not be read. Most likely, there is a programming error in the installer, or the file could not be read. 

Please inform the maintainer of this corpus installer of your problem. When doing so, include the following information in your message:

{type}
{code}"""

gui_label_query_button = "&Query"
gui_label_stop_button = "&Stop"

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


#resource_list = ResourceList()

def memory_dump():
    x = 0
    for obj in gc.get_objects():
        i = id(obj)
        size = sys.getsizeof(obj, 0)
        # referrers = [id(o) for o in gc.get_referrers(obj)]
        try:
            cls = str(obj.__class__)
        except:
            cls = "<no class>"
        if size > 1024 * 50:
            referents = set([id(o) for o in gc.get_referents(obj)])
            x += 1
            print(x, {'id': i, 'class': cls, 'size': size, "ref": len(referents)})
            #if len(referents) < 2000:
                #print(obj)

def get_available_resources():
    """ 
    Return a dictionary with the available corpus module resource classes
    as values, and the corpus module names as keys.
    
    This method scans the content of the sub-directory 'corpora' for valid
    corpus modules. If a corpus module is found, the three resource classes
    Resource, Corpus, and Lexicon are retrieved from the module.
    
    Returns
    -------
    d : dict
        A dictionary with resource names as keys, and tuples of resource
        classes as values.
    """
    d  = {}
    
    corpus_path = os.path.realpath(
        os.path.abspath(
            os.path.join(
                sys.path[0], "corpora")))
    if not os.path.exists(corpus_path):
        os.makedirs(corpus_path)

    for corpus in glob.glob(os.path.join(corpus_path, "*.py")):
        corpus_name, ext = os.path.splitext(os.path.basename(corpus))
        try:
            module = importlib.import_module("corpora.{}".format(corpus_name))
        except SyntaxError as e:
            warnings.warn("There is a syntax error in corpus module {}. Please remove this corpus module, and reinstall it afterwards.".format(corpus_name))
            raise e
        try:
            d[module.Resource.name.lower()] = (module.Resource, module.Corpus, module.Lexicon, corpus)
        except (AttributeError, ImportError):
            warnings.warn("{} does not appear to be a valid corpus module.".format(corpus_name))
    return d

def get_resource(name):
    """
    Return a tuple containing the Resource, Corpus, and Lexicon of the 
    corpus module specified by 'name'.
    
    Arguments
    ---------
    name : str
        The name of the corpus module
        
    Returns
    -------
    res : tuple
        A tuple consisting of the Resource class, Corpus class, and Lexicon 
        class defined in the corpus module
    """
    Resource, Corpus, Lexicon, _ = get_available_resources()[name]
    return Resource, Corpus, Lexicon
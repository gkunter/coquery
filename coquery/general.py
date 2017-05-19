# -*- coding: utf-8 -*-
"""
general.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import hashlib
import sys
import os
import tempfile
import itertools
import pandas as pd

from .unicode import utf8
from .defines import LANGUAGES

CONTRACTION = ["n't", "'s", "'ve", "'m", "'d", "'ll", "'em", "'t"]
PUNCT = '!\'),-./:;?^_`}’”]'

HTML_ESCAPE_TABLE = [
     ("&", "&amp;"),
     ('"', "&quot;"),
     ("'", "&apos;"),
     (">", "&gt;"),
     ("<", "&lt;")
     ]


def html_escape(text):
    for old, new in HTML_ESCAPE_TABLE:
        if old in text:
            text = text.replace(old, new)
    return text

def collapse_words(word_list):
    """ Concatenate the words in the word list, taking clitics, punctuation
    and some other stop words into account."""
    def is_tag(s):
        # there are some tags that should still be preceded by spaces. In
        # paricular those that are normally used for typesetting, including
        # <span>, but excluding <sup> and <sub>, because these are frequently
        # used in formula:

        if s.startswith("<span") or s.startswith("</span"):
            return False
        if s in set(["</b>", "<b>", "</i>", "<i>", "</u>", "<u>",
                     "</s>", "<s>", "<em>", "</em>"]):
            return False
        return s.startswith("<") and s.endswith(">") and len(s) > 2

    token_list = []
    context_list = [x.strip() if hasattr(x, "strip") else x
                    for x in word_list]
    open_quote = {}
    open_quote['"'] = False
    open_quote["'"] = False
    open_quote["``"] = False
    last_token = ""
    for current_token in context_list:
        if (current_token and
                not (isinstance(current_token, float) and
                     pd.np.isnan(current_token))):
            if '""""' in current_token:
                current_token = '"'

            # stupid list of exceptions in which the current_token should NOT
            # be preceded by a space:
            no_space = False
            if all([x in PUNCT for x in current_token]):
                no_space = True
            if current_token in CONTRACTION:
                no_space = True
            if last_token in '({[‘“':
                no_space = True
            if is_tag(last_token):
                no_space = True
            if is_tag(current_token):
                no_space = True
            if last_token.endswith("/"):
                no_space = True

            if current_token == "``":
                no_space = False
                open_quote["``"] = True
            if current_token == "''":
                open_quote["``"] = False
                no_space = True
            if last_token == "``":
                no_space = True

            if not no_space:
                token_list.append(" ")

            token_list.append(current_token)
            last_token = current_token
    return utf8("").join(token_list)


def check_fs_case_sensitive(path):
    """
    Check if the file system is case-sensitive.
    """
    with tempfile.NamedTemporaryFile(prefix="tMp", dir=path) as temp_path:
        return not os.path.exists(temp_path.lower())


def get_home_dir(create=True):
    """
    Return the path to the Coquery home directory. Also, create all required
    directories.

    The coquery_home path points to the directory where Coquery stores (and
    looks for) the following files:

    $COQ_HOME/coquery.cfg               configuration file
    $COQ_HOME/coquery.log               log files
    $COQ_HOME/binary/                   default directory for binary data
    $COQ_HOME/installer/                additional corpus installers
    $COQ_HOME/connections/$SQL_CONFIG/corpora
                                        installed corpus modules
    $COQ_HOME/connections/$SQL_CONFIG/adhoc
                                        adhoc installer modules
    $COQ_HOME/connections/$SQL_CONFIG/databases
                                        SQLite databases

    The location of $COQ_HOME depends on the operating system:

    Linux           either $XDG_CONFIG_HOME/Coquery or ~/.config/Coquery
    Windows         %APPDATA%/Coquery
    Mac OS X        ~/Library/Application Support/Coquery
    """

    if sys.platform.startswith("linux"):
        try:
            basepath = os.environ["XDG_CONFIG_HOME"]
        except KeyError:
            basepath = os.path.expanduser("~/.config")
    elif sys.platform in set(("win32", "cygwin")):
        try:
            basepath = os.environ["APPDATA"]
        except KeyError:
            basepath = os.path.expanduser("~")
    elif sys.platform == "darwin":
        basepath = os.path.expanduser("~/Library/Application Support")
    else:
        raise RuntimeError("Unsupported operating system: {}".format(
            sys.platform))

    coquery_home = os.path.join(basepath, "Coquery")
    connections_path = os.path.join(coquery_home, "connections")
    binary_path = os.path.join(coquery_home, "binary")
    custom_installer_path = os.path.join(coquery_home, "installer")

    if create:
        # create paths if they do not exist yet:
        for path in [coquery_home, custom_installer_path, connections_path,
                     binary_path]:
            if not os.path.exists(path):
                os.makedirs(path)

    return coquery_home


class CoqObject(object):
    """
    This class is a subclass of the default Python ``object`` class. It adds
    the method ``get_hash()``, which returns a hash based on the current
    instance attributes.
    """
    def get_hash(self):
        l = []
        dir_super = dir(super(CoqObject, self))
        for x in sorted([x for x in dir(self) if x not in dir_super]):
            if (not x.startswith("_") and
                    not hasattr(getattr(self, x), "__call__")):
                attr = getattr(self, x)
                # special handling of containers:
                if isinstance(attr, (set, dict, list, tuple)):
                    s = str([x.get_hash()
                             if isinstance(x, CoqObject) else str(x)
                             for x in attr])
                    l.append(s)
                else:
                    l.append(str(attr))
        return hashlib.md5(u"".join(l).encode()).hexdigest()


def get_visible_columns(df, manager, session, hidden=False):
    """
    Return a list with column names from the data frame.

    Internal columns, i.e. those whose name starts with the string
    'coquery_invisible', are never returned. The parameter 'hidden' controls
    if columns hidden by the data manager are included.

    Parameters
    ----------
    manager : Manager object
        The currently active manager.

    session : Session object
        The currently active session.

    hidden : bool
        True if columns hidden by the manager are included. False if columns
        hidden by the manager are excluded.
    """
    if hidden:
        l = [x for x in list(df.columns.values)
             if not x.startswith("coquery_invisible_")]
    else:
        l = [x for x in list(df.columns.values)
             if (not x.startswith("coquery_invisible_") and
                 x not in manager.hidden_columns)]

    #l = set_preferred_order(l)
    return l

def set_preferred_order(l, session):
    """
    Arrange the column names in l so that they occur in the preferred order.

    Columns not in the preferred order follow in an unspecified order.
    """

    resource_order = session.Resource.get_preferred_output_order()
    for x in resource_order[::-1]:
        lex_list = [y for y in l if x in y]
        lex_list = sorted(lex_list)[::-1]
        for lex in lex_list:
            l.remove(lex)
            l.insert(0, lex)
    return l


def is_language_name(code):
    return code in LANGUAGES["Language name"].values()


def is_language_code(code):
    return code in LANGUAGES["639-1"].values()


def language_by_code(code):
    ix = dict(zip(LANGUAGES["639-1"].values(),
                  LANGUAGES["639-1"].keys()))[code]
    return LANGUAGES["Language name"][ix]


def native_language_by_code(code):
    ix = dict(zip(LANGUAGES["639-1"].values(),
                  LANGUAGES["639-1"].keys()))[code]
    return LANGUAGES["Native name"][ix]


def code_by_language(code):
    ix = dict(zip(LANGUAGES["Language name"].values(),
                  LANGUAGES["Language name"].keys()))[code]
    return LANGUAGES["639-1"][ix]


def get_chunk(iterable, chunk_size=250000):
    """
    Yield a chunk from the big file given as 'iterable'.

    This function is based on a rather elegant solution posted on Stack
    Overflow: http://stackoverflow.com/a/24862655
    """
    iterable = iter(iterable)
    while True:
        yield itertools.chain(
            [next(iterable)],
            itertools.islice(iterable, chunk_size - 1))


# Memory status functions:

def memory_dump():
    import gc
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
            print(x, {'id': i,
                      'class': cls,
                      'size': size,
                      "ref": len(referents)})
            #if len(referents) < 2000:
                #print(obj)

try:
    from pympler import summary, muppy
    import psutil

    def summarize_memory():
        print("Virtual machine: {:.2f}Mb".format(
            psutil.Process().memory_info_ex().vms / (1024 * 1024)))
        summary.print_(summary.summarize(muppy.get_objects()), limit=1)
except Exception as e:
    def summarize_memory():
        print("summarize_memory: {}".format(lambda: str(e)))

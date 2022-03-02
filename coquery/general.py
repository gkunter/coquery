# -*- coding: utf-8 -*-
"""
general.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""


import math
import hashlib
import sys
import os
import tempfile
import itertools
import pandas as pd
import numpy as np
import io
import ctypes
import logging

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


def has_module(name):
    """
    Check if the Python module 'name' is available.

    Parameters
    ----------
    name : str
        The name of the Python module, as used in an import instruction.

    This function uses ideas from this Stack Overflow question:
    http://stackoverflow.com/questions/14050281/

    Returns
    -------
    b : bool
        True if the module exists, or False otherwise.
    """

    if sys.version_info > (3, 3):
        import importlib.util
        return importlib.util.find_spec(name) is not None
    elif sys.version_info > (2, 7, 99):
        import importlib
        return importlib.find_loader(name) is not None
    else:
        import pkgutil
        return pkgutil.find_loader(name) is not None


class Collapser(object):
    """
    Provides a language-specific way to collapse a list of word tokens into a
    single string.
    """

    whitespace = " "

    @classmethod
    def tag_spacing(cls, s):
        """
        Return a string that contains appropriate whitespaces around certain
        XML tags.

        Some tags are typically used for typesetting, such as <b> or <i>. These
        tags should be preceded by a whitespace. In the case of the
        corresponding closing tag, the tag should be followed by a whitespace.

        If the string does not contain a tag that is recognized, the return
        value is identical to the input value.
        """
        if s in {"<b>", "<u>", "<s>", "<em>"} or s.startswith("<span"):
            return f"{cls.whitespace}{s}"
        elif s in {"</b>", "</u>", "</s>", "</em>"} or s.startswith("</span"):
            return f"{s}{cls.whitespace}"
        return s

    @classmethod
    def _collapse_list(cls, word_list):
        lst = []
        for s in word_list:
            lst += [cls.whitespace, cls.tag_spacing(s)]
        return lst

    @classmethod
    def collapse(cls, word_list):
        if not isinstance(word_list, pd.Series):
            word_list = pd.Series(word_list)
        # return None if the word list contains only None:
        if word_list.isnull().sum() == len(word_list):
            val = None
        else:
            lst = cls._collapse_list(word_list)
            val = utf8("").join(lst).strip()
        return val


class EnglishCollapser(Collapser):
    CLITICS = {"#s", "#re", "#m", "#ve", "#d", "#ll", "#t", "n#t"}
    CONTRACTION_PUNCTUATION = ("'", "\N{RIGHT SINGLE QUOTATION MARK}",
                               "\N{MODIFIER LETTER APOSTROPHE}")
    CONTRACTIONS = []
    for p in CONTRACTION_PUNCTUATION:
        for c in CLITICS:
            CONTRACTIONS.append(c.replace("#", p))

    NONSPACING_PUNCTUATION = (".", ",", ":", ";", "?", "!",
                              ")", "}", "]",
                              "%")
    NONTRAILING_PUNCTUATION = ("(", "{", "[")
    CONJOINING_PUNCTUATION = ("\N{EM DASH}")

    QUOTE_PAIRS = (("\N{LEFT SINGLE QUOTATION MARK}",
                    "\N{RIGHT SINGLE QUOTATION MARK}"),
                   ("\N{LEFT DOUBLE QUOTATION MARK}",
                    "\N{RIGHT DOUBLE QUOTATION MARK}"),
                   ("'", "'"),
                   ('"', '"'),
                   ("\N{GRAVE ACCENT}\N{GRAVE ACCENT}",
                    "\N{ACUTE ACCENT}\N{ACUTE ACCENT}"),
                   ("\N{GRAVE ACCENT}\N{GRAVE ACCENT}", "''"),
                   ("\N{GRAVE ACCENT}", "\N{ACUTE ACCENT}"))

    @classmethod
    def _corresponding_openers(cls, closer):
        lst = []
        for o, c in cls.QUOTE_PAIRS:
            if c == closer:
                lst.append(o)
        return lst

    @classmethod
    def _corresponding_closers(cls, opener):
        lst = []
        for o, c in cls.QUOTE_PAIRS:
            if o == opener:
                lst.append(c)
        return lst

    @classmethod
    def _collapse_list(cls, word_list):
        """
        Take the element from the word list and concatenate them into a string
        with whitespaces corresponding to English spelling conventions.

        This is not a function that I'm proud of, especially when it comes to
        quotation marks. The general idea is that the algorithm goes through
        the list element by element. For each element, it adds a separator
        and the element itself to a list. The value of the separator depends on
        the element itself, but can also be affected by the previous element in
        the list.

        For elements like contracted forms like 've or 's, the separator is
        empty because here, the element is expected to be attached to the
        previous element.

        For elements like opening brackets, the separator for the NEXT
        separator is set to be empty, because here, the current element (i.e.
        the opening bracket) and the next element are expected to be attached
        to each other.

        For elements that may be quote-closing sequences, the algorithm tries
        to determine whether a matching quote-opening sequence has already been
        encountered. In this case, the value of the separator is set to empty,
        because the closing sequence is expected to be attached to the previous
        element.

        If the element is not a quote-closing sequence, the algorithm checks if
        if may be a quote-opening sequence. In this case, the NEXT separator is
        set to be empty because quote-opening sequences are expected to be
        attached to the following element.

        The algorithm corrects some cases of broken quotation sequences. A
        broken quotation sequence is one where the quotation punctuation is not
        correctly tokenized, i.e. where the punctation is still attached to the
        token, as in <word'>, <"happy>, etc. These tokens will be treated as if
        they consisted of a sequence of the token and the punctuation mark.

        This correction was, I hate to say it, developed in a trial-and-error
        fashion. As a result, the code may not be as clear as you'd hope. Any
        change to this function therefore needs to be tested very thoroughly by
        running the tests from the test suite!
        """
        lst = []
        next_sep = cls.whitespace

        opening, closing = zip(*cls.QUOTE_PAIRS)
        quote_stack = []

        for word in word_list:
            # per default, words will be joined using the language's
            # whitespace:
            sep = next_sep
            next_sep = cls.whitespace
            lw = word.lower()

            closer_found = False
            ignore_openers = False

            # handle punctuation, contractions and clitics:
            if (lw in cls.CONTRACTIONS):
                sep = ""
                ignore_openers = True
            elif lw in cls.NONSPACING_PUNCTUATION:
                sep = ""
            elif lw in cls.NONTRAILING_PUNCTUATION:
                next_sep = ""
            elif lw.startswith(cls.CONJOINING_PUNCTUATION):
                sep = ""
                next_sep = ""
                if lst and lst[-1] == cls.whitespace:
                    lst[-1] = ""

            # check if the current element ends in an element which may be a
            # quote-closing sequence:
            elif lw.endswith(tuple(closing)):
                if not quote_stack:
                    closer_found = lw in closing
                for closer in closing:
                    if lw.endswith(closer):
                        # check if no corresponding quote-opening sequence was
                        # previously encountered:
                        if not quote_stack:
                            # don't treat this element as a quote-closing
                            # sequence if there is a regular token attached to
                            # it:
                            closer_found = closer != lw
                            break

                        # check if there are quote-opening sequences that may
                        # be a match for the current quote-closing sequence:
                        matching_openers = cls._corresponding_openers(closer)
                        for i, stack_element in enumerate(quote_stack):
                            if stack_element in matching_openers:
                                # if a match is found, remove the quote-opening
                                # sequence from the stack, and treat this
                                # element as a quote-closing sequence.
                                quote_stack = quote_stack[i:]
                                sep = ""
                                closer_found = True
                                break

            # check if the current element is not treated as a quote-closing
            # sequence or a clitic element (or similar):
            if not closer_found and not ignore_openers:
                # check if the current element may be a quote-opening sequence:
                if lw.startswith(tuple(opening)):
                    if lw in opening:
                        next_sep = ""
                    # add the quote-opening sequence to the stack:
                    for opener in opening:
                        if lw.startswith(opener):
                            quote_stack.insert(0, opener)
                            break

            # add the current separator value and the current element to the
            # final list:
            lst += [sep, cls.tag_spacing(word)]

        return lst


def collapser_factory(language):
    mapping = {"en": EnglishCollapser}
    return mapping.get(language, Collapser)


def collapse_words(word_list, language=None):
    """ Concatenate the words in the word list, taking clitics, punctuation
    and some other stop words into account."""
    return collapser_factory(language).collapse(word_list)


def check_fs_case_sensitive(path):
    """
    Check if the file system is case-sensitive.
    """
    try:
        with tempfile.NamedTemporaryFile(prefix="tMp", dir=path) as temp_path:
            return not os.path.exists(temp_path.name.lower())
    except PermissionError:
        return sys.platform.startswith("linux")


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
    elif sys.platform in {"win32", "cygwin"}:
        try:
            basepath = os.environ["APPDATA"]
        except KeyError:
            basepath = os.path.expanduser("~")
    elif sys.platform == "darwin":
        basepath = os.path.expanduser("~/Library/Application Support")
    else:
        raise RuntimeError(f"Unsupported operating system: {sys.platform}")

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
        lst = [self.__class__.__name__]
        dir_super = dir(super(CoqObject, self))
        for x in sorted([x for x in dir(self) if x not in dir_super]):
            _session_removed = False
            if x == "kwargs":
                if "session" in getattr(self, "kwargs"):
                    session = getattr(self, "kwargs")["session"]
                    _session_removed = True
                    getattr(self, "kwargs").pop("session")
            if (not x.startswith("_") and
                    not hasattr(getattr(self, x), "__call__")):
                attr = getattr(self, x)
                # special handling of containers:
                if isinstance(attr, (set, list, tuple)):
                    s = str([x.get_hash()
                             if isinstance(x, CoqObject) else str(x)
                             for x in attr])
                    lst.append(s)
                elif isinstance(attr, dict):
                    for key in sorted(attr.keys()):
                        val = attr[key]
                        if isinstance(val, CoqObject):
                            lst.append(f"{x}{val.get_hash()}")
                        else:
                            lst.append(f"{x}{str(val)}")
                else:
                    lst.append(str(attr))
            if _session_removed:
                getattr(self, "kwargs")["session"] = session

        return hashlib.md5(u"".join(lst).encode()).hexdigest()


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


def sha1sum(path, chunk_size=io.DEFAULT_BUFFER_SIZE):
    """
    Calculate a SHA1 checksum for the given file.

    This function is based on https://stackoverflow.com/a/40961519/5215507 by
    Laurent LAPORTE.
    """
    sha1 = hashlib.sha1()
    with io.open(path, mode="rb") as input_file:
        for chunk in iter(lambda: input_file.read(chunk_size), b''):
            sha1.update(chunk)
    return sha1


def get_chunk(iterable, chunk_size=250000):
    """
    Yield a chunk from the big file given as 'iterable'.

    This function is based on a rather elegant solution posted on Stack
    Overflow: http://stackoverflow.com/a/24862655
    """
    iterable = iter(iterable)
    while True:
        try:
            yield itertools.chain(
                [next(iterable)],
                itertools.islice(iterable, chunk_size - 1))
        except StopIteration:
            return


def get_directory_size(path):
    total_size = 0
    for dir_path, _, files in os.walk(path):
        for file_name in files:
            try:
                size = os.path.getsize(os.path.join(dir_path, file_name))
            except Exception as e:
                print(e)
            else:
                total_size += size
    return total_size


def get_available_space(path):
    """
    Return available folder/drive space.

    This function is based on https://stackoverflow.com/a/2372171
    """
    if sys.platform == "win32":
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(path)
        return st.f_bavail * st.f_frsize


def format_file_size(size):
    if size == 0:
        power = 0
    else:
        power = math.floor(math.log2(abs(size)) / 10)
    unit = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'][power]
    return "{:0.1f} {}".format(size / 1024 ** power, unit)


def recycle(data, n, limit=None):
    """
    Recycle the data to return a list with n elements. If limit is not None,
    only the elements up to that value are used.
    """
    if limit:
        return (data[:limit] * (1 + n // limit))[:n]
    else:
        return (data * (1 + n // len(data)))[:n]


def pretty(vrange, n, endpoint=False):
    """
    Return a range of prettified values.

    Parameters
    ----------
    vrange : tuple
        A tuple (x, y) with x being the lower and y the upper end of the
        range

    n : int
        The number of values to be generated

    endpoint : bool
        If True, the list includes the prettified upper end of the range. If
        False (the default), the upper end is not included.

    Returns
    -------
    l : list
        A list with n equidistant values ranging from a prettified floor to a
        prettified ceiling
    """
    vmin, vmax = vrange

    if vmin > vmax:
        return pretty((vmax, vmin), n)

    exp = None
    exp_max = None
    exp_min = None

    if vmin >= 0 and vmax <= 1:
        exp = abs(np.ceil(np.log10(abs(vmax))) + 2)

        niced_min = np.floor(vmin * 10 ** exp) / 10 ** exp
        niced_max = np.ceil(vmax * 10 ** exp) / 10 ** exp
    elif vmin != 0:
        # limit the exponent of the lower boundary so that it does not exceed
        # three, i.e. only the lowest three digits will be cleared (this may
        # need revision):
        exp_min = min(np.floor(np.log10(abs(vmin))), 3)

        pretty_min = np.floor(vmin / 10 ** exp_min) * 10 ** exp_min
        exp_max = np.ceil(np.log10(abs(vmax - pretty_min)))
        exp = exp_max - exp_min

        pretty_min = np.floor(vmin / 10 ** exp) * 10 ** exp
        return pretty((0, vmax - pretty_min), n) + pretty_min

    else:
        exp = np.floor(np.log10(abs(vmax)))

        if np.floor(10 ** exp) < vmax < np.floor(1.5 * 10 ** exp):
            # Special case for ranges such as (0, 125) or any multiple by
            # ten: use   (0, 150) as boundary
            # instead of (0, 200)
            fiver_offset = 5 * 10 ** (exp - 1)

            niced_min = fiver_offset if vmin > fiver_offset else 0
            niced_max = 1.5 * 10 ** exp
        else:
            niced_min = np.floor(vmin / 10 ** exp) * 10 ** exp
            niced_max = np.ceil(vmax / 10 ** exp) * 10 ** exp

    val = np.linspace(niced_min, niced_max, n, endpoint=endpoint)
    return val


def memory_dump():
    """
    Dump a list of 'large' objects (i.e. larger than 50Kbyte) to stdout.
    """
    import gc
    x = 0
    for obj in gc.get_objects():
        i = id(obj)
        size = sys.getsizeof(obj, 0)
        # referrers = [id(o) for o in gc.get_referrers(obj)]
        try:
            cls = str(obj.__class__)
        except Exception:
            cls = "<no class>"
        if size > 1024 * 25:
            referents = set([id(o) for o in gc.get_referents(obj)])
            x += 1
            print(x, "{id:5} {id} {class} {ref}".format(
                **{'id': i, 'class': cls, 'size': size,
                   'len': len(obj), "ref": len(referents)}))
            if len(obj) > 1:
                if hasattr(obj, "items"):
                    if "__module__" in obj:
                        print("\tMODULE", obj["__module__"])
                    else:
                        print(list(obj.items())[:5])
                else:
                    try:
                        print(list(obj)[:5])
                    except Exception:
                        pass


def Print(*args, **kwargs):
    from .options import cfg
    if cfg.verbose:
        logging.debug(*args, **kwargs)


try:
    from pympler import summary, muppy
    import psutil

    def summarize_memory():
        print("Virtual machine: {:.2f}Mb".format(
            psutil.Process().memory_info_ex().vms / (1024 * 1024)))
        summary.print_(summary.summarize(muppy.get_objects()), limit=1)
except Exception as e:
    def summarize_memory(msg=str(e)):
        print("summarize_memory: {}".format(msg))


def uniques(S):
    """
    Get unique levels of Series by discarding NAs and then sorting
    the unique values.

    This function is much more efficient (but less transparent) than
    the equivalent sorted(S.dropna().unique().values()).
    """
    return sorted(set(S.values[~pd.isnull(S.values)]))
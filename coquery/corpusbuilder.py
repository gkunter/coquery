# -*- coding: utf-8 -*-
"""
corpusbuilder.py is part of Coquery.

Copyright (c) 2016-2021 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function

import getpass
import codecs
import logging
import collections
from io import BytesIO
import os.path
import warnings
import time
import pandas as pd
import re
import sys
import fnmatch
import inspect
from lxml import etree as ET

from . import sqlwrap
from . import options
from . import corpus
from .tables import Column, Identifier, Link, Table

from .errors import DependencyError, get_error_repr
from .defines import (SQL_MYSQL,
                      DEFAULT_MISSING_VALUE,
                      QUERY_ITEM_GLOSS, QUERY_ITEM_LEMMA,
                      QUERY_ITEM_TRANSCRIPT, QUERY_ITEM_POS,
                      QUERY_ITEM_WORD,
                      msg_nltk_tagger, msg_nltk_tagger_fallback)
from .unicode import utf8
from .general import check_fs_case_sensitive

"""
The module :mod:`corpusbuilder.py` provides the framework for corpus module
installers.

Different corpora may use different file formats and different file
layouts to provide the content of the corpus to the users. In order to
make this content available to Coquery, the content of the corpus files
must be processed, and stored in a database. Once this has been done,
a corpus module, containing information on the database layout, will be
written to a place where Coquery can find it. After that, the corpus
can be queried by Coquery.

Thus, in order to use a new corpus with Coquery, a subclass of
:class:`BaseCorpusBuilder` needs to be defined that is tailored to the
structure of that corpus. The name of this subclass has to be
:class:`BuilderClass`. Usually, such a subclass will at least
reimplement :func:`BaseCorpusBuilder.__init__`.. The reimplementation
contains the specifications for the data tables such as the name and data
type of the columns. It also specifies links between different data tables.
Please note that the reimplemented :func:`__init__`` should start with a
call to the inherited initialization method, like so::

    super(BuilderClass, self).__init__(gui)

In addition to that, most subclasses will also reimplement either
:func:`BaseCorpusBuilder.process_file` or one of the related methods (e.g.
:func:`BaseCorpusBuilder.process_text_file`. The reimplemented method is
aware of the data format that is used in the corpus data files, and is
therefore able to process the information stored in the data files. It is
responsible for storing the information correctly in the pertaining data
tables defined in :func:`BaseCorpusBuilder.__init__`.

Examples
--------
For examples of reimplementations of ``BaseCorpusBuilder``, see the
corpus installers distributed in the Coquery default installation. For
instance, :mod:`coq_install_generic.py` is a generic installer that process
any collection of text files in a directiory into a query-able corpus, and
:mod:`coq_install_bnc.py` contains an installer that reads and processes the
XML version of the British National Corpus.
"""

insert_cache = collections.defaultdict(list)

new_code_str = """
    @staticmethod
    def get_name():
        return "{name}"

    @staticmethod
    def get_db_name():
        return "{db_name}"

    @staticmethod
    def get_title():
        return "{name}: a {is_tagged_corpus}"

    _is_adhoc = True

    @staticmethod
    def get_description():
        return ['''{description}''']
    """


def disambiguate_label(base, lst):
    """
    Returns a label that is based on the string 'base' and which is not already
    contained in the list 'lst'.

    Disambiguation is done by adding a number if needed. This method is not
    case-sensitive.
    """
    i = 0
    label = base
    lst = [s.lower() for s in lst]
    while True:
        if label.lower() in lst:
            i = i + 1
            label = "{}{}".format(base, i)
        else:
            return label


def to_enum(lst, allow_null=False, normalize_strings=True):
    """
    Returns a string that represents the values of `lst` as a valid SQL ENUM
    declaration.

    Parameters
    ---------
    allow_null : bool
        Allow NULL values in the enum (default: False)

    normalize_strings : bool
        Replace occurrences of single quotation marks by double quotation
        marks so that the output string is a valid SQL representation of the
        list values (default: True)

    Returns
    -------
    enum_str : str
        A string containing a valid SQL ENUM type declaration
    """
    null_str = "" if allow_null else " NOT NULL"
    if normalize_strings:
        lst = [x.replace("'", "''") for x in lst]
    return "ENUM({}){}".format(
        ",".join(["'{}'".format(x) for x in lst]),
        null_str)


new_doc_string = """
This corpus installer was generated by the corpus query tool Coquery
(http://www.coquery.org).
"""


# module_code contains the Python skeleton code that will be used to write
# the Python corpus module.
module_code = """# -*- coding: utf-8 -*-
#
# FILENAME: {file_name} -- a corpus module for the Coquery corpus query tool
#
# This module was automatically created by corpusbuilder.py.
#

from __future__ import unicode_literals
from coquery.corpus import *


class Resource(SQLResource):
    name = '{name}'
    display_name = '{display_name}'
    db_name = '{db_name}'
    url = '{url}'
{variables}
{resource_code}


class Corpus(CorpusClass):
    '''
    Corpus-specific code
    '''
{corpus_code}
"""


class BaseCorpusBuilder(corpus.SQLResource):
    """
    This class is the base class used to build and install a corpus for
    Coquery. For corpora currently not supported by Coquery, new builders
    can be developed by subclassing this class.
    """
    module_code = None
    name = None
    table_description = None

    arguments = None
    parser = None
    DB = None
    additional_stages = []
    auto_create = []
    start_time = None
    file_filter = None
    encoding = "utf-8"
    expected_files = []
    lexical_features = []
    annotations = {}
    # special files are expected files that will not be stored in the file
    # table. For example, a corpus may include a file with speaker
    # information which needs to be evaluated during installation, and which
    # therefore has to be in the expected_files list, but which does not
    # contain token information, and therefore should not be stored as a
    # source file.
    special_files = []
    __version__ = "1.0"
    # file that contains meta data (only applicable in user corpora):
    meta_data = ""

    _read_file_formatter = "Reading {file} (%v of %m)..."

    def __init__(self, gui=None, *args):
        self.module_code = module_code
        self.table_description = {}
        self._time_features = []
        self._lexical_features = []
        self._speaker_features = []
        self._audio_features = []
        self._image_features = []
        self._video_features = []
        self._annotations = {}
        self._id_count = {}
        self._primary_keys = {}
        self._interrupted = False
        self._new_tables = {}

        self._corpus_buffer = None
        self._corpus_id = 0
        self._widget = gui
        self._file_list = []

        self._source_count = collections.Counter()

        # auto-create tables for which the variables TAB_table and
        # TAB_columns exists (with TAB being the name of the table):
        for x in self.auto_create:
            table = getattr(self, f"{x}_table", None)
            columns = getattr(self, f"{x}_columns", None)
            if not table:
                logging.warning(f"Could not find a table name for '{x}'")
            elif not columns:
                logging.warning(f"No columns specified for table '{table}'")
            else:
                self.create_table_description(table, columns)

    def get_table_names(self, **kwargs):
        """
        Return a list of tables that are specified in this corpus builder.

        The returned list represents the internal resource name, not the
        table name that is visible to the user. For example, for the SQL table
        that is specified by the following line to be named 'Lexicon', the
        list returned by this method will contain the string 'word', not
        'Lexicon':

        word_table = "Lexicon"

        :param **kwargs: Not used
        """
        lst = []
        for x in dir(self):
            name, _, field = x.partition("_")
            if field == "table" and not inspect.ismethod(getattr(self, x)):
                lst.append(name)
        return lst

    def add_tag_table(self, features_only=False):
        """
        Create the table description for a tag table.

        Corpora should usually have a tag table that is used to store
        text information. This method is called during :func:`build` and
        adds a tag table if none is present yet.
        """
        cls = type(self)
        cls.tag_table = "tags"
        cls.tag_id = "TagId"
        cls.tag_label = "Tag"
        cls.tag_type = "Type"
        cls.tag_corpus_id = self.corpus_id
        cls.tag_attribute = "Attribute"

        if not features_only:
            self.create_table_description(
                    self.tag_table,
                    [Identifier(self.tag_id, "MEDIUMINT UNSIGNED NOT NULL"),
                     Column(self.tag_type, "ENUM('open', 'close', 'empty')"),
                     Column(self.tag_label, "VARCHAR(1024) NOT NULL"),
                     Link(self.tag_corpus_id, self.corpus_table),
                     Column(self.tag_attribute, "VARCHAR(4048) NOT NULL")])

    def interrupt(self):
        """
        Interrupt the builder.

        Calling this method will interrupt the current building or
        installation process. All data written so far to the database will
        be discarded, and no corpus module will be written.

        In particular, this method is called in the GUI if the Cancel button
        is pressed.
        """
        self._interrupted = True

    @property
    def interrupted(self):
        return self._interrupted

    def check_arguments(self):
        """ Check the command line arguments. Add defaults if necessary."""
        return

    def commit_data(self):
        """
        Commit any corpus data that is still stored only in the internal
        tables to the database.

        :func:`commit_data` is usually called for each file after the content
        has been processed.

        """
        if self.interrupted:
            return

        for table in self._new_tables:
            self._new_tables[table].commit()

        if self._corpus_buffer:
            df = pd.DataFrame(self._corpus_buffer)
            df.to_sql(self.corpus_table,
                      self.DB.engine,
                      if_exists="append",
                      index=False)
            self._corpus_buffer = []

    def create_table_description(self, table_name, column_list):
        """
        Create the description of a MySQL table. The MySQL table described
        in this way will be created during :func:`build` by calling
        :func:`build_create_table`.

        Parameters
        ----------
        table_name : string
            The name of the MySQL table
        column_list : list
            A list of :class:`Column` instances
        """
        new_table = Table(table_name)
        for x in column_list:
            if isinstance(x, Link):
                try:
                    x.data_type = self._new_tables[x._link].primary.data_type
                except KeyError:
                    S = (f"Table description for '{table_name}' contains a"
                         f" link to unknown table '{x._link}'")
                    raise KeyError(S)
            try:
                new_table.add_column(x)
            except ValueError as e:
                print(table_name, x)
                raise e
        self._new_tables[table_name] = new_table

    def table(self, table_name):
        """
        Return a Table object matching the specified name.

        Parameters
        ----------
        table_name : string
            The name of the table

        Returns
        -------
        table : object
            A Table object, or None if there is no table of the given name
        """
        try:
            return self._new_tables[table_name]
        except KeyError:
            return None

    def build_create_tables(self):
        """
        Create the MySQL tables used by the corpus, based on the column
        information given in the table description (see
        :func:``create_table_description``).
        """
        # initialize progress bars:
        if self._widget:
            self._widget.progressSet.emit(len(self._new_tables),
                                          "Creating tables... (%v of %m)")
            self._widget.progressUpdate.emit(0)

        self.add_tag_table()

        for i, current_table in enumerate(self._new_tables):
            self._new_tables[current_table].setDB(self.DB)
            S = self._new_tables[current_table].get_create_string(
                options.cfg.current_connection.db_type(),
                self._new_tables.values(),
                index_gen=current_table == getattr(self, "corpus_table"))
            self.DB.create_table(current_table, S)
            if self._widget:
                self._widget.progressUpdate.emit(i + 1)
            if self.interrupted:
                return

    @classmethod
    def get_file_list(cls, path, file_filter, sort=True):
        """
        Return a list of valid file names from the given path.

        This method recursively searches in the directory ``path`` and its
        subdirectories for files that match the file filter specified in
        the class attribute ``file_filter``.

        Parameters
        ----------
        path : string
            The path in which to look for files
        file_filter : string
            A filter that is applied to all file names in the path
        sort : bool
            True if the file list should be returned in alphabetical order,
            or False otherwise.

        Returns
        -------
        l : list
            A list of strings, each representing a file name

        """
        L = []
        expect = list(cls.expected_files)
        for source_path, folders, files in os.walk(path):
            for current_file in files:
                full_name = os.path.join(source_path, current_file)
                if cls.expected_files:
                    if current_file in expect:
                        L.append(full_name)
                        expect.remove(current_file)
                elif not file_filter or fnmatch.fnmatch(current_file,
                                                        file_filter):
                    L.append(full_name)
        if sort:
            return sorted(L)
        else:
            return L

    def validate_path(self, path):
        """
        Validate that directory ``path`` contains corpus data files.

        Parameters
        ----------
        path : string
            The path to be validated

        Returns
        -------
        valid : bool
            True if the directory ``path`` contains valid corpus data files,
            or False otherwise.
        """

        # check if path exists:
        if not os.path.isdir(path):
            return False

        # check if path contains any file:
        for source_path, folders, files in os.walk(path):
            for current_file in files:
                full_name = os.path.join(source_path, current_file)
                if os.path.isfile(full_name):
                    return True
                if not self.file_filter or fnmatch.fnmatch(current_file,
                                                           self.file_filter):
                    return True
        return False

    @classmethod
    def validate_files(cls, file_list):
        """
        Validates the file list.

        The default implementation will compare the content of the argument
        to the class attribute expected_files. If there is an entry in
        expected_files that is not also in the argument list, the file list
        is considered to be invalid.

        Parameters
        ----------
        file_list : list
            A list of file names as created by get_file_list()

        """

        expected_files = cls.expected_files

        base_case = [os.path.basename(x) for x in expected_files]
        base_no_case = [os.path.basename(x).lower() for x in expected_files]

        for file_name in file_list:
            path, base_name = os.path.split(file_name)
            if check_fs_case_sensitive(path):
                if base_name in base_case:
                    base_case.remove(base_name)
            else:
                if base_name.lower() in base_no_case:
                    base_no_case.remove(base_name.lower())

        missing_list = [x for x in expected_files
                        if x in base_case and x.lower() in base_no_case]

        if missing_list:
            sample = "<br/>".join(missing_list[:5])
            if len(missing_list) > 6:
                sample = (f"{sample}</code>, and {len(missing_list) - 3} "
                          "other files")
            elif len(missing_list) == 6:
                sample = "<br/>".join(missing_list[:6])
            S = f"""
            <p>Not all expected corpora files were found in the specified
            corpus data directory. Missing files are:</p>
            <p><code>{sample}</code></p>"""
            raise RuntimeError(S)

    def get_corpus_code(self):
        """
        Return a text string containing the Python source code for the
        Corpus class of this module.

        The code is obtained from the the class attribute self._corpus_code.
        """
        try:
            lines = [x for x in inspect.getsourcelines(self._corpus_code)[0]
                     if not x.strip().startswith("class")]
        except AttributeError:
            lines = []
        return "".join(lines)

    def map_query_item(self, item_type, rc_feature):
        """
        Maps a query item type to the given resource feature

        Parameters
        ----------
        item_type : str
            One of the string constants from defines.py:
            QUERY_ITEM_WORD, QUERY_ITEM_LEMMA, QUERY_ITEM_TRANSCRIPT,
            QUERY_ITEM_POS, QUERY_ITEM_GLOSS

        rc_feature : str
            The resource feature that will be used to access the information
            needed for the query item type specified by 'item_type'.
        """
        if item_type == QUERY_ITEM_WORD:
            self.query_item_word = rc_feature
        elif item_type == QUERY_ITEM_LEMMA:
            self.query_item_lemma = rc_feature
        elif item_type == QUERY_ITEM_TRANSCRIPT:
            self.query_item_transcript = rc_feature
        elif item_type == QUERY_ITEM_POS:
            self.query_item_pos = rc_feature
        elif item_type == QUERY_ITEM_GLOSS:
            self.query_item_gloss = rc_feature

    def add_time_feature(self, rc_feature):
        """
        Add the resource feature to the list of time features.

        Time features are those features that can be visualized using a
        time series visualization.
        """
        self._time_features.append(rc_feature)

    def add_lexical_feature(self, rc_feature):
        """
        Add the resource feature to the list of lexical features.

        Any feature that comes from a ``word'' table or its descendants
        are considered lexical features. If the corpus stores lexical
        features directly in the ``corpus'' table, these features are
        therefore not automatically recognized as lexical. This method is
        used to register them so that they are treated as lexically.
        """
        self._lexical_features.append(rc_feature)

    def add_speaker_feature(self, rc_feature):
        """
        Add the resource feature to the list of speaker features.

        Any feature that refers to the speaker of a token that is not stored
        in a dedicated speaker table can be marked as a speaker feature by
        using this method. The feature will then be listed in the resource
        feature tree under the root node 'Speakers'.
        """
        self._speaker_features.append(rc_feature)

    def add_annotation(self, inner, outer):
        """
        Add a link between the inner and the outer table by time annotations.
        """
        self._annotations[inner] = outer

    def add_audio_feature(self, rc_feature):
        """
        Add the resource feature to the list of audio features.

        Audio features do not appear in the list of queryable corpus features.
        The context viewer can use them to visualize the audio in a separate
        tab.
        """
        self._audio_features.append(rc_feature)

    def add_video_feature(self, rc_feature):
        """
        Add the resource feature to the list of video features.

        Audio features do not appear in the list of queryable corpus features.
        The context viewer can use them to visualize the video in a separate
        tab.
        """
        self._video_features.append(rc_feature)

    def add_image_feature(self, rc_feature):
        """
        Add the resource feature to the list of image features.

        Audio features do not appear in the list of queryable corpus features.
        The context viewer can use them to visualize the image in a separate
        tab.
        """
        self._image_features.append(rc_feature)

    @classmethod
    def add_exposed_id(cls, table_name):
        """
        Add the identifier from the table name to the list of exposed IDs.

        Exposed IDs are selectable in the resource tree, i.e. they are added
        to the list of queryable corpus features.

        Parameters
        ----------
        table_name : str
            The resource table name that contains the ID to be exposed, e.g.
            "word" if the resource feature to be exposed is "word_id".
        """
        cls.exposed_ids.append(f"{table_name}_id")

    def get_resource_code(self):
        """ return a text string containing the Python source code from
        the class attribute self._resource_code. This function is needed
        to add resource-specific code the Python corpus module."""
        try:
            lines = [x.strip("\n")
                     for x in inspect.getsourcelines(self._resource_code)[0]
                     if not x.strip().startswith("class")]
            # make sure that there is a separating empty line:
            if lines[0]:
                lines.insert(0, "")
        except AttributeError:
            lines = []

        lines.insert(0, "")
        s_tf_list = ", ".join([f'"{x}"' for x in self._time_features])
        lines.insert(0, f"    time_features = [{s_tf_list}]")
        lines.insert(0, f"    number_of_tokens = {self._corpus_id}")
        if self._lexical_features:
            s_lf_list = ", ".join([f'"{x}"' for x in self._lexical_features])
            lines.insert(0, f"    lexical_features = [{s_lf_list}]")
        if self._speaker_features:
            s_sf_list = ", ".join([f'"{x}"' for x in self._speaker_features])
            lines.insert(0, f"    lexical_features = [{s_sf_list}]")
        if self._audio_features:
            s_af_list = ", ".join([f'"{x}"' for x in self._audio_features])
            lines.insert(0, f"    audio_features = [{s_af_list}]")
        if self._video_features:
            s_vf_list = ", ".join([f'"{x}"' for x in self._video_features])
            lines.insert(0, f"    video_features = [{s_vf_list}]")
        if self._image_features:
            s_if_list = ", ".join([f'"{x}"' for x in self._image_features])
            lines.insert(0, f"    image_features = [{s_if_list}]")
        if self._annotations:
            lines.insert(0, f"    annotations = {self._annotations}")

        if not lines:
            return "\n"
        else:
            return "\n".join(lines)

    def get_method_code(self, method):
        pass

    def store_filename(self, file_name):
        """
        Store the file in the file table, but not if it is a special file
        listed in self.special_files.

        Parameters
        ----------
        file_name : str
            The path to the file

        Returns
        -------
        file_id : int or None
            The id of the file in the table, or None if the file is a special
            file
        """
        self._file_name = file_name
        self._value_file_name = os.path.basename(file_name)
        self._value_file_path = os.path.split(file_name)[0]

        if self._value_file_name not in self.special_files:
            self._file_id = self.table(self.file_table).get_or_insert(
                {self.file_name: self._value_file_name,
                 self.file_path: self._value_file_path})

    def process_xlabel_file(self, file_name):
        """
        Process an xlabel file.

        This method reads the content of the file, and interprets it as an
        ESPS/waves+ xlabel file. Xlabel filess are used in some spoken
        corpora to represent phonetic annotations. A description of the file
        format can be found here:

        http://staffhome.ecm.uwa.edu.au/~00014742/research/speech/local/entropic/ESPSDoc/waves/manual/xlabel.pdf

        Basically, an xlabel file consists of a header and a file body,
        separated by a row containing only the hash mark '#'. This method
        ignores the data from the header. Rows in the file body consist of
        three columns ``time color word``, separated by whitespace. Rows with
        less than three columns are ignored.

        Parameters
        ----------
        file_name : string
            The path name of the file that is to be processed
        """
        file_body = False
        # read file using the specified encoding (default is 'utf-8), and
        # retry using 'ISO-8859-1'/'latin-1' in case of an error:
        try:
            with codecs.open(file_name, "r",
                             encoding=self.arguments.encoding) as input_file:
                input_data = input_file.read()
        except UnicodeDecodeError:
            with codecs.open(file_name, "r",
                             encoding="ISO-8859-1") as input_file:
                input_data = input_file.read()

        input_data = input_data.splitlines()
        for row in input_data:
            # only process the lines after the hash mark:
            if row.strip() == "#":
                file_body = True
            elif file_body:
                try:
                    time, color, word = row.split()
                # in xlabel files, rows can sometimes contain only the time
                # tag, but no other labels. In this case, the row is ignored:
                except ValueError:
                    continue

                word_dict = {self.word_label: word}
                # get a word id for the current word:
                word_id = self.table(self.word_table).get_or_insert(word_dict)

                # add the word as a new token to the corpus:

                self.add_token_to_corpus(
                    {self.corpus_word_id: word_id,
                        self.corpus_file_id: self._file_id,
                        self.corpus_time: time})

    def process_text_file(self, file_name):
        raise RuntimeError

    def _add_next_token_to_corpus(self, values):
        self._corpus_id += 1
        values[self.corpus_id] = self._corpus_id
        self._corpus_buffer.append(values)

    # pylint: disable=method-hidden
    def add_token_to_corpus(self, values):
        if len(values) < len(self._new_tables[self.corpus_table].columns) - 2:
            raise IndexError
        self._corpus_id += 1
        values[self.corpus_id] = self._corpus_id
        self._corpus_keys = values.keys()
        self._corpus_buffer = []
        self._corpus_buffer.append(values)

        self.add_token_to_corpus = self._add_next_token_to_corpus

    ### METHODS FOR XML FILES

    def xml_parse_file(self, file_object):
        """ Return the root of the XML parsed tree from the file object.
        If there is a parsing error, print the surrounding environment and
        raise an exception."""
        try:
            e = ET.parse(file_object).getroot()
        except ET.ParseError as e:
            # in case of a parsing error, print the environment that caused
            # the failure:
            m = re.search(r"line (\d*), column (\d*)", str(e))
            if m:
                line = int(m.group(1))
                column = int(m.group(2))
                start_line = max(0, line - 5)
                end_line = line + 5
            else:
                start_line = 0
                end_line = 999999
            # FIXME: Apparently, there was an error in the exception handling
            # that required to remove showing the source code that contained
            # the error. This should be returned at some point.
            # S = S.splitlines()
            S = []
            logging.error(e)
            for i, x in enumerate(S):
                if i > start_line:
                    warnings.warn("{:<3}: {}".format(i, x.decode("utf8")))
                if i == line - 1:
                    warnings.warn("      " + " " * (column - 1) + "^")
                if i > end_line:
                    break
            raise e
        return e

    def xml_get_body(self, root):
        """ Return the XML body from the root."""
        raise NotImplementedError("xml_get_body")

    def xml_get_meta_information(self, root):
        """ Retrieve and store all meta information from the root."""
        raise NotImplementedError("xml_get_meta_information")

    def xml_process_element(self, element):
        """ Process the XML element. Processing involves several stages:

        1. Call xml_preprocess_tag(element) for tag actions when entering
        2. Call xml_process_content(element.text) to process the content
        3. Call xml_process_element() for every nested element
        4. Call xml_postprocess_tag(element) for tag actions when leaving
        5. Call xml_process_tail(element.tail) to process the tail

        """

        self.xml_preprocess_tag(element)
        if element.text:
            self.xml_process_content(element.text)
        if list(element):
            for child in element:
                self.xml_process_element(child)
        self.xml_postprocess_tag(element)
        if element.tail is not None and element.tail.strip():
            self.xml_process_tail(element.tail.strip())

    def xml_preprocess_tag(self, element):
        """ Take any action that is triggered by the tag when entering the
        element."""
        pass

    def xml_process_content(self, element):
        pass

    def xml_process_tail(self, element):
        pass

    def xml_postprocess_tag(self, element):
        """ Take any action that is triggered by the tag when leaving the
        element."""
        pass

    def tag_token(self, token_id, tag, attributes, op=False, cl=False):
        """
        Add a tag to the specified token.

        Parameters
        ----------
        token_id : int
            The ID of the token to be tagged
        tag : str
            The tag type
        attributes : dict
            A dictionary containing the attributes for the tag
        op, cl: bool
            Set 'op' to True if the tag is an opening tag. Set 'cl' to
            True if the tag is a closing tag. If neither or both are True,
            a ValueError exception is raised.
        """
        if (op and cl) or (not op and not cl):
            raise ValueError
        if op:
            tag_type = "open"
        else:
            tag_type = "close"

        self.table(self.tag_table).add(
            {self.tag_label: f"{tag}",
                self.tag_corpus_id: token_id,
                self.tag_type: tag_type,
                self.tag_attribute: ", ".join([f"{x}={attributes[x]}"
                                               for x in attributes])})

    def tag_next_token(self, tag, attributes):
        """ Add an entry to the tag table that marks the next corpus_id.

        The tag is marked as an opening tag and contains the name ``tag``
        and a string representation of the dictionary ``attributes``.

        The closing counterpart can be added by calling
        :func:`tag_last_token`.

        Parameters
        ----------
        tag : string
            The name of the tag
        attributes : dict
            A dictionary containing the attributes of the opening tag.

        """
        self.table(self.tag_table).add(
            {self.tag_label: f"{tag}",
             self.tag_corpus_id: self._corpus_id + 1,
             self.tag_type: "open",
             self.tag_attribute: ", ".join([f"{x}='{attributes[x]}'"
                                            for x in attributes])})

    def tag_last_token(self, tag, attributes):
        """
        Add an entry to the tag table that marks the last corpus_id.

        The tag is marked as a closing tag and contains the name `tag` and a
        string representation of the dictionary `attributes`.

        The opening counterpart can be added by calling
        :func:`tag_next_token`.


        Parameters
        ----------
        tag : string
            The name of the tag
        attributes : dict
            A dictionary containing the attributes of the closing tag.
        """

        self.table(self.tag_table).add(
            {self.tag_label: f"{tag}",
             self.tag_corpus_id: self._corpus_id - 1,
             self.tag_type: "close",
             self.tag_attribute: ""})

    def add_empty_tag(self, tag, attributes):
        """
        Add an empty tag after the current corpus element.

        This method is usually called from within :func:`process_file` or a
        related method. It will add an entry to the tag table so that
        an empty tag is inserted into the corpus after the current corpus
        element. This empty tag has the name ``tag`` and the attributes
        given in ``attributes``.

        Parameters
        ----------
        tag : string
            The name of the tag
        attributes : dict
            A dictionary containing the attributes of the empty tag.

        Examples
        --------
        Let's assume that the corpus file contains an empty XML tag that
        serves as a placeholder for graphics that are contained in the
        original texts. In the ICE-NG files, such a placeholder is indicated
        by ``<object type="graphic">``. In order to store this information
        in the tag table, the corpus installer may have the line
        ``self.add_empty_tag("object", {"type": "graphic"})`` in the
        reimplementation of :func:`process_file` so that the method is
        called the placeholder tag is encountered in the source files.
        """
        self.table(self.tag_table).add(
            {self.tag_label: f"{tag}",
             self.tag_corpus_id: self._corpus_id + 1,
             self.tag_type: "empty",
             self.tag_attribute: ", ".join([f"{x}={attributes[x]}"
                                            for x in attributes])})

    ### END XML

    def process_file(self, file_name):
        """
        Pass the file name to a processing method.

        This method passes the file name to a method that reads the content
        from the file, parses the information relevant for the corpus, and
        stores the information to the database. The default implementation
        always calls :func:``process_text_file`` and assumes that the file
        is a plain text file.

        Subclasses of BaseCorpusBuilder should override this method so that
        the appropriate method is called for the file. In this way, it is
        possible for example to treat some files as plain text files by
        calling :func:``process_text_file`` on them, and other files as
        XML files by calling :func:``process_xml_file``.

        Parameters
        ----------
        file_name : string
            The path name of the file that is to be processed

        """
        self.process_text_file(file_name)

    def build_load_files(self):
        """ Goes through the list of suitable files, and calls process_file()
        on each file name. File names are added to the file table."""
        self._file_list = self.get_file_list(self.arguments.path,
                                             self.file_filter)
        if not self._file_list:
            logging.warning("No files found at %s" % self.arguments.path)
            return

        if self._widget:
            self._widget.progressSet.emit(len(self._file_list), "")
            self._widget.progressUpdate.emit(0)

        for i, file_name in enumerate(self._file_list):
            if self._widget:
                self._widget.labelSet.emit(
                    self._read_file_formatter.format(file=file_name))

            if self.interrupted:
                return
            if not self.db_has(self.file_table, {self.file_path: file_name}):
                logging.info("Loading file %s" % (file_name))
                self.store_filename(file_name)
                self.process_file(file_name)
            if self._widget:
                self._widget.progressUpdate.emit(i + 1)
            self.commit_data()

    def db_has(self, table, values, case=False):
        return len(self.db_find(table, values, case).index) > 0

    def db_find(self, table, values, case=False):
        """
        Obtain all records from table_name that match the column-value
        pairs given in the dict values.

        Parameters
        ----------
        table_name : str
            The name of the table
        values : dict
            A dictionary with column names as keys and cell contents as values
        case : bool
            Set to True if the find should be case-sensitive, or False
            otherwise.

        Returns
        -------
        df : pandas data frame
            a data frame containing the matching entries
        """

        variables = list(values.keys())
        where = []
        for column, value in values.items():
            where.append("{} = '{}'".format(column,
                                            str(value).replace("'", "''")))
        if case:
            S = "SELECT {} FROM {} WHERE BINARY {}".format(
                ", ".join(variables),
                table,
                " AND BINARY ".join(where))
        else:
            S = "SELECT {} FROM {} WHERE {}".format(", ".join(variables),
                                                    table,
                                                    " AND ".join(where))
        S = S.replace("\\", "\\\\")
        return pd.read_sql(S, self.DB.engine)

    def build_lookup_get_ngram_table(self):
        """
        Return the Table object that can be used to create the N-gram lookup
        table.
        """
        table = Table(self.corpusngram_table)
        corpus_tab = self._new_tables.get(self.corpus_table,
                                          Table(self.corpus_table))

        corpus_columns = []
        word_columns = []

        # determine the column of the corpus table in which word information
        # is stored:

        word_id = (getattr(self, "corpus_word_id", None) or
                   getattr(self, "corpus_word"))

        # FIXME: there should be columns for each lexical feature in the
        # corpus table!

        for col in corpus_tab.columns:
            name = "{}1".format(col.name)
            if col.name != word_id:
                if col.is_identifier:
                    new_col = Identifier(name,
                                         col.data_type, unique=col.unique)
                else:
                    new_col = Column(name, col.data_type)
                corpus_columns.append(new_col)
            else:
                for i in range(self.corpusngram_width):
                    name = "{}{}".format(col.name, i+1)
                    word_columns.append(Column(name, col.data_type))

        for col in corpus_columns:
            table.add_column(col)
        for col in word_columns:
            table.add_column(col)

        return table

    def build_lookup_get_ngram_columns(self):
        # determine the column of the corpus table in which word information
        # is stored:

        word_id = (getattr(self, "corpus_word_id", None) or
                   getattr(self, "corpus_word"))

        features = self.get_corpus_table_features()

        corpus_columns = ["{}1".format(self.corpus_id)]

        corpus_columns += ["{}1".format(y)
                           for _, y in features
                           if not y == word_id and
                           not "{}1".format(y) in corpus_columns]

        word_columns = ["{}{}".format(word_id, i+1)
                        for i in range(self.corpusngram_width)]

        return corpus_columns + word_columns

    def build_lookup_get_insert_string(self):
        template = """
            INSERT INTO {corpus_ngram} ({columns})
            SELECT {columns}
            {join}"""

        columns = self.build_lookup_get_ngram_columns()
        joins = self.get_corpus_joins(
            [(i+1, "*") for i in range(self.corpusngram_width)],
            ignore_ngram=True)

        s = template.format(
            corpus_ngram=self.corpusngram_table,
            columns=", ".join(columns),
            join="\n".join(joins))

        return s

    def build_lookup_get_padding_string(self):
        """
        Returns a string that can be used to pad the last rows of an N-gram
        lookup table.
        """
        template = """
            INSERT INTO {corpus_ngram} ({columns})
            VALUES {values}"""
        columns = self.build_lookup_get_ngram_columns()

        word_id = (getattr(self, "corpus_word_id", None) or
                   getattr(self, "corpus_word"))

        values = []
        corpus_table = self._new_tables[self.corpus_table]
        numerics = {col: corpus_table.get_column(
                            col.rstrip("1234567890")).is_numeric()
                    for col in columns}

        for pad in range(1, self.corpusngram_width):
            pos = self.corpusngram_width - pad
            row = ["{{last_row}} + {}".format(pos)]
            row += ["{{{}}}".format(x) if numerics[x] else
                    "'{{{}}}'".format(x)
                    for x in columns[1:-self.corpusngram_width]]

            word_columns = (["{{{word}{n}}}".format(
                                word=word_id,
                                n=self.corpusngram_width - i)
                             for i in reversed(range(pad))] +
                            ["{na_value}"] * (pos))

            values.insert(0, ", ".join(row + word_columns))

        return template.format(
            corpus_ngram=self.corpusngram_table,
            columns=", ".join(columns),
            values=""",
                   """.join(["({})".format(x) for x in values]))

    def build_lookup_ngram(self):
        """
        Create a lookup table for multi-item query strings.
        """

        # create N-gram class attributes:
        setattr(type(self),
                "corpusngram_table", "{}Ngram".format(self.corpus_table))
        setattr(type(self),
                "corpusngram_width", int(self.arguments.ngram_width))

        # determine highest ID in the corpus table
        S = "SELECT MAX({}) FROM {}".format(self.corpus_id, self.corpus_table)
        with self.DB.engine.connect() as connection:
            result = connection.execute(S).fetchone()
        print(S)
        print(result)
        max_id = result[0]
        logging.info("Creating lookup table, max_id is {}".format(max_id))

        # determine suitable NA value
        if hasattr(self, "corpus_word_id"):
            na_value = self._new_tables[self.word_table]._current_id + 1
        else:
            na_value = DEFAULT_MISSING_VALUE

        step = 250000 // self.corpusngram_width
        current_id = 0

        word_id = (getattr(self, "corpus_word_id", None) or
                   getattr(self, "corpus_word"))

        ngram_table = self.build_lookup_get_ngram_table()
        self.create_table_description(self.corpusngram_table,
                                      ngram_table.columns)
        self.DB.create_table(
            self.corpusngram_table,
            ngram_table.get_create_string(
                options.cfg.current_connection.db_type(),
                self._new_tables.values()))

        self._widget.progressSet.emit(
            1 + ((max_id-1) // step),
            "Creating ngram lookup table... (chunk %v of %m)")
        self._widget.progressUpdate.emit(1)

        sql_template = """
            {insert_str}
            WHERE {token_range}"""

        _chunk = 1
        with self.DB.engine.connect() as connection:
            while current_id <= max_id and not self.interrupted:
                token_range = (
                    "{token}1 >= {lower} AND {token}1 < {upper}".format(
                        token=self.corpus_id,
                        lower=current_id,
                        upper=current_id + step))

                S = sql_template.format(
                    insert_str=self.build_lookup_get_insert_string(),
                    token_range=token_range)

                connection.execute(S.strip().replace("\n", " "))
                current_id = current_id + step

                _chunk += 1
                self._widget.progressUpdate.emit(_chunk)

            padding_str = self.build_lookup_get_padding_string()

            # get the last (width - 1) tokens from the corpus:
            query_max_row = """
                SELECT *
                FROM {corpus}
                WHERE {corpus_id} > {max_id} - {width}
                ORDER BY {corpus_id}""".format(
                    corpus=self.corpus_table,
                    corpus_id=self.corpus_id,
                    max_id=max_id,
                    width=self.corpusngram_width - 1)
            print(query_max_row)
            df = pd.read_sql(query_max_row, connection)
            print(df)

            data_dict = {"{}1".format(x): df.iloc[-1][x]
                         for x in df.iloc[-1].index if x != word_id}
            word_dict = {"{}{}".format(word_id, i+2): x
                         for i, x in enumerate(df[word_id].values)}
            kwargs = {"na_value": na_value,
                      "last_row": (df.iloc[-1][self.corpus_id] -
                                   self.corpusngram_width + 1)}
            kwargs.update(data_dict)
            kwargs.update(word_dict)
            S = padding_str.format(**kwargs)
            print(S)
            connection.execute(S.replace("\n", " ").strip())

    def build_index_ngram(self):
        pass

    def build_optimize(self):
        """
        Optimizes the table columns so that they use a minimal amount
        of disk space.
        """
        totals = 0
        for table in self._new_tables:
            totals += len(self._new_tables[table].columns)

        totals -= 1

        if self._widget:
            self._widget.progressSet.emit(
                totals,
                "Optimizing table columns... (%v of %m)")
            self._widget.progressUpdate.emit(0)

        column_count = 0

        for table_name in self._new_tables:
            table = self._new_tables[table_name]
            if self.interrupted:
                return

            for column in table.columns:
                # Links should get the same optimal data type as the linked
                # column:
                if column.key:
                    try:
                        _table = self._new_tables[column._link]
                        _column = _table.primary
                        optimal = _table.suggest_data_type(_column.name)
                    except TypeError:
                        continue
                else:
                    try:
                        optimal = table.suggest_data_type(column.name)
                    except TypeError:
                        continue
                try:
                    current = self.DB.get_field_type(table.name, column.name)
                    current = current.strip().upper()
                except Exception as e:
                    print(e)
                    logging.error(str(e))
                    continue

                # length values are only used with VARCHAR types, otherwise,
                # they are stripped:
                if column.base_type.upper() != "VARCHAR":
                    current = re.sub(r"\(\d+\)", "", current)

                if current.lower() != optimal.lower():
                    logging.info(
                        "Optimizing column {}.{} from {} to {}".format(
                            table.name, column.name, current, optimal))
                    try:
                        self.DB.modify_field_type(table.name, column.name,
                                                  optimal)
                    except Exception as e:
                        print(e)
                        logging.warning(e)
                    else:
                        column.data_type = optimal
                column_count += 1

                if self._widget:
                    self._widget.progressUpdate.emit(column_count + 1)

        if self.interrupted:
            return

    def build_create_indices(self):
        """
        Create a MySQL index for each column in the database.

        In Coquery, each column of a corpus table can be included in the
        output, and the columns are also available for filtering. As access
        to MySQL columns can be very significantly faster if the column is
        indexed, the corpus builder creates indices for any data column.

        The downside is that indexing may take considerable time for larger
        corpora such as the British National Corpus or the Corpus of
        Contemporary American English. Indices also increase the disk space
        required to store the corpus database.

        However, the performance increase won by indexing usually clearly
        outweighs these disadvantages.
        """
        index_list = []
        for table_name in self._new_tables:
            table = self._new_tables[table_name]
            for column in table.columns:
                if not isinstance(column, Identifier):
                    index_list.append((table.name, column.name))

        if self._widget:
            self._widget.progressSet.emit(len(index_list),
                                          "Creating indices... (%v of %m)")
            self._widget.progressUpdate.emit(0)

        i = 0
        for table, column in index_list:
            if self.interrupted:
                return

            try:
                this_column = self._new_tables[table].get_column(column)

                # do not create an index for BLOBs (they are used only to
                # store binary information that should never be used for
                # queries or joins):
                if this_column.base_type.endswith("BLOB"):
                    continue

                # indices for TEXT columns require a key length:
                if this_column.base_type.endswith("TEXT"):
                    logging.warning("TEXT data type is deprecated")
                    if this_column.index_length:
                        length = this_column.index_length
                    else:
                        length = self.DB.get_index_length(table, column)
                else:
                    length = None

                self.DB.create_index(table, column, [column],
                                     index_length=length)
            except Exception as e:
                print(e)
                logging.warning(e)

            i += 1
            if self._widget:
                self._widget.progressUpdate.emit(i + 1)

    def get_class_variables(self):
        return dir(self)

    def set_query_items(self):
        """
        Set up the mapping between query item types and resource features.

        This method generates the attributes that specifies in the corpus
        module in which field the program should look when looking for word,
        lemma, transcription, or part-of-speech information. These mappings
        can be set in the corpus installer by using the add_query_item()
        method.

        If no specific add_query_item() method is called for a query type,
        a list of default resource features will be probed. If one of the
        resource features are provided by the corpus, that feature will be
        used when evaluating the respective query item.

        Mappings are realized by instanciating the class attributes
        query_item_word, query_item_lemma, query_item_transcript,
        query_item_gloss, and query_item_pos. If no mapping has been
        set for one of these query item types either by explicitly calling
        add_query_item() or by providing a resource feature that is in the
        default lists, that attribute will not be provided by the corpus
        module. In effect, that query item type will not be available for
        that corpus.

        These are the default resource features (in order; the first will be
        considered first):

        Query item type Resource features
        --------------------------------------------------------------------
        Word            word_label, corpus_label
        Lemma           lemma_label, word_lemma, corpus_lemma
        Transcript      transcript_label, word_transcript, corpus_transcript
        Gloss           gloss_label, word_gloss, lemma_gloss, corpus_gloss
        POS             pos_label, word_pos, lemma_pos, corpus_pos

        """
        if not hasattr(self, "query_item_word"):
            for x in ["word_label", "corpus_word"]:
                if hasattr(self, x):
                    self.query_item_word = x
                    break
        if not hasattr(self, "query_item_lemma"):
            for x in ["lemma_label", "word_lemma", "corpus_lemma"]:
                if hasattr(self, x):
                    self.query_item_lemma = x
                    break
        if not hasattr(self, "query_item_transcript"):
            for x in ["transcript_label", "word_transcript",
                      "corpus_transcript"]:
                if hasattr(self, x):
                    self.query_item_transcript = x
                    break
        if not hasattr(self, "query_item_pos"):
            for x in ["pos_label", "word_pos", "lemma_pos", "corpus_pos"]:
                if hasattr(self, x):
                    self.query_item_pos = x
                    break
        if not hasattr(self, "query_item_gloss"):
            for x in ["gloss_label", "word_gloss",
                      "lemma_gloss", "corpus_gloss"]:
                if hasattr(self, x):
                    self.query_item_gloss = x
                    break

    def store_metadata(self):
        pass

    def insert_metadata(self, *args):
        pass

    def set_surface_feature(self, rc_feature):
        """
        Set the surface feature, i.e. the one that is used to display the
        context of tokens either in the context viewer or in the results
        table. By default, the surface feature is the same as the word query
        feature.

        Parameters
        ----------
        rc_feature : string
            The feature that will be used as the new surface feature.
        """
        self.surface_feature = rc_feature

    def get_module_path(self, name):
        """
        Return the path to the corpus module that is written during a build.

        Parameters
        ----------
        name : str
            The name of the corpus

        Returns
        -------
        path : str
            The path to the corpus module.
        """
        return os.path.join(options.cfg.corpora_path, "{}.py".format(name))

    def build_write_module(self):
        """ Write a Python module with the necessary specifications to the
        Coquery corpus module directory."""
        base_variables = dir(type(self).__bases__[0])

        # all class variables that are defined in this class and which...
        # - are not stored in the base class
        # - do not start with an underscore '_'
        # - are not class methods
        # are considered to be part of the database specification and will
        # be included with their value in the Python code.

        variable_names = [x for x in dir(self)
                          if x not in base_variables and
                          not x.startswith("_") and
                          not inspect.ismethod(getattr(self, x))]

        # remove column lists, i.e. variables of the form 'TABLE_columns',
        # where TABLE is the name of the table, and which store the column
        # objects for the table:
        for var in list(variable_names):
            name, _, field = var.partition("_")
            if field == "table":
                try:
                    variable_names.remove("{}_columns".format(name))
                except ValueError:
                    pass

        variable_strings = []
        for variable_name in sorted(variable_names):
            value = getattr(self, variable_name)
            if isinstance(value, (int, float)):
                format_str = "    {} = {}"
            else:
                format_str = "    {} = '{}'"
            variable_strings.append(format_str.format(variable_name, value))
        variable_code = "\n".join(variable_strings)

        path = self.get_module_path(self.arguments.db_name)
        file_name = os.path.split(path)[-1]

        self.module_content = self.module_code.format(
                name=self.name,
                file_name=file_name,
                display_name=utf8(self.get_name()),
                db_name=utf8(self.arguments.db_name),
                url=utf8(self.get_url()),
                variables=utf8(variable_code),
                corpus_code=utf8(self.get_corpus_code()),
                resource_code=utf8(self.get_resource_code()))
        self.module_content = self.module_content.replace("\\", "\\\\")
        # write module code:
        with codecs.open(path, "w", encoding="utf-8") as output_file:
            output_file.write(self.module_content)
            logging.info("Corpus module %s written." % path)

    def setup_db(self, keep_db):
        """
        Create a connection to the server, and creates the database if
        necessary.
        """
        con = options.cfg.current_connection

        if con.has_database(self.arguments.db_name):
            if not keep_db:
                con.remove_database(self.arguments.db_name)
        if not con.has_database(self.arguments.db_name):
            con.create_database(self.arguments.db_name)

        kwargs = dict(Host=getattr(con, "host", None),
                      Port=getattr(con, "port", None),
                      User=getattr(con, "user", None),
                      Password=getattr(con, "password", None),
                      db_path=getattr(con, "path", None),
                      Type=con.db_type(),
                      db_name=self.arguments.db_name,
                      local_infile=1)

        self.DB = sqlwrap.SqlDB(**kwargs)
        self.DB.use_database(self.arguments.db_name)

    def add_metadata(self, file_name, column):
        pass

    def add_building_stage(self, stage):
        """ The parameter stage is a function that will be executed
        after the database tables have been created and the data data files
        have been processed, but before the tables are optimized and
        indexed. More than one function can be added."""
        self.additional_stages.append(stage)

    @staticmethod
    def get_license():
        return "(license not specified)"

    @staticmethod
    def get_title():
        return "(no title)"

    @staticmethod
    def get_language_code():
        """
        Return the ISO 639-1 code for the corpus language. Variant sub-codes
        may be linked by a hyphen, e.g. "en-NG" for Nigerian English".
        """
        return "(unspecified)"

    @staticmethod
    def get_description():
        return []

    @staticmethod
    def get_references():
        return []

    @staticmethod
    def get_url():
        return "(no URL)"

    @staticmethod
    def get_modules():
        """
        Return the Python modules that are required by this builder class.

        Returns
        -------
        l : list of tuples
            A list of tuples describing the Python modules that are required
            by this module. Each tuple consists of the module name, the
            package name, and the URL for this package.
        """
        return []

    @staticmethod
    def get_name():
        return "(unnamed)"

    @staticmethod
    def get_db_name():
        return "unnamed"

    @staticmethod
    def get_installation_note():
        return ""

    def build_initialize(self):
        """
        Initialize the corpus build.
        """

        self.start_time = time.time()
        logging.info("--- Starting ---")
        logging.info("Building corpus %s" % self.name)
        logging.info("Command line arguments: %s" % " ".join(sys.argv[1:]))

        # Corpus installers may require additional modules. For example,
        # Gabra is currently distributed as MongoDB files, which are read by
        # using the pymongo library.
        # Unless the user wishes to install only the corpus module, try to
        # import these additional modules, and raise an exception if they are
        # unavailable:
        if not self.arguments.only_module:
            for module, package, url in self.get_modules():
                logging.info("importing module: {}".format(module))
                try:
                    exec("import {}".format(module))
                except ImportError:
                    logging.info("Import failed.")
                    raise DependencyError(package, url)

        if self.DB.db_type == SQL_MYSQL:
            self.DB.connection.execute("SET NAMES 'utf8'")
            self.DB.connection.execute("SET CHARACTER SET 'utf8mb4'")
            self.DB.connection.execute("SET unique_checks=0")
            self.DB.connection.execute("SET foreign_key_checks=0")
        logging.info("Builder initialized")

    def remove_build(self):
        """
        Remove everything that has been built so far.

        This method removes the corpus components that have just been
        built, e.g. if the build was interrupted by the user or becauee
        an exception occurred.

        It attempts to remove the following:

        - the database (if the database was constructed during the build)
        - the corpus module
        - the corpus installer in case of adhoc corpora
        """
        try:
            options.cfg.current_connection.remove_database(
                self.arguments.db_name)
        except Exception:
            pass
        path = self.get_module_path(self.arguments.name)
        try:
            os.remove(path)
        except Exception:
            pass

        path = os.path.join(options.cfg.adhoc_path,
                            "coq_install_{}.py".format(self.arguments.db_name))
        try:
            os.remove(path)
        except Exception:
            pass

    def build_finalize(self):
        """ Wrap up everything after the corpus installation is complete. """
        if self.interrupted:
            self.remove_build()
            S = "Interrupted building {} (after {:.3f} seconds)".format(
                self.name, time.time() - self.start_time)
        else:
            S = "Done building {} (after {:.3f} seconds)".format(
                self.name, time.time() - self.start_time)
        logging.info("--- {} ---".format(S))

    def build(self):
        """
        Build the corpus database, and install the corpus module.

        This method runs all steps required to make the data from a corpus
        available to Coquery. Most importantly, it calls these functions (in
        order):

        * :func:`build_initialize` to set up the building process, which
          includes loading the required modules`
        * :func:`build_create_tables` to create all SQL tables that were
          specified by previous calls to :func:`create_table_description`
        * :func:`build_load_files` to read all datafiles, process their
          content, and insert the content into the SQL tables
        * :func:`build_lookup_ngram` to create an n-gram lookup table that
          increases query performance of multi-item queries, but which
          requires a lot of disk space
        * :func:`build_optimize` to ensure that the SQL tables use the optimal
          data format for the data
        * :func:`build_create_indices` to create database indices that speed
          up the SQL queries
        * :func:`build_write_module` to write the corpus module to the
          ``corpora`` sub-directory of the Coquery install directory (or the
          corpus directory specified in the configuration file)

        .. note::

            Self-joined tables are currently not supported by
            :class:`BaseCorpusBuilder`. Corpus installers that want to use
            this feature have to override :func:`build_lookup_ngram`.
        """

        def progress_next(count):
            if self._widget:
                count += 1
                self._widget.generalUpdate.emit(count)
                self._widget.progressSet.emit(0, "")
            return count

        def progress_done():
            if self._widget:
                self._widget.progressUpdate.emit(0)

        self.check_arguments()
        self.setup_db(self.arguments.only_module)

        if self._widget:
            steps = 3 + (int(self.arguments.lookup_ngram) +
                         int(self.additional_stages != []) +
                         int(self.DB.db_type == SQL_MYSQL))
            self._widget.ui.progress_bar.setMaximum(steps)

        current = 0
        current = progress_next(current)

        with self.DB.engine.connect() as self.DB.connection:
            logging.info("Stage 0")
            self.build_initialize()

            try:
                if not self.arguments.only_module:
                    # create tables
                    if not self.interrupted:
                        logging.info("Stage 1")
                        if self.arguments.metadata:
                            self.add_metadata(self.arguments.metadata,
                                              self.arguments.metadata_column)
                        self.build_create_tables()

                    # read files
                    if not self.interrupted:
                        logging.info("Stage 2")
                        current = progress_next(current)
                        if self.arguments.metadata:
                            self.store_metadata()
                        self.build_load_files()
                        self.commit_data()
                        # set_query_items() initializes those class variables
                        # that map the different query item types to resource
                        # features from the class. In order to make these
                        # mappings available in the corpus module, this is
                        # called before the module is written:
                        self.set_query_items()

                    # any additional stage
                    if not self.interrupted:
                        logging.info("Stage 3")
                        current = progress_next(current)
                        for stage in self.additional_stages:
                            if not self.interrupted:
                                stage()

                    # optimize
                    if (not self.interrupted and
                            self.DB.db_type == SQL_MYSQL):
                        logging.info("Stage 4")
                        current = progress_next(current)
                        self.build_optimize()

                    # lookup table
                    try:
                        if (not self.interrupted and
                                self.arguments.lookup_ngram):
                            logging.info("Stage 5")
                            current = progress_next(current)
                            self.build_lookup_ngram()
                    except Exception as e:
                        S = "Error building ngram lookup table: {}".format(e)
                        logging.error(S)
                        print(S)
                        raise e

                    # build indexes
                    if not self.interrupted:
                        logging.info("Stage 6")
                        current = progress_next(current)
                        self.build_create_indices()

                else:
                    self.set_query_items()

                # write module
                if not self.interrupted:
                    logging.info("Stage 8")
                    current = progress_next(current)
                    self.build_write_module()

                self.build_finalize()
            except Exception as e:
                for x in get_error_repr(sys.exc_info()):
                    print(x)
                    logging.warning(x)
                logging.warning(str(e))
                print(str(e))
                self.remove_build()
                self.DB.connection.close()
                raise e
        self.DB.engine.dispose()

    def create_description_text(self):
        if self.arguments.use_nltk:
            import nltk
            self._is_tagged_label = "POS-tagged text corpus"
            try:
                tagging_state = msg_nltk_tagger.format(
                    tagger=nltk.tag._POS_TAGGER.split("/")[1],
                    version=nltk.__version__)
            except Exception:
                tagging_state = msg_nltk_tagger_fallback.format(
                    version=nltk.__version__)
        else:
            self._is_tagged_label = "text corpus"
            tagging_state = ("Part-of-speech tags are not available for this "
                             "corpus.")

        desc_template = """<p>The {label} '{name}' was created on {date}.
            It contains {tokens} text tokens. {tagging_state}</p>
            <p>Directory:<br/> <code>{path}</code></p>
            <p>File{s}:<br/><code>{files}</code></p>"""
        description = [desc_template.format(
            label=utf8(self._is_tagged_label),
            date=utf8(time.strftime("%c")),
            user=utf8(getpass.getuser()),
            name=utf8(self.arguments.name),
            path=utf8(self.arguments.path),
            s="s" if len(self._file_list) > 1 else "",
            files="<br/>".join([utf8(os.path.basename(x)) for x
                                in sorted(self._file_list)]),
            tokens=self._corpus_id,
            tagging_state=utf8(tagging_state))]

        return description

    def create_installer_module(self):
        """
        Read the Python source of coq_install_generic.py, and modify it so that
        it can be stored as an adhoc installer module.
        """
        with codecs.open(
                os.path.join(options.cfg.installer_path,
                             "coq_install_generic.py"), "r") as input_file:
            source = input_file.readlines()

        description = self.create_description_text()

        new_code = new_code_str.format(
            name=self.name,
            db_name=self.arguments.db_name,
            is_tagged_corpus=self._is_tagged_label,
            description=" ".join(description))
        new_code = new_code.replace("\\", "\\\\")
        in_class = False
        in_docstring = False

        for x in source:
            if self.arguments.use_nltk:
                if x.strip().startswith("def __init__") and "pos=False" in x:
                    x = x.replace("pos=False", "pos=True")

            if x.startswith('"""'):
                if not in_docstring:
                    in_docstring = True
                    yield '"""'
                    yield new_doc_string
                else:
                    in_docstring = False
            if in_docstring:
                continue

            if not in_class:
                if x.startswith("class BuilderClass"):
                    in_class = True
                    yield x
                    continue
            else:
                if not x.startswith("    "):
                    in_class = False
                    yield new_code

            if self.arguments.use_nltk:
                if x.strip().startswith("word_lemma ="):
                    yield "    word_pos = 'POS'\n"
            yield x


class XMLCorpusBuilder(BaseCorpusBuilder):
    """
    Define a BaseCorpusBuilder subclass that can process XML files.
    """

    def __init__(self, gui=None, strip_namespace=True):
        super(XMLCorpusBuilder, self).__init__(gui=gui)
        self._namespaces = None
        self._strip_namespace = strip_namespace
        self.indent_depth = 0
        self._current_file = "(unknown)"

    def indent(self):
        return "    " * self.indent_depth

    def read_file(self, file_name, encoding="utf-8"):
        """
        Open the file, and read the data.

        Parameters
        ----------
        file_name : str
            The name of the file
        encoding : str
            The encoding that is used to read the file (default: 'utf-8')

        Returns
        -------
        data : list
            A list of strings, representing the data of the file.
        """
        with codecs.open(file_name,
                         "r",
                         encoding=encoding) as input_file:
            data = input_file.readlines()
        return data

    def preprocess_data(self, data):
        """
        Preprocess the data that has been retrieved from a file.

        Parameters
        ----------
        data : list
            A list of strings, representing the data of a file.

        Returns
        -------
        data : list
            A list, containing the preprocessed strings
        """
        return data

    def make_tree(self, data, **kwargs):
        stream = BytesIO(bytearray("\n".join(data), encoding="utf-8"))
        tree = ET.iterparse(stream, remove_comments=True, **kwargs)
        if self._strip_namespace:
            for _, element in tree:
                element.tag = element.tag.rpartition("}")[-1]
        else:
            for _ in tree:
                pass
        return tree

    def process_file(self, file_name):
        data = self.read_file(file_name, self.encoding)
        data = self.preprocess_data(data)
        try:
            tree = self.make_tree(data)
        except Exception as e:
            print(self._current_file)
            print_error_context(str(e), "\n".join(data).split("\n"))
            raise e
        self.process_tree(tree, file_name)

    def process_tree(self, tree, file_name=None):
        self.process_header(tree.root)
        self.process_body(tree.root)

    def process_header(self, tree):
        self.header = tree.find(self.header_tag,
                                namespaces=self._namespaces)

    def process_body(self, tree):
        self.body = tree.find(self.body_tag,
                              namespaces=self._namespaces)
        self.process_element(self.body)

    def preprocess_element(self, element):
        return

    def postprocess_element(self, element):
        return

    def process_element(self, element):
        self.preprocess_element(element)
        if element.text:
            self.process_content(element.text)
        for child in element:
            self.process_element(child)
        self.postprocess_element(element)
        if element.tail:
            self.process_content(element.tail)

    def tag_next_token(self, tag, attributes):
        """ Add an entry to the tag table that marks the next corpus_id.

        The tag is marked as an opening tag and contains the name ``tag``
        and a string representation of the dictionary ``attributes``.

        The closing counterpart can be added by calling
        :func:`tag_last_token`.

        Parameters
        ----------
        tag : string
            The name of the tag
        attributes : dict
            A dictionary containing the attributes of the opening tag.

        """
        self.table(self.tag_table).add(
            {self.tag_label: "{}".format(tag),
             self.tag_corpus_id: self._corpus_id + 1,
             self.tag_type: "open",
             self.tag_attribute: ", ".join(["{}='{}'".format(x, attributes[x])
                                            for x in attributes])})

    def tag_last_token(self, tag, attributes):
        """
        Add an entry to the tag table that marks the last corpus_id.

        The tag is marked as a closing tag and contains the name `tag` and a
        string representation of the dictionary `attributes`.

        The opening counterpart can be added by calling
        :func:`tag_next_token`.


        Parameters
        ----------
        tag : string
            The name of the tag
        attributes : dict
            A dictionary containing the attributes of the closing tag.
        """

        self.table(self.tag_table).add(
            {self.tag_label: "{}".format(tag),
             self.tag_corpus_id: self._corpus_id,
             self.tag_type: "close",
             self.tag_attribute: ""})


class TEICorpusBuilder(XMLCorpusBuilder):
    header_tag = "teiHeader"
    body_tag = "text"

    head_tag = "head"
    div_tag = "div"
    paragraph_tag = "p"
    sentence_tag = "s"
    utterance_tag = "u"
    word_tag = "w"

    def __init__(self, gui=None, strip_namespace=True):
        super(TEICorpusBuilder, self).__init__(gui=gui,
                                               strip_namespace=strip_namespace)
        self._open_tag_map = {self.head_tag: self.open_headline,
                              self.div_tag: self.open_div,
                              self.paragraph_tag: self.open_paragraph,
                              self.sentence_tag: self.open_sentence,
                              self.utterance_tag: self.open_utterance,
                              self.word_tag: self.open_word}

    def open_headline(self, element):
        pass

    def open_div(self, element):
        pass

    def open_sentence(self, element):
        pass

    def open_paragraph(self, element):
        pass

    def open_utterance(self, element):
        pass

    def open_word(self, element):
        pass

    def process_tree(self, tree, file_name=None):
        root = tree.root
        if root.tag == "teiCorpus":
            # assume that this is a file containing several TEI documents
            for tei_file in root.findall("TEI", ):
                self.process_tree(tei_file)
        elif root.tag == "TEI":
            # assume that this is just one TEI document
            super(TEICorpusBuilder, self).process_tree(tree)

    def process_header(self, tree):
        """
        See TEI Header examples:
        http://www.tei-c.org/release/doc/tei-p5-doc/en/html/examples-teiHeader.html
        """
        super(TEICorpusBuilder, self).process_header(tree)

    def preprocess_element(self, element):
        tag = element.tag
        print("<{}>".format(tag))
        try:
            self._open_tag_map[tag](element)
        except KeyError:
            print("Unsupported tag: {}".format(tag))

    def postprocess_element(self, element):
        print("</{}>".format(element.tag))

    def process_content(self, content):
        print(content)


def print_error_context(s, content):
    m = re.search(r"line (\d*), column (\d*)", s)
    if m:
        line = int(m.group(1))
        column = int(m.group(2))
        start_line = max(0, line - 5)
        end_line = line + 5
        for i, x in enumerate(content[start_line:end_line]):
            print("{:6} {}".format(i + start_line, x))
            if i == 4:
                print("      {}^ ERROR: {}".format(" " * column, s))
    else:
        print(s)

# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

"""
corpusbuilder.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

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

try:
    str = unicode
except:
    pass

import codecs

import logging
import collections
import os.path
import string
import imp
import importlib

import dbconnection
import argparse
import re
import time
import sys
import textwrap
import fnmatch
import inspect
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
        
import difflib

try:
    sys.path.append(os.path.join(sys.path[0], "../gui"))
    sys.path.append(os.path.join(sys.path[0], ".."))
    from pyqt_compat import QtCore, QtGui
    use_gui = True
except ImportError:
    warnings.warn("Import error; GUI will not be available.")
    use_gui = False
    pass

try:
    import nltk
except ImportError:
    warnings.warn("NLTK module not available.")
    try:
        QtGui.QMessageBox.warning("No NLTK module – Coquery", "The NLTK module could not be loaded. Automatic part-of-speech tagging will not be available.", QtGui.QMessageBox.Ok)
    except NameError:        
        pass
    nltk_available = False
else:
    nltk_available = True

import corpus
import options
from errors import *

insert_cache = collections.defaultdict(list)

class NLTKTokenizerError(Exception):
    def __init__(self, e, logger):
        logger.error("The NLTK tokenizer failed. This may be caused by a missing NLTK component. Please consult the 'Installing NLTK Data' guide on http://www.nltk.org/data.html for instructions on how to add the necessary components. Alternatively, you may want to use --no-nltk argument to disable the use of NLTK.")
        logger.error(e)
        if use_gui:
            error_box.ErrorBox.show(sys.exc_info(), self)
        
class NLTKTaggerError(Exception):
    def __init__(self, e, logger):
        logger.error("The NLTK tagger failed. This may be caused by a missing NLTK component. Please consult the 'Installing NLTK Data' guide on http://www.nltk.org/data.html for instructions on how to add the necessary components. Alternatively, you may want to use --no-nltk argument to disable the use of NLTK.")
        logger.error(e)
        if use_gui:
            error_box.ErrorBox.show(sys.exc_info(), self)

class MethodNotImplementedError(Exception):
    msg = "Function not implemented."

# module_code contains the Python skeleton code that will be used to write
# the Python corpus module."""
module_code = """# -*- coding: utf-8 -*-
#
# FILENAME: {name}.py -- a corpus module for the Coquery corpus query tool
# 
# This module was automatically created by corpusbuilder.py.
#

from __future__ import unicode_literals
from corpus import *

class Resource(SQLResource):
    name = '{name}'
    display_name = '{display_name}'
    db_name = '{db_name}'
    url = '{url}'
{variables}
{resource_code}
    
class Lexicon(SQLLexicon):
    provides = {lexicon_provides}
    
{lexicon_code}
class Corpus(SQLCorpus):
    provides = {corpus_provides}
    
{corpus_code}
"""

# Corpus builders should include code that determines word counts for 
# subcorpora. More specifically, they should produce a table with all
# combinations of corpus features and the associated number of words.
# For example, COCA should have a table with Genre, Year and Frequency,
# with 5 x 23 rows (5 Genres, 23 Years). 

class Column(object):
    """ Define an object that stores the description of a column in one 
    MySQL table."""
    primary = False
    key = False
    
    def __init__(self, name, data_type, index=True):
        """ Initialize the column. 'name' is the column name, 'data_type' is
        the MySQL data type for this column. If 'index' is True (the 
        default), an index will be created for this column."""
        self._name = name
        self._data_type = data_type
        self._index = index
        
    def __repr__(self):
        return "Column({}, {}, {})".format(self._name, self._data_type, self._index)
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):
        self._name = new_name
    
    @property
    def data_type(self):
        """
        Return the data type of the column.
        
        Returns
        -------
        data_type : string
            The data type of the column in the same form as used by the 
            MySQL CREATE TABLE command.
        
        """
        return self._data_type
    
    @property
    def base_type(self):
        """
        Return the base type of the column.
        
        This function does not return the field length, but only the base 
        data type, i.e. VARCHAR, MEDIUMINT, etc.
        
        Use data_type for the full column specification.

        Returns
        -------
        base_type : string
            A MySQL base data type.

        """
        return self._data_type.split()[0].partition("(")[0]
    
    @data_type.setter
    def data_type(self, new_type):
        self._data_type = new_type
        
class Primary(Column):
    """ Define a Column class that acts as the primary key in a table."""
    primary = True

    def __init__(self, name, data_type):
        super(Primary, self).__init__(name, data_type, False)

    def __repr__(self):
        return "Primary(name='{}', data_type='{}', {})".format(self._name, self._data_type, self._index)
        
class Link(Column):
    """ Define a Column class that links a table to another table. In MySQL
    terms, this acts like a foreign key."""
    key = True
    def __init__(self, name, table_name):
        super(Link, self).__init__(name, "", True)
        self._link = table_name

    def __repr__(self):
        return "Link(name='{}', '{}', data_type='{}')".format(self._name, self._link, self._data_type)
        
class Table(object):
    """ Define a class that is used to store table definitions."""
    def __init__(self, name):
        self._name = name
        self.columns = list()
        self.primary = None
        self._current_id = 0
        self._row_order = []
        self._add_cache = dict()
        self._commited = {}
        self._col_names = None

    @property
    def name(self):
        return self._name
        
    @name.setter
    def name(self, s):
        self._name = s
        
    def commit(self, db_connector, strange_check=False):
        """
        Commit the table content to the data base.
        
        This table commits the unsaved content of the table to the data base.
        After commiting, the values of all table entries are set to None, and
        only those data that have a value different from None will be 
        commited the next time this method is called.
        
        As this method is usually called after a file has been processed, 
        this ensures that all new table rows are commited, while at the same
        time preserving some memory space.
        """
        
        if self._add_cache:
            if self.primary.name not in self._col_names:
                fields = [self.primary.name] + self._col_names
            else:
                fields = self._col_names
            sql_string = "INSERT INTO {} ({}) VALUES ({})".format(
                self._name, ", ".join(fields), ", ".join(["%s"] * len(fields)))
            data = []
            new_keys = []
            # build a list of all new entries, i.e. those for which the value
            # is not Null
            for row in self._add_cache:
                row_id, row_data = self._add_cache[row]
                if row_data:
                    if strange_check:
                        if len(row_data) == 1:
                            for x in row_data:
                                row_data[x] = ["", row_data[x][0], "u"]
                    if self.primary.name in self._col_names:
                        data.append(list(row_data.values()))
                    else:
                        data.append([row_id] + list(row_data.values()))
                    new_keys.append(row)

            if data: 
                try:
                    db_connector.executemany(sql_string, data)
                except TypeError as e:
                    warnings.warn(sql_string)
                    warnings.warn(str(e))
                except Exception as e:
                    warnings.warn(sql_string)
                    warnings.warn(str(e))
                    raise e
                # Reset all new keys:
                for row in new_keys:
                    self._add_cache[row] = (self._add_cache[row][0], None)
    
    def _add_next_with_primary(self, row):
        """ Add a valid primary key to the data in the 'row' dictionary, 
        and store the data in add cache of the table. """ 
        self._current_id += 1
        self._add_cache[tuple([row[x] for x in self._row_order])] = (self._current_id, row)
        return self._current_id

    def _add_next_no_primary(self, row):
        """ Sotre the row in the add cache of the table. The primary key is 
        expected to be already in the row, so it is not added."""
        self._current_id = row[self.primary.name]
        self._add_cache[tuple([row[x] for x in self._row_order])] = (self._current_id, row)
        return self._current_id
    
    def add(self, row):
        """ Add a valid primary key to the data in the 'row' dictionary, 
        and store the data in add cache of the table. """ 

        if not self._col_names:
            self._col_names = list(row.keys())
        if self.primary.name in self._col_names:
            # if the primary key is in the row, use it:
            self._current_id = row[self.primary.name]
            self.add = self._add_next_no_primary
        else:
            # otherwise, the primary key is created:
            self._current_id += 1
            self.add = self._add_next_with_primary

        self._add_cache[tuple([row[x] for x in self._row_order])] = (self._current_id, row)
        return self._current_id
        
    def get_or_insert(self, values, case=False):
        """ 
        Returns the id of the first entry matching the values from the table.
        
        If there is no entry matching the values in the table, a new entry is
        added to the table based on the values. 
        description.
        
        Parameters
        ----------
        values : dict
            A dictionary with column names as keys, and the entry content
            as values.
            
        Returns
        -------
        id : int 
            The id of the entry, as it is stored in the MySQL table.
        """
        try:
            row_id = self._add_cache[tuple([values[x] for x in self._row_order])][0]
        except KeyError:
            return self.add(values)
        else:
            return row_id

    def find(self, values, db_connector):
        """ 
        Return the first row that matches the values, or None
        otherwise.
        """
        x = db_connector.find(self.name, values, [self.primary.name])
        if x:
            return x[0]
        else:
            return None
        
        #self._add_cache[tuple([row[x] for x in self._row_order])] = (self._current_id, row)
        #try:
            #return self.Con.find(table_name, values, [self._primary_keys[table_name]])[0]
        #except IndexError:
            #return None
        
    def add_column(self, column):
        self.columns.append(column)
        if column.primary:
            self.primary = column
        else:
            self._row_order.append(column.name)

    def get_column(self, name):
        """
        Return the specified column.
        
        Parameters
        ----------
        name : string
            The name of the column
            
        Returns
        -------
        col : object or NoneType
            The Column object matching the name, or None.
        """
        for x in self.columns:
            if x.name == name:
                return x
        return None
            
    def get_create_string(self):
        """
        Generates the MySQL command required to create the table.
        
        Returns
        -------
        S : str
            A string that can be sent to the MySQL server in order to create
            the table according to the specifications.
        """
        str_list = []
        columns_added = set([])
        for column in self.columns:
            if column.name not in columns_added:
                if column.primary:
                    # do not add AUTO_INCREMENT to ENUMs:
                    if column.data_type.upper().startswith("ENUM"):
                        pattern = "`{}` {}"
                    else:
                        pattern = "`{}` {} AUTO_INCREMENT"
                    str_list.insert(0, pattern.format(column.name, column.data_type))
                    str_list.append("PRIMARY KEY (`{}`)".format(column.name))
                else:
                    str_list.append("`{}` {}".format(
                        column.name,
                        column.data_type))
                columns_added.add(column.name)
        return ", ".join(str_list)
    
class BaseCorpusBuilder(corpus.BaseResource):
    """ 
    This class is the base class used to build and install a corpus for 
    Coquery. For corpora currently not supported by Coquery, new builders 
    can be developed by subclassing this class.
    """
    logger = None
    module_code = None
    name = None
    table_description = None
    lexicon_features = None
    #corpus_features = None
    arguments = None
    name = None
    additional_arguments = None
    parser = None
    Con = None
    additional_stages = []
    start_time = None
    file_filter = None
    encoding = "utf-8"
    expected_files = []
    special_files = []
    __version__ = "1.0"
    
    def __init__(self, gui=False):
        self.module_code = module_code
        self.table_description = {}
        self.lexicon_features = []
        #self.corpus_features = []
        self._time_features = []
        #self._tables = {}
        self._id_count = {}
        self._primary_keys = {}
        self._interrupted = False
        self._blocklist = set()
        self._new_tables = {}
        
        self._corpus_buffer = []
        self._corpus_id = 0
        self._widget = gui
        
        self._source_count = collections.Counter()
        
        # set up argument parser:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("name", help="name of the corpus", type=str)
        self.parser.add_argument("path", help="location of the text files", type=str)
        self.parser.add_argument("--db_user", help="name of the MySQL user (default: coquery)", type=str, default="coquery", dest="db_user")
        self.parser.add_argument("--db_password", help="password of the MySQL user (default: coquery)", type=str, default="coquery", dest="db_password")
        self.parser.add_argument("--db_host", help="name of the MySQL server (default: localhost)", type=str, default="127.0.0.1", dest="db_host")
        self.parser.add_argument("--db_port", help="port of the MySQL server (default: 3306)", type=int, default=3306, dest="db_port")
        self.parser.add_argument("--db_name", help="name of the MySQL database to be used (default: same as 'name')", type=str)
        self.parser.add_argument("-o", help="optimize field structure (can be slow)", action="store_true")
        self.parser.add_argument("-v", help="produce verbose output", action="store_true", dest="verbose")
        self.parser.add_argument("-i", help="create indices (can be slow)", action="store_true")
        if nltk_available:
            self.parser.add_argument("--no-nltk", help="Do not use NLTK library for automatic part-of-speech tagging", action="store_false", dest="use_nltk")
        self.parser.add_argument("-l", help="load source files", action="store_true")
        self.parser.add_argument("-c", help="create database tables", action="store_true")
        self.parser.add_argument("-w", help="write corpus module", action="store_true")
        self.parser.add_argument("--corpus_path", help="target location of the corpus library (default: $COQUERY_HOME/corpora)", type=str)
        self.parser.add_argument("--self_join", help="create a self-joined table (can be very big)", action="store_true")
        self.parser.add_argument("--encoding", help="select a character encoding for the input files (e.g. latin1, default: {})".format(self.encoding), type=str, default=self.encoding)
        self.additional_arguments()

    def add_tag_table(self):
        """ 
        Create the table description for a tag table.
        
        Corpora should usually have a tag table that is used to store
        text information. This method is called during :func:`build` and
        adds a tag table if none is present yet.
        
        Currently, the tag table cannot be queried, so no indices will be
        created for the data columns.
        """
        
        self.tag_table = "tags"
        self.tag_id = "TagId"
        self.tag_label = "Tag"
        self.tag_type = "Type"
        self.tag_corpus_id = self.corpus_id
        self.tag_attribute = "Attribute"
        
        self.create_table_description(self.tag_table,
            [Primary(self.tag_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.tag_type, "ENUM('open', 'close', 'empty')"),
             Column(self.tag_label, "TINYTEXT NOT NULL"),
             Link(self.tag_corpus_id, self.corpus_table),
             Column(self.tag_attribute, "TINYTEXT NOT NULL", index=False)])

        self.add_index_to_blocklist(("tags", self.tag_label))
        self.add_index_to_blocklist(("tags", self.tag_type))
        self.add_index_to_blocklist(("tags", self.tag_type))
        self.add_index_to_blocklist(("tags", self.tag_attribute))

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
        if not self._widget:
            self.arguments, unknown = self.parser.parse_known_args()
            if not nltk_available:
                self.arguments.use_nltk = False
            if not self.arguments.db_name:
                self.arguments.db_name = self.arguments.name
            if not self.arguments.corpus_path:
                self.arguments.corpus_path = options.cfg.corpora_path
            self.name = self.arguments.name
            
    def additional_arguments(self):
        """ Use this function if your corpus installer requires additional
        arguments."""
        pass
    
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
            self._new_tables[table].commit(self.Con, strange_check=True)

        if self._corpus_buffer:
            sql_string = "INSERT INTO {} ({}) VALUES ({})".format(
                self.corpus_table, ", ".join(self._corpus_keys), ", ".join(["%s"] * (len(self._corpus_keys))))
            data = [list(row.values()) for row in self._corpus_buffer]
            if data: 
                try:
                    self.Con.executemany(sql_string, data)
                except TypeError as e:
                    warnings.warn(sql_string)
                    warnings.warn(data[0])
                    raise(e)
            self._corpus_buffer = []        
            
        self.Con.commit()

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
                    raise KeyError("Table description for '{}' contains a link to unknown table '{}'".format(table_name, x._link))
            new_table.add_column(x)
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

    def setup_logger(self):
        """ 
        Initialize the logger.
        """
        class TextwrapFormatter(logging.Formatter):
            def __init__(self, fmt):
                super(TextwrapFormatter, self).__init__(fmt=fmt)
                self.wrap = textwrap.TextWrapper(width=79, subsequent_indent="        ").fill
                
            def format(self, entry):
                return "\n%s\n" % self.wrap(super(TextwrapFormatter, self).format(entry))
        
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel (logging.INFO)
        log_file_name = "%s.log" % self.name
        file_handler = logging.FileHandler(log_file_name)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
        self.logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(TextwrapFormatter("%(levelname)s %(message)s"))
        stream_handler.setLevel(logging.WARNING)
        self.logger.addHandler(stream_handler)

    def build_create_tables(self):
        """ 
        Create the MySQL tables used by the corpus, based on the column
        information given in the table description (see
        :func:``create_table_description``).
        """
        
        self.Con.start_transaction()
        self.add_tag_table()

        # initialize progress bars:
        if self._widget:
            self._widget.progressSet.emit(len(self._new_tables), "Creating tables... (%v of %m)")
            self._widget.progressUpdate.emit(0)

        for i, current_table in enumerate(self._new_tables):
            if not self.Con.has_table(current_table):
                self.Con.create_table(current_table, self._new_tables[current_table].get_create_string())
            if self._widget:
                self._widget.progressUpdate.emit(i + 1)
            if self.interrupted:
                return
        self.Con.commit()

    @staticmethod
    def get_file_list(path, file_filter):
        """ 
        Return a list of valid file names from the given path.
        
        This method recursively searches in the directory ``path`` and its
        subdirectories for files that match the file filter specified in 
        the class attribute ``file_filter``.
        
        Parameters
        ----------
        path : string
            The path in which to look for files
            
        Returns
        -------
        l : list
            A list of strings, each representing a file name        
        """
        L = []
        for source_path, folders, files in os.walk(path):
            for current_file in files:
                full_name = os.path.join(source_path, current_file)
                if not file_filter or fnmatch.fnmatch(current_file, file_filter):
                    L.append(full_name)
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
                if not self.file_filter or fnmatch.fnmatch(current_file, self.file_filter):
                    return True
        return False

    @staticmethod
    def validate_files(l):
        """
        Validates the file list.
        
        The default implementation will compare the content of the argument 
        to the class attribute expected_files. If there is an entry in 
        expected_files that is not also in the argument list, the file list 
        is considered to be invalid.
        
        Parameters
        ----------
        l : list
            A list of file names as created by get_file_list()
            
        """

        found_list = [x for x in [os.path.basename(y) for y in l] if x.lower() in [y.lower() for y in BaseCorpusBuilder.expected_files]]
        if len(found_list) < len(BaseCorpusBuilder.expected_files):
            missing_list = [x for x in BaseCorpusBuilder.expected_files if x.lower() not in [y.lower() for y in found_list]]
            sample = "<br/>".join(missing_list[:5])
            if len(missing_list) > 6:
                sample = "{}</code>, and {} other files".format(sample, len(missing_list) - 3)
            elif len(missing_list) == 6:
                sample = "<br/>".join(missing_list[:6])
            raise RuntimeError("<p>Not all expected corpora files were found in the specified corpus data directory. Missing files are:</p><p><code>{}</code></p>".format(sample))
        
    def get_corpus_code(self):
        """ 
        Return a text string containing the Python source code for the 
        Corpus class of this module.
        
        The code is obtained from the the class attribute self._corpus_code.
        """
        try:
            lines = [x for x in inspect.getsourcelines(self._corpus_code)[0] if not x.strip().startswith("class")]
        except AttributeError:
            lines = []
        return "".join(lines)

    def add_time_feature(self, x):
        self._time_features.append(x)
    
    def get_lexicon_code(self):
        """ return a text string containing the Python source code from
        the class attribute self._lexicon_code. This function is needed
        to add lexicon-specific code the Python corpus module."""
        try:
            lines = [x for x in inspect.getsourcelines(self._lexicon_code)[0] if not x.strip().startswith("class")]
        except AttributeError:
            lines = []
        return "".join(lines)
    
    def get_resource_code(self):
        """ return a text string containing the Python source code from
        the class attribute self._resource_code. This function is needed
        to add resource-specific code the Python corpus module."""
        try:
            lines = [x for x in inspect.getsourcelines(self._resource_code)[0] if not x.strip().startswith("class")]
        except AttributeError:
            lines = []
        lines.insert(0, "    time_features = {}".format(
            "[{}]".format(", ".join(['"{}"'.format(x) for x in self._time_features]))))
        return "".join(lines)
    
    def get_method_code(self, method):
        pass

    def store_filename(self, file_name):
        self._file_name = file_name
        self._value_file_name = os.path.basename(file_name)
        self._value_file_path = os.path.split(file_name)[0]

        self._file_id = self.table(self.file_table).get_or_insert(
            {self.file_name: self._value_file_name,
             self.file_path: self._value_file_path})

    #def get_lemma(self, word):
        #""" Return a lemma for the word. By default, this is simply the
        #word in lower case, but this method can be overloaded with methods
        #that use e.g. lemma dictionaries. 
        #The method is used by the default file processing methods. If your
        #corpus implements a specific file processing method, get_lemma() may
        #be obsolete. """
        #return word.lower()
    
    #def get_lemma_id(self, word):
        #""" Return a lemma identifier for the word. If there is a separate 
        #lemma table, the identifier is an index to that table. Otherwise, 
        #the identifier is the lemma label."""
        #try:
            #return self.table_get(self.lemma_table, 
                #{self.lemma_label: self.get_lemma(word)})
        #else:
            #return self.get_lemma(word)
    
    #def get_pos(self, word):
        #""" Return the part-of-speech for the word. By default, an empty
        #string is returned, but this method may be overloaded with methods
        #that use for example a pos-tagged dictionary.
        #The method is used by the default file processing methods. If your
        #corpus implements a specific file processing method, get_lemma() may
        #be obsolete. """
        #return ""
    
    #def get_pos_id(self, word):
        #""" Return a part-of-speech identifier for the word. If there is a 
        #separate part-of-speech table, the identifier is an index to that 
        #table. Otherwise, the identifier is the part-of-speech label."""
        
        #if "pos_table" in self.table_description:
            #return self.table_get(self.pos_table, 
                #{self.pos_label: self.get_pos(word)})
        #else:
            #return self.get_pos(word)        

    #def get_transcript(self, word):
        #""" Return the phonemic transcript for the word. By default, an 
        #empty string is returned, but this method may be overloaded with 
        #methods that use for example a pronunciation dictionary.
        #The method is used by the default file processing methods. If your
        #corpus implements a specific file processing method, get_lemma() may
        #be obsolete. """
        #return ""
    
    #def get_transcript_id(self, word):
        #""" Return a transcription identifier for the word. If there is a 
        #separate transcription table, the identifier is an index to that 
        #table. Otherwise, the identifier is the transcript label."""
        
        #if "transcript_table" in self.table_description:
            #return self.table_get(self.transcript_table, 
                #{self.transcript_label: self.get_transcript(word)})
        #else:
            #return self.get_transcript(word)        

    def process_xlabel_file(self, file_name):
        """ 
        Process an xlabel file.
        
        This method reads the content of the file, and interprets it as an
        ESPS/waves+ xlabel file. Xlabel filess are used in some spoken 
        corpora to represent phonetic annotations. A description of the file format can be found here: 
        
        http://staffhome.ecm.uwa.edu.au/~00014742/research/speech/local/entropic/ESPSDoc/waves/manual/xlabel.pdf

        Basically, an xlabel file consists of a header and a file body, 
        separated by a row containing only the hash mark '#'. This method 
        ignores the data from the header. Rows in the file body consist of
        three columns ``time color word``, separated by whitespace. Rows with less than three columns are ignored.
        
        Parameters
        ----------
        file_name : string
            The path name of the file that is to be processed
        """
        file_body = False
        # read file using the specified encoding (default is 'utf-8), and 
        # retry using 'ISO-8859-1'/'latin-1' in case of an error:
        try:
            with codecs.open(file_name, "r", encoding=self.arguments.encoding) as input_file:
                input_data = input_file.read()
        except UnicodeDecodeError:
            with codecs.open(file_name, "r", encoding="ISO-8859-1") as input_file:
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
                
                # create a dictionary containing the word label, plus
                # additional labels if provided by the lexicon:
                word_dict = {}
                word_dict[self.word_label] = word
                if "LEX_LEMMA" in self.lexicon_features:
                    word_dict[self.word_lemma_id] = self.get_lemma_id(word)
                if "LEX_POS" in self.lexicon_features:
                    word_dict[self.word_pos] = self.get_pos_id(word)
                if "LEX_PHON" in self.lexicon_features:
                    word_dict[self.word_transcript_id] = self.get_transcript_id(word)

                # get a word id for the current word:
                word_id = self.table(self.word_table).get_or_insert(word_dict)
                
                # add the word as a new token to the corpus:
                
                self.add_token_to_corpus(
                    {self.corpus_word_id: word_id, 
                        self.corpus_file_id: self._file_id,
                        self.corpus_time: time})
                
    def process_text_file(self, file_name):
        """ 
        Process a text file.
        
        This method reads the content of the file, and interprets it as an
        plain text file. It first attempt to tokenize the text, and to 
        assign a POS tag to each token (using NLTK if possible). Then, if
        the token does not exist in the word table, add a new word with its 
        POS tag to the word table. Then, try to lemmatize any new word. 
        Finally, add the token with its word identifier to the corpus table,
        and proceed with the next word.
        
        Parameters
        ----------
        file_name : string
            The path name of the file that is to be processed
        """
        
        # Read raw text from file:
        try:
            with codecs.open(file_name, "r", encoding=self.arguments.encoding) as input_file:
                raw_text = input_file.read()
        except UnicodeDecodeError:
            with codecs.open(file_name, "r", encoding="ISO-8859-1") as input_file:
                raw_text = input_file.read()
            
        tokens = []
        pos_map = []

        # if possible, use NLTK for lemmatization, tokenization, and tagging:
        if self.arguments.use_nltk:
            # the WordNet lemmatizer will be used to obtain the lemma for a
            # given word:
            self._lemmatize = lambda x,y: nltk.stem.wordnet.WordNetLemmatizer().lemmatize(x, pos=y)
            
            # The NLTK POS tagger produces some labels that are different from
            # the labels used in WordNet. In order to use the WordNet 
            # lemmatizer for all words, we need a function that translates 
            # these labels:
            self._pos_translate = lambda x: {'NN': nltk.corpus.wordnet.NOUN, 
                'JJ': nltk.corpus.wordnet.ADJ,
                'VB': nltk.corpus.wordnet.VERB,
                'RB': nltk.corpus.wordnet.ADV} [x.upper()[:2]]

            # Create a list of sentences from the content of the current file
            # and process this list one by one:
            sentence_list = nltk.sent_tokenize(raw_text)
            for sentence in sentence_list:
                # use NLTK tokenizer and POS tagger on this sentence:
                tokens = nltk.word_tokenize(sentence)
                pos_map = nltk.pos_tag(tokens)
                    
                for current_token, current_pos in pos_map:
                    # store each token:
                    self.add_token(current_token.strip(), current_pos)
        else:
        # The default lemmatizer is pretty dumb and simply turns the 
        # word-form to lower case so that at least 'Dogs' and 'dogs' are 
        # assigned the same lemma -- which is a different lemma from the
        # one assigned to 'dog' and 'Dog'.
        #
        # If NLTK is used, the lemmatizer will use the data from WordNet,
        # which will result in much better results.
            self._lemmatize = lambda x: x.lower()
            self._pos_translate = lambda x: x
            
            # use a dumb tokenizer that simply splits the file content by 
            # spaces:            
            tokens = raw_text.split(" ")
            tokens = [x.strip() for x in tokens if x.strip()]
            if not pos_map:
                pos_map = zip(tokens, [""] * len(tokens))
                if "LEX_POS" in self.lexicon_features:
                    self.lexicon_features.remove("LEX_POS")
            
            for current_token, current_pos in pos_map:
                # any punctuation at the beginning of the token is added to the
                # corpus as a punctuation token, and is also stripped from the
                # token:
                while current_token and current_token[0] in string.punctuation:
                    self.add_token(current_token[0], "PUNCT")
                    current_token = current_token[1:]
                if current_token:
                    # add the token to the corpus:
                    self.add_token(current_token, current_pos)
    
    def add_next_token_to_corpus(self, values):
        self._corpus_id += 1
        values[self.corpus_id] = self._corpus_id
        self._corpus_buffer.append(values)
        
    def add_token_to_corpus(self, values):
        if len(values) < len(self._new_tables[self.corpus_table].columns) - 2:
            raise IndexError
        self._corpus_id += 1
        values[self.corpus_id] = self._corpus_id
        self._corpus_keys = values.keys()
        self._corpus_buffer.append(values)
        self.add_token_to_corpus = self.add_next_token_to_corpus
    
    def add_token(self, token_string, token_pos):
        # get lemma string:
        if token_string in string.punctuation:
            token_pos = "PUNCT"
            lemma = token_string
        else:
            try:
                # use the current lemmatizer to assign the token to a lemma: 
                lemma = self._lemmatize(token_string, self._pos_translate(token_pos)).lower()
            except Exception as e:
                lemma = token_string.lower()

        # get word id, and create new word if necessary:
        word_dict = {self.word_lemma: lemma, 
                    self.word_label: token_string}
        if token_pos and "word_pos" in dir(self):
            word_dict[self.word_pos] = token_pos 
        word_id = self.table(self.word_table).get_or_insert(word_dict, case=True)

        # store new token in corpus table:
        self.add_token_to_corpus(
            {self.corpus_word_id: word_id,
             self.corpus_file_id: self._file_id})

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
            #S = S.splitlines()
            S = []
            self.logger.error(e)
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
        raise MethodNotImplementedError

    def xml_get_meta_information(self, root):
        """ Retrieve and store all meta information from the root."""
        raise MethodNotImplementedError
        
    def xml_process_element(self, element):
        """ Process the XML element. Processing involves several stages:
        
        1. Call xml_preprocess_tag(element) for tag actions when entering 
        2. Call xml_process_content(element.text) to process the content
        3. Call xml_process_element() for every nested element
        4. Call xml_process_tail(element.tail) to process the tail
        5. Call xml_postprocess_tag(element) for tag actions when leaving

        """
        self.xml_preprocess_tag(element)
        if element.text:
            self.xml_process_content(element.text)
        if list(element):
            for child in element:
                self.xml_process_element(child)
        if element.tail:
            self.xml_process_tail(element.tail)
        self.xml_postprocess_tag(element)
    
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
                self.tag_attribute: ", ".join(
                    ["{}={}".format(x, attributes[x]) for x in attributes])})

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
                self.tag_attribute: ", ".join(
                    ["{}={}".format(x, attributes[x]) for x in attributes])})

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
            {self.tag_label: "{}".format(tag),
             self.tag_corpus_id: self._corpus_id + 1,
             self.tag_type: "empty",
             self.tag_attribute: ", ".join(
                ["{}={}".format(x, attributes[x]) for x in attributes])})

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
        files = self.get_file_list(self.arguments.path, self.file_filter)
        if not files:
            self.logger.warning("No files found at %s" % self.arguments.path)
            return

        if self._widget:
            self._widget.progressSet.emit(len(files), "Reading text files... (%v of %m)")
            self._widget.progressUpdate.emit(0)
            
        #for x in self.table_description:
            #self._id_count[x] = self.Con.get_max(x, self._primary_keys[x])
        
        for i, file_name in enumerate(files):
            if self.interrupted:
                return

            if not self.Con.find(self.file_table, {self.file_path: file_name}):
                self.logger.info("Loading file %s" % (file_name))
                self.store_filename(file_name)
                self.process_file(file_name)
                
            if self._widget:
                self._widget.progressUpdate.emit(i + 1)

            self.commit_data()

    def build_create_frequency_table(self):
        """ 
        Create a frequency table for all combinations of corpus features.
        
        This method creates a database table named 'coq_frequency_count' with 
        all corpus features as columns, and a row for each comination of 
        corpus features that occur in the corpus. The last column 'Count' 
        gives the number of tokens in the corpus that occur in the corpus.
        
        The frequency table can be used to look up quickly the size of a 
        subcorpus as well as the overall corpus. This is important for 
        reporting frequency counts as per-million-word frequencies.
        """

        pass
        #print(self.module_content)
        #print(self.name)

        #module = importlib.import_module("..{}".format(self.name), "installer.{}".format(self.name))

        #exec self.resource_content
        ##print(self.resource_content)

        #module_path = os.path.join(self.arguments.corpus_path, "{}.py".format(self.name))
        #module_path = "/home/kunibert/Dev/coquery/coquery/corpora/ice_ng.py"
        #print(module_path)
        #print(sys.modules.keys())
        #module = imp.load_source(self.name, module_path)
        #print(module, dir(module))
        ##resource = module.Resource
        ##print(resource)
        
        
        
    
    def create_joined_table(self):
        pass
    
    def build_optimize(self):
        """ Optimizes the table columns so that they use a minimal amount
        of disk space."""
        totals = 0
        #for current_table in self.table_description:
            #totals += len(self.table_description[current_table]["CREATE"])

        for table in self._new_tables:
            totals += len(self._new_tables[table].columns)

        totals -= 1
        
        if self._widget:
            self._widget.progressSet.emit(totals, "Optimizing table columns... (%v of %m)")
            self._widget.progressUpdate.emit(0)
            
        column_count = 0
        self.Con.start_transaction()
        for table_name in self._new_tables:
            table = self._new_tables[table_name]
            if self.interrupted:
                return

            for column in table.columns:
                try:
                    ot = self.Con.get_optimal_field_type(table.name, column.name)
                except TypeError:
                    continue
                dt = column.data_type
                if dt.lower() != ot.lower():
                    try:
                        ot = ot.decode("utf-8")
                    except AttributeError:
                        pass
                    self.logger.info("Optimising column {}.{} from {} to {}".format(
                        table.name, column.name, dt, ot))
                    try:
                        self.Con.modify_field_type(table.name, column.name, ot)
                    except (
                        dbconnection.mysql.InterfaceError, 
                        dbconnection.mysql.DataError,
                        dbconnection.mysql.DatabaseError, 
                        dbconnection.mysql.OperationalError, 
                        dbconnection.mysql.IntegrityError, 
                        dbconnection.mysql.InternalError, 
                        dbconnection.mysql.ProgrammingError) as e:
                        if self.logger:
                            self.logger.warning(e)
                    else:
                        column.data_type = ot
                column_count += 1

                if self._widget:
                    self._widget.progressUpdate.emit(column_count + 1)

        if self.interrupted:
            return
        self.Con.commit()
        
    def add_index_to_blocklist(self, index):
        self._blocklist.add(index)
        
    def remove_index_from_blocklist(self, index):
        self._blocklist.remove(index)
        
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
                if not isinstance(column, Primary) and (table.name, column.name) not in self._blocklist:
                    index_list.append((table.name, column.name))

        if self._widget:
            self._widget.progressSet.emit(len(index_list), "Creating indices... (%v of %m)")
            self._widget.progressUpdate.emit(0)

        index_count = 0
        self.Con.start_transaction()
        i = 0
        for table, column in index_list:
            if self.interrupted:
                return

            if not self.Con.has_index(table, column):
                self.logger.info("Creating index {} on table '{}'".format(
                    column, table))
                try:
                    this_column = self._new_tables[table].get_column(column)
                    
                    # indices for TEXT/BLOB columns require a key length:
                    if this_column.base_type.endswith("TEXT") or this_column.base_type.endswith("BLOB"):
                        length = self.Con.get_index_length(table, column)
                    else:
                        length = None

                    self.Con.create_index(table, column, [column], index_length=length)
                except (
                        dbconnection.mysql.InterfaceError, 
                        dbconnection.mysql.DataError,
                        dbconnection.mysql.DatabaseError, 
                        dbconnection.mysql.OperationalError, 
                        dbconnection.mysql.IntegrityError, 
                        dbconnection.mysql.InternalError, 
                        dbconnection.mysql.ProgrammingError) as e:
                    if self.logger:
                        self.logger.warning(e)
                
                i += 1
                if self._widget:
                    self._widget.progressUpdate.emit(i + 1)

        if self.interrupted:
            return

        self.Con.commit()

    @staticmethod
    def get_class_variables():
        return dir(BaseCorpusBuilder)

    def verify_corpus(self):
        """
        Apply some basic checks to determine whether a MySQL database is
        available to the corpus module.
        
        This method first checks whether a database under the given name is
        exists on the MySQL server. It then tests whether the database
        contains all data tables specified in the table descriptions defined 
        by previous calls to :func:`create_table_description`.
        
        Returns
        -------
        bool : boolean
            True if the database and all tables in the table
            descriptions exist, or False otherwise.
        """
        no_fail = True
        if not self.Con.has_database(self.arguments.db_name):
            no_fail = False
            self.logger.warning("Database {} not found.".format(self.arguments.db_name))
        for x in self.table_description:
            if not self.Con.has_table(x):
                self.logger.warning("Table {} not found.".format(x))
                no_fail = False
        return no_fail
    
    def ask_overwrite(self, warning_msg, existing_code, output_code):
        existing_code = existing_code.split("\n")
        print("\n|".join(existing_code))
        output_code = output_code.split("\n")
        print("\n|".join(output_code))
        if not self._widget:
            while True:
                print("Enter Y to overwrite the existing version.")
                print("Enter N to keep the existing version.")
                print("Enter V to view the difference between the two versions.")
                try:
                    response = raw_input("Overwrite? [Y, N, or V] ")
                except NameError:
                    response = input("Overwrite? [Y, N, or V] ")
                if response.upper() in ["Y", "N"]:
                    break
                else:
                    for x in difflib.context_diff(existing_code, output_code):
                        sys.stdout.write(x)
            return response.upper() == "Y"
        else:
            warning_msg = "<p>{}</p><p>Do you really want to overwrite the existing version?</p>".format(warning_msg)
            return QtGui.QMessageBox.question(self._widget, "Library exists.", warning_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
                
    def build_write_module(self):
        """ Write a Python module with the necessary specifications to the
        Coquery corpus module directory."""
        
        if not self.arguments.w:
            return
        
        base_variables = type(self).get_class_variables()

        # all class variables that are defined in this class and which...
        # - are note stored in the base class
        # - do not start with an underscore '_'
        # - are not class methods
        # are considered to be part of the database specification and will
        # be included with their value in the Python code:
        
        variable_names = [x for x in dir(self) 
                          if x not in base_variables 
                          and not x.startswith("_")
                          and not inspect.ismethod(self.__getattribute__(x))]
        variable_strings = []
        for variable_name in sorted(variable_names):
            try:
                variable_strings.append("    {} = '{}'".format(
                    variable_name, type(self).__dict__[variable_name]))
            except KeyError:
                variable_strings.append("    {} = '{}'".format(
                    variable_name, self.__dict__[variable_name]))
        variable_code = "\n".join(variable_strings)
        
        lexicon_provides = "[{}]".format(", ".join(self.lexicon_features))
        corpus_provides = "[]"

        self.module_content = self.module_code.format(
                name=self.name,
                display_name=self.get_name(),
                db_name=self.arguments.db_name,
                url=self.get_url(),
                variables=variable_code,
                lexicon_provides=lexicon_provides,
                corpus_provides=corpus_provides,
                corpus_code=self.get_corpus_code(),
                lexicon_code=self.get_lexicon_code(),
                resource_code=self.get_resource_code())

        if os.access(options.cfg.corpora_path, os.W_OK|os.X_OK):
            corpus_path = os.path.join(options.cfg.corpora_path, options.cfg.current_server)
        else:
            corpus_path = os.path.join(options.cfg.custom_corpora_path, options.cfg.current_server)
        
        if not os.path.exists(corpus_path):
            os.makedirs(corpus_path)
        path = os.path.join(corpus_path, "{}.py".format(self.name))
        # Handle existing versions of the corpus module
        if os.path.exists(path):
            # Read existing code as string:
            with codecs.open(path, "r") as input_file:
                existing_code = input_file.read()
            # Keep if existing code is the same as the new code:
            if existing_code == self.module_content:
                self.logger.info("Identical corpus module %s already exists." % path)
                return
            # Ask if the existing code should be overwritten:
            else:
                msq_module_exists = "A different version of the corpus module already exists in %s." % path
                try:
                    self.logger.warning(msq_module_exists)
                except NameError:
                    pass
                if self.ask_overwrite(msq_module_exists, existing_code, self.module_content):
                    self.logger.warning("Overwriting existing corpus module.")
                else:
                    return
        
        # write module code:
        with codecs.open(path, "w") as output_file:
            output_file.write(self.module_content)
            self.logger.info("Library %s written." % path)
            
    def setup_db(self):
        """ Create a connection to the server, and creates the database if
        necessary."""
        dbconnection.verbose = self.arguments.verbose
        dbconnection.logger = self.logger
        self.Con = dbconnection.DBConnection(
            db_host=self.arguments.db_host,
            db_user=self.arguments.db_user,
            db_pass=self.arguments.db_password,
            db_port=self.arguments.db_port,
            local_infile=1)
        if self.Con.has_database(self.arguments.db_name) and self.arguments.l:
            self.Con.drop_database(self.arguments.db_name)
        if self.arguments.c:
            self.Con.create_database(self.arguments.db_name)
        self.Con.use_database(self.arguments.db_name)

        cursor = self.Con.Con.cursor()
        self.Con.execute(cursor, "SET autocommit=0")
        self.Con.execute(cursor, "SET unique_checks=0")
        self.Con.execute(cursor, "SET foreign_key_checks=0")

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
    def get_description():
        return []

    @staticmethod
    def get_references():
        return []

    @staticmethod
    def get_url():
        return "(no URL)"
    
    @staticmethod
    def get_name():
        return "(unnamed)"
    
    @staticmethod
    def get_db_name():
        return "unnamed"

    def initialize_build(self):
        """ Start logging, start the timer."""
        self.start_time = time.time()
        self.logger.info("--- Starting ---")
        self.logger.info("Building corpus %s" % self.name)
        self.logger.info("Command line arguments: %s" % " ".join(sys.argv[1:]))
        if not self._widget:
            print("\n%s\n" % textwrap.TextWrapper(width=79).fill(" ".join(self.get_description())))

    def build_finalize(self):
        """ Wrap up everything after the corpus installation is complete. """
        if self.interrupted:
            try:
                self.Con.drop_database(self.arguments.db_name)
            except:
                pass
            self.Con.close()
            self.logger.info("--- Interrupted (after %.3f seconds) ---" % (time.time() - self.start_time))
        else:
            self.Con.close()
            self.logger.info("--- Done (after %.3f seconds) ---" % (time.time() - self.start_time))

    def build(self):
        """ 
        Build the corpus database, and install the corpus module.
        
        This method runs all steps required to make the data from a corpus 
        available to Coquery. Most importantly, it calls these functions (in
        order):
        
        * :func:`build_create_tables` to create all MySQL tables that were specified by previous calls to :func:`create_table_description`
        * :func:`build_load_files` to read all datafiles, process their content, and insert the content into the MySQL tables
        * :func:`build_self_joined` to create a self-joined corpus table that increases query performance of multi-token queries, but which requires a lot of disk space
        * :func:`build_optimize` to ensure that the MySQL tables use the optimal data format for the data
        * :func:`build_create_indices` to create database indices that speed up the MySQL queries
        * :func:`build_write_module` to write the corpus module to the ``corpora`` sub-directory of the Coquery install directory (or the corpus directory specified in the configuration file)
        
        .. note:: 
        
            Self-joined tables are currently not supported by 
            :class:`BaseCorpusBuilder`. Corpus installers that want to use
            this feature have to override :func:`build_self_joined`.
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
        
        try:
            self.check_arguments()
            if not self._widget:
                self.setup_logger()
            self.setup_db()

            if self._widget:
                steps = 2 + int(self.arguments.c) + int(self.arguments.l) + int(self.arguments.self_join) + int(self.additional_stages != []) + int(self.arguments.o) + int(self.arguments.i) 
                self._widget.ui.progress_bar.setMaximum(steps)

            current = 0
            current = progress_next(current)
            self.initialize_build()
            progress_done()
            
            if (self.arguments.l or self.arguments.c) and not self.validate_path(self.arguments.path):
                raise RuntimeError("The given path {} does not appear to contain valid corpus data files.".format(self.arguments.path))
            
            if self.arguments.c and not self.interrupted:
                current = progress_next(current)
                self.build_create_tables()
                progress_done()

            if self.arguments.l and not self.interrupted:
                current = progress_next(current)
                self.build_load_files()
                progress_done()

            if self.arguments.self_join and not self.interrupted:
                current = progress_next(current)
                self.build_self_joined()
                current = progress_done()

            if not self.interrupted:
                current = progress_next(current)
                for stage in self.additional_stages and not self.interrupted:
                    stage()
                progress_done()

            if self.arguments.o and not self.interrupted:
                current = progress_next(current)
                self.build_optimize()
                progress_done()

            if self.arguments.i and not self.interrupted:
                current = progress_next(current)
                self.build_create_indices()
                progress_done()

            if self.verify_corpus() and not self.interrupted:
                current = progress_next(current)
                self.build_write_module()
                current = progress_next(current)
                
            if not self.interrupted:
                current = progress_next(current)
                self.build_create_frequency_table()
                progress_done

            self.build_finalize()
        except Exception as e:
            warnings.warn(str(e))
            raise e
            
if use_gui:
    import options
    import corpusInstallerUi
    import error_box
    import QtProgress
    from defines import * 
    
    class InstallerGui(QtGui.QDialog):
        button_label = "&Install"
        window_title = "Corpus installer – Coquery"
        
        installStarted = QtCore.Signal()
        
        progressSet = QtCore.Signal(int, str)
        labelSet = QtCore.Signal(str)
        progressUpdate = QtCore.Signal(int)
        
        generalUpdate = QtCore.Signal(int)
        
        def __init__(self, builder_class, parent=None):
            super(InstallerGui, self).__init__(parent)

            import __init__
            self.logger = logging.getLogger(__init__.NAME)        
            
            self.state = None
            
            self.ui = corpusInstallerUi.Ui_CorpusInstaller()
            self.ui.setupUi(self)
            self.ui.progress_box.hide()
            self.ui.button_input_path.clicked.connect(self.select_path)
            self.ui.input_path.textChanged.connect(lambda: self.validate_dialog(check_path=True))
            self.ui.radio_complete.toggled.connect(self.changed_radio)
            self.ui.radio_only_module.toggled.connect(self.changed_radio)
            self.ui.input_path.textChanged.connect(self.check_input)

            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setText(self.button_label)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).clicked.connect(self.start_install)
            
            self.installStarted.connect(self.show_progress)
            self.progressSet.connect(self.set_progress)
            self.labelSet.connect(self.set_label)
            self.progressUpdate.connect(self.update_progress)
            
            self.generalUpdate.connect(self.general_update)
            
            if options.cfg.corpus_source_path != os.path.expanduser("~"):
                self.ui.input_path.setText(options.cfg.corpus_source_path)
            
            self.accepted = False
            try:
                self.builder_class = builder_class
            except Exception as e:
                msg = msg_corpus_broken.format(
                    name=basename,
                    type=sys.exc_info()[0],
                    code=sys.exc_info()[1])
                logger.error(msg)
                QtGui.QMessageBox.critical(
                    None, "Corpus error – Coquery", 
                    msg, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                return
            
            self.ui.corpus_description.setText(
                str(self.ui.corpus_description.text()).format(
                    builder_class.get_title(), options.cfg.current_server))

        def validate_dialog(self, check_path=True):
            self.ui.input_path.setStyleSheet("")
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
            if self.ui.radio_only_module.isChecked():
                return
            if check_path:
                path = str(self.ui.input_path.text())
                if not path:
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
                    return
                if not os.path.isdir(path):
                    self.ui.input_path.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
                    return            

        def display(self):
            return self.exec_()

        def general_update(self, i):
            self.ui.progress_general.setValue(i)

        def set_label(self, s):
            self.ui.progress_bar.setFormat(s)

        def set_progress(self, vmax, s):
            self.ui.progress_bar.setFormat(s)
            self.ui.progress_bar.setMaximum(vmax)
            self.ui.progress_bar.setValue(0)
            
        def update_progress(self, i):
            self.ui.progress_bar.setValue(i)

        def select_path(self):
            name = QtGui.QFileDialog.getExistingDirectory(directory=options.cfg.corpus_source_path, options=QtGui.QFileDialog.ReadOnly|QtGui.QFileDialog.ShowDirsOnly|QtGui.QFileDialog.HideNameFilterDetails)
            if type(name) == tuple:
                name = name[0]
            if name:
                options.cfg.corpus_source_path = name
                self.ui.input_path.setText(name)

        def keyPressEvent(self, e):
            if e.key() == QtCore.Qt.Key_Escape:
                self.reject()
                
        def changed_radio(self):
            if self.ui.radio_complete.isChecked():
                self.ui.box_build_options.setEnabled(True)
                self.check_input()
            else:
                self.ui.box_build_options.setEnabled(False)
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)

        def show_progress(self):
            self.ui.progress_box.show()
            self.ui.progress_box.update()
                
        def do_install(self):
            self.builder.build()

        def finish_install(self):
            if self.state == "failed":
                S = "Installation of {} failed.".format(self.builder.name)
                self.ui.progress_box.hide()
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
                self.ui.frame.setEnabled(True)
            else:
                S = "Finished installing {}.".format(self.builder.name)
                self.ui.label.setText("Installation complete.")
                self.ui.progress_bar.setMaximum(1)
                self.ui.progress_bar.setValue(1)
                self.ui.buttonBox.removeButton(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes))
                self.ui.buttonBox.removeButton(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Cancel))
                self.ui.buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
            self.parent().showMessage(S)
            
        def install_exception(self):
            self.state = "failed"
            if type(self.exception) == RuntimeError:
                QtGui.QMessageBox.critical(self, "Installation error – Coquery",
                                           str(self.exception))
            else:
                error_box.ErrorBox.show(self.exc_info, self, no_trace=False)

        def reject(self):
            try:
                if self.install_thread:
                    response = QtGui.QMessageBox.warning(self,
                        "Aborting installation", 
                        msg_install_abort,
                        QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                    if response:
                        self.install_thread.quit()
                        super(InstallerGui, self).reject()
            except AttributeError:
                super(InstallerGui, self).reject()
                
        def check_input(self):
            if self.ui.radio_only_module.isChecked():
                self.ui.input_path.setStyleSheet('')
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
            else:
                path = str(self.ui.input_path.text())
                if os.path.isdir(path):
                    self.ui.input_path.setStyleSheet('')
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
                else:
                    self.ui.input_path.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
            
        def start_install(self):
            """
            Launches the installation.
            
            This method starts a new thread that runs the do_install() method.
            
            If this is a full install, i.e. the data base containing the
            corpus is to be created, a call to validate_files() is made first
            to check whether the input path is valid. The thread is only 
            started if the path is valid, or if the user decides to ignore
            the invalid path.
            """
            if self.ui.radio_complete.isChecked():
                try:
                    self.builder_class.validate_files(
                        self.builder_class.get_file_list(
                            str(self.ui.input_path.text()),
                            self.builder_class.file_filter))
                except RuntimeError as e:
                    reply = QtGui.QMessageBox.question(
                        None, "Corpus path not valid – Coquery",
                        msg_corpus_path_not_valid.format(e),
                        QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Discard)
                    if reply == QtGui.QMessageBox.Discard:
                        return

            self.installStarted.emit()
            self.accepted = True
            self.builder = self.builder_class(gui = self)
            self.builder.logger = self.logger
            self.builder.arguments = self.get_arguments_from_gui()
            self.builder.name = self.builder.arguments.name

            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
            self.ui.frame.setEnabled(False)

            #try:
                #self.do_install()
            #except RuntimeError as e:
                #error_box.ErrorBox.show(sys.exc_info(), e, no_trace=True)
            #except Exception as e:
                #error_box.ErrorBox.show(sys.exc_info(), e)
            #else:
                #self.finish_install()

            self.install_thread = QtProgress.ProgressThread(self.do_install, self)
            self.install_thread.setInterrupt(self.builder.interrupt)
            self.install_thread.taskFinished.connect(self.finish_install)
            self.install_thread.taskException.connect(self.install_exception)
            self.install_thread.start()
        
        def get_arguments_from_gui(self):
            namespace = argparse.Namespace()
            namespace.verbose = False
            
            if self.ui.radio_only_module.isChecked():
                namespace.o = False
                namespace.i = False
                namespace.l = False
                namespace.c = False
                namespace.w = True
                namespace.self_join = False
            else:
                namespace.w = True
                namespace.o = True
                namespace.i = True
                namespace.l = True
                namespace.c = True
                namespace.self_join = False

            namespace.encoding = self.builder_class.encoding
            
            namespace.name = self.builder_class.get_name()
            namespace.path = str(self.ui.input_path.text())

            namespace.db_name = self.builder_class.get_name().lower()
            try:
                namespace.db_host, namespace.db_port, namespace.db_user, namespace.db_password = options.get_mysql_configuration()
            except ValueError:
                raise SQLNoConfigurationError
            namespace.current_server = options.cfg.current_server
            namespace.corpus_path = os.path.join(sys.path[0], "corpora/", namespace.current_server)
            
            return namespace

    class BuilderGui(InstallerGui):
        button_label = "&Build"
        window_title = "Corpus builder – Coquery"
        
        def __init__(self, builder_class, parent=None):
            super(BuilderGui, self).__init__(builder_class, parent)
            self.ui.input_path.textChanged.disconnect()

            import __init__
            self.logger = logging.getLogger(__init__.NAME)        

            self.ui.corpus_description.setText("<html><head/><body><p><span style='font-weight:600;'>Corpus builder</span></p><p>You have requested to create a new corpus from a selection of text files on the MySQL server '{}'. The corpus will afterwards be available for queries.</p></body></html>".format(options.cfg.current_server))
            self.ui.label_5.setText("Build corpus from local text files and install corpus module (if you have a local database server)")
            self.ui.label_8.setText("Path to text files:")
            self.setWindowTitle(self.window_title)
            
            self.ui.name_layout = QtGui.QHBoxLayout()
            self.ui.name_label = QtGui.QLabel("&Name of new corpus:")
            self.ui.issue_label = QtGui.QLabel("")
            self.ui.corpus_name = QtGui.QLineEdit()
            self.ui.corpus_name.setMaxLength(32)
            self.ui.corpus_name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]*")))
            self.ui.name_label.setBuddy(self.ui.corpus_name)
            spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

            self.ui.name_layout.addWidget(self.ui.name_label)
            self.ui.name_layout.addWidget(self.ui.corpus_name)
            self.ui.name_layout.addWidget(self.ui.issue_label)
            self.ui.name_layout.addItem(spacerItem)
            self.ui.verticalLayout.insertLayout(1, self.ui.name_layout)

            if nltk_available:
                self.ui.use_pos_tagging = QtGui.QCheckBox("Use NLTK for part-of-speech tagging and lemmatization")
                self.ui.use_pos_tagging.setChecked(True)
            else:
                self.ui.use_pos_tagging = QtGui.QCheckBox("Use NLTK for part-of-speech tagging and lemmatization (NOT AVAILABLE, install the Python NLTK module)")
                self.ui.use_pos_tagging.setChecked(False)
                self.ui.use_pos_tagging.setEnabled(False)
            
            self.ui.gridLayout.addWidget(self.ui.use_pos_tagging, 2, 0)
            if options.cfg.text_source_path != os.path.expanduser("~"):
                self.ui.input_path.setText(options.cfg.text_source_path)
            else:
                self.ui.input_path.setText("")
                
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
            self.ui.input_path.textChanged.connect(lambda: self.validate_dialog(check_path=False))
            self.ui.corpus_name.textChanged.connect(lambda: self.validate_dialog(check_path=False))
            self.ui.corpus_name.setFocus()
        
        def validate_dialog(self, check_path=True):
            if hasattr(self.ui, "corpus_name"):
                self.ui.corpus_name.setStyleSheet("")
            super(BuilderGui, self).validate_dialog()
            if hasattr(self.ui, "corpus_name"):
                self.ui.issue_label.setText("")
                if not str(self.ui.corpus_name.text()):
                    self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                    self.ui.issue_label.setText("The corpus name cannot be empty.")
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
                elif str(self.ui.corpus_name.text()) in options.cfg.current_resources:
                    self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                    self.ui.issue_label.setText("There is already another corpus with this name..")
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
                else:
                    try:
                        db_host, db_port, db_user, db_password = options.get_mysql_configuration()
                    except ValueError:
                        raise SQLNoConfigurationError
                    Con = dbconnection.DBConnection(
                        db_user=db_user, db_host=db_host, db_port=db_port, db_pass=db_password)
                    if Con.has_database("coq_{}".format(str(self.ui.corpus_name.text()).lower())):
                        self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                        self.ui.issue_label.setText("There is already another database that uses this name.")
                        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
        
        def select_path(self):
            name = QtGui.QFileDialog.getExistingDirectory(directory=options.cfg.text_source_path)
            if type(name) == tuple:
                name = name[0]
            if name:
                options.cfg.text_source_path = name
                self.ui.input_path.setText(name)

        def install_exception(self):
            self.state = "failed"
            if type(self.exception) == RuntimeError:
                QtGui.QMessageBox.critical(self, "Corpus building error – Coquery",
                                           str(self.exception))
            else:
                error_box.ErrorBox.show(self.exc_info, self, no_trace=False)

        def get_arguments_from_gui(self):
            namespace = super(BuilderGui, self).get_arguments_from_gui()

            namespace.name = str(self.ui.corpus_name.text())
            namespace.use_nltk = self.ui.use_pos_tagging.checkState()
            namespace.db_name = "coq_".format(str(self.ui.corpus_name.text()).lower())
            
            return namespace

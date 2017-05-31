# -*- coding: utf-8 -*-
"""
session.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import time, datetime
import fileinput
import codecs
import logging
import collections
import sqlalchemy

import pandas as pd

from . import options
from . import NAME
from .errors import *
from .defines import *
from .general import *
from . import sqlhelper
from . import queries
from . import managers
from . import functionlist

class Session(object):
    _is_statistics = False
    query_id = 0

    def __init__(self):
        self.header = None
        self.max_number_of_input_columns = 0
        self.query_list = []
        self.requested_fields = []
        self.groups = []
        options.cfg.query_label = ""

        # load current corpus module depending on the value of options.cfg.corpus,
        # i.e. the corpus specified as an argumment:
        if options.cfg.corpus:

            ResourceClass, CorpusClass, LexiconClass, Path = options.cfg.current_resources[options.cfg.corpus]

            current_lexicon = LexiconClass()
            current_corpus = CorpusClass()
            current_resource = ResourceClass(current_lexicon, current_corpus)

            self.Corpus = current_corpus
            self.Corpus.lexicon = current_lexicon
            self.Corpus.resource = current_resource

            self.Lexicon = current_lexicon
            self.Lexicon.corpus = current_corpus
            self.Lexicon.resource= current_resource

            self.Resource = current_resource

            try:
                self.db_engine = sqlalchemy.create_engine(
                    sqlhelper.sql_url(options.cfg.current_server,
                                      self.Resource.db_name))
            except ImportError as e:
                self.db_engine = None

            logger.info("Corpus '{}' on connection '{}'".format(
                self.Resource.name, options.cfg.current_server))

        else:
            self.Corpus = None
            self.Resource = None
            self.Lexicon = None
            self.db_engine = None
            logger.warn("No corpus available on connection '{}'".format(
                options.cfg.current_server))

        self.query_type = queries.get_query_type(options.cfg.MODE)

        self.data_table = pd.DataFrame()
        self.output_object = pd.DataFrame()
        self.output_order = []
        self.header_shown = False
        self.input_columns = []
        self._manager_cache = {}
        self._first_saved_dataframe = True

        # Column functions are functions that the user specified from the
        # results table
        self.column_functions = functionlist.FunctionList()
        # Summary functions are functions that the user specified to be
        # applied after the summary
        self.summary_group = managers.Summary("summary")

        # row_visibility stores for each query type a pandas Series object
        # with the same index as the respective output object, and boolean
        # values. If the value is False, the row in the output object is
        # hidden, otherwise, it is visible.

        ## FIXME: reimplement row visibility
        #self.row_visibility = {}


    def get_max_token_count(self):
        """
        Return the maximal number of tokens that may be produced by the
        queries from this session.
        """
        maximum = 0
        for query in self.query_list:
            maximum = max(maximum, query.get_max_tokens())
        return maximum

    def start_timer(self):
        self.start_time = datetime.datetime.now()
        self.end_time = None

    def stop_timer(self):
        self.end_time = datetime.datetime.now()

    def save_dataframe(self, df, append=False):
        if not options.cfg.output_path:
            output_file = sys.stdout
        else:
            if append and not self._first_saved_dataframe:
                file_mode = "a"
            else:
                file_mode = "w"

            output_file = codecs.open(
                options.cfg.output_path,
                file_mode,
                encoding=options.cfg.output_encoding)

        columns = [x for x in df.columns.values if not x.startswith("coquery_invisible")]
        if self._first_saved_dataframe:
            header = [self.translate_header(x) for x in columns]
        else:
            header = False

        # FIXME:
        # saving doesn't work anymore!
        df[columns].to_csv(
            output_file,
            header=header,
            sep=options.cfg.output_separator,
            encoding="utf-8",
            float_format = "%.{}f".format(options.cfg.digits),
            index=False)
        output_file.flush()
        self._first_saved_dataframe = False

    def connect_to_db(self):
        def _sqlite_regexp(expr, item):
            """
            Function which adds regular expressions to SQLite
            """
            if options.cfg.query_case_sensitive:
                match = re.search(expr, item)
            else:
                match = re.search(expr, item, re.IGNORECASE)
            return match is not None

        self.db_connection = self.db_engine.connect()
        if self.Resource.db_type == SQL_SQLITE:
            self.db_connection.connection.create_function("REGEXP", 2,
                                                          _sqlite_regexp)

    def disconnect_from_db(self):
        self.db_connection.close()

    def prepare_queries(self):
        self.query_list = []
        for query_string in options.cfg.query_list:
            if self.query_type:
                new_query = self.query_type(query_string, self)
            else:
                raise CorpusUnavailableQueryTypeError(options.cfg.corpus, options.cfg.MODE)
            self.query_list.append(new_query)

    def run_queries(self, to_file=False, **kwargs):
        """
        Run each query in the query list, and append the results to the
        output object. Afterwards, apply all filters, and aggregate the data.
        If Coquery is run as a console program, write the aggregated data to
        a file (or the standard output).

        Parameters
        ----------
        to_file : bool
            True if the query results are directly written to a file, and
            False if they will be displayed in the GUI. Data that is written
            directly to a file contains less information, e.g. it doesn't
            contain an origin ID or a corpus ID (unless requested).
        """
        self.start_timer()

        if self.db_engine == None:
            raise SQLNoConnectorError

        self.connect_to_db()

        self.data_table = pd.DataFrame()
        self.quantified_number_labels = []
        Session.query_id += 1

        number_of_queries = len(self.query_list)
        manager = self.get_manager()
        manager.set_filters(options.cfg.filter_list)
        manager.set_groups(self.groups)

        dtype_list = []
        self.queries = {}
        _queried = []

        try:
            for i, current_query in enumerate(self.query_list):
                if current_query.query_string in _queried:
                    logger.warn("Duplicate query string detected: {}".format(
                        current_query.query_string))
                    continue
                _queried.append(current_query.query_string)
                self.queries[i] = current_query

                if options.cfg.gui and number_of_queries > 1:
                    options.cfg.main_window.updateMultiProgress.emit(i+1)
                if not self.quantified_number_labels:
                    self.quantified_number_labels = [
                        current_query.get_token_numbering(i)
                        for i in range(self.get_max_token_count())]
                start_time = time.time()
                if number_of_queries > 1:
                    logger.info("Start query ({} of {}): '{}'".format(
                        i+1, number_of_queries, current_query.query_string))
                else:
                    logger.info("Start query: '{}'".format(
                        current_query.query_string))
                df = current_query.run(connection=self.db_connection,
                                       to_file=to_file, **kwargs)

                # apply clumsy hack that tries to make sure that the dtypes of
                # data frames containing NaNs or empty strings does not change
                # when appending the new data frame to the previous.

                # The same hack is also needed in queries.run().
                if (len(self.data_table) > 0 and
                        df.dtypes.tolist() != dtype_list.tolist()):
                    for x in df.columns:
                        # the idea is that pandas/numpy use the 'object'
                        # dtype as a fall-back option for strange results,
                        # including those with NaNs.
                        # One problem is that integer columns become floats
                        # in the process. This is so because Pandas does not
                        # have an integer NA type:
                        # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na

                        try:
                            dtype_changed = df.dtypes[x] != dtype_list[x]
                        except (IndexError, KeyError):
                            continue

                        if df.dtypes[x] != dtype_list[x]:
                            if df.dtypes[x] == object:
                                if not df[x].any():
                                    df[x] = [pd.np.nan] * len(df)
                                    dtype_list[x] = self.data_table[x].dtype
                            elif dtype_list[x] == object:
                                if not self.data_table[x].any():
                                    self.data_table[x] = [pd.np.nan] * len(self.data_table)
                                    dtype_list[x] = df[x].dtype
                else:
                    dtype_list = df.dtypes

                df = current_query.insert_static_data(df)
                #df["coquery_invisible_query_number"] = i

                if not to_file:
                    self.data_table = self.data_table.append(df)
                else:
                    df = manager.process(df, session=self)
                    self.save_dataframe(df, append=True)

                logger.info("Query executed ({:.3f} seconds, {} match{})".format(
                    time.time() - start_time, len(df), "es" if len(df) != 1 else ""))

        finally:
            self.disconnect_from_db()

        self.data_table = self.data_table[set_preferred_order(
            list(self.data_table.columns),
            self)]

        for col in self.data_table.columns:
            if self.data_table.dtypes[col] == object:
                if sys.version_info < (3, 0):
                    try:
                        self.data_table[col] = self.data_table[col].apply(lambda x: x.encode("utf-8"))
                    except Exception as e:
                        print(e)
                        logger.warn(e)

        ## FIXME: reimplement row visibility
        #self.reset_row_visibility(queries.TokenQuery, self.data_table)

        if not options.cfg.gui:
            self.aggregate_data()
            if not options.cfg.output_path:
                output_file = sys.stdout
            else:
                if options.cfg.append:
                    file_mode = "a"
                else:
                    file_mode = "w"

                output_file = codecs.open(
                    options.cfg.output_path,
                    file_mode,
                    encoding=options.cfg.output_encoding)

            columns = [x for x in self.output_object.columns.values if not x.startswith("coquery_invisible")]

            self.output_object[columns].to_csv(
                output_file,
                header = [self.translate_header(x) for x in columns],
                sep=options.cfg.output_separator,
                encoding="utf-8",
                float_format = "%.{}f".format(options.cfg.digits),
                index=False)
            output_file.flush()

    def get_manager(self):
        if not self.Resource:
            return None
        else:
            return managers.get_manager(options.cfg.MODE, self.Resource.name)

    def has_cached_data(self):
        return (self, self.get_manager()) in self._manager_cache

    @classmethod
    def is_statistics_session(cls):
        return cls._is_statistics

    def aggregate_data(self, recalculate=True):
        """
        Use the current manager to process the data table. If requested, use
        a cached table (e.g. for sorting when no recalculation is needed).
        """

        manager = self.get_manager()
        manager.set_filters(options.cfg.filter_list)
        manager.set_groups(self.groups)

        column_properties = {}
        try:
            column_properties = options.settings.value("column_properties",
                                                       {})
        finally:
            options.settings.setValue("column_properties",
                                      column_properties)
        prop = column_properties.get(options.cfg.corpus, {})
        manager.set_column_substitutions(prop.get("substitutions", {}))

        self.output_object = manager.process(self.data_table, self, recalculate)

        #self._manager_cache[(self, manager)] = self.output_object

    def drop_cached_aggregates(self):
        self._manager_cache = {}

    ## FIXME: reimplement row visibility
    #def reset_row_visibility(self, query_type, df=pd.DataFrame()):
        #if df.empty:
            #df = self.output_object
        #self.row_visibility[query_type] = pd.Series(
            #data=[True] * len(df.index), index=df.index)

    def retranslate_header(self, label):
        """
        Return the column name in the current content data frame that matches
        the giben display name.
        """
        for x in self.data_table.columns:
            if self.translate_header(x) == label:
                return x
        return None

    def translate_header(self, header, ignore_alias=False):
        """
        Return a string that contains the display name for the header
        string.

        Translation removes the 'coq_' prefix and any numerical suffix,
        determines the resource feature from the remaining string, translates
        it to its display name, and returns the display name together with
        the numerical suffix attached.

        Parameters
        ----------
        header : string
            The resource string that is to be translated
        ignore_alias : bool
            True if user names should be ignored, and False if user names
            should be used.

        Returns
        -------
        s : string
            The display name of the resource string
        """

        if header == None:
            return header

        # If the column has been renamed by the user, that name has top
        # priority, unless ignore_alias is used:
        # if options.cfg.verbose: print("translate_header({})".format(header))
        if not ignore_alias and header in options.cfg.column_names:
            # if options.cfg.verbose: print(1)
            return options.cfg.column_names[header]

        # Retain the column header if the query string was from an input file
        if header == "coquery_query_string" and options.cfg.query_label:
            # if options.cfg.verbose: print(2)
            return options.cfg.query_label

        if header.startswith("coquery_invisible"):
            # if options.cfg.verbose: print(3)
            return header

        # treat frequency columns:
        if header == "statistics_frequency":
            if options.cfg.query_label:
                # if options.cfg.verbose: print(4)
                return "{}({})".format(COLUMN_NAMES[header], options.cfg.query_label)
            else:
                # if options.cfg.verbose: print(5)
                return "{}".format(COLUMN_NAMES[header])

        if header.startswith("statistics_g_test"):
            label = header.partition("statistics_g_test_")[-1]
            # if options.cfg.verbose: print(6)
            return "G('{}', y)".format(label)

        if header.startswith("coq_userdata"):
            return "Userdata{}".format(header.rpartition("_")[-1])

        if header.startswith("coq_context"):
            if header == "coq_context_left":
                s = "{}({})".format(COLUMN_NAMES[header], options.cfg.context_left)
            elif header == "coq_context_right":
                s = "{}({})".format(COLUMN_NAMES[header], options.cfg.context_right)
            elif header == "coq_context_string":
                s = "{}({}L, {}R)".format(COLUMN_NAMES[header],
                                            options.cfg.context_left,
                                            options.cfg.context_right)
            elif header.startswith("coq_context_lc"):
                s = "L{}".format(header.split("coq_context_lc")[-1])
            elif header.startswith("coq_context_rc"):
                s = "R{}".format(header.split("coq_context_rc")[-1])
            # if options.cfg.verbose: print(7)
            return s

        # other features:
        if header in COLUMN_NAMES:
            # if options.cfg.verbose: print(8)
            return COLUMN_NAMES[header]

        # deal with function headers:
        if header.startswith("func_"):
            manager = self.get_manager()
            # check if there is a parenthesis in the header (there shouldn't
            # ever be one, acutally)
            match = re.search("(.*)\((.*)\)", header)
            if match:
                s = match.group(1)
                # if options.cfg.verbose: print(s, header)
                fun = manager.get_function(s)
                try:
                    # if options.cfg.verbose: print(9)
                    return "{}({})".format(fun.get_label(session=self, manager=manager),
                                           match.group(2))
                except AttributeError:
                    # if options.cfg.verbose: print(10)
                    return header
            else:
                match = re.search("(func_\w+_\w+)_(\d+)_(\d*)", header)
                if match:
                    header = match.group(1)
                    num = match.group(2)
                else:
                    num = ""

                fun = manager.get_function(header)
                if fun == None:
                    # if options.cfg.verbose: print(11)
                    return header
                else:
                    # if options.cfg.verbose: print(12)
                    label = fun.get_label(session=self, manager=manager,
                                          unlabel=ignore_alias)
                    if not num:
                        return label
                    else:
                        return "{} (match {})".format(label, num)

        if header.startswith("db_"):
            match = re.match("db_(.*)_coq_(.*)", header)
            resource = options.get_resource_of_database(match.group(1))
            res_prefix = "{}.".format(resource.name)
            header = match.group(2)
        else:
            match = re.match("coq_(.*)", header)
            if match:
                header = match.group(1)
            res_prefix = ""
            resource = self.Resource

        rc_feature, _, number = header.rpartition("_")

        # If there is only one query token, number is set to "" so that no
        # number suffix is added to the labels in this case:
        if self.get_max_token_count() == 1:
            number = ""

        # special treatment of query tokens:
        if rc_feature == "coquery_query_token":
            try:
                number = self.quantified_number_labels[int(number) - 1]
            except (ValueError, AttributeError):
                pass
            # if options.cfg.verbose: print(14)
            return "{}{}{}".format(res_prefix, COLUMN_NAMES[rc_feature], number)

        # special treatment of lexicon features:
        if (rc_feature in [x for x, _ in resource.get_lexicon_features()]
            or resource.is_tokenized(rc_feature)):
            try:
                number = self.quantified_number_labels[int(number) - 1]
            except (ValueError, AttributeError):
                pass
            # if options.cfg.verbose: print(15)
            return "{}{}{}".format(res_prefix,
                                   getattr(resource, str(rc_feature)).replace("__", " "),
                                   number)

        # treat any other feature that is provided by the corpus:
        try:
            # if options.cfg.verbose: print(16)
            return "{}{}".format(res_prefix,
                                 getattr(resource, str(rc_feature)).replace("__", " "))
        except AttributeError:
            pass

        # other features:
        if rc_feature in COLUMN_NAMES:
            try:
                number = self.quantified_number_labels[int(number) - 1]
            except (ValueError, AttributeError):
                pass
            # if options.cfg.verbose: print(17)
            return "{}{}{}".format(res_prefix, COLUMN_NAMES[rc_feature], number)

        # if options.cfg.verbose: print(18)
        return header

class StatisticsSession(Session):
    _is_statistics = True
    def __init__(self):
        super(StatisticsSession, self).__init__()
        self.query_list.append(queries.StatisticsQuery(self.Corpus, self))
        self.header = ["Variable", "Value"]
        self.output_order = self.header

    def aggregate_data(self, recalculate=True):
        self.output_object = self.data_table

class SessionCommandLine(Session):
    def __init__(self):
        super(SessionCommandLine, self).__init__()
        if len(options.cfg.query_list) > 1:
            logger.info("{} queries".format(len(options.cfg.query_list)))
        self.max_number_of_input_columns = 0

class SessionInputFile(Session):
    def prepare_queries(self):
        with open(options.cfg.input_path, "rt") as InputFile:
            read_lines = 0
            try:
                input_file = pd.read_table(
                    filepath_or_buffer=InputFile,
                    header=0 if options.cfg.file_has_headers else None,
                    sep=options.cfg.input_separator,
                    quotechar=options.cfg.quote_char,
                    encoding=options.cfg.input_encoding,
                    na_filter=False)
            except ValueError:
                raise EmptyInputFileError(InputFile)

            if self.header is None:
                if options.cfg.file_has_headers:
                    self.header = input_file.columns.values.tolist()
                else:
                    self.header = ["X{}".format(i+1) for i, _
                                   in enumerate(input_file.columns)]
                    input_file.columns = self.header

            options.cfg.query_label = self.header.pop(
                options.cfg.query_column_number - 1)
            for current_line in input_file.iterrows():
                current_line = list(current_line[1])
                if options.cfg.query_column_number > len(current_line):
                    raise IllegalArgumentError("Column number for queries too big (-n %s)" % options.cfg.query_column_number)

                if read_lines >= options.cfg.skip_lines:
                    try:
                        query_string = current_line.pop(
                            options.cfg.query_column_number - 1)
                    except AttributeError:
                        continue
                    new_query = self.query_type(query_string, self)
                    if len(current_line) != len(self.header):
                        raise TokenParseError
                    new_query.input_frame = pd.DataFrame(
                        [current_line], columns=self.header)
                    self.query_list.append(new_query)
                self.max_number_of_input_columns = max(
                    len(current_line),
                    self.max_number_of_input_columns)
                read_lines += 1
            self.input_columns = ["coq_{}".format(x) for x in self.header]

        logger.info("Input file: {} ({} {})".format(options.cfg.input_path, len(self.query_list), "query" if len(self.query_list) == 1 else "queries"))
        if options.cfg.skip_lines:
            logger.info("Skipped first {}.".format("query" if options.cfg.skip_lines == 1 else "{} queries".format(options.cfg.skip_lines)))

class SessionStdIn(Session):
    def __init__(self):
        super(SessionStdIn, self).__init__()

        for current_string in fileinput.input("-"):
            read_lines = 0
            current_line = [x.strip() for x in current_string.split(options.cfg.input_separator)]
            if current_line:
                if options.cfg.file_has_headers and not self.header:
                    self.header = current_line
                else:
                    if read_lines >= options.cfg.skip_lines:
                        query_string = current_line.pop(options.cfg.query_column_number - 1)
                        new_query = self.query_type(query_string, self)
                        self.query_list.append(new_query)
                self.max_number_of_input_columns = max(len(current_line), self.max_number_of_input_columns)
            read_lines += 1
        logger.info("Reading standard input ({} {})".format(len(self.query_list), "query" if len(self.query_list) == 1 else "queries"))
        if options.cfg.skip_lines:
            logger.info("Skipping first %s %s." % (options.cfg.skip_lines, "query" if options.cfg.skip_lines == 1 else "queries"))

logger = logging.getLogger(NAME)

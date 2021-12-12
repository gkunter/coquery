# -*- coding: utf-8 -*-
"""
session.py is part of Coquery.

Copyright (c) 2016-2021 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import time
import datetime
import fileinput
import codecs
import warnings
import logging
import re

import pandas as pd
import numpy as np

from . import options
from .errors import (
    TokenParseError, IllegalArgumentError, SQLNoConnectorError,
    EmptyInputFileError, CorpusUnavailableQueryTypeError)
from .defines import SQL_SQLITE, COLUMN_NAMES
from .general import Print
from coquery.queries import StatisticsQuery, TokenQuery
from . import managers
from . import functionlist


class Session(object):
    _is_statistics = False
    query_id = 0

    def __init__(self, summary_groups=None):
        self.header = None
        self.max_number_of_input_columns = 0
        self.query_list = []
        self.requested_fields = []
        self.sql_queries = []
        self.groups = []
        self.to_file = False
        options.cfg.query_label = ""

        available_resources = options.cfg.current_connection.resources()
        current_connection = options.cfg.current_connection
        # load current corpus module depending on the value of
        # options.cfg.corpus, i.e. the corpus specified as an argumment:
        if len(available_resources) and options.cfg.corpus:
            try:
                tup = available_resources[options.cfg.corpus]
            except KeyError:
                tup = available_resources[list(available_resources.keys())[0]]
            ResourceClass, CorpusClass, Path = tup

            current_corpus = CorpusClass()
            current_resource = ResourceClass(None, current_corpus)

            self.Corpus = current_corpus
            self.Corpus.resource = current_resource

            self.Resource = current_resource

            self.db_engine = current_connection.get_engine(
                self.Resource.db_name)

            logging.info("Corpus '{}' on connection '{}'".format(
                self.Resource.name, current_connection.name))

        else:
            self.Corpus = None
            self.Resource = None
            self.db_engine = None
            warnings.warn("No corpus available on connection '{}'".format(
                current_connection.name))

        self.query_type = TokenQuery

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

        if summary_groups:
            self.summary_group = summary_groups[0]
        else:
            self.summary_group = managers.Summary("summary", [], [])

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
                if options.cfg.verbose:
                    info = "Writing query results to file {}".format(
                        options.cfg.output_path)
                    logging.info(info)

            output_file = codecs.open(
                options.cfg.output_path,
                file_mode,
                encoding=options.cfg.output_encoding)

        columns = [x for x in df.columns.values
                   if not x.startswith("coquery_invisible")]
        if self._first_saved_dataframe:
            header = [self.translate_header(x) for x in columns]
        else:
            header = False

        df[columns].to_csv(
            output_file,
            header=header,
            sep=options.cfg.output_separator,
            encoding="utf-8",
            float_format="%.{}f".format(options.cfg.digits),
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

        dbc = self.db_engine.connect()
        if options.cfg.current_connection.db_type() == SQL_SQLITE:
            dbc.connection.create_function("REGEXP", 2, _sqlite_regexp)
        return dbc

    def prepare_queries(self):
        self.query_list = []
        for query_string in options.cfg.query_list:
            if self.query_type:
                new_query = self.query_type(query_string, self)
            else:
                raise CorpusUnavailableQueryTypeError(options.cfg.corpus,
                                                      options.cfg.MODE)
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

        if self.db_engine is None:
            raise SQLNoConnectorError

        self.data_table = pd.DataFrame()
        self.quantified_number_labels = []
        Session.query_id += 1

        number_of_queries = len(self.query_list)
        manager = self.get_manager(options.cfg.MODE)
        manager.set_filters(options.cfg.filter_list)
        manager.set_groups(self.groups)
        manager.set_column_order(options.cfg.column_order)

        self.queries = {}
        _queried = []

        self.sql_queries = []

        db_connection = self.connect_to_db()

        try:
            for i, current_query in enumerate(self.query_list):
                if current_query.query_string in _queried and not to_file:
                    warnings.warn(
                        "Duplicate query string detected: {}".format(
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
                    info = (f"Start query ({i+1} of {number_of_queries}): "
                            f"'{current_query.query_string}'")
                else:
                    info = f"Start query: '{current_query.query_string}'"
                logging.info(info)
                df = current_query.run(
                    connection=db_connection, to_file=to_file, **kwargs)
                self.sql_queries.append(current_query.sql_list)
                raw_length = len(df)

                df = current_query.insert_static_data(df)
                self.to_file = to_file

                if not to_file:
                    self.data_table = self.data_table.append(df)
                else:
                    df = manager.process(df, session=self)
                    self.save_dataframe(df, append=True)

                s_list = ["{:.3f} seconds".format(time.time() - start_time),
                          "{} match{}".format(
                              raw_length,
                              "es" if raw_length != 1 else "")]
                if len(df) != raw_length:
                    s_list.append(
                        "{} output_row{}".format(
                            len(df),
                            "s" if len(df) != 1 else ""))
                logging.info(
                    "Query executed ({})".format(", ".join(s_list)))
        finally:
            db_connection.close()

        self.finalize_table()

    def finalize_table(self):
        """
        Apply final fixes to the data table retrieved by the current queries.

        The following fixes are applied:

        - Set preferred column order
        - Guess best dtypes, taking missing values into account
        - Resetting the internal index
        """

        # Set column order
        ordered_columns = self.set_preferred_order(
            list(self.data_table.columns))
        self.data_table = self.data_table[ordered_columns]

        # Handle dtypes and deal with missing values
        for col in self.data_table.columns:
            S = self.data_table[col]
            S = S.replace({None: pd.NA, np.NaN: pd.NA})
            dtype = S.dropna().convert_dtypes().dtype
            if pd.api.types.is_integer_dtype(dtype):
                S = pd.Series(S, dtype=pd.Int64Dtype())
            elif pd.api.types.is_numeric_dtype(dtype):
                S = pd.to_numeric(S, errors="coerce", downcast="integer")
            self.data_table[col] = S

        # Reset row index
        self.data_table = self.data_table.reset_index(drop=True)

    def get_manager(self, query_mode):
        if not self.Resource:
            return None
        else:
            return managers.get_manager(query_mode, self.Resource.name)

    def set_preferred_order(self, lst):
        """
        Arrange the column names in l so that they occur in the preferred
        order.

        Columns not in the preferred order follow in an unspecified order.
        """
        resource_order = self.Resource.get_preferred_output_order()
        for x in resource_order[::-1]:
            lex_list = [y for y in lst if x in y]
            lex_list = sorted(lex_list)[::-1]
            for lex in lex_list:
                lst.remove(lex)
                lst.insert(0, lex)
        return lst

    def has_cached_data(self, query_mode):
        return (self, self.get_manager(query_mode)) in self._manager_cache

    @classmethod
    def is_statistics_session(cls):
        return cls._is_statistics

    def aggregate_data(self, recalculate=True):
        """
        Use the current manager to process the data table. If requested, use
        a cached table (e.g. for sorting when no recalculation is needed).
        """

        manager = self.get_manager(options.cfg.MODE)
        manager.set_filters(options.cfg.filter_list)
        manager.set_groups(self.groups)
        manager.set_column_order(options.cfg.column_order)

        column_properties = {}
        if options.cfg.gui:
            try:
                column_properties = options.settings.value(
                    "column_properties", {})
            finally:
                options.settings.setValue(
                    "column_properties", column_properties)
        prop = column_properties.get(options.cfg.corpus, {})
        manager.set_column_substitutions(prop.get("substitutions", {}))

        self.output_object = manager.process(self.data_table,
                                             self,
                                             recalculate)

    def drop_cached_aggregates(self):
        self._manager_cache = {}

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
        Return a string that contains the display name for the header string.

        Translation removes the 'coq_' prefix and any numerical suffix,
        determines the resource feature from the remaining string, translates
        it to its display name, and returns the display name together with the
        numerical suffix attached.

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

        # FIXME: This method is an abomination and needs revision. Badly.

        if header is None:
            return header

        # If the column has been renamed by the user, that name has top
        # priority, unless ignore_alias is used:
        Print("translate_header({})".format(header))
        if not ignore_alias and header in options.cfg.column_names:
            Print(1)
            return options.cfg.column_names[header]

        # Retain the column header if the query string was from an input file
        if header == "coquery_query_string" and options.cfg.query_label:
            Print(2)
            return options.cfg.query_label

        if header.startswith("coquery_invisible"):
            Print(3)
            return header

        # treat frequency columns:
        if header == "statistics_frequency":
            if options.cfg.query_label:
                Print(4)
                return "{}({})".format(COLUMN_NAMES[header],
                                       options.cfg.query_label)
            else:
                Print(5)
                return "{}".format(COLUMN_NAMES[header])

        if header.startswith("statistics_g_test"):
            label = header.partition("statistics_g_test_")[-1]
            Print(6)
            return "G('{}', y)".format(label)

        if header.startswith("coq_userdata"):
            return "Userdata{}".format(header.rpartition("_")[-1])

        if header.startswith("coq_context"):
            if header == "coq_context_left":
                s = "{}({})".format(
                    COLUMN_NAMES[header], options.cfg.context_left)
            elif header == "coq_context_right":
                s = "{}({})".format(
                    COLUMN_NAMES[header], options.cfg.context_right)
            elif header == "coq_context_string":
                s = "{}({}L, {}R)".format(COLUMN_NAMES[header],
                                          options.cfg.context_left,
                                          options.cfg.context_right)
            elif header.startswith("coq_context_lc"):
                s = "L{}".format(header.split("coq_context_lc")[-1])
            elif header.startswith("coq_context_rc"):
                s = "R{}".format(header.split("coq_context_rc")[-1])
            else:
                s = header
            Print(7)
            return s

        # other features:
        if header in COLUMN_NAMES:
            Print(8)
            return COLUMN_NAMES[header]

        # deal with function headers:
        if header.startswith("func_"):
            manager = self.get_manager(options.cfg.MODE)
            # check if there is a parenthesis in the header (there shouldn't
            # ever be one, actually)
            match = re.search(r"(.*)\((.*)\)", header)
            if match:
                s = match.group(1)
                Print(s, header)
                fun = manager.get_function(s)
                try:
                    # Print(9)
                    return "{}({})".format(fun.get_label(session=self),
                                           match.group(2))
                except AttributeError:
                    Print(10)
                    return header
            else:
                match = re.search(r"(func_\w+_\w+)_(\d+)_(\d*)", header)
                if match:
                    header = match.group(1)
                    num = match.group(2)
                else:
                    num = ""

                fun = manager.get_function(header)
                if fun is None:
                    # Print(11)
                    return header
                else:
                    # Print(12)
                    label = fun.get_label(session=self, unlabel=ignore_alias)
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
            Print(14)
            return "{}{}{}".format(res_prefix,
                                   COLUMN_NAMES[rc_feature],
                                   number)

        try:
            # special treatment of lexicon features:
            lexicon_features = [
                x for x, _ in resource.get_lexicon_features()]
            if (rc_feature in lexicon_features or
                    resource.is_tokenized(rc_feature)):
                try:
                    number = self.quantified_number_labels[int(number) - 1]
                except ValueError:
                    pass

                name = getattr(resource, str(rc_feature))
                # Print(15)
                return "{}{}{}".format(res_prefix,
                                       name.replace("__", " "),
                                       number)
        except AttributeError:
            pass

        # treat any other feature that is provided by the corpus:
        try:
            Print(16)
            name = getattr(resource, str(rc_feature))
            return "{}{}".format(res_prefix,
                                 name.replace("__", " "))
        except AttributeError:
            pass

        # other features:
        if rc_feature in COLUMN_NAMES:
            try:
                number = self.quantified_number_labels[int(number) - 1]
            except (ValueError, AttributeError):
                pass
            Print(17)
            return "{}{}{}".format(res_prefix,
                                   COLUMN_NAMES[rc_feature],
                                   number)

        Print(18)
        return header

    def translated_headers(self, df):
        """
        Create a list that contains the translated column headers
        of the data frame.
        """
        return [self.translate_header(x) for x in df.columns]

    def limiter(self, df, column, subset=None):
        """
        Return a tuple that represents a suitable data range for the given
        column.

        Typically, this function is called by a visualization module that
        wants to determine the maximum token id range. The parameter subset
        is used to create a subcorpus.
        """
        #FIXME: implement corpus subests
        return (0, self.Corpus.get_corpus_size())

class StatisticsSession(Session):
    _is_statistics = True

    def __init__(self):
        super(StatisticsSession, self).__init__([])
        self.query_list.append(StatisticsQuery(self.Corpus, self))
        self.header = ["Variable", "Value"]
        self.output_order = self.header
        self.query_type = StatisticsQuery

    def aggregate_data(self, recalculate=True):
        self.output_object = self.data_table


class SessionCommandLine(Session):
    def __init__(self, summary_groups=None):
        super(SessionCommandLine, self).__init__(summary_groups)
        if len(options.cfg.query_list) > 1:
            logging.info(
                "{} queries".format(len(options.cfg.query_list)))
        self.max_number_of_input_columns = 0


class SessionInputFile(Session):
    def prepare_queries(self):
        with open(options.cfg.input_path, "rt") as InputFile:
            read_lines = 0
            try:
                input_file = pd.read_csv(
                    filepath_or_buffer=InputFile,
                    sep=options.cfg.input_separator,
                    header=0 if options.cfg.file_has_headers else None,
                    quotechar=options.cfg.quote_char,
                    encoding=options.cfg.input_encoding,
                    nrows=options.cfg.csv_restrict,
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
                    raise IllegalArgumentError(
                        "Column number for queries too big (-n {})".format(
                            options.cfg.query_column_number))

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

        logging.info(
            "Input file: {} ({} {})".format(
                options.cfg.input_path,
                len(self.query_list),
                "query" if len(self.query_list) == 1 else "queries"))
        if options.cfg.skip_lines:
            logging.info(
                "Skipped first {}.".format(
                    ("query" if options.cfg.skip_lines == 1
                     else "{} queries".format(options.cfg.skip_lines))))


class SessionStdIn(Session):
    def __init__(self, summary_groups=None):
        super(SessionStdIn, self).__init__(summary_groups)

        for current_string in fileinput.input("-"):
            read_lines = 0
            current_line = [x.strip() for x
                            in current_string.split(
                                options.cfg.input_separator)]
            if current_line:
                if options.cfg.file_has_headers and not self.header:
                    self.header = current_line
                else:
                    if read_lines >= options.cfg.skip_lines:
                        query_string = current_line.pop(
                            options.cfg.query_column_number - 1)
                        new_query = self.query_type(query_string, self)
                        self.query_list.append(new_query)
                self.max_number_of_input_columns = max(
                    len(current_line), self.max_number_of_input_columns)
            read_lines += 1
        logging.info("Reading standard input ({} {})".format(
            len(self.query_list),
            "query" if len(self.query_list) == 1 else "queries"))
        if options.cfg.skip_lines:
            logging.info("Skipping first {} {}.".format(
                options.cfg.skip_lines,
                "query" if options.cfg.skip_lines == 1 else "queries"))

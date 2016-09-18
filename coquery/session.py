# -*- coding: utf-8 -*-
"""
session.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import time, datetime
import fileinput
import codecs
import logging
import collections

import pandas as pd

from . import options
from .errors import *
from .corpus import *
from .defines import *
from .general import *
from . import queries
from . import filters
from . import managers
from . import tokens

class Session(object):
    def __init__(self):
        self.header = None
        self.max_number_of_input_columns = 0
        self.query_list = []
        self.requested_fields = []
        options.cfg.query_label = ""
            
        # load current corpus module depending on the value of options.cfg.corpus,
        # i.e. the corpus specified as an argumment:        
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

        self.show_header = options.cfg.show_header

        self.query_type = queries.get_query_type(options.cfg.MODE)

        logger.info("Corpus '{}' on connection '{}'".format(
            self.Resource.name, options.cfg.current_server))

        self.db_engine = sqlalchemy.create_engine(
            sqlhelper.sql_url(options.cfg.current_server, self.Resource.db_name))
        self.db_connection = self.db_engine.connect()

        self.data_table = pd.DataFrame()
        self.output_object = pd.DataFrame()
        self.output_order = []
        self.header_shown = False
        self.input_columns = []
        self._manager_cache = {}
        self._first_saved_dataframe = True
        
        # row_visibility stores for each query type a pandas Series object
        # with the same index as the respective output object, and boolean
        # values. If the value is False, the row in the output object is
        # hidden, otherwise, it is visible.
        
        ## FIXME: reimplement row visibility
        #self.row_visibility = {}

        # verify filter list:
        new_list = []
        if options.cfg.use_corpus_filters:
            for filt in options.cfg.filter_list:
                if isinstance(filt, filters.QueryFilter):
                    new_list.append(filt)
                else:
                    new_filt = filters.QueryFilter()
                    new_filt.resource = self.Resource
                    new_filt.text = filt
                    new_list.append(new_filt)
        self.filter_list = new_list
        self.Resource.filter_list = new_list
        
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

    def run_queries(self, to_file=False):
        """ 
        Run each query in the query list, and append the results to the 
        output object. Afterwards, apply all filters, and aggregate the data.
        If Coquery is run as a console program, write the aggregated data to 
        a file (or the standard output).
        """
        self.start_timer()
        
        self.data_table = pd.DataFrame()
        self.quantified_number_labels = []

        number_of_queries = len(self.query_list)
        manager = managers.get_manager(options.cfg.MODE, self.Resource.name)

        dtype_list = []

        for i, current_query in enumerate(self.query_list):
            if options.cfg.gui and number_of_queries > 1:
                options.cfg.main_window.updateMultiProgress.emit(i+1)
            if not self.quantified_number_labels:
                self.quantified_number_labels = [current_query.get_token_numbering(i) for i in range(self.get_max_token_count())]
            start_time = time.time()
            if number_of_queries > 1:
                logger.info("Start query ({} of {}): '{}'".format(i+1, number_of_queries, current_query.query_string))
            else:
                logger.info("Start query: '{}'".format(current_query.query_string))
            
            df = current_query.run()

            # FIXME:
            # If the current query did not return any match, nothing is added 
            # at all to the results table. This means that zero-frequency
            # queries are not recorded, which may lead to surprises.
            # Is there any sensible way of fixing that? For instance, queries 
            # which include the query string could at least contain that 
            # column, with NAs in all other columns.
            if len(df) > 0:
                if not to_file:
                    # apply clumsy hack that tries to make sure that the dtypes of 
                    # data frames containing NaNs or empty strings does not change
                    # when appending the new data frame to the previous.
                    
                    # The same hack is also needed in queries.run().
                    if len(self.data_table) > 0 and df.dtypes.tolist() != dtype_list.tolist():
                        for x in df.columns:
                            # the idea is that pandas/numpy use the 'object' 
                            # dtype as a fall-back option for strange results,
                            # including those with NaNs. 
                            # One problem is that integer columns become floats
                            # in the process. This is so because Pandas does not 
                            # have an integer NA type:
                            # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na

                            if df.dtypes[x] != dtype_list[x]:
                                _working = None
                                if df.dtypes[x] == object:
                                    if not df[x].any():
                                        df[x] = [np.nan] * len(df)
                                        dtype_list[x] = self.data_table[x].dtype
                                elif dtype_list[x] == object:
                                    if not self.data_table[x].any():
                                        self.data_table[x] = [np.nan] * len(self.data_table)
                                        dtype_list[x] = df[x].dtype
                    else:
                        dtype_list = df.dtypes

                    self.data_table = self.data_table.append(df)
                else:
                    self.save_dataframe(manager.process(df, self, True), append=True)
                
            logger.info("Query executed ({:.3f} seconds, {} match{})".format(
                time.time() - start_time, len(df), "es" if len(df) != 1 else ""))

        for col in self.data_table.columns:
            if self.data_table.dtypes[col] == object:
                if sys.version_info < (3, 0):
                    self.data_table[col] = self.data_table[col].apply(lambda x: x.encode("utf-8"))

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

    def get_frequency_table(self):
        frequency_table = queries.FrequencyQuery.aggregate_it(self.data_table, self.Corpus, session=self)
        frequency_table.fillna("", inplace=True)
        frequency_table.index = range(1, len(frequency_table.index) + 1)

        return frequency_table

    def has_cached_data(self):
        manager = managers.get_manager(options.cfg.MODE, self.Resource.name)
        return (self, manager) in self._manager_cache

    def aggregate_data(self, recalculate=True):
        """
        Use the current manager to process the data table. If requested, use 
        a cached table (e.g. for sorting when no recalculation is needed).
        """
        
        manager = managers.get_manager(options.cfg.MODE, self.Resource.name)
        
        if not recalculate:
            df = self.output_object
        else:
            df = self.data_table
            recalculate = True

        self.output_object = manager.process(df, self, recalculate)
        #self._manager_cache[(self, manager)] = self.output_object

    def drop_cached_aggregates(self):
        self._manager_cache = {}

    ## FIXME: reimplement row visibility
    #def reset_row_visibility(self, query_type, df=pd.DataFrame()):
        #if df.empty:
            #df = self.output_object
        #self.row_visibility[query_type] = pd.Series(
            #data=[True] * len(df.index), index=df.index)

    def filter_data(self, column="statistics_frequency"):
        return
        """
        Apply the frequency filters to the output object.
        """
        if not self.filter_list or not options.cfg.use_corpus_filters:
            return 
        no_freq = True
        for filt in self.filter_list:
            if filt.var == COLUMN_NAMES["statistics_frequency"]:
                if not hasattr(self, "frequency_table"):
                    self.frequency_table = self.get_frequency_table()
                try:
                    self.frequency_table = self.frequency_table[self.frequency_table[column].apply(filt.check_number)]
                    no_freq = False
                except AttributeError:
                    pass
        
        # did at least one of the filters contain a frequency filter?
        if no_freq:
            return

        columns = [x for x in self.data_table.columns if not x.startswith(("statistics_", "coquery_invisible")) and x != column]

        self.data_table = pd.merge(self.data_table, self.frequency_table[columns], how="inner", copy=False, on=columns)
        
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
        # If the column has been renamed by the user, that name has top
        # priority, unless ignore_alias is used:
        if not ignore_alias and header in options.cfg.column_names:
            return options.cfg.column_names[header]
        
        # FIXME:
        # this is an ugly hack: a RuntimeError is raised if the header could
        # be translated!
        try:
            # Retain the column header if the query string was from an input file
            if header == "coquery_query_string" and options.cfg.query_label:
                raise RuntimeError(options.cfg.query_label)

            if header.startswith("coquery_invisible"):
                raise RuntimeError(header)

            # treat frequency columns:
            if header == "statistics_frequency":
                if options.cfg.query_label:
                    raise RuntimeError("{}({})".format(COLUMN_NAMES[header], options.cfg.query_label))
                else:
                    raise RuntimeError("{}".format(COLUMN_NAMES[header]))
            
            if header.startswith("statistics_g_test"):
                label = header.partition("statistics_g_test_")[-1]
                raise RuntimeError("G²('{}', y)".format(label))

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
                raise RuntimeError(s)
                    
            # other features:
            if header in COLUMN_NAMES:
                raise RuntimeError(COLUMN_NAMES[header])
            
            # deal with function headers:
            if header.startswith("func_"):
                manager = managers.get_manager(options.cfg.MODE, self.Resource.name)
                match = re.search("(.*)\((.*)\)", header)
                if match:
                    s = match.group(1)
                    fun = manager.get_function(s)
                    raise RuntimeError("{}({})".format(
                                                    fun.get_label(session=self),
                                                    match.group(2)))
                else:
                    fun = manager.get_function(header)
                    if fun == None:
                        raise RuntimeError(header)
                    raise RuntimeError(fun.get_label(session=self))

            if header.startswith("db_"):
                match = re.match("db_(.*)_coq_(.*)", header)
                resource = options.get_resource_of_database(match.group(1))
                res_prefix = "{}.".format(resource.name)
                header = match.group(2)
            else:
                match = re.match("coq_(.*)", header)
                if not match:
                    raise RuntimeError(header)
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
                except ValueError:
                    pass
                raise RuntimeError("{}{}{}".format(res_prefix, COLUMN_NAMES[rc_feature], number))
            
            # special treatment of lexicon features:
            if rc_feature in [x for x, _ in resource.get_lexicon_features()] or resource.is_tokenized(rc_feature):
                try:
                    number = self.quantified_number_labels[int(number) - 1]
                except ValueError:
                    pass
                raise RuntimeError("{}{}{}".format(res_prefix, getattr(resource, str(rc_feature)), number))

            # treat any other feature that is provided by the corpus:
            try:
                raise RuntimeError("{}{}".format(res_prefix, getattr(resource, str(rc_feature))))
            except AttributeError:
                pass

            # other features:
            if rc_feature in COLUMN_NAMES:
                try:
                    number = self.quantified_number_labels[int(number) - 1]
                except ValueError:
                    pass
                raise RuntimeError("{}{}{}".format(res_prefix, COLUMN_NAMES[rc_feature], number))

            raise RuntimeError(header)

        except RuntimeError as e:
            return e.args[0]

class StatisticsSession(Session):
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
        for query_string in options.cfg.query_list:
            if self.query_type:
                new_query = self.query_type(query_string, self)
            else: 
                raise CorpusUnavailableQueryTypeError(options.cfg.corpus, options.cfg.MODE)
            self.query_list.append(new_query)
        self.max_number_of_input_columns = 0

class SessionInputFile(Session):
    def __init__(self):
        super(SessionInputFile, self).__init__()
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
            if self.header == None:
                if options.cfg.file_has_headers:
                    self.header = input_file.columns.values.tolist()
                else:
                    self.header = ["X{}".format(i+1) for i, _ in enumerate(input_file.columns)]
                    input_file.columns = self.header
            options.cfg.query_label = self.header.pop(options.cfg.query_column_number - 1)
            for current_line in input_file.iterrows():
                current_line = list(current_line[1])
                if options.cfg.query_column_number > len(current_line):
                    raise IllegalArgumentError("Column number for queries too big (-n %s)" % options.cfg.query_column_number)
                
                if read_lines >= options.cfg.skip_lines:
                    try:
                        query_string = current_line.pop(options.cfg.query_column_number - 1)
                    except AttributeError:
                        continue
                    new_query = self.query_type(query_string, self)
                    new_query.input_frame = pd.DataFrame(
                        [current_line], columns=self.header)
                    self.query_list.append(new_query)
                self.max_number_of_input_columns = max(len(current_line), self.max_number_of_input_columns)
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
    
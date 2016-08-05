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
from . import queries
from . import filters
from . import tokens
from . import dataengine

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

        options.cfg.current_engine = dataengine.get_engine(options.cfg.MODE)

        logger.info("Corpus '{}' on connection '{}'".format(
            self.Resource.name, options.cfg.current_server))

        self.data_table = pd.DataFrame()
        self.output_object = pd.DataFrame()
        self.output_order = []
        self.header_shown = False
        self.input_columns = []
        self._header_cache = {}
        self._engine_cache = {}

        # row_visibility stores for each query type a pandas Series object
        # with the same index as the respective output object, and boolean
        # values. If the value is False, the row in the output object is
        # hidden, otherwise, it is visible.
        self.row_visibility = {}
        self.column_visibility = defaultdict(pd.Series)

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

    def run_queries(self, to_file=False):
        """ 
        Run each query in the query list, and append the results to the 
        output object. Afterwards, apply all filters, and aggregate the data.
        If Coquery is run as a console program, write the aggregated data to 
        a file (or the standard output).
        """
        self.start_time = datetime.datetime.now()
        self.end_time = None
        
        self.data_table = pd.DataFrame()
        self.quantified_number_labels = []

        number_of_queries = len(self.query_list)

        for i, current_query in enumerate(self.query_list):
            if options.cfg.gui and number_of_queries > 1:
                options.cfg.main_window.showMessage("Running query ({} of {})...".format(
                    i+1, number_of_queries))
            if not self.quantified_number_labels:
                self.quantified_number_labels = [current_query.get_token_numbering(i) for i in range(self.get_max_token_count())]
            start_time = time.time()
            if number_of_queries > 1:
                logger.info("Start query ({} of {}): '{}'".format(i+1, number_of_queries, current_query.query_string))
            else:
                logger.info("Start query: '{}'".format(current_query.query_string))
            current_query.run()
            self.data_table = current_query.append_results(self.data_table)
            logger.info("Query executed (%.3f seconds)" % (time.time() - start_time))

        #self.frequency_table = self.get_frequency_table()
        
        self.filter_data()

        self.data_table.index = range(1, len(self.data_table.index) + 1)

        self.end_time = datetime.datetime.now()
        self.reset_row_visibility(queries.TokenQuery, self.data_table)

        if not options.cfg.gui or to_file:
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

    #def mask_data(self):
        #"""
        #Return a data frame that contains the currently visible rows and 
        #columns from the session's data table.
        #"""
        
        #print(options.cfg.row_visibility)
        #print(options.cfg.column_visibility)
        #print(self.query_type)
        
        #invisible_rows = options.cfg.row_visibility[self.query_type].keys()
        #visible_columns = [x for x in self.output_order if options.cfg.column_visibility[self.query_type].get(x, True)]

        #print(invisible_rows)
        #print(visible_columns)
        
        #print(self.data_table[visible_columns].iloc[~self.data_table.index.isin(invisible_rows)])

    def aggregate_data(self, recalculate=True):
        """
        Apply the aggegate function from the current query type to the 
        data table produced in this session.
        """
        
        engine_type = options.cfg.current_engine
        
        # if no explicit recalculation is requested, try to use a cached 
        # output object for the current query type:
        if not recalculate:
            if engine_type in self._engine_cache:
                print("using cached output for engine {}".format(engine_type.name))
                self.output_object = self._engine_cache[engine_type]
                return

        engine = engine_type(self)

        # Recalculate the output object for the current query type, excluding
        # invisible rows:
        if self.query_type == queries.TokenQuery:
            if not queries.TokenQuery in self.row_visibility:
                self.reset_row_visibility(queries.TokenQuery, self.data_table)
            tab = self.data_table
        else:
            tab = self.data_table[self.row_visibility[queries.TokenQuery]]

        old_index = tab.index

        self.output_object = engine.apply(engine.mutate(self.data_table))

        self.output_object.fillna("", inplace=True)
        self.output_object.index = range(1, len(self.output_object.index) + 1)

        if (not self.query_type in self.row_visibility or 
            len(old_index) != len(self.output_object.index) or
            not old_index.equals(self.output_object.index)):
            self.reset_row_visibility(self.query_type)

        self._engine_cache[engine] = self.output_object

    def drop_cached_aggregates(self):
        self._engine_cache = {}

    def reset_row_visibility(self, query_type, df=pd.DataFrame()):
        if df.empty:
            df = self.output_object
        self.row_visibility[query_type] = pd.Series(
            data=[True] * len(df.index), index=df.index)

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
        
        if header in self._header_cache:
            return self._header_cache[header]
        
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
            
            # other features:
            if header in COLUMN_NAMES:
                raise RuntimeError(COLUMN_NAMES[header])
            
            # deal with function headers:
            if header.startswith("func_"):
                match = re.match("func_(.*)_(\d+)_(\d+)$", header)
                core = match.group(1)
                function_number = int(match.group(2))
                item_number = int(match.group(3))
                #print(header, core, function_number, item_number)
                if core.startswith("db_"):
                    match2 = re.match("db_(.*)_coq_(.*)", core)
                    resource = options.get_resource_of_database(match2.group(1))
                    res_prefix = "{}.".format(resource.name)
                else:
                    match2 = re.match("coq_(.*)", core)
                    res_prefix = ""
                    resource = self.Resource

                if core.startswith("coq_"):
                    core = core.rpartition("coq_")[-1]
                _, hashed, tab, feat = self.Resource.split_resource_feature(core)
                if hashed != None:
                    res_hash = "{}.".format(hashed)
                else:
                    res_hash = ""

                lookup = "func.{}{}_{}".format(res_hash, tab, feat)
                count = 1
                for rc_feature, _, is_lexical, full_label, label in options.cfg.selected_functions:
                    if rc_feature == lookup:
                        if count == function_number:
                            if is_lexical:
                                try:
                                    raise RuntimeError(label.format(N=item_number))
                                except:
                                    raise RuntimeError(label)
                                    
                            else:
                                raise RuntimeError(label.format(N=""))
                        count += 1
                raise RuntimeError("FUNC")
                #return "FUNC({})".format(self.translate_header(header))

            ## treat functions:
            #if is_function:
                #func_counter = collections.Counter()
                #for res, _, label in options.cfg.selected_functions:
                    #res = res.rpartition(".")[-1]
                    #func_counter[res] += 1
                    #fc = func_counter[res]
                    
                    #new_name = "func_{}_{}".format(res, fc)
                    #if new_name == rc_feature:
                        #column_name = getattr(resource, res)
                        #function_label = label
                        #break
                #else:
                    #if options.cfg.selected_functions:
                        #column_name = res
                    #else:
                        #column_name = "UNKNOWN"
                    #function_label = rc_feature
                #try:
                    #number = self.quantified_number_labels[int(number) - 1]
                #except ValueError:
                    #pass
                #return str(function_label).replace(column_name, "{}{}{}".format(
                    #res_prefix, column_name, number))

            
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
                
            # special treatment of context columns:
            if header.startswith("context_lc"):
                raise RuntimeError("L{}".format(header.split("context_lc")[-1]))
            if header.startswith("context_rc"):
                raise RuntimeError("R{}".format(header.split("context_rc")[-1]))
            
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
            self._header_cache[header] = e.args[0]
            
        return self._header_cache[header]

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
    
# -*- coding: utf-8 -*-
"""
corpus.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function

from collections import *
import pandas as pd

from errors import *
import tokens
import options
import sqlwrap
from defines import *

def collapse_words(word_list):
    
    def is_tag(s):
        # there are some tags that should still be preceded by spaces. In 
        # paricular those that are normally used for typesetting, including
        # <span>, but excluding <sup> and <sub>, because these are frequently
        # used in formula:
        
        if s.startswith("<span") or s.startswith("</span"):
            return False
        if s in set(["</b>", "<b>", "</i>", "<i>", "</u>", "<u>", "</s>", "<s>"]):
            return False
        return s.startswith("<") and s.endswith(">") and len(s) > 2

    """ Concatenate the words in the word list, taking clitics, punctuation
    and some other stop words into account."""
    contraction = ["n't", "'s", "'ve", "'m", "'d", "'ll", "'em", "'t"]
    token_list = []
    punct = '!\'),-./:;?^_`}’”]'
    context_list = [x.strip() for x in word_list]
    open_quote = {}
    open_quote ['"'] = False
    open_quote ["'"] = False
    last_token = ""
    for i, current_token in enumerate(context_list):
        if '""""' in current_token:
            current_token = '"'
    
        # stupid list of exceptions in which the current_token should NOT
        # be preceded by a space:
        no_space = False
        if all([x in punct for x in current_token]):
            no_space = True        
        if current_token in contraction:
            no_space = True            
        if last_token in '({[‘“':
            no_space = True            
        if is_tag(last_token):
            no_space = True        
        if is_tag(current_token):
            no_space = True
        if last_token.endswith("/"):
            no_space = True
            
        if not no_space:
            token_list.append(" ")
        
        token_list.append(current_token)
        last_token = current_token
    return "".join(token_list)

class BaseLexicon(object):
    """
    Define a base lexicon class.
    """
    provides = [LEX_WORDID, LEX_ORTH]

    def __init__(self):
        self.resource = None
        self._word_cache = {}
        
    def is_part_of_speech(self, pos):
        """ 
        DESCRIPTION
        is_part_of_speech(pos) returns True if the content of the argument
        pos is considered a valid part-of-speech label for the lexicon. 
        Otherwise, it returns False.
        
        VALUE
        <type 'bool'>
        """
        raise LexiconFeatureUnavailableError("Part-of-speech")

    def check_pos_list(self, L):
        """ Returns the number of elements for which 
        Corpus.is_part_of_speech() is True, i.e. the number of
        elements that are considered a part of speech tag """
        count = 0
        for CurrentPos in L:
            if self.is_part_of_speech(CurrentPos):
                count += 1
        return count

    def get_statistics(self):
        raise CorpusUnsupportedFunctionError

#class ResFeature(str):
    #""" Define a feature class that acts like a string, but has some class
    #properties that makes using features somewhat easier."""
    #def __init__(self, s, *args):
        #if "_" not in s:
            #raise ValueError
        #super(ResFeature, self).__imit__(s, args)
        #self._s = s
        
    #@property
    #def table(self):
        #""" Return the resource table to which the feature belongs."""
        #return "{}_table".format(self._s.split("_")[0])
    
    #@property
    #def table_id(self):
        #""" Return the id resource feature for the table the feature belongs
        #to. """
        #return "{}_id".format(self._s.split("_")[0])

    #def link_id(self, table):
        #""" Return the link resource feature that links the feature's table
        #to the specified table. """
        #return "{}_{}_id".format(self._s.split("_")[0], table)
    
    #def is_id(self):
        #""" Return True if the resource feature is an identifier, i.e. ends
        #in "_id", or False otherwise."""
        #return _s.endswith("_id")


class BaseResource(object):
    """
    """
    # Add internal table that can be used to access system information:
    coquery_query_string = "Query string"
    coquery_expanded_query_string = "Expanded query string"
    coquery_query_file = "Input file"
    coquery_current_date = "Current date"
    coquery_current_time = "Current time"
    coquery_query_token = "Query token"

    # add internal table that can be used to access frequency information:
    coquery_query_string = "Query string"
    coquery_expanded_query_string = "Expanded query string"
    coquery_query_file = "Input file"
    coquery_current_date = "Current date"
    coquery_current_time = "Current time"
    coquery_query_token = "Query token"

    coquery_relative_frequency = "Relative frequency"
    coquery_per_million_words = "Per million words"

    special_table_list = ["coquery", "frequency", "tag"]

    render_token_style = "background: lightyellow"

    @classmethod
    def get_preferred_output_order(cls):
        prefer = ["corpus_word", "word_label", "word_pos", "pos_label", "word_transcript", "transcript_label", "word_lemma", "lemma_label"]
        
        all_features = cls.get_resource_features()
        order = []
        for rc_feature in list(all_features):
            if rc_feature in prefer:
                for i, ordered_feature in enumerate(order):
                    if prefer.index(ordered_feature) > prefer.index(rc_feature):
                        order.insert(i, rc_feature)
                        break
                else:
                    order.append(rc_feature)
                all_features.remove(rc_feature)
        return order + all_features
    
    @classmethod
    def get_resource_features(cls):
        return [x for x in dir(cls) if "_" in x and not x.startswith("_")]

    @classmethod
    def get_table_dict(cls):
        """ Return a dictionary with the table names specified in this
        resource as keys. The values of the dictionary are the table 
        columns. """
        table_dict = {}
        for x in cls.get_resource_features():
            if "_" in x and not x.startswith("_"):
                table, _, _ = x.partition("_")
                if table not in table_dict:
                    table_dict[table] = []
                table_dict[table].append(x)
        for x in list(table_dict.keys()):
            if x not in cls.special_table_list and not "{}_table".format(x) in table_dict[x]:
                table_dict.pop(x)
        try:
            table_dict.pop("tag")
        except (AttributeError, KeyError):
            pass
        return table_dict
    
    @classmethod
    def get_linked_tables(cls, table):
        table_dict = cls.get_table_dict()
        L = []
        for x in table_dict[table]:
            if x.endswith("_id") and x.count("_") == 2:
                _, linked, _ = x.split("_")
                L.append(linked)
        return L
    
    @classmethod
    def get_table_tree(cls, table):
        """ Return a list of all table names that are linked to 'table',
        including 'table' itself. """
        L = [table]
        for x in cls.get_linked_tables(table):
            L = L + cls.get_table_tree(x)
        return L
    
    @classmethod
    def get_table_path(cls, start, end):
        """ Return a list of table names that constitute a link chain from
        table 'start' to 'end', including these two tables. Return None if 
        no path was found, i.e. if table 'end' is not linked to 'start'. """
        table_dict = cls.get_table_dict()
        if "{}_id".format(end) in table_dict[start]:
            return [end]
        for x in table_dict[start]:
            if x.endswith("_id"):
                parts = x.split("_")
                if len(parts) == 3:
                    descend = cls.get_table_path(parts[1], end)
                    if descend:
                        return [start] + descend
        return None

    @classmethod
    def get_table_structure(cls, rc_table, rc_feature_list=[]):
        """ 
        Return a table structure for the table 'rc_table'. 
        
        The table structure is a dictionary with the following keys:
            'parent'        the resource name of the parent table
            'rc_table_name' the resource name of the table
            'children       a dictionary containing the table structures of 
                            all child tables
            'rc_features'   a list of strings containing all resource 
                            features in the table
            'rc_requested_features'  a list of strings containing those
                            resource features from argument 'rc_feature_list'
                            that are contained in this table
            'alias'         the string that is used to give a name to the 
                            table in the INNER JOIN string to avoid naming 
                            clashes with existing tables in the database, 
                            i.e. the resource table string prefixed by COQ_
        """
        D = {}
        D["parent"] = None
        rc_tab = rc_table.split("_")[0]
        
        available_features = []
        requested_features = []
        children = []
        for rc_feature in cls.get_resource_features():
            if rc_feature.endswith("{}_id".format(rc_tab)) and not rc_feature.startswith(rc_tab):
                D["parent"] = "{}_table".format(rc_feature.split("_")[0])
            if rc_feature.startswith("{}_".format(rc_tab)):
                if not rc_feature.endswith("_table"):
                    available_features.append(rc_feature)
                    if rc_feature in rc_feature_list:
                        requested_features.append(rc_feature)
                    # allow functions:
                    if "func.{}".format(rc_feature) in rc_feature_list:
                        requested_features.append("func.{}".format(rc_feature))
                if rc_feature.endswith("_id") and rc_feature.count("_") == 2:
                    children.append(
                        cls.get_table_structure(
                            "{}_table".format(rc_feature.split("_")[1]),
                                rc_feature_list))
        D["rc_table_name"] = rc_table
        D["children"] = children
        D["rc_features"] = sorted(available_features)
        D["rc_requested_features"] = sorted(requested_features)
        D["alias"] = "COQ_{}".format(rc_table.upper())
        return D
    
    @classmethod
    def get_sub_tree(cls, rc_table, tree_structure):
        if tree_structure["rc_table_name"] == rc_table:
            return tree_structure
        else:
            for child in tree_structure["children"]:
                sub_tree = cls.get_sub_tree(rc_table, child)
                if sub_tree:
                    return sub_tree
        return None            

    @classmethod
    def get_requested_features(cls, tree_structure):
        requested_features = tree_structure["rc_requested_features"]
        for child in tree_structure["children"]:
            requested_features += cls.get_requested_features(child)
        return requested_features

    @classmethod
    def get_table_order(cls, tree_structure):
        table_order = [tree_structure["rc_table_name"]]
        for child in tree_structure["children"]:
            table_order += cls.get_table_order(child)
        return table_order        

    @classmethod
    def get_corpus_features(cls):
        """ Return a list of tuples. Each tuple consists of a resource 
        variable name and the display name of that variable. Only those 
        variables are returned that all resource variable names that are 
        desendants of table 'corpus', but not of table 'word'. """
        table_dict = cls.get_table_dict()
        if "corpus" not in table_dict:
            return []
        lexicon_tables = cls.get_table_tree("word")

        corpus_variables = []
        for x in table_dict:
            if x not in lexicon_tables and x not in cls.special_table_list:
                for y in table_dict[x]:
                    if not y.endswith("_id") and not y.startswith("{}_table".format(x)):
                        corpus_variables.append((y, type(cls).__getattribute__(cls, y)))    
        return corpus_variables
    
    @classmethod
    def get_lexicon_features(cls):
        """ Return a list of tuples. Each tuple consists of a resource 
        variable name and the display name of that variable. Only those 
        variables are returned that all resource variable names that are 
        desendants of table 'word'. """
        table_dict = cls.get_table_dict()
        if "word" not in table_dict:
            return []
        lexicon_tables = cls.get_table_tree("word")
        lexicon_variables = []
        for x in table_dict:
            if x in lexicon_tables and x not in cls.special_table_list:
                for y in table_dict[x]:
                    if not y.endswith("_id") and not y.startswith("{}_table".format(x)):
                        lexicon_variables.append((y, type(cls).__getattribute__(cls, y)))    
        return lexicon_variables
    
    @staticmethod
    def get_feature_from_function(func):
        if func.count(".") > 1:
            return "_".join(func.split(".")[1:])
        else:
            return func.split(".")[-1]

    @staticmethod
    def get_referent_feature(rc_feature):
        """
        Get the referent feature name of a rc_feature.
        
        For normal output columns, the referent feautre name is identical 
        to the rc_feature string. 
        
        For functions, it is the rc_feature minus the prefix "func.". 
        
        For columns from an external table, or for functions applied to such 
        columns, it is the feature name of the column that the label is 
        linked to.
        
        Parameters
        ----------
        rc_feature : string
        
        Returns
        -------
        resource : string
        """
        
        if "." not in rc_feature:
            return rc_feature
        elif rc_feature.startswith("func.") and rc_feature.count(".") == 1:
            return rc_feature.rpartition("func.")[-1]
        else:
            prefix_stripped = rc_feature.rpartition("func.")[-1]
            external, internal = options.cfg.external_links[prefix_stripped]
            internal_table, internal_feature = internal.split(".")
            return internal_feature

    @classmethod
    def is_lexical(cls, rc_feature):
        lexicon_features = [x for x, _ in cls.get_lexicon_features()]
        resource = cls.get_referent_feature(rc_feature)
        return resource in lexicon_features
    
    @classmethod
    def translate_filters(cls, filters):
        """ Return a translation list that contains the corpus feature names
        of the variables used in the filter texts. """
        corpus_variables = cls.get_corpus_features()
        filter_list = []
        for filt in filters:
            variable = filt._variable
            for column_name, display_name in corpus_variables:
                if variable.lower() == display_name.lower():
                    break
            else:
                # illegal filter?
                print("illegal filter?", filt)
                column_name = ""
            if column_name:
                table = str("{}_table".format(
                        column_name.partition("_")[0]))
                table_name = type(cls).__getattribute__(cls, table)
                filter_list.append((variable, column_name, table_name, filt._op, filt._value_list, filt._value_range))
        return filter_list

    @classmethod
    def provides_pos(cls):
        """
        Return True if part-of-speech information is available for this 
        resource.
        """
        features = cls.get_resource_features()
        return "word_pos" in features or "pos_tabel" in features or "corpus_pos" in features

class BaseCorpus(object):
    provides = []
    
    def __init__(self):
        self.lexicon = None
        self.resource = None
        
    def get_corpus_size(self):
        """ Return the number of tokens in the corpus, taking the current 
        filter restrictions into account."""
        raise CorpusUnsupportedFunctionError

    def get_context(self, token_id):
        """ returns the context of the token specified by token_id. """
        raise CorpusUnsupportedFunctionError
    
    def provides_feature(self, x):
        return x in self.provides + self.lexicon.provides

    def get_statistics(self):
        raise CorpusUnsupportedFunctionError
    
class SQLResource(BaseResource):
    def get_operator(self, Token):
        """ returns a string containing the appropriate operator for an 
        SQL query using the Token (considering wildcards and negation) """
        if options.cfg.regexp:
            return "REGEXP"
        if Token.has_wildcards(Token.S):
            Operators = {True: "NOT LIKE", False: "LIKE"}
        else:
            Operators = {True: "!=", False: "="}
        return Operators [False]
    
    def __init__(self, lexicon, corpus):
        super(SQLResource, self).__init__()
        self.lexicon = lexicon
        self.corpus = corpus
        self.connect_to_database()

    def connect_to_database(self):
        self.DB = sqlwrap.SqlDB(Host=options.cfg.db_host, Port=options.cfg.db_port, User=options.cfg.db_user, Password=options.cfg.db_password, Database=self.db_name)
        logger.debug("Connected to database %s@%s:%s."  % (self.db_name, options.cfg.db_host, options.cfg.db_port))
        logger.debug("User=%s, password=%s" % (options.cfg.db_user, options.cfg.db_password))
        
    def get_statistics(self):
        lexicon_features = [x for x, _ in self.get_lexicon_features()]
        corpus_features = [x for x, _ in self.get_corpus_features()]
        resource_features = lexicon_features + corpus_features

        stats = []
        # determine table size for all columns
        table_sizes = {}
        for rc_table in [x for x in dir(self) if not x.startswith("_") and x.endswith("_table")]:
            table = getattr(self, rc_table)
            S = "SELECT COUNT(*) FROM {}".format(table)
            self.DB.execute(S)
            table_sizes[table] = self.DB.Cur.fetchone()[0]

        # get distinct values for each feature:
        for rc_feature in dir(self):
            if rc_feature.endswith("_table") or "_" not in rc_feature:
                continue
            rc_table = "{}_table".format(rc_feature.split("_")[0])
            try:
                if getattr(self, rc_table) not in table_sizes:
                    continue
            except AttributeError:
                continue
            if rc_feature == "{}_id".format(rc_feature.split("_")[0]):
                continue
            try:
                table = getattr(self, rc_table)
                column = getattr(self, rc_feature)
            except AttributeError:
                pass
            else:
                S = "SELECT COUNT(DISTINCT {}) FROM {}".format(column, table)
                self.DB.execute(S)
                stats.append([table, column, table_sizes[table], self.DB.Cur.fetchone()[0]])
        
        df = pd.DataFrame(stats)
        # calculate ratio:
        df[4] = df[2] / df[3]
        return df

    def yield_query_results(self, Query, token_list, self_joined=False):
        """
        Run the corpus query specified in the token_list on the corpus
        and yield the results.
        """
        try:
            if self_joined:
                query_string = self.corpus.sql_string_query_self_joined(Query, token_list)
            else:
                query_string = self.corpus.sql_string_query(Query, token_list)
        except WordNotInLexiconError:
            query_string = ""
            
        Query.Session.output_order = self.get_select_list(Query)

        if query_string:
            cursor = self.DB.execute_cursor(query_string)
        else:
            cursor = {}
        for current_result in cursor:
            if options.cfg.MODE != QUERY_MODE_COLLOCATIONS:
                # add contexts for each query match:
                if (options.cfg.context_left or options.cfg.context_right) and options.cfg.context_source_id:
                    left, target, right = self.get_context(
                        current_result["coquery_invisible_corpus_id"], 
                        Query._current_number_of_tokens, True)
                    if options.cfg.context_mode == CONTEXT_KWIC:
                        if options.cfg.context_left:
                            current_result["coq_context_left"] = collapse_words(left)
                        if options.cfg.context_right:
                            current_result["coq_context_right"] = collapse_words(right)
                    elif options.cfg.context_mode == CONTEXT_STRING:
                        current_result["coq_context"] = collapse_words(left + [x.upper() for x in target] + right)
                    elif options.cfg.context_mode == CONTEXT_SENTENCE:
                        current_result["coq_context"] = collapse_word(self.get_context_sentence())
            yield current_result

    def get_context(self, token_id, number_of_tokens, case_sensitive):
        if options.cfg.context_sentence:
            raise NotImplementedError("Sentence contexts are currently not supported.")
        token_id = int(token_id)
        source_id = self.corpus.get_source_id(token_id)

        old_verbose = options.cfg.verbose
        options.cfg.verbose = False

        left_span = options.cfg.context_left
        if left_span > token_id:
            start = 1
        else:
            start = token_id - left_span

        S = self.corpus.sql_string_get_wordid_in_range(
                start, 
                token_id - 1, source_id)
        self.DB.execute(S)
        left_context_words = self.lexicon.get_orth([x for x, in self.DB.Cur])
        left_context_words = [''] * (left_span - len(left_context_words)) + left_context_words

        S = self.corpus.sql_string_get_wordid_in_range(
                token_id + number_of_tokens, 
                token_id + number_of_tokens + options.cfg.context_right - 1, source_id)
        self.DB.execute(S)
        right_context_words = self.lexicon.get_orth([x for x, in self.DB.Cur])
        right_context_words = right_context_words + [''] * (options.cfg.context_right - len(right_context_words))

        options.cfg.verbose = old_verbose

        if options.cfg.context_mode == CONTEXT_STRING:
            S = self.corpus.sql_string_get_wordid_in_range(
                    token_id,
                    token_id + number_of_tokens - 1,
                    source_id)
            self.DB.execute(S)
            target_words = self.lexicon.get_orth([x for (x, ) in self.DB.Cur])
        else:
            target_words = []
        return (left_context_words, target_words, right_context_words)

    def get_context_sentence(self, sentence_id):
        raise NotImplementedError
        #S = self.sql_string_get_sentence_wordid(sentence_id)
        #self.resource.DB.execute(S)

    @classmethod
    def get_select_list(cls, query):
        """
        Return a list of field names that can be used to extract the 
        requested columns from the joined MySQL query table.
        
        This list is usually stored in Session.output_order and determines
        which columns appear in the output table. If a column is missing, 
        it may be because it is not correctly included in this set.
        
        Parameters
        ----------
        query : CorpusQuery
            The query for which a select set is required
            
        Returns
        -------
        select_list : list
            A list of strings representing the aliased columns in the joined
            MySQL query table.
        """
        
        lexicon_features = [x for x, _ in cls.get_lexicon_features() if x in options.cfg.selected_features]
        corpus_features = [x for x, _ in cls.get_corpus_features() if x in options.cfg.selected_features]
        max_token_count = query.Session.get_max_token_count()
        # the initial select list contains the columns from the input file
        # (if present):
        select_list = list(query.Session.input_columns)

        # then, add an appropriately aliased name for each selected feature:
        for rc_feature in options.cfg.selected_features:
            if rc_feature in lexicon_features:
                select_list += ["coq_{}_{}".format(rc_feature, x+1) for x in range(max_token_count)]
            elif rc_feature in corpus_features:
                select_list.append("coq_{}_1".format(rc_feature))
            elif rc_feature.startswith("coquery_"):
                if rc_feature == "coquery_query_token": 
                    select_list += ["coquery_query_token_{}".format(x + 1) for x in range(max_token_count)]
                else:
                    select_list.append(rc_feature)

        # linked columns
        for rc_feature in options.cfg.external_links:
            if rc_feature not in options.cfg.selected_features:
                continue
            if rc_feature.startswith("func"):
                continue
            external_table, external_feature = rc_feature.split(".")
            linked_feature = "{}_{}".format(external_table, external_feature)
            if cls.is_lexical(rc_feature):
                select_list += ["coq_{}_{}".format(linked_feature, x+1) for x in range(max_token_count)]
            else:
                select_list.append("coq_{}_1".format(linked_feature))

        # functions:
        func_counter = Counter()
        for rc_feature in options.cfg.selected_features:
            if rc_feature.startswith("func."):
                if rc_feature.count(".") > 1:
                    resource = "_".join(rc_feature.split(".")[1:])
                    #external, internal = options.cfg.external_links[rc_feature]
                    #is_lexical = internal.split(".")[-1] in lexicon_features
                else:
                    resource = rc_feature.split(".")[-1]
                    #is_lexical = resource in lexicon_features

                func_counter[resource] += 1
                fc = func_counter[resource]
                
                if cls.is_lexical(rc_feature):
                    select_list += ["coq_func_{}_{}_{}".format(resource, fc, x + 1) for x in range(max_token_count)]
                else:
                    select_list.append("coq_func_{}_{}_1".format(resource, fc))

        if options.cfg.MODE != QUERY_MODE_COLLOCATIONS:
            # add contexts for each query match:
            if (options.cfg.context_left or options.cfg.context_right) and options.cfg.context_source_id:
                if options.cfg.context_mode == CONTEXT_KWIC:
                    if options.cfg.context_left:
                        select_list.append("coq_context_left")
                    if options.cfg.context_right:
                        select_list.append("coq_context_right")
                elif options.cfg.context_mode == CONTEXT_STRING:
                    select_list.append("coq_context")
                elif options.cfg.context_mode == CONTEXT_SENTENCE:
                    select_list.append("coq_context")

        if options.cfg.context_source_id:
            select_list.append("coquery_invisible_corpus_id")
            select_list.append("coquery_invisible_number_of_tokens")
        return select_list

class SQLLexicon(BaseLexicon):
    entry_cache = {}
    
    def sql_string_is_part_of_speech(self, pos):
        current_token = tokens.COCAToken(pos, self, parse=True, replace=False)
        lexicon_features = [x for x, _ in self.resource.get_lexicon_features()]
        if "pos_table" in lexicon_features:
            return "SELECT {} FROM {} WHERE {} {} '{}' LIMIT 1".format(
                self.resource.pos_id, 
                self.resource.pos_table, 
                self.resource.pos_label,
                self.resource.get_operator(current_token),
                pos)
        elif "word_pos" in lexicon_features:
            return "SELECT {} FROM {} WHERE {} {} '{}' LIMIT 1".format(
                self.resource.word_pos,
                self.resource.word_table,
                self.resource.word_pos,
                self.resource.get_operator(current_token),
                pos)
        elif "corpus_pos" in lexicon_features:
            return "SELECT {} FROM {} WHERE {} {} '{}' LIMIT 1".format(
                self.resource.corpus_pos,
                self.resource.corpus_table,
                self.resource.corpus_pos,
                self.resource.get_operator(current_token),
                pos)
        else:
            raise LexiconFeatureUnavailableError

    def sql_string_get_other_wordforms(self, match):
        if "lemma_table" not in dir(self.resource):
            word_lemma_column = self.resource.word_lemma
        else:
            word_lemma_column = self.resource.word_lemma_id
            
        return 'SELECT {word_id} FROM {word_table} WHERE {word_lemma_id} IN (SELECT {word_lemma_id} FROM {word_table} WHERE {word_label} {operator} "{match}")'.format(
            word_id=self.resource.word_id,
            word_table=self.resource.word_table,
            word_label=self.resource.word_label,
            word_lemma_id=word_lemma_column,
            operator=self.resource.get_operator(match),
            match=match)
    
    def sql_string_get_posid_list_where(self, token):
        comparing_operator = self.resource.get_operator(token)
        where_clauses = []
        for current_pos in token.class_specifiers:
            #current_token = tokens.COCAToken(current_pos, self)
            current_token = current_pos
            if "pos_label" in dir(self.resource):
                pos_label = self.resource.pos_label
            else:
                pos_label = self.resource.word_pos
            S = '{} {} "{}"'.format(
                pos_label,
                comparing_operator, 
                current_token)
            where_clauses.append (S)
        return "(%s)" % "OR ".join (where_clauses)
    
    def sql_string_get_wordid_list_where(self, token):
        """ Returns a MySQL string that will return a list of all word_ids
        that match the given token. """
        # TODO: fix cfg.lemmatize
        # FIXME: this needs to be revised. 
        
        if options.cfg.lemmatize_tokens:
            dummy = self.get_other_wordforms(token)
        
        sub_clauses = []
        
        lexicon_features = [x for x, _ in self.resource.get_lexicon_features()]
        
        if token.lemma_specifiers:
            if not ("lemma_label" in lexicon_features or "word_lemma" in lexicon_features or "corpus_lemma" in lexicon_feature):
                raise LexiconUnsupportedFunctionError
            
            specifier_list = token.lemma_specifiers
            if "lemma_table" in dir(self.resource):
                target = "COQ_LEMMA_TABLE.{}".format(
                    self.resource.lemma_label)
            else:
                target = "{}.{}".format(
                    self.resource.word_table,
                    self.resource.word_lemma)
        else:
            specifier_list = token.word_specifiers
            target = "{}.{}".format(
                self.resource.word_table,
                self.resource.word_label)

        for CurrentWord in specifier_list:
            if CurrentWord != "%":
                current_token = tokens.COCAWord(CurrentWord, self, replace=False, parse=False)
                current_token.negated = token.negated
                if not isinstance(current_token.S, unicode):
                    S = unicode(current_token.S)
                else:
                    S = current_token.S
                # take care of quotation marks:
                S = S.replace('"', '""')
                sub_clauses.append('%s %s "%s"' % (target, self.resource.get_operator(current_token), S))
                
        for current_transcript in token.transcript_specifiers:
            if current_transcript:
                current_token = tokens.COCAWord(current_transcript, self, replace=False, parse=False)
                current_token.negated = token.negated
                if "transcript_table" not in dir(self.resource):
                    target = "{}.{}".format(
                        self.resource.word_table, 
                        self.resource.word_transcript)
                elif self.resource.transcript_table != self.resource.word_table:
                    target = "COQ_TRANSCRIPT_TABLE.{}".format(
                        self.resource.transcript_label)
                else:
                    target = "{}.{}".format(
                        self.resource.transcript_table,
                        self.resource.transcript_label)
                # take care of quotation marks:
                S = str(current_token)
                S = S.replace('"', '""')
                sub_clauses.append('%s %s "%s"' % (target, self.resource.get_operator(current_token), S))
        
        where_clauses = []
        if sub_clauses:
            where_clauses.append("(%s)" % " OR ".join (sub_clauses))
        if token.class_specifiers and self.resource.provides_pos():
            where_clauses.append(self.sql_string_get_posid_list_where(token))
        return " AND ".join(where_clauses)
            
    def is_part_of_speech(self, pos):
        self.resource.DB.execute(self.sql_string_is_part_of_speech(pos), ForceExecution=True)
        query_result = self.resource.DB.fetch_all ()
        return len(query_result) > 0
    
    def get_other_wordforms(self, Word):
        """ Return a list of word_id containing all other entries in the
        lexicon which have the same lemma as the word given as an argument.
        """ 

        if LEX_LEMMA not in self.provides:
            raise LexiconUnsupportedFunctionError
        
        current_word = tokens.COCAWord(Word, self, replace=False)
        # create an inner join of lexicon, containing all rows that match
        # the string stored in current_word:
        self.resource.DB.execute(self.sql_string_get_other_wordforms(current_word))
        return [result[0] for result in self.resource.DB.Cur]

    def get_orth(self, word_id):
        """ 
        Return the orthographic forms of the word_ids.
        
        If word_id_list is not a list, it is converted into one.
        
        Parameters
        ----------
        word_id : value or list
            A value or list of value designating the words_ids that are to 
            be looked up.
            
        Returns
        -------
        L : list
            A list of strings, giving the orthographic representation of the
            words.
        """
        if not hasattr(word_id, "__iter__"):
            word_id = [word_id]
        
        # if there is no attribute "corpus_word_id" in the resource, we have
        # to assume that the identifies provided are already all the 
        # information that we have on the words. This makes sense for 
        # example in the case of dictionaries. So, in that case, we simply
        # return the list:
        if not "corpus_word_id" in dir(self.resource):
            return word_id
        
        # prepare a partial MySQL query:
        S = "SELECT {} FROM {} WHERE {} = ".format(
                    self.resource.word_label, 
                    self.resource.word_table,
                    self.resource.word_id)

        # build the word list:
        L = []
        for x in word_id:
            # check the word cache:
            try:
                L.append(self._word_cache[x])
            except KeyError:
                self.resource.DB.execute("{}{}".format(S, x))
                try:
                    orth = self.resource.DB.Cur.fetchone()[0]
                except IndexError:
                    # no entry for this word_id -- return default value:
                    L.append("<NA>")
                else:
                    L.append(orth)
                    # add to cache:
                    self._word_cache[x] = orth
        return L
    def sql_string_get_posid_list(self, token):
        where_string = self.sql_string_get_posid_list_where(token)

        if "pos_table" in dir(self.resource):
            return "SELECT {word_table}.{word_pos} FROM {word_table} INNER JOIN {pos_table} ON {pos_table}.{pos_id} = {word_table}.{word_pos} WHERE {where_string}".format(
                word_pos=self.resource.word_pos_id,
                word_table=self.resource.word_table,
                pos_table=self.resource.pos_table,
                pos_id=self.resource.pos_id,
                where_string=where_string)
        else:
            return "SELECT {} FROM {} WHERE {}".format(
                self.resource.word_pos, self.resource.word_table, where_string)

    def get_posid_list(self, token):
        """ Return a list of all PosIds that match the query token. """
        S = self.sql_string_get_posid_list(token)
        self.resource.DB.execute(S)
        return set([x[0] for x in self.resource.DB.fetch_all()])

    def sql_string_get_matching_wordids(self, token):
        """ returns a string that may be used to query all word_ids that
        match the token specification."""
        self.where_list = [self.sql_string_get_wordid_list_where(token)]
        self.table_list = [self.resource.word_table]
        if token.lemma_specifiers:
            if "lemma_table" in dir(self.resource):
                self.table_list.append("LEFT JOIN {} AS COQ_LEMMA_TABLE ON {}.{} = COQ_LEMMA_TABLE.{}".format(
                    self.resource.lemma_table,
                    self.resource.word_table,
                    self.resource.word_lemma_id,
                    self.resource.lemma_id))
        if token.class_specifiers:
            if "pos_table" in dir(self.resource):
                self.table_list.append("LEFT JOIN {} AS COQ_POS_TABLE ON {}.{} = COQ_POS_TABLE.{}".format(
                    self.resource.pos_table,
                    self.resource.word_table,
                    self.resource.word_pos_id,
                    self.resource.pos_id))
        if token.transcript_specifiers:
            if "transcript_table" in dir(self.resource):
                self.table_list.append("LEFT JOIN {} AS COQ_TRANSCRIPT_TABLE ON {}.{} = COQ_TRANSCRIPT_TABLE.{}".format(
                    self.resource.transcript_table,
                    self.resource.word_table,
                    self.resource.word_transcript_id,
                    self.resource.transcript_id))
        where_string = " AND ".join(self.where_list)
        S = "SELECT {}.{} FROM {} WHERE {}".format(
                self.resource.word_table,
                self.resource.word_id,
                " ".join(self.table_list),
                where_string)
        return S

    def get_matching_wordids(self, token):
        if token.S == "%" or token.S == "":
            return []
        S = self.sql_string_get_matching_wordids(token)
        self.resource.DB.execute(S)
        query_results = self.resource.DB.fetch_all()
        if not query_results:
            raise WordNotInLexiconError
        else:
            return [x[0] for x in query_results]
        
    def get_statistics(self):
        stats = {}
        stats["lexicon_provides"] = " ".join(self.provides)
        stats["lexicon_features"] = " ".join([x for x, _ in self.resource.get_lexicon_features()])
        return stats

class SQLCorpus(BaseCorpus):
    def __init__(self):
        super(SQLCorpus, self).__init__()
        self._frequency_cache = {}
        self._corpus_size_cache = None

    def get_source_id(self, token_id):
        if "corpus_source_id" in dir(self.resource):
            origin_column = self.resource.__getattribute__("corpus_source_id")
        elif "corpus_file_id" in dir(self.resource):
            origin_column = self.resource.__getattribute__("corpus_file_id")
        else:
            raise NotImplementedError("Cannot determine token source.")
        S = "SELECT {} FROM {} WHERE {} = {}".format(
            origin_column, self.resource.corpus_table, self.resource.corpus_id, token_id)
        self.resource.DB.execute(S)
        return self.resource.DB.Cur.fetchone()[0]

    def get_corpus_size(self):
        """ Return the number of tokens in the corpus, taking the current 
        filter restrictions into account."""

        if not self._corpus_size_cache:
            filter_strings = self.sql_string_run_query_filter_list(self_joined=False)
            for x in filter_strings:
                pass
            S = "SELECT COUNT(*) FROM {}".format(self.resource.corpus_table)
            self.resource.DB.execute(S)
            self._corpus_size_cache = self.resource.DB.Cur.fetchone()[0]
        return self._corpus_size_cache

    def get_frequency(self, s):
        """ Return a longint that gives the corpus frequency of the token,
        taking the filter list from self.resource.filter_list into account."""
        if s in self._frequency_cache:
            return self._frequency_cache[s]
        
        if s in ["%", "_"]:
            s = "\\" + s
        
        if not s:
            return 0
        
        token = tokens.COCAToken(s, self, False)
        
        try:
            if "pos_table" not in dir(self.resource):
                word_pos_column = self.resource.word_pos
            else:
                word_pos_column = self.resource.word_pos_id
        except AttributeError:
            word_pos_column = None
        try:
            where_clauses = self.get_whereclauses(token, self.resource.word_id, word_pos_column)
        except WordNotInLexiconError:
            freq = 0
        else:
            S = "SELECT COUNT(*) FROM {0} WHERE {1}".format(
                self.resource.corpus_table, " AND ".join(where_clauses))
            self.resource.DB.execute(S)
            freq = self.resource.DB.Cur.fetchone()[0]
        self._frequency_cache[s] = freq
        return freq

    def get_whereclauses(self, token, WordTarget, PosTarget):
        if not token:
            return []
        where_clauses = []
        # FIXME: This is a hard-coded special case for 'coca'. Ugh. Instead,
        # it should probably be a check against 'self_joined' or something
        # like that
        if self.resource.name == "coca":
            L = set(self.lexicon.get_matching_wordids(token))
            if L:
                return ["{} IN ({})".format(
                    WordTarget, ", ".join(["{}".format(x) for x in L]))]
    
        if token.word_specifiers or token.lemma_specifiers or token.transcript_specifiers:
            # if there is a token with either a wordform, lemma, or token
            # specification, then get the list of matching word_ids from the 
            # lexicon:
            L = set(self.lexicon.get_matching_wordids(token))
            if L:
                where_clauses.append("{} IN ({})".format(
                    WordTarget, 
                    ", ".join (map (str, L))))
        else:
            # if only a class specification is given, this specification is
            # used as the where clause:
            if token.class_specifiers:                
                L = self.lexicon.get_posid_list(token)
                if L: 
                    where_clauses.append("{} IN ({})".format(
                        PosTarget, 
                        ", ".join (["'%s'" % x for x in L])))
        return where_clauses
    
    def sql_string_run_query_filter_list(self, self_joined):
        """ Return an SQL string that contains the result filters."""
        filter_list = self.resource.translate_filters(self.resource.filter_list)
        L = []
        for column, corpus_feature, table, operator, value_list, val_range in filter_list:
            s = ""
            if val_range:
                s = "{}.{} BETWEEN {} AND {}".format(table, column, min(val_range), max(val_range))
            else:
                if len(value_list) > 1:
                    raise TypeError
                    if any([x in self.wildcards for x in value_list]):
                        s = " OR ".join(["{}.{} LIKE {}".format(table, column, x) for x in value_list])
                        
                    else:
                        s = "{}.{} IN ({})".format(table, column, ", ".join(["'{}'".format(x) for x in value_list]))
                else:
                    s = "{}.{} = '{}'".format(table, column, value_list[0]) 
            L.append(s)
        return L

    def get_token_query_string(self, current_token, number, self_joined=False):
        """ 
        Return a MySQL SELECT string that selects a table matching the 
        current token, and which includes all columns that are requested, or 
        which are required to join the tables. 
        
        Parameters
        ----------
        current_token : CorpusToken
            An instance of CorpusToken as a part of a query string.
        number : int
            The number of current_token in the query string (starting with 0)
        self_joined : bool
            True if a self-joined table is used, or False otherwise.

        Returns
        -------
        s : string
            The partial MySQL string.
        """
            
        # corpus variables will only be included in the token query string if 
        # this is the first query token.
        if number == 0:
            requested_features = [x for x in options.cfg.selected_features]
            
            # if a GUI is used, include source features so the entries in the
            # result table can be made clickable to show the context:
            if options.cfg.gui or options.cfg.context_left or options.cfg.context_right:
                # in order to make this not depend on a fixed database layout 
                # (here: 'source' and 'file' tables), we should check for any
                # table that corpus_table is linked to except for word_table
                # (and all child tables).            
                if "corpus_source_id" in dir(self.resource):
                    requested_features.append("corpus_source_id")
                    options.cfg.context_source_id = "corpus_source_id"
                elif "corpus_file_id" in dir(self.resource):
                    requested_features.append("corpus_file_id")
                    options.cfg.context_source_id = "corpus_file_id"
                else:
                    options.cfg.context_source_id = None
        else:
            corpus_variables = [x for x, _ in self.resource.get_corpus_features()]
            requested_features = [x for x in options.cfg.selected_features if not x in corpus_variables]

        # add all features that are required for the query filters:
        rc_where_constraints = defaultdict(set)
        if number == 0:
            for filt in self.resource.translate_filters(self.resource.filter_list):
                variable, rc_feature, table_name, op, value_list, _value_range = filt
                if op.upper() == "LIKE":
                    if "*" not in value_list[0]:
                        value_list[0] = "*{}*".format(value_list[0])
                    value_list[0] = tokens.COCAToken.replace_wildcards(value_list[0])
                requested_features.append(rc_feature)
                rc_table = "{}_table".format(rc_feature.partition("_")[0])
                rc_where_constraints[rc_table].add(
                    '{} {} "{}"'.format(
                        self.resource.__getattribute__(rc_feature), op, value_list[0]))

        for linked in options.cfg.external_links:
            external, internal = options.cfg.external_links[linked]
            internal_feature = internal.rpartition(".")[-1]
            if internal_feature not in requested_features:
                requested_features.append(internal_feature)

        # make sure that the word_id is always included in the query:
        requested_features.append("corpus_word_id")

        # make sure that the tables and features that are required to 
        # match the current token are also requested as features:
        try:
            if "pos_table" not in dir(self.resource):
                pos_feature = "word_pos"
            else:
                pos_feature = "word_pos_id"
        except AttributeError:
            word_pos_column = None
        else:
            try:
                word_pos_column = self.resource.__getattribute__(pos_feature)
            except AttributeError:
                word_pos_column = None

        # create constraint lists:
        sub_list = set([])
        where_clauses = self.get_whereclauses(
            current_token, 
            self.resource.corpus_word_id, 
            word_pos_column)
        for x in where_clauses:
            if x: 
                sub_list.add(x)
        if sub_list:
            if current_token.negated:
                s = "NOT ({})".format(" AND ".join(sub_list))
            else:
                s = " AND ".join(sub_list)
            if current_token.class_specifiers and not (current_token.word_specifiers or current_token.lemma_specifiers or current_token.transcript_specifiers):
                requested_features.append(pos_feature)
                rc_where_constraints["word_table"].add(s)
            else:
                rc_where_constraints["corpus_table"].add(s)

        # get a list of all tables that are required to satisfy the 
        # feature request:
        required_tables = {}
        for rc_feature in requested_features:
            rc_table = "{}_table".format(rc_feature.split("_")[0])

            if rc_feature.startswith("func."):
                rc_table = rc_table.split("func.")[-1]
                function = True
            else:
                function = False

            if rc_table in ("coquery_table", "frequency_table", "tag_table"):
                continue

            if rc_table not in required_tables:
                tree = self.resource.get_table_structure(rc_table,  options.cfg.selected_features)
                parent = tree["parent"]
                table_id = "{}_id".format(rc_feature.split("func.")[-1].split("_")[0])
                required_tables[rc_table] = tree
                requested_features.append(table_id)
                if parent:
                    parent_id = "{}_{}".format(parent.split("_")[0], table_id)
                    requested_features.append(parent_id)

        join_strings = {}
        external_links = []
        join_strings[self.resource.corpus_table] = "{} AS COQ_CORPUS_TABLE".format(self.resource.corpus_table)
        full_tree = self.resource.get_table_structure("corpus_table", requested_features)
        # create a list of the tables 
        select_list = set([])
        for rc_table in required_tables:
            # FIXME: This section needs to be simplified!
           # linked table?
            if "." in rc_table and not rc_table.startswith("func."):
                external_corpus, rc_table = rc_table.split(".")
                resource = get_available_resources()[external_corpus][0]
                table = resource.__getattribute__(resource, rc_table)
                
                column_list = []
                for linked in options.cfg.external_links:
                    if linked.startswith("func"):
                        _, rc_corpus, rc_feature = linked.split(".")
                    else:
                        rc_corpus, rc_feature = linked.split(".")
                    if rc_corpus == external_corpus:
                        name = "coq_{}_{}_{}".format(external_corpus, rc_feature, number +1)
                        variable_string = "{} AS {}".format(
                            resource.__getattribute__(resource, rc_feature),
                            name)
                        column_list.append(variable_string)
                        select_list.add(name)

                        external, internal = options.cfg.external_links[linked]
                        internal_feature = internal.rpartition(".")[-1]
                        external_feature = external.rpartition(".")[-1]
                        linking_variable = "{} AS coq_{}_{}_{}".format(
                            resource.__getattribute__(resource, external_feature),
                            external_corpus,
                            external_feature, number+1)
                        
                        column_list.append(linking_variable)
                                        
                columns = ", ".join(set(column_list))
                alias = "coq_{}_{}".format(external_corpus, table).upper()
                S = "INNER JOIN (SELECT {columns} FROM {corpus}.{table}) AS {alias} ON coq_{internal_feature}_{n} = coq_{corpus}_{external_feature}_{n}".format(columns=columns, n=number+1, internal_feature=internal_feature, corpus=external_corpus, table=table, external_feature=external_feature, alias=alias)
                external_links.append(S)
            else:
                rc_tab = rc_table.split("_")[0]
                sub_tree = self.resource.get_sub_tree(rc_table, full_tree)
                parent_tree = self.resource.get_sub_tree(sub_tree["parent"], full_tree) 
                table = self.resource.__getattribute__(rc_table)
                if parent_tree:
                    rc_parent = parent_tree["rc_table_name"]
                else:
                    rc_parent = None

                column_list = set()
                for rc_feature in sub_tree["rc_requested_features"]:
                    if rc_feature.startswith("func."):
                        name = "coq_{}_{}".format(
                            rc_feature.split("func.")[-1], number+1)
                    else:
                        name = "coq_{}_{}".format(rc_feature, number+1)

                    variable_string = "{} AS {}".format(
                        self.resource.__getattribute__(rc_feature.split("func.")[-1]),
                        name)
                    column_list.add(variable_string)
                    select_list.add(name)
                
                columns = ", ".join(column_list)
                where_string = ""
                if rc_table in rc_where_constraints:
                    where_string = "WHERE {}".format(" AND ".join(list(rc_where_constraints[rc_table])))

                if rc_parent:
                    parent_id = "coq_{}_{}_id_{}".format(
                        rc_parent.split("_")[0], 
                        rc_table.split("_")[0],
                        number+1)
                    child_id = "coq_{}_id_{}".format(
                        rc_table.split("_")[0],
                        number+1)
                    
                    join_strings[rc_table] = "INNER JOIN (SELECT {columns} FROM {table} {where}) AS {alias} ON {parent_id} = {child_id}".format(
                        columns = columns, 
                        table = table,
                        alias = sub_tree["alias"],
                        parent = parent_tree["alias"],
                        where = where_string,
                        number = number+1,
                        parent_id = parent_id,
                        child_id = child_id)
                else:
                    join_strings[rc_table] = "(SELECT {columns} FROM {table} {where}) AS {alias}".format(
                        columns = columns, 
                        table = table,
                        alias = sub_tree["alias"],
                        where = where_string)

        # create a list containing the join strings for the different tables,
        # in the order in which they are required based on their position in
        # the database layout:
        table_order = self.resource.get_table_order(full_tree)
        L = []
        for x in table_order:
            if x in join_strings and not join_strings[x] in L:
                L.append(join_strings[x])
                
        for x in external_links:
            if x not in L:
                L.append(x)

        if not select_list:
            return ""
        
        # add the variable storing the source_id or file_id to the selected
        # columns so that they can be used to retrieve the context:
        if number == 0 and options.cfg.context_source_id:
            select_list.add("coq_{}_1".format(options.cfg.context_source_id))

        return "SELECT {} FROM {}".format(", ".join(select_list), " ".join(L))
    
    def get_token_query_order(self, token_list):
        """ 
        Return an order list in which the token queries should be executed. 
        
        Ideally, the order corresponds to the number of rows in the 
        corpus that match the token query, from small to large. This 
        increases query performance because it reduces the number of rows 
        that need to be scanned once all tables have been joined.
        
        The optimal order would be in decreasing frequency order for the 
        subcorpus specified by all source filters, but this is not 
        implemented yet. It may turn out that determining the subcorpus 
        frequency is too time-consuming after all. 
        
        Instead, the current implentation is a heuristic. It assumes that 
        a longer token string is more specific, and should therefore have
        precedence over a short token string. This may be true for normal
        queries, but queries that contain an OR selection the heuristic is
        probably suggesting suboptimal orders.
        
        The second criterion is the number of asterisks in the query string:
        a query string containing a '*' should be joined later than a query 
        string of the same length without '*'. 
        
        Parameters
        ----------
        token_list : list
            A list of token tuples, the first element stating the position of 
            the target output column, the second the token string
            
        Returns
        -------
        L : list
            A list of tuples. The first element contains the token number, 
            the second element contains the target output column
        """
        # FIXME: improve the heuristic.
        
        if len(token_list) == 1:
            return [(1, 1)]
        
        def calc_weight(s):
            """ 
            Calculates the weight of the query string s 
            """
            # word wildcards are strongly penalized:
            if s == "%":
                w = -9999
            else:
                w = len(s) * 2
            # character wildcards are penalized also, but take escaping 
            # into account:
            w = w - (s.count("_") - s.count("\\_"))
            return w
        
        sort_list = list(enumerate(token_list))
        # first, sort in reverse length:
        sort_list = sorted(sort_list, 
                           key=lambda x: calc_weight(x[1][1]), reverse=True)
        #return [x+1 for x, _ in sort_list]
        if options.cfg.align_quantified:
            L = []
            last_number = 0
            for x, (number, token) in sort_list:
                if number != last_number:
                    token_counter = number - 1
                    last_number = number
                else:
                    token_counter += 1
                L.append((x+1, token_counter + 1))
            return L
        else:
            return [(x+1, x+1) for x, _ in sort_list]

    def get_token_query_string_self_joined(self, token, number):
        """
        Return a MySQL SELECT string that queries one token in a query on an 
        n-gram corpus table.
        """
        
        # get a list of all tables that are required to satisfy the 
        # feature request:
        
        if number == 0:
            requested_features = [x for x in options.cfg.selected_features]
            
            # if a GUI is used, include source features so the entries in the
            # result table can be made clickable to show the context:
            if options.cfg.gui or options.cfg.context_left or options.cfg.context_right:
                # in order to make this not depend on a fixed database layout 
                # (here: 'source' and 'file' tables), we should check for any
                # table that corpus_table is linked to except for word_table
                # (and all child tables).            
                if "corpus_denorm_source_id" in dir(self.resource):
                    requested_features.append("corpus_denorm_source_id")
                    options.cfg.context_source_id = "corpus_denorm_source_id"
                elif "corpus_denorm_file_id" in dir(self.resource):
                    requested_features.append("corpus_denorm_file_id")
                    options.cfg.context_source_id = "corpus_denorm_file_id"
                else:
                    options.cfg.context_source_id = None
        else:
            corpus_variables = [x for x, _ in self.resource.get_corpus_features()]
            requested_features = [x for x in options.cfg.selected_features if not x in corpus_variables]

        
        lexicon_variables = [x for x, _ in self.resource.get_lexicon_features()]
        requested_features = [x for x in options.cfg.selected_features if x in lexicon_variables]
        
        requested_features.append("word_id")
        
        column_list = []
        for rc_feature in requested_features:
            column_list.append("{} AS coq_{}_{}".format(
                self.resource.__getattribute__(rc_feature),
                rc_feature, number + 1))

        where_clauses = []
        L = []
        word_label = self.resource.__getattribute__("word_label")
        for word in token.word_specifiers:
            current_token = tokens.COCAWord(word, self, replace=False, parse=False)
            current_token.negated = token.negated
            if not isinstance(current_token.S, unicode):
                S = unicode(current_token.S)
            else:
                S = current_token.S
            # take care of quotation marks:
            S = S.replace('"', '""')
            L.append('%s %s "%s"' % (word_label, self.resource.get_operator(current_token), S))
        if L:
            where_clauses.append("({})".format(" OR ".join(L)))

        L = []
        lemma_label = self.resource.__getattribute__("word_lemma")
        for lemma in token.lemma_specifiers:
            current_token = tokens.COCAWord(lemma, self, replace=False, parse=False)
            current_token.negated = token.negated
            if not isinstance(current_token.S, unicode):
                S = unicode(current_token.S)
            else:
                S = current_token.S
            # take care of quotation marks:
            S = S.replace('"', '""')
            L.append('%s %s "%s"' % (lemma_label, self.resource.get_operator(current_token), S))
        if L:
            where_clauses.append("({})".format(" OR ".join(L)))
            
        L = []
        pos_label = self.resource.__getattribute__("word_pos")
        for pos in token.class_specifiers:
            current_token = tokens.COCAWord(pos, self, replace=False, parse=False)
            current_token.negated = token.negated
            if not isinstance(current_token.S, unicode):
                S = unicode(current_token.S)
            else:
                S = current_token.S
            # take care of quotation marks:
            S = S.replace('"', '""')
            L.append('%s %s "%s"' % (pos_label, self.resource.get_operator(current_token), S))
        if L:
            where_clauses.append("({})".format(" OR ".join(L)))
        
        return """
        SELECT  {columns}
        FROM    {lexicon}
        WHERE   {constraints}
        """.format(
            columns=", ".join(column_list),
            lexicon=self.resource.__getattribute__("word_table"),
            constraints=" AND ".join(where_clauses))
        
    def sql_string_query_self_joined(self, Query, token_list):
        """ 
        Return a string that is sufficient to run the query on the
        MySQL database. 
        """

        # the next variable is set in get_token_query_string() to store the 
        # name of that resource feature which that keeps track of the source 
        # of the first token of the query. 
        # FIXME: Is this still really necessary?
        options.cfg.context_source_id = None
        token_query_list = {}

        corpus_features = [x for x, y in self.resource.get_corpus_features() if x in options.cfg.selected_features]
        lexicon_features = [x for x, y in self.resource.get_lexicon_features() if x in options.cfg.selected_features]
        
        print(corpus_features)
        
        for i, tup in enumerate(token_list):
            number, token = tup
            s = self.get_token_query_string_self_joined(tokens.COCAToken(token, self.lexicon), i)
            if s:
                join_string = "INNER JOIN ({s}) AS e{i}\nON coq_word_id_{i} = W{i}".format(
                    s = s, 
                    i=i+1)
                token_query_list[i+1] = join_string
        final_select = []

        # FIXME:
        # Not working: 
        # - align_quantified
        # - linked tables

        for rc_feature in self.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features:
                if rc_feature in lexicon_features:
                    for i in range(Query.Session.get_max_token_count()):
                        if i < len(token_list):
                            final_select.append("coq_{}_{}".format(rc_feature, i+1))
                        else:
                            final_select.append("NULL AS coq_{}_{}".format(rc_feature, i+1))
                elif rc_feature in corpus_features:
                    final_select.append("coq_{}_1".format(rc_feature))


        #for rc_feature in options.cfg.selected_features:
            #select_feature = "coq_{}_1".format(rc_feature)
            #if rc_feature in corpus_features or rc_feature in lexicon_features:
                #final_select.append(select_feature)
            #else:
                #final_select.append("NULL AS {}".format(select_feature))

        final_select.append("{} AS coquery_invisible_corpus_id".format(self.resource.__getattribute__("corpus_denorm_id")))

        # Add filters:
        # FIXME: What happens if the filter does not apply to something
        # in the ngram table, but to a linked table?
        where_string_list = []
        for filt in self.resource.translate_filters(self.resource.filter_list):
            variable, rc_feature, table_name, op, value_list, _value_range = filt
            if op.upper() == "LIKE":
                if "*" not in value_list[0]:
                    value_list[0] = "*{}*".format(value_list[0])
                value_list[0] = tokens.COCAToken.replace_wildcards(value_list[0])

            rc_table = "{}_table".format(rc_feature.partition("_")[0])
            s = '{} {} "{}"'.format(getattr(self.resource, rc_feature), op, value_list[0])
            where_string_list.append(s)
        return """
        SELECT  {}
        FROM    {}
        {}
        {}
        """.format(
            ", ".join(final_select),
            self.resource.corpus_denorm_table,
            "\n".join(token_query_list.values()),
            "WHERE {}".format(" AND ".join(where_string_list)) if where_string_list else "",
            )

    def sql_string_query(self, Query, token_list):
        """ 
        Return a string that is sufficient to run the query on the
        MySQL database. 
        """

        # the next variable is set in get_token_query_string() to store the 
        # name of that resource feature which that keeps track of the source 
        # of the first token of the query. 
        # FIXME: Is this still really necessary?
        options.cfg.context_source_id = None
        token_query_list = {}

        corpus_features = [(x, y) for x, y in self.resource.get_corpus_features() if x in options.cfg.selected_features]
        lexicon_features = [(x, y) for x, y in self.resource.get_lexicon_features() if x in options.cfg.selected_features]

        order = self.get_token_query_order(token_list)
        if not order:
            return
            
        referent_id, referent_column = order.pop(0)

        # get a partial query string for each token:
        last_offset = 0
        token_counter = None
        positions_lexical_items = []
        
        # column_number
        # sub_select_number
        last_pffset = None
        for i, tup in enumerate(token_list):
            offset, token = tup

            if options.cfg.align_quantified:
                if offset != last_offset:
                    token_count = 0
                    last_offset = offset
                column_number = offset + token_count - 1
                token_count += 1
            else:
                column_number = i

            positions_lexical_items.append(column_number)

            s = self.get_token_query_string(
                tokens.COCAToken(token, self.lexicon), 
                column_number)

            if i + 1 == referent_id:
                token_query_list[i+1] = s                
            elif i + 1 < referent_id:
                if s:
                    join_string = "INNER JOIN ({s}) AS e{num} ON coq_corpus_id_{ref_col} > {offset} AND coq_corpus_id_{col_number} = coq_corpus_id_{ref_col} - {offset}".format(
                        s=s, 
                        num=i+1, 
                        col_number=column_number + 1,
                        offset=referent_id - i - 1, 
                        ref_col=referent_column)
                    token_query_list[i+1] = join_string
            else:
                if s:
                    join_string = "INNER JOIN ({s}) AS e{num} ON coq_corpus_id_{col_number} = coq_corpus_id_{ref_col} + {offset}".format(
                        s = s,
                        num=i+1,
                        offset=i - referent_id + 1,
                        col_number=column_number + 1,
                        ref_col=referent_column)
                    token_query_list[i+1] = join_string
        query_string_part = [
            "SELECT COQ_OUTPUT_FIELDS FROM ({}) AS e{}".format(token_query_list.pop(referent_id), referent_id)]
        for referent_id, _ in order:
            query_string_part.append(token_query_list[referent_id])

        # change the order of the output column so that output columns 
        # showing the same lexicon feature for different tokens are grouped
        # together, followed by all corpus features.
        # The overall order is specified in resource.get_preferred_output_order()
        final_select = []        
        for rc_feature in self.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in lexicon_features]:
                    for i in range(Query.Session.get_max_token_count()):
                        if options.cfg.align_quantified:
                            last_offset = 0
                            if i in positions_lexical_items:
                                final_select.append("coq_{}_{}".format(rc_feature, i+1))
                            else:
                                final_select.append("NULL AS coq_{}_{}".format(rc_feature, i+1))
                        else:
                            if i < len(token_list):
                                final_select.append("coq_{}_{}".format(rc_feature, i+1))
                            else:
                                final_select.append("NULL AS coq_{}_{}".format(rc_feature, i+1))

        # add any external feature that is not a function:
        for linked in options.cfg.external_links:
            if linked.startswith("func."):
                continue

            external, internal = options.cfg.external_links[linked]
            internal_feature = internal.split(".")[-1]
            external_corpus, external_feature = linked.split(".")

            if self.resource.is_lexical(linked):
                for i in range(Query.Session.get_max_token_count()):
                    if options.cfg.align_quantified:
                        if i in positions_lexical_items:
                            final_select.append("coq_{}_{}_{}".format(external_corpus, external_feature, i+1))
                    else:
                        final_select.append("coq_{}_{}_{}".format(external_corpus, external_feature, i+1))
            else:
                final_select.append("coq_{}_{}_1".format(external_corpus, external_feature))


        # add the corpus features in the preferred order:
        for rc_feature in self.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in corpus_features]:
                    final_select.append("coq_{}_1".format(rc_feature))

        # Add any feature that is selected that is neither a corpus feature,
        # a lexicon feature nor a Coquery feature:
        for rc_feature in options.cfg.selected_features:
            if any([x == rc_feature for x, _ in self.resource.get_corpus_features()]):
                break
            if any([x == rc_feature for x, _ in self.resource.get_lexicon_features()]):
                break
            if not rc_feature.startswith("coquery_") and not rc_feature.startswith("frequency_"):
                if "." not in rc_feature:
                    final_select.append("coq_{}_1".format(rc_feature.replace(".", "_")))

        # add any resource feature that is required by a function:
        for res, fun, _ in options.cfg.selected_functions:
            # check if the function is applied to an external link:
            if res.count(".") > 1:
                rc_feature = "_".join(res.split(".")[1:])
            else:
                rc_feature = res.split(".")[-1]
            if rc_feature in [x for x, _ in self.resource.get_lexicon_features()]:
                final_select += ["coq_{}_{}".format(rc_feature, x + 1) for x in range(Query.Session.get_max_token_count())]
            else:
                final_select.append("coq_{}_1".format(rc_feature))

        # construct the query string from the token query parts:
        query_string = " ".join(query_string_part)

        if options.cfg.context_source_id or not final_select:
            final_select.append("coq_corpus_id_1 AS coquery_invisible_corpus_id")

        query_string = query_string.replace("COQ_OUTPUT_FIELDS", ", ".join(set(final_select)))
        
        # add LIMIT clause if necessary:
        if options.cfg.number_of_tokens:
            query_string = "{} LIMIT {}".format(
                query_string, options.cfg.number_of_tokens)

        # if verbose, add some line breaks and tabs to the query string so
        # that it is somewhat easier to read:
        if options.cfg.verbose:
            query_string = query_string.replace("INNER JOIN ", "\nINNER JOIN \n\t")
            query_string = query_string.replace("SELECT ", "SELECT \n\t")
            query_string = query_string.replace("FROM ", "\n\tFROM \n\t\t")
            query_string = query_string.replace("WHERE ", "\n\tWHERE \n\t\t")

        return query_string

    def sql_string_get_sentence_wordid(self,  source_id):
        return "SELECT {corpus_wordid} FROM {corpus} INNER JOIN {source} ON {corpus}.{corpus_source} = {source}.{source_id} WHERE {source}.{source_id} = {this_source}{verbose}".format(
            corpus_wordid=self.resource.corpus_word_id,
            corpus=self.resource.corpus_table,
            source=self.resource.source_table,
            corpus_source=self.resource.corpus_source_id,
            source_id=self.resource.source_id,
            corpus_token=self.resource.corpus_id,
            this_source=source_id,
            verbose=" -- sql_string_get_sentence_wordid" if options.cfg.verbose else "")

    def sql_string_get_wordid_in_range(self, start, end, source_id):
        if options.cfg.context_source_id and source_id:
            return "SELECT {corpus_wordid} from {corpus} WHERE {token_id} BETWEEN {start} AND {end} AND {corpus_source} = {this_source}".format(
                corpus_wordid=self.resource.corpus_word_id,
                corpus=self.resource.corpus_table,
                token_id=self.resource.corpus_id,
                start=start, end=end,
                corpus_source=self.resource.__getattribute__(options.cfg.context_source_id),
                this_source=source_id)
        else:
            # if no source id is specified, simply return the tokens in
            # the corpus that are within the specified range.
            return "SELECT {corpus_wordid} FROM {corpus} WHERE {corpus_token} BETWEEN {start} AND {end} {verbose}".format(
                corpus_wordid=self.resource.corpus_word_id,
                corpus=self.resource.corpus_table,
                corpus_token=self.resource.corpus_id,
                start=start, end=end,
                verbose=" -- sql_string_get_wordid_in_range" if options.cfg.verbose else "")

    def get_tag_translate(self, s):
        # Define some TEI tags:
        tag_translate = {
            "head": "h1",
            "list": "ul",
            "item": "li",
            "div": "div",
            "label": "li",
            "pb": "div type='page_break'",
            "p": "p"}
        try:
            return tag_translate[s]
        except AttributeError:
            return s

    def tag_to_html(self, tag, attributes={}):
        """ Translate a tag to a corresponding HTML/QHTML tag by checking 
        the tag_translate dictionary."""
        try:
            if tag == "hi":
                if attributes.get("rend") == "it":
                    return "i"
            if tag == "head":
                if attributes.get("type") == "MAIN":
                    return "h1"
                if attributes.get("type") == "SUB":
                    return "h2"
                if attributes.get("type") == "BYLINE":
                    return "h3"
            return self.get_tag_translate(tag)
        except KeyError:
            warnings.warn("unsupported tag: {}".format(tag))
            print("unsupported tag: {}".format(tag))
            return None

    def renderer_open_element(self, tag, attributes):
        label = self.tag_to_html(tag, attributes)
        if label:
            if attributes:
                return ["<{} {}>".format(
                    label, 
                    ", ".join(["{}='{}'".format(x, attributes[x]) for x in attributes]))]
            else:
                return ["<{}>".format(label)]
        else:
            return []
        
    def renderer_close_element(self, tag, attributes):
        label = self.tag_to_html(tag, attributes)
        if label:
            if attributes:
                return ["</{} {}>".format(
                    label, 
                    ", ".join(["{}='{}'".format(x, attributes[x]) for x in attributes]))]
            else:
                return ["</{}>".format(label)]
        else:
            return []

    def render_context(self, token_id, source_id, token_width, context_width, widget):
        """ Return a visual representation of the context around the 
        specified token. The result is shown in an instance of the 
        ContextView class.
        
        The most simple visual representation of the context is a plain text
        display, but in principle, a corpus might implement a more elaborate
        renderer. For example, a corpus may contain information about the
        page layout, and the renderer could use that information to create a
        facsimile of the original page.
        
        The renderer can interact with the widget in which the context will
        be displayed. The area in which the context is shown is a QLabel
        named widget.ui.context_area. """

        tab = options.cfg.main_window.Session.data_table

        # create a list of all token ids that are also listed in the results
        # table:
        id_list = []
        #tab = tab[tab.coquery_invisible_origin_id == source_id]
        #tab["end"] = tab.apply(
            #lambda x: x["coquery_invisible_corpus_id"] + x["coquery_invisible_number_of_tokens"],
            #axis=1)
        #for x in tab.index:
            #id_list += [y for y in range(
                #int(tab.loc[x].coquery_invisible_corpus_id), 
                #int(tab.loc[x].end))]

        start = max(0, token_id - context_width)
        end = token_id + token_width + context_width - 1
            
        origin_id = ""
        try:
            origin_id = self.resource.corpus_source_id
        except AttributeError:
            try:
                origin_id = self.resource.corpus_file_id
            except AttributeError:
                origin_id = self.resource.corpus_sentence_id

        if "tag_table" in dir(self.resource):
            format_string = "SELECT {corpus}.{corpus_id}, {word}, {tag}, {tag_table}.{tag_type}, {attribute}, {tag_id} FROM {corpus} INNER JOIN {word_table} ON {corpus}.{corpus_word_id} = {word_table}.{word_id} LEFT JOIN {tag_table} ON {corpus}.{corpus_id} = {tag_table}.{tag_corpus_id} WHERE {corpus}.{corpus_id} BETWEEN {start} AND {end}"
        else:
            format_string = "SELECT {corpus}.{corpus_id}, {word} FROM {corpus} INNER JOIN {word_table} ON {corpus}.{corpus_word_id} = {word_table}.{word_id} WHERE {corpus}.{corpus_id} BETWEEN {start} AND {end}"
            
        if origin_id:
            format_string += " AND {corpus}.{source_id} = {current_source_id}"
    
        if "tag_table" in dir(self.resource):
        
            S = format_string.format(
                corpus=self.resource.corpus_table,
                corpus_id=self.resource.corpus_id,
                corpus_word_id=self.resource.corpus_word_id,
                source_id=origin_id,
                
                word=self.resource.word_label,
                word_table=self.resource.word_table,
                word_id=self.resource.word_id,
                
                tag_table=self.resource.tag_table,
                tag=self.resource.tag_label,
                tag_id=self.resource.tag_id,
                tag_corpus_id=self.resource.tag_corpus_id,
                tag_type=self.resource.tag_type,
                attribute=self.resource.tag_attribute,
                
                current_source_id=source_id,
                start=start, end=end)
        else:
            S = format_string.format(
                corpus=self.resource.corpus_table,
                corpus_id=self.resource.corpus_id,
                corpus_word_id=self.resource.corpus_word_id,
                source_id=origin_id,
                
                word=self.resource.word_label,
                word_table=self.resource.word_table,
                word_id=self.resource.word_id,
                
                current_source_id=source_id,
                start=start, end=end)

        cur = self.resource.DB.execute_cursor(S)
        entities = {}

        for row in cur:
            if row[self.resource.corpus_id] not in entities:
                entities[row[self.resource.corpus_id]] = []
            entities[row[self.resource.corpus_id]].append(row)

        context = deque()
        # we need to keep track of any opening and closing tag that does not
        # have its matching tag in the selected context:
        opened_elements = []
        closed_elements = []
        
        for context_token_id in sorted(entities):
            print()
            print("TOKEN ", context_token_id)
            print()
            opening_elements = []
            closing_elements = []
            word = ""
   
            if "tag_id" in dir(self.resource):
                # create lists of opening and closing elements, and get the 
                # current word:
                for x in sorted(entities[context_token_id],
                            key=lambda x:x[self.resource.tag_id]):
                    tag_type = x[self.resource.tag_type]
                    if tag_type:
                        if tag_type in ("open", "empty"):
                            opening_elements.append(x)
                        if tag_type in ("close", "empty"):
                            closing_elements.append(x)
            word = entities[context_token_id][0][self.resource.word_label]
            
            if opening_elements:
                print("OPENING")
                print("\t", opening_elements)
                print()
            if closing_elements:
                print("CLOSING")
                print("\t", closing_elements)
                print()
                
            print("WORD", word)
            
            # process all opening elements:
            for element in opening_elements:
                tag = element[self.resource.tag_label]
                attr = element[self.resource.tag_attribute]
                if attr:
                    try:
                        attributes = dict([x.split("=") for x in attr.split(",")])
                    except ValueError:
                        attributes = dict([attr.split("=")])
                else: 
                    attributes = {}
                open_element = self.renderer_open_element(tag, attributes)
                if open_element:
                    context += open_element
                    opened_elements.append(tag)
                
            if word:
                # process the context word:
                
                # highlight words that are in the results table:
                if context_token_id in id_list:
                    context.append("<span style='{}'; >".format(self.resource.render_token_style))
                # additional highlight if the word is the target word:
                if token_id <= context_token_id < token_id + token_width:
                    context.append("<b>")
                context.append(word)
                if token_id <= context_token_id < token_id + token_width:
                    context.append("</b>")
                if context_token_id in id_list:
                    context.append("</span>")
            
            # process all closing elements:
            for element in closing_elements:
                tag = element[self.resource.tag_label]
                attr = element[self.resource.tag_attribute]
                if attr:
                    try:
                        attributes = dict([x.split("=") for x in attr.split(",")])
                    except ValueError:
                        attributes = dict([attr.split("=")])
                else: 
                    attributes = {}
                    
                close_element = self.renderer_close_element(tag, attributes)
                if close_element:
                    context += close_element
                    # remove the opening element if the current element closes it:
                    if opened_elements and tag == opened_elements[-1]:
                        opened_elements.pop()
                    else:
                        # otherwise, keep track of unmatched closing elements:
                        closed_elements.append(tag)

        # for all unmatchend opened elements, add a matching closing one:
        for tag in opened_elements[::-1]:
            if tag:
                context.append("</{}>".format(self.tag_to_html(tag)))
                
        # for all unmatchend closing elements, add a matching opening one:
        for tag in closed_elements:
            if tag:
                context.appendleft("<{}>".format(self.tag_to_html(tag)))

        widget.ui.context_area.setText(collapse_words(context))

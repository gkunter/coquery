# -*- coding: utf-8 -*-
"""
corpus.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import warnings
from collections import *

try:
    import sqlalchemy
    import pandas as pd
    import numpy as np
except ImportError:
    # Missing dependencies are handled in check_system() from coquery.py,
    # so we can pass any ImportError here.
    pass

from .errors import *
from .defines import *
from .general import *
from . import tokens
from . import options
from . import sqlhelper
from .links import get_by_hash
from .filters import QueryFilter

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

class LexiconClass(object):
    """
    Define a base lexicon class.
    """

    def check_pos_list(self, L):
        """ Returns the number of elements for which 
        Corpus.is_part_of_speech() is True, i.e. the number of
        elements that are considered a part of speech tag """
        count = 0
        for CurrentPos in L:
            if self.is_part_of_speech(CurrentPos):
                count += 1
        return count
                                                            
    def sql_string_get_posid_list_where(self, token):
        comparing_operator = self.resource.get_operator(token)
        where_clauses = []
        target = self.resource.get_field(getattr(self.resource, QUERY_ITEM_POS))
        for current_pos in token.class_specifiers:
            S = '{} {} "{}"'.format(target, comparing_operator, current_pos)
            where_clauses.append (S)
        return "(%s)" % "OR ".join (where_clauses)
    
    def sql_string_is_part_of_speech(self, pos):
        current_token = tokens.COCAToken(pos, self, parse=True, replace=False)
        rc_feature = getattr(self.resource, QUERY_ITEM_POS)
        _, _, table, _ = self.resource.split_resource_feature(rc_feature)
        S = "SELECT {} FROM {} WHERE {} {} '{}' LIMIT 1".format(
            getattr(self.resource, "{}_id".format(table)),
            getattr(self.resource, "{}_table".format(table)),
            getattr(self.resource, rc_feature),
            self.resource.get_operator(current_token),
            pos.replace("'", "''"))
        return S

    def is_part_of_speech(self, pos):
        if hasattr(self.resource, QUERY_ITEM_POS):
            S = self.sql_string_is_part_of_speech(pos)
            df = pd.read_sql(S.replace("%", "%%"), self.resource.get_engine())
            return len(df.index) > 0
        else:
            return False
    
    def sql_string_get_posid_list(self, token):
        word_feature = getattr(self.resource, QUERY_ITEM_WORD)
        _, _, w_table, _ = self.resource.split_resource_feature(word_feature)
        word_table = getattr(self.resource, "{}_table".format(w_table))
        word_id = getattr(self.resource, "{}_id".format(w_table))
    
        pos_feature = getattr(self.resource, QUERY_ITEM_POS)
        pos_field = getattr(self.resource, pos_feature)
        _, _, p_table, _ = self.resource.split_resource_feature(pos_feature)
        pos_table = getattr(self.resource, "{}_table".format(p_table))
        pos_id = getattr(self.resource, "{}_id".format(p_table))
        
        self.table_list = [word_table]
        
        if p_table != w_table:
            self.joined_tables = [word_table]
            self.add_table_path(word_feature, pos_feature)
            where_string = self.sql_string_get_wordid_list_where(token)
        else:
            where_string = self.sql_string_get_posid_list_where(token)
        return "SELECT DISTINCT {}.{} FROM {} WHERE {}".format(
            pos_table, pos_field, " ".join(self.table_list), where_string)

    def get_posid_list(self, token):
        """ Return a list of all PosIds that match the query token. """
        S = self.sql_string_get_posid_list(token)
        df = pd.read_sql(S.replace("%", "%%"), self.resource.get_engine())
        return set(list(df.ix[:,0]))

    def sql_string_get_wordid_list_where(self, token):
        """ 
        Return an SQL string that contains the WHERE conditions matching the 
        token.
        
        Returns
        -------
        S : str 
            A string that can be used in an SQL query created in 
            get_wordid_list().
        """
        where_clauses = []
        for spec_list, label in [(token.word_specifiers, QUERY_ITEM_WORD),
                                (token.lemma_specifiers, QUERY_ITEM_LEMMA),
                                (token.class_specifiers, QUERY_ITEM_POS),
                                (token.transcript_specifiers, QUERY_ITEM_TRANSCRIPT),
                                (token.gloss_specifiers, QUERY_ITEM_GLOSS)]:
            sub_clauses = []
            rc_feature = getattr(self.resource, label, "")
            if spec_list:
                target = self.resource.get_field(rc_feature)
                for spec in spec_list:
                    if spec != "%":
                        dummy = tokens.COCAToken(spec, self, replace=False, parse=False)
                        dummy.negated = token.negated
                        S = dummy.S
                        # For the construction of the query string, 
                        # any escaped wildcard-like string is replaced 
                        # by the unescaped equivalent. This fixes 
                        # Issue #175.
                        if not dummy.has_wildcards(S):
                            S = S.replace("\\_", "_")
                            S = S.replace("\\%", "%")
                        S = S.replace("'", "''")
                        format_string = "{} {} '{}'"
                        if options.cfg.query_case_sensitive:
                            if self.resource.db_type == SQL_SQLITE:
                                format_string = "{} COLLATE BINARY".format(format_string)
                            elif self.resource.db_type == SQL_MYSQL:
                                format_string = "BINARY {} {} '{}'"
                                
                        sub_clauses.append(format_string.format(
                            target, self.resource.get_operator(dummy), S))
            if sub_clauses:
                where_clauses.append("({})".format(" OR ".join(sub_clauses)))
        S = " AND ".join(where_clauses)
        return S
            
    def add_table_path(self, start_feature, end_feature):
        """
        Add the join string  needed to access end_feature from the table 
        containing start_feature.
        
        This method modifies the class attributes joined_tables (to keep
        track of tables that are already included in the join) and 
        table_list (which contains the join strings).
        """
        # FIXME: treat features from linked tables like native features
        _, _, last_table, _ = self.resource.split_resource_feature(start_feature)
        _, _, end_table, _ = self.resource.split_resource_feature(end_feature)

        table_path = self.resource.get_table_path(last_table, end_table)
        for table in table_path[1:]:
            if table not in self.joined_tables:
                self.table_list.append("LEFT JOIN {table} ON {table}.{table_id} = {prev_table}.{prev_table_id}".format(
                    table=getattr(self.resource, "{}_table".format(table)),
                    table_id=getattr(self.resource, "{}_id".format(table)),
                    prev_table=getattr(self.resource, "{}_table".format(last_table)),
                    prev_table_id=getattr(self.resource, "{}_{}_id".format(last_table, table))))
                self.joined_tables.append(table)
            last_table = table

    def sql_string_get_matching_wordids(self, token):
        """ returns a string that may be used to query all word_ids that
        match the token specification."""       
        
        word_feature = getattr(self.resource, QUERY_ITEM_WORD)
        _, _, table, _ = self.resource.split_resource_feature(word_feature)
        word_table = getattr(self.resource, "{}_table".format(table))
        word_id = getattr(self.resource, "{}_id".format(table))
        
        if hasattr(self.resource, "word_table"):
            start_table = self.resource.word_table
        else:
            start_table = self.resource.corpus_table
        
        self.joined_tables = []
        self.table_list = [start_table]
        
        if word_table != start_table:
            # this happens if there is a meta table between corpus and 
            # lexicon, e.g. in the Buckeye corpus:
            self.add_table_path("word_id", getattr(self.resource, QUERY_ITEM_WORD))
            _, _, table, _ = self.resource.split_resource_feature("word_id")
            word_table = getattr(self.resource, "{}_table".format(table))
            word_id = getattr(self.resource, "{}_id".format(table))            
        
        if token.lemma_specifiers:
            self.add_table_path(word_feature, getattr(self.resource, QUERY_ITEM_LEMMA))

        if token.class_specifiers:
            self.add_table_path(word_feature, getattr(self.resource, QUERY_ITEM_POS))

        if token.transcript_specifiers:
            self.add_table_path(word_feature, getattr(self.resource, QUERY_ITEM_TRANSCRIPT))

        if token.gloss_specifiers:
            self.add_table_path(word_feature, getattr(self.resource, QUERY_ITEM_GLOSS))
            
        where_string = self.sql_string_get_wordid_list_where(token)
        S = "SELECT {}.{} FROM {} WHERE {}".format(
                word_table, word_id, " ".join(self.table_list), where_string)
        return S

    def sql_string_get_lemmatized_wordids(self, token):
        """ 
        Return an SQL string that may be used to gather all word ids which 
        match the token while using auto-lemmatization.
        
        Auto-lemmatization means that first, the lemmas matching the token 
        specifications are looked up, and then, all word ids linked to these 
        lemmas are determined.
        """
        
        # How to do that:
        #
        # - first, get a normal list of matching word ids 
        # - second, get the list of lemmas for these word ids 
        # - third, get a list of all word ids that have these lemmas
        
        # if the query string already contains a lemma specification, 
        # lemmatization is ignored:
        if not hasattr(self.resource, QUERY_ITEM_LEMMA):
            raise UnsupportedQueryItemError("Lemmatization by \"#\" flag")
        
        if token.lemma_specifiers:
            return self.sql_string_get_matching_wordids(token)
        
        # first, get a list of word ids that match the token:
        L = self.get_matching_wordids(token)
        
        # next, create a table path from the word table to the lemma table 
        word_feature = getattr(self.resource, QUERY_ITEM_WORD)
        _, _, table, _ = self.resource.split_resource_feature(word_feature)
        word_table = getattr(self.resource, "{}_table".format(table))
        word_id = getattr(self.resource, "{}_id".format(table))

        lemma_feature = getattr(self.resource, QUERY_ITEM_LEMMA)
        _, _, table, _ = self.resource.split_resource_feature(lemma_feature)
        lemma_table = getattr(self.resource, "{}_table".format(table))
        lemma_id = getattr(self.resource, "{}_id".format(table))
        
        self.joined_tables = [word_table]
        self.table_list = [word_table]
        
        self.add_table_path(word_feature, getattr(self.resource, QUERY_ITEM_LEMMA))

        where_string = "{}.{} IN ({})".format(word_table, word_id, ", ".join(["{}".format(x) for x in L]))

        # using the path, get a list of all lemma labels that belong to 
        # the word ids from the list:
        S = "SELECT {}.{} FROM {} WHERE {}".format(
                lemma_table, 
                getattr(self.resource, lemma_feature), " ".join(self.table_list), where_string)
        
        engine = self.resource.get_engine()
        df = pd.read_sql(S, engine, columns=["Lemma"]).drop_duplicates()
        engine.dispose()
        # construct a new token that uses the list of lemmas as its token 
        # specification:
        token = tokens.COCAToken("[{}]".format("|".join(list(df[getattr(self.resource, lemma_feature)]))), lexicon=self)
        # return the SQL string for the new token:
        return self.sql_string_get_matching_wordids(token)

    def get_lemmatized_wordids(self, token, stopwords=True):
        """
        Return a list of all word ids that belong to the same lemmas as the 
        word ids matched by the token.
        """
        if token.S == "%" or token.S == "":
            return []
        
        S = self.sql_string_get_lemmatized_wordids(token)
        engine = self.resource.get_engine()
        df = pd.read_sql(S.replace("%", "%%"), engine)
        engine.dispose()
        if not len(df.index):
            if token.negated:
                return []
            else:
                raise WordNotInLexiconError
        else:
            if stopwords:
                return [x for x in list(df.ix[:,0]) if not x in stopword_ids]
            else:
                return list(df.ix[:,0])
        
    def get_matching_wordids(self, token, stopwords=True):
        """
        Return a list of word ids that match the tokens. This takes the 
        entries from the stopword list into account.
        """
        if token.S == "%" or token.S == "":
            return []
        S = self.sql_string_get_matching_wordids(token)
        df = pd.read_sql(S.replace("%", "%%"), self.resource.get_engine())
        if not len(df.index):
            if token.negated:
                return []
            else:
                raise WordNotInLexiconError
        else:
            x = list(df.ix[:,0])
            return x
        
class BaseResource(object):
    """
    """
    # add internal table that can be used to access frequency information:
    coquery_query_string = "Query string"
    coquery_expanded_query_string = "Expanded query string"
    #coquery_query_file = "Input file"
    #coquery_current_date = "Current date"
    #coquery_current_time = "Current time"
    coquery_query_token = "Query item"

    special_table_list = ["coquery", "tag"]

    render_token_style = "background: lightyellow"
    
    @classmethod
    def format_resource_feature(cls, rc_feature, N):
        """
        Return a list of formatted feature labels as they occur in the query
        table as headers.
        
        All labels start with the prefix 'coq_' and end with a number. For 
        lexicon features, the numbers range from 1 to N. For other features, 
        the number is always 1.
        
        Special resource features, i.e. those that belong to one of the tables
        in the 'special_table_list' class attribute, are returned as they are.
        
        Parameters
        ----------
        rc_feature : str 
            The name of the resource feature
        N : int 
            The maximum number of query items
            
        Returns:
        --------
        l : list
            A list of header labels. 
        """
        # special case for "coquery_query_token", which receives numbers like
        # a query item resource:
        if rc_feature == "coquery_query_token": 
            return ["coquery_query_token_{}".format(x + 1) for x in range(N)]

        # handle resources from one of the special tables:
        if rc_feature.startswith(tuple(cls.special_table_list)):
            return [rc_feature]

        # handle external links by delegating the formatting to the external
        # resource:
        _, hashed, table, feature = cls.split_resource_feature(rc_feature)
        if hashed != None:
            link, res = get_by_hash(hashed)
            l = res.format_resource_feature("{}_{}".format(table, feature), N)
            return ["db_{}_{}".format(res.db_name, x) for x in l]
        
        # handle lexicon features:
        lexicon_features = [x for x, _ in cls.get_lexicon_features()]
        if rc_feature in lexicon_features or cls.is_tokenized(rc_feature):
            return ["coq_{}_{}".format(rc_feature, x+1) for x in range(N)]
        # handle remaining features
        else:
            return ["coq_{}_1".format(rc_feature)]

    @classmethod
    def split_resource_feature(cls, rc_feature):
        """
        Split a resource feature into a tuple containing the prefix, the 
        table name, and the resource feature display name.
        
        Parameters:
        -----------
        rc_feature : str
            The name of the resource feature
            
        Returns:
        --------
        tup : tuple
            A tuple consisting of a boolean specificing whether it is a 
            function, the hashed of the link (or None), the resource table 
            name, and the feature name
        """
        is_function = rc_feature.startswith("func.")
        if is_function:
            _, _, s = rc_feature.partition(".")
        else:
            s = rc_feature
        if "." in s:
            hashed, _, s= s.partition(".")
        else:
            hashed = None
        table, _, feature = s.partition("_")
        if not table or not feature:
            raise ValueError("either no table or no feature: {}".format(rc_feature))
        
        return (is_function, hashed, table, feature)

    @classmethod
    def get_preferred_output_order(cls):
        all_features = cls.get_resource_features()
        order = []
        for rc_feature in list(all_features):
            if rc_feature in PREFERRED_ORDER:
                for i, ordered_feature in enumerate(order):
                    if PREFERRED_ORDER.index(ordered_feature) > PREFERRED_ORDER.index(rc_feature):
                        order.insert(i, rc_feature)
                        break
                else:
                    order.append(rc_feature)
                all_features.remove(rc_feature)
        
        # make sure that if there is timing information, the ending time 
        # occurs after the start time by default (fixes Issue #177):
        for i, rc_feature in enumerate(order):
            _, _, tab, feat = cls.split_resource_feature(rc_feature)
            if feat == "starttime":
                j = order.index("{}_starttime".format(tab))
                if j < i:
                    order[j] = "{}_starttime".format(tab)
                    order[i] = "{}_endtime".format(tab)

        for i, rc_feature in enumerate(all_features):
            _, _, tab, feat = cls.split_resource_feature(rc_feature)
            if feat == "starttime":
                j = all_features.index("{}_endtime".format(tab))
                if j < i:
                    all_features[j] = "{}_starttime".format(tab)
                    all_features[i] = "{}_endtime".format(tab)

        return order + all_features
    
    @classmethod
    def get_resource_features(cls):
        """
        Return a list of all resource feature names.
        
        A resource feature is a class attribute that either contains the 
        display name of a resource table or of a resource table variable.
        Resource table features take the form TABLENAME_table, where 
        TABLENAME is the resource name of the table. Resource features 
        take the form TABLENAME_COLUMNNAME, where COLUMNNAME is the 
        resource name of the column.
        
        Returns
        -------
        l : list 
            List of strings containing the resource feature names
        """
        # create a list with all split resources:
        split_features = [cls.split_resource_feature(x) for x in dir(cls) if "_" in x and not x.startswith("_")]

        # create a list of table names from the resource features:
        tables = [table for _, _, table, feature in split_features if feature == "table"]
        # add special tables:
        tables += cls.special_table_list
        
        # return the features that can be constructed from the feature name 
        # and the table:
        return ["{}_{}".format(table, feature) for _, _, table, feature in split_features if table in tables]

    @classmethod
    def get_table_dict(cls):
        """ Return a dictionary with the table names specified in this
        resource as keys. The values of the dictionary are the table 
        columns. """
        table_dict = defaultdict(set)
        for x in cls.get_resource_features():
            table, _, _ = x.partition("_")
            table_dict[table].add(x)
        #for x in list(table_dict.keys()):
            #if x not in cls.special_table_list and not "{}_table".format(x) in table_dict[x]:
                #table_dict.pop(x)
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
        """ 
        Return a list of table names that constitute a link chain from
        table 'start' to 'end', including these two tables. Return None if 
        no path was found, i.e. if table 'end' is not linked to 'start'. 
        
        Parameters
        ----------
        start : string
            A resource feature name, indicating the starting point of the 
            search
        end : string
            A resource feature name, indicating the end point of the search
        
        Returns
        -------
        l : list or None
            A list of the resource table names that lead from resource 
            feature 'start' to resource feature'end'. The list contains 
            start and end as the first and the last element if such a path
            exists. If no path exists, the method returns None.
        """
        table_dict = cls.get_table_dict()
        if "{}_id".format(end) in table_dict[start]:
            return [end]
        for rc_feature in table_dict[start]:
            try:
                from_table, to_table, id_spec = rc_feature.split("_")
            except ValueError:
                # this resource feature is not a linking feature
                continue
            else:
                # this is a linking feature, so descend into the 
                # table:
                descend = cls.get_table_path(to_table, end)
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
        """
        D = {}
        D["parent"] = None
        rc_tab = rc_table.split("_")[0]
        
        available_features = []
        requested_features = []
        children = []
        for rc_feature in cls.get_resource_features():
            if rc_feature.endswith("_{}_id".format(rc_tab)) and not rc_feature.startswith(rc_tab):
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
        return D

    @classmethod
    def get_feature_from_name(cls, name):
        """
        Get all resource features that match the given display name.
        
        Parameters
        ----------
        name : str 
            The display name for which to search 
            
        Returns
        -------
        l : list 
            A list of strings, each representing a resource feature that has 
            the same display name as 'name'.
        """
        return [x for x in cls.get_resource_features() if getattr(cls, x) == name]
    
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

    #@classmethod
    #def get_requested_features(cls, tree_structure):
        #requested_features = tree_structure["rc_requested_features"]
        #for child in tree_structure["children"]:
            #requested_features += cls.get_requested_features(child)
        #return requested_features

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
                    if y == "corpus_id":
                        corpus_variables.append((y, cls.corpus_id))    
                    elif not y.endswith("_id") and not y.startswith("{}_table".format(x)):
                        corpus_variables.append((y, getattr(cls, y)))
        return corpus_variables
    
    @classmethod
    def get_lexicon_features(cls):
        """ Return a list of tuples. Each tuple consists of a resource 
        variable name and the display name of that variable. Only those 
        variables are returned that all resource variable names that are 
        desendants of table 'word'. """
        table_dict = cls.get_table_dict()
        table = "word"
        #try:
            #_, _, table, _ = cls.split_resource_feature(getattr(cls, QUERY_ITEM_WORD))
        #except AttributeError:
            #return []
        #if table == "corpus":
            #return []
        lexicon_tables = cls.get_table_tree(table)
        lexicon_variables = []
        for x in table_dict:
            if x in lexicon_tables and x not in cls.special_table_list:
                for y in table_dict[x]:
                    if not y.endswith("_id") and not y.startswith("{}_table".format(x)):
                        lexicon_variables.append((y, getattr(cls, y)))    
        return lexicon_variables
    
    @staticmethod
    def get_feature_from_function(func):
        if func.count(".") > 1:
            return "_".join(func.split(".")[1:])
        else:
            return func.split(".")[-1]

    @classmethod
    def get_field(cls, rc_feature):
        """
        Get a full SQL field name for the resource feature.
        """
        _, _, table, _ = cls.split_resource_feature(rc_feature)
        return "{}.{}".format(
            getattr(cls, "{}_table".format(table)), getattr(cls, rc_feature))

    @classmethod
    def get_referent_feature(cls, rc_feature):
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

        func, hashed, table, feature = cls.split_resource_feature(rc_feature)

        # Check if the feature has the same database as the current 
        # resource, i.e. check if the feature is NOT from a linked table:
        if hashed == None:
            return "{}_{}".format(table, feature)
        else:
            link, res = get_by_hash(hashed)
            _, _, tab, feat = res.split_resource_feature(link.rc_from)
            return "{}_{}".format(tab, feat)

    @classmethod
    def is_lexical(cls, rc_feature):
        lexicon_features = [x for x, _ in cls.get_lexicon_features()]
        resource = cls.get_referent_feature(rc_feature)
        return resource in lexicon_features
    
    @classmethod
    def is_tokenized(cls, rc_feature):
        """
        Tokenized features are features that contain token-specific 
        data. In an output table, they should occur numbered for each 
        query item. 
        
        Unlike lexical features, they are not descendants of word_table,
        but are directly stored in the corpus table.
        """
        return (rc_feature == "corpus_id") or (
                rc_feature.startswith("corpus_") and not rc_feature.endswith("_id"))
    
    @classmethod
    def translate_filters(cls, filters):
        """ Return a translation list that contains the corpus feature names
        of the variables used in the filter texts. """
        print("translate_filters")
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
                table = str("{}_table".format(column_name.partition("_")[0]))
                table_name = getattr(cls, table)
                filter_list.append((variable, column_name, table_name, filt._op, filt._value_list, filt._value_range))
        return filter_list
    
    @classmethod
    def get_query_item_map(cls):
        """
        Return the mapping of query item types to resource features for the 
        resource.
        
        Returns
        -------
        d : dict 
            A dictionary with the query item type constants from defines.py as 
            keys and the resource feature that this query item type is mapped 
            to as values. Query item types that are not supported by the 
            resource will have no key in this dictionary.
        """
        item_map = {}
        for x in (QUERY_ITEM_WORD, QUERY_ITEM_LEMMA, QUERY_ITEM_POS,
                  QUERY_ITEM_TRANSCRIPT, QUERY_ITEM_GLOSS):
            if hasattr(cls, x):
                item_map[x] = getattr(cls, x)
        return item_map

class SQLResource(BaseResource):
    _get_orth_str = None
    
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
        self._word_cache = {}
        self.lexicon = lexicon
        self.corpus = corpus
        _, _, self.db_type, _, _ = options.get_con_configuration()

        # FIXME: in order to make this not depend on a fixed database layout 
        # (here: 'source' and 'file' tables), we should check # for any table 
        # that corpus_table is linked to except for # word_table (and all 
        # child tables).
        # FIXME: some mechanism is probably necessary to handle self-joined 
        # tables
        
        for x in ["corpus_source_id", "corpus_file_id", "corpus_sentence_id", "corpus_id"]:
            if hasattr(self, x):
                options.cfg.token_origin_id = x
                break
            
    @classmethod
    def get_engine(cls, *args, **kwargs):
        return sqlalchemy.create_engine(
            sqlhelper.sql_url(options.cfg.current_server, cls.db_name),
            *args, **kwargs)

    def get_statistics(self):
        stats = []
        # determine table size for all columns
        table_sizes = {}
        engine = self.get_engine()
        for rc_table in [x for x in dir(self) if not x.startswith("_") and x.endswith("_table") and not x.startswith("tag_")]:
            table = getattr(self, rc_table)
            S = "SELECT COUNT(*) FROM {}".format(table)
            df = pd.read_sql(S, engine)
            table_sizes[table] = df.values.ravel()[0]

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
                #S = "SELECT COUNT(DISTINCT {}) FROM {}".format(column, table)
                #df = pd.read_sql(S, engine)
                S = "SELECT {} FROM {}".format(column, table)
                df = pd.read_sql(S, engine)
                stats.append([table, column, table_sizes[table], len(df[column].unique()), 0, 0, rc_feature])
        
        df = pd.DataFrame(stats)

        # calculate ratio:
        df[4] = df[3] / df[2]
        df[5] = df[2] / df[3]
        
        try:
            df.sort_values(by=list(df.columns)[:2], inplace=True)
        except AttributeError:
            df.sort(columns=list(df.columns)[:2], inplace=True)
        
        return df
    
    def get_query_string(self, Query, token_list, to_file=False):
        """
        Get a query string that can be used to retrieve the query matches.

        If any of the tokens does not match any word in the current lexicon,
        an empty query string is returned.
        
        Parameters
        ----------
        query : TokenQuery
            An TokenQuery instance that specifies the current query.
        token_list : list 
            A list of Tokens
        to_file : bool
            True if the query results are directly written to a file, and 
            False if they will be displayed in the GUI. Data that is written
            directly to a file contains less information, e.g. it doesn't 
            contain an origin ID or a corpus ID (unless requested).
            
        Returns
        -------
        query_string : str 
            A string that can be executed by an SQL engine.
        """
        try:
            # if there is a lookup ngram table, and if the length of the 
            # query string does not exceed that table, use it for the 
            # query
            if (hasattr(self, "corpusngram_table") and  
                1 < len(token_list) <= self.corpusngram_width) and options.cfg.experimental:
                    query_string = self.corpus.sql_string_query_lookup(Query, token_list)
            else:
                # otherwise, use the self-joined corpus table:
                query_string = self.corpus.sql_string_query(Query, token_list, to_file)
                #l = self.corpus.get_required_features(Query, token_list)
                #if options.cfg.verbose:
                    #print(l)
        except WordNotInLexiconError:
            query_string = ""
            
        Query.Session.output_order = self.get_select_list(Query)
        return query_string

    def get_context(self, token_id, origin_id, number_of_tokens, db_connection):
        def get_orth(word_id):
            """ 
            Return the orthographic forms of the word_ids.
            
            If word_id is not a list, it is converted into one.
            
            Parameters
            ----------
            word_id : list
                A list of values designating the words_ids that are to 
                be looked up.
                
            Returns
            -------
            L : list
                A list of strings, giving the orthographic representation of the
                words.
            """
            L = []
            for i in word_id:
                if i not in self._word_cache:
                    if not self._get_orth_str:
                        if hasattr(self, "surface_feature"):
                            word_feature = self.surface_feature
                        else:
                            word_feature = getattr(self, QUERY_ITEM_WORD)
                        _, _, table, feature = self.split_resource_feature(word_feature)

                        self.lexicon.joined_tables = []
                        self.lexicon.table_list = [self.word_table]
                        self.lexicon.add_table_path("word_id", word_feature)
                        
                        self._get_orth_str = "SELECT {0} FROM {1} WHERE {2}.{3} = {{}} LIMIT 1".format(
                            getattr(self, word_feature),
                            " ".join(self.lexicon.table_list),
                            self.word_table,
                            self.word_id)
                    try:
                        self._word_cache[i], = db_connection.execute(self._get_orth_str.format(i)).fetchone()
                    except TypeError as e:
                        print(e)
                        print(i)
                        print(self._get_orth_str.format(i))
                        self._word_cache[i] = DEFAULT_MISSING_VALUE
                L.append(self._word_cache[i])
            return L
                
        if options.cfg.context_sentence:
            raise NotImplementedError("Sentence contexts are currently not supported.")

        left_span = options.cfg.context_left
        right_span = options.cfg.context_right

        try:
            token_id = int(token_id)
        except ValueError:
            return [None] * int(left_span), [None] * int(number_of_tokens), [None] * int(right_span)

        if left_span > token_id:
            start = 1
        else:
            start = token_id - left_span
        
        # Get words in left context:
        S = self.corpus.sql_string_get_wordid_in_range(
                start, token_id - 1, origin_id)

        results = db_connection.execute(S)
        if not hasattr(self, "corpus_word_id"):
            left_context_words = [x for (x, ) in results]
        else:
            left_context_words = get_orth([x for (x, ) in results])
        left_context_words = [''] * (left_span - len(left_context_words)) + left_context_words

        if options.cfg.context_mode == CONTEXT_STRING:
            # Get words matching the query:
            S = self.corpus.sql_string_get_wordid_in_range(
                    token_id, token_id + number_of_tokens - 1, origin_id)
            results = db_connection.execute(S)
            if not hasattr(self, "corpus_word_id"):
                string_context_words = [x for (x, ) in results if x]
            else:
                string_context_words = get_orth([x for (x, ) in results if x])
        else:
            string_context_words = []

        # Get words in right context:
        S = self.corpus.sql_string_get_wordid_in_range(
                token_id + number_of_tokens, 
                token_id + number_of_tokens + options.cfg.context_right - 1, 
                origin_id)
        results = db_connection.execute(S)
        if not hasattr(self, "corpus_word_id"):
            right_context_words = [x for (x, ) in results]
        else:
            right_context_words = get_orth([x for (x, ) in results])
        right_context_words = right_context_words + [''] * (options.cfg.context_right - len(right_context_words))

        return (left_context_words, string_context_words, right_context_words)

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

        ordered_selected_features = []
        for feature in cls.get_preferred_output_order():
            if feature in options.cfg.selected_features:
                ordered_selected_features.append(feature)

        # then, add an appropriately aliased name for each selected feature:
        #for rc_feature in options.cfg.selected_features:
        for rc_feature in ordered_selected_features:
            select_list += cls.format_resource_feature(rc_feature, max_token_count)

        # linked columns
        for rc_feature in options.cfg.selected_features:
            func, hashed, table, feature = cls.split_resource_feature(rc_feature)
            if hashed != None and not func:
                link, res = get_by_hash(hashed)
                linked_feature = "db_{}_coq_{}_{}".format(res.db_name, table, feature)
                if cls.is_lexical(link.rc_from):
                    select_list += ["{}_{}".format(linked_feature, x+1) for x in range(max_token_count)]
                else:
                    select_list.append("{}_1".format(linked_feature))
    
        # functions:
        func_counter = Counter()
        for rc_feature in options.cfg.selected_features:
            func, hashed, table, feature = cls.split_resource_feature(rc_feature)
            if func:
                if hashed != None:
                    link, res = get_by_hash(hashed)
                    resource = "db_{}_coq_{}_{}".format(res.db_name, table, feature)
                else:
                    resource = "coq_{}_{}".format(table, feature)

                func_counter[resource] += 1
                fc = func_counter[resource]
                
                if cls.is_lexical(rc_feature):
                    select_list += ["func_{}_{}_{}".format(resource, fc, x + 1) for x in range(max_token_count)]
                else:
                    select_list.append("func_{}_{}_1".format(resource, fc))

        # if requested and possible, add contexts for each query match:
        if (options.cfg.context_mode != CONTEXT_NONE and 
            (options.cfg.context_left or options.cfg.context_right) and
            options.cfg.token_origin_id):

            # KWIC and context columns should by default be placed around 
            # the lexical features in order to be similar to standard 
            # concordancing software. In order to do so, we determine the 
            # current positions of lexical features in the output list:
            first_lexical_feature = len(select_list)
            last_lexical_feature = 0
            for i, field in enumerate(select_list):
                try:
                    feature = re.match("coq_(.*)_\d+$", field).group(1)
                except AttributeError:
                    # This is raised if the RE doesn't match the field name.
                    # In particular, it is raised for columns from special
                    # tables (Statistics, Coquery, Tag). They never count as
                    # Lexical features, so they should not be considered as 
                    # places for the context anyway.
                    pass
                else:
                    if feature in lexicon_features:
                        first_lexical_feature = min(i, first_lexical_feature)
                        last_lexical_feature = max(i, last_lexical_feature)
            
            # KWIC: add context columns to left and right of lexical features:
            if options.cfg.context_mode == CONTEXT_KWIC:
                if options.cfg.context_left:
                    select_list.insert(first_lexical_feature, "coq_context_left")
                if options.cfg.context_right:
                    select_list.insert(last_lexical_feature + int(options.cfg.context_left > 1) + 1, 
                                       "coq_context_right")

            # Strings and Sentences: add context columns after all other columns
            elif options.cfg.context_mode == CONTEXT_STRING:
                select_list.append("coq_context_string")
            elif options.cfg.context_mode == CONTEXT_SENTENCE:
                select_list.append("coq_context_string")

            # Columns: add context columns for each word to left and right of 
            # lexical features:
            elif options.cfg.context_mode == CONTEXT_COLUMNS:
                for x in range(options.cfg.context_left):
                    select_list.insert(first_lexical_feature,
                                       "coq_context_lc{}".format(x+1))
                for x in range(options.cfg.context_right):
                    select_list.insert(last_lexical_feature + options.cfg.context_left + x + 1,
                                       "coq_context_rc{}".format(x+1))
                    
            select_list.append("coquery_invisible_origin_id")

        select_list.append("coquery_invisible_corpus_id")
        select_list.append("coquery_invisible_number_of_tokens")
        assert sorted(list(set(select_list))) == sorted(select_list), "Duplicates in select_list: {}".format(select_list)
        return select_list
    
class CorpusClass(object):
    
    _frequency_cache = {}
    _corpus_size_cache = {}
    _context_cache = {}
    
    def __init__(self):
        self.lexicon = None
        self.resource = None

    def get_source_id(self, token_id):
        if not options.cfg.token_origin_id:
            return None
        S = "SELECT {} FROM {} WHERE {} = {}".format(
            getattr(self.resource, options.cfg.token_origin_id), 
            self.resource.corpus_table, 
            self.resource.corpus_id, 
            token_id)
        df = pd.read_sql(S, self.resource.get_engine())
        return df.values.ravel()[0]

    def get_file_data(self, token_id, features):
        """
        Return a data frame containing the requested features for the token
        id.
        """
        if isinstance(token_id, list):
            tokens = token_id
        elif isinstance(token_id, pd.Series):
            tokens = list(token_id.values)
        else:
            tokens = list(token_id)

        self.lexicon.joined_tables = ["corpus"]
        self.lexicon.table_list = [self.resource.corpus_table]
        
        self.lexicon.add_table_path("corpus_id", "file_id")

        f = ", ".join(["{}.{}".format(
                    self.resource.file_table, getattr(self.resource, x)) for x in features] + ["{}.{}".format(self.resource.corpus_table, self.resource.corpus_id)])
        S = "SELECT {features} FROM {path} WHERE {corpus}.{corpus_id} IN {token_ids}".format(
                features=f,
                corpus=self.resource.corpus_table,
                path = " ".join(self.lexicon.table_list),
                files=self.resource.file_table,
                corpus_file=self.resource.corpus_file_id,
                file_id=self.resource.file_id,
                corpus_id=self.resource.corpus_id,
                token_ids="({})".format(", ".join([str(x) for x in tokens])))

        return pd.read_sql(S, self.resource.get_engine())

    def get_origin_data(self, token_id):
        """
        Return a dictionary containing all origin data that is available for 
        the given token.
        
        This method traverses the table tree for the origin table as 
        determined by options.cfg.token_origin_id. For each table, all 
        matching fields are added.
        
        Parameters
        ----------
        token_id : int
            The id identifying the token.
            
        Returns
        -------
        l : list
            A list of tuples. Each tuple consists of the resource name of the 
            source table, and a dictionary with resource features as keys and 
            the matching field content as values.
        """
        if not options.cfg.token_origin_id:
            return []
        l = []
        
        # get the complete row from the corpus table for the current token:
        S = "SELECT * FROM {} WHERE {} = {}".format(
            self.resource.corpus_table,
            self.resource.corpus_id,
            token_id)

        df = pd.read_sql(S, sqlalchemy.create_engine(sqlhelper.sql_url(options.cfg.current_server, self.resource.db_name)))
        
        # as each of the columns could potentially link to origin information,
        # we go through all of them:
        for column in df.columns:
            # exclude the Token ID:
            if column == self.resource.corpus_id:
                continue
            # do not look into the word column of the corpus:
            try:
                if column == self.resource.corpus_word_id:
                    continue
                if column == self.resource.corpus_word:
                    continue
            except AttributeError:
                pass

            # Now, look for all features in the resource that the corpus table
            # links to. In order to do so, we first get a list of all feature 
            # names that match the current column, deterimine whether they are 
            # a feature of the corpus table, and if so, whether they link to 
            # a different table. If that is the case, we get all fields from 
            # that table that match the current entry, and add the information 
            # to the origin data list:

            # get the resource feature name from the corpus table that belongs 
            # to the current column display name:
            try:
                rc_feature = [x for x in self.resource.get_feature_from_name(column) if x.startswith("corpus_")][0]
            except IndexError:
                continue
    
            # obtain the field name from the resource name:
            _, _, _, feature = self.resource.split_resource_feature(rc_feature)
            # determine whether the field name is a linking field:
            try:
                _, _, tab, feat = self.resource.split_resource_feature(feature)
            except ValueError:
                # split_resource_feature() raises a ValueError exception if 
                # the passed string does not appear to be a resource feature.
                # In that case, the resource is not considered for origin data.                
                continue
            if feat == "id":
                id_column = getattr(self.resource, "{}_id".format(tab))
                table_name = getattr(self.resource, "{}_table".format(tab))
                S = "SELECT * FROM {} WHERE {} = {}".format(
                    table_name, id_column, df[column].values[0])
                # Fetch all fields from the linked table for the current 
                # token:
                row = pd.read_sql(S, self.resource.get_engine())
                if len(row.index) > 0:
                    D = dict([(x, row.at[0,x]) for x in row.columns if x != id_column])
                    # append the row data to the list:
                    l.append((table_name, D))
        return l

    def get_corpus_size(self, filters=[]):
        """ 
        Return the number of tokens in the corpus.

        The corpus can be filtered by providing a filter list.

        Parameters
        ----------
        filters : list 
            A list of QueryFilter instances. Such a list is created for the 
            current session in Session.__init__(), but arbitrary lists can 
            be generated by using the QueryFilter class directly. This class
            is defined in queries.py.

        Returns
        -------
        size : int 
            The number of tokens in the corpus, or in the filtered corpus.
        """

        if not filters and getattr(self.resource, "number_of_tokens", None):
            return self.resource.number_of_tokens
        
        filter_list = self.resource.translate_filters(filters)
        if filter_list:
            filter_strings = ["{}.{} {} '{}'".format(tab, col, op, val[0].replace("'", "''")) for col, _, tab, op, val, _ in filter_list]
            self.lexicon.table_list = []
            self.lexicon.joined_tables = []
            for column, corpus_feature, table, operator, value_list, val_range in filter_list:
                self.lexicon.add_table_path("corpus_id", corpus_feature)
            from_str = "{} WHERE {}".format(" ".join([self.resource.corpus_table] + self.lexicon.table_list), " AND ".join(filter_strings))
        else:
            from_str = self.resource.corpus_table

        S = "SELECT COUNT(*) FROM {}".format(from_str)
        if not S in self._corpus_size_cache:
            df = pd.read_sql(S.replace("%", "%%"), self.resource.get_engine())
            self._corpus_size_cache[S] = df.values.ravel()[0]
        return self._corpus_size_cache[S]

    def get_subcorpus_size(self, row, columns=None, filters=[]):
        """
        Return the size of the subcorpus specified by the corpus features in 
        the row.

        Parameters
        ----------
        row : A Pandas Series 
            A Series with stylized resource feature names as columns, and 
            values that match a row in the query result table.
        filters : list 
            A list of QueryFilter instances. Such a list is created for the 
            current session in Session.__init__(), but arbitrary lists can 
            be generated by using the QueryFilter class directly. This class
            is defined in queries.py.
        """
        filter_list = []
        if columns == None:
            corpus_features = [x for x, _ in self.resource.get_corpus_features() if x in options.cfg.selected_features]
            for column in row.index:
                match = re.match("coq_(.*)_1", column)
                if match:
                    if match.group(1) in corpus_features:
                        filt = QueryFilter()
                        filt.resource = self.resource
                        filt.text = "{} = {}".format(
                                                getattr(self.resource, match.group(1)), 
                                                row[column].replace("'", "''"))
                        filter_list.append(filt)
        else:
            for column in columns:
                filt = QueryFilter()
                filt.resource = self.resource
                filt.text = "{} = {}".format(
                                        getattr(self.resource, column), 
                                        row["coq_{}_1".format(column)])
                filter_list.append(filt)
        return self.get_corpus_size(filter_list + filters)
        
    def get_frequency(self, s, engine=False, filters=[]):
        """ 
        Return the frequency for a token specified by s.
        
        The string ``s`` contains a query item specification. The frequency 
        can be restricted to only a part of the corpus by providing a filter 
        list.
        
        Frequencies are cached so that recurrent calls of the method with the 
        same values for ``s`` and ``filters`` are not queried from the SQL 
        database but from the working memory.
        
        Parameters
        ----------
        s : str
            A query item specification
        filters : list 
            A list of QueryFilter instances. Such a list is created for the 
            current session in Session.__init__(), but arbitrary lists can 
            be generated by using the QueryFilter class directly. This class
            is defined in queries.py.
        engine : An SQLAlchemy engine
            If provided, use this SQL engine. Otherwise, initialize a new 
            engine, and use that.
            
        Returns
        -------
        freq : longint 
            The number of tokens that match the query item specification after
            the filter list is applied.
        """
        filter_list = self.resource.translate_filters(filters)

        if s in ["%", "_"]:
            s = "\\" + s
        
        tup = s, tuple([str(filt) for filt in filters])
        
        if tup in self._frequency_cache:
            return self._frequency_cache[tup]
        
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
        except CompleteLexiconRequestedError:
            where_clauses = []
        except WordNotInLexiconError:
            freq = 0
        else:

            self.lexicon.table_list = []
            self.lexicon.joined_tables = []

            filter_strings = ["{}.{} {} '{}'".format(
                tab, col, op, val[0]) for col, _, tab, op, val, _ in filter_list]
                
            if filter_list:
                for column, corpus_feature, table, operator, value_list, val_range in filter_list:
                    self.lexicon.add_table_path("corpus_id", corpus_feature)
                from_str = "{}".format(" ".join([self.resource.corpus_table] + self.lexicon.table_list))
            else:
                from_str = self.resource.corpus_table

            S = "SELECT COUNT(*) FROM {} WHERE {}".format(
                from_str, " AND ".join(where_clauses + filter_strings))

            if not engine:
                tmp_engine = self.resource.get_engine()
                df = pd.read_sql(S.replace("%", "%%"), tmp_engine)
                tmp_engine.dispose()
            else:
                df = pd.read_sql(S.replace("%", "%%"), engine)
                
            freq = df.values.ravel()[0]

        self._frequency_cache[tup] = freq
        return freq

    def get_whereclauses(self, token, WordTarget, PosTarget=None):
        if not token:
            return []

        where_clauses = []
        
        # Make sure that the token contains only those query item types that 
        # are actually supported by the resource:
        for spec_list, label, item_type in [(token.word_specifiers, QUERY_ITEM_WORD, "Word"),
                                (token.lemma_specifiers, QUERY_ITEM_LEMMA, "Lemma"),
                                (token.class_specifiers, QUERY_ITEM_POS, "Part-of-speech"),
                                (token.transcript_specifiers, QUERY_ITEM_TRANSCRIPT, "Transcription"),
                                (token.gloss_specifiers, QUERY_ITEM_GLOSS, "Gloss")]:
            if spec_list and not hasattr(self.resource, label):
                raise UnsupportedQueryItemError(item_type)

        # if only a class specification is given, this specification is
        # used as the where clause:
        if PosTarget and token.class_specifiers and not (token.word_specifiers or token.lemma_specifiers or token.transcript_specifiers):
            L = self.lexicon.get_posid_list(token)
            if L: 
                where_clauses.append("{} IN ({})".format(
                    PosTarget, ", ".join (["'{}'".format(x) for x in L])))
        # if there is a token with either a wordform, lemma, or token
        # specification, then get the list of matching word_ids from the 
        # lexicon:
        else:
            if token.lemmatize:
                L = set(self.lexicon.get_lemmatized_wordids(token))
            else:
                L = set(self.lexicon.get_matching_wordids(token))
                
            if L:
                if hasattr(self.resource, "word_id"):
                    L = [str(x) for x in L]
                else:
                    L = ["'{}'".format(x) for x in L]
                where_clauses.append("{} IN ({})".format(
                    WordTarget, ", ".join(L)))
            else:
                # no word ids were available for this token. this can happen 
                # if (a) there is no word in the lexicon that matches the 
                # specification, or (b) the word is blocked by the stopword 
                # list.
               
                if token.S not in ("%", ""):
                    if token.negated:
                        return []
                    else:
                        raise WordNotInLexiconError
        return where_clauses
    
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
            if s.strip().startswith("~"):
                w = -w
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

    def filter_to_sql(self, filt):
        """
        Return an SQL string that can be used in a WHERE clause to fulfil 
        the filter.
        """
        variable, rc_feature, table_name, op, value_list, _value_range = filt
        _, hashed, tab, feat = self.resource.split_resource_feature(rc_feature)
        if hashed != None:
            link, ext_resource = get_by_hash(hashed)
            db = ext_resource.db_name
            sql_field = "{}.{}.{}".format(
                db, 
                getattr(ext.resource, "{}_table".format(tab)),
                getattr(ext.resource, "{}_{}".format(tab, feat)))
        else:
            sql_field = getattr(self.resource, rc_feature)
            
        if op.upper() == "LIKE":
            sql_template = "{} LIKE '{}'"
            if "*" not in value_list[0]:
                value_list[0] = "*{}*".format(value_list[0])
            value_list[0] = tokens.COCAToken.replace_wildcards(value_list[0])
        else:
            sql_template = "{} = '{}'"
        return sql_template.format(sql_field, value_list[0])

    def get_required_features(self, query, token_list, only_lexical=False):
        """ 
        Get a set of all feature names that are required to fulfil the 
        query.
        """

        required_features = set([])

        # add all features that are required because they are in the current 
        # selection:
        for rc_feature in options.cfg.selected_features:
            func, hashed, table, feat = self.resource.split_resource_feature(rc_feature)
            if func:
                print("FUNC")
            if table not in self.resource.special_table_list:
                s = "{}_{}".format(table, feat)
                if hashed != None:
                    link, res = get_by_hash(hashed)
                    required_features.add("{}.{}".format(res.name , s))
                else:
                    required_features.add(s)
                
        # if a GUI is used, include source features so the entries in the
        # result table can be made clickable to show the context:
        if (options.cfg.gui and not options.cfg.to_file) or options.cfg.context_left or options.cfg.context_right:
            if options.cfg.token_origin_id:
                required_features.add(options.cfg.token_origin_id)

        for _, rc_feature, _, _, _, _ in self.resource.translate_filters(self.resource.filter_list):
            required_features.add(rc_feature)

        # add features required for links:
        for link, _ in options.cfg.external_links:
            required_features.add(link.rc_from)
            required_features.add("{}.{}".format(link.res_to, link.rc_to))

        # add features required for functions:
        for res, _, _, _ in options.cfg.selected_functions:
            func, hashed, table, feature = self.resource.split_resource_feature(res)
            assert hashed == None, "External functions currently not available"
            assert func
            print("FNC", res, table, feature)
            required_features.add("{}_{}".format(table, feature))
        
        # make sure that the word_id is always included in the query:
        # FIXME: Why is this needed?
        required_features.add("corpus_word_id")

        for i, tup in enumerate(token_list):
            _, tok = tup
            token = tokens.COCAToken(tok, self.lexicon)

            if token.class_specifiers and not (
                token.word_specifiers or 
                token.lemma_specifiers or 
                token.gloss_specifiers or
                token.transcript_specifiers):
                
                try:
                    required_features.add(
                        getattr(self.resource, QUERY_ITEM_POS))
                except AttributeError:
                    pass

        for feat in list(required_features):
            _, _, tab, _ = self.resource.split_resource_feature(feat)
            self.lexicon.table_list = []
            self.lexicon.joined_tables = ["corpus"]
            self.lexicon.add_table_path("corpus_id", feat)
            tabs = self.lexicon.joined_tables
            for i, tab in enumerate(tabs[:-1]):
                required_features.add("{}_{}_id".format(tab, tabs[i+1]))
                required_features.add("{}_id".format(tabs[i+1]))
        return required_features

    def get_required_tables(self, feature_list):
        """
        Return a list containing the tables required for the feature list.
        """

        self.lexicon.table_list = []
        self.lexicon.joined_tables = ["corpus"]

        table_set = set([])

        for rc_feature in feature_list:
            _, hashed, table, feature = self.resource.split_resource_feature(rc_feature)
            # FIXME: what about linked tables?
            self.lexicon.joined_tables = ["corpus"]
            self.lexicon.add_table_path("corpus_id", rc_feature)
            for tab in self.lexicon.joined_tables:
                table_set.add(tab)
        return table_set

    def get_token_query_string(self, current_token, number, to_file=False):
        """ 
        Return a SQL SELECT string that selects a table matching the current 
        token, and which includes all columns that are requested, or which 
        are required to join the tables. 
        
        Parameters
        ----------
        current_token : CorpusToken
            An instance of CorpusToken as a part of a query string.
        number : int
            The number of current_token in the query string (starting with 0)
        to_file : bool
            True if the query results are directly written to a file, and 
            False if they will be displayed in the GUI. Data that is written
            directly to a file contains less information, e.g. it doesn't 
            contain an origin ID or a corpus ID (unless requested).

        Returns
        -------
        s : string
            The partial SQL string.
        """
        # corpus variables will only be included in the token query string if 
        # this is the first query token.
        if number == 0:
            requested_features = [x for x in options.cfg.selected_features]
            
            # if a GUI is used, include source features so the entries in the
            # result table can be made clickable to show the context:
            if (options.cfg.gui and not options.cfg.to_file) or options.cfg.context_left or options.cfg.context_right:
                if options.cfg.token_origin_id:
                    requested_features.append(options.cfg.token_origin_id)
        else:
            corpus_variables = [x for x, _ in self.resource.get_corpus_features() if not x.endswith(("_starttime", "_endtime"))]
            requested_features = [x for x in options.cfg.selected_features if not x in corpus_variables]

        rc_where_constraints = defaultdict(set)

        # FIXME:
        # is this still needed if filters are applied after the query?
        ## add all features that are required for the query filters:
        #if number == 0:
            #for filt in self.resource.translate_filters(self.resource.filter_list):
                #variable, rc_feature, table_name, op, value_list, _value_range = filt
                #if op.upper() == "LIKE":
                    #if "*" not in value_list[0]:
                        #value_list[0] = "*{}*".format(value_list[0])
                    #value_list[0] = tokens.COCAToken.replace_wildcards(value_list[0])
                #requested_features.append(rc_feature)
                #rc_table = "{}_table".format(rc_feature.partition("_")[0])
                #rc_where_constraints[rc_table].add(
                    #'{} {} "{}"'.format(
                        #getattr(self.resource, rc_feature), op, value_list[0]))

        # make sure that the word_id is always included in the query:
        # FIXME: Why is this needed?
        requested_features.append("corpus_word_id")

        try:
            pos_feature = getattr(self.resource, QUERY_ITEM_POS)
        except AttributeError:
            word_pos_column = None
            pos_feature = ""
        else:
            word_pos_column = getattr(self.resource, pos_feature)
        # make sure that the tables and features that are required to 
        # match the current token are also requested as features:

        # create constraint lists:
        sub_list = set([])
        
        if hasattr(self.resource, "corpus_word_id"):
            word_id_column = self.resource.corpus_word_id
        elif hasattr(self.resource, "corpus_word"):
            #word_id_column = self.resource.corpus_word
            word_id_column = self.resource.corpus_id
        else:
            word_id_column = None
            
        where_clauses = self.get_whereclauses(
            current_token, 
            word_id_column,
            word_pos_column)
        for x in where_clauses:
            if x: 
                sub_list.add(x)
        s = ""
        if sub_list or current_token.S in ["%", ""]:
            if sub_list:
                if current_token.negated:
                    s = "NOT ({})".format(" AND ".join(sub_list))
                else:
                    s = " AND ".join(sub_list)

            if s:
                if current_token.class_specifiers and not (current_token.word_specifiers or current_token.lemma_specifiers or current_token.transcript_specifiers):
                    requested_features.append(pos_feature)
                    _, _, table, _ = self.resource.split_resource_feature(pos_feature)
                    rc_where_constraints["{}_table".format(table)].add(s)
                else:
                    rc_where_constraints["corpus_table"].add(s)

        for col in options.cfg.group_columns:
            if col not in requested_features:
                requested_features.append(col)        

        # get a list of all tables that are required to satisfy the 
        # feature request:
        
        required_tables = defaultdict(list)
        for rc_feature in requested_features:
            function, hashed, tab, _ = self.resource.split_resource_feature(rc_feature)

            # ignore features from one of the special tables:
            if tab in self.resource.special_table_list:
                continue

            if hashed != None:
                required_tables["{}.{}_table".format(hashed, tab)].append(rc_feature)
                link, _ = get_by_hash(hashed)
                if link.rc_from not in requested_features:
                    requested_features.append(link.rc_from)
            else:
                rc_table = "{}_table".format(tab)
                if rc_table not in required_tables:
                    tree = self.resource.get_table_structure(rc_table,  options.cfg.selected_features)
                    parent = tree["parent"]
                    table_id = "{}_id".format(tab)
                    required_tables[rc_table].append(rc_feature)
                    requested_features.append(table_id)
                    if parent:
                        _, _, parent_tab, _ = self.resource.split_resource_feature(parent)
                        parent_id = "{}_{}_id".format(parent_tab, tab)
                        requested_features.append(parent_id)

        join_strings = {}
        external_links = []
        join_strings[self.resource.corpus_table] = "{} AS COQ_CORPUS_TABLE".format(self.resource.corpus_table)
        full_tree = self.resource.get_table_structure("corpus_table", requested_features)
        # create a list of the tables 
        select_list = set([])

        for rc_table in required_tables:
            func, hashed, table, feature = self.resource.split_resource_feature(rc_table)

            if hashed != None:
                link, ex_res = get_by_hash(hashed)
                linked_table = "{}_table".format(table)

                column_list = []
                
                # add linking variable:
                column_list.append("{} AS db_{}_coq_{}_{}".format(
                    getattr(ex_res, link.rc_to), 
                    ex_res.db_name, 
                    link.rc_to, 
                    number+1))
                
                # add selected variables from external table:
                for rc_feature in required_tables[rc_table]:
                    _, _, tab, feat = ex_res.split_resource_feature(rc_feature)
                    rc_ext = "{}_{}".format(tab, feat)
                    alias = "db_{}_coq_{}_{}".format(
                        ex_res.db_name, rc_ext, number+1)
                    column_list.append("{} AS {}".format(
                        getattr(ex_res, rc_ext), alias))
                    select_list.add(alias)
                        
                # construct subquery that joins the external table:
                columns = ", ".join(set(column_list))
                alias = "db_{}_coq_{}_{}".format(ex_res.db_name, table, hashed).upper()
                
                sql_template = """
                LEFT JOIN 
                        (SELECT {columns}
                        FROM    {corpus}.{table})
                        AS      {alias}
                ON      coq_{internal_feature}_{n} = {alias}.db_{corpus}_coq_{external_feature}_{n}
                """
                
                S = sql_template.format(
                    columns=columns, n=number+1, 
                    internal_feature=link.rc_from, 
                    corpus=ex_res.db_name, 
                    table=getattr(ex_res, linked_table), 
                    external_feature=link.rc_to, alias=alias)
                
                external_links.append(S)
                
                if self.resource.db_type == SQL_SQLITE:
                    if not hasattr(self.resource, "attach_list"):
                        self.resource.attach_list = set([])
                    self.resource.attach_list.add(ex_res.db_name)

            else:
                rc_tab = rc_table.split("_")[0]
                sub_tree = self.resource.get_sub_tree(rc_table, full_tree)
                parent_tree = self.resource.get_sub_tree(sub_tree["parent"], full_tree) 
                table = getattr(self.resource, rc_table)
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
                        getattr(self.resource, rc_feature.split("func.")[-1]),
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
                    
                    join_strings[rc_table] = "INNER JOIN (SELECT {columns} FROM {table} {where}) AS COQ_{rc_table} ON {parent_id} = {child_id}".format(
                        columns = columns, 
                        table = table,
                        rc_table = rc_table.upper(),
                        where = where_string,
                        parent_id = parent_id,
                        child_id = child_id)
                else:
                    join_strings[rc_table] = "(SELECT {columns} FROM {table} {where}) AS COQ_{rc_table}".format(
                        columns = columns, 
                        table = table,
                        rc_table = rc_table.upper(),
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
        
        # in order to make the context viewer work in the gui, add the 
        # corpus origin resource (which is either the source id or the file
        # id) to the selected columns, but only for the first query item, 
        # and only if the gui is used:
        if (to_file or options.cfg.to_file) and number == 0 and options.cfg.token_origin_id:
            select_list.add("coq_{}_1".format(options.cfg.token_origin_id))

        S = "SELECT {} FROM {}".format(", ".join(select_list), " ".join(L))
        return S
    
    #def get_token_query_string_self_joined(self, token, number):
        #"""
        #Return a MySQL SELECT string that queries one token in a query on an 
        #n-gram corpus table.
        #"""

        ## get a list of all tables that are required to satisfy the 
        ## feature request:
        #corpus_variables = [x for x, _ in self.resource.get_corpus_features()]
        #requested_features = [x for x in options.cfg.selected_features if not x in corpus_variables]

        #requested_features.append("word_id")
        
        #column_list = []
        #for rc_feature in requested_features:
            #column_list.append("{} AS coq_{}_{}".format(
                #getattr(self.resource, rc_feature),
                #rc_feature, number + 1))

        #where_clauses = self.get_whereclauses(
            #token, 
            #self.resource.corpus_word_id, 
            #None)

        #where_clauses = []
        #L = []
        #try:
            #word_label = self.resource.word_label
        #except AttributeError:
            #pass
        #else:
            #for word in token.word_specifiers:
                #current_token = tokens.COCAToken(word, self, replace=False, parse=False)
                #current_token.negated = token.negated
                #S = current_token.S
                #if S != "%":
                    ## take care of quotation marks:
                    #S = S.replace("'", "''")
                    #L.append("%s %s '%s'" % (word_label, self.resource.get_operator(current_token), S))
        #if L:
            #where_clauses.append("({})".format(" OR ".join(L)))

        #L = []
        #try:
            #lemma_label = self.resource.word_lemma
        #except AttributeError:
            #pass
        #else:
            #for lemma in token.lemma_specifiers:
                #current_token = tokens.COCAToken(lemma, self, replace=False, parse=False)
                #current_token.negated = token.negated
                #S = current_token.S
                #if S != "%":
                    ## take care of quotation marks:
                    #S = S.replace("'", "''")
                    #L.append("%s %s '%s'" % (lemma_label, self.resource.get_operator(current_token), S))
        #if L:
            #where_clauses.append("({})".format(" OR ".join(L)))
            
        #L = []
        #try:
            #pos_label = self.resource.pos
        #except AttributeError:
            #pass
        #else:
            #for pos in token.class_specifiers:
                #current_token = tokens.COCAToken(pos, self, replace=False, parse=False)
                #current_token.negated = token.negated
                #S = current_token.S
                ## take care of quotation marks:
                #if S != "%":
                    #S = S.replace("'", "''")
                    #L.append("%s %s '%s'" % (pos_label, self.resource.get_operator(current_token), S))
        #if L:
            #where_clauses.append("({})".format(" OR ".join(L)))
        
        #if where_clauses:
            #S = """
            #SELECT  {columns}
            #FROM    {lexicon}
            #WHERE   {constraints}
            #""".format(
                #columns=", ".join(column_list),
                #lexicon=self.resource.word_table,
                #constraints=" AND ".join(where_clauses))
        #else:
            #S = """
            #SELECT  {columns}
            #FROM    {lexicon}
            #""".format(
                #columns=", ".join(column_list),
                #lexicon=self.resource.word_table),
        #return S
        
    def sql_string_query_lookup(self, Query, token_list):
        """ 
        Return a string that is sufficient to run the query on the
        MySQL database. 
        """

        def sql_string_join_lexical():
            """
            Return a string containing the inline views required to fulfil
            the lexicon feature selections.
            
            The string contains a format placeholder {N} that can be filled 
            with the correct query item number. 
            """
            table_features = defaultdict(list)
            table_chain = defaultdict(list)
            s_set = []

            lexicon_features = [x for x, _ in self.resource.get_lexicon_features()]

            self.lexicon.table_list = []
            self.lexicon.joined_tables = ["corpus"]

            for x in [x for x in options.cfg.selected_features if x in lexicon_features]:
                _, _, table, _ = self.resource.split_resource_feature(x)
                self.lexicon.joined_tables = ["corpus"]
                self.lexicon.add_table_path("corpus_id", x)
                table_features[table].append(x)
                id_feature = "{}_id".format(table)
                if id_feature not in table_features[table]:
                    table_features[table].append(id_feature)
                table_chain[table] = self.lexicon.joined_tables
                for i, _ in enumerate(self.lexicon.joined_tables[:-1]):
                    this_tab = self.lexicon.joined_tables[i]
                    next_tab = self.lexicon.joined_tables[i + 1]
                    table_features[this_tab].append("{}_id".format(this_tab))
                    table_features[this_tab].append("{}_{}_id".format(this_tab, next_tab))

            sql_template = """
            INNER JOIN 
                    (SELECT {features} 
                    FROM    {table}) 
                    AS      {alias} 
            ON      {alias_id} = {ref_id}
            """
            for table in table_features:
                if table != "corpus":
                    l = []
                    for feature in table_features[table]:
                        l.append("{} AS coq_{}_{{N}}".format(
                            getattr(self.resource, feature), feature))
                    features = ", ".join(l)
                    prev_table = table_chain[table][-2]
                    s_set.append(sql_template.format(
                        features=features,
                        table=getattr(self.resource, "{}_table".format(table)),
                        alias="COQ_{}_TABLE_{{N}}".format(table.upper()),
                        alias_id="coq_{}_id_{{N}}".format(table),
                        ref_table="COQ_{}_TABLE".format(prev_table.upper()), 
                        ref_id="coq_{}_{}_id_{{N}}".format(prev_table, table)))

            return "\n".join(s_set)

        # For a query string 'the [n*2]', this is the query string this method
        # should produce (in COCA):
        
        # SELECT  e1.Word AS coq_word_label_1, 
        #         e2.Word AS coq_word_label_2, 
        #         Genre AS coq_corpus_source_1
        # FROM    CorpusNgram 
        # INNER JOIN 
        #         Sources 
        # ON      CorpusNgram.SourceId = Sources.SourceId 
        # INNER JOIN
        #         Lexicon AS e1
        # ON      CorpusNgram.WordId1 = e1.WordId
        # INNER JOIN
        #         Lexicon AS e2
        # ON      CorpusNgram.WordId2 = e2.WordId
        # WHERE   e1.Word = 'the' AND e2.POS LIKE 'n%2'

        sql_master = """
        SELECT  {fields}
        FROM    {corpus}
                {table_join}
        WHERE   {where_string}
        """

        
        corpus_features = [(x, y) for x, y in self.resource.get_corpus_features()]
        lexicon_features = [(x, y) for x, y in self.resource.get_lexicon_features()]

        # determine how words are stored: either directly as a string in a
        # word column, or as keys to a word table:
        if hasattr(self.resource, "corpus_word_id"):
            word_id_column = self.resource.corpus_word_id
        elif hasattr(self.resource, "corpus_word"):
            word_id_column = self.resource.corpus_id

        corpus_fields = ["{id} AS coq_corpus_id_1".format(
            tab=self.resource.corpusngram_table, 
            id=self.resource.corpus_id)]

        for i in range(len(token_list)):
            corpus_fields.append("{col}{i} AS coq_corpus_word_id_{i}".format(
                tab=self.resource.corpusngram_table, 
                col=word_id_column, 
                i=i+1))
            
        if options.cfg.token_origin_id:
            corpus_fields.append("{} AS coq_{}_1".format(
                getattr(self.resource, options.cfg.token_origin_id),
                options.cfg.token_origin_id))


        #### OLD:
        
        
        corpus_features = [(x, y) for x, y in self.resource.get_corpus_features()]
        lexicon_features = [(x, y) for x, y in self.resource.get_lexicon_features()]

        # determine how words are stored: either directly as a string in a
        # word column, or as keys to a word table:
        if hasattr(self.resource, "corpus_word_id"):
            word_id_column = self.resource.corpus_word_id
        elif hasattr(self.resource, "corpus_word"):
            word_id_column = self.resource.corpus_id

        corpus_fields = ["{id} AS coq_corpus_id_1".format(
            tab=self.resource.corpusngram_table, 
            id=self.resource.corpus_id)]

        for i in range(len(token_list)):
            corpus_fields.append("{col}{i} AS coq_corpus_word_id_{i}".format(
                tab=self.resource.corpusngram_table, 
                col=word_id_column, 
                i=i+1))
            
        if options.cfg.token_origin_id:
            corpus_fields.append("{} AS coq_{}_1".format(
                getattr(self.resource, options.cfg.token_origin_id),
                options.cfg.token_origin_id))

        # get word_id constraints for each query item:
        where_clauses = []
        for i, tup in enumerate(token_list):
            _, item = tup
            try:
                where_clauses += self.get_whereclauses(
                    tokens.COCAToken(item, self.lexicon),
                    "{}{}".format(word_id_column, i+1))
            except CompleteLexiconRequestedError:
                where_clauses = []
                
        table_joins = []
        for i in range(len(token_list)):
            s = sql_string_join_lexical()
            s = s.format(N=i+1)
            table_joins.append(s)
        
        final_select = self.get_select_columns(Query, token_list)
        if where_clauses:
            where_string = "WHERE {}".format(" AND ".join(where_clauses))
        else:
            where_string = ""
            
        # get inline view of corpus table
        # FIXME: Currently, this selects only the word id fields, and not 
        # any other fields in the corpus table.
        sql_template = """
        (SELECT {corpus_fields} 
        FROM    {corpusngram_table} 
        {where}) AS COQ_CORPUS_TABLE
        """
        aliased_corpus = sql_template.format(
            corpus_fields=", ".join(corpus_fields), 
            corpusngram_table=self.resource.corpusngram_table,
            where=where_string)

        sql_template = """
        SELECT  {fields}
        FROM    {aliased_corpus}
                {table_joins}
        """
        query_string = sql_template.format(
            fields=", ".join(set(final_select)),
            aliased_corpus=aliased_corpus,
            table_joins=" ".join(table_joins))

        # add LIMIT clause if necessary:
        if options.cfg.number_of_tokens:
            query_string = "{} LIMIT {}".format(
                query_string, options.cfg.number_of_tokens)

        return query_string


        #token_query_list = {}

        #corpus_features = [x for x, y in self.resource.get_corpus_features() if x in options.cfg.selected_features]
        #lexicon_features = [x for x, y in self.resource.get_lexicon_features() if x in options.cfg.selected_features]
        
        #for i, tup in enumerate(token_list):
            #number, token = tup
            #s = self.get_token_query_string(tokens.COCAToken(token, self.lexicon), i)
            #if s:
                #join_string = "INNER JOIN ({s}) AS e{i}\nON coq_word_id_{i} = W{i}".format(
                    #s = s, 
                    #i=i+1)
                #token_query_list[i+1] = join_string
        #final_select = []

        #requested_features = [x for x in options.cfg.selected_features]
        #if options.cfg.context_left or options.cfg.context_right:
            ## in order to make this not depend on a fixed database layout 
            ## (here: 'source' and 'file' tables), we should check for any
            ## table that corpus_table is linked to except for word_table
            ## (and all child tables).            
            #if options.cfg.token_origin_id:
                #requested_features.append(options.cfg.token_origin_id.replace("corpus", "corpusngram"))
                
        #for rc_feature in requested_features:
            #try:
                #final_select.append(
                    #"{} AS coq_{}_1".format(getattr(self.resource, "corpusngram_{}".format(rc_feature)), rc_feature))
            #except AttributeError:
                ## This means that the requested feature is not directly
                ## stored in the n-gram table. This means that a table 
                ## link is necessary.
                #pass

        ## FIXME:
        ## Not working: 
        ## - align_quantified
        ## - linked tables

        #for rc_feature in self.resource.get_preferred_output_order():
            #if rc_feature in requested_features:
                #if rc_feature in lexicon_features:
                    #for i in range(Query.Session.get_max_token_count()):
                        #if i < len(token_list):
                            #final_select.append("coq_{}_{}".format(rc_feature, i+1))
                        #else:
                            #final_select.append("NULL AS coq_{}_{}".format(rc_feature, i+1))
                #elif rc_feature in corpus_features:
                    #pass
                    ##final_select.append("coq_{}_1".format(rc_feature))

        ##for rc_feature in options.cfg.selected_features:
            ##select_feature = "coq_{}_1".format(rc_feature)
            ##if rc_feature in corpus_features or rc_feature in lexicon_features:
                ##final_select.append(select_feature)
            ##else:
                ##final_select.append("NULL AS {}".format(select_feature))

        #final_select.append("{} AS coquery_invisible_corpus_id".format(self.resource.corpus_id))

        ## Add filters:
        ## FIXME: What happens if the filter does not apply to something
        ## in the ngram table, but to a linked table?
        #where_string_list = []
        #for filt in self.resource.translate_filters(self.resource.filter_list):
            #variable, rc_feature, table_name, op, value_list, _value_range = filt
            #if op.upper() == "LIKE":
                #if "*" not in value_list[0]:
                    #value_list[0] = "*{}*".format(value_list[0])
                #value_list[0] = tokens.COCAToken.replace_wildcards(value_list[0])

            #rc_table = "{}_table".format(rc_feature.partition("_")[0])
            #s = '{} {} "{}"'.format(getattr(self.resource, rc_feature), op, value_list[0])
            #where_string_list.append(s)
        #return """
        #SELECT  {}
        #FROM    {}
        #{}
        #{}
        #""".format(
            #", ".join(final_select),
            #self.resource.corpusngram_table,
            #"\n".join(token_query_list.values()),
            #"WHERE {}".format(" AND ".join(where_string_list)) if where_string_list else "",
            #)


    def get_select_columns(self, Query, token_list, to_file=False):
        """
        Get a list of aliased columns that is used in the query string.

        Parameters
        ----------
        to_file : bool
            True if the query results are directly written to a file, and 
            False if they will be displayed in the GUI. Data that is written
            directly to a file contains less information, e.g. it doesn't 
            contain an origin ID or a corpus ID (unless requested).
        """

        corpus_features = [(x, y) for x, y in self.resource.get_corpus_features() if x in options.cfg.selected_features]
        lexicon_features = [(x, y) for x, y in self.resource.get_lexicon_features() if x in options.cfg.selected_features]

        positions_lexical_items = self.get_lexical_item_positions(token_list)

        max_token_count = Query.Session.get_max_token_count()

        final_select = []        
        for rc_feature in self.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in lexicon_features] or self.resource.is_tokenized(rc_feature):
                    for i in range(max_token_count):
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
        for link, rc_feature in options.cfg.external_links:
            res, _, _ = options.get_resource(link.res_to)
            _, _, tab, feat = self.resource.split_resource_feature(rc_feature)
            rc_feat = "{}_{}".format(tab, feat)
            if self.resource.is_lexical(link.rc_from):
                for i in range(max_token_count):
                    if options.cfg.align_quantified:
                        if i in positions_lexical_items:
                            final_select.append("db_{}_coq_{}_{}".format(res.db_name, rc_feat, i+1))
                    else:
                        final_select.append("db_{}_coq_{}_{}".format(res.db_name, rc_feat, i+1))
            else:
                final_select.append("db_{}_coq_{}_1".format(res.db_name, rc_feat))

        # add the corpus features in the preferred order:
        # FIXME: Is this still necessary?
        for rc_feature in self.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in corpus_features]:
                    final_select.append("coq_{}_1".format(rc_feature))

        # Add any feature that is selected that is neither a corpus feature,
        # a lexicon feature nor a Coquery feature:
        # FIXME: What does this do, then?
        for rc_feature in options.cfg.selected_features:
            if any([x == rc_feature for x, _ in self.resource.get_corpus_features()]):
                break
            if any([x == rc_feature for x, _ in self.resource.get_lexicon_features()]):
                break
            _, _, table, _ = self.resource.split_resource_feature(rc_feature)
            if table not in self.resource.special_table_list:
                if "." not in rc_feature:
                    final_select.append("coq_{}_1".format(rc_feature.replace(".", "_")))

        # add any resource feature that is required by a function:
        for res, _, _, _, _ in options.cfg.selected_functions:
            func, hashed, table, feature = self.resource.split_resource_feature(res)
            assert func
            # function on field from external table?
            if hashed != None:
                link, res = get_by_hash(hashed)
                db_name = res.db_name
                field_str = "db_{db_name}_coq_{rc_feature}_{{N}}"
            else:
                db_name = None
                field_str = "coq_{rc_feature}_{{N}}"
            
            rc_feature= "{}_{}".format(table, feature)
            label = field_str.format(db_name=db_name, rc_feature=rc_feature)
            
            if rc_feature in [x for x, _ in self.resource.get_lexicon_features()]:
                final_select += [label.format(N=x+1) for x in range(Query.Session.get_max_token_count())]
            else:
                final_select.append(label.format(N=1))

        for rc_feature in options.cfg.group_columns:
            L = self.resource.format_resource_feature(rc_feature, max_token_count)
            for col in L:
                try:
                    num = int(col.rpartition("_")[-1]) - 1
                except ValueError:
                    # this happens if the column label does not end in a 
                    # number, e.g. for fields from the special tables.
                    continue
                if options.cfg.align_quantified:
                    if num in positions_lexical_items:
                        final_select.append(col)
                    else:
                        final_select.append("NULL AS {}".format(col))
                else:
                    if num < len(token_list):
                        final_select.append(col)
                    else:
                        final_select.append("NULL AS {}".format(col))

        ## add coquery_invisible_origin_id if a context is requested:
        #if (options.cfg.context_mode != CONTEXT_NONE and 
            #options.cfg.token_origin_id != None and
            #(options.cfg.context_left or options.cfg.context_right)):
        if not to_file or (options.cfg.use_context):
            final_select.append("coq_{}_1 AS coquery_invisible_origin_id".format(options.cfg.token_origin_id))
            # Always add the corpus id to the output fields:
            final_select.append("coq_corpus_id_1 AS coquery_invisible_corpus_id")
        return final_select

    def get_lexical_item_positions(self, token_list):
        """
        Return a list of integers that indicate the positions of the items in
        the token list. This list takes quantification into account so that
        items following quantified icons can be aligned below each other.
        """
        last_offset = 0
        token_counter = None
        positions_lexical_items = []
        
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
        return positions_lexical_items

    def sql_string_query(self, Query, token_list, to_file=False):
        """ 
        Return a string that is sufficient to run the query on the
        MySQL database. 
        
        Parameters
        ----------
        Query : instance of TokenQuery
            The currently active query
        token_list : list
            A list of Token instances
        to_file : bool
            True if the query results are directly written to a file, and 
            False if they will be displayed in the GUI. Data that is written
            directly to a file contains less information, e.g. it doesn't 
            contain an origin ID or a corpus ID (unless requested).
        """

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
                column_number, to_file)
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
                        col_number=column_number + 1,
                        offset=i - referent_id + 1,
                        ref_col=referent_column)
                    token_query_list[i+1] = join_string
        query_string_part = [
            "SELECT COQ_OUTPUT_FIELDS FROM ({}) AS e{}".format(token_query_list.pop(referent_id), referent_id)]
        for referent_id, _ in order:
            query_string_part.append(token_query_list[referent_id])

        final_select = self.get_select_columns(Query, token_list, to_file)
        
        # construct the query string from the token query parts:
        query_string = " ".join(query_string_part)
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

    def sql_string_get_wordid_in_range(self, start, end, origin_id):
        if hasattr(self.resource, "corpus_word_id"):
            word_id_column = self.resource.corpus_word_id
        elif hasattr(self.resource, "corpus_word"):
            word_id_column = self.resource.corpus_word
        if options.cfg.token_origin_id and origin_id:
            return "SELECT {corpus_wordid} from {corpus} WHERE {token_id} BETWEEN {start} AND {end} AND {corpus_source} = {this_source}".format(
                corpus_wordid=word_id_column,
                corpus=self.resource.corpus_table,
                token_id=self.resource.corpus_id,
                start=start, end=end,
                corpus_source=getattr(self.resource, options.cfg.token_origin_id),
                this_source=origin_id)
        else:
            # if no source id is specified, simply return the tokens in
            # the corpus that are within the specified range.
            return "SELECT {corpus_wordid} FROM {corpus} WHERE {corpus_token} BETWEEN {start} AND {end} {verbose}".format(
                corpus_wordid=word_id_column,
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
        except KeyError:
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

    def get_context_stylesheet(self):
        """
        Return a string that formats the used elements in a context viewer.
        """
        return ""

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

    def _read_context_for_renderer(self, token_id, source_id, token_width):
        origin_id = getattr(self.resource, "corpus_source_id",
                        getattr(self.resource, "corpus_file_id",
                            getattr(self.resource, "corpus_sentence_id",
                                self.resource.corpus_id)))
        
        if hasattr(self.resource, "tag_table"):
            format_string = "SELECT {corpus}.{corpus_id} AS COQ_TOKEN_ID, {word_table}.{word} AS COQ_WORD, {tag} AS COQ_TAG_TAG, {tag_table}.{tag_type} AS COQ_TAG_TYPE, {attribute} AS COQ_ATTRIBUTE, {tag_id} AS COQ_TAG_ID FROM {corpus} {joined_tables} LEFT JOIN {tag_table} ON {corpus}.{corpus_id} = {tag_table}.{tag_corpus_id} WHERE {corpus}.{corpus_id} BETWEEN {start} AND {end}"
        else:
            format_string = "SELECT {corpus}.{corpus_id} AS COQ_TOKEN_ID, {word_table}.{word} AS COQ_WORD FROM {corpus} {joined_tables} WHERE {corpus}.{corpus_id} BETWEEN {start} AND {end}"
            
        if origin_id:
            format_string += " AND {corpus}.{source_id} = '{current_source_id}'"
    
        if hasattr(self.resource, "surface_feature"):
            word_feature = self.resource.surface_feature
        else:
            word_feature = getattr(self.resource, QUERY_ITEM_WORD)
            
        if hasattr(self.resource, "corpus_word_id"):
            corpus_word_id = self.resource.corpus_word_id
        else:
            corpus_word_id = self.resource.corpus_word
            
        _, _, tab, _ = self.resource.split_resource_feature(word_feature)
        word_table = getattr(self.resource, "{}_table".format(tab))
        word_id = getattr(self.resource, "{}_id".format(tab))
        
        self.lexicon.table_list = []
        self.lexicon.joined_tables = []
        self.lexicon.add_table_path("corpus_id", word_feature)

        if hasattr(self.resource, "tag_table"):
            S = format_string.format(
                corpus=self.resource.corpus_table,
                corpus_id=self.resource.corpus_id,
                corpus_word_id=corpus_word_id,
                source_id=origin_id,
                
                word=getattr(self.resource, word_feature),
                word_table=word_table,
                word_id=word_id,
                
                joined_tables=" ".join(self.lexicon.table_list),
                
                tag_table=self.resource.tag_table,
                tag=self.resource.tag_label,
                tag_id=self.resource.tag_id,
                tag_corpus_id=self.resource.tag_corpus_id,
                tag_type=self.resource.tag_type,
                attribute=self.resource.tag_attribute,
                
                current_source_id=source_id,
                start=max(0, token_id - 1000), 
                end=token_id + token_width + 999)
            headers = ["COQ_TOKEN_ID", "COQ_TAG_ID"]
        else:
            S = format_string.format(
                corpus=self.resource.corpus_table,
                corpus_id=self.resource.corpus_id,
                corpus_word_id=self.resource.corpus_word_id,
                source_id=origin_id,
                
                word=getattr(self.resource, word_feature),
                word_table=word_table,
                word_id=word_id,

                joined_tables=" ".join(self.lexicon.table_list),
                
                current_source_id=source_id,
                start=max(0, token_id - 1000), 
                end=token_id + token_width + 999)
            headers = ["COQ_TOKEN_ID"]
        if options.cfg.verbose:
            logger.info(S)
            print(S)
        df = pd.read_sql(S, self.resource.get_engine())

        try:
            df = df.sort_values(by=headers)
        except AttributeError:
            df = df.sort(columns=headers)
        self._context_cache[(token_id, source_id, token_width)] = df
        
    def get_rendered_context(self, token_id, source_id, token_width, context_width, widget):
        """ 
        Return a string containing the markup for the context around the 
        specified token.
        
        The most simple visual representation of the context is a plain text
        display, but in principle, a corpus might implement a more elaborate
        renderer. For example, a corpus may contain information about the
        page layout, and the renderer could use that information to create a
        facsimile of the original page.
        
        The renderer can interact with the widget in which the context will
        be displayed. The area in which the context is shown is a QLabel
        named widget.ui.context_area. """

        def expand_row(x):
            self.id_list += list(range(int(x.coquery_invisible_corpus_id), int(x.end)))

        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
            }

        def escape_html(s):
            """
            Based on http://stackoverflow.com/questions/2077283/
            """
            return "".join(html_escape_table.get(c, c) for c in s)

        if not hasattr(self.resource, QUERY_ITEM_WORD):
            raise UnsupportedQueryItemError

        if not (token_id, source_id, token_width) in self._context_cache:
            self._read_context_for_renderer(token_id, source_id, token_width)
        df = self._context_cache[(token_id, source_id, token_width)]

        context_start = max(0, token_id - context_width)
        context_end = token_id + token_width + context_width - 1

        # create a list of all token ids that are also listed in the results
        # table:
        self.id_list = []
        tab = options.cfg.main_window.Session.data_table
        tab = tab[(tab.coquery_invisible_corpus_id> token_id - 1000) & (
            tab.coquery_invisible_corpus_id < token_id + 1000 + token_width)]
        tab["end"] = tab[["coquery_invisible_corpus_id", 
                          "coquery_invisible_number_of_tokens"]].sum(axis=1)

        # the function expand_row has the side effect that it adds the 
        # token id range for each row to the list self.id_list
        tab.apply(expand_row, axis=1)
            
        context = deque()
        # we need to keep track of any opening and closing tag that does not
        # have its matching tag in the selected context:
        opened_elements = []
        closed_elements = []
    
        for context_token_id in [x for x in range(context_start, context_end) if x in df.COQ_TOKEN_ID.unique()]:
            opening_elements = []
            closing_elements = []
            word = ""

            df_sub = df[df.COQ_TOKEN_ID == context_token_id]
            if "COQ_TAG_ID" in df_sub.columns:
                for x in df_sub.index:
                    if df_sub.COQ_TAG_TYPE[x] is not None:
                        if df_sub.COQ_TAG_TYPE[x] == "open":
                            opening_elements.append(x)
                        if df_sub.COQ_TAG_TYPE[x] == "empty":
                            opening_elements.append(x)
                            closing_elements.append(x)
                        if df_sub.COQ_TAG_TYPE[x] == "close":
                            closing_elements.append(x)

            word = escape_html(df_sub.COQ_WORD.iloc[0])
            
            # process all opening elements:
            for ix in opening_elements:
                tag = df_sub.loc[ix].COQ_TAG_TAG
                attr = df_sub.loc[ix].COQ_ATTRIBUTE
                if attr:
                    attr_list = [x.partition("=") for x in attr.split(",")]
                    attributes = dict([(l, r) for l, _, r in attr_list])
                else: 
                    attributes = {}
                open_element = self.renderer_open_element(tag, attributes)
                if open_element:
                    context += open_element
                    opened_elements.append(tag)
                
            if word:
                # process the context word:
                
                # highlight words that are in the results table:
                if context_token_id in self.id_list:
                    context.append("<span style='{};'>".format(self.resource.render_token_style))
                # additional highlight if the word is the target word:
                if token_id <= context_token_id < token_id + token_width:
                    context.append("<b>")
                    context.append(word)
                    context.append("</b>")
                else:
                    context.append(word)
                if context_token_id in self.id_list:
                    context.append("</span>")
            
            # process all opening elements:
            for ix in closing_elements:
                tag = df_sub.loc[ix].COQ_TAG_TAG
                attr = df_sub.loc[ix].COQ_ATTRIBUTE
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
        s = collapse_words(context)
        s = s.replace("</p>", "</p>\n")
        s = s.replace("<br/>", "<br/>\n")
        return s

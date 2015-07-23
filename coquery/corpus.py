# -*- coding: utf-8 -*-
"""
FILENAME: corpus.py -- part of Coquery corpus query tool

This module defines classes BaseLexicon and BaseCorpus.

LICENSE:
Copyright (c) 2015 Gero Kunter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from __future__ import unicode_literals
from __future__ import print_function

from errors import *
import tokens
import options
import sqlwrap
import time
import datetime
from defines import *

class BaseLexicon(object):
    """
    CLASS
    BaseLexicon(object)
    
    METHODS
    __init__()
        initialize the lexicon.
    get_entry(word_id)
        returns the lexicon entry of type Entity() corresoponding to word_id
    is_part_of_speech(pos)
        returns True if pos is a valid part-of-speech label, or False 
        otherwise. Supports wildcards.
    find_other_wordforms(word)
        returns a list containing the word_id of all other entries sharing
        the same lemma as the argument
        
    PROPERTIES
    list(provides)
        list of features provided by the lexicon. All lexicons should 
        provide at least LEX_WORDID and LEX_ORTH (i.e. every entry should
        have a unique identifier and an orthographic representation).
    list(wildcards)
        list of characters that are considered wild cards in the lexicon.
    """
    provides = [LEX_WORDID, LEX_ORTH]

    class Entry(object):
        """ 
        CLASS 
        Entry(object)

        METHODS
        __init__()
            initialize the Entry. Creates a property for every feature 
            provided by the current lexicon. Entities should therefore have
            at least the properties Entity.word_id and Entity.orth. 
            Properties created in this way are always initialized with 
            value None. 
        """
        def __init__(self, provides, features = None):
            """
            CALL
            Entity.__init__(word_id=None)
            
            DESCRIPTION
            __init__() initializes the lexicon entry object. For each 
            property in BaseLexicon.provides, a new object attribute is
            created. The initial value of the these attributes is None.
            
            VALUE
            None
            """

            # deprecated code:
            for current_attribute in provides:
                self.__setattr__(current_attribute, None)
            self.attributes = provides
                
        def set_values(self, value_list, feature_list=None):
            # deprecated:
            for i, current_attribute in enumerate(self.attributes):
                if current_attribute in self.__dict__:
                    self.__dict__[current_attribute] = value_list[i]
            
    def __init__(self, resource):
        """
        CALL
        BaseLexicon.__init__(lexicon, resource)
        
        DESCRIPTION
        __init__() initializes the lexicon. After initialization, the
        method get_entry(word_id) can be used to obtain an Entity() object
        that contains the lexicon entry specified by word_id.
        
        ARGUMENTS
        lexicon, resource
        
        VALUE
        None
        """
        self.resource = resource
        
        self.features = resource.get_lexicon_features()
        
        if LEX_POS in self.provides:
            self.pos_dict = {}

    def get_entry(self, word_id, requested):
        """
        CALL
        BaseLexicon.get_entry(word_id)
        
        DESCRIPTION
        get_entry(word_id) returns an object of type Entity() corresoponding 
        to the lexicon entry indexed by the value of word_id. This function
        sets all properties of Entity() to the correct values from the
        lexicon.
        
        VALUE
        <class 'Entity'>
        """        
        entry = self.Entry(word_id)
        return entry
    
    def is_part_of_speech(self, pos):
        """ 
        CALL
        BaseLexicon.is_part_of_speech(pos)
        
        DESCRIPTION
        is_part_of_speech(pos) returns True if the content of the argument
        pos is considered a valid part-of-speech label for the lexicon. 
        Otherwise, it returns False.
        
        VALUE
        <type 'bool'>
        """
        if LEX_POS not in self.provides:
            raise LexiconUnprovidedError(LEX_POS)
        else:
            return pos in self.pos_dict

    def check_pos_list(self, L):
        """ Returns the number of elements for which 
        Corpus.is_part_of_speech() is True, i.e. the number of
        elements that are considered a part of speech tag """
        count = 0
        for CurrentPos in L:
            if self.is_part_of_speech(CurrentPos):
                count += 1
        return count

    def get_other_wordforms(self, word):
        """ returns a list of word_id containing all other entries in the
        lexicon which have the same lemma as the word given as an argument.
        """ 
        raise CorpusUnsupportedFunctionError

    def get_posid_list(self, query_token):
        """ returns a list of all PosIds that match the query token. """
        raise CorpusUnsupportedFunctionError
    
    def get_wordid_list(self, query_token):
        """ returns a list of all word_ids that match the query token. """
        raise CorpusUnsupportedFunctionError
    
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
    wildcards = ["*", "?"]
    
    # Add internal table that can be used to access system information:
    coquery_query_string = "Query string"
    coquery_query_file = "Input file"
    coquery_current_date = "Current date"
    coquery_current_time = "Current time"
    
    def __init__(self, *args):
        self.table_dict = type(self).get_table_dict()
    
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
            if x != "coquery" and not "{}_table".format(x) in table_dict[x]:
                table_dict.pop(x)
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
        """ Return a table structure for the table 'rc_table'. 
        
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
                            i.e. the resource table string prefixed by COQ_"""
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
        corpus_table = table_dict["corpus"]
        lexicon_tables = cls.get_table_tree("word")

        corpus_variables = []
        for x in table_dict:
            if x not in lexicon_tables and x != "coquery":
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
        lexicon_tables = cls.get_table_tree("word")
        lexicon_variables = []
        for x in table_dict:
            if x in lexicon_tables and x != "coquery":
                for y in table_dict[x]:
                    if not y.endswith("_id") and not y.startswith("{}_table".format(x)):
                        lexicon_variables.append((y, type(cls).__getattribute__(cls, y)))    
        return lexicon_variables
    
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
    def translate_header(cls, header):
        """ Return a string that contains the display name for the header 
        string. Translation removes the 'coq_' prefix and any numerical 
        suffix, determines the resource feature from the remaining string,
        translates it to its display name, and returns the display name
        together with the numerical suffix attached."""
        
        if header in COLUMN_NAMES:
            return COLUMN_NAMES[header]
        
        if header.startswith("coq_"):
            header = header.partition("coq_")[2]
        header_fields = header.split("_")
        if len(header_fields) == 1:
            try:
                return COLUMN_NAMES[header_fields[0]]
            except KeyError:
                return header_fields[0].capitalize()
        if "_".join(header_fields[:-1]) in cls.get_resource_features():
            rc_feature = "_".join(header_fields[:-1])
            return "{}{}".format(type(cls).__getattribute__(cls, str(rc_feature)), header_fields[-1])
        return header
    
class BaseCorpus(object):
    provides = []
    
    def __init__(self, lexicon, resource):
        self.query_cache = {}
        self.lexicon = lexicon
        self.resource = resource

    def get_word_id(self, token_id):
        """ returns the word id of the token specified by token_id. """
        raise CorpusUnsupportedFunctionError
    
    def get_context(self, token_id):
        """ returns the context of the token specified by token_id. """
        raise CorpusUnsupportedFunctionError
    
    def get_context_header(self, max_number_of_tokens):
        if self.provides_feature(CORP_CONTEXT):
            L = []
            if options.cfg.context_columns:
                L += ["LC%s" % (x+1) for x in range(options.cfg.context_left)[::-1]]
                L += ["X%s" % (x+1) for x in range(max_number_of_tokens)]
                L += ["RC%s" % (x+1) for x in range(options.cfg.context_right)]
            else:
                L.append ("Context")
            return L
        else:
            raise CorpusUnsupportedFunctionError
        
    def get_context_sentence_header(self):
        return ["Sentence"]
        
    def get_source_info(self, source_id):
        """ returns a list containing the text information associated with 
        the text specified by TextId. If text_id == None, return a placeholder
        for failed queries. """
        raise CorpusUnsupportedFunctionError
    
    def get_source_info_header(self):
        raise CorpusUnsupportedFunctionError

    def get_speaker_info(self, speaker_id):
        """ returns a list containing the speaker information associated 
        with the speaker specified by speaker_id. """
        raise CorpusUnsupportedFunctionError

    def get_speaker_info_header(self):
        raise CorpusUnsupportedFunctionError

    def get_time_info(self, token_id):
        """ returns a list containing timing information associated 
        with the token_id. """
        raise CorpusUnsupportedFunctionError

    def get_time_info_header(self):
        raise CorpusUnsupportedFunctionError

    def get_file_info(self, source_id):
        """ returns a list containing filename information associated 
        with the source_id. """
        raise CorpusUnsupportedFunctionError

    def get_file_info_header(self):
        raise CorpusUnsupportedFunctionError

    def provides_feature(self, x):
        return x in self.provides + self.lexicon.provides

    def get_statistics(self):
        raise CorpusUnsupportedFunctionError
    
class SQLResource(BaseResource):
    wildcards = ["%", "_"]
    def has_wildcards(self, Token):
        """ 
        has_wildcards() returns True if the token string contains an SQL 
        wildcard, i.e. either % or _. """
        if len(Token.S) < 2:
            return False
        else:
            return any([x in self.wildcards for x in Token.S])
    
    def get_operator(self, Token):
        """ returns a string containing the appropriate operator for an 
        SQL query using the Token (considering wildcards and negation) """
        if options.cfg.regexp:
            return "REGEXP"
        if self.has_wildcards(Token):
            Operators = {True: "NOT LIKE", False: "LIKE"}
        else:
            Operators = {True: "!=", False: "="}
        return Operators [False]
    
    def __init__(self):
        super(SQLResource, self).__init__()

    def connect_to_database(self):
        self.DB = sqlwrap.SqlDB(Host=options.cfg.db_host, Port=options.cfg.db_port, User=options.cfg.db_user, Password=options.cfg.db_password, Database=self.db_name)
        logger.debug("Connected to database %s@%s:%s."  % (self.db_name, options.cfg.db_host, options.cfg.db_port))
        logger.debug("User=%s, password=%s" % (options.cfg.db_user, options.cfg.db_password))
        
        #create aliases for all tables for which no alias is specified:
        for x in dir(self):
            if x.endswith("_table"):
                if "{}_alias".format(x) not in dir(self):
                    self.__setattr__("{}_alias".format(x), self.__getattribute__(x))
                if "{}_construct".format(x) not in dir(self):
                    self.__setattr__("{}_construct".format(x), self.__getattribute__(x))
                  
    #@classmethod
    #def get_select_list(cls, base, rc_features):
        #""" Return a list of strings that contain all joins that are needed
        #to query the features in the list rc_features."""

        ## get a list of all tables that are required to query the requested
        ## features:
        #required_tables = {}
        #for rc_feature in [ResFeature(x) for x in rc_features]:
            #if rc_feature.table == "coquery_table":
                #continue
            #if rc_table not in required_tables and rc_table != corpus:
                #tree = cls.resource.get_table_structure(rc_table, options.cfg.selected_features)
                #parent = tree["parent"]
                #table_id = "{}_id".format(rc_feature.split("_")[0])
                #required_tables[rc_table] = tree
                #requested_features.append(table_id)
                #if parent:
                    #parent_id = "{}_{}".format(parent.split("_")[0], table_id)
                    #requested_features.append(parent_id)
        
        #join_strings = {}
        #join_strings[corpus] = "{} AS COQ_CORPUS_TABLE".format(corpus)
        #full_tree = cls.resource.get_table_structure("corpus_table", requested_features)
        #select_list = []
        #for rc_table in required_tables:
            #rc_tab = rc_table.split("_")[0]
            #sub_tree = cls.resource.get_sub_tree(rc_table, full_tree)
            #parent_tree = cls.resource.get_sub_tree(sub_tree["parent"], full_tree)
            #table = cls.resource.__getattribute__(rc_table)
            #if parent_tree:
                #rc_parent = parent_tree["rc_table_name"]
            #else:
                #rc_parent = None

            #column_list = []
            #for rc_feature in sub_tree["rc_requested_features"]:
                #name = "coq_{}_{}".format(
                    #rc_feature,
                    #number+1)
                #variable_string = "{} AS {}".format(
                    #cls.resource.__getattribute__(rc_feature),
                    #name)
                #column_list.append(variable_string)
                #if not rc_feature.endswith("_id"):
                    #select_list.append(name)
                
            #columns = ", ".join(column_list)
            
            #where_string = ""
            #if rc_table in rc_where_constraints:
            ##if rc_table == "word_table" and where_constraints:
                #where_string = "WHERE {}".format(" AND ".join(list(rc_where_constraints[rc_table])))

            #if rc_parent:
                #parent_id = "coq_{}_{}_id_{}".format(
                    #rc_parent.split("_")[0], 
                    #rc_table.split("_")[0],
                    #number+1)
                #child_id = "coq_{}_id_{}".format(
                    #rc_table.split("_")[0],
                    #number+1)
                
                #join_strings[rc_table] = "INNER JOIN (SELECT {columns} FROM {table} {where}) AS {alias} ON {parent_id} = {child_id}".format(
                    #columns = columns, 
                    #table = table,
                    #alias = sub_tree["alias"],
                    #parent = parent_tree["alias"],
                    #where = where_string,
                    #number = number+1,
                    #parent_id = parent_id,
                    #child_id = child_id)
            #else:
                #join_strings[rc_table] = "(SELECT {columns} FROM {table} {where}) AS {alias}".format(
                    #columns = columns, 
                    #table = table,
                    #alias = sub_tree["alias"],
                    #where = where_string)

        #output_columns = []
        #for x in options.cfg.selected_features:
            #if x in corpus_variables and number > 0:
                #break
            #rc_table = "{}_table".format(x.split("_")[0])
            #if rc_table == "coquery_table":
                #continue
            #tree = required_tables[rc_table]
            #output_columns.append("{}.{}{}".format(tree["alias"], cls.resource.__getattribute__(x), number + 1))
        
        #table_order = cls.resource.get_table_order(full_tree)
        #L = []
        #for x in table_order:
            #if x in join_strings:
                #if join_strings[x] not in L:
                    #L.append(join_strings[x])
        
        #if not select_list:
            #return "", None, None

class SQLLexicon(BaseLexicon):
    entry_cache = {}
    
    def sql_string_is_part_of_speech(self, pos):
        if LEX_POS not in self.provides:
            return False
        current_token = tokens.COCAToken(pos, self)
        if "pos_table" in dir(self.resource):
            return "SELECT {} FROM {} WHERE {} {} '{}' LIMIT 1".format(
                self.resource.pos_id, 
                self.resource.pos_table, 
                self.resource.pos_label,
                self.resource.get_operator(current_token),
                pos)
        else:
            return "SELECT {} FROM {} WHERE {} {} '{}' LIMIT 1".format(
                self.resource.word_pos,
                self.resource.word_table,
                self.resource.word_pos,
                self.resource.get_operator(current_token),
                pos)

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
            current_token = tokens.COCAToken(current_pos, self)
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
        # TODO: fix cfg.lemmatize
        # FIXME: this needs to be revised. 
        sub_clauses = []

        if token.lemma_specifiers:
            if LEX_LEMMA not in self.provides:
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
            if CurrentWord != "*":
                current_token = tokens.COCAWord(CurrentWord, self)
                current_token.negated = token.negated
                sub_clauses.append('%s %s "%s"' % (target, self.resource.get_operator(current_token), current_token))
                
        for current_transcript in token.transcript_specifiers:
            if current_transcript:
                current_token = tokens.COCAWord(current_transcript, self)
                current_token.negated = token.negated
                if "transcript_table" not in dir(self.resource):
                    target = "{}.{}".format(
                        self.resource.word_table, 
                        self.resource.word_transcript)
                elif self.resource.transcript_table != self.resource.word_table:
                    target = "TRANSCRIPT.{}".format(
                        self.resource.transcript_label)
                else:
                    target = "{}.{}".format(
                        self.resource.transcript_table,
                        self.resource.transcript_label)
                sub_clauses.append('%s %s "%s"' % (target, self.resource.get_operator(current_token), current_token))
        
        where_clauses = []
        
        if sub_clauses:
            where_clauses.append("(%s)" % " OR ".join (sub_clauses))
        if token.class_specifiers and LEX_POS in self.provides:
            where_clauses.append(self.sql_string_get_posid_list_where(token))
        return " AND ".join(where_clauses)
            
    def is_part_of_speech(self, pos):
        self.resource.DB.execute(self.sql_string_is_part_of_speech(pos), ForceExecution=True)
        query_result = self.resource.DB.fetch_all ()
        return len(query_result) > 0
    
    def get_other_wordforms(self, Word):
        if LEX_LEMMA not in self.provides:
            raise LexiconUnsupportedFunctionError
        
        current_word = tokens.COCAWord(Word, self)
        # create an inner join of lexicon, containing all rows that match
        # the string stored in current_word:
        self.resource.DB.execute(self.sql_string_get_other_wordforms(current_word))
        return [result[0] for result in self.resource.DB.Cur]

    def sql_string_get_entry(self, word_id, requested):
        # For the experimental stuff, this function needs to be incorporated
        # into sql_string_run_query_column_string() and
        # sql_string_run_query_table_string()
        
        if word_id == "NA":
            word_id = -1
        
        select_variable_list = []
        self.where_list = ["{}.{} = {}".format(
            self.resource.word_table,
            self.resource.word_id,
            word_id)]
        self.table_list = [self.resource.word_table]
        for current_attribute in requested:
            if current_attribute == LEX_WORDID:
                select_variable_list.append("{}.{}".format(
                    self.resource.word_table,
                    self.resource.word_id))
            
            if current_attribute == LEX_LEMMA:
                if "lemma_table" in dir(self.resource):
                    select_variable_list.append("COQ_LEMMA_TABLE.{}".format(
                        self.resource.lemma_label))
                    self.table_list.append("LEFT JOIN {} AS COQ_LEMMA_TABLE ON {}.{} = COQ_LEMMA_TABLE.{}".format(
                        self.resource.lemma_table,
                        self.resource.word_table,
                        self.resource.word_lemma_id,
                        self.resource.lemma_id))
                else:
                    select_variable_list.append("{}.{}".format(
                        self.resource.word_table,
                        self.resource.word_lemma))
            
            if current_attribute == LEX_ORTH:
                select_variable_list.append("{}.{}".format(
                    self.resource.word_table,
                    self.resource.word_label))
            
            if current_attribute == LEX_POS:
                if "pos_table" in dir(self.resource):
                    select_variable_list.append("PARTOFSPEECH.{}".format(
                        self.resource.pos_label))
                    self.table_list.append("LEFT JOIN {} AS PARTOFSPEECH ON {}.{} = PARTOFSPEECH.{}".format(
                        self.resource.pos_table,
                        self.resource.word_table,
                        self.resource.word_pos_id,
                        self.resource.pos_id))
                else:
                    select_variable_list.append("{}.{}".format(
                        self.resource.word_table,
                        self.resource.word_pos))
            
            if current_attribute == LEX_PHON:
                if "transcript_table" in dir(self.resource):
                    select_variable_list.append("TRANSCRIPT.{}".format(
                        self.resource.transcript_label))
                    self.table_list.append("LEFT JOIN {} AS TRANSCRIPT ON {}.{} = TRANSCRIPT.{}".format(
                        self.resource.transcript_table,
                        self.resource.word_table,
                        self.resource.word_transcript_id,
                        self.resource.transcript_id))
                else:
                    select_variable_list.append("{}.{}".format(
                        self.resource.word_table,
                        self.resource.word_transcript))
                
        select_variables = ", ".join(select_variable_list)
        select_string = ("SELECT {0} FROM {1}{2}".format(
            ", ".join(select_variable_list),
            " ".join(self.table_list),
            (" WHERE " + " AND ".join(self.where_list)) if self.where_list else ""))
        return select_string
    
    def get_entry(self, word_id, requested):
        # check if there is an entry in the cache for the word_id with the
        # requested features:
        if not tuple(requested) in self.entry_cache:
            self.entry_cache[tuple(requested)] = {}
        try:
            return self.entry_cache[tuple(requested)][word_id]
        except KeyError:
            pass

        # an entry has to provide at least LEX_ORTH:
        provide_fields = set(self.provides) & set(requested) | set([LEX_ORTH])
        error_value = ["<NA>"] * (len(self.provides) - 1)
        entry = self.Entry(provide_fields)
        S = self.sql_string_get_entry(word_id, provide_fields)
        self.resource.DB.execute(S)
        query_results = self.resource.DB.Cur.fetchone()
        if query_results:
            entry.set_values(query_results)
        else:
            entry.set_values(error_value)
            
        # add entry to cache:
        self.entry_cache[tuple(requested)][word_id] = entry
        return entry

    def sql_string_get_posid_list(self, token):
        where_string = self.sql_string_get_posid_list_where(token)

        if "pos_table" in dir(self.resource):
            return "SELECT DISTINCT {word_table}.{word_pos} FROM {word_table} INNER JOIN {pos_table} ON {pos_table}.{pos_id} = {word_table}.{word_pos} WHERE {where_string}".format(
                word_pos=self.resource.word_pos_id,
                word_table=self.resource.word_table,
                pos_table=self.resource.pos_table,
                pos_id=self.resource.pos_id,
                where_string=where_string)
        else:
            return "SELECT DISTINCT {} FROM {} WHERE {}".format(
                self.resource.word_pos, self.resource.word_table, where_string)

    def get_posid_list(self, token):
        print(1)
        S = self.sql_string_get_posid_list(token)
        self.resource.DB.execute(S)
        return [x[0] for x in self.resource.DB.fetch_all()]

    def sql_string_get_matching_wordids(self, token):
        """ returns a string that may be used to query all word_ids that
        match the token specification."""
        # FIXME: This doesn't seem to work correctly; apparently, the
        # returned word_ids are not unique.
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
        if token.S == "*":
            return []
        self.resource.DB.execute(self.sql_string_get_matching_wordids(token))
        query_results = self.resource.DB.fetch_all ()
        if not query_results:
            return [-1]
        else:
            return [x[0] for x in query_results]
        
    def get_statistics(self):
        stats = {}
        stats["lexicon_features"] = " ".join(self.provides)
        stats["lexicon_variables"] = " ".join([x for x, _ in self.resource.get_lexicon_features()])
        self.resource.DB.execute("SELECT COUNT(*) FROM {word_table}".format(
            word_table=self.resource.word_table))
        stats["lexicon_words"] = self.resource.DB.Cur.fetchone()[0]
        if LEX_POS in self.provides:
            if "pos_table" in dir(self.resource):
                self.resource.DB.execute("SELECT COUNT(DISTINCT {}) FROM {}".format(
                    self.resource.pos_id, self.resource.pos_table))
            else:
                self.resource.DB.execute("SELECT COUNT(DISTINCT {}) FROM {}".format(
                    self.resource.word_pos, self.resource.word_table))
            stats["lexicon_distinct_pos"] = self.resource.DB.Cur.fetchone()[0]
        if LEX_LEMMA in self.provides:
            if "lemma_table" in dir(self.resource):
                lemma_table = self.resource.lemma_table
                lemma_label = self.resource.lemma_label
            else:
                lemma_table = self.resource.word_table
                lemma_label = self.resource.word_lemma
            self.resource.DB.execute("SELECT COUNT(DISTINCT {}) FROM {}".format(
                lemma_label, lemma_table))
            stats["lexicon_lemmas"] = self.resource.DB.Cur.fetchone()[0]
        return stats

class SQLCorpus(BaseCorpus):
    def __init__(self, lexicon, resource):
        super(SQLCorpus, self).__init__(lexicon, resource)
        self.query_results = None

    def sql_string_get_word_id_of_token(self, token_id):
        return "SELECT {} FROM {} WHERE {} = {} LIMIT 1".format(
            self.resource.corpus_word_id,
            self.resource.corpus_table,
            self.resource.corpus_id,
            token_id)
    
    def get_word_id(self, token_id):
        self.resource.DB.execute(self.sql_string_get_word_id_of_token(token_id))
        return self.resource.DB.Cur.fetchone()[0]
        
    def sql_string_run_query_textfilter(self, Query, self_join):

        Genres, Years, Negated = tokens.COCATextToken(Query.source_filter, self.lexicon).get_parse()
        filters = []
        genre_clauses = []
        if any(x.count("source_info_genre") for x in dir(self.resource)):
            if self_join:
                source_table = self.resource.corpus_denorm_table
                try:
                    source_genre = self.resource.corpus_denorm_source_info_genre
                except AttributeError as e:
                    raise e
            else:
                source_table = self.resource.source_table_alias
            for current_genre in Genres:
                if current_genre != "*":
                    if "*" in current_genre:
                        Operator = "LIKE"
                        current_genre = current_genre.replace ("*", "%")
                    else:
                        Operator = "="
                    genre_clauses.append("{}.{} {} '{}'".format(
                        source_table, 
                        self.resource.source_info_genre,
                        Operator, current_genre))
        
        selected_years = []
        if "source_info_year" in dir(self.resource):
            for current_year in Years:
                if current_year.count ("-") == 1:
                    Low, High = current_year.split("-")
                    try:
                        selected_years += [str(x) for x in range(int(Low), int(High)+1)]
                    except:
                        raise InvalidFilterError
                else:
                    selected_years.append(current_year)
        
        if genre_clauses:
            filters.append(" OR ".join(genre_clauses))
        if selected_years:
            filters.append(" OR ".join(
                ["{}.{} LIKE '%{}%'".format(
                    self.resource.source_table_alias,
                    self.resource.source_info_year, 
                    x)
                    for x in selected_years]))
        
        filter_string = " AND ".join(["({})".format(x) for x in filters])
        
        if filter_string:
            if Negated:
                return "NOT ({})".format(filter_string)
            else:
                return "{}".format(filter_string)
        raise InvalidFilterError
    
    def sql_string_table_for_token(self, Query, number, token, requested, self_joined=False):
        def add_word_table(corpus_table, corpus_word_id):
            self.table_list.add(self.resource.word_table)
            self.table_list.add(corpus_table)
            self.where_list.add("{}.{} = {}.{}".format(
                        corpus_table,
                        corpus_word_id,
                        self.resource.word_table, 
                        self.resource.word_id))
            
        def get_where_list_entries(specifiers, table, label):
            """ create a list of WHERE conditions depending on the 
            strings in the specifiers. Strings containing wildcards will
            be included by separate LIKE conditions. Strings without
            wildcards will be included in a single IN (or =) condition."""
            entries = set([])
            like_list = set([])
            is_list = set([])
            
            for x in specifiers:
                if x not in self.resource.wildcards and x != "*":
                    if any([y in x for y in self.resource.wildcards]):
                        like_list.add(x)
                    else:
                        is_list.add(x)
            if is_list:
                if len(is_list) == 1:
                    entries.add('{}.{} = "{}"'.format(
                        table, label, ", ".join(is_list)))
                else:
                    entries.add('{}.{} IN ({})'.format(
                        table, label, ", ".join(['"{}"'.format(x) for x in is_list])))
            if like_list:
                entries.add(" OR ".join(
                    ['{}.{} LIKE "{}"'.format(
                        table, label, x) for x in like_list]))
            return entries
            
        self.where_list = set([])
        self.table_list = set([])
        self.column_list = set([])
        
        if options.cfg.experimental:
            operator = self.resource.get_operator(token)

            if not self_joined:
                self.column_list.add("{}.{}".format(
                    self.resource.corpus_table, self.resource.corpus_id))
                self.table_list.add(self.resource.corpus_table)
                if token != "*" or LEX_ORTH in requested:
                    add_word_table(self.resource.corpus_table, self.resource.corpus_word_id)
                if options.cfg.source_filter and number == 1:
                    self.table_list.add(self.resource.corpus_table)
                    if "source_table" in dir(self.resource):
                        self.table_list.add(self.resource.source_table)
                        self.where_list.add("{}.{} = {}.{}".format(
                            self.resource.source_table,
                            self.resource.source_id,
                            self.resource.corpus_table,
                            self.resource.corpus_source_id))
                    self.column_list.add("{}.{}".format(
                        self.resource.corpus_table,
                        self.resource.corpus_source_id))
                    self.where_list.add(self.sql_string_run_query_textfilter(Query, self_joined))
            else:
                self.column_list.add("{}.{} AS COQ_WORD_ID".format(
                    self.resource.word_table, self.resource.word_id))

            if LEX_ORTH in requested or CORP_CONTEXT in requested or token.word_specifiers:
                word_table = self.resource.word_table
                word_label = self.resource.word_label
                if token != "*" or LEX_ORTH in requested:
                    self.table_list.add(word_table)
            if LEX_ORTH in requested:
                self.column_list.add("{}.{} AS COQ_WORD_LABEL".format(
                    word_table, word_label))
            if token.word_specifiers:
                self.where_list.update(get_where_list_entries(token.word_specifiers, word_table, word_label))

            if LEX_LEMMA in requested or token.lemma_specifiers:
                if "lemma_table" in dir(self.resource):
                    self.where_list.add("{}.{} = {}.{}".format(
                        self.resource.lemma_table,
                        self.resource.lemma_id,
                        self.resource.word_table,
                        self.resource.word_lemma_id))
                    lemma_table = self.resource.lemma_table
                    lemma_label = self.resource.lemma_id
                else:
                    lemma_table = self.resource.word_table
                    lemma_label = self.resource.word_lemma
                self.table_list.add(lemma_table)
            if LEX_LEMMA in requested:
                self.column_list.add("{}.{} AS COQ_LEMMA_LABEL".format(
                    lemma_table, lemma_label))
            if token.lemma_specifiers:
                self.where_list.update(get_where_list_entries(token.lemma_specifiers, lemma_table, lemma_label))

            if LEX_PHON in requested or token.transcript_specifiers:
                if "transcript_table" in dir(self.resource):
                    self.where_list.add("{}.{} = {}.{}".format(
                        self.resource.transcript_table,
                        self.resource.transcript_id,
                        self.resource.word_table,
                        self.resource.word_transcript_id))
                    transcript_table = self.resource.transcript_table
                    transcript_label = self.resource.transcript_id
                else:
                    transcript_table = self.resource.word_table
                    transcript_label = self.resource.word_transcript
                self.table_list.add(transcript_table)
            if LEX_PHON in requested:
                self.column_list.add("{}.{} AS COQ_PHON_LABEL".format(
                    transcript_table, transcript_label))
            if token.transcript_specifiers:
                self.where_list.update(get_where_list_entries(token.transcript_specifiers, transcript_table, transcript_label))

            if LEX_POS in requested or token.class_specifiers:
                if "pos_table" in dir(self.resource):
                    self.where_list.add("{}.{} = {}.{}".format(
                        self.resource.pos_table,
                        self.resource.pos_id,
                        self.resource.word_table,
                        self.resource.word_pos_id))
                    pos_table = self.resource.pos_table
                    pos_label = self.resource.pos_label
                else:
                    pos_table = self.resource.word_table
                    pos_label = self.resource.word_pos
                self.table_list.add(pos_table)
            if LEX_POS in requested:
                self.column_list.add("{}.{} AS COQ_POS_LABEL".format(
                    pos_table, pos_label))
            if token.class_specifiers:
                self.where_list.update(
                    get_where_list_entries(token.class_specifiers, pos_table, pos_label))

            table_string = "SELECT {} FROM {}".format(
                    ", ".join (self.column_list),
                    ", ".join (self.table_list))
            if self.where_list:
                if token.negated:
                    table_string = "{} WHERE NOT ({})".format(
                        table_string, " AND ".join ([x for x in self.where_list if x]))
                else:
                    table_string = "{} WHERE {}".format(
                        table_string, " AND ".join ([x for x in self.where_list if x]))


            if number:
                table_string = "({}) AS e{}".format(table_string, number)
        # Stable version follows:
        else:
            self.column_list.add("{}.{}".format(
                self.resource.corpus_table, 
                self.resource.corpus_word_id))
            self.table_list.add(self.resource.corpus_table)

            if CORP_CONTEXT in self.provides:
                self.column_list.add("{}.{}".format(
                    self.resource.corpus_table,
                    self.resource.corpus_id))
                self.table_list.add(self.resource.corpus_table)
            if number == 1:
                if options.cfg.filter_list:
                    filters = self.resource.translate_filters(options.cfg.filter_list)
                    
                    for filt in filters:
                        display_column, corpus_feature, table, operator, value_list, value_range = filt
                        if operator.upper() == "LIKE":
                            if "*" not in value_list[0]:
                                value_list[0] = "*{}*".format(value_list[0])
                            value_list[0] = value_list[0].replace("*", "%")
                            value_list[0] = value_list[0].replace("?", "_")
                                                    
                        table_name = corpus_feature.partition("_")[0]
                        table_path = self.resource.get_table_path("corpus", table_name)
                        if table_path:
                            for x in table_path[1:]:
                                real_table_name = self.resource.__getattribute__("{}_table".format(x))
                                real_id_name = self.resource.__getattribute__("{0}_id".format(x))
                                
                                self.table_list.add(real_table_name)
                                self.column_list.add("{}.{}".format(real_table_name, real_id_name))
                
                if CORP_SOURCE in requested or CORP_FILENAME in requested or CORP_CONTEXT in requested or options.cfg.source_filter:
                    self.table_list.add(self.resource.corpus_table)
                    if "corpus_source_id" in dir(self.resource):
                        source = self.resource.corpus_source_id
                    else:
                        source = self.resource.corpus_file_id
                    self.column_list.add("{}.{}".format(
                        self.resource.corpus_table,
                        source))

            if (token.class_specifiers and LEX_POS in self.lexicon.provides):
                self.table_list.add(self.resource.word_table)
                self.where_list.add("{}.{} = {}.{}".format(
                self.resource.corpus_table,
                self.resource.corpus_word_id,
                self.resource.word_table,
                self.resource.word_id))
                if "pos_table" not in dir(self.resource):
                    # CASE 1:
                    # No separate pos_table, POS is stored as a column in
                    # word_table:
                    self.column_list.add("{}.{}".format(
                        self.resource.word_table,
                        self.resource.word_pos))
                #self.column_list.add("{}.{}".format(
                    #self.resource.word_table,
                    #self.resource.word_pos_id))
                #self.table_list.add(self.resource.word_table)
                #self.where_list.add("{}.{} = {}.{}".format(
                    #self.resource.corpus_table,
                    #self.resource.corpus_word_id,
                    #self.resource.word_table,
                    #self.resource.word_id))
                #if "pos_table" not in dir(self.resource):
                    ## CASE 1:
                    ## No separate pos_table, POS is stored as a column in
                    ## word_table:
                    #self.where_list.add("{}.{} = {}.{}".format(
                        #self.resource.corpus_table,
                        #self.resource.corpus_word_id,
                        #self.resource.word_table,
                        #self.resource.word_id))
                else:
                    # CASE 2:
                    # POS stored in pos_table indexed by pos_id
                    self.column_list.add("{}.{}".format(
                        self.resource.word_table,
                        self.resource.word_pos_id))
                    self.where_list.add("{}.{} = COQ_POS_TABLE.{}".format(
                        self.resource.word_table,
                        self.resource.word_pos_id,
                        self.resource.pos_id))
                    self.table_list.add("{} AS COQ_POS_TABLE".format(self.resource.pos_table))
                    self.table_list.add(self.resource.word_table)
                    
            table_string = "SELECT {} FROM {}".format(
                    ", ".join (self.column_list),
                    ", ".join (self.table_list))
            if self.where_list:
                table_string = "{} WHERE {}".format(
                    table_string, " AND ".join (self.where_list))

            if number:
                table_string = "({}) AS e{}".format(table_string, number)
        return table_string
    
    def sql_string_run_query_source_table_string(self, Query, self_joined):
        if self_joined:
            corpus_table = self.resource.corpus_denorm_table
        else:
            corpus_table = "e1"
            
        if options.cfg.experimental:
            if self_joined:
                return ""
            else:
                return "INNER JOIN {source_table} ON ({corpus_table}.{corpus_source} = {source_table_alias}.{source_id})".format(
                    corpus_table=corpus_table,
                    corpus_source=self.resource.corpus_source_id,
                    source_table=self.resource.source_table_construct,
                    source_table_alias=self.resource.source_table_alias,
                    source_id=self.resource.source_id)
        else:
            if self_joined:
                return ""
            else:
                return "INNER JOIN {source_table} ON ({corpus_table}.{corpus_source} = {source_table_alias}.{source_id})".format(
                corpus_table=corpus_table,
                corpus_source=self.resource.corpus_source_id,
                source_table=self.resource.source_table_construct,
                source_table_alias=self.resource.source_table_alias,
                source_id=self.resource.source_id)
    
    def sql_string_run_query_table_string(self, Query, self_joined):        
        
        table_string_list = []
        
        if self_joined:
            if options.cfg.experimental:
                # self_joined, experimental
                table_string_list.append(self.resource.corpus_denorm_table)
                corpus_table = self.resource.corpus_denorm_table
                
                for i, current_token in enumerate(Query.tokens):
                    table_string_list.append(
                        "INNER JOIN {table} ON (e{num}.COQ_WORD_ID = {corpus}.W{num})".format(
                            table = self.sql_string_table_for_token(Query, i+1, current_token, Query.Session.output_fields, self_joined),
                            num = i + 1,
                            corpus = self.resource.corpus_denorm_table))
            else:
                # self_joined, old:
                table_string_list.append(self.resource.corpus_denorm_table)
                corpus_table = self.resource.corpus_denorm_table
        else:
            # not self_joined, both
            if options.cfg.source_filter:
                self.source_filter_string = self.sql_string_run_query_textfilter(Query, self_joined)
            corpus_table = "e1"
            for i, current_token in enumerate (Query.tokens):
                table_string = self.sql_string_table_for_token(Query, i+1, current_token, Query.Session.output_fields)
                if len(table_string_list) > 0:
                    table_string = "INNER JOIN {table_string} ON (e{num1}.{token_id} = e1.{token_id} + {num})".format(
                        table_string=table_string,
                        token_id=self.resource.corpus_id,
                        num1=i+1, num=i)
                table_string_list.append(table_string)

        if options.cfg.experimental:
            if self_joined:
                for i in range(options.cfg.context_left):
                    table_string_list.append(
                        "INNER JOIN (SELECT {corpus}.{token_id}, {word}.{label} AS RC{num} FROM {corpus}, {word} WHERE {corpus}.{corpus_word_id} = {word}.{word_id}) AS cr{num} ON (cr{num}.{token_id} = {corpusBig}.{token_id} + {offset})".format(
                            num=i + 1,
                            corpus=self.resource.corpus_table,
                            token_id=self.resource.corpus_id,
                            corpus_word_id=self.resource.corpus_word_id,
                            word=self.resource.word_table,
                            word_id=self.resource.word_id,
                            corpusBig=self.resource.corpus_denorm_table,
                            offset=i + Query.number_of_tokens,
                            label=self.resource.word_label))
                for i in range(options.cfg.context_right):
                    table_string_list.append(
                        "INNER JOIN (SELECT {corpus}.{token_id}, {word}.{label} AS LC{num} FROM {corpus}, {word} WHERE {corpus}.{corpus_word_id} = {word}.{word_id}) AS cl{num} ON (cl{num}.{token_id} = {corpusBig}.{token_id} - {num})".format(
                            num=i + 1,
                            corpus=self.resource.corpus_table,
                            token_id=self.resource.corpus_id,
                            corpus_word_id=self.resource.corpus_word_id,
                            word=self.resource.word_table,
                            word_id=self.resource.word_id,
                            corpusBig=self.resource.corpus_denorm_table,
                            label=self.resource.word_label))
            else:
                for i in range(options.cfg.context_left):
                    table_string_list.append(
                        "INNER JOIN (SELECT {corpus}.{token_id}, {word}.{label} AS RC{num} FROM {corpus}, {word} WHERE {corpus}.{corpus_word_id} = {word}.{word_id}) AS cr{num} ON (cr{num}.{token_id} = {corpus}.{token_id} + {num})".format(
                            num=i + 1,
                            corpus=self.resource.corpus_table,
                            token_id=self.resource.corpus_id,
                            corpus_word_id=self.resource.corpus_word_id,
                            word=self.resource.word_table,
                            word_id=self.resource.word_id,
                            label=self.resource.word_label))
                for i in range(options.cfg.context_right):
                    table_string_list.append(
                        "INNER JOIN (SELECT {corpus}.{token_id}, {word}.{label} AS LC{num} FROM {corpus}, {word} WHERE {corpus}.{corpus_word_id} = {word}.{word_id}) AS cl{num} ON (cl{num}.{token_id} = {corpus}.{token_id} - {num})".format(
                            num=i + 1,
                            corpus=self.resource.corpus_table,
                            token_id=self.resource.corpus_id,
                            corpus_word_id=self.resource.corpus_word_id,
                            word=self.resource.word_table,
                            word_id=self.resource.word_id,
                            label=self.resource.word_label))

        if Query.source_filter and not options.cfg.experimental:
            if self.resource.source_table_alias != self.resource.corpus_table:
                
                table_string_list.append(self.sql_string_run_query_source_table_string(Query, self_joined))
        if options.cfg.verbose:
            return "\n\t".join(table_string_list)
        else:
            return " ".join(table_string_list)

    def get_frequency(self, token):
        """ Return a longint that gives the corpus frequency of the token,
        taking the filter list from options.cfg.filter_list into account."""
        pass

    def get_whereclauses(self, Token, WordTarget, PosTarget):
        if not Token:
            return []

        where_clauses = []
        if self.resource.name == "coca":
            L = set(self.lexicon.get_matching_wordids(Token))
            if L:
                where_clauses = ["{} IN ({})".format(
                    WordTarget, ", ".join(["{}".format(x) for x in L]))]
            return where_clauses
    
        if Token.word_specifiers or Token.lemma_specifiers or Token.transcript_specifiers:
            L = set(self.lexicon.get_matching_wordids(Token))
            if L:
                where_clauses.append("%s IN (%s)" % (WordTarget, ", ".join (map (str, L))))
        else:
            if Token.class_specifiers:
                L = self.lexicon.get_posid_list(Token)
                if L: 
                    where_clauses.append("%s IN (%s)" % (PosTarget, ", ".join (["'%s'" % x for x in L])))
        return where_clauses
        #return where_clauses
    
    def sql_string_run_query_where_string(self, Query, self_joined):
        where_clauses = []

        where_clauses = self.sql_string_run_query_filter_list(Query, self_joined)

        if Query.source_filter:
            where_clauses = [self.sql_string_run_query_textfilter(Query, self_joined)]
            
        for i, current_token in enumerate (Query.tokens):
            if self_joined:
                current_where_clauses = self.get_whereclauses(
                    current_token, 
                    "W{}".format(i+1),
                    "P{}".format(i+1))
                if current_where_clauses:
                    if not current_token.negated:
                        where_clauses.append(" AND ".join(current_where_clauses))
                    else:
                        where_clauses.append("NOT ({})".format(
                            " AND ".join(current_where_clauses)))
            else:
                corpus_word_id = self.resource.corpus_word_id
                if "pos_table" not in dir(self.resource):
                    word_pos_column = self.resource.word_pos
                else:
                    word_pos_column = self.resource.word_pos_id
                current_where_clauses = self.get_whereclauses(
                    current_token, 
                    corpus_word_id, 
                    word_pos_column)
                prefixed_clauses = ["e{num}.{clause}".format(
                    num=i+1, 
                    clause=clause) for clause in current_where_clauses]
                if prefixed_clauses:
                    if not current_token.negated:
                        where_clauses.append(" AND ".join(prefixed_clauses))
                    else:
                        where_clauses.append("NOT ({})".format(" AND ".join(prefixed_clauses)))
        if options.cfg.verbose:
            return  " AND\n\t".join(where_clauses)
        else:
            return  " AND ".join(where_clauses)
        
    def sql_string_run_query_column_string(self, Query, self_joined, only_names=False):
        """
        # Create a list of the columns that the query should return:
        # - a Wx column for each query token
        # - a TokenId column if context is requested
        # - a SourceId column if context, the source or the filename is
        #   requested"""

        self.column_list = set([])
        
        # make the experimental query mode the default for frequency queries 
        # with exactly one token, but optional otherwise:
        if options.cfg.experimental or (options.cfg.MODE == QUERY_MODE_FREQUENCIES and (len(Query.Session.output_fields) == 1) and not only_names):
            # add token_id if needed:
            if options.cfg.context_span or options.cfg.context_columns:
                if self_joined:
                    corpus_table = self.resource.corpus_denorm_table
                else:
                    corpus_table = self.resource.corpus_table
                self.column_list.add("{}.{} AS TokenId".format(
                    corpus_table, self.resource.corpus_id))
            # add source_id if needed:
            if options.cfg.show_filename or options.cfg.show_source:
                self.column_list.add("{} AS SourceId".format(
                    self.resource.corpus_source_id))
                
            if options.cfg.show_orth or options.cfg.context_span or options.cfg.context_columns:
                self.column_list.update(["e{num}.COQ_WORD_LABEL AS W{num}_orth".format(num=x+1) for x in range(Query.number_of_tokens)])
            if options.cfg.show_phon:
                self.column_list.update(["e{num}.COQ_PHON_LABEL AS W{num}_phon".format(num=x+1) for x in range(Query.number_of_tokens)])
            if options.cfg.show_lemma:
                self.column_list.update(["e{num}.COQ_LEMMA_LABEL AS L{num}_orth".format(num=x+1) for x in range(Query.number_of_tokens)])                    
            if options.cfg.show_pos:
                self.column_list.update(["e{num}.COQ_POS_LABEL AS W{num}_pos".format(num=x+1) for x in range(Query.number_of_tokens)])
                
            if options.cfg.context_left or options.cfg.context_right:
                self.column_list.update(["cl{num}.LC{num}".format(num=x+1) for x in range(options.cfg.context_left)])
                self.column_list.update(["cr{num}.RC{num}".format(num=x+1) for x in range(options.cfg_context_right)])
            
            # use new frequency query mode:
            if (options.cfg.MODE == QUERY_MODE_FREQUENCIES) and not only_names:
                self.column_list.add("COUNT(*) AS {}".format(options.cfg.freq_label))                    
                
            if not self.column_list and not only_names:
                self.column_list.add("e1.{} AS TokenId".format(
                        self.resource.corpus_id))
                
            if self_joined and not options.cfg.experimental and len(Query.Session.output_fields) > 1:
                self.column_list.update(["{}.W{}".format(
                    self.resource.corpus_denorm_table,
                    x+1) for x in range(Query.number_of_tokens)])        
                

        else:
            if self_joined:
                ## construct a list of all tokens that are not empty:
                #non_empty_token = [x for x in range(Query.number_of_tokens) if Query.tokens[x] != "*"]
                non_empty_token = range(Query.number_of_tokens)
                self.column_list.add("{}.{} AS TokenId".format(
                    self.resource.corpus_denorm_table,
                    self.resource.corpus_id))
                if any([x in Query.Session.output_fields for x in [CORP_SOURCE, CORP_FILENAME, CORP_CONTEXT]]):
                    self.column_list.add("{}.{} AS SourceId".format(
                        self.resource.corpus_denorm_table,
                        self.resource.corpus_source_id))
                self.column_list.update(["{}.W{}".format(
                    self.resource.corpus_denorm_table,
                    x+1) for x in non_empty_token])        
            else:
                if CORP_CONTEXT in self.provides:
                    self.column_list.add("e1.{} AS TokenId".format(
                        self.resource.corpus_id))
                if any([x in Query.Session.output_fields for x in [CORP_SOURCE, CORP_CONTEXT]]):
                    if "corpus_source_id" in dir(self.resource):
                        source = self.resource.corpus_source_id
                    else:
                        source = self.resource.corpus_file_id
                    self.column_list.add("e1.{} AS SourceId".format(source))
                self.column_list.update(["e{num}.{corpus_word} AS W{num}".format(num=x+1, corpus_word=self.resource.corpus_word_id) for x in range(Query.number_of_tokens)])
               
        if only_names:
            return ", ".join([x.rpartition(" AS ")[-1] for x in self.column_list])
        if options.cfg.verbose:
            return ",\n\t".join(self.column_list)
        else:
            return ", ".join(self.column_list)
    
    def sql_string_run_query_filter_list(self, Query, self_joined):
        filter_list = self.resource.translate_filters(options.cfg.filter_list)
        L = []
        for column, corpus_feature, table, operator, value_list, val_range in filter_list:
            s = ""
            if val_range:
                s = "{}.{} BETWEEN {} AND {}".format(table, column, min(val_range), max(val_range))
            else:
                if len(value_list) > 1:
                    if any([x in self.wildcards for x in value_list]):
                        s = " OR ".join(["{}.{} LIKE {}".format(table, column, x) for x in value_list])
                        
                    else:
                        s = "{}.{} IN ({})".format(table, column, ", ".join(["'{}'".format(x) for x in value_list]))
                else:
                    s = "{}.{} = '{}'".format(table, column, value_list[0]) 
            L.append(s)
        return L

    def sort_output_columns(self, output_columns, expected_columns):
        """ Return a list of output columns for the corpus query. The 
        returned list has the order and number of columns as expected so that
        the results from the database query can be directly used as output in
        the results table."""
        # FIXME: This is not working yet.
        return output_columns
    
    def get_sub_query_string(self, current_token, number, self_joined=False):
        """ Return a MySQL string that selects a table matching the current
        token, and which includes all columns that are requested, or which
        are required to join the tables. """
            
        # corpus variables will only be included in the subquery string if 
        # this is the first subquery.
        corpus_variables = [x for x, _ in self.resource.get_corpus_features()]
        if number == 0:
            requested_features = [x for x in options.cfg.selected_features]
            
            # if a GUI is used, include source features so the entries in the
            # result table can be made clickable to show the context:
            
            # in order to make this not depend on a fixed database layout 
            # (here: 'source' and 'file' tables), we should check for any
            # table that corpus_table is linked to except for word_table
            # (and all child tables).            
            if "source_id" in dir(self.resource):
                requested_features.append("source_id")
                options.cfg.context_source_id = "source_id"
            elif "file_id" in dir(self.resource):
                requested_features.append("file_id")
                options.cfg.context_source_id = "file_id"

            #if options.cfg.MODE != QUERY_MODE_FREQUENCIES and (options.cfg.context_left or options.cfg.context_right):
                #if "source_id" in dir(self.resource):
                    #requested_features.append("source_id")
                    #options.cfg.context_source_id = "source_id"
                #elif "file_id" in dir(self.resource):
                    #requested_features.append("file_id")
                    #options.cfg.context_source_id = "file_id"
        else:
            requested_features = [x for x in options.cfg.selected_features if not x in corpus_variables]

        # add all features that are required for the query filters:
        rc_where_constraints = {}
        if number == 0:
            for filt in self.resource.translate_filters(options.cfg.filter_list):
                variable, rc_feature, table_name, op, value_list, _value_range = filt
                if op.upper() == "LIKE":
                    if "*" not in value_list[0]:
                        value_list[0] = "*{}*".format(value_list[0])
                    value_list[0] = value_list[0].replace("*", "%")
                    value_list[0] = value_list[0].replace("?", "_")

                if rc_feature not in requested_features:
                    requested_features.append(rc_feature)
                rc_table = "{}_table".format(rc_feature.partition("_")[0])
                if rc_table not in rc_where_constraints:
                    rc_where_constraints[rc_table] = set([])
                rc_where_constraints[rc_table].add(
                    '{} {} "{}"'.format(
                        self.resource.__getattribute__(rc_feature), op, value_list[0]))

        if current_token.word_specifiers or current_token.transcript_specifiers or current_token.class_specifiers:
            requested_features.append("corpus_word_id")

        # add requested features depending on the token specifications:
        if current_token.word_specifiers:
            if "word_label" in dir(self.resource):
                requested_features.append("word_label")
        if current_token.transcript_specifiers:
            if "transcript_label" in dir(self.resource):
                requested_features.append("word_transcript")
            elif "transcript_label" in dir(self.resource):
                requested_features.append("transcript_label")
        if current_token.class_specifiers:
            if "word_pos" in dir(self.resource):
                requested_features.append("word_pos")
            elif "pos_label" in dir(self.resource):
                requested_features.append("pos_label")
        if current_token.lemma_specifiers:
            if "word_lemma" in dir(self.resource):
                requested_features.append("word_lemma")
            elif "lemma_label" in dir(self.resource):
                requested_features.append("lemma_label")

        # get a list of all tables that are required to query the requested
        # features:
        required_tables = {}
        for rc_feature in requested_features:
            rc_table = "{}_table".format(rc_feature.split("_")[0])
            if rc_table == "coquery_table":
                continue
            if rc_table not in required_tables:
                tree = self.resource.get_table_structure(rc_table, options.cfg.selected_features)
                parent = tree["parent"]
                table_id = "{}_id".format(rc_feature.split("_")[0])
                required_tables[rc_table] = tree
                requested_features.append(table_id)
                if parent:
                    parent_id = "{}_{}".format(parent.split("_")[0], table_id)
                    requested_features.append(parent_id)
        
        join_strings = {}
        join_strings[self.resource.corpus_table] = "{} AS COQ_CORPUS_TABLE".format(self.resource.corpus_table)
        full_tree = self.resource.get_table_structure("corpus_table", requested_features)

        try:
            if "pos_table" not in dir(self.resource):
                word_pos_column = self.resource.word_pos
            else:
                word_pos_column = self.resource.word_pos_id
        except AttributeError:
            word_pos_column = None
        
        #where_constraints = set([])
        sub_list = set([])
        for x in self.get_whereclauses(current_token, self.resource.word_id, word_pos_column):
            if x: 
                sub_list.add(x)
        if sub_list:
            if current_token.negated:
                s = "NOT ({})".format(" AND ".join(sub_list))
            else:
                s = " AND ".join(sub_list)
            if "word_table" not in rc_where_constraints:
                rc_where_constraints["word_table"] = set([])
            rc_where_constraints["word_table"].add(s)
            #if "corpus_table" not in rc_where_constraints:
                #rc_where_constraints["corpus_table"] = set([])
            #rc_where_constraints["corpus_table"].add(s)
            
        #print(rc_where_constraints)
        #print(required_tables)

        select_list = set([])
        for rc_table in required_tables:
            #print(rc_table)
            rc_tab = rc_table.split("_")[0]
            sub_tree = self.resource.get_sub_tree(rc_table, full_tree)
            parent_tree = self.resource.get_sub_tree(sub_tree["parent"], full_tree) 
            table = self.resource.__getattribute__(rc_table)
            if parent_tree:
                rc_parent = parent_tree["rc_table_name"]
            else:
                rc_parent = None

            column_list = []
            for rc_feature in sub_tree["rc_requested_features"]:
                name = "coq_{}_{}".format(
                    rc_feature,
                    number+1)
                variable_string = "{} AS {}".format(
                    self.resource.__getattribute__(rc_feature),
                    name)
                column_list.append(variable_string)
                #if not rc_feature.endswith("_id"):
                select_list.add(name)
                
            columns = ", ".join(column_list)
            #print("columns", columns)
            #print("select", select_list)
            where_string = ""
            if rc_table in rc_where_constraints:
                where_string = "WHERE {}".format(" AND ".join(list(rc_where_constraints[rc_table])))
                #print(where_string)

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

        output_columns = []
        for x in options.cfg.selected_features:
            if x in corpus_variables and number > 0:
                break
            rc_table = "{}_table".format(x.split("_")[0])
            if rc_table == "coquery_table":
                continue
            tree = required_tables[rc_table]
            output_columns.append("{}.{}{}".format(tree["alias"], self.resource.__getattribute__(x), number + 1))
        
        table_order = self.resource.get_table_order(full_tree)
        L = []
        for x in table_order:
            if x in join_strings:
                if join_strings[x] not in L:
                    L.append(join_strings[x])
        if not select_list:
            return "", None, None

        # add the variable storing the source_id or file_id to the selected
        # columns so that they can be used to retrieve the context:
        if number == 0:
        #if number == 0 and options.cfg.MODE != QUERY_MODE_FREQUENCIES and (options.cfg.context_left or options.cfg.context_right):
            select_list.add("coq_corpus_{}_1".format(options.cfg.context_source_id))

        select_list.add("coq_corpus_id_{}".format(number+1))

        return "SELECT {} FROM {}".format(
            ", ".join(select_list), 
            " ".join(L)), select_list, L
        
    def sql_string_query_new(self, Query, self_joined):
        """ Return a string that is sufficient to run the query on the
        MySQL database. """

        # the next variable is set in get_sub_query_string() to store the 
        # name of that resource feature which that keeps track of the source 
        # of the first token of the query. 
        options.cfg.context_source_id = None

        for i, current_token in enumerate(Query.tokens):
            s, select_list, join_list = self.get_sub_query_string(current_token, i, self_joined)
            if i == 0:
                outer_list = join_list
                query_string_part = ["SELECT COQ_OUTPUT_FIELDS FROM ({}) AS e1".format(s)]
            else:
                if s:
                    join_string = "INNER JOIN ({s}) AS e{i1} ON coq_corpus_id_{i1} = coq_corpus_id_1 + {i}".format(s = s, i=i, i1=i+1, token=self.resource.corpus_id)
                    if not join_string in query_string_part:
                        query_string_part.append(join_string)
        

        corpus_features = [(x, y) for x, y in self.resource.get_corpus_features() if x in options.cfg.selected_features]
        lexicon_features = [(x, y) for x, y in self.resource.get_lexicon_features() if x in options.cfg.selected_features]
        
        # change the order of the output column so that output columns 
        # showing the same lexicon feature for different tokens are grouped
        # together, followed by all corpus features.
        # The overall order is specified in resource.get_preferred_output_order()
        final_select = []        
        for rc_feature in self.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in lexicon_features]:
                    for i in range(Query.Session.max_number_of_tokens):
                        if i < Query.number_of_tokens:
                            final_select.append("coq_{}_{}".format(rc_feature, i+1))
                        else:
                            final_select.append("NULL AS coq_{}_{}".format(rc_feature, i+1))
        
        # add the corpus features in the preferred order:
        for rc_feature in self.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in corpus_features]:
                    final_select.append("coq_{}_1".format(rc_feature))
        
        # Add any feature that is selected that is neither a corpus feature,
        # a lexicon feature nor a Coquery feature:
        for rc_feature in options.cfg.selected_features:
            if not rc_feature.startswith("coquery_") and "coq_{}_1".format(rc_feature) not in final_select:
                final_select.append("coq_{}_1".format(rc_feature))

        if options.cfg.context_right or options.cfg.context_left:
            if options.cfg.context_left:
                final_select.append('NULL AS coq_context_left')
            if options.cfg.context_right:
                final_select.append('NULL AS coq_context_right')
        
        # Add NULL values for all Coquery features; they are supplied not
        # by the SQL query, but by the Python script in yield_query_results().
        for x in options.cfg.selected_features:
            if x.startswith("coquery_"):
                final_select.append("NULL AS {}".format(x))

        # construct the query string from the sub-query parts:
        query_string = " ".join(query_string_part)

        # For Frequeny queries, add a COUNT() column named 'coq_frequency' as
        # well as a GROUP BY clause:
        if options.cfg.MODE == QUERY_MODE_FREQUENCIES:
            if final_select:
                query_string = "{} GROUP BY {}".format(query_string, ", ".join([x.split(" AS ")[-1] for x in final_select]))
            if options.cfg.MODE == QUERY_MODE_FREQUENCIES:
                final_select.append("COUNT(*) AS coq_frequency")

        # include variables that are required to make entries in the result
        # table clickable, but only if a GUI is used:
        if options.cfg.context_source_id:
        #if options.cfg.MODE != QUERY_MODE_FREQUENCIES and (options.cfg.context_left or options.cfg.context_right) and options.cfg.context_source_id:
            final_select.append("coq_corpus_id_1 AS coquery_invisible_corpus_id")
            final_select.append("coq_corpus_{}_1 AS coquery_invisible_origin_id".format(options.cfg.context_source_id))
            final_select.append("{} AS coquery_invisible_number_of_tokens".format(Query.number_of_tokens))

        query_string = query_string.replace("COQ_OUTPUT_FIELDS", ", ".join(final_select))
        
        # add LIMIT clause if necessary:
        if options.cfg.number_of_tokens:
            query_string = "{} LIMIT {}".format(
                query_string, options.cfg.number_of_tokens)

        if options.cfg.verbose:
            query_string = query_string.replace("INNER JOIN ", "INNER JOIN \n\t")
            query_string = query_string.replace("SELECT ", "SELECT \n\t")
            query_string = query_string.replace("FROM ", "\n\tFROM \n\t\t")
            query_string = query_string.replace("WHERE ", "\n\tWHERE \n\t\t")

        #print(query_string)
        #sys.exit(0)

        Query.Session.output_order = [x.split(" AS ")[-1] for x in final_select]

        if Query.Session.output_order:
            return query_string
        else:
            return ""
        
    def yield_query_results_new(self, Query, self_joined=False):
        """ Run the corpus query specified in the Query object on the corpus
        and yield the results. """
        
        query_string = self.sql_string_query_new(Query, self_joined)
        
        D = {}
        show_day = False
        show_time = False
        for x in options.cfg.selected_features:
            if x.startswith("coquery_"):
                D[x] = ""
                if x == "coquery_query_string":
                    try:
                        D[x] = Query.query_string
                    except AttributeError:
                        pass
                elif x == "coquery_query_file":
                    try:
                        D[x] = options.cfg.input_path
                    except AttributeError:
                        pass
                elif x == "coquery_current_date":
                    show_day = True
                elif x == "coquery_current_time":
                    show_time = True
        cursor = self.resource.DB.execute_cursor(query_string)
        for current_result in cursor:
            now = datetime.datetime.now()
            if show_day:
                current_result["coquery_current_date"] = now.strftime("%Y-%m-%d")
            if show_time: 
                current_result["coquery_current_time"] = now.strftime("%H:%M:%S")
            current_result.update(D)

            #if options.cfg.MODE != QUERY_MODE_FREQUENCIES and (options.cfg.context_left or options.cfg.context_right):
            if (options.cfg.context_left or options.cfg.context_right):
                left, right = self.get_context(
                    current_result["coquery_invisible_corpus_id"], 
                    current_result["coquery_invisible_origin_id"], 
                    Query.number_of_tokens, True)
                if options.cfg.context_left:
                    current_result["coq_context_left"] = collapse_words(left)
                if options.cfg.context_right:
                    current_result["coq_context_right"] = collapse_words(right)
            yield current_result

    def yield_query_results(self, Query, self_joined=False):
        """ Run the corpus query specified in the Query object on the corpus
        and yield the results. """

        # see if there are already results for the current query string 
        # in the Session cache. If so, do not run the query at all.
        
        column_string = self.sql_string_run_query_column_string(Query, self_joined)
        table_string = self.sql_string_run_query_table_string(Query, self_joined)
        
        query_filter_list = self.sql_string_run_query_filter_list(Query, self_joined)
        
        # make the experimental query mode the default for frequency queries 
        # with exactly one token, but optional otherwise:
        if options.cfg.experimental or (options.cfg.MODE == QUERY_MODE_FREQUENCIES and (len(Query.Session.output_fields) == 1)):
            query_string = "SELECT {} FROM {}".format(
                column_string, table_string)

            if options.cfg.experimental:
                if self_joined:
                    if options.cfg.source_filter:
                        where_string = self.sql_string_run_query_textfilter(Query, self_joined)
                        query_string = "SELECT {} FROM {} WHERE {}".format(column_string, table_string, where_string)
            else:
                where_string = self.sql_string_run_query_where_string(Query, self_joined)
                if where_string:
                    query_string = "SELECT {} FROM {} WHERE {}".format(column_string, table_string, where_string)
            if len(Query.Session.output_fields) > 1:
                query_string += " GROUP BY {}".format(
                    self.sql_string_run_query_column_string(Query, self_joined, only_names=True))
                
                
        else:
            where_string = self.sql_string_run_query_where_string(Query, self_joined)
            if where_string:
                query_string = "SELECT {} FROM {} WHERE {}".format(
                    column_string, table_string, where_string)
            else:
                query_string = "SELECT {} FROM {}".format(
                    column_string, table_string)

        # add LIMIT clause if necessary:
        if options.cfg.number_of_tokens:
            query_string = "{} LIMIT {}".format(
                query_string, options.cfg.number_of_tokens)


            query_string = query_string.replace("SELECT ", "SELECT \n\t")
            query_string = query_string.replace("FROM ", "\nFROM \n\t")
            query_string = query_string.replace("WHERE ", "\nWHERE \n\t")

        #Run the MySQL query:
        #print(query_string)
        
        #sys.exit(0)
        cursor = self.resource.DB.execute_cursor(query_string)
        #return(cursor)
        for current_result in cursor:
            yield current_result

    def sql_string_get_sentence_wordid(self,  source_id):
        return "SELECT {corpus_wordid} FROM {corpus} INNER JOIN {source} ON {corpus}.{corpus_source} = {source_alias}.{source_id} WHERE {source_alias}.{source_id} = {this_source}{verbose}".format(
            corpus_wordid=self.resource.corpus_word_id,
            corpus=self.resource.corpus_table,
            source=self.resource.source_table,
            source_alias=self.resource.source_table_alias,
            corpus_source=self.resource.corpus_source_id,
            source_id=self.resource.source_id,
            corpus_token=self.resource.corpus_id,
            this_source=source_id,
            verbose=" -- sql_string_get_sentence_wordid" if options.cfg.verbose else "")

    def get_context_sentence(self, sentence_id):
        self.resource.DB.execute(
            self.sql_string_get_sentence_wordid(sentence_id))
        return [self.lexicon.get_entry(x, [LEX_ORTH]).orth for (x, ) in self.resource.DB.Cur]

    def sql_string_get_wordid_in_range(self, start, end, source_id):
        if options.cfg.experimental:
            if options.cfg.context_source_id and source_id:
                return "SELECT {corpus_wordid} from {corpus} WHERE {token_id} BETWEEN {start} AND {end} AND {corpus_source} = {this_source}".format(
                    corpus_wordid=self.resource.corpus_word_id,
                    corpus=self.resource.corpus_table,
                    token_id=self.resource.corpus_id,
                    start=start, end=end,
                    corpus_source=self.resource.__getattribute__("corpus_{}".format(options.cfg.context_source_id)),
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

        if False and source_id:
            return "SELECT {corpus_wordid} FROM {corpus} WHERE {corpus_token} BETWEEN {start} and {end} AND {corpus_source} = '{this_source}'".format(
            corpus_wordid=self.resource.corpus_word_id,
            corpus=self.resource.corpus_table,
            source=self.resource.source_table,
            source_alias=self.resource.source_table_alias,
            corpus_source=self.resource.corpus_source_id,
            source_id=self.resource.source_id,
            corpus_token=self.resource.corpus_id,
            start=start,
            end=end,
            this_source=source_id,
            verbose=" -- sql_string_get_sentence_wordid" if options.cfg.verbose else "")
        else:
            return "SELECT {corpus_wordid} FROM {corpus} WHERE {corpus_token} BETWEEN {start} AND {end} {verbose}".format(
                corpus_wordid=self.resource.corpus_word_id,
                corpus=self.resource.corpus_table,
                corpus_token=self.resource.corpus_id,
                start=start, end=end,
                verbose=" -- sql_string_get_wordid_in_range" if options.cfg.verbose else "")
 
    def get_context(self, token_id, source_id, number_of_tokens, case_sensitive):
        if options.cfg.context_sentence:
            asd
        #if options.cfg.context_span:
            #span = options.cfg.context_span
        #elif options.cfg.context_columns:
            #span = options.cfg.context_columns

        old_verbose = options.cfg.verbose
        options.cfg.verbose = False

        left_span = options.cfg.context_left
        if left_span > token_id:
            start = 1
        else:
            start = token_id - left_span
                
        self.resource.DB.execute(
            self.sql_string_get_wordid_in_range(
                start, 
                token_id - 1, source_id))
        left_context_words = [self.lexicon.get_entry(x, [LEX_ORTH]).orth for (x, ) in self.resource.DB.Cur]
        left_context_words = [''] * (left_span - len(left_context_words)) + left_context_words

        self.resource.DB.execute(
            self.sql_string_get_wordid_in_range(
                token_id + number_of_tokens, 
                token_id + number_of_tokens + options.cfg.context_right - 1, source_id))
        right_context_words = [self.lexicon.get_entry(x, [LEX_ORTH]).orth for (x, ) in self.resource.DB.Cur]
        right_context_words =  right_context_words + [''] * (options.cfg.context_right - len(right_context_words))

        options.cfg.verbose = old_verbose

        return (left_context_words, right_context_words)

    def sql_string_get_source_info(self, source_id):
        if options.cfg.experimental:
            return "SELECT * FROM {} WHERE {} = {} LIMIT 1".format(
                self.resource.source_table,
                self.resource.source_id, source_id)
        
        if "source_table" in dir(self.resource) and "source_table_alias" in dir(self.resource):
            return "SELECT * FROM {} WHERE {}.{} = {} LIMIT 1".format(
                self.resource.source_table_construct, 
                self.resource.source_table_alias, 
                self.resource.source_id, source_id)
        else:
            raise ResourceIncompleteDefinitionError

    def get_source_info(self, source_id, header=None):
        if not header:
            source_info_header = self.get_source_info_header()
        else:
            source_info_header = header
        error_values = ["<na>"] * len(source_info_header)
        if not source_id:
            return error_values
        S = self.sql_string_get_source_info(source_id)
        cursor = self.resource.DB.execute_cursor(S)
        query_result = cursor.fetchone()
        return [query_result[x] for x in source_info_header]

    def get_source_info_header(self):
        potential_header = [self.resource.__getattribute__(x) for x in dir(self.resource) if x.startswith("source_info_")]
        if not options.cfg.source_columns:
            return []
        for x in options.cfg.source_columns:
            if x.upper() == "ALL":
                return potential_header
        return [x for x in options.cfg.source_columns if x.lower() in potential_header]

    def sql_string_get_time_info(self, token_id):
        raise CorpusUnsupportedFunctionError

    def get_time_info(self, token_id):
        time_info_header = self.get_time_info_header()
        error_values = ["<na>"] * len(time_info_header)
        if not token_id:
            return error_values
        cursor = self.resource.DB.execute_cursor(self.sql_string_get_time_info(token_id))
        query_result = cursor.fetchone()
        return [query_result[x] for x in time_info_header]

    def sql_string_get_file_info(self, source_id):
        if "file_table" in dir(self.resource) and "file_id" in dir(self.resource) and "file_label" in dir(self.resource):
            return "SELECT {} as File FROM {} WHERE {} = {} LIMIT 1".format(
                    self.resource.file_label,
                    self.resource.file_table,
                    self.resource.file_id,
                    source_id)        
        else:
            raise ResourceIncompleteDefinitionError
    
    def get_file_info(self, source_id):
        file_info_header = self.get_file_info_header()
        error_values = ["<na>"] * len(file_info_header)
        if not source_id:
            return error_values
        cursor = self.resource.DB.execute_cursor(self.sql_string_get_file_info(source_id))
        query_result = cursor.fetchone()
        return [query_result[x] for x in file_info_header]
    
    def get_file_info_header(self):
        return ["File"]

    def get_statistics(self):
        stats = self.lexicon.get_statistics()
        stats["corpus_variables"] = " ".join([x for x, _ in self.resource.get_corpus_features()])
        for table in [x for x in dir(self.resource) if not x.startswith("_")]:
            if table.endswith("_table"):
                tab, _, _ = table.partition("_table")
                S = "SELECT COUNT(*) FROM {}".format(getattr(self.resource, table))
                self.resource.DB.execute(S)
                if tab == TABLE_CORPUS:
                    var_name = "{}_tokens".format(tab)
                else:
                    var_name = "{}_entries".format(tab)
                stats[var_name] = self.resource.DB.Cur.fetchone()[0]
                for variable in [x for x in dir(self.resource) if x.startswith(tab) and not x.startswith(table)]:
                    if not variable.endswith("_id"):
                        S = "SELECT COUNT(DISTINCT {}) FROM {}".format(getattr(self.resource, variable), getattr(self.resource, table))
                        self.resource.DB.execute(S)
                        stats["{}_distinct".format(variable)] = self.resource.DB.Cur.fetchone()[0]
        return stats

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

        start = max(0, token_id - context_width)
        end = token_id + token_width + context_width - 1
        
        self.resource.DB.execute(
            self.sql_string_get_wordid_in_range(
                start, 
                token_id - 1, source_id))
        left = [self.lexicon.get_entry(x, [LEX_ORTH]).orth for (x, ) in self.resource.DB.Cur]
        
        self.resource.DB.execute(
            self.sql_string_get_wordid_in_range(
                token_id, 
                token_id + token_width - 1, source_id))
        token = [self.lexicon.get_entry(x, [LEX_ORTH]).orth for (x, ) in self.resource.DB.Cur]

        self.resource.DB.execute(
            self.sql_string_get_wordid_in_range(
                token_id + token_width, 
                end,
                source_id))
        right = [self.lexicon.get_entry(x, [LEX_ORTH]).orth for (x, ) in self.resource.DB.Cur]

        context = "{} <b>{}</b> {}".format(
            collapse_words(left), collapse_words(token), collapse_words(right))
        widget.ui.context_area.setText(context)

        
class TestLexicon(BaseLexicon):
    def is_part_of_speech(self, pos):
        return pos in ["N", "V"]
    
""" Revised query for self-joins?



SELECT coq_corpus_id_1, coq_word_label_1, coq_word_label_2, coq_word_label_3, coq_frequency, coq_source_genre_1, coq_source_genre_1 FROM 

(SELECT 
    TokenId AS coq_corpus_id_1, TextId AS coq_corpus_source_id_1, W1 AS coq_corpus_word_id_1, W2 AS coq_corpus_word_id_2, W3 AS coq_corpus_word_id_3, COUNT(*) AS coq_frequency 
FROM 
    corpusBig
WHERE 
    W1 IN 
        (4454405, 306695, 286733, 22, 354855, 28201, 4618797, 1313838, 6704, 3405879, 3866688, 1305014, 458310, 72775, 309326, 745039, 46674, 1081615, 4574812, 463967, 113254, 1420920, 22141, 640, 641158, 802442, 161932, 20113, 551570, 4071070, 41643, 267951, 176, 689, 3262, 830655, 9937, 119507, 166625, 3756771, 309493, 5370, 540420, 614666, 40718, 389391, 4312852, 2609953, 608573, 447809, 2844997, 919373, 1411402, 16205, 19278, 73551, 5465, 355, 3943, 52073, 85866, 126866, 1378159, 429713, 551811, 745348, 42889, 4770192, 19858, 320405, 138665, 68522, 4616775, 152492, 438, 33730, 76739, 67532, 843726, 2511, 1055703, 3046, 2958316, 195154, 2491375, 358388, 555004, 1312255) 
    AND
    W2 IN 
        (15012, 13542, 1959, 1540457, 214411, 23468, 155823, 43892, 125174, 4617, 5000760, 101564, 4249533) 
    AND 
    W3 IN 
        (24, 1345)

GROUP BY 
    coq_corpus_word_id_1, coq_corpus_word_id_2, coq_corpus_word_id_3
) AS coq_master

INNER JOIN 
    (SELECT Word as coq_word_label_1, WordId AS coq_word_id_1 FROM lex) AS e1
    ON coq_word_id_1 = coq_corpus_word_id_1

INNER JOIN 
    (SELECT Word as coq_word_label_2, WordId AS coq_word_id_2 FROM lex) AS e2
    ON coq_word_id_2 = coq_corpus_word_id_2

INNER JOIN
    (SELECT Word as coq_word_label_3, WordId AS coq_word_id_3 FROM lex) AS e3
    ON coq_word_id_3 = coq_corpus_word_id_3

INNER JOIN
    (SELECT TextId AS coq_source_id_1, Genre AS coq_source_genre_1, Year AS coq_source_year_1 FROM sources) AS coq_source_table
    ON coq_corpus_source_id_1 = coq_source_id_1
    
OLD :


SELECT corpusBig.TokenId AS TokenId,
        corpusBig.W1,
        corpusBig.W3,
        corpusBig.W2 FROM corpusBig WHERE W1 IN (4454405, 306695, 286733, 22, 354855, 28201, 4618797, 1313838, 6704, 3405879, 3866688, 1305014, 458310, 72775, 309326, 745039, 46674, 1081615, 4574812, 463967, 113254, 1420920, 22141, 640, 641158, 802442, 161932, 20113, 551570, 4071070, 41643, 267951, 176, 689, 3262, 830655, 9937, 119507, 166625, 3756771, 309493, 5370, 540420, 614666, 40718, 389391, 4312852, 2609953, 608573, 447809, 2844997, 919373, 1411402, 16205, 19278, 73551, 5465, 355, 3943, 52073, 85866, 126866, 1378159, 429713, 551811, 745348, 42889, 4770192, 19858, 320405, 138665, 68522, 4616775, 152492, 438, 33730, 76739, 67532, 843726, 2511, 1055703, 3046, 2958316, 195154, 2491375, 358388, 555004, 1312255) AND
        W2 IN (15012, 13542, 1959, 1540457, 214411, 23468, 155823, 43892, 125174, 4617, 5000760, 101564, 4249533) AND
        W3 IN (17408, 771, 8581, 1545478, 28481, 32392, 56331, 372876, 2551949, 84878, 126352, 1400387, 407, 24, 398617, 979354, 706715, 418972, 14493, 1316383, 146208, 33, 23074, 283, 700319, 783833, 4521, 341639, 40620, 557, 260189, 72992, 343841, 753864, 2357301, 487862, 3632312, 73204, 2875066, 573791, 857916, 276543, 1345, 103875, 89412, 2923719, 15176, 622220, 6346, 1941964, 3704738, 54048, 3325520, 2162971, 51026, 440547, 68308, 20666, 3775320, 133977, 40026, 3429616, 223644, 148575, 482016, 1783163, 474855, 738792, 8553, 806123, 884205, 71022, 3364891, 41164, 208114, 262739, 1017204, 52086, 204137, 2485371, 382, 196735) """
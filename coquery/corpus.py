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
        self.resource = resource
        self._query_cache = {}
        
        if LEX_POS in self.provides:
            self.pos_dict = {}

    def is_part_of_speech(self, pos):
        """ 
        DESCRIPTION
        is_part_of_speech(pos) returns True if the content of the argument
        pos is considered a valid part-of-speech label for the lexicon. 
        Otherwise, it returns False.
        
        VALUE
        <type 'bool'>
        """
        if self.pos_dict:
            return pos in self.pos_dict
        else:
            raise LexiconFeatureUnavailableError(LEX_POS)

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
    # Add internal table that can be used to access system information:
    coquery_query_string = "Query string"
    coquery_expanded_query_string = "Expanded query string"
    coquery_query_file = "Input file"
    coquery_current_date = "Current date"
    coquery_current_time = "Current time"
    coquery_query_token = "Query token"

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
    
    #@classmethod
    #def get_link_dictionary(self, dictionary):
        #""" Try to link a dictionary to the word table of this resource. The
        #argument 'dictionary' is a valid Resource class.
        
        #A dictionary is a corpus module that does not contain a sequential 
        #list of tokens. Instead, every entry in the corpus table represents
        #one dictionary entry.
        
        #Note that using linked dictionaries can slow down queries very
        #significantly.
        
        #"""
        
        #d = {}
        
        #word_label = ""
        #if "word_label" in dir(cls):
            #word_label = self.word_label
        #elif "corpus_word" in dir(cls):
            #word_label = cls.corpus_word

        #d["word_{}_id".format(dictionary.name)] = word_label
        #d["{}_table".format(dictionary.name)] = "{}.{}".format(dictionary.db_name, dictionary.corpus_table)
        #d["{}_id".format(dictionary.name)] = dictionary.word_label
            
        #try:
            #d["{}_id".format(dictionary.name)] = dictionary.word_transcript
        #except AttributeError:
            #pass
        
        #return d.keys()

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
        if "word" not in table_dict:
            return []
        lexicon_tables = cls.get_table_tree("word")
        lexicon_variables = []
        for x in table_dict:
            if x in lexicon_tables and x not in ("tags", "coquery"):
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
            
        # Retain the column header if the query string was from an input file
        if header == "coquery_query_string" and options.cfg.query_label:
            return options.cfg.query_label
        
        if header in COLUMN_NAMES:
            return COLUMN_NAMES[header]
        
        # strip coq_ prefix:
        if header.startswith("coq_"):
            header = header.partition("coq_")[2]

        rc_feature, _, number = header.rpartition("_")

        if rc_feature in [x for x, _ in cls.get_lexicon_features()]:
            return "{}{}".format(type(cls).__getattribute__(cls, str(rc_feature)), number)
        else:
            try:
                return "{}".format(type(cls).__getattribute__(cls, str(rc_feature)))
            except AttributeError:
                if rc_feature in COLUMN_NAMES:
                    return "{}{}".format(COLUMN_NAMES[rc_feature], number)
                else:
                    return header
        return header

class BaseCorpus(object):
    provides = []
    
    def __init__(self, lexicon, resource):
        self.lexicon = lexicon
        self.resource = resource
        
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
        if token.class_specifiers and LEX_POS in self.provides:
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

    def sql_string_get_orth(self, word_id):
        return     
    def get_orth(self, word_id):
        """ Return the orthographic form of the lexicon entry 'word_id'. """
        try:
            return self._query_cache[word_id]
        except KeyError:
            self.resource.DB.execute(
                "SELECT {} FROM {} WHERE {} = {} LIMIT 1".format(
                self.resource.word_label, 
                self.resource.word_table,
                self.resource.word_id,
                word_id))
            orth = self.resource.DB.Cur.fetchone()
            if orth:
                orth = orth[0]
                self._query_cache[word_id] = orth
                return orth
            else:
                return "<NA>"

    #def sql_string_get_entry(self, word_id, requested):
        #""" Return a MySQL string that can be used to query the requested
        #fields for the lexical entry 'word_id. """        
        #print("IS THIS CALLED ANYWAY?")
        #if word_id == "NA":
            #word_id = -1
        
        #select_variable_list = []
        #self.where_list = ["{}.{} = {}".format(
            #self.resource.word_table,
            #self.resource.word_id,
            #word_id)]
        #self.table_list = [self.resource.word_table]
        #for current_attribute in requested:
            #if current_attribute == LEX_WORDID:
                #select_variable_list.append("{}.{}".format(
                    #self.resource.word_table,
                    #self.resource.word_id))
            
            #if current_attribute == LEX_LEMMA:
                #if "lemma_table" in dir(self.resource):
                    #select_variable_list.append("COQ_LEMMA_TABLE.{}".format(
                        #self.resource.lemma_label))
                    #self.table_list.append("LEFT JOIN {} AS COQ_LEMMA_TABLE ON {}.{} = COQ_LEMMA_TABLE.{}".format(
                        #self.resource.lemma_table,
                        #self.resource.word_table,
                        #self.resource.word_lemma_id,
                        #self.resource.lemma_id))
                #else:
                    #select_variable_list.append("{}.{}".format(
                        #self.resource.word_table,
                        #self.resource.word_lemma))
            
            #if current_attribute == LEX_ORTH:
                #select_variable_list.append("{}.{}".format(
                    #self.resource.word_table,
                    #self.resource.word_label))
            
            #if current_attribute == LEX_POS:
                #if "pos_table" in dir(self.resource):
                    #select_variable_list.append("PARTOFSPEECH.{}".format(
                        #self.resource.pos_label))
                    #self.table_list.append("LEFT JOIN {} AS PARTOFSPEECH ON {}.{} = PARTOFSPEECH.{}".format(
                        #self.resource.pos_table,
                        #self.resource.word_table,
                        #self.resource.word_pos_id,
                        #self.resource.pos_id))
                #else:
                    #select_variable_list.append("{}.{}".format(
                        #self.resource.word_table,
                        #self.resource.word_pos))
            
            #if current_attribute == LEX_PHON:
                #if "transcript_table" in dir(self.resource):
                    #select_variable_list.append("TRANSCRIPT.{}".format(
                        #self.resource.transcript_label))
                    #self.table_list.append("LEFT JOIN {} AS TRANSCRIPT ON {}.{} = TRANSCRIPT.{}".format(
                        #self.resource.transcript_table,
                        #self.resource.word_table,
                        #self.resource.word_transcript_id,
                        #self.resource.transcript_id))
                #else:
                    #select_variable_list.append("{}.{}".format(
                        #self.resource.word_table,
                        #self.resource.word_transcript))
                
        #select_string = ("SELECT {0} FROM {1}{2}".format(
            #", ".join(select_variable_list),
            #" ".join(self.table_list),
            #(" WHERE " + " AND ".join(self.where_list)) if self.where_list else ""))
        #return select_string
    
    #def get_entry(self, word_id, requested):
        #""" Return a Entry() instance that contains the requested fields for 
        #the lexicon entry with 'word_id'.
        
        #This function is deprecated, and may be removed in future versions if
        #no obvious usecase emerges. It is the only place where the Entry()
        #class is used, it makes use of the old feature specification, it is 
        #not very much aware of more complex database hierarchies, and it 
        #contains code that is redundant with sql_string_get_matching_wordids().
        #"""
        
        #if not tuple(requested) in self.entry_cache:
            #self.entry_cache[tuple(requested)] = {}
        #try:
            #return self.entry_cache[tuple(requested)][word_id]
        #except KeyError:
            #pass

        ## an entry has to provide at least LEX_ORTH:
        #provide_fields = set(self.provides) & set(requested) | set([LEX_ORTH])
        #error_value = ["<NA>"] * (len(self.provides) - 1)
        #entry = self.Entry(provide_fields)
        #S = self.sql_string_get_entry(word_id, provide_fields)
        #self.resource.DB.execute(S)
        #query_results = self.resource.DB.Cur.fetchone()
        #if query_results:
            #entry.set_values(query_results)
        #else:
            #entry.set_values(error_value)
            
        ## add entry to cache:
        #self.entry_cache[tuple(requested)][word_id] = entry
        #return entry

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
    def __init__(self, lexicon, resource):
        super(SQLCorpus, self).__init__(lexicon, resource)
        self._frequency_cache = {}
        self._corpus_size_cache = None

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
        taking the filter list from options.cfg.filter_list into account."""
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
        filter_list = self.resource.translate_filters(options.cfg.filter_list)
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

    def get_sub_query_string_self_joined(self, token, number):
        
        # get a list of all tables that are required to satisfy the 
        # feature request:
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
        
    def get_select_list(self, query):
        """
        Return a list of field names that can be used to extract the 
        requested columns from the joined MySQL query table.
        
        This list is usually stored in Session.output_order and determines
        which columns appear in the output table. If a column is missing, 
        it may be because it is not correctly included in this list.
        
        Parameters
        ----------
        query : CorpusQuery
            The query for which a select list is required
            
        Returns
        -------
        l : list
            A list of strings representing the aliased columns in the joined
            MySQL query table.
        """
        
        lexicon_features = [x for x, _ in self.resource.get_lexicon_features() if x in options.cfg.selected_features]
        corpus_features = [x for x, _ in self.resource.get_corpus_features() if x in options.cfg.selected_features]

        # the initial select list contains the columns from the input file
        # (if present):
        select_list = list(query.Session.input_columns)

        # then, add an appropriately aliased name for each selected feature:
        for rc_feature in options.cfg.selected_features:
            if rc_feature in lexicon_features:
                select_list += ["coq_{}_{}".format(rc_feature, x+1) for x in range(query.max_number_of_tokens)]
            elif rc_feature in corpus_features:
                select_list.append("coq_{}_1".format(rc_feature))
            elif rc_feature.startswith("coquery_"):
                if rc_feature == "coquery_query_token": 
                    select_list += ["coquery_query_token_{}".format(x + 1) for x in range(query.number_of_tokens)]
                else:
                    select_list.append(rc_feature)

        # MISSING:
        # linked columns and functions

        func_count =  Counter()
        for rc_feature in options.cfg.selected_features:
            if rc_feature.startswith("func."):
                target = rc_feature.split("func.")[-1]
                func_count[target] += 1
                select_list.append("coq_func_{}_{}".format(target, func_count[target]))

            if not rc_feature.startswith("coquery_") and "coq_{}_1".format(rc_feature) not in select_list:
                if "." not in rc_feature:
                    select_list.append("coq_{}_1".format(rc_feature.replace(".", "_")))

        if options.cfg.MODE != QUERY_MODE_COLLOCATIONS:
            # add contexts for each query match:
            if (options.cfg.context_left or options.cfg.context_right) and options.cfg.context_source_id:
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
            select_list.append("coquery_invisible_origin_id")
            select_list.append("coquery_invisible_number_of_tokens")

        return select_list        

    def get_sub_query_string(self, current_token, number, self_joined=False):
        """ 
        Return a MySQL string that selects a table matching the current
        token, and which includes all columns that are requested, or which
        are required to join the tables. 
        
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
            
        # corpus variables will only be included in the subquery string if 
        # this is the first subquery.
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
            for filt in self.resource.translate_filters(options.cfg.filter_list):
                variable, rc_feature, table_name, op, value_list, _value_range = filt
                if op.upper() == "LIKE":
                    if "*" not in value_list[0]:
                        value_list[0] = "*{}*".format(value_list[0])
                    value_list[0] = tokens.COCAToken.replace_wildcards(value_list[0])

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

            if rc_table == "coquery_table":
                continue
            if rc_table == "tag_table":
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

                column_list = []
                for rc_feature in sub_tree["rc_requested_features"]:
                    if rc_feature.startswith("func."):
                        name = "coq_func_{}_{}".format(
                            rc_feature.split("func.")[-1], number+1)
                    else:
                        name = "coq_{}_{}".format(rc_feature, number+1)

                    variable_string = "{} AS {}".format(
                        self.resource.__getattribute__(rc_feature.split("func.")[-1]),
                        name)
                    column_list.append(variable_string)
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
    
    def get_subquery_order(self, Query):
        """ Return an order list in which the subqueries should be executed. 
        Ideally, the order corresponds to the number of rows in the corpus
        that match the subquery, from small to large. This increases query
        performance because it reduces the number of rows that need to be 
        scanned once all tables have been joined.
        
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
        string of the same length without '*'. """
        # FIXME: improve the heuristic.
        
        if len(Query) == 1:
            return [1]
        
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
        
        sort_list = list(enumerate(Query.tokens))
        # first, sort in reverse length:
        sort_list = sorted(sort_list, 
                           key=lambda x: calc_weight(x[1].S), reverse=True)
        return [x+1 for x, _ in sort_list]
    
    def sql_string_query(self, Query, self_joined):
        """ Return a string that is sufficient to run the query on the
        MySQL database. """

        # the next variable is set in get_sub_query_string() to store the 
        # name of that resource feature which that keeps track of the source 
        # of the first token of the query. 
        options.cfg.context_source_id = None
        sub_query_list = {}

        corpus_features = [(x, y) for x, y in self.resource.get_corpus_features() if x in options.cfg.selected_features]
        lexicon_features = [(x, y) for x, y in self.resource.get_lexicon_features() if x in options.cfg.selected_features]

        if self_joined:
            corpus_features = [x for x, y in self.resource.get_corpus_features() if x in options.cfg.selected_features]
            lexicon_features = [x for x, y in self.resource.get_lexicon_features() if x in options.cfg.selected_features]
            for i, token in enumerate(Query.tokens):
                s = self.get_sub_query_string_self_joined(token, i)
                if s:
                    join_string = "INNER JOIN ({s}) AS e{i}\nON coq_word_id_{i} = W{i}".format(
                        s = s, 
                        i=i+1)
                    sub_query_list[i+1] = join_string
            final_select = []
            for rc_feature in options.cfg.selected_features:
                if rc_feature in corpus_features or rc_feature in lexicon_features:
                    final_select.append(select_feature)
                else:
                    final_select.append("NULL AS {}".format(select_feature))

            # include variables that are required to make entries in the result
            # table clickable, but only if a GUI is used:
            if options.cfg.context_source_id:
                final_select.append("{} AS coquery_invisible_corpus_id".format(self.resource.__getattribute__("corpus_denorm_token_id")))
                final_select.append("{} AS coquery_invisible_origin_id".format(self.resource.__getattribute__("corpus_denorm_source_id")))

            final_select.append("{} AS coquery_invisible_corpus_id".format(
                self.resource.__getattribute__("corpus_denorm_id")))
                
            return """
            SELECT  {}
            FROM    {}
            {}
            """.format(
                ", ".join(final_select),
                self.resource.corpus_denorm_table,
                "\n".join(sub_query_list.values())
                )

        order = self.get_subquery_order(Query)
        logger.info("Token order: {}".format(", ".join([Query.tokens[x-1].S for x in order])))
        referent_id = order.pop(0)

        # get a partial query string for each token:
        for i, token in enumerate(Query.tokens):
            s = self.get_sub_query_string(token, i, self_joined)
            if i + 1 == referent_id:
                sub_query_list[i+1] = s                
            elif i + 1 < referent_id:
                if s:
                    join_string = "INNER JOIN ({s}) AS e{i} ON coq_corpus_id_{ref} > {i1} AND coq_corpus_id_{i} = coq_corpus_id_{ref} - {i1}".format(
                        s = s, 
                        i=i+1, 
                        i1=referent_id - i - 1, 
                        ref=referent_id,
                        token=self.resource.corpus_id)
                    sub_query_list[i+1] = join_string
            else:
                if s:
                    join_string = "INNER JOIN ({s}) AS e{i1} ON coq_corpus_id_{i1} = coq_corpus_id_{ref} + {i}".format(
                        s = s, i=i - referent_id + 1,
                        i1=i+1, token=self.resource.corpus_id, ref=referent_id)
                    sub_query_list[i+1] = join_string

        query_string_part = [
            "SELECT COQ_OUTPUT_FIELDS FROM ({}) AS e{}".format(sub_query_list.pop(referent_id), referent_id)]
        for x in order:
            query_string_part.append(sub_query_list[x])

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

        # add any external feature that is linked to a lexicon feature:
        for linked in options.cfg.external_links:
            external, internal = options.cfg.external_links[linked]
            internal_feature = internal.split(".")[-1]
            external_corpus, external_feature = linked.split(".")
            if internal_feature in [x for x, _ in self.resource.get_lexicon_features()]:
                for i in range(Query.Session.max_number_of_tokens):
                    if i < Query.number_of_tokens:
                        final_select.append("coq_{}_{}_{}".format(external_corpus, external_feature, i+1))
                    else:
                        final_select.append("NULL AS coq_{}_{}_{}".format(external_corpus, external_feature, i+1))

        # add the corpus features in the preferred order:
        for rc_feature in self.resource.get_preferred_output_order():
            if rc_feature in options.cfg.selected_features:
                if rc_feature in [x for x, _ in corpus_features]:
                    final_select.append("coq_{}_1".format(rc_feature))
        
        # Add any feature that is selected that is neither a corpus feature,
        # a lexicon feature nor a Coquery feature:
        for rc_feature in options.cfg.selected_features:
            if not rc_feature.startswith("coquery_") and "coq_{}_1".format(rc_feature) not in final_select:
                if "." not in rc_feature:
                    final_select.append("coq_{}_1".format(rc_feature.replace(".", "_")))

        if options.cfg.MODE != QUERY_MODE_COLLOCATIONS:
            if (options.cfg.context_right or options.cfg.context_left) and options.cfg.context_source_id:
                if options.cfg.context_mode == CONTEXT_STRING:
                    final_select.append('NULL AS coq_context')
                elif options.cfg.context_mode == CONTEXT_KWIC:
                    if options.cfg.context_left:
                        final_select.append('NULL AS coq_context_left')
                    if options.cfg.context_right:
                        final_select.append('NULL AS coq_context_right')
        
        # construct the query string from the sub-query parts:
        query_string = " ".join(query_string_part)

        func_counter = Counter()
        for x in options.cfg.selected_functions:
            resource = x.rpartition(".")[-1]
            func_counter[resource] += 1
            name = "coq_func_{}_{}".format(resource, func_counter[resource])
            final_select.append(name)

        # include variables that are required to make entries in the result
        # table clickable, but only if a GUI is used:
        if options.cfg.context_source_id:
            final_select.append("coq_corpus_id_1 AS coquery_invisible_corpus_id")
            final_select.append("coq_{}_1 AS coquery_invisible_origin_id".format(options.cfg.context_source_id))

        # if nothing is selected at all, add at least the corpus id to the 
        # list:
        if not final_select:
            final_select.append("coq_corpus_id_1 AS coquery_invisible_corpus_id")
            
        query_string = query_string.replace("COQ_OUTPUT_FIELDS", ", ".join(final_select))
        
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
        
    def yield_query_results(self, Query, self_joined=False):
        """ Run the corpus query specified in the Query object on the corpus
        and yield the results. """
        try:
            query_string = self.sql_string_query(Query, self_joined)
        except WordNotInLexiconError:
            query_string = ""
            
        Query.Session.output_order = self.get_select_list(Query)

        if query_string:
            cursor = self.resource.DB.execute_cursor(query_string)
        else:
            cursor = {}
        for current_result in cursor:
            if options.cfg.MODE != QUERY_MODE_COLLOCATIONS:
                # add contexts for each query match:
                if (options.cfg.context_left or options.cfg.context_right) and options.cfg.context_source_id:
                    left, target, right = self.get_context(
                        current_result["coquery_invisible_corpus_id"], 
                        current_result["coquery_invisible_origin_id"], 
                        Query.number_of_tokens, True)
                    if options.cfg.context_mode == CONTEXT_KWIC:
                        if options.cfg.context_left:
                            current_result["coq_context_left"] = collapse_words(left)
                        if options.cfg.context_right:
                            current_result["coq_context_right"] = collapse_words(right)
                    elif options.cfg.context_mode == CONTEXT_STRING:
                        current_result["coq_context"] = collapse_words(left + target + right)
                    elif options.cfg.context_mode == CONTEXT_SENTENCE:
                        current_result["coq_context"] = collapse_word(self.get_context_sentence())
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
        raise NotImplementedError
        #S = self.sql_string_get_sentence_wordid(sentence_id)
        #self.resource.DB.execute(S)

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

    def get_context(self, token_id, source_id, number_of_tokens, case_sensitive):
        if options.cfg.context_sentence:
            asd
        #if options.cfg.context_span:
            #span = options.cfg.context_span
        #elif options.cfg.context_columns:
            #span = options.cfg.context_columns
        token_id = int(token_id)
        source_id = int(source_id)

        old_verbose = options.cfg.verbose
        options.cfg.verbose = False

        left_span = options.cfg.context_left
        if left_span > token_id:
            start = 1
        else:
            start = token_id - left_span

        S = self.sql_string_get_wordid_in_range(
                start, 
                token_id - 1, source_id)
        self.resource.DB.execute(S)
        results = list(self.resource.DB.Cur)
        left_context_words = [self.lexicon.get_orth(x) for (x, ) in results]
        left_context_words = [''] * (left_span - len(left_context_words)) + left_context_words

        S = self.sql_string_get_wordid_in_range(
                token_id + number_of_tokens, 
                token_id + number_of_tokens + options.cfg.context_right - 1, source_id)
        self.resource.DB.execute(S)
        results = list(self.resource.DB.Cur)
        right_context_words = [self.lexicon.get_orth(x) for (x, ) in results]
        right_context_words = right_context_words + [''] * (options.cfg.context_right - len(right_context_words))

        options.cfg.verbose = old_verbose

        if options.cfg.context_mode == CONTEXT_STRING:
            S = self.sql_string_get_wordid_in_range(
                    token_id,
                    token_id + number_of_tokens - 1,
                    source_id)
            self.resource.DB.execute(S)
            results = list(self.resource.DB.Cur)
            target_words = [self.lexicon.get_orth(x) for (x, ) in results]
        else:
            target_words = []
        return (left_context_words, target_words, right_context_words)

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
        tab = tab[tab.coquery_invisible_origin_id == source_id]
        tab["end"] = tab.apply(
            lambda x: x["coquery_invisible_corpus_id"] + x["coquery_invisible_number_of_tokens"],
            axis=1)
        for x in tab.index:
            id_list += [y for y in range(
                int(tab.loc[x].coquery_invisible_corpus_id), 
                int(tab.loc[x].end))]

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

        #print(context)
        widget.ui.context_area.setText(collapse_words(context))

    
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
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

from errors import *
import tokens
import options
import sqlwrap
import time
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
        def __init__(self, provides):
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
            for current_attribute in provides:
                self.__setattr__(current_attribute, None)
            self.attributes = provides
                
        def set_values(self, value_list):
            #assert len(value_list) == len(self.attributes), "provided values: %s, expected: %s" % (value_list, self.attributes)
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
    
class BaseResource(object):
    wildcards = ["*", "?"]
    pass

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
                L += ["LC%s" % (x+1) for x in range(options.cfg.context_columns)[::-1]]
                L += ["X%s" % (x+1) for x in range(max_number_of_tokens)]
                L += ["RC%s" % (x+1) for x in range(options.cfg.context_columns)]
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

    def get_posid_list(self, token):
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
                        raise TextFilterError
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
        raise TextFilterError
    
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
                if CORP_SOURCE in requested or CORP_FILENAME in requested or CORP_CONTEXT in requested or options.cfg.source_filter:
                    self.table_list.add(self.resource.corpus_table)
                    self.column_list.add("{}.{}".format(
                        self.resource.corpus_table,
                        self.resource.corpus_source_id))

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
                for i in range(options.cfg.context_span):
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
                for i in range(options.cfg.context_span):
                    table_string_list.append(
                        "INNER JOIN (SELECT {corpus}.{token_id}, {word}.{label} AS RC{num} FROM {corpus}, {word} WHERE {corpus}.{corpus_word_id} = {word}.{word_id}) AS cr{num} ON (cr{num}.{token_id} = {corpus}.{token_id} + {num})".format(
                            num=i + 1,
                            corpus=self.resource.corpus_table,
                            token_id=self.resource.corpus_id,
                            corpus_word_id=self.resource.corpus_word_id,
                            word=self.resource.word_table,
                            word_id=self.resource.word_id,
                            label=self.resource.word_label))
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

    def get_whereclauses(self, Token, WordTarget, PosTarget):
        if not Token:
            return []

        where_clauses = []
        if self.resource.name == "coca" and self.resource.word_table == "lex":
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
                
            if options.cfg.context_span or options.cfg.context_columns:
                context = max(options.cfg.context_span, options.cfg.context_columns)
                self.column_list.update(["cl{num}.LC{num}".format(num=x+1) for x in range(context)])
                self.column_list.update(["cr{num}.RC{num}".format(num=x+1) for x in range(context)])
            
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
                if any([x in Query.Session.output_fields for x in [CORP_SOURCE, CORP_FILENAME, CORP_CONTEXT]]):
                    self.column_list.add("e1.{} AS SourceId".format(
                        self.resource.corpus_source_id))
                self.column_list.update(["e{num}.{corpus_word} AS W{num}".format(num=x+1, corpus_word=self.resource.corpus_word_id) for x in range(Query.number_of_tokens)])
               
        if only_names:
            return ", ".join([x.rpartition(" AS ")[-1] for x in self.column_list])
        if options.cfg.verbose:
            return ",\n\t".join(self.column_list)
        else:
            return ", ".join(self.column_list)
    
    def yield_query_results(self, Query, self_joined=False):
        # see if there are already results for the current query string 
        # in the Session cache. If so, do not run the query at all.
        #if Query.query_string in Query.Session._results:
            #return
            #yield
        column_string = self.sql_string_run_query_column_string(Query, self_joined)
        table_string = self.sql_string_run_query_table_string(Query, self_joined)

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

        if options.cfg.verbose:
            query_string = query_string.replace("SELECT ", "SELECT \n\t")
            query_string = query_string.replace("FROM ", "\nFROM \n\t")
            query_string = query_string.replace("WHERE ", "\nWHERE \n\t")

        # Run the MySQL query:
        #print(query_string)
        
        #sys.exit(0)
        cursor = self.resource.DB.execute_cursor(query_string)
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
        if source_id:
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
        if options.cfg.context_span:
            span = options.cfg.context_span
        elif options.cfg.context_columns:
            span = options.cfg.context_columns

        if span:
            if span > token_id:
                start = 1
            else:
                start = token_id - span
                
        self.resource.DB.execute(
            self.sql_string_get_wordid_in_range(
                start, 
                token_id - 1, source_id))
        left_context_words = [self.lexicon.get_entry(x, [LEX_ORTH]).orth for (x, ) in self.resource.DB.Cur]
        left_context_words = [''] * (span - len(left_context_words)) + left_context_words

        self.resource.DB.execute(
            self.sql_string_get_wordid_in_range(
                token_id + number_of_tokens, 
                token_id + number_of_tokens + span - 1, source_id))
        right_context_words = [self.lexicon.get_entry(x, [LEX_ORTH]).orth for (x, ) in self.resource.DB.Cur]
        right_context_words =  right_context_words + [''] * (span - len(right_context_words))

        return (left_context_words, right_context_words)

    def sql_string_get_source_info(self, source_id):
        if "source_table" in dir(self.resource) and "source_table_alias" in dir(self.resource):
            return "SELECT * FROM {} WHERE {}.{} = {}".format(
                self.resource.source_table_construct, 
                self.resource.source_table_alias, 
                self.resource.source_id, source_id)
        else:
            raise ResourceIncompleteDefinitionError

    def get_source_info(self, source_id):
        source_info_header = self.get_source_info_header()
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
            return "SELECT {} as File FROM {} WHERE {} = {}".format(
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
        stats = {}
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
        
        
        #stats = self.lexicon.get_statistics()
        #stats["corpus_features"] = " ".join(self.provides)
        #if CORP_CONTEXT in self.provides:
            #self.resource.DB.execute("SELECT COUNT(*) FROM {corpus_table}".format(
                #corpus_table=self.resource.corpus_table))
            #stats["corpus_tokens"] = self.resource.DB.Cur.fetchone()[0]
        #if CORP_SOURCE in self.provides:
            #self.resource.DB.execute("SELECT COUNT(*) FROM {source_table}".format(
                #source_table=self.resource.source_table))
            #stats["corpus_sources"] = self.resource.DB.Cur.fetchone()[0]
        #if CORP_FILENAME in self.provides:
            #self.resource.DB.execute("SELECT COUNT(*) FROM {}".format(
                #self.resource.file_table))
            #stats["corpus_files"] = self.resource.DB.Cur.fetchone()[0]
        
        #return stats

class TestLexicon(BaseLexicon):
    def is_part_of_speech(self, pos):
        return pos in ["N", "V"]
    

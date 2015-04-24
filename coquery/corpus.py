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


from errors import *
import tokens
import options

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
            assert len(value_list) == len(self.attributes), "provided values: %s, expected: %s" % (value_list, self.attributes)
            for i, current_attribute in enumerate(self.attributes):
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

    def get_entry(self, word_id):
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

    def find_other_wordforms(self, word):
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

    def run_query(self, Query):
        """ Runs the specified query. 
        
        Each row of the output contains a column for each token in the 
        query. Token columns are labeled W1, W2, ... . They contain a 
        word_id that can be used as an argument for Lexicon.get_entry(word_id) 
        to look up the associated lexicon entry.
        
        Depending the features provided by the corpus, the following columns
        are also contained in the output row:
        
        TokenId     required by CORP_CONTEXT and CORP_TIMING, a unique 
                    identifier for the token that allows retrieval of the 
                    context. Additionally, the TokenId is used to access 
                    timing data.
        SourceId    required by CORP_SOURCE, specifies the source in which the 
                    token can be found
        SpeakerId   required by CORP_SPEAKER, specifies the speaker who has 
                    produced the token
        FileId      required by CORP_FILE, specifies the file the in which
                    token can be found
        """
        raise CorpusUnsupportedFunctionError
    
    def get_word_id(self, token_id):
        """ returns the word id of the token specified by token_id. """
        raise CorpusUnsupportedFunctionError
    
    def get_context(self, token_id):
        """ returns the context of the token specified by token_id. """
        raise CorpusUnsupportedFunctionError
    
    def get_context_headers(self, context_span, max_number_of_tokens, separate_columns):
        if self.provides_feature(CORP_CONTEXT):
            L = []
            if separate_columns:
                L += ["LC%s" % (x+1) for x in range(context_span)[::-1]]
                L += ["X%s" % (x+1) for x in range(max_number_of_tokens)]
                L += ["RC%s" % (x+1) for x in range(context_span)]
            else:
                L.append ("Context")
            return L
        else:
            raise CorpusUnsupportedFunctionError
        
    def get_source_info(self, source_id):
        """ returns a list containing the text information associated with 
        the text specified by TextId. If text_id == None, return a placeholder
        for failed queries. """
        raise CorpusUnsupportedFunctionError
    
    def get_source_info_headers(self):
        raise CorpusUnsupportedFunctionError

    def get_speaker_info(self, speaker_id):
        """ returns a list containing the speaker information associated 
        with the speaker specified by speaker_id. """
        raise CorpusUnsupportedFunctionError

    def get_speaker_info_headers(self):
        raise CorpusUnsupportedFunctionError

    def get_time_info(self, token_id):
        """ returns a list containing timing information associated 
        with the token_id. """
        raise CorpusUnsupportedFunctionError

    def get_time_info_headers(self):
        raise CorpusUnsupportedFunctionError

    def get_file_info(self, file_id):
        """ returns a list containing filename information associated 
        with the file_id. """
        raise CorpusUnsupportedFunctionError

    def get_file_info_headers(self):
        raise CorpusUnsupportedFunctionError

    def provides_feature(self, x):
        return x in self.provides + self.lexicon.provides

    def get_statistics(self):
        raise CorpusUnsupportedFunctionError
    
class SQLResource(BaseResource):
    wildcards = ["%", "_"]
    def has_wildcards(self, Token):
        """ 
has_wildcards() returns True if the token string contains an SQL wildcard,
i.e. either % or _.
        """
        if len(Token.S) < 2:
            return False
        else:
            return any([x in self.wildcards for x in Token.S])
    
    def get_operator(self, Token):
        """ returns a string containing the appropriate operator for an 
        SQL query using the Token (considering wildcards and negation) """
        Operators = {True:                                  # has wildcard?
                        {True: "NOT LIKE", False: "LIKE"},  # is negated?
                     False:                                 # no wildcard?
                        {True: "!=", False: "="}}           # is negated?
        return Operators [self.has_wildcards(Token)] [False]
        #return Operators [self.has_wildcards(Token)] [Token.negated]

class SQLLexicon(BaseLexicon):
    entry_cache = {}
    
    def sql_string_is_part_of_speech(self, pos):
        current_token = tokens.COCAToken(pos, self)
        return "SELECT {pos_id_column} FROM {pos_table} WHERE {pos_label_column} {operator} '{pos}' LIMIT 1".format(
            pos_id_column=self.resource.pos_id_column, 
            pos_table=self.resource.pos_table, 
            pos_label_column=self.resource.pos_label_column,
            operator=self.resource.get_operator(current_token),
            pos=pos)

    def sql_string_find_other_wordforms(self, match):
        return 'SELECT {word_id} FROM {word_table} WHERE {word_lemma_id} IN (SELECT {word_lemma_id} FROM {word_table} WHERE {word_label} {operator} "{match}")'.format(
            word_id=self.resource.word_id_column,
            word_table=self.resource.word_table,
            word_label=self.resource.word_label_column,
            word_lemma_id=self.resource.word_lemma_id_column,
            operator=self.resource.get_operator(match),
            match=match)
    
    def sql_string_get_entry(self, word_id):
        ## FIXME: currently, get_entry fetches all provided fields, but this
        ## may be a performance hit (especially with linked tables).
        #select_variable_list = []
        #where_list = ["{}.{} = {}".format(
            #self.resource.word_table,
            #self.resource.word_id_column,
            #word_id)]
        #table_list = [self.resource.word_table]
        #for current_attribute in self.provides:
            #if current_attribute == LEX_WORDID:
                #select_variable_list.append("{}.{}".format(
                    #self.resource.word_table,
                    #self.resource.word_id_column))
            
            #if current_attribute == LEX_LEMMA:
                #if self.resource.lemma_table != self.resource.word_table:
                    #select_variable_list.append("LEMMATABLE.{}".format(
                        #self.resource.lemma_label_column))
                    #table_list.append("{} AS LEMMATABLE".format(self.resource.lemma_table))
                    #where_list.append("{}.{} = LEMMATABLE.{}".format(
                        #self.resource.word_table,
                        #self.resource.word_lemma_id_column,
                        #self.resource.lemma_id_column))
                #else:
                    #select_variable_list.append("{}.{}".format(
                        #self.resource.lemma_table,
                    #self.resource.lemma_label_column))
            
            #if current_attribute == LEX_ORTH:
                #select_variable_list.append("{}.{}".format(
                    #self.resource.word_table,
                    #self.resource.word_label_column))
            
            #if current_attribute == LEX_POS:
                #if self.resource.pos_table != self.resource.word_table:
                    #select_variable_list.append("PARTOFSPEECH.{}".format(
                        #self.resource.transcript_label_column))
                    #table_list.append("{} AS PARTOFSPEECH".format(self.resource.pos_table))
                    #where_list.append("{}.{} = PARTOFSPEECH.{}".format(
                        #self.resource.word_table,
                        #self.resource.word_pos_id_column,
                        #self.resource.pos_id_column))
                #else:
                    #select_variable_list.append("{}.{}".format(
                        #self.resource.pos_table,
                        #self.resource.pos_label_column))
            
            #if current_attribute == LEX_PHON:
                #if self.resource.transcript_table != self.resource.word_table:
                    #select_variable_list.append("TRANSCRIPT.{}".format(
                        #self.resource.transcript_label_column))
                    #table_list.append("{} AS TRANSCRIPT".format(self.resource.transcript_table))
                    #where_list.append("{}.{} = TRANSCRIPT.{}".format(
                        #self.resource.word_table,
                        #self.resource.word_transcript_id_column,
                        #self.resource.transcript_id_column))
                #else:
                    #select_variable_list.append("{}.{}".format(
                        #self.resource.transcript_table,
                        #self.resource.transcript_label_column))
                    
                
        #select_variables = ", ".join(select_variable_list)
        #select_string = ("SELECT {0} FROM {1}{2}".format(
            #", ".join(select_variable_list),
            #", ".join(table_list),
            #(" WHERE " + " AND ".join(where_list)) if where_list else ""))
        #return select_string
        
        # FIXME: currently, get_entry fetches all provided fields, but this
        # may be a performance hit (especially with linked tables).
        
        if word_id == "NA":
            word_id = -1
        
        select_variable_list = []
        where_list = ["{}.{} = {}".format(
            self.resource.word_table,
            self.resource.word_id_column,
            word_id)]
        table_list = [self.resource.word_table]
        for current_attribute in self.provides:
            if current_attribute == LEX_WORDID:
                select_variable_list.append("{}.{}".format(
                    self.resource.word_table,
                    self.resource.word_id_column))
            
            if current_attribute == LEX_LEMMA:
                if self.resource.lemma_table != self.resource.word_table:
                    select_variable_list.append("LEMMATABLE.{}".format(
                        self.resource.lemma_label_column))
                    table_list.append("LEFT JOIN {} AS LEMMATABLE ON {}.{} = LEMMATABLE.{}".format(
                        self.resource.lemma_table,
                        self.resource.word_table,
                        self.resource.word_lemma_id_column,
                        self.resource.lemma_id_column))
                else:
                    select_variable_list.append("{}.{}".format(
                        self.resource.lemma_table,
                    self.resource.lemma_label_column))
            
            if current_attribute == LEX_ORTH:
                select_variable_list.append("{}.{}".format(
                    self.resource.word_table,
                    self.resource.word_label_column))
            
            if current_attribute == LEX_POS:
                if self.resource.pos_table != self.resource.word_table:
                    select_variable_list.append("PARTOFSPEECH.{}".format(
                        self.resource.transcript_label_column))
                    table_list.append("LEFT JOIN {} AS PARTOFSPEECH ON {}.{} = PARTOFSPEECH.{}".format(
                        self.resource.pos_table,
                        self.resource.word_table,
                        self.resource.word_pos_id_column,
                        self.resource.pos_id_column))
                else:
                    select_variable_list.append("{}.{}".format(
                        self.resource.pos_table,
                        self.resource.pos_label_column))
            
            if current_attribute == LEX_PHON:
                if self.resource.transcript_table != self.resource.word_table:
                    select_variable_list.append("TRANSCRIPT.{}".format(
                        self.resource.transcript_label_column))
                    table_list.append("LEFT JOIN {} AS TRANSCRIPT ON {}.{} = TRANSCRIPT.{}".format(
                        self.resource.transcript_table,
                        self.resource.word_table,
                        self.resource.word_transcript_id_column,
                        self.resource.transcript_id_column))
                else:
                    select_variable_list.append("{}.{}".format(
                        self.resource.transcript_table,
                        self.resource.transcript_label_column))
                    
                
        select_variables = ", ".join(select_variable_list)
        select_string = ("SELECT {0} FROM {1}{2}".format(
            ", ".join(select_variable_list),
            " ".join(table_list),
            (" WHERE " + " AND ".join(where_list)) if where_list else ""))
        return select_string
    
    def sql_string_get_posid_list_where(self, token):
        comparing_operator = self.resource.get_operator(token)
        clause_list = []
        for current_pos in token.class_specifiers:
            current_token = tokens.COCAToken(current_pos, self)
            S = '{pos_label_column} {operator} "{value}"'.format(
                pos_label_column=self.resource.pos_label_column, 
                operator=comparing_operator, 
                value=current_token)
            clause_list.append (S)
        return "(%s)" % "OR ".join (clause_list)
    
    def sql_string_get_posid_list(self, token):
        where_string = self.sql_string_get_posid_list_where(token)
        return "SELECT DISTINCT {word_pos} FROM {word_table} WHERE {match_pos_id}".format(
            word_pos=self.resource.word_pos_column,
            word_table=self.resource.word_table,
            match_pos_id=where_string)

    def sql_string_get_wordid_list_where(self, token):
        # TODO: fix cfg.lemmatize
        # FIXME: this needs to be revised. 
        sub_clauses = []

        if token.lemma_specifiers:
            if LEX_LEMMA not in self.provides:
                raise LexiconUnsupportedFunctionError
            
            specifier_list = token.lemma_specifiers
            if self.resource.lemma_table != self.resource.word_table:
                target_column = "LEMMATABLE.{}".format(
                    self.resource.lemma_label_column)
            else:
                target_column = "{}.{}".format(
                    self.resource.lemma_table,
                    self.resource.lemma_label_column)
        else:
            specifier_list = token.word_specifiers
            target_column = "{}.{}".format(
                self.resource.word_table,
                self.resource.word_label_column)

        for CurrentWord in specifier_list:
            if CurrentWord != "*":
                CurrentToken = tokens.COCAWord(CurrentWord, self)
                CurrentToken.negated = token.negated
                sub_clauses.append('%s %s "%s"' % (target_column, self.resource.get_operator(CurrentToken), CurrentToken))
                
        for current_transcript in token.transcript_specifiers:
            if current_transcript:
                CurrentToken = tokens.COCAWord(current_transcript, self)
                CurrentToken.negated = token.negated
                if self.resource.transcript_table != self.resource.word_table:
                    target_column = "TRANSCRIPT.{}".format(
                        self.resource.transcript_label_column)
                else:
                    target_column = "{}.{}".format(
                        self.resource.transcript_table,
                        self.resource.transcript_label_column)
                sub_clauses.append('%s %s "%s"' % (target_column, self.resource.get_operator(CurrentToken), CurrentToken))
        
        where_clauses = []
        
        if sub_clauses:
            where_clauses.append("(%s)" % " OR ".join (sub_clauses))
        if token.class_specifiers:
            where_clauses.append(self.sql_string_get_posid_list_where(token))
        return " AND ".join(where_clauses)
            
    def sql_string_get_wordid_list(self, token):
        # FIXME: what if POS is in a different table?
        # FIXME: This needs to me merged with the stuff from sql_string_get_entry!
        where_list = [self.sql_string_get_wordid_list_where(token)]
        table_list = [self.resource.word_table]
        if token.class_specifiers or token.lemma_specifiers:
            if self.resource.lemma_table != self.resource.word_table:
                table_list.append("LEFT JOIN {} AS LEMMATABLE ON {}.{} = LEMMATABLE.{}".format(
                    self.resource.lemma_table,
                    self.resource.word_table,
                    self.resource.word_lemma_id_column,
                    self.resource.lemma_id_column))
        
        if token.transcript_specifiers:
            if self.resource.transcript_table != self.resource.word_table:
                table_list.append("LEFT JOIN {} AS TRANSCRIPT ON {}.{} = TRANSCRIPT.{}".format(
                    self.resource.transcript_table,
                    self.resource.word_table,
                    self.resource.word_transcript_id_column,
                    self.resource.transcript_id_column))
                
        where_string = " AND ".join(where_list)
        S = "SELECT {}.{} FROM {} WHERE ({})".format(
                self.resource.word_table,
                self.resource.word_id_column,
                " ".join(table_list),
                where_string)
        return S

    def is_part_of_speech(self, pos):
        self.resource.DB.execute(self.sql_string_is_part_of_speech(pos), ForceExecution=True)
        Result = self.resource.DB.fetch_all ()
        return len(Result) > 0
    
    def find_other_wordforms(self, Word):
        if LEX_LEMMA not in self.provides:
            raise LexiconUnsupportedFunctionError
        
        current_word = tokens.COCAWord(Word, self)
        # create an inner join of lexicon, containing all rows that match
        # the string stored in current_word:
        self.resource.DB.execute(self.sql_string_find_other_wordforms(current_word))
        return [result[0] for result in self.resource.DB.Cur]
    
    def get_entry(self, word_id):
        # FIXME: currently, get_entry fetches all provided fields, but this
        # may be a performance issue (especially with linked tables).
        if word_id in self.entry_cache:
            return self.entry_cache[word_id]
        error_value = [word_id] + ["<na>"] * (len(self.provides) - 1)
        entry = self.Entry(self.provides)
        try:
            S = self.sql_string_get_entry(word_id)
            self.resource.DB.execute(S)
            Results = self.resource.DB.Cur.fetchone()
            if Results:
                entry.set_values(Results)
            else:
                entry.set_values(error_value)
        except (SQLOperationalError):
            entry.set_values(error_value)
        self.entry_cache[word_id] = entry
        return entry

    def get_posid_list(self, token):
        try:
            self.resource.DB.execute(self.sql_string_get_posid_list(token))
        except SQLProgrammingError:
            return []
        return [x[0] for x in self.resource.DB.fetch_all()]

    def get_wordid_list(self, token):
        if token.S == "*":
            return []
        try:
            self.resource.DB.execute(self.sql_string_get_wordid_list(token))
        except SQLOperationalError:
            return []
        Results = self.resource.DB.fetch_all ()
        if not Results:
            return [-1]
        else:
            return [x[0] for x in Results]
        
    def get_statistics(self):
        stats = {}
        self.resource.DB.execute("SELECT COUNT(*) FROM {word_table}".format(
            word_table=self.resource.word_table))
        stats["lexicon_words"] = self.resource.DB.Cur.fetchone()[0]
        if LEX_POS in self.provides:
            self.resource.DB.execute("SELECT COUNT(DISTINCT {pos_column}) FROM {pos_table}".format(
                pos_table=self.resource.pos_table,
                pos_column=self.resource.pos_id_column))
            stats["lexicon_distinct_pos"] = self.resource.DB.Cur.fetchone()[0]
        if LEX_LEMMA in self.provides:
            self.resource.DB.execute("SELECT COUNT(DISTINCT {lemma_column}) FROM {lemma_table}".format(
                lemma_table=self.resource.lemma_table,
                lemma_column=self.resource.lemma_id_column))
            stats["lexicon_lemmas"] = self.resource.DB.Cur.fetchone()[0]
        return stats

class SQLCorpus(BaseCorpus):
    def __init__(self, lexicon, resource):
        super(SQLCorpus, self).__init__(lexicon, resource)
        self.query_results = None
    
    def get_whereclauses(self, Token, WordTarget, PosTarget):
        if not Token:
            return []
        WhereClauses = []
        if Token.word_specifiers or Token.lemma_specifiers or Token.transcript_specifiers:
            L = self.lexicon.get_wordid_list(Token)
            if L:
                WhereClauses.append ("%s IN (%s)" % (WordTarget, ", ".join (map (str, L))))
        else:
            if Token.class_specifiers:
                L = self.lexicon.get_posid_list(Token)
                if L: 
                    WhereClauses.append ("%s IN (%s)" % (PosTarget, ", ".join (["'%s'" % x for x in L])))
        return WhereClauses
    
    def run_query(self, Query):
        def get_table_string(number, token):
            # FIXME: this needs to be revised so that pos can be in a different
            # table, similarly to the sql_string_get_entry() above
            if token.class_specifiers and not (token.lemma_specifiers or token.word_specifiers):
                S = "(SELECT {corpus_table}.{corpus_token_id}, {corpus_table}.{corpus_word_id}, {pos_table}.{pos_column} FROM {corpus_table},{word_table} WHERE {corpus_table}.{corpus_word_id} = {word_table}.{word_id}) AS e{num}".format(
                    corpus_table=self.resource.corpus_table,
                    corpus_token_id=self.resource.corpus_token_id_column,
                    corpus_word_id=self.resource.corpus_word_id_column,
                    word_table=self.resource.word_table,
                    word_id=self.resource.word_id_column,
                    pos_table=self.resource.pos_table,
                    pos_column=self.resource.pos_label_column,
                    num=number)
            else:
                S = "(SELECT {corpus_table}.{corpus_token_id}, {corpus_table}.{corpus_word_id} FROM {corpus_table}) AS e{num}".format(
                    corpus_token_id=self.resource.corpus_token_id_column,
                    corpus_word_id=self.resource.corpus_word_id_column,
                    corpus_table=self.resource.corpus_table, num=number)
            return S        

        where_clauses = []
        join_list = []

        for i, CurrentToken in enumerate (Query.tokens):
            CurrentToken.parse()
            table_string = get_table_string(i+1, CurrentToken)
            # create a new inner join for any token on top of the first one:
            if len(join_list) > 0:
                table_string = "INNER JOIN {table_string} ON (e{num1}.{token_id} = e1.{token_id} + {num})".format(
                    token_id=self.resource.corpus_token_id_column,
                    table_string=table_string,
                    num1=i+1, num=i)
            join_list.append(table_string)

            if "corpus_word_id_column" in dir(self.resource) and "word_pos_id_column" in dir(self.resource):
                current_where_clauses = self.get_whereclauses(
                    CurrentToken, 
                    self.resource.corpus_word_id_column, 
                    self.resource.word_pos_id_column)
            else:
                current_where_clauses = []

            if current_where_clauses:
                prefixed_clauses = ["e{num}.{clause}".format(
                    num=i+1, 
                    clause=clause) for clause in current_where_clauses]
                where_clauses.append (" AND ".join(prefixed_clauses))

        word_variables = ["e{num}.{corpus_word_id}".format(
            corpus_word_id=self.resource.corpus_word_id_column, 
            num=x+1) for x in range(Query.number_of_tokens)]

        select_variables = ["e1.{token_id} AS TokenId".format(
            token_id=self.resource.corpus_token_id_column,
            num=Query.number_of_tokens)]
        select_variables += ["%s AS W%s" % (word, number+1) for number, word in enumerate(word_variables)]

        if Query.requested(CORP_SOURCE):
            select_variables.append("e1.{corpus_source_id} AS SourceId".format(
                corpus_source_id=self.resource.corpus_source_id_column))
            join_list[0] = join_list[0].replace(
                "SELECT ", 
                "SELECT {corpus_table}.{corpus_source_id},".format(
                    corpus_table=self.resource.corpus_table,
                    corpus_source_id=self.resource.corpus_source_id_column))
        
        if where_clauses:
            new_list = []
            for i, current_clause in enumerate(where_clauses):
                if "-1" in current_clause:
                    if Query.tokens[i].negated:
                        new_list.append(current_clause.replace(" IN ", " NOT IN "))
                    else:
                        Query.set_result_list([None] * len(select_variables))
                        return
            where_string = "WHERE (%s)" % (" AND ".join(where_clauses))            
        else:
            where_string = ""
        join_string = " ".join(join_list)

        #if options.cfg.MODE == query_mode_frequencies:
            #query_string = "SELECT {select_variables},COUNT(*) AS {freq_label} FROM {join_string} {where_string} GROUP BY {group_variables} ORDER BY NULL".format(
                #select_variables=", ".join(select_variables), 
                #freq_label=options.cfg.freq_label, 
                #join_string=join_string, 
                #where_string=where_string, 
                #group_variables=", ".join(word_variables))
        #else:
            #query_string = "SELECT %s FROM %s %s" % (", ".join(select_variables), join_string, where_string)
        query_string = "SELECT %s FROM %s %s" % (", ".join(select_variables), join_string, where_string)
        if options.cfg.number_of_tokens:
            query_string = "%s LIMIT %s" % (query_string, options.cfg.number_of_tokens)
        try:
            cursor = self.resource.DB.execute_cursor (query_string)
        except SQLOperationalError:
            raise SQLOperationalError(query_string)
            Query.Results = [None]
        else:
            Query.set_result_list(cursor)
    
    def get_word_id(self, token_id):
        if len(token_id) == 1:
            S = "SELECT {word_id} FROM {corpus_table} WHERE {token_id} = {current_id}"
            current_id = token_id
        else:
            S = "SELECT {word_id} FROM {corpus_table} WHERE {token_id} IN ({current_id})"
            current_id = ", ".join([str(x) for x in token_id])

        query_string = S.format(
            word_id=self.resource.corpus_word_id_column,
            corpus_table=self.resource.corpus_table,
            token_id=self.resource.corpus_token_id_column,
            current_id=current_id)
        self.resource.DB.execute(query_string)
        return [int(x[0]) for x in self.resource.DB.Cur]
    
    def get_context(self, token_id, number_of_tokens):
        if options.cfg.context_span > token_id:
            left_span = token_id - 1
        else:
            left_span = options.cfg.context_span
        start = token_id - left_span
        end = token_id + number_of_tokens + options.cfg.context_span - 1
        QueryString = "SELECT {word_id} AS W1 FROM {corpus_table} WHERE {token_id} BETWEEN {start} AND {end}".format(
            word_id=self.resource.corpus_word_id_column,
            corpus_table=self.resource.corpus_table,
            token_id=self.resource.corpus_token_id_column,
            start=start, end=end)
        self.resource.DB.execute(QueryString)
        ContextList = []
        i = start
        for i, CurrentResult in enumerate(self.resource.DB.Cur):
            entry = self.lexicon.get_entry(CurrentResult[0])
            # if the query is not case sensitive, capitalize the words that
            # match the query string:
            if not options.cfg.case_sensitive and i in range(left_span, left_span + number_of_tokens):
                ContextList.append (entry.orth.upper())
            else:
                ContextList.append (entry.orth)
        return ContextList

    def get_source_info(self, source_id):
        source_info_headers = self.get_source_info_headers()
        ErrorValue = ["<na>"] * len(source_info_headers)
        if not source_id:
            return ErrorValue
        try:
            cursor = self.resource.DB.execute_cursor("SELECT * FROM {source_table} WHERE {corpus_id} = {source_id}".format(
                source_table=self.resource.source_table,
                corpus_id=self.resource.source_id_column,
                source_id=source_id))
            Result = cursor.fetchone()
        except SQLOperationalError:
            return ErrorValue
        return [Result[x] for x in source_info_headers]
    
    def get_source_info_headers(self):
        return ["Text"]

    def get_statistics(self):
        stats = self.lexicon.get_statistics()
        if CORP_CONTEXT in self.provides:
            self.resource.DB.execute("SELECT COUNT(*) FROM {corpus_table}".format(
                corpus_table=self.resource.corpus_table))
            stats["corpus_tokens"] = self.resource.DB.Cur.fetchone()[0]
        if CORP_SOURCE in self.provides:
            self.resource.DB.execute("SELECT COUNT(*) FROM {source_table}".format(
                source_table=self.resource.source_table))
            stats["corpus_sources"] = self.resource.DB.Cur.fetchone()[0]
        if CORP_FILENAME in self.provides:
            self.resource.DB.execute("SELECT COUNT(*) FROM {source_table}".format(
                source_table=self.resource.source_table))
            stats["corpus_sources"] = self.resource.DB.Cur.fetchone()[0]
        
        return stats

Resource = BaseResource()

# -*- coding: utf-8 -*-
"""
FILENAME: coca.py -- corpus module for the Coquery corpus query tool

This module contains the classes required to make COCA queries.

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

from __future__ import print_function
import sys

import __init__

import logging

from corpus import *
import options
import sqlwrap
import tokens

class COCAResource(SQLResource):
    DB = sqlwrap.SqlDB (Host=options.cfg.db_host, Port=options.cfg.db_port, User=options.cfg.db_user, Password=options.cfg.db_password, Database=options.cfg.db_name)
    
    pos_table = "pos"
    pos_label_column = "PoS"
    pos_id_column = "PosId"

    word_table = "lexicon"
    word_id_column = "WordId"
    word_label_column = "Word"
    word_pos_column = "PosId"
    word_lemma_id_column = "Lemma"
    word_transcript_id_column = "Word"
    
    lemma_table = "lexicon"
    lemma_id_column = "Lemma"
    lemma_label_column = "Lemma"

    transcript_table = "cmudict.dict"
    transcript_id_column = "Text"
    transcript_label_column = "Transcript"

    corpus_table = "corpus"
    corpus_word_id_column = "WordId"
    corpus_token_id_column = "TokenId"
    corpus_source_id_column = "TextId"
    
    #source_table = "source"
    #source_id_column = "SourceId"


class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_ORTH, LEX_LEMMA, LEX_POS, LEX_PHON]

    pos_table = "pos"
    pos_label_column = "PoS"
    pos_id_column = "PosId"

    def is_part_of_speech(self, pos):
        self.resource.DB.execute("SELECT {pos_id_column} FROM {pos_table} WHERE {pos_label_column} LIKE '{pos_label}' LIMIT 1".format(pos_id_column=self.pos_id_column, pos_table=self.pos_table, pos_label_column=self.pos_label_column, pos_label=pos), ForceExecution=True)
        Result = self.resource.DB.fetch_all ()
        return len(Result) > 0
    
    def __init__(self, resource):
        super(Lexicon, self).__init__(resource)
        self.resource = resource
        self.resource.DB.execute("SELECT * FROM pos", ForceExecution=True)
        Results = self.resource.DB.fetch_all ()
        for CurrentResult in Results:
            if options.cfg.ignore_pos_chars:
                self.pos_dict[CurrentResult [0]] = CurrentResult [2]
            else:
                self.pos_dict[CurrentResult [0]] = CurrentResult [1]
        self.pos_dict[0] = "<na>"

    def get_entry(self, word_id):
        ErrorValue = [word_id, "<na>", "<na>", 369, 0]
        entry = self.Entry(self.provides)
        try:
            self.resource.DB.execute("SELECT WordId, Word, Lemma, PosId, Frequency FROM lexicon WHERE WordId = %s" % word_id)
            entry.word_id, entry.orth, entry.lemma, entry.pos, entry.freq = self.resource.DB.Cur.fetchone()
            if not entry.pos:
                entry.pos = "<na>"
            else:
                entry.pos = self.pos_dict[entry.pos]
        except (SQLOperationalError):
            entry.word_id, entry.orth, entry.lemma, entry.pos, entry.freq = ErrorValue
        except (IndexError, TypeError):
            logger.warning("WordId %s not found in lexicon." % word_id)
            entry.word_id, entry.orth, entry.lemma, entry.pos, entry.freq = ErrorValue
        return entry

    def find_other_wordforms(self, Word):
        current_word = tokens.COCAWord(Word, self)
        # create an inner join of lexicon, containing all rows that match
        # the string stored in current_word:
        self.resource.DB.execute('SELECT l1.WordId FROM (lexicon as l1) INNER JOIN lexicon AS l2 ON (l1.Lemma = l2.Lemma) AND (l1.Lemma != "") AND (l2.Word %s "%s")' % (self.resource.get_operator(current_word), current_word))
        return [result[0] for result in self.resource.DB.Cur]


    def get_posid_list(self, Token):
        """ return list containing all PosId that match the current token."""

        QueryString = "SELECT PosId FROM pos WHERE (%s)" % (self.get_posid_wherestring (Token))
        try:
            self.resource.DB.execute(QueryString, ForceExecution=True)
        except SQLProgrammingError:
            return []
        PosIdList = []
        Results = self.resource.DB.fetch_all ()
        for CurrentResult in Results:
            PosIdList.append (CurrentResult [0])
        return PosIdList

    def get_wordid_list(self, Token):
        if Token.S == "*":
            return []
        sub_clauses = []
        AnyWord = False
        if Token.lemma_specifiers:
            specifier_list = Token.lemma_specifiers
            target_column = "lexicon.Lemma"
        else:
            specifier_list = Token.word_specifiers
            target_column = "lexicon.Word"

        if options.cfg.lemmatize_tokens:
            for CurrentWord in specifier_list:
                if CurrentWord != "*":
                    return self.find_other_wordforms(CurrentWord)
                else:
                    AnyWord = True
        else:
            for CurrentWord in specifier_list:
                if CurrentWord != "*":
                    CurrentToken = tokens.COCAWord(CurrentWord, self)
                    CurrentToken.negated = Token.negated
                    sub_clauses.append('%s %s "%s"' % (target_column, self.resource.get_operator(CurrentToken), CurrentToken))

        where_clauses = []
        
        if sub_clauses:
            where_clauses.append(" OR ".join (sub_clauses))
        if Token.class_specifiers:
            where_clauses.append(self.get_posid_wherestring(Token))
        if len(where_clauses) == 2:
            where_string = "(%s) AND (%s)" % (tuple(where_clauses))
        else:
            where_string = where_clauses [0]
        if Token.class_specifiers:
            QueryString = "SELECT WordID FROM lexicon, pos WHERE (lexicon.PosId = pos.PosId) AND %s" % where_string
        else:
            QueryString = "SELECT WordId FROM lexicon WHERE (%s)" % (where_string)
        try:
            self.resource.DB.execute(QueryString)
        except SQLOperationalError:
            return []

        WordIdList = []
        Results = self.resource.DB.fetch_all ()
        if not Results:
            return [-1]
        for CurrentResult in Results:
            WordIdList.append (CurrentResult [0])
        return WordIdList

    def get_posid_wherestring (self, Token):
        comparing_operator = self.resource.get_operator(Token)
        WhereClauses = []
        for CurrentPOS in Token.class_specifiers:
            CurrentToken = tokens.COCAToken(CurrentPOS, self)
            WhereClauses.append ('PoS %s "%s"' % (comparing_operator, CurrentToken))
        return "(%s)" % " OR ".join (WhereClauses)

class Corpus(SQLCorpus):
    provides = [CORP_SOURCE, CORP_CONTEXT, CORP_STATISTICS]
    
    def __init__(self, lexicon, resource):
        super(Corpus, self).__init__(lexicon, resource)
        self.query_results = None
        
    def get_text_wherelist(self, S):
        Genres, Years, Negated = tokens.COCATextToken(S, self.lexicon).get_parse()
        
        GenreClauses = []
        YearClauses = []
        WhereClauses = []

        if Genres:
            for current_genre in Genres:
                if current_genre != "*":
                    if "*" in current_genre:
                        if Negated:
                            Operator = "NOT LIKE"
                        else:
                            Operator = "LIKE"
                        GenreClauses.append ("corpusBig.Genre %s '%s'" % (Operator, current_genre.replace ("*", "%")))
                    else:
                        if Negated:
                            Operator = "!="
                        else:
                            Operator = "="
                        GenreClauses.append ("corpusBig.Genre %s '%s'" % (Operator, current_genre))

        if Years:
            for CurrentYear in Years:
                if CurrentYear.count ("-") == 1:
                    Low, High = CurrentYear.split ("-")
                    if Negated:
                        Operator = "NOT BETWEEN"
                    else:
                        Operator = "BETWEEN"
                    YearClauses.append ("corpusBig.Year %s '%s' AND '%s'" % (Operator, Low, High))
                else:
                    if Negated:
                        Operator = "!="
                    else:
                        Operator = "="
                    YearClauses.append ("corpusBig.Year %s '%s'" % (Operator, CurrentYear))

        if GenreClauses:
            WhereClauses.append (" OR ".join (GenreClauses))
        if YearClauses:
            WhereClauses.append (" OR ".join (YearClauses))
        
        WhereString = "(" + ") AND (".join (WhereClauses) + ")"
        return WhereString
    
    def get_whereclauses(self, Token, WordTarget, PosTarget):
        WhereClauses = []
        if Token.word_specifiers or Token.lemma_specifiers:
            WhereClauses.append ("%s IN (%s)" % (WordTarget, ", ".join (map (str, self.lexicon.get_wordid_list(Token)))))
        else:
            if Token.class_specifiers:
                ## new:
                #wordid_set = set()
                #for current_item in Token.class_specifiers:
                    #current_token = tokens.COCAToken(current_item, self.lexicon)
                    #comparing_operator = self.get_operator(Token)
                    #sql_query = 'SELECT WordId from lexicon, pos WHERE lexicon.PosId = pos.PosId and pos.Pos %s "%s"' % (comparing_operator, current_token)
                    #self.resource.DB.execute(sql_query)
                    #Results = [x[0] for x in self.resource.DB.Cur.fetchall()]
                    #wordid_set = wordid_set.union(Results)
                #WhereClauses.append ("%s IN (%s)" % (WordTarget, ",".join (map (str, wordid_set))))
                ## end new
                WhereClauses.append ("%s IN (%s)" % (PosTarget, ", ".join (map (str, self.lexicon.get_posid_list(Token)))))
        return WhereClauses
    
    def run_query(self, Query):
        logger.info("Querying: %s" % Query)
        if Query.number_of_tokens > 7:
            logger.info("alternative query.")
            self.run_query_long(Query)
            return
        """ run a corpus query, and set the MySQL cursor to a structure
        corresponding to the results of the query. """

        if len(Query.tokens) == 0:
            Query.Results = [None]
            return
        
        if Query.query_string in self.query_cache:
            Query.Results = self.query_cache[Query.query_string]
            return 
        
        WhereClauses = []
        if Query.text_filter:
            WhereClauses = [self.get_text_wherelist(Query.text_filter)]
        for i, CurrentToken in enumerate (Query.tokens):
            CurrentToken.parse()
            current_clause = self.get_whereclauses(CurrentToken, "W%s" % (i + 1), "P%s" % (i + 1))
            if current_clause and "()" not in current_clause[0]:
                WhereClauses += current_clause

        WhereString = " AND ".join(WhereClauses)

        select_variables = []
        grouping_variables = []
        table_list = []
        #if options.cfg.MODE in (query_mode_frequencies):
            #select_variables.append("COUNT(*) AS Freq")
        if Query.number_of_tokens > 1:
            word_variables = ["W%s" % (x+1) for x in range(Query.number_of_tokens)]
            select_variables += word_variables
            #if options.cfg.MODE in (query_mode_frequencies):
                #grouping_variables = word_variables
            table_list = ["corpusBig"]
            genre_table = "corpusBig"
        else:
            #if options.cfg.MODE in (query_mode_frequencies):
                #grouping_variables = ["WordId"]
            select_variables.append("WordId AS W1")
            table_list = ["corpus"]
            genre_table = "sources"
            if options.cfg.text_filter or Query.requested(CORP_SOURCE):
                table_list.append ("sources")
                WhereString += " AND corpus.TextId = sources.TextId"
                WhereString = WhereString.replace("corpusBig.Genre", "sources.Genre")
                WhereString = WhereString.replace("corpusBig.Year", "sources.Year")
            WhereString = WhereString.replace("W1", "WordId")
            WhereString = WhereString.replace("P1", "PosId")
            
        WhereString = "WHERE (%s)" % WhereString
        if Query.requested(CORP_SOURCE):
            select_variables.append("{}.TextId AS SourceId".format(genre_table))
        if Query.requested(CORP_CONTEXT):
            select_variables.append("TokenId")
        if Query.requested(CORP_SPEAKER):
            select_variables.append("SpeakerId")
        if Query.requested(CORP_FILENAME):
            select_variables.append("SpeakerId")

        if grouping_variables:
            sql_query = "SELECT %s FROM %s %s GROUP BY %s" % (",".join(select_variables), ", ".join(table_list), WhereString, ",".join(grouping_variables))
        else:
            sql_query = "SELECT %s FROM %s %s" % (",".join(select_variables), ", ".join(table_list), WhereString)

        if options.cfg.number_of_tokens:
            sql_query = "%s LIMIT %s" % (sql_query, options.cfg.number_of_tokens)
        try:
            cursor = self.resource.DB.execute_cursor (sql_query)
        except SQLOperationalError:
            raise SQLOperationalError(sql_query)
            Query.Results = [None]
        else:
            Query.set_result_list(cursor)

    def run_query_long(self, Query):
        """ run a corpus query, and set the MySQL cursor to a structure
        corresponding to the results of the query. """

        WhereClauses = []
        if Query.text_filter:
            WhereClauses = [[self.get_text_wherelist(Query.text_filter)]]
        for i, CurrentToken in enumerate (Query.tokens):
            CurrentToken.parse()
            where_clause = self.get_whereclauses(CurrentToken, "WordId", "PosId")
            if where_clause:
                WhereClauses.append(where_clause)

        L = []
        for i, x in enumerate(WhereClauses):
            if x:
                L.append((len(x[0]), i))
            else:
                L.append((0, i))

        sql_query = ""
        offset = 0
        for i, (size, index) in enumerate(L):
            if size:
                offset = index
                break
        for i, (size, index) in enumerate(L):
            current_clause = WhereClauses [index]
            if not sql_query:
                if current_clause and "()" not in current_clause[0]:
                    sql_query = """
                    SELECT TokenId
                        FROM corpus
                        WHERE %s""" % (current_clause[0])
            else:
                if current_clause and "()" not in current_clause[0]:
                    sql_query += """
                        AND TokenId + %s IN
                        (SELECT TokenId 
                            FROM corpus
                            WHERE %s)""" % (index - offset, current_clause[0])
        self.resource.DB.execute(sql_query)
        tokens = [str(x[0] - offset) for x in self.resource.DB.fetch_all()]
        if not tokens:
            Query.Results = [None]
            return
        WhereString = "TokenId IN (%s)" % ", ".join(tokens)

        select_variables = []
        grouping_variables = []
        #if options.cfg.MODE in (query_mode_frequencies):
            #select_variables.append("COUNT(*) AS Freq")
            
        word_variables = ["W%s" % (x+1) for x in range(Query.number_of_tokens)]
        select_variables += word_variables
        #if options.cfg.MODE in (query_mode_frequencies):
            #grouping_variables = word_variables
        corpus_name = "corpusBig"
        if Query.requested(CORP_SOURCE):
            select_variables.append("TextId AS SourceId")
        if Query.requested(CORP_CONTEXT):
            select_variables.append("TokenId")
        if Query.requested(CORP_SPEAKER):
            select_variables.append("SpeakerId")
        if Query.requested(CORP_FILENAME):
            select_variables.append("SpeakerId")

        if grouping_variables:
            sql_query = "SELECT %s FROM %s WHERE (%s) GROUP BY %s" % (",".join(select_variables), corpus_name, WhereString, ",".join(grouping_variables))
        else:
            sql_query = "SELECT %s FROM %s WHERE (%s)" % (",".join(select_variables), corpus_name, WhereString)

        if options.cfg.number_of_tokens:
            sql_query = "%s LIMIT %s" % (sql_query, options.cfg.number_of_tokens)
        try:
            cursor = self.resource.DB.execute_cursor (sql_query)
        except SQLOperationalError:
            raise SQLOperationalError(sql_query)
            Query.Results = [None]
        else:
            Query.set_result_list(cursor)

    def get_context(self, token_id, number_of_tokens):
        start = max(0, token_id - options.cfg.context_span)
        end = token_id + number_of_tokens + options.cfg.context_span - 1
        QueryString = "SELECT WordId FROM corpus WHERE TokenId BETWEEN %s AND %s" % (start, end)
        self.resource.DB.execute(QueryString)
        ContextList = []
        i = start
        for i, CurrentResult in enumerate(self.resource.DB.Cur):
            entry = self.lexicon.get_entry(CurrentResult[0])
            # if the query is not case sensitive, capitalize the words that
            # match the query string:
            if not options.cfg.case_sensitive and i in range(options.cfg.context_span, options.cfg.context_span + number_of_tokens):
                ContextList.append (entry.orth.upper())
            else:
                ContextList.append (entry.orth)
        return ContextList
 
    def get_source_info(self, source_id):
        source_info_headers = self.get_source_info_headers()
        try:
            cursor = self.resource.DB.execute_cursor("SELECT * FROM sources WHERE TextId = %s" % source_id)
            Result = cursor.fetchone()
        except (SQLOperationalError, IndexError):
            return ["<na>" for x in source_info_headers]
        else:
            return [Result[x] for x in source_info_headers]

    def get_source_info_headers(self):
        return ["Year", "Genre", "Source", "Title"]


if __name__ == "__main__":
    print("""This module is part of the Coquery corpus query tool and cannot be run on its own.""", file=sys.stderr)
    sys.exit(1)
else:
    logger = logging.getLogger(__init__.NAME)
    Resource = COCAResource()

    logger.info("Connected to database %s@%s:%s."  % (options.cfg.db_name, options.cfg.db_host, options.cfg.db_port))
    logger.info("User=%s, password=%s" % (options.cfg.db_user, options.cfg.db_password))            

    if options.cfg.no_cache:
        logger.info("Resetting query cache.")
        self.resource.DB.execute("RESET QUERY CACHE")
        self.resource.DB.execute("SET SESSION query_cache_type = OFF")

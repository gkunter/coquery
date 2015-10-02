# -*- coding: utf-8 -*-
"""
FILENAME: tokens.py -- part of Coquery corpus query tool

This module defines classes that represent tokens in a query string.

"""

# tokens.py contains classes that represent a query token from a query 
# string. For instance, the COCA query [n*] has [v*] consists of the three
# tokens [n*], 'has', and [v*]. 
#
# The syntax used for the tokens is corpus-specific, and different classes
# can be used to represent different syntaxes.
#
# Each QueryToken should be parseable into four pieces of information:
#    
# word_specifiers     a list of strings that specify word-forms
# lemma_specifiers    a list of strings that specifies lemmas
# class_specifiers    a list of strings that specifies part-of-speech
# negated             a boolean flag that indicates negation
#
# The method parse() is used to translate the token string into these
# structures.

from __future__ import unicode_literals

import itertools
import string
import re

from defines import *
from errors import *

class QueryToken(object):
    """ 
    Define the QueryToken class. A query token is one element in a query
    string.
    """
    
    bracket_open = "("
    bracket_close = ")"
    transcript_open = "/"
    transcript_close = "/"
    or_character = "|"
    
    def __init__(self, S, lexicon, replace=True, parse=True):
        self.lexicon = lexicon
        self.S = S.strip()
        if replace:
            self.S = self.replace_wildcards(self.S)
        self.word_specifiers = []
        self.class_specifiers = []
        self.lemma_specifiers = []
        self.transcript_specifiers = []
        self.negated = False
        if parse:
            self.parse()
        
    def __eq__(self, S):
        return self.S == S
    
    def __ne__(self, S):
        return self.S != S
    
    def __repr__(self):
        if self.negated:
            return "NOT({})".format(self.S)
        else:
            return self.S
    
    @staticmethod
    def has_wildcards(s, replace=False):
        """
        Process wildcards and escaped characters in the string
        
        This method replaces any non-escaped occurrence of '*' and '?' by 
        their MySQL equivalents '%' and '_', respectively. At the same time,
        any occurrence of '%' and '?' is escaped so that these characters 
        can be queried.
        
        Parameters
        ----------
        s : string
            The string to be processed
        
        Returns
        -------
        s : string 
            The string with proper replacements and escapes
        """
        skip_next = False
        
        if s in set(["%", "_"]):
                return True
        for x in s:
            if skip_next:
                if x in ["%", "_"]:
                    return True
                skip_next = False
            else:
                if x == "\\":
                    skip_next = True
                else:
                    if x in ["%", "_"]:
                        return True
        return False
    
    @staticmethod
    def replace_wildcards(s):
        rep = []
        parse_next = False
        
        for x in s:
            if parse_next:
                rep.append(x)
                parse_next = False
            else:
                if x == "\\":
                    parse_next = True
                else:
                    if x == "*":
                        rep.append("%")
                    elif x == "?":
                        rep.append("_")
                    elif x == "_":
                        rep.append("\\_")
                    elif x == "%":
                        rep.append("\\%")
                    else:
                        rep.append(x)
        return "".join(rep)
        
    def get_parse(self):
        if self.word_specifiers:
            assert not self.lemma_specifiers
        return self.word_specifiers, self.lemma_specifiers, self.class_specifiers, self.negated

    def parse (self):
        """ parse() is the function that derives word, lemma, and class
        specificiations from the token string. The syntax is 
        corpus-specific. """
        self.lemma_specifiers = []
        self.class_specifiers = []
        self.word_specifiers = self.S.split(",")


class COCAToken(QueryToken):
    bracket_open = "["
    bracket_close = "]"
    transcript_open = "/"
    transcript_close = "/"
    NegationChar = "#"
    
    def parse (self):
        self.word_specifiers = []
        self.class_specifiers = []
        self.lemma_specifiers = []        
        self.transcript_specifiers = []

        while self.S.startswith(self.NegationChar):
            self.negated = not self.negated
            self.S = self.S[1:]
        
        if self.S == "//" or self.S == "[]":
            word_specification = self.S
            lemma_specification = None
            class_specification = None
            transcript_specification = None
        else:
            match = re.match("(\[(?P<lemma>.*)\]|/(?P<trans>.*)/|(?P<word>.*)){1}(\.\[(?P<class>.*)\]){1}", self.S)
            if not match:
                match = re.match("(\[(?P<lemma>.*)\]|/(?P<trans>.*)/|(?P<word>.*)){1}", self.S)

            word_specification = match.groupdict()["word"]
            lemma_specification = match.groupdict()["lemma"]
            transcript_specification = match.groupdict()["trans"]
            try:
                class_specification = match.groupdict()["class"]
            except KeyError:
                class_specification = None

        if word_specification:
            self.word_specifiers = [x.strip() for x in word_specification.split("|") if x.strip()]
        if transcript_specification:
            self.transcript_specifiers = [x.strip() for x in transcript_specification.split("|") if x.strip()]
        if lemma_specification:
            self.lemma_specifiers = [x.strip() for x in lemma_specification.split("|") if x.strip()]
        if class_specification:
            self.class_specifiers = [x.strip() for x in class_specification.split("|") if x.strip()]
        
        if lemma_specification and not class_specification:
            # check if all elements pass as part-of-speech-tags:
            if len(self.lemma_specifiers) == self.lexicon.check_pos_list(self.lemma_specifiers):
                # if so, interpret elements as part-of-speech tags:
                self.class_specifiers = self.lemma_specifiers
                self.lemma_specifiers = []
        # special case: allow *.[POS]
        if all([x in set(["%", "_"]) for x in self.word_specifiers]) and self.class_specifiers:
            self.word_specifiers = []

class COCAWord(COCAToken):
    """ A class that is simply parsed as a single word. """
    def parse(self):
        self.lemma_specifiers = []
        self.class_specifiers = []
        self.word_specifiers = [self.S]

class COCATextToken(COCAToken):
    # do not use the corpus to determine whether a token string like 
    # [xx] contains a part-of-speech tag:

    def get_parse(self):
        return self.word_specifiers, self.class_specifiers, self.negated
    
    def parse(self):
        """ 
Syntax:     GENRE.[YEAR], with alternatives separated by '|'.
            Negation is possible by preceding the filter with '-'
Examples:   FIC (equivalent to FIC.[*])
            -FIC (equivalent to ACAD|NEWS|MAG)
            FIC|ACAD 
            FIC.[2003]
            FIC|ACAD.[2003|2004]
            FIC|ACAD.[2003-2007]
            [2003-2007] (equivalent to *.[2003-2007])
        """
        super(COCATextToken, self).parse()
        # Special case that allows '.[*]' as a year specifier:
        if len(self.class_specifiers) == 1 and self.class_specifiers[0] in ["*", "?"]:
            self.class_specifiers = []
        # Special case that allows the use of '[2003]' format (i.e. 
        # specification of year, but not of genre:
        if self.lemma_specifiers:
            self.class_specifiers = self.lemma_specifiers
            self.lemma_specifiers = []

def parse_query_string(S, token_type):
    
    ST_NORMAL = 0
    ST_IN_BRACKET = 1
    ST_IN_TRANSCRIPT = 2
    
    tokens = []
    state = ST_NORMAL
    current_word = ""
    negated = False
    
    for current_char in S:
        if state == ST_NORMAL:
            if current_char == " ":
                if current_word:
                    tokens.append(current_word)
                    current_word = ""
            else:
                current_char = current_char.strip()
                if current_char:
                    current_word = "%s%s" % (current_word, current_char)
            if current_char == token_type.transcript_open:
                state = ST_IN_TRANSCRIPT
            elif current_char == token_type.bracket_open:
                state = ST_IN_BRACKET
                    
        elif state == ST_IN_BRACKET:
            if current_char == token_type.bracket_close:
                current_word = "%s%s" % (current_word, token_type.bracket_close)
                state = ST_NORMAL
            elif current_char not in [token_type.bracket_open, token_type.transcript_open, token_type.transcript_close]:
                current_word = "%s%s" % (current_word, current_char)
            else:
                raise TokenParseError(S)
            
        elif state == ST_IN_TRANSCRIPT:
            if current_char == token_type.transcript_close:
                current_word = "%s%s" % (current_word, token_type.transcript_close)
                state = ST_NORMAL
            elif current_char != token_type.or_character:
                current_word = "%s%s" % (current_word, current_char)
            # FIXME: or character may be broken
            elif current_char == token_type.or_character:
                current_word = "%s%s" % (current_word, current_char)
            else:
                raise TokenParseError(S)
                
    if state != ST_NORMAL:
        raise TokenParseError(S)
    if current_word:
        tokens.append(current_word)
    return tokens

def get_quantifiers(S):
    """
    Analyze the upper and lower quantification in the token string.
    
    In token strings, quantification is realized by attaching {n,m} to the
    query string, where n is the lower and m is the upper number of
    repetitions of that string.
    
    This function analyzes the passed string, and tries to determine n and
    m. If successful, it returns a tuple containing the token string without
    the quantification suffix, the lower value, and the upper value.
    
    If no quantifier is specified, or if the quantification syntax is 
    invalid, the unchanged query token string is returned, as well as n and 
    m set to 1.
    
    Parameters
    ----------
    S : string
        A query token string
        
    Returns
    -------
    tup : tuple
        A tuple containing three elements: the stripped token string, plus 
        the lower and upper number of repetions (in order)
    """
    match = re.match("(?P<token>.*)(\{\s*(?P<start>\d+)(,\s*(?P<end>\d+))?\s*\})+", S)
    if match:
        start = int(match.groupdict()["start"])
        try:
            end = int(match.groupdict()["end"])
        except TypeError:
            end = start
        token = match.groupdict()["token"]
        return (token, start, end)
    else:
        return (S, 1, 1)

def preprocess_query(S):
    """ 
    Analyze the quantification in S, and return a list of strings so that 
    all permutations are included.
    
    This function splits the string, analyzes the quantification of each
    token, and produces a query string for all quantified token combinations.
    
    Parameters
    ----------
    S : string
        A string that could be used as a query string
        
    Returns
    -------
    L : list
        A list of query strings
    """
    tokens = S.split(" ")
    token_lists = []
    token_map = []
    current_pos = 1
    for i, current_token in enumerate(tokens):
        L = []
        token, start, end = get_quantifiers(current_token)
        for x in range(start, end + 1):
            if not x:
                L.append([(current_pos, "")])
            else:
                L.append([(current_pos, token)] * x)
        current_pos += end
        token_lists.append(L)    
    L = []
    for x in itertools.product(*token_lists):
        l = [(number, token) for number, token in list(itertools.chain.from_iterable(x)) if token]
        L.append(l)
    return L
  
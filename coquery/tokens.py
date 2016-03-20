# -*- coding: utf-8 -*-

""" 
tokens.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import absolute_import

import itertools
import string
import re

from .defines import *
from .errors import *

class QueryToken(object):
    """ 
    Define the QueryToken class. A query token is one element in a query
    string.

    For instance, the COCA query [n*] has [v*] consists of the three
    tokens [n*], 'has', and [v*]. 
    
    The syntax used for the tokens is corpus-specific, and different classes
    can be used to represent different syntaxes.
    
    Each QueryToken should be parseable into several types of specification:
       
    word_specifiers       a list of strings that specify word-forms
    lemma_specifiers      a list of strings that specifies lemmas
    class_specifiers      a list of strings that specifies part-of-speech
    transcript_specifiers a list of strings that specifies phonemic transcripts
    gloss_specifiers      a list of strings that specify glosses
    negated               a boolean flag that indicates negation
    
    The method parse() is used to translate the token string into these
    structures.
    """
    
    bracket_open = "("
    bracket_close = ")"
    transcript_open = "/"
    transcript_close = "/"
    or_character = "|"
    
    def __init__(self, S, lexicon, replace=True, parse=True):
        self.lexicon = lexicon
        # token strings should always be unicode. They are already in 
        # Python 3.x, but for Python 2.7, we convert them first:
        try:
            S = S.decode("utf-8")
        except (UnicodeEncodeError):
            # This happens if S is already a unicode string
            pass
        except (AttributeError):
            # This happens in Python 3.x, because unicode strings don't have 
            # decode() any more.
            pass
        assert type(S) == type(u"")
        
        self.S = S.strip()
        if replace:
            self.S = self.replace_wildcards(self.S)
        self.word_specifiers = []
        self.class_specifiers = []
        self.lemma_specifiers = []
        self.transcript_specifiers = []
        self.gloss_specifiers = []
        self.negated = None
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
        Check if there are MySQL wildcards in the given string.
        
        This method considers non-escaped occurrence of '%' and '_' as
        wildcards.
        
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
        """
        Replace the wildcards '*' and '?' by SQL wildcards '%' and '_', 
        respectively. Escape exististing characters '%' and '_'.
        
        Parameters
        ----------
        s : string 
        
        Returns
        -------
        s : string 
            The input string, with wildcard characters replaced.
        """
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
        self.word_specifiers = [self.S]

class COCAToken(QueryToken):

    bracket_open = "["
    bracket_close = "]"
    transcript_open = "/"
    transcript_close = "/"
    quantification_open = "{"
    quantification_close = "}"
    pos_separator = "."
    negation_flag = "~"
    lemmatize_flag = "#"
    quote_open = '"'
    quote_close = '"'
    
    def parse (self):
        self.word_specifiers = []
        self.class_specifiers = []
        self.lemma_specifiers = []        
        self.transcript_specifiers = []
        self.gloss_specifiers = []

        word_specification = None
        lemma_specification = None
        class_specification = None
        transcript_specification = None
        gloss_specification = None

        self.negated = bool(self.S.count(self.negation_flag) & 1)
        self.negated = bool(re.search("^\s*({}*)".format(self.negation_flag), self.S).group(0).count(self.negation_flag) & 1)
        pat = "^\s*({}*)(\\\\#)?(#*)(.*)".format(self.negation_flag, self.lemmatize_flag)
        self.lemmatize = bool(re.search(pat, self.S).groups()[2])
        work = self.S.strip(self.negation_flag)
        
        if work == "//" or work == "[]":
            word_specification = work
        else:
            # try to match WORD|LEMMA|TRANS.[POS]:
            match = re.match("{}*(\[(?P<lemma>.*)\]|/(?P<trans>.*)/|(?P<word>.*)){{1}}(\.\[(?P<class>.*)\]){{1}}".format(self.lemmatize_flag), work)
            if not match:
                # try to match WORD|LEMMA|TRANS:
                match = re.match("{}*(\[(?P<lemma>.*)\]|/(?P<trans>.*)/|(?P<word>.*)){{1}}".format(self.lemmatize_flag), work)

            word_specification = match.groupdict()["word"]
            # word specification that begin and end with quotation marks '"'
            # are considered GLOSS specifications:
            if word_specification and re.match('".+"', word_specification):
                gloss_specification = word_specification
                word_specification = None
                gloss_specification = gloss_specification.strip('"')

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
        if gloss_specification:
            self.gloss_specifiers = [x.strip() for x in gloss_specification.split("|") if x.strip()]
        
        if lemma_specification and not class_specification:
            # check if all elements pass as part-of-speech-tags:
            if len(self.lemma_specifiers) == self.lexicon.check_pos_list(self.lemma_specifiers):
                # if so, interpret elements as part-of-speech tags:
                self.class_specifiers = self.lemma_specifiers
                self.lemma_specifiers = []
        # special case: allow *.[POS]
        if all([x in set(["%", "_"]) for x in self.word_specifiers]) and self.class_specifiers:
            self.word_specifiers = []

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
    """
    Split a string into query items, making sure that bracketing and
    quotations are valid. Escaping is allowed.
    
    If the string is not valid, e.g. because a bracket is opened, but not 
    closed, a TokenParseError is raised.
    """

    def add(S, ch):
        return "{}{}".format(S, ch)
    
    ST_NORMAL = "NORMAL"
    ST_IN_BRACKET = "BRACKET"
    ST_IN_TRANSCRIPT = "TRANS"
    ST_IN_QUOTE = "QUOTE"
    ST_IN_QUANTIFICATION = "QUANT"
    ST_POS_SEPARATOR = "POS"
    
    tokens = []
    state = ST_NORMAL
    current_word = ""
    negated = False
    
    escaping = False
    token_closed = False
    comma_added = False
    try:
        S = S.decode("utf-8")
    except UnicodeEncodeError:
        # already a unicode string
        pass
    except AttributeError:
        # using Python 3.x
        pass
    for current_char in S:
        if escaping:
            current_word = add(current_word, current_char)
            escaping = False
            continue
        if current_char == "\\":
            escaping = True
            continue
        
        # Normal word state:
        if state == ST_NORMAL:
            # Check for whitespace:
            if current_char == " ":
                if current_word:
                    tokens.append(current_word)
                    current_word = ""
                token_closed = False
                continue
            
            # Check for other characters
            
            if token_closed:
                if current_char not in [token_type.quantification_open, 
                                        token_type.pos_separator]:
                    # Raise exception if another character follows other than 
                    # the character opening a quantification:
                    raise TokenParseError("{}: expected a quantifier starting with <code style='color: #aa0000'>{}</code> or a part-of-speech specifier of the form <code style='color: #aa0000'>{}{}POS{}</code>".format(
                        S, 
                        token_type.quantification_open, 
                        token_type.pos_separator,
                        token_type.bracket_open,
                        token_type.bracket_close))
                elif current_char == token_type.pos_separator:
                    state = ST_POS_SEPARATOR
                    token_closed = False

            if current_char in set([token_type.negation_flag, token_type.lemmatize_flag]):
                current_word = add(current_word, current_char)
                continue
            
            # check for opening characters:
            if current_char in set([token_type.transcript_open, token_type.bracket_open, token_type.quantification_open, token_type.quote_open]):
                if current_word.strip("".join([token_type.negation_flag, token_type.lemmatize_flag])):
                    # raise an exception if an opening bracket occurs within
                    # a word, but not after a full stop (i.e. if it does not 
                    # open a POS specification):
                    if current_char == token_type.bracket_open:
                        if len(current_word) < 2 or current_word[-1] != ".":
                            raise TokenParseError("{}: unexpected opening bracket <code style='color: #aa0000'>{}</code> within a word".format(S, token_type.bracket_open))
                    # any character other than an opening quantification is 
                    # forbidden if the current word is not empty
                    elif current_char != token_type.quantification_open:
                        raise TokenParseError("{}: Only quantifiers starting with <code style='color: #aa0000'>{}</code> are allowed after a query token (encountered {})".format(S, token_type.quantification_open, current_char))
                else:
                    # quantifications are only allowed if they follow a 
                    # query item:
                    if current_char == token_type.quantification_open:
                        raise TokenParseError("{}: Query items may not start with the quantifier bracket <code style='color: #aa0000'>{}</code>".format(S, token_type.quantification_open))
                
                # set new state:
                if current_char == token_type.transcript_open:
                    state = ST_IN_TRANSCRIPT
                elif current_char == token_type.bracket_open:
                    state = ST_IN_BRACKET
                elif current_char == token_type.quote_open:
                    state = ST_IN_QUOTE
                elif current_char == token_type.quantification_open:
                    state = ST_IN_QUANTIFICATION
                    comma_added = False

            current_char = current_char.strip()

            # add character to word:
            if current_char:
                current_word = add(current_word, current_char)
        
        elif state == ST_POS_SEPARATOR:
            current_word = add(current_word, current_char)
            if current_char == token_type.bracket_open:
                state = ST_IN_BRACKET
                token_closed = False
            else:
                raise TokenParseError("{}: illegal character after full stop, expected <code style='color: #aa0000'>{}</code>".format(
                    S, token_type.bracket_open))
        
        # bracket state?
        elif state == ST_IN_BRACKET:
            current_word = add(current_word, current_char)
            if current_char == token_type.bracket_close:
                state = ST_NORMAL
                token_closed = True
            
        # transcript state?
        elif state == ST_IN_TRANSCRIPT:
            current_word = add(current_word, current_char)
            if current_char == token_type.transcript_close:
                state = ST_NORMAL
                token_closed = True
        
        # quote state?
        elif state == ST_IN_QUOTE:
            current_word = add(current_word, current_char)
            if current_char == token_type.quote_close:
                state = ST_NORMAL
                token_closed = True
                
        # quantification state?
        elif state == ST_IN_QUANTIFICATION:
            # only add valid quantification characters to the current word:
            if current_char in "0123456789, " + token_type.quantification_close:
                # ignore spaces:
                if current_char.strip():

                    if current_char == ",":
                        # raise an exception if a comma immediately follows 
                        # an opening bracket:
                        if current_word[-1] == token_type.quantification_open:
                            raise TokenParseError("{}: no lower range in the quantification".format(S))
                        # raise exception if a comma has already been added:
                        if comma_added:
                            raise TokenParseError("{}: only one comma is allowed within a quantification".format(S))
                        else:
                            comma_added = True
                    if current_char == token_type.quantification_close:
                        # raise an exception if the closing bracket follows 
                        # immediately after a comma or the opening bracket:
                        if current_word[-1] in [",", token_type.quantification_open]:
                            raise TokenParseError("{}: no upper range in quantification".format(S))
                        state = ST_NORMAL
                        token_closed = True

                    current_word = add(current_word, current_char)
            else:
                raise TokenParseError("{}: Illegal character <code style='color: #aa0000'>{}</code> within the quantification".format(S, current_char))
            
    if state != ST_NORMAL:
        if state == ST_POS_SEPARATOR:
            raise TokenParseError("{}: Missing a part-of-speech specification after '.'".format(S))
        if state == ST_IN_BRACKET:
            op = token_type.bracket_open
            cl = token_type.bracket_close
        elif state == ST_IN_TRANSCRIPT:
            op = token_type.transcript_open
            cl = token_type.transcript_close
        elif state == ST_IN_QUOTE:
            op = token_type.quote_open
            cl = token_type.quote_close
        elif state == ST_IN_QUANTIFICATION:
            op = token_type.quantification_open
            cl = token_type.quantification_close
        raise TokenParseError(msg_token_dangling_open.format(str=S, open=op, close=cl))
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
    
    tokens = parse_query_string(S, COCAToken)
    token_lists = []
    token_map = []
    current_pos = 1
    for i, current_token in enumerate([x for x in tokens if x]):
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

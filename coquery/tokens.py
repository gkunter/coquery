# -*- coding: utf-8 -*-

"""
tokens.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import itertools
import re

from .defines import (
    msg_token_dangling_open, msg_unexpected_quantifier_start,
    msg_missing_pos_spec)
from .errors import TokenParseError
from .unicode import utf8


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

    wildcard_characters = ["*", "?"]

    @classmethod
    def _check_pos_list(cls, l):
        return [False] * len(l)

    def __init__(self, S=None):
        self.word_specifiers = []
        self.class_specifiers = []
        self.lemma_specifiers = []
        self.transcript_specifiers = []
        self.gloss_specifiers = []
        self.negated = None
        self.wildcards = None
        self.lemmatize = None
        if S is not None:
            self.S = utf8(S).strip()
            self.parse()
        else:
            self.S = S

    def __eq__(self, S):
        return self.S == S

    def __ne__(self, S):
        return self.S != S

    def __repr__(self):
        return "{}(S='{}')".format(self.__class__.__name__, self.S)

    @classmethod
    def set_pos_check_function(cls, fnc):
        cls._check_pos_list = fnc

    @classmethod
    def has_wildcards(cls, s):
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

        if s in set(cls.wildcard_characters):
            return True
        for x in s:
            if skip_next:
                skip_next = False
            else:
                if x == "\\":
                    skip_next = True
                else:
                    if x in set(cls.wildcard_characters):
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
                if x in ["~", "#"]:
                    rep.append("\\")
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

    def parse(self):
        """
        Parse the token string.

        This function sets the values of a range of object attributes
        according to the query syntax realized by the QueryToken class.

        The attributes are evaluated by the ``get_query_string()`` method of
        the SQLResource class.

        Used object attributes
        ----------------------

        word_specifiers : list
            A list of strings that are matched against the word query item
            mapping of the current resource. If the list contains more than
            one element, the match will combine them using the OR relation.

        lemma_specifiers : list
            A list of strings that are matched against the lemma query item
            mapping of the current resource. If the list contains more than
            one element, the match will combine them using the OR relation.

        pos_specifiers : list
            A list of strings that are matched against the POS query item
            mapping of the current resource. If the list contains more than
            one element, the match will combine them using the OR relation.

        transcript_specifiers : list
            A list of strings that are matched against the transcript query
            item mapping of the current resource. If the list contains more
            than one element, the match will combine them using the OR
            relation.

        gloss_specifiers : list
            A list of strings that are matched against the gloss query item
            mapping of the current resource. If the list contains more than
            one element, the match will combine them using the OR relation.

        negated : bool
            True if the current query item is negated, and False otherwise.

        lemmatize : bool
            True if the current query item will be lemmatized, or False
            otherwise. 'Lemmatization' in this context means that the query
            will first find all word forms that match the query item, and will
            then look up all lemmas that these word forms are associated with.

        wildcards : bool
            True if the current query item contains wildcards, or False
            otherwise.

        Returns
        -------
        None
            The result of the parsing is stored in the object attributes
        """
        self.word_specifiers = [self.S]


class COCAToken(QueryToken):
    """
    A QueryToken subclass that uses old-style COCA syntax.
    """

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

    def parse(self):
        def split_spec(s, or_char=self.or_character):
            if not s:
                return []
            else:
                return [x.strip() for x in s.split(or_char) if x.strip()]

        self.word_specifiers = []
        self.class_specifiers = []
        self.lemma_specifiers = []
        self.transcript_specifiers = []
        self.gloss_specifiers = []

        if self.S is None:
            return

        word_specification = None
        lemma_specification = None
        class_specification = None
        transcript_specification = None
        gloss_specification = None

        pat = r"^\s*(?P<negated>~*)(?P<lemmatize>#*)(?P<item>.*)"
        match = re.search(pat, self.S)

        if match.groupdict()["negated"]:
            self.negated = bool(len(match.groupdict()["negated"]) % 2)
        else:
            self.negated = False

        self.lemmatize = bool(match.groupdict()["lemmatize"])
        work = (match.groupdict()["item"]
                     .replace(r"\#", "#")
                     .replace(r"\~", "~")
                     .replace("'", "''")
                     .replace(r"\{", "{"))

        if work == "//" or work == "[]":
            word_specification = work
        else:
            # try to match WORD|LEMMA|TRANS.[POS]:
            regex = ("(\[(?P<lemma>.*)\]|"
                     "/(?P<trans>.*)/|"
                     "(?P<word>.*)){1}(\.\[(?P<class>.*)\]){1}")
            match = re.match(regex, work)
            if not match:
                # try to match WORD|LEMMA|TRANS:
                regex = ("(\[(?P<lemma>.*)\]|"
                         "/(?P<trans>.*)/|"
                         "(?P<word>.*)){1}")
                match = re.match(regex, work)

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

        self.word_specifiers = split_spec(word_specification)
        self.transcript_specifiers = split_spec(transcript_specification)
        self.lemma_specifiers = split_spec(lemma_specification)
        self.class_specifiers = split_spec(class_specification)
        self.gloss_specifiers = split_spec(gloss_specification)

        if lemma_specification and not class_specification:
            # check if all elements pass as part-of-speech-tags:
            if all(COCAToken._check_pos_list(self.lemma_specifiers)):
                # if so, interpret elements as part-of-speech tags:
                self.class_specifiers = self.lemma_specifiers
                self.lemma_specifiers = []
        # special case: allow *.[POS]
        if all([x in set(self.wildcard_characters) for
                x in self.word_specifiers]) and self.class_specifiers:
            self.word_specifiers = []

        self.wildcards = any([self.has_wildcards(x)
                              for x in (self.word_specifiers +
                                        self.transcript_specifiers +
                                        self.lemma_specifiers +
                                        self.class_specifiers +
                                        self.gloss_specifiers)])


def parse_query_string(S, token_type):
    """
    Split a string into query items, making sure that bracketing and
    quotations are valid. Escaping is allowed.

    If the string is not valid, e.g. because a bracket is opened, but not
    closed, a TokenParseError is raised.
    """

    def add(S, ch):
        return "{}{}".format(S, ch)

    try:
        S = S.decode("utf-8")
    except UnicodeEncodeError:
        # already a unicode string
        pass
    except AttributeError:
        # using Python 3.x
        pass

    ST_NORMAL = "NORMAL"
    ST_IN_BRACKET = "BRACKET"
    ST_IN_TRANSCRIPT = "TRANS"
    ST_IN_QUOTE = "QUOTE"
    ST_IN_QUANTIFICATION = "QUANT"
    ST_POS_SEPARATOR = "POS"

    tokens = []
    current_word = ""

    escaping = False
    token_closed = False
    comma_added = False

    state = ST_NORMAL

    # main loop
    for char_pos, current_char in enumerate(S):
        # this string is used to mark the position of syntax errors
        pos_string = ("." * (char_pos) +
                      "↥" +
                      "." * (len(S) - char_pos - 1))

        if escaping:
            current_word = add(current_word, current_char)
            escaping = False
            continue
        if current_char == "\\":
            escaping = True
            continue

        # Normal word state:
        if state == ST_NORMAL:
            # the stripped word is the current word excluding negations and
            # lemmatization characters
            stripped_word = bool(
                current_word.strip("".join([token_type.negation_flag,
                                            token_type.lemmatize_flag])))

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
                    S = ("{}: expected a quantifier starting with <code "
                         "style='color: #aa0000'>{}</code> or a "
                         "part-of-speech specifier of the form <code "
                         "style='color: #aa0000'>{}{}POS{}</code>").format(
                            S,
                            token_type.quantification_open,
                            token_type.pos_separator,
                            token_type.bracket_open,
                            token_type.bracket_close)
                    raise TokenParseError(S)
                if current_char == token_type.pos_separator:
                    state = ST_POS_SEPARATOR
                    token_closed = False

            if current_char in set([token_type.negation_flag,
                                    token_type.lemmatize_flag]):
                current_word = add(current_word, current_char)
                continue

            # check for opening characters:
            if current_char in set([token_type.transcript_open,
                                    token_type.bracket_open,
                                    token_type.quote_open]):

                if not stripped_word:
                    # set new state:
                    if current_char == token_type.transcript_open:
                        state = ST_IN_TRANSCRIPT
                    elif current_char == token_type.bracket_open:
                        state = ST_IN_BRACKET
                    elif current_char == token_type.quote_open:
                        state = ST_IN_QUOTE

            if current_char == token_type.quantification_open:
                if stripped_word:
                    state = ST_IN_QUANTIFICATION
                    comma_added = False
                else:
                    if current_char == token_type.quantification_open:
                        raise TokenParseError(
                            msg_unexpected_quantifier_start.format(
                                S, pos_string,
                                token_type.quantification_open))

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
                S = ("{}: illegal character after full stop, expected <code "
                     "style='color: #aa0000'>{}</code>").format(
                    S, token_type.bracket_open)
                raise TokenParseError(S)

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
            if (current_char
                    in "0123456789, " + token_type.quantification_close):
                # ignore spaces:
                if current_char.strip():

                    if current_char == ",":
                        # raise an exception if a comma immediately follows
                        # an opening bracket:
                        if current_word[-1] == token_type.quantification_open:
                            S = "{}: {}".format(
                                S, "no lower range in the quantification")
                            raise TokenParseError(S)
                        # raise exception if a comma has already been added:
                        if comma_added:
                            S = "{}: {}".format(
                                S, ("only one comma is allowed within a "
                                    "quantification"))
                            raise TokenParseError(S)
                        else:
                            comma_added = True
                    if current_char == token_type.quantification_close:
                        # raise an exception if the closing bracket follows
                        # immediately after a comma or the opening bracket:
                        if (current_word[-1]
                                in [",", token_type.quantification_open]):
                            S = "{}: {}".format(
                                S, "no upper range in quantification")
                            raise TokenParseError(S)
                        state = ST_NORMAL
                        token_closed = True

                    current_word = add(current_word, current_char)
            else:
                S = ("{}: Illegal character <code style='color: #aa0000'>{}"
                     "</code> within the quantification").format(
                         S, current_char)
                raise TokenParseError(S)

    if state != ST_NORMAL:
        if state == ST_POS_SEPARATOR:
            raise TokenParseError(msg_missing_pos_spec.format(
                S, pos_string, token_type.pos_separator))
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
        S = msg_token_dangling_open.format(S, pos_string, cl, op)
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
    regexp = "(?P<token>.*)({\s*(?P<start>\d+)(,\s*(?P<end>\d+))?\s*})+"
    match = re.match(regexp, S)
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
        A list of query string tokens
    """

    tokens = parse_query_string(S, COCAToken)

    outer = []
    current_pos = 1
    # is there something that replaces these nested loops?
    for current_token in tokens:
        val, start, end = get_quantifiers(current_token)

        if val == "_NULL":
            val = None
        elif re.match("~?_PUNCT", val):
            neg = val.startswith("~")
            val = "|".join(list(".,;!-+") + ["\\?"])
            # FIXME: negation doesn't work
            if neg:
                val = "~{}".format(val)
        inner = []
        # For each tuple, create a list of constant length
        # Each element contains a different number of
        # repetitions of the value of the tuple, padded
        # by the value None if needed.
        for n in range(start, end + 1):
            x = ([(current_pos, val)] * n +
                 [(current_pos, None)] * (end - n))
            inner.append(x)
        outer.append(inner)
        current_pos += len(x)
    # Outer is now a list of lists.

    final = []
    # use itertools.product to combine the elements in the
    # list of lists:
    for combination in itertools.product(*outer):
        # flatten the elements in the current combination,
        # and append them to the final list:
        final.append([x for x
                      in itertools.chain.from_iterable(combination)])
    return final

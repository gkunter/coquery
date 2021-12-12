# -*- coding: utf-8 -*-
""" This model tests the Coquery token parsers."""

from __future__ import print_function


from coquery.tokens import (
    COCAToken,
    TokenParseError,
    get_quantifiers, preprocess_query, parse_query_string)
from test.testcase import CoqTestCase, run_tests


class TestTokensModuleMethods(CoqTestCase):
    def test_parse_query_string1(self):
        S1 = "this is a query"
        S2 = "this    is a query    "
        L = ["this", "is", "a", "query"]
        self.assertEqual(parse_query_string(S1, COCAToken), L)
        self.assertEqual(parse_query_string(S2, COCAToken), L)

    def test_parse_query_string2(self):
        S = "/this/ /is/ /a/ /query/"
        L = ["/this/", "/is/", "/a/", "/query/"]
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string3(self):
        S = "/this is a query/"
        L = ["/this is a query/"]
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string4(self):
        S = "[this] [is] [a] [query]"
        L = ["[this]", "[is]", "[a]", "[query]"]
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string5(self):
        S = "[this is a query]"
        L = ["[this is a query]"]
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string6(self):
        S = '"this" "is" "a" "query"'
        L = ['"this"', '"is"', '"a"', '"query"']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string7(self):
        S = '"this is a query"'
        L = ['"this is a query"']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string8(self):
        S = '/this|that/ is a query'
        L = ['/this|that/', 'is', 'a', 'query']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string9(self):
        S = '[this|that] is a query'
        L = ['[this|that]', 'is', 'a', 'query']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string10(self):
        S = '"this|that" is a query'
        L = ['"this|that"', 'is', 'a', 'query']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string11(self):
        S = '#this is a query'
        L = ['#this', 'is', 'a', 'query']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string12(self):
        S = '~this is a query'
        L = ['~this', 'is', 'a', 'query']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string_escape1(self):
        S = r'\"this is a query\"'
        L = ['\\"this', 'is', 'a', 'query\\"']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string_escape2(self):
        S1 = r'this \[is] a query'
        L1 = ['this', '\\[is]', 'a', 'query']
        S2 = r'this \[is a query'
        L2 = ['this', '\\[is', 'a', 'query']
        self.assertEqual(parse_query_string(S1, COCAToken), L1)
        self.assertEqual(parse_query_string(S2, COCAToken), L2)

    def test_parse_query_string_escape3(self):
        S1 = r'this \/is] a query'
        L1 = ['this', '\\/is]', 'a', 'query']
        S2 = r'this is a que\/ry'
        L2 = ['this', 'is', 'a', 'que\\/ry']
        self.assertEqual(parse_query_string(S1, COCAToken), L1)
        self.assertEqual(parse_query_string(S2, COCAToken), L2)

    def test_parse_query_string_escape4(self):
        S = r'this\ is a query'
        L = ['this\\ is', 'a', 'query']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string_illegal_escape1(self):
        S = "\\"
        with self.assertRaises(TokenParseError):
            parse_query_string(S, COCAToken)

    def test_unicode_1(self):
        B = b"string"
        U = u"string"
        self.assertEqual(
            type(parse_query_string(B, COCAToken)[0]), type(U))
        B = "string_äöü"
        U = u"string"
        self.assertEqual(
            type(parse_query_string(B, COCAToken)[0]), type(U))

    def test_unicode_2(self):
        S = 'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        L = [u'ȧƈƈḗƞŧḗḓ', u'ŧḗẋŧ', u'ƒǿř', u'ŧḗşŧīƞɠ']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_unicode_3(self):
        S = '[ȧƈƈḗƞŧḗḓ|ŧḗẋŧ] ƒǿř ŧḗşŧīƞɠ'
        L = [u'[ȧƈƈḗƞŧḗḓ|ŧḗẋŧ]', u'ƒǿř', u'ŧḗşŧīƞɠ']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_unicode_4(self):
        S = u'[ȧƈƈḗƞŧḗḓ|ŧḗẋŧ] ƒǿř ŧḗşŧīƞɠ'
        L = [u'[ȧƈƈḗƞŧḗḓ|ŧḗẋŧ]', u'ƒǿř', u'ŧḗşŧīƞɠ']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string_bad1(self):
        L = [
             '"this is a query',
             '/this is a query',
             '[this is a query',
             '/th/is is a query',
             '[th]is is a query',
             '"th"is is a query',
             '[[this]] is a query',
             '//this// is a query',
             '""this"" is a query',
             'this{1}} is a query',
             'this{{1} is a query',
             'this{} is a query',
             'this{,} is a query',
             'this{,1} is a query',
             'this{a,a} is a query',
             'this{1,,2} is a query',
            ]

        for x in L:
            with self.assertRaises(TokenParseError):
                parse_query_string(x, COCAToken)

    def test_word_internal_slashes(self):
        for S in ["th/is/", "t/hi/s", "th/is/"]:
            self.assertEqual(
                parse_query_string(S, COCAToken),
                [S])

    def test_word_internal_brackets(self):
        for S in ["th[is]", "t[hi]s", "th[is]"]:
            self.assertEqual(
                parse_query_string(S, COCAToken),
                [S])

    def test_word_internal_quotes(self):
        for S in ['th"is"', 't"hi"s', 'th"is"']:
            self.assertEqual(
                parse_query_string(S, COCAToken),
                [S])

    def test_parse_query_string_quantifiers(self):
        S = '[this]{1,3} *.[v*]{2} a query'
        L = ['[this]{1,3}', '*.[v*]{2}', 'a', 'query']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string_transcript_pos(self):
        S = '/b*n*/.[n*]'
        L = ['/b*n*/.[n*]']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string_lemma_pos(self):
        S = '[b*n*].[n*]'
        L = ['[b*n*].[n*]']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string_gloss_pos(self):
        S = '"b*n*".[n*]'
        L = ['"b*n*".[n*]']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_query_string_word_pos(self):
        S = 'b*n*.[n*]'
        L = ['b*n*.[n*]']
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_parse_lemmatized_transcript(self):
        S = "#/'bɐlɐl/"
        L = [u"#/'bɐlɐl/"]
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_potentially_malformed_query(self):
        S = "ABC/"
        L = ["ABC/"]
        self.assertEqual(parse_query_string(S, COCAToken), L)

    def test_preprocess_string_literal(self):
        S = r"\? \* \_ \%"
        L = [[(1, "\\?"), (2, "\\*"), (3, "\\_"), (4, "\\%")]]
        try:
            self.assertItemsEqual(preprocess_query(S, literal=True), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S, literal=True), L)

    def test_preprocess_string_not_literal(self):
        S = r"\? \* \_ \% ? * _ %"
        L = [[(1, "\\?"), (2, "\\*"), (3, "\\_"), (4, "\\%"),
              (5, "?"), (6, "*"), (7, "_"), (8, "%")]]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)


class TestQueryTokenCOCA(CoqTestCase):
    token_type = COCAToken

    def setUp(self):
        self.token_type.set_pos_check_function(self.pos_check_function)

    @classmethod
    def pos_check_function(cls, l):
        return [x in ["V", "N"] for x in l]

    def test_unicode_1(self):
        token = self.token_type(b"word")
        self.assertEqual(type(token.S), type(u"word"))
        token = self.token_type(u"word")
        self.assertEqual(type(token.S), type(u"word"))
        token = self.token_type(u"'ȧƈƈḗƞŧḗḓ ŧḗẋŧ'")
        self.assertEqual(type(token.S), type(u"word"))

    def test_word_only(self):
        token = self.token_type("word")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word"])

    def test_several_words(self):
        token = self.token_type("word1|word2")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])

    def test_lemma_only(self):
        token = self.token_type("[lemma]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, ["lemma"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_several_lemmas(self):
        token = self.token_type("[lemma1|lemma2]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_words_and_pos(self):
        token = self.token_type("word1|word2.[N]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])

    def test_words_and_several_pos(self):
        token = self.token_type("word1|word2.[N|V]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])

    def test_lemmas_and_pos(self):
        token = self.token_type("[lemma1|lemma2].[N]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_ambiguous_lemma_pos1(self):
        token = self.token_type("[N]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_ambiguous_lemma_pos2(self):
        token = self.token_type("[N|V]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_ambiguous_lemma_pos3(self):
        token = self.token_type("[N|Lemma]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, ["N", "Lemma"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_lemmas_and_several_pos(self):
        token = self.token_type("[lemma1|lemma2].[N|V]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_only_pos(self):
        token = self.token_type("[N|V]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_strange_pos_spec(self):
        token = self.token_type("abc..[n*]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["n*"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc."])

    def test_quotation_mark1(self):
        token = self.token_type('"')
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ['"'])

    def test_quotation_mark2(self):
        token = self.token_type('"abc"')
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, ["abc"])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_quotation_mark3(self):
        token = self.token_type('"abc|def"')
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, ["abc", "def"])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_quotation_mark4(self):
        token = self.token_type('["abc|def"]')
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, ['"abc', 'def"'])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_quotation_mark5(self):
        token = self.token_type('"abc')
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ['"abc'])

    def test_quotation_mark6(self):
        token = self.token_type('abc"')
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ['abc"'])

    def test_quotation_mark7(self):
        token = self.token_type('"[abc|def]"')
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, ['[abc', 'def]'])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_wildcard_pos(self):
        token = self.token_type("*.[N|V]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts(self):
        token = self.token_type("/trans1|trans2/")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1", "trans2"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcript_and_pos(self):
        token = self.token_type("/trans/.[N]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans"])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcript_spaced(self):
        token = self.token_type("/a b c d e/")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["a b c d e"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcript_and_pos2(self):
        token = self.token_type("/b*n*/.[N]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["b*n*"])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_and_several_pos(self):
        token = self.token_type("/trans1|trans2/.[N|V]")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1", "trans2"])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_multiple_slashes_1(self):
        token = self.token_type("/trans1/|/trans2/")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1/", "/trans2"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_multiple_slashes_2(self):
        token = self.token_type("/S K*/")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["S K*"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_single_slash1(self):
        token = self.token_type("/trans")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["/trans"])

    def test_transcripts_single_slash2(self):
        token = self.token_type("trans/")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["trans/"])

    def test_transcripts_single_slash3(self):
        token = self.token_type("/")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["/"])

    def test_wildcards(self):
        token = self.token_type("*")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["*"])

    def test_wildcards2(self):
        token = self.token_type(r"\*")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [r"\*"])

    def test_wildcards3(self):
        token = self.token_type("%")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [r"%"])

    def test_wildcards4(self):
        token = self.token_type("?")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["?"])

    def test_wildcards5(self):
        token = self.token_type(r"\?")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [r"\?"])

    def test_wildcards6(self):
        token = self.token_type("_")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["_"])

    def test_wildcards7(self):
        token = self.token_type("*e??r")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["*e??r"])

    def test_has_wildcards1(self):
        self.assertFalse(self.token_type.has_wildcards("abc"))

    def test_has_wildcards2(self):
        self.assertTrue(self.token_type.has_wildcards("*"))
        self.assertTrue(self.token_type.has_wildcards("*abc"))
        self.assertTrue(self.token_type.has_wildcards("abc*abc"))
        self.assertTrue(self.token_type.has_wildcards("abc*"))

    def test_has_wildcards3(self):
        self.assertFalse(self.token_type.has_wildcards("%"))
        self.assertFalse(self.token_type.has_wildcards("%abc"))
        self.assertFalse(self.token_type.has_wildcards("abc%abc"))
        self.assertFalse(self.token_type.has_wildcards("abc%"))

    def test_has_wildcards4(self):
        self.assertFalse(self.token_type.has_wildcards(r"\*"))
        self.assertFalse(self.token_type.has_wildcards(r"\*abc"))
        self.assertFalse(self.token_type.has_wildcards(r"abc\*abc"))
        self.assertFalse(self.token_type.has_wildcards(r"abc\*"))

    def test_has_wildcards5(self):
        self.assertTrue(self.token_type.has_wildcards("?"))
        self.assertTrue(self.token_type.has_wildcards("?abc"))
        self.assertTrue(self.token_type.has_wildcards("abc?abc"))
        self.assertTrue(self.token_type.has_wildcards("abc?"))

    def test_has_wildcards6(self):
        self.assertFalse(self.token_type.has_wildcards("_"))
        self.assertFalse(self.token_type.has_wildcards("_abc"))
        self.assertFalse(self.token_type.has_wildcards("abc_abc"))
        self.assertFalse(self.token_type.has_wildcards("abc_"))

    def test_has_wildcards7(self):
        self.assertFalse(self.token_type.has_wildcards(r"\?"))
        self.assertFalse(self.token_type.has_wildcards(r"\?abc"))
        self.assertFalse(self.token_type.has_wildcards(r"abc\?abc"))
        self.assertFalse(self.token_type.has_wildcards(r"abc\?"))

    def test_replace_wildcards(self):
        self.assertEqual(self.token_type.replace_wildcards("*ab"), "%ab")
        self.assertEqual(self.token_type.replace_wildcards("a*b"), "a%b")
        self.assertEqual(self.token_type.replace_wildcards("ab*"), "ab%")

        self.assertEqual(self.token_type.replace_wildcards(r"\*ab"), r"*ab")
        self.assertEqual(self.token_type.replace_wildcards(r"a\*b"), r"a*b")
        self.assertEqual(self.token_type.replace_wildcards(r"ab\*"), r"ab*")

        self.assertEqual(self.token_type.replace_wildcards("%ab"), r"\%ab")
        self.assertEqual(self.token_type.replace_wildcards("a%b"), r"a\%b")
        self.assertEqual(self.token_type.replace_wildcards("ab%"), r"ab\%")

        self.assertEqual(self.token_type.replace_wildcards("?ab"), "_ab")
        self.assertEqual(self.token_type.replace_wildcards("a?b"), "a_b")
        self.assertEqual(self.token_type.replace_wildcards("ab?"), "ab_")

        self.assertEqual(self.token_type.replace_wildcards(r"\?ab"), r"?ab")
        self.assertEqual(self.token_type.replace_wildcards(r"a\?b"), r"a?b")
        self.assertEqual(self.token_type.replace_wildcards(r"ab\?"), r"ab?")

        self.assertEqual(self.token_type.replace_wildcards("_ab"), r"\_ab")
        self.assertEqual(self.token_type.replace_wildcards("a_b"), r"a\_b")
        self.assertEqual(self.token_type.replace_wildcards("ab_"), r"ab\_")

    def test_escaped_braces_1(self):
        token = self.token_type(r"\{b_trans}")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["{b_trans}"])

    def test_escaped_braces_2(self):
        token = self.token_type(r"\{E_TRANS}")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["{E_TRANS}"])

    def test_escaped_braces_3(self):
        token = self.token_type(r"\{E?TRANS}")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["{E?TRANS}"])

    def test_negation0(self):
        token = self.token_type("abc")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_negation1(self):
        token = self.token_type("~abc")
        self.assertTrue(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_negation2(self):
        token = self.token_type("~~abc")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_negation3(self):
        token = self.token_type("~~~abc")
        self.assertTrue(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_lemmatize1(self):
        token = self.token_type("#abc")
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_lemmatize2(self):
        token = self.token_type("##abc")
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_lemmatize3(self):
        token = self.token_type("a#bc")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["a#bc"])

    def test_lemmatize4(self):
        token = self.token_type("abc#")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc#"])

    def test_lemmatize5(self):
        token = self.token_type("#abc|cde")
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc", "cde"])

    def test_lemmatize6(self):
        token = self.token_type("#[abc]")
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, ["abc"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_lemmatize7(self):
        token = self.token_type('#"abc"')
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, ["abc"])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_lemmatize8(self):
        token = self.token_type("#/abc/")
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["abc"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_lemmatize8a(self):
        token = self.token_type("#/'bɪrɛr/")
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [u"''bɪrɛr"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_lemmatize_pos(self):
        S = "#abc.[N*]"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertTrue(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N*"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_treat_apostrophes_1(self):
        S = "'ll"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["''ll"])

    def test_treat_apostrophes_2(self):
        S = "x'"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["x''"])

    def test_treat_apostrophes_3(self):
        S = "x'x"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["x''x"])

    def test_treat_apostrophes_4(self):
        S = "''ll"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["''''ll"])

    def test_treat_apostrophes_5(self):
        S = "x''"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["x''''"])

    def test_treat_apostrophes_6(self):
        S = "x'''x"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["x''''''x"])

    def test_escape_negation1(self):
        S = "\\~abc"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["~abc"])

    def test_escape_negation2(self):
        token = self.token_type(r"~\~abc")
        self.assertTrue(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["~abc"])

    def test_escape_negation3(self):
        token = self.token_type(r"\~~abc")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["~~abc"])

    def test_escape_hash1(self):
        token = self.token_type(r"\#abc")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["#abc"])

    def test_escape_hash2(self):
        token = self.token_type(r"#\#abc")
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["#abc"])

    def test_escape_hash3(self):
        S = r"\##abc"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["##abc"])

    def test_unescaped_hash(self):
        S = "#"
        with self.assertRaises(TokenParseError):
            _ = self.token_type(S)

    def test_single_backslash(self):
        S = "\\"
        with self.assertRaises(TokenParseError):
            _ = self.token_type(S)

    def test_escaped_backslash(self):
        S = r"\\"
        token = self.token_type(S)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["\\"])

    def test_mix_flag1(self):
        token = self.token_type("~#abc")
        self.assertTrue(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_mix_flag2(self):
        token = self.token_type("#~abc")
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["~abc"])


class TestIDQuery(CoqTestCase):
    token_type = COCAToken

    def test_id_query_1(self):
        token = self.token_type("=123")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, ["123"])
        self.assertEqual(token.word_specifiers, [])

    def test_id_query_2(self):
        token = self.token_type("=123|124")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, ["123", "124"])
        self.assertEqual(token.word_specifiers, [])

    def test_escape_1(self):
        token = self.token_type(r"\=123")
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.wildcards)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.id_specifiers, [])
        self.assertEqual(token.word_specifiers, ["=123"])


class TestQuantification(CoqTestCase):
    def test_no_quantifiers(self):
        self.assertEqual(get_quantifiers("xxx"), ("xxx", 1, 1))

    def test_quantifiers(self):
        self.assertEqual(get_quantifiers("xxx{0,1}"), ("xxx", 0, 1))

    def test_single_zero_quantifier(self):
        self.assertEqual(get_quantifiers("xxx{0}"), ("xxx", 0, 0))

    def test_single_nonzero_quantifier(self):
        self.assertEqual(get_quantifiers("xxx{1}"), ("xxx", 1, 1))

    def test_broken_quantifiers(self):
        self.assertEqual(get_quantifiers("xxx0,1}"), ("xxx0,1}", 1, 1))

        # Actually, none of the remaining quantifiers will occur if the query
        # string is first processed by parse_query_string(), which will raise
        # an exception for them:
        self.assertEqual(get_quantifiers("xxx{0,1"), ("xxx{0,1", 1, 1))
        self.assertEqual(get_quantifiers("xxx{a,1}"), ("xxx{a,1}", 1, 1))
        self.assertEqual(get_quantifiers("xxx{0,b}"), ("xxx{0,b}", 1, 1))
        self.assertEqual(get_quantifiers("xxx{a,b}"), ("xxx{a,b}", 1, 1))
        self.assertEqual(get_quantifiers("xxx{a}"), ("xxx{a}", 1, 1))

    def test_preprocess_string0(self):
        S = "a{0,1} fish"
        L = [
            [(1, 'a'),  (2, 'fish')],
            [(1, None), (2, 'fish')]]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)

    def test_preprocess_string1a(self):
        S = "one more{0,1} thing"
        L = [
            [(1, 'one'), (2, None),   (3, 'thing')],
            [(1, 'one'), (2, 'more'), (3, 'thing')]]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)

    def test_preprocess_string1b(self):
        S = "one little{0,2} thing"
        L = [
            [(1, 'one'), (2, None),     (2, None),     (4, 'thing')],
            [(1, 'one'), (2, 'little'), (2, None),     (4, 'thing')],
            [(1, 'one'), (2, 'little'), (2, 'little'), (4, 'thing')]]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)

    def test_preprocess_string1(self):
        S = "[dt]{0,1} more [j*] [n*]"

        L = [
            [(1, '[dt]'), (2, 'more'), (3, '[j*]'), (4, '[n*]')],
            [(1, None),   (2, 'more'), (3, '[j*]'), (4, '[n*]')],
            ]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)

    def test_preprocess_string2(self):
        S = "[dt]{0,1} [jjr] [n*]"

        L = [
            [(1, '[dt]'), (2, '[jjr]'), (3, '[n*]')],
            [(1, None),   (2, '[jjr]'), (3, '[n*]')],
            ]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)

    def test_preprocess_string3(self):
        S = "[dt]{0,1} more [j*]{1,2} [n*]"
        L = [
            [(1, '[dt]'), (2, 'more'), (3, '[j*]'), (3, None),   (5, '[n*]')],
            [(1, '[dt]'), (2, 'more'), (3, '[j*]'), (3, '[j*]'), (5, '[n*]')],
            [(1, None),   (2, 'more'), (3, '[j*]'), (3, None),   (5, '[n*]')],
            [(1, None),   (2, 'more'), (3, '[j*]'), (3, '[j*]'), (5, '[n*]')],
            ]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)

    def test_preprocess_string4(self):
        S = "more [j*]{0,4} [n*]{1,2}"
        L = [
                [(1, 'more'),
                 (2, None),   (2, None),   (2, None),   (2, None),
                 (6, '[n*]'), (6, None)],
                [(1, 'more'),
                 (2, '[j*]'), (2, None),   (2, None),   (2, None),
                 (6, '[n*]'), (6, None)],
                [(1, 'more'),
                 (2, '[j*]'), (2, '[j*]'), (2, None),   (2, None),
                 (6, '[n*]'), (6, None)],
                [(1, 'more'),
                 (2, '[j*]'), (2, '[j*]'), (2, '[j*]'), (2, None),
                 (6, '[n*]'), (6, None)],
                [(1, 'more'),
                 (2, '[j*]'), (2, '[j*]'), (2, '[j*]'), (2, '[j*]'),
                 (6, '[n*]'), (6, None)],
                [(1, 'more'),
                 (2, None),   (2, None),   (2, None),   (2, None),
                 (6, '[n*]'), (6, '[n*]')],
                [(1, 'more'),
                 (2, '[j*]'), (2, None),   (2, None),   (2, None),
                 (6, '[n*]'), (6, '[n*]')],
                [(1, 'more'),
                 (2, '[j*]'), (2, '[j*]'), (2, None),   (2, None),
                 (6, '[n*]'), (6, '[n*]')],
                [(1, 'more'),
                 (2, '[j*]'), (2, '[j*]'), (2, '[j*]'), (2, None),
                 (6, '[n*]'), (6, '[n*]')],
                [(1, 'more'),
                 (2, '[j*]'), (2, '[j*]'), (2, '[j*]'), (2, '[j*]'),
                 (6, '[n*]'), (6, '[n*]')],
            ]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)

    def test_preprocess_string5(self):
        S = "prove that"
        L = [
            [(1, "prove"), (2, "that")]
            ]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)

    def test_preprocess_string_NULL_1(self):
        S = "prove _NULL that"
        L = [[(1, "prove"), (2, None), (3, "that")]]
        try:
            self.assertItemsEqual(preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(preprocess_query(S), L)


# An CQL query syntax is not implemented yet, but might be in the future.
#class TestQueryTokenCQL(unittest.TestCase):
    #token_type = CQLToken

    #def runTest(self):
        #super(TestQueryToken, self).runTest()

    #def test_word_only(self):
        #token = self.token_type('[word="teapot"]')
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, [])
        #self.assertEqual(token.transcript_specifiers, [])
        #self.assertEqual(token.class_specifiers, [])
        #self.assertEqual(token.word_specifiers, ["teapot"])

    #def test_word_wildcard(self):
        #token = self.token_type('[word="confus.*"]')
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, [])
        #self.assertEqual(token.transcript_specifiers, [])
        #self.assertEqual(token.class_specifiers, [])
        #self.assertEqual(token.word_specifiers, ["confus*"])

    #def test_several_words(self):
        #for S in [
            #'[word="great" | word = "small"]',
            #'[word="great"|"small"]',
            #'[word="great|small"]']:
            #token = self.token_type(S)
            #token.parse()
            #self.assertEqual(token.lemma_specifiers, [])
            #self.assertEqual(token.transcript_specifiers, [])
            #self.assertEqual(token.class_specifiers, [])
            #self.assertEqual(token.word_specifiers, ["great", "small"])

    #def test_lemma_only(self):
        #token = self.token_type('[lemma = "have"]')
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, ["have"])
        #self.assertEqual(token.transcript_specifiers, [])
        #self.assertEqual(token.class_specifiers, [])
        #self.assertEqual(token.word_specifiers, [])

    #def test_several_lemmas(self):
        #for S in [
            #'[lemma="great" | lemma = "small"]',
            #'[lemma="great"|"small"]',
            #'[lemma="great|small"]']:
            #token = self.token_type(S)
            #token.parse()
            #self.assertEqual(token.lemma_specifiers, ["great", "small"])
            #self.assertEqual(token.transcript_specifiers, [])
            #self.assertEqual(token.class_specifiers, [])
            #self.assertEqual(token.word_specifiers, [])

    #def test_words_and_pos(self):
        #for S in [
            #'[word = "dog|cat" & tag="N.*"]',
            #'[word = "dog" & tag="N.*"] | [word="cat" & tag="N.*"]']:
            #token = self.token_type(S)
            #token.parse()
            #self.assertEqual(token.lemma_specifiers, [])
            #self.assertEqual(token.transcript_specifiers, [])
            #self.assertEqual(token.class_specifiers, ["N*"])
            #self.assertEqual(token.word_specifiers, ["dog", "cat"])

    #def test_words_and_several_pos(self):
        #for S in [
            #'[word = "dog|cat" & tag="N.*|V.*"]',
            #'[word = "dog" & tag="N.*|V.*"] | [word="cat" & tag="N.*|V.*"]']:
            #token = self.token_type(S)
            #token.parse()
            #self.assertEqual(token.lemma_specifiers, [])
            #self.assertEqual(token.transcript_specifiers, [])
            #self.assertEqual(token.class_specifiers, ["N*", "V*"])
            #self.assertEqual(token.word_specifiers, ["dog", "cat"])


provided_tests = [TestTokensModuleMethods,
                  TestQueryTokenCOCA,
                  TestIDQuery,
                  TestQuantification]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

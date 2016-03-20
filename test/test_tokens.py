# -*- coding: utf-8 -*-
""" This model tests the Coquery token parsers."""

from __future__ import print_function

import unittest
import os.path
import sys

sys.path.append(os.path.normpath(os.path.join(sys.path[0], "../coquery")))

# Mock module requirements:
class mock_module(object):
    pass

sys.modules["sqlalchemy"] = mock_module
sys.modules["options"] = mock_module
from corpus import LexiconClass, BaseResource

import tokens

class TestLexicon(LexiconClass):
    def is_part_of_speech(self, pos):
        return pos in ["N", "V"]

class TestModuleMethods(unittest.TestCase):
    def test_parse_query_string1(self):
        S1 = "this is a query"
        S2 = "this    is a query    "
        L = ["this", "is", "a", "query"]
        self.assertEqual(tokens.parse_query_string(S1, tokens.COCAToken), L)
        self.assertEqual(tokens.parse_query_string(S2, tokens.COCAToken), L)

    def test_parse_query_string2(self):
        S = "/this/ /is/ /a/ /query/"
        L = ["/this/", "/is/", "/a/", "/query/"]
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string3(self):
        S = "/this is a query/"
        L = ["/this is a query/"]
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string4(self):
        S = "[this] [is] [a] [query]"
        L = ["[this]", "[is]", "[a]", "[query]"]
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string5(self):
        S = "[this is a query]"
        L = ["[this is a query]"]
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string6(self):
        S = '"this" "is" "a" "query"'
        L = ['"this"', '"is"', '"a"', '"query"']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string7(self):
        S = '"this is a query"'
        L = ['"this is a query"']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string8(self):
        S = '/this|that/ is a query'
        L = ['/this|that/', 'is', 'a', 'query']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
        
    def test_parse_query_string9(self):
        S = '[this|that] is a query'
        L = ['[this|that]', 'is', 'a', 'query']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
        
    def test_parse_query_string10(self):
        S = '"this|that" is a query'
        L = ['"this|that"', 'is', 'a', 'query']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string11(self):
        S = '#this is a query'
        L = ['#this', 'is', 'a', 'query']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
        
    def test_parse_query_string12(self):
        S = '~this is a query'
        L = ['~this', 'is', 'a', 'query']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
        
    def test_parse_query_string_escape1(self):
        S = '\\"this is a query\\"'
        L = ['"this', 'is', 'a', 'query"']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string_escape2(self):
        S1 = 'this \\[is] a query'
        L1 = ['this', '[is]', 'a', 'query']
        S2 = 'this \\[is a query'
        L2 = ['this', '[is', 'a', 'query']
        self.assertEqual(tokens.parse_query_string(S1, tokens.COCAToken), L1)
        self.assertEqual(tokens.parse_query_string(S2, tokens.COCAToken), L2)

    def test_parse_query_string_escape2(self):
        S1 = 'this \\/is] a query'
        L1 = ['this', '/is]', 'a', 'query']
        S2 = 'this is a que\\/ry'
        L2 = ['this', 'is', 'a', 'que/ry']
        self.assertEqual(tokens.parse_query_string(S1, tokens.COCAToken), L1)
        self.assertEqual(tokens.parse_query_string(S2, tokens.COCAToken), L2)
        
    def test_parse_query_string_escape3(self):
        S = 'this\\ is a query'
        L = ['this is', 'a', 'query']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
        
    def test_unicode_1(self):
        B = b"string"
        U = u"string"
        self.assertEqual(type(tokens.parse_query_string(B, tokens.COCAToken)[0]), 
                         type(U))
        B = "string_äöü"
        U = u"string"
        self.assertEqual(type(tokens.parse_query_string(B, tokens.COCAToken)[0]), 
                         type(U))

    def test_unicode_2(self):
        S = 'ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ'
        L = [u'ȧƈƈḗƞŧḗḓ', u'ŧḗẋŧ', u'ƒǿř', u'ŧḗşŧīƞɠ']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
        
    def test_unicode_3(self):
        S = '[ȧƈƈḗƞŧḗḓ|ŧḗẋŧ] ƒǿř ŧḗşŧīƞɠ'
        L = [u'[ȧƈƈḗƞŧḗḓ|ŧḗẋŧ]', u'ƒǿř', u'ŧḗşŧīƞɠ']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_unicode_3(self):
        S = u'[ȧƈƈḗƞŧḗḓ|ŧḗẋŧ] ƒǿř ŧḗşŧīƞɠ'
        L = [u'[ȧƈƈḗƞŧḗḓ|ŧḗẋŧ]', u'ƒǿř', u'ŧḗşŧīƞɠ']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string_bad1(self):
        L = ['"this is a query',
             '/this is a query',
             '[this is a query',
             'th/is/ is a query',
             '/th/is is a query',
             't/hi/s is a query',
             'th"is" is a query',
             '"th"is is a query',
             't"hi"s is a query',
             'th[is] is a query',
             '[th]is is a query',
             't[hi]s is a query',
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
            try:
                self.assertRaises(tokens.TokenParseError, tokens.parse_query_string, x, tokens.COCAToken)
            except AssertionError as e:
                print(x)
                raise e

    def test_parse_query_string_quantifiers(self):
        S = '[this]{1,3} *.[v*]{2} a query'
        L = ['[this]{1,3}', '*.[v*]{2}', 'a', 'query']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string_transcript_pos(self):
        S = '/b*n*/.[n*]'
        L = ['/b*n*/.[n*]']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
        
    def test_parse_query_string_lemma_pos(self):
        S = '[b*n*].[n*]'
        L = ['[b*n*].[n*]']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
    
    def test_parse_query_string_gloss_pos(self):
        S = '"b*n*".[n*]'
        L = ['"b*n*".[n*]']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

    def test_parse_query_string_word_pos(self):
        S = 'b*n*.[n*]'
        L = ['b*n*.[n*]']
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)
        
    def test_parse_lemmatized_transcript(self):
        S = "#/'bɐlɐl/"
        L = [u"#/'bɐlɐl/"]
        result = tokens.parse_query_string(S, tokens.COCAToken)
        self.assertEqual(tokens.parse_query_string(S, tokens.COCAToken), L)

class TestQueryTokenCOCA(unittest.TestCase):
    token_type = tokens.COCAToken
    
    def runTest(self):
        super(TestQueryToken, self).runTest()
    
    def setUp(self):
        self.lexicon = TestLexicon()
    
    def test_unicode_1(self):
        token = self.token_type(b"word", self.lexicon)
        self.assertEqual(type(token.S), type(u"word"))
        token = self.token_type(u"word", self.lexicon)
        self.assertEqual(type(token.S), type(u"word"))
        token = self.token_type(u"'ȧƈƈḗƞŧḗḓ ŧḗẋŧ'", self.lexicon)
        self.assertEqual(type(token.S), type(u"word"))

    def test_word_only(self):
        token = self.token_type("word", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word"])

    def test_several_words(self):
        token = self.token_type("word1|word2", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])

    def test_lemma_only(self):
        token = self.token_type("[lemma]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, ["lemma"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_several_lemmas(self):
        token = self.token_type("[lemma1|lemma2]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_words_and_pos(self):
        token = self.token_type("word1|word2.[N]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])
        
    def test_words_and_several_pos(self):
        token = self.token_type("word1|word2.[N|V]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])

    def test_lemmas_and_pos(self):
        token = self.token_type("[lemma1|lemma2].[N]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])
        
    def test_ambiguous_lemma_pos1(self):
        token = self.token_type("[N]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])
        
    def test_ambiguous_lemma_pos2(self):
        token = self.token_type("[N|V]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])
        
    def test_ambiguous_lemma_pos3(self):
        token = self.token_type("[N|Lemma]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, ["N", "Lemma"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])


    def test_lemmas_and_several_pos(self):
        token = self.token_type("[lemma1|lemma2].[N|V]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])
        
    def test_only_pos(self):
        token = self.token_type("[N|V]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])        

    def test_strange_pos_spec(self):
        token = self.token_type("abc..[n*]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["n%"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc."])
        
    def test_quotation_mark1(self):
        token = self.token_type('"', self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ['"'])        
        
    def test_quotation_mark2(self):
        token = self.token_type('"abc"', self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, ["abc"])
        self.assertEqual(token.word_specifiers, [])
        
    def test_quotation_mark3(self):
        token = self.token_type('"abc|def"', self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, ["abc", "def"])
        self.assertEqual(token.word_specifiers, [])

    def test_quotation_mark4(self):
        token = self.token_type('["abc|def"]', self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, ['"abc', 'def"'])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_quotation_mark5(self):
        token = self.token_type('"abc', self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ['"abc'])
        
    def test_quotation_mark6(self):
        token = self.token_type('abc"', self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ['abc"'])

    def test_quotation_mark7(self):
        token = self.token_type('"[abc|def]"', self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, ['[abc', 'def]'])
        self.assertEqual(token.word_specifiers, [])
        
    def test_wildcard_pos(self):
        token = self.token_type("*.[N|V]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])        
        
    def test_transcripts(self):
        token = self.token_type("/trans1|trans2/", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1", "trans2"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcript_and_pos(self):
        token = self.token_type("/trans/.[N]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans"])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])
        
    def test_transcript_and_pos2(self):
        token = self.token_type("/b*n*/.[N]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["b%n%"])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_and_several_pos(self):
        token = self.token_type("/trans1|trans2/.[N|V]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1", "trans2"])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_multiple_slashes(self):
        token = self.token_type("/trans1/|/trans2/", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1/", "/trans2"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_multiple_slashes(self):
        token = self.token_type("/S K*/", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["S K%"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

        
    def test_transcripts_single_slash1(self):
        token = self.token_type("/trans", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["/trans"])
        
    def test_transcripts_single_slash2(self):
        token = self.token_type("trans/", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["trans/"])
        
    def test_transcripts_single_slash3(self):
        token = self.token_type("/", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["/"])
        
    def test_wildcards(self):
        token = self.token_type("*", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["%"])
        
    def test_wildcards2(self):
        token = self.token_type("\\*", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["*"])

    def test_wildcards3(self):
        token = self.token_type("%", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["\\%"])
        
    def test_wildcards4(self):
        token = self.token_type("?", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["_"])
        
    def test_wildcards5(self):
        token = self.token_type("\\?", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["?"])
        
    def test_wildcards6(self):
        token = self.token_type("_", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["\\_"])
        
    def test_wildcards7(self):
        token = self.token_type("*e??r", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["%e__r"])
        
    def test_has_wildcards1(self):
        token = self.token_type("", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.has_wildcards("abc"))
        
    def test_has_wildcards2(self):
        token = self.token_type("", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.has_wildcards("*"))
        self.assertFalse(token.has_wildcards("*abc"))
        self.assertFalse(token.has_wildcards("abc*abc"))
        self.assertFalse(token.has_wildcards("abc*"))

    def test_has_wildcards3(self):
        token = self.token_type("", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.has_wildcards("%"))
        self.assertTrue(token.has_wildcards("%abc"))
        self.assertTrue(token.has_wildcards("abc%abc"))
        self.assertTrue(token.has_wildcards("abc%"))

    def test_has_wildcards4(self):
        token = self.token_type("", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.has_wildcards("\\%"))
        self.assertFalse(token.has_wildcards("\\%abc"))
        self.assertFalse(token.has_wildcards("abc\\%abc"))
        self.assertFalse(token.has_wildcards("abc\\%"))
        
    def test_has_wildcards5(self):
        token = self.token_type("", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.has_wildcards("?"))
        self.assertFalse(token.has_wildcards("?abc"))
        self.assertFalse(token.has_wildcards("abc?abc"))
        self.assertFalse(token.has_wildcards("abc?"))

    def test_has_wildcards6(self):
        token = self.token_type("", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertTrue(token.has_wildcards("_"))
        self.assertTrue(token.has_wildcards("_abc"))
        self.assertTrue(token.has_wildcards("abc_abc"))
        self.assertTrue(token.has_wildcards("abc_"))
        
    def test_has_wildcards7(self):
        token = self.token_type("", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertFalse(token.has_wildcards("\\_"))
        self.assertFalse(token.has_wildcards("\\_abc"))
        self.assertFalse(token.has_wildcards("abc\\_abc"))
        self.assertFalse(token.has_wildcards("abc\\_"))
        
    def test_replace_wildcards(self):
        self.assertEqual(self.token_type.replace_wildcards("*ab"), "%ab")
        self.assertEqual(self.token_type.replace_wildcards("a*b"), "a%b")
        self.assertEqual(self.token_type.replace_wildcards("ab*"), "ab%")

        self.assertEqual(self.token_type.replace_wildcards("\\*ab"), "*ab")
        self.assertEqual(self.token_type.replace_wildcards("a\\*b"), "a*b")
        self.assertEqual(self.token_type.replace_wildcards("ab\\*"), "ab*")

        self.assertEqual(self.token_type.replace_wildcards("%ab"), "\\%ab")
        self.assertEqual(self.token_type.replace_wildcards("a%b"), "a\\%b")
        self.assertEqual(self.token_type.replace_wildcards("ab%"), "ab\\%")

        self.assertEqual(self.token_type.replace_wildcards("?ab"), "_ab")
        self.assertEqual(self.token_type.replace_wildcards("a?b"), "a_b")
        self.assertEqual(self.token_type.replace_wildcards("ab?"), "ab_")

        self.assertEqual(self.token_type.replace_wildcards("\\?ab"), "?ab")
        self.assertEqual(self.token_type.replace_wildcards("a\\?b"), "a?b")
        self.assertEqual(self.token_type.replace_wildcards("ab\\?"), "ab?")

        self.assertEqual(self.token_type.replace_wildcards("_ab"), "\\_ab")
        self.assertEqual(self.token_type.replace_wildcards("a_b"), "a\\_b")
        self.assertEqual(self.token_type.replace_wildcards("ab_"), "ab\\_")


    def test_underscore1(self):
        token = self.token_type("\\{b_trans}", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["{b\\_trans}"])
        
    def test_negation0(self):
        token = self.token_type("abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_negation1(self):
        token = self.token_type("~abc", self.lexicon)
        self.assertTrue(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_negation2(self):
        token = self.token_type("~~abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_negation3(self):
        token = self.token_type("~~~abc", self.lexicon)
        self.assertTrue(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])
        
    def test_lemmatize1(self):
        token = self.token_type("#abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_lemmatize2(self):
        token = self.token_type("##abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])

    def test_lemmatize3(self):
        token = self.token_type("a#bc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["a#bc"])

    def test_lemmatize4(self):
        token = self.token_type("abc#", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc#"])

    def test_lemmatize5(self):
        token = self.token_type("#abc|cde", self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc", "cde"])

    def test_lemmatize6(self):
        token = self.token_type("#[abc]", self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, ["abc"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_lemmatize7(self):
        token = self.token_type('#"abc"', self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, ["abc"])
        self.assertEqual(token.word_specifiers, [])

    def test_lemmatize8(self):
        token = self.token_type("#/abc/", self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["abc"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_lemmatize8a(self):
        token = self.token_type("#/'bɪrɛr/", self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [u"'bɪrɛr"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_escape_negation1(self):
        token = self.token_type("\\~abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["~abc"])
        
    def test_escape_negation2(self):
        token = self.token_type("~\\~abc", self.lexicon)
        self.assertTrue(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["~abc"])
        
    def test_escape_negation3(self):
        token = self.token_type("\\~~abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["~~abc"])

    def test_escape_hash1(self):
        token = self.token_type("\\#abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["#abc"])
        
    def test_escape_hash2(self):
        token = self.token_type("#\\#abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["#abc"])
        
    def test_escape_hash3(self):
        token = self.token_type("\\##abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertFalse(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["##abc"])
        
    def test_mix_flag1(self):
        token = self.token_type("~#abc", self.lexicon)
        self.assertTrue(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["abc"])
        
    def test_mix_flag2(self):
        token = self.token_type("#~abc", self.lexicon)
        self.assertFalse(token.negated)
        self.assertTrue(token.lemmatize)
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.gloss_specifiers, [])
        self.assertEqual(token.word_specifiers, ["~abc"])

class TestQuantification(unittest.TestCase):
    def test_no_quantifiers(self):
        self.assertEqual(tokens.get_quantifiers("xxx"), ("xxx", 1, 1))
        
    def test_quantifiers(self):
        self.assertEqual(tokens.get_quantifiers("xxx{0,1}"), ("xxx", 0, 1))
        
    def test_single_zero_quantifier(self):
        self.assertEqual(tokens.get_quantifiers("xxx{0}"), ("xxx", 0, 0))
        
    def test_single_nonzero_quantifier(self):
        self.assertEqual(tokens.get_quantifiers("xxx{1}"), ("xxx", 1, 1))
        
    def test_broken_quantifiers(self):
        self.assertEqual(tokens.get_quantifiers("xxx0,1}"), ("xxx0,1}", 1, 1))

        # Actually, none of the remaining quantifiers will occur if the query 
        # string is first processed by parse_query_string(), which will raise 
        # an exception for them:
        self.assertEqual(tokens.get_quantifiers("xxx{0,1"), ("xxx{0,1", 1, 1))
        self.assertEqual(tokens.get_quantifiers("xxx{a,1}"), ("xxx{a,1}", 1, 1))
        self.assertEqual(tokens.get_quantifiers("xxx{0,b}"), ("xxx{0,b}", 1, 1))
        self.assertEqual(tokens.get_quantifiers("xxx{a,b}"), ("xxx{a,b}", 1, 1))
        self.assertEqual(tokens.get_quantifiers("xxx{a}"), ("xxx{a}", 1, 1))
    
    def test_preprocess_string1(self):
        S = "[dt]{0,1} more [j*] [n*]"
        
        L = [
            [(1, '[dt]'), (2, 'more'), (3, '[j*]'), (4, '[n*]')],
            [             (2, 'more'), (3, '[j*]'), (4, '[n*]')], 
            ]
        try:
            self.assertItemsEqual(tokens.preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(tokens.preprocess_query(S), L)

    def test_preprocess_string2(self):
        S = "[dt]{0,1} [jjr] [n*]"
        
        L = [
            [(1, '[dt]'), (2, '[jjr]'), (3, '[n*]')],
            [             (2, '[jjr]'), (3, '[n*]')], 
            ]
        try:
            self.assertItemsEqual(tokens.preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(tokens.preprocess_query(S), L)

    def test_preprocess_string3(self):
        S = "[dt]{0,1} more [j*]{1,2} [n*]"
        L = [
            [(1, '[dt]'), (2, 'more'), (3, '[j*]'),              (5, '[n*]')], 
            [(1, '[dt]'), (2, 'more'), (3, '[j*]'), (3, '[j*]'), (5, '[n*]')],
            [             (2, 'more'), (3, '[j*]'),              (5, '[n*]')], 
            [             (2, 'more'), (3, '[j*]'), (3, '[j*]'), (5, '[n*]')], 
            ]
        try:
            self.assertItemsEqual(tokens.preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(tokens.preprocess_query(S), L)

    def test_preprocess_string4(self):
        S = "more [j*]{0,4} [n*]{1,2}"
        L = [
            [(1, 'more'),                                                     (6, '[n*]')], 
            [(1, 'more'), (2, '[j*]'),                                        (6, '[n*]')], 
            [(1, 'more'), (2, '[j*]'), (2, '[j*]'),                           (6, '[n*]')], 
            [(1, 'more'), (2, '[j*]'), (2, '[j*]'), (2, '[j*]'),              (6, '[n*]')], 
            [(1, 'more'), (2, '[j*]'), (2, '[j*]'), (2, '[j*]'), (2, '[j*]'), (6, '[n*]')], 
            [(1, 'more'),                                                     (6, '[n*]'), (6, '[n*]')],
            [(1, 'more'), (2, '[j*]'),                                        (6, '[n*]'), (6, '[n*]')], 
            [(1, 'more'), (2, '[j*]'), (2, '[j*]'),                           (6, '[n*]'), (6, '[n*]')], 
            [(1, 'more'), (2, '[j*]'), (2, '[j*]'), (2, '[j*]'),              (6, '[n*]'), (6, '[n*]')], 
            [(1, 'more'), (2, '[j*]'), (2, '[j*]'), (2, '[j*]'), (2, '[j*]'), (6, '[n*]'), (6, '[n*]')],
            ]
        try:
            self.assertItemsEqual(tokens.preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(tokens.preprocess_query(S), L)
            
    def test_preprocess_string5(self):
        S = "prove that"
        L = [
            [(1, "prove"), (2, "that")]
            ]
        try:
            self.assertItemsEqual(tokens.preprocess_query(S), L)
        except AttributeError:
            self.assertCountEqual(tokens.preprocess_query(S), L)

# An CQL query syntax is not implemented yet, but might be in the future.
#class TestQueryTokenCQL(unittest.TestCase):
    #token_type = tokens.CQLToken
    
    #def runTest(self):
        #super(TestQueryToken, self).runTest()
    
    #def setUp(self):
        #import corpus
        #self.lexicon = corpus.TestLexicon(corpus.BaseResource())
    
    #def test_word_only(self):
        #token = self.token_type('[word="teapot"', self.lexicon)
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, [])
        #self.assertEqual(token.transcript_specifiers, [])
        #self.assertEqual(token.class_specifiers, [])
        #self.assertEqual(token.word_specifiers, ["teapot"])
        
    #def test_word_wildcard(self):
        #token = self.token_type('[word="confus.*"', self.lexicon)
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
            #token = self.token_type(S, self.lexicon)
            #token.parse()
            #self.assertEqual(token.lemma_specifiers, [])
            #self.assertEqual(token.transcript_specifiers, [])
            #self.assertEqual(token.class_specifiers, [])
            #self.assertEqual(token.word_specifiers, ["great", "small"])

    #def test_lemma_only(self):
        #token = self.token_type('[lemma = "have"]', self.lexicon)
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
            #token = self.token_type(S, self.lexicon)
            #token.parse()
            #self.assertEqual(token.lemma_specifiers, ["great", "small"])
            #self.assertEqual(token.transcript_specifiers, [])
            #self.assertEqual(token.class_specifiers, [])
            #self.assertEqual(token.word_specifiers, [])

    #def test_words_and_pos(self):
        #for S in [
            #'[word = "dog|cat" & tag="N.*"]',
            #'[word = "dog" & tag="N.*"] | [word="cat" & tag="N.*"]']:
            #token = self.token_type(S, self.lexicon)
            #token.parse()
            #self.assertEqual(token.lemma_specifiers, [])
            #self.assertEqual(token.transcript_specifiers, [])
            #self.assertEqual(token.class_specifiers, ["N*"])
            #self.assertEqual(token.word_specifiers, ["dog", "cat"])
        
    #def test_words_and_several_pos(self):
        #for S in [
            #'[word = "dog|cat" & tag="N.*|V.*"]',
            #'[word = "dog" & tag="N.*|V.*"] | [word="cat" & tag="N.*|V.*"]']:
            #token = self.token_type(S, self.lexicon)
            #token.parse()
            #self.assertEqual(token.lemma_specifiers, [])
            #self.assertEqual(token.transcript_specifiers, [])
            #self.assertEqual(token.class_specifiers, ["N*", "V*"])
            #self.assertEqual(token.word_specifiers, ["dog", "cat"])

    #def test_lemmas_and_pos(self):
        #token = self.token_type("[lemma1|lemma2].[N]", self.lexicon)
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        #self.assertEqual(token.transcript_specifiers, [])
        #self.assertEqual(token.class_specifiers, ["N"])
        #self.assertEqual(token.word_specifiers, [])
        
    #def test_lemmas_and_several_pos(self):
        #token = self.token_type("[lemma1|lemma2].[N|V]", self.lexicon)
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        #self.assertEqual(token.transcript_specifiers, [])
        #self.assertEqual(token.class_specifiers, ["N", "V"])
        #self.assertEqual(token.word_specifiers, [])
        
    #def test_only_pos(self):
        #token = self.token_type("[N|V]", self.lexicon)
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, [])
        #self.assertEqual(token.transcript_specifiers, [])
        #self.assertEqual(token.class_specifiers, ["N", "V"])
        #self.assertEqual(token.word_specifiers, [])        
        
    #def test_transcripts(self):
        #token = self.token_type("/trans1|trans2/", self.lexicon)
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, [])
        #self.assertEqual(token.transcript_specifiers, ["trans1", "trans2"])
        #self.assertEqual(token.class_specifiers, [])
        #self.assertEqual(token.word_specifiers, [])

    #def test_transcripts_and_several_pos(self):
        #token = self.token_type("/trans1|trans2/.[N|V]", self.lexicon)
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, [])
        #self.assertEqual(token.transcript_specifiers, ["trans1", "trans2"])
        #self.assertEqual(token.class_specifiers, ["N", "V"])
        #self.assertEqual(token.word_specifiers, [])

    #def test_transcripts_multiple_slashes(self):
        #token = self.token_type("/trans1/|/trans2/", self.lexicon)
        #token.parse()
        #self.assertEqual(token.lemma_specifiers, [])
        #self.assertEqual(token.transcript_specifiers, ["trans1/", "/trans2"])
        #self.assertEqual(token.class_specifiers, [])
        #self.assertEqual(token.word_specifiers, [])



if __name__ == '__main__':
    import timeit
    
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestModuleMethods),
        unittest.TestLoader().loadTestsFromTestCase(TestQueryTokenCOCA),
        unittest.TestLoader().loadTestsFromTestCase(TestQuantification),
        ])
    
    print()
    print(" ----- START ----- ")
    print()
    unittest.TextTestRunner().run(suite)

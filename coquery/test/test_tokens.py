""" This model tests the Coquery token parsers."""

from __future__ import print_function

import unittest
import os.path
import sys

sys.path.append(os.path.normpath(os.path.join(sys.path[0], "..")))
import tokens
from corpus import BaseLexicon, BaseResource

class TestLexicon(BaseLexicon):
    def is_part_of_speech(self, pos):
        return pos in ["N", "V"]

class TestQueryTokenCOCA(unittest.TestCase):
    token_type = tokens.COCAToken
    
    def runTest(self):
        super(TestQueryToken, self).runTest()
    
    def setUp(self):
        self.lexicon = TestLexicon()
    
    def test_word_only(self):
        token = self.token_type("word", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word"])

    def test_several_words(self):
        token = self.token_type("word1|word2", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])

    def test_lemma_only(self):
        token = self.token_type("[lemma]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, ["lemma"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_several_lemmas(self):
        token = self.token_type("[lemma1|lemma2]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_words_and_pos(self):
        token = self.token_type("word1|word2.[N]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])
        
    def test_words_and_several_pos(self):
        token = self.token_type("word1|word2.[N|V]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.word_specifiers, ["word1", "word2"])

    def test_lemmas_and_pos(self):
        token = self.token_type("[lemma1|lemma2].[N]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N"])
        self.assertEqual(token.word_specifiers, [])
        
    def test_lemmas_and_several_pos(self):
        token = self.token_type("[lemma1|lemma2].[N|V]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, ["lemma1", "lemma2"])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.word_specifiers, [])
        
    def test_only_pos(self):
        token = self.token_type("[N|V]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.word_specifiers, [])        
        
    def test_wildcard_pos(self):
        token = self.token_type("*.[N|V]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.word_specifiers, [])        
        
    def test_transcripts(self):
        token = self.token_type("/trans1|trans2/", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1", "trans2"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_and_several_pos(self):
        token = self.token_type("/trans1|trans2/.[N|V]", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1", "trans2"])
        self.assertEqual(token.class_specifiers, ["N", "V"])
        self.assertEqual(token.word_specifiers, [])

    def test_transcripts_multiple_slashes(self):
        token = self.token_type("/trans1/|/trans2/", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, ["trans1/", "/trans2"])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, [])
        
    def test_wildcards(self):
        token = self.token_type("*", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["%"])
        
    def test_wildcards2(self):
        token = self.token_type("\\*", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["*"])

    def test_wildcards3(self):
        token = self.token_type("%", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["\\%"])
        
    def test_wildcards4(self):
        token = self.token_type("?", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["_"])
        
    def test_wildcards5(self):
        token = self.token_type("\\?", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["?"])
        
    def test_wildcards6(self):
        token = self.token_type("_", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["\\_"])
        
    def test_wildcards7(self):
        token = self.token_type("*e??r", self.lexicon)
        token.parse()
        self.assertEqual(token.lemma_specifiers, [])
        self.assertEqual(token.transcript_specifiers, [])
        self.assertEqual(token.class_specifiers, [])
        self.assertEqual(token.word_specifiers, ["%e__r"])
        
    def test_has_wildcards1(self):
        token = self.token_type("", self.lexicon)
        token.parse()
        self.assertFalse(token.has_wildcards("abc"))
        
    def test_has_wildcards2(self):
        token = self.token_type("", self.lexicon)
        token.parse()
        self.assertFalse(token.has_wildcards("*"))
        self.assertFalse(token.has_wildcards("*abc"))
        self.assertFalse(token.has_wildcards("abc*abc"))
        self.assertFalse(token.has_wildcards("abc*"))

    def test_has_wildcards3(self):
        token = self.token_type("", self.lexicon)
        token.parse()
        self.assertTrue(token.has_wildcards("%"))
        self.assertTrue(token.has_wildcards("%abc"))
        self.assertTrue(token.has_wildcards("abc%abc"))
        self.assertTrue(token.has_wildcards("abc%"))

    def test_has_wildcards4(self):
        token = self.token_type("", self.lexicon)
        token.parse()
        self.assertFalse(token.has_wildcards("\\%"))
        self.assertFalse(token.has_wildcards("\\%abc"))
        self.assertFalse(token.has_wildcards("abc\\%abc"))
        self.assertFalse(token.has_wildcards("abc\\%"))
        
    def test_has_wildcards5(self):
        token = self.token_type("", self.lexicon)
        token.parse()
        self.assertFalse(token.has_wildcards("?"))
        self.assertFalse(token.has_wildcards("?abc"))
        self.assertFalse(token.has_wildcards("abc?abc"))
        self.assertFalse(token.has_wildcards("abc?"))

    def test_has_wildcards6(self):
        token = self.token_type("", self.lexicon)
        token.parse()
        self.assertTrue(token.has_wildcards("_"))
        self.assertTrue(token.has_wildcards("_abc"))
        self.assertTrue(token.has_wildcards("abc_abc"))
        self.assertTrue(token.has_wildcards("abc_"))
        
    def test_has_wildcards7(self):
        token = self.token_type("", self.lexicon)
        token.parse()
        self.assertFalse(token.has_wildcards("\\_"))
        self.assertFalse(token.has_wildcards("\\_abc"))
        self.assertFalse(token.has_wildcards("abc\\_abc"))
        self.assertFalse(token.has_wildcards("abc\\_"))
        

class TestQuantification(unittest.TestCase):
    def test_no_quantifiers(self):
        self.assertEqual(tokens.get_quantifiers("xxx"), ("xxx", 1, 1))
        
    def test_quantifiers(self):
        self.assertEqual(tokens.get_quantifiers("xxx{0,1}"), ("xxx", 0, 1))
        
    def test_single_zero_quantifier(self):
        self.assertEqual(tokens.get_quantifiers("xxx{0}"), ("xxx", 0, 0))
        
    def test_single_nonzero_quantifier(self):
        self.assertEqual(tokens.get_quantifiers("xxx{1}"), ("xxx", 1, 1))
        
    def test_corrupt_quantifiers(self):
        self.assertEqual(tokens.get_quantifiers("xxx{0,1"), ("xxx{0,1", 1, 1))
        self.assertEqual(tokens.get_quantifiers("xxx0,1}"), ("xxx0,1}", 1, 1))
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
        unittest.TestLoader().loadTestsFromTestCase(TestQueryTokenCOCA),
        unittest.TestLoader().loadTestsFromTestCase(TestQuantification)])
    
    print()
    print(" ----- START ----- ")
    print()
    unittest.TextTestRunner().run(suite)

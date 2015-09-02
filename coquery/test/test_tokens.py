""" This model tests the Coquery token parsers."""

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
        self.lexicon = TestLexicon(BaseResource())
    
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
        self.assertEqual(token.word_specifiers, ["*"])
        

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
        unittest.TestLoader().loadTestsFromTestCase(TestQueryTokenCOCA)])
    unittest.TextTestRunner().run(suite)

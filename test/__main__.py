import unittest

from test.test_bibliography import (
    TestPerson, TestPersonList, TestEditorList, TestReference, TestArticle,
    TestBook, TestInCollection)
from test.test_celex import TestCELEX
from test.test_corpora import TestCorpus
from test.test_filters import TestFilterString, TestApply
from test.test_functions import (
    TestFrequencyFunctions, TestStringFunctions, TestMathFunctions,
    TestLogicalFunctions)
from test.test_options import TestQueryStringParse
from test.test_sessions import TestSessionInputFile
from test.test_textgrids import TestTextGridModuleMethods
from test.test_tokens import (
    TestTokensModuleMethods, TestQueryTokenCOCA, TestQuantification)
from test.test_unicode import TestUnicodeModuleMethods

def main():

    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in [TestPerson, TestPersonList, TestEditorList, TestReference,
                   TestArticle, TestBook, TestInCollection,
                   TestCELEX,
                   TestCorpus,
                   TestFilterString, TestApply,
                   TestQueryStringParse,
                   TestTextGridModuleMethods,
                   TestTokensModuleMethods, TestQueryTokenCOCA,
                   TestQuantification,
                   TestUnicodeModuleMethods]])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

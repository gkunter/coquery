from __future__ import print_function

import unittest
import sys

def main():
    test_list = []
    args = sys.argv[1:]
    if args:
        print("Running tests for these modules:")
        print("\t", ", ".join(sorted(args)))
    else:
        print("Running complete tests")

    if not args or "bibliography" in args:
        from test.test_bibliography import (
            TestPerson, TestPersonList, TestEditorList, TestReference,
            TestArticle, TestBook, TestInCollection)
        test_list += [TestPerson, TestPersonList, TestEditorList,
                      TestReference, TestArticle, TestBook,
                      TestInCollection]

    if not args or  "celex" in args:
        from test.test_celex import TestCELEX
        test_list += [TestCELEX]

    if not args or  "corpus" in args:
        from test.test_corpora import TestCorpus, TestCorpusWithExternal
        test_list += [TestCorpus, TestCorpusWithExternal]

    if not args or "corpusbuilder" in args:
        from test.test_corpusbuilder import (
            TestXMLCorpusBuilder,TestTEICorpusBuilder)
        test_list += [TestXMLCorpusBuilder, TestTEICorpusBuilder]

    if not args or  "filters" in args:
        from test.test_filters import TestFilterString, TestApply
        test_list += [TestFilterString, TestApply]

    if not args or  "functions" in args:
        from test.test_functions import (
            TestFrequencyFunctions, TestStringFunctions, TestMathFunctions,
            TestLogicalFunctions)
        test_list += [TestFrequencyFunctions, TestStringFunctions,
                      TestMathFunctions, TestLogicalFunctions]

    if not args or  "managers" in args:
        from test.test_managers import TestManager
        test_list += [TestManager]

    if not args or  "options" in args:
        from test.test_options import TestQueryStringParse
        test_list += [TestQueryStringParse]

    if not args or  "sessions" in args:
        from test.test_sessions import TestSessionInputFile
        test_list += [TestSessionInputFile]

    if not args or "textgrids" in args:
        from test.test_textgrids import TestTextGridModuleMethods
        test_list += [TestTextGridModuleMethods]

    if not args or  "tokens" in args:
        from test.test_tokens import (
            TestTokensModuleMethods, TestQueryTokenCOCA, TestQuantification)
        test_list += [TestTokensModuleMethods, TestQueryTokenCOCA,
                      TestQuantification]

    if not args or  "unicode" in args:
        from test.test_unicode import TestUnicodeModuleMethods
        test_list += [TestUnicodeModuleMethods]

    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in test_list])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

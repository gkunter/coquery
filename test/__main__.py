from __future__ import print_function

import unittest
import sys
from pprint import pprint

def main():
    test_list = []
    args = sys.argv[1:]
    if args:
        print("Running tests for these modules:")
        print()
        pprint(sorted(args), indent=4)
        print()
    else:
        print("Running complete tests")

    if not args or "bibliography" in args:
        from test.test_bibliography import (
            TestPerson, TestPersonList, TestEditorList, TestReference,
            TestArticle, TestBook, TestInCollection)
        test_list += [TestPerson, TestPersonList, TestEditorList,
                      TestReference, TestArticle, TestBook,
                      TestInCollection]

    if not args or "celex" in args:
        from test.test_celex import TestCELEX
        test_list += [TestCELEX]

    if not args or "corpus" in args:
        from test.test_corpora import (
            TestCorpus, TestSuperFlat,
            TestCorpusWithExternal, TestNGramCorpus)
        test_list += [TestCorpus, TestSuperFlat,
                      TestCorpusWithExternal, TestNGramCorpus]

    if not args or "corpusbuilder" in args:
        from test.test_corpusbuilder import provided_tests
        test_list += provided_tests

    if not args or "filters" in args:
        from test.test_filters import provided_tests
        test_list += provided_tests

    if not args or "functionlist" in args:
        from test.test_functionlist import TestFunctionList
        test_list += [TestFunctionList]

    if not args or "functions" in args:
        from test import test_functions
        test_list += test_functions.provided_tests

    if not args or "general" in args:
        from test import test_general
        test_list += test_general.provided_tests

    if not args or "managers" in args:
        from test.test_managers import TestManager
        test_list += [TestManager]

    if not args or "options" in args:
        from test.test_options import TestQueryStringParse
        test_list += [TestQueryStringParse]

    if not args or "sessions" in args:
        from test.test_sessions import (
            TestSessionInputFile, TestSessionMethods)
        test_list += [TestSessionInputFile, TestSessionMethods]

    if not args or "switchboard" in args:
        from test.test_switchboard import TestSwitchboard
        test_list += [TestSwitchboard]

    if not args or "tables" in args:
        from test.test_tables import provided_tests
        test_list += provided_tests

    if not args or "textgrids" in args:
        from test.test_textgrids import TestTextGridModuleMethods
        test_list += [TestTextGridModuleMethods]

    if not args or "tokens" in args:
        from test.test_tokens import (
            TestTokensModuleMethods, TestQueryTokenCOCA, TestQuantification)
        test_list += [TestTokensModuleMethods, TestQueryTokenCOCA,
                      TestQuantification]

    if not args or "unicode" in args:
        from test.test_unicode import TestUnicodeModuleMethods
        test_list += [TestUnicodeModuleMethods]

    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in test_list])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

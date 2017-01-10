import test.test_bibliography
import test.test_celex
import test.test_corpora
import test.test_filters
import test.test_functions
import test.test_options
import test.test_textgrids
import test.test_tokens
import test.test_unicode

def main():
    test.test_bibliography.main()
    test.test_celex.main()
    test.test_corpora.main()
    test.test_filters.main()
    test.test_functions.main()
    test.test_options.main()
    test.test_textgrids.main()
    test.test_tokens.main()
    test.test_unicode.main()

if __name__ == '__main__':
    main()

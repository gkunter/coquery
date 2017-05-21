# -*- coding: utf-8 -*-
"""
defines.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

DEFAULT_MISSING_VALUE = "<NA>"

# The following labels are used to refer to the different types of query
# tokens, e.g. in corpusbuilder.py when mapping the different query item
# types to different fields in the data base:
QUERY_ITEM_WORD = "query_item_word"
QUERY_ITEM_LEMMA = "query_item_lemma"
QUERY_ITEM_TRANSCRIPT = "query_item_transcript"
QUERY_ITEM_POS = "query_item_pos"
QUERY_ITEM_GLOSS = "query_item_gloss"

QUERY_MODE_TOKENS = "Do not transform"
QUERY_MODE_TYPES = "Only distinct rows"
QUERY_MODE_FREQUENCIES = "Frequency list"
QUERY_MODE_STATISTICS = "Statistics"
QUERY_MODE_COLLOCATIONS = "Collocation list"
QUERY_MODE_CONTINGENCY = "Contingency table"
QUERY_MODE_CONTRASTS = "G-test matrix"

# this dictionary is used to provide keywords for the command line interface:
QUERY_MODES = {
    "TOKEN": QUERY_MODE_TOKENS,
    "TYPES": QUERY_MODE_TYPES,
    "FREQ": QUERY_MODE_FREQUENCIES,
    "STATS": QUERY_MODE_STATISTICS,
    "COLL": QUERY_MODE_COLLOCATIONS,
    "GTEST": QUERY_MODE_CONTRASTS,
    "CONT": QUERY_MODE_CONTINGENCY
    }

# this list is used to populate and query the summary mode combo box in the
# user # interface
SUMMARY_MODES = [
    QUERY_MODE_TOKENS,
    QUERY_MODE_TYPES,
    QUERY_MODE_FREQUENCIES,
    QUERY_MODE_CONTINGENCY,
    QUERY_MODE_CONTRASTS,
    QUERY_MODE_COLLOCATIONS,
    ]

FILTER_STAGE_BEFORE_TRANSFORM = 0
FILTER_STAGE_FINAL = 1

_OPERATORS = ["OP_EQ", "OP_LE", "OP_LT", "OP_GE", "OP_GT", "OP_NE", "OP_IN",
              "OP_NIN", "OP_RANGE", "OP_MATCH", "OP_NMATCH"]
(OP_EQ,
OP_LE,
OP_LT,
OP_GE,
OP_GT,
OP_NE,
OP_IN,
OP_NIN,
OP_RANGE,
OP_MATCH,
OP_NMATCH) = _OPERATORS

OPERATOR_STRINGS = {
    OP_EQ: "==",
    OP_LE: "<=",
    OP_LT: "<",
    OP_GE: ">=",
    OP_GT: ">",
    OP_NE: "!=",
    OP_IN: "in",
    OP_NIN: "not in",
    OP_RANGE: "is within the range of",
    OP_MATCH: "contains",
    OP_NMATCH: "does not contain",
    }

OPERATOR_LABELS = {
    OP_EQ: "is",
    OP_LE: "is less than or equals",
    OP_LT: "is less than",
    OP_GE: "is greater than or equals",
    OP_GT: "is greater than",
    OP_NE: "does not equal",
    OP_IN: "is one of",
    OP_NIN: "is not one of",
    OP_RANGE: "is within the range of",
    OP_MATCH: "contains",
    OP_NMATCH: "does not contain",
    }


SORT_NONE = "sort_none"
SORT_INC = "sort_inc"
SORT_DEC = "sort_dec"
SORT_REV_INC = "sort_rev_inc"
SORT_REV_DEC = "sort_rev_dec"

CONTEXT_NONE = "None"
CONTEXT_KWIC = "KWIC"
CONTEXT_STRING = "String"
CONTEXT_COLUMNS = "Columns"
CONTEXT_SENTENCE = "Sentence"

VIEW_MODE_TABLES = 0
VIEW_MODE_GROUPED = 1

AUTO_VISIBILITY = 0
AUTO_FUNCTION = 1
AUTO_SUBSTITUTE = 2
AUTO_STOPWORDS = 3
AUTO_FILTER = 4
AUTO_TRANSFORM = 5
AUTO_ORDER = 6
AUTO_APPLY_DEFAULT = [AUTO_VISIBILITY]

(TOOLBOX_ORDER, TOOLBOX_CONTEXT, TOOLBOX_STOPWORDS, TOOLBOX_GROUPING,
TOOLBOX_AGGREGATE, TOOLBOX_SUMMARY) = range(6)

# These labels are used in the corpus manager:
INSTALLER_DEFAULT = "Default corpus installers"
INSTALLER_CUSTOM = "Downloaded corpus installers"
INSTALLER_ADHOC = "User corpora"

COLUMN_NAMES = {
    # Labels that are used in the Collocations aggregation:
    "coq_context_left": "Left context",
    "coq_context_right": "Right context",
    "coq_context_string": "Context",
    "coq_collocate_label": "Collocate",
    "coq_collocate_frequency": "Collocate frequency",
    "coq_collocate_frequency_left": "Left context frequency",
    "coq_collocate_frequency_right": "Right context frequency",
    "coq_collocate_node": "Node",
    "coq_mutual_information": "Mutual information",
    "coq_conditional_probability": "Pc(total)",
    "coq_conditional_probability_left": "Pc(left)",
    "coq_conditional_probability_right": "Pc(right)",

    # Labels that are used in the Coquery special table:
    "coquery_query_token": "Query token",
    "coquery_expanded_query_string": "Matched query string",
    "coquery_query_string": "Query string",

    # function labels
    "statistics_proportion": "Proportion",
    "statistics_row_number": "Row number",
    "statistics_percent": "Percentage",
    "statistics_entropy": "Entropy",
    "statistics_frequency": "Frequency",
    "statistics_corpus_size": "Corpus size: Total",
    "statistics_subcorpus_size": "Corpus size: Subcorpus",
    "statistics_subcorpus_range_min": "Subcorpus: Lower boundary",
    "statistics_subcorpus_range_max": "Subcorpus: Upper boundary",
    "statistics_frequency_pmw": "Frequency pmw",
    "statistics_frequency_ptw": "Frequency ptw",
    "statistics_frequency_normalized": "Frequency (normalized)",
    "statistics_tokens": "Number of matches",
    "statistics_types": "Number of unique matches",
    "statistics_ttr": "Type-token ratio",
    #"statistics_passing_rows": "Passing rows",
    #"statistics_filtered_rows": "Filtered rows",
    "statistics_column_total": "ALL",

    # Labels for reference corpus:
    "reference_frequency": "Reference Frequency",
    "reference_corpus_size": "Reference Corpus size",
    "reference_diff_keyness": "Keyness: %DIFF",
    "reference_ll_keyness": "Keyness: LL",
    "reference_frequency_pmw": "Reference Frequency pmw",
    "reference_frequency_ptw": "Reference Frequency ptw",

    # Labels that are used when displaying the corpus statistics:
    "coq_statistics_table": "Table",
    "coq_statistics_column": "Column",
    "coq_statistics_entries": "Entries",
    "coq_statistics_uniques": "Uniques",
    "coq_statistics_uniquenessratio": "Uniqueness ratio",
    "coq_statistics_averagefrequency": "Average frequency",
        }

ROW_NAMES = {
    "row_total": "ALL",
    }

FUNCTION_DESC = {
    "statistics_passing_rows": "Count the number of rows that passed the filter",
    "statistics_filtered_rows": "Count the number of rows that were removed by a filter",
    "statistics_row_number": "Row number of the match",
    "statistics_corpus_size": "Size of the corpus in words",
    "statistics_subcorpus_size": "Size of the subcorpus in words",
    "statistics_entropy": "Calculate Shannon's entropy",
    "statistics_frequency": "Count the frequency of each match",
    "statistics_frequency_normalized": "Count the frequency of each match, normalized by corpus size in words",
    "statistics_frequency_ptw": "Calculate the average frequency of each match per thousand words",
    "statistics_frequency_pmw": "Calculate the average frequency of each match per million words",

    "statistics_proportion": "Calculate the proportion for each match",
    "statistics_percent": "Calculate the percentage for each match",
    "statistics_tokens": "Count the number of tokens",
    "statistics_types": "Count the number of types",
    "statistics_ttr": "Calculate the type-token ratio",
    "reference_frequency": "Count the frequeny of the match in the reference corpus",
    "reference_frequency_ptw": "Calculate the frequency per million words in the reference corpus",
    "reference_frequency_pmw": "Calculate the frequency per thousand words in the reference corpus",
    "reference_ll_keyness": "Calculate the log-likelihood keyness relative to the reference corpus",
    "reference_diff_keyness": "Calculate the %DIFF keyness relative to the reference corpus",

    "LENGTH": "Count the number of characters",
    "CONCAT": "Concatenate the columns, separated by <i>Argument</i>",
    "COUNT": "Count the number of occurrences of <i>Argument</i> (regexp)",
    "MATCH": "Test whether the columns match <i>Argument</i> (regexp)",
    "EXTRACT": "Extract from the columns the string that matches <i>Argument</i> (regexp)",

    "EQUAL": "'yes' if values are equal, or 'false' otherwise",
    "GREATER": "'yes' if values are greater, or 'false' otherwise",
    "GREATEREQUAL": "'yes' if values are greater or equal, or 'false' otherwise",
    "LESS": "'yes' if values are less, or 'false' otherwise",
    "LESSEQUAL": "'yes' if values are less or equal, or 'false' otherwise",
    "NOTEQUAL": "'yes' if values are not equal, or 'false' otherwise",

    "AND": "Combine the selected columns by logical AND",
    "OR": "Combine the selected columns by logical OR",
    "XOR": "Combine the selected columns by logical XOR",

    "ADD": "Add the selected column, or add the argument",
    "DIV": "Divide the selected columns (in order), or divide by the argument",
    "MUL": "Multiply the selected columns (in order), or multiply by the argument",
    "SUB": "Subtract the selected columns (in order), or subtract the argument",

    "IQR": "Calculate the row-wise interquartile range",
    "MAX": "Calculate the row-wise maximum",
    "MEAN": "Calculate the row-wise mean",
    "MEDIAN": "Calculate the row-wise median",
    "MIN": "Calculate the row-wise minimum",
    "SD": "Calculate the row-wise standard deviation",
        }

PREFERRED_ORDER = ["corpus_word", "word_label",
                   "corpus_pos", "word_pos", "pos_label",
                   "corpus_transcript", "word_transcript", "transcript_label",
                   "corpus_lemma", "word_lemma", "lemma_label",
                   "lemma_pos",
                   "corpus_gloss", "word_gloss", "gloss_label"]

DEFAULT_CONFIGURATION = "Default"

SQL_MYSQL = "mysql"
SQL_SQLITE = "sqlite"

SQL_ENGINES = [SQL_MYSQL, SQL_SQLITE]

# the tuples in MODULE_INFORMATION contain the following
# - title
# - minimum version
# - short description
# - URL
MODULE_INFORMATION = {
    "matplotlib": ("Python 2D plotting library",
                   "2.0.0",
                   "required for visualizations",
                   "http://http://matplotlib.org/"),
    "PyQt5": ("A set of Python Qt bindings for the Qt toolkit",
               "5.6",
               "Provides access to the Qt toolkit used for the GUI",
               "https://www.riverbankcomputing.com/software/pyqt/download"),
    "SQLAlchemy": ("The Python SQL toolkit",
            "1.0",
            "Use SQL databases for corpus storage",
            "http://http://www.sqlalchemy.org/"),
    "Pandas": ("Python data analysis library",
            "0.16",
            "Provides data structures to manage query result tables",
            "http://pandas.pydata.org/index.html"),
    "SciPy": ("SciPy is open-source software for mathematics, science, and engineering",
              "0.13.0",
              "Offer tests like the log-likelihood test",
              "https://www.scipy.org/scipylib/index.html"),
    "NLTK": ("The Natural Language Toolkit",
             "3.2.1",
            "Lemmatization and tagging when building your own corpora",
            "http://www.nltk.org"),
    "PyMySQL": ("A pure-Python MySQL client library",
            "0.6.4",
            "Connect to MySQL database servers",
            "https://github.com/PyMySQL/PyMySQL/"),
    "PDFMiner": ("PDF parser and analyzer (for Python 2.7)",
            "",
            "Build your own corpora from PDF files",
            "http://euske.github.io/pdfminer/index.html"),
    "pdfminer3k": ("PDF parser and analyzer (for Python 3.x)",
            "1.3",
            "Build your own corpora from PDF files",
            "https://pypi.python.org/pypi/pdfminer3k"),
    "python-docx": ("A Python library for creating and updating Microsoft Word (.docx) files",
            "0.3.0",
            "Build your own corpora from Microsoft Word (.docx) files",
            "https://python-docx.readthedocs.org/en/latest/"),
    "odfpy": ("API for OpenDocument in Python",
            "1.2.0",
            "Build your own corpora from OpenDocument Text (.odt) files",
            "https://github.com/eea/odfpy"),
    "BeautifulSoup": ("A Python library for pulling data out of HTML and XML files",
            "4.0",
            "Build your own corpora from HTML files",
            "http://www.crummy.com/software/BeautifulSoup/"),
    "tgt": ("TextGridTools - read, write, and manipulate Praat TextGrid files",
            "1.3.1",
            "Create <a href='http://www.praat.org'>Praat TextGrid</a> files for corpus queries",
            "https://github.com/hbuschme/TextGridTools/"),
    "chardet": ("The universal character encoding detector",
            "2.0.0",
            "Detect the encoding of your text files when building a corpus",
            "https://github.com/chardet/chardet"),
    "Seaborn": ("A Python statistical data visualization library",
            "0.7",
            "Create visualizations of your query results",
            "http://stanford.edu/~mwaskom/software/seaborn/"),
    "cachetools": ("cachetools — Extensible memoizing collections and decorators",
            "1.1.6",
            "Remember query results to speed up queries",
            "https://github.com/tkem/cachetools"),
    "statsmodels": ("statsmodels — Statistical computations and models for use with SciPy",
            "0.7.0",
            "Plot estimated cumulative distributions",
            "http://www.statsmodels.org/stable/"),
    "alsaaudio": ("alsaaudio – A package containing wrappers for accessing the ALSA API from Python",
            "0.8.2",
            "Audio support under Linux",
            "https://github.com/larsimmisch/pyalsaaudio/")
    }

# for Python 3 compatibility:
try:
    unicode()
except NameError:
    # Python 3 does not have unicode and long, so define them here:
    unicode = str
    long = int

msg_runtime_error_function = """
<p>Error during the evaluation of function</p>
<code style='color: #aa0000'>{}</code>:<br>{}</p>
<p>The function will be discarded.</p>"""

msg_parsing_error_template = """
<p><b>Syntax error in query string</b><p>
<p><code>{{}}<br>{{}}</code></p>
<p>{}</p>
"""

msg_escapable_template = """
<p><b>Syntax error in query string</b><p>
<p><code>{{}}<br>{{}}</code></p>
<p>{}</p>
<p>If you want to query for the character that caused this error as a
literal character, try to precede it by the backslash: <code>\</code><p>
"""

msg_unexpected_quantifier_start = msg_escapable_template.format("""
Query items may not start with the quantifier bracket
<code style='color: #aa0000'>{}</code>
""")

msg_unexpected_quantifier = msg_parsing_error_template.format("""
Only quantifiers starting with <code style='color: #aa0000'>{}</code> are
allowed after a query token (encountered {}).
""")

msg_unexpected_bracket = msg_parsing_error_template.format("""
Unexpected opening bracket <code style='color: #aa0000'>{}</code> within a
word
""")

msg_token_dangling_open = msg_escapable_template.format("""
There is no matching closing character <code style='color:
#aa0000'>{}</code> for the opening character <code style='color:
#aa0000'>{}</code>.</p>
""")

msg_missing_pos_spec = msg_parsing_error_template.format("""
Missing a part-of-speech specification after
<code style='color: #aa0000'>{}</code>.
""")

msg_userdata_warning = """
<p><b>Your results table contains user data.</b></p>
<p>If you start a new query, the user data that you have entered manually
will be lost.</p>
<p>Do you really want to start a new query?</p>
"""

msg_invalid_metadata = """
<p><b>The file that you selected does not appear to contain valid meta data.</b></p>
<p>A valid meta data file is a CSV file, i.e. a text file in which the
column values are separated by commas.</p>
<p>The first row of the meta data file contains the column names. One of
the column names has to be either <code>File</code> or <code>Filename</code>.
The values in this column have to contain the file name that the meta data
in the other columns of that row refers to.</p>
"""

msg_no_word_information = """
<p><b>Your stopword filters could not be applied to the results table.</b></p>
<p>In order to be able to use stopword filtering, the results table must
contain the orthographic representation of the matches. However, this
information was not selected as an output column in the last query.</p>
<p>Please activate the output column '<b>{}</b>' and run the query again
in order to be able to use stopword filtering.</p>
"""

msg_column_not_in_data = """
<p>This column is not contained in the results table.</p>
<p>Select the column in the output column table and re-run the query.</p>
"""

msg_adhoc_builder_texts = """
<p>You can build a new corpus by storing the words from a selection of text
files in a database that can be queried by Coquery. Your installation of
Coquery will recognize the following text file formats (more file formats
may be available if you install one of the optional modules, see
<a href='http://www.coquery.org/download/index.html#optional-python-modules'>
http://www.coquery.org/download</a>):</p>
<p><ul>{list}</uk></p>
<p>If the Natural Language Toolkit NLTK (<a href='http://www.nltk.org'>
http://www.nltk.org</a>) is installed on your computer, you can use it to
automatically lemmatize and POS-tag your new corpus.</p>"""

msg_adhoc_builder_table = """
<p>You can build a new corpus by storing the rows from a table in a database
that can be queried by Coquery.</p>"""

msg_invalid_filter = """
<p><b>The corpus filter '{}' is not valid.</b></p>
<p>One of your filters is not not valid for the currently selected corpus.
Please either disable using corpus filter from the Preferences menu, or
delete the invalid filter from the filter list.</p>
"""
msg_clear_filters = """
<p><b>You have requested to reset the list of corpus filters.</b></p>
<p>Click <b>Yes</b> if you really want to delete all filters in the list,
or <b>No</b> if you want to leave the stop word list unchanged.</p>
"""
msg_clear_stopwords = """
<p><b>You have requested to reset the list of stop words.</b></p>
<p>Click <b>Yes</b> if you really want to delete all stop words in the list,
or <b>No</b> if you want to leave the stop word list unchanged.</p>
"""
msg_missing_modules = """
<p><b>Not all required Python modules could be found.</b></p>
<p>Some of the Python modules that are required to run and use Coquery could
not be located on your system. The missing modules are:</p>
<p><code>\t{}</code></p>
<p>Please refer to the <a href="http://coquery.org/doc/">Coquery documentation</a>
for instructions on how to install the required modules.</p>
"""
msg_missing_module = """
<p><b>The optional Python module '<code>{name}</code>' could not be loaded.</b></p>
<p>The Python module called '{name}' is not installed on this computer.
Without this module, the following function is not available:</p>
<p>{function}</p>
<p>Please refer to the <a href="http://coquery.org/download/index.html#optional-python-modules">Coquery website</a> or
the module website for installation instructions: <a href="{url}">{url}</a>.</p>
"""
msg_visualization_error = """
<p><b>An error occurred while plotting.</b></p>
<p>While plotting the visualization, the following error was encountered:</p>
<p><code>{}</code></p>
<p>The visualization may be incorrect. Please contact the Coquery maintainers.</p>
"""
msg_no_lemma_information = """
<p><b>The current resource does not provide lemma information.</b></p>
<p>Your last query makes use of the lemma search syntax by enclosing query
tokens in square brackets <code>[...]</code>, but the current resource does
not provide lemmatized word entries.</p>
<p>Please change your query, for example by removing the square brackets
around the query token.</p>
"""
msg_corpus_path_not_valid = """
<p><b>The corpus data path does not seem to be valid.</b></p>
<p>{}</p>
<p>If you choose to <b>ignore</b> that the corpus data path is invalid,
Coquery will start the corpus installation using this directiory. After the
installation, you may still be able to use the corpus, but it will be
incomplete, or in an unusuable state.</p>
<p>If you choose to <b>discard</b> the invalid corpus data path, you can
enter the correct data path in the previous dialog, or cancel the corpus
installation altogether.</p>
<p>Do you wish to ignore or to discard the invalid corpus data path?</p>
"""
msg_mysql_no_configuration = """
<p><b>No database server configuration is available.</b></p>
<p>You haven't specified the configuration for your database server yet.
Please call 'Database servers...' from the Preferences menu, and set up a
configuration for your MySQL database server.</p>
<p>If you need assistance setting up your database server, call 'MySQL
server help' from the Help menu.</p>
"""
msg_options_error = """
<p><b>An error occurred while starting Coquery.</b></p>
<p>Coquery could not start due to an unexpected error while setting up
the program configuration.</p>
<p>We apologize for this problem. Please help us fix it by sending a
message to us: <a href="mailto:support@coquery.org">support@coquery.org</a>.
We will be in touch with you as quickly as possible.</p>
<p>To help us, include the following text in your message:<br><br><span style='color: #aa0000'>{}</span></p>
"""
msg_error_in_config = """
<p><b>There is an error in your configuration file.</b><p>
<p>While trying to read the configuration file, the following error occurred:
<br><br><code>{}</code></p>
<p>You can abort Coquery now, and try to fix the problem with the configuration file.</p>
<p>Alternatively, you can proceed without reading the configuration file.</p>
<p><b>Warning:</b> If you proceed without reading the configuration file,
all database connections that you have manually configured will be lost. You
will have to set them up again.<br></p>
<p>Do you want to abort Coquery now?</p>
"""
msg_warning_statistics = """
<p><b>You have unsaved data in the results table.</b></p>
<p>The corpus statistics will discard the results table from your last
query.</p>
<p>If you want to retrieve that results table later, you will have to
run the query again.</p>
<p>Do you wish to continue?</p>
"""
msg_no_context_available = """
<p><b>Context information is not available.</b></p>
<p>There is no context information available for the item that you have
selected.</p>"""
msg_corpus_no_documentation = """
<p><b>Corpus documentation for corpus '{corpus}' is not available.</b></p>
<p>The corpus module '{corpus}' does not provide a link to the corpus
documentation. You may find help on how the corpus is structured by using an
internet search engine.</p>"""
msg_install_abort = """
<p><b>You have requested to abort the installation.</b></p>
<p>The installation has not been completed yet. If you abort now, the data
installed so far will be discarded, and the corpus will still not be
available for queries.</p>"""
msg_invalid_installer = """
<p><b>The corpus installer '{name}' contains invalid code.</b></p>
<p>{code}</p>
<p>Please note that running an invalid corpus installer can potentially be
a security risk. For this reason, the corpus installer was disabled.</p>
"""

msg_validated_install = """
<p><b>You have requested the installation of the corpus '{corpus}'.</b></p>
<p>The Coquery website stores validation codes for all corpus installers that
have passed a security screening. During this screening, the installer code is
manually scanned for instructions that may be harmful to your computer,
software, or privacy.</p>
<p>The installer '{corpus}' has been validated. This means that the Coquery
maintainers do not consider it to be a security risk, but please note that
the Coquery maintainers cannot be held liable for damages arising out of the
use of this installer. See Section 16 of the
<a href="http://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License
</a> for details.</p>
<p>Click <b>Yes</b> to proceed with the installation, or <b>No</b> to abort it.
</p>
"""

msg_failed_validation_install = """
<p><b>The validation of the corpus installer '{corpus}' failed.</b></p>
<p>The Coquery website stores validation codes for all corpus installers that
have passed a security screening. During this screening, the installer code is
manually scanned for instructions that may be harmful to your computer,
software, or privacy.</p>
<p>The validation of the installer '{corpus}' failed. This means that your
copy of the installer does not match any copy of the installer that has been
validated by the Coquery maintainers. Please note that
the Coquery maintainers cannot be held liable for damages arising out of the
use of this installer. See Section 16 of the
<a href="http://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License
</a> for details.</p>
<p><b>You are advised to proceed with the installation only if you are certain
that the installer is from a trustworthy source.</b></p>
<p>Click <b>Yes</b> to proceed with the installation, or <b>No</b> to abort it.
</p>
"""
msg_unvalidated_install = """
<p><b>The corpus installer '{corpus}' could not be validated.</b></p>
<p>The Coquery website stores validation codes for all corpus installers that
have passed a security screening. During this screening, the installer code is
manually scanned for instructions that may be harmful to your computer,
software, or privacy.</p>
<p>For the installer '{corpus}', no validation code is available. This means
either that the installer has not yet been submitted to the screening process,
or that no validation code could be fetched from the Coquery website. Please
note that the Coquery maintainers cannot be held liable for damages arising
out of the use of this installer. See Section 16 of the
<a href="http://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License
</a> for details.</p>
<p><b>You are advised to proceed with the installation only if you are certain
that the installer is from a trustworthy source.</b></p>
<p>Click <b>Yes</b> to proceed with the installation, or <b>No</b> to abort it.
</p>
"""

msg_rejected_install = """
<p><b>The corpus installer '{corpus}' may be a security risk.</b></p>
<p>The Coquery website stores validation codes for all corpus installers that
have passed a security screening. During this screening, the installer code is
manually scanned for instructions that may be harmful to your computer,
software, or privacy.</p>
<p>The corpus installer '{corpus}' has been <b>rejected</b> during this
screening process. This means that the Coquery maintainers considered the
installer to be potentially harmful. Please note that
the Coquery maintainers cannot be held liable for damages arising out of the
use of this installer. See Section 16 of the
<a href="http://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License
</a> for details.</p>
<p><b>You are strongly advised not to continue with the installation of this
corpus.</b></p>
<p>If you with to ignore this warning, click <b>Yes</b> to continue with the
istallation. Click <b>No</b> if you wish to abort the installation of this
corpus.</p>
"""

msg_corpus_broken = """
<p><b>An error occurred while reading the installer '{name}'</b></p>
<p>The corpus installer stored in the file {name} could not be read. Most
likely, there is a programming error in the installer, or the file could
not be read.</p>
<p>Please inform the maintainer of this corpus installer of your problem.
When doing so, include the following information in your message:</p>
{type}
{code}"""
msg_disk_error = """
<p><b>An error occurred while accessing the disk storage.</b></p>
<p>The results have not been saved. Please try again. If the error persists,
try saving to a different location</p>"""
msg_encoding_error = """
<p><b>An encoding error occurred while trying to save the results.</b></p>
<p><span color="darkred">The save file is probably incomplete.</span></p>
<p>At least one column contains special characters which could not be
translated to a format that can be written to a file. You may try to work
around this issue by reducing the number of output columns so that the
offending character is not in the output anymore.</p>
<p>We apologize for this problem. Please do not hesitate to contact the
authors about it so that the problem may be fixed in a future
version.</p>"""
msg_query_running = """
<p><b>The last query is still running.</b></p>
<p>If you interrupt it, the results that have been retrieved so far will be discarded.</p>
<p>Do you really want to interrupt this query?</p>"""
msg_csv_encoding_error = """
<p><b>Illegal character encoding encountered.</b></p>
<p>An error occurred while trying to open the file {file} with the character
encoding <code>{encoding}</code>. Choose a different encoding from the list.</p>
"""
msg_csv_file_error = """
<p><b>The file could not be read.</b></p>
<p>An error occurred while trying to open the file {}.</p>
<p>Possible reasons include:
<ul><li>The file is empty</li>
<li>The file uses an unsupported character encoding</li>
<li>The storage device has an error</li></ul></p>
<p>Open the file in an editor to make sure that it is not empty. Save it using
one of the supported character encodings. Unicode/UTF-8 is strongly recommended.</p>
"""
msg_filename_error = """
<p><b>The file name is not valid.</b></p>
<p>You have chosen to read the query strings from a file, but the query file
name that you have entered is not valid. Please enter a valid query file
name, or select a file by pressing the Open button.</p>"""
msg_initialization_error = """
<p><b>An error occurred while initializing the database {code}.</b></p>
<p>Possible reasons include:
<ul><li>The database server is not running.</li>
<li>The host name or the server port are incorrect.</li>
<li>The user name or password are incorrect, or the user has insufficient
privileges.</li>
<li>You are trying to access a local database on a remote server, or vice
versa.</li>
</ul></p>
<p>Open <b>Database connections </b> in the Preferences menu to check whether
the connection to the database server is working, and if the settings are
correct.</p>"""
msg_corpus_remove = """
<p><b>You have requested to remove the corpus '{corpus}'.</b></p>
<p>This step cannot be reverted. If you proceed, the corpus will not be
available for further queries before you install it again.</p>
<p>Removing '{corpus}' will free approximately {size:.1S} of disk space.</p>
<p>Do you really want to remove the corpus?</p>"""
msg_remove_corpus_error = """
<p><b>A database error occurred while deleting the corpus '{corpus}'.</b></p>
<p>The corpus was <b>not</b> removed.</p>
<p>The database connection returned the following error message:</p>
<p><code>{code}</code></p>
<p>Please verify that the MySQL privileges for the current user allow you to
delete databases.</p>
"""
msg_remove_corpus_disk_error = """
<p><b>A disk error occurred while deleting the corpus database.</b></p>
<p>Please try removing the corpus another time. If the problem persists,
use your system tools to ensure that the storage device is fully
operational.</p>"""
msg_unsaved_data = """
<p><b>The last query results have not been saved.</b></p>
<p>If you quit now, they will be lost.</p>
<p>Do you really want to quit?</p>"""
msg_no_corpus = """
<p>Coquery could not find a corpus module. Without a corpus module, you cannot
run any query.</p>"""
msg_details = """
<p>To build a new corpus module from a selection of text files, select
<b>Build new corpus...</b> from the Corpus menu.</p>
<p>To install the corpus module for one of the corpora that are supported by
Coquery, select <b>Manage corpora...</b> from the Corpus menu.</p>"""
msg_orphanaged_databases = """
<p>An orphanaged database is a database file in Coquery's corpus folder that
is not associated with a corpus module. Therefore, this database cannot be
queried by Coquery.</p>
<p>Orphanaged databases are usually remains from previous failed attempts to
build a user corpus. If an error occurs during the corpus building procedure,
sometimes an incomplete database is created.</p>
<p>In general, it is save to delete orphanaged databases. Yet, as as this
step cannot be undone, you should carefully check the list of orphans.</p>
"""

gui_label_query_button = "&Query"
gui_label_stop_button = "&Stop"

# this is a list of all character encodings understood by Python, straight
# from the
CHARACTER_ENCODINGS = ["ascii",
    "big5",
    "big5hkscs",
    "cp037",
    "cp424",
    "cp437",
    "cp500",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp875",
    "cp932",
    "cp949",
    "cp950",
    "cp1006",
    "cp1026",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "euc_jp",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_kr",
    "gb2312",
    "gbk",
    "gb18030",
    "hz",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "latin_1",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "iso8859_10",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "johab",
    "koi8_r",
    "koi8_u",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "ptcp154",
    "shift_jis",
    "shift_jis_2004",
    "shift_jisx0213",
    "utf_32",
    "utf_32_be",
    "utf_32_le",
    "utf_16",
    "utf_16_be",
    "utf_16_le",
    "utf_7",
    "utf_8",
    "utf_8_sig"]

LANGUAGES = {
    'Language name': {
        0: 'Afar',
        1: 'Abkhaz',
        2: 'Avestan',
        3: 'Afrikaans',
        4: 'Akan',
        5: 'Amharic',
        6: 'Aragonese',
        7: 'Arabic',
        8: 'Assamese',
        9: 'Avaric',
        10: 'Aymara',
        11: 'Azerbaijani',
        12: 'Bashkir',
        13: 'Belarusian',
        14: 'Bulgarian',
        15: 'Bihari',
        16: 'Bislama',
        17: 'Bambara',
        18: 'Bengali',
        19: 'Tibetan',
        20: 'Breton',
        21: 'Bosnian',
        22: 'Catalan',
        23: 'Chechen',
        24: 'Chamorro',
        25: 'Corsican',
        26: 'Cree',
        27: 'Czech',
        28: 'Old Church Slavonic',
        29: 'Chuvash',
        30: 'Welsh',
        31: 'Danish',
        32: 'German',
        33: 'Maldivian',
        34: 'Dzongkha',
        35: 'Ewe',
        36: 'Greek',
        37: 'English',
        38: 'Esperanto',
        39: 'Spanish',
        40: 'Estonian',
        41: 'Basque',
        42: 'Farsi',
        43: 'Fula',
        44: 'Finnish',
        45: 'Fijian',
        46: 'Faroese',
        47: 'French',
        48: 'West Frisian',
        49: 'Irish',
        50: 'Scottish Gaelic',
        51: 'Galician',
        52: 'Guaraní',
        53: 'Gujarati',
        54: 'Manx',
        55: 'Hausa',
        56: 'Hebrew',
        57: 'Hindi',
        58: 'Hiri Motu',
        59: 'Croatian',
        60: 'Haitian Creole',
        61: 'Hungarian',
        62: 'Armenian',
        63: 'Herero',
        64: 'Interlingua',
        65: 'Indonesian',
        66: 'Interlingue',
        67: 'Igbo',
        68: 'Nuosu',
        69: 'Inupiaq',
        70: 'Ido',
        71: 'Icelandic',
        72: 'Italian',
        73: 'Inuktitut',
        74: 'Japanese',
        75: 'Javanese',
        76: 'Georgian',
        77: 'Kongo',
        78: 'Kikuyu',
        79: 'Kwanyama',
        80: 'Kazakh',
        81: 'Kalaallisut',
        82: 'Khmer',
        83: 'Kannada',
        84: 'Korean',
        85: 'Kanuri',
        86: 'Kashmiri',
        87: 'Kurdish',
        88: 'Komi',
        89: 'Cornish',
        90: 'Kyrgyz',
        91: 'Latin',
        92: 'Luxembourgish',
        93: 'Ganda',
        94: 'Limburgish',
        95: 'Lingala',
        96: 'Lao',
        97: 'Lithuanian',
        98: 'Luba-Katanga',
        99: 'Latvian',
        100: 'Malagasy',
        101: 'Marshallese',
        102: 'Māori',
        103: 'Macedonian',
        104: 'Malayalam',
        105: 'Mongolian',
        106: 'Marathi (Marāṭhī)',
        107: 'Malay',
        108: 'Maltese',
        109: 'Burmese',
        110: 'Nauruan',
        111: 'Norwegian Bokmål',
        112: 'Northern Ndebele',
        113: 'Nepali',
        114: 'Ndonga',
        115: 'Dutch',
        116: 'Norwegian Nynorsk',
        117: 'Norwegian',
        118: 'Southern Ndebele',
        119: 'Navajo',
        120: 'Chichewa',
        121: 'Occitan',
        122: 'Ojibwe',
        123: 'Oromo',
        124: 'Oriya',
        125: 'Ossetian',
        126: 'Eastern Punjabi',
        127: 'Pāli',
        128: 'Polish',
        129: 'Pashto',
        130: 'Portuguese',
        131: 'Quechua',
        132: 'Romansh',
        133: 'Kirundi',
        134: 'Romanian',
        135: 'Russian',
        136: 'Kinyarwanda',
        137: 'Sanskrit',
        138: 'Sardinian',
        139: 'Sindhi',
        140: 'Northern Sami',
        141: 'Sango',
        142: 'Sinhalese',
        143: 'Slovak',
        144: 'Slovene',
        145: 'Samoan',
        146: 'Shona',
        147: 'Somali',
        148: 'Albanian',
        149: 'Serbian',
        150: 'Swati',
        151: 'Southern Sotho',
        152: 'Sundanese',
        153: 'Swedish',
        154: 'Swahili',
        155: 'Tamil',
        156: 'Telugu',
        157: 'Tajik',
        158: 'Thai',
        159: 'Tigrinya',
        160: 'Turkmen',
        161: 'Tagalog',
        162: 'Tswana',
        163: 'Tongan',
        164: 'Turkish',
        165: 'Tsonga',
        166: 'Tatar',
        167: 'Twi',
        168: 'Tahitian',
        169: 'Uyghur',
        170: 'Ukrainian',
        171: 'Urdu',
        172: 'Uzbek',
        173: 'Venda',
        174: 'Vietnamese',
        175: 'Volapük',
        176: 'Walloon',
        177: 'Wolof',
        178: 'Xhosa',
        179: 'Yiddish',
        180: 'Yoruba',
        181: 'Zhuang',
        182: 'Chinese',
        183: 'Zulu'
    },
    '639-1': {
        0: 'aa',
        1: 'ab',
        2: 'ae',
        3: 'af',
        4: 'ak',
        5: 'am',
        6: 'an',
        7: 'ar',
        8: 'as',
        9: 'av',
        10: 'ay',
        11: 'az',
        12: 'ba',
        13: 'be',
        14: 'bg',
        15: 'bh',
        16: 'bi',
        17: 'bm',
        18: 'bn',
        19: 'bo',
        20: 'br',
        21: 'bs',
        22: 'ca',
        23: 'ce',
        24: 'ch',
        25: 'co',
        26: 'cr',
        27: 'cs',
        28: 'cu',
        29: 'cv',
        30: 'cy',
        31: 'da',
        32: 'de',
        33: 'dv',
        34: 'dz',
        35: 'ee',
        36: 'el',
        37: 'en',
        38: 'eo',
        39: 'es',
        40: 'et',
        41: 'eu',
        42: 'fa',
        43: 'ff',
        44: 'fi',
        45: 'fj',
        46: 'fo',
        47: 'fr',
        48: 'fy',
        49: 'ga',
        50: 'gd',
        51: 'gl',
        52: 'gn',
        53: 'gu',
        54: 'gv',
        55: 'ha',
        56: 'he',
        57: 'hi',
        58: 'ho',
        59: 'hr',
        60: 'ht',
        61: 'hu',
        62: 'hy',
        63: 'hz',
        64: 'ia',
        65: 'id',
        66: 'ie',
        67: 'ig',
        68: 'ii',
        69: 'ik',
        70: 'io',
        71: 'is',
        72: 'it',
        73: 'iu',
        74: 'ja',
        75: 'jv',
        76: 'ka',
        77: 'kg',
        78: 'ki',
        79: 'kj',
        80: 'kk',
        81: 'kl',
        82: 'km',
        83: 'kn',
        84: 'ko',
        85: 'kr',
        86: 'ks',
        87: 'ku',
        88: 'kv',
        89: 'kw',
        90: 'ky',
        91: 'la',
        92: 'lb',
        93: 'lg',
        94: 'li',
        95: 'ln',
        96: 'lo',
        97: 'lt',
        98: 'lu',
        99: 'lv',
        100: 'mg',
        101: 'mh',
        102: 'mi',
        103: 'mk',
        104: 'ml',
        105: 'mn',
        106: 'mr',
        107: 'ms',
        108: 'mt',
        109: 'my',
        110: 'na',
        111: 'nb',
        112: 'nd',
        113: 'ne',
        114: 'ng',
        115: 'nl',
        116: 'nn',
        117: 'no',
        118: 'nr',
        119: 'nv',
        120: 'ny',
        121: 'oc',
        122: 'oj',
        123: 'om',
        124: 'or',
        125: 'os',
        126: 'pa',
        127: 'pi',
        128: 'pl',
        129: 'ps',
        130: 'pt',
        131: 'qu',
        132: 'rm',
        133: 'rn',
        134: 'ro',
        135: 'ru',
        136: 'rw',
        137: 'sa',
        138: 'sc',
        139: 'sd',
        140: 'se',
        141: 'sg',
        142: 'si',
        143: 'sk',
        144: 'sl',
        145: 'sm',
        146: 'sn',
        147: 'so',
        148: 'sq',
        149: 'sr',
        150: 'ss',
        151: 'st',
        152: 'su',
        153: 'sv',
        154: 'sw',
        155: 'ta',
        156: 'te',
        157: 'tg',
        158: 'th',
        159: 'ti',
        160: 'tk',
        161: 'tl',
        162: 'tn',
        163: 'to',
        164: 'tr',
        165: 'ts',
        166: 'tt',
        167: 'tw',
        168: 'ty',
        169: 'ug',
        170: 'uk',
        171: 'ur',
        172: 'uz',
        173: 've',
        174: 'vi',
        175: 'vo',
        176: 'wa',
        177: 'wo',
        178: 'xh',
        179: 'yi',
        180: 'yo',
        181: 'za',
        182: 'zh',
        183: 'zu'
    },
    '639-2': {
        0: 'aar',
        1: 'abk',
        2: 'ave',
        3: 'afr',
        4: 'aka',
        5: 'amh',
        6: 'arg',
        7: 'ara',
        8: 'asm',
        9: 'ava',
        10: 'aym',
        11: 'aze',
        12: 'bak',
        13: 'bel',
        14: 'bul',
        15: 'bih',
        16: 'bis',
        17: 'bam',
        18: 'ben',
        19: 'bod',
        20: 'bre',
        21: 'bos',
        22: 'cat',
        23: 'che',
        24: 'cha',
        25: 'cos',
        26: 'cre',
        27: 'ces',
        28: 'chu',
        29: 'chv',
        30: 'cym',
        31: 'dan',
        32: 'deu',
        33: 'div',
        34: 'dzo',
        35: 'ewe',
        36: 'ell',
        37: 'eng',
        38: 'epo',
        39: 'spa',
        40: 'est',
        41: 'eus',
        42: 'fas',
        43: 'ful',
        44: 'fin',
        45: 'fij',
        46: 'fao',
        47: 'fra',
        48: 'fry',
        49: 'gle',
        50: 'gla',
        51: 'glg',
        52: 'grn',
        53: 'guj',
        54: 'glv',
        55: 'hau',
        56: 'heb',
        57: 'hin',
        58: 'hmo',
        59: 'hrv',
        60: 'hat',
        61: 'hun',
        62: 'hye',
        63: 'her',
        64: 'ina',
        65: 'ind',
        66: 'ile',
        67: 'ibo',
        68: 'iii',
        69: 'ipk',
        70: 'ido',
        71: 'isl',
        72: 'ita',
        73: 'iku',
        74: 'jpn',
        75: 'jav',
        76: 'kat',
        77: 'kon',
        78: 'kik',
        79: 'kua',
        80: 'kaz',
        81: 'kal',
        82: 'khm',
        83: 'kan',
        84: 'kor',
        85: 'kau',
        86: 'kas',
        87: 'kur',
        88: 'kom',
        89: 'cor',
        90: 'kir',
        91: 'lat',
        92: 'ltz',
        93: 'lug',
        94: 'lim',
        95: 'lin',
        96: 'lao',
        97: 'lit',
        98: 'lub',
        99: 'lav',
        100: 'mlg',
        101: 'mah',
        102: 'mri',
        103: 'mkd',
        104: 'mal',
        105: 'mon',
        106: 'mar',
        107: 'msa',
        108: 'mlt',
        109: 'mya',
        110: 'nau',
        111: 'nob',
        112: 'nde',
        113: 'nep',
        114: 'ndo',
        115: 'nld',
        116: 'nno',
        117: 'nor',
        118: 'nbl',
        119: 'nav',
        120: 'nya',
        121: 'oci',
        122: 'oji',
        123: 'orm',
        124: 'ori',
        125: 'oss',
        126: 'pan',
        127: 'pli',
        128: 'pol',
        129: 'pus',
        130: 'por',
        131: 'que',
        132: 'roh',
        133: 'run',
        134: 'ron',
        135: 'rus',
        136: 'kin',
        137: 'san',
        138: 'srd',
        139: 'snd',
        140: 'sme',
        141: 'sag',
        142: 'sin',
        143: 'slk',
        144: 'slv',
        145: 'smo',
        146: 'sna',
        147: 'som',
        148: 'sqi',
        149: 'srp',
        150: 'ssw',
        151: 'sot',
        152: 'sun',
        153: 'swe',
        154: 'swa',
        155: 'tam',
        156: 'tel',
        157: 'tgk',
        158: 'tha',
        159: 'tir',
        160: 'tuk',
        161: 'tgl',
        162: 'tsn',
        163: 'ton',
        164: 'tur',
        165: 'tso',
        166: 'tat',
        167: 'twi',
        168: 'tah',
        169: 'uig',
        170: 'ukr',
        171: 'urd',
        172: 'uzb',
        173: 'ven',
        174: 'vie',
        175: 'vol',
        176: 'wln',
        177: 'wol',
        178: 'xho',
        179: 'yid',
        180: 'yor',
        181: 'zha',
        182: 'zho',
        183: 'zul'
    },
    'Native name': {
        0: ['Afaraf'],
        1: ['аҧсуа бызшәа', 'аҧсшәа'],
        2: ['avesta'],
        3: ['Afrikaans'],
        4: ['Akan'],
        5: ['አማርኛ'],
        6: ['aragonés'],
        7: ['العربية'],
        8: ['অসমীয়া'],
        9: ['авар мацӀ', 'магӀарул мацӀ'],
        10: ['aymar aru'],
        11: ['azərbaycan dili'],
        12: ['башҡорт теле'],
        13: ['беларуская мова'],
        14: ['български език'],
        15: ['भोजपुरी'],
        16: ['Bislama'],
        17: ['bamanankan'],
        18: ['বাংলা'],
        19: ['བོད་ཡིག'],
        20: ['brezhoneg'],
        21: ['bosanski jezik'],
        22: ['català'],
        23: ['нохчийн мотт'],
        24: ['Chamoru'],
        25: ['corsu', 'lingua corsa'],
        26: ['ᓀᐦᐃᔭᐍᐏᐣ'],
        27: ['čeština', 'český jazyk'],
        28: ['ѩзыкъ словѣньскъ'],
        29: ['чӑваш чӗлхи'],
        30: ['Cymraeg'],
        31: ['dansk'],
        32: ['Deutsch'],
        33: ['ދިވެހި'],
        34: ['རྫོང་ཁ'],
        35: ['Eʋegbe'],
        36: ['ελληνικά'],
        37: ['English'],
        38: ['Esperanto'],
        39: ['español'],
        40: ['eesti', 'eesti keel'],
        41: ['euskara', 'euskera'],
        42: ['فارسی'],
        43: ['Fulfulde', 'Pulaar', 'Pular'],
        44: ['suomi', 'suomen kieli'],
        45: ['vosa Vakaviti'],
        46: ['føroyskt'],
        47: ['français', 'langue française'],
        48: ['Frysk'],
        49: ['Gaeilge'],
        50: ['Gàidhlig'],
        51: ['galego'],
        52: ["Avañe'ẽ"],
        53: ['ગુજરાતી'],
        54: ['Gaelg', 'Gailck'],
        55: ['(Hausa) هَوُسَ'],
        56: ['עברית'],
        57: ['हिन्दी', 'हिंदी'],
        58: ['Hiri Motu'],
        59: ['hrvatski jezik'],
        60: ['Kreyòl ayisyen'],
        61: ['magyar'],
        62: ['Հայերեն'],
        63: ['Otjiherero'],
        64: ['Interlingua'],
        65: ['Bahasa Indonesia'],
        66: ['Interlingue'],
        67: ['Asụsụ Igbo'],
        68: ['ꆈꌠ꒿ Nuosuhxop'],
        69: ['Iñupiaq', 'Iñupiatun'],
        70: ['Ido'],
        71: ['Íslenska'],
        72: ['italiano'],
        73: ['ᐃᓄᒃᑎᑐᑦ'],
        74: ['日本語\xa0(にほんご)'],
        75: ['ꦧꦱꦗꦮ', 'Basa Jawa'],
        76: ['ქართული'],
        77: ['Kikongo'],
        78: ['Gĩkũyũ'],
        79: ['Kuanyama'],
        80: ['қазақ тілі'],
        81: ['kalaallisut', 'kalaallit oqaasii'],
        82: ['ខ្មែរ', 'ខេមរភាសា', 'ភាសាខ្មែរ'],
        83: ['ಕನ್ನಡ'],
        84: ['한국어', '\xa0조선어'],
        85: ['Kanuri'],
        86: ['कश्मीरी', '\xa0كشميري\u200e'],
        87: ['Kurdî', '\xa0كوردی\u200e'],
        88: ['коми кыв'],
        89: ['Kernewek'],
        90: ['Кыргызча', 'Кыргыз тили'],
        91: ['latine', 'lingua latina'],
        92: ['Lëtzebuergesch'],
        93: ['Luganda'],
        94: ['Limburgs'],
        95: ['Lingála'],
        96: ['ພາສາລາວ'],
        97: ['lietuvių kalba'],
        98: ['Tshiluba'],
        99: ['latviešu valoda'],
        100: ['fiteny malagasy'],
        101: ['Kajin M̧ajeļ'],
        102: ['te reo Māori'],
        103: ['македонски јазик'],
        104: ['മലയാളം'],
        105: ['Монгол хэл'],
        106: ['मराठी'],
        107: ['bahasa Melayu', 'بهاس ملايو\u200e'],
        108: ['Malti'],
        109: ['ဗမာစာ'],
        110: ['Dorerin Naoero'],
        111: ['Norsk bokmål'],
        112: ['isiNdebele'],
        113: ['नेपाली'],
        114: ['Owambo'],
        115: ['Nederlands', 'Vlaams'],
        116: ['Norsk nynorsk'],
        117: ['Norsk'],
        118: ['isiNdebele'],
        119: ['Diné bizaad'],
        120: ['chiCheŵa', 'chinyanja'],
        121: ['occitan', " lenga d'òc"],
        122: ['ᐊᓂᔑᓈᐯᒧᐎᓐ'],
        123: ['Afaan Oromoo'],
        124: ['ଓଡ଼ିଆ'],
        125: ['ирон æвзаг'],
        126: ['ਪੰਜਾਬੀ'],
        127: ['पाऴि'],
        128: ['język polski', 'polszczyzna'],
        129: ['پښتو'],
        130: ['Português'],
        131: ['Runa Simi', 'Kichwa'],
        132: ['rumantsch grischun'],
        133: ['Ikirundi'],
        134: ['Română'],
        135: ['Русский'],
        136: ['Ikinyarwanda'],
        137: ['संस्कृतम्'],
        138: ['sardu'],
        139: ['सिन्धी', '\xa0سنڌي، سندھی\u200e'],
        140: ['Davvisámegiella'],
        141: ['yângâ tî sängö'],
        142: ['සිංහල'],
        143: ['slovenčina', 'slovenský jazyk'],
        144: ['slovenski jezik', 'slovenščina'],
        145: ["gagana fa'a Samoa"],
        146: ['chiShona'],
        147: ['Soomaaliga', 'af Soomaali'],
        148: ['Shqip'],
        149: ['српски језик'],
        150: ['SiSwati'],
        151: ['Sesotho'],
        152: ['Basa Sunda'],
        153: ['svenska'],
        154: ['Kiswahili'],
        155: ['தமிழ்'],
        156: ['తెలుగు'],
        157: ['тоҷикӣ', '\xa0toçikī', 'تاجیکی\u200e'],
        158: ['ไทย'],
        159: ['ትግርኛ'],
        160: ['Türkmen', 'Түркмен'],
        161: ['Wikang Tagalog'],
        162: ['Setswana'],
        163: ['faka Tonga'],
        164: ['Türkçe'],
        165: ['Xitsonga'],
        166: ['татар теле', 'tatar tele'],
        167: ['Twi'],
        168: ['Reo Tahiti'],
        169: ['ئۇيغۇرچە\u200e', 'Uyghurche'],
        170: ['Українська'],
        171: ['اردو'],
        172: ['Oʻzbek', '\xa0Ўзбек', 'أۇزبېك\u200e'],
        173: ['Tshivenḓa'],
        174: ['Tiếng Việt'],
        175: ['Volapük'],
        176: ['walon'],
        177: ['Wollof'],
        178: ['isiXhosa'],
        179: ['ייִדיש'],
        180: ['Yorùbá'],
        181: ['Saɯ cueŋƅ', 'Saw cuengh'],
        182: ['中文(Zhōngwén)', '\xa0汉语', '\xa0漢語'],
        183: ['isiZulu']
    }
    }

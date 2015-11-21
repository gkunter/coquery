# -*- coding: utf-8 -*-
"""
errors.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import traceback
import os
import logging
import __init__

class GenericException(Exception):
    def __init__(self, *par):
        self.par = ", ".join([str(x) for x in par])

    def __str__(self):
        if self.par:
            S = "%s: '%s'" % (self.error_message, self.par)
        else:
            S = self.error_message
        logger.error(S)
        return S

class NoTraceException(GenericException):
    """ For NoTraceException and derived exception classes, no call trace
    is printed in the exception handler print_exception(). This is useful
    for system errors. """

class NoArgumentsError(NoTraceException):
    error_message = "No arguments given to script."

class VisualizationNoDataError(NoTraceException):
    error_message = """
    <p><b>The 'Query results' view is empty.</b></p>
    <p>You have either not run a query in this session yet, there are no 
    tokens in the corpus that match your last query, or you have hidden all
    output columns.</p>
    <p>Try to run a visualization again once the Query results view is not 
    empty anymore.</p>
    """

class VisualizationModuleError:
    def __init__(self, module, msg):
        self.error_message = """
        <p><b>Could not load module '{module}'</b></p>
        <p>There is a problem with the visualization module named '{module}'. If
        you downloaded this module from an external source, you may want to
        see if an updated version is available. Otherwise, either contact
        the author of the module, or report this error on the Coquery bug
        tracker.</p>
        <p>Please include this error message:</p>
        <p>{msg}</p>
        """.format(module=module, msg=msg)
    
class VisualizationInvalidLayout(NoTraceException):
    error_message = """<p><b>The visualization grid layout is too large.</b></p>
    <p>The visualization could not be plotted because either the row grouping 
    factor or the column grouping factor contains more than 16 distinct values.
    The resulting plot would thus contain more than 16 rows or columns, which
    is too small to plot.</p>
    <p>You may try to rearrange your results table by either hiding or moving 
    the column that causes this problem, or by selecting other output columns
    with less distinct values.</p>"""

class VisualizationInvalidDataError(NoTraceException):
    error_message = """<p><b>Your results table cannot be plotted by this visualizer.</b></p>
    <p>The visualizer that you selected expects a particular type of data that
    could not be found in the results table. For example, the 'Time Data' 
    visualizers expect a data column that contains temporal data (e.g. Date
    or Age).</p>
    <p>You can either choose a different visualization for your results table,
    or you can select those output columns which provide the required data. 
    After you have re-run the query with these additional output columns, you
    can try to visualize the results table again.</p>"""
    
class CollocationNoContextError(NoTraceException):
    error_message = """<p><b>Cannot calculate the collocations</b></p>
    <p>In order to calculate the collocations of a word, a context span
    has to be defined. Use the "Left context" and "Right context" field to 
    set the span of words within which Coquery will search for collocates.
    </p>"""
    
class ContextUnvailableError(NoTraceException):
    error_message = """
    <p>The selected corpus does not provide enough information to show the
    context of the token.</p>
    """

class UnknownArgumentError(NoTraceException):
    error_message = "Unknown argument given to script."

class ConfigurationError(GenericException):
    error_message = "Configuration file incomplete or with errors."

class NoCorpusError(NoTraceException):
    error_message = "No corpus is available."

class NoCorpusSpecifiedError(NoTraceException):
    error_message = "No corpus name given to script."
    
class CorpusUnavailableError(NoTraceException):
    error_message = "No corpus available with given name"

class DependencyError(NoTraceException):
    def __init__(self, module):
        if type(module) == list:
            self.error_message = "Missing one of the following Python modules"
            self.par = "{} or {}".format(", ".join(module[:-1]), module[-1])
        else:
            self.error_message = "Missing the following Python module"
            self.par = "{}".format(module)

class QueryModeError(NoTraceException):
    error_message = "Query mode {mode} not supported by corpus {corpus}."
    def __init__(self, Corpus, Mode):
        self.error_message = self.error_message.format(mode = Mode, corpus = Corpus)
        self.par = ""

class IllegalArgumentError(NoTraceException):
    error_message = "Illegal argument value"
    def __init__(self, par):
        self.par = par

class EmptyInputFileError(NoTraceException):
    error_message = "The query input file {} is empty or cannot be read."
    def __init__(self, par):
        self.par = ""
        self.error_message = self.error_message.format(par)

class TokenPartOfSpeechError(NoTraceException):
    error_message = "Illegal part of speech specification"

class TokenParseError(NoTraceException):
    error_message = "Illegal token format"

class TokenUnsupportedTranscriptError(NoTraceException):
    error_message = "Lexicon does not support phonetic transcriptions"

class InvalidFilterError(NoTraceException):
    error_message = "Invalid query filter specification"

class CorpusUnavailableQueryTypeError(GenericException):
    error_message = "Query type %s not available for corpus %s"
    def __init__(self, Corpus, Type):
        self.error_message = self.error_message % (Type, Corpus)
        self.par = ""

class CorpusUnsupportedFunctionError(GenericException):
    error_message = "Function not yet supported by corpus."

class ResourceIncompleteDefinitionError(GenericException):
    error_message = "Resource definition does not contain all requested fields."

class LexiconUnsupportedFunctionError(GenericException):
    error_message = "Function not yet supported by lexicon."

class WordNotInLexiconError(NoTraceException):
    error_message = "Word is not in the lexicon"

class LexiconUnknownPartOfSpeechTag(GenericException):
    error_message = "Part-of-speech tag not in current lexicon"
    def __init__(self, par):
        self.par = par

class LexiconFeatureUnavailableError(NoTraceException):
    error_message = "Lexicon feature not provided by current lexicon"
    #def __init__(self, S):
        #self.par = S

class SourceFeatureUnavailableError(NoTraceException):
    error_message = "Requested source feature not provided by corpus"

class CorpusUnsupportedError(NoTraceException):
    error_message = "Corpus not supported"

class TextFilterError(NoTraceException):
    error_message = "Your source filter caused an error."

class SQLInitializationError(GenericException):
    error_message = "SQL initialization error"

class SQLOperationalError(GenericException):
    error_message = "SQL operational error"

class SQLProgrammingError(GenericException):
    error_message = "SQL programming error"

class SQLNoConfigurationError(NoTraceException):
    error_message = "No MySQL configuration could be detected."

class SQLNoConnectorError(GenericException):
    error_message = """The MySQL connector module 'pymysql' was not found for 
    your current Python configuration.
    
    Please install this module, and try again. On many systems, you can use
    the Python package installer 'pip' to do this. The command to install
    pymysql using pip is:
    
    pip install pymysql
    
    If your receive an error message which states that the command 'pip' 
    could not be found, you need to install it first. Please refer to 
    https://pip.pypa.io/ for instructions.
    """

def get_error_repr(exc_info):
    exc_type, exc_obj, exc_tb = exc_info
    Trace = traceback.extract_tb(exc_tb)
    trace_string = ""
    Indent = ""
    Text = ""
    for FileName, LineNo, FunctionName, Text in Trace:
        ModuleName = os.path.split(FileName) [1]
        trace_string += "%s %s, line %s: %s\n" % (Indent, ModuleName, LineNo, FunctionName)
        Indent += "  "
    if Text:
        trace_string += "%s> %s\n" % (Indent[:-1], Text)
    return (exc_type, exc_obj, trace_string)

def print_exception(e):
    error_string = ""
    if not isinstance(e, NoTraceException):
        _, _, error_string = get_error_repr(sys.exc_info())
        error_string = "TRACE:\n" + error_string
    error_string += "ERROR %s: %s\n" % (type(e).__name__, e)
    print(error_string, file=sys.stderr)

try:
    logger = logging.getLogger(__init__.NAME)
except AttributeError:
    pass

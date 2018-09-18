# -*- coding: utf-8 -*-
"""
errors.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import traceback
import os
import re
import textwrap
import logging

from .unicode import utf8

_source_paths = [sys.path[0]]


def add_source_path(s):
    global _source_paths
    _source_paths.append(s)


def remove_source_path(s):
    global _source_paths
    _source_paths.remove(s)


def get_source_paths():
    return _source_paths


class GenericException(Exception):
    def __init__(self, *par):
        self.par = ", ".join([utf8(x) for x in par])
        self.error_message = "Error"

    def __str__(self):
        if self.par:
            S = "%s: '%s'" % (self.error_message, self.par)
        else:
            S = self.error_message
        if hasattr(self, "additional"):
            S = "<p>{}</p><p>{}</p>".format(
                S, self.additional)
        try:
            logging.error(S)
        except Exception as e:
            print_exception(e)
        return S


class NoTraceException(GenericException):
    """ For NoTraceException and derived exception classes, no call trace
    is printed in the exception handler print_exception(). This is useful
    for system errors. """


class NoArgumentsError(NoTraceException):
    error_message = "No arguments given to script."


class RegularExpressionError(NoTraceException):
    _msg = """

    <p><b>There is an error in your regular expression.</b></p>
    <p>Your regular expression <code>'{}'</code> caused an error at position
    {}:</p>
    <p><span style='color: red'>{}</span></p>"""

    def __init__(self, prefix, pat, pos, msg):
        self.par = None
        self.error_message = self._msg.format(pat, pos, msg)


class VisualizationNoDataError(NoTraceException):
    error_message = """
    <p><b>The 'Query results' view is empty.</b></p>
    <p>You have either not run a query in this session yet, there are no
    tokens in the corpus that match your last query, or you have hidden all
    output columns.</p>
    <p>Try to run a visualization again once the Query results view is not
    empty anymore.</p>
    """


class VisualizationInvalidLayout(NoTraceException):
    error_message = """
    <p><b>The visualization grid layout is too large.</b></p>
    <p>The visualization could not be plotted because either the row grouping
    factor or the column grouping factor contains more than 16 distinct
    values. The resulting plot would thus contain more than 16 rows or
    columns, which is too small to plot.</p>
    <p>You may try to rearrange your results table by either hiding or moving
    the column that causes this problem, or by selecting other output columns
    with less distinct values.</p>"""


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


class IllegalCodeInModuleError(NoTraceException):
    error_message = ("The corpus module '{}' for configuration '{}' contains "
                     "illegal code  (line {}).")

    def __init__(self, module, configuration, lineno):
        self.par = ""
        self.error_message = self.error_message.format(
            module, configuration, lineno)


class IllegalFunctionInModuleError(NoTraceException):
    error_message = ("The corpus module '{}' for configuration '{}' contains "
                     "illegal class definition: {} (line {})")

    def __init__(self, module, configuration, class_name, lineno):
        self.par = ""
        self.error_message = self.error_message.format(
            module, configuration, class_name, lineno)


class IllegalImportInModuleError(NoTraceException):
    error_message = ("The corpus module '{}' for configuration '{}' attempts "
                     "to import a blocked module: {}  (line {})")

    def __init__(self, module, configuration, module_name, lineno):
        self.par = ""
        self.error_message = self.error_message.format(
            module, configuration, module_name, lineno)


class ModuleIncompleteError(NoTraceException):
    error_message = ("The corpus module '{}' for configuration '{}' does not "
                     "contain all required definitions. Missing: {}")

    def __init__(self, module, configuration, element_list):
        self.par = ""
        self.error_message = self.error_message.format(
            module, configuration, ", ".join(element_list))


class UnsupportedQueryItemError(NoTraceException):
    error_message = ("The current corpus does not support query items of the "
                     "type '{}'. Please change your query string.")

    def __init__(self, query_item_type):
        self.par = ""
        self.error_message = self.error_message.format(query_item_type)


class ConfigurationError(GenericException):
    def __init__(self, msg):
        self.error_message = msg
        self.par = ""


class NoCorpusError(NoTraceException):
    error_message = "No corpus is available."


class NoCorpusSpecifiedError(NoTraceException):
    error_message = "No corpus name given to script."


class CorpusUnavailableError(NoTraceException):
    error_message = "No corpus available with given name"


class DependencyError(NoTraceException):
    def __init__(self, module, url=None):
        if type(module) == list:
            self.error_message = "Missing one of the following Python modules"
            self.par = "{} or {}".format(", ".join(module[:-1]), module[-1])
        else:
            self.error_message = "Missing the following Python module"
            self.par = "{}".format(module)
        if url:
            self.additional = ("Go to <a href='{url}'>{url}</a> for details "
                               "on how to obtain the module.".format(url=url))


class IllegalArgumentError(NoTraceException):
    error_message = "Illegal argument value"

    def __init__(self, par):
        self.par = par


class EmptyInputFileError(NoTraceException):
    error_message = "The query input file {} is empty or cannot be read."

    def __init__(self, par):
        self.par = ""
        self.error_message = self.error_message.format(par)


class TokenParseError(NoTraceException):
    error_message = "Illegal token format"


class CorpusUnavailableQueryTypeError(GenericException):
    error_message = "Query type %s not available for corpus %s"

    def __init__(self, Corpus, Type):
        self.error_message = self.error_message % (Type, Corpus)
        self.par = ""


class SQLInitializationError(GenericException):
    error_message = "SQL initialization error"


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
    trace = traceback.extract_tb(exc_tb)
    trace_string = ""
    indent = ""
    text = ""
    file_location = ""
    for file_name, line_no, func_name, text in trace:
        path, module_name = os.path.split(file_name)
        # only print exceptions from Coquery files:
        if any([path.startswith(x) for x in get_source_paths()]):
            trace_string += "{} {}, line {}: {}\n".format(
                indent, module_name, line_no, func_name.replace("<", "&lt;"))
            indent += "  "
        file_location = "{}, line {}".format(file_name, line_no)
    if text:
        trace_string += "%s> %s\n" % (indent[:-1], text)
    return (exc_type, exc_obj, trace_string, file_location)


def print_exception(exc):
    """
    Prints the exception string to StdErr. XML tags are stripped.
    """
    error_string = ""
    if isinstance(exc, Exception):
        if not isinstance(exc, NoTraceException):
            _, _, error_string, _ = get_error_repr(sys.exc_info())
            error_string = "TRACE:\n{}".format(error_string)
        error_string += "ERROR {}: {}\n".format(type(exc).__name__, exc)
    else:
        error_string = exc

    for par in [x.strip(" ") for
                x in error_string.split("</p>") if x.strip(" ")]:
        par = par.replace("\n", " ").strip(" ")
        par = par.replace("  ", " ")
        l = textwrap.wrap(re.sub('<[^>]*>', '', par),
                          width=70, replace_whitespace=False)
        print("\n".join(l), file=sys.stderr)
        print(file=sys.stderr)

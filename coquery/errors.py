# -*- coding: utf-8 -*-
"""
FILENAME: errors.py -- part of Coquery corpus query tool

This module defines the exception classes used in Coquery.

LICENSE:
Copyright (c) 2015 Gero Kunter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import print_function

import sys
import traceback
import os
import logging

import __init__



class GenericException(Exception):
    def __init__(self, par=""):
        self.par = par

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
    
class UnknownArgumentError(NoTraceException):
    error_message = "Unknown argument given to script."

class QueryModeError(NoTraceException):
    error_message = "Query mode {mode} not supported by corpus {corpus}."
    def __init__(self, Corpus, Mode):
        self.error_message = self.error_message.format(mode = Mode, corpus = Corpus)
        self.par = ""

class IllegalArgumentError(NoTraceException):
    error_message = "Illegal argument value"
    def __init__(self, par):
        self.par = par

class TokenPartOfSpeechError(NoTraceException):
    error_message = "Illegal part of speech specification"

class TokenParseError(NoTraceException):
    error_message = "Illegal token format"

class TokenUnsupportedTranscriptError(NoTraceException):
    error_message = "Lexicon does not support phonetic transcriptions"

class TextfilterError(NoTraceException):
    error_message = "Illegal text filter specification"

class CorpusUnavailableQueryTypeError(GenericException):
    error_message = "Query type %s not available for corpus %s"
    def __init__(self, Corpus, Type):
        self.error_message = self.error_message % (Type, Corpus)
        self.par = ""

class CorpusUnsupportedFunctionError(GenericException):
    error_message = "Function not yet supported by corpus."

class LexiconUnsupportedFunctionError(GenericException):
    error_message = "Function not yet supported by lexicon."

class LexiconUnknownPartOfSpeechTag(GenericException):
    error_message = "Part-of-speech tag not in current lexicon"
    def __init__(self, par):
        self.par = par

class LexiconUnprovidedError(NoTraceException):
    error_message = "Lexicon feature not provided by current lexicon"
    #def __init__(self, S):
        #self.par = S

class CorpusUnsupportedError(NoTraceException):
    error_message = "Corpus not supported"

class SQLInitializationError(GenericException):
    error_message = "SQL initialization error"

class SQLOperationalError(GenericException):
    error_message = "SQL operational error"

class SQLProgrammingError(GenericException):
    error_message = "SQL programming error"

class SQLNoConnectorError(GenericException):
    error_message = "Could not load a MySQL connector module for your Python configuration.\nPlease install such a module on your system.\nCurrently supported are: MySQLdb, pymysql."

def print_exception(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    error_string = ""
    if not isinstance(e, NoTraceException):
        Trace = traceback.extract_tb(exc_tb)
        error_string += "TRACE: "
        Indent = ""
        for FileName, LineNo, FunctionName, Text in Trace:
            ModuleName = os.path.split(FileName) [1]
            error_string += "%s %s, line %s: %s\n" % (Indent, ModuleName, LineNo, FunctionName)
            if not Indent:
                Indent = "       "
            Indent += "  "
        if Text:
            error_string += "%s> %s\n" % (Indent[:-1], Text)
    error_string += "ERROR: %s\n" % (e)
    #logger.error(error_string)
    print(error_string, file=sys.stderr)
    
logger = logging.getLogger(__init__.NAME)

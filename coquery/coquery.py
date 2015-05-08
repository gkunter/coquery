#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FILENAME: coquery.py -- main module of Coquery corpus query tool

This is the main module of Coquery.

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

import sys
sys.path.append("/opt/coquery")


import logging
import logging.handlers

import options
from session import *
from errors import *

import cProfile

import time
import __init__

def set_logger():
    logger = logging.getLogger(__init__.NAME)
    logger.setLevel (logging.INFO)
    log_file_name = "/home/kunter/coquery.log"
    file_handler = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=1024*1024, backupCount=10)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
    logger.addHandler(file_handler)
    return logger

def main():
    logger = set_logger()
    start_time = time.time()
    logger.info("--- Started (%s %s) ---" % (__init__.NAME, __init__.__version__))

    try:
        options.process_options()
    except Exception as e:
        print_exception(e)
        sys.exit(1)
    
    if options.cfg.verbose:
        logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
        logger.addHandler(stream_handler)

    try:
        if options.cfg.MODE == QUERY_MODE_STATISTICS:
            Session = StatisticsSession()
        else:
            if options.cfg.input_path:
                Session = SessionInputFile()
            elif options.cfg.query_list:
                Session = SessionCommandLine()
            else:
                Session = SessionStdIn()

        if options.cfg.profile:
            cProfile.runctx("Session.run_queries()", globals(), locals())
        else:
            Session.run_queries()
    except KeyboardInterrupt:
        logger.error("Execution interrupted, exiting.")
    except Exception as e:
        print_exception(e)
    logger.info("--- Done (after %.3f seconds) ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
    
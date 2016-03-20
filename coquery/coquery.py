#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the main module of Coquery, a free corpus query tool.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
version 3 along with this program.  If not, see
<http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import sys
import os.path
import time

import logging
import logging.handlers

from .errors import *
from . import options
from .defines import *
from .unicode import utf8

def set_logger(log_file_path):
    logger = logging.getLogger(NAME)
    logger.setLevel(logging.INFO)
    file_handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=10)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
    logger.addHandler(file_handler)
    logging.captureWarnings(True)
    return logger

def check_system():
    if options.missing_modules:
        if options._use_qt:
            from .gui.pyqt_compat import QtGui
            app = QtGui.QApplication(sys.argv)
            QtGui.QMessageBox.critical(None,
                "Missing dependencies – Coquery",
                msg_missing_modules.format("<br/>".join([str(x) for x in options.missing_modules])))
            print_exception(msg_missing_modules.format(", ".join(options.missing_modules)))
        else:
            print_exception(msg_missing_modules.format(", ".join(options.missing_modules)))
        sys.exit(1)

def main():
    check_system()
    options.process_options()
    coquery_home = options.get_home_dir()
    logger = set_logger(os.path.join(coquery_home, "coquery.log"))

    #if options._use_qt:
        #sys.path.append(os.path.join(sys.path[0], "gui"))

    start_time = time.time()
    logger.info("--- Started (%s %s) ---" % (NAME, VERSION))
    logger.info("{}".format(sys.version))
    try:
        options.cfg.coquery_home = coquery_home
        options.cfg.log_file_path = os.path.join(coquery_home, "coquery.log")

        # Check if a valid corpus was specified, but only if no GUI is
        # requested (the GUI will handle corpus selection later):
        if not (options.cfg.gui):
            if not options.cfg.current_resources:
                raise NoCorpusError

            if not options.cfg.corpus:
                raise NoCorpusSpecifiedError

            options.cfg.corpus = utf8(options.cfg.corpus)
            if options.cfg.corpus not in options.cfg.current_resources:
                raise CorpusUnavailableError(options.cfg.corpus)

    except Exception as e:
        print_exception(e)
        sys.exit(1)

    # In verbose mode, debugging messages will be printed as well. Also, all
    # logging messages will be printed to the console, and not only to the
    # log file.
    if options.cfg.verbose:
        logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
        logger.addHandler(stream_handler)

    if options.cfg.comment:
        logger.info(options.cfg.comment)

    # Run the Application GUI?
    if options.cfg.gui and options._use_qt:
        from .gui.pyqt_compat import QtGui, QtCore
        from .gui.app import CoqueryApp
        from .gui.app import GuiHandler

        options.cfg.gui_logger = GuiHandler()
        options.cfg.gui_logger.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
        logger.addHandler(options.cfg.gui_logger)

        if sys.platform == "darwin":
            QtGui.QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")
            QtGui.QFont.insertSubstitution(".Helvetica Neue DeskInterface", "Helvetica Neue")
            QtGui.QFont.insertSubstitution(".SF NS Text", "Helvetica Neue")
        options.cfg.app = QtGui.QApplication(sys.argv)

        Coq = CoqueryApp()
        options.cfg.gui = Coq
        options.cfg.gui_logger.setGui(Coq)
        Coq.show()
        Coq.setGUIDefaults()

        options.cfg.icon = Coq.get_icon("coquerel_icon.png", small_n_flat=False)
        Coq.setWindowIcon(options.cfg.icon)
        if options.cfg.profile:
            import cProfile
            cProfile.runctx("options.cfg.app.exec_()", globals(), locals())
        else:
            options.cfg.app.exec_()
        logger.info("--- Finished program (after %.3f seconds) ---" % (time.time() - start_time))

    # Otherwise, run program as a command-line tool:
    else:
        options.set_current_server(options.cfg.current_server)
        from . import session
        # Choose the appropriate Session type instance:
        if options.cfg.MODE == QUERY_MODE_STATISTICS:
            Session = session.StatisticsSession()
        else:
            if options.cfg.input_path:
                Session = session.SessionInputFile()
            elif options.cfg.query_list:
                Session = session.SessionCommandLine()
            else:
                Session = session.SessionStdIn()

        # Catch keyboard interruptions:
        try:
            # Check if profiling is requested. If so, wrap the profiler
            # around the query execution:
            if options.cfg.profile:
                import cProfile
                cProfile.runctx("Session.run_queries()", globals(), locals())
            # Otherwise, run queries normally:
            else:
                Session.run_queries()
        except KeyboardInterrupt:
            logger.error("Execution interrupted, exiting.")
        logger.info("--- Done (after %.3f seconds) ---" % (time.time() - start_time))

if __name__ == "__main__":
    for x in sys.argv[1:]:
        if x == "--benchmark":
            import timeit
            benchmark_time = timeit.timeit("main()", setup="from __main__ import main", number=10)
            print("Execution time (25 times): {}".format(benchmark_time))
            sys.exit(0)
    main()

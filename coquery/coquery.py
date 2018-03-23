#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the main module of Coquery, a free corpus query tool.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

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

import os
import sys
import time
import traceback

import logging.handlers

from . import NAME, __version__
from . import general
from .errors import (print_exception,
                     NoCorpusError, NoCorpusSpecifiedError,
                     CorpusUnavailableError)
from . import options
from .defines import (msg_missing_modules, msg_options_error,
                      msg_error_in_config,
                      QUERY_MODE_STATISTICS)
from .unicode import utf8

from .gui.classes import CoqApplication


def set_logger(log_file_path):
    fstr = "%(asctime)s %(levelname)-8s %(message)s"
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format=fstr)

    logger = logging.getLogger(NAME)
    logging.captureWarnings(True)

    return logger


def check_system():
    if options.missing_modules:
        missing_str = msg_missing_modules.format(
            "<br/>".join(options.missing_modules))
        if options.use_qt:
            from .gui.pyqt_compat import QtWidgets
            app = QtWidgets.QApplication(sys.argv)
            QtWidgets.QMessageBox.critical(
                None, "Missing dependencies – Coquery", missing_str)
        print_exception(missing_str.replace("<br/>", ", "))
        sys.exit(1)


def main():
    coquery_home = general.get_home_dir()
    logger = set_logger(os.path.join(coquery_home, "coquery.log"))

    check_system()
    read_config_file = True
    configuration_error = None
    while True:
        try:
            options.process_options(read_config_file)
        except Exception as e:
            l = []
            for i, line in enumerate(
                    traceback.format_exception(*sys.exc_info())):
                l.append("{}{}".format("&nbsp;&nbsp;" * i, line))
            s = ("".join(l).replace("\n", "<br>"))
            configuration_error = s
            if not read_config_file:
                # Fatal configuration error that is not caused by a faulty
                # configuration file; break the while loop so that the
                # user can react
                read_config_file = True
                break
            read_config_file = False
        else:
            break

    start_time = time.time()
    logger.info("--- Started ({}, {}) ---".format(NAME, __version__))
    logger.info("{}".format(sys.version))
    try:
        options.cfg.coquery_home = coquery_home
        options.cfg.log_file_path = os.path.join(coquery_home, "coquery.log")

        # Check if a valid corpus was specified, but only if no GUI is
        # requested (the GUI will handle corpus selection later):
        if not (options.cfg.gui):
            if not options.cfg.current_connection.resources():
                raise NoCorpusError

            if not options.cfg.corpus:
                raise NoCorpusSpecifiedError

            options.cfg.corpus = utf8(options.cfg.corpus)
            if (options.cfg.corpus not in
                    options.cfg.current_connection.resources()):
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
        frm = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
        stream_handler.setFormatter(frm)
        logger.addHandler(stream_handler)

    if options.cfg.comment:
        logger.info(options.cfg.comment)

    options.set_current_server(options.cfg.current_connection.name)

    # Run the Application GUI?
    if options.cfg.gui and options.use_qt:
        from .gui.pyqt_compat import (
            QtWidgets, QtGui, close_toplevel_widgets, QtCore)

        options.cfg.app = CoqApplication(sys.argv)
        translator = QtCore.QTranslator()
        translator.load("coquery_" + QtCore.QLocale.system().name())
        options.cfg.app.installTranslator(translator)

        if configuration_error:
            if read_config_file:
                s = msg_options_error.format(configuration_error)
            else:
                s = msg_error_in_config.format(configuration_error)
            if read_config_file:
                QtWidgets.QMessageBox.critical(None,
                                               "Options error – Coquery", s)
                sys.exit(1)
            else:
                response = QtWidgets.QMessageBox.critical(
                    None,
                    "Error in configuration file – Coquery", s,
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                print(response)
                sys.exit(1)
        from .gui.app import CoqMainWindow
        from .gui.app import GuiHandler

        options.cfg.gui_logger = GuiHandler()
        frm = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
        options.cfg.gui_logger.setFormatter(frm)
        logger.addHandler(options.cfg.gui_logger)

        if sys.platform == "darwin":
            for old, new in (
                    (".Lucida Grande UI", "Lucida Grande"),
                    (".Helvetica Neue DeskInterface", "Helvetica Neue"),
                    (".SF NS Text", "Helvetica Neue")):
                QtGui.QFont.insertSubstitution(old, new)

        from . import session
        session = session.SessionCommandLine()

        Coq = CoqMainWindow(session)
        options.cfg.gui = Coq
        options.cfg.gui_logger.setGui(Coq)
        Coq.setGUIDefaults()

        options.cfg.icon = Coq.get_icon("coquerel_icon.png",
                                        small_n_flat=False)
        Coq.setWindowIcon(options.cfg.icon)
        if options.cfg.profile:
            import cProfile
            cProfile.runctx("options.cfg.app.exec_()", globals(), locals())
        else:
            options.cfg.app.exec_()
        close_toplevel_widgets()
        logger.info("--- Finished program (after {:.3} seconds) ---".format(
            time.time() - start_time))

    # Otherwise, run program as a command-line tool:
    else:
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
        logger.info("--- Done (after {.3f} seconds) ---".format(
            time.time() - start_time))

    if options.cfg.use_cache:
        options.cfg.query_cache.save()


if __name__ == "__main__":
    main()

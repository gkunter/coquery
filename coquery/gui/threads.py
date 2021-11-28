# -*- coding: utf-8 -*-
"""
threads.py is part of Coquery.

Copyright (c) 2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys

from coquery import options
from coquery import general
from .pyqt_compat import QtCore


class CoqWorker(QtCore.QObject):
    """
    The CoqWorker class uses a thread to work a specified activity.
    It raises the signal `started` when it starts working on the activity, and
    it raises the signal `finished` when the activity is completed. If an
    exception occurs during the work on the activity, the signal
    `exceptionRaised` is raised.
    """

    started = QtCore.Signal()
    finished = QtCore.Signal()
    exceptionRaised = QtCore.Signal(Exception)

    def __init__(self, activity, *args, **kwargs):
        super(CoqWorker, self).__init__(parent=None)
        self._activity = activity
        self._thread = QtCore.QThread()
        self._args = args
        self._kwargs = kwargs
        self.moveToThread(self._thread)
        self._thread.started.connect(self._perform_activity)

    @QtCore.Slot()
    def _perform_activity(self):
        try:
            self._activity(*self._args, **self._kwargs)
        except Exception as e:
            self.exceptionRaised.emit(e)
        self._thread.quit()
        self.finished.emit()

    def start(self):
        self._thread.start()
        self.started.emit()


class CoqThread(QtCore.QThread):
    taskStarted = QtCore.Signal()
    taskFinished = QtCore.Signal()
    taskException = QtCore.Signal(Exception)
    taskAbort = QtCore.Signal()

    def __init__(self, FUN, parent=None, *args, **kwargs):
        super(CoqThread, self).__init__(parent)
        self.FUN = FUN
        self.exiting = False
        self.args = args
        self.kwargs = kwargs
        self.quitted = False

    def __del__(self):
        self.exiting = True
        try:
            self.wait()
        except RuntimeError:
            pass

    def setInterrupt(self, fun):
        self.INTERRUPT_FUN = fun

    def quit(self):
        self.quitted = True
        if hasattr(self, "INTERRUPT_FUN"):
            self.INTERRUPT_FUN()
        super(CoqThread, self).quit()

    def run(self):
        self.taskStarted.emit()
        self.exiting = False
        self.quitted = False
        result = None
        try:
            if options.cfg.profile:
                import cProfile
                profiler = cProfile.Profile()
                try:
                    result = profiler.runcall(self.FUN,
                                              *self.args, **self.kwargs)
                finally:
                    profiler.dump_stats(os.path.join(
                        general.get_home_dir(),
                        "thread{}.profile".format(hex(id(self)))))
            else:
                result = self.FUN(*self.args, **self.kwargs)
        except Exception as e:
            if self.parent:
                self.parent().exc_info = sys.exc_info()
                self.parent().exception = e
            self.taskException.emit(e)
            print("CoqThread.run():", e)
        self.taskFinished.emit()
        return result

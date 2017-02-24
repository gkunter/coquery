# -*- coding: utf-8 -*-
"""
capturer.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import sys
from ast import literal_eval

# ensure Python 2.7 compatibility
try:
    import StringIO as io
except ImportError:
    import io as io


class Capturer(object):
    """
    Define the Capturer iterator class which allows capture of the standard
    streams stdout and stderr.

    Capturer is best used as a content manager.
    """

    def __init__(self, stdout=None, stderr=None):
        if ((not stdout and not stderr) or
                (stdout and stderr)):
            raise ValueError("Provide either 'stdout=True' or 'stderr=True'")
        self._capture_stdout = stdout
        self._catch = io.StringIO()

    def __iter__(self):
        self._index = 0
        try:
            content = literal_eval(self._catch.getvalue()).decode("utf-8")
        except (ValueError, AttributeError, UnicodeDecodeError, SyntaxError):
            content = self._catch.getvalue()
        self._content = [x for x in content.split("\n") if x]
        return self

    def next(self):
        """
        Call self.__next__().

        Needed by Python 2.7.
        """
        return self.__next__()

    def __next__(self):
        try:
            result = self._content[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        return result

    def __enter__(self):
        if self._capture_stdout:
            sys.stdout.flush()
            self._old = sys.stdout
            sys.stdout = self._catch
        else:
            sys.stderr.flush()
            self._old = sys.stderr
            sys.stderr = self._catch

    def __exit__(self, exc_type, exc_value, traceback):
        self._catch.flush()
        if self._capture_stdout:
            sys.stdout = self._old
        else:
            sys.stderr = self._old

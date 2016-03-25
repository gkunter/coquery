# -*- coding: utf-8 -*-

""" 
unicode.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import sys

if sys.version_info < (3, 0):
    def utf8(s, errors="strict"):
        """
        Return the string s as a unicode string (Python 2.7)

        Parameters
        ----------
        s : string or an object
            either a string or an object that will be coerced to a string 
            by calling its __str__() method.
            
        Returns
        -------
        uni : string
            the unicode string equivalent of s
        """
        if isinstance(s, str):
            return s.decode("utf-8", errors=errors)
        elif isinstance(s, unicode):
            # do not attemt a conversion if string is already unicode
            return s
        else:
            # call __str__() for non-string object, and convert the 
            # result to unicode if needed:
            s_str = s.__str__()
            if isinstance(s_str, unicode):
                return s_str
            else:
                return s_str.decode("utf-8", errors=errors)
else:
    def utf8(s, errors="strict"):
        """
        Return the string s as a unicode string (Python 3.x)

        Parameters
        ----------
        s : string or an object
            either a string or an object that will be coerced to a string 
            by calling its __str__() method.
            
        Returns
        -------
        uni : string
            the unicode string equivalent of s
        """
        if isinstance(s, str):
            return s
        elif hasattr(s, "decode"):
            # this is called e.g. by byte strings:
            return s.decode("utf-8", errors=errors)
        else:
            return str(s)

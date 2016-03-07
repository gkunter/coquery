# -*- coding: utf-8 -*-

""" 
unicode.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

def _utf8(s):
    """
    Return the string s as a unicode string.
    
    This method tries to faciltiate handling of unicode strings in Python 
    2.7 and 3.x, which is plainly horrible in the old Python version. 
    """
    try:
        s = s.__str__().decode("utf-8")
    except UnicodeEncodeError:
        # This exception is raised by Python 2.7 if s is already a unicode 
        # string. In this case, do nothing.
        pass
    except AttributeError:
        # This exception is raised by Python 3.x, because all strings are
        # unicode by default, and therefore do not need the decode() method.
        pass
    
    assert type(s) == type(u""), "utf8: type of {} is {}, not unicode".format(s, type(s))
    
    return s

def utf8(x):
    """
    Convert the passed argument to unicode.
    
    Parameters
    ----------
    x : string or list of strings
        A single string or a list of strings that will be converted to 
        unicode
        
    Returns
    -------
    c : string or list of strings
        Either a unicode string (if x was also a string) or a list of strings 
        (if x was a list)
    """
    
    if isinstance(x, list):
        return [_utf8(s) for s in x]
    else:
        return _utf8(x)
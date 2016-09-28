# -*- coding: utf-8 -*-

""" 
mockmodule.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import sys

# Mock module requirements:
class mock_module(object):
    try:
        __spec__ = __spec__
    except NameError:
        pass

def setup_module(s):
    sys.modules[s] = mock_module

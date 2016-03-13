# -*- coding: utf-8 -*-

"""
__init__.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os

#base_path, _ = os.path.split(os.path.realpath(__file__))
#if base_path and base_path not in sys.path:
    #sys.path.append(base_path)

#for x in sys.path:
    #print("x\t{}".format(x))

#import coquery.corpus1

from .gui import *
from .visualizer import *
from .installer import *

__version__ = "0.9"
NAME = "Coquery"
DATE = "2016"


# -*- coding: utf-8 -*-
"""
link.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals

import hashlib

class Link(object):
    """
    The Link class is used to link a table from one corpus to another corpus.
    """
    
    def __init__(self, res_from, rc_from, res_to, rc_to, join="LEFT JOIN", case=False):
        """
        Parameters
        ----------
        res_from : str
            The name of the resource from which the link starts
        rc_from : str
            The resource feature from which the link starts
        res_to : str 
            The name of the resource where the link ends
        rc_to : str
            The resource feature where the link ends
        join : str
            The SQL join type
        case : bool 
            Determine whether the the join will be case sensitive
        """
        self.res_from = res_from
        self.rc_from = rc_from
        self.res_to = res_to
        self.rc_to = rc_to
        self.join_type = join
        self.case = case
        
    def get_hash(self):
        l = []
        for x in sorted(dir(self)):
            if not x.startswith("_") and not hasattr(getattr(self, x), "__call__"):
                l.append(str(getattr(self, x)))
        return hashlib.md5(u"".join(l).encode()).hexdigest()
        
    def __repr__(self):
        return "Link(res_from='{}', rc_from='{}', res_to='{}', rc_to='{}', join='{}', case={})".format(
            self.res_from, self.rc_from, self.res_to, self.rc_to, self.join_type, self.case)

def get_by_hash(link_list, hash):
    for link in link_list:
        if link.get_hash() == hash:
            return link

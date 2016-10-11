# -*- coding: utf-8 -*-
"""
links.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals

import hashlib

from .defines import *

class Link(object):
    """
    The Link class is used to link a table from one corpus to another corpus.
    """
    
    def __init__(self, res_from, rc_from, res_to, rc_to, join="LEFT JOIN", case=False,
                 one_to_many=False):
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
        one_to_many : bool
            True if all entries in the linked table are returned, or False if 
            only the first entry is returned
        case : bool 
            Determine whether the the join will be case sensitive
        """
        self.res_from = res_from
        self.rc_from = rc_from
        self.res_to = res_to
        self.rc_to = rc_to
        self.join_type = join
        self.case = case
        self.one_to_many = one_to_many
        
    def get_hash(self):
        l = []
        for x in sorted(dir(self)):
            if not x.startswith("_") and not hasattr(getattr(self, x), "__call__"):
                l.append(str(getattr(self, x)))
        return hashlib.md5(u"".join(l).encode()).hexdigest()
        
    def __repr__(self):
        return "Link(res_from='{}', rc_from='{}', res_to='{}', rc_to='{}', join='{}', case={})".format(
            self.res_from, self.rc_from, self.res_to, self.rc_to, self.join_type, self.case)

def get_link_by_hash(link_list, hash):
    for link in link_list:
        if link.get_hash() == hash:
            return link

def get_by_hash(hashed, link_list=None):
    """
    Return the link and the linked resource for the hash.
    
    Parameters
    ----------
    hashed : str 
        A hash string that has been produced by the get_hash() method.
    
    link_list : list of Link objects
        A list of links that is used to lookup the hash. If not provided,
        the link list for the current server and resource is used.
    
    Returns
    -------
    tup : tuple
        A tuple with the associated link as the first and the linked resource
        as the second element.
    """
    from . import options
    if not link_list:
        link_list = options.cfg.table_links[options.cfg.current_server]
    
    link = get_link_by_hash(link_list, hashed)
    res = options.get_resource(link.res_to)[0]
    return (link, res)
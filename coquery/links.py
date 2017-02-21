# -*- coding: utf-8 -*-
"""
links.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals
import re

from .general import CoqObject


class Link(CoqObject):
    """
    The Link class is used to link a table from one corpus to another corpus.
    """

    def __init__(self, res_from, rc_from, res_to, rc_to, join="LEFT JOIN",
                 case=False, one_to_many=False):
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
            True if all entries in the linked table are returned, or False
            if only the first entry is returned
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

    def __repr__(self):
        S = ("Link(res_from='{}', rc_from='{}', res_to='{}', rc_to='{}', "
             "join='{}', case={})")
        return S.format(
            self.res_from, self.rc_from, self.res_to, self.rc_to,
            self.join_type, self.case)


def parse_link_text(s):
    """
    Parse the string, and return a Link instance that matches the string.

    This function is used by the option file parser to restore saved links.

    The string is assumed to be produced by Link.__repr__. No attempt is made
    to parse other strings (e.g. those with different argument orders).

    If the string cannot be parsed for whatever reason, the function rises a
    ValueError.

    This function asserts that the value of __repr__ from the created Link
    object is the same as 's'. Otherwise, it raises an AssertionError.
    """
    try:
        regex = re.match(r"^Link\((.*)\)$", s)
        arguments = [x.split("=") for x in regex.group(1).split(", ")]
        kwargs = dict([(key, val.strip("'")) for key, val in arguments])
        kwargs["case"] = kwargs["case"] == "True"
        link = Link(**kwargs)
    except Exception as e:
        raise ValueError(str(e))
    assert link.__repr__() == s, link.__repr__()
    return link


def get_link_by_hash(link_list, hash_val):
    """
    Look up the link that matches the hash value.
    """
    for link in link_list:
        if link.get_hash() == hash_val:
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
    if not link:
        raise ValueError(hashed, link_list)
    res = options.get_resource(link.res_to)[0]
    return (link, res)

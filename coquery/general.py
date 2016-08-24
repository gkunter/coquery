# -*- coding: utf-8 -*-
"""
general.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import hashlib

from .unicode import utf8

contraction = ["n't", "'s", "'ve", "'m", "'d", "'ll", "'em", "'t"]
punct = '!\'),-./:;?^_`}’”]'

def collapse_words(word_list):
    """ Concatenate the words in the word list, taking clitics, punctuation
    and some other stop words into account."""
    def is_tag(s):
        # there are some tags that should still be preceded by spaces. In 
        # paricular those that are normally used for typesetting, including
        # <span>, but excluding <sup> and <sub>, because these are frequently
        # used in formula:
        
        if s.startswith("<span") or s.startswith("</span"):
            return False
        if s in set(["</b>", "<b>", "</i>", "<i>", "</u>", "<u>", "</s>", "<s>", "<em>", "</em>"]):
            return False
        return s.startswith("<") and s.endswith(">") and len(s) > 2

    token_list = []
    context_list = [x.strip() if hasattr(x, "strip") else x for x in word_list]
    open_quote = {}
    open_quote ['"'] = False
    open_quote ["'"] = False
    open_quote["``"] = False
    last_token = ""
    for i, current_token in enumerate(context_list):
        if current_token and not (isinstance(current_token, float) and np.isnan(current_token)):
            if '""""' in current_token:
                current_token = '"'
        
            # stupid list of exceptions in which the current_token should NOT
            # be preceded by a space:
            no_space = False
            if all([x in punct for x in current_token]):
                no_space = True        
            if current_token in contraction:
                no_space = True            
            if last_token in '({[‘“':
                no_space = True            
            if is_tag(last_token):
                no_space = True        
            if is_tag(current_token):
                no_space = True
            if last_token.endswith("/"):
                no_space = True

            if current_token == "``":
                no_space = False
                open_quote["``"] = True
            if current_token == "''":
                open_quote["``"] = False
                no_space = True
            if last_token == "``":
                no_space = True

            if not no_space:
                token_list.append(" ")
            
            token_list.append(current_token)
            last_token = current_token
    return utf8("").join(token_list)

class CoqObject(object):
    """
    This class is a subclass of the default Python ``object`` class. It adds 
    the method ``get_hash()``, which returns a hash based on the current 
    instance attributes.
    """
    
    def get_hash(self):
        l = []
        for x in sorted(dir(self)):
            if not x.startswith("_") and not hasattr(getattr(self, x), "__call__"):
                attr = getattr(self, x)
                # special handling of containers:
                if isinstance(attr, (set, dict, list, tuple)):
                    l.append(str([x.get_hash() if isinstance(x, CoqObject) else str(x) for x in attr]))
                else:
                    l.append(str(attr))
        return hashlib.md5(u"".join(l).encode()).hexdigest()
    
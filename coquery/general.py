# -*- coding: utf-8 -*-
"""
general.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division

import hashlib
import sys
import platform
import os

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

def get_home_dir(create=True):
    """
    Return the path to the Coquery home directory. Also, create all required
    directories.
    
    The coquery_home path points to the directory where Coquery stores (and 
    looks for) the following files:
    
    $COQ_HOME/coquery.cfg               configuration file
    $COQ_HOME/coquery.log               log files
    $COQ_HOME/installer/                additional corpus installers
    $COQ_HOME/connections/$MYSQL_CONFIG/corpora
                                        installed corpus modules
    $COQ_HOME/connections/$MYSQL_CONFIG/adhoc
                                        adhoc installer modules
    $COQ_HOME/connections/$MYSQL_CONFIG/databases
                                        SQLite databases
    
    The location of $COQ_HOME depends on the operating system:
    
    Linux           either $XDG_CONFIG_HOME/Coquery or ~/.config/Coquery
    Windows         %APPDATA%/Coquery
    Mac OS X        ~/Library/Application Support/Coquery
    """

    if platform.system() == "Linux":
        try:
            basepath = os.environ["XDG_CONFIG_HOME"]
        except KeyError:
            basepath = os.path.expanduser("~/.config")
    elif platform.system() == "Windows":
        try:
            basepath = os.environ["APPDATA"]
        except KeyError:
            basepath = os.path.expanduser("~")
    elif platform.system() == "Darwin":
        basepath = os.path.expanduser("~/Library/Application Support")
        
    coquery_home = os.path.join(basepath, "Coquery")
    connections_path = os.path.join(coquery_home, "connections")
    custom_installer_path = os.path.join(coquery_home, "installer")
    
    if create:
        # create paths if they do not exist yet:
        for path in [coquery_home, custom_installer_path, connections_path]:
            if not os.path.exists(path):
                os.makedirs(path)

    return coquery_home


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

def get_visible_columns(df, manager, session, hidden=False):
    """
    Return a list with the column names that are currently visible.
    """
    if hidden:
        l = list(df.columns.values)
    else:
        l = [x for x in list(df.columns.values) if (
                not x.startswith("coquery_invisible") and 
                not x in manager.hidden_columns)]

    resource_order = session.Resource.get_preferred_output_order()
    for x in resource_order[::-1]:
        lex_list = [y for y in l if x in y]
        lex_list = sorted(lex_list)[::-1]
        for lex in lex_list:
            l.remove(lex)
            l.insert(0, lex)
    return l

try:
    from pympler import summary, muppy
    import psutil

    def summarize_memory():
        print("Virtual machine: {:.2f}Mb".format(psutil.Process().memory_info_ex().vms / (1024 * 1024)))
        summary.print_(summary.summarize(muppy.get_objects()), limit=1)

except Exception as e:
    def summarize_memory():
        print("summarize_memory: {}".format(lambda: str(e)))

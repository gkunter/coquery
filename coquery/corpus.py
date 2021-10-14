# -*- coding: utf-8 -*-
"""
corpus.py is part of Coquery.

Copyright (c) 2016-2021 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import warnings
from collections import defaultdict
import re
import logging
import math
import pandas as pd
import numpy as np
import os
import tempfile
import zipfile
import json
from csv import QUOTE_NONNUMERIC
from datetime import datetime

from .errors import UnsupportedQueryItemError
from .defines import (
    QUERY_ITEM_WORD, QUERY_ITEM_LEMMA, QUERY_ITEM_POS,
    QUERY_ITEM_TRANSCRIPT, QUERY_ITEM_GLOSS, QUERY_ITEM_ID,
    SQL_MYSQL, SQL_SQLITE,
    CONTEXT_NONE,
    PREFERRED_ORDER)

from .general import collapse_words, CoqObject, html_escape, Print
from . import tokens
from . import options
from .links import get_by_hash


class LexiconClass():
    pass


class BaseResource(CoqObject):
    """
    """
    # add internal table that can be used to access frequency information:
    coquery_query_string = "Query string"
    coquery_query_token = "Query item"

    special_table_list = ["coquery", "tag"]
    render_token_style = "background: lightyellow"
    audio_features = []
    image_features = []
    video_features = []
    lexical_features = []
    exposed_ids = []

    def __init__(self):
        super(BaseResource, self).__init__()
        self._joined_tables = []
        self._table_list = []

    @staticmethod
    def get_language():
        """
        Return the corpus language as a string.

        Defaults to "en" (English).
        """
        return "en"

    @classmethod
    def format_resource_feature(cls, rc_feature, N):
        """
        Return a list of formatted feature labels as they occur in the query
        table as headers.

        All labels start with the prefix 'coq_' and end with a number. For
        lexicon features, the numbers range from 1 to N. For other features,
        the number is always 1.

        Special resource features, i.e. those that belong to one of the tables
        in the 'special_table_list' class attribute, are returned as they are.

        Parameters
        ----------
        rc_feature : str
            The name of the resource feature
        N : int
            The maximum number of query items

        Returns:
        --------
        l : list
            A list of header labels.
        """
        # special case for "coquery_query_token", which receives numbers like
        # a query item resource:
        if rc_feature == "coquery_query_token":
            return ["coquery_query_token_{}".format(x + 1) for x in range(N)]

        # handle resources from one of the special tables:
        if rc_feature.startswith(tuple(cls.special_table_list)):
            return [rc_feature]

        # handle external links by delegating the formatting to the external
        # resource:
        hashed, table, feature = cls.split_resource_feature(rc_feature)
        if hashed is not None:
            link, res = get_by_hash(hashed)
            l = res.format_resource_feature("{}_{}".format(table, feature), N)
            return ["db_{}_{}".format(res.db_name, x) for x in l]

        # handle lexicon features:
        lexicon_features = [x for x, _ in cls.get_lexicon_features()]
        if rc_feature in lexicon_features or cls.is_tokenized(rc_feature):
            return ["coq_{}_{}".format(rc_feature, x+1) for x in range(N)]
        # handle remaining features
        else:
            return ["coq_{}_1".format(rc_feature)]

    @classmethod
    def split_resource_feature(cls, rc_feature):
        """
        Split a resource feature into a tuple containing the prefix, the
        table name, and the resource feature display name.

        Parameters:
        -----------
        rc_feature : str
            The name of the resource feature

        Returns:
        --------
        tup : tuple
            A tuple consisting of a boolean specifying the hash of the link
            (or None), the resource table name, and the feature name
        """
        s = rc_feature
        if "." in s:
            hashed, _, s = s.partition(".")
        else:
            hashed = None
        table, _, feature = s.partition("_")
        if not table or not feature:
            raise ValueError("either no table or no feature: '{}'".format(rc_feature))

        return (hashed, table, feature)

    @classmethod
    def get_preferred_output_order(cls):
        all_features = cls.get_resource_features()
        order = []
        for rc_feature in list(all_features):
            if rc_feature in PREFERRED_ORDER:
                for i, ordered_feature in enumerate(order):
                    if PREFERRED_ORDER.index(ordered_feature) > PREFERRED_ORDER.index(rc_feature):
                        order.insert(i, rc_feature)
                        break
                else:
                    order.append(rc_feature)
                all_features.remove(rc_feature)

        # make sure that if there is timing information, the ending time
        # occurs after the start time by default (fixes Issue #177):
        for i, rc_feature in enumerate(order):
            _, tab, feat = cls.split_resource_feature(rc_feature)
            if feat == "starttime":
                j = order.index("{}_starttime".format(tab))
                if j < i:
                    order[j] = "{}_starttime".format(tab)
                    order[i] = "{}_endtime".format(tab)

        for i, rc_feature in enumerate(all_features):
            _, tab, feat = cls.split_resource_feature(rc_feature)
            if feat == "starttime":
                j = all_features.index("{}_endtime".format(tab))
                if j < i:
                    all_features[j] = "{}_starttime".format(tab)
                    all_features[i] = "{}_endtime".format(tab)

        return order + all_features

    @classmethod
    def get_resource_features(cls):
        """
        Return a list of all resource feature names.

        A resource feature is a class attribute that either contains the
        display name of a resource table or of a resource table variable.
        Resource table features take the form TABLENAME_table, where
        TABLENAME is the resource name of the table. Resource features
        take the form TABLENAME_COLUMNNAME, where COLUMNNAME is the
        resource name of the column.

        Returns
        -------
        l : list
            List of strings containing the resource feature names
        """
        # create a list with all split resources:
        split_features = [cls.split_resource_feature(x) for x in dir(cls)
                          if "_" in x and not x.startswith("_")]

        # create a list of table names from the resource features:
        tables = [table for _, table, feature in split_features
                  if feature == "table"]
        # add special tables:
        tables += cls.special_table_list

        # return the features that can be constructed from the feature name
        # and the table:
        return ["{}_{}".format(table, feature) for _, table, feature in split_features if table in tables]

    @classmethod
    def get_queryable_features(cls):
        """
        Return a list of the resource features that can be selected as
        features in a query.

        Features that represent binary data (audio, video, images) cannot be
        selected because the result table stores only numeric or string data.
        """
        l = cls.get_resource_features()
        # FIXME: this function might be usable to make some table IDs
        # exposable (see issue #174)
        return [x for x in l if
                x not in cls.audio_features and
                x not in cls.video_features and
                x not in cls.image_features]

    @classmethod
    def get_exposed_ids(cls):
        """
        Return the list of exposed IDs.

        The corpus ID is always an exposed ID. The IDs from other tables can
        be added by using add_exposed_id().
        """
        if "corpus_id" not in cls.exposed_ids:
            return cls.exposed_ids + ["corpus_id"]
        else:
            return cls.exposed_ids

    @classmethod
    def get_table_dict(cls):
        """ Return a dictionary with the table names specified in this
        resource as keys. The values of the dictionary are the table
        columns. """
        table_dict = defaultdict(set)
        for x in cls.get_resource_features():
            table, _, _ = x.partition("_")
            table_dict[table].add(x)
        try:
            table_dict.pop("tag")
        except (AttributeError, KeyError):
            pass
        return table_dict

    @classmethod
    def get_linked_tables(cls, table):
        table_dict = cls.get_table_dict()
        L = []
        for x in table_dict[table]:
            if cls.is_foreign_key(x):
                _, linked, _ = x.split("_")
                L.append(linked)
        return L

    @classmethod
    def get_table_tree(cls, table):
        """ Return a list of all table names that are linked to 'table',
        including 'table' itself. """
        L = [table]
        for x in cls.get_linked_tables(table):
            L = L + cls.get_table_tree(x)
        return L

    @classmethod
    def get_table_path(cls, start, end):
        """
        Return a list of table names that constitute a link chain from
        table 'start' to 'end', including these two tables. Return None if
        no path was found, i.e. if table 'end' is not linked to 'start'.

        Parameters
        ----------
        start : string
            A resource feature name, indicating the starting point of the
            search
        end : string
            A resource feature name, indicating the end point of the search

        Returns
        -------
        l : list or None
            A list of the resource table names that lead from resource
            feature 'start' to resource feature 'end'. The list contains
            start and end as the first and the last element if such a path
            exists. If no path exists, the method returns None.
        """
        table_dict = cls.get_table_dict()
        if "{}_id".format(end) in table_dict[start]:
            return [end]
        for rc_feature in table_dict[start]:
            try:
                from_table, to_table, id_spec = rc_feature.split("_")
            except ValueError:
                # this resource feature is not a linking feature
                continue
            else:
                # this is a linking feature, so descend into the
                # table:
                descend = cls.get_table_path(to_table, end)
                if descend:
                    return [start] + descend
        return None

    @classmethod
    def get_table_structure(cls, rc_table, rc_feature_list=None):
        """
        Return a table structure for the table 'rc_table'.

        The table structure is a dictionary with the following keys:
            'parent'        the resource name of the parent table
            'rc_table_name' the resource name of the table
            'children       a dictionary containing the table structures of
                            all child tables
            'rc_features'   a list of strings containing all resource
                            features in the table
            'rc_requested_features'  a list of strings containing those
                            resource features from argument 'rc_feature_list'
                            that are contained in this table
        """
        rc_feature_list = rc_feature_list or []

        D = {"parent": None}
        rc_tab = rc_table.split("_")[0]

        available_features = []
        requested_features = []
        children = []
        for rc_feature in cls.get_resource_features():
            if rc_feature.endswith("_{}_id".format(rc_tab)) and not rc_feature.startswith(rc_tab):
                D["parent"] = "{}_table".format(rc_feature.split("_")[0])
            if rc_feature.startswith("{}_".format(rc_tab)):
                if not rc_feature.endswith("_table"):
                    available_features.append(rc_feature)
                    if rc_feature in rc_feature_list:
                        requested_features.append(rc_feature)
                if cls.is_foreign_key(rc_feature):
                    children.append(
                        cls.get_table_structure(
                            "{}_table".format(rc_feature.split("_")[1]),
                            rc_feature_list))
        D["rc_table_name"] = rc_table
        D["children"] = children
        D["rc_features"] = sorted(available_features)
        D["rc_requested_features"] = sorted(requested_features)
        return D

    @staticmethod
    def is_foreign_key(s):
        return s.endswith("_id") and s.count("_") == 2

    @classmethod
    def get_feature_from_name(cls, name):
        """
        Get all resource features that match the given display name.

        Parameters
        ----------
        name : str
            The display name for which to search

        Returns
        -------
        l : list
            A list of strings, each representing a resource feature that has
            the same display name as 'name'.
        """
        return [x for x in cls.get_resource_features() if getattr(cls, x) == name]

    @classmethod
    def get_corpus_features(cls):
        """ Return a list of tuples. Each tuple consists of a resource
        variable name and the display name of that variable. Only those
        variables are returned that all resource variable names that are
        desendants of table 'corpus', but not of table 'word'. """
        table_dict = cls.get_table_dict()
        if "corpus" not in table_dict:
            return []
        lexicon_tables = cls.get_table_tree(getattr(cls, "lexicon_root_table", "word"))

        corpus_variables = []
        cls_lexical_features = getattr(cls, "lexical_features", [])
        for x in table_dict:
            if x not in lexicon_tables and x not in cls.special_table_list:
                for y in table_dict[x]:
                    if y not in cls_lexical_features:
                        if y == "corpus_id":
                            corpus_variables.append((y, cls.corpus_id))
                        elif not y.endswith("_id") and not y.startswith("{}_table".format(x)):
                            corpus_variables.append((y, getattr(cls, y)))
        return corpus_variables

    @classmethod
    def get_corpus_table_features(cls):
        """
        Return a list of tuples.

        The first element of each tuple is the resource feature name, and the
        second element is the display name.
        """
        return [(x, getattr(cls, x)) for x in dir(cls)
                if x.startswith("corpus_") and not
                x.endswith(("_table", "_columns"))]

    @classmethod
    def get_lexicon_features(cls):
        """
        Return a list of tuples. Each tuple consists of a resource variable
        name and the display name of that variable. Only those variables are
        returned that all resource variable names that are desendants of
        table 'word'.
        """
        table_dict = cls.get_table_dict()
        lexicon_tables = cls.get_table_tree(
            getattr(cls, "lexicon_root_table", "word"))
        lexicon_variables = []
        l = []
        for x in table_dict:
            if x in lexicon_tables and x not in cls.special_table_list:
                for y in table_dict[x]:
                    if (not y.endswith("_id") and
                            not y.startswith("{}_table".format(x))):
                        lexicon_variables.append((y, getattr(cls, y)))
                        l.append(y)

        for x in getattr(cls, "lexical_features", []):
            if x not in l:
                lexicon_variables.append((x, getattr(cls, x)))

        # make sure that all query items are treated as lexicon features:
        for query_item_type in [QUERY_ITEM_GLOSS, QUERY_ITEM_LEMMA,
                                QUERY_ITEM_POS, QUERY_ITEM_TRANSCRIPT,
                                QUERY_ITEM_WORD]:
            query_item_col = getattr(cls, query_item_type, None)
            if query_item_col and query_item_col not in lexicon_variables:
                label = getattr(cls, query_item_col, None)
                if label:
                    lexicon_variables.append((query_item_col, label))
        return lexicon_variables

    @classmethod
    def get_field(cls, rc_feature):
        """
        Get a full SQL field name for the resource feature.
        """
        _, table, _ = cls.split_resource_feature(rc_feature)
        return "{}.{}".format(
            getattr(cls, "{}_table".format(table)), getattr(cls, rc_feature))

    @classmethod
    def get_referent_feature(cls, rc_feature):
        """
        Get the referent feature name of a rc_feature.

        For normal output columns, the referent feautre name is identical
        to the rc_feature string.

        For columns from an external table, it is the feature name of the
        column that the label is linked to.

        Parameters
        ----------
        rc_feature : string

        Returns
        -------
        resource : string
        """

        hashed, table, feature = cls.split_resource_feature(rc_feature)

        # Check if the feature has the same database as the current
        # resource, i.e. check if the feature is NOT from a linked table:
        if hashed is None:
            return "{}_{}".format(table, feature)
        else:
            link, res = get_by_hash(hashed)
            _, tab, feat = res.split_resource_feature(link.rc_from)
            return "{}_{}".format(tab, feat)

    @classmethod
    def is_lexical(cls, rc_feature):
        """
        Return True if the given resource feature is a lexical feature.

        There will be as many numbered columns for each lexical feature as
        there are query items in the query strings.

        Features that are not lexical features will occur only once in the
        results table regardless of the number of query items.

        A resource feature that is mapped to a query item type, i.e. Word,
        Lemma, POS, Gloss, Transcript, is always considered a lexical feature.
        The corpus ID is also always a lexical feature.

        A resource feature that is stored in a table that is linked to a table
        that contains a feature that is mapped to a query item type is also
        considered a lexical feature.

        For resources that represent links (i.e. that contain an identifier
        that is used as the key to another table, and which therefore have the
        shape xxx_yyy_id), the corresponding id field from the other table is
        considered.

        An external resource feature is considered a lexical feature if the
        linking feature is lexical.

        Additional features can be declared as lexical by using the method
        add_lexical_feature() during the initialization. For example, features
        from the corpus table in a flat corpus that are not mapped to a query
        item type may require this treatment.
        """

        # lookup feature in list of features explicitly declared lexical:
        if rc_feature in cls.lexical_features:
            return True

        # get feature (taking external links into account):
        feature = cls.get_referent_feature(rc_feature)
        if feature not in dir(cls):
            return False

        if feature == "corpus_id":
            # corpus ID is always lexical
            return True

        _, table, feat = cls.split_resource_feature(feature)
        if feat.endswith("_id"):
            _, table, feat = cls.split_resource_feature(feat)
        for item_type in (
                QUERY_ITEM_WORD, QUERY_ITEM_LEMMA, QUERY_ITEM_POS,
                QUERY_ITEM_TRANSCRIPT, QUERY_ITEM_GLOSS):
            if feature == getattr(cls, item_type, None):
                # features mapped onto query items are always lexical
                return True

        item_tab_list = set([])
        for item_type in (QUERY_ITEM_WORD, QUERY_ITEM_LEMMA, QUERY_ITEM_POS,
                          QUERY_ITEM_TRANSCRIPT, QUERY_ITEM_GLOSS):
            query_feature = getattr(cls, item_type, None)
            if query_feature and not query_feature.startswith("corpus_"):
                _, tab, _ = cls.split_resource_feature(query_feature)
                item_tab_list.add(tab)

        path = cls.get_table_path("corpus", table)

        return any([x in path for x in item_tab_list])

    @classmethod
    def is_tokenized(cls, rc_feature):
        """
        Tokenized features are features that contain token-specific
        data. In an output table, they should occur numbered for each
        query item.

        Unlike lexical features, they are not descendants of word_table,
        but are directly stored in the corpus table.
        """
        return (rc_feature == "corpus_id" or
                (rc_feature.startswith("corpus_") and
                 not rc_feature.endswith("_id")))

    def audio_to_source(self, audio_name, strip_path=True):
        """
        Return the name of the source file that belongs to an audio file.

        Parameters
        ----------

        audio_name : str
            The name of the audio file.

        strip_path : bool
            Currently ignored.

        Returns
        -------

        grid_name : list
            A list of file names that are associated with the given audio file
            name. The default behavior is to return a list with the base name
            of the audio file name as the only element, but corpus installers
            may override this behavior.

            For example, the audio files in the Switchboard corpus are named
            sw0XXXX, where XXXX is an integer digit. The corresponding source
            files which are used to construct the corpus in Coquery are named
            swXXXXY-ms98-a-word, where XXXX is the same integer digit as in
            the audio file, and Y is either 'A' or 'B' depending on which
            speaker is transcribed. Hence, for Switchboard, the call

            audio_to_source("sw02317")

            returns the list ["sw2317A-ms98-a-word", "sw2317B-ms98-a-word"].

            If the resource does not support audio, None is returned.
        """
        path, file_name = os.path.split(audio_name)
        base, ext = os.path.splitext(file_name)

        if not self.audio_features:
            return None
        else:
            return [base]

    def convert_source_to_audio(self, source_name, strip_path=True):
        """
        Return the name of the audio file that belongs to a source file.

        Parameters
        ----------

        source_name : str
            The name of the source file.

        strip_path : bool
            Currently ignored.

        Returns
        -------

        audio_file : str
            The file name of the associated audio file.

            The default behavior is to return the same base name as the
            source file.
        """
        path, file_name = os.path.split(source_name)
        base, ext = os.path.splitext(file_name)
        if not self.audio_features:
            return None
        else:
            return base


class SQLResource(BaseResource):
    _get_orth_str = None

    def __init__(self, _, corpus):
        super(SQLResource, self).__init__()
        self._word_cache = {}
        self.corpus = corpus
        self.attach_list = []
        self._context_string_template = self.get_context_string_template()
        self._sentence_feature = (
            getattr(self, "corpus_sentence", None) or
            getattr(self, "corpus_sentence_id", None) or
            getattr(self, "corpus_utterance", None) or
            getattr(self, "corpus_utterance_id", None))

    @staticmethod
    def get_operator(Token):
        """ returns a string containing the appropriate operator for an
        SQL query using the Token (considering wildcards and negation) """
        if options.cfg.regexp:
            return "REGEXP"
        if Token.has_wildcards(Token.S):
            Operators = {True: "NOT LIKE", False: "LIKE"}
        else:
            Operators = {True: "!=", False: "="}
        return Operators[False]

    @classmethod
    def get_sentence_feature(cls):
        return (getattr(cls, "corpus_sentence", None) or
                getattr(cls, "corpus_sentence_id", None) or
                getattr(cls, "corpus_utterance", None) or
                getattr(cls, "corpus_utterance_id", None))

    @classmethod
    def get_origin_rc(cls):
        """
        Return the resource feature that identifies the origin of any given
        token in the corpus. The origin resource feature is used to look up
        contexts when clicking on an entry, and when retrieving surrounding
        words in get_context().
        """

        # FIXME: in order to make this not depend on a fixed database layout
        # (here: 'source' and 'file' tables), we might want to check for any
        # table that corpus_table is linked to except for word_table (and all
        # child tables).
        for x in ["corpus_source_id", "corpus_file_id",
                  "corpus_sentence_id", "corpus_id"]:
            if hasattr(cls, x):
                return x
        return None

    def get_table_size(self, rc_table):
        engine = options.cfg.current_connection.get_engine(self.db_name)
        table = getattr(self, "{}_table".format(rc_table))
        S = "SELECT COUNT(*) FROM {}".format(table)
        size = pd.read_sql(S, con=engine).iloc[0][0]
        engine.dispose()
        return size

    def get_table_names(self, rc_table):
        """
        Return a list containing the SQL table field information.
        """

        # FIXME: This is probably a method that should be provided by the
        # connection and not by the resource
        engine = options.cfg.current_connection.get_engine(self.db_name)
        table_name = getattr(self, "{}_table".format(rc_table))
        db_type = options.cfg.current_connection.db_type()
        if db_type == SQL_MYSQL:
            S = "SHOW FIELDS FROM {}"
            columns = "name", "type", "null", "key", "default", "ex"
        else:
            S = "PRAGMA table_info({})"
            columns = "cid", "name", "type", "null", "default", "key"

        with engine.connect() as connection:
            rows = [dict(zip(columns, x)) for
                    x in connection.execute(S.format(table_name))]
        return rows

    def get_primary_key(self, rc_table):
        """
        Return the name of the primary key in the SQL table, or None.
        """
        # FIXME: This is probably a method that should be provided by the
        # connection and not by the resource
        for row in self.get_table_names(rc_table):
            if row["key"] in ("PRI", 1):
                return row["name"]
        return None

    def dump_table(self, path, rc_table, table_size, chunk_signal,
                   chunksize=250000):
        engine = options.cfg.current_connection.get_engine(self.db_name)
        table = getattr(self, "{}_table".format(rc_table))
        primary = self.get_primary_key(rc_table)
        S = "SELECT * FROM {} WHERE {} BETWEEN {{}} AND {{}}".format(
            table, primary)
        first = True

        chunks = table_size // chunksize
        for i in range(chunks + 1):
            if chunk_signal:
                chunk_signal.emit((i, chunks + 1))
            sql_query = S.format(i * chunksize, (i + 1) * chunksize - 1)
            chunk = pd.read_sql(sql_query, engine)
            chunk.to_csv(path, header=first, index=False, mode="a",
                         encoding="utf-8",
                         quoting=QUOTE_NONNUMERIC)
            first = False
        if chunk_signal:
            chunk_signal.emit((chunks + 1, chunks + 1))
        engine.dispose()

    def get_module_path(self):
        path = options.cfg.current_connection.resources()[self.name][-1]
        return path

    def get_table_descriptor(self):
        """
        Return a description of all SQL tables provided by the resource.

        This method is used by pack_corpus().

        Returns
        -------
        d : dict
            A dictionary with table short names as keys, and table
            dictionaries as values.
        """
        d = {}
        feature_map = [(x, getattr(self, x))
                       for x in self.get_resource_features()]

        for tab in self.get_table_tree("corpus") + ["tag"]:
            table_name = getattr(self, "{}_table".format(tab))

            d[tab] = dict(Fields={}, Primary=None, Name=table_name)
            for row in self.get_table_names(tab):
                field_name = row["name"]
                rc_feature = None
                for rc_feature, name in feature_map:
                    tup = self.split_resource_feature(rc_feature)
                    _, table, feature = tup
                    if table == tab and name == field_name:
                        break

                if row["key"] in ["PRI", 1]:
                    d[tab]["Primary"] = rc_feature

                d[tab]["Fields"][rc_feature] = {
                    "Type": row["type"],
                    "Null": ("NOT NULL" if row["null"] in ["NO", 1] else ""),
                    "Name": field_name}
        return d

    @classmethod
    def get_pack_steps(cls):
        """
        Return an estimation of the number of steps that are required to
        pack this resource.

        Used to advance the progress bar in the corpus builder GUI.
        """
        return 3 + len(cls.get_table_tree("corpus")) * 3

    def pack_corpus(self, name, license, file_signal=None, chunk_signal=None):
        """
        Creates a self-contained corpus package.

        The corpus package is in essence a zip file containing a dump of each
        table in the data base alongside a corpus module.

        Parameters
        ----------
        name : str
            Name of the package file
        license : str
            A string that is stored into the file LICENSE
        file_signal : Signal or None
            If not None, this Qt signal is emitted at the beginning of each
            new file that is packed. A tuple consisting of the current file
            name and a string describing the packing stage for the current
            file is passed as an argument to the signal.
        chunk_signal : Signal or None
            If not None, this Qt signal is emitted for each chunk that is
            written to the current file. A tuple consisting of the current
            chunk number and the total number of chunks is passed as an
            argument to the signal.
        """
        zf = zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED)

        # write CSV files
        for tab in self.get_table_tree("corpus") + ["tag"]:
            tab_name = "{}.csv".format(tab)
            if file_signal:
                file_signal.emit((tab_name, "Determining size of "))
            size = self.get_table_size(tab)
            if file_signal:
                file_signal.emit((tab_name, "Extracting"))
            temp_file = tempfile.NamedTemporaryFile()
            temp_name = temp_file.name
            try:
                self.dump_table(temp_name, tab, size, chunk_signal)
                if file_signal:
                    file_signal.emit((tab_name, "Packaging"))
                zf.write(temp_name, arcname=tab_name)
            finally:
                temp_file.close()

        # get temp file name:
        temp_file = tempfile.NamedTemporaryFile()
        temp_name = temp_file.name
        temp_file.close()

        # write tables.json
        if file_signal:
            file_signal.emit(("tables.json", "Packaging"))
        with open(temp_name, mode="w", encoding="utf-8") as temp_file:
            json.dump(self.get_table_descriptor(), temp_file,
                      ensure_ascii=False)
        zf.write(temp_name, arcname="tables.json")

        # write LICENSE
        if file_signal:
            file_signal.emit(("LICENSE", "Packaging"))

        with open(temp_name, mode="w", encoding="utf-8") as temp_file:
            temp_file.write(license)
        zf.write(temp_name, arcname="LICENSE")

        # write module file
        module_name = os.path.basename(self.get_module_path())
        if file_signal:
            file_signal.emit((module_name, "Packaging"))
        zf.write(self.get_module_path(), arcname=module_name)

        zf.close()

    def get_statistics(self, db_connection, signal=None, s=None):
        stats = []
        # determine table size for all columns
        table_sizes = {}
        for rc_table in [x for x in dir(self)
                         if not x.startswith("_") and
                         x.endswith("_table") and
                         not x.startswith("tag_")]:
            table = getattr(self, rc_table)
            if type(table) != str:
                continue
            S = "SELECT COUNT(*) FROM {}".format(table)
            df = pd.DataFrame(db_connection.execute(S).fetchall())
            table_sizes[table] = df.values.ravel()[0]
            if signal:
                signal.emit(s.format(rc_table))

        # get distinct values for each feature:
        for rc_feature in dir(self):
            if rc_feature.endswith("_table") or "_" not in rc_feature:
                continue
            rc_table = "{}_table".format(rc_feature.split("_")[0])
            try:
                if getattr(self, rc_table) not in table_sizes:
                    continue
            except AttributeError:
                continue
            if rc_feature == "{}_id".format(rc_feature.split("_")[0]):
                continue
            try:
                table = getattr(self, rc_table)
                column = getattr(self, rc_feature)
            except AttributeError:
                pass
            else:
                #S = "SELECT COUNT(DISTINCT {}) FROM {}".format(column, table)
                #df = pd.read_sql(S, engine)
                S = "SELECT {} FROM {}".format(column, table)
                df = pd.DataFrame(db_connection.execute(S).fetchall(),
                                  columns=[column])
                stats.append([table, column, table_sizes[table], len(df[column].unique()), 0, 0, rc_feature])
                if signal:
                    signal.emit(s.format(rc_feature))

        df = pd.DataFrame(stats)

        # calculate ratio:
        df[4] = df[3] / df[2]
        df[5] = df[2] / df[3]

        df.columns = [
            "coq_statistics_table",
            "coq_statistics_column",
            "coq_statistics_entries",
            "coq_statistics_uniques",
            "coq_statistics_uniquenessratio",
            "coq_statistics_averagefrequency",
            "coquery_invisible_rc_feature"]

        try:
            df.sort_values(by=list(df.columns)[:2], inplace=True)
        except AttributeError:
            df.sort(columns=list(df.columns)[:2], inplace=True)
        return df

    @classmethod
    def get_subselect_corpus(cls, N, ref_N):
        """
        Returns a string that contains the subselect for the self-joined
        corpus N.

        ref_N is the number of the reference corpus (i.e. the self-joined
        corpus that contains the links to the origin ID, and which provides
        the token ID).
        """

        template = "(SELECT {fields} FROM {corpus})"

        fields = []
        aliases = []
        for x in dir(cls):
            if (x.startswith("corpus_") and
                    not x.endswith(("_table", "_columns"))):
                field_name = getattr(cls, x)
                alias = "{field}{N}".format(field=field_name, N=N)
                S = "{field} AS {alias}".format(field=field_name, alias=alias)
                if alias not in aliases:
                    fields.append(S)
                    aliases.append(alias)
        return template.format(fields=", ".join(sorted(fields)),
                               corpus=cls.corpus_table)

    @staticmethod
    def string_entropy(s):
        """
        Estimate the Boltzmann entropy of a string (kind of).

        This function approximates the specificity of a query string by using
        a formula that built around Bolzmann entropy

        S = N * -sum(p_i * log(p_i))

        with N being the number of characters in the string and p_i being the
        "probability state" of each character within the string.

        "Probability state" is, of course, not well-defined in this context.
        You could use, for instance, the overall probability of the character
        within the target language, but you could also take the preceding
        character into account and calculate something like a conditional
        probability.

        The function is tweaked to produce the results expected for the query
        strings found in the module tests.

        Wildcard '?' is treated as a character of probability 0.5
        Wildcard '*' has a probability of something extremely low; in fact the
        presence of this character is strongly penalized and yields a very low
        entropy.

        """
        _MAX_ENTROPY = 10

        any_char = -0.001
        wildcard_q = 13/26 * math.log2(13/26)
        wildcard_a = -0.75

        if s.startswith("~"):
            l = []
            s = s.strip("~")
            for ch in s:
                if ch == "?":
                    l.append("#")
                elif ch == "*":
                    l.append("*")
                else:
                    l.append("?")
            s = "".join(l)

        s = s.replace("\\?", "#")
        s = s.replace("\\*", "#")
        s = s.replace("\\[", "#")
        s = s.replace("\\", "")
        POS = "[" in s and "]" in s
        s = s.replace("[", "")
        s = s.replace("]", "")
        while "**" in s:
            s = s.replace("**", "*")
        s = s.replace("?*", "*")
        s = s.replace("*?", "*")

        S = _MAX_ENTROPY
        N = 1
        for chunk in s.split("|"):
            if chunk == "*":
                return _MAX_ENTROPY

            x = 0
            for i, ch in enumerate(chunk):
                if ch == "?":
                    # penalize initial wildcards, see issue #285
                    if i == 0:
                        x += wildcard_q * 2
                    else:
                        x += wildcard_q / i
                elif ch == "*":
                    # penalize initial wildcards, see issue #285
                    if i == 0:
                        x += wildcard_a * 2
                    else:
                        x += wildcard_a / i
                else:
                    x += -any_char / math.sqrt(len(chunk))

            S = min(S, -x)
            N = max(N, len(chunk))

        # penalize POS query items:
        if POS:
            S = (3 / math.sqrt(N)) * S
        return S

    @classmethod
    def get_token_order(cls, token_list):
        l = sorted(token_list, key=lambda x: cls.string_entropy(x[1][1]))
        return l

    @classmethod
    def get_corpus_joins(cls, query_items, ignore_ngram=False):
        """
        Returns a list of corpus joins for the sub query
        """

        joins = []

        token_list = []
        offset = 0

        for i, (_, item_string) in enumerate(query_items):
            if item_string is not None:
                token_list.append((offset, (i+1, item_string)))
                offset += 1

        token_list = cls.get_token_order(token_list)

        width = getattr(cls, "corpusngram_width", 0)
        joined = False
        for i, (offset, (N, _)) in enumerate(token_list):
            if (offset < width and
                    cls.has_ngram() and
                    not ignore_ngram and
                    len(token_list) > 1):
                # use ngram lookup table
                if not joined:
                    if i == 0:
                        joins.append("FROM {corpus}".format(
                            corpus=cls.corpusngram_table))
                        ref_N = 1
                        ref_offs = 0
                    else:
                        if N > ref_N:
                            comp = "{id}{ref_N} + {offs}"
                            offs = offset - ref_offs
                        else:
                            comp = "{id}{ref_N} - {offs}"
                            offs = abs(offset - ref_offs)

                        s = """
                        INNER JOIN {{corpus}}
                        ON {{id}}1 = {comp}""".format(comp=comp)
                        joins.append(s.format(corpus=cls.corpusngram_table,
                                              id=cls.corpus_id,
                                              ref_N=ref_N,
                                              offs=offs))
                    joined = True
            else:
                # use self-joined corpus tables
                if i == 0:
                    s = "FROM       {corpus} AS COQ_CORPUS_{N}"
                    comp = ""
                    ref_N = N
                    ref_offs = offset
                else:
                    if N > ref_N:
                        comp = "{{id}}{{ref_N}} + {offs}"
                        offs = offset - ref_offs
                    else:
                        comp = "{{id}}{{ref_N}} - {offs}"
                        offs = abs(offset - ref_offs)
                    s = ("INNER JOIN {{corpus}} AS COQ_CORPUS_{{N}} "
                         "ON {{id}}{{N}} = {comp}").format(
                             comp=comp.format(offs=offs))
                s = s.format(
                    corpus=cls.get_subselect_corpus(N, ref_N),
                    id=cls.corpus_id,
                    N=N, ref_N=ref_N,
                    comp=comp)

                joins.append(s)
        return joins

    @classmethod
    def get_required_tables(cls, root, selected, conditions):
        """
        Returns a tuple that represents the table structure that is required
        to query the features given in `selected`.

        The tuple consists of two elements. The first element is the root
        table name. The second element is a list of tuples that recursively
        represent the tables that have to be joined to the root table.

        Example
        -------

        Assuming a table structure

        corpus
        + source
        + word

        A call get_required_tables("corpus", ["source_label", "word_label"])
        might return the following structure:

        ("corpus", [("source", []), ("word", [])])
        """

        # First, create a set containing all tables that are needed to
        # target all selected features. At the bare minimum, those tables
        # are needed which are required to fulfil the conditions.
        tables = set(conditions.keys())
        for rc_feature in sorted(selected):
            _, target, _ = cls.split_resource_feature(rc_feature)
            table_path = cls.get_table_path(root, target)
            if table_path:
                tables = tables.union(table_path)

        # also add those tables that are required in order to pull in an
        # external table:
        for rc_feature in selected:
            hashed, table, feature = cls.split_resource_feature(rc_feature)
            if hashed is not None:
                link, res = get_by_hash(hashed)
                _, tab, _ = cls.split_resource_feature(link.rc_from)
                table_path = cls.get_table_path(root, tab)
                if table_path:
                    tables = tables.union(table_path)

        # second, create a list of dummy features for each table. This list
        # is then used to pull in all required tables in order:
        selected = ["{}_dummy".format(x) for x in tables]
        l = []
        for dummy in sorted(selected):
            _, target, _ = cls.split_resource_feature(dummy)
            # check if the current table is a neighbor of the current root
            # table:
            table_path = cls.get_table_path(root, target)
            if table_path and len(table_path) == 2:
                # if the table is a neighbor of root, recursively get the
                # children of the current table:
                sub_select = list(selected)
                sub_select.remove(dummy)
                tup = cls.get_required_tables(target, sub_select, conditions)
                # insert tuple for current table into list:
                l.append(tup)
        return root, l

    def add_table_path(self, start_feature, end_feature):
        """
        Add the join string  needed to access end_feature from the table
        containing start_feature.

        This method modifies the class attributes joined_tables (to keep
        track of tables that are already included in the join) and
        table_list (which contains the join strings).
        """
        # FIXME: treat features from linked tables like native features
        _, last_table, _ = self.split_resource_feature(start_feature)
        _, end_table, _ = self.split_resource_feature(end_feature)

        table_path = self.get_table_path(last_table, end_table)
        sql_template = """
            INNER JOIN {table}
            ON {table}.{table_id} = {prev_table}.{prev_table_id}"""

        for table in table_path[1:]:
            if table not in self.joined_tables:
                self.table_list.append(sql_template.format(
                    table=getattr(self, "{}_table".format(table)),
                    table_id=getattr(self, "{}_id".format(table)),
                    prev_table=getattr(self, "{}_table".format(last_table)),
                    prev_table_id=getattr(self, "{}_{}_id".format(last_table,
                                                                  table))))
                self.joined_tables.append(table)
            last_table = table

    @classmethod
    def has_ngram(cls):
        return (hasattr(cls, "corpusngram_table") and
                not options.cfg.no_ngram and
                options.cfg.experimental)

    @staticmethod
    def alias_external_table(n, link, res):
        _, table, _ = res.split_resource_feature(link.rc_to)
        ext_table = getattr(res, "{}_table".format(table))
        return "{db_name}_{table}_{N}".format(
            db_name=res.db_name.upper(),
            table=ext_table, N=n+1).upper()

    @classmethod
    def get_external_join(cls, n, rc_feature):
        """
        Return the join string for the link represented by the
        resource feature.
        """
        hashed, table, _ = cls.split_resource_feature(rc_feature)
        link, res = get_by_hash(hashed)
        _, int_tab, int_feat = cls.split_resource_feature(link.rc_from)
        int_alias = "COQ_{}_{}".format(int_tab.upper(), n+1)
        int_column = getattr(cls, link.rc_from)

        ext_table = getattr(res, "{}_table".format(table))
        ext_alias = cls.alias_external_table(n, link, res)
        ext_name = "{}.{}".format(res.db_name, ext_table)
        ext_column = getattr(res, link.rc_to)

        table_string = "{ext_name} AS {ext_alias}".format(
            ext_name=ext_name, ext_alias=ext_alias)

        if int_tab == "corpus":
            s = "{ext_alias}.{ext_column} = {int_alias}.{int_column}{N}"
        else:
            s = "{ext_alias}.{ext_column} = {int_alias}.{int_column}"
        where_string = s.format(
            ext_alias=ext_alias, ext_column=ext_column,
            int_alias=int_alias, int_column=int_column,
            N=n+1)

        table_string = "{} {} ON {}".format(
            link.join_type, table_string, where_string)
        return table_string

    @classmethod
    def get_feature_joins(cls, n, selected, conditions=None, first_item=1):
        """
        Returns a list of table joins that are needed to satisfy the given
        list of selected features.
        """
        def get_join(n, table, parent):
            """
            Construct a partial SQL table statement that can be used as an
            argument for the feature joins.
            """
            table_name = getattr(cls, "{}_table".format(table))
            table_alias = "COQ_{}_{}".format(table.upper(), n+1)
            table_id = getattr(cls, "{}_id".format(table))
            parent_id = getattr(cls, "{}_{}_id".format(parent, table))

            sql_template = "{table_name} AS {table_alias}"
            table_str = sql_template.format(
                table_name=table_name, table_alias=table_alias)

            if cls.has_ngram():
                n = n - first_item + 1

            if parent == "corpus":
                sql_template = "{table_alias}.{table_id} = {parent_id}{N}"
            else:
                sql_template = "{table_alias}.{table_id} = COQ_{parent}_{N}.{parent_id}"
            where_str = sql_template.format(
                table_alias=table_alias, table_id=table_id,
                parent=parent.upper(), parent_id=parent_id, N=n+1)

            table_str = "INNER JOIN {} ON {}".format(table_str, where_str)
            return [table_str], []

        def add_joins(n, parent, tup):
            """
            Recursively build a list containing the partial SQL statements
            used for the feature joins.
            """
            root, joins = tup
            table_list, where_list = get_join(n, root, parent)
            for x in joins:
                l1, l2 = add_joins(n, root, x)
                table_list += l1
                where_list += l2
            return table_list, where_list

        conditions = conditions or {}
        table_list = []
        where_list = []

        if n == 0 or n + 1 == first_item:
            features = [x for x in sorted(selected)
                        if not x.startswith("segment_")]
            if first_item:
                n = first_item - 1
        else:
            lexicon_features = [x for x, _ in cls.get_lexicon_features()]
            features = [x for x in sorted(selected)
                        if not x.startswith("segment_") and
                        x in lexicon_features]

        root, tables = cls.get_required_tables("corpus", features, conditions)

        for tup in tables:
            table_strings, where_strings = add_joins(n, "corpus", tup)
            for s in table_strings:
                if s not in table_list:
                    table_list.append(s)
            for s in where_strings:
                if s not in where_list:
                    where_list.append(s)

        # also add those tables that are required in order to pull in an
        # external table:
        for rc_feature in sorted(selected):
            hashed, _, _ = cls.split_resource_feature(rc_feature)
            if hashed is not None:
                table_string = cls.get_external_join(n, rc_feature)
                if table_string not in table_list:
                    table_list.append(table_string)

        return table_list, where_list

    @classmethod
    def get_attach_list(cls, selected):
        """
        Return a list of data bases that have to be attached in order to
        fulfil this query. This is only needed for SQL_SQLITE.
        """
        attach_list = set([])
        for rc_feature in sorted(selected):
            hashed, _, _ = cls.split_resource_feature(rc_feature)
            if hashed is not None:
                link, res = get_by_hash(hashed)
                attach_list.add(res.db_name)
        return attach_list

    @classmethod
    def get_lemmatized_conditions(cls, i, token):
        if not hasattr(cls, QUERY_ITEM_LEMMA):
            raise UnsupportedQueryItemError("Lemmatization by \"#\" flag")

        # create a table path from the word table to the lemma table
        word_feature = getattr(cls, QUERY_ITEM_WORD)
        _, w_tab, _ = cls.split_resource_feature(word_feature)
        word_table = getattr(cls, "{}_table".format(w_tab))
        word_alias = "COQ_{}_{}".format(w_tab.upper(), i+1)

        lemma_feature = getattr(cls, QUERY_ITEM_LEMMA)
        _, l_tab, _ = cls.split_resource_feature(lemma_feature)
        lemma_column = getattr(cls, lemma_feature)
        lemma_alias = "COQ_{}_{}".format(l_tab.upper(), i+1)

        table_list = ["{} AS {}".format(word_table, word_alias)]
        _, last_table, _ = cls.split_resource_feature(word_feature)

        path = cls.get_table_path(w_tab, l_tab)
        prev_alias = word_alias
        prev_tab = w_tab

        if path:
            for table in path[1:]:
                table_name = getattr(cls, "{}_table".format(table))
                table_id = getattr(cls, "{}_id".format(table))
                table_alias = "COQ_{}_{}".format(table.upper(), i+1)

                prev_id = getattr(cls, "{}_{}_id".format(prev_tab, table))

                linking_condition = "{}.{} = {}.{}".format(
                    table_alias, table_id,
                    prev_alias, prev_id)

                table_list.append("INNER JOIN {} AS {} ON {}".format(
                    table_name, table_alias,
                    linking_condition))

                prev_alias = table_alias

        # using the path, get a list of all lemma labels that belong to
        # the word ids from the list:
        inner_select = "SELECT DISTINCT {} FROM {} WHERE {{where}}".format(
            lemma_column, " ".join(table_list))

        kwargs = {
            "lemma_alias": lemma_alias,
            "lemma_column": lemma_column,
            "inner_select": inner_select}

        S = "{lemma_alias}.{lemma_column} IN ({inner_select})".format(
            **kwargs)
        return S

    @classmethod
    def get_token_conditions(cls, i, token):
        """
        Return a dictionary with required tables as names, and SQL
        conditions as values.
        """

        def handle_case(s):
            db_type = options.cfg.current_connection.db_type()

            # take care of case options:
            if (options.cfg.query_case_sensitive):
                if (db_type == SQL_MYSQL):
                    return "BINARY {}".format(s)
                elif db_type == SQL_SQLITE:
                    return "{} COLLATE BINARY".format(s)
            else:
                if (db_type == SQL_MYSQL):
                    return s
                elif db_type == SQL_SQLITE:
                    return "{} COLLATE NOCASE".format(s)

        def get_operator(S):
            if options.cfg.regexp:
                operator = "REGEXP"
            else:
                token = tokens.COCAToken(S)
                if token.has_wildcards(S):
                    operator = "LIKE"
                else:
                    operator = "="
            return operator

        d = defaultdict(list)
        # Make sure that the token contains only those query item types that
        # are actually supported by the resource:
        for spec_list, label, item_type in [
                (token.word_specifiers, QUERY_ITEM_WORD, "Word"),
                (token.lemma_specifiers, QUERY_ITEM_LEMMA, "Lemma"),
                (token.class_specifiers, QUERY_ITEM_POS, "Part-of-speech"),
                (token.transcript_specifiers, QUERY_ITEM_TRANSCRIPT,
                 "Transcription"),
                (token.gloss_specifiers, QUERY_ITEM_GLOSS, "Gloss"),
                (token.id_specifiers, QUERY_ITEM_ID, "ID")]:
            if not spec_list:
                continue

            if spec_list == ["*"]:
                continue

            if item_type == "ID":
                col = getattr(cls, "corpus_id")
                tab = "corpus"
            else:
                try:
                    col = getattr(cls, getattr(cls, label))
                except AttributeError:
                    raise UnsupportedQueryItemError(item_type)
                _, tab, _ = cls.split_resource_feature(getattr(cls, label))

            if tab == "corpus":
                template = "{name}{N}"
            else:
                template = "COQ_{table}_{N}.{name}"

            alias = template.format(table=tab.upper(),
                                    name=col,
                                    N=i+1)
            if (len(spec_list) == 1):
                x = spec_list[0]
                val = tokens.COCAToken.replace_wildcards(x)
                format_str = handle_case("{alias} {op} '{val}'")
                s = format_str.format(alias=alias,
                                      op=get_operator(x),
                                      val=val)
            else:
                wildcards = []
                explicit = []
                for x in spec_list:
                    if tokens.COCAToken.has_wildcards(x):
                        wildcards.append(x)
                    else:
                        explicit.append(x)

                if explicit:
                    format_str = handle_case("{alias} IN ({val_list})")
                    s_list = ", ".join(["'{}'".format(x) for x in explicit])
                    s_exp = [format_str.format(alias=alias, val_list=s_list)]
                else:
                    s_exp = []

                if options.cfg.regexp:
                    operator = "REGEXP"
                else:
                    operator = "LIKE"
                format_str = handle_case("{alias} {op} '{val}'")
                s_list = [format_str.format(
                            alias=alias,
                            op=operator,
                            val=tokens.COCAToken.replace_wildcards(x))
                          for x in wildcards]
                s = " OR ".join(s_list + s_exp)

            d[tab].append(s)
            if token.lemmatize and label == QUERY_ITEM_POS:
                pos_spec = s
            else:
                pos_spec = None

        if token.lemmatize:
            # rewrite token conditions so that the specifications are used to
            # obtain the matching lemmas in a subquery:
            conditions = ["({})".format(x) for x in list(d.values())[0]]
            condition_template = cls.get_lemmatized_conditions(i, token)
            d = {"word": [
                condition_template.format(where=" AND ".join(conditions))]}
            if pos_spec:
                # add POS specification if provided:
                d["word"].append(pos_spec)

        return d

    @classmethod
    def get_annotation(cls, length, table):
        """
        Get the join string that is needed to query time-aligned annotations.

        Parameters
        ----------
        length : int
            The number of query items
        table : str
            The resource table name, e.g. "segments"
        """
        sql_template = "LEFT JOIN {table_name} AS {table_alias}"
        kwargs = {
            "table_name": getattr(cls, "{}_table".format(table)),
            "table_alias": "COQ_{}_1".format(table.upper())}
        table_str = sql_template.format(**kwargs)

        sql_template = (
            "{table_alias}.{table_end} - {parent_start}1 > 0.001"
            " AND {parent_end}{N} - {table_alias}.{table_start} > 0.001"
            " AND {table_alias}.{table_origin} = {parent_origin}1")
        kwargs = {
            "N": length,
            "table_alias": "COQ_{}_1".format(table.upper()),
            "table_start": getattr(cls, "{}_starttime".format(table)),
            "table_end": getattr(cls, "{}_endtime".format(table)),
            "table_origin": getattr(cls, "{}_origin_id".format(table)),
            "parent_alias": "COQ_CORPUS_{}".format(length),
            "parent_start": cls.corpus_starttime,
            "parent_end": cls.corpus_endtime,
            "parent_origin": (getattr(cls, "corpus_source_id", "") or
                              getattr(cls, "corpus_file_id", ""))}
        where_str = sql_template.format(**kwargs)

        table_str = "{} ON {}".format(table_str, where_str)
        return table_str

    @classmethod
    def get_token_offset(cls, token_list):
        """
        Return the token offset for the given token list.

        The token offset corresponds to the number of columns that are
        prepended to the actual output columns in a query string that starts
        with _NULL query items.

        For corpora with n-gram lookup tables, the offset is always 0 in order
        to maximize the informativity of the look-up table (in the spirit of
        issue #286).
        """

        if cls.has_ngram():
            return 0

        # _first_item stores the number of the first item that is not
        # _NULL. This number will be used for coquery_invisible_corpus_id and
        # coquery_invisible_origin_id.
        pos = None

        for i, (_, token) in enumerate(token_list):
            if pos is None and token:
                pos = i
        return pos or 0

    @classmethod
    def get_required_columns(cls, token_list, selected, to_file=False):
        """
        Return a list of strings. Each string refers to a column in the
        query data frame. They represent the aliasing translation from the
        SQL column lables to the format used in Coquery for column lables.
        For example, the string for the resource `word_label` is
        "COQ_WORD_x AS coq_word_label_x", where 'x' is the number of the
        query item.
        """
        lexicon_features = [x for x, _ in cls.get_lexicon_features()]
        corpus_features = [x for x, _ in cls.get_corpus_features()]
        annotations = getattr(cls, "annotations", {})

        # _first_item stores the number of the first item that is not
        # _NULL. This number will be used for coquery_invisible_corpus_id and
        # coquery_invisible_origin_id.
        _token_offset = cls.get_token_offset(token_list)
        _first_item = _token_offset + 1

        columns = []
        for rc_feature in selected:
            current_pos = 1
            for i, (pos, token) in enumerate(token_list):
                hashed, tab, feat = cls.split_resource_feature(rc_feature)
                # external resources:
                if hashed:
                    link, res = get_by_hash(hashed)
                    if link.rc_from in lexicon_features:
                        ext_alias = cls.alias_external_table(i, link, res)
                        ext_rc = "{}_{}".format(tab, feat)
                        ext_column = getattr(res, ext_rc)
                        if token is not None:
                            column = "{ext_alias}.{ext_column}".format(
                                ext_alias=ext_alias, ext_column=ext_column)
                        else:
                            column = "NULL"
                        s = "{column} AS db_{db_name}_coq_{ext_rc}_{N}"
                        alias = s.format(
                            column=column,
                            db_name=res.db_name, ext_rc=ext_rc, N=i+1)
                        columns.append(alias)
                        current_pos += 1

                if rc_feature in lexicon_features:
                    if token is not None:
                        if tab != "corpus":
                            template = "COQ_{table}_{pos}.{name}"
                        else:
                            template = "{name}{pos}"
                        column = template.format(
                            table=tab.upper(), pos=i+1,
                            name=getattr(cls, rc_feature))
                        current_pos += 1
                    else:
                        column = "NULL"
                    s = "{column} AS coq_{rc_feature}_{N}".format(
                        column=column, rc_feature=rc_feature, N=i+1)
                    if s not in columns:
                        columns.append(s)

        if not _first_item:
            _first_item = 1

        # FIXME: It's not fully clear why we go through the selected features
        # a second time. The first time for lexical features, and the second
        # for corpus features?
        for rc_feature in selected:
            if rc_feature in corpus_features:
                _, tab, feat = cls.split_resource_feature(rc_feature)
                if tab != "corpus":
                    template = "COQ_{table}_{N}.{name}"
                else:
                    template = "{name}{N}"
                template = "{} AS coq_{{rc_feature}}_1".format(template)
                s = template.format(N=_token_offset + 1,
                                    table=tab.upper(),
                                    name=getattr(cls, rc_feature),
                                    rc_feature=rc_feature)
                if s not in columns:
                    columns.append(s)

            if tab in annotations:
                s = "COQ_{tab_upper}_{N}.{tab_id} AS coquery_invisible_{tab}_id".format(
                    N=_first_item,
                    tab=tab, tab_upper=tab.upper(),
                    tab_id=getattr(cls, "{}_id".format(tab)))
                if s not in columns:
                    columns.append(s)

        id_str = "{name}{N} AS coquery_invisible_corpus_id".format(
                    N=_first_item, name=cls.corpus_id)

        origin_id = (getattr(cls, "corpus_source_id", "") or
                     getattr(cls, "corpus_file_id", ""))
        if origin_id:
            origin_str = "{name}{N} AS coquery_invisible_origin_id".format(
                    N=_first_item, name=origin_id)
        else:
            origin_str = None

        if to_file:
            if not columns or (options.cfg.context_mode != CONTEXT_NONE):
                columns.append(id_str)
            if options.cfg.context_mode != CONTEXT_NONE and origin_str:
                columns.append(origin_str)
        else:
            if id_str not in columns:
                columns.append(id_str)
            if origin_str:
                columns.append(origin_str)

        return columns

    @classmethod
    def get_condition_list(cls, query_items, join_list, selected):
        condition_list = []
        current_pos = 0
        # go through the query items and add all required list as well as
        # the WHERE conditions based on the query item specification

        first_item = None

        for i, (pos, s) in enumerate(query_items):
            if s is not None:
                if first_item is None:
                    first_item = pos
                token = tokens.COCAToken(s)
                if s != "*":
                    conditions = cls.get_token_conditions(i, token)
                else:
                    conditions = {}
                for _, l in conditions.items():
                    s = " AND ".join(["({})".format(x) for x in l])
                    if token.negated:
                        s = "NOT ({})".format(s)
                    condition_list.append(s)

                if first_item != 1:
                    table_list, where_list = cls.get_feature_joins(
                        i, selected, conditions, first_item)
                else:
                    table_list, where_list = cls.get_feature_joins(
                        i, selected, conditions)

                join_list += table_list
                condition_list += ["({})".format(x) for x in where_list]
                current_pos += 1
        return condition_list

    @classmethod
    def get_query_string(cls,
                         query_items, selected, columns=None, to_file=False):
        """
        Return an SQL string for the specified query.
        """
        if columns is None or columns == []:
            columns = cls.get_required_columns(query_items, selected, to_file)

        # get list of self-joints for the corpus:
        join_list = cls.get_corpus_joins(query_items)

        # Some tables are not linked by an ID, but by time alignments.
        # One example is the Segments table from the Buckeye corpus.
        # These tables are explicitly added:
        features = [x for x in sorted(selected) if x.startswith("segment_")]
        for rc_feature in features:
            _, tab, _ = cls.split_resource_feature(rc_feature)
            if tab in cls.annotations:
                table_string = cls.get_annotation(len(query_items), tab)
                if table_string not in join_list:
                    join_list.append(table_string)

        sql_template = """
        SELECT {columns}
        {joins}"""

        # get list of conditions that will be placed in the WHERE clause:
        condition_list = cls.get_condition_list(query_items,
                                                join_list,
                                                selected)

        if condition_list:
            sql_template = """{}
            WHERE  {{conditions}}""".format(sql_template)

        S = sql_template.format(columns=", ".join(columns),
                                joins=" ".join(join_list),
                                conditions=" AND ".join(condition_list))

        if options.cfg.limit_matches and options.cfg.number_of_tokens:
            S = """{}
            LIMIT  {}
            """.format(S, int(options.cfg.number_of_tokens))
        return S

    def is_part_of_speech(self, pos):
        pos_feature = getattr(self, QUERY_ITEM_POS, None)
        if pos_feature:
            current_token = tokens.COCAToken(pos)
            _, table, _ = self.split_resource_feature(pos_feature)
            S = "SELECT {} FROM {} WHERE {} {} '{}' LIMIT 1".format(
                getattr(self, "{}_id".format(table)),
                getattr(self, "{}_table".format(table)),
                getattr(self, pos_feature),
                self.get_operator(current_token),
                pos)
            engine = options.cfg.current_connection.get_engine(self.db_name)
            df = pd.read_sql(S.replace("%", "%%"), engine)
            engine.dispose()
            return len(df.index) > 0
        else:
            return False

    def pos_check_function(self, l):
        return [self.is_part_of_speech(s) for s in l]

    def get_sentence_ids(self, id_list):
        """
        Return a list containing the sentence IDs that belong to the list of
        corpus Ids.
        """

        if hasattr(self, "corpus_sentence"):
            sentence = self.corpus_sentence
        elif hasattr(self, "corpus_sentence_id"):
            sentence = self.corpus_sentence_id
        else:
            return [None] * len(id_list)

        if id_list.isnull().all():
            return pd.DataFrame(id_list)

        S = """
        SELECT {sentence} AS coquery_invisible_sentence_id,
               {token_id} AS coquery_invisible_corpus_id
        FROM {corpus}
        WHERE {token_id} IN ({id_list})""".format(
            corpus=self.corpus_table,
            token_id=self.corpus_id,
            sentence=sentence,
            id_list=", ".join([str(x) for x in id_list]))

        engine = options.cfg.current_connection.get_engine(self.db_name)
        df = pd.read_sql(S, engine)
        engine.dispose()

        return df

    def get_context(self, token_id, origin_id, number_of_tokens,
                    db_connection, sentence_id=None, left=None, right=None):

        left_span = left if not pd.isna(left) else options.cfg.context_left
        right_span = right if not pd.isna(right) else options.cfg.context_right
        n_tokens = int(number_of_tokens if not pd.isna(number_of_tokens)
                       else 0)

        if np.isnan(origin_id):
            results = ([(None, 0)] * left_span +
                       [(None, 1)] * n_tokens +
                       [(None, 2)] * right_span)
        else:
            S = self.get_context_string(token_id, number_of_tokens,
                                        left_span, right_span,
                                        origin_id, sentence_id)
            results = db_connection.execute(S)
        word_lists = [[], [], []]

        for word, pos in results:
            word_lists[pos].append(word)

        return ([''] * (left_span - len(word_lists[0])) + word_lists[0],
                word_lists[1],
                word_lists[2] + [''] * (right_span - len(word_lists[2])))

    @classmethod
    def get_context_string_template(cls):
        template = """
        SELECT     {columns}
        FROM       {corpus} AS COQ_CORPUS_1
        {joins}
        WHERE      {{where}}
        LIMIT      {{length}}
        """

        word_feature = getattr(cls, QUERY_ITEM_WORD)
        _, w_tab, _ = cls.split_resource_feature(word_feature)
        word_table = "COQ_{}_1".format(w_tab.upper())

        joins = "\n".join([x for x in
                           cls.get_feature_joins(0, [word_feature])[0]])

        columns = ["{word_table}.{word}{n} AS Context".format(
                        n="1" if hasattr(cls, "corpus_word") else "",
                        word_table=word_table,
                        word=getattr(cls, word_feature)),
                   "{position}"]
        return template.format(
            columns=", ".join(columns),
            corpus=cls.get_subselect_corpus(1, 1),
            joins=joins)

    def get_context_string(self,
                           token_id, width,
                           left, right,
                           origin_id, sentence_id=None):

        start = max(0, token_id - left)
        end = token_id + width + right - 1

        S = """
            (COQ_CORPUS_1.{corpus_token}1 BETWEEN {start} AND {end}) AND
            (COQ_CORPUS_1.{corpus_origin}1 = {origin_id})
            """.format(corpus_token=self.corpus_id,
                       start=start, end=end,
                       corpus_origin=getattr(self, self.get_origin_rc()),
                       origin_id=origin_id)

        _sentence_feature = self.get_sentence_feature()
        if sentence_id and _sentence_feature:
            S = "{S} AND (COQ_CORPUS_1.{sentence}1 = '{sentence_id}')".format(
                S=S,
                sentence=_sentence_feature, sentence_id=sentence_id)

        position = """
            (CASE
                WHEN ID1 < {token_id} THEN 0
                WHEN ID1 >= {token_id} + {width} THEN 2
                ELSE 1
            END) AS Position
            """.format(token_id=token_id, width=width)

        return self.get_context_string_template().format(
            where=S,
            length=int(end - start + 1),
            position=position)

    def get_origin_id(self, token_id):
        origin_rc = self.get_origin_rc()
        if not origin_rc:
            return None

        S = "SELECT {origin} FROM {corpus} WHERE {id} = {token_id} LIMIT 1"
        S = S.format(origin=getattr(self, origin_rc),
                     corpus=self.corpus_table,
                     id=self.corpus_id,
                     token_id=token_id)
        engine = options.cfg.current_connection.get_engine(self.db_name)
        df = pd.read_sql(S, engine)
        engine.dispose()

        return df.values.ravel()[0]

    def get_origin_data(self, token_id):
        """
        Return a dictionary containing all origin data that is available for
        the given token.

        This method traverses the table tree for the origin table as
        determined by get_origin_rc(). For each table, all matching fields are
        added.

        Parameters
        ----------
        token_id : int
            The id identifying the token.

        Returns
        -------
        l : list
            A list of tuples. Each tuple consists of the resource name of the
            source table, and a dictionary with resource features as keys and
            the matching field content as values.
        """
        l = []

        # get the complete row from the corpus table for the current token:
        S = "SELECT * FROM {} WHERE {} = {}".format(
            self.corpus_table,
            self.corpus_id,
            token_id)

        engine = options.cfg.current_connection.get_engine(
            self.db_name)
        df = pd.read_sql(S, engine)
        engine.dispose()

        # as each of the columns could potentially link to origin information,
        # we go through all of them:
        for column in df.columns:
            # exclude the Token ID:
            if column == self.corpus_id:
                continue
            # do not look into the word column of the corpus:
            try:
                if column == self.corpus_word_id:
                    continue
                if column == self.corpus_word:
                    continue
            except AttributeError:
                pass

            # Now, look for all features in the resource that the corpus table
            # links to. In order to do so, we first get a list of all feature
            # names that match the current column, deterimine whether they are
            # a feature of the corpus table, and if so, whether they link to
            # a different table. If that is the case, we get all fields from
            # that table that match the current entry, and add the information
            # to the origin data list:

            # get the resource feature name from the corpus table that belongs
            # to the current column display name:
            try:
                rc_feature = [x for x
                              in self.get_feature_from_name(column)
                              if x.startswith("corpus_")][0]
            except IndexError:
                continue

            # obtain the field name from the resource name:
            _, _, feature = self.split_resource_feature(rc_feature)
            # determine whether the field name is a linking field:
            try:
                _, tab, feat = self.split_resource_feature(feature)
            except ValueError:
                # split_resource_feature() raises a ValueError exception if
                # the passed string does not appear to be a resource feature.
                # In that case, the resource is not considered for origin data.
                continue
            if feat == "id":
                id_column = getattr(self, "{}_id".format(tab))
                table_name = getattr(self, "{}_table".format(tab))
                S = "SELECT * FROM {} WHERE {} = {}".format(
                    table_name, id_column, df[column].values[0])
                # Fetch all fields from the linked table for the current
                # token:
                engine = options.cfg.current_connection.get_engine(
                    self.db_name)
                row = pd.read_sql(S, engine)
                engine.dispose()

                if len(row.index) > 0:
                    D = dict([(x, row.at[0, x]) for x in row.columns
                              if x != id_column])
                    # append the row data to the list:
                    l.append((table_name, D))
        return l

    def get_file_data(self, token_id, features):
        """
        Return a data frame containing the requested features for the token
        id.
        """
        if isinstance(token_id, list):
            tokens = token_id
        elif isinstance(token_id, pd.Series):
            tokens = list(token_id.values)
        else:
            tokens = list(token_id)

        self.joined_tables = ["corpus"]
        self.table_list = [self.corpus_table]

        self.add_table_path("corpus_id", "file_id")

        feature_list = ["{}.{}".format(self.file_table, getattr(self, x))
                        for x in features]
        feature_list.append("{}.{}".format(self.corpus_table, self.corpus_id))
        token_ids = [str(x) for x in tokens]
        S = "SELECT {features} FROM {path} WHERE {corpus}.{corpus_id} IN ({token_ids})".format(
                features=", ".join(feature_list),
                path=" ".join(self.table_list),
                corpus=self.corpus_table,
                corpus_id=self.corpus_id,
                token_ids=", ".join(token_ids))

        engine = options.cfg.current_connection.get_engine(self.db_name)
        df = pd.read_sql(S, engine)
        engine.dispose()
        return df


class CorpusClass(object):
    """
    """
    _frequency_cache = {}
    _corpus_size_cache = {}
    _subcorpus_size_cache = {}
    _corpus_range_cache = {}
    _context_cache = {}

    def __init__(self):
        super(CorpusClass, self).__init__()
        self.resource = None

    def get_corpus_size(self, filters=None):
        """
        Return the number of tokens in the corpus.

        The corpus can be filtered by providing a filter list.

        Parameters
        ----------
        filters : list
            A list of tuples. The first element is a corpus feature, and
            the second is a list of possible values.

        Returns
        -------
        size : int
            The number of tokens in the corpus, or in the filtered corpus.
        """
        filters = filters or []

        if not filters and getattr(self.resource, "number_of_tokens", None):
            return self.resource.number_of_tokens

        self.resource.table_list = []
        self.resource.joined_tables = []
        filter_strings = []
        for rc_feature, values in filters:
            _, tab, feat = self.resource.split_resource_feature(rc_feature)
            self.resource.add_table_path("corpus_id", rc_feature)

            # FIXME: remove code replication with get_subcorpus_range()
            if len(values) == 1:
                if type(values[0]) is str:
                    val = "'{}'".format(values[0])
                else:
                    val = values[0]
                s = "{}.{} = {}".format(
                    getattr(self.resource, "{}_table".format(tab)),
                    getattr(self.resource, rc_feature),
                    val)
            else:
                if any([type(x) is str for x in values]):
                    l = ["'{}'".format(x) for x in values]
                else:
                    l = values
                s = "{}.{} IN ({})".format(
                    getattr(self.resource, "{}_table".format(tab)),
                    getattr(self.resource, rc_feature),
                    ",".join(l))
            filter_strings.append(s)

        if filter_strings:
            from_str = "{} WHERE {}".format(
                " ".join([self.resource.corpus_table] + self.resource.table_list),
                " AND ".join(filter_strings))
        else:
            from_str = self.resource.corpus_table

        S = "SELECT COUNT(*) FROM {}".format(from_str)
        if S not in self._corpus_size_cache:
            engine = options.cfg.current_connection.get_engine(
                self.resource.db_name)
            df = pd.read_sql(S.replace("%", "%%"), engine)
            engine.dispose()
            self._corpus_size_cache[S] = df.values.ravel()[0]
        if not filters:
            self.resource.number_of_tokens = self._corpus_size_cache[S]
        return self._corpus_size_cache[S]

    def get_subcorpus_size(self, row, columns=None, subst=None):
        """
        Return the size of the subcorpus specified by the corpus features in
        the row.

        Parameters
        ----------
        row : A Pandas Series
            A Series with stylized resource feature names as columns, and
            values that match a row in the query result table.
        """
        filter_list = []
        if columns is None:
            columns = row.index
            corpus_features = [x for x, _ in self.resource.get_corpus_features() if x in options.cfg.selected_features]
            for column in columns:
                match = re.match("coq_(.*)_1", column)
                if match:
                    col = match.group(1)
                else:
                    col = None
                if col in corpus_features:
                    value = row[column]
                    raw_values = self.reverse_substitution(column, value, subst)
                    filter_list.append((col, raw_values))
        else:
            for column in columns:
                col = "coq_{}_1".format(column)

                value = row[col]
                raw_values = self.reverse_substitution(col, value)
                filter_list.append((column, tuple(raw_values)))
        tup = tuple(filter_list)
        if tup not in self._subcorpus_size_cache:
            size = self.get_corpus_size(filter_list)
            self._subcorpus_size_cache[tup] = size
        return self._subcorpus_size_cache[tup]

    @staticmethod
    def reverse_substitution(column, value, subst=None):
        """
        Return a list of values that could have been the raw value before
        substitution.

        The method takes the current value substitution table for the given
        column. It returns a list of all values that could have been mapped
        onto the given value.
        """
        subst = subst or {}
        l = [key for key, val in subst.get(column, {}).items()
             if value == val]
        l.append(value)
        return l

    def get_subcorpus_range(self, row=None):
        """
        Return the lowest and the highest corpus id in the subcorpus specified
        by the values in `row`.

        Parameters
        ----------
        row : pandas.Series
            A Series with corpus feature values

        Returns
        -------
        min, max : tuple
            The lowest and the highest corpus id that share the values in
            `row'.
        """
        row = row or pd.Series()
        cache_key = (tuple(row.index), tuple(row.values))
        if cache_key in self._corpus_range_cache:
            return self._corpus_range_cache[cache_key]

        if len(row) == 0:
            val = 0, self.get_corpus_size()
        else:
            self.resource.table_list = []
            self.resource.joined_tables = []
            conditions = []
            for column in row.index:
                try:
                    rc_feature = re.match("coq_(.*)_1", column).group(1)
                except AttributeError:
                    print("couldn't split", column)
                    continue
                _, tab, feat = self.resource.split_resource_feature(rc_feature)
                self.resource.add_table_path("corpus_id", rc_feature)

                # FIXME: remove code replication with get_corpus_size()
                raw_values = self.reverse_substitution(column, row[column])
                if len(raw_values) == 1:
                    s = "{}.{} = '{}'".format(
                        getattr(self.resource, "{}_table".format(tab)),
                        getattr(self.resource, rc_feature),
                        raw_values[0])
                else:
                    s = "{}.{} IN ({})".format(
                        getattr(self.resource, "{}_table".format(tab)),
                        getattr(self.resource, rc_feature),
                        ",".join(["'{}'".format(x) for x in raw_values]))
                conditions.append(s)

            tables = [self.resource.corpus_table] + self.resource.table_list
            from_str = "{} WHERE {}".format(" ".join(tables),
                                            " AND ".join(conditions))

            S = "SELECT MIN({id}), MAX({id}) FROM {tables}".format(
                id=self.resource.corpus_id, tables=from_str)
            engine = options.cfg.current_connection.get_engine(
                self.resource.db_name)
            df = pd.read_sql(S.replace("%", "%%"), engine)
            engine.dispose()
            val = df.values.ravel()[0:2]
        self._corpus_range_cache[cache_key] = val
        return self._corpus_range_cache[cache_key]

    def get_frequency(self, s, engine, literal=False):
        """
        Return the frequency for a token specified by s.

        The string ``s`` contains a query item specification.

        Frequencies are cached so that recurrent calls of the method with the
        same values for ``s`` are not queried from the SQL
        database but from the working memory.

        Parameters
        ----------
        s : str
            A query item specification
        engine : SQLAlchemy Engine
            The DB engine to be used for the frequency query

        Returns
        -------
        freq : int
            The number of tokens that match the query item specification
        """

        if isinstance(s, (int, float)):
            s = str(s)
        # escape asterisks and question marks so that they are not interpreted
        # as wildcards:
        s = s.replace("*", "\\*")
        s = s.replace("?", "\\?")
        s = s.replace('"', '\\"')
        s = s.replace("#", "\\#")
        s = s.replace("/", "\\/")
        s = s.replace("%", "\\%")

        if options.cfg.query_case_sensitive:
            key = (engine.url, s, True)
        else:
            key = (engine.url, s.lower(), False)

        if key in self._frequency_cache:
            return self._frequency_cache[key]

        query_list = tokens.preprocess_query(s, literal=literal)
        freq = None

        for sub in query_list:
            S = self.resource.get_query_string(sub, [], columns=["COUNT(*)"])
            try:
                df = pd.read_sql(S, engine)
            except Exception as e:
                logging.warning(str(e))
                print(str(e))
            else:
                if freq is None:
                    freq = 0
                freq += df.values.ravel()[0]

        self._frequency_cache[key] = freq
        return freq

    def get_tag_translate(self, s):
        """
        Translates a corpus tag string to a HTML tag string
        """
        # Define some TEI tags:
        tag_translate = {
            "head": "h1",
            "list": "ul",
            "item": "li",
            "div": "div",
            "label": "li",
            "pb": "div type='page_break'",
            "p": "p"}
        try:
            return tag_translate[s]
        except KeyError:
            return s

    def tag_to_html(self, tag, attributes=None):
        """ Translate a tag to a corresponding HTML/QHTML tag by checking
        the tag_translate dictionary."""
        attributes = attributes or {}
        try:
            if tag == "hi":
                if attributes.get("rend") == "it":
                    return "i"
            if tag == "head":
                if attributes.get("type") == "MAIN":
                    return "h1"
                if attributes.get("type") == "SUB":
                    return "h2"
                if attributes.get("type") == "BYLINE":
                    return "h3"
            return self.get_tag_translate(tag)
        except KeyError:
            warnings.warn("unsupported tag: {}".format(tag))
            print("unsupported tag: {}".format(tag))
            return None

    def get_context_stylesheet(self):
        """
        Return a string that formats the used elements in a context viewer.
        """
        return ""

    def renderer_open_element(self, tag, attributes):
        label = self.tag_to_html(tag, attributes)
        if label:
            if attributes:
                return ["<{} {}>".format(
                    label,
                    ", ".join(["{}='{}'".format(x, attributes[x])
                               for x in attributes]))]
            else:
                return ["<{}>".format(label)]
        else:
            return []

    def renderer_close_element(self, tag, attributes):
        label = self.tag_to_html(tag, attributes)
        if label:
            if attributes:
                return ["</{} {}>".format(
                    label,
                    ", ".join(["{}='{}'".format(x, attributes[x])
                               for x in attributes]))]
            else:
                return ["</{}>".format(label)]
        else:
            return []

    def _read_context_for_renderer(self, token_id, source_id, token_width):
        origin_id = (getattr(self.resource, "corpus_source_id", None) or
                     getattr(self.resource, "corpus_file_id", None) or
                     getattr(self.resource, "corpus_sentence_id", None) or
                     self.resource.corpus_id)
        if hasattr(self.resource, "surface_feature"):
            word_feature = self.resource.surface_feature
        else:
            word_feature = getattr(self.resource, QUERY_ITEM_WORD)

        corpus_word_id = (getattr(self.resource, "corpus_word_id", None) or
                          getattr(self.resource, "corpus_word"))

        _, tab, _ = self.resource.split_resource_feature(word_feature)
        word_table = getattr(self.resource, "{}_table".format(tab))
        word_id = getattr(self.resource, "{}_id".format(tab))

        word_start = getattr(self.resource, "{}_starttime".format(tab), None)
        word_end = getattr(self.resource, "{}_endtime".format(tab), None)

        self.resource.table_list = []
        self.resource.joined_tables = []
        self.resource.add_table_path("corpus_id", word_feature)

        if hasattr(self.resource, "tag_table"):
            headers = ["coquery_invisible_corpus_id", "COQ_TAG_ID"]
            kwargs = {
                "corpus": self.resource.corpus_table,
                "corpus_id": self.resource.corpus_id,
                "corpus_word_id": corpus_word_id,
                "source_id": origin_id,

                "word": getattr(self.resource, word_feature),
                "word_table": word_table,
                "word_id": word_id,

                "joined_tables": " ".join(self.resource.table_list),

                "tag_table": self.resource.tag_table,
                "tag": self.resource.tag_label,
                "tag_id": self.resource.tag_id,
                "tag_corpus_id": self.resource.tag_corpus_id,
                "tag_type": self.resource.tag_type,
                "attribute": self.resource.tag_attribute,

                "current_source_id": source_id,
                "start": max(0, token_id - 1000),
                "end": token_id + token_width + 999}
            column_string = """
                    {corpus}.{corpus_id} AS coquery_invisible_corpus_id,
                    {word_table}.{word} AS coq_word_label_1,
                    {tag} AS COQ_TAG_TAG,
                    {tag_table}.{tag_type} AS COQ_TAG_TYPE,
                    {attribute} AS COQ_ATTRIBUTE,
                    {tag_id} AS COQ_TAG_ID"""
            format_string = """
                SELECT {columns}
                FROM {corpus}
                {joined_tables}
                LEFT JOIN {tag_table} ON {corpus}.{corpus_id} = {tag_table}.{tag_corpus_id}
                WHERE {corpus}.{corpus_id} BETWEEN {start} AND {end}
                """
        else:
            headers = ["coquery_invisible_corpus_id"]
            column_string = """
                    {corpus}.{corpus_id} AS coquery_invisible_corpus_id,
                    {word_table}.{word} AS coq_word_label_1"""
            format_string = """
            SELECT {columns}
            FROM {corpus}
            {joined_tables}
            WHERE {corpus}.{corpus_id} BETWEEN {start} AND {end}
            """
            kwargs = {
                "corpus": self.resource.corpus_table,
                "corpus_id": self.resource.corpus_id,
                "corpus_word_id": corpus_word_id,
                "source_id": origin_id,

                "word": getattr(self.resource, word_feature),
                "word_table": word_table,
                "word_id": word_id,

                "joined_tables": " ".join(self.resource.table_list),

                "current_source_id": source_id,
                "start": max(0, token_id - 1000),
                "end": token_id + token_width + 999}

        if word_start and word_end:
            column_string = """{},
                {{word_table}}.{{start_time}} AS coq_word_starttime_1,
                {{word_table}}.{{end_time}} AS coq_word_endtime_1""".format(
                    column_string)
            kwargs.update({"start_time": word_start, "end_time": word_end})

        kwargs["columns"] = column_string.format(**kwargs)

        if origin_id:
            format_string += (
                "    AND {corpus}.{source_id} = '{current_source_id}'")
        S = format_string.format(**kwargs)

        Print(S)
        engine = options.cfg.current_connection.get_engine(
            self.resource.db_name)
        df = pd.read_sql(S, engine)
        if hasattr(self.resource, "tag_table"):
            S = """
                SELECT {tag} AS COQ_TAG_TAG,
                       {tag_table}.{tag_type} AS COQ_TAG_TYPE,
                       {attribute} AS COQ_ATTRIBUTE,
                       {corpus_id} AS COQ_ID
                FROM {tag_table}
                WHERE {corpus_id} BETWEEN {start} AND {end}
                ORDER BY {tag_id}
            """.format(tag_table=self.resource.tag_table,
                       tag=self.resource.tag_label,
                       tag_id=self.resource.tag_id,
                       corpus_id=self.resource.tag_corpus_id,
                       tag_corpus_id=self.resource.tag_corpus_id,
                       tag_type=self.resource.tag_type,
                       attribute=self.resource.tag_attribute,
                       current_source_id=source_id,
                       start=max(0, token_id - 1000),
                       end=token_id + token_width + 999)
            tags = pd.read_sql(S, engine)
        else:
            tags = pd.DataFrame(columns=["COQ_TAG_TAG", "COQ_TAG_TYPE",
                                         "COQ_ATTRIBUTE", "COQ_ID"])
        engine.dispose()

        try:
            df = df.sort_values(by=headers)
        except AttributeError:
            df = df.sort(columns=headers)
        self._context_cache[(token_id, source_id, token_width)] = (df, tags)

    def parse_tags(self, row, open=True):
        if open:
            s1 = "<{} {}>"
            s2 = "<{}>"
        else:
            s1 = "</{} {}>"
            s2 = "</{}>"
        attr = row.COQ_ATTRIBUTE
        tag = self.tag_to_html(row.COQ_TAG_TAG)
        if attr:
            attr = re.sub("=([^,]*)", r"='\g<1>'", attr)
            return s1.format(tag, attr)
        else:
            return s2.format(tag)

    def parse_row(self, row, tags, token_id, token_width):
        Print("parse_row", len(tags))
        word = row.coq_word_label_1
        word_id = row.coquery_invisible_corpus_id
        if len(tags):
            opening = tags[(tags.COQ_ID == word_id) &
                           ((tags.COQ_TAG_TYPE == "open") |
                            (tags.COQ_TAG_TYPE == "empty"))]
            closing = tags[(tags.COQ_ID == word_id) &
                           ((tags.COQ_TAG_TYPE == "close") |
                            (tags.COQ_TAG_TYPE == "empty"))]
        else:
            opening = pd.DataFrame(columns=tags.columns)
            closing = pd.DataFrame(columns=tags.columns)
        lst = []
        if len(opening):
            lst.extend(list(opening.apply(lambda x: self.parse_tags(x, True),
                                          axis="columns")))
        token_style = "<span style='{};'>".format(
            self.resource.render_token_style)
        if word:
            # highlight words that are in the results table:
            if word_id in self.id_list:
                lst.append(token_style)
            # additional highlight if the word is the target word:
            if token_id <= word_id < token_id + token_width:
                lst.append("<b>")
                lst.append(html_escape(word))
                lst.append("</b>")
            else:
                lst.append(html_escape(word))
            if word_id in self.id_list:
                lst.append("</span>")
        if len(closing):
            lst.extend(list(closing.apply(lambda x: self.parse_tags(x, False),
                                          axis="columns")))
        return lst

    def expand_row(self, x):
        return list(range(int(x.coquery_invisible_corpus_id), int(x.end)))

    #def parse_df(self, df, tags, token_id, token_width):
        #df = df.apply(
            #lambda x: self.parse_row(x, tags, token_id, token_width),
            #axis="columns")
        #return df

    def parse_df(self, df, tags, token_id, token_width):
        df["COQ_FORMATTED"] = df["coq_word_label_1"].apply(lambda x: [x])

        token_style = "<span style='{};'>".format(
            self.resource.render_token_style)

        mask = df["coquery_invisible_corpus_id"] == token_id
        df.loc[mask, "COQ_FORMATTED"] = df.loc[mask, "COQ_FORMATTED"].apply(
            lambda x: ["<b>"] + x)
        mask = df["coquery_invisible_corpus_id"] == token_id + token_width - 1
        df.loc[mask, "COQ_FORMATTED"] = df.loc[mask, "COQ_FORMATTED"].apply(
            lambda x: x + ["</b>"])

        mask = df["coquery_invisible_corpus_id"].isin(self.id_start_list)
        df.loc[mask, "COQ_FORMATTED"] = df.loc[mask, "COQ_FORMATTED"].apply(
            lambda x: [token_style] + x)
        mask = df["coquery_invisible_corpus_id"].isin(self.id_end_list)
        df.loc[mask, "COQ_FORMATTED"] = df.loc[mask, "COQ_FORMATTED"].apply(
            lambda x: x + ["</span>"])

        return [item for sublist in df["COQ_FORMATTED"] for item in sublist]

    def get_rendered_context(self, token_id, source_id, token_width,
                             context_width, widget):
        """
        Return a dictionary with the context data.

        The dictionary has the following keys:

        text: str
            A string containing the markup for the context around the
            specified token.
        audio: bool
            A boolean indicating whether audio context is available
        start_time, end_time: float
            The starting and end time of the audio context. If `audio` is
            False, the content of these variables in unspecified.

        The most simple visual representation of the context is a plain text
        display, but in principle, a corpus might implement a more elaborate
        renderer. For example, a corpus may contain information about the
        page layout, and the renderer could use that information to create a
        facsimile of the original page.

        The renderer can interact with the widget in which the context will
        be displayed. The area in which the context is shown is a QLabel
        named widget.ui.context_area. """

        if not hasattr(self.resource, QUERY_ITEM_WORD):
            raise UnsupportedQueryItemError

        time_lst = [(datetime.now().timestamp(), "start")]

        if not (token_id, source_id, token_width) in self._context_cache:
            self._read_context_for_renderer(token_id, source_id, token_width)
        time_lst.append((datetime.now().timestamp(), "reading context"))
        df, tags = self._context_cache[(token_id, source_id, token_width)]
        df = df.reset_index(drop=True)

        ix = df.index[df.coquery_invisible_corpus_id == token_id][0]
        context_start = max(0, ix - context_width)
        context_end = ix + token_width + context_width

        df = df[(df.index >= context_start) & (df.index < context_end)]
        time_lst.append((datetime.now().timestamp(), "limiting rows"))

        # create a list of all token ids that are also listed in the results
        # table:
        template = "{lower} < coquery_invisible_corpus_id < {upper}"
        tab = options.cfg.main_window.Session.data_table.query(
                template.format(lower=token_id - 1000,
                                upper=token_id + 1000 + token_width))

        time_lst.append((datetime.now().timestamp(), "retrieving ids"))
        self.id_start_list = tab["coquery_invisible_corpus_id"]
        self.id_end_list = (self.id_start_list +
                            tab["coquery_invisible_number_of_tokens"] - 1)

        time_lst.append((datetime.now().timestamp(), "creating id lists"))
        context = self.parse_df(df, tags, token_id, token_width)

        time_lst.append((datetime.now().timestamp(), "parsing dataframe"))
        s = collapse_words(context, self.resource.get_language())
        time_lst.append((datetime.now().timestamp(), "collapsing words"))
        if s is None:
            s = ""
        else:
            s = s.replace("</p>", "</p>\n")
            s = s.replace("<br/>", "<br/>\n")
        time_lst.append((datetime.now().timestamp(), "fixing breaks"))

        lst = [(t1 - t2, stage) for ((t1, stage), (t2, _)) in
               list(zip(time_lst[1:], time_lst[:-1]))]

        Print("\n".join(
            ["{}: {:6.1f} ms ({})".format(i, 1000 * x, stage)
             for i, (x, stage) in enumerate(lst)]))
        Print("Total: {:6.1f} ms".format(
            1000 * (time_lst[-1][0] - time_lst[0][0])))

        audio = self.resource.audio_features != []
        start_time = None
        end_time = None

        if audio:
            try:
                start_time = df.coq_word_starttime_1.min()
                end_time = df.coq_word_endtime_1.max()
            except Exception as e:
                print(e)
                raise e

        return {"text": s, "df": df,
                "audio": audio,
                "start_time": start_time, "end_time": end_time}

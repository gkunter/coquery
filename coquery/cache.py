# -*- coding: utf-8 -*-
"""
cache.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import os
import cachetools
import logging
import sys
import shutil


try:
    import cPickle as pickle
except ImportError:
    import pickle

from . import options, NAME


class CoqQueryCache(object):
    def __init__(self, read_cache=False):
        self._cache = None
        self._backup = None
        if read_cache:
            path = os.path.join(options.cfg.cache_path, "coq_cache.db")
            if os.path.exists(path):
                try:
                    self._cache = pickle.load(open(path, "rb"))
                    s = "Using query cache (current size: {}, max size: {})."
                    if options.cfg.verbose:
                        s = s.format(self._cache.currsize, self._cache.maxsize)
                        logger.info(s)
                        print(s)
                except (IOError, ValueError, EOFError):
                    S = "Cannot read query cache, creating a new one (size: {})."
                    S = S.format(options.cfg.query_cache_size)
                    logger.warning(S)

        if self._cache is None:
            self._cache = cachetools.LFUCache(
                maxsize=options.cfg.query_cache_size,
                getsizeof=sys.getsizeof)

    def add(self, key, x):
        # if enabled, cache data frame
        if options.cfg.use_cache:
            size = sys.getsizeof(x)

            # do not attempt to cache overly large data frames:
            if size > self._cache.maxsize:
                S = ("Query result too large for the query cache ({} MBytes"
                     "missing).")
                S = S.format((size - self._cache.maxsize) // (1024*1024))
                logger.warning(S)

            # remove items from cache if necessary:
            while self._cache.currsize + size > self._cache.maxsize:
                self._cache.popitem()

            # add data frame to cache
            self._cache[key] = x

            self._backup = None

    def get(self, key):
        return self._cache[key]

    def resize(self, newsize):
        new_cache = cachetools.LFUCache(
            maxsize=newsize,
            getsizeof=sys.getsizeof)
        cached = [self._cache.popitem() for x in range(len(self._cache))]
        for key, val in cached:
            if sys.getsizeof(val) + new_cache.currsize <= new_cache.maxsize:
                new_cache[key] = val
        self._cache = new_cache

    def size(self):
        return self._cache.currsize

    def clear(self):
        self._backup = self._cache
        self._cache = cachetools.LFUCache(
            maxsize=self._backup.maxsize,
            getsizeof=sys.getsizeof)

    def restore(self):
        self._cache = self._backup
        self._backup = None

    def has_backup(self):
        return self._backup is not None

    def save(self):
        if not os.path.exists(options.cfg.cache_path):
            os.makedirs(options.cfg.cache_path)
        file_name = os.path.join(options.cfg.cache_path, "coq_cache.db")
        pickle.dump(self._cache, open(file_name, "wb"))

    def move(self, new_path):
        shutil.move(os.path.join(options.cfg.cache_path, "coq_cache.db"),
                    os.path.join(new_path, "coq_cache.db"))


logger = logging.getLogger(NAME)

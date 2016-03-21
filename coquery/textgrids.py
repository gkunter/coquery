# -*- coding: utf-8 -*-
"""
textgrids.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import collections
import warnings
import os

import tgt

from . import options
from .unicode import utf8

class TextgridWriter(object):
    def __init__(self, df, resource):
        self.df = df
        self.resource = resource
        self._artificial_corpus_id = False

    def get_file_data(self):
        file_data = self.resource.corpus.get_file_data(
            self.df.coquery_invisible_corpus_id, ["file_name", "file_duration"])
        file_data.reset_index(drop=True, inplace=True)
        return file_data
        
    def prepare_textgrids(self):
        grids = {}
        
        self.file_data = self.get_file_data()
        self.feature_timing = dict()
        for f in self.file_data[self.resource.file_name]:
            grids[f] = tgt.TextGrid()

        #
        # for feature in selected_features:
        #   if feature is not timing:
        #       grids.add_tier(IntervalTier(feature))
        #   # get timing sources for feature:
        #   path = get_table_path(feature)
        #   for table in path:
        #       if table in timed_tables:
        #           feature_timing = table_timing

        if ("corpus_starttime" in options.cfg.selected_features and 
            "corpus_endtime" in options.cfg.selected_features):
            self.feature_timing["corpus_id"] = ("corpus_starttime", "corpus_endtime")

        for rc_feature in options.cfg.selected_features:
            _, db_name, tab, feature = self.resource.split_resource_feature(rc_feature)

            if db_name != self.resource.db_name:
                for link, linked_feature in options.cfg.external_links:
                    if linked_feature == "{}_{}".format(tab, feature):
                        external_tab = tab
                        _, _, tab, _ = self.resource.split_resource_feature(link.key_feature)
                        break

            # determine the table that contains timing information by 
            # following the table path:
            self.resource.lexicon.joined_tables = ["corpus"]
            self.resource.lexicon.table_list = ["corpus"]
            self.resource.lexicon.add_table_path("corpus_id", "{}_id".format(tab))

            for current_tab in self.resource.lexicon.joined_tables:
                # check if timing information has been selected for the 
                # current table from the table path:
                start_label = "{}_starttime".format(current_tab)
                end_label = "{}_endtime".format(current_tab)

                # if so, set the timing entry for the current feature 
                # to these timings:
                if (start_label in options.cfg.selected_features and 
                    end_label in options.cfg.selected_features) and not (
                        rc_feature.endswith(("endtime", "starttime"))):
                    self.feature_timing[rc_feature] = (start_label, end_label)
            
            rc_feat = "{}_{}".format(tab, feature)
            if db_name != self.resource.db_name:
                tier_name = "{}.{}_{}".format(db_name, external_tab, feature)
            else:
                tier_name = rc_feat
            if not (rc_feat == start_label or rc_feat == end_label):
                # ... but only if it is not containing timing information
                for x in grids:
                    grids[x].add_tier(tgt.IntervalTier(name=tier_name))

        # if there is no tier in the grids, but the corpus times were 
        # selected, add a tier for the corpus IDs in all grids:
        if not (grids[list(grids.keys())[0]].tiers) and ("corpus_starttime" in options.cfg.selected_features and "corpus_endtime" in options.cfg.selected_features) and not self._artificial_corpus_id:
            self._artificial_corpus_id = True
            for f in grids:
                grids[f].add_tier(tgt.IntervalTier(name="corpus_id"))
        return grids

    def fill_grids(self):
        """
        Fill the grids required for the data frame.
        
        Filling is done by iterating over the rows in the data frame. For
        each row, an interval is added to the tier corresponding to the 
        columns of the data frame. 
        """
        grids = self.prepare_textgrids()
        file_data = self.get_file_data()

        for i in self.df.index:
            row = self.df.loc[i]
            
            # get grid for the file containing this token:
            file_index = row["coquery_invisible_corpus_id"]
            file_name = file_data[file_data[self.resource.corpus_id] == file_index][self.resource.file_name].values[0]
            grid = grids[file_name]
            
            # set all tiers to the durations stored in the file table.
            file_duration = file_data[file_data[self.resource.corpus_id] == file_index][self.resource.file_duration].values[0]
            for tier in grid.tiers:
                tier.end_time = file_duration
            
            for col in self.df.columns:
                # add the corpus IDs if no real feature is selected:
                if col == "coquery_invisible_corpus_id" and self._artificial_corpus_id:
                    rc_feature = "corpus_id"
                else:
                    # special treatment of columns from linked tables:
                    # handle external columns:
                    if "$" in col:
                        db_name, column = col.split("$")
                        external_db = db_name.partition("coq_")[-1]
                        external_feature, _, number = column.rpartition("_")
                        for link, link_feature in options.cfg.external_links:
                            if link_feature == external_feature:
                                rc_feature = link.key_feature
                                break
                    else:
                        s = col.partition("coq_")[-1]
                        rc_feature, _, number = s.rpartition("_")
                if rc_feature:
                    if not hasattr(self.resource, rc_feature):
                        logger.warn("Textgrid export not possible for column {}".format(col))
                    else:
                        _, db_name, tab, feature = self.resource.split_resource_feature(rc_feature)
                        rc_feat = "{}_{}".format(tab, feature)
                        
                        # special tier name for external columns:
                        if "$" in col:
                            tier_name = "{}.{}".format(external_db, external_feature)
                        else:
                            tier_name = rc_feat
                        if not rc_feat.endswith(("_starttime", "_endtime")):
                            if rc_feat in [x for x, _ in self.resource.get_corpus_features()] and not self.resource.is_tokenized(rc_feat):
                                tier = grid.get_tier_by_name(tier_name)
                                start = 0
                                end = tier.end_time
                                content = utf8(row[col])
                                interval = tgt.Interval(start, end, content)
                                if len(tier.intervals) == 0:
                                    grid.get_tier_by_name(tier_name).add_interval(interval)
                            else:
                                start_label, end_label = self.feature_timing[rc_feat]
                                start = row["coq_{}_{}".format(start_label, number)]
                                end = row["coq_{}_{}".format(end_label, number)]
                                content = row[col]
                                if rc_feature == "corpus_id":
                                    content = utf8(int(content))
                                else:
                                    content = utf8(content)
                                interval = tgt.Interval(start, end, content)
                                try:
                                    grid.get_tier_by_name(tier_name).add_interval(interval)
                                except ValueError as e:
                                    # ValueErrors occur if the new interval 
                                    # overlaps with a previous interval. This
                                    # can happen if the boundaries are not 
                                    # exactly aligned. It also happens, and 
                                    # this is absolutely harmless, if the 
                                    # data frame contains multiple rows per 
                                    # token, e.g. because the token is
                                    # segmented.
                                    # Anyway. in this case, the overlapping
                                    # interval is discarded silently:
                                    pass

            grids[file_name] = grid

        return grids
    
    def write_grids(self, path):
        grids = self.fill_grids()
        
        for x in grids:
            grid = grids[x]
            for i, tier in enumerate(grid.tiers):
                _, db_name, tab, feature = self.resource.split_resource_feature(tier.name)
                if db_name != self.resource.db_name:
                    for res in options.cfg.current_resources:
                        resource, _, _, _ = options.cfg.current_resources[res]
                        if resource.db_name == db_name:
                            external_feature = "{}_{}".format(tab, feature) 
                            name = getattr(resource, external_feature)
                            tier_name = "{}.{}".format(resource.name, name)
                            grid.tiers[i].name = tier_name
                            break
                else:
                    tier.name = getattr(self.resource, tier.name, tier.name)
            filename, ext = os.path.splitext(os.path.basename(x))
            tgt.write_to_file(grid, os.path.join(path, "{}.TextGrid".format(filename)))
        return len(grids)
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
import logging

import tgt

from . import options
from . import defines
from .links import get_by_hash
from .unicode import utf8

class TextgridWriter(object):
    def __init__(self, df, resource):
        self.df = df
        self.resource = resource
        self._artificial_corpus_id = False
        self._offsets = {}

    def get_file_data(self):
        file_data = self.resource.corpus.get_file_data(
            self.df.coquery_invisible_corpus_id, ["file_name", "file_duration"])
        file_data.reset_index(drop=True, inplace=True)
        return file_data
        
    def prepare_textgrids(self, order=None, one_grid_per_match=False):
        """
        Parameters
        ----------
        order: list 
            A list of columns that specifies the order of the text grid tiers.
        """
        self.feature_timing = dict()
        self.file_data = self.get_file_data()

        grids = {}
        
        if one_grid_per_match:
            for i in self.file_data.index:
                row = self.file_data.iloc[i][[self.resource.file_name, self.resource.corpus_id]]
                grids[tuple(row)] = tgt.TextGrid()
        else:
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

        if order:
            features = [x.rpartition("coq_")[-1].rpartition("_")[0] for x in order]
        else:
            features = options.cfg.selected_features

        tiers = set([])
        for rc_feature in [x for x in features if not x.startswith(("func_", "coquery_"))]:
            _, hashed, tab, feature = self.resource.split_resource_feature(rc_feature)

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
            if hashed != None:
                link, res = get_by_hash(hashed)
                tier_name = "{}.{}_{}".format(res.db_name, link.rc_to)
            else:
                tier_name = rc_feat
            if not (rc_feat == start_label or rc_feat == end_label) and not tier_name in tiers:
                # ... but only if it is not containing timing information
                for x in grids:
                    grids[x].add_tier(tgt.IntervalTier(name=tier_name))
                    tiers.add(tier_name)

        session = options.cfg.main_window.Session
        for func in [x for x in features if x.startswith("func")]:
            tier_name = session.translate_header(func)
            for x in grids:
                grids[x].add_tier(tgt.IntervalTier(name=tier_name))
                tiers.add(tier_name)

        # if there is no tier in the grids, but the corpus times were 
        # selected, add a tier for the corpus IDs in all grids:
        if not (grids[list(grids.keys())[0]].tiers) and ("corpus_starttime" in options.cfg.selected_features and "corpus_endtime" in options.cfg.selected_features) and not self._artificial_corpus_id:
            self._artificial_corpus_id = True
            for f in grids:
                grids[f].add_tier(tgt.IntervalTier(name="corpus_id"))
        return grids

    def fill_grids(self, columns=None, one_grid_per_match=False, sound_path=""):
        """
        Fill the grids required for the data frame.
        
        Filling is done by iterating over the rows in the data frame. For
        each row, an interval is added to the tier corresponding to the 
        columns of the data frame. 
        
        Parameters
        ----------
        order: list 
            A list of columns that specifies the order of the text grid tiers.
        """
        grids = self.prepare_textgrids(columns, one_grid_per_match)
        file_data = self.get_file_data()

        session = options.cfg.main_window.Session

        for i in self.df.index:
            row = self.df.loc[i]
            
            # get grid for the file containing this token:
            ix = row["coquery_invisible_corpus_id"]
            file_data_row = file_data[file_data[self.resource.corpus_id] == ix]
            
            if one_grid_per_match:
                # one text grid per match that covers only the span of
                # the match
                if sound_path:
                    # If sound_path is set, the text grid writer will also try
                    # to extract the sound bits from the recording that 
                    # contain the matches. These extract will be saved to the 
                    # output path as WAV files. As WAV files always start at 
                    # 0.0, the starting time of the matches will be stripped 
                    # from the text grids.
                    offset = row[[ix for ix in row.index if "_starttime_" in ix]].min()
                    end_time = row[[ix for ix in row.index if "_endtime_" in ix]].max() - offset
                else:
                    end_time = file_data[file_data[self.resource.corpus_id] == ix][self.resource.file_duration].values[0]
                grid_id = tuple(file_data_row[[self.resource.file_name, self.resource.corpus_id]].values[0])
                grid = grids[grid_id]
            else:
                # one text grid that covers the whole recording, with all 
                # matches from that recording as intervals:
                offset = 0
                end_time = file_data[file_data[self.resource.corpus_id] == ix][self.resource.file_duration].values[0]
                grid_id = file_data_row[self.resource.file_name].values[0]
                grid = grids[grid_id]
            
            self._offsets[grid_id] = offset
            
            for tier in grid.tiers:
                tier.start_time = 0
                tier.end_time = end_time
            
            for col in self.df.columns:
                # add the corpus IDs if no real feature is selected:
                if col == "coquery_invisible_corpus_id" and self._artificial_corpus_id:
                    rc_feature = "corpus_id"
                # Handle functions
                elif col.startswith("func_"):
                    rc_feature = None
                    value = row[col]
                    interval = tgt.Interval(0, tier.end_time, utf8(value))
                    tier_name = session.translate_header(col)
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
                                # corpus feature -- add one interval that 
                                # covers the whole text grid
                                tier = grid.get_tier_by_name(tier_name)
                                start = 0
                                end = tier.end_time
                                content = utf8(row[col])
                                interval = tgt.Interval(start, end, content)
                                if len(tier.intervals) == 0:
                                    grid.get_tier_by_name(tier_name).add_interval(interval)
                            else:
                                # lexical feature -- add one interval per 
                                # entry
                                try:
                                    start_label, end_label = self.feature_timing[rc_feat]
                                    start = row["coq_{}_{}".format(start_label, number)]
                                    end = row["coq_{}_{}".format(end_label, number)]
                                except KeyError:
                                    # this is raised e.g. if the boundary 
                                    # output columns are currently not 
                                    # selected

                                    # FIXME:
                                    # functions need to look up their 
                                    # boundaries from the columns they work on

                                    start = 0
                                    end = tier.end_time
                                content = row[col]
                                if rc_feature == "corpus_id":
                                    content = utf8(int(content))
                                else:
                                    content = utf8(content)
                                interval = tgt.Interval(start - offset, end - offset, content)
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

            grids[grid_id] = grid

        return grids
    
    def write_grids(self, output_path, columns, one_grid_per_match, sound_path, left_padding, right_padding):
        self.output_path = output_path
        grids = self.fill_grids(columns, one_grid_per_match, sound_path)
        print(self._offsets)
        
        textgrids = collections.defaultdict(list)
        
        for x in grids:
            grid = grids[x]
            for i, tier in enumerate(grid.tiers):
                _, hashed, tab, feature = self.resource.split_resource_feature(tier.name)
                if hashed != None:
                    link, res = get_by_hash(hashed)
                    tier_name = "{}.{}".format(
                        res.name, 
                        get_attr(res, "{}_{}".format(tab, feature)))
                else:
                    tier.name = getattr(self.resource, tier.name, tier.name)
            if one_grid_per_match:
                match_fn, match_id = x
                basename, _ = os.path.splitext(os.path.basename(match_fn))
                filename = "{}_id{}".format(basename, match_id)
            else:
                basename, _ = os.path.splitext(os.path.basename(x))
                filename = basename
            tgt.write_to_file(grid, os.path.join(output_path, "{}.TextGrid".format(filename)))
            textgrids[basename].append((grid, filename, self._offsets[x]))
            
        sound_files = {}
        if sound_path:
            import wave
            from . import sound
            
            for root, _, files in os.walk(sound_path):
                for file_name in files:
                    basename, _ = os.path.splitext(file_name)
                    if basename in textgrids:
                        for grid, grid_name, offset in textgrids[basename]:
                            try:
                                sound.extract_sound(os.path.join(root, file_name),
                                                    os.path.join(output_path, "{}.wav".format(grid_name)),
                                                    offset,
                                                    offset + grid.end_time)
                            except wave.Error:
                                pass
                
        self.n = len(grids)
    
logger = logging.getLogger("Coquery")

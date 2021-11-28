# -*- coding: utf-8 -*-
"""
textgrids.py is part of Coquery.

Copyright (c) 2016-2021 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import collections
import os
import logging

import tgt

from . import options
from .links import get_by_hash
from .unicode import utf8


class TextgridWriter(object):
    def __init__(self, df, session):
        self.df = df
        self.resource = session.Resource
        self.session = session
        self._artificial_corpus_id = False
        self._offsets = {}
        self._file_data = None

    @property
    def file_data(self):
        if self._file_data is None:
            self._file_data = self.resource.get_file_data(
                self.df.coquery_invisible_corpus_id,
                ["file_name", "file_duration"])
        return self._file_data.reset_index(drop=True)

    def prepare_textgrids(self, order=None, one_grid_per_match=False,
                          remember_time=False):
        """
        Parameters
        ----------
        order: list
            A list of columns that specifies the order of the text grid tiers.
        """
        self.feature_timing = dict()
        grids = {}

        if "coquery_invisible_origin_id" not in self.df.columns:
            one_grid_per_match = True

        if one_grid_per_match:
            key_columns = [self.resource.file_name, self.resource.corpus_id]
        else:
            key_columns = [self.resource.file_name]

        for i in self.file_data.index:
            grid_id = tuple(self.file_data.iloc[i][key_columns])
            grids[grid_id] = tgt.TextGrid()

        if ("corpus_starttime" in options.cfg.selected_features and
                "corpus_endtime" in options.cfg.selected_features):
            self.feature_timing["corpus_id"] = ("corpus_starttime",
                                                "corpus_endtime")

        if order:
            features = []
            for column in order:
                if column.startswith("coq_"):
                    name = column.rpartition("coq_")[-1].rpartition("_")[0]
                else:
                    name = column
                if (name not in features and
                        not name.startswith("coquery_invisible")):

                    features.append(name)
        else:
            features = options.cfg.selected_features

        tiers = set([])
        for rc_feature in [x for x in features
                           if not x.startswith(("func_", "coquery_", "db_"))]:
            hashed, tab, feature = (
                self.resource.split_resource_feature(rc_feature))

            if tab == "segment":
                # the segment table is hard-wired:
                start_label = f"{tab}_starttime"
                end_label = f"{tab}_endtime"
                self.feature_timing[rc_feature] = (start_label, end_label)
            else:
                # determine the table that contains timing information by
                # following the table path:
                self.resource.joined_tables = ["corpus"]
                self.resource.table_list = ["corpus"]
                self.resource.add_table_path("corpus_id", f"{tab}_id")

                for current_tab in self.resource.joined_tables:
                    # check if timing information has been selected for the
                    # current table from the table path:
                    start_label = f"{current_tab}_starttime"
                    end_label = f"{current_tab}_endtime"

                    # if so, set the timing entry for the current feature
                    # to these timings:
                    if (not rc_feature.endswith(("endtime", "starttime")) and
                            start_label in options.cfg.selected_features and
                            end_label in options.cfg.selected_features):
                        self.feature_timing[rc_feature] = (start_label,
                                                           end_label)

            rc_feat = f"{tab}_{feature}"
            if hashed is not None:
                link, res = get_by_hash(hashed)
                # FIXME: the tier name for external fields is wrong!
                tier_name = f"{res.db_name}.{link.rc_to}_{link.rc_to}"
            else:
                tier_name = rc_feat
            if (rc_feat not in [start_label, end_label] and
                    tier_name not in tiers):

                # ... but only if it is not containing timing information
                for x in grids:
                    grids[x].add_tier(tgt.IntervalTier(name=tier_name))
                    tiers.add(tier_name)

        for col in [x for x in features
                    if x.startswith(("func", "coquery", "db"))]:
            # FIXME:
            # db and func columns are never treated as lexicalized columns.
            # The fix for this is probably not quite trivial.
            tier_name = self.session.translate_header(col)
            for x in grids:
                grids[x].add_tier(tgt.IntervalTier(name=tier_name))
                tiers.add(tier_name)

        # if there is no tier in the grids, but the corpus times were
        # selected, add a tier for the corpus IDs in all grids:
        if (not (grids[list(grids.keys())[0]].tiers) and
                ("corpus_starttime" in options.cfg.selected_features and
                 "corpus_endtime" in options.cfg.selected_features) and
                not self._artificial_corpus_id):
            self._artificial_corpus_id = True
            for f in grids:
                grids[f].add_tier(tgt.IntervalTier(name="corpus_id"))
        if remember_time:
            for f in grids:
                grids[f].add_tier(tgt.PointTier(name="Original timing"))

        return grids

    def process_dataframe(self, df, grid, offset, end_time, left_padding,
                          right_padding, remember_time, grid_id):
        """
        Fill the grid by using the content of the data frame.
        """
        corpus_features = [x for x, _ in self.resource.get_corpus_features()]

        data_columns = [x for x in df.columns
                        if "_starttime_" not in x and "_endtime_" not in x]

        max_stop = end_time + left_padding + right_padding

        for col in data_columns:
            interval = None
            # add the corpus IDs if no real feature is selected:
            if col == "coquery_invisible_corpus_id":
                if self._artificial_corpus_id:
                    tier_name = "corpus_id"
                else:
                    continue
                number = 1
            elif col.startswith("coquery_invisible"):
                continue
            elif col.startswith(("func", "coquery", "db")):
                tier_name = self.session.translate_header(col)
            else:
                s = col.partition("coq_")[-1]
                rc_feature, _, number = s.rpartition("_")
                _, tab, feature = (
                    self.resource.split_resource_feature(rc_feature))
                tier_name = f"{tab}_{feature}"

            tier = grid.get_tier_by_name(tier_name)
            if (not tier_name.startswith("segment") and
                    tier_name in corpus_features and
                    not self.resource.is_tokenized(tier_name)):
                # corpus feature -- add one interval that
                # covers the whole text grid
                content = utf8(df[col].values[0])
                stop = max_stop
                interval = tgt.Interval(0, stop, content)
                if len(tier.intervals) == 0:
                    tier.add_interval(interval)
            else:
                if not tier_name.startswith("segment"):
                    # lexical feature -- add one interval per entry
                    for i in df.index:
                        row = df.loc[i]
                        dtype = df.dtypes[col]
                        try:
                            val = utf8(row[col].astype(dtype))
                        except AttributeError:
                            val = utf8(row[col])
                        try:
                            label_s, label_e = self.feature_timing[tier_name]
                            start_col = f"coq_{label_s}_{number}"
                            end_col = f"coq_{label_e}_{number}"
                            start = left_padding - offset + row[start_col]
                            stop = left_padding - offset + row[end_col]
                        except KeyError:
                            start = 0
                            stop = max_stop

                        interval = tgt.Interval(start, stop, val)
                        try:
                            tier.add_interval(interval)
                        except ValueError:
                            # ValueErrors occur if the new interval overlaps
                            # with a previous interval.
                            # This can happen if no word boundaries are
                            # selected in a multi-word query.
                            pass
                else:
                    # segment features
                    start_label, end_label = self.feature_timing[tier_name]
                    start_col = f"coq_{start_label}_1"
                    end_col = f"coq_{end_label}_1"
                    for i in df.index:
                        row = df.loc[i]
                        val = utf8(row[col])
                        try:
                            start = row[start_col]
                            end = row[end_col]
                        except KeyError:
                            start = 0
                            end = end_time

                        interval = tgt.Interval(
                            left_padding - offset + start,
                            left_padding - offset + end,
                            val)
                        try:
                            tier.add_interval(interval)
                        except ValueError as e:
                            logging.warning("{}: {} ({})".format(
                                self.session.translate_header(tier.name),
                                e, grid_id))
            if interval:
                # make sure that the tier is always correctly padded to the
                # right:
                tier.end_time = max(tier.end_time,
                                    interval.end_time + right_padding)
                tier.end_time = min(tier.end_time, max_stop)

        if remember_time:
            tier = grid.get_tier_by_name("Original timing")
            str_start = utf8(offset - left_padding)
            str_end = utf8(offset + grid.end_time - left_padding)
            tier.add_point(tgt.Point(0, str_start))
            tier.add_point(tgt.Point(grid.end_time, str_end))

        return grid

    def fill_grids(self, columns=None, one_grid_per_match=False,
                   sound_path="", left_padding=0, right_padding=0,
                   remember_time=False):
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
        grids = self.prepare_textgrids(columns,
                                       one_grid_per_match, remember_time)

        if "coquery_invisible_origin_id" not in self.df.columns:
            one_grid_per_match = True

        if one_grid_per_match:
            grouped = self.df.groupby("coquery_invisible_corpus_id")
        else:
            grouped = self.df.groupby("coquery_invisible_origin_id")

        for key, match_df in grouped:
            if one_grid_per_match:
                corpus_id = key
            else:
                corpus_id = match_df["coquery_invisible_corpus_id"].values[0]

            f_row = self.file_data[
                self.file_data[self.resource.corpus_id] == corpus_id]

            start_columns = [x for x in match_df.columns if "starttime_" in x]
            end_columns = [x for x in match_df.columns if "endtime_" in x]

            if sound_path and start_columns and end_columns:
                offset = match_df[start_columns].values.min()
                end_time = match_df[end_columns].values.max() - offset
            else:
                offset = 0
                end_time = f_row[self.resource.file_duration].values[0]

            if one_grid_per_match:
                key_columns = [self.resource.file_name,
                               self.resource.corpus_id]
            else:
                key_columns = [self.resource.file_name]

            grid_id = tuple(f_row[key_columns].values[0])
            grid = grids[grid_id]
            grids[grid_id] = self.process_dataframe(
                match_df, grid, offset, end_time,
                left_padding, right_padding, remember_time, grid_id)

            self._offsets[grid_id] = offset

        return grids

    def write_grids(self, output_path, columns, one_grid_per_match,
                    sound_path, left_padding, right_padding, remember_time,
                    file_prefix):
        if "coquery_invisible_origin_id" not in self.df.columns:
            one_grid_per_match = True

        self.output_path = output_path
        grids = self.fill_grids(columns, one_grid_per_match, sound_path,
                                left_padding, right_padding, remember_time)

        textgrids = collections.defaultdict(list)

        self.n = 0

        for x in grids:
            grid = grids[x]
            for i, tier in enumerate(grid.tiers):
                try:
                    tup = self.resource.split_resource_feature(tier.name)
                    hashed, tab, feature = tup

                    if hashed is not None:
                        link, res = get_by_hash(hashed)
                        label = getattr(res, f"{tab}_{feature}")
                        tier.name = f"{res.name}.{label}"
                    else:
                        # try to retrieve a resource label for the tier name:
                        tier.name = getattr(self.resource, tier.name)
                except (ValueError, AttributeError):
                    # Failed to retrieve the tier name. This may happen if
                    # it's not a resource feature name, but for example an
                    # entry from the Query output branch.
                    pass

            if one_grid_per_match:
                match_fn, match_id = x
                basename, _ = os.path.splitext(os.path.basename(match_fn))
                filename = f"{basename}_id{match_id}"
            else:
                match_fn, = x
                basename, _ = os.path.splitext(os.path.basename(match_fn))
                filename = basename
            target = os.path.join(output_path,
                                  f"{file_prefix}{filename}.TextGrid")
            tgt.write_to_file(grid, target)
            self.n += 1
            textgrids[basename].append((grid, filename, self._offsets[x]))

        if sound_path:
            from .sound import Sound

            for root, _, files in os.walk(sound_path):
                for file_name in files:
                    basename, _ = os.path.splitext(file_name)
                    sources = self.resource.audio_to_source(basename)
                    for source in sources:
                        if source in textgrids:
                            source_path = os.path.join(root, file_name)

                            try:
                                sound = Sound(source_path)
                            except TypeError:
                                continue

                            for tup in textgrids.get(source, []):
                                grid, grid_name, offs = tup
                                wav_name = f"{file_prefix}{grid_name}.wav"
                                dest_path = os.path.join(output_path, wav_name)

                                start = max(0, offs - left_padding)
                                end = offs - left_padding + grid.end_time

                                sound.write(dest_path, start, end)

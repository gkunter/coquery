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

import tgt

import options
from unicode import utf8

#def write_to_textgrid(df, resource, filename):
    #"""
    #Evaluate the data frame, and export the timing information to a Praat
    #text grid.
    
    #Parameters
    #----------
    #df : pandas.DataFrame
        #A data frame constructed by a corpus query
    #resource : corpus.SQLResource
        #A resource with resource features
    #filename : string 
        #The file name of the textgrid
    #"""
    
    #lexicon_features = resource.get_lexicon_features()
    #corpus_features = resource.get_corpus_features()
    
    #all_features = [rc_feat for rc_feat, _ in resource.get_resource_features()]
    
    ## keep stock of tables that contain timing information. The keys in the
    ## dictionary are the tables, the values are tuple
    #timed_tables = []
    #lexicon_tables = []
    #corpus_tables = []
    
    #grid = tgt.TextGrid()
    #for rc_feature in options.cfg.selected_features:
        #_, db_name, tab, feature = resource.split_resource_feature(rc_feature)
        #if db_name == resource.db_name:
            #if feature == "starttime" and "{}_endtime".format(tab) in all_features:
                #timed_tables.append("{}_table".format(tab))
                #grid.tiers.append(tgt.IntervalTier(getattr(resource, tab)))
            
    #grid.write_textgrid(filename)

class TextgridWriter(object):
    def __init__(self, df, resource):
        self.df = df
        self.resource = resource
        self.dur_label = "{}.{}".format(self.resource.file_table, self.resource.file_duration)
        self.name_label = "{}.{}".format(self.resource.file_table, self.resource.file_label)
        self.corpus_id = "{}.{}".format(self.resource.corpus_table, self.resource.corpus_id)
        self._artificial_corpus_id = False

    def get_file_data(self):
        file_data = self.resource.corpus.get_file_data(
            self.df.coquery_invisible_corpus_id, ["file_label", "file_duration"])
        file_data.reset_index(drop=True, inplace=True)
        return file_data
        
    def prepare_textgrids(self):
        #all_features = [rc_feat for rc_feat, _ in self.resource.get_resource_features()]

        #all_features = self.resource.get_resource_features()

        #lexicon_features = self.resource.get_lexicon_features()
        #corpus_features = self.resource.get_corpus_features()


        # keep stock of tables that contain timing information. The keys in the
        # dictionary are the tables, the values are tuple

        grids = {}
        
        self.file_data = self.get_file_data()
        self.feature_timing = dict()
        
        for f in self.file_data[self.name_label]:
            grids[f] = tgt.TextGrid()

        #file_ids = self.df.apply(lambda x: self.resource.get_file_id(x["coquery_invisible_corpus_id"]), axis=1).unique()

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
                continue

            # determine the table that contains timing information by 
            # following the table path:
            self.resource.lexicon.joined_tables = ["corpus"]
            self.resource.lexicon.table_list = ["corpus"]
            self.resource.lexicon.add_table_path("corpus_id", "{}_id".format(tab))

            for current_tab in self.resource.lexicon.table_list:
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
            
            # add an interval tier to all text grids for this feature...
            rc_feat = "{}_{}".format(tab, feature)
            if not (rc_feat == start_label or rc_feat == end_label):
                # ... but only if it is not containing timing information
                for x in grids:
                    grids[x].add_tier(tgt.IntervalTier(name=rc_feat))

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
            row = self.df.iloc[i]
            
            # get grid for the file containing this token:
            file_index = row["coquery_invisible_corpus_id"]
            file_name = file_data[file_data[self.corpus_id] == file_index][self.name_label].values[0]
            grid = grids[file_name]
            
            # set all tiers to the durations stored in the file table.
            file_duration = file_data[file_data[self.corpus_id] == file_index][self.dur_label].values[0]
            for tier in grid.tiers:
                tier.end_time = file_duration
            
            for col in self.df.columns:
                # add the corpus IDs if no real feature is selected:
                if col == "coquery_invisible_corpus_id" and self._artificial_corpus_id:
                    rc_feature = "corpus_id"
                else:
                    s = col.partition("coq_")[-1]
                    rc_feature, _, number = s.rpartition("_")
                if rc_feature:
                    if not hasattr(self.resource, rc_feature):
                        warnings.warn("Textgrid export not possible for column {}".format(col))
                    else:
                        _, db_name, tab, feature = self.resource.split_resource_feature(rc_feature)
                        rc_feat = "{}_{}".format(tab, feature)
                        
                        if not rc_feat.endswith(("_starttime", "_endtime")):
                            start_label, end_label = self.feature_timing[rc_feat]
                            start = row["coq_{}_{}".format(start_label, number)]
                            end = row["coq_{}_{}".format(end_label, number)]
                            content = row[col]
                            
                            if rc_feature == "corpus_id":
                                content = utf8(int(content))
                            else:
                                content = utf8(content)
                            interval = tgt.Interval(start, end, content)
                            grid.get_tier_by_name(rc_feat).add_interval(interval)

            grids[file_name] = grid

        return grids
    
    def write_grids(self, path):
        grids = fill_grids(self)
        
        for x in grids:
            grid = grids[x]
            for tier in grid.tiers:
                tier.name = getattr(self.resource, tier.name)
            filename, ext = os.path.splitext(x)
            tgt.write_to_file(grid, os.path.join(path, "{}.TextGrid".format(filename)))
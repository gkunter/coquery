# -*- coding: utf-8 -*-
"""
beeswarmplot.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import seaborn as sns
import numpy as np
import pandas as pd

from coquery.visualizer import barcodeplot


class BeeswarmPlot(barcodeplot.BarcodePlot):
    axes_style = "whitegrid"
    name = "Beeswarm plot"
    icon = "Beeswarm_plot"

    def draw_tokens(self, *args, rug=None, **kwargs):
        return sns.swarmplot(*args, **kwargs)

    def _determine_limits(self):
        if self.horizontal:
            keys = ("ylim", "xlim")
            lim = (-1, 0 + len(self.levels_y or [""]))
        else:
            keys = ("xlim", "ylim")
            lim = (-1, 0 + len(self.levels_x or [""]))
        return keys, lim

    def _extract_data(self, coll, column):
        if self.horizontal:
            lst = [x for (x, _) in coll.get_offsets()]
        else:
            lst = [y for (_, y) in coll.get_offsets()]

        data = pd.Series(np.rint(lst), dtype=int)
        return pd.DataFrame(data=data, columns=[column])

    def get_tick_params(self):
        if self.horizontal:
            keys = ("yticks", "yticklabels")
            order = self.levels_y[::-1] or [""]
        else:
            keys = ("xticks", "xticklabels")
            order = self.levels_x or [""]

        return dict(zip(keys,
                        (np.arange(len(order)), order)))

updated_to_new_interface = True
provided_visualizations = [BeeswarmPlot]

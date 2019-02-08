# -*- coding: utf-8 -*-
"""
beeswarmplot.py is part of Coquery.

Copyright (c) 2016-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function

import seaborn as sns
import pandas as pd

from coquery.visualizer import barcodeplot


class BeeswarmPlot(barcodeplot.BarcodePlot):
    axes_style = "whitegrid"
    name = "Beeswarm plot"
    icon = "Beeswarm_plot"

    def draw_tokens(self, *args, **kwargs):
        return sns.swarmplot(*args, **kwargs)

    def _extract_data(self, coll, column):
        if self.horizontal:
            lst = [x for (x, _) in coll.get_offsets()]
        else:
            lst = [y for (_, y) in coll.get_offsets()]

        data = pd.np.rint(lst)
        return pd.DataFrame(data=data, columns=[column])


provided_visualizations = [BeeswarmPlot]

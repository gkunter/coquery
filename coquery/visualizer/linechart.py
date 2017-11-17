# -*- coding: utf-8 -*-
"""
linechart.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from coquery.visualizer import visualizer as vis
import math
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

from coquery.errors import *
from coquery.gui.pyqt_compat import QtWidgets

class LineChart(vis.Visualizer):
    axes_style = "whitegrid"

    def plot_facet(self, data, color, **kwargs):

        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        levels_x = kwargs.get("levels_x")
        levels_y = kwargs.get("levels_y")
        levels_z = kwargs.get("levels_z")

        category = None
        numeric = {}

        if x:
            self._xlab = x
            if data.dtypes[x] == object:
                category = x
            else:
                numeric = x
                self._ylab = x

        if y:
            self._ylab = y
            if data.dtypes[y] == object:
                category = y
            else:
                numeric = y
                self._ylab = y

        if z and data.dtypes[z] == object:
            hue = data[z]
            levels = levels_z
        else:
            hue = [1] * len(data)
            levels = ["no hue"]

        if category:
            col = sns.color_palette(kwargs.get("palette"),
                                    n_colors=len(levels))[::-1]
            sns.pointplot(x=x, y=y, hue=hue, data=data, palette=col)
        else:
            col = sns.color_palette(kwargs.get("palette"),
                                    n_colors=len(levels))
            self._xlab = "Index"
            sns.pointplot(x=list(range(len(data))),
                          y=data[numeric],
                          hue=hue,
                          palette=col)

        if z and data.dtypes[z] == object:
            self.legend_title = z
            self.legend_levels = levels_z


    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) != 1:
            return False

        if len(cat) > 2:
            return False
        return True

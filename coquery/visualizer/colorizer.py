# -*- coding: utf-8 -*-
"""
colorizer.py is part of Coquery.

Copyright (c) 2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import pandas as pd
import seaborn as sns

from coquery.gui.pyqt_compat import QtCore
from coquery.defines import PALETTE_BW
from coquery import options


class Colorizer(QtCore.QObject):
    def __init__(self, palette, ncol, values=None):
        self.palette = palette
        self.ncol = ncol
        self.values = values

    def get_palette(self):
        base, _, rev = self.palette.partition("_")

        if base == PALETTE_BW:
            col = ([(0, 0, 0), (1, 1, 1)] * (1 + self.ncol // 2))[:self.ncol]
        else:
            col = sns.color_palette(base, self.ncol)

        if rev:
            col = col[::-1]

        return col

    def get_hues(self, data=None, n=None):
        base, _, rev = self.palette.partition("_")
        if data is not None:
            n = len(data)
        return (self.get_palette() * ((n // self.ncol) + 1))[:n]

    def legend_title(self, z):
        return ""

    def legend_palette(self):
        return self.get_palette()

    def legend_levels(self):
        return list(self.values)


class ColorizeByFactor(Colorizer):
    def get_hues(self, data):
        hues = super(ColorizeByFactor, self).get_hues(data)
        return [hues[self.values.index(val)] for val in data]

    def legend_title(self, z):
        return "Most frequent {z}".format(z=z)


class ColorizeByNum(Colorizer):
    def __init__(self, palette, ncol, vmin, vmax, dtype):
        super(ColorizeByNum, self).__init__(palette, ncol)
        self.vmin = vmin
        self.vmax = vmax
        self.dtype = dtype
        self.bins = pd.np.linspace(self.vmin, self.vmax,
                                   self.ncol,
                                   endpoint=False)

    def get_hues(self, data):
        hues = super(ColorizeByNum, self).get_hues(n=self.ncol)[::-1]
        binned = pd.np.digitize(data, self.bins, right=False) - 1
        return [hues[val] for val in binned]

    def legend_title(self, z):
        return z

    def legend_levels(self):
        if self.dtype == int:
            frm_str = "{:.0f}"
        else:
            frm_str = options.cfg.float_format
        print(frm_str)
        return ["≥ {}".format(frm_str.format(x)) for x in self.bins][::-1]


class ColorizeByFreq(Colorizer):
    def get_hues(self, data):
        self.bins = pd.np.linspace(data.min(), data.max(),
                                   self.ncol,
                                   endpoint=False)
        hues = super(ColorizeByFreq, self).get_hues(n=self.ncol)
        binned = pd.np.digitize(data, self.bins, right=False) - 1
        return [hues[val] for val in binned]

    def legend_title(self, z):
        return ""

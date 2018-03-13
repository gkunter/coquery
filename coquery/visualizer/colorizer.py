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

from coquery.gui.pyqt_compat import QtCore, QtGui
from coquery.defines import PALETTE_BW
from coquery.general import pretty
from coquery import options


COQ_SINGLE = "COQSINGLE"


class Colorizer(QtCore.QObject):
    def __init__(self, palette, ncol, values=None):
        self.palette = palette
        self.ncol = ncol
        self.values = values
        self._title_frm = ""

    def get_palette(self):
        base, _, rev = self.palette.partition("_")

        if base == PALETTE_BW:
            col = ([(0, 0, 0), (1, 1, 1)] * (1 + self.ncol // 2))[:self.ncol]
        elif base == COQ_SINGLE:
            color = QtGui.QColor(rev)
            col = [tuple(x / 255 for x in color.getRgb()[:-1])] * self.ncol
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
        return self._title_frm.format(z=z)

    def legend_palette(self):
        return []

    def legend_levels(self):
        return []

    def set_title_frm(self, s):
        self._title_frm = s


class ColorizeByFactor(Colorizer):
    def __init__(self, palette, ncol, values):
        super(ColorizeByFactor, self).__init__(palette, ncol, values)
        self.set_title_frm("{z}")

    def get_hues(self, data):
        pal = self.get_palette()
        color_indices = [self.values.index(val) % len(pal) for val in data]
        return [pal[ix] for ix in color_indices]

    def legend_palette(self):
        n = len(self.values)
        pal = self.get_palette()
        return (pal * ((n // len(pal)) + 1))[:n]

    def legend_levels(self):
        return self.values


class ColorizeByNum(Colorizer):
    def __init__(self, palette, ncol, vrange, dtype):
        super(ColorizeByNum, self).__init__(palette, ncol)
        self.dtype = dtype
        self.bins = pretty(vrange, ncol)
        self.set_title_frm("{z}")

    def get_hues(self, data):
        hues = super(ColorizeByNum, self).get_hues(n=self.ncol)[::-1]
        binned = pd.np.digitize(data, self.bins, right=False) - 1
        return [hues[val] for val in binned]

    def legend_levels(self):
        if self.dtype == int:
            frm_str = "{:.0f}"
        else:
            frm_str = options.cfg.float_format
        return ["≥ {}".format(frm_str.format(x)) for x in self.bins][::-1]


class ColorizeByFreq(Colorizer):
    def get_hues(self, data):
        self.bins = pd.np.linspace(data.min(), data.max(),
                                   self.ncol,
                                   endpoint=False)
        hues = super(ColorizeByFreq, self).get_hues(n=self.ncol)
        binned = pd.np.digitize(data, self.bins, right=False) - 1
        return [hues[val] for val in binned]

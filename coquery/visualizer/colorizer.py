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
        self._entry_frm = "{val}"

    def get_palette(self, n=None):
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

        if n:
            col = (col * (1 + n // len(col)))[:n]

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

    def set_entry_frm(self, s):
        self._entry_frm = s


class ColorizeByFactor(Colorizer):
    def __init__(self, palette, ncol, values):
        super(ColorizeByFactor, self).__init__(palette, ncol, values)
        self.set_title_frm("{z}")

    def get_hues(self, data=None, n=None):
        if data is None:
            data = (self.values * self.ncol)[:n]

        pal = self.get_palette()
        color_indices = [self.values.index(val) % len(pal) for val in data]
        hues = [pal[ix] for ix in color_indices]
        return hues

    def legend_palette(self):
        n = len(self.values)
        pal = self.get_palette()
        return (pal * ((n // len(pal)) + 1))[:n]

    def legend_levels(self):
        return [self._entry_frm.format(val=x) for x in self.values]


class ColorizeByNum(Colorizer):
    def __init__(self, palette, ncol, values, vrange=None):
        super(ColorizeByNum, self).__init__(palette, ncol, values)

        if not vrange:
            vmin, vmax = values.min(), values.max()
        else:
            vmin, vmax = vrange

        self.dtype = values.dtype

        self._direct_mapping = (len(values) <= ncol and
                                len(values) == len(values.unique()))

        if self._direct_mapping:
            self.bins = sorted(values)
            self.set_entry_frm("{val}")
        else:
            self.bins = pretty((vmin, vmax), ncol)
            self.set_entry_frm("≥ {val}")

        self.set_title_frm("{z}")

    def set_entry_frm(self, s):
        self._entry_frm = s

    def get_hues(self, data):
        hues = super(ColorizeByNum, self).get_hues(n=self.ncol)

        if not self._direct_mapping:
            hues = hues[::-1]

        binned = pd.np.digitize(data, self.bins, right=False) - 1
        return [hues[val] for val in binned]

    def legend_palette(self):
        return self.get_palette()

    def legend_levels(self):
        if self.dtype == int:
            frm_str = "{:.0f}"
        else:
            frm_str = options.cfg.float_format

        l = [self._entry_frm.format(val=frm_str.format(x))
             for x in self.bins]

        if len(self.values) <= self.ncol:
            return l
        else:
            return l[::-1]

class ColorizeByFreq(Colorizer):
    def get_hues(self, data):
        self.bins = pd.np.linspace(data.min(), data.max(),
                                   self.ncol,
                                   endpoint=False)
        hues = super(ColorizeByFreq, self).get_hues(n=self.ncol)
        binned = pd.np.digitize(data, self.bins, right=False) - 1
        return [hues[val] for val in binned]

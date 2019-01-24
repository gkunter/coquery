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
COQ_CUSTOM = "COQCUSTOM"


class Colorizer(QtCore.QObject):
    def __init__(self, palette, ncol, values=None):
        # FIXME: ncol is obsolete now.
        super(Colorizer, self).__init__()
        self.palette = palette
        self.ncol = ncol
        self.values = values
        self._title_frm = ""
        self._entry_frm = "{val}"
        self._reversed = False

    def update(self, palette, color_number, **kwargs):
        self.palette = palette
        self.ncol = color_number

    def get_palette(self, n=None):
        """
        Return the palette values used by the current visualizer.

        NEW BEHAVIOR:
        Instead of calculating the palette based on a palette name and the
        number of colors, colorizers now use a predefined palette that is
        passed on to them during initialization.

        This makes it possible to deal with non-standard and custom palettes.

        Arguments
        ---------
        n : int
            The number of palette values that is requested. If n is larger
            than the number of entries in the current palette, the palette is
            recylced.

        Returns
        -------
        lst : list
            A list of tuples containing Matplotlib color specifications.
        """

        col = self.palette

        if n:
            col = (col * (1 + n // len(col)))[:n]

        return col

    def set_reversed(self, rev):
        self._reversed = rev

    def get_hues(self, data):
        n = len(data)
        pal = self.get_palette()
        if self._reversed:
            pal = pal[::-1]
        return (pal * ((n // self.ncol) + 1))[:n]

    @staticmethod
    def hex_to_rgb(l):
        return [(int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))
                for s in l]

    @staticmethod
    def rgb_to_hex(l):
        return ["#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))
                for r, g, b in l]

    @staticmethod
    def rgb_to_mpt(l):
        return [(r / 255, g / 255, b / 255) for r, g, b in l]

    @staticmethod
    def mpt_to_rgb(l):
        return [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in l]

    @staticmethod
    def hex_to_mpt(l):
        return Colorizer.rgb_to_mpt(Colorizer.hex_to_rgb(l))

    @staticmethod
    def mpt_to_hex(l):
        return Colorizer.rgb_to_hex(Colorizer.mpt_to_rgb(l))

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

    def get_hues(self, data):
        pal = self.get_palette()
        color_indices = [self.values.index(val) % len(pal)
                         if not pd.isnull(val) else None
                         for val in data]
        hues = [pal[ix] if not pd.isnull(ix) else None
                for ix in color_indices]
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
            # Use direct mapping if there are not more categories than
            # colors
            self.bins = sorted(values)
            self.set_entry_frm("{val}")
        else:
            self.bins = pretty((vmin, vmax), ncol)
            self.set_entry_frm("≥ {val}")
            #self.set_entry_frm("> {val}")

        self.set_title_frm("{z}")

    def set_entry_frm(self, s):
        self._entry_frm = s

    def get_hues(self, data):
        pal = self.get_palette(n=self.ncol)

        if not self._direct_mapping:
            pal = pal[::-1]

        binned = pd.np.digitize(data, self.bins, right=False) - 1
        return [pal[val] for val in binned]

    def legend_palette(self):
        return self.get_palette()

    def legend_levels(self):
        if self.dtype == int:
            frm_str = "{:.0f}"
        else:
            frm_str = options.cfg.float_format

        lst = [self._entry_frm.format(val=frm_str.format(x))
               for x in self.bins]

        if len(self.values) <= self.ncol:
            return lst
        else:
            return lst[::-1]


class ColorizeByFreq(Colorizer):
    def get_hues(self, data):
        self.bins = pd.np.linspace(data.min(), data.max(),
                                   self.ncol,
                                   endpoint=False)
        pal = self.get_palette(n=self.ncol)
        binned = pd.np.digitize(data, self.bins, right=False) - 1
        return [pal[val] for val in binned]

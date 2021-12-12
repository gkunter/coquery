# -*- coding: utf-8 -*-
"""
colorizer.py is part of Coquery.

Copyright (c) 2018–2021 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import pandas as pd
import numpy as np

from coquery.gui.pyqt_compat import QtCore
from coquery.general import pretty, recycle
from coquery import options


COQ_SINGLE = "COQSINGLE"
COQ_CUSTOM = "COQCUSTOM"


class Colorizer(QtCore.QObject):
    def __init__(self, palette):
        super().__init__()
        self.palette = palette
        self._title_frm = ""
        self._entry_frm = "{val}"

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
        palette : list
            A list of tuples containing Matplotlib color specifications.
        """
        if n:
            return recycle(self.palette, n)

        return self.palette

    def get_hues(self, data, ncol=None):
        ncol = ncol or len(self.palette)
        return recycle(self.palette, len(data), ncol)

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

    @staticmethod
    def hex_to_rgb(lst):
        return [(int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))
                for s in lst]

    @staticmethod
    def rgb_to_hex(lst):
        return [f"#{int(r):02x}{int(g):02x}{int(b):02x}" for r, g, b in lst]

    @staticmethod
    def rgb_to_mpt(lst):
        return [(r / 255, g / 255, b / 255) for r, g, b in lst]

    @staticmethod
    def mpt_to_rgb(lst):
        return [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in lst]

    @staticmethod
    def hex_to_mpt(lst):
        return Colorizer.rgb_to_mpt(Colorizer.hex_to_rgb(lst))

    @staticmethod
    def mpt_to_hex(lst):
        return Colorizer.rgb_to_hex(Colorizer.mpt_to_rgb(lst))


class ColorizeByFactor(Colorizer):
    def __init__(self, palette, values):
        super().__init__(palette)
        self.values = values
        self.set_title_frm("{z}")

    def get_hues(self, data, ncol=None):
        pal = self.get_palette()
        color_indices = [self.values.index(val) % len(pal)
                         if not pd.isnull(val) else None
                         for val in data]
        hues = [pal[ix] if not pd.isnull(ix) else None
                for ix in color_indices]
        return hues

    def legend_palette(self):
        return recycle(self.palette, len(self.values))

    def legend_levels(self):
        return [self._entry_frm.format(val=x) for x in self.values]


class ColorizeByNum(Colorizer):
    def __init__(self, palette, vrange):
        super().__init__(palette)
        self.vrange = vrange
        self.set_title_frm("{z}")
        self.dtype = None

    def set_entry_frm(self, s):
        self._entry_frm = s

    def get_hues(self, data, ncol=None):
        self.dtype = data.dtype
        ncol = len(self.palette)
        vmin, vmax = self.vrange

        self._direct_mapping = (len(data) <= ncol and
                                len(data) == len(data.unique()))

        if self._direct_mapping:
            # Use direct mapping if there are not more categories than
            # colors
            self.bins = sorted(data)
            self.set_entry_frm("{val}")
        else:
            self.bins = pretty((vmin, vmax), ncol)
            self.set_entry_frm("≥ {val}")

        self.binned = np.digitize(data, self.bins, right=False) - 1
        pal = self.palette
        return [pal[val] for val in self.binned]

    def legend_palette(self):
        return self.palette

    def legend_levels(self):
        msg = "Colorizer hasn't been used yet. No legend levels are available."
        assert self.dtype, msg
        if self.dtype == int:
            frm_str = "{:.0f}"
        else:
            frm_str = options.cfg.float_format

        lst = [self._entry_frm.format(val=frm_str.format(x))
               for x in self.bins]

        return lst[::-1]


class ColorizeByFreq(Colorizer):
    def get_hues(self, data, ncol=None):
        self.bins = np.linspace(data.min(), data.max(),
                                ncol,
                                endpoint=False)
        pal = self.get_palette(n=ncol)
        binned = np.digitize(data, self.bins, right=False) - 1
        return [pal[val] for val in binned]

# -*- coding: utf-8 -*-
"""
barcodeplot.py is part of Coquery.

Copyright (c) 2016-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import matplotlib.pyplot as plt
import pandas as pd

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets, QtCore, tr


class BarcodePlot(vis.Visualizer):
    axes_style = "white"
    TOP = 0.975
    BOTTOM = 0.025
    COLOR = None

    name = "Barcode plot"
    icon = "Barcode_plot"

    DEFAULT_LABEL = "Corpus position"

    force_horizontal = True

    def get_custom_widgets(self, *args, **kwargs):
        label = tr("BarcodePlot", "Plot horizontal by default", None)

        self.check_horizontal = QtWidgets.QCheckBox(label)
        self.check_horizontal.setCheckState(
            QtCore.Qt.Checked if self.force_horizontal else
            QtCore.Qt.Unchecked)

        return ([self.check_horizontal],
                [self.check_horizontal.stateChanged],
                [])

    def update_values(self):
        self.force_horizontal = self.check_horizontal.isChecked()

    def draw_tokens(self, x, y, order, rug=None):
        if self.horizontal:
            _func = plt.vlines
        else:
            _func = plt.hlines

        order = order or [""]

        if x.dtype != object:
            numeric, categorical = x, y
        else:
            numeric, categorical = y, x
            order = order[::-1]

        for i, level in enumerate(order):
            pos = len(order) - i - 1
            if not rug:
                values = numeric[categorical == level]
                lower = [pos + self.BOTTOM] * len(values)
                upper = [pos + self.TOP] * len(values)
            else:
                values = numeric[categorical == level].repeat(2)
                lower = [pos, pos + 0.9] * len(values)
                upper = [pos + 0.1, pos + 1] * len(values)
            _func(values, upper, lower)

    def _extract_data(self, coll, column):
        if self.horizontal:
            lst = [x for (x, _), (_, _) in coll.get_segments()]
        else:
            lst = [y for (_, y), (_, _) in coll.get_segments()]
        data = pd.np.rint(lst)
        return pd.DataFrame(data=data, columns=[column])

    def prepare_arguments(self, data, x, y, z, levels_x, levels_y, **kwargs):
        data = data.sort_values(by=self._id_column).reset_index(drop=True)
        values = self.get_id_values(data)
        if x and not y:
            X, Y, Ord = data[x], values, levels_x
        elif y and not x:
            X, Y, Ord = values, data[y], levels_y
        else:
            # see https://github.com/mwaskom/seaborn/issues/1343 for the
            # rationale behind using a dummy variable
            grouping = pd.Series([""] * len(data))
            if self.force_horizontal:
                X, Y, Ord = values, grouping, None
            else:
                X, Y, Ord = grouping, values, None
        if z:
            Z = data[z]
        else:
            Z = None

        horizontal = values.equals(X)
        dct = {"x": X, "y": Y, "z": Z,
               "order": Ord, "horizontal": horizontal}
        return dct

    def plot_facet(self, **kwargs):
        self.horizontal = kwargs["horizontal"]
        self.draw_tokens(kwargs["x"], kwargs["y"], order=kwargs["order"],
                         rug=kwargs.get("rug"))
        return plt.gca().collections

    def get_colors(self, colorizer, elements, **kwargs):
        if kwargs["horizontal"]:
            values = kwargs["x"]
        else:
            values = kwargs["y"]
        if kwargs["z"] is not None:
            colors = colorizer.get_hues(kwargs["z"])
        else:
            colors = colorizer.get_hues(values, ncol=1)

        df_col = pd.DataFrame({self._id_column: values,
                               "Z": kwargs["z"],
                               "COQ_COLOR": colorizer.mpt_to_hex(colors)})
        lst = []
        for collection in elements:
            df = self._extract_data(collection, self._id_column)
            df = df.merge(df_col, on=self._id_column, how="left")
            lst.append(df["COQ_COLOR"].values.tolist())
        return lst

    def colorize_elements(self, elements, colors):
        for collection, cols in zip(elements, colors):
            collection.set_color(cols)

    def suggest_legend(self):
        return self.z != self.x and self.z != self.y

    def get_factor_frm(self):
        return self.get_default_frm()

    def get_num_frm(self):
        return self.get_default_frm()

    def get_tick_params(self):
        if self.horizontal:
            keys = ("yticks", "yticklabels")
            order = self.levels_y or [""]
        else:
            keys = ("xticks", "xticklabels")
            order = self.levels_x or [""]

        return dict(zip(keys,
                        (0.5 + pd.np.arange(len(order)), order)))

    def set_limits(self, grid, values):
        if self.horizontal:
            keys = ("ylim", "xlim")
            lim = (0, len(self.levels_y or [""]))
        else:
            keys = ("xlim", "ylim")
            lim = (0, len(self.levels_x or [""]))
        grid.set(**dict(
            zip(keys, (lim, self._limiter_fnc(self.df, None, None)))))

    def set_annotations(self, grid, values):
        grid.set(**self.get_tick_params())
        super(BarcodePlot, self).set_annotations(grid, values)

    def set_titles(self, **kwargs):
        self._xlab = self.x or ""
        self._ylab = self.y or ""

        if kwargs["horizontal"]:
            self._xlab = self.DEFAULT_LABEL
        else:
            self._ylab = self.DEFAULT_LABEL

    def get_subordinated(self, x, y):
        return None

    @staticmethod
    def validate_data(data_x, data_y, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, df, session)

        if len(df) == 0:
            return False

        if len(num) > 0 or len(cat) > 1:
            return False
        return True


provided_visualizations = [BarcodePlot]

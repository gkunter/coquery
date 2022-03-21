# -*- coding: utf-8 -*-
"""
barcodeplot.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5 import QtWidgets, QtCore

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from coquery.visualizer import visualizer as vis
from coquery.gui.visualizationdesigner import tr

DEFAULT_LABEL = tr("BarcodePlot", "Corpus position", None)

LABEL_HORIZONTAL = tr("BarcodePlot",
                      "Draw horizontal barcode if no axis is specified",
                      None)

LABEL_ADJUST = tr("BarcodePlot",
                  "Adjust grid data ranges to subcorpora sizes",
                  None)

RUG_TOP = 0.975
RUG_BOTTOM = 0.025


class BarcodePlot(vis.Visualizer):
    axes_style = "white"

    COLOR = None

    name = tr("BarcodePlot", "Barcode plot", None)
    icon = "Barcode_plot"

    def __init__(self, df, session, id_column=None, limiter_fnc=None):
        super().__init__(df, session, id_column, limiter_fnc)
        self.horizontal = None
        self.adjust_to_subcorpus = True
        self.check_horizontal = None
        self.check_adjust_to_subcorpus = None
        self.force_horizontal = True
        self.column_feature = None
        self.row_feature = None

    def prepare_arguments(self, data, x, y, z, levels_x, levels_y, **kwargs):
        data = data.sort_values(by=self._id_column).reset_index(drop=True)
        values = self.get_id_values(data)
        if x and not y:
            var_x, var_y, var_order = data[x], values, levels_x
        elif y and not x:
            var_x, var_y, var_order = values, data[y], levels_y
        else:
            # see https://github.com/mwaskom/seaborn/issues/1343 for the
            # rationale behind using a dummy variable
            grouping = pd.Series([""] * len(data))
            if self.force_horizontal:
                var_x, var_y, var_order = values, grouping, None
            else:
                var_x, var_y, var_order = grouping, values, None
        if z:
            var_z = data[z]
        else:
            var_z = None

        horizontal = values.equals(var_x)
        dct = {"x": var_x, "y": var_y, "z": var_z,
               "order": var_order, "horizontal": horizontal}
        return dct

    def plot_facet(self, **kwargs):
        """
        Plot the barcode plot by calling draw_tokens() with the arguments
        passed as kwargs. draw_tokens() may be overridden by other visualizers
        such as BeeswarmPlot.

        Parameters
        ----------
        kwargs

        Returns
        -------
        coll : matplotlib.collections.Collection

        """
        self.horizontal = kwargs["horizontal"]
        self.draw_tokens(kwargs["x"], kwargs["y"],
                         order=kwargs["order"],
                         rug=kwargs.get("rug"))

        return plt.gca().collections

    def draw_tokens(self, x, y, order, rug=None, **kwargs):
        if self.horizontal:
            _func = plt.vlines
        else:
            _func = plt.hlines

        order = order or [""]

        if pd.api.types.is_numeric_dtype(x):
            numeric, categorical = x, y
        else:
            numeric, categorical = y, x
            order = order[::-1]
        for i, level in enumerate(order):
            pos = len(order) - i - 1
            if rug:
                values = numeric[categorical == level].repeat(2)
                lower = [pos, pos + 0.9] * len(values)
                upper = [pos + 0.1, pos + 1] * len(values)
            else:
                values = numeric[categorical == level]
                lower = [pos + RUG_BOTTOM] * len(values)
                upper = [pos + RUG_TOP] * len(values)
            _func(values, upper, lower)

    def colorize_elements(self, elements, colors):
        for collection, cols in zip(elements, colors):
            collection.set_color(cols)

    def get_widgets(self, *args, **kwargs):
        self.check_horizontal = QtWidgets.QCheckBox(LABEL_HORIZONTAL)
        self.check_horizontal.setCheckState(
            QtCore.Qt.Checked if self.force_horizontal else
            QtCore.Qt.Unchecked)

        self.check_adjust_to_subcorpus = QtWidgets.QCheckBox(LABEL_ADJUST)
        self.check_adjust_to_subcorpus.setCheckState(
            QtCore.Qt.Checked if self.adjust_to_subcorpus else
            QtCore.Qt.Unchecked)

        return ([self.check_horizontal, self.check_adjust_to_subcorpus],
                [self.check_horizontal.stateChanged,
                 self.check_adjust_to_subcorpus.stateChanged],
                [])

    def update_widget_values(self):
        self.force_horizontal = self.check_horizontal.isChecked()
        self.adjust_to_subcorpus = self.check_adjust_to_subcorpus.isChecked()

    def _extract_data(self, coll, column):
        """
        Returns a data frame containing the coordinate values from the segments
        in the provided collection.

        Parameters
        ----------
        coll : matplotlib.collections.LineCollection
            A collection of line segments
        column : str
            The column name

        Returns
        -------
        df : pd.DataFrame
        """
        if self.horizontal:
            lst = [x for (x, _), (_, _) in coll.get_segments()]
        else:
            lst = [y for (_, y), (_, _) in coll.get_segments()]
        data = pd.Series(np.rint(lst), dtype=int)
        df = pd.DataFrame(data=data, columns=[column])
        return df

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

    def suggest_legend(self):
        return self.z != self.x and self.z != self.y

    def get_factor_frm(self):
        return self.get_default_frm()

    def get_num_frm(self):
        return self.get_default_frm()

    def get_tick_params(self):
        if self.horizontal:
            keys = ("yticks", "yticklabels")
            order = self.levels_y[::-1] or [""]
        else:
            keys = ("xticks", "xticklabels")
            order = self.levels_x or [""]

        return dict(zip(keys,
                        (0.5 + np.arange(len(order)), order)))

    def _determine_limits(self):
        if self.horizontal:
            keys = ("ylim", "xlim")
            lim = (0, len(self.levels_y or [""]))
        else:
            keys = ("xlim", "ylim")
            lim = (0, len(self.levels_x or [""]))
        return keys, lim

    def set_limits(self, grid, values):
        keys, lim = self._determine_limits()
        grid.set(**dict(
            zip(keys, (lim, self._limiter_fnc(self.df, None, None)))))

        columns = values.get("columns")
        rows = values.get("rows")
        if (columns or rows) and self.adjust_to_subcorpus:
            res = self.session.Resource
            for feature, name in res.get_corpus_features():
                if columns and (feature in columns):
                    self.column_feature = feature
                if rows and (feature in rows):
                    self.row_feature = feature

            for ax in grid.fig.axes:
                level = ax.title.get_text()
                filters = []
                if self.column_feature:
                    filters.append((self.column_feature, [level]))
                if self.row_feature:
                    filters.append((self.row_feature, [level]))
                if filters:
                    min_id = res.corpus.get_corpus_statistic(
                        "MIN({})".format(res.corpus_id),
                        filters)
                    max_id = res.corpus.get_corpus_statistic(
                        "MAX({})".format(res.corpus_id),
                        filters)
                    if values.get("x"):
                        ax.set_ylim(min_id, max_id)
                    else:
                        ax.set_xlim(min_id, max_id)

    def set_annotations(self, grid, values):
        grid.set(**self.get_tick_params())
        super().set_annotations(grid, values)

        if self.column_feature:
            for ax in grid.fig.axes:
                ax.get_yaxis().set_visible(True)
                ax.tick_params(labelbottom=True)

    def set_titles(self, **kwargs):
        self._xlab = self.x or ""
        self._ylab = self.y or ""

        if kwargs["horizontal"]:
            self._xlab = DEFAULT_LABEL
        else:
            self._ylab = DEFAULT_LABEL

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

    def get_grid(self, **kwargs):
        values = kwargs.pop("values")

        kwargs["data"] = self.df
        if kwargs.get("col") or kwargs.get("row"):
            if values.get("x"):
                kwargs["sharey"] = False
            elif values.get("y"):
                kwargs["sharex"] = False
        with sns.axes_style(self.axes_style):
            with sns.plotting_context(self.plotting_context):
                grid = sns.FacetGrid(**kwargs)
        return grid


updated_to_new_interface = True
provided_visualizations = [BarcodePlot]

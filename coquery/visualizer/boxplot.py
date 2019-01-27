# -*- coding: utf-8 -*-
"""
boxplot.py is part of Coquery.

Copyright (c) 2017-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets, QtCore, tr


class BoxPlot(vis.Visualizer):
    name = "Box-Whisker plot"
    icon = "Boxplot"

    axes_style = "whitegrid"

    draw_boxen = True

    def get_custom_widgets(self, *args, **kwargs):
        if not hasattr(sns, "boxenplot"):
            return ([], [], [])
        label = tr("BoxPlot", "Draw multiple boxes", None)

        self.check_horizontal = QtWidgets.QCheckBox(label)
        self.check_horizontal.setCheckState(
            QtCore.Qt.Checked if self.draw_boxen else
            QtCore.Qt.Unchecked)

        return ([self.check_horizontal],
                [self.check_horizontal.stateChanged],
                [])

    def update_values(self):
        self.draw_boxen = self.check_horizontal.isChecked()

    def prepare_arguments(self, data, x, y, z, levels_x, levels_y, **kwargs):
        data = data.sort_values(by=self._id_column).reset_index(drop=True)

        if x and y:
            order = levels_x if data[x].dtype == object else levels_y
        else:
            order = None

        dct = {"x": None if not x else data[x],
               "y": None if not y else data[y],
               "order": order}

        return dct

    def get_subordinated(self, x, y):
        return None

    def plot_fnc(self, **kwargs):
        if self._boxen:
            ax = sns.boxenplot(**kwargs)
            return ax.collections
        else:
            ax = sns.boxplot(**kwargs)
            return ax.artists

    def plot_facet(self, **kwargs):
        self._boxen = hasattr(sns, "boxenplot") and self.draw_boxen
        return self.plot_fnc(**kwargs)

    def get_colors(self, colorizer, elements, **kwargs):
        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        order = kwargs.get("order")
        if z:
            # FIXME: determine appropriate colors based on variable
            pass
        else:
            if isinstance(x, pd.Series) and isinstance(y, pd.Series):
                hues = colorizer.get_hues(order)
            else:
                hues = colorizer.get_hues(pd.Series([""]))
        rgb = [colorizer.mpt_to_hex([hue]) for hue in hues]
        return rgb

    def colorize_elements(self, elements, colors):
        if not self._boxen:
            for patch, col in zip(elements, colors):
                patch.set_facecolor(col[0])
        else:
            for coll, col in zip(elements[0::2], colors):
                coll.set_facecolors(col[0])
            for coll, col in zip(elements[1::2], colors):
                cmap = sns.light_palette(col[0], len(coll.get_paths()))
                coll.set_facecolors(cmap)
        plt.gcf().canvas.draw()

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) != 1:
            return False
        if len(cat) > 1:
            return False
        return True


class ViolinPlot(BoxPlot):
    name = "Violin plot"
    icon = "Violinplot"

    def plot_fnc(self, **kwargs):
        return sns.violinplot(**kwargs)


provided_visualizations = [BoxPlot, ViolinPlot]

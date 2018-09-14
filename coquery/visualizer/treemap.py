# -*- coding: utf-8 -*-
"""
treemap.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function

try:
    import squarify
except ImportError:
    # the missing module is handled at the end of this script
    pass

from matplotlib.patches import Rectangle
from matplotlib import pyplot as plt
import seaborn as sns

from coquery.visualizer import visualizer as vis
from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByFreq, ColorizeByNum)

from coquery import options
from coquery.gui.pyqt_compat import QtWidgets, QtCore, tr


class TreeMap(vis.Visualizer):
    name = "Treemap"
    icon = "Scatterplot"
    text_boxes = 70
    text_rotate = False
    box_padding = True
    box_border = False
    box_style = {"boxstyle": "round", "fc": "w", "ec": "0.5", "alpha": 0.7}

    axes_style = "white"

    def get_custom_widgets(self, *args, **kwargs):
        label = tr("TreeMap", "Padding", None)
        self.check_padding = QtWidgets.QCheckBox(label)
        self.check_padding.setCheckState(
            QtCore.Qt.Checked if self.box_padding is not None else
            QtCore.Qt.Unchecked)

        label = tr("TreeMap", "Draw border", None)
        self.check_border = QtWidgets.QCheckBox(label)
        self.check_border.setCheckState(
            QtCore.Qt.Checked if self.box_border else
            QtCore.Qt.Unchecked)

        label = tr("TreeMap", "Draw text boxes", None)
        self.group_transparency = QtWidgets.QGroupBox()
        self.group_transparency.setTitle(label)
        layout_group = QtWidgets.QHBoxLayout()
        self.group_transparency.setLayout(layout_group)
        self.group_transparency.setCheckable(True)
        self.group_transparency.setChecked(self.text_boxes is not None)

        label = tr("TreeMap", "Transparency:", None)
        self.label_transparency = QtWidgets.QLabel(label)
        self.slide_transparency = QtWidgets.QSlider()
        self.slide_transparency.setOrientation(QtCore.Qt.Horizontal)
        self.slide_transparency.setMinimum(0)
        self.slide_transparency.setMaximum(100)
        self.slide_transparency.setSingleStep(5)
        self.slide_transparency.setPageStep(25)
        self.slide_transparency.setTickPosition(
            self.slide_transparency.TicksAbove)
        self.slide_transparency.setValue(self.text_boxes)

        layout_group.addWidget(self.label_transparency)
        layout_group.addWidget(self.slide_transparency)
        layout_group.setStretch(1, 1)
        layout_group.setAlignment(QtCore.Qt.AlignCenter)

        label = tr("TreeMap", "Rotate text", None)
        self.check_rotate = QtWidgets.QCheckBox(label)
        self.check_rotate.setCheckState(
            QtCore.Qt.Checked if self.text_rotate else
            QtCore.Qt.Unchecked)

        hlayout1 = QtWidgets.QHBoxLayout()
        hlayout1.addWidget(self.check_padding)
        hlayout1.addWidget(self.check_border)

        return ([hlayout1, self.check_rotate, self.group_transparency],
                [self.check_padding.stateChanged,
                 self.check_border.stateChanged,
                 self.group_transparency.toggled,
                 self.check_rotate.stateChanged,
                 self.slide_transparency.valueChanged],
                [])

    def update_values(self):
        self.box_border = self.check_border.isChecked()
        self.box_padding = self.check_padding.isChecked()
        if self.slide_transparency.isEnabled():
            self.text_boxes = self.slide_transparency.value()
        else:
            self.text_boxes = None
        self.text_rotate = self.check_rotate.isChecked()

    def transform(self, rect, x, y, dx, dy, padding=1):
        if not self.box_padding:
            return rect

        if (rect["x"] > x and rect["dx"] > padding):
            rect["x"] += padding
            rect["dx"] -= padding

        if (rect["x"] + rect["dx"] < dx - padding and
                rect["dx"] > padding):
            rect["dx"] -= padding

        if (rect["y"] > y and rect["dy"] > padding):
            rect["y"] += padding
            rect["dy"] -= padding

        if (rect["y"] + rect["dy"] < dy - padding and
                rect["dy"] > padding):
            rect["dy"] -= padding

        return rect

    def add_text(self, label, rect):
        x, y, dx, dy = rect["x"], rect["y"], rect["dx"], rect["dy"]
        plt.gca().text(x + dx / 2.0, y + dy / 2.0, label,
                       va="center", ha="center",
                       rotation=90 if self.text_rotate else 0,
                       bbox=self.box_style if self.text_boxes else None)

    def draw_rect(self, rect, col, norm_x, norm_y):
        rect = self.transform(rect, 0, 0, norm_x, norm_y)
        x, y, dx, dy = rect["x"], rect["y"], rect["dx"], rect["dy"]
        patch = Rectangle(
            xy=(x, y),
            width=dx, height=dy,
            facecolor=col,
            edgecolor="black" if self.box_border else "none")
        plt.gca().add_patch(patch)

        if self.text_boxes:
            self.box_style["alpha"] = self.text_boxes / 100

    def get_frm_string(self, S):
        if S.dtype == int:
            return "{:.0f}"
        else:
            return options.cfg.float_format

    def get_rects(self, values, x, y, dx, dy):
        normed = [val * dx * dy / values.sum() for val in values]
        return squarify.squarify(normed, x, y, dx, dy)

    def plot_facet(self, data, color, x=None, y=None, z=None,
                   levels_x=None, levels_y=None, levels_z=None,
                   palette=None, color_number=None, **kwargs):

        def _get_most_frequent(x):
            return x.value_counts().index[0]

        norm_x, norm_y = self.get_figure_size()

        category = None
        numeric = None
        second_category = None

        aggregator = vis.Aggregator()

        if (x and data[x].dtype == object and
                y and data[y].dtype == object):
            category = x
            second_category = y
            numeric = "COQ_FREQ"
            aggregator.add(second_category, "count", name=numeric)
        else:
            if x:
                if data.dtypes[x] == object:
                    category = x
                else:
                    numeric = x

            if y:
                if data.dtypes[y] == object:
                    category = y
                else:
                    numeric = y

            if not numeric:
                numeric = "COQ_FREQ"
                aggregator.add(category, "count", name=numeric)
            else:
                aggregator.add(numeric, "mean")

        # Add hue variable to aggregation:
        if z:
            if z == category:
                hues = numeric
                self._colorizer = ColorizeByFreq(palette, color_number)
            else:
                hues = "COQ_HUE"
                if data[z].dtype == object:
                    fnc = "mode"
                    self._colorizer = ColorizeByFactor(
                        palette, color_number, levels_z)
                else:
                    fnc = "max"
                    self._colorizer = ColorizeByNum(
                        palette, color_number, data[z])
                aggregator.add(z, fnc, name=hues)
        else:
            hues = category
            self._colorizer = Colorizer(palette, color_number,
                                        levels_x or levels_y)
        if second_category:
            df = aggregator.process(data, [category, second_category])
            _df = (df[[category, numeric]].drop_duplicates()
                                          .groupby(category)
                                          .agg({numeric: "sum"})
                                          .reset_index()
                                          .sort_values([numeric, category]))
            values = _df[numeric].values
        else:
            df = aggregator.process(data, category)
            df = df.sort_values([numeric, category])
            values = df[numeric].values

        rects = self.get_rects(values, 0, 0, norm_x, norm_y)

        self._ylab = ""
        self._xlab = category

        self.legend_title = self._colorizer.legend_title(z)
        self.legend_palette = self._colorizer.legend_palette()
        self.legend_levels = self._colorizer.legend_levels()

        if not second_category:
            frm = "{{}}\n{}".format(self.get_frm_string(df[numeric]))
            labels = df.apply(
                lambda row: frm.format(row[category], row[numeric]),
                axis="columns")
            for rect, col in zip(rects,
                                 self._colorizer.get_hues(df[hues])[::-1]):
                self.draw_rect(rect, col, norm_x, norm_y)
            for label, rect in zip(labels, rects):
                self.add_text(label, rect)
        else:
            numeric2 = "COQ_FREQ2"
            frm = "{{}}:{{}}\n{}".format(self.get_frm_string(df[numeric]))

            for rect, xval, col in zip(
                    rects, df[x], self._colorizer.get_hues(df[hues])[::-1]):
                rect = self.transform(rect, 0, 0, norm_x, norm_y)
                rx = rect["x"]
                ry = rect["y"]
                dx = rect["dx"]
                dy = rect["dy"]

                sub_agg = vis.Aggregator()
                sub_agg.add(numeric, "sum", name=numeric2)

                dsub = sub_agg.process(df[df[x] == xval], y)
                values = dsub[numeric2].values
                rsub = self.get_rects(values, 0, 0, dx, dy)
                for sr, yval, count in zip(rsub, dsub[y], values):
                    sr["x"] += rx
                    sr["y"] += ry
                    self.draw_rect(sr, col, rx + dx, ry + dy)
                    # FIXME: The labels don't work as expected
                    self.add_text(frm.format(xval, yval, count), sr)
        ax = plt.gca()
        ax.set(xticklabels=[], xlim=[0, norm_x])
        ax.set(yticklabels=[], ylim=[0, norm_y])
        sns.despine(ax=ax, top=True, bottom=True, left=True, right=True)
        return ax

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 1 or len(cat) == 0:
            return False

        return True

    def suggest_legend(self):
        return self.z


if "squarify" in globals():
    provided_visualizations = [TreeMap]
else:
    provided_visualizations = []

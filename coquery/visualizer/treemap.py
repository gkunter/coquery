""" Tree mapping based on http://hcil.cs.umd.edu/trs/91-03/91-03.html.

Another Python implementation is given here:

http://wiki.scipy.org/Cookbook/Matplotlib/TreeMap

"""

from __future__ import division
from __future__ import print_function

try:
    import squarify
except ModuleNotFoundError:
    # the missing module is handled at the end of this script
    pass

from matplotlib.patches import Rectangle
from matplotlib import pyplot as plt
import seaborn as sns

from coquery.visualizer import visualizer as vis
from coquery.visualizer.colorizer import (
    Colorizer, ColorizeByFactor, ColorizeByFreq, ColorizeByNum)

from coquery import options
from coquery.gui.pyqt_compat import QtWidgets, QtCore


class TreeMap(vis.Visualizer):
    name = "Treemap"
    icon = "Scatterplot"
    text_boxes = True
    text_rotate = False
    box_padding = True
    box_border = False
    box_style = {"boxstyle": "round", "fc": "w", "ec": "0.5", "alpha": 0.7}

    axes_style = "white"

    def __init__(self, *args, **kwargs):
        super(TreeMap, self).__init__(*args, **kwargs)
        self.aggregator = vis.Aggregator()

    def get_custom_widgets(self, *args, **kwargs):
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QApplication.instance().translate(
                    "TreeMap", "Padding", None)
        TreeMap.check_padding = QtWidgets.QCheckBox(label)
        TreeMap.check_padding.setCheckState(
            QtCore.Qt.Checked if TreeMap.box_padding else
            QtCore.Qt.Unchecked)
        TreeMap.check_padding.stateChanged.connect(
            lambda x: TreeMap.button_apply.setEnabled(True))

        label = QtWidgets.QApplication.instance().translate(
                    "TreeMap", "Draw border", None)
        TreeMap.check_border = QtWidgets.QCheckBox(label)
        TreeMap.check_border.setCheckState(
            QtCore.Qt.Checked if TreeMap.box_border else
            QtCore.Qt.Unchecked)
        TreeMap.check_border.stateChanged.connect(
            lambda x: TreeMap.button_apply.setEnabled(True))

        label = QtWidgets.QApplication.instance().translate(
                    "TreeMap", "Draw text boxes", None)
        TreeMap.check_boxes = QtWidgets.QCheckBox(label)
        TreeMap.check_boxes.setCheckState(
            QtCore.Qt.Checked if TreeMap.text_boxes else
            QtCore.Qt.Unchecked)
        TreeMap.check_boxes.stateChanged.connect(
            lambda x: TreeMap.button_apply.setEnabled(True))

        label = QtWidgets.QApplication.instance().translate(
                    "TreeMap", "Rotate text", None)
        TreeMap.check_rotate = QtWidgets.QCheckBox(label)
        TreeMap.check_rotate.setCheckState(
            QtCore.Qt.Checked if TreeMap.text_rotate else
            QtCore.Qt.Unchecked)
        TreeMap.check_rotate.stateChanged.connect(
            lambda x: TreeMap.button_apply.setEnabled(True))

        button = QtWidgets.QApplication.instance().translate(
                    "Visualizer", "Apply", None)
        TreeMap.button_apply = QtWidgets.QPushButton(button)
        TreeMap.button_apply.setDisabled(True)
        TreeMap.button_apply.clicked.connect(
            lambda: TreeMap.update_figure(
                self,
                TreeMap.check_padding.checkState(),
                TreeMap.check_border.checkState(),
                TreeMap.check_boxes.checkState(),
                TreeMap.check_rotate.checkState()))

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(TreeMap.check_padding)
        hlayout.addWidget(TreeMap.check_border)
        hlayout.setStretch(0, 1)
        hlayout.setStretch(1, 1)
        layout.addLayout(hlayout)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(TreeMap.check_boxes)
        hlayout.addWidget(TreeMap.check_rotate)
        hlayout.setStretch(0, 1)
        hlayout.setStretch(1, 1)
        layout.addLayout(hlayout)

        layout.addWidget(TreeMap.button_apply)

        return [layout]

    @classmethod
    def update_figure(cls, self, padding, border, boxes, rotate):
        cls.box_border = bool(border)
        cls.box_padding = bool(padding)
        cls.text_boxes = bool(boxes)
        cls.text_rotate = bool(rotate)
        cls.button_apply.setDisabled(True)
        self.updateRequested.emit()

    def transform(self, rect, x, y, dx, dy):
        if not self.box_padding:
            return rect

        if (rect["x"] > x and rect["dx"] > 1):
            rect["x"] += 1
            rect["dx"] -= 1

        if (rect["x"] + rect["dx"] < dx - 1 and rect["dx"] > 1):
            rect["dx"] -= 1

        if (rect["y"] > y and rect["dy"] > 1):
            rect["y"] += 1
            rect["dy"] -= 1

        if (rect["y"] + rect["dy"] < dy - 1 and rect["dy"] > 1):
            rect["dy"] -= 1

        return rect

    def draw_rect(self, rect, col, label, norm_x, norm_y):
        rect = self.transform(rect, 0, 0, norm_x, norm_y)
        x, y, dx, dy = rect["x"], rect["y"], rect["dx"], rect["dy"]
        patch = Rectangle(
            xy=(x, y),
            width=dx, height=dy,
            facecolor=col,
            edgecolor="black" if self.box_border else "none")
        plt.gca().add_patch(patch)
        plt.gca().text(x + dx / 2.0, y + dy / 2.0, label,
                       va="center", ha="center",
                       rotation=90 if self.text_rotate else 0,
                       bbox=self.box_style if self.text_boxes else None)

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

        if (x and data[x].dtype == object and
                y and data[y].dtype == object):
            category = x
            second_category = y
            numeric = "COQ_FREQ"
            self.aggregator.add(second_category, "count", name=numeric)
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
                self.aggregator.add(category, "count", name=numeric)
            else:
                self.aggregator.add(numeric, "mean")

        if z:
            if z == category:
                hues = numeric
                self._colorizer = ColorizeByFreq(palette, color_number)
            else:
                hues = "COQ_HUE"
                if data[z].dtype == object:
                    fnc = _get_most_frequent
                    self._colorizer = ColorizeByFactor(
                        palette, color_number, levels_z)
                else:
                    fnc = "max"
                    self._colorizer = ColorizeByNum(
                        palette, color_number,
                        data[z].min(), data[z].max(), data[z].dtype)
                self.aggregator.add(z, fnc, name=hues)
        else:
            hues = category
            self._colorizer = Colorizer(palette, color_number,
                                        levels_x or levels_y)
        if second_category:
            df = self.aggregator.process(data, [category, second_category])
            _df = (df[[category, numeric]].drop_duplicates()
                                          .groupby(category)
                                          .agg({numeric: "sum"})
                                          .reset_index()
                                          .sort_values([numeric, category]))
            values = _df[numeric].values
        else:
            df = self.aggregator.process(data, category)
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
            for rect, label, col in zip(rects, labels,
                                        self._colorizer.get_hues(df[hues])):
                self.draw_rect(rect, col, label, norm_x, norm_y)
        else:
            numeric2 = "COQ_FREQ2"
            frm = "{{}}:{{}}\n{}".format(self.get_frm_string(df[numeric]))

            for rect, xval, col in zip(rects, df[x],
                                       self._colorizer.get_hues(df[hues])):
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
                    self.draw_rect(sr, col,
                                   frm.format(xval, yval, count),
                                   rx + dx, ry + dy)

        ax = plt.gca()
        ax.set(xticklabels=[], xlim=[0, norm_x])
        ax.set(yticklabels=[], ylim=[0, norm_y])
        sns.despine(ax=ax, top=True, bottom=True, left=True, right=True)
        return ax

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 1 or len(cat) == 0 or len(cat) > 2:
            return False

        return True


if "squarify" in globals():
    provided_visualizations = [TreeMap]
else:
    provided_visualizations = []

# -*- coding: utf-8 -*-
"""
barcodeplot.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import math

import matplotlib.pyplot as plt
import pandas as pd

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets, QtCore, tr


class BarcodePlot(vis.Visualizer):
    axes_style = "white"
    TOP = 0.975
    BOTTOM = 0.025
    COLOR = None

    NUM_COLUMN = "coquery_invisible_corpus_id"

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

    def prepare_ax_kwargs(self, data, x, y, z, levels_x, levels_y, **kwargs):
        if x and not y:
            ax_kwargs = {
                "xticks": 0.5 + pd.np.arange(len(levels_x)),
                "xticklabels": levels_x,
                "xlim": (0, len(levels_x))}
        elif y and not x:
            ax_kwargs = {
                "yticks": 0.5 + pd.np.arange(len(levels_y)),
                "yticklabels": levels_y[::-1],
                "ylim": (0, len(levels_y))}
        else:
            if self.force_horizontal:
                ax_kwargs = {"yticklabels": []}
            else:
                ax_kwargs = {"xticklabels": []}
        return ax_kwargs

    def prepare_arguments(self, data, x, y, z, levels_x, levels_y, **kwargs):
        if x or y:
            levels = levels_x if x else levels_y[::-1]
            val = data[x or y].apply(lambda val: levels.index(val))
        else:
            # neither x nor y is specified, plot default
            val = pd.Series([0] * len(data), index=data.index)
            levels = [None]

        kwargs = {"values": data[self.NUM_COLUMN], "pos": val}

        if x and not y:
            kwargs["horizontal"] = True
            kwargs["func"] = plt.hlines

        elif y and not x:
            kwargs["horizontal"] = False
            kwargs["func"] = plt.vlines

        else:
            if self.force_horizontal:
                kwargs["horizontal"] = False
                kwargs["func"] = plt.vlines
            else:
                kwargs["horizontal"] = True
                kwargs["func"] = plt.hlines

        return kwargs

    def prepare_colors(self, data, x, y, z, levels_x, levels_y, **kwargs):
        if z:
            cols = self.colorizer.get_hues(data[z])
        else:
            if x:
                levels = levels_x
                rgb = self.colorizer.get_hues(levels)
                cols = data[x].apply(lambda val: rgb[levels.index(val)])
            elif y:
                levels = levels_y[::-1]
                rgb = self.colorizer.get_hues(levels)
                cols = data[y].apply(lambda val: rgb[levels.index(val)])
            else:
                rgb = self.colorizer.get_palette()
                cols = [rgb[0]] * len(data)
        return cols

    def plot_facet(self, data, color, rug=None, **kwargs):
        """
        Plot a barcode plot.

        In a barcode plot, each token is represented by a line drawn at the
        location of the corresponding corpus id.
        """
        params = self.prepare_arguments(data, **kwargs)
        _func = params["func"]
        self.horizontal = params["horizontal"]

        cols = self.prepare_colors(data, **kwargs)

        if rug:
            if "top" in rug:
                _func(params["values"],
                      params["pos"] + 0.9, params["pos"] + 1,
                      cols)
            if "bottom" in rug:
                _func(params["values"],
                      params["pos"], params["pos"] + 0.1,
                      cols)
        else:
            _func(params["values"],
                  params["pos"] + self.BOTTOM, params["pos"] + self.TOP,
                  cols)

        ax = kwargs.get("ax", plt.gca())
        ax_kwargs = self.prepare_ax_kwargs(data, **kwargs)
        ax.set(**ax_kwargs)

    def suggest_legend(self):
        return self.z

    def get_factor_frm(self):
        return self.get_default_frm()

    def get_num_frm(self):
        return self.get_default_frm()

    def set_annotations(self, grid, values):
        lim = (0, self.session.Corpus.get_corpus_size())
        if self.horizontal:
            grid.set(ylim=lim)
        else:
            grid.set(xlim=lim)
        vis.Visualizer.set_annotations(self, grid, values)

    def set_titles(self):
        self._xlab = ""
        self._ylab = ""

        if self.x:
            self._xlab = self.x
            self._ylab = self.DEFAULT_LABEL
        elif self.y:
            self._ylab = self.y
            self._xlab = self.DEFAULT_LABEL
        else:
            if self.horizontal:
                self._ylab = self.DEFAULT_LABEL
            else:
                self._xlab = self.DEFAULT_LABEL

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(df) == 0:
            return False

        if len(num) > 0 or len(cat) > 1:
            return False
        return True


class HeatbarPlot(BarcodePlot):
    """
    Produce a heat bar instead of single bars.
    """

    name = "Heatbar plot"
    icon = "Barcode_plot"

    TOP = 0.05
    BOTTOM = 0.0
    COLOR = "Black"

    bandwidth = None
    plot_rug = False
    normalize = False

    def __init__(self, *args, **kwargs):
        super(HeatbarPlot, self).__init__(*args, **kwargs)

    def get_custom_widgets(self, *args, **kwargs):
        label = tr("HeatbarPlot", "Plot horizontal by default", None)
        bandwidth_text = tr("HeatbarPlot", "Use custom bandwidth:", None)
        suffix_text = tr("HeatbarPlot", " words", None)
        rug_text = tr("HeatbarPlot", "Add coloured rugs", None)
        normalize_text = tr("HeatbarPlot", "Normalize within groups", None)

        self.check_bandwidth = QtWidgets.QCheckBox(bandwidth_text)
        self.spin_bandwidth = QtWidgets.QSpinBox(self.bandwidth)
        self.spin_bandwidth.setDisabled(True)
        self.spin_bandwidth.setSuffix(suffix_text)
        self.spin_bandwidth.setMaximum(99999999)
        self.spin_bandwidth.setMinimum(5)
        self.spin_bandwidth.setSingleStep(1)
        self.layout_bandwidth = QtWidgets.QHBoxLayout()
        self.layout_bandwidth.addWidget(self.check_bandwidth)
        self.layout_bandwidth.addWidget(self.spin_bandwidth)

        self.check_normalize = QtWidgets.QCheckBox(normalize_text)
        self.check_normalize.setCheckState(
            QtCore.Qt.Checked if self.normalize else
            QtCore.Qt.Unchecked)

        self.check_rug = QtWidgets.QCheckBox(rug_text)
        self.check_rug.setCheckState(
            QtCore.Qt.Checked if self.plot_rug else
            QtCore.Qt.Unchecked)

        self.check_horizontal = QtWidgets.QCheckBox(label)
        self.check_horizontal.setCheckState(
            QtCore.Qt.Checked if self.force_horizontal else
            QtCore.Qt.Unchecked)

        return ([self.check_horizontal,
                 self.layout_bandwidth,
                 self.check_rug,
                 self.check_normalize],
                [self.check_horizontal.stateChanged,
                 self.check_bandwidth.stateChanged,
                 self.check_rug.stateChanged,
                 self.check_normalize.stateChanged,
                 self.spin_bandwidth.valueChanged],
                [self.check_bandwidth.stateChanged])

    def update_widgets(self):
        self.spin_bandwidth.setEnabled(self.check_bandwidth.isChecked())

    def update_values(self):
        if self.check_bandwidth.isChecked():
            self.bandwidth = int(self.spin_bandwidth.value())
        else:
            self.bandwidth = None
        self.force_horizontal = self.check_horizontal.isChecked()
        self.plot_rug = self.check_rug.isChecked()
        self.normalize = self.check_normalize.isChecked()

    def increment_bins(self, bins, value, bw):
        """
        Increment the right bins from `bins` containing `value` given the
        bandwidth `bw`.

        A total increment of 1.0 is assigned to one or two bins from the list
        of bins provided. The spread of the increment is determined by the
        position `p` of the value relative to the left edge of the target bin.
        The target bin is defined by `target_bin = value // bin`. The
        relative position `p` is defined as `p = value/bin - target_bin`.

        The following table summarizes the behavior for different values of
        `p`, the relative position of a token id to the beginning of a bin.
        A value of p=0.0 indicates that the token is located at the left edge
        of the target bin, and a value of p=1.0 indicates that the token is
        located at the right edge of the target bin.

        The columns B(-1), B(0), B(+1) give the increments for the target bin
        B(0), the bin preceding the target bin B(-1) and the bin folloowing
        the target bin B(+1).

        The largest increment is added when p=0.5, i.e. when the token is
        located at the center of the bin. In this case, the whole increment is
        given to the target bin, and no spread to a neighboring bin takes
        place. If the token is located at the edge of a bin (p=0.0), the
        increment is spread equally across the preceding bin and the target
        bin.

        ------------------------
          P  B(-1)   B(0)  B(+1)
        ------------------------
        0.0   +0.5   +0.5
        0.1   +0.4   +0.6
        0.2   +0.3   +0.7
        0.3   +0.2   +0.8
        0.4   +0.1   +0.9
        0.5          +1.0
        0.6          +0.9  +0.1
        0.7          +0.8  +0.2
        0.8          +0.7  +0.3
        0.9          +0.6  +0.4
        ------------------------
        """

        pct_in_bin, target_bin = math.modf(value / bw)
        target_bin = int(target_bin)

        if pct_in_bin <= 0.5:
            bins[target_bin] += 0.5 + pct_in_bin
        else:
            bins[target_bin] += 1.5 - pct_in_bin

        if target_bin > 0:
            bins[target_bin - 1] += max(0, 0.5 - pct_in_bin)
        if target_bin < len(bins) - 1:
            bins[target_bin + 1] += max(0, pct_in_bin - 0.5)

        return bins

    def prepare_im_arguments(self, data, x, y, z, levels_x, levels_y,
                             size, bw,
                             **kwargs):
        """
        Returns the arguments required for a subsequent call to plt.imshow().

        The following arguments are produced:

            aspect: "auto"
            interpolation: "gaussian"
            extent: (None, None, 0, MAX) or (0, MAX, None, None) (for
                    horizontal or vertical plots, respectively)

        In addition, the argument `M` is produced, which is a list of arrays
        that contain the image data used by plt.imshow().
        """

        kwargs = {"aspect": "auto", "interpolation": "gaussian"}

        M = []

        if x or y:
            self.horizontal = bool(x)

            for val in levels_x or levels_y:
                binned = pd.np.zeros(1 + (size // bw))
                values = (data[self.NUM_COLUMN][data[x or y] == val]).values
                for i in values:
                    binned = self.increment_bins(binned, i, bw)

                M.append(pd.np.array(binned))
        else:
            self.horizontal = not self.force_horizontal

            binned = pd.np.zeros(1 + (size // bw))
            values = data[self.NUM_COLUMN].values
            for i in values:
                binned = self.increment_bins(binned, i, bw)

            M.append(pd.np.array(binned))

        width = len(binned) * bw - 1
        if x:
            kwargs["extent"] = (None, None, 0, width)
        elif y:
            kwargs["extent"] = (0, width, None, None)
        elif self.force_horizontal:
            kwargs["extent"] = (0, width, None, None)
        else:
            kwargs["extent"] = (None, None, 0, width)

        kwargs["M"] = pd.np.array(M)
        return kwargs

    def set_bandwidth(self, bw):
        self.bandwidth = int(bw)
        self.spin_bandwidth.blockSignals(True)
        self.spin_bandwidth.setValue(bw)
        self.spin_bandwidth.blockSignals(False)

    def plot_facet(self, data, color, **kwargs):
        """
        Plot a HeatBar plot.

        A heatbar plot is like a barcode plot, only that there is also a
        heat map plotted under the lines.
        """

        size = self.session.Corpus.get_corpus_size()
        if not self.bandwidth:
            self.set_bandwidth(max(size / 250, 5))
        param = self.prepare_im_arguments(data, bw=self.bandwidth, size=size,
                                          **kwargs)
        M = param.pop("M")

        left, right, bottom, top = param["extent"]

        if self.normalize:
            M = pd.np.array([[val / max(X) for val in X] for X in M])

        if not self.horizontal:
            M = M[::-1]

        for i, x in enumerate(M):
            if left is None and right is None:
                param["extent"] = (i, i+1, bottom, top)
                x = pd.np.array([x[::-1]]).T
            else:
                param["extent"] = (left, right, i, i+1)
                x = pd.np.array([x])

            plt.imshow(x, vmax=M.max(), **param)

        if self.plot_rug:
            super(HeatbarPlot, self).plot_facet(
                data, color, rug=("top", "bottom"), **kwargs)

        ax = kwargs.get("ax", plt.gca())
        ax_kwargs = self.prepare_ax_kwargs(data, **kwargs)
        ax.set(**ax_kwargs)

        if self.horizontal:
            plt.xlim(0, len(M))
        else:
            plt.ylim(0, len(M))


provided_visualizations = [BarcodePlot, HeatbarPlot]

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
from coquery.gui.pyqt_compat import QtWidgets, QtCore


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
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QApplication.instance().translate(
                    "BarcodePlot", "Plot horizontal by default", None)
        button = QtWidgets.QApplication.instance().translate(
                    "Visualizer", "Apply", None)

        BarcodePlot.check_horizontal = QtWidgets.QCheckBox(label)
        BarcodePlot.check_horizontal.setCheckState(
            QtCore.Qt.Checked if BarcodePlot.force_horizontal else
            QtCore.Qt.Unchecked)

        BarcodePlot.button_apply = QtWidgets.QPushButton(button)
        BarcodePlot.button_apply.setDisabled(True)
        BarcodePlot.button_apply.clicked.connect(
            lambda: BarcodePlot.update_figure(
                self, BarcodePlot.check_horizontal.checkState()))

        BarcodePlot.check_horizontal.stateChanged.connect(
            lambda x: BarcodePlot.button_apply.setEnabled(True))

        layout.addWidget(BarcodePlot.check_horizontal)
        layout.addWidget(BarcodePlot.button_apply)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        self._layout = layout
        return [layout]

    @classmethod
    def update_figure(cls, self, i):
        cls.force_horizontal = bool(i)
        BarcodePlot.button_apply.setDisabled(True)
        self.updateRequested.emit()

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

    custom_bandwidth = None
    plot_rug = False
    normalize = False

    def __init__(self, *args, **kwargs):
        super(HeatbarPlot, self).__init__(*args, **kwargs)

    def get_custom_widgets(self, *args, **kwargs):
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QApplication.instance().translate(
                    "HeatbarPlot", "Plot horizontal by default", None)
        button = QtWidgets.QApplication.instance().translate(
                    "Visualizer", "Apply", None)
        bandwidth_text = QtWidgets.QApplication.instance().translate(
            "HeatbarPlot", "Use custom bandwidth:", None)
        suffix_text = QtWidgets.QApplication.instance().translate(
            "HeatbarPlot", " words", None)
        rug_text = QtWidgets.QApplication.instance().translate(
            "HeatbarPlot", "Add coloured rugs", None)
        normalize_text = QtWidgets.QApplication.instance().translate(
            "HeatbarPlot", "Normalize within groups", None)

        HeatbarPlot.check_bandwidth = QtWidgets.QCheckBox(bandwidth_text)
        HeatbarPlot.spin_bandwidth = QtWidgets.QSpinBox(
            HeatbarPlot.custom_bandwidth)
        HeatbarPlot.spin_bandwidth.setDisabled(True)
        HeatbarPlot.spin_bandwidth.setSuffix(suffix_text)
        HeatbarPlot.spin_bandwidth.setMaximum(99999999)
        HeatbarPlot.spin_bandwidth.setMinimum(5)
        HeatbarPlot.spin_bandwidth.setSingleStep(1)

        spin_layout = QtWidgets.QHBoxLayout()
        spin_layout.addWidget(HeatbarPlot.check_bandwidth)
        spin_layout.addWidget(HeatbarPlot.spin_bandwidth)

        HeatbarPlot.check_normalize = QtWidgets.QCheckBox(normalize_text)
        HeatbarPlot.check_normalize.setCheckState(
            QtCore.Qt.Checked if HeatbarPlot.normalize else
            QtCore.Qt.Unchecked)

        HeatbarPlot.check_rug = QtWidgets.QCheckBox(rug_text)
        HeatbarPlot.check_rug.setCheckState(
            QtCore.Qt.Checked if HeatbarPlot.plot_rug else
            QtCore.Qt.Unchecked)

        HeatbarPlot.check_horizontal = QtWidgets.QCheckBox(label)
        HeatbarPlot.check_horizontal.setCheckState(
            QtCore.Qt.Checked if HeatbarPlot.force_horizontal else
            QtCore.Qt.Unchecked)

        HeatbarPlot.button_apply = QtWidgets.QPushButton(button)
        HeatbarPlot.button_apply.setDisabled(True)
        HeatbarPlot.button_apply.clicked.connect(
            lambda: HeatbarPlot.update_figure(
                self,
                HeatbarPlot.check_horizontal.checkState(),
                None if HeatbarPlot.check_bandwidth.checkState() else
                HeatbarPlot.spin_bandwidth.value()))

        for signal in (HeatbarPlot.check_horizontal.stateChanged,
                       HeatbarPlot.check_bandwidth.stateChanged,
                       HeatbarPlot.check_rug.stateChanged,
                       HeatbarPlot.check_normalize.stateChanged,
                       HeatbarPlot.spin_bandwidth.valueChanged):
            signal.connect(
                lambda x: HeatbarPlot.button_apply.setEnabled(True))
            signal.connect(self.update_widgets)

        layout.addWidget(HeatbarPlot.check_horizontal)
        layout.addLayout(spin_layout)
        layout.addWidget(HeatbarPlot.check_rug)
        layout.addWidget(HeatbarPlot.check_normalize)
        layout.addWidget(HeatbarPlot.button_apply)
        return [layout]

    def update_widgets(self):
        HeatbarPlot.spin_bandwidth.setEnabled(
            HeatbarPlot.check_bandwidth.checkState())
        if HeatbarPlot.check_bandwidth.checkState():
            HeatbarPlot.custom_bandwidth = int(
                HeatbarPlot.spin_bandwidth.value())
        HeatbarPlot.force_horizontal = bool(
            HeatbarPlot.check_horizontal.checkState())

    @classmethod
    def update_figure(cls, self, i, bw):
        HeatbarPlot.button_apply.setDisabled(True)
        self.updateRequested.emit()

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
                binned = [0.0] * (1 + (size // bw))
                values = (data[self.NUM_COLUMN][data[x or y] == val]).values
                for i in sorted(values):
                    pct_in_bin, target_bin = math.modf(i / bw)
                    target_bin = int(target_bin)

                    if pct_in_bin <= 0.5:
                        binned[target_bin] += 0.5 + pct_in_bin
                    else:
                        binned[target_bin] += 1.5 - pct_in_bin

                    if target_bin > 0:
                        binned[target_bin - 1] += max(0, 0.5 - pct_in_bin)
                    if target_bin < len(binned) - 1:
                        binned[target_bin + 1] += max(0, pct_in_bin - 0.5)

                M.append(pd.np.array(binned))
        else:
            self.horizontal = not self.force_horizontal
            values = data[self.NUM_COLUMN].values
            binned = [0.0] * (1 + (size // bw))
            for i in sorted(values):
                pct_in_bin, target_bin = math.modf(i / bw)
                target_bin = int(target_bin)

                if pct_in_bin <= 0.5:
                    binned[target_bin] += 0.5 + pct_in_bin
                else:
                    binned[target_bin] += 1.5 - pct_in_bin

                if target_bin > 0:
                    binned[target_bin - 1] += max(0, 0.5 - pct_in_bin)
                if target_bin < len(binned) - 1:
                    binned[target_bin + 1] += max(0, pct_in_bin - 0.5)

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
        HeatbarPlot.spin_bandwidth.blockSignals(True)
        HeatbarPlot.spin_bandwidth.setValue(bw)
        HeatbarPlot.spin_bandwidth.blockSignals(False)

    def plot_facet(self, data, color, **kwargs):
        """
        Plot a HeatBar plot.

        A heatbar plot is like a barcode plot, only that there is also a
        heat map plotted under the lines.
        """

        size = self.session.Corpus.get_corpus_size()

        if not HeatbarPlot.spin_bandwidth.isEnabled():
            self.set_bandwidth(max(size / 250, 5))

        bw = HeatbarPlot.spin_bandwidth.value()
        param = self.prepare_im_arguments(data, bw=bw, size=size,
                                          **kwargs)

        M = param.pop("M")

        left, right, bottom, top = param["extent"]

        if HeatbarPlot.check_normalize.isChecked():
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

        if HeatbarPlot.check_rug.isChecked():
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

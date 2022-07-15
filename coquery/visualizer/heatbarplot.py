# -*- coding: utf-8 -*-
"""
heatbarplot.py is part of Coquery.

Copyright (c) 2018-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import coquery.visualizer.visualizer as vis
from coquery.visualizer import barcodeplot
from coquery.gui.pyqt_compat import QtWidgets, QtCore, tr


class HeatbarPlot(barcodeplot.BarcodePlot):
    """
    Produce a heat bar instead of single bars.
    """

    name = "Heatbar plot"
    icon = "Barcode_plot"

    TOP = 0.05
    BOTTOM = 0.0
    COLOR = "Black"

    bandwidth = None
    plot_rug = True
    normalize = False

    def __init__(self, df, session, id_column=None, limiter_fnc=None):
        super().__init__(df, session, id_column, limiter_fnc)
        self.layout_bandwidth = None
        self.spin_bandwidth = None
        self.check_bandwidth = None
        self.check_normalize = None
        self.check_horizontal = None
        self.check_rug = None

    def get_widgets(self, *args, **kwargs):
        label = tr("HeatbarPlot", "Plot horizontal by default", None)
        bandwidth_text = tr("HeatbarPlot", "Use custom bandwidth:", None)
        suffix_text = tr("HeatbarPlot", " words", None)
        rug_text = tr("HeatbarPlot", "Add coloured rugs", None)
        normalize_text = tr("HeatbarPlot", "Normalize within groups", None)

        self.check_bandwidth = QtWidgets.QCheckBox(bandwidth_text)
        self.spin_bandwidth = QtWidgets.QSpinBox()
        self.layout_bandwidth = QtWidgets.QHBoxLayout()
        self.check_normalize = QtWidgets.QCheckBox(normalize_text)
        self.check_rug = QtWidgets.QCheckBox(rug_text)
        self.check_horizontal = QtWidgets.QCheckBox(label)

        self.spin_bandwidth.setValue(self.bandwidth or 0)
        self.spin_bandwidth.setDisabled(True)
        self.spin_bandwidth.setSuffix(suffix_text)
        self.spin_bandwidth.setMaximum(99999999)
        self.spin_bandwidth.setMinimum(5)
        self.spin_bandwidth.setSingleStep(1)

        self.layout_bandwidth.addWidget(self.check_bandwidth)
        self.layout_bandwidth.addWidget(self.spin_bandwidth)

        self.check_normalize.setCheckState(
            QtCore.Qt.Checked if self.normalize else
            QtCore.Qt.Unchecked)

        self.check_rug.setCheckState(
            QtCore.Qt.Checked if self.plot_rug else
            QtCore.Qt.Unchecked)

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

    def update_widget_values(self):
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
        B(0), the bin preceding the target bin B(-1) and the bin following
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
            bins[target_bin - 1] += max(0.0, 0.5 - pct_in_bin)
        if target_bin < len(bins) - 1:
            bins[target_bin + 1] += max(0.0, pct_in_bin - 0.5)

        return bins

    def img_arguments(self, data, x, y, z, levels_x, levels_y, size, bw,
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

        m = []
        binned = []

        if self._id_column:
            num_column = data[self._id_column]
        else:
            num_column = pd.Series(data.index)

        if x or y:
            self.horizontal = bool(y)

            for val in levels_x or levels_y:
                binned = np.zeros(1 + (size // bw))
                values = (num_column[data[x or y] == val]).values
                for i in values:
                    binned = self.increment_bins(binned, i, bw)

                m.append(np.array(binned))
        else:
            self.horizontal = self.force_horizontal

            binned = np.zeros(1 + (size // bw))
            values = num_column.values
            for i in values:
                binned = self.increment_bins(binned, i, bw)

            m.append(np.array(binned))

        width = len(binned) * bw - 1
        if x:
            tup = (None, None, 0, width)
        elif y:
            tup = (0, width, None, None)
        elif self.force_horizontal:
            tup = (0, width, None, None)
        else:
            tup = (None, None, 0, width)
        kwargs["extent"] = tup

        kwargs["M"] = np.array(m)
        return kwargs

    def set_bandwidth(self, bw):
        self.bandwidth = int(bw)
        self.spin_bandwidth.blockSignals(True)
        self.spin_bandwidth.setValue(bw)
        self.spin_bandwidth.blockSignals(False)

    def prepare_arguments(self, data, x, y, z, levels_x, levels_y, **kwargs):
        dct = super(HeatbarPlot, self).prepare_arguments(
            data, x, y, z, levels_x, levels_y, **kwargs)

        size = self.session.Corpus.get_corpus_size()
        if not self.bandwidth:
            self.set_bandwidth(max(size / 250, 5))
        dct["img"] = self.img_arguments(
            data, bw=self.bandwidth, size=size,
            x=x, y=y, z=z,
            levels_x=levels_x, levels_y=levels_y, **kwargs)
        dct["M"] = dct["img"].pop("M")
        return dct

    def plot_facet(self, **kwargs):
        """
        Plot a HeatBar plot.

        A heatbar plot is like a barcode plot, only that there is also a
        heat map plotted under the lines.
        """
        param = kwargs["img"]
        m = kwargs["M"]

        left, right, bottom, top = param["extent"]

        if self.normalize:
            m = np.array([[val / max(X) for val in X] for X in m])

        if self.y:
            m = m[::-1]

        for i, x in enumerate(m):
            if left is None and right is None:
                param["extent"] = (i, i+1, bottom, top)
                x = np.array([x[::-1]]).T
            else:
                param["extent"] = (left, right, i, i+1)
                x = np.array([x])
            plt.imshow(x, vmax=m.max(initial=None), **param)

        if self.plot_rug:
            elements = super().plot_facet(rug=True, **kwargs)
        else:
            elements = []

        return elements


updated_to_new_interface = vis.VisualizerStatus.Complete
provided_visualizations = [HeatbarPlot]

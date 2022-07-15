# -*- coding: utf-8 -*-
"""
densityplot.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

import seaborn as sns
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import tr

from coquery.visualizer.colorizer import Colorizer


class DensityPlot(vis.Visualizer):
    name = "Kernel density"
    icon = "Normal Distribution Histogram"

    cumulative = False

    axes_style = "whitegrid"
    _default = "Density estimate"

    shading = True
    alpha = 50

    def get_widgets(self, *args, **kwargs):
        label = tr("DensityPlot", "Shade transparency", None)
        check = tr("DensityPlot", "Use shading", None)

        self.label_transparency = QtWidgets.QLabel(label)

        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setValue(self.alpha)
        self.slider.setTickPosition(self.slider.TicksAbove)

        self.check_shading = QtWidgets.QCheckBox(check)
        self.check_shading.setChecked(self.shading)

        slide_layout = QtWidgets.QHBoxLayout()
        slide_layout.addWidget(self.label_transparency)
        slide_layout.addWidget(self.slider)
        slide_layout.setStretch(0, 0)
        slide_layout.setStretch(1, 1)

        return ([self.check_shading, slide_layout],
                [self.check_shading.toggled, self.slider.valueChanged],
                [self.check_shading.toggled])

    def update_widgets(self):
        self.slider.setEnabled(self.check_shading.isChecked())

    def update_widget_values(self):
        self.shading = self.check_shading.isChecked()
        self.alpha = int(self.slider.value())

    def plt(self, *args, shade=None, alpha=None, **kwargs):
        if shade:
            sns.kdeplot(*args, shade=shade, alpha=alpha, **kwargs)
        sns.kdeplot(*args, shade=False, **kwargs)

    def plot_facet(self, data, color, x=None, y=None, z=None,
                   levels_x=None, levels_y=None, levels_z=None,
                   color_number=None, palette=None, *args, **kwargs):

        args = {"shade": self.shading,
                "alpha": 1 - self.alpha / 100,
                "ax": plt.gca()}

        self._xlab = x or self._default
        self._ylab = y or self._default

        if not (x and y):
            # only one variable provided, create simple univariate plot
            self._colorizer = Colorizer(palette, color_number)
            self.plt(data[x or y], vertical=bool(y),
                     color=self._colorizer.get_palette()[0],
                     cumulative=self.cumulative, **args)
        else:
            if data[x].dtype == object:
                cat = x
                levels = levels_x
                self._xlab = self._default
            elif data[y].dtype == object:
                cat = y
                levels = levels_y
                self._ylab = self._default
            else:
                if levels_z:
                    cat = z
                    levels = levels_z
                else:
                    cat = None
                    levels = [0]

            self._colorizer = Colorizer(palette, color_number)
            cols = self._colorizer.get_palette(n=len(levels))
            colnames = self._colorizer.mpt_to_hex(cols)

            for i, level in enumerate(levels):
                df = data[data[cat] == level] if cat else data
                try:
                    if cat == x or cat == y:
                        self.plt(df[y if cat == x else x],
                                 vertical=(cat == x),
                                 color=cols[i],
                                 cumulative=self.cumulative, **args)
                    else:
                        cmap = sns.light_palette(colnames[i], as_cmap=True)
                        self.plt(df[x], df[y],
                                 cmap=cmap,
                                 shade_lowest=False, **args)
                except ValueError:
                    pass

            self.legend_title = cat
            self.legend_levels = levels
            self.legend_palette = cols

    @staticmethod
    def validate_data(*args):
        _, num, _ = vis.Visualizer.count_parameters(*args)
        return len(num) > 0


class CumulativePlot(DensityPlot):
    name = "Cumulative distribution"
    icon = "Positive Dynamic"

    cumulative = True
    _default = "Cumulative probability"

    def plot_facet(self, data, color, x=None, y=None, **kwargs):
        super(CumulativePlot, self).plot_facet(data, color,
                                               x=x, y=y, **kwargs)
        ax = plt.gca()
        if x and data[x].dtype != object:
            ax.set_ylim(0, 1)
        else:
            ax.set_xlim(0, 1)

    @staticmethod
    def validate_data(*args):
        _, num, _ = vis.Visualizer.count_parameters(*args)
        return len(num) == 1


provided_visualizations = [DensityPlot, CumulativePlot]

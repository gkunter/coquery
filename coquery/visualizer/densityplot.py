# -*- coding: utf-8 -*-
"""
densityplot.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

import seaborn as sns
import matplotlib.pyplot as plt

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets, QtCore


sequential_palettes = ["Blues", "Reds", "Greens", "Oranges", "Purples",
                       "BuGn", "BuPu", "RdPu", "OrRd", "YlGn",
                       "BrBG", "PiYG", "PRGn", "PuOr", "RdBu", "RdGy"]


class DensityPlot(vis.Visualizer):
    cumulative = False
    axes_style = "whitegrid"
    _default = "Density estimate"
    alpha = 50

    def get_custom_widgets(self):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QApplication.instance().translate(
                    "DensityPlot", "Transparency", None)
        button = QtWidgets.QApplication.instance().translate(
                    "DensityPlot", "Apply", None)

        DensityPlot.label_transparency = QtWidgets.QLabel(label)

        DensityPlot.slider = QtWidgets.QSlider()
        DensityPlot.slider.setOrientation(QtCore.Qt.Horizontal)
        DensityPlot.slider.setMinimum(0)
        DensityPlot.slider.setMaximum(100)
        DensityPlot.slider.setSingleStep(1)
        DensityPlot.slider.setPageStep(1)
        DensityPlot.slider.setValue(DensityPlot.alpha)
        DensityPlot.slider.setTickPosition(DensityPlot.slider.TicksAbove)

        DensityPlot.button_apply = QtWidgets.QPushButton(button)
        DensityPlot.button_apply.setDisabled(True)
        DensityPlot.button_apply.clicked.connect(
            lambda: DensityPlot.update_figure(self,
                                              DensityPlot.slider.value()))

        DensityPlot.slider.valueChanged.connect(
            lambda x: DensityPlot.button_apply.setEnabled(True))

        layout.addWidget(DensityPlot.label_transparency)
        layout.addWidget(DensityPlot.slider)
        layout.addWidget(DensityPlot.button_apply)

        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        layout.setStretch(2, 0)
        return [layout]

    @classmethod
    def update_figure(cls, self, i):
        cls.alpha = i
        DensityPlot.button_apply.setDisabled(True)
        self.updateRequested.emit()

    def plot_facet(self, data, color, x=None, y=None, z=None,
                   levels_z=None, palette=None, **kwargs):

        self._xlab = x or self._default
        self._ylab = y or self._default

        if z:
            # Use hue
            palette = self.get_palette(palette, len(levels_z))
            for i, level in enumerate(levels_z):
                df = data[data[z] == level]
                if x and y:
                    pal = sequential_palettes[i % len(sequential_palettes)]
                    try:
                        sns.kdeplot(df[x], df[y],
                                    cmap=pal,
                                    shade=True, shade_lowest=False,
                                    alpha=DensityPlot.alpha / 100)
                    except ValueError:
                        pass
                    self.legend_palette += sns.color_palette(pal, 1)
                else:
                    sns.kdeplot(df[x or y], vertical=y,
                                color=palette[i],
                                cumulative=self.cumulative)
            self.legend_title = z
            self.legend_levels = levels_z
        else:
            palette = self.get_palette(palette, kwargs["color_number"])
            if x and y:
                try:
                    sns.kdeplot(data[x], data[y],
                                colors=palette,
                                cmap=None,
                                shade=True, shade_lowest=False,
                                alpha=DensityPlot.alpha / 100)
                except ValueError:
                    pass
            else:
                sns.kdeplot(data[x or y], vertical=y,
                            color=palette[0],
                            cumulative=self.cumulative)

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if not (0 < len(num) < 3):
            return False

        if len(cat) > 0:
            return False

        return True


class CumulativePlot(DensityPlot):
    cumulative = True
    _default = "Cumulative probability"

    def plot_facet(self, data, color, x=None, y=None, **kwargs):
        super(CumulativePlot, self).plot_facet(data, color,
                                               x=x, y=y, **kwargs)
        ax = plt.gca()
        if x:
            ax.set_ylim(0, 1)
        else:
            ax.set_xlim(0, 1)

    def get_custom_widgets(self):
        pass

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) != 1:
            return False
        if len(cat) > 0:
            return False
        else:
            return True


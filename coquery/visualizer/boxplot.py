# -*- coding: utf-8 -*-
"""
boxplot.py is part of Coquery.

Copyright (c) 2017-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5 import QtWidgets, QtCore

from coquery.visualizer import visualizer as vis
import seaborn as sns
from coquery.gui.pyqt_compat import tr

class BoxPlot(vis.Visualizer):
    name = "Box-Whisker plot"
    icon = "Boxplot"

    axes_style = "whitegrid"

    draw_boxen = True

    def get_custom_widgets(self, *args, **kwargs):
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

    def plot_fnc(self, *args, **kwargs):
        if self.draw_boxen:
            sns.boxenplot(*args, **kwargs)
        else:
            sns.boxplot(*args, **kwargs)

    def plot_facet(self, data, color, **kwargs):
        x = kwargs.get("x")
        y = kwargs.get("y")
        palette = kwargs.get("palette")

        self.plot_fnc(x, y, data=data, palette=palette)
        self._xlab = x
        self._ylab = y

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) != 1:
            return False
        if len(cat) != 1:
            return False
        return True


class ViolinPlot(BoxPlot):
    name = "Violin plot"
    icon = "Violinplot"

    def plot_fnc(self, *args, **kwargs):
        sns.violinplot(*args, **kwargs)


provided_visualizations = [BoxPlot, ViolinPlot]

# -*- coding: utf-8 -*-
"""
heatmap.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import seaborn as sns
import pandas as pd

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets


def _annotate_heatmap(self, ax, mesh):
    """
    This function monkey-patches an issue with annotations in heatmaps in
    seaborn versions earlier than 0.7.0.
    """
    import colorsys

    """Add textual labels with the value in each cell."""
    try:

        mesh.update_scalarmappable()
        height, width = self.annot_data.shape
        xpos, ypos = pd.np.meshgrid(pd.np.arange(width) + 0.5,
                                    pd.np.arange(height) + 0.5)
        print(xpos, ypos, mesh, self.annot_data)
        for x, y, m, color, val in zip(xpos.flat, ypos.flat,
                                       mesh.get_array(),
                                       mesh.get_facecolors(),
                                       self.annot_data.flat):
            print(m, pd.np.ma.masked)
            if m is not pd.np.ma.masked:
                _, l, _ = colorsys.rgb_to_hls(*color[:3])
                text_color = ".15" if l > .408 else "w"
                annotation = ("{:" + self.fmt + "}").format(val)
                text_kwargs = dict(color=text_color, ha="center", va="center")
                text_kwargs.update(self.annot_kws)
                ax.text(x, y, annotation, **text_kwargs)
    except Exception as e:
        print(e)
        raise e

if sns.__version__ < "0.7.0" or True:
    sns.matrix._HeatMapper._annotate_heatmap = _annotate_heatmap


class Heatmap(vis.Visualizer):
    name = "Heatmap"
    icon = "Heatmap"

    normalization = 0

    def plot_facet(self, data, color, **kwargs):

        def get_crosstab(data, row_fact, col_fact, row_names, col_names):
            ct = pd.crosstab(data[row_fact], data[col_fact])
            ct = ct.reindex_axis(row_names, axis=0).fillna(0)
            ct = ct.reindex_axis(col_names, axis=1).fillna(0)
            return ct

        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        levels_x = kwargs.get("levels_x")
        levels_y = kwargs.get("levels_y")
        levels_z = kwargs.get("levels_z")

        cmap = (kwargs.get("palette", "Blues"))
        param_count = sum([bool(x), bool(y), bool(z)])

        if param_count == 3:
            if data[x].dtype in (int, float):
                numeric = x
                x = z
                levels_x = levels_z
            elif data[y].dtype in (int, float):
                numeric = y
                y = z
                levels_y = levels_z
            else:
                numeric = z
            ct = (data[[x, y, numeric]].groupby([x, y])
                                       .agg("mean")
                                       .reset_index()
                                       .pivot(x, y, numeric)
                                       .T)
            ct = ct.reindex_axis(levels_y, axis=0)
            ct = ct.reindex_axis(levels_x, axis=1)
            self._xlab = x
            self._ylab = y

        elif param_count == 2:
            numeric = None
            cat = []
            if x:
                if data[x].dtype in (int, float):
                    numeric = x
                    x = None
            if y:
                if data[y].dtype in (int, float):
                    numeric = y
                    y = None
            if z:
                if data[z].dtype in (int, float):
                    numeric = z
                    z = None
            if numeric:
                cat = [fact for fact in [x, y, z] if fact][0]
                ct = (data[[cat, numeric]].groupby(cat)
                                          .agg("mean"))
                if cat == x or cat == z:
                    ct = ct.reindex_axis(levels_x).T
                else:
                    ct = ct.reindex_axis(levels_y)
            else:
                ct = get_crosstab(data, x, y, levels_x, levels_y).T
            self._xlab = x
            self._ylab = y
        elif x:
            ct = pd.crosstab(pd.Series([""] * len(data[x]), name=""),
                             data[x])
            ct = ct.reindex_axis(levels_x, axis=1)
            self._xlab = x
            self._ylab = "Frequency"
        elif y:
            ct = pd.crosstab(pd.Series([""] * len(data[y]), name=""),
                             data[y]).T
            ct = ct.reindex_axis(levels_y, axis=0)
            self._ylab = y
            self._xlab = "Frequency"

        fmt = ".1%"
        if Heatmap.normalization == 1:
            ct = ct.apply(lambda col: col / sum(col), axis="columns")
        elif Heatmap.normalization == 2:
            ct = ct.apply(lambda row: row / sum(row), axis="rows")
        elif Heatmap.normalization == 3:
            ct = pd.DataFrame(ct.values / ct.values.sum(),
                              columns=ct.columns, index=ct.index)
        else:
            fmt = "g"

        sns.heatmap(ct.fillna(0),
                    robust=True,
                    annot=True,
                    cbar=False,
                    cmap=cmap,
                    fmt=fmt,
                    linewidths=1)

    def get_custom_widgets(self, *args, **kwargs):
        layout = QtWidgets.QHBoxLayout()

        tr = QtWidgets.QApplication.instance().translate

        label = tr("HeatMap", "Normalization", None)
        rowwise = tr("HeatMap", "By row", None)
        columnwise = tr("HeatMap", "By column", None)
        tablewise = tr("HeatMap", "Across all cells", None)
        no_normalization = tr("HeatMap", "No normalization", None)
        button = tr("HeatMap", "Apply", None)

        Heatmap.label_normalization = QtWidgets.QLabel(label)
        Heatmap.combo_normalize = QtWidgets.QComboBox()
        Heatmap.combo_normalize.addItems(
            [no_normalization, rowwise, columnwise, tablewise])
        Heatmap.combo_normalize.setCurrentIndex(Heatmap.normalization)
        Heatmap.button_apply = QtWidgets.QPushButton(button)
        Heatmap.button_apply.setDisabled(True)
        Heatmap.button_apply.clicked.connect(
            lambda: Heatmap.update_figure(
                self, Heatmap.combo_normalize.currentIndex()))
        Heatmap.combo_normalize.currentIndexChanged.connect(
            lambda x: Heatmap.button_apply.setEnabled(True))
        layout.addWidget(Heatmap.label_normalization)
        layout.addWidget(Heatmap.combo_normalize)
        layout.addWidget(Heatmap.button_apply)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        layout.setStretch(2, 0)
        return [layout]

    @classmethod
    def update_figure(cls, self, i):
        cls.normalization = i
        Heatmap.button_apply.setDisabled(True)
        self.updateRequested.emit()

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 1 or len(cat) > 2 or len(cat) == 0:
            return False
        else:
            return True


provided_visualizations = [Heatmap]

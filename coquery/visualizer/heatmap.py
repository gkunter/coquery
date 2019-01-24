# -*- coding: utf-8 -*-
"""
heatmap.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import seaborn as sns
import pandas as pd

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets, QtCore, tr
from coquery import options


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
        logging.debug("{}, {}\n\t{}\n\t{}".format(
            xpos, ypos, mesh, self.annot_data))
        for x, y, m, color, val in zip(xpos.flat, ypos.flat,
                                       mesh.get_array(),
                                       mesh.get_facecolors(),
                                       self.annot_data.flat):
            logging.debug("\t\t{}{}".format(m, pd.np.ma.masked))
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

    center = None

    NORM_BY_ROW = "By row"
    NORM_BY_COLUMN = "By column"
    NORM_ACROSS = "Across all cells"
    NORM_NONE = "No normalization"

    NORMALIZATIONS = [NORM_BY_ROW, NORM_BY_COLUMN, NORM_ACROSS, NORM_NONE]
    normalization = NORM_NONE

    fill = None

    def get_custom_widgets(self, *args, **kwargs):
        text_normalization = tr("HeatMap", "Normalization", None)
        text_centering = tr("HeatMap", "Set center value:", None)
        text_fill = tr("HeatMap", "Supply missing value:", None)

        self.label_normalization = QtWidgets.QLabel(text_normalization)
        self.combo_normalize = QtWidgets.QComboBox()
        self.combo_normalize.addItems(
            [tr("HeatMap", text, None) for text in self.NORMALIZATIONS])
        self.combo_normalize.setCurrentIndex(
            self.NORMALIZATIONS.index(self.normalization))

        self.check_centering = QtWidgets.QCheckBox(text_centering)
        self.spin_centering = QtWidgets.QDoubleSpinBox()

        if self.center is None:
            self.check_centering.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.check_centering.setCheckState(QtCore.Qt.Checked)
            self.spin_centering.setValue(self.center)
        self.spin_centering.setDisabled(self.center is None)

        self.check_fill = QtWidgets.QCheckBox(text_fill)
        self.spin_fill = QtWidgets.QDoubleSpinBox()

        if self.fill is None:
            self.check_fill.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.check_fill.setCheckState(QtCore.Qt.Checked)
            self.spin_fill.setValue(self.fill)
        self.spin_fill.setDisabled(self.fill is None)

        norm_layout = QtWidgets.QHBoxLayout()
        norm_layout.addWidget(self.label_normalization)
        norm_layout.addWidget(self.combo_normalize)
        norm_layout.setStretch(0, 1)
        norm_layout.setStretch(1, 0)

        center_layout = QtWidgets.QHBoxLayout()
        center_layout.addWidget(self.check_centering)
        center_layout.addWidget(self.spin_centering)

        fill_layout = QtWidgets.QHBoxLayout()
        fill_layout.addWidget(self.check_fill)
        fill_layout.addWidget(self.spin_fill)

        return ([fill_layout, norm_layout, center_layout],
                [self.combo_normalize.currentIndexChanged,
                 self.check_centering.stateChanged,
                 self.spin_centering.valueChanged,
                 self.check_fill.stateChanged,
                 self.spin_fill.valueChanged],
                [self.check_centering.stateChanged,
                 self.check_fill.stateChanged])

    def update_widgets(self):
        self.spin_centering.setEnabled(self.check_centering.isChecked())
        self.spin_fill.setEnabled(self.check_fill.isChecked())

    def update_values(self):
        if self.check_centering.isChecked():
            self.center = float(self.spin_centering.value())
        else:
            self.center = None
        if self.check_fill.isChecked():
            self.fill = float(self.spin_fill.value())
        else:
            self.fill = None
        ix = int(self.combo_normalize.currentIndex())
        self.normalization = self.NORMALIZATIONS[ix]

    def plot_facet(self, data, color, **kwargs):
        def get_crosstab(data, row_fact, col_fact, row_names, col_names):
            ct = pd.crosstab(data[row_fact], data[col_fact])
            ct = ct.reindex_axis(row_names, axis=0)
            ct = ct.reindex_axis(col_names, axis=1)
            if self.fill is not None:
                ct = ct.fillna(self.fill)
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

        ct = ct.fillna(self.fill) if self.fill is not None else ct

        if self.z:
            fmt = "+.{}f".format(options.cfg.digits)
            if self.normalization == self.NORM_BY_ROW:
                means = ct.mean(axis="columns", skipna=True)
                std = ct.std(axis="columns", skipna=True)
                ct = (ct.subtract(means, axis="rows")
                        .divide(std, axis="rows"))
            elif self.normalization == self.NORM_BY_COLUMN:
                means = ct.mean(axis="rows", skipna=True)
                std = ct.std(axis="rows", skipna=True)
                ct = (ct.subtract(means, axis="columns")
                        .divide(std, axis="columns"))
            elif self.normalization == self.NORM_ACROSS:
                ct = (ct - pd.np.nanmean(ct.values)) / pd.np.nanstd(ct.values)
            else:
                fmt = ".{}f".format(options.cfg.digits)

            if self.center is None:
                center = None
            else:
                center = self.center
        else:
            if self.normalization == self.NORM_BY_ROW:
                ct = ct.divide(ct.sum(axis="columns", skipna=True),
                               axis="rows")
            elif self.normalization == self.NORM_BY_COLUMN:
                ct = ct.divide(ct.sum(axis="rows", skipna=True),
                               axis="columns")
            elif self.normalization == self.NORM_ACROSS:
                ct = pd.DataFrame(ct.values / ct.values.sum(),
                                  columns=ct.columns, index=ct.index)
            else:
                fmt = "g"


            if self.center is None:
                center = None
            else:
                if self.normalization == self.NORM_NONE:
                    center = self.center
                else:
                    center = self.center / 100

        sns.heatmap(ct,
                    robust=True,
                    annot=True,
                    cbar=False,
                    center=center,
                    cmap=cmap,
                    fmt=fmt,
                    linewidths=1)

    @staticmethod
    def validate_data(data_x, data_y, data_z, df, session):
        cat, num, none = vis.Visualizer.count_parameters(
            data_x, data_y, data_z, df, session)

        if len(num) > 1 or len(cat) > 2 or len(cat) == 0:
            return False
        else:
            return True


provided_visualizations = [Heatmap]

# -*- coding: utf-8 -*-
"""
heatmap.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""


import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from coquery.visualizer import visualizer as vis
from coquery.gui.pyqt_compat import QtWidgets


def _annotate_heatmap(self, ax, mesh):
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
                print(1)
                _, l, _ = colorsys.rgb_to_hls(*color[:3])
                text_color = ".15" if l > .408 else "w"
                print(l, text_color)
                annotation = ("{:" + self.fmt + "}").format(val)
                print(annotation)
                text_kwargs = dict(color=text_color, ha="center", va="center")
                text_kwargs.update(self.annot_kws)
                print(text_kwargs)
                ax.text(x, y, annotation, **text_kwargs)
    except Exception as e:
        print(e)
        raise e

if sns.__version__ < "0.7.0" or True:
    sns.matrix._HeatMapper._annotate_heatmap = _annotate_heatmap


class Visualizer(vis.BaseVisualizer):
    dimensionality=2

    def setup_figure(self):
        with sns.axes_style("white"):
            super(Visualizer, self).setup_figure()

    def set_defaults(self):
        self.options["color_palette"] = "RdPu"
        super(Visualizer, self).set_defaults()

        if len(self._groupby) == 2:
            self.options["label_y_axis"] = self._groupby[0]
            self.options["label_legend"] = self._groupby[1]
        else:
            self.options["label_legend"] = self._groupby[0]



    def draw(self):
        """ Draw a heat map. """

        def get_crosstab(data, row_fact,col_fact, row_names, col_names):
            ct = pd.crosstab(data[row_fact], data[col_fact])
            ct = ct.reindex_axis(row_names, axis=0).fillna(0)
            ct = ct.reindex_axis(col_names, axis=1).fillna(0)
            return ct

        def plot(data, color):
            ct = get_crosstab(
                    data,
                    self._groupby[0],
                    self._groupby[1],
                    self._levels[0],
                    self._levels[1])

            sns.heatmap(ct,
                robust=True,
                annot=True,
                cbar=False,
                cmap=cmap,
                fmt="g",
                vmax=vmax,
                #ax=plt.gca(),
                linewidths=1)

        if len(self._groupby) < 2:
            # create a dummy cross tab with one dimension containing empty
            # values:
            data_column = self._table[self._groupby[0]].reset_index(drop=True)
            tab = pd.crosstab(
                pd.Series([""] * len(data_column), name=""),
                data_column)
            plot_facet = lambda data, color: sns.heatmap(
                tab,
                robust=True,
                annot=True,
                cbar=False,
                cmap=cmap,
                fmt="g",
                linewidths=1)
        else:
            plot_facet = plot
            vmax = pd.crosstab(
                [self._table[x] for x in [self._row_factor, self._groupby[0]] if x != None],
                [self._table[x] for x in [self._col_factor, self._groupby[1]] if x != None]).values.max()

        cmap = ListedColormap(self.options["color_palette_values"])
        self.map_data(plot_facet)

class Heatmap(vis.Visualizer):
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
            #vmax=vmax,
            linewidths=1)

    def get_custom_widgets(self):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QApplication.instance().translate(
                    "HeatMap", "Normalization", None)
        rowwise = QtWidgets.QApplication.instance().translate(
                    "HeatMap", "By row", None)
        columnwise = QtWidgets.QApplication.instance().translate(
                    "HeatMap", "By column", None)
        tablewise = QtWidgets.QApplication.instance().translate(
                    "HeatMap", "Across all cells", None)
        no_normalization = QtWidgets.QApplication.instance().translate(
                    "HeatMap", "No normalization", None)
        button = QtWidgets.QApplication.instance().translate(
                    "HeatMap", "Apply", None)

        Heatmap.label_normalization = QtWidgets.QLabel(label)
        Heatmap.combo_normalize = QtWidgets.QComboBox()
        Heatmap.combo_normalize.addItems(
            [no_normalization, rowwise, columnwise, tablewise])
        Heatmap.combo_normalize.setCurrentIndex(0)
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

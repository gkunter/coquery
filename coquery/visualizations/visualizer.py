# -*- coding: utf-8 -*-
""" 
visualizer.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


"""
This module provides the base classes required for data visualization:

* :class:`Visualizer`
* :class:`VisualizerDialog`

The class :class:`Visualizer` provides the framework for new visualizations. 
Implementation a new visualization usually involves the following steps:

* Write a subclass of :class:`Visualizer`. The subclass will reimplement at least :func:`draw` to contain the plotting routines for the new visualization.
* Store the Python file containing the subclass in the directory `visualizations`.
* Make the new visualizer available to Coquery. At the moment, this can only be done by manually adding a menu entry to the `Visualizations` menu, and setting up the required signal connections in :mod:`gui/app.py`. Future versions of Coquery may provide a more simple interface for supplying visualizations.

The class :class:`VisualizerDialog` provides a dialog window for 
visualizations. This dialog makes use of the Matplotlib navigation toolbar 
for zooming, panning, and saving. It also provides the capability to freeze 
and unfreeze the current visualization. A visualization dialog with a 
specific visualization type can be opened by calling :func:`VisualizerDialog.Plot`.

Examples
--------
Examples of different visualizations can be found in the `visualizations` 
folder of the Coquery installation. For instance,
:mod:`visualizations/barplot.py` contains the subclass :class:`BarchartVisualizer` which visualizes the frequency distribution of 
the current results table in the form of one or more barcharts, and  :mod:`visualizations/barcodeplot.py` contains the subclass :class:`BarcodeVisualizer` which draws a barcode plot where vertical lines 
indicate the position within the corpus for each token in the result table.
"""
import sys
import os
import collections
import itertools
import math
import logging
import __init__

import numpy as np
import pandas as pd
import matplotlib as mpl
    
from pyqt_compat import QtGui, QtCore, pyside
# Tell matplotlib if PySide is being used:
if pyside:
    mpl.use("Qt4Agg")
    mpl.rcParams["backend.qt4"] = "PySide"

mpl.rcParams["font.family"] = str(QtGui.QFont().family())


from ui.visualizerUi import Ui_Visualizer
import QtProgress

import options
from defines import *
from errors import *
import queries

# import required matplotlib classes
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import seaborn as sns


#def table_to_tree(table, label="count"):
    #""" Return a tree that contains a tree representation of the table. It
    #is assumed that the first column represents the highest tree level, the
    #second column the second tree level, and so on. The last column gives
    #the values of the terminal nodes."""
    #tree = {}
    
    ## go through each table entry:
    #for path in table:
        #parent = tree
        #for i, child in enumerate(path[:-1]):
            #if i == len(path[:-1]) - 1:
                #parent = parent.setdefault(child, {label: path[-1]})
            #else:
                #parent = parent.setdefault(child, {})
    #return tree

#def tree_weight(tree):
    #""" Return the summed values of all terminal nodes in the tree."""
    #i = 0
    #for node in tree:
        #if isinstance(tree[node], (int, float, long)):
            #i += tree[node]
        #else:
            #i += tree_weight(tree[node])
    #return i

class CoqNavigationToolbar(NavigationToolbar):
    
    def __init__(self, canvas, parent, coordinates=True):
        super(CoqNavigationToolbar, self).__init__(canvas, parent, coordinates)
        if options.cfg.experimental:
            self.check_freeze = QtGui.QCheckBox()
            self.check_freeze.setText("Freeze visualization")
            self.check_freeze.setObjectName("check_freeze")
            self.addWidget(self.check_freeze)

    def edit_parameters(self, *args):
        import figureoptions
        new_values = figureoptions.FigureOptions.manage(self.parent.visualizer.options)
        if new_values:
            self.parent.visualizer.options.update(new_values)
            self.parent.update_plot()

class BaseVisualizer(QtCore.QObject):
    """ 
    Define a class that contains the code to visualize data in several
    ways. 
    
    The data to be visualized is passed to the visualizer by calling 
    :func:`set_data_source`. :func:`update_data` contains the code that is
    required to translate the data from the data source into a format that
    is usable for the visualizer. This method is also called whenever the
    layout or content of the data source changes. The visualization routines
    are specified in :func:`draw`. This method is usually called externally 
    by :func:`VisualizerDialog.Plot`. 
    """
    _plot_frequency = False

    def __init__(self, data_model, data_view, parent = None):
        super(BaseVisualizer, self).__init__(parent=parent)
        self._model = None
        self._view = None
        self._df = None
        self.options = {}
        self.set_data_source(data_model, data_view)
        self.set_defaults()
        self.setup_figure()

        self.function = self.draw

    def set_defaults(self):
        if self._plot_frequency:
            if not self.options.get("color_number"):
                self.options["color_number"] = 1
            if not self.options.get("label_legend_columns"):
                self.options["label_legend_columns"] = 1
            if not self.options.get("color_palette"):
                self.options["color_palette"] = "Paired"
                self.options["color_number"] = 1
        else:
            if not self.options.get("color_number"):
                self.options["color_number"] = len(self._levels[-1])
            if not self.options.get("label_legend_columns"):
                self.options["label_legend_columns"] = 1
            if not self.options.get("color_palette"):
                if len(self._levels) == 0:
                    self.options["color_palette"] = "Paired"
                    self.options["color_number"] = 1
                elif len(self._levels[-1]) in (2, 4, 6):
                    self.options["color_palette"] = "Paired"
                elif len(self._groupby) == 2:
                    self.options["color_palette"] = "Paired"
                else:
                    self.options["color_palette"] = "RdPu"
            
        if not self.options.get("color_palette_values"):
            self.set_palette_values(self.options["color_number"])

    def set_palette_values(self, n=None):
        """
        Set the color palette values to the specified number.
        """
        if not n:
            n = self.options["color_number"]
        else:
            self.options["color_number"] = n

        if self.options["color_palette"] != "custom":
            self.options["color_palette_values"] = sns.color_palette(
                self.options["color_palette"], n)
                                                                                                                         
    def _validate_layout(func):
        def func_wrapper(self):
            if self._plot_frequency:
                return func(self)
            if self._col_wrap:
                if self._col_wrap > 16:
                    raise VisualizationInvalidLayout
                else:
                    return func(self)
            if self._col_factor and len(pd.unique(self._table[self._col_factor].values.ravel())) > 16:
                raise VisualizationInvalidLayout
            if self._row_factor and len(pd.unique(self._table[self._row_factor].values.ravel())) > 16:
                raise VisualizationInvalidLayout
            return func(self)
        return func_wrapper
    
    def set_data_table(self, df):
        self._df = df
        
    def get_data_table(self):
        return self._df
    
    @_validate_layout
    def setup_figure(self):
        """ Prepare the matplotlib figure for plotting. """ 
        with sns.plotting_context("paper"):
            self.g = sns.FacetGrid(self._table, 
                            col=self._col_factor,
                            col_wrap=self._col_wrap,
                            row=self._row_factor,
                            sharex=True,
                            sharey=True)

    def map_data(self, func):
        """
        Map the dataframe using :func:`func`.
        
        This method wraps the function :func:`func` so that a facet is 
        plotted for the grouping variables. In order for this to work, 
        :func:`func` has to take two values: `data`, which is a sub-
        dataframe after grouping, and `color`, which is currently not
        used, but which must be handled by `func` anyway.
        
        Technically, it calls :func:`FacetGrid.map_dataframe` from
        `seaborn` with `func` as a parameter if more than one plot 
        is required. Otherwise, it calls `func` directly, as `FacetGrid`
        can have problems if only one plot is drawn.
        
        Parameters
        ----------
        func : function
            The plotting function.
        """
        if self._col_factor:
            self.g.map_dataframe(func) 
        else:
            func(self._table, None)
    
    def get_grid_layout(self, n):
        """ Return a tuple containing a nrows, ncols pair that can be used to
        utilize the screen space more or less nicely for the number of grids
        n. This function doesn't take the window ratio into account yet, but
        always assumes a rectangular screen. 
        
        This function is an adaption of the R function n2mfrow. """
        
        if  n <= 3:
            return (n, 1)
        elif n <= 6:
            return ((n + 1) // 2, 2)
        elif n <= 12:
            return ((n + 2) // 3, 3)
        else:
            nrows = int(math.sqrt(n)) + 1
            ncols = int(n / nrows) + 1
            return (nrows, ncols)
        
    def draw(self):
        """ Do the visualization."""
        pass

    def set_data_source(self, model, view):
        """ Set the data for the the visualizer. Currently, the method takes
        two parameters, 'model' and 'view', which are expected to be instances
        of QAbstractDataModel and QTableView classes, respectively. """
        self._model = model
        self._view = view
        self.update_data()
        
    def get_palette(self):
        """ 
        Return a palette that is suitable for the data. 
        """
        # choose the "Paired" palette if the number of grouping factor
        # levels is even and below 13, or the "Set3" palette otherwise:
        if len(self._levels) == 0:
            if len(self._groupby) == 1:
                return sns.color_palette("Paired")[0]
            else:
                palette_name = "Paired"        
        elif len(self._levels[-1]) in (2, 4, 6):
            palette_name = "Paired"
        else:
            # use 'Set3', a quantitative palette, if there are two grouping
            # factors, or a palette diverging from Red to Purple otherwise:
            palette_name = "Paired" if len(self._groupby) == 2 else "RdPu"
        return sns.color_palette(palette_name)
        
    def update_data(self):
        """
        Update the internal representation of the model content so that
        it is usable by the visualizer.
        """

        if not options.cfg.main_window.Session:
            raise VisualizationNoDataError
        
        ## get the column order from the visual QTableView:
        #header = self._view.horizontalHeader()
        #column_order = [self._model.header[header.logicalIndex(i)] for i in range(header.count())]
        #if self._plot_frequency:
            #column_order = [x for x in column_order if options.cfg.column_visibility.get(x, True)]
        #else:
            #column_order = [x for x in column_order if options.cfg.column_visibility.get(x, True) and not x.startswith("statistics")]

        #print(options.cfg.main_window.Session.data_table.columns)
        #print(column_order)

        header = self._view.horizontalHeader()
        view_columns = [self._model.header[header.logicalIndex(i)] for i in range(header.count())]
        
        view_columns = [x for x in view_columns if x in options.cfg.main_window.Session.data_table.columns]
        
        if self._plot_frequency:
            view_columns = [x for x in view_columns if options.cfg.column_visibility.get(x, True)]
        else:
            view_columns = [x for x in view_columns if options.cfg.column_visibility.get(x, True) and not x.startswith("statistics")]
        
        column_order = view_columns

        column_order.append("coquery_invisible_corpus_id")

        try:
            self._time_columns = options.cfg.main_window.Session.Corpus.resource.time_features
        except NameError:
            self._time_columns = []
       
        try:
            self._table = self._df[column_order]
        except TypeError:
            self._table = options.cfg.main_window.Session.data_table.iloc[
                    ~options.cfg.main_window.Session.data_table.index.isin(
                        pd.Series(options.cfg.row_visibility[queries.TokenQuery].keys()))]

            self._table = self._table[column_order]

        self._table.columns = [options.cfg.main_window.Session.translate_header(x) for x in self._table.columns]
        
        # get list of visible rows:
        #visible_rows = list(options.cfg.row_visibility.keys())
        #self._row_order = ~self._table.index.isin(pd.Series(visible_rows) - 1)
        #self._table = self._table[self._row_order]
        
        
        # in order to prepare the layout of the figure, first determine
        # how many dimensions the data table has.

        self._factor_columns = [x for x in self._table.columns[self._table.dtypes == object] if not x in self._time_columns]
        self._number_columns = [x for x in self._table.select_dtypes(include=["int", "float"]).columns if not x.startswith("coquery_invisible")]
        
        if self.dimensionality:
            self._groupby = self._factor_columns[-self.dimensionality:]
        else:
            self._groupby = []

        self._levels = [list(pd.unique(self._table[x].ravel())) for x in self._groupby]

        
        if options.cfg.verbose:
            print("grouping:     ", self._groupby)
            print("levels:       ", self._levels)
            print("factors:      ", self._factor_columns)
            #print("factor names: ", self._factor_names) 
            print("dimensions:   ", self.dimensionality)
        
        if len(self._factor_columns) > self.dimensionality:
            self._col_factor = self._factor_columns[-self.dimensionality - 1]
        else:
            self._col_factor = None
        if options.cfg.verbose:
            print("col_factor:   ", self._col_factor)
            print(self._table.head())
            
        if len(self._factor_columns) > self.dimensionality + 1:
            self._row_factor = self._factor_columns[-self.dimensionality - 2]
            self._col_wrap = None
        else:
            self._row_factor = None
            if self._col_factor:
                self._col_wrap, _ = self.get_grid_layout(
                    len(pd.unique(self._table[self._col_factor].ravel())))
            else:
                self._col_wrap = None
        if options.cfg.verbose:
            print("col_factor:   ", self._col_factor)
            print("col_wrap:     ", self._col_wrap)
            print("row_factor:   ", self._row_factor)
            print("time_columns: ", self._time_columns)
        #if not self._groupby:
            #raise VisualizationNoDataError

    def adjust_fonts(self):
        """
        Adjust the fonts of the figure.
        
        The font sizes are either retrieved from the 'options' dictionary of 
        this instance, or from the system default. If the default is used,
        the font size of axis tick labels and legend entries is scaled by 
        the factor 0.833.
        """
        # Set font sizes of axis labels and ticks, separately for each axis:
        for ax in self.g.fig.axes:
            for element, font in [(ax.xaxis.label, "font_x_axis"),
                                  (ax.yaxis.label, "font_y_axis")]:
                self.options[font] = self.options.get(font, QtGui.QFont())
                element.set_fontsize(self.options[font].pointSize())

            if not self.options.get("font_x_ticks"):
                self.options["font_x_ticks"] = QtGui.QFont()
                self.options["font_x_ticks"].setPointSize(round(self.options["font_x_axis"].pointSize() / 1.2))
            for element in ax.get_xticklabels():
                element.set_fontsize(self.options["font_x_ticks"].pointSize())
                
            if not self.options.get("font_y_ticks"):
                self.options["font_y_ticks"] = QtGui.QFont()
                self.options["font_y_ticks"].setPointSize(round(self.options["font_y_axis"].pointSize() / 1.2))
            for element in ax.get_yticklabels():
                element.set_fontsize(self.options["font_y_ticks"].pointSize())

        # This should be one way to get fonts for the different elements:
        #x_font = mpl.font_manager.FontProperties(
            #family=self.options["font_x_axis"].family(), 
            #style='normal', 
            #size=self.options["font_x_axis"].pointSize(), 
            #weight='normal', 
            #stretch='normal')

        # Set font size of main title:
        if not self.options.get("font_main"):
            self.options["font_main"] = QtGui.QFont()
            self.options["font_main"].setPointSize(round(QtGui.QFont().pointSize() * 1.2))
        if "label_main" in self.options:
            plt.title(self.options["label_main"], size=self.options["font_main"].pointSize())
        
        # set font size of legend:
        legend = plt.gca().get_legend()
        if legend:
            if not self.options.get("font_legend"):
                self.options["font_legend"] = QtGui.QFont()
            legend.get_title().set_fontsize(self.options["font_legend"].pointSize())
            
            if not self.options.get("font_legend_entries"):
                self.options["font_legend_entries"] = QtGui.QFont()
                self.options["font_legend_entries"].setPointSize(round(self.options["font_legend"].pointSize() / 1.2))
            plt.setp(legend.get_texts(), fontsize=self.options["font_legend_entries"].pointSize())
        
    def get_content_tree(self, table, label="count"):
        """ 
        Return a tree that contains a tree representation of the table.
        
        It is assumed that the first column represents the highest tree 
        level, the second column the second tree level, and so on. The last 
        column gives the values of the terminal nodes.
        
        Parameters
        ----------
        table : container object
            A data object containing one or more columns that will be used
            as branches for the tree, and a numeric column as the last 
            column which will be used as the weight value for each branch.
        label : string
            The string used to label branch weights.        
            
        Returns
        -------
        tree : dict
            A dictionary containing the tree structure of the data table.
        """
        tree = {}
        
        # go through each table entry:
        for path in table:
            parent = tree
            for i, child in enumerate(path[:-1]):
                if i == len(path[:-1]) - 1:
                    parent = parent.setdefault(child, {label: path[-1]})
                else:
                    parent = parent.setdefault(child, {})
        return tree

    def tree_weight(self, tree):
        """
        Return the summed values of all terminal nodes in the tree.
        
        Parameters
        ----------
        tree : dict
            A dictionary created by :func:`get_content_tree`.
        """
        i = 0
        for node in tree:
            if isinstance(tree[node], (int, float, long)):
                i += tree[node]
            else:
                i += self.tree_weight(tree[node])
        return i

    def get_levels(self, name):
        """ 
        Return a set containing all distinct values in the column 'name'.
        
        The values are returned in alphabetical order. 
        
        Parameters
        ----------
        name : string
            The column name for which the unique values are requested
            
        Returns
        -------
        levels : list
            A unique list of all values that are contained in the specified
            data column.
        """
        return pd.unique(self._table[name].values.ravel())
        
    def get_ordered_row(self, index):
        """ 
        Return a list containing the values of the dictionary 'row', in 
        the order of the columns in the table view.
        
        Parameters
        ----------
        index : int
            The row number 
            
        Returns
        -------
        row : a list of values from the data table
        """
        return self._table.iloc[index]

    def adjust_axes(self):
        """
        Try to make the axis labels as readable as possible.
        
        This method tries to make both axis labels horizontal. If overlaps 
        are created, the axis labels are rotated by 45 degrees. If there are 
        still overlaps after this rotation, the labels are set to be vertical.
        """
        
        def _axis_ticklabels_overlap(labels, fig):
            """Return a boolean for whether the list of ticklabels have overlaps.

            Parameters
            ----------
            labels : list of ticklabels

            Returns
            -------
            overlap : boolean
                True if any of the labels overlap.

            """
            if not labels:
                return False

            # Use the method from http://stackoverflow.com/questions/22667224/ to
            # get a renderer even on backends where they are normally unavailable:
            if hasattr(fig.canvas, "get_renderer"):
                renderer = fig.canvas.get_renderer()
            else:
                import io
                fig.canvas.print_pdf(io.BytesIO())
                renderer = fig._cachedRenderer

            try:
                bboxes = [l.get_window_extent(renderer) for l in labels]
                overlaps = [b.count_overlaps(bboxes) for b in bboxes]
                return max(overlaps) > 1
            except RuntimeError as e:
                print("RT", e)
                # Issue on macosx backend rasies an error in the above code
                return False

        x_overlap = False

        for ax in self.g.fig.axes:
            xtl = ax.get_xticklabels()
            ytl = ax.get_yticklabels()
            plt.setp(xtl, rotation="horizontal")
            plt.setp(ytl, rotation="horizontal")

            sns_overlap = sns.utils.axis_ticklabels_overlap(xtl)
            coq_overlap = _axis_ticklabels_overlap(xtl, self.g.fig)
            
            if sns_overlap != coq_overlap:
                print("Incongruent overlap detection: sns: {}, coq: {}".format(sns_overlap, coq_overlap))
                
            if sns_overlap or coq_overlap:
                x_overlap = True

        if x_overlap:
            self.g.fig.autofmt_xdate()
            
            #for ax in self.g.fig.axes:
                #plt.setp(xtl, rotation="vertical")

    def setup_axis(self, axis, label=None):
        """ 
        Setup the selected axis
        
        This method sets the labels on the vertical axis so that they are
        always displayed in parallel to the horizotnal axis, and not rotated.
        
        For the vertical axis, it attempts to detect overlapping labels. If
        overlap is found, the Matplotlib function
        :func:`FigureCanvas.autofmt_xdate` is called which rotates the label
        by 45 degrees in order to avoid overlap while still keeping 
        readability high.
        
        Parameters
        ----------
        axis : string, either 'y' or 'x'
            The axis for which the rotation is determined
            
        
        """
        print("setup_axis")
        #if axis.upper() == "Y":
            #return 90
            ## get adjusted width:
        #return 0
        return

        #if axis.upper() == "Y":
            #self.g.set_yticklabels(rotation=0)
            ##for tick in self.subplot.get_yticklabels():
                ##tick.set_rotation(0)
            ##if label:
                ##self.subplot.yaxis.set_label(label)
        #if axis.upper() == "X":
            #for ax in self.g.fig.axes:
                #if sns.utils.axis_ticklabels_overlap(ax.get_xticklabels()):
                    #self.g.fig.autofmt_xdate()
                    #break

            #fact = self._table[self._groupby[0]].unique()
            #max_length=0
            #for x in fact:
                #max_length = max(max_length, len(x))
            #width = self.figure.get_figwidth() * self.figure.dpi
            ## Estimate whether all tick labels will fit horizontally on the
            ## x axis. Rotate the labels if the estimated number of characters
            ## that can be fitted on the x axis is smaller than the maximally
            ## possible length of factor levels:
            #if width / (8 * self.get_font_scale()) < len(fact) * max_length:
                #self.figure.autofmt_xdate()
            #if label:
                #self.subplot.xaxis.set_label(label)

    def get_plot_context(self):
        """ 
        Return one of the Seaborn contexts. 
        
        The :mod:`Seaborn` library, which handles the overall layout of the
        :mod:`matplotlib` canvas that is used for drawing, provides different
        plotting contexts that manage font sizes, margins, and so on. The 
        available contexts are: `paper`, `notebook`, `talk`, and `poster`,
        in increasing context size order.
        
        This method selects a suitable context based on the current font 
        scaling that is determined by calling :func:`get_font_scale`. For 
        larger font sizes, larger context sizes are chosen. This should 
        adjust spacing for displays with different resolutions.
        
        Returns
        -------
        context : string
            A Seaborn context, either `paper`, `notebook`, `talk`, or `poster`
        """
        default = 12
        
        font_scale = options.cfg.app.font().pointSize() / default
        
        if font_scale <= 0.7:
            return "paper"
        if font_scale <= 1.2:
            return "notebook"
        if font_scale <= 1.5:
            return "talk"
        return "poster"
    
    def get_colors_for_factor(self, column, palette, rgb_string=False):
        """ 
        Create a dictionary with colors for each factor level. 
        
        The method assigns each distinct value from a data column to a 
        color from the palette. If there are distinct values than colors, 
        the palette is recycled.
        
        Parameters
        ----------
        column : string
            The data column for which colors are requested
        palette : iterable
            An iterable containing tuples of three values (R, G, B) 
            representing a color
        rgb_string : bool
            A boolean variable that specifies whether the color 
            representations returned by this method should be strings of the
            form #rrggbb if True. If False, the method returns tuples of
            three RGB values scaled from 0 to 1 as representations
        
        Returns
        -------
        colors : dict
            A dictionary with a color representation as the value for each 
            factor level
        """
        if rgb_string:
            col = ["#{:02X}{:02X}{:02X}".format(r, g, b) for r, g, b in color_categories]
        else:
            col = [[x / 255 for x in rgb] for rgb in color_categories]
        fact = self._table[column].unique()
        return dict(zip(fact, (col * (1 + (len(fact) // len(col))))[0:len(fact)]))

class VisualizerDialog(QtGui.QWidget):
    """ Defines a QDialog that is used to visualize the data in the main 
    data preview area. It connects the dataChanged signal of the abstract 
    data table and the sectionMoved signal of the header of the table view to 
    the update_plot() method so that the method is called whenever either the
    content of the results table changes, or the columns are moved.
    
    The visualizer dialog has a 'Freeze visualization' checkbox. If the box 
    is checked, the visualization is not updated on changes.
    """
    def __init__(self, parent=None):
        super(VisualizerDialog, self).__init__(parent)
        
        self.ui = Ui_Visualizer()
        self.ui.setupUi(self)
        self.ui.progress_bar.setRange(0, 0)
        self.ui.box_visualize.hide()
        self.ui.progress_bar.hide()
        self.ui.label.hide()
        
        self.setWindowIcon(options.cfg.icon)
        self.dialog_stack = []

        self.frozen = False
        self.spinner = QtGui.QSpinBox()
        self.spinner.setFrame(True)
        self.spinner.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.spinner.setMaximum(10)
        self.spinner.setMinimum(1)
        self.spinner.setSuffix(" year(s)")
        self.spinner_label = QtGui.QLabel("Buckets: ")
        self.spinner.valueChanged.connect(self.update_plot)
        
        self.toolbar = None
        self.canvas = None
        
        try:
            self.resize(options.settings.value("visualizer_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("visualizer_size", self.size())
        self.close()

    def add_visualizer(self, visualizer):
        """ Add a Visualizer instance to the visualization dialog. Also, 
        add a matplotlib canvas and a matplotlib navigation toolbar to the 
        dialog. """
        self.visualizer = visualizer
        self.connect_signals()
        options.cfg.main_window.widget_list.append(self)

    def update_plot(self):
        """ 
        Update the plot. 
        
        During the update, the canvas and the navigation toolbar are 
        replaced by new instances, as is the figure used by the visualizer.
        Finally, the draw() method of the visualizer is called to plot the
        visualization again. 
        """
        if self.smooth:
            self.spinner.setEnabled(False)
            self.visualizer.update_data(bandwidth=self.spinner.value())
        else:
            self.visualizer.update_data()

        self.visualizer.setup_figure()
        
        self.remove_matplot()
        self.add_matplot()
            
        self.visualizer.draw()
        self.visualizer.g.fig.tight_layout()
        self.visualizer.adjust_axes()
        self.visualizer.adjust_fonts()

        if self.smooth:
            self.spinner.setEnabled(True)

    def add_matplot(self):
        """ Add a matplotlib canvas and a navigation bar to the dialog. """
        if not self.canvas:
            self.canvas = FigureCanvas(self.visualizer.g.fig)
            self.ui.verticalLayout.addWidget(self.canvas)
            self.canvas.setParent(self.ui.box_visualize)
            self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.canvas.setFocus()

        if not self.toolbar:
            self.toolbar = CoqNavigationToolbar(self.canvas, self, True)       
            if options.cfg.experimental:
                self.toolbar.check_freeze.stateChanged.connect(self.toggle_freeze)
            if self.smooth:
                self.toolbar.addWidget(self.spinner)
                self.toolbar.addWidget(self.spinner_label)
            self.ui.navigation_layout.addWidget(self.toolbar)
        else:
            self.toolbar.canvas = self.canvas
        self.canvas.mpl_connect('key_press_event', self.keyPressEvent)

    def remove_matplot(self):
        """ 
        Remove the matplotlib canvas and the navigation bar from the 
        dialog. 
        """
        if self.canvas:
            self.canvas.close()
        self.ui.verticalLayout.removeWidget(self.canvas)
        self.canvas = None
        
    def close(self, *args):
        """ Close the visualizer widget, disconnect the signals, and remove 
        the visualizer from the list of visualizers when closing."""
        try:
            self.disconnect_signals()
        except TypeError:
            # TypeErrors can be raised if there is no connected object. This
            # can be ignored:
            pass
        self.remove_matplot()
        super(VisualizerDialog, self).close()
        try:
            options.cfg.main_window.widget_list.remove(self)
        except ValueError:
            pass
        try:
            del self.visualizer
        except AttributeError:
            pass
        
    def keyPressEvent(self, event):
        """ Catch key events so that they can be passed on to the matplotlib
        toolbar. """
        try:
            key_press_handler(event, self.canvas, self.toolbar)
        except AttributeError:
            # Attribute errors seem to occur when a key is pressed while the 
            # mouse is outside of the figure area:
            #
            # AttributeError: 'QKeyEvent' object has no attribute 'inaxes'
            #
            # This exception may be safely ignored.
            pass
        except Exception as e:
            print(e)
            raise e
            
    def connect_signals(self):
        """ Connect the dataChanged signal of the abstract data table and the 
        sectionMoved signal of the header of the table view to the 
        update_plot() method so that the method is called whenever either the
        content of the results table changes, or the columns are moved."""
        if not options.cfg.experimental:
            return
        options.cfg.main_window.table_model.dataChanged.connect(self.update_plot)
        options.cfg.main_window.table_model.layoutChanged.connect(self.update_plot)
        self.visualizer._view.horizontalHeader().sectionMoved.connect(self.update_plot)

    def disconnect_signals(self):
        """ Disconnect the dataChanged signal of the abstract data table and 
        the sectionMoved signal of the header of the table view so that the 
        update_plot() method is not called anymore when the content of the 
        results table changes or the columns are moved."""
        if not options.cfg.experimental:
            return
        options.cfg.main_window.table_model.dataChanged.disconnect(self.update_plot)
        options.cfg.main_window.table_model.layoutChanged.disconnect(self.update_plot)
        self.visualizer._view.horizontalHeader().sectionMoved.disconnect(self.update_plot)
        
    def toggle_freeze(self):
        """ Toggle the 'frozen' state of the visualization. This method is 
        called whenever the 'Freeze visualization' box is checked or
        unchecked. 
        
        If the box is checked, the visualization is frozen, and the plot is 
        not updated if the content of the results table changes or if the 
        columns of the table view are moved. 
        
        If the box is unchecked (the default), the visualization is not 
        frozen, and the plot is updated on changes to the results table. """
        if not options.cfg.experimental:
            return
        self.frozen = not self.frozen
        if self.frozen:
            self.disconnect_signals()
        else:
            self.connect_signals()

    def Plot(self, model, view, visualizer_class, parent=None, **kwargs):
        """ Use the visualization type given as 'visualizer_class' to display
        the data given in the abstract data table 'model', using the table 
        view given in 'view'. """
        dialog = self
        self.smooth = kwargs.get("smooth", False)
        self.visualizer = visualizer_class(model, view, parent=None, **kwargs)
        if not self.visualizer._table.empty:
            self.setVisible(True)
            self.connect_signals()
            options.cfg.main_window.widget_list.append(self)
            self.add_matplot()
            
            self.thread = QtProgress.ProgressThread(self.visualizer.draw, parent=self)
            self.thread.taskStarted.connect(self.startplot)
            self.thread.taskFinished.connect(self.finishplot)

            self.visualizer.moveToThread(self.thread)
            self.thread.start()

    def startplot(self):
        self.ui.box_visualize.hide()
        self.ui.frame.setDisabled(True)        
        self.ui.frame_placeholder.show()
        self.ui.progress_bar.show()
        self.ui.label.show()
        self.repaint()

    def finishplot(self):
        self.ui.frame_placeholder.hide()
        self.ui.progress_bar.hide()
        self.ui.label.hide()        
        self.ui.box_visualize.show()
        self.ui.frame.setDisabled(False)        
        self.repaint()
        
        self.visualizer.g.fig.canvas.draw()
        self.visualizer.g.fig.tight_layout()
        self.visualizer.adjust_axes()
        self.visualizer.adjust_fonts()

        self.show()

        # Create an alert in the system taskbar to indicate that the
        # visualization has completed:
        options.cfg.app.alert(self, 0)
  
if __name__ == "__main__":
    unittest.main()
            
    #app = QtGui.QApplication(sys.argv)

    #TreeMap.MosaicPlot(table)
    #TreeMap.MosaicPlot([x for x in table if x[0] == "WIS" and x[1] == "female"])
    #tm.tree_map(tree, [0, 0], [500, 500], 0, None, None)
    #sys.exit(app.exec_())


logger = logging.getLogger(__init__.NAME)
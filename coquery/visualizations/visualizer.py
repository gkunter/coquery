# -*- coding: utf-8 -*-
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

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import collections
import itertools
import math
import logging
import __init__

import numpy as np
import pandas as pd
import seaborn as sns

from pyqt_compat import QtGui, QtCore, pyside

import options
sys.path.append(os.path.join(sys.path[0], "../gui/"))
from QtProgress import ProgressIndicator
import visualizerUi
from defines import *
from errors import *
import error_box

import matplotlib as mpl
# Tell matplotlib if PySide is being used:
if pyside:
    mpl.use("Qt4Agg")
    mpl.rcParams["backend.qt4"] = "PySide"

# import required matplotlib classes
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt

import multiprocessing

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

class Visualizer(object):
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
    
    visualize_frequency = True
    
    def _validate_layout(func):
        def func_wrapper(self):
            if self._col_wrap and self._col_wrap > 16:
                raise InvalidGraphLayout
            if self._col_factor and len(pd.unique(self._table[self._col_factor].values.ravel())) > 16:
                raise InvalidGraphLayout
            if self._row_factor and len(pd.unique(self._table[self._row_factor].values.ravel())) > 16:
                raise InvalidGraphLayout
            return func(self)
        return func_wrapper
    
    def __init__(self, data_model, data_view):
        self._model = None
        self._view = None
        self.set_data_source(data_model, data_view)
        self.setup_figure()
    
    #def get_xlim(self):
        #return (0, options.cfg.main_window.Session.Corpus.get_corpus_size())
    
    #def get_ylim(self):
        #return (0, 1)

    @_validate_layout
    def setup_figure(self):
        """ Prepare the matplotlib figure for plotting. """ 
        with mpl.rc_context({"legend.fontsize": 16}):
            with sns.plotting_context(
                context=self.get_plot_context(), 
                font_scale=self.get_font_scale()):

                print("col_factor: ", self._col_factor)
                print("col_wrap:   ", self._col_wrap)
                print("row_factor: ", self._row_factor)
                self.g = sns.FacetGrid(self._table, 
                                    #xlim=self.get_xlim(),
                                    #ylim=self.get_ylim(),
                                    col=self._col_factor,
                                    col_wrap=self._col_wrap,
                                    row=self._row_factor,
                                    sharex=True,
                                    sharey=True)

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
        print("not implemented")
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
        
        # _table stores the data from the model in such a way that it is 
        # accessible by the visualizer. """
        
        self._table = []

        # get the column order from the visual QTableView:
        header = self._view.horizontalHeader()
        self._column_order = [self._model.content.columns[header.logicalIndex(section)] for section in range(header.count())]
        # ... but make sure that the frequency is the last column:
        try:
            self._column_order.remove("coq_frequency")
        except ValueError:
            pass
        else:
            # ... but only if the current visualizer displays frequency
            # data. The frequency column is stripped otherwise.
            if self.visualize_frequency:
                self._column_order.append("coq_frequency")
        
        self._column_order += [x for x in options.cfg.main_window.Session.output_order if x.startswith("coquery_invisible") and x not in self._column_order]
        try:
            self._time_columns = options.cfg.main_window.Session.Corpus.resource.time_features
        except AttributeError:
            self._time_columns = []
            
        # Remove hidden columns:
        self._column_order = [x for x in self._column_order if 
            options.cfg.column_visibility.get(x, True)]
        
        self._table = self._model.content.reindex(columns=self._column_order)
        
        self._table = self._table.sort(columns=self._column_order, axis="rows")
        self._table.columns = [
            options.cfg.main_window.Session.Corpus.resource.translate_header(x) for x in self._table.columns]

        # in order to prepare the layout of the figure, first determine
        # how many dimensions the data table has.
        self._factor_columns = [x for x in self._table.columns[self._table.dtypes == object] if not x.startswith("coquery_invisible")]

        if self.dimensionality:
            self._groupby = self._factor_columns[-self.dimensionality:]
        else:
            self._groupby = []
        self._levels = [list(pd.unique(self._table[x].ravel())) for x in self._groupby]
        
        print("grouping:   ", self._groupby)
        print("levels:      ", self._levels)
        print("factors:    ", self._factor_columns)
        print("dimensions: ", self.dimensionality)
        
        if len(self._factor_columns) > self.dimensionality:
            self._col_factor = self._factor_columns[-self.dimensionality - 1]
        else:
            self._col_factor = None
            
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
        if axis.upper() == "Y":
            return 90
            # get adjusted width:
        return 0


        if axis.upper() == "Y":
            self.g.set_yticklabels(rotation=0)
            #for tick in self.subplot.get_yticklabels():
                #tick.set_rotation(0)
            #if label:
                #self.subplot.yaxis.set_label(label)
        if axis.upper() == "X":
            for ax in self.g.fig.axes:
                if sns.utils.axis_ticklabels_overlap(ax.get_xticklabels()):
                    self.g.fig.autofmt_xdate()
                    break

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



    def get_font_scale(self, default=12):
        """ 
        Return the scaling factor of the current font, relative to a default
        font size.
        
        Parameters
        ----------
        default : int (default=12)
            The default font size for which the relative scaling factor of 
            the current font is calculated.
            
        Returns
        -------
        scale : float
            The scaling factor of the current font.
        """
        return options.cfg.app.font().pointSize()/default

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
        font_scale = self.get_font_scale()
        
        if font_scale <= 0.7:
            return "paper"
        if font_scale <= 1.2:
            return "notebook"
        if font_scale <= 1.5:
            return "talk"
        return "poster"
    
    def start_draw_thread(self):
        """
        Wrap a progress indicator around :func:`draw`.
        
        As drawing using matplotlib is not exactly lightning-fast, a progress
        bar from :mod:`gui.QtProgress` is used to show that there is still 
        activity.
        """
        
        progress = ProgressIndicator(FUN=None, label="Drawing...")
        
        self.draw()
        progress.close()

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
        
        self.ui = visualizerUi.Ui_Visualizer()
        self.ui.setupUi(self)
        self.ui.button_close.setIcon(QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_DialogCloseButton))
        
        self.setWindowIcon(options.cfg.icon)
        self.dialog_stack = []

        # Connect the required signals so the plot is updated on changes to
        # the results table:
        self.connect_signals()
        self.ui.button_close.clicked.connect(self.close)
        self.ui.check_freeze.stateChanged.connect(self.toggle_freeze)
        self.frozen = False

    def add_smooth_spinner(self):
        self.ui.spinner = QtGui.QSpinBox()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.spinner.sizePolicy().hasHeightForWidth())
        self.ui.spinner.setSizePolicy(sizePolicy)
        self.ui.spinner.setFrame(True)
        self.ui.spinner.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.ui.spinner.setMaximum(10)
        self.ui.spinner.setMinimum(1)
        self.ui.spinner.setSuffix(" year(s)")
        self.ui.horizontalLayout_3.insertWidget(2, self.ui.spinner)
        self.ui.horizontalLayout_3.insertWidget(2, QtGui.QLabel("Bins: "))
        
        self.ui.spinner.valueChanged.connect(self.update_plot)

    def add_visualizer(self, visualizer):
        """ Add a Visualizer instance to the visualization dialog. Also, 
        add a matplotlib canvas and a matplotlib navigation toolbar to the 
        dialog. """
        self.visualizer = visualizer
        options.cfg.main_window.widget_list.append(self)

    def update_plot(self):
        """ Update the plot. During the update, the canvas and the navigation
        toolbar are replaced by new instances, as is the figure used by the 
        visualizer. Finally, the draw() method of the visualizer is called to
        plot the visualization again. """
        if self.smooth:
            self.ui.spinner.valueChanged.disconnect(self.update_plot)
            self.ui.spinner.setEnabled(False)
        self.visualizer.setup_figure()
        self.remove_matplot()
        self.add_matplot()
        if self.smooth:
            self.visualizer.update_data(bandwidth=self.ui.spinner.value())
        else:
            self.visualizer.update_data()
            
        self.visualizer.start_draw_thread()
        if self.smooth:
            self.ui.spinner.valueChanged.connect(self.update_plot)
            self.ui.spinner.setEnabled(True)

    def add_matplot(self):
        """ Add a matplotlib canvas and a navigation bar to the dialog. """
        self.canvas = FigureCanvas(self.visualizer.g.fig)
        self.ui.verticalLayout.addWidget(self.canvas)
        self.canvas.setParent(self.ui.box_visualize)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        self.canvas.mpl_connect('key_press_event', self.keyPressEvent)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.ui.navigation_layout.addWidget(self.toolbar)

    def remove_matplot(self):
        """ Remove the matplotlib canvas and the navigation bar from the 
        dialog. """
        self.ui.verticalLayout.removeWidget(self.canvas)
        self.canvas.close()
        self.ui.navigation_layout.removeWidget(self.toolbar)
        self.toolbar.close()
        
    def close(self, *args):
        """ Close the visualizer widget, disconnect the signals, and remove 
        the visualizer from the list of visualizers when closing."""
        self.disconnect_signals()
        self.remove_matplot()
        super(VisualizerDialog, self).close()
        options.cfg.main_window.widget_list.remove(self)
        
    def keyPressEvent(self, event):
        """ Catch key events so that they can be passed on to the matplotlib
        toolbar. """
        try:
            key_press_handler(event, self.canvas, self.toolbar)
        except (ValueError, AttributeError) as e:
            logger.warn("The keypress '{}' could not be handled correctly by the graph library.".format(event.key))
            
    def connect_signals(self):
        """ Connect the dataChanged signal of the abstract data table and the 
        sectionMoved signal of the header of the table view to the 
        update_plot() method so that the method is called whenever either the
        content of the results table changes, or the columns are moved."""

        options.cfg.main_window.table_model.dataChanged.connect(self.update_plot)
        options.cfg.main_window.table_model.layoutChanged.connect(self.update_plot)
        options.cfg.main_window.ui.data_preview.horizontalHeader().sectionMoved.connect(self.update_plot)

    def disconnect_signals(self):
        """ Disconnect the dataChanged signal of the abstract data table and 
        the sectionMoved signal of the header of the table view so that the 
        update_plot() method is not called anymore when the content of the 
        results table changes or the columns are moved."""
        options.cfg.main_window.table_model.dataChanged.disconnect(self.update_plot)
        options.cfg.main_window.table_model.layoutChanged.disconnect(self.update_plot)
        options.cfg.main_window.ui.data_preview.horizontalHeader().sectionMoved.disconnect(self.update_plot)
        
    def toggle_freeze(self):
        """ Toggle the 'frozen' state of the visualization. This method is 
        called whenever the 'Freeze visualization' box is checked or
        unchecked. 
        
        If the box is checked, the visualization is frozen, and the plot is 
        not updated if the content of the results table changes or if the 
        columns of the table view are moved. 
        
        If the box is unchecked (the default), the visualization is not 
        frozen, and the plot is updated on changes to the results table. """
        self.frozen = not self.frozen
        if self.frozen:
            self.disconnect_signals()
        else:
            self.connect_signals()

    def plot_it(self):
        print("starting")
        self.visualizer.setup_figure()
        self.visualizer.start_draw_thread()
        print("done")

    def Plot(self, model, view, visualizer_class, parent=None, **kwargs):
        """ Use the visualization type given as 'visualizer_class' to display
        the data given in the abstract data table 'model', using the table 
        view given in 'view'. """
        dialog = self
        self.smooth = kwargs.get("smooth", False)
        if self.smooth:
            self.add_smooth_spinner()
        try:
            visualizer = visualizer_class(model, view, **kwargs)
            if visualizer._model:
                dialog.setVisible(True)
                dialog.add_visualizer(visualizer)
                dialog.add_matplot()
                #self.sub_process = multiprocessing.Process(target=self.plot_it, args=())
                #self.sub_process.start()
                self.visualizer.start_draw_thread()
        except InvalidGraphLayout as e:
            QtGui.QMessageBox.critical(self, "Visualization error", e.error_message)
        except VisualizationInvalidDataError as e:
            QtGui.QMessageBox.critical(self, "Visualization error", e.error_message)
            

if __name__ == "__main__":
    unittest.main()
            
    #app = QtGui.QApplication(sys.argv)

    #TreeMap.MosaicPlot(table)
    #TreeMap.MosaicPlot([x for x in table if x[0] == "WIS" and x[1] == "female"])
    #tm.tree_map(tree, [0, 0], [500, 500], 0, None, None)
    #sys.exit(app.exec_())


logger = logging.getLogger(__init__.NAME)
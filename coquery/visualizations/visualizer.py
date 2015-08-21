# -*- coding: utf-8 -*-
""" Provide the base classes required for data visualization. 

The class Visualizer() provides the framework for new visualizations. Its 
method draw() can be overridden to create a new plot type, and the method 
setup_figure() can be used to define the grid layout required for this plot
type. Visualizer classes have the class attribute visualize_frequency. If
True, the class provides a plot type that can be used to display the result 
of frequency queries. If False, it provides a plot type that can be used to
display token queries (either DISTINCT or ALL).

Visualizer() also contains some interfaces to the result table, but these 
functions may be moved to an independent class that provides some dataframe-
like interfaces.

The second base class is VisualizerDialog(), which can be used to provide a
dialog window for visualizations. This dialog makes use of the Matplotlib
navigation toolbar for zooming, panning, and saving. It also provides the
capability to freeze and unfreeze the current visualization.

A visualization dialog with a specific visualization type can be opened by 
calling the static method Plot(). """

from __future__ import division
from __future__ import print_function

import sys
import os
import collections
import itertools
import math

import numpy as np
import pandas as pd
import seaborn as sns

from pyqt_compat import QtGui, QtCore, pyside

import options
sys.path.append(os.path.join(sys.path[0], "../gui/"))
import visualizerUi
from defines import *
import error_box


# Tell matplotlib if PySide is being used:
if pyside:
    import matplotlib
    matplotlib.use("Qt4Agg")
    matplotlib.rcParams["backend.qt4"] = "PySide"

# import required matplotlib classes
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
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

# pandas snippet:
# check if a column contains only a single value:
# len(pd.unique(self._table[column].values.ravel())) == 1

class Visualizer(object):
    """ Define a class that contains the code to visualize data in several
    ways. The visualizer is provided with the data by calling the method
    set_model(), and it gains access to the matplotlib figure by calling
    the method set_subplot(). The method refresh() is called whenever
    the data source changes. """
    
    visualize_frequency = True
    
    def __init__(self, data_model, data_view):
        self._model = None
        self._view = None
        self.set_data_source(data_model, data_view)
        self.setup_figure()
    
    #def get_xlim(self):
        #return (0, options.cfg.main_window.Session.Corpus.get_corpus_size())
    
    #def get_ylim(self):
        #return (0, 1)
        
    def setup_figure(self):
        """ Prepare the matplotlib figure for plotting. """ 

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
        """ Return a palette that is suitable for the data. """
        
        # choose the "Paired" palette if the number of grouping factor
        # levels is even and below 13, or the "Set3" palette otherwise:
        if len(self._levels) == 0:
            if len(self._groupby) == 1:
                return sns.color_palette("Paired")[0]
            else:
                palette_name = "Paired"        
        elif len(self._levels[-1]) in (2, 4, 6, 8, 12):
            palette_name = "Paired"
        else:
            # use 'Set3', a quantitative palette, if there are two grouping
            # factors, or a palette diverging from Red to Purple otherwise:
            palette_name = "Set3" if len(self._groupby) == 2 else "RdPu"
        return sns.color_palette(palette_name)
        
    def update_data(self):
        """ Update the internal representation of the model content so that
        it is usable by the visualizer."""
        
        # _table stores the data from the model in such a way that it is 
        # accessible by the visualizer. """
        
        self._table = []

        if options.cfg.experimental:
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
            
            # Remove hidden columns:
            self._column_order = [x for x in self._column_order if 
                options.cfg.column_visibility.get(x, True)]
            
            self._table = self._model.content.reindex(columns=self._column_order)
        else:
            self._table = [x for x in self._model.content]
        
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
        """ Return a tree that contains a tree representation of the table.
        It is assumed that the first column represents the highest tree 
        level, the second column the second tree level, and so on. The last 
        column gives the values of the terminal nodes.
        
        If an abstract data frame class is implemented at some point in the
        future, this method should become a class method of that class.
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
        """ Return the summed values of all terminal nodes in the tree.
        
        If an abstract data frame class is implemented at some point in the
        future, this method should become a class method of that class.
        """

        i = 0
        for node in tree:
            if isinstance(tree[node], (int, float, long)):
                i += tree[node]
            else:
                i += self.tree_weight(tree[node])
        return i

    def get_levels(self, name):
        """ Return a set containing all distinct values in the column 'name'.
        The values are returned in alphabetical order. """
        return pd.unique(self._table[name].values.ravel())
        
    def get_ordered_row(self, index):
        """ Return a list containing the values of the dictionary 'row', in 
        the order of the columns in the table view."""
        return self._table.iloc[index]

    def get_axis_rotation(self, axis, column):
        """ Return a rotation angle for the axis text. The angle depends on
        the oritentation of the axis, the number of factors to be drawn, and
        on the current dimension of the subplot."""
        if axis.upper() == "Y":
            return 90
            # get adjusted width:
        return 0

    def setup_axis(self, axis, label=None):
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
        """ Return the scale of the font that Qt is using, relative to the
        default font size."""
        return options.cfg.app.font().pointSize()/12

    def get_colors_for_factor(self, column, rgb_string=False):
        """ Return a dictionary with colors for each factor level. Colors
        are recycled if necessary. If the argument 'rgb_string' is True, 
        the dictionary will contain as values strings of the form #rrggbb. 
        Otherwise, the values will be tuples with RGB values scaled from
        0 to 1. """
        if rgb_string:
            col = ["#{:02X}{:02X}{:02X}".format(r, g, b) for r, g, b in color_categories]
        else:
            col = [[x / 255 for x in rgb] for rgb in color_categories]
        fact = self._table[column].unique()
        return dict(zip(fact, (col * (1 + (len(fact) // len(col))))[0:len(fact)]))

    def get_plot_context(self):
        """ Return one of the Seaborn contexts. The selection depends on the
        font size."""
        font_scale = self.get_font_scale()
        
        if font_scale <= 0.7:
            return "paper"
        if font_scale <= 1.2:
            return "notebook"
        if font_scale <= 1.5:
            return "talk"
        return "poster"

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
        self.visualizer.setup_figure()
        self.remove_matplot()
        self.add_matplot()
        self.visualizer.update_data()
        self.visualizer.draw()

    def add_matplot(self):
        """ Add a matplotlib canvas and a navigation bar to the dialog. """
        self.canvas = FigureCanvas(self.visualizer.g.fig)
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.ui.verticalLayout.addWidget(self.canvas)
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
        super(VisualizerDialog, self).close(*args)
        try:
            options.cfg.main_window.widget_list.remove(self)
        except ValueError:
            pass
        try:
            self.disconnect_signals()
        except RuntimeError:
            pass
        
    def closeEvent(self, *args):
        """ Catch close event so that the visualizer is disconnected and 
        removed from the list of visualizers. """
        self.close()
        super(VisualizerDialog, self).closeEvent(*args)

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
        self.visualizer.draw()
        print("done")

    def Plot(self, model, view, visualizer_class, parent=None, **kwargs):
        """ Use the visualization type given as 'visualizer_class' to display
        the data given in the abstract data table 'model', using the table 
        view given in 'view'. """
        dialog = self
        print(kwargs)
        visualizer = visualizer_class(model, view, **kwargs)
        if visualizer._model:
            dialog.setVisible(True)
            dialog.add_visualizer(visualizer)
            dialog.add_matplot()
            #self.sub_process = multiprocessing.Process(target=self.plot_it, args=())
            #self.sub_process.start()
            self.visualizer.draw()
            
if __name__ == "__main__":
    unittest.main()
            
    #app = QtGui.QApplication(sys.argv)

    #TreeMap.MosaicPlot(table)
    #TreeMap.MosaicPlot([x for x in table if x[0] == "WIS" and x[1] == "female"])
    #tm.tree_map(tree, [0, 0], [500, 500], 0, None, None)
    #sys.exit(app.exec_())

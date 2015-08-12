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

import unittest
import sys
import os
import options
sys.path.append(os.path.join(sys.path[0], "../gui/"))
import visualizerUi
from pyqt_compat import QtGui, QtCore, pyside
import collections
import itertools
import math
from defines import *
import error_box

import numpy as np
import pandas as pd

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

#color_map = {"young": "DarkOrange", "middle": "Red", "old": "RoyalBlue"}

#color_pairs = ["rgb(166,206,227)", "rgb(31,120,180)", 
    #"rgb(178,223,138)", "rgb(51,160,44)", 
    #"rgb(251,154,153)", "rgb(227,26,28)", 
    #"rgb(253,191,111)", "rgb(255,127,0)", 
    #"rgb(202,178,214)", "rgb(106,61,154)", 
    #"rgb(255,255,153)", "rgb(177,89,40)"]


#color_categories = ["rgb(228,26,28)", "rgb(55,126,184)", "rgb(77,175,74)", 
#"rgb(152,78,163)", "rgb(255,127,0)", "rgb(255,255,51)", 
#"rgb(166,86,40)", "rgb(247,129,191)", "rgb(153,153,153)"]

color_categories = ((228, 26, 28), (55,126,184), (77,175,74), (152,78,163), 
                    (255,127,0), (255,255,51), (166,86,40), (247,129,191), (153,153,153))

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
        
    def get_default_figure(self):
        """ Return a Figure() instance with the default appearance 
        parameters. """
        return Figure(edgecolor="pink")
        
    def setup_figure(self):
        """ Prepare the matplotlib figure for plotting. """ 
        self.figure = self.get_default_figure()
        self.subplot = self.figure.add_subplot(111)

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
            self._table = self._model.content.reindex(columns=self._column_order)
        else:
            self._table = [x for x in self._model.content]

        self._table = self._table.sort(columns=self._column_order, axis="rows")
        self._table.columns = [
            options.cfg.main_window.Session.Corpus.resource.translate_header(x) for x in self._table.columns]

    def get_table_levels(self):
        """ Return an OrderedDict with column names as keys, and sets of 
        factor levels as values. 
        
        If an abstract data frame class is implemented at some point in the
        future, this method should become a class method of that class. """
        d = collections.OrderedDict()
        header = self._view.horizontalHeader()
        self._column_order = [self._model.content.columns[header.logicalIndex(section)] for section in range(header.count())]
        for column in self._column_order:
            d[column] = self.get_levels(column)
        return d

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
        return self._table[name].unique()
        
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

    def setup_axis(self, axis):
        if axis.upper() == "Y":
            for tick in self.subplot.get_yticklabels():
                tick.set_rotation(0)
        if axis.upper() == "X":
            fact = self._table[self.col_factor].unique()
            max_length=0
            for x in fact:
                max_length = max(max_length, len(x))
            width = self.figure.get_figwidth() * self.figure.dpi
            print(width)
            print(fact)
            print(max_length)
            print(len(fact) * max_length)
            print(width / (12 * self.get_font_scale()))
            # Estimate whether all tick labels will fit horizontally on the
            # x axis. Rotate the labels if the estimated number of characters
            # that can be fitted on the x axis is smaller than the maximally
            # possible length of factor levels:
            if width / (12 * self.get_font_scale()) < len(fact) * max_length:
                self.figure.autofmt_xdate()

    def get_font_scale(self, default=12):
        """ Return the scale of the font that Qt is using, relative to the
        default font size."""
        return options.cfg.app.font().pointSize()/12

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

class VisualizerDialog(QtGui.QDialog):
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
        
        self.ui = visualizerUi.Ui_visualizer()
        self.ui.setupUi(self)
        self.setWindowIcon(options.cfg.icon)

        # Connect the required signals so the plot is updated on changes to
        # the results table:
        self.connect_signals()
        self.ui.check_freeze.stateChanged.connect(self.toggle_freeze)
        self.frozen = False

        # Matplotlib visualizations do not use the QLabel called graph_area 
        # for plotting, so it is removed from the dialog:
        self.ui.graph_area.close()
        self.ui.verticalLayout.removeWidget(self.ui.graph_area)

    def add_visualizer(self, visualizer):
        """ Add a Visualizer instance to the visualization dialog. Also, 
        add a matplotlib canvas and a matplotlib navigation toolbar to the 
        dialog. """
        self.visualizer = visualizer
        self.visualizer.draw()

    def update_plot(self):
        """ Update the plot. During the update, the canvas and the navigation
        toolbar are replaced by new instances, as is the figure used by the 
        visualizer. Finally, the draw() method of the visualizer is called to
        plot the visualization again. """
        self.remove_matplot()
        self.visualizer.setup_figure()
        self.add_visualizer(self.visualizer)
        self.add_matplot()
        self.visualizer.update_data()
        self.visualizer.draw()

    def add_matplot(self):
        """ Add a matplotlib canvas and a navigation bar to the dialog. """
        self.canvas = FigureCanvas(self.visualizer.figure)
        self.ui.verticalLayout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.ui.verticalLayout.addWidget(self.toolbar)

    def remove_matplot(self):
        """ Remove the matplotlib canvas and the navigation bar from the 
        dialog. """
        self.ui.verticalLayout.removeWidget(self.canvas)
        self.canvas.close()
        self.ui.verticalLayout.removeWidget(self.toolbar)
        self.toolbar.close()
        
    def connect_signals(self):
        """ Connect the dataChanged signal of the abstract data table and the 
        sectionMoved signal of the header of the table view to the 
        update_plot() method so that the method is called whenever either the
        content of the results table changes, or the columns are moved."""
        options.cfg.main_window.table_model.dataChanged.connect(self.update_plot)
        options.cfg.main_window.ui.data_preview.horizontalHeader().sectionMoved.connect(self.update_plot)

    def disconnect_signals(self):
        """ Disconnect the dataChanged signal of the abstract data table and 
        the sectionMoved signal of the header of the table view so that the 
        update_plot() method is not called anymore when the content of the 
        results table changes or the columns are moved."""
        if self.frozen:
            return
        options.cfg.main_window.table_model.dataChanged.disconnect(self.update_plot)
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

    def done(self, *args):
        """ Disconnect all signals, and close the dialog normally."""
        self.disconnect_signals()
        super(VisualizerDialog, self).done(*args)

    @staticmethod
    def Plot(model, view, visualizer_class, parent=None):
        """ Use the visualization type given as 'visualizer_class' to display
        the data given in the abstract data table 'model', using the table 
        view given in 'view'. """
        dialog = VisualizerDialog(parent)
        visualizer = visualizer_class(model, view)
        if visualizer._model:
            dialog.add_visualizer(visualizer)
            dialog.add_matplot()
            return dialog.show()
 
if __name__ == "__main__":
    unittest.main()
            
    #app = QtGui.QApplication(sys.argv)

    #TreeMap.MosaicPlot(table)
    #TreeMap.MosaicPlot([x for x in table if x[0] == "WIS" and x[1] == "female"])
    #tm.tree_map(tree, [0, 0], [500, 500], 0, None, None)
    #sys.exit(app.exec_())

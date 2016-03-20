# -*- coding: utf-8 -*-
""" 
visualization.py is part of Coquery.

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

import logging
import matplotlib as mpl

from coquery import options
from coquery.defines import *
from coquery.errors import *

from . import classes
from .ui.visualizerUi import Ui_Visualizer
from .pyqt_compat import QtGui, QtCore, pyside

# Tell matplotlib whether PySide or PyQt4 is used:
if pyside:
    mpl.use("Qt4Agg")
    mpl.rcParams["backend.qt4"] = "PySide"

# import required matplotlib classes
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5 import SubplotToolQt

class CoqNavigationToolbar(NavigationToolbar):
    """
    See matplotlib/backends/backend_qt5.py for the implementation.
    """
    
    def __init__(self, canvas, parent, coordinates=True):
        super(CoqNavigationToolbar, self).__init__(canvas, parent, coordinates)
        if options.cfg.experimental:
            self.check_freeze = QtGui.QCheckBox()
            self.check_freeze.setText("Freeze visualization")
            self.check_freeze.setObjectName("check_freeze")
            self.addWidget(self.check_freeze)

        self._buttons = {}

        for x in self.children():
            if isinstance(x, QtGui.QToolButton):
                self._buttons[str(x.text())] = x

        self._buttons["Forward"].setIcon(options.cfg.main_window.get_icon("sign-right"))
        self._buttons["Back"].setIcon(options.cfg.main_window.get_icon("sign-left"))
        self._buttons["Home"].setIcon(options.cfg.main_window.get_icon("sign-up"))
        self._buttons["Zoom"].setIcon(options.cfg.main_window.get_icon("search"))
        self._buttons["Save"].setIcon(options.cfg.main_window.get_icon("floppy"))
        self._buttons["Customize"].setIcon(options.cfg.main_window.get_icon("pencil"))
        self._buttons["Pan"].setIcon(options.cfg.main_window.get_icon("pan"))
        self._buttons["Subplots"].setIcon(options.cfg.main_window.get_icon("scale"))
        
        self._buttons["Subplots"].setToolTip("Adjust figure margins")
        self._buttons["Customize"].setToolTip("Edit labels, colors, and fonts")

        self._buttons["Zoom"].toggled.connect(self.toggle_zoom)
        self._buttons["Pan"].toggled.connect(self.toggle_pan)

        self._zoom = False
        self._pan = False

    def toggle_zoom(self):
        self._zoom = not self._zoom

    def toggle_pan(self):
        self._pan = not self._pan

    def isPanning(self):
        return self._pan
    
    def isZooming(self):
        return self._zoom

    def edit_parameters(self, *args):
        from . import figureoptions
        
        new_values = figureoptions.FigureOptions.manage(self.parent.visualizer.options)
        if new_values:
            self.parent.visualizer.options.update(new_values)

            #store old margin values:
            _d = {}
            for attr in ('left', 'bottom', 'right', 'top', 'wspace', 'hspace', ):
                _d[attr] = getattr(self.parent.visualizer.g.fig.subplotpars, attr)

            self.parent.update_plot()

            #reset margin values:
            self.parent.visualizer.g.fig.subplots_adjust(**_d)


    def configure_subplots(self):
        self.margin_dialog = SubplotToolQt(self.canvas.figure, self.parent)
        self.margin_dialog.setWindowTitle("Adjust figure margins – Coquery")
        self.margin_dialog.donebutton.hide()
        self.margin_dialog.resetbutton.hide()
        self.margin_dialog.tightlayout.setText("&Reset")
        self.margin_dialog.show()
        options.cfg.main_window.widget_list.append(self.margin_dialog)
        
class VisualizerDialog(QtGui.QWidget):
    """ Defines a QDialog that is used to visualize the data in the main 
    data preview area. It connects the dataChanged signal of the abstract 
    data table and the sectionMoved signal of the header of the table view to 
    the update_plot() method so that the method is called whenever either the
    content of the results table changes, or the columns are moved.
    
    The visualizer dialog has a 'Freeze visualization' checkbox. If the box 
    is checked, the visualization is not updated on changes.
    
    FIXME: Live updates are currently disabled.
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
        self.margin_dialoglog_stack = []

        self.frozen = False
        self.spinner = QtGui.QSpinBox()
        self.spinner.setFrame(True)
        self.spinner.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.spinner.setMaximum(10)
        self.spinner.setMinimum(1)
        self.spinner.setSuffix(" year(s)")
        self.spinner_label = QtGui.QLabel("Bandwidth: ")
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
        if hasattr(self.toolbar, "margin_dialog"):
            self.toolbar.margin_dialog.hide()
            self.toolbar.margin_dialog.close()
            options.cfg.main_window.widget_list.remove(self.toolbar.margin_dialog)
            del self.toolbar.margin_dialog
            
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
        self.visualizer.g.fig.tight_layout()
        
        if hasattr(self.toolbar, "margin_dialog"):
            self.toolbar.configure_subplots()

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
                self.toolbar.addWidget(self.spinner_label)
                self.toolbar.addWidget(self.spinner)
            self.ui.navigation_layout.addWidget(self.toolbar)
        else:
            self.toolbar.canvas = self.canvas
        self.canvas.mpl_connect('key_press_event', self.keyPressEvent)
        self.canvas.mpl_connect('button_press_event', self.onclick)

    def onclick(self, event):
        """
        Pass any click event onward to the visualizer, unless the dialog is 
        in panning or zooming mode.
        """
        if not self.toolbar.isPanning() and not self.toolbar.isZooming():
            self.visualizer.onclick(event)

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
        self.smooth = kwargs.get("smooth", False)
        self.visualizer = visualizer_class(model, view, parent=None, **kwargs)
        if not self.visualizer._table.empty:
            self.setVisible(True)
            self.connect_signals()
            options.cfg.main_window.widget_list.append(self)
            self.add_matplot()
            
            self.thread = classes.CoqThread(self.visualizer.draw, parent=self)
            self.thread.taskStarted.connect(self.startplot)
            self.thread.taskFinished.connect(self.finishplot)
            self.thread.taskException.connect(self.plotexception)

            self.visualizer.moveToThread(self.thread)
            self.thread.start()

    def plotexception(self, e):
        print(e)
        QtGui.QMessageBox.critical(self, "Error while plotting – Coquery", 
            msg_visualization_error.format(self.exception),
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

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

        self.visualizer.set_hover()
        self.visualizer.g.fig.tight_layout()
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


logger = logging.getLogger(NAME)
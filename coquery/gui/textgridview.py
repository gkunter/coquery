from __future__ import division

import types
import numpy as np

from coquery import options
from .pyqt_compat import QtGui, pyside

import matplotlib as mpl
if pyside:
    mpl.use("Qt4Agg")
    mpl.rcParams["backend.qt4"] = "PySide"

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import seaborn as sns

from scipy.io.wavfile import read
from scipy.signal import gaussian

class LockedAxes(mpl.axes.Axes):
    """
    Custom Axes class that allows only panning along the x axis. Based on
    http://stackoverflow.com/a/16709952/5215507
    """
    name = "LockedAxes"

    def drag_pan(self, button, key, x, y):
        mpl.axes.Axes.drag_pan(self, button, 'x', x, y)


mpl.projections.register_projection(LockedAxes)

def press_zoom(self, event):
    """
    Method that is used to limit zoom to the x axis. Based on
    http://stackoverflow.com/a/16709952/5215507
    """
    event.key='x'
    NavigationToolbar.press_zoom(self, event)


#class DynamicRange(colors.Normalize):
    #def __init__(self, vmax=None, dynamic_range=None):
        #colors.Normalize.__init__(self, vmax - dynamic_range, vmax, clip)

    #def __call__(self, value, clip=None):
        ## I'm ignoring masked values and all kinds of edge cases to make a
        ## simple example...
        #x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        #return np.ma.masked_array(np.interp(value, x, y))


class CoqTextgridView(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(CoqTextgridView, self).__init__(*args, **kwargs)
        self._dynamic_range = 50

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.press_zoom = types.MethodType(press_zoom, self.toolbar)

        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        gs = mpl.gridspec.GridSpec(3, 1, height_ratios=[4.5, 4.5, 1])
        self.ax_waveform = self.figure.add_subplot(gs[0],
                                                   projection="LockedAxes")
        self.ax_spectrogram = self.figure.add_subplot(gs[1],
                                                      sharex=self.ax_waveform,
                                                      projection="LockedAxes")
        self.ax_textgrid = self.figure.add_subplot(gs[2],
                                                      sharex=self.ax_waveform)
        self.figure.subplotpars.hspace = 0

        self.selector_waveform = SpanSelector(
            self.ax_waveform, self.on_select, 'horizontal', useblit=True,
            rectprops=dict(alpha=0.25, facecolor='red'))
        self.selector_spectrogram = SpanSelector(
            self.ax_spectrogram, self.on_select, 'horizontal', useblit=True,
            rectprops=dict(alpha=0.25, facecolor='red'))

        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)

        control_layout = QtGui.QHBoxLayout()
        self.spin_dynamic_range = QtGui.QSpinBox()
        self.spin_dynamic_range.setValue(self._dynamic_range)
        self.spin_dynamic_range.valueChanged.connect(self.change_dynamic_range)
        control_layout.addWidget(self.spin_dynamic_range)

        self.setLayout(layout)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)
        self.layout().addLayout(control_layout)

    def on_key_press(self, *args, **kwargs):
        pass

    def on_select(self, xmin, xmax):
        print(xmin, xmax)

    def change_dynamic_range(self, x):
        self.setDynamicRange(int(x))
        self.plotSpectrogram()

    def _get_spectrogram(self, **kwargs):
        self._data, ybins, xbins, im = self.ax_spectrogram.specgram(
            self._wave,
            NFFT=self._NFFT,
            Fs=self._sr,
            noverlap=self._noverlap,
            window=gaussian(M=self._NFFT, std=self._noverlap))
        self._extent = [xbins.min(), xbins.max(), ybins.min(), ybins.max()]
        self._transformed = self.transform(self._data)

    def transform(self, data):
        return 10 * np.log10(data)

    def normalize(self):
        return mpl.colors.SymLogNorm(linthresh=0.03,
                                     vmin=self._transformed.max() - self.dynamicRange(),
                                     vmax=self._transformed.max())

    def dynamicRange(self):
        return self._dynamic_range

    def setDynamicRange(self, x):
        self._dynamic_range = x

    def plotSpectrogram(self, cmap="gray_r"):
        self.ax_spectrogram.imshow(self._transformed,
                                extent=self._extent,
                                origin="lower", aspect="auto",
                                cmap=cmap,
                                norm=self.normalize())
        self.canvas.draw()

    def showWave(self, filename, **kwargs):
        self._sr, self._wave = read(filename)
        dt = 1 / self._sr
        t = np.arange(0.0, len(self._wave) * dt, dt)
        scaled = self._wave / max(abs(self._wave))
        self.ax_waveform.plot(t, scaled)

        self._NFFT = int(self._sr * kwargs.get("window_length", 0.005))
        self._noverlap = kwargs.get("noverlap", int(self._NFFT / 2))

        self._get_spectrogram()
        self.plotSpectrogram()

        self.ax_spectrogram.grid(False)
        self.ax_spectrogram.set_ylim([0, 5000])
        self.ax_spectrogram.set_xlabel("Time (s)")
        self.ax_spectrogram.set_ylabel("Frequency (Hz)")

        self.ax_textgrid.grid(False)

        self.figure.tight_layout()

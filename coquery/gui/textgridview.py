from __future__ import division

import types
import numpy as np
import sys

from .pyqt_compat import QtGui, pyside

import matplotlib as mpl
if pyside:
    mpl.use("Qt4Agg")
    mpl.rcParams["backend.qt4"] = "PySide"

from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import seaborn as sns

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
    event.key = 'x'
    NavigationToolbar.press_zoom(self, event)


class CoqFigure(Figure):
    def tight_layout(self, *args, **kwargs):
        super(CoqFigure, self).tight_layout(*args, **kwargs)
        self.subplots_adjust(hspace=0)


class CoqTextgridView(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(CoqTextgridView, self).__init__(*args, **kwargs)
        self._dynamic_range = 50
        self._window_length = 0.005
        self._textgrid = None
        self._sound = None
        self._spectrogram = None

        self.figure = CoqFigure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.press_zoom = types.MethodType(press_zoom, self.toolbar)

        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        gs = mpl.gridspec.GridSpec(3, 1, height_ratios=[2.5, 5, 2.5])
        self.ax_waveform = self.figure.add_subplot(gs[0],
                                                   projection="LockedAxes")
        self.ax_spectrogram = self.figure.add_subplot(gs[1],
                                                      sharex=self.ax_waveform,
                                                      projection="LockedAxes")
        self.ax_textgrid = self.figure.add_subplot(gs[2],
                                                   sharex=self.ax_waveform)
        self.figure.subplots_adjust(hspace=0)

        # prepare axes
        self.ax_waveform.set_ylim([-1, 1])
        self.ax_waveform.set_ylabel("Amplitude")
        self.ax_waveform.get_xaxis().set_visible(False)
        self.ax_spectrogram.set_ylabel("Frequency (Hz)")
        self.ax_spectrogram.get_xaxis().set_visible(False)
        self.ax_textgrid.set_xlabel("Time (s)")
        self.ax_textgrid.xaxis.get_offset_text().set_visible(False)

        self.selector_waveform = SpanSelector(
            self.ax_waveform, self.on_select, 'horizontal', useblit=True,
            rectprops=dict(alpha=0.25, facecolor='red'), span_stays=True)
        self.selector_spectrogram = SpanSelector(
            self.ax_spectrogram, self.on_select, 'horizontal', useblit=True,
            rectprops=dict(alpha=0.25, facecolor='red'), span_stays=True)

        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)

        self.setLayout(layout)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    def on_key_press(self, *args, **kwargs):
        pass

    def on_select(self, xmin, xmax):
        print(xmin, xmax)

    def change_dynamic_range(self, x):
        if x == self.dynamicRange():
            return
        self.setDynamicRange(int(x))
        self.plotSpectrogram()

    def change_window_length(self, x):
        if x == self.windowLength():
            return
        self.setWindowLength(float(x))
        # new window length requires recalculation of the spectrogram:
        self._get_spectrogram()
        self.plotSpectrogram()

    def _get_spectrogram(self, **kwargs):
        NFFT = int(self.sound().framerate * self.windowLength())
        noverlap = kwargs.get("noverlap", int(NFFT / 2))
        data, ybins, xbins, im = self.ax_spectrogram.specgram(
            self.sound().astype(np.int32),
            NFFT=NFFT,
            Fs=self.sound().framerate,
            noverlap=noverlap,
            window=gaussian(M=NFFT, std=noverlap))
        self._extent = [xbins.min(), xbins.max(), ybins.min(), ybins.max()]
        self._spectrogram = self.transform(data)

    def transform(self, data):
        return 10 * np.log10(data)

    def normalize(self):
        max_db = self._spectrogram.max()
        return mpl.colors.SymLogNorm(linthresh=0.03,
                                     vmin=max_db - self.dynamicRange(),
                                     vmax=max_db)

    def dynamicRange(self):
        return self._dynamic_range

    def setDynamicRange(self, x):
        self._dynamic_range = x

    def windowLength(self):
        return self._window_length

    def setWindowLength(self, x):
        self._window_length = x

    def sound(self):
        return self._sound

    def setSound(self, s):
        self._sound = s

    def setTextgrid(self, textgrid):
        self._textgrid = textgrid

    def textgrid(self):
        return self._textgrid

    def plotSpectrogram(self, cmap="gray_r"):
        if self._spectrogram is None:
            self._get_spectrogram()
        self.ax_spectrogram.imshow(self._spectrogram,
                                   extent=self._extent,
                                   origin="lower", aspect="auto",
                                   cmap=cmap,
                                   norm=self.normalize())
        self.ax_spectrogram.set_ylim([0, 5000])
        self.canvas.draw()

    def plotWave(self):
        t = np.linspace(0.0, self.sound().duration(), len(self.sound()))
        amp = self.sound().astype(np.int32)
        self.ax_waveform.plot(t, amp / abs(max(amp)))

    def plotTextgrid(self):
        tier_labels = []
        n_tiers = len(self._textgrid.tiers)
        for i, tier in enumerate(self._textgrid.tiers):
            tier_labels.append(tier.name)
            y_start = 1 - i / n_tiers
            y_end = 1 - (i+1) / n_tiers
            for interval in tier.intervals:
                patch = Rectangle(
                    (interval.start_time, y_start),
                    interval.duration(),
                    y_end - y_start,
                    fill=False)
                self.ax_textgrid.add_patch(patch)
                self.ax_textgrid.text(
                    interval.start_time + 0.5 * (interval.duration()),
                    y_start + 0.5 * (y_end - y_start),
                    interval.text,
                    verticalalignment="center",
                    horizontalalignment="center")
                self.ax_spectrogram.vlines((interval.start_time,
                                            interval.end_time), 5000, 0)
                self.ax_waveform.vlines((interval.start_time,
                                         interval.end_time), -1, 1)

        self.ax_textgrid.yaxis.set_ticks(
            [(i + 0.5) / n_tiers for i in range(n_tiers)])
        self.ax_textgrid.yaxis.set_ticklabels(reversed(tier_labels))

    def display(self, **kwargs):
        if self.sound():
            self.plotWave()
            self.plotSpectrogram()

            self.ax_spectrogram.grid(False)

        if self._textgrid:
            self.plotTextgrid()

        self.ax_textgrid.grid(False)
        self.figure.tight_layout()

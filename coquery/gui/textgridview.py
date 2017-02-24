# -*- coding: utf-8 -*-
"""
textgridview.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

import types
import numpy as np
import sys

import matplotlib as mpl
mpl.use("Qt5Agg")
mpl.rcParams["backend"] = "Qt5Agg"

from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import seaborn as sns
import scipy
from scipy import signal

from .pyqt_compat import QtWidgets, QtCore, QtGui


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


class CoqTextgridView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(CoqTextgridView, self).__init__(*args, **kwargs)
        self._dynamic_range = 50
        self._window_length = 0.005
        self._textgrid = None
        self._sound = None
        self._spectrogram = None
        self._drag = False
        self._start_pos = None

        self.scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
        self.scrollbar.valueChanged.connect(self.change_position)

        self.figure = CoqFigure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        #self.toolbar = NavigationToolbar(self.canvas, self)
        #self.toolbar.press_zoom = types.MethodType(press_zoom, self.toolbar)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        gs = mpl.gridspec.GridSpec(3, 1, height_ratios=[2.5, 5, 2.5])
        self.ax_waveform = self.figure.add_subplot(gs[0],
                                                   projection="LockedAxes")
        self.ax_spectrogram = self.figure.add_subplot(gs[1],
                                                      sharex=self.ax_waveform,
                                                      projection="LockedAxes")
        self.ax_textgrid = self.figure.add_subplot(gs[2],
                                                   sharex=self.ax_waveform,
                                                   projection="LockedAxes")
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
            rectprops=dict(alpha=0.25, facecolor='red'), span_stays=False,
            button=1)
        self.selector_spectrogram = SpanSelector(
            self.ax_spectrogram, self.on_select, 'horizontal', useblit=True,
            rectprops=dict(alpha=0.25, facecolor='red'), span_stays=False,
            button=1)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
        #self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)
        self.layout().addWidget(self.scrollbar)

    def clear(self):
        #self.layout().removeWidget(self.toolbar)
        self.layout().removeWidget(self.canvas)
        #del self.toolbar
        del self.canvas
        del self.figure

    def on_key_press(self, *args, **kwargs):
        pass

    def on_button_press(self, event):
        print(event)
        if event.button == 1:
            if event.inaxes == self.ax_textgrid:
                print("clicked", event.xdata)
                tier = self._textgrid.get_tier_by_name(
                    self._textgrid.get_tier_names()[0])
                print(tier.intervals)
                print("nearest", tier.get_annotations_by_time(event.xdata))
                interval = tier.get_annotations_by_time(event.xdata)[0]
                self._sound.extract_sound(interval.start_time,
                                          interval.end_time).play()
        elif event.button == 3:
            QtCore.QCoreApplication.instance().setOverrideCursor(
                QtGui.QCursor(QtCore.Qt. SizeHorCursor))
            self._drag = True
            self._start_pos = event.xdata

    def on_mouse_move(self, event):
        if not event.button:
            return
        if self._drag and event.xdata:
            dist = self._start_pos - event.xdata
            trans = self.ax_textgrid.transAxes.transform([dist, 0])[0]
            if abs(dist) > 0:
                xmin, xmax = self.ax_textgrid.get_xlim()
                xmin = xmin - dist
                xmax = xmax + dist
                self.ax_textgrid.set_xlim(xmin, xmax)
                self.check_zoom()
                self.canvas.draw()
                self.change_slider()

    def on_button_release(self, event):
        if event.button == 3:
            QtCore.QCoreApplication.instance().restoreOverrideCursor()
            self._drag = False
        self.check_zoom()

    def check_zoom(self, *args, **kwargs):
        xmin, xmax = self.ax_textgrid.get_xlim()
        if xmax - xmin > self._sound.duration():
            xmin = 0
            xmax = self._sound.duration()
            self.ax_textgrid.set_xlim(xmin, xmax)
            self.canvas.draw()
        elif xmin < 0:
            xmax = xmax - xmin
            xmin = 0
            self.ax_textgrid.set_xlim(xmin, xmax)
            self.canvas.draw()
        elif xmax > self._sound.duration():
            xmin = self._sound.duration() - (xmax - xmin)
            xmax = self._sound.duration()
            self.ax_textgrid.set_xlim(xmin, xmax)
            self.canvas.draw()
        self.change_slider()

    def change_slider(self):
        xmin, xmax = self.ax_textgrid.get_xlim()
        ps = max(0, int(1000 * (xmax - xmin) / self._sound.duration()))
        val = min(1000 - ps, int(1000 * (xmin / self._sound.duration())))
        new_max = 1000 - ps
        print(xmin, xmax, self._sound.duration(), new_max, ps, val)
        self.scrollbar.blockSignals(True)
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(new_max)
        self.scrollbar.setPageStep(ps)
        self.scrollbar.setValue(val)
        self.scrollbar.blockSignals(False)
        print("NEW")
        print(self.scrollbar.minimum(),
              self.scrollbar.maximum(),
              self.scrollbar.value(),
              self.scrollbar.pageStep())

    def change_position(self, i):
        pos = self._sound.duration() * i / 1000
        xmin, xmax = self.ax_textgrid.get_xlim()
        self.ax_textgrid.set_xlim(pos, pos + xmax - xmin)
        self.canvas.draw()

    def on_select(self, xmin, xmax):
        if xmin == xmax:
            self._sound.extract_sound(*self.ax_textgrid.get_xlim()).play()
        else:
            self._sound.extract_sound(xmin, xmax).play()

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
            window=signal.gaussian(M=NFFT, std=noverlap))
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
                x_pos = interval.start_time + 0.5 * (interval.duration())
                self.ax_textgrid.text(
                    x_pos,
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
        self.offset = kwargs.get("offset", 0)
        if self.sound():
            self.plotWave()
            self.plotSpectrogram()

            self.ax_spectrogram.grid(False)

        if self._textgrid:
            self.plotTextgrid()

        if self.offset:
            x_ticks = self.ax_textgrid.get_xticklabels()
            x_ticks = [str(self.offset + float(x.get_text()))
                       if x.get_text() else "" for x in x_ticks]
            lower = self.offset + self.ax_textgrid.get_xlim()[0]
            upper = self.offset + self.ax_textgrid.get_xlim()[1]
            self.ax_textgrid.set_xticklabels(x_ticks)

        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(0)
        self.scrollbar.setPageStep(1000)
        self.scrollbar.setSingleStep(10)
        #print("START")
        #print(self.scrollbar.minimum(),
              #self.scrollbar.maximum(),
              #self.scrollbar.value(),
              #self.scrollbar.pageStep())

        self.ax_textgrid.grid(False)
        self.check_zoom()
        self.figure.tight_layout()

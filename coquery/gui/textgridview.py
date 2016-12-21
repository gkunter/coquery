from __future__ import division

import matplotlib.pyplot as plt
import numpy as np
from scipy.io.wavfile import read
from scipy.signal import gaussian
import seaborn as sns

from coquery import options
from .pyqt_compat import QtGui, pyside

# Tell matplotlib whether PySide or PyQt4 is used:
if pyside:
    mpl.use("Qt4Agg")
    mpl.rcParams["backend.qt4"] = "PySide"

# import required matplotlib classes
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

#from .ui import textgridViewUi

class CoqTextgridView(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(CoqTextgridView, self).__init__(*args, **kwargs)

        self.figure_waveform = Figure()
        self.canvas_waveform = FigureCanvas(self.figure_waveform)
        self.canvas_waveform.setParent(self)

        self.canvas_waveform.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                           QtGui.QSizePolicy.Expanding)
        self.canvas_waveform.updateGeometry()
        self.ax_waveform = self.figure_waveform.add_subplot(211)
        self.ax_spectrogram = self.figure_waveform.add_subplot(212, sharex=self.ax_waveform)

        self.selector_waveform = SpanSelector(
            self.ax_waveform, self.onselect, 'horizontal', useblit=True,
            rectprops=dict(alpha=0.25, facecolor='red'))
        self.selector_spectrogram = SpanSelector(
            self.ax_spectrogram, self.onselect, 'horizontal', useblit=True,
            rectprops=dict(alpha=0.25, facecolor='red'))

        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.layout().addWidget(self.canvas_waveform)

    def onselect(self, xmin, xmax):
        print(xmin, xmax)

    def showWave(self, filename, **kwargs):
        self._sr, self._wave = read(filename)

        dt = 1/self._sr

        t = np.arange(0.0, len(self._wave) / self._sr, dt)
        NFFT = int(self._sr * kwargs.get("window_length", 0.005))
        noverlap = kwargs.get("noverlap", int(NFFT / 2))

        amp = self._wave / max(self._wave)
        self.ax_waveform.plot(t, amp)

        Pxx, freqs, bins, im = self.ax_spectrogram.specgram(
            self._wave,
            NFFT=NFFT,
            Fs=self._sr,
            noverlap=noverlap,
            cmap=plt.cm.gray_r,
            window=gaussian(M=NFFT, std=noverlap))
        print(Pxx)
        self.ax_spectrogram.grid(False)
        self.ax_spectrogram.set_ylim([0, 5000])
        self.ax_spectrogram.set_xlabel("Time (s)")
        self.ax_spectrogram.set_ylabel("Frequency (Hz)")

        self.figure_waveform.tight_layout()

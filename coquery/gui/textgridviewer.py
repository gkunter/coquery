# -*- coding: utf-8 -*-
"""
contextviewer.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import numpy as np
from numpy.lib import stride_tricks
import scipy.io.wavfile as wav

from coquery.unicode import utf8
from .pyqt_compat import QtCore, QtGui, get_toplevel_window
from .ui.textgridViewUi import Ui_Form

class TextgridViewer(QtGui.QDialog):
    def __init__(self, textgrid=None, wave=None, parent=None):
        super(TextgridViewer, self).__init__(parent)
        
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.tgt = textgrid
        self.wav = wave

    def show_wave(self):
        pass

    def show_spectogram(self):

        """ short time fourier transform of audio signal """
        def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):
            win = window(frameSize)
            hopSize = int(frameSize - np.floor(overlapFac * frameSize))

            # zeros at beginning (thus center of 1st window should be for sample nr. 0)
            samples = np.append(np.zeros(np.floor(frameSize/2.0)), sig)
            # cols for windowing
            cols = np.ceil( (len(samples) - frameSize) / float(hopSize)) + 1
            # zeros at end (thus samples can be fully covered by frames)
            samples = np.append(samples, np.zeros(frameSize))

            frames = stride_tricks.as_strided(samples, shape=(cols, frameSize), strides=(samples.strides[0]*hopSize, samples.strides[0])).copy()
            frames *= win

            return np.fft.rfft(frames)

        """ scale frequency axis logarithmically """
        def logscale_spec(spec, sr=44100, factor=20.):
            timebins, freqbins = np.shape(spec)

            scale = np.linspace(0, 1, freqbins) ** factor
            scale *= (freqbins-1)/max(scale)
            scale = np.unique(np.round(scale))

            # create spectrogram with new freq bins
            newspec = np.complex128(np.zeros([timebins, len(scale)]))
            for i in range(0, len(scale)):
                if i == len(scale)-1:
                    newspec[:,i] = np.sum(spec[:,scale[i]:], axis=1)
                else:
                    newspec[:,i] = np.sum(spec[:,scale[i]:scale[i+1]], axis=1)

            # list center freq of bins
            allfreqs = np.abs(np.fft.fftfreq(freqbins*2, 1./sr)[:freqbins+1])
            freqs = []
            for i in range(0, len(scale)):
                if i == len(scale)-1:
                    freqs += [np.mean(allfreqs[scale[i]:])]
                else:
                    freqs += [np.mean(allfreqs[scale[i]:scale[i+1]])]

            return newspec, freqs

        """ plot spectrogram"""
        def plotstft(self, binsize=1024, colormap="gray"):
            s = stft(self.wave.data, binsize)

            sshow, freq = logscale_spec(s, factor=1.0, sr=self.wave.samplerate)
            ims = 20.*np.log10(np.abs(sshow)/10e-6) # amplitude to decibel

            timebins, freqbins = np.shape(ims)

            plt.figure(figsize=(15, 7.5))
            plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")

            plt.xlabel("time (s)")
            plt.ylabel("frequency (hz)")
            plt.xlim([0, timebins-1])
            plt.ylim([0, freqbins])

            xlocs = np.float32(np.linspace(0, timebins-1, 5))
            plt.xticks(xlocs, ["%.02f" % l for l in ((xlocs*len(samples)/timebins)+(0.5*binsize))/samplerate])
            ylocs = np.int16(np.round(np.linspace(0, freqbins-1, 10)))
            plt.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

            plt.show()

    def closeEvent(self, event):
        pass
        #options.settings.setValue("uniqueviewer_size", self.size())
        #options.settings.setValue("uniqueviewer_details", self.ui.button_details.isExpanded())

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    #@staticmethod
    #def show(textgrid, wave, parent=None):
        #dialog = TextgridViewer(textgrid, wave, parent=parent)
        #dialog.setVisible(True)
        
        
def main():
    app = QtGui.QApplication(sys.argv)
    TextgridViewer.show(None, None)
    
if __name__ == "__main__":
    main()
    
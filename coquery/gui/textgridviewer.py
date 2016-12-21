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

    import matplotlib.pyplot as plt
    import numpy as np


    sr, x = input_data
    dt = 1/sr
    t = np.arange(0.0, len(x) / sr, dt)


    NFFT = 1024       # the length of the windowing segments
    Fs = int(1.0/dt)  # the sampling frequency

    # Pxx is the segments x freqs array of instantaneous power, freqs is
    # the frequency vector, bins are the centers of the time bins in which
    # the power is computed, and im is the matplotlib.image.AxesImage
    # instance

    ax1 = plt.subplot(211)
    plt.plot(t, x)
    plt.subplot(212, sharex=ax1)
    Pxx, freqs, bins, im = plt.specgram(x, NFFT=NFFT, Fs=Fs, noverlap=900,
                                    cmap=plt.cm.gray_r)
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
    
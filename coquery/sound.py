# -*- coding: utf-8 -*-
"""
sound.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division

import wave
import warnings


try:
    import alsaaudio
except ImportError:
    _ALSA = False
else:
    _ALSA = True

def read_wav(source, start=0, end=None):
    in_wav = wave.open(source, "rb")
    fr = in_wav.getframerate()
    chan = in_wav.getnchannels()
    sw = in_wav.getsampwidth()
    in_wav.setpos(int(start * fr))
    if end is None:
        end = (in_wav.getnframes() - start / fr)
    data = in_wav.readframes(int((end - start) * fr))
    in_wav.close()

    d = {"framerate": fr,
         "channels": chan,
         "samplewidth": sw,
         "length": end - start,
         "state": 0,
         "data": data}

    return d

def extract_sound(source, target, start=0, end=None):
    """
    Extract a portion from the given source, and write it to the target.
    
    Parameters
    ----------
    source: either a stream object or a string with the source file name
    target: either a stream object or a string with the target file name
    start, end : Beginning and end in seconds
    """
    sound = read_wav(source, start, end)

    out_wav = wave.open(target, "wb")
    out_wav.setframerate(sound["framerate"])
    out_wav.setnchannels(sound["channels"])
    out_wav.setsampwidth(sound["samplewidth"])
    out_wav.writeframes(sound["data"])
    out_wav.close()

if _ALSA:
    from sys import byteorder
    import threading


    # detect byte order:
    try:
        from alsaaudio import PCM_FORMAT_S16_NE as _pcm_format
    except ImportError:
        if 'little' in byteorder.lower():
            _pcm_format = alsaaudio.PCM_FORMAT_S16_LE
        else:
            _pcm_format = alsaaudio.PCM_FORMAT_S16_BE

    class _SoundThread(threading.Thread):
        def __init__(self, data, out):
            super(_SoundThread, self).__init__()
            self.data = data
            self.out = out
            self.state = 0
            _threads.append(self)

        def run(self):
            self.state = 1
            self.out.write(self.data)
            self.state = 0
            self.out.close()
            try:
                _threads.remove(self)
            except ValueError:
                pass

    def _playALSA(source, start=0, end=None, block=True):
        sound = read_wav(source, start, end)

        out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
        out.setchannels(sound["channels"])
        out.setrate(sound["framerate"])
        out.setformat(_pcm_format)
        out.setperiodsize(160)

        thread = _SoundThread(sound["data"], out)
        if block:
            _threads.append(thread)
            thread.run()
            _threads.remove(thread)
        else:
            thread.start()

        return thread

    play_wav = _playALSA
else:
    def play_wav(data, start=0, end=None, block=True):
        warnings.warn("No supported sound system detected.")
        pass

_threads = []


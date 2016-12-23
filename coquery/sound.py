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
import threading

# ensure Python 2.7 compatibility
try:
    import StringIO as io
except ImportError:
    import io as io

try:
    import alsaaudio
except ImportError:
    _ALSA = False
else:
    _ALSA = True

if not _ALSA:
    try:
        import winsound
    except ImportError:
        _WINSOUND = False
    else:
        _WINSOUND = True

if not _ALSA and not _WINSOUND:
    pass

class Sound(object):
    def __init__(self, source, start=0, end=None):
        in_wav = wave.open(source, "rb")
        self.framerate = in_wav.getframerate()
        self.channels = in_wav.getnchannels()
        self.samplewidth = in_wav.getsampwidth()
        in_wav.setpos(int(start * self.framerate))
        if end is None:
            end = (in_wav.getnframes() - start / self.framerate)
        self.raw = in_wav.readframes(int((end - start) * self.framerate))
        in_wav.close()

    def __len__(self):
        """
        Return the length of the sound in frames
        """
        return len(self.raw)

    def to_index(self, t):
        return int(self.framerate * t * self.samplewidth)

    def to_time(self, i):
        return i / (self.framerate * self.samplewidth)

    def extract_sound(self, start=0, end=None):
        if not start and not end:
            raise ValueError
        start_pos = self.to_index(start)
        if end:
            end_pos = self.to_index(end)
        else:
            end_pos = len(self.raw)

        _buffer = io.BytesIO()
        _output = wave.open(_buffer, "wb")
        _output.setnchannels(self.channels)
        _output.setsampwidth(self.samplewidth)
        _output.setframerate(self.framerate)
        _output.writeframes(self.raw[start_pos:end_pos])
        _output.close()
        _buffer.seek(0)
        return Sound(_buffer)

    def play(self, start=0, end=None, async=True):
        thread = SoundThread(self, start, end)
        if not async:
            thread.run()
            return None
        else:
            thread.start()
            return thread


    def write(self, target, start=0, end=None):
        start_pos = self.to_index(start)
        if end:
            end_pos = self.to_index(time)
        else:
            end_pos = len(self.raw)

        _output = wave.open(_buffer, "wb")
        _output.setnchannels(self.channels)
        _output.setsampwidth(self.samplewidth)
        _output.setframerate(self.framerate)
        _output.writeframes(self.raw[start_pos:end_pos])
        _output.close()

class _SoundThread(threading.Thread):
    def __init__(self, sound, start=0, end=None):
        super(_SoundThread, self).__init__()
        if start or end:
            self.sound = sound.extract_sound(start, end)
        else:
            self.sound = sound
        self.state = 0
        self.paused = False

    def stop_device(self):
        pass

    def play_device(self):
        pass

    def run(self):
        _threads.append(self)
        self.state = 1
        self.play_device()
        self.stop_device()
        self.state = 0
        try:
            _threads.remove(self)
        except ValueError:
            pass


if _ALSA:
    # detect byte order:
    try:
        from sys import byteorder
        from alsaaudio import PCM_FORMAT_S16_NE as _pcm_format
    except ImportError:
        if 'little' in byteorder.lower():
            _pcm_format = alsaaudio.PCM_FORMAT_S16_LE
        else:
            _pcm_format = alsaaudio.PCM_FORMAT_S16_BE

    class SoundThread(_SoundThread):
        def __init__(self, sound, start=0, end=None):
            super(SoundThread, self).__init__()
            self.alsa_pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
            self.alsa_pcm.setchannels(sound.channels)
            self.alsa_pcm.setrate(sound.framerate)
            self.alsa_pcm.setformat(_pcm_format)
            self.alsa_pcm.setperiodsize(160)

        def play_device(self):
            self.alsa_pcm.write(self.sound.raw)

        def pause_device(self):
            self.paused = not self.paused
            self.alsa_pcm.pause(int(self.paused))

        def stop_device(self):
            self.alsa_pcm.close()

elif _WINSOUND:
    import winsound

    class SoundThread(_Sound):
        def __init__(self, sound, start=0, end=None):
            super(SoundThread, self).__init__()
            self.wav_buffer = io.BytesIO()
            _output = wave.open(self.wav_buffer, "wb")
            _output.setnchannels(self.sound.channels)
            _output.setsampwidth(self.sound.samplewidth)
            _output.setframerate(self.sound.framerate)
            _output.writeframes(self.sound.raw)
            _output.close()
            self.wav_buffer.seek(0)

        def play_device(self):
            winsound.PlaySound(self.wav_buffer, winsound.SND_FILENAME | winsound.SND_NOSTOP)

        def stop_device(self):
            winsound.PlaySound(self.wav_buffer, winsound.SND_PURGE)

_threads = []


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


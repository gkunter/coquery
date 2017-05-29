# -*- coding: utf-8 -*-
"""
sound.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division

import wave
import warnings
import threading
import struct
import sys
import numpy as np

try:
    import StringIO as io
except ImportError:
    import io as io

_use_alsaaudio = False
_use_winsound = False
_use_simpleaudio = False

if sys.version_info < (3, 0):
    if sys.platform.startswith("linux"):
        try:
            import alsaaudio
        except ImportError:
            warnings.warn("Could not load audio module 'alsaaudio'.")
        else:
            _use_alsaaudio = True
    elif sys.platform in ("win32", "cygwin"):
        try:
            import winsound
        except ImportError:
            warnings.warn("Could not load audio module 'winsound'.")
        else:
            _use_winsound = True
else:
    if sys.platform.startswith("linux"):
        try:
            import alsaaudio
        except ImportError:
            warnings.warn("Could not load audio module 'alsaaudio'.")
        else:
            _use_alsaaudio = True
    #try:
        #import simpleaudio
    #except ImportError:
        #warnings.warn("Could not load audio module 'simpleaudio'.")
    #else:
        #_use_simpleaudio = True

if not(_use_alsaaudio or _use_simpleaudio or _use_winsound):
    warnings.warn("No audio module available.")

class Sound(object):
    def __init__(self, source, start=0, end=None):
        if type(source) is bytes:
            in_wav = wave.open(io.BytesIO(source))
        else:
            in_wav = wave.open(source, "rb")
        self.framerate = in_wav.getframerate()
        self.channels = in_wav.getnchannels()
        self.samplewidth = in_wav.getsampwidth()
        in_wav.setpos(int(start * self.framerate))
        if end is None:
            end = (in_wav.getnframes() - start / self.framerate)
        self.raw = in_wav.readframes(int((end - start) * self.framerate))
        in_wav.close()

    def astype(self, t):
        if self.samplewidth == 2:
            c_type = "h"
        else:
            c_type = "b"
        if "little" in sys.byteorder:
            frm = "<{}".format(c_type)
        else:
            frm = ">{}".format(c_type)

        S = struct.Struct(frm)
        return np.array([S.unpack(self.raw[x * self.samplewidth:
                                           (x+1) * self.samplewidth])[0]
                         for x in range(len(self))]).astype(t)

    def __len__(self):
        """
        Return the length of the sound in frames
        """
        return int(len(self.raw) / self.samplewidth)

    def duration(self):
        return len(self) / self.framerate

    def to_index(self, t):
        val = int(self.framerate * t) * self.samplewidth
        return val

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
        raw = self.raw[start_pos:end_pos]
        _output.writeframes(self.raw[start_pos:end_pos])
        _output.close()
        _buffer.seek(0)
        return Sound(_buffer)

    def play(self, start=0, end=None, async=True):
        self.thread = SoundThread(sound=self, start=start, end=end)
        if not async:
            self.thread.run()
            return None
        else:
            self.thread.start()
            return self.thread

    def stop(self):
        self.thread.pause_device()
        self.thread.stop_device()

    def write(self, target, start=0, end=None):
        start_pos = self.to_index(start)
        if end:
            end_pos = self.to_index(time)
        else:
            end_pos = len(self.raw)

        _output = wave.open(target, "wb")
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

    def device_active(self):
        return True

    def run(self):
        _threads.append(self)
        self.state = 1
        self.play_device()
        self.stop_device()
        self.state = 0
        try:
            _threads.remove(self)
            pass
        except ValueError:
            pass

if _use_simpleaudio:
    import time

    class SoundThread(_SoundThread):
        def play_device(self):
            args = [self.sound.astype(np.int32),
                    2,
                    self.sound.samplewidth,
                    self.sound.framerate]
            self.play_object = simpleaudio.play_buffer(*args)
            time.sleep(self.sound.duration() + 0.01)

        def stop_device(self):
            self.play_object.stop()

elif _use_alsaaudio:
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
            super(SoundThread, self).__init__(sound, start, end)
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

elif _use_winsound:
    class SoundThread(_SoundThread):
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
            winsound.PlaySound(self.wav_buffer,
                               winsound.SND_FILENAME | winsound.SND_NOSTOP)

        def stop_device(self):
            winsound.PlaySound(self.wav_buffer, winsound.SND_PURGE)

_threads = []


def read_wav(source, start=0, end=None):
    warnings.warn(
        "read_wav() is deprecated, use Sound() class instead",
        DeprecationWarning)
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
    warnings.warn(
        "extract_sound() is deprecated, use Sound() class instead",
        DeprecationWarning)
    sound = read_wav(source, start, end)

    out_wav = wave.open(target, "wb")
    out_wav.setframerate(sound["framerate"])
    out_wav.setnchannels(sound["channels"])
    out_wav.setsampwidth(sound["samplewidth"])
    out_wav.writeframes(sound["data"])
    out_wav.close()

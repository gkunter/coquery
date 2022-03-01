# -*- coding: utf-8 -*-
"""
sound.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import wave
import logging
import threading
import tempfile
import os
import struct
import sys
import numpy as np

try:
    import StringIO as io
except ImportError:
    import io as io

_use_sphfile = False
try:
    import sphfile
    _use_sphfile = True
except ImportError:
    pass

_use_alsaaudio = False
_use_winsound = False
_use_simpleaudio = False
_audio_loaded = False

ERROR = "Could not load audio module '{}'."


def _warn(S, *args, **kwargs):
    logging.warning(S, *args, **kwargs)
    print(S)


# Try to initialize an audio module.
#
# This method tries to load one of the potentially available audio modules.
# Depending on the operating system, the order of modules is different:
#
# Linux:      (1) alsaaudio   (2) simpleaudio
# macOS:      (1) simpleaudio
# Windows:    (1) simpleaudio (2) winsound

if sys.platform.startswith("linux"):
    _audio_module = "alsaaudio"
    try:
        import alsaaudio
    except ImportError:
        _warn(ERROR.format(_audio_module))
    else:
        _use_alsaaudio = True
        _audio_loaded = True

        from sys import byteorder
        try:
            from alsaaudio import PCM_FORMAT_S16_NE as _pcm_format
        except ImportError:
            if 'little' in byteorder.lower():
                _pcm_format = alsaaudio.PCM_FORMAT_S16_LE
            else:
                _pcm_format = alsaaudio.PCM_FORMAT_S16_BE

if not _audio_loaded:
    _audio_module = "simpleaudio"
    try:
        import simpleaudio
        import time
    except ImportError:
        _warn(ERROR.format(_audio_module))
    else:
        _use_simpleaudio = True
        _audio_loaded = True

if not _audio_loaded:
    if sys.platform in ("win32", "cygwin"):
        _audio_module = "winsound"
        try:
            import winsound
        except ImportError:
            _warn(ERROR.format(_audio_module))
        else:
            _use_winsound = True
            _audio_loaded = True

if not _audio_loaded:
    _warn("No audio module available.")
    _audio_module = None
else:
    logging.info("Loaded audio module: {}".format(_audio_module))
    print("Loaded audio module: {}".format(_audio_module))


def _read_as_wav(source):
    try:
        if type(source) is bytes:
            in_wav = wave.open(io.BytesIO(source))
        else:
            in_wav = wave.open(source, "rb")
    except FileNotFoundError:
        raise IOError("Could not read WAV file '{}'.".format(source))
    except wave.Error:
        raise TypeError("WAV file not readable")
    else:
        return in_wav


def _read_as_sph(source):
    in_wav = None
    if _use_sphfile:
        try:
            if type(source) is bytes:
                raise NotImplementedError
            else:
                with open(source, "rb") as f:
                    header = f.read(4)
                    if header != "NIST":
                        raise TypeError
                sph_file = sphfile.SPHFile(source)
                sph_file.open()

                tmp = tempfile.NamedTemporaryFile()
                temp_name = tmp.name
                tmp.close()

                try:
                    sph_file.write_wav(temp_name)
                    in_wav = _read_as_wav(tmp.name)
                finally:
                    os.remove(temp_name)

        except (wave.Error, ValueError, TypeError) as e:
            raise TypeError
        else:
            return in_wav
    else:
        raise TypeError("SPHFile not unsupported")


class AudioReader(object):
    """
    This class provides the read() class method which can be used to read an
    audio file. It takes the file name as an input, and returns a
    wave.Wave_read instance, or None the audio file could not be read.

    Support for different audio file formats is provided by adding a reader
    method to the class module `reader_methods`.
    """

    reader_methods = [_read_as_wav, _read_as_sph]

    def __init__(self, source=None):
        self._n = len(self.reader_methods)
        self._i = 0
        self._source = source

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self._i < self._n:
            reader = self.reader_methods[self._i]
            self._i += 1

            try:
                result = reader(self._source)
            except TypeError:
                result = None
            return result
        else:
            raise StopIteration

    @classmethod
    def read(cls, source):
        for wav in cls(source):
            if wav:
                return wav
        return None


class Sound(object):
    def __init__(self, source, start=0, end=None):

        in_wav = AudioReader.read(source)

        if not in_wav:
            raise TypeError

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
        _output.writeframes(self.raw[start_pos:end_pos])
        _output.close()
        _buffer.seek(0)
        return Sound(_buffer)

    def play(self, start=0, end=None, async=True):
        self.thread = _get_sound_thread(sound=self, start=start, end=end)
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
            end_pos = self.to_index(end)
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


class _simpleaudio_SoundThread(_SoundThread):
    def play_device(self):
        args = [self.sound.astype(np.int32),
                2,
                self.sound.samplewidth,
                self.sound.framerate]
        self.play_object = simpleaudio.play_buffer(*args)
        time.sleep(self.sound.duration() + 0.01)

    def stop_device(self):
        self.play_object.stop()


class _alsaaudio_SoundThread(_SoundThread):
    def __init__(self, sound, start=0, end=None):
        super(_alsaaudio_SoundThread, self).__init__(sound, start, end)
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


class _winsound_SoundThread(_SoundThread):
    def __init__(self, sound, start=0, end=None):
        super(_winsound_SoundThread, self).__init__(sound, start, end)
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


def _get_sound_thread(*args, **kwargs):
    if _use_alsaaudio:
        return _alsaaudio_SoundThread(*args, **kwargs)
    elif _use_simpleaudio:
        return _simpleaudio_SoundThread(*args, **kwargs)
    elif _use_winsound:
        return _winsound_SoundThread(*args, **kwargs)
    else:
        return _SoundThread(*args, **kwargs)


def read_wav(source, start=0, end=None):
    _warn("read_wav() is deprecated, use Sound() class instead",
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
    _warn("extract_sound() is deprecated, use Sound() class instead",
          DeprecationWarning)
    sound = read_wav(source, start, end)

    out_wav = wave.open(target, "wb")
    out_wav.setframerate(sound["framerate"])
    out_wav.setnchannels(sound["channels"])
    out_wav.setsampwidth(sound["samplewidth"])
    out_wav.writeframes(sound["data"])
    out_wav.close()

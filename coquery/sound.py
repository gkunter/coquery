# -*- coding: utf-8 -*-
"""
sound.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import wave

def extract_sound(source, target, start, end):
    """
    Extract a portion from the given source, and write it to the target.
    
    Parameters
    ----------
    source: either a stream object or a string with the source file name
    target: either a stream object or a string with the target file name
    start, end : Beginning and end in seconds    
    """
    in_wav = wave.open(source, "rb")
    fr = in_wav.getframerate()
    chan = in_wav.getnchannels()
    sw = in_wav.getsampwidth()
    in_wav.setpos(int(start * fr))
    data = in_wav.readframes(int((end - start) * fr))
    in_wav.close()
    
    out_wav = wave.open(target, "wb")
    out_wav.setframerate(fr)
    out_wav.setnchannels(chan)
    out_wav.setsampwidth(sw)
    out_wav.writeframes(data)
    out_wav.close()


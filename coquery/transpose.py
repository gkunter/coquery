# -*- coding: utf-8 -*-
"""
transpose.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

def arpa_to_ipa(s):
    """
    Translates an ARPAbet string to an IPA-encoded string.
    
    This translation is based on the information given on 
    https://en.wikipedia.org/wiki/Arpabet.
    """
    d = {"AO": "ɔ",
        "AA": "ɑ",
        "IY": "i",
        "UW": "u",
        "EH": "ɛ",
        "IH": "ɪ",
        "UH": "ʊ",
        "AH": "ʌ",
        "AX": "ə",
        "AE": "æ",
        "EY": "eɪ",
        "AY": "aɪ",
        "OW": "oʊ",
        "AW": "aʊ",
        "OY": "ɔɪ",
        "ER": "ɝ",
        "AXR": "ɚ",
        "EH": "ɛ",
        "UH": "ʊ",
        "IH": "ɪ",
        "AW": "aʊ",
        "P": "p",
        "B": "b",
        "T": "t",
        "D": "d",
        "K": "k",
        "G": "ɡ",
        "CH": "tʃ",
        "JH": "dʒ",
        "F": "f",
        "V": "v",
        "TH": "θ",
        "DH": "ð",
        "S": "s",
        "Z": "z",
        "SH": "ʃ",
        "ZH": "ʒ",
        "HH": "h",
        "M": "m",
        "EM": "m̩",
        "N": "n",
        "EN": "n̩",
        "NG": "ŋ",
        "ENG": "ŋ̍",
        "L": "l",
        "EL": "l̩̩",
        "R": "ɹ",
        "DX": "ɾ",
        "NX": "ɾ̃",
        "Y": "j",
        "W": "w",
        "Q": "ʔ"}
    phonemes = []
    for x in s.split():
        stress = None
        if x[-1] in "012":
            stress = x[-1]
            if x.endswith("1"):
                phonemes.append("ˈ")
            elif x.endswith("2"):
                phonemes.append("ˌ")
            x = x[:-1]
        if x == "AH" and stress == "0":
            x = "AX"
        phonemes.append(d.get(x, "?"))
    return "".join(phonemes)
# -*- coding: utf-8 -*-
"""
regextester.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

import re

from .pyqt_compat import QtWidgets
from .ui.regexTesterUi import Ui_RegexDialog

from coquery.unicode import utf8


class RegexDialog(QtWidgets.QDialog):
    content = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body>
<p align="justify" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Regular expression cheatsheet</span></p>
<p align="justify" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Any character that is not listed below has its literal meaning.</p>
<p align="justify" style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" width="100%" cellspacing="0" cellpadding="4">
<tr>
<td width="18%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Special character</span><span style=" text-decoration: underline;"> </span></p></td>
<td width="82%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Function</span><span style=" text-decoration: underline;"> </span></p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">.</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches any character except a new line </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">^</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the start of the string </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">$</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the end of the string </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Escapes the following special character, or signal a special sequence </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">A|B</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches either expression A or expression B </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">[ ]</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Indicates a set of characters</p></td></tr></table>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" width="100%" cellspacing="0" cellpadding="4">
<tr>
<td width="18%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Characters in a set</span><span style=" text-decoration: underline;"> </span></p></td>
<td width="82%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Function</span><span style=" text-decoration: underline;"> </span></p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">-</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Specifies a range of characters </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">^</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Negates the set, but only if it is the first character </p></td></tr></table>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" width="100%" cellspacing="0" cellpadding="4">
<tr>
<td width="18%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Character placeholders</span><span style=" text-decoration: underline;"> </span></p></td>
<td width="82%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Function</span><span style=" text-decoration: underline;"> </span></p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\A</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the start of string </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\\b</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the beginning of a word </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\B</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the end of a word </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\d</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches any decimal digit </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\D</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches any non-digit character </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\s</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches any whitespace character (e.g. spaces, tabs, newlines) </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\S</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches any non-whitespace character (e.g. alphanumeric characters, punctuation marks) </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\w</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches any alphanumeric character </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\W</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches any non-alphanumeric character </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">\Z</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the end of the string </p></td></tr></table>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" width="100%" cellspacing="0" cellpadding="4">
<tr>
<td width="18%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Quantifiers</span><span style=" text-decoration: underline;"> </span></p></td>
<td width="82%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Function</span><span style=" text-decoration: underline;"> </span></p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">*</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches zero or more repetitions of the preceding expression </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">*?</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Like <span style=" font-family:'Mono';">*</span>, but matches as few repetionts as possible </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">+</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches one or more repetitions of the preceding expression </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">+?</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Like <span style=" font-family:'Mono';">+</span>, but matches as few repetitions as possible </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">?</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches zero or one repetitions of the preceding expression </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">??</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Like <span style=" font-family:'Mono';">?</span>, but matches as few repetitions as possible </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">{m}</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches exactly <span style=" font-style:italic;">m</span> repetitions of the preceding expression </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">{m,n}</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches at least <span style=" font-style:italic;">m</span> repetitions, but up to <span style=" font-style:italic;">n</span> repetitions of the preceding expression </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">{m,n}?</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Like <span style=" font-family:'Mono';">{m,n}</span>, but matches as few repetitions as possible </p></td></tr></table>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" width="100%" cellspacing="0" cellpadding="4">
<tr>
<td width="18%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Groups</span><span style=" text-decoration: underline;"> </span></p></td>
<td width="82%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Function</span><span style=" text-decoration: underline;"> </span></p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(A)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the expression A, and places the result in a match group </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?:A)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the expression A, but do not form a match group </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?P&lt;name&gt;A)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the expression A, and places the result in a match group labelled name </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?P=name)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches the text that was matched by the earlier group labelled name </p></td></tr></table>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" width="100%" cellspacing="0" cellpadding="4">
<tr>
<td width="18%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Positional assertions</span><span style=" text-decoration: underline;"> </span></p></td>
<td width="82%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Function</span><span style=" text-decoration: underline;"> </span></p></td></tr>
<tr>
<td colspan="2" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">These assertions match if the specified expression matches either the text preceding or following the current position. They do not consume the matching string, i.e. they do not change the current position. </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?=A)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches if the following string matches the expression A (“lookahead assertion“) </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?!A)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches if the following string does not match the expression A; “negative lookahead assertion“, i.e. the negation of <span style=" font-family:'Mono';">(?=A)</span> </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?&lt;=A)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches if the current position in the string is preceded by a match of the expression A; “positive lookbehind assertion“ </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?&lt;!A)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Matches if the current position in the string is not preceded by a match of the expression A; “negative lookbehind assertion“, i.e. the negation of <span style=" font-family:'Mono';">(?&lt;=A)</span> </p></td></tr></table>
<p align="justify" style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" width="100%" cellspacing="0" cellpadding="4">
<tr>
<td width="18%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Switches</span><span style=" text-decoration: underline;"> </span></p></td>
<td width="82%" style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Function</span><span style=" text-decoration: underline;"> </span></p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?i)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Makes the match case-insensitive </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?L)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Makes the match use the locale setting of the current system </p></td></tr>
<tr>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Mono';">(?iL)</span> </p></td>
<td style=" vertical-align:top; padding-left:0; padding-right:0; padding-top:0; padding-bottom:0;">
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Combines the effect of <span style=" font-family:'Mono';">(?i)</span> and <span style=" font-family:'Mono';">(?L)</span> </p></td></tr></table>
<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">"""

    def __init__(self, parent=None):
        super(RegexDialog, self).__init__(parent)
        self.ui = Ui_RegexDialog()
        self.ui.setupUi(self)
        self.ui.text_cheatsheet.setText(self.content)

        self.ui.edit_regex.textChanged.connect(self.evaluate_regex)
        self.ui.edit_test_string.textChanged.connect(self.evaluate_regex)

    def evaluate_regex(self):
        regex = utf8(self.ui.edit_regex.text())
        test_string = utf8(self.ui.edit_test_string.text())

        # put the regex into parentheses if there is no match group:
        if not re.search(r"\([^)]*\)", regex):
            regex = "({})".format(regex)

        match = None
        try:
            match = re.search(regex, test_string)
        except Exception as e:
            self.ui.label_error.setText(str(e))
            self.ui.label_error.setStyleSheet("""
                background-color: red; color: white; """)
        else:
            self.ui.label_error.setText("")
            self.ui.label_error.setStyleSheet("")

            if not match:
                self.ui.label_error.setText("No match.")
                self.ui.table_groups.setRowCount(0)
                self.ui.edit_regex.setStyleSheet("""
                    background-color: rgb(255, 255, 192); color: black; """)
            else:
                self.ui.edit_regex.setStyleSheet("")
                self.ui.table_groups.setRowCount(len(match.groups()))
                for i, grp in enumerate(match.groups()):
                    self.ui.table_groups.setItem(
                        i, 0, QtWidgets.QTableWidgetItem(str(grp)))

    @staticmethod
    def show(parent=None):
        dialog = RegexDialog(parent=parent)
        dialog.setVisible(True)
        return dialog.exec_()

# -*- coding: utf-8 -*-
"""
independencetestviewer.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import sys

from coquery import options
from coquery.unicode import utf8
from coquery.queries import ContrastQuery

from .pyqt_compat import QtGui, QtCore
from .ui.independenceTestViewerUi import Ui_IndependenceTestViewer

if options._use_scipy:
    from scipy import stats
    import numpy as np

class IndependenceTestViewer(QtGui.QDialog):
    html_template = """
        <body>
            <p><span style="font-weight:600;">Contingency table</span></p>
            <p>
            <table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" cellspacing="2" cellpadding="0">
                <tr style="border-syle:solid; border-width: 1px 0px 1px 0px;">
                    <td></td>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">{{label_1}}</span></p></td>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">{{label_2}}</span></p></td>
                </tr>
                <tr>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">Frequency</span></p></td>
                    <td><p align="right" style="margin-right: 2em;">{{freq_1}}</p></td>
                    <td><p align="right" style="margin-right: 2em;">{{freq_2}}</p></td>
                </tr>
                <tr style="border-syle:solid; border-width: 0px 0px 1px 0px;">
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">Subcorpus size</span></p></td>
                    <td><p align="right" style="margin-right: 2em;">{{total_1}}</p></td>
                    <td><p align="right" style="margin-right: 2em;">{{total_2}}</p></td>
                </tr>
            </table></p>
            <p><span style="font-weight:600;">Log-likelihood ratio test of independence</span></p>
            <p><span style=" font-style:italic;">G</span><sup>2</sup> = {{g2:0.3f}}, <span style=" font-style:italic;">df</span> = 1, <span style=" font-style:italic;">p</span> {{p_op}} {{p_g2:0.3f}}</p>
            {chisquare}
            {{yates}}
    """.strip()

    if options._use_scipy:
        chisq_template = """
                <p><span style="font-weight:600;">Chi-square test of independence</span></p>
                <p><span style=" font-style:italic;">χ</span><sup>2</sup> = {chi2:0.3f}, <span style=" font-style:italic;">df</span> = 1, <span style=" font-style:italic;">p</span> = {p_chi2:0.3f}</p>
        """.strip()
    else:
        chisq_template = ""
        
    html_template = html_template.format(chisquare=chisq_template)    
    
    def __init__(self, data=dict(), parent=None, icon=None):
        super(IndependenceTestViewer, self).__init__(parent)
        
        self.parent = parent
        self.ui = Ui_IndependenceTestViewer()
        self.ui.setupUi(self)
        
        freq_1 = data["freq_row"]
        freq_2 = data["freq_col"]
        total_1 = data["total_row"]
        total_2 = data["total_col"]

        yates = ""

        if options._use_scipy:
            obs = [ [freq_1, freq_2], [total_1 - freq_1, total_2 - freq_2]]
            expected = stats.contingency.expected_freq(obs)
            if np.min(expected) < 5:
                yates = "<p>(using Yates' correction for continuity)</p>"
            
            g2, p_g2, _, _ = stats.chi2_contingency(obs, correction=bool(yates), lambda_="log-likelihood")
            p_op = "="
            chi2, p_chi2, _, _ = stats.chi2_contingency(obs, correction=bool(yates))
        else:
            g2 = ContrastQuery.g_test(freq_1, freq_2, total_1, total_2)
            p_op = "&lt;"
            if g2 > 10.83:
                p_g2 = 0.001
            elif g2 > 6.63:
                p_g2 = 0.01
            elif g2 > 3.84:
                p_g2 = 0.05
            else:
                p_g2 = 0.05
                p_op = "&ge;"
            chi2 = ""
            p_chi2 = ""
        
        self.ui.textBrowser.setHtml(utf8(self.html_template.format(
            label_1="Label1", label_2="Label2",
            freq_1=freq_1, freq_2=freq_2,
            total_1=total_1, total_2=total_2,
            g2=g2, p_g2=p_g2, p_op=p_op,
            chi2=chi2, p_chi2=p_chi2,
            yates=yates)))
        
        try:
            self.resize(options.settings.value("independencetestviewer_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("independencetestviewer_size", self.size())
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

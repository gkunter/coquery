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
import math

from coquery import options
from coquery.unicode import utf8
from coquery.queries import ContrastQuery

from .pyqt_compat import QtGui, QtCore
from .ui.independenceTestViewerUi import Ui_IndependenceTestViewer

import numpy as np
if options._use_scipy:
    from scipy import stats

class IndependenceTestViewer(QtGui.QDialog):
    html_template = """
        <body>
            <h1><span style="font-weight:600;">Corpus {corpus}</span></h1>
            {filters}
            <p>
            <table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" cellspacing="2" cellpadding="0">
                <tr style="border-syle:solid; border-width: 1px 0px 1px 0px;">
                    <td></td>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">{label_1}</span></p></td>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">{label_2}</span></p></td>
                </tr>
                <tr>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">Frequency</span></p></td>
                    <td><p align="right" style="margin-right: 2em;">{freq_1}</p></td>
                    <td><p align="right" style="margin-right: 2em;">{freq_2}</p></td>
                </tr>
                <tr style="border-syle:solid; border-width: 0px 0px 1px 0px;">
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">Subcorpus size</span></p></td>
                    <td><p align="right" style="margin-right: 2em;">{total_1}</p></td>
                    <td><p align="right" style="margin-right: 2em;">{total_2}</p></td>
                </tr>
            </table></p>
            <h2>Log-likelihood ratio test of independence</h2>
            <p><span style=" font-style:italic;">G</span><sup>2</sup> = {g2}, <span style=" font-style:italic;">df</span> = 1, <span style=" font-style:italic;">p</span> {g2_op} {p_g2}</p>
            <h2>Chi-square test of independence</h2>
            <p><span style=" font-style:italic;">χ</span><sup>2</sup> = {chi2}, <span style=" font-style:italic;">df</span> = 1, <span style=" font-style:italic;">p</span> {chi2_op} {p_chi2}</p>
            {yates}
            <h2>Effect size estimations</h2>
            <p><span style=" font-style:italic;">&phi;</span> = {phi}, indicating a {strength} effect size (see Cohen 1992, <a href='https://dx.doi.org/10.1037%2F0033-2909.112.1.155'>doi:10.1037/0033-2909.112.1.155)</a></p>
            <p>Odds ratio <span style=" font-style:italic;">OR</span>= {odds_ratio}</p>
        </body>
    """.strip()

    latex_template = """
    \\textbf{{Corpus {corpus}}}
    {filters}
    \\begin{{table}}[htbp]
        \\centering
        \\begin{{tabular}}{{rrr}}
        \\hline
                            & \\textbf{{{label_1}}}  & \\textbf{{{label_2}}} \\\\ 
        \\hline
        \\textbf{{Frequency}}        & {freq_1}  & {freq_2} \\\\ 
        \\textbf{{Subcorpus size}}   & {total_1} & {total_2}  \\\\ 
        \\hline
        \\end{{tabular}}
    \\end{{table}}

    \\textbf{{Log-likelihood ratio test of independence}}
    
    $G^2 = {g2}, p {g2_op} {p_g2}$

    \\textbf{{Chi-square test of independence}}
    
    $\\chi^2 = {chi2}, p {chi2_op} {p_chi2}$
    """

    def __init__(self, data=dict(), parent=None, icon=None):
        def estimate_p(chi):
            """
            Return an approximation of the p value for the parameter.
            
            Returns
            -------
            value : str 
                A string, giving an estimat eof p. Possible values are:
                "< 0.001"
                "< 0.01"
                "< 0.05"
                "≥ 0.05"
            """
            if chi > 10.83:
                return "< 0.001"
            elif chi > 6.63:
                return "< 0.01"
            elif chi > 3.84:
                return "< 0.05"
            else:
                return "≥ 0.05"

        def estimate_strength(phi):
            if phi <= 0.1:
                return "small"
            elif phi <= 0.3:
                return "medium"
            else:
                return "strong"

        super(IndependenceTestViewer, self).__init__(parent)
        
        self.parent = parent
        self.ui = Ui_IndependenceTestViewer()
        self.ui.setupUi(self)
        
        freq_1 = data["freq_row"]
        freq_2 = data["freq_col"]
        total_1 = data["total_row"]
        total_2 = data["total_col"]
        label_1 = data["label_row"]
        label_2 = data["label_col"]
        yates = ""
        obs = np.array([ [freq_1, freq_2], [total_1 - freq_1, total_2 - freq_2]])

        if options._use_scipy:
            expected = stats.contingency.expected_freq(obs)
            if np.min(expected) < 5:
                yates = "<p>(using Yates' correction for continuity)</p>"
            
            g2, p_g2, _, _ = stats.chi2_contingency(obs, correction=bool(yates), lambda_="log-likelihood")
            g2_op = "="
            chi2_op = "="
            chi2, p_chi2, _, _ = stats.chi2_contingency(obs, correction=bool(yates))
        else:
            g2 = ContrastQuery.g_test(freq_1, freq_2, total_1, total_2)
            g2_op, p_g2 = estimate_p(g2).split()

            # calculate chi-square:
            total_freq = freq_1 + freq_2
            total_corpus = total_1 + total_2 - total_freq
            total_table = total_freq + total_corpus
            
            expected = np.array([ 
                [total_freq * total_1 / total_table, total_freq * total_2 / total_table],
                [total_corpus * total_1 / total_table, total_corpus * total_2 / total_table]
                ])
                
            if yates:
                correct = 0.5
            else:
                correct = 0
            chisq = (np.vectorize(lambda x: x**2)(abs(obs - expected) - correct)/expected).sum()
            chi2_op, p_chi2 = estimate_p(chisq).split()
        
        if options.cfg.main_window.Session.filter_list:
            filter_html = """
            <p>Active filters:<br/>
            {}
            </p>
            """.format("<br/>".join(["<code>{}</code>".format(x) for x in options.cfg.main_window.Session.filter_list]))
            filter_latex = """
            <p>Active filters:\\\\
            {}
            </p>
            """.format("\\\\".join(["\\texttt{{{}}}".format(x) for x in options.cfg.main_window.Session.filter_list]))
        else:
            filter_html = ""
            filter_latex = ""

        phi = math.sqrt(chi2/obs.sum())
        odds_ratio = (freq_1/freq_2)/((total_1 - freq_1)/(total_2 - freq_2))

        str_flt = "{{:0.{digits}f}}".format(digits=options.cfg.digits)
        
        self._html = utf8(self.html_template.format(
            corpus=utf8(options.cfg.main_window.ui.combo_corpus.currentText()),
            filters=filter_html,
            label_1=label_1, label_2=label_2,
            freq_1=freq_1, freq_2=freq_2,
            total_1=total_1, total_2=total_2,
            g2=str_flt.format(g2), p_g2=str_flt.format(p_g2), g2_op=g2_op,
            chi2=str_flt.format(chi2), p_chi2=str_flt.format(p_chi2), chi2_op=chi2_op,
            phi=str_flt.format(phi), strength=estimate_strength(phi),
            odds_ratio=str_flt.format(odds_ratio),
            yates=yates))
        
        self._latex = utf8(self.latex_template.format(
            corpus=utf8(options.cfg.main_window.ui.combo_corpus.currentText()),
            filters=filter_latex,
            label_1=label_1, label_2=label_2,
            freq_1=freq_1, freq_2=freq_2,
            total_1=total_1, total_2=total_2,
            g2=str_flt.format(g2), p_g2=str_flt.format(p_g2), g2_op=g2_op,
            chi2=str_flt.format(chi2), p_chi2=str_flt.format(p_chi2), chi2_op=chi2_op,
            yates=yates))

        self.ui.textBrowser.setHtml(self._html)

        self.ui.button_copy_text.clicked.connect(lambda: self.copy_to_clipboard("text"))
        self.ui.button_copy_html.clicked.connect(lambda: self.copy_to_clipboard("html"))
        self.ui.button_copy_latex.clicked.connect(lambda: self.copy_to_clipboard("latex"))

        try:
            self.resize(options.settings.value("independencetestviewer_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("independencetestviewer_size", self.size())
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def copy_to_clipboard(self, mode):
        cb = QtGui.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        if mode == "text":
            cb.setText(self.ui.textBrowser.toPlainText())
        elif mode == "html":
            cb.setText(self._html)
        elif mode == "latex":
            cb.setText(self._latex)
            
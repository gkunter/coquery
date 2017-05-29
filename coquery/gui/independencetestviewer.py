# -*- coding: utf-8 -*-
"""
independencetestviewer.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import math
import numpy as np
import scipy

from coquery import options
from coquery.unicode import utf8

from .pyqt_compat import QtWidgets, QtCore, get_toplevel_window
from .ui.independenceTestViewerUi import Ui_IndependenceTestViewer


class IndependenceTestViewer(QtWidgets.QDialog):
    html_template = """
        <body>
            <h1><span style="font-weight:600;">Corpus: {corpus}</span></h1>
            <p>
            <table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" cellspacing="2" cellpadding="0">
                <tr>
                    <td></td>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">{label_1}</span></p></td>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">{label_2}</span></p></td>
                </tr>
                <tr>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">Frequency</span></p></td>
                    <td><p align="right" style="margin-right: 2em;">{freq_1}</p></td>
                    <td><p align="right" style="margin-right: 2em;">{freq_2}</p></td>
                </tr>
                <tr>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">Subcorpus size</span></p></td>
                    <td><p align="right" style="margin-right: 2em;">{total_1}</p></td>
                    <td><p align="right" style="margin-right: 2em;">{total_2}</p></td>
                </tr>
                <tr>
                    <td><p align="right" style="margin-right: 2em;"><span style=" font-weight:600;">Normalized frequency</span></p></td>
                    <td><p align="right" style="margin-right: 2em;">{nfreq_1}&nbsp;%</p></td>
                    <td><p align="right" style="margin-right: 2em;">{nfreq_2}&nbsp;%</p></td>
                </tr>
            </table></p>
            <h2>Log-likelihood ratio test of independence</h2>
            <p><span style="font-style:italic;">G</span> = {g2}, <span style=" font-style:italic;">df</span> = 1, <span style=" font-style:italic;">p</span> {g2_op} {p_g2} {sign}</p>
            <h2>Chi-square test of independence</h2>
            <p><span style="font-style:italic;">χ</span><sup>2</sup> = {chi2}, <span style=" font-style:italic;">df</span> = 1, <span style=" font-style:italic;">p</span> {chi2_op} {p_chi2}</p>
            {yates}
            <h2>Effect size estimations</h2>
            <p><span style=" font-style:italic;">&phi;</span> = {phi}, indicating a {strength} effect size (see Cohen 1992, <a href='https://dx.doi.org/10.1037%2F0033-2909.112.1.155'>doi:10.1037/0033-2909.112.1.155</a>)</p>
            <p>Odds ratio <span style=" font-style:italic;">OR</span> = {odds_ratio} (95&nbsp;% confidence interval: {odds_ci_lower} to {odds_ci_upper}, <span style=" font-style:italic;">z</span> = {odds_z}, <span style=" font-style:italic;">p</span> {odds_op} {p_odds}). {odds_explain}</p>
        </body>
    """.strip()

    latex_template = """
    \\textbf{{Corpus: {corpus}}}
    \\begin{{table}}[htbp]
        \\centering
        \\begin{{tabular}}{{rrr}}
        \\hline
                            & \\textbf{{{label_1}}}  & \\textbf{{{label_2}}} \\\\
        \\hline
        \\textbf{{Frequency}}        & {freq_1}  & {freq_2} \\\\
        \\textbf{{Subcorpus size}}   & {total_1} & {total_2}  \\\\
        \\textbf{{Normalized frequency}}   & {nfreq_1}~\\% & {nfreq_2}~\\%  \\\\
        \\hline
        \\end{{tabular}}
    \\end{{table}}

    \\textbf{{Log-likelihood ratio test of independence}}

    $G = {g2}, p {g2_op} {p_g2}$

    \\textbf{{Chi-square test of independence}}

    $\\chi^2 = {chi2}, p {chi2_op} {p_chi2}$

    {yates}
    \\textbf{{Effect size estimations}}

    $\\phi = {phi}$, indicating a {strength} effect size (see Cohen 1992, doi:10.1037/0033-2909.112.1.155)

    Odds ratio $OR = {odds_ratio}$, (95~\\% confidence interval: {odds_ci_lower} to {odds_ci_upper}, $z = {odds_z}, p {odds_op} {p_odds}$). {odds_explain}.
    """

    def __init__(self, data=dict(), parent=None, icon=None):
        def estimate_strength(phi):
            """
            Apply standard interpretation of effect sizes (Cohen 1988, 1992)
            """
            if phi < 0.1:
                return "marginal"
            elif 0.1 <= phi < 0.3:
                return "small"
            elif 0.3 <= phi < 0.5:
                return "medium"
            elif 0.5 <= phi:
                return "strong"

        super(IndependenceTestViewer, self).__init__(parent)
        session = get_toplevel_window().Session
        manager = session.get_manager()
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
        obs = np.array([
            [freq_1, freq_2],
            [total_1 - freq_1, total_2 - freq_2]])

        str_flt = "{{:0.{digits}f}}".format(digits=options.cfg.digits)

        expected = scipy.stats.contingency.expected_freq(obs)
        if np.min(expected) < 5:
            yates = "<p>Tests use Yates' correction for continuity.</p>"

        g2, p_g2, _, _ = scipy.stats.chi2_contingency(
            obs, correction=bool(yates), lambda_="log-likelihood")
        g2_op = "="
        chi2_op = "="
        chi2, p_chi2, _, _ = scipy.stats.chi2_contingency(
            obs, correction=bool(yates))

        sign_template = "({res} at adjusted <span style='font-style:italic;'>α</span> = {adj_a}{ref})"
        sign_string = sign_template.format(
                        res=("not significant"
                             if p_g2 > manager.alpha else "significant"),
                        adj_a=(str_flt.format(manager.alpha)
                               if manager.alpha < 0.05 else 0.05),
                        ref=(", Benjamini and Hochberg 1995"
                             if manager.alpha < 0.05 else ""))

        # Calculate Cramér's Phi for the 2x2 case:
        try:
            phi = math.sqrt(chi2/obs.sum())
        except:
            phi = "(undefined)"

        # calculate odds ratio (with correction for empty cells):
        if not freq_1 or not freq_2 or freq_1 == total_1 or freq_2 == total_2:
            odds_ratio = (((freq_1 + 0.5) / (freq_2 + 0.5)) /
                          ((total_1 - freq_1 + 0.5)/(total_2 - freq_2 + 0.5)))
            odds_se = math.sqrt(
                1/(freq_1 + 0.5) +
                1/(freq_2 + 0.5) +
                1/(total_1 - freq_1 + 0.5) +
                1/(total_2 - freq_2 + 0.5))
        else:
            odds_ratio = ((freq_1/freq_2) /
                          ((total_1 - freq_1)/(total_2 - freq_2)))
            odds_se = math.sqrt(
                1/freq_1 +
                1/freq_2 +
                1/(total_1 - freq_1) +
                1/(total_2 - freq_2))
        odds_ci_lower = math.exp(math.log(odds_ratio) - 1.96 * odds_se)
        odds_ci_upper = math.exp(math.log(odds_ratio) + 1.96 * odds_se)
        odds_z = math.log(odds_ratio) / odds_se

        p_odds = scipy.stats.norm.sf(abs(odds_z)) * 2
        odds_op = "="

        if p_odds < 0.05:
            odds_explain = "This means that the odds of encountering tokens which match the query in the subcorpus '<code>{label_1}</code>' is {odds_prose} times {odds_relation} than the odds of encountering matching tokens in the subcorpus '<code>{label_2}</code>'.".format(
                odds_prose=str_flt.format(
                    odds_ratio if odds_ratio > 1 else 1/odds_ratio),
                odds_relation="higher" if odds_ratio > 1 else "lower",
                label_1=label_1, label_2=label_2
                )
        else:
            odds_explain = "The high value of <span style=' font-style:italic;'>p</span> suggests that the odds of encountering tokens which match the query in the subcorpus '<code>{label_1}</code>' is not significantly different from the odds of encountering matching tokens in the subcorpus '<code>{label_2}</code>'.".format(
                label_1=label_1, label_2=label_2)

        corpus = utf8(get_toplevel_window().ui.combo_corpus.currentText())
        self._html = utf8(self.html_template.format(
            corpus=corpus,
            label_1=label_1, label_2=label_2,
            freq_1=freq_1, freq_2=freq_2,
            total_1=total_1, total_2=total_2,
            nfreq_1=str_flt.format(100*freq_1/total_1),
            nfreq_2=str_flt.format(100*freq_2/total_2),
            g2=str_flt.format(g2),
            p_g2=str_flt.format(p_g2),
            sign=sign_string,
            adj_a=str_flt.format(manager.alpha),
            g2_op=g2_op.replace("<", "&lt;"),
            chi2=str_flt.format(chi2),
            p_chi2=str_flt.format(p_chi2),
            chi2_op=chi2_op.replace("<", "&lt;"),
            phi=str_flt.format(phi), strength=estimate_strength(phi),
            odds_ratio=str_flt.format(odds_ratio),
            odds_ci_lower=str_flt.format(odds_ci_lower),
            odds_ci_upper=str_flt.format(odds_ci_upper),
            odds_z=str_flt.format(odds_z),
            odds_op=odds_op.replace("<", "&lt;"),
            odds_explain=odds_explain,
            p_odds=str_flt.format(p_odds),
            yates=yates))

        self._latex = utf8(self.latex_template.format(
            corpus=corpus,
            label_1=label_1, label_2=label_2,
            freq_1=freq_1, freq_2=freq_2,
            total_1=total_1, total_2=total_2,
            nfreq_1=str_flt.format(100*freq_1/total_1),
            nfreq_2=str_flt.format(100*freq_2/total_2),
            g2=str_flt.format(g2),
            p_g2=str_flt.format(p_g2),
            sign=sign_string,
            adj_a=str_flt.format(manager.alpha),
            g2_op=g2_op,
            chi2=str_flt.format(chi2),
            p_chi2=str_flt.format(p_chi2),
            chi2_op=chi2_op,
            phi=str_flt.format(phi), strength=estimate_strength(phi),
            odds_ratio=str_flt.format(odds_ratio),
            odds_ci_lower=str_flt.format(odds_ci_lower),
            odds_ci_upper=str_flt.format(odds_ci_upper),
            odds_prose=str_flt.format(
                odds_ratio if odds_ratio > 1 else 1/odds_ratio),
            odds_relation="higher" if odds_ratio > 1 else "lower",
            odds_z=str_flt.format(odds_z),
            odds_op=odds_op,
            p_odds=str_flt.format(p_odds),
            odds_explain=odds_explain,
            yates=yates))

        self.ui.textBrowser.setHtml(self._html)

        self.ui.button_copy_text.clicked.connect(
            lambda: self.copy_to_clipboard("text"))
        self.ui.button_copy_html.clicked.connect(
            lambda: self.copy_to_clipboard("html"))
        self.ui.button_copy_latex.clicked.connect(
            lambda: self.copy_to_clipboard("latex"))

        try:
            self.resize(options.settings.value(
                "independencetestviewer_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue(
            "independencetestviewer_size", self.size())

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def copy_to_clipboard(self, mode):
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        if mode == "text":
            cb.setText(self.ui.textBrowser.toPlainText())
        elif mode == "html":
            cb.setText(self._html)
        elif mode == "latex":
            cb.setText(self._latex)

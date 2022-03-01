# -*- coding: utf-8 -*-
"""
poshelper.py is part of Coquery.

Copyright (c) 2017-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5 import QtCore, QtWidgets

from coquery import options
from coquery.gui.pyqt_compat import get_toplevel_window, STYLE_WARN
from coquery.gui.ui.posHelperDialogUi import Ui_PosHelperDialog
from coquery.gui.widgets.coqwidgetfader import CoqWidgetFader
from coquery.unicode import utf8

tagsets = {"Penn Treebank": [
            ("CC", "Coordinating conjunction"),
            ("CD", "Cardinal number"),
            ("DT", "Determiner"),
            ("EX", "Existential there"),
            ("FW", "Foreign word"),
            ("IN", "Preposition or subordinating conjunction"),
            ("JJ", "Adjective"),
            ("JJR", "Adjective, comparative"),
            ("JJS", "Adjective, superlative"),
            ("LS", "List item marker"),
            ("MD", "Modal"),
            ("NN", "Noun, singular or mass"),
            ("NNS", "Noun, plural"),
            ("NNP", "Proper noun, singular"),
            ("NNPS", "Proper noun, plural"),
            ("PDT", "Predeterminer"),
            ("POS", "Possessive ending"),
            ("PRP", "Personal pronoun"),
            ("PRP$", "Possessive pronoun"),
            ("RB", "Adverb"),
            ("RBR", "Adverb, comparative"),
            ("RBS", "Adverb, superlative"),
            ("RP", "Particle"),
            ("SYM", "Symbol"),
            ("TO", "to"),
            ("UH", "Interjection"),
            ("VB", "Verb, base form"),
            ("VBD", "Verb, past tense"),
            ("VBG", "Verb, gerund or present participle"),
            ("VBN", "Verb, past participle"),
            ("VBP", "Verb, non-3rd person singular present"),
            ("VBZ", "Verb, 3rd person singular present"),
            ("WDT", "Wh-determiner"),
            ("WP", "Wh-pronoun"),
            ("WP$", "Possessive wh-pronoun"),
            ("WRB", "Wh-adverb")],
        "CLAWS5": [
            ("AJ0", "adjective (unmarked) (e.g. <i>GOOD</i>, <i>OLD</i>)"),
            ("AJC", "comparative adjective (e.g. <i>BETTER</i>, <i>OLDER</i>)"),
            ("AJS", "superlative adjective (e.g. <i>BEST</i>, <i>OLDEST</i>)"),
            ("AT0", "article (e.g. <i>THE</i>, <i>A</i>, <i>AN</i>)"),
            ("AV0", "adverb (unmarked) (e.g. <i>OFTEN</i>, <i>WELL</i>, <i>LONGER</i>, <i>FURTHEST</i>)"),
            ("AVP", "adverb particle (e.g. <i>UP</i>, <i>OFF</i>, <i>OUT</i>)"),
            ("AVQ", "wh-adverb (e.g. <i>WHEN</i>, <i>HOW</i>, <i>WHY</i>)"),
            ("CJC", "coordinating conjunction (e.g. <i>AND</i>, <i>OR</i>)"),
            ("CJS", "subordinating conjunction (e.g. <i>ALTHOUGH</i>, <i>WHEN</i>)"),
            ("CJT", "the conjunction <i>THAT</i>"),
            ("CRD", "cardinal numeral (e.g. <i>3</i>, <i>FIFTY</i>-FIVE, <i>6609</i>) (excl <i>ONE</i>)"),
            ("DPS", "possessive determiner form (e.g. <i>YOUR</i>, <i>THEIR</i>)"),
            ("DT0", "general determiner (e.g. <i>THESE</i>, <i>SOME</i>)"),
            ("DTQ", "wh-determiner (e.g. <i>WHOSE</i>, <i>WHICH</i>)"),
            ("EX0", "existential <i>THERE</i>"),
            ("ITJ", "interjection or other isolate (e.g. <i>OH</i>, <i>YES</i>, <i>MHM</i>)"),
            ("NN0", "noun (neutral for number) (e.g. <i>AIRCRAFT</i>, <i>DATA</i>)"),
            ("NN1", "singular noun (e.g. <i>PENCIL</i>, <i>GOOSE</i>)"),
            ("NN2", "plural noun (e.g. <i>PENCILS</i>, <i>GEESE</i>)"),
            ("NP0", "proper noun (e.g. <i>LONDON</i>, <i>MICHAEL</i>, <i>MARS</i>)"),
            ("ORD", "ordinal (e.g. <i>SIXTH</i>, <i>77TH</i>, <i>LAST</i>)"),
            ("PNI", "indefinite pronoun (e.g. <i>NONE</i>, <i>EVERYTHING</i>)"),
            ("PNP", "personal pronoun (e.g. <i>YOU</i>, <i>THEM</i>, <i>OURS</i>)"),
            ("PNQ", "wh-pronoun (e.g. <i>WHO</i>, <i>WHOEVER</i>)"),
            ("PNX", "reflexive pronoun (e.g. <i>ITSELF</i>, <i>OURSELVES</i>)"),
            ("POS", "the possessive (or genitive morpheme) <i>'S</i> or <i>'</i>"),
            ("PRF", "the preposition <i>OF</i>"),
            ("PRP", "preposition (except for <i>OF</i>) (e.g. <i>FOR</i>, <i>ABOVE</i>, <i>TO</i>)"),
            ("PUL", "punctuation - left bracket (i.e. <i>(</i> or <i>[</i> )"),
            ("PUN", "punctuation - general mark (i.e. <i>. ! , : ; - ? ... </i>)"),
            ("PUQ", "punctuation - quotation mark (i.e. <i>` ' \"</i>)"),
            ("PUR", "punctuation - right bracket (i.e. <i>)</i> or <i>]</i> )"),
            ("TO0", "infinitive marker <i>TO</i>"),
            ("UNC", "'unclassified' items which are not words of the English lexicon"),
            ("VBB", "the 'base forms' of the verb 'BE' (except the infinitive), i.e. <i>AM</i>, <i>ARE</i>"),
            ("VBD", "past form of the verb 'BE', i.e. <i>WAS</i>, <i>WERE</i>"),
            ("VBG", "-ing form of the verb 'BE', i.e. <i>BEING</i>"),
            ("VBI", "infinitive of the verb 'BE'"),
            ("VBN", "past participle of the verb 'BE', i.e. <i>BEEN</i>"),
            ("VBZ", "-s form of the verb 'BE', i.e. <i>IS</i>, <i>'S</i>"),
            ("VDB", "base form of the verb 'DO' (except the infinitive), i.e. <i>DO</i>"),
            ("VDD", "past form of the verb 'DO', i.e. <i>DID</i>"),
            ("VDG", "-ing form of the verb 'DO', i.e. <i>DOING</i>"),
            ("VDI", "infinitive of the verb 'DO'"),
            ("VDN", "past participle of the verb 'DO', i.e. <i>DONE</i>"),
            ("VDZ", "-s form of the verb 'DO', i.e. <i>DOES</i>"),
            ("VHB", "base form of the verb 'HAVE' (except the infinitive), i.e. <i>HAVE</i>"),
            ("VHD", "past tense form of the verb 'HAVE', i.e. <i>HAD</i>, <i>'D</i>"),
            ("VHG", "-ing form of the verb 'HAVE', i.e. <i>HAVING</i>"),
            ("VHI", "infinitive of the verb 'HAVE'"),
            ("VHN", "past participle of the verb 'HAVE', i.e. <i>HAD</i>"),
            ("VHZ", "-s form of the verb 'HAVE', i.e. <i>HAS</i>, <i>'S</i>"),
            ("VM0", "modal auxiliary verb (e.g. <i>CAN</i>, <i>COULD</i>, <i>WILL</i>, <i>'LL</i>)"),
            ("VVB", "base form of lexical verb (except the infinitive)(e.g. <i>TAKE</i>, <i>LIVE</i>)"),
            ("VVD", "past tense form of lexical verb (e.g. <i>TOOK</i>, <i>LIVED</i>)"),
            ("VVG", "-ing form of lexical verb (e.g. <i>TAKING</i>, <i>LIVING</i>)"),
            ("VVI", "infinitive of lexical verb"),
            ("VVN", "past participle form of lex. verb (e.g. <i>TAKEN</i>, <i>LIVED</i>)"),
            ("VVZ", "-s form of lexical verb (e.g. <i>TAKES</i>, <i>LIVES</i>)"),
            ("XX0", "the negative <i>NOT</i> or <i>N'T</i>"),
            ("ZZ0", "alphabetical symbol (e.g. <i>A</i>, <i>B</i>, <i>c</i>, <i>d</i>)")],
        "CLAWS7": [
            ("APPGE", "possessive pronoun, pre-nominal (e.g. <i>my</i>, <i>your</i>, <i>our</i>)"),
            ("AT", "article (e.g. <i>the</i>, <i>no</i>)"),
            ("AT1", "singular article (e.g. <i>a</i>, <i>an</i>, <i>every</i>)"),
            ("BCL", "before-clause marker (e.g. <i>in order (that)</i>,<i>in order (to)</i>)"),
            ("CC", "coordinating conjunction (e.g. <i>and</i>, <i>or</i>)"),
            ("CCB", "adversative coordinating conjunction (<i>but</i>)"),
            ("CS", "subordinating conjunction (e.g. <i>if</i>, <i>because</i>, <i>unless</i>, <i>so</i>, <i>for</i>)"),
            ("CSA", "<i>as</i> (as conjunction)"),
            ("CSN", "<i>than</i> (as conjunction)"),
            ("CST", "<i>that</i> (as conjunction)"),
            ("CSW", "<i>whether</i> (as conjunction)"),
            ("DA", "after-determiner or post-determiner capable of pronominal function (e.g. <i>such</i>, <i>former</i>, <i>same</i>)"),
            ("DA1", "singular after-determiner (e.g. <i>little</i>, <i>much</i>)"),
            ("DA2", "plural after-determiner (e.g. <i>few</i>, <i>several</i>, <i>many</i>)"),
            ("DAR", "comparative after-determiner (e.g. <i>more</i>, <i>less</i>, <i>fewer</i>)"),
            ("DAT", "superlative after-determiner (e.g. <i>most</i>, <i>least</i>, <i>fewest</i>)"),
            ("DB", "before determiner or pre-determiner capable of pronominal function (<i>all</i>, <i>half</i>)"),
            ("DB2", "plural before-determiner (<i>both</i>)"),
            ("DD", "determiner (capable of pronominal function) (e.g <i>any</i>, <i>some</i>)"),
            ("DD1", "singular determiner (e.g. <i>this</i>, <i>that</i>, <i>another</i>)"),
            ("DD2", "plural determiner (<i>these</i>, <i>those</i>)"),
            ("DDQ", "wh-determiner (<i>which</i>, <i>what</i>)"),
            ("DDQGE", "wh-determiner, genitive (<i>whose</i>)"),
            ("DDQV", "wh-ever determiner, (<i>whichever</i>, <i>whatever</i>)"),
            ("EX", "existential <i>there</i>"),
            ("FO", "formula"),
            ("FU", "unclassified word"),
            ("FW", "foreign word"),
            ("GE", "germanic genitive marker - (<i>'</i></i> or <i>'s</i></i>)"),
            ("IF", "<i>for</i> (as preposition)"),
            ("II", "general preposition"),
            ("IO", "<i>of</i> (as preposition)"),
            ("IW", "<i>with</i>, <i>without</i> (as prepositions)"),
            ("JJ", "general adjective"),
            ("JJR", "general comparative adjective (e.g. <i>older</i>, <i>better</i>, <i>stronger</i>)"),
            ("JJT", "general superlative adjective (e.g. <i>oldest</i>, <i>best</i>, <i>strongest</i>)"),
            ("JK", "catenative adjective (<i>able</i> in <i>be able to</i>, <i>willing</i> in <i>be willing to</i>)"),
            ("MC", "cardinal number, neutral for number (<i>two</i>, <i>three</i>, ...)"),
            ("MC1", "singular cardinal number (<i>one</i>)"),
            ("MC2", "plural cardinal number (e.g. <i>sixes</i>, <i>sevens</i>)"),
            ("MCGE", "genitive cardinal number, neutral for number (<i>two's</i></i>, <i>100's</i></i>)"),
            ("MCMC", "hyphenated number (<i>40-50</i></i>, <i>1770-1827</i></i>)"),
            ("MD", "ordinal number (e.g. <i>first</i>, <i>second</i>, <i>next</i>, <i>last</i>)"),
            ("MF", "fraction,neutral for number (e.g. <i>quarters</i>, <i>two-thirds</i></i>)"),
            ("ND1", "singular noun of direction (e.g. <i>north</i>, <i>southeast</i>)"),
            ("NN", "common noun, neutral for number (e.g. <i>sheep</i>, <i>cod</i>, <i>headquarters</i>)"),
            ("NN1", "singular common noun (e.g. <i>book</i>, <i>girl</i>)"),
            ("NN2", "plural common noun (e.g. <i>books</i>, <i>girls</i>)"),
            ("NNA", "following noun of title (e.g. <i>M.A.</i>)"),
            ("NNB", "preceding noun of title (e.g. <i>Mr.</i></i>, <i>Prof</i>.</i>)"),
            ("NNL1", "singular locative noun (e.g. <i>Island</i>, <i>Street</i>)"),
            ("NNL2", "plural locative noun (e.g. <i>Islands</i>, <i>Streets</i>)"),
            ("NNO", "numeral noun, neutral for number (e.g. <i>dozen</i>, <i>hundred</i>)"),
            ("NNO2", "numeral noun, plural (e.g. <i>hundreds</i>, <i>thousands</i>)"),
            ("NNT1", "temporal noun, singular (e.g. <i>day</i>, <i>week</i>, <i>year</i>)"),
            ("NNT2", "temporal noun, plural (e.g. <i>days</i>, <i>weeks</i>, <i>years</i>)"),
            ("NNU", "unit of measurement, neutral for number (e.g. <i>in</i>, <i>cc</i>)"),
            ("NNU1", "singular unit of measurement (e.g. <i>inch</i>, <i>centimetre</i>)"),
            ("NNU2", "plural unit of measurement (e.g. <i>ins</i>., <i>feet</i>)"),
            ("NP", "proper noun, neutral for number (e.g. <i>IBM</i>, <i>Andes</i>)"),
            ("NP1", "singular proper noun (e.g. <i>London</i>, <i>Jane</i>, <i>Frederick</i>)"),
            ("NP2", "plural proper noun (e.g. <i>Browns</i>, <i>Reagans</i>, <i>Koreas</i>)"),
            ("NPD1", "singular weekday noun (e.g. <i>Sunday</i>)"),
            ("NPD2", "plural weekday noun (e.g. <i>Sundays</i>)"),
            ("NPM1", "singular month noun (e.g. <i>October</i>)"),
            ("NPM2", "plural month noun (e.g. <i>Octobers</i>)"),
            ("PN", "indefinite pronoun, neutral for number (<i>none</i>)"),
            ("PN1", "indefinite pronoun, singular (e.g. <i>anyone</i>, <i>everything</i>, <i>nobody</i>, <i>one</i>)"),
            ("PNQO", "objective wh-pronoun (<i>whom</i>)"),
            ("PNQS", "subjective wh-pronoun (<i>who</i>)"),
            ("PNQV", "wh-ever pronoun (<i>whoever</i>)"),
            ("PNX1", "reflexive indefinite pronoun (<i>oneself</i>)"),
            ("PPGE", "nominal possessive personal pronoun (e.g. <i>mine</i>, <i>yours</i>)"),
            ("PPH1", "3rd person sing. neuter personal pronoun (<i>it</i>)"),
            ("PPHO1", "3rd person sing. objective personal pronoun (<i>him</i>, <i>her</i>)"),
            ("PPHO2", "3rd person plural objective personal pronoun (<i>them</i>)"),
            ("PPHS1", "3rd person sing. subjective personal pronoun (<i>he</i>, <i>she</i>)"),
            ("PPHS2", "3rd person plural subjective personal pronoun (<i>they</i>)"),
            ("PPIO1", "1st person sing. objective personal pronoun (<i>me</i>)"),
            ("PPIO2", "1st person plural objective personal pronoun (<i>us</i>)"),
            ("PPIS1", "1st person sing. subjective personal pronoun (<i>I</i>)"),
            ("PPIS2", "1st person plural subjective personal pronoun (<i>we</i>)"),
            ("PPX1", "singular reflexive personal pronoun (e.g. <i>yourself</i>, <i>itself</i>)"),
            ("PPX2", "plural reflexive personal pronoun (e.g. <i>yourselves</i>, <i>themselves</i>)"),
            ("PPY", "2nd person personal pronoun (<i>you</i>)"),
            ("RA", "adverb, after nominal head (e.g. <i>else</i>, <i>galore</i>)"),
            ("REX", "adverb introducing appositional constructions (<i>namely</i>, <i>e</i>.g.</i>)"),
            ("RG", "degree adverb (<i>very</i>, <i>so</i>, <i>too</i>)"),
            ("RGQ", "<i>wh-</i></i> degree adverb (<i>how</i>)"),
            ("RGQV", "<i>wh-ever</i></i> degree adverb (<i>however</i>)"),
            ("RGR", "comparative degree adverb (<i>more</i>, <i>less</i>)"),
            ("RGT", "superlative degree adverb (<i>most</i>, <i>least</i>)"),
            ("RL", "locative adverb (e.g. <i>alongside</i>, <i>forward</i>)"),
            ("RP", "prep. adverb, particle (e.g <i>about</i>, <i>in</i>)"),
            ("RPK", "prep. adv., catenative (<i>about</i> in <i>be about to</i>)"),
            ("RR", "general adverb"),
            ("RRQ", "<i>wh-</i> general adverb (<i>where</i>, <i>when</i>, <i>why</i>, <i>how</i>)"),
            ("RRQV", "<i>wh-ever</i> general adverb (<i>wherever</i>, <i>whenever</i>)"),
            ("RRR", "comparative general adverb (e.g. <i>better</i>, <i>longer</i>)"),
            ("RRT", "superlative general adverb (e.g. <i>best</i>, <i>longest</i>)"),
            ("RT", "quasi-nominal adverb of time (e.g. <i>now</i>, <i>tomorrow</i>)"),
            ("TO", "infinitive marker (<i>to</i>)"),
            ("UH", "interjection (e.g. <i>oh</i>, <i>yes</i>, <i>um</i>)"),
            ("VB0", "<i>be</i>, base form (finite i.e. imperative, subjunctive)"),
            ("VBDR", "<i>were</i>"),
            ("VBDZ", "<i>was</i>"),
            ("VBG", "<i>being</i>"),
            ("VBI", "be<i></i>, infinitive (<i>To be or not...</>, <i>It will be ...</i>)"),
            ("VBM", "<i>am</i>"),
            ("VBN", "<i>been</i>"),
            ("VBR", "<i>are</i>"),
            ("VBZ", "<i>is</i>"),
            ("VD0", "<i>do</i>, base form (finite)"),
            ("VDD", "<i>did</i>"),
            ("VDG", "<i>doing</i>"),
            ("VDI", "<i>do</i>, infinitive (<i>I may do...</i>, <i>To do...</i>)"),
            ("VDN", "<i>done</i>"),
            ("VDZ", "<i>does</i>"),
            ("VH0", "<i>have</i>, base form (finite)"),
            ("VHD", "<i>had</i> (past tense)"),
            ("VHG", "<i>having</i>"),
            ("VHI", "<i>have</i>, infinitive"),
            ("VHN", "<i>had</i> (past participle)"),
            ("VHZ", "<i>has</i>"),
            ("VM", "modal auxiliary (<i>can</i>, <i>will</i>, <i>would</i>, etc.)"),
            ("VMK", "modal catenative (<i>ought</i>, <i>used</i>)"),
            ("VV0", "base form of lexical verb (e.g. <i>give</i>, <i>work</i>)"),
            ("VVD", "past tense of lexical verb (e.g. <i>gave</i>, <i>worked</i>)"),
            ("VVG", "<i>-ing</i> participle of lexical verb (e.g. <i>giving</i>, <i>working</i>)"),
            ("VVGK", "<i>-ing</i> participle catenative (<i>going</i><i></i> in <i>be going to</i>)"),
            ("VVI", "infinitive (e.g. <i>to give...</i>, <i>It will work...</i>)"),
            ("VVN", "past participle of lexical verb (e.g. <i>given</i>, <i>worked</i>)"),
            ("VVNK", "past participle catenative (e.g. <i>bound</i> in <i>be</i> bound to</i>)"),
            ("VVZ", "<i>-s</i> form of lexical verb (e.g. <i>gives</i>, <i>works</i>)"),
            ("XX", "<i>not</i>, <i>n't</i>"),
            ("ZZ1", "singular letter of the alphabet (e.g. <i>A</i>, <i>b</i>)"),
            ("ZZ2", "plural letter of the alphabet (e.g. <i>A's</i>, <i>b's</i>)")],
        }


class PosHelperDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(PosHelperDialog, self).__init__(parent)
        self.ui = Ui_PosHelperDialog()
        self.ui.setupUi(self)

        self._available_sets = list(sorted(tagsets.keys()))
        self.ui.combo_tagset.addItems(self._available_sets)
        self.ui.combo_tagset.currentIndexChanged.connect(self.change_tagset)
        self.ui.button_insert.clicked.connect(self.insert_content)
        self.ui.table_mappings.cellClicked.connect(self.toggle_pos)
        self.ui.table_mappings.cellPressed.connect(self.toggle_press_pos)
        self.ui.edit_search.textChanged.connect(self.search)
        self.ui.edit_search.returnPressed.connect(self.search_next)

        current = int(options.settings.value("poshelper_tagset", 0))
        self.ui.combo_tagset.setCurrentIndex(current)
        self.change_tagset(current)
        self.ui.edit_search.setFocus(True)

    def change_tagset(self, number):
        self._selected_pos = set()
        self.ui.table_mappings.setRowCount(0)
        self._tagset = tagsets[self._available_sets[number]]
        self.ui.table_mappings.setRowCount(len(self._tagset))
        self._check_boxes = []
        for row, (tag, desc) in enumerate(self._tagset):
            tag_item = QtWidgets.QTableWidgetItem(tag)
            tag_item.setCheckState(QtCore.Qt.Unchecked)
            desc_item = QtWidgets.QTableWidgetItem()
            desc_widget = QtWidgets.QLabel(desc,
                                           parent=self.ui.table_mappings)
            self.ui.table_mappings.setItem(row, 0, tag_item)
            self.ui.table_mappings.setItem(row, 1, desc_item)
            self.ui.table_mappings.setCellWidget(row, 1, desc_widget)
        self.ui.table_mappings.resizeColumnsToContents()
        self.ui.table_mappings.horizontalHeader().setStretchLastSection(True)
        self.ui.table_mappings.resizeRowsToContents()
        self.set_edit()

    def set_edit(self):
        selected = [x for x in sorted(self._selected_pos)]
        if selected:
            s = "*.[{}]".format("|".join(selected))
        else:
            s = ""
        self.ui.button_insert.setEnabled(bool(s))
        self.ui.edit_pos.setText(s)

    def toggle_press_pos(self, row, column):
        if column == 1:
            self.toggle_pos(row, column)

    def toggle_pos(self, row, column):
        self.select_row(row)

        tag = self._tagset[row][0]
        tag_item = self.ui.table_mappings.item(row, 0)
        if tag in self._selected_pos:
            self._selected_pos.remove(tag)
            tag_item.setCheckState(QtCore.Qt.Unchecked)
        else:
            self._selected_pos.add(tag)
            tag_item.setCheckState(QtCore.Qt.Checked)
        self.set_edit()

    def select_row(self, row):
        self.ui.table_mappings.clearSelection()
        tag_item = self.ui.table_mappings.item(row, 0)
        desc_item = self.ui.table_mappings.item(row, 1)
        tag_item.setSelected(True)
        desc_item.setSelected(True)

    def insert_content(self):
        s = utf8(self.ui.edit_pos.text())
        if s:
            widget = get_toplevel_window().ui.edit_query_string
            widget.textCursor().insertText(s)
            CoqWidgetFader(widget).fade()

    def current_tag(self):
        indices = self.ui.table_mappings.selectedIndexes()
        if not indices:
            return None
        else:
            return indices[0].row()

    def search_next(self):
        text = utf8(self.ui.edit_search.text())
        self.search(text, find_next=True)

    def search(self, text, find_next=False):
        text = utf8(text.lower())
        if not text:
            return

        current_row = self.current_tag()
        if current_row is None:
            pos = 0
        else:
            if find_next:
                pos = current_row + 1
            else:
                pos = current_row

        mappings = self._tagset[pos:] + self._tagset[:pos]
        for i, (tag, desc) in enumerate(mappings):
            row = i + pos
            if row > len(mappings):
                row = i + pos - len(mappings)
            if text in tag.lower() or text in desc.lower():
                self.select_row(row)
                self.ui.table_mappings.scrollToItem(
                    self.ui.table_mappings.item(row, 0))
                self.ui.edit_search.setStyleSheet("")
                return
        self.ui.edit_search.setStyleSheet(STYLE_WARN)

    def reject(self):
        options.settings.setValue("poshelper_tagset",
                                  self.ui.combo_tagset.currentIndex())
        return super(PosHelperDialog, self).reject()

    def closeEvent(self, event):
        options.settings.setValue("poshelper_tagset",
                                  self.ui.combo_tagset.currentIndex())

    @staticmethod
    def show(parent=None):
        dialog = PosHelperDialog(parent=parent)
        dialog.setVisible(True)
        return dialog.exec_()

# -*- coding: utf-8 -*-
"""
poshelper.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window
from .ui.posHelperDialogUi import Ui_PosHelperDialog
from .classes import CoqWidgetFader

from coquery.unicode import utf8
from coquery import options

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
            ("AJ0", "adjective (unmarked) (e.g. GOOD, OLD)"),
            ("AJC", "comparative adjective (e.g. BETTER, OLDER)"),
            ("AJS", "superlative adjective (e.g. BEST, OLDEST)"),
            ("AT0", "article (e.g. THE, A, AN)"),
            ("AV0", "adverb (unmarked) (e.g. OFTEN, WELL, LONGER, FURTHEST)"),
            ("AVP", "adverb particle (e.g. UP, OFF, OUT)"),
            ("AVQ", "wh-adverb (e.g. WHEN, HOW, WHY)"),
            ("CJC", "coordinating conjunction (e.g. AND, OR)"),
            ("CJS", "subordinating conjunction (e.g. ALTHOUGH, WHEN)"),
            ("CJT", "the conjunction THAT"),
            ("CRD", "cardinal numeral (e.g. 3, FIFTY-FIVE, 6609) (excl ONE)"),
            ("DPS", "possessive determiner form (e.g. YOUR, THEIR)"),
            ("DT0", "general determiner (e.g. THESE, SOME)"),
            ("DTQ", "wh-determiner (e.g. WHOSE, WHICH)"),
            ("EX0", "existential THERE"),
            ("ITJ", "interjection or other isolate (e.g. OH, YES, MHM)"),
            ("NN0", "noun (neutral for number) (e.g. AIRCRAFT, DATA)"),
            ("NN1", "singular noun (e.g. PENCIL, GOOSE)"),
            ("NN2", "plural noun (e.g. PENCILS, GEESE)"),
            ("NP0", "proper noun (e.g. LONDON, MICHAEL, MARS)"),
            ("ORD", "ordinal (e.g. SIXTH, 77TH, LAST)"),
            ("PNI", "indefinite pronoun (e.g. NONE, EVERYTHING)"),
            ("PNP", "personal pronoun (e.g. YOU, THEM, OURS)"),
            ("PNQ", "wh-pronoun (e.g. WHO, WHOEVER)"),
            ("PNX", "reflexive pronoun (e.g. ITSELF, OURSELVES)"),
            ("POS", "the possessive (or genitive morpheme) 'S or '"),
            ("PRF", "the preposition OF"),
            ("PRP", "preposition (except for OF) (e.g. FOR, ABOVE, TO)"),
            ("PUL", "punctuation - left bracket (i.e. ( or [ )"),
            ("PUN", "punctuation - general mark (i.e. . ! , : ; - ? ... )"),
            ("PUQ", "punctuation - quotation mark (i.e. ` ' \" )"),
            ("PUR", "punctuation - right bracket (i.e. ) or ] )"),
            ("TO0", "infinitive marker TO"),
            ("UNC", "'unclassified' items which are not words of the English lexicon"),
            ("VBB", "the 'base forms' of the verb 'BE' (except the infinitive), i.e. AM, ARE"),
            ("VBD", "past form of the verb 'BE', i.e. WAS, WERE"),
            ("VBG", "-ing form of the verb 'BE', i.e. BEING"),
            ("VBI", "infinitive of the verb 'BE'"),
            ("VBN", "past participle of the verb 'BE', i.e. BEEN"),
            ("VBZ", "-s form of the verb 'BE', i.e. IS, 'S"),
            ("VDB", "base form of the verb 'DO' (except the infinitive), i.e."),
            ("VDD", "past form of the verb 'DO', i.e. DID"),
            ("VDG", "-ing form of the verb 'DO', i.e. DOING"),
            ("VDI", "infinitive of the verb 'DO'"),
            ("VDN", "past participle of the verb 'DO', i.e. DONE"),
            ("VDZ", "-s form of the verb 'DO', i.e. DOES"),
            ("VHB", "base form of the verb 'HAVE' (except the infinitive), i.e. HAVE"),
            ("VHD", "past tense form of the verb 'HAVE', i.e. HAD, 'D"),
            ("VHG", "-ing form of the verb 'HAVE', i.e. HAVING"),
            ("VHI", "infinitive of the verb 'HAVE'"),
            ("VHN", "past participle of the verb 'HAVE', i.e. HAD"),
            ("VHZ", "-s form of the verb 'HAVE', i.e. HAS, 'S"),
            ("VM0", "modal auxiliary verb (e.g. CAN, COULD, WILL, 'LL)"),
            ("VVB", "base form of lexical verb (except the infinitive)(e.g. TAKE, LIVE)"),
            ("VVD", "past tense form of lexical verb (e.g. TOOK, LIVED)"),
            ("VVG", "-ing form of lexical verb (e.g. TAKING, LIVING)"),
            ("VVI", "infinitive of lexical verb"),
            ("VVN", "past participle form of lex. verb (e.g. TAKEN, LIVED)"),
            ("VVZ", "-s form of lexical verb (e.g. TAKES, LIVES)"),
            ("XX0", "the negative NOT or N'T"),
            ("ZZ0", "alphabetical symbol (e.g. A, B, c, d)")],
        "CLAWS7": [
            ("APPGE", "possessive pronoun, pre-nominal (e.g. my, your, our)"),
            ("AT", "article (e.g. the, no)"),
            ("AT1", "singular article (e.g. a, an, every)"),
            ("BCL", "before-clause marker (e.g. in order (that),in order (to))"),
            ("CC", "coordinating conjunction (e.g. and, or)"),
            ("CCB", "adversative coordinating conjunction ( but)"),
            ("CS", "subordinating conjunction (e.g. if, because, unless, so, for)"),
            ("CSA", "as (as conjunction)"),
            ("CSN", "than (as conjunction)"),
            ("CST", "that (as conjunction)"),
            ("CSW", "whether (as conjunction)"),
            ("DA", "after-determiner or post-determiner capable of pronominal function (e.g. such, former, same)"),
            ("DA1", "singular after-determiner (e.g. little, much)"),
            ("DA2", "plural after-determiner (e.g. few, several, many)"),
            ("DAR", "comparative after-determiner (e.g. more, less, fewer)"),
            ("DAT", "superlative after-determiner (e.g. most, least, fewest)"),
            ("DB", "before determiner or pre-determiner capable of pronominal function (all, half)"),
            ("DB2", "plural before-determiner ( both)"),
            ("DD", "determiner (capable of pronominal function) (e.g any, some)"),
            ("DD1", "singular determiner (e.g. this, that, another)"),
            ("DD2", "plural determiner ( these,those)"),
            ("DDQ", "wh-determiner (which, what)"),
            ("DDQGE", "wh-determiner, genitive (whose)"),
            ("DDQV", "wh-ever determiner, (whichever, whatever)"),
            ("EX", "existential there"),
            ("FO", "formula"),
            ("FU", "unclassified word"),
            ("FW", "foreign word"),
            ("GE", "germanic genitive marker - (' or's)"),
            ("IF", "for (as preposition)"),
            ("II", "general preposition"),
            ("IO", "of (as preposition)"),
            ("IW", "with, without (as prepositions)"),
            ("JJ", "general adjective"),
            ("JJR", "general comparative adjective (e.g. older, better, stronger)"),
            ("JJT", "general superlative adjective (e.g. oldest, best, strongest)"),
            ("JK", "catenative adjective (able in be able to, willing in be willing to)"),
            ("MC", "cardinal number,neutral for number (two, three..)"),
            ("MC1", "singular cardinal number (one)"),
            ("MC2", "plural cardinal number (e.g. sixes, sevens)"),
            ("MCGE", "genitive cardinal number, neutral for number (two's, 100's)"),
            ("MCMC", "hyphenated number (40-50, 1770-1827)"),
            ("MD", "ordinal number (e.g. first, second, next, last)"),
            ("MF", "fraction,neutral for number (e.g. quarters, two-thirds)"),
            ("ND1", "singular noun of direction (e.g. north, southeast)"),
            ("NN", "common noun, neutral for number (e.g. sheep, cod, headquarters)"),
            ("NN1", "singular common noun (e.g. book, girl)"),
            ("NN2", "plural common noun (e.g. books, girls)"),
            ("NNA", "following noun of title (e.g. M.A.)"),
            ("NNB", "preceding noun of title (e.g. Mr., Prof.)"),
            ("NNL1", "singular locative noun (e.g. Island, Street)"),
            ("NNL2", "plural locative noun (e.g. Islands, Streets)"),
            ("NNO", "numeral noun, neutral for number (e.g. dozen, hundred)"),
            ("NNO2", "numeral noun, plural (e.g. hundreds, thousands)"),
            ("NNT1", "temporal noun, singular (e.g. day, week, year)"),
            ("NNT2", "temporal noun, plural (e.g. days, weeks, years)"),
            ("NNU", "unit of measurement, neutral for number (e.g. in, cc)"),
            ("NNU1", "singular unit of measurement (e.g. inch, centimetre)"),
            ("NNU2", "plural unit of measurement (e.g. ins., feet)"),
            ("NP", "proper noun, neutral for number (e.g. IBM, Andes)"),
            ("NP1", "singular proper noun (e.g. London, Jane, Frederick)"),
            ("NP2", "plural proper noun (e.g. Browns, Reagans, Koreas)"),
            ("NPD1", "singular weekday noun (e.g. Sunday)"),
            ("NPD2", "plural weekday noun (e.g. Sundays)"),
            ("NPM1", "singular month noun (e.g. October)"),
            ("NPM2", "plural month noun (e.g. Octobers)"),
            ("PN", "indefinite pronoun, neutral for number (none)"),
            ("PN1", "indefinite pronoun, singular (e.g. anyone, everything, nobody, one)"),
            ("PNQO", "objective wh-pronoun (whom)"),
            ("PNQS", "subjective wh-pronoun (who)"),
            ("PNQV", "wh-ever pronoun (whoever)"),
            ("PNX1", "reflexive indefinite pronoun (oneself)"),
            ("PPGE", "nominal possessive personal pronoun (e.g. mine, yours)"),
            ("PPH1", "3rd person sing. neuter personal pronoun (it)"),
            ("PPHO1", "3rd person sing. objective personal pronoun (him, her)"),
            ("PPHO2", "3rd person plural objective personal pronoun (them)"),
            ("PPHS1", "3rd person sing. subjective personal pronoun (he, she)"),
            ("PPHS2", "3rd person plural subjective personal pronoun (they)"),
            ("PPIO1", "1st person sing. objective personal pronoun (me)"),
            ("PPIO2", "1st person plural objective personal pronoun (us)"),
            ("PPIS1", "1st person sing. subjective personal pronoun (I)"),
            ("PPIS2", "1st person plural subjective personal pronoun (we)"),
            ("PPX1", "singular reflexive personal pronoun (e.g. yourself, itself)"),
            ("PPX2", "plural reflexive personal pronoun (e.g. yourselves, themselves)"),
            ("PPY", "2nd person personal pronoun (you)"),
            ("RA", "adverb, after nominal head (e.g. else, galore)"),
            ("REX", "adverb introducing appositional constructions (namely, e.g.)"),
            ("RG", "degree adverb (very, so, too)"),
            ("RGQ", "wh- degree adverb (how)"),
            ("RGQV", "wh-ever degree adverb (however)"),
            ("RGR", "comparative degree adverb (more, less)"),
            ("RGT", "superlative degree adverb (most, least)"),
            ("RL", "locative adverb (e.g. alongside, forward)"),
            ("RP", "prep. adverb, particle (e.g about, in)"),
            ("RPK", "prep. adv., catenative (about in be about to)"),
            ("RR", "general adverb"),
            ("RRQ", "wh- general adverb (where, when, why, how)"),
            ("RRQV", "wh-ever general adverb (wherever, whenever)"),
            ("RRR", "comparative general adverb (e.g. better, longer)"),
            ("RRT", "superlative general adverb (e.g. best, longest)"),
            ("RT", "quasi-nominal adverb of time (e.g. now, tomorrow)"),
            ("TO", "infinitive marker (to)"),
            ("UH", "interjection (e.g. oh, yes, um)"),
            ("VB0", "be, base form (finite i.e. imperative, subjunctive)"),
            ("VBDR", "were"),
            ("VBDZ", "was"),
            ("VBG", "being"),
            ("VBI", "be, infinitive (To be or not... It will be ..)"),
            ("VBM", "am"),
            ("VBN", "been"),
            ("VBR", "are"),
            ("VBZ", "is"),
            ("VD0", "do, base form (finite)"),
            ("VDD", "did"),
            ("VDG", "doing"),
            ("VDI", "do, infinitive (I may do... To do...)"),
            ("VDN", "done"),
            ("VDZ", "does"),
            ("VH0", "have, base form (finite)"),
            ("VHD", "had (past tense)"),
            ("VHG", "having"),
            ("VHI", "have, infinitive"),
            ("VHN", "had (past participle)"),
            ("VHZ", "has"),
            ("VM", "modal auxiliary (can, will, would, etc.)"),
            ("VMK", "modal catenative (ought, used)"),
            ("VV0", "base form of lexical verb (e.g. give, work)"),
            ("VVD", "past tense of lexical verb (e.g. gave, worked)"),
            ("VVG", "-ing participle of lexical verb (e.g. giving, working)"),
            ("VVGK", "-ing participle catenative (going in be going to)"),
            ("VVI", "infinitive (e.g. to give... It will work...)"),
            ("VVN", "past participle of lexical verb (e.g. given, worked)"),
            ("VVNK", "past participle catenative (e.g. bound in be bound to)"),
            ("VVZ", "-s form of lexical verb (e.g. gives, works)"),
            ("XX", "not, n't"),
            ("ZZ1", "singular letter of the alphabet (e.g. A,b)"),
            ("ZZ2", "plural letter of the alphabet (e.g. A's, b's)")],
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
        self.ui.table_mappings.cellPressed.connect(lambda: print("pressed"))

        current = int(options.settings.value("poshelper_tagset", 0))
        self.ui.combo_tagset.setCurrentIndex(current)
        self.change_tagset(current)

    def change_tagset(self, number):
        self._selected_pos = set()
        self.ui.table_mappings.setRowCount(0)
        self._tagset = tagsets[self._available_sets[number]]
        self.ui.table_mappings.setRowCount(len(self._tagset))
        self._check_boxes = []
        for row, (tag, desc) in enumerate(self._tagset):
            tag_item = QtWidgets.QTableWidgetItem(tag)
            tag_item.setCheckState(QtCore.Qt.Unchecked)
            desc_item = QtWidgets.QTableWidgetItem(desc)
            self.ui.table_mappings.setItem(row, 0, tag_item)
            self.ui.table_mappings.setItem(row, 1, desc_item)
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

    def toggle_pos(self, row, column):
        self.ui.table_mappings.clearSelection()
        tag_item = self.ui.table_mappings.item(row, 0)
        desc_item = self.ui.table_mappings.item(row, 1)
        tag_item.setSelected(True)
        desc_item.setSelected(True)

        tag = self._tagset[row][0]
        if tag in self._selected_pos:
            self._selected_pos.remove(tag)
            tag_item.setCheckState(QtCore.Qt.Unchecked)
        else:
            self._selected_pos.add(tag)
            tag_item.setCheckState(QtCore.Qt.Checked)
        self.set_edit()

    def insert_content(self):
        s = utf8(self.ui.edit_pos.text())
        if s:
            widget = get_toplevel_window().ui.edit_query_string
            widget.textCursor().insertText(s)
            CoqWidgetFader(widget).fade()
            try:
                print(widget.palette())
            except AttributeError:
                pass

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

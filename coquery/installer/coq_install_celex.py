# -*- coding: utf-8 -*-

"""
coq_install_celex.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import unicodedata
import os

from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.tables import (Column, Link, Identifier,
                            enum, varchar, mediumint, smallint)
from coquery.defines import (
    QUERY_ITEM_POS, QUERY_ITEM_TRANSCRIPT, QUERY_ITEM_WORD, VIEW_MODE_TABLES)
from coquery.gui.pyqt_compat import tr


def dia_to_unicode(s):
    """
    Translates a string that contains CELEX encodings of diacritics to a
    Unicode string.

    Parameters
    ----------
    s : string
        A string containing CELEX diacritics (see CELEX/english/eol/README
        for details)

    Returns
    -------
    s : string
        The corresponding unicode string
    """

    encoded_diacritics = {
        "#": "COMBINING ACUTE ACCENT",
        "`": "COMBINING GRAVE ACCENT",
        '"': "COMBINING DIAERESIS",
        "^": "COMBINING CIRCUMFLEX ACCENT",
        ",": "COMBINING CEDILLA",
        "~": "COMBINING TILDE",
        "@": "COMBINING RING ABOVE"}

    diacritic = None
    char_list = []
    for ch in s:
        if ch in encoded_diacritics:
            diacritic = unicodedata.lookup(encoded_diacritics[ch])
        else:
            char_list.append(ch)
            # add diacritics:
            if diacritic:
                char_list.append(diacritic)
                diacritic = None
    # join and normalize characters:
    unicode_string = unicodedata.normalize("NFC", "".join(char_list))
    return unicode_string


def _tr(s):
    return tr(__name__, s, None)


class CELEXBuilderClass(BaseCorpusBuilder):
    lexicon_root_table = "corpus"

    def __init__(self, gui, *args):
        super(CELEXBuilderClass, self).__init__(gui, *args)
        self.set_fnc_map()
        self.map_query_items()

    def build_load_files(self):
        file_list = sorted(self.get_file_list(self.arguments.path,
                                              self.file_filter))
        files = [x for x in file_list
                 if os.path.basename(x).lower() in self.expected_files]

        self._widget.progressSet.emit(len(files), "")
        self._widget.progressUpdate.emit(0)

        print(file_list)
        print(files)

        for i, file_name in enumerate(files):
            component = file_name.lower()[-6:-3]
            s = self.component_to_label(component)
            self._widget.progressUpdate.emit(i)
            print(component)

            if s:
                label = _tr("Loading from {}.cd: {}").format(component, s)
                self._widget.labelSet.emit(label)

                _process_fnc = self._FNC_MAP[component]

                with open(file_name, "r") as input_file:
                    for current_line in input_file.readlines():
                        if self.interrupted:
                            return
                        _process_fnc(current_line.strip().split("\\"))
                self.commit_data()

    @staticmethod
    def get_url():
        return 'https://catalog.ldc.upenn.edu/LDC96L14'

    @staticmethod
    def get_references():
        return [
            "Baayen, R., R. Piepenbrock, and L. Gulikers. 1995. "
            "<i>CELEX2 LDC96L14</i>. Web Download. "
            "Philadelphia: Linguistic Data Consortium."]

    @staticmethod
    def get_license():
        return (
            "The CELEX Lexical Database is available under the terms of the "
            "<a href='https://catalog.ldc.upenn.edu/license/celex-user-"
            "agreement.pdf'>CELEX 2 User Agreement</a>.")


class BuilderClass(CELEXBuilderClass):
    default_view_mode = VIEW_MODE_TABLES
    file_filter = "e??.cd"

    _ORTH_WORDS = "eow"
    _ORTH_LEMMAS = "eol"
    _PHONO_WORDS = "epw"
    _PHONO_LEMMAS = "epl"
    _MORPH_WORDS = "emw"
    _MORPH_LEMMAS = "eml"
    _SYNTAX_LEMMAS = "esl"

    _POS_LIST = ["N", "A", "NUM", "V", "ART", "PRON", "ADV", "PREP", "C", "I",
                 "SCON", "CCON", "LET", "ABB", "TO"]

    _POS_MAP = {str(k+1): v for k, v in dict(enumerate(_POS_LIST)).items()}

    lemma_table = "Ortho_Lemmas"
    lemma_id = "LemmaId"
    lemma_label = "Head"
    lemma_headdia = "HeadDia"
    lemma_cob = "Lemma_Cob"
    lemma_orthocnt = "Lemma_OrthoCnt"
    lemma_orthostatus = "Lemma_OrthoStatus"
    lemma_cobspelldev = "Lemma_CobSpellDev"
    lemma_headsyldia = "Lemma_HeadSylDia"
    lemma_columns = [
        Identifier(lemma_id, smallint(5), unique=False),
        Column(lemma_label, varchar(34)),
        Column(lemma_headdia, varchar(34)),
        Column(lemma_cob, mediumint(7)),
        Column(lemma_orthocnt, enum("1", "2", "3", "4", "5")),
        Column(lemma_orthostatus, enum("B", "A"),),
        Column(lemma_cobspelldev, mediumint(5)),
        Column(lemma_headsyldia, varchar(42))]

    phonoword_table = "Phono_Words"
    phonoword_id = "PhonoWordId"
    phonoword_word = "Word"
    phonoword_phonstrsdisc = "Word_PhonStrsDISC"
    phonoword_proncnt = "Word_PronCnt"
    phonoword_phoncvbr = "Word_PhonCVBr"
    phonoword_phonsylbclx = "Word_PhonSylBCLX"
    phonoword_columns = [
        Identifier(phonoword_id, mediumint(6)),
        Column(phonoword_phonstrsdisc, varchar(41)),
        Column(phonoword_word, varchar(35)),
        Column(phonoword_proncnt, enum(
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
            "13", "14", "15", "16", "18", "20", "21", "24", "25", "28", "30",
            "32", "36", "40", "48", "60")),
        Column(phonoword_phoncvbr, varchar(53)),
        Column(phonoword_phonsylbclx, varchar(53))]

    phonolemma_table = "Phono_Lemmas"
    phonolemma_id = "PhonoLemmaId"
    phonolemma_head = "Head"
    phonolemma_proncnt = "Lemma_PronCnt"
    phonolemma_phonstrsdisc = "Lemma_PhonStrsDISC"
    phonolemma_phoncvbr = "Lemma_PhonCVBr"
    phonolemma_phonsylbclx = "Lemma_PhonSylBCLX"
    phonolemma_columns = [
        Identifier(phonolemma_id, smallint(5)),
        Column(phonolemma_head, varchar(34)),
        Column(phonolemma_proncnt, enum(
            "1", "10", "11", "12", "13", "14", "15", "16", "18", "2", "20",
            "21", "24", "25", "3", "30", "32", "36", "4", "40", "48", "5", "6",
            "60", "7", "8", "9")),
        Column(phonolemma_phonstrsdisc, varchar(40), ),
        Column(phonolemma_phoncvbr, varchar(53)),
        Column(phonolemma_phonsylbclx, varchar(53))]

    morphword_table = "Morpho_Words"
    morphword_id = "MorphWordId"
    morphword_word = "Word"
    morphword_flecttype = "Word_FlectType"
    morphword_transinfl = "Word_TransInfl"
    morphword_columns = [
        Identifier(morphword_id, mediumint(6)),
        Column(morphword_word, varchar(35)),
        Column(morphword_flecttype, enum(
            "a1S", "a1Sr", "a2S", "a2Sr", "a3S", "a3Sr", "aP", "aPr", "b", "c",
            "e1S", "e2S", "e2Sr", "e3S", "e3Sr", "eP", "i", "P", "pa", "par",
            "pe", "Pr", "S", "X")),
        Column(morphword_transinfl,
               "ENUM('','@','@ @','@ @ @','@ @ @ @','@ @ @ @ @','@ @ @ @ @+s','@ @ @ @-y+ies','@ @ @ @+es','@ @ @ @+s','@ @ @-y+ies','@ @ @+ed','@ @ @+es','@ @ @+ing','@ @ @+s','@ @-e+ing','@ @-f+ves','@ @-fe+ves','@ @-y+ied','@ @-y+ier','@ @-y+ies','@ @-y+iest','@ @+bed','@ @+bing','@ @+d','@ @+ed','@ @+es','@ @+ged','@ @+ging','@ @+ing','@ @+led','@ @+ling','@ @+ped','@ @+ping','@ @+red','@ @+ring','@ @+s','@ @+ted','@ @+ting','@-e+ing','@-e+ing @','@-e+ing @ @','@-ey+ier','@-ey+iest','@-f+ves','@-fe+ves','@-y+ied','@-y+ied @','@-y+ied @ @','@-y+ier','@-y+ier @','@-y+ies','@-y+ies @','@-y+ies @ @','@-y+ies @ @ @','@-y+iest','@-y+iest @','@+@d','@+@ing','@+@s','@+bed','@+bed @','@+bed @ @','@+ber','@+best','@+bing','@+bing @','@+bing @ @','@+d','@+d @','@+d @ @','@+ded','@+ded @','@+der','@+dest','@+ding','@+ding @','@+ed','@+ed @','@+ed @ @','@+ed @ @ @','@+er','@+er @','@+er @ @','@+es','@+es @','@+es @ @','@+es @ @ @','@+est','@+est @','@+ged','@+ged @','@+ged @ @','@+ger','@+gest','@+ging','@+ging @','@+ging @ @','@+ing','@+ing @','@+ing @ @','@+ing @ @ @','@+ked','@+ked @','@+king','@+king @','@+led','@+led @','@+ler','@+lest','@+ling','@+ling @','@+med','@+med @','@+mer','@+mest','@+ming','@+ming @','@+ned','@+ned @','@+ner','@+ner @','@+nest','@+nest @','@+ning','@+ning @','@+ning @ @','@+ped','@+ped @','@+ped @ @','@+ping','@+ping @','@+ping @ @','@+r','@+r @','@+red','@+red @','@+ring','@+ring @','@+s','@+s @','@+s @ @','@+s @ @ @','@+sed','@+sed @','@+ses','@+ses @','@+sing','@+sing @','@+st','@+st @','@+ted','@+ted @','@+ted @ @','@+ter','@+ter @','@+test','@+test @','@+ting','@+ting @','@+ting @ @','@+ved','@+ved @','@+ving','@+ving @','@+zed','@+zes','@+zing','IRR') NOT NULL")]

    morphlemma_table = "Morpho_Lemmas"
    morphlemma_id = "MorphLemmaId"
    morphlemma_head = "Head"
    morphlemma_morphstatus = "Lemma_MorphStatus"
    morphlemma_lang = "Lemma_Lang"
    morphlemma_morphcnt = "Lemma_MorphCnt"
    morphlemma_nvaffcomp = "Lemma_NVAffComp"
    morphlemma_der = "Lemma_Der"
    morphlemma_comp = "Lemma_Comp"
    morphlemma_dercomp = "Lemma_DerComp"
    morphlemma_def = "Lemma_Def"
    morphlemma_imm = "Lemma_Imm"
    morphlemma_immsubcat = "Lemma_ImmSubCat"
    morphlemma_immsa = "Lemma_ImmSA"
    morphlemma_immallo = "Lemma_ImmAllo"
    morphlemma_immsubst = "Lemma_ImmSubst"
    morphlemma_immopac = "Lemma_ImmOpac"
    morphlemma_transder = "Lemma_TransDer"
    morphlemma_imminfix = "Lemma_ImmInfix"
    morphlemma_immrevers = "Lemma_ImmRevers"
    morphlemma_flatsa = "Lemma_FlatSA"
    morphlemma_struclab = "Lemma_StrucLab"
    morphlemma_strucallo = "Lemma_StrucAllo"
    morphlemma_strucsubst = "Lemma_StrucSubst"
    morphlemma_strucopac = "Lemma_StrucOpac"
    morphlemma_columns = [
        Identifier(morphlemma_id, "SMALLINT(5) UNSIGNED NOT NULL"),
        Column(morphlemma_morphstatus,
               "ENUM('C','F','I','M','O','R','U','Z') NOT NULL"),
        Column(morphlemma_head, "VARCHAR(34) NOT NULL"),
        Column(morphlemma_lang,
               "ENUM('','A','B','D','F','G','I','L','S') NOT NULL"),
        Column(morphlemma_morphcnt,
               "ENUM('0','1','2','3','4','5','8') NOT NULL"),

        Column(morphlemma_nvaffcomp, enum("N", "Y")),
        Column(morphlemma_der, enum("N", "Y")),
        Column(morphlemma_comp, enum("N", "Y")),
        Column(morphlemma_dercomp, enum("N", "Y")),
        Column(morphlemma_def, enum("N", "Y")),
        Column(morphlemma_imm, "VARCHAR(27) NOT NULL"),
        Column(morphlemma_immsubcat,
               "ENUM('','?','?3','?N','?O','?x','0','0B','0N','0P','0x','1',"
               "'1?','11','12x','1A','1B','1I','1N','1Nx','1P','1x','1xx','2',"
               "'2?','22','23','2A','2B','2N','2Nx','2O','2P','2x','2x3x',"
               "'2xN','2xP','2xx','3','3?','31','32','32x','33','3A','3Ax',"
               "'3B','3Bx','3C','3N','3Nx','3O','3P','3x','3x3x','3xB','3xN',"
               "'3xx','A','A0','A1','A1x','A2','A2x','A3','A3x','AA','AB',"
               "'AI','AN','ANx','AP','AQ','Ax','AxAx','AxB','AxN','AxP','Axx',"
               "'B','B0','B1','B1x','B2','B2x','B3','B3x','BA','BB','BBx',"
               "'BC','BN','BNx','BP','BPx','Bx','C','C2','CB','CC','CP','D',"
               "'DN','DO','I','II','IN','Ix','N','N0','N0x','N1','N1x','N2',"
               "'N2x','N3','N3x','NA','NB','NBx','NN','NNx','NP','NQ','Nx',"
               "'Nx2','NxB','NxN','NxNx','NxP','Nxx','NxxN','O','O1','O3',"
               "'OA','OB','OC','ON','ONx','OO','OP','Ox','P','PB','PN','PO',"
               "'PP','PQx','Px','Q','Q?x','Q3x','QA','QN','QNx','QO','QQ',"
               "'Qx','x0','x1','x1N','x1x','x2','x2Bx','x2P','x2x','x3','x3P',"
               "'x3x','xA','xAN','xAP','xAx','xB','xN','xNN','xNx','xNxP',"
               "'xO','xP','xx','xx3','xxN','xxx') NOT NULL"),
        Column(morphlemma_immsa,
               "ENUM('','AA','AAA','AAF','AAS','AF','AFS','AS','ASA','ASAS',"
               "'ASS','ASSA','F','FA','FAFA','FAS','FF','FS','FSA','S','SA',"
               "'SAA','SAAS','SAS','SASA','SF','SFA','SS','SSA') NOT NULL"),
        Column(morphlemma_immallo,
               "ENUM('','B','C','D','F','N','Z') NOT NULL"),
        Column(morphlemma_immsubst, "ENUM('','N','Y') NOT NULL"),
        Column(morphlemma_immopac, "ENUM('','N','Y') NOT NULL"),
        Column(morphlemma_transder,
               "ENUM('','-a#','-a+er#','-a+o#','-a+t#','-able#','-about',"
               "'-about#','-aceti#','-acy#','-after','-against','-age#',"
               "'-age##','-ah#','-ail+al#','-aim+am#','-ain#','-ain+an#',"
               "'-ain+en#','-ain+ent#','-ain+ic#','-ain+in#','-ainto+in#',"
               "'-air+ar#','-air+er#','-al#','-al+e#','-al+ll#','-al+u#',"
               "'-along+long#','-ample+empl#','-an#','-anentwave',"
               "'-anniversary','-ant#','-ar#','-ar+er#','-ar+i#',"
               "'-ar+re#-ey+y','-aratoryschool+school','-ard+er#',"
               "'-are+re','-arithm','-ark+eark#','-ary#','-as#',"
               "'-ase+ss#','-ass+iss#','-ast+st#','-ast+sti#',"
               "'-asure+nsur#','-asy#','-at+d#','-at+t#','-ate#',"
               "'-ate#-star+ar','-ate##','-ateagainst#','-atein#',"
               "'-ation','-ation#','-ation+e','-atrol#-orpedoboat+boat',"
               "'-auxiliary','-away+way#','-ax#-carbon+on','-ay#','-b#',"
               "'-b+m#','-b+pt#','-bagpipes+pipes','-be+p#','-be+pt#',"
               "'-bebop+bop','-ber+er#','-bereft+reft','-beto+pt#',"
               "'-binations+s','-ble#','-ble+il#','-blue','-bockers+s',"
               "'-c#','-c+qu#','-cal#','-castic+ky','-cat','-cate#',"
               "'-ce+ci#','-ce+s#','-ce+se#','-ce+t#','-ce+ti#',"
               "'-chop#','-chute#','-ck+qu#','-cks+x#','-code',"
               "'-coleslaw+slaw','-colonelblimp+blimp','-consonant',"
               "'-cotton','-crat#','-crophone+ke','-ct+g#','-cy+ti#',"
               "'-cycle+ke','-d#','-d+s#','-d+t#','-day','-de+s#',"
               "'-de+ss#','-deep','-densation#','-detached',"
               "'-detective+tec','-deto+s#','-disease','-dish','-dive',"
               "'-dkerchief+k#','-dle#','-dle+l#','-dmother',"
               "'-dmother+n#','-dog#','-down#','-duction',"
               "'-dvancedlevel+level','-dyboy','-e#','-e#-e#','-e##',"
               "'-e+a#','-e+ac#','-e+an#','-e+ar#','-e+at#','-e+ct#',"
               "'-e+i#','-e+ic#','-e+ig#','-e+in#','-e+it#','-e+l#',"
               "'-e+m#','-e+n#','-e+o#','-e+ot#','-e+pt#','-e+s#',"
               "'-e+t#','-e+u#','-eabout+t#','-eace+ac#',"
               "'-eakfast#-lunch+unch','-eal+el#','-ear+ar#','-ear+ir#',"
               "'-ear+or#','-east+est#','-eat+et#',"
               "'-eaudecologne+cologne','-ece+c#','-ect+ic#','-ect+ig#',"
               "'-ed+d#','-ed+ss#','-edo','-edplatypus','-edy#',"
               "'-edy+i#','-ee','-ee#','-ee+a#','-eel+il#','-eer#',"
               "'-efrom#','-eian','-eian+b#','-ein#','-eive+ipi#',"
               "'-el+uls#','-eleison','-elsalvador+salvadore#',"
               "'-em+mpt#','-emathics','-ematics+s','-eme#',"
               "'-empire+imper#','-en+in#','-en+n#','-encefiction+fi',"
               "'-end#','-ening+ning','-ent#','-entitycard+card',"
               "'-eof#','-eon','-eon#','-eous#','-ep+p#','-er#',"
               "'-er+r#','-er+ri#','-erambulator+ram','-eration',"
               "'-eration+s','-erations+s','-erative','-eree','-erer#',"
               "'-erer+r#','-ergeant+arge','-ern','-ern#-venience',"
               "'-ernist','-eror+r#','-ers+s','-erto+r#','-ery#','-es#',"
               "'-es+a#','-escape+scape#','-essor','-et','-et+t#',"
               "'-etable','-etarian#','-ethering+ithering','-eto',"
               "'-eto#','-eum#','-eur#','-evatedrailway','-evision+l#',"
               "'-ew+a#','-ewith#','-ex#','-ey#','-ey+i#',"
               "'-eyeglasses+glasses','-f#','-f+ic#','-f+v#','-f+ve',"
               "'-f+ve#','-falcon','-fall+al','-fessional#-ateur',"
               "'-fibre','-fidencetrick','-footlights+lights','-for#',"
               "'-ford#-cambridge+bridge','-frenchfries+fries','-from#',"
               "'-g#','-ghfidelity+fi','-got','-graph','-gun','-gy#',"
               "'-h#','-h+n#','-had+d','-haddock','-handcuffs+cuffs',"
               "'-hant+ant#','-has+s','-have+ai#-ot+t','-have+ve',"
               "'-house','-hronization','-i#','-i#-stellar+ar','-ia#',"
               "'-ian#','-ian+o#','-ic#','-ic##','-ic+er#','-ic+o#',"
               "'-ican#','-ice+et#','-iceberg+berg','-id#',"
               "'-idatedannuities+s','-ie#','-ief+ev#','-ier#','-ies+y',"
               "'-ign+gn#','-ik#','-il+vy#','-ill+o#-ot+t','-im+m#',"
               "'-imate','-imensional','-in#','-in+n#','-in+ni#',"
               "'-in+nn#','-ination','-incense+cense','-ind+ound#',"
               "'-ine#','-ine+ens#','-inese+e','-influenza+flu',"
               "'-ing+n#-to+na','-ingroom#','-ink+unk#','-intosh',"
               "'-io#','-ion#','-ion+or#','-ion+u#','-ior#','-ious#',"
               "'-ir+red#','-ir+ri#','-is#','-is+s','-is+t#','-isement',"
               "'-ish#','-ism#','-istan#','-it+t#','-ite#','-itory',"
               "'-itous#','-itulate','-ity#','-ity+ar#','-ium#',"
               "'-ivarius','-ive#','-ive+p#','-ive+pt#','-iwog#',"
               "'-ix+ec#','-ize#','-k#','-k+c#','-k+ch#','-k+quer#',"
               "'-k+t#','-ke#-fog+g','-ke+c#','-ke+ch#','-ke+ck#',"
               "'-keeper#','-l#','-l#-l','-l#-monologue+logue','-l+t#',"
               "'-le#','-le+ell#-e#','-le+il#','-le+ol#','-le+ul#',"
               "'-leadingreins+reins','-lemen#','-ll#-ot+t','-lunch',"
               "'-m+i#-ot+t','-m+t#','-ma#','-magazine','-maker#',"
               "'-maniac','-matography','-meter','-mime','-monger',"
               "'-motor','-mum','-n#','-n#-corundum+rundum','-nasium',"
               "'-nation#-inflation+flation','-nent#','-ner',"
               "'-nstration','-o#','-o##','-oad+ead#','-oanalyse#',"
               "'-ock#','-of','-of#','-of+d#','-off','-off#','-og',"
               "'-ography','-oia#','-oid#','-oil','-oin+unct#',"
               "'-oisleather+m#','-oitre+aiss#','-ol+l#','-olate',"
               "'-olate#','-old+eld##','-omrade+amarad#','-on','-on#',"
               "'-on+ti#','-onamide+a','-onate','-ong+eng#','-onia#',"
               "'-ooth+eethe','-ope+ap#','-ophrenia#','-or#',"
               "'-or#-hotel+el','-or+r#','-orary','-oratory',"
               "'-ortable#','-orus#','-ory#','-os#','-ose#','-ose+s#',"
               "'-ose+uzz#','-ounce+unci#','-ound+und#','-our+or#',"
               "'-ous#','-ous+eg#','-ous+os#','-out+ut#','-overnment#',"
               "'-overnor+uv','-ow#','-oy+uct#','-path','-pea','-pen',"
               "'-pere#','-pet#','-phonic','-piano','-point',"
               "'-pointpen+pen','-pore','-pperclass',"
               "'-procuratorfiscal+fiscal','-pronoun','-que+c#','-r#',"
               "'-r#-country','-r+n#','-r+t#','-randum','-raphone#',"
               "'-rdinarylevel+level','-re+s#','-ree+ir#',"
               "'-refrigerator+fridge','-rication','-rigine','-rmation',"
               "'-ry#','-ry##','-ry+er#','-s','-s#','-s#-y+ie#','-s+e#',"
               "'-s+k#','-s+l#','-s+rul#','-s+t#','-sband+bb#',"
               "'-school','-scope','-se#','-se+c#','-se+ce','-se+n#',"
               "'-se+t#','-se+ti#','-se+z#','-section','-sexual',"
               "'-sh+c#','-sh+t#','-shall+ll','-shipman+d#','-sia+t#',"
               "'-sin+t#','-sis+t#','-sistor+n#','-sition','-skyist',"
               "'-sole#','-soprano','-ss+z#','-ssiere','-stone',"
               "'-stroke','-sun','-sy+t#','-t#','-t#-to+na','-t+d#',"
               "'-t+n#','-t+s#','-t+ss#','-tacles+s','-te#',"
               "'-telephone+phone','-tense','-ter','-ter+s#','-terrier',"
               "'-th#','-th##','-the+s#-e','-them+em','-therapist',"
               "'-tic#','-tical#','-tide','-tingroom',"
               "'-tion+k#-rumpus+us','-tive#-electron+tron','-to',"
               "'-to#','-tobacco','-tombomb+bomb','-tor','-tralian+s#',"
               "'-troops+s','-tto+s#','-turboprop+prop#','-ty#',"
               "'-ty+st#','-uary#','-uate','-ucational','-ue#','-ular',"
               "'-ulary','-ulate','-ulation','-uli','-um#','-umn+onn#',"
               "'-unist#','-unition+o','-up#','-up+m#','-ur#','-ur+or#',"
               "'-ur+r#','-ure#','-ure+or#','-uroys+s','-urteen+rt#',"
               "'-ury+ri#','-us','-us#','-us##','-us+e#','-us+i#',"
               "'-us+os#','-us+s#','-usiness+iz','-utation','-ute+aut#',"
               "'-uth','-val','-ve#','-ve+b#','-ve+f','-ve+f#','-ve+ff',"
               "'-ve+of','-ve+p#','-vein','-veon#','-verb',"
               "'-vertisement','-vict','-voice','-w+v#','-wall#',"
               "'-wave','-will+ll','-winds+s','-with','-with#','-woman',"
               "'-would+d','-x+c#','-x+ct#','-x+g#','-x+ge#','-x+go#',"
               "'-xy+ct#','-y#','-y#-worth+orth','-y#-y+i#','-y##',"
               "'-y+act#','-y+di#','-y+et#','-y+eut#','-y+i#','-y+i##',"
               "'-y+iac#','-y+iast#','-y+ic#','-y+ie#','-y+ix#','-y+j#',"
               "'-y+t#','-yclub+i#','-ydrogenbomb+bomb',"
               "'-ylatedspirits+s','-yon+i#','-yse#','-ysis#','#',"
               "'#-a#','#-adam','#-am+m','#-am+rm','#-analyse+alyse',"
               "'#-ant#','#-ar#','#-are+re','#-ase+ss#','#-be+p#',"
               "'#-beneath+neath','#-ber+er#','#-bicycle+cycle',"
               "'#-broadcast+cast','#-bulldozer+dozer',"
               "'#-catamaran+maran','#-cavalcade+cade',"
               "'#-conception+ception','#-confound+found',"
               "'#-consecrate+secrate','#-did+d','#-does+s','#-e',"
               "'#-e#','#-e+in#','#-edge+age','#-electron+tron',"
               "'#-eller','#-en+in#','#-enforce+inforce',"
               "'#-estimate+timate','#-execute+cute','#-f+ve','#-for',"
               "'#-ge+se','#-had+d','#-has+s','#-have+ve',"
               "'#-hijack+jack','#-ic#','#-idolatry+olatry','#-ile#',"
               "'#-inflate+flate','#-ion#','#-is+s','#-k+c#',"
               "'#-kangaroo+aroo','#-l','#-l+n#','#-le#',"
               "'#-lfpenny+penny','#-n','#-not+t','#-o+a','#-of+a',"
               "'#-ology+ogy','#-on','#-ork+urc#','#-ot+t','#-our+or#',"
               "'#-ous#','#-s#','#-shall+ll','#-t','#-to','#-um#',"
               "'#-ur+r#','#-us+s','#-utic+ic#','#-ution','#-will+ll',"
               "'#-would+d','#-y#','#-y##','#-y+i#','##',"
               "'##-ed+d','###','#+b#','#+d','#+e','#+g#','#+l#','#+m#',"
               "'#+n#','#+o#','#+p#','#+r#','#+s',"
               "'#+t#','+a#','+ac#','+al#','+an#','+at#','+b#','+b##',"
               "'+c#','+d#','+e','+e#','+en#','+er#','+f#','+g#','+g##',"
               "'+i#','+il#','+in#','+ion#','+is#','+ist#','+it#','+k#',"
               "'+l','+l#','+le#','+m','+m#','+m##','+mat#','+n','+n#',"
               "'+ni#','+o#','+od#','+p','+p#','+p#-of+a','+p##',"
               "'+p##+p#','+per#','+r#','+ri#','+s#','+sim#','+t','+t#',"
               "'+t##','+to#','+u#','+ul#','+v#','+y#','+z#') NOT NULL"),
        Column(morphlemma_imminfix, "ENUM('','N','Y') NOT NULL"),
        Column(morphlemma_immrevers, "ENUM('','N','Y') NOT NULL"),
        Column(morphlemma_flatsa,
               "ENUM('','AA','AAA','AAAA','AAAAA','AAAF','AAAS','AAASA',"
               "'AAASS','AAF','AAFA','AAS','AASA','AASAA','AASAAA','AASSA',"
               "'AF','AFA','AFS','AFSA','AS','ASA','ASAA','ASAAA','ASAAAA',"
               "'ASAAAAA','ASAAS','ASAS','ASASA','ASASAA','ASF','ASS','ASSA',"
               "'ASSAA','ASSAAA','ASSS','F','FA','FAA','FAAS','FAF','FAFA',"
               "'FAS','FF','FFA','FS','FSA','FSAA','FSAS','FSS','FSSA','S',"
               "'SA','SAA','SAAA','SAAAA','SAAAAA','SAAAF','SAAAS','SAAASA',"
               "'SAAF','SAAS','SAASA','SAASAA','SAASS','SAF','SAS','SASA',"
               "'SASAA','SASS','SF','SFA','SFF','SFS','SFSA','SS','SSA',"
               "'SSAA','SSAS','SSASA','SSASF','SSASS','SSF','SSFS','SSS',"
               "'SSSA','SSSS') NOT NULL"),
        Column(morphlemma_struclab, "VARCHAR(111) NOT NULL"),
        Column(morphlemma_strucallo,
               "ENUM('','B','BC','C','CD','D','F','N','Z') NOT NULL"),
        Column(morphlemma_strucsubst, "ENUM('','N','Y') NOT NULL"),
        Column(morphlemma_strucopac, "ENUM('','N','Y') NOT NULL")]

    syntaxlemma_table = "Syntax_Lemmas"
    syntaxlemma_id = "SyntaxLemmaId"
    syntaxlemma_head = "Head"
    syntaxlemma_classnum = "Lemma_ClassNum"
    syntaxlemma_class = "Lemma_Class"
    syntaxlemma_c_n = "Lemma_C_N"
    syntaxlemma_unc_n = "Lemma_Unc_N"
    syntaxlemma_sing_n = "Lemma_Sing_N"
    syntaxlemma_plu_n = "Lemma_Plu_N"
    syntaxlemma_grc_n = "Lemma_GrC_N"
    syntaxlemma_grunc_n = "Lemma_GrUnc_N"
    syntaxlemma_attr_n = "Lemma_Attr_N"
    syntaxlemma_postpos_n = "Lemma_PostPos_N"
    syntaxlemma_voc_n = "Lemma_Voc_N"
    syntaxlemma_proper_n = "Lemma_Proper_N"
    syntaxlemma_exp_n = "Lemma_Exp_N"
    syntaxlemma_trans_v = "Lemma_Trans_V"
    syntaxlemma_transcomp_v = "Lemma_TransComp_V"
    syntaxlemma_intrans_v = "Lemma_Intrans_V"
    syntaxlemma_ditrans_v = "Lemma_Ditrans_V"
    syntaxlemma_link_v = "Lemma_Link_V"
    syntaxlemma_phr_v = "Lemma_Phr_V"
    syntaxlemma_prep_v = "Lemma_Prep_V"
    syntaxlemma_phrprep_v = "Lemma_PhrPrep_V"
    syntaxlemma_exp_v = "Lemma_Exp_V"
    syntaxlemma_ord_a = "Lemma_Ord_A"
    syntaxlemma_attr_a = "Lemma_Attr_A"
    syntaxlemma_pred_a = "Lemma_Pred_A"
    syntaxlemma_postpos_a = "Lemma_PostPos_A"
    syntaxlemma_exp_a = "Lemma_Exp_A"
    syntaxlemma_ord_adv = "Lemma_Ord_ADV"
    syntaxlemma_pred_adv = "Lemma_Pred_ADV"
    syntaxlemma_postpos_adv = "Lemma_PostPos_ADV"
    syntaxlemma_comb_adv = "Lemma_Comb_ADV"
    syntaxlemma_exp_adv = "Lemma_Exp_ADV"
    syntaxlemma_card_num = "Lemma_Card_NUM"
    syntaxlemma_ord_num = "Lemma_Ord_NUM"
    syntaxlemma_exp_num = "Lemma_Exp_NUM"
    syntaxlemma_pers_pron = "Lemma_Pers_PRON"
    syntaxlemma_dem_pron = "Lemma_Dem_PRON"
    syntaxlemma_poss_pron = "Lemma_Poss_PRON"
    syntaxlemma_refl_pron = "Lemma_Refl_PRON"
    syntaxlemma_wh_pron = "Lemma_Wh_PRON"
    syntaxlemma_det_pron = "Lemma_Det_PRON"
    syntaxlemma_pron_pron = "Lemma_Pron_PRON"
    syntaxlemma_exp_pron = "Lemma_Exp_PRON"
    syntaxlemma_cor_c = "Lemma_Cor_C"
    syntaxlemma_sub_c = "Lemma_Sub_C"
    syntaxlemma_columns = [
        Identifier(syntaxlemma_id, "SMALLINT(5) UNSIGNED NOT NULL"),
        Column(syntaxlemma_head, "VARCHAR(34) NOT NULL"),
        Column(syntaxlemma_classnum,
               "ENUM('1','10','11','12','13','14','15','2','3','4','5','6',"
               "'7','8','9') NOT NULL"),
        Column(syntaxlemma_class,
               "ENUM('A','ABB','ADV','ART','C','CCON','I','LET','N','NUM',"
               "'PREP','PRON','SCON','TO','V') NOT NULL"),
        Column(syntaxlemma_c_n, enum("N", "Y")),
        Column(syntaxlemma_unc_n, enum("N", "Y")),
        Column(syntaxlemma_sing_n, enum("N", "Y")),
        Column(syntaxlemma_plu_n, enum("N", "Y")),
        Column(syntaxlemma_grc_n, enum("N", "Y")),
        Column(syntaxlemma_grunc_n, enum("N", "Y")),
        Column(syntaxlemma_attr_n, enum("N", "Y")),
        Column(syntaxlemma_postpos_n, enum("N", "Y")),
        Column(syntaxlemma_voc_n, enum("N", "Y")),
        Column(syntaxlemma_proper_n, enum("N", "Y")),
        Column(syntaxlemma_exp_n, enum("N", "Y")),
        Column(syntaxlemma_trans_v, enum("N", "Y")),
        Column(syntaxlemma_transcomp_v, enum("N", "Y")),
        Column(syntaxlemma_intrans_v, enum("N", "Y")),
        Column(syntaxlemma_ditrans_v, enum("N", "Y")),
        Column(syntaxlemma_link_v, enum("N", "Y")),
        Column(syntaxlemma_phr_v, enum("N", "Y")),
        Column(syntaxlemma_prep_v, enum("N", "Y")),
        Column(syntaxlemma_phrprep_v, enum("N", "Y")),
        Column(syntaxlemma_exp_v, enum("N", "Y")),
        Column(syntaxlemma_ord_a, enum("N", "Y")),
        Column(syntaxlemma_attr_a, enum("N", "Y")),
        Column(syntaxlemma_pred_a, enum("N", "Y")),
        Column(syntaxlemma_postpos_a, enum("N", "Y")),
        Column(syntaxlemma_exp_a, enum("N", "Y")),
        Column(syntaxlemma_ord_adv, enum("N", "Y")),
        Column(syntaxlemma_pred_adv, enum("N", "Y")),
        Column(syntaxlemma_postpos_adv, enum("N", "Y")),
        Column(syntaxlemma_comb_adv, enum("N", "Y")),
        Column(syntaxlemma_exp_adv, enum("N", "Y")),
        Column(syntaxlemma_card_num, enum("N", "Y")),
        Column(syntaxlemma_ord_num, enum("N", "Y")),
        Column(syntaxlemma_exp_num, enum("N", "Y")),
        Column(syntaxlemma_pers_pron, enum("N", "Y")),
        Column(syntaxlemma_dem_pron, enum("N", "Y")),
        Column(syntaxlemma_poss_pron, enum("N", "Y")),
        Column(syntaxlemma_refl_pron, enum("N", "Y")),
        Column(syntaxlemma_wh_pron, enum("N", "Y")),
        Column(syntaxlemma_det_pron, enum("N", "Y")),
        Column(syntaxlemma_pron_pron, enum("N", "Y")),
        Column(syntaxlemma_exp_pron, enum("N", "Y")),
        Column(syntaxlemma_cor_c, enum("N", "Y")),
        Column(syntaxlemma_sub_c, enum("N", "Y"))]

    corpus_table = "Ortho_Words"
    corpus_id = "ID"
    corpus_phonoword_id = "ID"
    corpus_morphword_id = "ID"
    corpus_word = "Word"
    corpus_worddia = "WordDia"
    corpus_cob = "Word_Cob"
    corpus_lemma_id = "LemmaId"
    corpus_phonolemma_id = "LemmaId"
    corpus_morphlemma_id = "LemmaId"
    corpus_syntaxlemma_id = "LemmaId"
    corpus_orthocnt = "Word_OrthoCnt"
    corpus_orthostatus = "Word_OrthoStatus"
    corpus_cobspelldev = "Word_CobSpellDev"
    corpus_wordsyldia = "Word_WordSylDia"
    corpus_columns = [
        Identifier(corpus_id,
                   "MEDIUMINT(6) UNSIGNED NOT NULL", unique=False),
        Link(corpus_lemma_id, lemma_table),
        Link(corpus_phonoword_id, phonoword_table, create=False),
        Link(corpus_morphword_id, morphword_table, create=False),
        Link(corpus_phonolemma_id, phonolemma_table, create=False),
        Link(corpus_morphlemma_id, morphlemma_table, create=False),
        Link(corpus_syntaxlemma_id, syntaxlemma_table, create=False),
        Column(corpus_word, "VARCHAR(35) NOT NULL"),
        Column(corpus_worddia, "VARCHAR(35) NOT NULL"),
        Column(corpus_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
        Column(corpus_orthocnt, "ENUM('1','2','3','4','5') NOT NULL"),
        Column(corpus_orthostatus, "ENUM('B', 'A') NOT NULL"),
        Column(corpus_cobspelldev, "MEDIUMINT(6) UNSIGNED NOT NULL"),
        Column(corpus_wordsyldia, "VARCHAR(43) NOT NULL")]

    auto_create = ["lemma", "phonoword", "phonolemma", "morphlemma",
                   "morphword", "syntaxlemma", "corpus"]

    expected_files = sorted(["eow.cd", "eol.cd", "epw.cd", "epl.cd",
                             "emw.cd", "eml.cd", "esl.cd"])

    def set_fnc_map(self):
        """
        Set up a mapping between each CELEX file and the corresponding
        processing method.

        Called during __init__().
        """
        self._FNC_MAP = {
            self._ORTH_WORDS: self.process_orth_word,
            self._ORTH_LEMMAS: self.process_orth_lemma,
            self._PHONO_WORDS: self.process_phono_word,
            self._PHONO_LEMMAS: self.process_phono_lemma,
            self._MORPH_WORDS: self.process_morph_word,
            self._MORPH_LEMMAS: self.process_morph_lemma,
            self._SYNTAX_LEMMAS: self.process_syntax_lemma}

    def map_query_items(self):
        """
        Assign query items to columns.

        Called during __init__().
        """
        self.map_query_item(QUERY_ITEM_TRANSCRIPT, "phonoword_phonstrsdisc")
        self.map_query_item(QUERY_ITEM_POS, "syntaxlemma_class")
        self.map_query_item(QUERY_ITEM_WORD, "corpus_worddia")

    @classmethod
    def component_to_label(cls, component):
        _MAP = {cls._PHONO_WORDS: _tr("Phonology word forms"),
                cls._PHONO_LEMMAS: _tr("Phonology lemmas"),
                cls._MORPH_WORDS: _tr("Morphology words forms"),
                cls._MORPH_LEMMAS: _tr("Morphology lemmas"),
                cls._ORTH_WORDS: _tr("Orthography word forms"),
                cls._ORTH_LEMMAS: _tr("Orthography lemmas"),
                cls._SYNTAX_LEMMAS: _tr("Syntax lemmas")}

        return _MAP.get(component, None)

    def process_orth_word(self, columns):
        def _orth_wdict():
            return {self.corpus_id: wid,
                    self.corpus_word: word,
                    self.corpus_worddia: worddia,
                    self.corpus_cob: cob,
                    self.corpus_lemma_id: lemma_id,
                    self.corpus_orthocnt: orthocnt,
                    self.corpus_orthostatus: orthostatus,
                    self.corpus_cobspelldev: cobspelldev,
                    self.corpus_wordsyldia: wordsyldia}

        (wid, worddia, cob, lemma_id,
         orthocnt, orthostatus, _, cobspelldev, wordsyldia) = columns[:9]

        word = dia_to_unicode(worddia)
        self.table(self.corpus_table).add(_orth_wdict())

        # add alternative spellings:
        for cnt in range(int(orthocnt)-1):
            try:
                (worddia,
                 orthostatus,
                 _,
                 cobspelldev,
                 wordsyldia) = columns[(9 + cnt * 5):(14 + cnt * 5)]
            except ValueError:
                pass
            else:
                self.table(self.corpus_table).add(_orth_wdict())

    def process_orth_lemma(self, columns):
        def _orth_ldict():
            return {self.lemma_id: lid,
                    self.lemma_label: label,
                    self.lemma_headdia: headdia,
                    self.lemma_cob: cob,
                    self.lemma_orthocnt: orthocnt,
                    self.lemma_orthostatus: orthostatus,
                    self.lemma_cobspelldev: cobspelldev,
                    self.lemma_headsyldia: headsyldia}

        (lid, headdia, cob, orthocnt,
         orthostatus, _, cobspelldev, headsyldia) = columns[:8]

        label = dia_to_unicode(headdia)
        self.table(self.lemma_table).add(_orth_ldict())

        # add alternative spellings:
        for cnt in range(int(orthocnt)-1):
            try:
                (orthostatus,
                 _,
                 cobspelldev,
                 headsyldia) = (
                     columns[(8 + cnt * 4):(12 + cnt * 4)])
            except ValueError:
                pass
            else:
                self.table(self.lemma_table).add(_orth_ldict())

    def process_phono_word(self, columns):
        (wid, word, _, _, proncnt,
         _, phonstrsdisc, phoncvbr, phonsylbclx) = columns[:9]

        self.table(self.phonoword_table).add(
            {self.phonoword_id: wid,
             self.phonoword_word: word,
             self.phonoword_phonstrsdisc: phonstrsdisc,
             self.phonoword_proncnt: proncnt,
             self.phonoword_phoncvbr: phoncvbr,
             self.phonoword_phonsylbclx: phonsylbclx})

    def process_phono_lemma(self, columns):
        (lid, head, _, proncnt, _,
         phonstrsdisc, phoncvbr, phonsylbclx) = columns[:8]

        self.table(self.phonolemma_table).add(
            {self.phonolemma_id: lid,
             self.phonolemma_head: head,
             self.phonolemma_proncnt: proncnt,
             self.phonolemma_phonstrsdisc: phonstrsdisc,
             self.phonolemma_phoncvbr: phoncvbr,
             self.phonolemma_phonsylbclx: phonsylbclx})

    def process_morph_word(self, columns):
        wid, word, _, _, flecttype, transinfl = columns[:6]

        self.table(self.morphword_table).add(
            {self.morphword_id: wid,
             self.morphword_word: word,
             self.morphword_flecttype: flecttype,
             self.morphword_transinfl: transinfl})

    def process_morph_lemma(self, columns):
        (lid,
         head,
         _,
         morphstatus,
         lang,
         morphcnt,
         nvaffcomp,
         der,
         comp,
         dercomp,
         ldef,
         imm,
         immsubcat,
         immsa,
         immallo,
         immsubst,
         immopac,
         transder,
         imminfix,
         immrevers,
         flatsa,
         struclab,
         strucallo,
         strucsubst,
         strucopac) = columns[:25]

        self.table(self.morphlemma_table).add(
            {self.morphlemma_id: lid,
             self.morphlemma_head: head,
             self.morphlemma_morphstatus: morphstatus,
             self.morphlemma_lang: lang,
             self.morphlemma_morphcnt: morphcnt,
             self.morphlemma_nvaffcomp: nvaffcomp,
             self.morphlemma_der: der,
             self.morphlemma_comp: comp,
             self.morphlemma_dercomp: dercomp,
             self.morphlemma_def: ldef,
             self.morphlemma_imm: imm,
             self.morphlemma_immsubcat: immsubcat,
             self.morphlemma_immsa: immsa,
             self.morphlemma_immallo: immallo,
             self.morphlemma_immsubst: immsubst,
             self.morphlemma_immopac: immopac,
             self.morphlemma_transder: transder,
             self.morphlemma_imminfix: imminfix,
             self.morphlemma_immrevers: immrevers,
             self.morphlemma_flatsa: flatsa,
             self.morphlemma_struclab: struclab,
             self.morphlemma_strucallo: strucallo,
             self.morphlemma_strucsubst: strucsubst,
             self.morphlemma_strucopac: strucopac})

    def process_syntax_lemma(self, columns):
        (lid,
         head,
         _,
         classnum,
         c_n,
         unc_n,
         sing_n,
         plu_n,
         grc_n,
         grunc_n,
         attr_n,
         postpos_n,
         voc_n,
         proper_n,
         exp_n,
         trans_v,
         transcomp_v,
         intrans_v,
         ditrans_v,
         link_v,
         phr_v,
         prep_v,
         phrprep_v,
         exp_v,
         ord_a,
         attr_a,
         pred_a,
         postpos_a,
         exp_a,
         ord_adv,
         pred_adv,
         postpos_adv,
         comb_adv,
         exp_adv,
         card_num,
         ord_num,
         exp_num,
         pers_pron,
         dem_pron,
         poss_pron,
         refl_pron,
         wh_pron,
         det_pron,
         pron_pron,
         exp_pron,
         cor_c,
         sub_c) = columns[:47]

        lclass = self._POS_MAP[classnum]

        self.table(self.syntaxlemma_table).add(
            {self.syntaxlemma_id: lid,
             self.syntaxlemma_head: head,
             self.syntaxlemma_classnum: classnum,
             self.syntaxlemma_class: lclass,
             self.syntaxlemma_c_n: c_n,
             self.syntaxlemma_unc_n: unc_n,
             self.syntaxlemma_sing_n: sing_n,
             self.syntaxlemma_plu_n: plu_n,
             self.syntaxlemma_grc_n: grc_n,
             self.syntaxlemma_grunc_n: grunc_n,
             self.syntaxlemma_attr_n: attr_n,
             self.syntaxlemma_postpos_n: postpos_n,
             self.syntaxlemma_voc_n: voc_n,
             self.syntaxlemma_proper_n: proper_n,
             self.syntaxlemma_exp_n: exp_n,
             self.syntaxlemma_trans_v: trans_v,
             self.syntaxlemma_transcomp_v: transcomp_v,
             self.syntaxlemma_intrans_v: intrans_v,
             self.syntaxlemma_ditrans_v: ditrans_v,
             self.syntaxlemma_link_v: link_v,
             self.syntaxlemma_phr_v: phr_v,
             self.syntaxlemma_prep_v: prep_v,
             self.syntaxlemma_phrprep_v: phrprep_v,
             self.syntaxlemma_exp_v: exp_v,
             self.syntaxlemma_ord_a: ord_a,
             self.syntaxlemma_attr_a: attr_a,
             self.syntaxlemma_pred_a: pred_a,
             self.syntaxlemma_postpos_a: postpos_a,
             self.syntaxlemma_exp_a: exp_a,
             self.syntaxlemma_ord_adv: ord_adv,
             self.syntaxlemma_pred_adv: pred_adv,
             self.syntaxlemma_postpos_adv: postpos_adv,
             self.syntaxlemma_comb_adv: comb_adv,
             self.syntaxlemma_exp_adv: exp_adv,
             self.syntaxlemma_card_num: card_num,
             self.syntaxlemma_ord_num: ord_num,
             self.syntaxlemma_exp_num: exp_num,
             self.syntaxlemma_pers_pron: pers_pron,
             self.syntaxlemma_dem_pron: dem_pron,
             self.syntaxlemma_poss_pron: poss_pron,
             self.syntaxlemma_refl_pron: refl_pron,
             self.syntaxlemma_wh_pron: wh_pron,
             self.syntaxlemma_det_pron: det_pron,
             self.syntaxlemma_pron_pron: pron_pron,
             self.syntaxlemma_exp_pron: exp_pron,
             self.syntaxlemma_cor_c: cor_c,
             self.syntaxlemma_sub_c: sub_c,
             })

    @staticmethod
    def get_title():
        return "CELEX2 Lexical Database (English)"

    @staticmethod
    def get_name():
        return "CELEX2 (EN)"

    @staticmethod
    def get_db_name():
        return "coq_celexen"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en"

    @staticmethod
    def get_description():
        return [
            "The CELEX lexical database for English contains detailed "
            "information for XXX lemmas (about 100,000 inflected forms) on:",
            "<ul><li>orthography (variations in spelling [not supported by "
            "Coquery], hyphenation)</li> <li>phonology (phonetic "
            "transcriptions, variations in pronunciation [not supported by "
            "Coquery], syllable structure, primary stress)</li> <li>"
            "morphology (derivational and compositional structure, "
            "inflectional paradigms)</li> <li>syntax (word class, word "
            "class-specific subcategorizations, argument structures)</li>"
            "<li>word frequency (summed word and lemma counts, based on "
            "representative text corpora)</li></ul>"]


if __name__ == "__main__":
    BuilderClass().build()

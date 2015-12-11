# -*- coding: utf-8 -*-

"""
coq_install_celex.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function

import codecs
import unicodedata

from corpusbuilder import *

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

class BuilderClass(BaseCorpusBuilder):
    file_filter = "e??.cd"

    expected_files = sorted(["eow.cd", "eol.cd", "epw.cd", "epl.cd", "emw.cd", "eml.cd", "esl.cd"])

    
    def __init__(self, gui=False, *args):
        # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        self.corpus_table = "eow"
        self.corpus_id = "IdNum"
        self.corpus_word_id = "IdNum"
        
        self.word_table = "eow"
        self.word_id = "IdNum"
        self.word_phonoword_id = "IdNum"
        self.word_morphword_id = "IdNum"
        self.word_label = "Word"
        self.word_worddia = "WordDia"
        self.word_cob = "Word_Cob"
        self.word_lemma_id = "IdNumLemma"
        self.word_phonolemma_id = "IdNumLemma"
        self.word_morphlemma_id = "IdNumLemma"
        self.word_syntaxlemma_id = "IdNumLemma"
        self.word_orthocnt = "Word_OrthoCnt"
        self.word_orthostatus = "Word_OrthoStatus"
        self.word_cobspellfreq = "Word_CobSpellFreq"
        self.word_cobspelldev = "Word_CobSpellDev"
        self.word_wordsyldia = "Word_WordSylDia"
        
        self.lemma_table = "eol"
        self.lemma_id = "IdNum"
        self.lemma_label = "Head"
        self.lemma_headdia = "HeadDia"
        self.lemma_cob = "Lemma_Cob"
        self.lemma_orthocnt = "Lemma_OrthoCnt"
        self.lemma_orthostatus = "Lemma_OrthoStatus"
        self.lemma_cobspellfreq = "Lemma_CobSpellFreq"
        self.lemma_cobspelldev = "Lemma_CobSpellDev"
        self.lemma_headsyldia = "Lemma_HeadSylDia"
        
        self.phonoword_table = "epw"
        self.phonoword_id = "IdNum"
        self.phonoword_label = "PhonoWord_Word"
        self.phonoword_cob = "PhonoWord_Cob"
        self.phonoword_proncnt = "PhonoWord_PronCnt"
        self.phonoword_phonstrsdisc = "PhonoWord_PhonStrsDISC"
        self.phonoword_phoncvbr = "PhonoWord_PhonCVBr"
        self.phonoword_phonsylbclx = "PhonoWord_PhonSylBCLX"

        self.phonolemma_table = "epl"
        self.phonolemma_id = "IdNum"
        self.phonolemma_label = "PhonoLemma_Head"
        self.phonolemma_cob = "PhonoLemma_Cob"
        self.phonolemma_proncnt = "PhonoLemma_PronCnt"
        self.phonolemma_phonstrsdisc = "PhonoLemma_PhonStrsDISC"
        self.phonolemma_phoncvbr = "PhonoLemma_PhonCVBr"
        self.phonolemma_phonsylbclx = "PhonoLemma_PhonSylBCLX"

        self.morphword_table = "emw"
        self.morphword_id = "IdNum"
        self.morphword_label = "MorphWord_Word"
        self.morphword_cob = "MorphWord_Cob"
        self.morphword_flecttype = "MorphWord_FlectType"
        self.morphword_transinfl = "MorphWord_TransInfl"

        self.morphlemma_table = "eml"
        self.morphlemma_id = "IdNum"
        self.morphlemma_label = "MorphLemma_Head"
        self.morphlemma_cob = "MorphLemma_Cob"
        self.morphlemma_morphstatus = "MorphLemma_MorphStatus"
        self.morphlemma_lang = "MorphLemma_Lang"
        self.morphlemma_morphcnt = "MorphLemma_MorphCnt"
        self.morphlemma_nvaffcomp = "MorphLemma_NVAffComp"
        self.morphlemma_der = "MorphLemma_Der"
        self.morphlemma_comp = "MorphLemma_Comp"
        self.morphlemma_dercomp = "MorphLemma_DerComp"
        self.morphlemma_def = "MorphLemma_Def"
        self.morphlemma_imm = "MorphLemma_Imm"
        self.morphlemma_immsubcat = "MorphLemma_ImmSubCat"
        self.morphlemma_immsa = "MorphLemma_ImmSA"
        self.morphlemma_immallo = "MorphLemma_ImmAllo"
        self.morphlemma_immsubst = "MorphLemma_ImmSubst"
        self.morphlemma_immopac = "MorphLemma_ImmOpac"
        self.morphlemma_transder = "MorphLemma_TransDer"
        self.morphlemma_imminfix = "MorphLemma_ImmInfix"
        self.morphlemma_immrevers = "MorphLemma_ImmRevers"
        self.morphlemma_flatsa = "MorphLemma_FlatSA"
        self.morphlemma_struclab = "MorphLemma_StrucLab"
        self.morphlemma_strucallo = "MorphLemma_StrucAllo"
        self.morphlemma_strucsubst = "MorphLemma_StrucSubst"
        self.morphlemma_strucopac = "MorphLemma_StrucOpac"

        self.syntaxlemma_table = "esl"
        self.syntaxlemma_id = "SyntaxLemma_IdNum"
        self.syntaxlemma_label = "SyntaxLemma_Head"
        self.syntaxlemma_cob = "SyntaxLemma_Cob"
        self.syntaxlemma_classnum = "SyntaxLemma_ClassNum"
        self.syntaxlemma_c_n = "SyntaxLemma_C_N"
        self.syntaxlemma_unc_n = "SyntaxLemma_Unc_N"
        self.syntaxlemma_sing_n = "SyntaxLemma_Sing_N"
        self.syntaxlemma_plu_n = "SyntaxLemma_Plu_N"
        self.syntaxlemma_grc_n = "SyntaxLemma_GrC_N"
        self.syntaxlemma_grunc_n = "SyntaxLemma_GrUnc_N"
        self.syntaxlemma_attr_n = "SyntaxLemma_Attr_N"
        self.syntaxlemma_postpos_n = "SyntaxLemma_PostPos_N"
        self.syntaxlemma_voc_n = "SyntaxLemma_Voc_N"
        self.syntaxlemma_proper_n = "SyntaxLemma_Proper_N"
        self.syntaxlemma_exp_n = "SyntaxLemma_Exp_N"
        self.syntaxlemma_trans_v = "SyntaxLemma_Trans_V"
        self.syntaxlemma_transcomp_v = "SyntaxLemma_TransComp_V"
        self.syntaxlemma_intrans_v = "SyntaxLemma_Intrans_V"
        self.syntaxlemma_ditrans_v = "SyntaxLemma_Ditrans_V"
        self.syntaxlemma_link_v = "SyntaxLemma_Link_V"
        self.syntaxlemma_phr_v = "SyntaxLemma_Phr_V"
        self.syntaxlemma_prep_v = "SyntaxLemma_Prep_V"
        self.syntaxlemma_phrprep_v = "SyntaxLemma_PhrPrep_V"
        self.syntaxlemma_exp_v = "SyntaxLemma_Exp_V"
        self.syntaxlemma_ord_a = "SyntaxLemma_Ord_A"
        self.syntaxlemma_attr_a = "SyntaxLemma_Attr_A"
        self.syntaxlemma_pred_a = "SyntaxLemma_Pred_A"
        self.syntaxlemma_postpos_a = "SyntaxLemma_PostPos_A"
        self.syntaxlemma_exp_a = "SyntaxLemma_Exp_A"
        self.syntaxlemma_ord_adv = "SyntaxLemma_Ord_ADV"
        self.syntaxlemma_pred_adv = "SyntaxLemma_Pred_ADV"
        self.syntaxlemma_postpos_adv = "SyntaxLemma_PostPos_ADV"
        self.syntaxlemma_comb_adv = "SyntaxLemma_Comb_ADV"
        self.syntaxlemma_exp_adv = "SyntaxLemma_Exp_ADV"
        self.syntaxlemma_card_num = "SyntaxLemma_Card_NUM"
        self.syntaxlemma_ord_num = "SyntaxLemma_Ord_NUM"
        self.syntaxlemma_exp_num = "SyntaxLemma_Exp_NUM"
        self.syntaxlemma_pers_pron = "SyntaxLemma_Pers_PRON"
        self.syntaxlemma_dem_pron = "SyntaxLemma_Dem_PRON"
        self.syntaxlemma_poss_pron = "SyntaxLemma_Poss_PRON"
        self.syntaxlemma_refl_pron = "SyntaxLemma_Refl_PRON"
        self.syntaxlemma_wh_pron = "SyntaxLemma_Wh_PRON"
        self.syntaxlemma_det_pron = "SyntaxLemma_Det_PRON"
        self.syntaxlemma_pron_pron = "SyntaxLemma_Pron_PRON"
        self.syntaxlemma_exp_pron = "SyntaxLemma_Exp_PRON"
        self.syntaxlemma_cor_c = "SyntaxLemma_Cor_C"
        self.syntaxlemma_sub_c = "SyntaxLemma_Sub_C"

        self.create_table_description(self.phonolemma_table,
            [Primary(self.phonolemma_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.phonolemma_label, "VARCHAR(34) NOT NULL"),
             Column(self.phonolemma_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.phonolemma_proncnt, "ENUM('1','10','11','12','13','14','15','16','18','2','20','21','24','25','3','30','32','36','4','40','48','5','6','60','7','8','9') NOT NULL"),
             Column(self.phonolemma_phonstrsdisc, "VARCHAR(40) NOT NULL"),
             Column(self.phonolemma_phoncvbr, "VARCHAR(53) NOT NULL"),
             Column(self.phonolemma_phonsylbclx, "VARCHAR(53) NOT NULL")])

        self.create_table_description(self.phonoword_table,
            [Primary(self.phonoword_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.phonoword_label, "VARCHAR(35) NOT NULL"),
             Column(self.phonoword_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.phonoword_proncnt, "ENUM('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','18','20','21','24','25','28','30','32','36','40','48','60') NOT NULL"),
             Column(self.phonoword_phonstrsdisc, "VARCHAR(41) NOT NULL"),
             Column(self.phonoword_phoncvbr, "VARCHAR(53) NOT NULL"),
             Column(self.phonoword_phonsylbclx, "VARCHAR(53) NOT NULL")])

        self.create_table_description(self.morphlemma_table,
            [Primary(self.morphlemma_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.morphlemma_label, "VARCHAR(34) NOT NULL"),
             Column(self.morphlemma_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.morphlemma_morphstatus, "ENUM('C','F','I','M','O','R','U','Z') NOT NULL"),
             Column(self.morphlemma_lang, "ENUM('','A','B','D','F','G','I','L','S') NOT NULL"),
             Column(self.morphlemma_morphcnt, "ENUM('0','1','2','3','4','5','8') NOT NULL"),
             Column(self.morphlemma_nvaffcomp, "ENUM('N','Y') NOT NULL"),
             Column(self.morphlemma_der, "ENUM('N','Y') NOT NULL"),
             Column(self.morphlemma_comp, "ENUM('N','Y') NOT NULL"),
             Column(self.morphlemma_dercomp, "ENUM('N','Y') NOT NULL"),
             Column(self.morphlemma_def, "ENUM('N','Y') NOT NULL"),
             Column(self.morphlemma_imm, "VARCHAR(27) NOT NULL"),
             Column(self.morphlemma_immsubcat, "ENUM('','?','?3','?N','?O','?x','0','0B','0N','0P','0x','1','1?','11','12x','1A','1B','1I','1N','1Nx','1P','1x','1xx','2','2?','22','23','2A','2B','2N','2Nx','2O','2P','2x','2x3x','2xN','2xP','2xx','3','3?','31','32','32x','33','3A','3Ax','3B','3Bx','3C','3N','3Nx','3O','3P','3x','3x3x','3xB','3xN','3xx','A','A0','A1','A1x','A2','A2x','A3','A3x','AA','AB','AI','AN','ANx','AP','AQ','Ax','AxAx','AxB','AxN','AxP','Axx','B','B0','B1','B1x','B2','B2x','B3','B3x','BA','BB','BBx','BC','BN','BNx','BP','BPx','Bx','C','C2','CB','CC','CP','D','DN','DO','I','II','IN','Ix','N','N0','N0x','N1','N1x','N2','N2x','N3','N3x','NA','NB','NBx','NN','NNx','NP','NQ','Nx','Nx2','NxB','NxN','NxNx','NxP','Nxx','NxxN','O','O1','O3','OA','OB','OC','ON','ONx','OO','OP','Ox','P','PB','PN','PO','PP','PQx','Px','Q','Q?x','Q3x','QA','QN','QNx','QO','QQ','Qx','x0','x1','x1N','x1x','x2','x2Bx','x2P','x2x','x3','x3P','x3x','xA','xAN','xAP','xAx','xB','xN','xNN','xNx','xNxP','xO','xP','xx','xx3','xxN','xxx') NOT NULL"),
             Column(self.morphlemma_immsa, "ENUM('','AA','AAA','AAF','AAS','AF','AFS','AS','ASA','ASAS','ASS','ASSA','F','FA','FAFA','FAS','FF','FS','FSA','S','SA','SAA','SAAS','SAS','SASA','SF','SFA','SS','SSA') NOT NULL"),
             Column(self.morphlemma_immallo, "ENUM('','B','C','D','F','N','Z') NOT NULL"),
             Column(self.morphlemma_immsubst, "ENUM('','N','Y') NOT NULL"),
             Column(self.morphlemma_immopac, "ENUM('','N','Y') NOT NULL"),
             Column(self.morphlemma_transder, "ENUM('','-a#','-a+er#','-a+o#','-a+t#','-able#','-about','-about#','-aceti#','-acy#','-after','-against','-age#','-age##','-ah#','-ail+al#','-aim+am#','-ain#','-ain+an#','-ain+en#','-ain+ent#','-ain+ic#','-ain+in#','-ainto+in#','-air+ar#','-air+er#','-al#','-al+e#','-al+ll#','-al+u#','-along+long#','-ample+empl#','-an#','-anentwave','-anniversary','-ant#','-ar#','-ar+er#','-ar+i#','-ar+re#-ey+y','-aratoryschool+school','-ard+er#','-are+re','-arithm','-ark+eark#','-ary#','-as#','-ase+ss#','-ass+iss#','-ast+st#','-ast+sti#','-asure+nsur#','-asy#','-at+d#','-at+t#','-ate#','-ate#-star+ar','-ate##','-ateagainst#','-atein#','-ation','-ation#','-ation+e','-atrol#-orpedoboat+boat','-auxiliary','-away+way#','-ax#-carbon+on','-ay#','-b#','-b+m#','-b+pt#','-bagpipes+pipes','-be+p#','-be+pt#','-bebop+bop','-ber+er#','-bereft+reft','-beto+pt#','-binations+s','-ble#','-ble+il#','-blue','-bockers+s','-c#','-c+qu#','-cal#','-castic+ky','-cat','-cate#','-ce+ci#','-ce+s#','-ce+se#','-ce+t#','-ce+ti#','-chop#','-chute#','-ck+qu#','-cks+x#','-code','-coleslaw+slaw','-colonelblimp+blimp','-consonant','-cotton','-crat#','-crophone+ke','-ct+g#','-cy+ti#','-cycle+ke','-d#','-d+s#','-d+t#','-day','-de+s#','-de+ss#','-deep','-densation#','-detached','-detective+tec','-deto+s#','-disease','-dish','-dive','-dkerchief+k#','-dle#','-dle+l#','-dmother','-dmother+n#','-dog#','-down#','-duction','-dvancedlevel+level','-dyboy','-e#','-e#-e#','-e##','-e+a#','-e+ac#','-e+an#','-e+ar#','-e+at#','-e+ct#','-e+i#','-e+ic#','-e+ig#','-e+in#','-e+it#','-e+l#','-e+m#','-e+n#','-e+o#','-e+ot#','-e+pt#','-e+s#','-e+t#','-e+u#','-eabout+t#','-eace+ac#','-eakfast#-lunch+unch','-eal+el#','-ear+ar#','-ear+ir#','-ear+or#','-east+est#','-eat+et#','-eaudecologne+cologne','-ece+c#','-ect+ic#','-ect+ig#','-ed+d#','-ed+ss#','-edo','-edplatypus','-edy#','-edy+i#','-ee','-ee#','-ee+a#','-eel+il#','-eer#','-efrom#','-eian','-eian+b#','-ein#','-eive+ipi#','-el+uls#','-eleison','-elsalvador+salvadore#','-em+mpt#','-emathics','-ematics+s','-eme#','-empire+imper#','-en+in#','-en+n#','-encefiction+fi','-end#','-ening+ning','-ent#','-entitycard+card','-eof#','-eon','-eon#','-eous#','-ep+p#','-er#','-er+r#','-er+ri#','-erambulator+ram','-eration','-eration+s','-erations+s','-erative','-eree','-erer#','-erer+r#','-ergeant+arge','-ern','-ern#-venience','-ernist','-eror+r#','-ers+s','-erto+r#','-ery#','-es#','-es+a#','-escape+scape#','-essor','-et','-et+t#','-etable','-etarian#','-ethering+ithering','-eto','-eto#','-eum#','-eur#','-evatedrailway','-evision+l#','-ew+a#','-ewith#','-ex#','-ey#','-ey+i#','-eyeglasses+glasses','-f#','-f+ic#','-f+v#','-f+ve','-f+ve#','-falcon','-fall+al','-fessional#-ateur','-fibre','-fidencetrick','-footlights+lights','-for#','-ford#-cambridge+bridge','-frenchfries+fries','-from#','-g#','-ghfidelity+fi','-got','-graph','-gun','-gy#','-h#','-h+n#','-had+d','-haddock','-handcuffs+cuffs','-hant+ant#','-has+s','-have+ai#-ot+t','-have+ve','-house','-hronization','-i#','-i#-stellar+ar','-ia#','-ian#','-ian+o#','-ic#','-ic##','-ic+er#','-ic+o#','-ican#','-ice+et#','-iceberg+berg','-id#','-idatedannuities+s','-ie#','-ief+ev#','-ier#','-ies+y','-ign+gn#','-ik#','-il+vy#','-ill+o#-ot+t','-im+m#','-imate','-imensional','-in#','-in+n#','-in+ni#','-in+nn#','-ination','-incense+cense','-ind+ound#','-ine#','-ine+ens#','-inese+e','-influenza+flu','-ing+n#-to+na','-ingroom#','-ink+unk#','-intosh','-io#','-ion#','-ion+or#','-ion+u#','-ior#','-ious#','-ir+red#','-ir+ri#','-is#','-is+s','-is+t#','-isement','-ish#','-ism#','-istan#','-it+t#','-ite#','-itory','-itous#','-itulate','-ity#','-ity+ar#','-ium#','-ivarius','-ive#','-ive+p#','-ive+pt#','-iwog#','-ix+ec#','-ize#','-k#','-k+c#','-k+ch#','-k+quer#','-k+t#','-ke#-fog+g','-ke+c#','-ke+ch#','-ke+ck#','-keeper#','-l#','-l#-l','-l#-monologue+logue','-l+t#','-le#','-le+ell#-e#','-le+il#','-le+ol#','-le+ul#','-leadingreins+reins','-lemen#','-ll#-ot+t','-lunch','-m+i#-ot+t','-m+t#','-ma#','-magazine','-maker#','-maniac','-matography','-meter','-mime','-monger','-motor','-mum','-n#','-n#-corundum+rundum','-nasium','-nation#-inflation+flation','-nent#','-ner','-nstration','-o#','-o##','-oad+ead#','-oanalyse#','-ock#','-of','-of#','-of+d#','-off','-off#','-og','-ography','-oia#','-oid#','-oil','-oin+unct#','-oisleather+m#','-oitre+aiss#','-ol+l#','-olate','-olate#','-old+eld##','-omrade+amarad#','-on','-on#','-on+ti#','-onamide+a','-onate','-ong+eng#','-onia#','-ooth+eethe','-ope+ap#','-ophrenia#','-or#','-or#-hotel+el','-or+r#','-orary','-oratory','-ortable#','-orus#','-ory#','-os#','-ose#','-ose+s#','-ose+uzz#','-ounce+unci#','-ound+und#','-our+or#','-ous#','-ous+eg#','-ous+os#','-out+ut#','-overnment#','-overnor+uv','-ow#','-oy+uct#','-path','-pea','-pen','-pere#','-pet#','-phonic','-piano','-point','-pointpen+pen','-pore','-pperclass','-procuratorfiscal+fiscal','-pronoun','-que+c#','-r#','-r#-country','-r+n#','-r+t#','-randum','-raphone#','-rdinarylevel+level','-re+s#','-ree+ir#','-refrigerator+fridge','-rication','-rigine','-rmation','-ry#','-ry##','-ry+er#','-s','-s#','-s#-y+ie#','-s+e#','-s+k#','-s+l#','-s+rul#','-s+t#','-sband+bb#','-school','-scope','-se#','-se+c#','-se+ce','-se+n#','-se+t#','-se+ti#','-se+z#','-section','-sexual','-sh+c#','-sh+t#','-shall+ll','-shipman+d#','-sia+t#','-sin+t#','-sis+t#','-sistor+n#','-sition','-skyist','-sole#','-soprano','-ss+z#','-ssiere','-stone','-stroke','-sun','-sy+t#','-t#','-t#-to+na','-t+d#','-t+n#','-t+s#','-t+ss#','-tacles+s','-te#','-telephone+phone','-tense','-ter','-ter+s#','-terrier','-th#','-th##','-the+s#-e','-them+em','-therapist','-tic#','-tical#','-tide','-tingroom','-tion+k#-rumpus+us','-tive#-electron+tron','-to','-to#','-tobacco','-tombomb+bomb','-tor','-tralian+s#','-troops+s','-tto+s#','-turboprop+prop#','-ty#','-ty+st#','-uary#','-uate','-ucational','-ue#','-ular','-ulary','-ulate','-ulation','-uli','-um#','-umn+onn#','-unist#','-unition+o','-up#','-up+m#','-ur#','-ur+or#','-ur+r#','-ure#','-ure+or#','-uroys+s','-urteen+rt#','-ury+ri#','-us','-us#','-us##','-us+e#','-us+i#','-us+os#','-us+s#','-usiness+iz','-utation','-ute+aut#','-uth','-val','-ve#','-ve+b#','-ve+f','-ve+f#','-ve+ff','-ve+of','-ve+p#','-vein','-veon#','-verb','-vertisement','-vict','-voice','-w+v#','-wall#','-wave','-will+ll','-winds+s','-with','-with#','-woman','-would+d','-x+c#','-x+ct#','-x+g#','-x+ge#','-x+go#','-xy+ct#','-y#','-y#-worth+orth','-y#-y+i#','-y##','-y+act#','-y+di#','-y+et#','-y+eut#','-y+i#','-y+i##','-y+iac#','-y+iast#','-y+ic#','-y+ie#','-y+ix#','-y+j#','-y+t#','-yclub+i#','-ydrogenbomb+bomb','-ylatedspirits+s','-yon+i#','-yse#','-ysis#','#','#-a#','#-adam','#-am+m','#-am+rm','#-analyse+alyse','#-ant#','#-ar#','#-are+re','#-ase+ss#','#-be+p#','#-beneath+neath','#-ber+er#','#-bicycle+cycle','#-broadcast+cast','#-bulldozer+dozer','#-catamaran+maran','#-cavalcade+cade','#-conception+ception','#-confound+found','#-consecrate+secrate','#-did+d','#-does+s','#-e','#-e#','#-e+in#','#-edge+age','#-electron+tron','#-eller','#-en+in#','#-enforce+inforce','#-estimate+timate','#-execute+cute','#-f+ve','#-for','#-ge+se','#-had+d','#-has+s','#-have+ve','#-hijack+jack','#-ic#','#-idolatry+olatry','#-ile#','#-inflate+flate','#-ion#','#-is+s','#-k+c#','#-kangaroo+aroo','#-l','#-l+n#','#-le#','#-lfpenny+penny','#-n','#-not+t','#-o+a','#-of+a','#-ology+ogy','#-on','#-ork+urc#','#-ot+t','#-our+or#','#-ous#','#-s#','#-shall+ll','#-t','#-to','#-um#','#-ur+r#','#-us+s','#-utic+ic#','#-ution','#-will+ll','#-would+d','#-y#','#-y##','#-y+i#','##','##-ed+d','###','#+b#','#+d','#+e','#+g#','#+l#','#+m#','#+n#','#+o#','#+p#','#+r#','#+s','#+t#','+a#','+ac#','+al#','+an#','+at#','+b#','+b##','+c#','+d#','+e','+e#','+en#','+er#','+f#','+g#','+g##','+i#','+il#','+in#','+ion#','+is#','+ist#','+it#','+k#','+l','+l#','+le#','+m','+m#','+m##','+mat#','+n','+n#','+ni#','+o#','+od#','+p','+p#','+p#-of+a','+p##','+p##+p#','+per#','+r#','+ri#','+s#','+sim#','+t','+t#','+t##','+to#','+u#','+ul#','+v#','+y#','+z#') NOT NULL"),
             Column(self.morphlemma_imminfix, "ENUM('','N','Y') NOT NULL"),
             Column(self.morphlemma_immrevers, "ENUM('','N','Y') NOT NULL"),
             Column(self.morphlemma_flatsa, "ENUM('','AA','AAA','AAAA','AAAAA','AAAF','AAAS','AAASA','AAASS','AAF','AAFA','AAS','AASA','AASAA','AASAAA','AASSA','AF','AFA','AFS','AFSA','AS','ASA','ASAA','ASAAA','ASAAAA','ASAAAAA','ASAAS','ASAS','ASASA','ASASAA','ASF','ASS','ASSA','ASSAA','ASSAAA','ASSS','F','FA','FAA','FAAS','FAF','FAFA','FAS','FF','FFA','FS','FSA','FSAA','FSAS','FSS','FSSA','S','SA','SAA','SAAA','SAAAA','SAAAAA','SAAAF','SAAAS','SAAASA','SAAF','SAAS','SAASA','SAASAA','SAASS','SAF','SAS','SASA','SASAA','SASS','SF','SFA','SFF','SFS','SFSA','SS','SSA','SSAA','SSAS','SSASA','SSASF','SSASS','SSF','SSFS','SSS','SSSA','SSSS') NOT NULL"),
             Column(self.morphlemma_struclab, "VARCHAR(111) NOT NULL"),
             Column(self.morphlemma_strucallo, "ENUM('','B','BC','C','CD','D','F','N','Z') NOT NULL"),
             Column(self.morphlemma_strucsubst, "ENUM('','N','Y') NOT NULL"),
             Column(self.morphlemma_strucopac, "ENUM('','N','Y') NOT NULL")])

        self.create_table_description(self.morphword_table,
            [Primary(self.morphword_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.morphword_label, "VARCHAR(35) NOT NULL"),
             Column(self.morphword_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.morphword_flecttype, "ENUM('a1S','a1Sr','a2S','a2Sr','a3S','a3Sr','aP','aPr','b','c','e1S','e2S','e2Sr','e3S','e3Sr','eP','i','P','pa','par','pe','Pr','S','X') NOT NULL"),
             Column(self.morphword_transinfl, "ENUM('','@','@ @','@ @ @','@ @ @ @','@ @ @ @ @','@ @ @ @ @+s','@ @ @ @-y+ies','@ @ @ @+es','@ @ @ @+s','@ @ @-y+ies','@ @ @+ed','@ @ @+es','@ @ @+ing','@ @ @+s','@ @-e+ing','@ @-f+ves','@ @-fe+ves','@ @-y+ied','@ @-y+ier','@ @-y+ies','@ @-y+iest','@ @+bed','@ @+bing','@ @+d','@ @+ed','@ @+es','@ @+ged','@ @+ging','@ @+ing','@ @+led','@ @+ling','@ @+ped','@ @+ping','@ @+red','@ @+ring','@ @+s','@ @+ted','@ @+ting','@-e+ing','@-e+ing @','@-e+ing @ @','@-ey+ier','@-ey+iest','@-f+ves','@-fe+ves','@-y+ied','@-y+ied @','@-y+ied @ @','@-y+ier','@-y+ier @','@-y+ies','@-y+ies @','@-y+ies @ @','@-y+ies @ @ @','@-y+iest','@-y+iest @','@+@d','@+@ing','@+@s','@+bed','@+bed @','@+bed @ @','@+ber','@+best','@+bing','@+bing @','@+bing @ @','@+d','@+d @','@+d @ @','@+ded','@+ded @','@+der','@+dest','@+ding','@+ding @','@+ed','@+ed @','@+ed @ @','@+ed @ @ @','@+er','@+er @','@+er @ @','@+es','@+es @','@+es @ @','@+es @ @ @','@+est','@+est @','@+ged','@+ged @','@+ged @ @','@+ger','@+gest','@+ging','@+ging @','@+ging @ @','@+ing','@+ing @','@+ing @ @','@+ing @ @ @','@+ked','@+ked @','@+king','@+king @','@+led','@+led @','@+ler','@+lest','@+ling','@+ling @','@+med','@+med @','@+mer','@+mest','@+ming','@+ming @','@+ned','@+ned @','@+ner','@+ner @','@+nest','@+nest @','@+ning','@+ning @','@+ning @ @','@+ped','@+ped @','@+ped @ @','@+ping','@+ping @','@+ping @ @','@+r','@+r @','@+red','@+red @','@+ring','@+ring @','@+s','@+s @','@+s @ @','@+s @ @ @','@+sed','@+sed @','@+ses','@+ses @','@+sing','@+sing @','@+st','@+st @','@+ted','@+ted @','@+ted @ @','@+ter','@+ter @','@+test','@+test @','@+ting','@+ting @','@+ting @ @','@+ved','@+ved @','@+ving','@+ving @','@+zed','@+zes','@+zing','IRR') NOT NULL")])

        self.create_table_description(self.syntaxlemma_table,
            [Primary(self.syntaxlemma_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.syntaxlemma_label, "VARCHAR(34) NOT NULL"),
             Column(self.syntaxlemma_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.syntaxlemma_classnum, "ENUM('1','10','11','12','13','14','15','2','3','4','5','6','7','8','9') NOT NULL"),
             Column(self.syntaxlemma_c_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_unc_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_sing_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_plu_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_grc_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_grunc_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_attr_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_postpos_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_voc_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_proper_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_exp_n, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_trans_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_transcomp_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_intrans_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_ditrans_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_link_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_phr_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_prep_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_phrprep_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_exp_v, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_ord_a, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_attr_a, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_pred_a, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_postpos_a, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_exp_a, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_ord_adv, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_pred_adv, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_postpos_adv, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_comb_adv, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_exp_adv, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_card_num, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_ord_num, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_exp_num, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_pers_pron, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_dem_pron, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_poss_pron, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_refl_pron, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_wh_pron, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_det_pron, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_pron_pron, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_exp_pron, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_cor_c, "ENUM('N','Y') NOT NULL"),
             Column(self.syntaxlemma_sub_c, "ENUM('N','Y') NOT NULL")])

        self.create_table_description(self.lemma_table,
            [Primary(self.lemma_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.lemma_label, "VARCHAR(34) NOT NULL"),
             Column(self.lemma_headdia, "VARCHAR(34) NOT NULL"),
             Column(self.lemma_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.lemma_orthocnt, "ENUM('1','2','3','4','5') NOT NULL"),
             Column(self.lemma_orthostatus, "ENUM('B') NOT NULL"),
             Column(self.lemma_cobspellfreq, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.lemma_cobspelldev, "MEDIUMINT(5) UNSIGNED NOT NULL"),
             Column(self.lemma_headsyldia, "VARCHAR(42) NOT NULL")])

        self.create_table_description(self.word_table,
            [Primary(self.word_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Link(self.word_phonoword_id, self.phonoword_table),
             Link(self.word_morphword_id, self.morphword_table),
             Column(self.word_label, "VARCHAR(35) NOT NULL"),
             Column(self.word_worddia, "VARCHAR(35) NOT NULL"),
             Column(self.word_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Link(self.word_lemma_id, self.lemma_table),
             Link(self.word_phonolemma_id, self.phonolemma_table),
             Link(self.word_morphlemma_id, self.morphlemma_table),
             Link(self.word_syntaxlemma_id, self.syntaxlemma_table),
             Column(self.word_orthocnt, "ENUM('1','2','3','4','5') NOT NULL"),
             Column(self.word_orthostatus, "ENUM('B') NOT NULL"),
             Column(self.word_cobspellfreq, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.word_cobspelldev, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.word_wordsyldia, "VARCHAR(43) NOT NULL")])

    def build_load_files(self):
        files = [x for x in sorted(self.get_file_list(self.arguments.path, self.file_filter)) if os.path.basename(x).lower() in BuilderClass.expected_files]
        if self._widget:
            self._widget.progressSet.emit(len(files), "")
            self._widget.progressUpdate.emit(0)

        for i, file_name in enumerate(files):
            component = file_name.lower()[-6:-3]

            if component == "epw":
                s = "Phonology word forms"
            elif component == "epl":
                s = "Phonology lemmas"
            elif component == "emw":
                s = "Morphology word forms"
            elif component == "eml":
                s = "Morphology lemmas"
            elif component == "eow":
                s = "Orthography word forms"
            elif component == "eol":
                s = "Orthography lemmas"
            elif component == "esl":
                s = "Syntax word forms"
            else:
                component = None

            if self._widget:
                self._widget.progressUpdate.emit(i)
                
            if component:
                if self._widget:
                    self._widget.labelSet.emit("Loading from {}.cd: {}".format(component, s))

                with open(file_name, "r") as input_file:
                    content = input_file.readlines()

                for i, current_line in enumerate(content):
                    if self.interrupted:
                        return
                    current_line = current_line.strip()
                    columns = current_line.split("\\")
                    if component == "eow":
                        (self._value_word_id,
                        self._value_word_worddia,
                        self._value_word_cob,
                        self._value_word_lemma_id,
                        self._value_word_orthocnt,
                        self._value_word_orthostatus,
                        self._value_word_cobspellfreq,
                        self._value_word_cobspelldev,
                        self._value_word_wordsyldia) = columns[:9]
                        self._value_word_label = dia_to_unicode(self._value_word_worddia)
                        self.table(self.word_table).add(
                            {self.word_id: self._value_word_id,
                            self.word_label: self._value_word_label,
                            self.word_worddia: self._value_word_worddia,
                            self.word_cob: self._value_word_cob,
                            self.word_lemma_id: self._value_word_lemma_id,
                            self.word_orthocnt: self._value_word_orthocnt,
                            self.word_orthostatus: self._value_word_orthostatus,
                            self.word_cobspellfreq: self._value_word_cobspellfreq,
                            self.word_cobspelldev: self._value_word_cobspelldev,
                            self.word_wordsyldia: self._value_word_wordsyldia})
                    elif component == "eol":
                        (self._value_lemma_id,
                        self._value_lemma_headdia,
                        self._value_lemma_cob,
                        self._value_lemma_orthocnt,
                        self._value_lemma_orthostatus,
                        self._value_lemma_cobspellfreq,
                        self._value_lemma_cobspelldev,
                        self._value_lemma_headsyldia) = columns[:8]
                        self._value_lemma_label = dia_to_unicode(self._value_lemma_headdia)
                        
                        self.table(self.lemma_table).add(
                            {self.lemma_id: self._value_lemma_id,
                            self.lemma_label: self._value_lemma_label,
                            self.lemma_headdia: self._value_lemma_headdia,
                            self.lemma_cob: self._value_lemma_cob,
                            self.lemma_orthocnt: self._value_lemma_orthocnt,
                            self.lemma_orthostatus: self._value_lemma_orthostatus,
                            self.lemma_cobspellfreq: self._value_lemma_cobspellfreq,
                            self.lemma_cobspelldev: self._value_lemma_cobspelldev,
                            self.lemma_headsyldia: self._value_lemma_headsyldia})
                    
                    elif component == "epw":
                        (self._value_phonoword_id, 
                        self._value_phonoword_label,
                        self._value_phonoword_cob,
                        _, 
                        self._value_phonoword_proncnt,
                        _,
                        self._value_phonoword_phonstrsdisc,
                        self._value_phonoword_phoncvbr,
                        self._value_phonoword_phonsylbclx) = columns[:9]

                        self.table(self.phonoword_table).add(
                            {self.phonoword_id: self._value_phonoword_id,
                            self.phonoword_label: self._value_phonoword_label,
                            self.phonoword_cob: self._value_phonoword_cob,
                            self.phonoword_proncnt: self._value_phonoword_proncnt,
                            self.phonoword_phonstrsdisc: self._value_phonoword_phonstrsdisc,
                            self.phonoword_phoncvbr: self._value_phonoword_phoncvbr,
                            self.phonoword_phonsylbclx: self._value_phonoword_phonsylbclx})
                    
                    elif component == "epl":
                        (self._value_phonolemma_id, 
                        self._value_phonolemma_label,
                        self._value_phonolemma_cob,
                        self._value_phonolemma_proncnt,
                        _,
                        self._value_phonolemma_phonstrsdisc,
                        self._value_phonolemma_phoncvbr,
                        self._value_phonolemma_phonsylbclx) = columns[:8]

                        self.table(self.phonolemma_table).add(
                            {self.phonolemma_id: self._value_phonolemma_id,
                            self.phonolemma_label: self._value_phonolemma_label,
                            self.phonolemma_cob: self._value_phonolemma_cob,
                            self.phonolemma_proncnt: self._value_phonolemma_proncnt,
                            self.phonolemma_phonstrsdisc: self._value_phonolemma_phonstrsdisc,
                            self.phonolemma_phoncvbr: self._value_phonolemma_phoncvbr,
                            self.phonolemma_phonsylbclx: self._value_phonolemma_phonsylbclx})
                    
                    elif component == "emw":
                        (self._value_morphword_id,
                        self._value_morphword_label,
                        self._value_morphword_cob,
                        _,
                        self._value_morphword_flecttype,
                        self._value_morphword_transinfl) = columns[:6]

                        self.table(self.morphword_table).add(
                            {self.morphword_id: self._value_morphword_id,
                            self.morphword_label: self._value_morphword_label,
                            self.morphword_cob: self._value_morphword_cob,
                            self.morphword_flecttype: self._value_morphword_flecttype,
                            self.morphword_transinfl: self._value_morphword_transinfl})
                    
                    elif component == "eml":
                        (self._value_morphlemma_id,
                        self._value_morphlemma_label,
                        self._value_morphlemma_cob,
                        self._value_morphlemma_morphstatus,
                        self._value_morphlemma_lang,
                        self._value_morphlemma_morphcnt,
                        self._value_morphlemma_nvaffcomp,
                        self._value_morphlemma_der,
                        self._value_morphlemma_comp,
                        self._value_morphlemma_dercomp,
                        self._value_morphlemma_def,
                        self._value_morphlemma_imm,
                        self._value_morphlemma_immsubcat,
                        self._value_morphlemma_immsa,
                        self._value_morphlemma_immallo,
                        self._value_morphlemma_immsubst,
                        self._value_morphlemma_immopac,
                        self._value_morphlemma_transder,
                        self._value_morphlemma_imminfix,
                        self._value_morphlemma_immrevers,
                        self._value_morphlemma_flatsa,
                        self._value_morphlemma_struclab,
                        self._value_morphlemma_strucallo,
                        self._value_morphlemma_strucsubst,
                        self._value_morphlemma_strucopac) = columns[:25]

                        self.table(self.morphlemma_table).add(
                            {self.morphlemma_id: self._value_morphlemma_id,
                            self.morphlemma_label: self._value_morphlemma_label,
                            self.morphlemma_cob: self._value_morphlemma_cob,
                            self.morphlemma_morphstatus: self._value_morphlemma_morphstatus,
                            self.morphlemma_lang: self._value_morphlemma_lang,
                            self.morphlemma_morphcnt: self._value_morphlemma_morphcnt,
                            self.morphlemma_nvaffcomp: self._value_morphlemma_nvaffcomp,
                            self.morphlemma_der: self._value_morphlemma_der,
                            self.morphlemma_comp: self._value_morphlemma_comp,
                            self.morphlemma_dercomp: self._value_morphlemma_dercomp,
                            self.morphlemma_def: self._value_morphlemma_def,
                            self.morphlemma_imm: self._value_morphlemma_imm,
                            self.morphlemma_immsubcat: self._value_morphlemma_immsubcat,
                            self.morphlemma_immsa: self._value_morphlemma_immsa,
                            self.morphlemma_immallo: self._value_morphlemma_immallo,
                            self.morphlemma_immsubst: self._value_morphlemma_immsubst,
                            self.morphlemma_immopac: self._value_morphlemma_immopac,
                            self.morphlemma_transder: self._value_morphlemma_transder,
                            self.morphlemma_imminfix: self._value_morphlemma_imminfix,
                            self.morphlemma_immrevers: self._value_morphlemma_immrevers,
                            self.morphlemma_flatsa: self._value_morphlemma_flatsa,
                            self.morphlemma_struclab: self._value_morphlemma_struclab,
                            self.morphlemma_strucallo: self._value_morphlemma_strucallo,
                            self.morphlemma_strucsubst: self._value_morphlemma_strucsubst,
                            self.morphlemma_strucopac: self._value_morphlemma_strucopac})

                    elif component == "esl":
                        (self._value_syntaxlemma_id,                          
                        self._value_syntaxlemma_label,                        
                        self._value_syntaxlemma_cob,                          
                        self._value_syntaxlemma_classnum,                     
                        self._value_syntaxlemma_c_n,                          
                        self._value_syntaxlemma_unc_n,                        
                        self._value_syntaxlemma_sing_n,                       
                        self._value_syntaxlemma_plu_n,                        
                        self._value_syntaxlemma_grc_n,                        
                        self._value_syntaxlemma_grunc_n,                      
                        self._value_syntaxlemma_attr_n,                       
                        self._value_syntaxlemma_postpos_n,                    
                        self._value_syntaxlemma_voc_n,                        
                        self._value_syntaxlemma_proper_n,                     
                        self._value_syntaxlemma_exp_n,                        
                        self._value_syntaxlemma_trans_v,                      
                        self._value_syntaxlemma_transcomp_v,                  
                        self._value_syntaxlemma_intrans_v,                    
                        self._value_syntaxlemma_ditrans_v,                    
                        self._value_syntaxlemma_link_v,                       
                        self._value_syntaxlemma_phr_v,                        
                        self._value_syntaxlemma_prep_v,                       
                        self._value_syntaxlemma_phrprep_v,                    
                        self._value_syntaxlemma_exp_v,                        
                        self._value_syntaxlemma_ord_a,                        
                        self._value_syntaxlemma_attr_a,                       
                        self._value_syntaxlemma_pred_a,                       
                        self._value_syntaxlemma_postpos_a,                    
                        self._value_syntaxlemma_exp_a,                        
                        self._value_syntaxlemma_ord_adv,                      
                        self._value_syntaxlemma_pred_adv,                     
                        self._value_syntaxlemma_postpos_adv,                  
                        self._value_syntaxlemma_comb_adv,                     
                        self._value_syntaxlemma_exp_adv,                      
                        self._value_syntaxlemma_card_num,                     
                        self._value_syntaxlemma_ord_num,                      
                        self._value_syntaxlemma_exp_num,                      
                        self._value_syntaxlemma_pers_pron,                    
                        self._value_syntaxlemma_dem_pron,                     
                        self._value_syntaxlemma_poss_pron,                    
                        self._value_syntaxlemma_refl_pron,                    
                        self._value_syntaxlemma_wh_pron,                      
                        self._value_syntaxlemma_det_pron,                     
                        self._value_syntaxlemma_pron_pron,                    
                        self._value_syntaxlemma_exp_pron,                     
                        self._value_syntaxlemma_cor_c,
                        self._value_syntaxlemma_sub_c) = columns[:47]         
                        self.table(self.syntaxlemma_table).add(               
                            {self.syntaxlemma_id: self._value_syntaxlemma_id, 
                            self.syntaxlemma_label: self._value_syntaxlemma_label, 
                            self.syntaxlemma_cob: self._value_syntaxlemma_cob, 
                            self.syntaxlemma_classnum: self._value_syntaxlemma_classnum, 
                            self.syntaxlemma_c_n: self._value_syntaxlemma_c_n, 
                            self.syntaxlemma_unc_n: self._value_syntaxlemma_unc_n, 
                            self.syntaxlemma_sing_n: self._value_syntaxlemma_sing_n, 
                            self.syntaxlemma_plu_n: self._value_syntaxlemma_plu_n, 
                            self.syntaxlemma_grc_n: self._value_syntaxlemma_grc_n, 
                            self.syntaxlemma_grunc_n: self._value_syntaxlemma_grunc_n, 
                            self.syntaxlemma_attr_n: self._value_syntaxlemma_attr_n, 
                            self.syntaxlemma_postpos_n: self._value_syntaxlemma_postpos_n, 
                            self.syntaxlemma_voc_n: self._value_syntaxlemma_voc_n, 
                            self.syntaxlemma_proper_n: self._value_syntaxlemma_proper_n, 
                            self.syntaxlemma_exp_n: self._value_syntaxlemma_exp_n, 
                            self.syntaxlemma_trans_v: self._value_syntaxlemma_trans_v, 
                            self.syntaxlemma_transcomp_v: self._value_syntaxlemma_transcomp_v, 
                            self.syntaxlemma_intrans_v: self._value_syntaxlemma_intrans_v, 
                            self.syntaxlemma_ditrans_v: self._value_syntaxlemma_ditrans_v, 
                            self.syntaxlemma_link_v: self._value_syntaxlemma_link_v, 
                            self.syntaxlemma_phr_v: self._value_syntaxlemma_phr_v, 
                            self.syntaxlemma_prep_v: self._value_syntaxlemma_prep_v, 
                            self.syntaxlemma_phrprep_v: self._value_syntaxlemma_phrprep_v, 
                            self.syntaxlemma_exp_v: self._value_syntaxlemma_exp_v, 
                            self.syntaxlemma_ord_a: self._value_syntaxlemma_ord_a, 
                            self.syntaxlemma_attr_a: self._value_syntaxlemma_attr_a, 
                            self.syntaxlemma_pred_a: self._value_syntaxlemma_pred_a, 
                            self.syntaxlemma_postpos_a: self._value_syntaxlemma_postpos_a, 
                            self.syntaxlemma_exp_a: self._value_syntaxlemma_exp_a, 
                            self.syntaxlemma_ord_adv: self._value_syntaxlemma_ord_adv, 
                            self.syntaxlemma_pred_adv: self._value_syntaxlemma_pred_adv, 
                            self.syntaxlemma_postpos_adv: self._value_syntaxlemma_postpos_adv, 
                            self.syntaxlemma_comb_adv: self._value_syntaxlemma_comb_adv, 
                            self.syntaxlemma_exp_adv: self._value_syntaxlemma_exp_adv, 
                            self.syntaxlemma_card_num: self._value_syntaxlemma_card_num, 
                            self.syntaxlemma_ord_num: self._value_syntaxlemma_ord_num, 
                            self.syntaxlemma_exp_num: self._value_syntaxlemma_exp_num, 
                            self.syntaxlemma_pers_pron: self._value_syntaxlemma_pers_pron, 
                            self.syntaxlemma_dem_pron: self._value_syntaxlemma_dem_pron, 
                            self.syntaxlemma_poss_pron: self._value_syntaxlemma_poss_pron, 
                            self.syntaxlemma_refl_pron: self._value_syntaxlemma_refl_pron, 
                            self.syntaxlemma_wh_pron: self._value_syntaxlemma_wh_pron, 
                            self.syntaxlemma_det_pron: self._value_syntaxlemma_det_pron, 
                            self.syntaxlemma_pron_pron: self._value_syntaxlemma_pron_pron, 
                            self.syntaxlemma_exp_pron: self._value_syntaxlemma_exp_pron, 
                            self.syntaxlemma_cor_c: self._value_syntaxlemma_cor_c,
                            self.syntaxlemma_sub_c: self._value_syntaxlemma_sub_c,
                            })
                self.commit_data()

    @staticmethod
    def get_title():
        return "CELEX2 Lexical Database (English)"

    @staticmethod
    def get_url():
        return 'https://catalog.ldc.upenn.edu/LDC96L14'
    
    @staticmethod
    def get_name():
        return "CELEX2"
    
    @staticmethod
    def get_db_name():
        return "celex"
    
    @staticmethod
    def get_references():
        return ["Baayen, R, R Piepenbrock, and L Gulikers. 1995. <i>CELEX2 LDC96L14</i>. Web Download. Philadelphia: Linguistic Data Consortium."]

    @staticmethod
    def get_license():
        return "The CELEX Lexical Database is released under the terms of the <a href='https://catalog.ldc.upenn.edu/license/celex-user-agreement.pdf'>CELEX 2 User Agreement</a>."
    
    @staticmethod
    def get_description():
        return ["The CELEX lexical database for English contains detailed information for XXX lemmas (about 100,000 inflected forms) on:",
                """<ul><li>orthography (variations in spelling [not supported by Coquery], hyphenation)</li>
                <li>phonology (phonetic transcriptions, variations in pronunciation [not supported by Coquery], syllable structure, primary stress)</li>
                <li>morphology (derivational and compositional structure, inflectional paradigms)</li>
                <li>syntax (word class, word class-specific subcategorizations, argument structures)</li>
                <li>word frequency (summed word and lemma counts, based on representative text corpora)</li></ul>"""]

if __name__ == "__main__":
    BuilderClass().build()
    
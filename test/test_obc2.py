# -*- coding: utf-8 -*-
"""
This module tests the OBC2 installer module.

Run it like so:

coquery$ python -m test.test_obc2

"""

from __future__ import unicode_literals

import os
import shutil
import tempfile
import argparse

from coquery.coquery import options
from coquery.installer.coq_install_obc2 import BuilderClass
from test.testcase import CoqTestCase, run_tests


mock_17300116 = """
<?xml version="1.0" encoding="UTF-8"?>
<TEI.2>
    <text>
        <body>
            <div0 id="17300116" type="sessionsPaper">
                <interp inst="17300116" type="year" value="1730" />
                <interp inst="17300116" type="date" value="17300116" />
                <div1 id="t17300116-1" type="trialAccount" n="1">
                    <interp inst="t17300116-1" type="uri" value="sessionsPapers/19130304" />
                    <interp inst="t17300116-1" type="date" value="17300116" />
                    <p>
                        <u age="" editor="Delecombe Roome" event="19130304-1" n="1" printer="The Argus Printing Company" publisher="George Walpole" role="Witness" scribe="George Walpole " sex="m" speaker="19130304-0011" trial="t19130304-8" year="1913" class="" wc="183" p2="1817-1913" p3="1850-1913" p4="1866-1913" p5="1876-1913" hisclass="" hiscoCode="" hiscoLabel="" nTrial="1" p6="1882-1913">
                            On_II February_NPM1 13_MC I_PPIS1 saw_VVD prisoner_NN1 go_VVI to_II Customs_NN2 Station_NN1 Post_NN1 Office_NN1 ._. He_PPHS1 handed_VVD the_AT clerk_NN1 the_AT book_NN1
                            <activity />
                            ,_, the_AT clerk_NN1 gave_VVD him_PPHO1 the_AT warrant_NN1
                            <activity />
                            ;_; this_DD1 he_PPHS1 filled_VVD up_RP and_CC signed_VVD ,_, also_RR the_AT receipt_NN1 form_NN1
                            <activity />
                            ,_, purporting_VVG to_TO be_VBI signed_VVN by_II Richard_NP1 Vickers_NP1 ,_, T._NP1 Gell_NP1 ,_, and_CC A._NP1 Gell_NP1 ._. I_PPIS1 asked_VVD him_PPHO1 to_TO go_VVI with_IW me_PPIO1 to_II the_AT General_JJ Post_NN1 Office_NN1 and_CC he_PPHS1 did_VDD so_RR ._. There_RL ,_, after_CS the_AT usual_JJ caution_NN1 ,_, he_PPHS1 said_VVD he_PPHS1 had_VHD nothing_PN1 to_TO say_VVI ._. Later_RRR he_PPHS1 said_VVD ,_, "_" I_PPIS1 did_VDD sign_VVI the_AT warrant_NN1 ;_; the_AT money_NN1 is_VBZ wanted_VVN to_TO pay_VVI the_AT lodge_NN1 dues_NN2 at_II the_AT chief_JJ office_NN1 ;_; the_AT two_MC trustees_NN2 ,_, T._NP1 and_CC A._NP1 Gell_NP1 ,_, whose_DDQGE names_NN2 I_PPIS1 signed_VVD ,_, have_VH0 resigned_VVN ,_, and_CC their_APPGE two_MC successors_NN2 have_VH0 not_XX yet_RR received_VVN their_APPGE papers_NN2 to_TO sign_VVI as_CSA trustees_NN2 ._. "_" At_II the_AT end_NN1 of_IO January_NPM1 a_AT1 notice_NN1 of_IO withdrawal_NN1 had_VHD been_VBN sent_VVN ,_, and_CC was_VBDZ returned_VVN by_II the_AT department_NN1 on_II the_AT ground_NN1 that_CST it_PPH1 did_VDD not_XX bear_VVI the_AT signatures_NN2 of_IO all_DB the_AT trustees_NN2 ._. Prisoner_NN1 wrote_VVD on_II February_NPM1 1_MC1 stating_VVG that_CST another_DD1 member_NN1 of_IO the_AT society_NN1 had_VHD signed_VVN for_IF A._NP1 Gell_NP1 ,_, as_CSA he_PPHS1 was_VBDZ not_XX available_JJ ,_, so_CS21 that_CS22 there_EX might_VM be_VBI no_AT delay_NN1 ._.
                        </u>
                    </p>
                </div1>
            </div0>
        </body>
    </text
</TEI.2>
"""


mock_contents = {"OBC2POS-17300116.xml": mock_17300116}


class TestOBC2(CoqTestCase):
    def setUp(self):
        self._temp_path = tempfile.mkdtemp()
        for file_name in BuilderClass.expected_files:
            with open(os.path.join(self._temp_path, file_name), "w") as f:
                f.write(mock_contents.get(file_name, ""))

        options.cfg = argparse.Namespace()

    def tearDown(self):
        shutil.rmtree(self._temp_path)

    def assert_df_equal(self, df1, df2):
        self.assertListEqual(sorted(df1.columns), sorted(df2.columns))
        self.assertEqual(len(df1), len(df2))
        for col in df1.columns:
            l1 = df1[col].dropna().reset_index(drop=True).values.tolist()
            l2 = df2[col].dropna().reset_index(drop=True).values.tolist()
            check = (df1[col].reset_index(drop=True).isnull() ==
                     df2[col].reset_index(drop=True).isnull())

            try:
                self.assertTrue(check.all())
                self.assertListEqual(l1, l2)
            except Exception as e:
                e.args = tuple([x.replace("Lists", "Columns '{}'".format(col))
                                for x in e.args])
                raise e

    def test_get_file_list(self):
        installer = BuilderClass()
        lst = installer.get_file_list(self._temp_path, None)
        self.assertListEqual(
            sorted(lst),
            sorted([os.path.join(self._temp_path, x)
                    for x in BuilderClass.expected_files]))


provided_tests = [
    TestOBC2,
    ]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

"""
test_celex.py is part of Coquery.

Copyright (c) 2016-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery.installer.coq_install_celex import dia_to_unicode
from test.testcase import CoqTestCase, run_tests


class TestCELEX(CoqTestCase):
    def test_dia_to_unicode(self):
        self.assertEqual(dia_to_unicode("cause c#el`ebre"), "cause célèbre")
        self.assertEqual(dia_to_unicode("#eclat"), "éclat")
        self.assertEqual(dia_to_unicode("`a la"), "à la")
        self.assertEqual(dia_to_unicode('k"ummel'), "kümmel")
        self.assertEqual(dia_to_unicode('d#eb^acle'), "débâcle")
        self.assertEqual(dia_to_unicode('fa,cade'), "façade")
        self.assertEqual(dia_to_unicode('sm@aland'), "småland")


provided_tests = [TestCELEX]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

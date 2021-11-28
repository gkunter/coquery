# -*- coding: utf-8 -*-
"""
This module tests the package coq_install_ice_ng module.

Run it like so:

coquery$ python -m test.test_ice_ng

"""


from __future__ import unicode_literals

from coquery.installer.coq_install_ice_ng import BuilderClass
from test.testcase import CoqTestCase, run_tests


class TestIceNG(CoqTestCase):
    def test_replace(self):
        replace_func = BuilderClass._replace_encoding_errors

        pairs = [
            ("YarâAdua", "Yar’Adua"),
            ("-âEkidâ", "-‘Ekid’"),
            ("ÄkÃ­d", "ĕkíd"),
            ]

        for mangled, correct in pairs:
            self.assertEqual(replace_func(mangled), correct)


provided_tests = [TestIceNG]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

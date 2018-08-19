# -*- coding: utf-8 -*-
"""
testcase.py is part of Coquery.

Copyright (c) 2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import pandas as pd


class CoqTestCase(unittest.TestCase):
    def assertDictEqual(self, d1, d2):
        """
        This overrides assertDictEqual so that any Series or DataFrame value
        of the dictionaries is asserted using a Pandas test, and Numpy arrays
        are asserted using a Numpy test.
        """

        D1 = d1.copy()
        D2 = d2.copy()

        d_df1 = {}
        d_df2 = {}

        d_s1 = {}
        d_s2 = {}

        d_np1 = {}
        d_np2 = {}

        for key, val in d1.items():
            if isinstance(val, pd.Series):
                d_s1[key] = D1.pop(key)
            elif isinstance(val, pd.np.ndarray):
                d_np1[key] = D1.pop(key)
            elif isinstance(val, pd.DataFrame):
                d_df1[key] = D1.pop(key)

        for key, val in d2.items():
            if isinstance(val, pd.Series):
                d_s2[key] = D2.pop(key)
            elif isinstance(val, pd.np.ndarray):
                d_np2[key] = D2.pop(key)
            elif isinstance(val, pd.DataFrame):
                d_df2[key] = D2.pop(key)

        super(CoqTestCase, self).assertDictEqual(D1, D2)

        self.assertEqual(sorted(d_df1.keys()), sorted(d_df2.keys()))
        self.assertEqual(sorted(d_s1.keys()), sorted(d_s2.keys()))
        self.assertEqual(sorted(d_np1.keys()), sorted(d_np2.keys()))

        for key in d_s1.keys():
            pd.testing.assert_series_equal(d_s1[key], d_s2[key])

        for key in d_df1.keys():
            pd.testing.assert_frame_equal(d_df1[key], d_df2[key])

        for key in d_np1.keys():
            pd.np.testing.assert_array_almost_equal(d_np1[key], d_np2[key])

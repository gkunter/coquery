# -*- coding: utf-8 -*-
"""
testcase.py is part of Coquery.

Copyright (c) 2018-2021 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import tempfile
import pandas as pd


def tmp_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = tmp_dir
    return path


def tmp_filename():
    temp_file = tempfile.NamedTemporaryFile("w")
    temp_file.close()
    return temp_file.name


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

        d_i1 = {}
        d_i2 = {}

        d_np1 = {}
        d_np2 = {}

        map_dtypes = ((pd.Series, d_s1, d_s2),
                      (pd.Index, d_i1, d_i2),
                      (pd.np.ndarray, d_np1, d_np2),
                      (pd.DataFrame, d_df1, d_df2))

        for key, val in d1.items():
            for dtype, dct1, _ in map_dtypes:
                if isinstance(val, dtype):
                    dct1[key] = D1.pop(key)
                    break

        for key, val in d2.items():
            for dtype, _, dct2 in map_dtypes:
                if isinstance(val, dtype):
                    dct2[key] = D2.pop(key)
                    break

        super(CoqTestCase, self).assertDictEqual(D1, D2)

        try:
            self.assertEqual(sorted(d_df1.keys()), sorted(d_df2.keys()))
            self.assertEqual(sorted(d_s1.keys()), sorted(d_s2.keys()))
            self.assertEqual(sorted(d_i1.keys()), sorted(d_i2.keys()))
            self.assertEqual(sorted(d_np1.keys()), sorted(d_np2.keys()))

            for key in d_s1.keys():
                pd.testing.assert_series_equal(d_s1[key], d_s2[key])

            for key in d_i1.keys():
                pd.testing.assert_index_equal(d_i1[key], d_i2[key])

            for key in d_df1.keys():
                pd.testing.assert_frame_equal(d_df1[key], d_df2[key])

            for key in d_np1.keys():
                pd.np.testing.assert_array_almost_equal(d_np1[key], d_np2[key])
        except AssertionError:
            msg = "Dictionaries are different\n\nLeft:  {d1}\nRight: {d2}"
            raise AssertionError(msg.format(d1=d1, d2=d2))


def run_tests(test_list):
    """
    This function is used to call the test cases from the list `test_list`.

    It's supposed to be used by a test module inside of its main() function.
    """
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in test_list])
    unittest.TextTestRunner().run(suite)

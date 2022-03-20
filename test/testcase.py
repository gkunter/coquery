# -*- coding: utf-8 -*-
"""
testcase.py is part of Coquery.

Copyright (c) 2018-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import tempfile
import pandas as pd
import numpy as np


def tmp_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = tmp_dir
    return path


def tmp_filename():
    temp_file = tempfile.NamedTemporaryFile("w")
    temp_file.close()
    return temp_file.name


class CoqTestCase(unittest.TestCase):
    @staticmethod
    def get_default_df():
        np.random.seed(123)
        return pd.DataFrame({"X": list("AAAAAAAAAAAAAAAAAAABBBBBBBBBBB"),
                             "Y": list("xxxxxxxxyyyyyyyyyyyxxxxxxxyyyy"),
                             "Z": list("111122221111222211221122112222"),
                             "ID": sorted(np.random.choice(np.arange(1, 100),
                                                           30,
                                                           replace=False)),
                             "NUM": np.random.randint(0, 100, 30)})

    def assertDictEqual(self, d1, d2, **kwargs):
        """
        This overrides assertDictEqual so that any Series or DataFrame value
        of the dictionaries is asserted using a Pandas test, and Numpy arrays
        are asserted using a Numpy test.

        Parameters
        ----------
        d1 : dict
        d2 : dict
        **kwargs
        """

        test1 = d1.copy()
        test2 = d2.copy()

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
                      (np.ndarray, d_np1, d_np2),
                      (pd.DataFrame, d_df1, d_df2))

        for key, val in d1.items():
            for dtype, dct1, _ in map_dtypes:
                if isinstance(val, dtype):
                    dct1[key] = test1.pop(key)
                    break

        for key, val in d2.items():
            for dtype, _, dct2 in map_dtypes:
                if isinstance(val, dtype):
                    dct2[key] = test2.pop(key)
                    break

        super().assertDictEqual(test1, test2, **kwargs)

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
                np.testing.assert_array_almost_equal(d_np1[key], d_np2[key])
        except AssertionError:
            msg = f"Dictionaries are different\n\nLeft:  {d1}\nRight: {d2}"
            raise AssertionError(msg)


class CoqQtTestCase(CoqTestCase):
    """
    Adopted from https://stackoverflow.com/a/48128768/5215507 (user zalavari)
    """
    def setUp(self):
        from coquery.gui.pyqt_compat import QtWidgets

        self.app = (QtWidgets.QApplication.instance() or
                    QtWidgets.QApplication([]))

    def tearDown(self):
        del self.app

    def assertSignalReceived(self, signal, *args):
        return SignalReceiver(self, signal, *args)


class SignalReceiver(object):
    """
    Class that can be used to test whether a signal was correctly emitted.

    Adopted from https://stackoverflow.com/a/48128768/5215507 (user zalavari)
    """
    def __init__(self, test, signal, *args):
        self.actual_args = None
        self.expected_args = args
        self.test = test
        self.signal = signal
        self.called = False

    def slot(self, *args):
        self.actual_args = args
        self.called = True

    def __enter__(self):
        self.signal.connect(self.slot)

    def __exit__(self, e, msg, traceback):
        if e:
            raise e(msg)
        self.test.assertTrue(self.called, "Signal not called!")
        self.test.assertEqual(self.expected_args, self.actual_args, """Signal arguments don't match!
            actual:   {}
            expected: {}""".format(self.actual_args, self.expected_args))


def run_tests(test_list):
    """
    This function is used to call the test cases from the list `test_list`.

    It's supposed to be used in the main() function of a test module.
    """
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in test_list])
    unittest.TextTestRunner().run(suite)

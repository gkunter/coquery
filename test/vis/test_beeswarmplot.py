# -*- coding: utf-8 -*-
"""
This module tests the beeswarm plot visualizer module.

Run it like so:

coquery$ python -m test.vis.test_beeswarmplot

"""

import unittest
import matplotlib.pyplot as plt

from coquery.visualizer.beeswarmplot import BeeswarmPlot
from test.vis.test_barcodeplot import TestBarcodePlot


class TestBeeswarmPlot(TestBarcodePlot):
    """
    For test details, see TestBarCodePlot.
    """
    def setUp(self):
        super(TestBeeswarmPlot, self).setUp()
        self.vis = BeeswarmPlot(None, None, id_column=self.ID_COLUMN)


class TestBeeswarmPlotRandomized(TestBeeswarmPlot):
    def setUp(self):
        super(TestBeeswarmPlotRandomized, self).setUp()
        self.df = self.df.sample(frac=1).reset_index(drop=True)


provided_tests = (
    TestBeeswarmPlot,
    TestBeeswarmPlotRandomized,
    )


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

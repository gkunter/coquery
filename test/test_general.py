# -*- coding: utf-8 -*-
"""
This module tests the general.py module.

Run it like so:

coquery$ python -m test.test_general

"""

from __future__ import print_function
import sys
import os
import numpy as np

from coquery.general import (
    check_fs_case_sensitive, has_module, recycle,
    pretty, collapse_words, EnglishCollapser)
from test.testcase import CoqTestCase, run_tests


class TestGeneral(CoqTestCase):

    def test_check_fs_case_sensitive(self):
        if sys.platform == "linux":
            self.assertTrue(check_fs_case_sensitive(os.path.expanduser("~")))
        elif sys.platform in ("win32", "darwin"):
            self.assertFalse(check_fs_case_sensitive(os.path.expanduser("~")))
        else:
            raise NotImplementedError

    def test_has_module_1(self):
        self.assertFalse(has_module("a1b2c3d4e5f"[::-1]))
        self.assertTrue(has_module("os"))


class TestPretty(CoqTestCase):
    def assertListEqual(self, l1, l2):
        if (any([type(x) == object for x in l1]) or
                any([type(x) == object for x in l2])):
            return super(TestPretty, self).assertListEqual(l1, l2)
        else:
            if not np.allclose(l1, l2):
                raise self.failureException(
                    "Lists not equal enough:\n\t{}\n\t{}".format(l1, l2))
            return all(np.equal(l1, l2))

    def test_pretty_1(self):
        vrange = (0, 100)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [0, 20, 40, 60, 80])

    def test_pretty_1a(self):
        vrange = (5, 95)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [0, 20, 40, 60, 80])

    def test_pretty_2(self):
        vrange = (0, 100)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0, 25, 50, 75])

    def test_pretty_2a(self):
        vrange = (5, 95)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0, 25, 50, 75])

    def test_pretty_3(self):
        vrange = (0, 1000)
        bins = pretty(vrange, 10)
        self.assertListEqual(list(bins),
                             [0, 100, 200, 300, 400, 500, 600, 700, 800, 900])

    def test_pretty_3a(self):
        vrange = (5, 995)
        bins = pretty(vrange, 10)
        self.assertListEqual(list(bins),
                             [0, 100, 200, 300, 400, 500, 600, 700, 800, 900])

    def test_pretty_3b(self):
        vrange = (50, 950)
        bins = pretty(vrange, 10)
        self.assertListEqual(list(bins),
                             [0, 100, 200, 300, 400, 500, 600, 700, 800, 900])

    def test_pretty_4(self):
        vrange = (-200, 200)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [-200, -100, 0, 100])

    def test_pretty_4a(self):
        vrange = (-195, 195)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [-200, -100, 0, 100])

    def test_pretty_5(self):
        vrange = (-200, -100)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [-200, -175, -150, -125])

    def test_pretty_6(self):
        vrange = (100, 200)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [100, 125, 150, 175])

    def test_pretty_7(self):
        vrange = (0, 10)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [0, 2, 4, 6, 8])

    def test_pretty_8(self):
        vrange = (0, 10)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0, 2.5, 5, 7.5])

    def test_pretty_9(self):
        vrange = (0, 1)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0, 0.25, 0.5, 0.75])

    def test_pretty_10(self):
        vrange = (0.5, 1)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [0.5, 0.625, 0.75, 0.875])

    def test_pretty_10a(self):
        vrange = (0.05, 0.10)
        bins = pretty(vrange, 4)
        self.assertListEqual(bins,
                             [0.0, 0.025, 0.05, 0.075])

    def test_pretty_11(self):
        vrange = (0, 136)
        bins = pretty(vrange, 2)
        self.assertListEqual(list(bins),
                             [0, 75])

    def test_pretty_12(self):
        vrange = (13452, 32787)
        bins = pretty(vrange, 2)
        self.assertListEqual(list(bins),
                             [13400, 23400])

    def test_pretty_12a(self):
        vrange = (13452, 32787)
        bins = pretty(vrange, 4)
        self.assertListEqual(list(bins),
                             [13400, 18400, 23400, 28400])

    def test_pretty_13(self):
        vrange = (13452, 33061)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [13400, 17400, 21400, 25400, 29400])

    def test_pretty_14(self):
        vrange = (134528, 330612)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [134000, 174000, 214000, 254000, 294000])

    def test_pretty_15(self):
        vrange = (20033, 32399)
        bins = pretty(vrange, 5)
        self.assertListEqual(list(bins),
                             [20000, 23000, 26000, 29000, 32000])

    def test_pretty_16(self):
        vrange = (75, 136)
        bins = pretty(vrange, 7)
        self.assertListEqual(list(bins),
                             [70, 80, 90, 100, 110, 120, 130])


class TestRecycle(CoqTestCase):
    def test_recycle_1(self):
        """
        Test if the data is correctly recycled.
        """
        data = [0, 1, 2, 3, 4]
        target = data * 5
        requested_length = len(target)
        value = recycle(data, requested_length)
        self.assertListEqual(value, target)

    def test_recycle_2(self):
        """
        Test if recycling works when only the first two elements of the data
        are requested.
        """
        data = [0, 1, 2, 3, 4]
        target = [0, 1] * 5
        requested_data_length = 2
        requested_length = len(target)
        value = recycle(data, requested_length, requested_data_length)
        self.assertListEqual(value, target)

    def test_recycle_3(self):
        """
        Test if recycling works when there is more data than needed
        """
        data = [0, 1, 2, 3, 4]
        target = [0, 1]
        requested_data_length = len(data)
        requested_length = len(target)
        value = recycle(data, requested_length)
        self.assertListEqual(value, target)


class TestCollapseWords(CoqTestCase):
    def test_default_collapser1(self):
        lst = ["this", "is", "a", "test"]
        target = "this is a test"
        value = collapse_words(lst)
        self.assertEqual(target, value)

    def test_default_collapser2(self):
        lst = ["this", "is", "a", "test", ".", "go", "on", "."]
        target = "this is a test . go on ."
        value = collapse_words(lst)
        self.assertEqual(target, value)

    def test_empty(self):
        lst = [None] * 4
        target = None
        value = collapse_words(lst)
        self.assertEqual(target, value)


class TestEnglishCollapseWords(CoqTestCase):
    def test_punctuation_spacing_1(self):
        lst = ["this", "is", "a", "test", ",", "go", "on", "."]
        target = "this is a test, go on."
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_punctuation_spacing_2(self):
        lst = list("a.b,c:d;e!f?g%h+i-j)k]l}m—n")
        target = "a. b, c: d; e! f? g% h + i - j) k] l} m—n"
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_collapse_1(self):
        lst = ["this", "is", "a", "test", "."]
        target = "this is a test."
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_contractions_1(self):
        """
        Use U+0027 (APOSTROPHE) as the character marking contractions.
        """
        lst = ["I", "'ve", "I", "'m", "he", "'s", "hasn", "'t",
               "she", "'d", "you", "'re"]
        target = "I've I'm he's hasn't she'd you're"
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_contractions_2(self):
        """
        Use U+2019 (RIGHT SINGLE QUOTATION MARK) as the character marking
        contractions.
        """
        lst = ["I", "\U00002019ve", "I", "\U00002019m", "he", "\U00002019s",
               "hasn", "\U00002019t", "she", "\U00002019d",
               "you", "\U00002019re"]
        target = ("I\U00002019ve I\U00002019m he\U00002019s hasn\U00002019t "
                  "she\U00002019d you\U00002019re")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_contractions_3(self):
        """
        Use U+02BC (MODIFIER LETTER APOSTROPHE) as the character marking
        contractions.
        """
        lst = ["I", "\U00002019ve", "I", "\U00002019m", "he", "\U00002019s",
               "hasn", "\U00002019t", "she", "\U00002019d",
               "you", "\U00002019re"]
        target = ("I\U00002019ve I\U00002019m he\U00002019s hasn\U00002019t "
                  "she\U00002019d you\U00002019re")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_brackets_1(self):
        lst = list("a(b)c[d]e{f}")
        target = "a (b) c [d] e {f}"
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_single_quoting_1(self):
        lst = ["he", "said",
               "\N{LEFT SINGLE QUOTATION MARK}",
               "no",
               "\N{RIGHT SINGLE QUOTATION MARK}",
               "to", "me", "."]
        target = ("he said \N{LEFT SINGLE QUOTATION MARK}no"
                  "\N{RIGHT SINGLE QUOTATION MARK} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_single_quoting_1(self):
        """
        Test LEFT/RIGHT SINGLE QUOTATION MARK with broken opening tokenization
        """
        lst = ["he", "said",
               "\N{LEFT SINGLE QUOTATION MARK}no",
               "\N{RIGHT SINGLE QUOTATION MARK}",
               "to", "me", "."]
        target = ("he said \N{LEFT SINGLE QUOTATION MARK}no"
                  "\N{RIGHT SINGLE QUOTATION MARK} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_single_quoting_2(self):
        """
        Test LEFT/RIGHT SINGLE QUOTATION MARK with broken closing tokenization
        """
        lst = ["he", "said",
               "\N{LEFT SINGLE QUOTATION MARK}",
               "no\N{RIGHT SINGLE QUOTATION MARK}",
               "to", "me", "."]
        target = ("he said \N{LEFT SINGLE QUOTATION MARK}no"
                  "\N{RIGHT SINGLE QUOTATION MARK} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_double_quoting_1(self):
        """
        Test LEFT/RIGHT DOUBLE QUOTATION MARK
        """
        lst = ["he", "said",
               "\N{LEFT DOUBLE QUOTATION MARK}",
               "no",
               "\N{RIGHT DOUBLE QUOTATION MARK}",
               "to", "me", "."]
        target = ("he said \N{LEFT DOUBLE QUOTATION MARK}no"
                  "\N{RIGHT DOUBLE QUOTATION MARK} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_double_quoting_1(self):
        """
        Test LEFT/RIGHT DOUBLE QUOTATION MARK with broken opening tokenization
        """
        lst = ["he", "said",
               "\N{LEFT DOUBLE QUOTATION MARK}no",
               "\N{RIGHT DOUBLE QUOTATION MARK}",
               "to", "me", "."]
        target = ("he said \N{LEFT DOUBLE QUOTATION MARK}no"
                  "\N{RIGHT DOUBLE QUOTATION MARK} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_double_quoting_2(self):
        """
        Test LEFT/RIGHT DOUBLE QUOTATION MARK with broken closing tokenization
        """
        lst = ["he", "said",
               "\N{LEFT DOUBLE QUOTATION MARK}",
               "no\N{RIGHT DOUBLE QUOTATION MARK}",
               "to", "me", "."]
        target = ("he said \N{LEFT DOUBLE QUOTATION MARK}no"
                  "\N{RIGHT DOUBLE QUOTATION MARK} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_double_quoting_3(self):
        """
        Test LEFT/RIGHT DOUBLE QUOTATION MARK with fully broken tokenization
        """
        lst = [
            "he", "said",
            "\N{LEFT DOUBLE QUOTATION MARK}no\N{RIGHT DOUBLE QUOTATION MARK}",
            "to", "me", "."]
        target = ("he said \N{LEFT DOUBLE QUOTATION MARK}no"
                  "\N{RIGHT DOUBLE QUOTATION MARK} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_single_tick_quoting_1(self):
        """
        Use single LaTeX-style tick quotes (GRAVE ACCENT and ACUTE ACCENT)
        """
        lst = ["he", "said",
               "\N{GRAVE ACCENT}",
               "no",
               "\N{ACUTE ACCENT}",
               "to", "me", "."]
        target = ("he said \N{GRAVE ACCENT}no\N{ACUTE ACCENT} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_single_tick_quoting_1(self):
        """
        Use single LaTeX-style tick quotes (GRAVE ACCENT and ACUTE ACCENT) with
        broken opening tokenization
        """
        lst = ["he", "said",
               "\N{GRAVE ACCENT}no",
               "\N{ACUTE ACCENT}",
               "to", "me", "."]
        target = ("he said \N{GRAVE ACCENT}no\N{ACUTE ACCENT} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_single_tick_quoting_2(self):
        """
        Use single LaTeX-style tick quotes (GRAVE ACCENT and ACUTE ACCENT) with
        broken closing tokenization
        """
        lst = ["he", "said",
               "\N{GRAVE ACCENT}",
               "no\N{ACUTE ACCENT}",
               "to", "me", "."]
        target = ("he said \N{GRAVE ACCENT}no\N{ACUTE ACCENT} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_double_tick_quoting_1(self):
        """
        Use double LaTeX-style tick quotes (GRAVE ACCENT and ACUTE ACCENT)
        """
        lst = ["he", "said",
               "\N{GRAVE ACCENT}\N{GRAVE ACCENT}",
               "no",
               "\N{ACUTE ACCENT}\N{ACUTE ACCENT}",
               "to", "me", "."]
        target = ("he said \N{GRAVE ACCENT}\N{GRAVE ACCENT}no"
                  "\N{ACUTE ACCENT}\N{ACUTE ACCENT} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_double_tick_quoting_1(self):
        """
        Use double LaTeX-style tick quotes (GRAVE ACCENT and ACUTE ACCENT) with
        broken opening tokenization
        """
        lst = ["he", "said",
               "\N{GRAVE ACCENT}\N{GRAVE ACCENT}no",
               "\N{ACUTE ACCENT}\N{ACUTE ACCENT}",
               "to", "me", "."]
        target = ("he said \N{GRAVE ACCENT}\N{GRAVE ACCENT}no"
                  "\N{ACUTE ACCENT}\N{ACUTE ACCENT} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_double_tick_quoting_2(self):
        """
        Use double LaTeX-style tick quotes (GRAVE ACCENT and ACUTE ACCENT) with
        broken closing tokenization
        """
        lst = ["he", "said",
               "\N{GRAVE ACCENT}\N{GRAVE ACCENT}",
               "no\N{ACUTE ACCENT}\N{ACUTE ACCENT}",
               "to", "me", "."]
        target = ("he said \N{GRAVE ACCENT}\N{GRAVE ACCENT}no"
                  "\N{ACUTE ACCENT}\N{ACUTE ACCENT} to me.")
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_double_mixed_quote_1(self):
        """
        Use double mixed quotes `` and '' (like in BROWN)
        """
        lst = ["he", "said", "\N{GRAVE ACCENT}\N{GRAVE ACCENT}",
               "xxx", "''", "to", "me", "."]
        target = "he said \N{GRAVE ACCENT}\N{GRAVE ACCENT}xxx'' to me."
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_single_ascii_quoting_1(self):
        """
        Use single ASCII quoting.
        """
        lst = ["he", "said",
               "'"
               "xxx",
               "'",
               "to", "me", "."]
        target = "he said 'xxx' to me."
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_single_ascii_quoting_1(self):
        """
        Use single ASCII quoting with broken opening tokenization
        """
        lst = ["he", "said",
               "'xxx",
               "'", "to", "me", "."]
        target = "he said 'xxx' to me."
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_single_ascii_quoting_2(self):
        """
        Use single ASCII quoting with broken closing tokenization
        """
        lst = ["he", "said",
               "'",
               "xxx'",
               "to", "me", "."]
        target = "he said 'xxx' to me."
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_incomplete_single_quoting(self):
        """
        Use single ASCII quoting with broken opening tokenization and no closer
        """
        lst = ["he", "said", "'who", "is", "this"]
        target = "he said 'who is this"
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)



    def test_double_ascii_quoting_1(self):
        """
        Use double ASCII quoting.
        """
        lst = ["he", "said",
               '"',
               "xxx",
               '"',
               "to", "me", "."]
        target = 'he said "xxx" to me.'
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_double_ascii_quoting_1(self):
        """
        Use double ASCII quoting with broken opening tokenization
        """
        lst = ["he", "said",
               '"xxx',
               '"',
               "to", "me", "."]
        target = 'he said "xxx" to me.'
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_double_ascii_quoting_2(self):
        """
        Use double ASCII quoting with broken closing tokenization
        """
        lst = ["he", "said",
               '"',
               'xxx"',
               "to", "me", "."]
        target = 'he said "xxx" to me.'
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_broken_punctuation_1(self):
        lst = ["cats,", "dogs", ",", "and", "carrots"]
        target = 'cats, dogs, and carrots'
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_empty_1(self):
        lst = []
        target = None
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)

    def test_empty_2(self):
        lst = None
        target = None
        value = collapse_words(lst, "en")
        self.assertEqual(target, value)



class TestFailing(CoqTestCase):

    pass



provided_tests = [TestGeneral, TestPretty,
                  TestCollapseWords, TestEnglishCollapseWords,
                  TestRecycle,
                  TestFailing]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

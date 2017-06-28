# -*- coding: utf-8 -*-
"""
This module tests the Switchboard installer module.

Run it like so:

coquery$ python -m test.test_switchboard

"""

from __future__ import unicode_literals

import unittest
import sys, os, shutil
import tempfile
import argparse
import pandas as pd

sys.path.append(os.path.join(sys.path[0], "../coquery/installer"))
sys.path.append(os.path.join(sys.path[0], "../coquery"))

from coquery.coquery import options
from coquery.installer.coq_install_switchboard import BuilderClass
from coquery.tables import Table

# Dummy data to mock the file call_con_tab.csv:
mock_call_con_tab = """1001, "A", 1, "555-2368", 5, 100, "", "Y"
1001, "B", 2, "555-5555", 5, 100, "", "Y"
1337, "A", 3, "555-7896", 8, 101, "", "Y"
1337, "B", 1, "555-1793", 8, 101, "", "Y"
"""

mock_topic_tab = """"FIRST", 100, "SHOULD THERE BE A FIRST TOPIC?", "N", "", ""
"SECOND", 101, "IS ONE TOPIC ENOUGH?", "Y", "", ""
"""

mock_rating_tab = """1001, 1, 2, 3, 8, 8, 4, 4, 2, 2, ""
1337, 9, 9, 9, 1, 5, 5, 1, 1, 5, ""
"""

mock_caller_tab = """1, 99, "Y", "FEMALE", 1954, "NYC", 5, 0, "GIFT", 10, "N", "", 5, "EN1"
2, 98, "N", "MALE", 1940, "WESTERN", 4, 0, "GIFT", 10, "N", "", 5, "EN2"
3, 97, "Y", "MALE", 1977, "SOUTH MIDLAND", 3, 0, "CASH", 15, "N", "", 5, "XP"
"""

mock_contents = {"call_con_tab.csv": mock_call_con_tab,
                 "topic_tab.csv": mock_topic_tab,
                 "rating_tab.csv": mock_rating_tab,
                 "caller_tab.csv": mock_caller_tab}

df_call_con_tab = pd.DataFrame({
    "ConversationId": [1001, 1001, 1337, 1337],
    "Side": ["A", "B"] * 2,
    "SpeakerId": [1, 2, 3, 1],
    "Length": [5, 5, 8, 8],
    "ivi_no": [100, 100, 101, 101],
    })

df_topic_tab = pd.DataFrame({
    "Topic": ["FIRST", "SECOND"],
    "ivi_no": [100, 101]
    })

df_rating_tab = pd.DataFrame({
    "ConversationId": [1001, 1337],
    "Difficulty": [1, 9],
    "Topicality": [2, 9],
    "Naturalness": [3, 9],
    "Remarks": ["", ""]})

df_caller_tab = pd.DataFrame({
    "SpeakerId": [1, 2, 3],
    "Sex": ["FEMALE", "MALE", "MALE"],
    "BirthYear": [1954, 1940, 1977],
    "DialectArea": ["NYC", "WESTERN", "SOUTH MIDLAND"],
    "Education": [5, 4, 3]})

df_meta = pd.DataFrame({
    "ConversationId": [1001, 1337],
    "Topic": ["FIRST", "SECOND"],
    "Difficulty": [1, 9],
    "Topicality": [2, 9],
    "Naturalness": [3, 9],
    "Remarks": ["", ""]
    })

class MockTable(Table):
    def __init__(self, *args, **kwargs):
        self.content = {}

    def get_or_insert(self, d):
        word = d["Word"]
        if word not in self.content:
            self.content[word] = (len(self.content) + 1, d)
        return self.content[word][0]

class TestSwitchboard(unittest.TestCase):
    def setUp(self):
        self._temp_path = tempfile.mkdtemp()
        for file_name in BuilderClass.expected_files:
            with open(os.path.join(self._temp_path, file_name), "w") as f:
                f.write(mock_contents.get(file_name, ""))

        options.cfg = argparse.Namespace()
        audio_path = os.path.join(self._temp_path, "audio")
        os.makedirs(audio_path)
        options.cfg.binary_path = audio_path
        for file_name in ["sw01001.sph", "sw01337.sph"]:
            open(os.path.join(audio_path, file_name), "w").close()

    def tearDown(self):
        shutil.rmtree(self._temp_path)

    def assert_df_equal(self, df1, df2):
        self.assertListEqual(sorted(df1.columns), sorted(df2.columns))
        self.assertEqual(len(df1), len(df2))
        for col in df1.columns:
            try:
                self.assertListEqual(df1[col].values.tolist(),
                                     df2[col].values.tolist())
            except Exception as e:
                e.args = tuple([x.replace("Lists", "Columns '{}'".format(col))
                                for x in e.args])
                raise e

    def test_get_file_list(self):
        installer = BuilderClass()
        l = installer.get_file_list(self._temp_path, None)
        self.assertListEqual(
            sorted(l),
            sorted([os.path.join(self._temp_path, x)
                    for x in BuilderClass.expected_files]))

    def test_binary_files(self):
        installer = BuilderClass()
        installer.get_file_list(self._temp_path, None)
        print(BuilderClass.binary_files)

        self.assertListEqual(
            sorted(BuilderClass.binary_files.keys()),
            ["sw01001.sph", "sw01337.sph"])

    def test_read_call_con(self):
        path = os.path.join(self._temp_path, "call_con_tab.csv")
        df = BuilderClass.process_call_con(path)
        self.assert_df_equal(df, df_call_con_tab)

    def test_read_topic(self):
        path = os.path.join(self._temp_path, "topic_tab.csv")
        df = BuilderClass.process_topic(path)
        self.assert_df_equal(df, df_topic_tab)

    def test_read_rating(self):
        path = os.path.join(self._temp_path, "rating_tab.csv")
        df = BuilderClass.process_rating(path)
        self.assert_df_equal(df, df_rating_tab)

    def test_read_caller(self):
        path = os.path.join(self._temp_path, "caller_tab.csv")
        df = BuilderClass.process_caller(path)
        self.assert_df_equal(df, df_caller_tab)

    def test_merge_meta_data(self):
        path = os.path.join(self._temp_path, "call_con_tab.csv")
        df_source = BuilderClass.process_call_con(path)
        path = os.path.join(self._temp_path, "topic_tab.csv")
        df_topic = BuilderClass.process_topic(path)
        path = os.path.join(self._temp_path, "rating_tab.csv")
        df_rating = BuilderClass.process_rating(path)

        df = BuilderClass.merge_meta_data(df_source, df_topic, df_rating)
        self.assert_df_equal(df, df_meta)

    def test_process_content(self):
        def mock_table_method(x):
            return lexicon

        lexicon = MockTable()
        installer = BuilderClass()
        path = os.path.join(self._temp_path, "call_con_tab.csv")
        installer._df_call = BuilderClass.process_call_con(path)
        installer.table = mock_table_method

        content = ["sw1001A-ms98-a-0001 0.000000 1.000000 hi",
                   "sw1001A-ms98-a-0002 1.000000 2.000000 [silence]",
                   "sw1001A-ms98-a-0003 2.000000 3.000000 nice",
                   "sw1001A-ms98-a-0003 3.000000 4.000000 to",
                   "sw1001A-ms98-a-0003 4.000000 5.000000 meet",
                   "sw1001A-ms98-a-0003 5.000000 6.000000 you",
                   "sw1001A-ms98-a-0004 6.000000 12.000000 [silence]"]

        types = ["hi", "[silence]", "nice", "to", "meet", "you"]
        conv_id = 1001
        side = "A"

        tokens, duration = installer.process_content(content, conv_id, side)

        # assert that all words have entered the lexicon, and that the lexicon
        # contains nothing but types from the content:
        for word in list(lexicon.content.keys()):
            self.assertTrue(word in types)
            types.remove(word)
        self.assertTrue(types == [])

        # assert that the word ids have been assigned in the expected order:
        self.assertListEqual([d["WordId"] for d in tokens],
                             [1, 2, 3, 4, 5, 6, 2])

        token = tokens[0]
        # assert that SpeakerId, ConversationId and FileId are correct:
        self.assertEqual(token["SpeakerId"], 1)
        self.assertEqual(token["ConversationId"], 1001)
        self.assertEqual(token["FileId"], 1)

        # assert that the overall duration was correctly determined:
        self.assertEqual(duration, 12)

def main():
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestSwitchboard),
        ])
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

from __future__ import print_function
import unittest
import sys
import tempfile
import os
import argparse

from coquery.defines import SQL_SQLITE
from coquery.coquery import options
from coquery.corpusbuilder import (
    BaseCorpusBuilder, XMLCorpusBuilder, TEICorpusBuilder)
from coquery.tables import Table, Column, Identifier, Link

from .test_corpora import simple

options.cfg = argparse.Namespace()

try:
    from lxml import etree as ET
except ImportError:
    try:
        import xml.etree.cElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET

xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<file>
    <header>
        <source>XXX</source>
        <date>1999</date>
        <genre>Written</genre>
    </header>
    <text>
        <p>
            This is a test.
        </p>
    </text>
</file>
"""

# the following TEI example is CC-BY-SA 3.0 by teibyexample@kanti.be
# http://teibyexample.org/examples/TBED04v00.htm#shakespeare
tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <encodingDesc>
            <!--...-->
            <metDecl pattern="((+|-)+\|?/?)*">
                <metSym value="trochee" terminal="false">+-</metSym>
                <metSym value="iamb" terminal="false">-+</metSym>
                <metSym value="spondee" terminal="false">++</metSym>
                <metSym value="pyrrhic" terminal="false">--</metSym>
                <metSym value="amphibrach" terminal="false">-+-</metSym>
                <metSym value="anapaest" terminal="false">--+</metSym>
                <metSym value="+">metrical promimence</metSym>
                <metSym value="-">metrical non-prominence</metSym>
                <metSym value="|">foot boundary</metSym>
                <metSym value="/">metrical line boundary</metSym>
            </metDecl>
            <metDecl>
                <p>Metrically prominent syllables are marked '+' and other syllables '-'. Foot divisions are marked by a vertical bar, and line divisions with a solidus.</p>
                <p>This notation may be applied to any metrical unit, of any size (including, for example, individual feet as well as groups of lines).</p>
                <p>The 'real' attribute has been used to indicate possible variations in the iambic base metre. Where this attribute is not included, it is assumed each foot inherits the iambic metre defined for the overall division of text.</p>
                <p>The 'met' attribute has been used in feet which have a missing or additional syllable rather than the two syllables expected, although the line may still confirm to the metre of the poem.</p>
            </metDecl>
        </encodingDesc>
        <!--...-->
    </teiHeader>
    <text>
        <body>
            <lg type="poem" met="-+ | -+ | -+ | -+ | -+ /">
                <head>
                    <title>Sonnet 17</title>
                </head>
                <lg type="sonnet" rhyme="abab cdcd efef gg">
                    <lg type="quatrain">
                        <l>
                            <seg type="foot" real="+-">Who will</seg>
                            <seg type="foot">believe</seg>
                            <seg type="foot">my verse</seg>
                            <seg type="foot">in time</seg>
                            <seg type="foot">to come,</seg>
                        </l>
                        <l>
                            <seg type="foot">If it</seg>
                            <seg type="foot">were fill'd</seg>
                            <seg type="foot">with your</seg>
                            <seg type="foot">most high</seg>
                            <seg type="foot" real="+-">deserts?</seg>
                        </l>
                        <l>
                            <seg type="foot">Though yet,</seg>
                            <seg type="foot" real="+-">heaven knows,</seg>
                            <seg type="foot">it is</seg>
                            <seg type="foot">but as</seg>
                            <seg type="foot">a tomb</seg>
                        </l>
                        <l>
                            <seg type="foot">Which hides</seg>
                            <seg type="foot">your life</seg>
                            <seg type="foot">and shows</seg>
                            <seg type="foot">not half</seg>
                            <seg type="foot">your parts.</seg>
                        </l>
                    </lg>
                    <lg type="quatrain">
                        <l enjamb="y">
                            <seg type="foot">If I</seg>
                            <seg type="foot">could write</seg>
                            <seg type="foot">the beau</seg>
                            <seg type="foot">ty of</seg>
                            <seg type="foot">your eyes</seg>
                        </l>
                        <l>
                            <seg type="foot" real="--">And in</seg>
                            <seg type="foot" real="++">fresh num</seg>
                            <seg type="foot">bers num</seg>
                            <seg type="foot">ber all</seg>
                            <seg type="foot" met="-+-">your graces,</seg>
                        </l>
                        <l>
                            <seg type="foot">The age</seg>
                            <seg type="foot">to come</seg>
                            <seg type="foot">would say</seg>
                            <seg type="foot">‘This po</seg>
                            <seg type="foot">et lies;</seg>
                        </l>
                        <l>
                            <seg type="foot">Such heaven</seg>
                            <seg type="foot">ly touch</seg>
                            <seg type="foot">es ne'er</seg>
                            <seg type="foot">touch'd earth</seg>
                            <seg type="foot" met="-+-">ly faces’.</seg>
                        </l>
                    </lg>
                    <lg type="quatrain">
                        <l>
                            <seg type="foot">So should</seg>
                            <seg type="foot">my pap</seg>
                            <seg type="foot">
                                ers,
                                <caesura />
                                yell
                            </seg>
                            <seg type="foot">owed with</seg>
                            <seg type="foot">their age,</seg>
                        </l>
                        <l>
                            <seg type="foot">Be scorn'd</seg>
                            <seg type="foot">like old</seg>
                            <seg type="foot" real="+-">men of</seg>
                            <seg type="foot">less truth</seg>
                            <seg type="foot">than tongue;</seg>
                        </l>
                        <l>
                            <seg type="foot">And your</seg>
                            <seg type="foot">true rights</seg>
                            <seg type="foot">be term'</seg>
                            <seg type="foot">a po</seg>
                            <seg type="foot">et's rage,</seg>
                        </l>
                        <l>
                            <seg type="foot">And stretch</seg>
                            <seg type="foot">ed me</seg>
                            <seg type="foot">tre of</seg>
                            <seg type="foot">an an</seg>
                            <seg type="foot">tique song.</seg>
                        </l>
                    </lg>
                    <lg type="couplet">
                        <l>
                            <seg type="foot">But were</seg>
                            <seg type="foot">some child</seg>
                            <seg type="foot">of yours</seg>
                            <seg type="foot">alive</seg>
                            <seg type="foot">that time,</seg>
                        </l>
                        <l>
                            <seg type="foot">You should</seg>
                            <seg type="foot">live twice-</seg>
                            <seg type="foot">in it,</seg>
                            <caesura />
                            <seg type="foot">and in</seg>
                            <seg type="foot">my rhyme.</seg>
                        </l>
                    </lg>
                </lg>
            </lg>
        </body>
    </text>
</TEI>"""


class TestingXML(XMLCorpusBuilder):
    def __init__(self):
        super(TestingXML, self).__init__()
        self.content = []
        self._last_open = None
        self._last_close = None

        self.header_tag = "header"
        self.body_tag = "text"

    def process_content(self, content):
        new_content = content.split()
        for x in new_content:
            self.content.append(x)
            self._corpus_id += 1
            self._last_id = self._corpus_id

    def preprocess_element(self, element):
        self._last_open = element.tag

    def postprocess_element(self, element):
        self._last_close = element.tag


class TestingTEI(TEICorpusBuilder):
    def __init__(self):
        super(TestingTEI, self).__init__()
        self.content = []
        self._last_open = None
        self._last_close = None

    def process_content(self, content):
        new_content = content.split()
        for x in new_content:
            self.content.append(x)
            self._corpus_id += 1
            self._last_id = self._corpus_id

    def preprocess_element(self, element):
        self._last_open = element.tag

    def postprocess_element(self, element):
        self._last_close = element.tag


class NgramBuilder(BaseCorpusBuilder):
    corpusngram_table = "CorpusNgram"
    corpusngram_width = 3

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_columns = [
        Identifier(word_id, "INT"),
        Column(word_label, "VARCHAR")]

    source_table = "Files"
    source_id = "FileId"
    source_label = "Title"
    source_columns = [
        Identifier(source_id, "INT"),
        Column(source_label, "VARCHAR")]

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_source_id = "FileId"
    corpus_columns = [
        Identifier(corpus_id, "INT"),
        Link(corpus_word_id, word_table),
        Link(corpus_source_id, source_table)]

    auto_create = ["word", "source", "corpus"]
    query_item_word = "word_label"


class NGramBuilderFlat(BaseCorpusBuilder):
    corpusngram_table = "CorpusNgram"
    corpusngram_width = 3

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word = "Word"
    corpus_pos = "POS"
    corpus_columns = [
        Identifier(corpus_id, "INT"),
        Column(corpus_word, "VARCHAR"),
        Column(corpus_pos, "VARCHAR")]

    auto_create = ["corpus"]


class TestCorpusNgram(unittest.TestCase):

    def setUp(self):
        self.builder = NgramBuilder()
        self.maxDiff = None
        options.cfg.no_ngram = False


    def test_get_ngram_columns(self):
        l = self.builder.build_lookup_get_ngram_columns()
        self.assertEqual(
            l, ["ID1", "FileId1", "WordId1", "WordId2", "WordId3"])

    def test_get_ngram_padding_1(self):
        s = self.builder.build_lookup_get_padding_string()
        self.assertEqual(simple(s),
                         simple("""
        INSERT INTO CorpusNgram (ID1, FileId1, WordId1, WordId2, WordId3)
        VALUES ({last_row} + 1, {FileId1}, {WordId2}, {WordId3}, {na_value}),
               ({last_row} + 2, {FileId1}, {WordId3}, {na_value}, {na_value})
               """))

    def test_get_ngram_table(self):
        corpus_table = Table(self.builder.corpus_table)
        for col in [Identifier(self.builder.corpus_id, "INT(3)"),
                    Column(self.builder.corpus_word_id, "INT(7)"),
                    Column(self.builder.corpus_source_id, "INT(5)")]:
            corpus_table.add_column(col)
        self.builder._new_tables[self.builder.corpus_table] = corpus_table

        table = self.builder.build_lookup_get_ngram_table()

        s = table.get_create_string(SQL_SQLITE,
                                    self.builder._new_tables.values())
        self.assertEqual(simple(s),
                         simple("""
                         ID1 INT(3) PRIMARY KEY,
                         FileId1 INT(5),
                         WordId1 INT(7),
                         WordId2 INT(7),
                         WordId3 INT(7)
                         """))

    def test_get_insert_string(self):
        options.cfg.no_ngram = False
        s1 = self.builder.build_lookup_get_insert_string()
        s2 = """
            INSERT INTO CorpusNgram (ID1, FileId1, WordId1, WordId2, WordId3)
            SELECT ID1, FileId1, WordId1, WordId2, WordId3
            FROM    (SELECT FileId AS FileId1, ID AS ID1, WordId AS WordId1
                     FROM   Corpus) AS COQ_CORPUS_1
            INNER JOIN
                    (SELECT FileId AS FileId2, ID AS ID2, WordId AS WordId2
                     FROM   Corpus) AS COQ_CORPUS_2 ON ID2 = ID1 + 1
            INNER JOIN
                    (SELECT FileId AS FileId3, ID AS ID3, WordId AS WordId3
                     FROM   Corpus) AS COQ_CORPUS_3 ON ID3 = ID1 + 2"""

        self.assertEqual(simple(s1), simple(s2))


class TestFlatCorpusBuilder(unittest.TestCase):
    def test_get_ngram_padding_1(self):
        self.builder = NGramBuilderFlat()
        s = self.builder.build_lookup_get_padding_string()
        self.assertEqual(simple(s),
                         simple("""
        INSERT INTO CorpusNgram (ID1, FileId1, POS1, POS2, POS3, Word1, Word2, Word3)
        VALUES ({last_row} + 1, {FileId1}, {POS2}, {POS3}, {na_value},{WordId2}, {WordId3}, {na_value}),
               ({last_row} + 2, {FileId1}, {POS3}, {na_value}, {na_value}, {WordId3}, {na_value}, {na_value})
               """))


class TestXMLCorpusBuilder(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile("w")
        self.temp_file_name = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        try:
            os.remove(self.temp_file_name)
        except (OSError, IOError):
            pass

    def _get_tree(self, content):
        if sys.version_info < (3, 0):
            tree = ET.XML(xml_content)
        else:
            tree = ET.XML(bytes(xml_content, encoding="utf8"))
        return tree

    def test_read_file(self):
        with open(self.temp_file_name, "w") as temp_file:
            temp_file.write(xml_content)

        builder = TestingXML()

        result = builder.read_file(self.temp_file_name)
        self.assertListEqual(
            ["{}\n".format(x) for x in xml_content.split("\n") if x.strip("\n")],
            [x for x in result if x.strip("\n")])

    def test_preprocess_data(self):
        with open(self.temp_file_name, "w") as temp_file:
            temp_file.write(xml_content)

        builder = TestingXML()

        data = builder.read_file(self.temp_file_name)
        self.assertEqual(data, builder.preprocess_data(data))

    def test_process_file(self):
        with open(self.temp_file_name, "w") as temp_file:
            temp_file.write(xml_content)

        builder = TestingXML()
        builder.process_file(self.temp_file_name)
        self.assertEqual(len(builder.header), 3)
        self.assertEqual(len(builder.content), 4)

    def test_process_header(self):
        builder = TestingXML()
        tree = self._get_tree(xml_content)
        builder.process_header(tree)
        children = [child.tag for child in builder.header]
        self.assertListEqual(children, ["source", "date", "genre"])
        self.assertEqual(builder.header[0].text, "XXX")
        self.assertEqual(builder.header[1].text, "1999")
        self.assertEqual(builder.header[2].text, "Written")

    def test_process_body(self):
        builder = TestingXML()
        tree = self._get_tree(xml_content)
        builder.process_body(tree)
        self.assertListEqual(builder.content,
                             ["This", "is", "a", "test."])
        self.assertEqual(builder._corpus_id, 4)
        self.assertEqual(builder._last_open, "p")
        self.assertEqual(builder._last_close, "text")

    def test_process_element_1(self):
        builder = TestingXML()
        element = ET.XML("<el>test element</el>")
        builder.process_element(element)
        self.assertEqual(builder._last_open, "el")
        self.assertEqual(builder._last_close, "el")
        self.assertListEqual(builder.content, ["test", "element"])
        self.assertEqual(builder._last_id, 2)

    def test_process_element_2(self):
        builder = TestingXML()
        element = ET.XML("<el>test <b>this</b> element</el>")
        builder.process_element(element)
        self.assertEqual(builder._last_open, "b")
        self.assertEqual(builder._last_close, "el")
        self.assertListEqual(builder.content,
                             ["test", "this", "element"])
        self.assertEqual(builder._last_id, 3)

    def test_process_element_3(self):
        builder = TestingXML()
        element = ET.XML("<el><b>this</b> element</el>")
        builder.process_element(element)
        self.assertEqual(builder._last_open, "b")
        self.assertEqual(builder._last_close, "el")
        self.assertListEqual(builder.content,
                             ["this", "element"])
        self.assertEqual(builder._last_id, 2)

    def test_process_element_4(self):
        builder = TestingXML()
        element = ET.XML("<el><b>element</b></el>")
        builder.process_element(element)
        self.assertEqual(builder._last_open, "b")
        self.assertEqual(builder._last_close, "el")
        self.assertListEqual(builder.content,
                             ["element"])
        self.assertEqual(builder._last_id, 1)

    def test_preprocess_element(self):
        builder = TestingXML()
        element = ET.XML("<el>test element</el>")
        builder.preprocess_element(element)
        self.assertEqual(builder._last_open, "el")

    def test_process_content(self):
        builder = TestingXML()
        element = ET.XML("<el>test element</el>")
        builder.process_content(element.text)
        self.assertListEqual(builder.content, ["test", "element"])
        self.assertEqual(builder._last_id, 2)

    def test_postprocess_element(self):
        builder = TestingXML()
        element = ET.XML("<el>test element</el>")
        builder.postprocess_element(element)
        self.assertEqual(builder._last_close, "el")


class TestTEICorpusBuilder(TestXMLCorpusBuilder):
    def test_process_tree(self):
        with open(self.temp_file_name, "w") as temp_file:
            temp_file.write(tei_content)

        builder = TestingTEI()
        builder.process_file(self.temp_file_name)
        self.assertEqual(len(builder.header), 1)
        self.assertEqual(len(builder.content), 139)


provided_tests = [TestCorpusNgram, TestFlatCorpusBuilder,
                  TestXMLCorpusBuilder, TestTEICorpusBuilder]


def main():
    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(x)
         for x in provided_tests])
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()

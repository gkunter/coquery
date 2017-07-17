# -*- coding: utf-8 -*-

from __future__ import print_function
import unittest
import sys
import tempfile
import os

from coquery.defines import SQL_SQLITE
from coquery.corpusbuilder import (
    BaseCorpusBuilder, XMLCorpusBuilder, TEICorpusBuilder)
from coquery.tables import Table, Column, Identifier, Link

from .test_corpora import simple

try:
    from lxml import etree as ET
except ImportError:
    try:
        import xml.etree.cElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET

try:
    from cStringIO import StringIO as IO_Stream
except ImportError:
    from io import BytesIO as IO_Stream

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
tei_content = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
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
            <p>
                <s n="1">
                    <w n="1">This</w>
                    <w n="2">This</w>
                    <w n="3">This</w>
                    <w n="4">This</w>
                </s>
            </p>
        </body>
    </text>
</TEI>
"""


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

        self.assertEqual(simple(table.get_create_string(SQL_SQLITE)),
                         simple("""
                         ID1 INT(3) PRIMARY KEY,
                         FileId1 INT(5),
                         WordId1 INT(7),
                         WordId2 INT(7),
                         WordId3 INT(7)
                         """))

    def test_get_insert_string(self):
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
        INSERT INTO CorpusNgram (ID1, FileId1, Word1, Word2, Word3, POS1, POS2, POS3)
        VALUES ({last_row} + 1, {FileId1}, {WordId2}, {WordId3}, {na_value}, {POS2}, {POS3}, {na_value}),
               ({last_row} + 2, {FileId1}, {WordId3}, {na_value}, {na_value}, {POS3}, {na_value}, {na_value})
               """))


class TestXMLCorpusBuilder(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile("w")
        self.temp_file_name = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        try:
            os.remove(self.temp_file_name)
        except IOError as e:
            pass

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
        tree = ET.XML(bytes(xml_content, encoding="utf8"))
        builder.process_header(tree)
        children = [child.tag for child in builder.header]
        self.assertListEqual(children, ["source", "date", "genre"])
        self.assertEqual(builder.header[0].text, "XXX")
        self.assertEqual(builder.header[1].text, "1999")
        self.assertEqual(builder.header[2].text, "Written")

    def test_process_body(self):
        builder = TestingXML()
        tree = ET.XML(bytes(xml_content, encoding="utf8"))
        builder.process_body(tree)
        children = [child.tag for child in builder.body]
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

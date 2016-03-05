# -*- coding: utf-8 -*-
""" This module tests the bibliography module."""

from __future__ import unicode_literals

import unittest
import os.path
import sys

sys.path.append(os.path.join(sys.path[0], "../coquery"))
from bibliography import *

# Create a tuple containing the available string types 
# (Python 3 has no unicode):
try:
    string_types = (unicode, str)
except NameError:
    string_types = (str, )

class TestPerson(unittest.TestCase):
    def test_property_name(self):
        name = Person()
        name.first = "Jürgen"
        name.middle = ["Otto", "Emil"]
        name.prefix = "Dr."
        name.suffix = "MA"
        name.last = "Münster"

        self.assertEqual(name.first, "Jürgen")
        self.assertEqual(name.middle, ["Otto", "Emil"])
        self.assertEqual(name.prefix, "Dr.")
        self.assertEqual(name.suffix, "MA")
        self.assertEqual(name.last, "Münster")

        name = Person(first="Jürgen", middle="M.", last="Münster")
        self.assertTrue(isinstance(name.first, (unicode, str)))
        self.assertTrue(isinstance(name.middle, list))
        self.assertTrue(isinstance(name.last, (unicode, str)))

    def test_repr(self):
        name = Person(first="Jürgen", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Münster")
        # The order of the named arguments in __repr__ is not fixed, so we 
        # test equality by sorting all the characters in the strings:
        self.assertEqual(sorted(name.__repr__()), sorted("Person(first='Jürgen', middle=['Otto', 'Emil'], prefix='Dr.', suffix='MA', last='Münster')"))

    def test_name_str(self):
        name = Person(first="Jürgen", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Münster")
        self.assertEqual(name.__str__(), name.full_name())

    def test_full_name(self):
        name = Person(first="Jürgen", last="Münster")
        self.assertEqual(name.full_name(), "Jürgen Münster")
        self.assertEqual(name.full_name("middle"), "Jürgen Münster")
        self.assertEqual(name.full_name("all"), "J. Münster")

        name = Person(first="Jürgen", middle="M.", last="Münster")
        self.assertEqual(name.full_name(), "Jürgen M. Münster")
        self.assertEqual(name.full_name("middle"), "Jürgen M. Münster")
        self.assertEqual(name.full_name("all"), "J. M. Münster")

        name = Person(first="Jürgen", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Münster")
        self.assertEqual(name.full_name(), "Dr. Jürgen Otto Emil Münster MA")
        self.assertEqual(name.full_name("middle"), "Dr. Jürgen O. E. Münster MA")
        self.assertEqual(name.full_name("all"), "Dr. J. O. E. Münster MA")

    def test_bibliographic_name(self):
        name = Person(first="Jürgen", last="Münster")
        self.assertEqual(name.bibliographic_name(), "Münster, Jürgen")
        self.assertEqual(name.bibliographic_name("middle"), "Münster, Jürgen")
        self.assertEqual(name.bibliographic_name("all"), "Münster, J.")

        name = Person(first="Jürgen", middle="M.", last="Münster")
        self.assertEqual(name.bibliographic_name(), "Münster, Jürgen M.")
        self.assertEqual(name.bibliographic_name("middle"), "Münster, Jürgen M.")
        self.assertEqual(name.bibliographic_name("all"), "Münster, J. M.")

        name = Person(first="Jürgen", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Münster")
        self.assertEqual(name.bibliographic_name(), "Münster MA, Dr. Jürgen Otto Emil")
        self.assertEqual(name.bibliographic_name("middle"), "Münster MA, Dr. Jürgen O. E.")
        self.assertEqual(name.bibliographic_name("all"), "Münster MA, Dr. J. O. E.")

class TestPersonList(unittest.TestCase):
    name1 = Person(first="Jürgen", last="Münster")
    name2 = Person(first="John", middle=["William"], last="Doe")
    name3 = Person(first="Juan", last="Pérez")

    def test_init(self):
        authors = PersonList()
        authors = PersonList(self.name1, self.name2)
        
    def test_repr(self):
        authors = PersonList()
        self.assertEqual(authors.__repr__(), "PersonList()")
        authors = PersonList(self.name1)
        self.assertEqual(authors.__repr__(), "PersonList({})".format(self.name1.__repr__()))
        authors = PersonList(self.name1, self.name2)
        self.assertEqual(authors.__repr__(), "PersonList({}, {})".format(
            self.name1.__repr__(), self.name2.__repr__()))

    def test_str(self):
        authors = PersonList()
        self.assertEqual(authors.__str__(), "")

        # one-person list:
        authors = PersonList(self.name1)
        self.assertEqual(authors.get_names(), self.name1.bibliographic_name())

        # two-persons list:
        authors = PersonList(self.name1, self.name2)
        self.assertEqual(authors.get_names(), "{}, and {}".format(
            self.name1.bibliographic_name(), self.name2.full_name()))
        
        # three-persons list:
        authors = PersonList(self.name1, self.name2, self.name3)
        self.assertEqual(authors.get_names(), "{}, {}, and {}".format(
            self.name1.bibliographic_name(), self.name2.full_name(), self.name3.full_name()))

    def test_get_names_separation(self):

        # change separation of two names:
        authors = PersonList(self.name1, self.name2)
        self.assertEqual(authors.get_names(two_sep=" & "), "{} & {}".format(
            self.name1.bibliographic_name(), self.name2.full_name()))

        # change separation of three names:
        authors = PersonList(self.name1, self.name2, self.name3)
        # two_sep should not have an effect:
        self.assertEqual(authors.get_names(two_sep=" & "), "{}, {}, and {}".format(
            self.name1.bibliographic_name(), self.name2.full_name(), self.name3.full_name()))

        # sep should have an effect:
        self.assertEqual(authors.get_names(sep=" & "), "{} & {}, and {}".format(
            self.name1.bibliographic_name(), self.name2.full_name(), self.name3.full_name()))

        self.assertEqual(authors.get_names(last_sep=" & "), "{}, {} & {}".format(
            self.name1.bibliographic_name(), self.name2.full_name(), self.name3.full_name()))

    def test_get_names_name_orders(self):
        authors = PersonList(self.name1, self.name2, self.name3)
        # start first name with first name:
        self.assertEqual(authors.get_names(mode_first="first"), "Jürgen Münster, John William Doe, and Juan Pérez")
        # start other names with last names:
        self.assertEqual(authors.get_names(mode_others="last"), "Münster, Jürgen, Doe, John William, and Pérez, Juan")

    def test_get_names_initialization(self):
        authors = PersonList(self.name1, self.name2, self.name3)
        # only middle as initials:
        self.assertEqual(authors.get_names(initials="middle"), "Münster, Jürgen, John W. Doe, and Juan Pérez")
        # first and middle as initials:
        self.assertEqual(authors.get_names(initials="all"), "Münster, J., J. W. Doe, and J. Pérez")

class TestEditorList(unittest.TestCase):
    name1 = Person(first="Jürgen", last="Münster")
    name2 = Person(first="John", middle=["William"], last="Doe")
    name3 = Person(first="Juan", last="Pérez")
    
    def test_repr(self):
        namelist = EditorList(self.name1, self.name2)
        self.assertEqual(namelist.__repr__(), "EditorList({}, {})".format(
            self.name1.__repr__(), self.name2.__repr__()))
    
    def test_get_names(self):
        # one editor:
        namelist = EditorList(self.name1)
        self.assertEqual(namelist.get_names(), "{} (ed.)".format(
            self.name1.bibliographic_name()))

        # two editors:
        namelist = EditorList(self.name1, self.name2)
        self.assertEqual(namelist.get_names(), "{}, and {} (eds.)".format(
            self.name1.bibliographic_name(), self.name2.full_name()))

        # three editors:
        namelist = EditorList(self.name1, self.name2, self.name3)
        self.assertEqual(namelist.get_names(), "{}, {}, and {} (eds.)".format(
            self.name1.bibliographic_name(), self.name2.full_name(), self.name3.full_name()))

    def test_change_labels(self):
        # one editor:
        namelist = EditorList(self.name1)
        self.assertEqual(namelist.get_names(one_editor="(Hg.)"), "{} (Hg.)".format(
            self.name1.bibliographic_name()))
        # two_editors should have no effect:
        self.assertEqual(namelist.get_names(two_editors="(Hgg.)"), "{} (ed.)".format(
            self.name1.bibliographic_name()))
        # many_editors should have no effect:
        self.assertEqual(namelist.get_names(many_editors="(Hgg.)"), "{} (ed.)".format(
            self.name1.bibliographic_name()))

        # two editors:
        namelist = EditorList(self.name1, self.name2)
        self.assertEqual(namelist.get_names(two_editors="(Hgg.)"), "{}, and {} (Hgg.)".format(
            self.name1.bibliographic_name(), self.name2.full_name()))
        # one_editor have no effect:
        self.assertEqual(namelist.get_names(one_editor="(Hgg.)"), "{}, and {} (eds.)".format(
            self.name1.bibliographic_name(), self.name2.full_name()))
        # many_editors should have no effect:
        self.assertEqual(namelist.get_names(many_editors="(Hgg.)"), "{}, and {} (eds.)".format(
            self.name1.bibliographic_name(), self.name2.full_name()))

        # three editors:
        namelist = EditorList(self.name1, self.name2, self.name3)
        self.assertEqual(namelist.get_names(many_editors="(Hgg.)"), "{}, {}, and {} (Hgg.)".format(
            self.name1.bibliographic_name(), self.name2.full_name(), self.name3.full_name()))
        # one_editor have no effect:
        self.assertEqual(namelist.get_names(one_editor="(Hgg.)"), "{}, {}, and {} (eds.)".format(
            self.name1.bibliographic_name(), self.name2.full_name(), self.name3.full_name()))
        # two_editors should have no effect:
        self.assertEqual(namelist.get_names(two_editors="(Hgg.)"), "{}, {}, and {} (eds.)".format(
            self.name1.bibliographic_name(), self.name2.full_name(), self.name3.full_name()))

class TestReference(unittest.TestCase):
    name1 = Person(first="Jürgen", last="Müstermann")
    name2 = Person(first="John", middle=["William"], last="Doe")

    title = "test document"
    year = 1999
    namelist = PersonList(name1, name2)    

    def test_init(self):
        self.assertRaises(ValueError, Reference)        
        # no exceptions if at least a title is provided:
        Reference(title=self.title)
        Reference(title=self.title, authors=self.namelist)
        Reference(title=self.title, year=self.year)
        Reference(title=self.title, authors=self.namelist, year=self.year)
        # no exception even if an unused property is provided:
        Reference(title=self.title, authors=self.namelist, year=self.year, journal="Journal")
        
    def test_required(self):
        ref = Reference(title=self.title, authors=self.namelist)
        self.assertEqual(ref.required_properties(), ["title"])
        
    def test_validate(self):
        # expect a ValueError if no title is given:
        self.assertRaises(ValueError, Reference.validate, 
            {"author": self.namelist})
        # no ValueError expected:
        Reference.validate({"title": self.title})

    def test_repr(self):
        ref = Reference(title=self.title)
        self.assertEqual(ref.__repr__(), "Reference(title={})".format(self.title.__repr__()))

        ref = Reference(title=self.title, authors=self.namelist)
        # The order of the named arguments in __repr__ is not fixed, so we 
        # test equality by sorting all the characters in the strings:
        self.assertEqual(sorted(ref.__repr__()), sorted("Reference(title={}, authors={})".format(
            self.title.__repr__(), self.namelist.__repr__())))

        ref = Reference(title=self.title, year=self.year)
        self.assertEqual(sorted(ref.__repr__()), sorted("Reference(title={}, year={})".format(
            self.title.__repr__(), self.year.__repr__())))

        ref = Reference(title=self.title, year=self.year, authors=self.namelist)
        self.assertEqual(sorted(ref.__repr__()), sorted("Reference(title={}, authors={}, year=1999)".format(
            self.title.__repr__(), self.namelist.__repr__(), self.year.__repr__())))

    def test_str(self):
        ref = Reference(title=self.title)
        self.assertEqual(ref.__str__(), "<i>{title}</i>.".format(
            title=self.title))

        ref = Reference(title=self.title, authors=self.namelist)
        self.assertEqual(ref.__str__(), "{authors}. <i>{title}</i>.".format(
            authors=self.namelist.get_names(), 
            title=self.title))

        ref = Reference(title=self.title, year=self.year)
        self.assertEqual(ref.__str__(), "{year}. <i>{title}</i>.".format(
            year=self.year, 
            title=self.title))

        ref = Reference(title=self.title, year=self.year, authors=self.namelist)
        self.assertEqual(ref.__str__(), "{authors}. {year}. <i>{title}</i>.".format(
            authors=self.namelist.get_names(), 
            year=self.year, 
            title=self.title))

class TestArticle(unittest.TestCase):
    name1 = Person(first="Jürgen", last="Münster")

    title = "test article"
    year = 1999
    namelist = PersonList(name1)
    journal = "journal"
    volume = 123
    number = 1
    pages = "1-42"
    
    def test_init(self):
        self.assertRaises(ValueError, Article, 
            kwargs={"title": self.title})
        self.assertRaises(ValueError, Article, 
            kwargs={"title": self.title, "authors": self.namelist})
        self.assertRaises(ValueError, Article, 
            kwargs={"title": self.title, "year": self.year})
        self.assertRaises(ValueError, Article, 
            kwargs={"title": self.title, "journal": self.journal})
        self.assertRaises(ValueError, Article, 
            kwargs={"title": self.title, "authors": self.namelist, "year": self.year})
        self.assertRaises(ValueError, Article, 
            kwargs={"title": self.title, "authors": self.namelist, "journal": self.journal})
        self.assertRaises(ValueError, Article, 
            kwargs={"title": self.title, "year": self.year, "journal": self.journal})

        # no exception expected:
        Article(title=self.title, 
                year=self.year, 
                journal=self.journal, 
                authors=self.namelist)
        Article(title=self.title, 
                year=self.year, 
                journal=self.journal, 
                authors=self.namelist,
                volume=self.volume)
        Article(title=self.title, 
                year=self.year, 
                journal=self.journal, 
                authors=self.namelist,
                pages=self.pages)
        Article(title=self.title, 
                year=self.year, 
                journal=self.journal, 
                authors=self.namelist,
                volume=self.volume,
                pages=self.pages)
        Article(title=self.title, 
                year=self.year, 
                journal=self.journal, 
                authors=self.namelist,
                volume=self.volume,
                number=self.number,
                pages=self.pages)

        # exception expected if number, but no volume is given:
        self.assertRaises(ValueError, Article, 
            kwargs={"title": self.title, 
                    "year": self.year, 
                    "journal": self.journal,
                    "authors": self.namelist,
                    "number": self.number})
            
    def test_validate(self):
        self.assertRaises(ValueError, Article.validate, 
            kwargs={"title": self.title, 
                    "year": self.year, 
                    "journal": self.journal,
                    "authors": self.namelist,
                    "number": self.number})
            
    def test_str(self):
        art = Article(title=self.title, 
                      year=self.year, 
                      authors=self.namelist, 
                      journal=self.journal)
        self.assertEqual(art.__str__(), "{authors}. {year}. {title}. <i>{journal}</i>.".format(
            authors=self.namelist, 
            year=self.year, 
            title=self.title, 
            journal=self.journal))

        art = Article(title=self.title, 
                      year=self.year, 
                      authors=self.namelist, 
                      journal=self.journal,
                      volume=self.volume)
        self.assertEqual(art.__str__(), "{authors}. {year}. {title}. <i>{journal}</i> {volume}.".format(
            authors=self.namelist, 
            year=self.year, 
            title=self.title, 
            journal=self.journal,
            volume=self.volume))

        art = Article(title=self.title, 
                      year=self.year, 
                      authors=self.namelist, 
                      journal=self.journal,
                      volume=self.volume,
                      number=self.number)
        self.assertEqual(art.__str__(), "{authors}. {year}. {title}. <i>{journal}</i> {volume}({number}).".format(
            authors=self.namelist, 
            year=self.year, 
            title=self.title, 
            journal=self.journal,
            volume=self.volume,
            number=self.number))

        art = Article(title=self.title, 
                      year=self.year, 
                      authors=self.namelist, 
                      journal=self.journal,
                      pages=self.pages)
        self.assertEqual(art.__str__(), "{authors}. {year}. {title}. <i>{journal}</i>. {pages}.".format(
            authors=self.namelist, 
            year=self.year, 
            title=self.title, 
            journal=self.journal,
            volume=self.volume,
            pages=self.pages))

        art = Article(title=self.title, 
                      year=self.year, 
                      authors=self.namelist, 
                      journal=self.journal,
                      volume=self.volume,
                      pages=self.pages)
        self.assertEqual(art.__str__(), "{authors}. {year}. {title}. <i>{journal}</i> {volume}. {pages}.".format(
            authors=self.namelist, 
            year=self.year, 
            title=self.title, 
            journal=self.journal,
            volume=self.volume,
            pages=self.pages))

        art = Article(title=self.title, 
                      year=self.year, 
                      authors=self.namelist, 
                      journal=self.journal,
                      volume=self.volume,
                      number=self.number,
                      pages=self.pages)
        self.assertEqual(art.__str__(), "{authors}. {year}. {title}. <i>{journal}</i> {volume}({number}). {pages}.".format(
            authors=self.namelist, 
            year=self.year, 
            title=self.title, 
            journal=self.journal,
            volume=self.volume,
            number=self.number,
            pages=self.pages))

class TestBook(unittest.TestCase):
    name1 = Person(first="Jürgen", last="Münster")
    namelist = PersonList(name1)
    editorlist = EditorList(name1)

    title = "test book"
    year = 1999
    publisher = "publishing"
    address = "location"
    series = "series"
    number = 1   
    
    def test_init(self):
        self.assertRaises(ValueError, Book, 
            kwargs={"title": self.title, 
                    "authors": self.namelist, 
                    "year": self.year, 
                    "publisher": self.publisher})
        self.assertRaises(ValueError, Book, 
            kwargs={"title": self.title, 
                    "authors": self.namelist, 
                    "year": self.year, 
                    "address": self.address})
        self.assertRaises(ValueError, Book, 
            kwargs={"title": self.title, 
                    "authors": self.namelist, 
                    "address": self.address, 
                    "publisher": self.publisher})
        self.assertRaises(ValueError, Book, 
            kwargs={"title": self.title, 
                    "address": self.address, 
                    "year": self.year, 
                    "publisher": self.publisher})

        self.assertRaises(ValueError, Book, 
            kwargs={"authors": self.namelist, 
                    "address": self.address, 
                    "year": self.year, 
                    "publisher": self.publisher})

        # no exception expected:
        Book(title=self.title, 
            year=self.year, 
            authors=self.namelist,
            publisher=self.publisher,
            address=self.address)
        
        # no exception expected:
        Book(title=self.title, 
            year=self.year, 
            editors=self.editorlist,
            publisher=self.publisher,
            address=self.address)

        # in series:
        Book(authors=self.namelist,
             year=self.year,
             title=self.title,
             series=self.series,
             publisher=self.publisher,
             address=self.address)

        # in series with number
        Book(authors=self.namelist,
             year=self.year,
             title=self.title,
             series=self.series,
             number=self.number,
             publisher=self.publisher,
             address=self.address)

        # number without series is not allowed:
        self.assertRaises(ValueError, Book,
            kwargs={"authors": self.namelist, 
                    "year": self.year, 
                    "title": self.title,
                    "number": self.number,
                    "address": self.address, 
                    "publisher": self.publisher})
        
        # editors and authors at the same time are not allowed:
        self.assertRaises(ValueError, Book,
            kwargs={"authors": self.namelist, 
                    "title": self.title,
                    "editors": self.editorlist,
                    "address": self.address, 
                    "year": self.year, 
                    "publisher": self.publisher})
            
    def test_get_book_title(self):
        # book not in series:
        book = Book(title=self.title, 
                    year=self.year, 
                    authors=self.namelist, 
                    publisher=self.publisher,
                    address=self.address)
        self.assertEqual(book.get_book_title(), "<i>{title}</i>".format(
            title=self.title))
        
        # book in series:
        book = Book(title=self.title, 
                    year=self.year, 
                    authors=self.namelist, 
                    series=self.series,
                    publisher=self.publisher,
                    address=self.address)
        self.assertEqual(book.get_book_title(), "<i>{title}</i> ({series})".format(
            title=self.title,
            series=self.series))

        # book in series with number:
        book = Book(title=self.title, 
                    year=self.year, 
                    authors=self.namelist, 
                    series=self.series,
                    number=self.number,
                    publisher=self.publisher,
                    address=self.address)
        self.assertEqual(book.get_book_title(), "<i>{title}</i> ({series} {number})".format(
            title=self.title,
            series=self.series,
            number=self.number))
        
    def test_get_publishing_information(self):
        # only publisher:
        book = Book(title=self.title, 
                    year=self.year, 
                    authors=self.namelist, 
                    publisher=self.publisher)
        self.assertEqual(book.get_publishing_information(), "{publisher}".format(
            publisher=self.publisher))
        
        # publisher with address:
        book = Book(title=self.title, 
                    year=self.year, 
                    authors=self.namelist, 
                    publisher=self.publisher,
                    address=self.address)
        self.assertEqual(book.get_publishing_information(), "{address}: {publisher}".format(
            address=self.address,
            publisher=self.publisher))

    def test_str(self):
        book = Book(title=self.title, 
                    year=self.year, 
                    authors=self.namelist, 
                    publisher=self.publisher,
                    address=self.address)
        self.assertEqual(book.__str__(), "{authors}. {year}. {tit}. {pub}.".format(
            authors=self.namelist, 
            year=self.year, 
            tit=book.get_book_title(),
            pub=book.get_publishing_information()))

        # book with editors:
        book = Book(title=self.title, 
                    year=self.year, 
                    editors=self.editorlist, 
                    publisher=self.publisher,
                    address=self.address)
        self.assertEqual(book.__str__(), "{editors}. {year}. {tit}. {pub}.".format(
            editors=self.editorlist, 
            year=self.year, 
            tit=book.get_book_title(),
            pub=book.get_publishing_information()))

class TestInCollection(unittest.TestCase):
    name1 = Person(first="Jürgen", last="Münster")
    name2 = Person(first="John", middle=["William"], last="Doe")
    namelist = PersonList(name1)
    editorlist = EditorList(name2)

    contributiontitle = "contribution"
    title = "test book"
    year = 1999
    publisher = "publishing"
    address = "location"
    series = "series"
    number = 1   
    pages = "1-42"
    
    def test_validate(self):
        self.assertRaises(ValueError, InCollection.validate, 
            kwargs={"title": self.title, 
                    "contributiontitle": self.contributiontitle,
                    "year": self.year, 
                    "authors": self.namelist,
                    "number": self.number})
    
    def test_init(self):
        self.assertRaises(ValueError, InCollection, 
            kwargs={"title": self.title, 
                    "authors": self.namelist, 
                    "year": self.year, 
                    "publisher": self.publisher})

        # no exception expected:
        InCollection(title=self.title, 
            contributiontitle=self.contributiontitle,
            authors=self.namelist, 
            year=self.year, 
            publisher=self.publisher)
        
        InCollection(title=self.title, 
            contributiontitle=self.contributiontitle,
            authors=self.namelist, 
            year=self.year, 
            address=self.address,
            publisher=self.publisher)
        
        InCollection(title=self.title, 
            contributiontitle=self.contributiontitle,
            authors=self.namelist, 
            year=self.year, 
            publisher=self.publisher,
            pages=self.pages)

        InCollection(title=self.title, 
            contributiontitle=self.contributiontitle,
            authors=self.namelist, 
            year=self.year, 
            address=self.address,
            publisher=self.publisher,
            pages=self.pages)

    def test_get_source_information(self):
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            publisher=self.publisher)
        self.assertEqual(coll.get_source_information(), "In {tit}".format(
            tit=coll.get_book_title()))
        
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            editors=self.editorlist,
                            publisher=self.publisher)
        self.assertEqual(coll.get_source_information(), "In {editors}, {tit}".format(
            editors=self.editorlist.get_names(),
            tit=coll.get_book_title()))
        
            

    def test_str(self):
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            publisher=self.publisher)
        self.assertEqual(coll.__str__(), "{authors}. {year}. {contribution}. {source}. {pub}.".format(
            authors=self.namelist.get_names(),
            year=self.year,
            contribution=self.contributiontitle,
            source=coll.get_source_information(),
            pub=coll.get_publishing_information()))
                        
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            editors=self.editorlist,
                            publisher=self.publisher)
        self.assertEqual(coll.__str__(), "{authors}. {year}. {contribution}. {source}. {pub}.".format(
            authors=self.namelist.get_names(),
            year=self.year,
            contribution=self.contributiontitle,
            source=coll.get_source_information(),
            pub=coll.get_publishing_information()))
                        
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            pages=self.pages,
                            publisher=self.publisher)
        self.assertEqual(coll.__str__(), "{authors}. {year}. {contribution}. {source}, {pages}. {pub}.".format(
            authors=self.namelist.get_names(),
            year=self.year,
            contribution=self.contributiontitle,
            source=coll.get_source_information(),
            pages=self.pages,
            pub=coll.get_publishing_information()))
                        


if __name__ == '__main__':
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestPerson),
        unittest.TestLoader().loadTestsFromTestCase(TestPersonList),
        unittest.TestLoader().loadTestsFromTestCase(TestEditorList),
        unittest.TestLoader().loadTestsFromTestCase(TestReference),
        unittest.TestLoader().loadTestsFromTestCase(TestArticle),
        unittest.TestLoader().loadTestsFromTestCase(TestBook),
        unittest.TestLoader().loadTestsFromTestCase(TestInCollection),
        ])
    unittest.TextTestRunner().run(suite)

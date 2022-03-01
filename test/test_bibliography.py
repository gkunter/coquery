# -*- coding: utf-8 -*-
""" This module tests the bibliography module."""
from coquery.bibliography import (
    Reference, Article, Book, InCollection,
    Person, PersonList, EditorList)
from test.testcase import CoqTestCase, run_tests


class TestPerson(CoqTestCase):
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
        self.assertTrue(isinstance(name.first, str))
        self.assertTrue(isinstance(name.middle, list))
        self.assertTrue(isinstance(name.last, str))

    def test_repr(self):
        name = Person(first="Jürgen", middle=["Otto", "Emil"],
                      prefix="Dr.", suffix="MA", last="Münster")
        # The order of the named arguments in __repr__ is not fixed, so we
        # test equality by sorting all the characters in the strings:
        self.assertEqual(
            sorted(name.__repr__()),
            sorted("Person(first='Jürgen', middle=['Otto', 'Emil'], "
                   "prefix='Dr.', suffix='MA', last='Münster')"))

    def test_name_str(self):
        name = Person(first="Jürgen", middle=["Otto", "Emil"],
                      prefix="Dr.", suffix="MA", last="Münster")
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

        name = Person(first="Jürgen", middle=["Otto", "Emil"],
                      prefix="Dr.", suffix="MA", last="Münster")
        self.assertEqual(name.full_name(), "Dr. Jürgen Otto Emil Münster MA")
        self.assertEqual(name.full_name("middle"),
                         "Dr. Jürgen O. E. Münster MA")
        self.assertEqual(name.full_name("all"), "Dr. J. O. E. Münster MA")

    def test_bibliographic_name(self):
        name = Person(first="Jürgen", last="Münster")
        self.assertEqual(name.bibliographic_name(), "Münster, Jürgen")
        self.assertEqual(name.bibliographic_name("middle"), "Münster, Jürgen")
        self.assertEqual(name.bibliographic_name("all"), "Münster, J.")

        name = Person(first="Jürgen", middle="M.", last="Münster")
        self.assertEqual(name.bibliographic_name(), "Münster, Jürgen M.")
        self.assertEqual(name.bibliographic_name("middle"),
                         "Münster, Jürgen M.")
        self.assertEqual(name.bibliographic_name("all"), "Münster, J. M.")

        name = Person(first="Jürgen", middle=["Otto", "Emil"],
                      prefix="Dr.", suffix="MA", last="Münster")
        self.assertEqual(name.bibliographic_name(),
                         "Münster MA, Dr. Jürgen Otto Emil")
        self.assertEqual(name.bibliographic_name("middle"),
                         "Münster MA, Dr. Jürgen O. E.")
        self.assertEqual(name.bibliographic_name("all"),
                         "Münster MA, Dr. J. O. E.")


class TestPersonList(CoqTestCase):
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
        self.assertEqual(authors.__repr__(),
                         "PersonList({})".format(self.name1.__repr__()))
        authors = PersonList(self.name1, self.name2)
        self.assertEqual(authors.__repr__(), "PersonList({}, {})".format(
            self.name1.__repr__(), self.name2.__repr__()))

    def test_str(self):
        authors = PersonList()
        self.assertEqual(authors.__str__(), "")

        # one-person list:
        authors = PersonList(self.name1)
        self.assertEqual(authors.names(), self.name1.bibliographic_name())

        # two-persons list:
        authors = PersonList(self.name1, self.name2)
        self.assertEqual(authors.names(), "{}, and {}".format(
            self.name1.bibliographic_name(), self.name2.full_name()))

        # three-persons list:
        authors = PersonList(self.name1, self.name2, self.name3)
        self.assertEqual(authors.names(),
                         "{}, {}, and {}".format(
                             self.name1.bibliographic_name(),
                             self.name2.full_name(),
                             self.name3.full_name()))

    def test_names_separation(self):

        # change separation of two names:
        authors = PersonList(self.name1, self.name2)
        self.assertEqual(authors.names(two_sep=" & "),
                         "{} & {}".format(self.name1.bibliographic_name(),
                                          self.name2.full_name()))

        # change separation of three names:
        authors = PersonList(self.name1, self.name2, self.name3)
        # two_sep should not have an effect:
        self.assertEqual(authors.names(two_sep=" & "),
                         "{}, {}, and {}".format(
                             self.name1.bibliographic_name(),
                             self.name2.full_name(),
                             self.name3.full_name()))

        # sep should have an effect:
        self.assertEqual(authors.names(sep=" & "),
                         "{} & {}, and {}".format(
                             self.name1.bibliographic_name(),
                             self.name2.full_name(),
                             self.name3.full_name()))

        self.assertEqual(authors.names(last_sep=" & "),
                         "{}, {} & {}".format(self.name1.bibliographic_name(),
                                              self.name2.full_name(),
                                              self.name3.full_name()))

    def test_names_name_orders(self):
        authors = PersonList(self.name1, self.name2, self.name3)
        # start first name with first name:
        self.assertEqual(authors.names(mode_first="first"),
                         "Jürgen Münster, John William Doe, and Juan Pérez")
        # start other names with last names:
        self.assertEqual(
            authors.names(mode_others="last"),
            "Münster, Jürgen, Doe, John William, and Pérez, Juan")

    def test_names_initialization(self):
        authors = PersonList(self.name1, self.name2, self.name3)
        # only middle as initials:
        self.assertEqual(authors.names(initials="middle"),
                         "Münster, Jürgen, John W. Doe, and Juan Pérez")
        # first and middle as initials:
        self.assertEqual(
            authors.names(initials="all"),
            "Münster, J., J. W. Doe, and J. Pérez")


class TestEditorList(CoqTestCase):
    name1 = Person(first="Jürgen", last="Münster")
    name2 = Person(first="John", middle=["William"], last="Doe")
    name3 = Person(first="Juan", last="Pérez")

    def test_repr(self):
        namelist = EditorList(self.name1, self.name2)
        self.assertEqual(namelist.__repr__(), "EditorList({}, {})".format(
            self.name1.__repr__(), self.name2.__repr__()))

    def test_names(self):
        # one editor:
        namelist = EditorList(self.name1)
        self.assertEqual(namelist.names(), "{} (ed.)".format(
            self.name1.bibliographic_name()))

        # two editors:
        namelist = EditorList(self.name1, self.name2)
        self.assertEqual(
            namelist.names(),
            "{}, and {} (eds.)".format(self.name1.bibliographic_name(),
                                       self.name2.full_name()))

        # three editors:
        namelist = EditorList(self.name1, self.name2, self.name3)
        self.assertEqual(
            namelist.names(),
            "{}, {}, and {} (eds.)".format(self.name1.bibliographic_name(),
                                           self.name2.full_name(),
                                           self.name3.full_name()))

    def test_change_labels(self):
        # one editor:
        namelist = EditorList(self.name1)
        self.assertEqual(
            namelist.names(one_editor="(Hg.)"),
            "{} (Hg.)".format(self.name1.bibliographic_name()))
        # two_editors should have no effect:
        self.assertEqual(
            namelist.names(two_editors="(Hgg.)"),
            "{} (ed.)".format(self.name1.bibliographic_name()))
        # many_editors should have no effect:
        self.assertEqual(
            namelist.names(many_editors="(Hgg.)"),
            "{} (ed.)".format(self.name1.bibliographic_name()))

        # two editors:
        namelist = EditorList(self.name1, self.name2)
        self.assertEqual(
            namelist.names(two_editors="(Hgg.)"),
            "{}, and {} (Hgg.)".format(self.name1.bibliographic_name(),
                                       self.name2.full_name()))
        # one_editor have no effect:
        self.assertEqual(
            namelist.names(one_editor="(Hgg.)"),
            "{}, and {} (eds.)".format(self.name1.bibliographic_name(),
                                       self.name2.full_name()))
        # many_editors should have no effect:
        self.assertEqual(
            namelist.names(many_editors="(Hgg.)"),
            "{}, and {} (eds.)".format(self.name1.bibliographic_name(),
                                       self.name2.full_name()))

        # three editors:
        namelist = EditorList(self.name1, self.name2, self.name3)
        self.assertEqual(
            namelist.names(many_editors="(Hgg.)"),
            "{}, {}, and {} (Hgg.)".format(self.name1.bibliographic_name(),
                                           self.name2.full_name(),
                                           self.name3.full_name()))
        # one_editor have no effect:
        self.assertEqual(
            namelist.names(one_editor="(Hgg.)"),
            "{}, {}, and {} (eds.)".format(self.name1.bibliographic_name(),
                                           self.name2.full_name(),
                                           self.name3.full_name()))

        # two_editors should have no effect:
        self.assertEqual(
            namelist.names(two_editors="(Hgg.)"),
            "{}, {}, and {} (eds.)".format(self.name1.bibliographic_name(),
                                           self.name2.full_name(),
                                           self.name3.full_name()))


class TestReference(CoqTestCase):
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
        Reference(title=self.title,
                  authors=self.namelist,
                  year=self.year,
                  journal="Journal")

    def test_required(self):
        ref = Reference(title=self.title, authors=self.namelist)
        self.assertEqual(ref.required_properties(), ["title"])

    def test_validate(self):
        # expect a ValueError if no title is given:
        self.assertRaises(ValueError,
                          Reference.validate,
                          {"author": self.namelist})
        # no ValueError expected:
        Reference.validate({"title": self.title})

    def test_repr_1(self):
        ref = Reference(title=self.title)
        frm = "Reference(title={title})"
        self.assertEqual(ref.__repr__(),
                         frm.format(title=self.title.__repr__()))

    def test_repr_2(self):
        ref = Reference(title=self.title, authors=self.namelist)
        frm = "Reference(authors={authors}, title={title})"
        self.assertEqual(ref.__repr__(),
                         frm.format(authors=self.namelist.__repr__(),
                                    title=self.title.__repr__()))

    def test_repr_3(self):
        ref = Reference(title=self.title, year=self.year)
        frm = "Reference(title={title}, year={year})"
        self.assertEqual(ref.__repr__(),
                         frm.format(title=self.title.__repr__(),
                                    year=self.year.__repr__()))

    def test_repr_4(self):
        ref = Reference(title=self.title,
                        year=self.year,
                        authors=self.namelist)
        frm = "Reference(authors={authors}, title={title}, year={year})"
        self.assertEqual(ref.__repr__(),
                         frm.format(title=self.title.__repr__(),
                                    authors=self.namelist.__repr__(),
                                    year=self.year.__repr__()))

    def test_str_1(self):
        ref = Reference(title=self.title)
        frm = "<i>{title}</i>."
        self.assertEqual(ref.__str__(),
                         frm.format(title=self.title))

    def test_str_2(self):
        ref = Reference(title=self.title, authors=self.namelist)
        frm = "{authors}. <i>{title}</i>."
        self.assertEqual(ref.__str__(),
                         frm.format(authors=self.namelist.names(),
                                    title=self.title))

    def test_str_3(self):
        ref = Reference(title=self.title, year=self.year)
        frm = "{year}. <i>{title}</i>."

        self.assertEqual(ref.__str__(),
                         frm.format(year=self.year, title=self.title))

    def test_str_4(self):
        ref = Reference(title=self.title,
                        year=self.year,
                        authors=self.namelist)
        frm = "{authors}. {year}. <i>{title}</i>."

        self.assertEqual(ref.__str__(),
                         frm.format(authors=self.namelist.names(),
                                    year=self.year,
                                    title=self.title))


class TestArticle(CoqTestCase):
    name1 = Person(first="Jürgen", last="Münster")

    title = "test article"
    year = 1999
    namelist = PersonList(name1)
    journal = "journal"
    volume = 123
    number = 1
    pages = "1-42"

    def test_init(self):
        self.assertRaises(ValueError,
                          Article,
                          kwargs={"title": self.title})

        self.assertRaises(ValueError,
                          Article,
                          kwargs={"title": self.title,
                                  "authors": self.namelist})

        self.assertRaises(ValueError,
                          Article,
                          kwargs={"title": self.title,
                                  "year": self.year})

        self.assertRaises(ValueError,
                          Article,
                          kwargs={"title": self.title,
                                  "journal": self.journal})

        self.assertRaises(ValueError,
                          Article,
                          kwargs={"title": self.title,
                                  "authors": self.namelist,
                                  "year": self.year})

        self.assertRaises(ValueError,
                          Article,
                          kwargs={"title": self.title,
                                  "authors": self.namelist,
                                  "journal": self.journal})

        self.assertRaises(ValueError,
                          Article,
                          kwargs={"title": self.title,
                                  "year": self.year,
                                  "journal": self.journal})

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
        self.assertRaises(ValueError,
                          Article,
                          kwargs={"title": self.title,
                                  "year": self.year,
                                  "journal": self.journal,
                                  "authors": self.namelist,
                                  "number": self.number})

    def test_validate(self):
        self.assertRaises(ValueError,
                          Article.validate,
                          kwargs={"title": self.title,
                                  "year": self.year,
                                  "journal": self.journal,
                                  "authors": self.namelist,
                                  "number": self.number})

    def test_str_1(self):
        """
        Test __str__() for an article when the following elements are given:

        authors, title, year, journal

        """
        dct = dict(title=self.title,
                   year=self.year,
                   authors=self.namelist,
                   journal=self.journal)
        frm = "{authors}. {year}. {title}. <i>{journal}</i>."

        s1 = Article(**dct).__str__()
        s2 = frm.format(**dct)

        self.assertEqual(s1, s2)

    def test_str_2(self):
        """
        Test __str__() for an article when the following elements are given:

        authors, title, year, journal, volume

        """
        dct = dict(title=self.title,
                   year=self.year,
                   authors=self.namelist,
                   journal=self.journal,
                   volume=self.volume)
        frm = "{authors}. {year}. {title}. <i>{journal}</i> {volume}."

        s1 = Article(**dct).__str__()
        s2 = frm.format(**dct)

        self.assertEqual(s1, s2)

    def test_str_3(self):
        """
        Test __str__() for an article when the following elements are given:

        authors, title, year, journal, volume, number

        """
        dct = dict(title=self.title,
                   year=self.year,
                   authors=self.namelist,
                   journal=self.journal,
                   volume=self.volume,
                   number=self.number)
        frm = ("{authors}. {year}. {title}. <i>{journal}</i> "
               "{volume}({number}).")

        s1 = Article(**dct).__str__()
        s2 = frm.format(**dct)

        self.assertEqual(s1, s2)

    def test_str_4(self):
        """
        Test __str__() for an article when the following elements are given:

        authors, title, year, journal, pages

        """
        dct = dict(title=self.title,
                   year=self.year,
                   authors=self.namelist,
                   journal=self.journal,
                   pages=self.pages)
        frm = "{authors}. {year}. {title}. <i>{journal}</i>. {pages}."

        s1 = Article(**dct).__str__()
        s2 = frm.format(**dct)

        self.assertEqual(s1, s2)

    def test_str_5(self):
        """
        Test __str__() for an article when the following elements are given:

        authors, title, year, journal, volume, pages

        """
        dct = dict(title=self.title,
                   year=self.year,
                   authors=self.namelist,
                   journal=self.journal,
                   volume=self.volume,
                   pages=self.pages)
        frm = ("{authors}. {year}. {title}. <i>{journal}</i> {volume}. "
               "{pages}.")

        s1 = Article(**dct).__str__()
        s2 = frm.format(**dct)

        self.assertEqual(s1, s2)

    def test_str_6(self):
        """
        Test __str__() for an article when the following elements are given:

        authors, title, year, journal, volume, number, pages

        """
        dct = dict(title=self.title,
                   year=self.year,
                   authors=self.namelist,
                   journal=self.journal,
                   volume=self.volume,
                   number=self.number,
                   pages=self.pages)
        frm = ("{authors}. {year}. {title}. <i>{journal}</i> "
               "{volume}({number}). {pages}.")

        s1 = Article(**dct).__str__()
        s2 = frm.format(**dct)

        self.assertEqual(s1, s2)


class TestBook(CoqTestCase):
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
        self.assertRaises(ValueError,
                          Book,
                          kwargs={"title": self.title,
                                  "authors": self.namelist,
                                  "year": self.year,
                                  "publisher": self.publisher})

        self.assertRaises(ValueError,
                          Book,
                          kwargs={"title": self.title,
                                  "authors": self.namelist,
                                  "year": self.year,
                                  "address": self.address})

        self.assertRaises(ValueError,
                          Book,
                          kwargs={"title": self.title,
                                  "authors": self.namelist,
                                  "address": self.address,
                                  "publisher": self.publisher})

        self.assertRaises(ValueError,
                          Book,
                          kwargs={"title": self.title,
                                  "address": self.address,
                                  "year": self.year,
                                  "publisher": self.publisher})

        self.assertRaises(ValueError,
                          Book,
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
        self.assertRaises(ValueError,
                          Book,
                          kwargs={"authors": self.namelist,
                                  "year": self.year,
                                  "title": self.title,
                                  "number": self.number,
                                  "address": self.address,
                                  "publisher": self.publisher})

        # editors and authors at the same time are not allowed:
        self.assertRaises(ValueError,
                          Book,
                          kwargs={"authors": self.namelist,
                                  "title": self.title,
                                  "editors": self.editorlist,
                                  "address": self.address,
                                  "year": self.year,
                                  "publisher": self.publisher})

    def test_book_title_1(self):
        """
        Test title formatting for a stand-alone publication.
        """
        book = Book(title=self.title,
                    year=self.year,
                    authors=self.namelist,
                    publisher=self.publisher,
                    address=self.address)
        frm = "<i>{title}</i>"
        self.assertEqual(book.book_title(),
                         frm.format(title=self.title))

    def test_book_title_2(self):
        """
        Test title formatting for a book from a series.
        """
        book = Book(title=self.title,
                    year=self.year,
                    authors=self.namelist,
                    series=self.series,
                    publisher=self.publisher,
                    address=self.address)
        frm = "<i>{title}</i> ({series})"
        self.assertEqual(book.book_title(),
                         frm.format(title=self.title, series=self.series))

    def test_book_title_3(self):
        """
        Test title formatting for a book from a numbered series.
        """
        # book in series with number:
        book = Book(title=self.title,
                    year=self.year,
                    authors=self.namelist,
                    series=self.series,
                    number=self.number,
                    publisher=self.publisher,
                    address=self.address)
        frm = "<i>{title}</i> ({series} {number})"
        self.assertEqual(book.book_title(),
                         frm.format(title=self.title,
                                    series=self.series,
                                    number=self.number))

    def test_publishing_information_1(self):
        """
        Test the publisher information if only the publisher, but no address
        is provided.
        """
        book = Book(title=self.title,
                    year=self.year,
                    authors=self.namelist,
                    publisher=self.publisher)
        frm = "{publisher}"
        self.assertEqual(book.publishing_information(),
                         frm.format(publisher=self.publisher))

    def test_publishing_information_2(self):
        """
        Test the publisher information if the publisher and an address are
        provided.
        """
        book = Book(title=self.title,
                    year=self.year,
                    authors=self.namelist,
                    publisher=self.publisher,
                    address=self.address)
        frm = "{address}: {publisher}"
        self.assertEqual(book.publishing_information(),
                         frm.format(address=self.address,
                                    publisher=self.publisher))

    def test_str_1(self):
        book = Book(title=self.title,
                    year=self.year,
                    authors=self.namelist,
                    publisher=self.publisher,
                    address=self.address)
        frm = "{authors}. {year}. {title}. {pub}."
        self.assertEqual(book.__str__(),
                         frm.format(authors=self.namelist,
                                    year=self.year,
                                    title=book.book_title(),
                                    pub=book.publishing_information()))

    def test_str_2(self):
        """
        Test the __str__ method of a book with editors instead of authors.
        """
        book = Book(title=self.title,
                    year=self.year,
                    editors=self.editorlist,
                    publisher=self.publisher,
                    address=self.address)
        frm = "{editors}. {year}. {title}. {pub}."
        self.assertEqual(book.__str__(),
                         frm.format(editors=self.editorlist,
                                    year=self.year,
                                    title=book.book_title(),
                                    pub=book.publishing_information()))


class TestInCollection(CoqTestCase):
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
        self.assertRaises(ValueError,
                          InCollection.validate,
                          kwargs={"title": self.title,
                                  "contributiontitle": self.contributiontitle,
                                  "year": self.year,
                                  "authors": self.namelist,
                                  "number": self.number})

    def test_init(self):
        """
        Test if InCollection class initialization is sensitive to required
        information.
        """

        # the following class instantiations count as passed tests if no
        # exception is raised:
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

        # this should raise an exception, because no contribution title is
        # provided:
        self.assertRaises(ValueError, InCollection,
                          kwargs={"title": self.title,
                                  "authors": self.namelist,
                                  "year": self.year,
                                  "publisher": self.publisher})

    def test_source_information_1(self):
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            publisher=self.publisher)
        self.assertEqual(coll.source_information(),
                         "In {title}".format(title=coll.book_title()))

    def test_source_information_2(self):
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            editors=self.editorlist,
                            publisher=self.publisher)
        self.assertEqual(coll.source_information(),
                         "In {editors}, {title}".format(
                             editors=self.editorlist.names(),
                             title=coll.book_title()))

    def test_str_1(self):
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            publisher=self.publisher)
        frm = "{authors}. {year}. {contribution}. {source}. {pub}."
        self.assertEqual(coll.__str__(),
                         frm.format(authors=self.namelist.names(),
                                    year=self.year,
                                    contribution=self.contributiontitle,
                                    source=coll.source_information(),
                                    pub=coll.publishing_information()))

    def test_str_2(self):
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            editors=self.editorlist,
                            publisher=self.publisher)
        frm = "{authors}. {year}. {contribution}. {source}. {pub}."
        self.assertEqual(coll.__str__(),
                         frm.format(authors=self.namelist.names(),
                                    year=self.year,
                                    contribution=self.contributiontitle,
                                    source=coll.source_information(),
                                    pub=coll.publishing_information()))

    def test_str_3(self):
        coll = InCollection(authors=self.namelist,
                            year=self.year,
                            contributiontitle=self.contributiontitle,
                            title=self.title,
                            pages=self.pages,
                            publisher=self.publisher)
        frm = "{authors}. {year}. {contribution}. {source}, {pages}. {pub}."
        self.assertEqual(coll.__str__(),
                         frm.format(authors=self.namelist.names(),
                                    year=self.year,
                                    contribution=self.contributiontitle,
                                    source=coll.source_information(),
                                    pages=self.pages,
                                    pub=coll.publishing_information()))


provided_tests = [TestPerson, TestPersonList, TestEditorList,
                  TestReference, TestArticle, TestBook, TestInCollection]


def main():
    run_tests(provided_tests)


if __name__ == '__main__':
    main()

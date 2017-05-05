# -*- coding: utf-8 -*-
"""
bibliography.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import warnings
import sys


# Create a tuple containing the available string types
if sys.version_info < (3, 0):
    STRING_TYPES = (basestring, )
else:
    STRING_TYPES = (str, )

MSG_WARN_FULL_NAME_MODE = (
    "Unknown mode '{}' for Name.full_name(), assuming 'none' instead")

MSG_PERSONLIST_ILLEGAL_MODE_FIRST = (
    "Illegal value '{}' for parameter 'mode_first'.")
MSG_PERSONLIST_ILLEGAL_MODE_OTHERS = (
    "Illegal value '{}' for parameter 'mode_others'.")

MSG_REFERENCE_MISSING_PROPERTY = (
    "Missing properties for entry type '{}': {}")

MSG_BOOK_NO_SERIES = (
    "Book: you have specified a series number, but no series name.")
MSG_BOOK_EDITOR_AND_AUTHOR = (
    "Book: you have specified both author(s) and editor(s).")
MSG_BOOK_NEITHER_EDITOR_NOR_AUTHOR = (
    "Book: you have specified neither author(s) nor editor(s).")

MSG_INCOLLECTION_NO_SERIES_NAME = (
    "InCollection: you have specified a series number, but no series name.")

MSG_ARTICLE_NO_VOLUME = (
    "Article: you have specified a journal number, but no journal volume.")


class Person(object):
    """
    This class defines a person that can be used in a bibliographic reference.

    The approach taken here is -- primarily out of ignorance, but also for
    practical reasons -- to assume a mostly European naming scheme. A person
    has a first (given) name, any number of middle names (including no middle
    name), and a last (family) name. The last name is the name used in
    bibliographic references to refer to the person. It is also the name
    under which publications by the author would be ordered in a list of
    references, unless a `sortby` name is provided.

    Person names can also include prefixes and suffixes (such as honorary
    titles) which precede and follow the name, respectively.
    """
    def __init__(self, first=None, middle=None, last=None,
                 prefix=None, suffix=None, sortby=None):
        self.first = first
        self.last = last
        if isinstance(middle, STRING_TYPES):
            self.middle = [middle]
        elif isinstance(middle, list):
            self.middle = middle
        else:
            self.middle = []
            # raise ValueError(MSG_PERSON_ILLEGAL_MIDDLE_NAME_TYPE)
        self.prefix = prefix
        self.suffix = suffix
        self.sortby = sortby

    def __repr__(self):
        l = []
        for x in ["first", "middle", "last", "prefix", "suffix", "sortby"]:
            attr = getattr(self, x)
            if attr:
                if isinstance(attr, list):
                    attr_values = ", ".join(["'{}'".format(m) for m in attr])
                    l.append("{}=[{}]".format(x, attr_values))
                else:
                    l.append("{}='{}'".format(x, attr))
        return "Person({})".format(", ".join(l))

    def __str__(self, **kwargs):
        return self.full_name(**kwargs)

    @staticmethod
    def _join(l, sep=" "):
        """
        Return a string with the list elements separated by ``sep``

        This function is similar to ``sep.join(l)``, but it provides type
        conversion to string of the list elements, and removes empty
        elements.

        Parameters
        ----------
        l : list
            A list that is to be joined
        sep : string
            The string or character that is used to join the elements

        Returns
        -------
        s : string
            The joined string
        """
        return sep.join(["{}".format(x) for x in l if x])

    def _middlename(self, mode="full"):
        """
        Return the middle names either initialized (if mode is "initials") or
        in their full form (if mode is "full").

        Parameters
        ----------
        mode :
        """
        if not hasattr(self, "middle"):
            return None
        if mode not in ["initials", "full"]:
            s = "Unknown mode '{}' for Name.middlename(), assuming 'full' instead".format(mode)
            warnings.warn(s)
            mode = "full"

        if mode == "full":
            return self._join(self.middle)
        elif mode == "initials":
            return self._join(["{}.".format(x[:1]) for x in self.middle])

    def full_name(self, mode='none'):
        """
        Get the full name of the person.

        Parameters
        ----------
        mode : string
            'none' (the default) if no initials are used, 'middle' if the
            middle names are given in initials, 'all' if all names except
            the last are given in initials

        Returns
        -------
        s : string
            The full name of the person, with name constituents in the
            following order:

            prefix - first name - middle name(s) - last name - suffix
        """
        if mode not in ["none", "middle", "all"]:
            warnings.warn(MSG_WARN_FULL_NAME_MODE.format(mode))
            mode = "none"
        if mode == "none":
            first = self.first
            middle = self._middlename("full")
        elif mode == "middle":
            first = self.first
            middle = self._middlename("initials")
        else:
            first = "{}.".format(self.first[0])
            middle = self._middlename("initials")

        return self._join([self.prefix, first, middle, self.last, self.suffix])

    def bibliographic_name(self, initials="none"):
        """
        Get the name of the person, arranged by last name

        This method returns the name of the person in a form that would be
        useable in a bibliography: the last name comes first, then, after a
        comma, the first and middle name.

        Returns
        -------
        s : string
            The name of the person, with name constituents in the
            following order:

            last name - suffix, prefix - first name - middle name(s)
        """
        if initials == "none":
            S = "{}, {}".format(
                self._join([self.last,
                            self.suffix]),
                self._join([self.prefix,
                            self.first,
                            self._join(getattr(self, "middle", []))]))
        elif initials == "middle":
            S = "{}, {}".format(
                self._join([self.last,
                            self.suffix]),
                self._join([self.prefix,
                            self.first,
                            self._join(["{}.".format(x[:1]) for x
                                        in getattr(self, "middle", [])])]))
        else:
            S = "{}, {}".format(
                self._join([self.last,
                            self.suffix]),
                self._join([self.prefix,
                            "{}.".format(self.first[:1]),
                            self._join(["{}.".format(x[:1]) for x
                                        in getattr(self, "middle", [])])]))
        return S.strip(" ,")


class PersonList(object):
    """
    This class defines a list of Persons which can be used in a bibliographic
    entry.
    """

    def __init__(self, *args):
        """
        Initialize the name list.

        Parameters
        ----------
        *args : any number of Person objects
        """
        self._list = args

    def __repr__(self):
        people = [x.__repr__() for x in self._list]
        return "PersonList({})".format(", ".join(people))

    def __str__(self, **kwargs):
        return self.get_names(**kwargs)

    def get_names(self, mode_first="last", mode_others="first",
                  sep=", ", two_sep=", and ", last_sep=", and ",
                  initials="none"):
        """
        Return the name(s) in a form suitable for a bibliography.

        Parameters
        ----------
        mode_first : string, either "last" or "first"
            If "last", the name of the first Person is given in the form
            "last name, first name(s)". If "first", the name of the first
            Person is given in the form "first name(s) last name(s)".

        mode_others : string, either "last" or "first"
            If "last", the names of any other other Person are given in the
            form "last name, first name(s)". If "first", they are given in the
            form "first name(s) last names".

        sep : string
            The character or string used to separate the Persons except the
            last Person.

        two_sep : string
            The character or string used to separate two Persons. If there is
            only one Person, `two_sep` is ignored. If there are more than two
            Persons, `two_sep` is ignored, and `sep` is used instead.

        last_sep : string
            The character or string used to separate the names of Persons
            the last Person. If there is only one Person, `last_sep` is
            ignored. If thare two Persons, `last_sep` is ignored and `two_sep`
            is used instead.

        initials : string, either "none", "middle", or "all", default: "none"
            'none' (the default) if no initials are used, 'middle' if the
            middle names are given in initials, 'all' if all names except
            the last are given in initials

        Returns
        -------
        s : string
            The name(s).
        """

        if not self._list:
            return ""

        if mode_first not in ["last", "first"]:
            s = MSG_PERSONLIST_ILLEGAL_MODE_FIRST.format(mode_first)
            raise ValueError(s)
        if mode_others not in ["last", "first"]:
            s = MSG_PERSONLIST_ILLEGAL_MODE_OTHERS.format(mode_others)
            raise ValueError(s)

        if mode_first == "first":
            first_name = self._list[0].full_name(initials)
        else:
            first_name = self._list[0].bibliographic_name(initials)

        if mode_others == "first":
            other_names = [x.full_name(initials) for x in self._list[1:]]
        else:
            other_names = [x.bibliographic_name(initials) for x
                           in self._list[1:]]

        if len(self._list) == 1:
            return first_name
        elif len(self._list) == 2:
            return "{first}{sep}{second}".format(
                first=first_name,
                sep=two_sep,
                second=other_names[0])
        else:
            return "{first}{sep}{next}{last_sep}{last}".format(
                first=first_name,
                sep=sep,
                next=sep.join(other_names[:-1]),
                last_sep=last_sep,
                last=other_names[-1])


class EditorList(PersonList):
    """
    This class defines a list of names that are the editors of a source.
    """
    def __repr__(self):
        people = [x.__repr__() for x in self._list]
        return "EditorList({})".format(", ".join(people))

    def get_names(self, one_editor="(ed.)", two_editors="(eds.)",
                  many_editors="(eds.)", **kwargs):
        """
        Return the name(s) in a form suitable for a bibliography.

        Parameters
        ----------
        one_editor : string
        two_editors : string
        many_editors : string
            The string placed after the name list (usually an abbreviation
            for 'editor').

        kwargs : dict
            Other parameters passed to PersonList.get_names()

        Returns
        -------
        s : string
            The name(s), followed by the suitable editor abbreviation string
        """
        s = super(EditorList, self).get_names(**kwargs)
        if len(self._list) == 1:
            return "{} {}".format(s, one_editor)
        elif len(self._list) == 2:
            return "{} {}".format(s, two_editors)
        else:
            return "{} {}".format(s, many_editors)


def stop(S):
    """
    Add a full stop, but only if the string doesn't end already in a
    full stop.
    """
    if isinstance(S, STRING_TYPES):
        return "{}.".format(S) if not S.endswith(".") else S
    else:
        return "{}.".format(S)


class Reference(object):
    """
    This class defines a minimal bibliographic reference.

    Properties
    ----------

    title: string
        The title of the reference

    authors: NameList (optional)
        A NameList of author names

    year: string (optional)
        The publication year.

    Reference is a minimal bibliographic entry. The property 'title' is
    required, and 'author' and 'year' are optional properties. Other types of
    bibliographic entries are specified by subclassing :class:`Reference`.

    :func:`__str__` returns a string representation of the reference that can
    be used in a bibliography. If you want to adjust the formatting of the
    entry, you can subclass Reference and overload :func:`__str__` to return
    the desired representation.
    """
    _class_name = "Reference"
    _required = ["title"]

    def __init__(self, **kwargs):
        """
        Initialize the reference.

        __init__() calls :func:`validate` to determine whether all required
        data are passed as named arguments. :func:`validate` raises a
        ValueError if any required argument is missing.
        """
        self.validate(kwargs)
        self.title = kwargs.get("title")
        try:
            self.authors = kwargs["authors"]
        except KeyError:
            pass
        try:
            self.year = kwargs["year"]
        except KeyError:
            pass

    @classmethod
    def required_properties(cls):
        """
        Return a list of property names that are required for this type of
        bibliographic reference.

        Returns
        -------
        req: list of strings
            A list containing all property names that are required.
        """
        return cls._required

    @classmethod
    def validate(cls, kwargs):
        """
        Validate the keyword arguments.

        This method tests whether all properties in cls.required_properties
        are present as keys in the dictionary ``kwargs``.

        Raises
        ------
        ValueError(MSG_REFERENCE_MISSING_PROPERTY)
            Raised if one or more required properties are missing.
        """
        missing = []
        for prop in cls.required_properties():
            if prop not in kwargs:
                missing.append(prop)
        if missing:
            s = MSG_REFERENCE_MISSING_PROPERTY.format(
                cls._class_name,
                ", ".join(missing))
            raise ValueError(s)

    def __repr__(self):
        l = []
        for x in dir(self):
            attr = getattr(self, x)
            if not x.startswith("_") and not hasattr(attr, "__call__"):
                if isinstance(attr, list):
                    missing = ["'{}'".format(m.__repr__()) for m in attr]
                    attr_repr = ", ".join(missing)
                    l.append("{}=[{}]".format(x, attr_repr))
                else:
                    l.append("{}={}".format(x, attr.__repr__()))
        return "{}({})".format(self._class_name, ", ".join(l))

    def __str__(self, **kwargs):
        title = self.title

        if hasattr(self, "authors") and hasattr(self, "year"):
            authors = self.authors.get_names(**kwargs)
            year = self.year
            return "{} {} <i>{}</i>.".format(stop(authors), stop(year), title)
        elif hasattr(self, "authors"):
            authors = self.authors.get_names(**kwargs)
            return "{} <i>{}</i>.".format(stop(authors), title)
        elif hasattr(self, "year"):
            year = self.year
            return "{} <i>{}</i>.".format(stop(year), title)
        else:
            return "<i>{}</i>.".format(title)


class Article(Reference):
    """
    This class defines an Article reference.

    The default format string of the Article class is:

    {authors}. {year}. {title}. <i>{journal}</i> {volume}({number}). {pages}.

    Properties
    ----------
    authors: NameList
        A list of authors

    title: string
        The title of the article

    year: string
        The year of publication

    journal: string
        The name of the journal

    volume: string (optional)
        The volume in which the article appeared

    number: string (optional)
        The number in which the article appeared. Can be None if the journal
        is not published in numbered issues.

    pages: string (optional)
        The pages of the article
    """
    _class_name = "Article"
    _required = ["authors", "year", "title", "journal"]

    def __init__(self, **kwargs):
        self.validate(kwargs)
        self.authors = kwargs["authors"]
        self.year = kwargs["year"]
        self.title = kwargs["title"]
        self.journal = kwargs["journal"]

        # optional arguments:
        try:
            self.volume = kwargs["volume"]
        except KeyError:
            pass
        try:
            self.number = kwargs["number"]
        except KeyError:
            pass
        try:
            self.pages = kwargs["pages"]
        except KeyError:
            pass

    @classmethod
    def validate(cls, kwargs):
        super(Article, cls).validate(kwargs)
        if "number" in kwargs and "volume" not in kwargs:
            raise ValueError(MSG_ARTICLE_NO_VOLUME)

    def __str__(self):
        if hasattr(self, "number"):
            vol = "{}({})".format(self.volume, self.number)
        elif hasattr(self, "volume"):
            vol = "{}".format(self.volume)
        else:
            vol = ""

        S = "{authors} {year} {title} <i>{journal}</i>".format(
            authors=stop(self.authors.get_names()),
            year=stop(self.year),
            title=stop(self.title),
            journal=self.journal)
        if vol:
            S = "{} {}".format(S, vol)
        if hasattr(self, "pages"):
            S = "{} {}".format(stop(S), self.pages)

        return "{}".format(stop(S))


class Book(Reference):
    """
    This class defines a Book reference.

    The default format string of the Book class is:

    {authors}. {year}. <i>{title}</i>. {address}: {publisher}.

    Books published in a series takes the form:

    {authors}. {year}. <i>{title}</i> ({series} {number}). {address}: {publisher}.

    Instead of authors, a list of editors can also be provided, but not both
    at the same time.

    Properties
    ----------
    authors: NameList
        A list of authors (mutually exclusive with editors)

    editors: NameList
        A list of editors (mutually exclusive with authors)

    title: string
        The title of the book

    year: string
        The year of publication

    publisher: string
        The publishing company or organization

    address: string  (ptional)
        The location of the publisher

    series : string (optional)
        The name of the series in which the book is published

    number : string (optional)
        The number in the series

    """
    _class_name = "Book"
    _required = ["year", "title", "publisher"]

    def __init__(self, **kwargs):
        self.validate(kwargs)
        try:
            self.authors = kwargs["authors"]
        except KeyError:
            pass
        try:
            self.editors = kwargs["editors"]
        except KeyError:
            pass

        self.year = kwargs["year"]
        self.title = kwargs["title"]
        self.publisher = kwargs["publisher"]

        # optional arguments:
        try:
            self.address = kwargs["address"]
        except KeyError:
            pass
        try:
            self.series = kwargs["series"]
        except KeyError:
            pass
        try:
            self.number = kwargs["number"]
        except KeyError:
            pass

    @classmethod
    def validate(cls, kwargs):
        super(Book, cls).validate(kwargs)
        if "number" in kwargs and "series" not in kwargs:
            raise ValueError(MSG_BOOK_NO_SERIES)
        if "authors" in kwargs and "editors" in kwargs:
            raise ValueError(MSG_BOOK_EDITOR_AND_AUTHOR)
        if not "authors" in kwargs and "editors" not in kwargs:
            raise ValueError(MSG_BOOK_NEITHER_EDITOR_NOR_AUTHOR)

    def get_book_title(self):
        """
        Return the formatted title of the book. If the book appeared in a
        series, include the formatted series title and the number, if given.
        """
        if hasattr(self, "series") and hasattr(self, "number"):
            ser = "({} {})".format(self.series, self.number)
        elif hasattr(self, "series"):
            ser = "({})".format(self.series)
        else:
            ser = ""

        if ser:
            return "<i>{}</i> {}".format(self.title, ser)
        else:
            return "<i>{}</i>".format(self.title)

    def get_publishing_information(self):
        """
        Return the publisher and the publishing address (if available) as a
        string formatted for a bibliographic entry.
        """
        if hasattr(self, "publisher") and hasattr(self, "address"):
            return "{address}: {publisher}".format(
                address=self.address,
                publisher=self.publisher)
        else:
            return self.publisher

    def __str__(self):
        if hasattr(self, "editors"):
            persons = self.editors
        else:
            persons = self.authors

        S = "{persons} {year} {title} {pub}".format(
            persons=stop(persons.get_names()),
            year=stop(self.year),
            title=stop(self.get_book_title()),
            pub=stop(self.get_publishing_information()))
        return S


class InCollection(Book):
    """
    This class defines a InCollection reference, i.e. a contribution in an
    edited volume.

    The default format string of the InCollection class is:

    {authors}. {year}. {contributiontitle}. In {editors}, <i>{title}</i>,
    {pages}. {address}: {publisher}.

    If there are no editors (which is, for example, sometimes the case with
    conference proceedings), the format takes the following form:

    {authors}. {year}. {contributiontitle}. In <i>{title}</i>, {pages}. {address}: {publisher}.

    If no pages are given (for example in an online publication), the
    following format is used:

    {authors}. {year}. {contributiontitle}. In {editors}, <i>{title}</i>. {address}: {publisher}.

    The format of the title is inherited from Book.

    Properties
    ----------
    authors: NameList
        A list of authors

    editors: NameList (optional)
        A list of editors

    booktitle: string
        The title of the book

    contributiontitle: string
        The title of the contribution

    year: string
        The year of publication

    publisher: string
        The publishing company or organization

    address: string
        The location of the publisher

    series : string (optional)
        The name of the series in which the book is published

    number : string (optional)
        The number in the series

    pages : string (optional)
        The pages in the edited volume

    """
    _class_name = "InCollection"
    _required = ["authors", "contributiontitle", "year", "title", "publisher"]

    def __init__(self, **kwargs):
        self.validate(kwargs)
        self.authors = kwargs["authors"]
        self.contributiontitle = kwargs["contributiontitle"]
        self.year = kwargs["year"]
        self.title = kwargs["title"]
        self.publisher = kwargs["publisher"]

        # optional arguments:
        try:
            self.address = kwargs["address"]
        except KeyError:
            pass
        try:
            self.editors = kwargs["editors"]
        except KeyError:
            pass
        try:
            self.series = kwargs["series"]
        except KeyError:
            pass
        try:
            self.number = kwargs["number"]
        except KeyError:
            pass
        try:
            self.pages = kwargs["pages"]
        except KeyError:
            pass

    @classmethod
    def validate(cls, kwargs):
        # skip the inherited method of Book:
        Reference.validate(kwargs)
        if "number" in kwargs and "series" not in kwargs:
            raise ValueError(MSG_INCOLLECTION_NO_SERIES_NAME)

    def get_source_information(self, **kwargs):
        """
        Returns editors (if given) and the title of the volume as a formatted
        string.
        """
        if hasattr(self, "editors"):
            return "In {editors}, {title}".format(
                editors=self.editors.get_names(**kwargs),
                title=self.get_book_title())
        else:
            return "In {title}".format(
                title=self.get_book_title())

    def __str__(self, **kwargs):
        source = self.get_source_information()

        if hasattr(self, "pages"):
            source = "{source}, {pages}".format(
                source=source,
                pages=self.pages)

        S = "{authors} {year} {contributiontitle} {source} {pub}".format(
            authors=stop(self.authors.get_names(**kwargs)),
            year=stop(self.year),
            contributiontitle=stop(self.contributiontitle),
            source=stop(source),
            pub=stop(self.get_publishing_information()))
        return S

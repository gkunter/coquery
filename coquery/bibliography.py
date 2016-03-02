from __future__ import unicode_literals
import warnings

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
    def __init__(self, first=None, middle=[], last=None, prefix=None, suffix=None, sortby=None):
        self._first = first
        self._last = last
        self._middle = middle
        self._prefix = prefix
        self._suffix = suffix
        self._sortby = sortby

    def __repr__(self):
        l = []
        for x in ["_first", "_middle", "_last", "_prefix", "_suffix", "_sortby"]:
            attr = getattr(self, x)
            if attr:
                if isinstance(attr, list):
                    l.append("{}=[{}]".format(x.strip("_"), 
                                            ", ".join(["'{}'".format(m) for m in attr])))
                else:
                    l.append("{}='{}'".format(x.strip("_"), attr))
        return "Person({})".format(", ".join(l))

    def __str__(self):
        return self.full_name()
    
    #def __eq__(self, other):
        #if self._middle != [] and
        #if self._middle != other._middle:
            
    @property
    def first(self):
        """
        string : The first name
        """
        return self._first
    
    @first.setter
    def first(self, s):
        self._first = s
    
    @property
    def last(self):
        """
        string : The last name
        """
        return self._last
    
    @last.setter
    def last(self, s):
        self._last = s
    
    @property
    def middle(self):
        """
        list : The middle names
        """
        return self._middle
    
    @middle.setter
    def middle(self, x):
        if not isinstance(x, list):
            x = [x]
        self._middle = x

    @property
    def prefix(self):
        """
        string : the name prefix.
        """
        return self._prefix
    
    @prefix.setter
    def prefix(self, s):
        self._prefix= s
    
    @property
    def suffix(self):
        """
        string : the name suffix.
        """
        return self._suffix
    
    @suffix.setter
    def suffix(self, s):
        self._suffix= s
    
    def _join(self, l, sep=" "):
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
        return sep.join([str(x) for x in l if x])
    
    def _middlename(self, mode="full"):
        """
        Return the middle names either initialized (if mode is "initials") or
        in their full form (if mode is "full").        
        
        Parameters
        ----------
        mode : 
        """
        if mode not in ["initials", "full"]:
            warnings.Warning("Unknown mode '{}' for Name.middlename(), assuming 'full' instead".format(mode))
            mode = "full"
        
        if mode == "full":
            return self._join(self._middle)
        elif mode == "initials":
            return self._join(["{}.".format(x[:1]) for x in self._middle])
    
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
            warnings.Warning("Unknown mode '{}' for Name.full_name(), assuming 'none' instead".format(mode))
            mode = "none"
        
        if mode == "none": 
            first = self._first
            middle = self._middlename("full")
        elif mode == "middle":
            first = self._first
            middle = self._middlename("initials")
        else:
            first = "{}.".format(self._first[0])
            middle = self._middlename("initials")
            
        return self._join([self._prefix, first, middle, self._last, self._suffix])
    
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
                self._join([self._last, self._suffix]),
                self._join([self._prefix, self._first, self._join(self._middle)]))
        elif initials == "middle":
            S = "{}, {}".format(
                self._join([self._last, 
                           self._suffix]),
                self._join([self._prefix, 
                           self._first, 
                           self._join(["{}.".format(x[:1]) for x in self._middle])]))
        else: 
            S = "{}, {}".format(
                self._join([self._last, 
                           self._suffix]),
                self._join([self._prefix, 
                           "{}.".format(self._first[:1]), 
                           self._join(["{}.".format(x[:1]) for x in self._middle])]))
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

    def __str__(self):
        return self.get_names()
    
    def get_names(self, mode_first="last", mode_others="first", sep=", ", two_sep=", and ", last_sep=", and "):
        """
        Return the name(s) in a form suitable for a bibliography.
        
        Parameters
        ----------
        mode_first : string, either "last" or "first"
            If "last", the name of the first Person is given in the form 
            "last name, first name(s)". If "first", the name of the first 
            Person is given in the form "first name(s) last name(s)".
            
        mode_others : string, either "last or "first"
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
        
        Returns
        -------
        s : string
            The name(s). 
        """
        
        if not self._list:
            return ""
        
        if mode_first not in ["last", "first"]:
            raise ValueError("Illegal value '{}' for parameter 'mode_first'.".format(mode_first))
        if mode_others not in ["last", "first"]:
            raise ValueError("Illegal value '{}' for parameter 'mode_others'.".format(mode_others))
        
        if mode_first == "first":
            first_name = self._list[0].full_name()
        else:
            first_name = self._list[0].bibliographic_name()

        if mode_others == "first":
            other_names = [x.full_name() for x in self._list[1:]]
        else:
            other_names = [x.bibliographic_name() for x in self._list[1:]]

        if len(self._list) == 1:
            return first_name
        elif len(self._list) == 2:
            return "{first}{sep}{second}".format(
                first = first_name,
                sep=two_sep,
                second = other_names[0])
        else:
            return "{first}{sep}{next}{last_sep}{last}".format(
                first=first_name,
                sep=sep,
                next=sep.join(other_names[:-1]),
                last_sep=last_sep,
                last=other_names[-1])

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
    
    def __init__(self, **kwargs):
        """
        Initialize the reference.
        
        __init__() calls :func:`validate` to determine whether all required 
        data are passed as named arguments. :func:`validate` raises a 
        ValueError if any required argument is missing.
        """
        self.validate(kwargs)
        self._title = kwargs.get("title")
        self._authors = kwargs.get("authors", PersonList())
        self._year = kwargs.get("year")

    def required_properties(self):
        """
        Return a list of property names that are required for this type of 
        bibliographic reference.
        
        Returns
        -------
        req: list of strings 
            A list containing all property names that are required.
        """
        return ["title"]

    def validate(self, kwargs):
        missing = []
        for prop in self.required_properties():
            if not prop in kwargs:
                missing.append(prop)
        if missing:
            raise ValueError("One or more propery is missing for entry type {}. Missing properties: {}".format(self._class_name, ", ".join(missing)))

    def __repr__(self):
        l = []
        for x in dir(self):
            attr = getattr(self, x)
            if x.startswith("_") and not x.startswith("__") and not hasattr(attr, "__call__") and not x == "_class_name":
                if isinstance(attr, list):
                    l.append("{}=[{}]".format(x.strip("_"), 
                                            ", ".join(["'{}'".format(m) for m in attr])))
                else:
                    l.append("{}='{}'".format(x.strip("_"), attr))
        return "{}({})".format(self._class_name, ", ".join(l))
        
    def __str__(self, mode=None):
        authors = self.authors.get_names(mode)
        year = self.year
        title = self.title
        
        if authors and year:
            return "{}. {}. <i>{}</i>".format(authors, year, title)
        elif authors:
            return "{}. <i>{}</i>".format(authors, title)
        elif year:
            return "{}. <i>{}</i>".format(year, title)
        else:
            return "<i>{}</i>".format(title)
        
    @property
    def authors(self):
        """
        NameList: the author(s)
        """
        return self._authors
    
    @authors.setter
    def authors(self, x):
        self._authors = x
            
    @property
    def year(self):
        """
        string : the publication year
        """
        return self._year
    
    @year.setter
    def year(self, s):
        if not isinstance(s, str):
            s = str(s)
        self._year = s
        
    @property
    def title(self):
        """
        string : the title of the reference
        """
        
        return self._title
    
    @title.setter
    def title(self, x):
        self._title = x

class Article(Reference):
    """
    This class defines an reference.
  
    The default format string of the Article class is:
    
    {author} {year}. {title}. <i>{journal}</i> {volume}({number}). {pages}.
    
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

    def __init__(self, **kwargs):
        self.validate(kwargs)
        self._authors = kwargs.get("authors")
        self._year = kwargs.get("year")
        self._title = kwargs.get("title")
        self._journal = kwargs.get("journal")
        self._volume = kwargs.get("volume")
        self._number = kwargs.get("number")
        self._pages = kwargs.get("pages")

    def required_properties(self):
        return ["author", "year", "title", "journal"]
  
    def __str__(self):
        if self.number:
            vol = "{}({})".format(self.volume, self.number)
        elif self.volume:
            vol = "{}".format(self.volume)
        else:
            vol = ""

        S = "{authors}. {year}. {title}. <i>{journal}</i>".format(
            authors=self.authors.get_names(), 
            year=self.year, 
            title=self.title, 
            journal=self.journal)
        if vol:
            S = "{} {}".format(S, vol)
        if self.pages:
            S = "{}. {}".format(S, self.pages)
            
        return "{}.".format(S)

    @property
    def journal(self):
        """
        string : the name of the journal
        """
        return self._journal
    
    @journal.setter
    def journal(self, s):
        self._journal = s
        
    @property
    def pages(self):
        """
        string : the page numbers
        """
        return self._pages
    
    @pages.setter
    def pages(self, s):
        self._pages = s
        
    @property
    def volume(self):
        """
        string : the journal volume
        """
        return self._volume

    @volume.setter
    def volume(self, s):
        if not isinstance(s, str):
            s = str(s)
        self._volume = s

    @property
    def number(self):
        """
        string : the journal number
        """
        return self._number

    @number.setter
    def number(self, s):
        if not isinstance(s, str):
            s = str(s)
        self._number = s

    
    #def get_publishing_information(self):
        #"""
        #Return the publisher and the publishing address (if available) as a 
        #string formatted for a bibliographic entry.
        
        #Returns
        #-------
        #s : string 
            #An HTML representation of the publishing information. If both the 
            #publisher and the publishing address are available, this takes the 
            #form ADDRESS: PUBLISHER. Otherwise, s contains either the address 
            #or the publisher as a string.        
        #"""
        #if self.publisher and self.address:
            #addr = "{}: {}".format(self.address, self.publisher)
        #elif self.publisher:
            #addr = self.publisher
        #elif self.address:
            #addr = self.address
        #else:
            #addr = ""
        #return addr

    #def get_editing_information(self):
        #"""
        #Return the editors of a volume as a string formatted for a
        #bibliographic entry.
        
        #Returns
        #-------
        #s : string 
            #An HTML representation of the editor(s).        
        #"""
        
    
    #def get_inproceedings_html(self):
        #"""
        #Return the bibliographic entry as a contribution in a proceedings 
        #volume.
        
        #Returns
        #-------
        #s : string
            #An HTML representation of the bibliographic entry
        #"""

        #S = "{name} {year}. <i>{title}</i>. In {editor} {booktitle}".format(
            #names=self.get_names(),
            #year=self.year,
            #title=self.title,
            #editor=self.get_editors(),
            #volume=self.booktitle)
        #publ = self.get_publishing_information()
        #if publ:
            #S = "{}. {}".format(S, publ)
            
        #return S
        
    
    #def get_book_html(self):
        #"""
        #Return the bibliographic entry as a book publication
        
        #Returns
        #-------
        #s : string
            #An HTML representation of the bibliographic entry
        #"""
        
        #S = "{names} {year}. <i>{title}</i>.".format(
            #names=self.get_names(), 
            #year=self.year, 
            #title=self.title)
        #publ = self.get_publishing_information()
        #if publ:
            #S = "{}. {}".format(S, publ)
            
        #return S
    

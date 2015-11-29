from __future__ import unicode_literals

import warnings

class Name(object):
    """
    This class defines a name that can be used in a bibliographic reference.
    
    The approach taken here is -- primarily out of ignorance, but also for
    practical reasons -- to follow a mostly European naming scheme. A person
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
        Return a string with the list element separated by ``sep``
        
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
    
    def full_name(self, initials='none'):
        """
        Get the full name of the person.
        
        Parameters
        ----------
        initials : string
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
        if initials not in ["none", "middle", "all"]:
            warnings.Warning("Unknown initial mode '{}', using 'none' instead".format(initials))
            initials = "none"
        
        if initials == "none": 
            return self._join([self._prefix,
                            self._first,
                            self._join(self._middle),
                            self._last,
                            self._suffix])
        elif initials == "middle":
            return self._join([self._prefix,
                            self._first,
                            self._join(["{}.".format(x[:1]) for x in self._middle]),
                            self._last,
                            self._suffix])
        else: 
            return self._join([self._prefix,
                            "{}.".format(self._first[:1]),
                            self._join(["{}.".format(x[:1]) for x in self._middle]),
                            self._last,
                            self._suffix])
    
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
    
class Reference(object):
    """
    This class defines a bibliographic reference.
  
    The central method is :func:`get_html`, which returns the bibliographic
    information as an HTML-formatted string. In order to do so, the method
    calls a helper function (e.g. :func:`get_article_html`), depending on 
    the publication type. 
    
    For other bibliographic styles than the default, the Reference class can 
    be subclassed with different implementations of these helper functions.
    """
    
    def __init__(self, pub_type=None, author=[], title=None, year=None, pages=None, publisher=None, address=None, journal=None, volume=None, number=None, url=None, date=None, access_date=None, editor=None, booktitle=None):
        self._pub_type = pub_type
        self._author = author
        self._title = title
        self._year = year
        self._pages = pages
        self._publisher = publisher
        self._address = address
        self._journal = journal
        self._volume = volume
        self._number = number
        self._url = url
        self._access_date = access_date
        self._date = date
        self._editor = editor
        self._booktitle = booktitle
        
    @property
    def author(self):
        """
        list : the author(s),represented as a lsit of Name objects 
        """
        return self._author
    
    @author.setter
    def author(self, x):
        if not isinstance(x, list):
            x = [x]
        self._author = x
            
    @property
    def title(self):
        """
        string : the title
        """
        return self._title
    
    @title.setter
    def title(self, s):
        self._title = s
        
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
        if not isinstance(s, str):
            s = str(s)
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
    
    @property
    def pub_type(self):
        """
        string : the publication type

        The publication type is used in getHTML to format the reference.
        Currently, the only supported publication types are "article" and 
        "book".
        """
        return self._pub_type

    @pub_type.setter
    def pub_type(self, s):
        self._pub_type = s

    def get_html(self):
        """
        Get a HTML representation of the publication.
        
        In order to get the HTML representation for the different 
        publication types, helper functions like :func:`get_article_html` 
        are called.
        
        Returns
        -------
        s : string
            A HTML representation of the reference
        """
        if self.pub_type == "article":
            return self.get_article_html()
        elif self.pub_type == "book":
            return self.get_book_html()
        else:
            raise ValueError("The publication type '{}' is currently not supported.".format(self.pub_type))
        
    def get_names(self, mode_first="last", mode_others="first", sep=", ", two_sep=", and ", last_sep=", and "):
        """
        Return the author name(s) in a form suitable for a bibliography.
        
        Parameters
        ----------
        mode_first : string
            If "last", the first author is given in the form "last name, 
            first name(s)". If "first", the first author is given in the 
            form "first name(s) last names".
            
        mode_others : string
            If "last", the other authors (if any) are given in the form 
            "last name, first name(s)". If "first", they are given in the 
            form "first name(s) last names".
            
        sep : string
            The character or string used to separate the author names except
            the last
            
        two_sep : string
            The character or string used to separate two author names. If 
            there is only one author, `two_sep` is ignored. If there are 
            more than two authors, `two_sep` is ignored and `sep` is used
            instead. 
            
        last_sep : string
            The character or string used to separate the author names except
            the last. If there is only one author, `last_sep` is ignored. If 
            thare two authors, `last_sep` is ignored and `two_sep` is used 
            instead.
        
        Returns
        -------
        s : string
            The author name(s). 
        """
        
        if mode_first not in ["last", "first"]:
            raise ValueError("Illegal value '{}' for parameter 'mode_first'.".format(mode_first))
        if mode_others not in ["last", "first"]:
            raise ValueError("Illegal value '{}' for parameter 'mode_others'.".format(mode_others))
        
        if not self.author:
            return ""
        
        if mode_first == "first":
            first_name = self.author[0].full_name()
        else:
            first_name = self.author[0].bibliographic_name()

        if mode_others == "first":
            other_names = [x.full_name() for x in self.author[1:]]
        else:
            other_names = [x.bibliographic_name() for x in self.author[1:]]

        if len(self.author) == 1:
            return first_name
        elif len(self.author) == 2:
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
        
    def get_article_html(self):
        """
        Return the bibliographic entry as a journal publication
        
        Returns
        -------
        s : string
            An HTML string of the bibliographic entry
        """
        
        if self.number:
            vol = "{}({})".format(self.volume, self.number)
        elif self.volume:
            vol = "{}".format(self.volume)
        else:
            vol = ""

        S = "{names}. {year}. {title}. <i>{journal}</i>".format(
            names=self.get_names(), 
            year=self.year, 
            title=self.title, 
            journal=self.journal)
        if vol:
            S = "{} {}".format(S, vol)
        if self.pages:
            S = "{}. {}".format(S, self.pages)
            
        return "{}.".format(S)
    
    def get_book_html(self):
        """
        Return the bibliographic entry as a book publication
        
        Returns
        -------
        s : string
            An HTML string of the bibliographic entry
        """
        
        if self.publisher and self.address:
            addr = "{}: {}".format(self.address, self.publisher)
        elif self.publisher:
            addr = self.publisher
        elif self.address:
            addr = self.address
        else:
            addr = ""

        S = "{names} {year}. <i>{title}</i>.".format(
            names=self.get_names(), 
            year=self.year, 
            title=self.title)
        if addr:
            S = "{}. {}".format(S, addr)
            
        return S
    

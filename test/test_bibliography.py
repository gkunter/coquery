""" This module tests the bibliography module."""

import unittest
import os.path
import sys

sys.path.append(os.path.join(sys.path[0], "../coquery"))
from bibliography import *

class TestPerson(unittest.TestCase):
    def test_property_name(self):
        name = Person()
        name.first = "Max"
        name.middle = ["Otto", "Emil"]
        name.prefix = "Dr."
        name.suffix = "MA"
        name.last = "Mustermann"

        self.assertEqual(name.first, "Max")
        self.assertEqual(name.middle, ["Otto", "Emil"])
        self.assertEqual(name.prefix, "Dr.")
        self.assertEqual(name.suffix, "MA")
        self.assertEqual(name.last, "Mustermann")

    def test_name_repr(self):
        name = Person(first="Max", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Mustermann")
        # The order of the named arguments in __repr__ is not fixed, so we 
        # test equality by sorting all the characters in the strings:
        self.assertEqual(sorted(name.__repr__()), sorted("Person(first='Max', middle=['Otto', 'Emil'], prefix='Dr.', suffix='MA', last='Mustermann')"))

    def test_name_str(self):
        name = Person(first="Max", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Mustermann")
        
    def test_full_name(self):
        name = Person(first="Max", last="Mustermann")
        self.assertEqual(name.full_name(), "Max Mustermann")
        self.assertEqual(name.full_name("middle"), "Max Mustermann")
        self.assertEqual(name.full_name("all"), "M. Mustermann")

        name = Person(first="Max", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Mustermann")
        self.assertEqual(name.full_name(), "Dr. Max Otto Emil Mustermann MA")
        self.assertEqual(name.full_name("middle"), "Dr. Max O. E. Mustermann MA")
        self.assertEqual(name.full_name("all"), "Dr. M. O. E. Mustermann MA")

    def test_bibliographic_name(self):
        name = Person(first="Max", last="Mustermann")
        self.assertEqual(name.bibliographic_name(), "Mustermann, Max")
        self.assertEqual(name.bibliographic_name("middle"), "Mustermann, Max")
        self.assertEqual(name.bibliographic_name("all"), "Mustermann, M.")

        name = Person(first="Max", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Mustermann")
        self.assertEqual(name.bibliographic_name(), "Mustermann MA, Dr. Max Otto Emil")
        self.assertEqual(name.bibliographic_name("middle"), "Mustermann MA, Dr. Max O. E.")
        self.assertEqual(name.bibliographic_name("all"), "Mustermann MA, Dr. M. O. E.")

class TestPersonList(unittest.TestCase):
    name1 = Person(first="Max", last="Mustermann")
    name2 = Person(first="John", last="Doe")
    name3 = Person(first="John", last="Doe")

    def test_personlist_init(self):
        authors = PersonList()
        authors = PersonList(self.name1, self.name2)
        
    def test_personlist_repr(self):
        authors = PersonList()
        self.assertEqual(authors.__repr__(), "PersonList()")
        authors = PersonList(self.name1)
        self.assertEqual(authors.__repr__(), "PersonList({})".format(self.name1.__repr__()))
        authors = PersonList(self.name1, self.name2)
        self.assertEqual(authors.__repr__(), "PersonList({}, {})".format(
            self.name1.__repr__(), self.name2.__repr__()))

    def test_personlist_str(self):
        authors = PersonList()
        self.assertEqual(authors.__str__(), "")
        authors = PersonList(self.name1)
        self.assertEqual(authors.__str__(), "Mustermann, Max")

class TestReference(unittest.TestCase):
    def test_reference_init(self):
        name = Person(first="Max", last="Mustermann")
        self.assertRaises(ValueError, Reference)
        Reference(title="Test document")
        Reference(title="Test document", authors=PersonList(name))
        Reference(title="Test document", year=1999)
        Reference(title="Test document", authors=PersonList(name), year=1999)
        Reference(title="Test document", authors=PersonList(name), year=1999, journal="Journal")
        
        

#class TestReference(unittest.TestCase):
    #def test_properties(self):
        #ref = Reference()
        #ref.author = [Person(first = "Eva-Maria", last = "Wunder"), Person(first = "Holger", last = "Voormann"), Person(first = "Ulrike", last = "Gut")]
        #ref.title = "The ICE Nigeria corpus project: Creating an open, rich and accurate corpus"
        #ref.year = 2009
        #ref.journal = "ICAME Journal"
        #ref.volume = 34
        #ref.number = 999
        #ref.pages = "78-88"
        #ref.pub_type = "article"




    
    #def test_article(self):
        #ref = Reference()
        #ref.author = [Person(first = "Eva-Maria", last = "Wunder"), Person(first = "Holger", last = "Voormann"), Person(first = "Ulrike", last = "Gut")]
        #ref.title = "The ICE Nigeria corpus project: Creating an open, rich and accurate corpus"
        #ref.year = 2009
        #ref.journal = "ICAME Journal"
        #ref.volume = 34
        #ref.pages = "78-88"
        #ref.pub_type = "article"
        
        #self.assertEqual(ref.get_html(),
            #"Wunder, Eva-Maria, Holger Voormann, and Ulrike Gut. 2009. The ICE Nigeria corpus project: Creating an open, rich and accurate corpus. <i>ICAME Journal</i> 34. 78-88.")

    #def test_article_init(self):
        #ref = Reference(
            #author=[Person(first = "Eva-Maria", last = "Wunder"), Person(first = "Holger", last = "Voormann"), Person(first = "Ulrike", last = "Gut")], 
            #title = "The ICE Nigeria corpus project: Creating an open, rich and accurate corpus",
            #year = 2009,
            #journal = "ICAME Journal",
            #volume = 34,
            #pages = "78-88",
            #pub_type = "article")
        
        #self.assertEqual(ref.get_html(),
            #"Wunder, Eva-Maria, Holger Voormann, and Ulrike Gut. 2009. The ICE Nigeria corpus project: Creating an open, rich and accurate corpus. <i>ICAME Journal</i> 34. 78-88.")



if __name__ == '__main__':
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestPerson),
        unittest.TestLoader().loadTestsFromTestCase(TestPersonList),
        unittest.TestLoader().loadTestsFromTestCase(TestReference),
        ])
    unittest.TextTestRunner().run(suite)


#class 
#>>> from bibliography import *
#>>> ref = Reference()
#>>> ref.name = ref.name + Person(first = "Eva-Maria", last = "Wunder")
#Traceback (most recent call last):
  #File "<stdin>", line 1, in <module>
#TypeError: can only concatenate list (not "Name") to list
#>>> ref.name = ref.name + [Person(first = "Eva-Maria", last = "Wunder")]
#>>> ref.name = ref.name + [Person(first = "Holger", last = "Voormann")]
#>>> ref.name = ref.name + [Person(first = "Ulrike", last = "Gut")]      
#>>> ref.title = 
#>>> ref.journal = "ICAME Journal"
#>>> ref.number = "34"
#>>> ref.pages = "78-88"
#>>> ref.pub_type = "article"
#>>> ref.get_html()


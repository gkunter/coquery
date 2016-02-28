""" This module tests the bibliography module."""

import unittest
import os.path
import sys

sys.path.append(os.path.join(sys.path[0], "coquery"))
from bibliography import *

class TestName(unittest.TestCase):
    def test_simple_name(self):
        name = Name()
        name.first = "Max"
        name.last = "Mustermann"
        self.assertEqual(name.full_name(), "Max Mustermann")
        self.assertEqual(name.full_name("middle"), "Max Mustermann")
        self.assertEqual(name.full_name("all"), "M. Mustermann")
        self.assertEqual(name.bibliographic_name(), "Mustermann, Max")
        self.assertEqual(name.bibliographic_name("middle"), "Mustermann, Max")
        self.assertEqual(name.bibliographic_name("all"), "Mustermann, M.")

    def test_complex_name(self):
        name = Name()
        name.first = "Max"
        name.middle = ["Otto", "Emil"]
        name.prefix = "Dr."
        name.suffix = "MA"
        name.last = "Mustermann"
        self.assertEqual(name.full_name(), "Dr. Max Otto Emil Mustermann MA")
        self.assertEqual(name.full_name("middle"), "Dr. Max O. E. Mustermann MA")
        self.assertEqual(name.full_name("all"), "Dr. M. O. E. Mustermann MA")
        self.assertEqual(name.bibliographic_name(), "Mustermann MA, Dr. Max Otto Emil")
        self.assertEqual(name.bibliographic_name("middle"), "Mustermann MA, Dr. Max O. E.")
        self.assertEqual(name.bibliographic_name("all"), "Mustermann MA, Dr. M. O. E.")

    def test_name_init(self):
        name = Name(first="Max", middle=["Otto", "Emil"], prefix="Dr.", suffix="MA", last="Mustermann")
        self.assertEqual(name.full_name(), "Dr. Max Otto Emil Mustermann MA")
        self.assertEqual(name.full_name("middle"), "Dr. Max O. E. Mustermann MA")
        self.assertEqual(name.full_name("all"), "Dr. M. O. E. Mustermann MA")
        self.assertEqual(name.bibliographic_name(), "Mustermann MA, Dr. Max Otto Emil")
        self.assertEqual(name.bibliographic_name("middle"), "Mustermann MA, Dr. Max O. E.")
        self.assertEqual(name.bibliographic_name("all"), "Mustermann MA, Dr. M. O. E.")


class TestReference(unittest.TestCase):
    def test_article(self):
        ref = Reference()
        ref.author = [Name(first = "Eva-Maria", last = "Wunder"), Name(first = "Holger", last = "Voormann"), Name(first = "Ulrike", last = "Gut")]
        ref.title = "The ICE Nigeria corpus project: Creating an open, rich and accurate corpus"
        ref.year = 2009
        ref.journal = "ICAME Journal"
        ref.volume = 34
        ref.pages = "78-88"
        ref.pub_type = "article"
        
        self.assertEqual(ref.get_html(),
            "Wunder, Eva-Maria, Holger Voormann, and Ulrike Gut. 2009. The ICE Nigeria corpus project: Creating an open, rich and accurate corpus. <i>ICAME Journal</i> 34. 78-88.")

    def test_article_init(self):
        ref = Reference(
            author=[Name(first = "Eva-Maria", last = "Wunder"), Name(first = "Holger", last = "Voormann"), Name(first = "Ulrike", last = "Gut")], 
            title = "The ICE Nigeria corpus project: Creating an open, rich and accurate corpus",
            year = 2009,
            journal = "ICAME Journal",
            volume = 34,
            pages = "78-88",
            pub_type = "article")
        
        self.assertEqual(ref.get_html(),
            "Wunder, Eva-Maria, Holger Voormann, and Ulrike Gut. 2009. The ICE Nigeria corpus project: Creating an open, rich and accurate corpus. <i>ICAME Journal</i> 34. 78-88.")



if __name__ == '__main__':
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestName),
        unittest.TestLoader().loadTestsFromTestCase(TestReference)
        ])
    unittest.TextTestRunner().run(suite)


#class 
#>>> from bibliography import *
#>>> ref = Reference()
#>>> ref.name = ref.name + Name(first = "Eva-Maria", last = "Wunder")
#Traceback (most recent call last):
  #File "<stdin>", line 1, in <module>
#TypeError: can only concatenate list (not "Name") to list
#>>> ref.name = ref.name + [Name(first = "Eva-Maria", last = "Wunder")]
#>>> ref.name = ref.name + [Name(first = "Holger", last = "Voormann")]
#>>> ref.name = ref.name + [Name(first = "Ulrike", last = "Gut")]      
#>>> ref.title = 
#>>> ref.journal = "ICAME Journal"
#>>> ref.number = "34"
#>>> ref.pages = "78-88"
#>>> ref.pub_type = "article"
#>>> ref.get_html()


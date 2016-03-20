# -*- coding: utf-8 -*-
"""
pdf2txt.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser

# account for API change in pdfminer that didn't make it to 
# the Python 3 version:
try:
    from pdfminer.pdfpage import PDFPage
except ImportError:
    from pdfminer.pdfparser import PDFDocument

# Use either cStringIO or io:
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

def pdf_to_txt(path, encoding="utf-8"):
    content = StringIO()
    manager = PDFResourceManager()
    ## not all versions of TextConverter support encodings:
    try:
        device = TextConverter(manager, content, codec=encoding, laparams=LAParams())
    except TypeError:
        device = TextConverter(manager, content, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, device)

    with open(path, "rb") as pdf:
        # account for API change:
        try:
            pages = PDFPage.get_pages(pdf, set())
        except (NameError, AttributeError):
            parser = PDFParser(pdf)
            document = PDFDocument()
            parser.set_document(document)
            document.set_parser(parser)

            pages = document.get_pages()

        for page in pages:
            interpreter.process_page(page)

    txt = content.getvalue()
    content.close()

    return txt

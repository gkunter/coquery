.. title:: Coquery: Download and installation


.. _download:

.. |nbsp| unicode:: 0xA0 
   :trim:

.. |anaconda| raw:: html
    
    <a href="https://www.continuum.io" target="_blank">https://www.continuum.io</a>

Download
========

Coquery can be installed in two ways: as a binary package, or as a 
source code package. 

Binary installer (Windows only)
-------------------------------

The binary package installs all files on your computer required to run 
Coquery. Currently, it is currently only available on Windows.

.. raw:: html

    <p><a href="download/coquery-0.9-win.exe" class="btn btn-primary btn-sm">Download</a></p>

After installing, start Coquery from the Windows application menu.

Source code package (Windows, Linux, and Mac OS |nbsp| X)
---------------------------------------------------------

In order to run Coquery from a source code package, a Python interpreter has 
to be available on your system. Most Linux and Mac OS |nbsp| X systems provide
a Python interpreter by default. Windows users can download and install a 
free Python distribution, for example Anaconda (|anaconda|).

To install the source code package, you can use the Python package installer 
``pip``, which will also install required packages if they are not present 
on your system. Start a command-line interface (``cmd.exe`` on Windows), and 
type the following command::
    
    pip install coquery

After installing, start Coquery by typing ``coquery`` at the command line.

Optional Python modules
+++++++++++++++++++++++

If you use the software installation, you may want to install the following
optional Python packages to enable all features in Coquery. They are already
included in the binary installation.

* `PyMySQL <https://github.com/PyMySQL/PyMySQL/>`_ 0.6.4 or later – A pure-Python MySQL client library (Connect to MySQL database servers)
* `Seaborn <http://stanford.edu/~mwaskom/software/seaborn/>`_ 0.7 or later – A Python statistical data visualization library (Create visualizations of your query results)
* `NLTK <http://www.nltk.org>`_ 3.0 or later – The Natural Language Toolkit (Lemmatization and tagging when building your own corpora)
* `PDFMiner <http://euske.github.io/pdfminer/index.html>`_ – PDF parser and analyzer (for Python 2.7) (Build your own corpora from PDF documents)
* `pdfminer3k <https://pypi.python.org/pypi/pdfminer3k>`_ 1.3 or later – PDF parser and analyzer (for Python 3.x) (Build your own corpora from PDF documents)

The following command installs these modules using ``pip`` (for Python 2.7)::

    pip install pymysql seaborn nltk pdfminer
    
The following command installs these modules using ``pip`` (for Python 3.x)::

    pip install pymysql seaborn nltk pdfminer3k

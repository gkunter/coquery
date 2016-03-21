.. title:: Coquery: Download and installation


.. _download:

.. |nbsp| unicode:: 0xA0 
   :trim:

.. |anaconda| raw:: html
    
    <a href="https://www.continuum.io" target="_blank">https://www.continuum.io</a>

Download
========

The current version of Coquery is 0.9. This version is fully functional, and 
is sufficiently stable for regular use. 

There are a few bugs, problems, and unexpected behaviors, though. For a list 
of known bugs, see the `Issue tracker <https://github.com/gkunter/coquery/issues>`_ 
on the Coquery `GitHub site <https://github.com/gkunter/coquery>`_. If you
encounter a bug that is not listed in the Issue tracker, please do not 
hesitate to create a new issue so that it can be fixed in a future Coquery 
release.

Windows
-------

The Windows installer will install everything on your computer that is 
needed to run Coquery. After installing, start Coquery from the Windows application 
menu.

.. raw:: html

    <p>Windows installer: <code>coquery-0.9-setup-win32.exe</code> <a href="coquery-0.9-setup-win32.exe" class="btn btn-primary btn-sm">Download</a></p>

Mac OS X
--------

For Mac OS X, the Coquery application is bundled in a disk image. After 
downloading and opening the disk image, move the Coquery application to a 
folder on your computer, e.g. the Applications folder.

.. raw:: html

    <p>Mac OS X disk image: <code>coquery-0.9-osx-el-capitan.dmg</code> <a href="coquery-0.9-osx-el-capitan.dmg" class="btn btn-primary btn-sm">Download</a></p>

Linux
-----

The easiest way of installing Coquery on a Linux computer is as a Python 
package. This option is also available to Windows and Mac OS X users. 

In order to install Coquery as a Python package, follow these steps:
    
* Download and install the free Anaconda Python distribution from |anaconda|.
* Open a terminal, and execute the following command::
    
    pip install coquery
    
  This command will download and install the Coquery program, as well as any 
  additional Python module that is required to run Coquery. A network 
  connection is needed during the install.

Coquery can now be started by typing ``coquery`` at the command line.

.. note::
    Most Linux and Mac OS |nbsp| X systems already provide a Python 
    installation by default. Do not install Anaconda if you do not want to 
    change this Python interpreter.
    
    However, using Anaconda (or a similar distribution) is strongly 
    recommended. Most of the additional Python packages required by Coquery 
    are already included in this distribution. On most default Python 
    installations, many of these packages need to be installed together with 
    Coquery, and some of them (most notably, the packages NumPy and PySide)
    can occassionally be rather difficult to install on default Python 
    installations.
    
Optional Python modules
+++++++++++++++++++++++

If you have installed Coquery as a Python package, you may want to install 
the following optional Python packages to enable all features in Coquery. 

* `PyMySQL <https://github.com/PyMySQL/PyMySQL/>`_ 0.6.4 or later – A pure-Python MySQL client library (Connect to MySQL database servers)
* `Seaborn <http://stanford.edu/~mwaskom/software/seaborn/>`_ 0.7 or later – A Python statistical data visualization library (Create visualizations of your query results)
* `NLTK <http://www.nltk.org>`_ 3.0 or later – The Natural Language Toolkit (Lemmatization and tagging when building your own corpora)
* `PDFMiner <http://euske.github.io/pdfminer/index.html>`_ – PDF parser and analyzer (for Python 2.7) (Build your own corpora from PDF documents)
* `pdfminer3k <https://pypi.python.org/pypi/pdfminer3k>`_ 1.3 or later – PDF parser and analyzer (for Python 3.x) (Build your own corpora from PDF documents)

The following command installs these modules using ``pip`` (for Python 2.7)::

    pip install pymysql seaborn nltk pdfminer
    
The following command installs these modules using ``pip`` (for Python 3.x)::

    pip install pymysql seaborn nltk pdfminer3k

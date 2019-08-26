.. title:: Coquery: Download and installation


.. _download:

.. |nbsp| unicode:: 0xA0
   :trim:

.. |anaconda| raw:: html

    <a href="https://www.continuum.io" target="_blank">https://www.continuum.io</a>

Download
========

The current version of Coquery is 0.10.0. This version is fully functional, and
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

    <p>Windows installer: <code>coquery-0.10.0-setup-win32.exe</code> <a href="coquery-0.10.0-setup-win32.exe" class="btn btn-primary btn-sm">Download</a></p>

Mac OS X
--------

For Mac OS X, the Coquery application is bundled in a disk image. After
downloading and opening the disk image, move the Coquery application to a
folder on your computer, e.g. the Applications folder.

.. raw:: html

    <p>Mac OS X disk image: <code>coquery-0.10.0-macos-sierra.dmg</code> <a href="coquery-0.10.0-macos-sierra.dmg" class="btn btn-primary btn-sm">Download</a></p>

If the disk image does not work on your version of Mac OS X, you can follow
the installation instructions given below for Linux on your computer.

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

If you have installed Coquery as a Python package, you may will have to install
the following optional Python packages to enable all features in Coquery.

* `PyMySQL <https://github.com/PyMySQL/PyMySQL/>`_ 0.6.4 or later – A pure-Python MySQL client library (Connect to MySQL database servers)
* `Seaborn <http://stanford.edu/~mwaskom/software/seaborn/>`_ 0.7 or later – A Python statistical data visualization library (Create visualizations of your query results)
* `SciPy <https://www.scipy.org/scipylib/index.html/>`_ 0.13.0 or later – Open-source software for mathematics, science, and engineering (Use more accurate statisticsal tests)
* `TextGridTools <https://github.com/hbuschme/TextGridTools/>`_ 1.3.1 or later – Read, write, and manipulate Praat TextGrid files (save results from time-annotated corpora as `Praat TextGrids <http://www.praat.org>`_)

The following command installs these modules:

    pip install pymysql scipy seaborn tgt

Additionally, the following modules may be installed if you want to create
new corpora from your own collection of files:

* `NLTK <http://www.nltk.org>`_ 3.2.1 or later – The Natural Language Toolkit (provides automatic lemmatization and part-of-speech tagging, English only)
* `PDFMiner <http://euske.github.io/pdfminer/index.html>`_ – Support for PDF documents (for Python 2.7)
* `pdfminer3k <https://pypi.python.org/pypi/pdfminer3k>`_ 1.3 or later – Support for PDF documents (for Python 3.x)
* `python-docx <https://python-docx.readthedocs.org/en/latest/>`_ 0.3.0 or later – Support for Microsoft Word (.docx) files
* `odfpy <https://github.com/eea/odfpy/>`_ 1.2.0 or later – Support for OpenDocument files (e.g. Open Office, Libre Office)
* `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_ 4.0 or later – Support for HTML documents
* `chardet <https://github.com/chardet/chardet>`_ 2.0.0 or later – Automatical detection of character encodings in your text files

The following command installs these modules using ``pip`` (for Python 2.7)::

    pip install nltk pdfminer python-docx odfpy bs4 chardet

The following command installs these modules using ``pip`` (for Python 3.x)::

    pip install nltk pdfminer3k python-docx odfpy bs4 chardet


Development version
===================

In addition to the released version of Coquery, there is also a development
version that contains all changes, extensions, and additions that have been
made since the last release version.

.. note::
    The development version is not a stable version -- it may contain bugs and
    errors, it may crash, and it may mess with the installed corpora.
    Use the development version with extreme caution!

The following commands will allow you to run the development version of
Coquery. It is assumed that Anaconda 4.6 or later is installed on your
computer. It is also assumed that you are running a command line terminal under
Linux or MacOS. Windows users will need to adapt the commands to the needs of
their operating system (support may be very limited if you run the development
version under Windows).

The development version will be located in the directory ``sandbox/coquery``
in your home directory.

.. code-block:: console

    # Create an Anaconda environment with all required packages:
    conda create -n coquery python=3.6 pandas sqlalchemy scipy pyqt lxml

    # Install additional packages required for visualizations:
    conda install -n coquery seaborn statsmodels

    # Install packages required for full-featured text imports:
    conda install -n coquery nltk chardet beautifulsoup4 xlrd
    conda install -n coquery -c conda-forge pdfminer3k python-docx odfpy

    # Install package that extend SQL support:
    conda install -n coquery pymysql sqlparse

    # Retrieve development version of Coquery (target: ~/sandbox/coquery)
    git clone https://github.com/gkunter/coquery.git ~/sandbox/coquery

    # Run the development version of Coquery:
    conda activate coquery
    cd ~/sandbox/coquery
    git checkout develop
    python Coquery.py --verbose


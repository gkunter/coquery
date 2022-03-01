.. title:: Coquery Documentation: Corpus guide

.. _corpora:

Corpus guide
############

.. _building:

Building your own corpus
------------------------

There

.. _filetypes:

File types
==========

Currently, Coquery supports the following file types for a user corpus text
corpus:

- Plain text (e.g. .txt) (Unicode support)
- Rich Text Format (.rtf) (no Unicode support)
- MS Office (.docx/.doc)
- OpenDocument Text (.odt)
- PDF (.pdf)
- HTML (.htm/.html)

Table-based corpora can be generated using the following table file types:

- CSV (e.g. .csv) (Unicode support, flexible delimiters and separators)
- MS Office (.xlsx/.xls)
- OpenDocument Spreadsheet (.ods)

.. _tagging:

Using NLTK for tagging
======================

If you create a corpus based on untagged text files, you can use the Natural
Language Toolkit NLTK (https://www.nltk.org/) to add part-of-speech tags to
your corpus. NLTK also provides a lexicon-based lemmatizer, which will allow
you to use lemma queries in your corpus.

In order to use NLTK, you need to activate the corresponding checkbox in the
installer dialog. Coquery will check if NLTK is available, and if all required
NLTK data files have been installed. If some datafiles are missing, Coquery
will try to download these files automatically. If the download fails, you can
still download the required files from the NLTK website, and install them
manually from the downloaded files.

Providing metadata
==================

You can choose to add metadata to the text files that you use to generate your
custom text corpus. The metadata has to be stored in a table file either in
CSV, MS Excel, or LibreOffice/OpenOffice Calc formats. Each row in the table
contains metadata for one text file that will be included in your corpus. The
number of columns in the table is not limited, and each column will contain
one piece of information about the text files. For instance, you can add
columns that state the genre or the publication date of the corresponding text
files.

One column needs to contain the exact file name of the corresponding text
file, and you need to associate this column in the metadata dialog by first
selecting the column, and then pressing the "File name" button.

.. _packages:
Corpus packages
----------------

A corpus package is a single file that can be used as an easy way of sharing
the information stored in a corpus installation with other users. The package
contains all levels of annotation and all metadata that was also contained in
the original installation. Users installing a corpus from a package file will
just have to name the new corpus, and they will have to select the package
file from their local file system.

.. note::
    You may only share a corpus package with other users if you are licensed
    to do so. For instance, if you install a corpus on your computer, and then
    create a package file for that installation, you need to consult the
    license of the corpus if you are allowed to redistribute the corpus in
    this format. Likewise, if you create a user corpus based on a collection
    of texts, and then create a package file for that user corpus, you may
    only share this package file with other users if the copyrights of the
    original texts permit you to do so.

.. note::
    **The Coquery developers are not liable for any breaches of licenses,
    copyrights, or any other form of terms of use that are caused by creating
    and distributing packages that were created by Coquery. Users may only
    create and share a package file for a corpus if the corpus license,
    copyrights, or any other form of terms of use permit them to do so.**

.. _thirdparty:

Installing third-party corpora 
------------------------------

A third-party corpus is a corpus that requires a dedicated installer file, but
this installer file is not included in the Coquery distributions. For example,
corpus compilers may wish to make all annotations and features from their
corpus available to Coquery users. In that case, they can decide to program
a installer for their corpus, and distribute this installer together with
their corpus files. The Settings dialog contains an option to set up the
folder in which Coquery will look for these third-party installers.

.. note::
    **Warning**: Only run third-party installers from trustworthy sources! A
    corpus installer has access to all files that you can read, write, or
    modify yourself. A malicious attacker may exploit this by adding harmful
    code to their installer file. Please note that you will be running
    third-party installers at your own risk. The Coquery developers cannot be
    held accountable for any damage caused by a third-party installer.

As a starting point for creating your own third-party installer, you may have
a look at the corpus installers provided by Coquery in the installer folder.
The installers are programmed in Python, and can be modified to match the
structure of your corpus. If you need assistance, do not hesitate to contact
the Coquery developers.

.. _supporting:

Supporting more corpora
-----------------------

If you know of a corpus that you would like to see supported in Coquery, or if
you are a corpus compiler and would like to have your corpus supported by
Coquery but are daunted by the perspective of having to develop your own
third-party installer, feel free to get in touch with the Coquery developers,
who may be happy to add your corpus to the list of supported corpora.

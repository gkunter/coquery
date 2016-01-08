# Coquery #

Coquery is a corpus query tool.

## About ##
Coquery is a tool that can search a number of linguistic corpora using a unified interface. Its initial purpose was to handle the off-line texts from the [Corpus of Contemporary American English](http://corpus.byu.edu/coca/) on your own computer, but has quickly developed into a more generic corpus query tool.

The latest release is version 0.9. 

## Features ##
* Different query modes: Frequency, Collocations, Token, Types
* One query syntax for all supported corpora
* Flexible selection of query output columns
* Multiple queries can be read from an input file (useful for creating frequency lists)
* Data columns from different corpora can be linked
* Build-in graphical visualizations
* Simple corpus creation from local text files (including lemmatization and tagging)
* New corpora can be added quite easily

## Supported corpora ##
* [Bostom University Radio Speech Corpus](https://catalog.ldc.upenn.edu/LDC96S36)
* [British National Corpus](http://www.natcorp.ox.ac.uk/)
* [Corpus of Contemporary American English](http://corpus.byu.edu/coca/)
* [Corpus of Historical American English](http://corpus.byu.edu/coha/)
* [Buckeye Corpus](http://buckeyecorpus.osu.edu/)
* [CELEX Lexical Database](https://catalog.ldc.upenn.edu/LDC96L14)
* [ICE-Nigeria](http://sourceforge.net/projects/ice-nigeria/)

Coquery does not provide any corpus data. You can only use these corpora if you have acquired the data files from the corpus maintainers. Coquery supplies tools that read these data files into MySQL databases that then can be queried. You can also build and query your own part-of-speech-tagged corpus using Coquery: simply put your text files into a folder and run the necessary tool.

## Getting started ##
Before you start Coquery for the first time, make sure that all system 
requirements are met. See the file INSTALLATION.md for details.

### Starting Coquery ###

Coquery can either be run either using a graphical user interface (GUI) or as 
a command line tool. The GUI offers many features that are not available 
when using the the command line, e.g. table linking, data functions, extended
context views, or graphical visualizations. Yet, the command line tool 
requires less memory and can execute queries somewhat faster. 

For new users, it is recommended that you try the GUI first. You can start it
by executing the following command from the folder where you unpacked the 
source code:
    
```
python coquery.py --gui
```

### Setting up the MySQL server ###
The first step that you'll have to do is to ensure that the connectio to the
MySQL database server can be established. Once you have started the GUI, call
"MySQL settings" from the Settings menu. 

### Installing a corpus ###
Now that the MySQL server can be used, you can either install your first 
corpus, or you can choose a directory with text files in order to 
compile a custom corpus from these files.

To install a corpus, call "Manage corpora" from the Corpus menu. In the 
dialog, all currently supported corpora are listed. Choose the corpus that
you want to install. If you haven't done so yet, you can download the corpus
data files following the link given for each corpus. Then, press the Install 
button. In the next dialog, select the directory that contains the corpus 
data files, and click on "Install". A status bar at the bottom of the dialog 
will show the progress of the installation. 

Please note that depending on the size and structure of the corpus, the
installation may take a long time, and require a considerable amount of 
memory and hard disk space. For example, installing the British National 
Corpus requires about 3Gb memory and about 6Gb hard disk space. Depending on
your hardware speed, this process may take four hours or more. Other, smaller
corpora can be installed almost instantly. The ICE Nigeria for example is 
typically installed in less than two minutes.

If you wish to use your own collection of texts as a corpus, call "Build new
corpus" from the Corpus menu. Enter the name of the new corpus, and select the
directory that contains your text files. If you have the Natural Language 
Toolkit (NLTK) installed, you can use the toolkit to lemmatize and tag the 
words in your text files. After pressing Ok, your texts will be processed, and
be made available for queries.

### Querying a corpus ###
Coquery uses a syntax that is very similar to the syntax from the BYU corpus resources, with a few extensions and modifications. For example, it is not possible to query the asterisk '*' in COCA, because it is always interpreted as a placeholder for any number of characters. In a Coquery string, the asterisk ``*`` has also this interpretation, but in addition, the term ``\*`` (i.e. an asterisk preceded by a backslash) queries the asterisk.

## Acknowledgements ##
Initial development was supported by: 

Anglistik III, English Language and Linguistics
Heinrich-Heine-Universität Düsseldorf

## License ##
Copyright (c) Gero Kunter (gero.kunter@coquery.org)

Coquery is free software: you can redistribute it and/or modify
it under the terms of the [GNU General Public License](http://www.gnu.org/licenses/), 
either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

### Additional permission under GNU GPL version 3 section 7 ###

In addition to the terms of the GNU GPL version 3, as a special exception, 
the copyright holders of Coquery give you permission to distribute the 
source code of any corpus installer module generated by the "Build new 
corpus" functionality under a license of your own choosing, provided 
that the source file refers in its docstring to Coquery by name and 
contains a link to the [Coquery website](http://www.coquery.org/).


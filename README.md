# Coquery #

Coquery is a corpus query tool.

### About ###
Coquery is a tool that can search a number of linguistic corpora using a unified interface. Its initial purpose was to handle the off-line texts from the [Corpus of Contemporary American English](http://corpus.byu.edu/coca/) on your own computer, but has quickly developed into a more generic corpus query tool.

The latest release is version 0.9. 

### Features ###
* Different query modes: Frequency, Collocations, Token, Types
* One query syntax for all supported corpora
* Flexible selection of query output columns
* Multiple queries can be read from an input file (useful for creating frequency lists)
* Data columns from different corpora can be linked
* Build-in graphical visualizations
* Simple corpus creation from local text files (including lemmatization and tagging)
* New corpora can be added quite easily

### Supported corpora ###
* [Bostom University Radio Speech Corpus](https://catalog.ldc.upenn.edu/LDC96S36)
* [British National Corpus](http://www.natcorp.ox.ac.uk/)
* [Corpus of Contemporary American English](http://corpus.byu.edu/coca/)
* [Corpus of Historical American English](http://corpus.byu.edu/coha/)
* [Buckeye Corpus](http://buckeyecorpus.osu.edu/)
* [CELEX Lexical Database](https://catalog.ldc.upenn.edu/LDC96L14)
* [ICE-Nigeria](http://sourceforge.net/projects/ice-nigeria/)

Coquery does not provide any corpus data. You can only use these corpora if you have acquired the data files from the corpus maintainers. Coquery supplies tools that read these data files into MySQL databases that then can be queried. You can also build and query your own part-of-speech-tagged corpus using Coquery: simply put your text files into a folder and run the necessary tool.

### Installation ###

See the (Installation guide)[INSTALLATION.md].

### Syntax ###
Coquery uses a syntax that is very similar to the syntax from the BYU corpus resources, with a few extensions and modifications. For example, it is not possible to query the asterisk '*' in COCA, because it is always interpreted as a placeholder for any number of characters. In a Coquery string, the asterisk ``*`` has also this interpretation, but in addition, the term ``\*`` (i.e. an asterisk preceded by a backslash) queries the asterisk.

### Acknowledgements
Initial development was supported by: 

Anglistik III, English Language and Linguistics
Heinrich-Heine-Universität Düsseldorf

### License ###
Copyright (c) Gero Kunter (gero.kunter@coquery.org)

Coquery is free software: you can redistribute it and/or modify
it under the terms of the [GNU General Public License](http://www.gnu.org/licenses/), 
either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

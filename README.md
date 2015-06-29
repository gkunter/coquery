# Coquery #

Coquery is a corpus query tool.

### About ###
Coquery is a tool that can search a number of linguistic corpora using a unified interface. Its initial purpose was to handle the off-line texts from the [Corpus of Contemporary American English](http://corpus.byu.edu/coca/) on your own computer, but has quickly developed into a more generic corpus query tool.

The latest release is version 0.9. 

### Features ###
* Uses MySQL database for fast searches on big corpora, much faster than processing textfiles
* Corpora that are already stored in a database can easily be incorporated by writing a new corpus module
* Many query strings can be stored in one input file that is processed in one go -- ideal for obtaining frequency lists
* Frequency counts can be grouped by word, lemma, part-of-speech, text genre, ...
* Supports the easy COCA query syntax, but is modular enough to support CQL or other query syntaxes
* Provides a flexible framework that should allow retrieval of multi-level corpus information
* Link data from different corpora -- for example, use the transcriptions from CMUdict to query the BNC

### Supported corpora ###
* [British National Corpus](http://www.natcorp.ox.ac.uk/)
* [Corpus of Contemporary American English](http://corpus.byu.edu/coca/)
* [Corpus of Historical American English](http://corpus.byu.edu/coha/)
* [Buckeye Corpus](http://buckeyecorpus.osu.edu/)
* [CELEX Lexical Database](https://catalog.ldc.upenn.edu/LDC96L14)
* [ICE-Nigeria](http://sourceforge.net/projects/ice-nigeria/)

Coquery does not provide any corpus data. You can only use these corpora if you have acquired the data files from the corpus maintainers. Coquery supplies tools that read these data files into MySQL databases that then can be queried. You can also build and query your own part-of-speech-tagged corpus using Coquery: simply put your text files into a folder and run the necessary tool.

### Installation ###

See the (Installation guide)[INSTALLATION.md].

### Examples ###

Coquery is a command line tool (a graphical interface may be added at a later stage). Here are a view examples of how Coquery can be used:

**Get a word frequency list, based on orthographic form**
```
#!bash
coquery -q "*" -O FREQ
```
**Get a bigram frequency list, based on orthographic form**
```
#!bash
coquery -q "* *" -O FREQ
```
**Get a frequency list of the part-of-speech labels, and store results in file output.csv**
```
#!bash
coquery -q "*" -p FREQ -o output.csv
```
**Get a list of all co-occurrences of the word 'residualized' followed by a noun**
```
#!bash
coquery -q "residualized [n*]" -O
```
**Get all five-word contexts preceding and following an ART-NOUN sequence**
```
#!bash
coquery -q "the|a|an [n*]" -c 5
```
**Run all queries given in the 3rd column (-n 3) of file input.csv. Output the orthographic form (-O), the part-of-speech tag (-p), a five-word context (-c 5) and the text information (-t) of all matches to file output.csv**
```
#!bash
coquery -i input.csv -o output.csv -n 3 -O -p -t
```

### Maintainer ###

[Gero Kunter](http://www.anglistik.hhu.de/sections/anglistik-iii-english-language-and-linguistics/facultystaff/detailseite-kunter.html)

# Coquery #

Coquery is a corpus query tool.

### What is Coquery for? ###

Coquery was conceived to make the search features from the [Corpus of Contemporary American English](http://corpus.byu.edu/coca/) available locally, but has quickly developed into a more generic corpus query tool. It

The latest release is version 0.9. 

### Supported corpora ###
* [British National Corpus](http://www.natcorp.ox.ac.uk/)
* [Corpus of Contemporary American English](http://corpus.byu.edu/coca/)
* [Corpus of Historical American English](http://corpus.byu.edu/coha/)
* [Buckeye Corpus](http://buckeyecorpus.osu.edu/)
* [CELEX Lexical Database](https://catalog.ldc.upenn.edu/LDC96L14)

Coquery does not provide any corpus data. You can only use these corpora if you have acquired the data files from the corpus maintainers. Coquery supplies tools that read these data files into MySQL databases that then can be queried.

You can also build and query your own corpus using Coquery: simply put your text files into a folder and run the necessary tool. Part-of-speech tagging is done using the [Natural Language Toolkit](http://www.nltk.org/).

### Requirements ###

* For most corpora: MySQL server 
* Python 2.7 and Python 3.3 compatible
* Depends on these Python modules: argparse, MySQLdb (alternativly: PyMySQL)

### Examples ###

Coquery is a command line tool (a graphical interface may be added at a later stage). Here are a view examples of how Coquery can be used:

* Get a word frequency list, based on orthographic form:
```
#!bash

coquery -q "*" -O FREQ
```
* Get a bigram frequency list, based on orthographic form
```
#!bash
coquery -q "* *" -O FREQ
```

* Get a frequency list of the part-of-speech labels:
```
#!bash
coquery -q "*" -P FREQ
```

* Get a list of all co-occurrences of the word 'residualized' followed by a noun:
```
#!bash
coquery -q "residualized [n*]" -O
```
* Get all five-word contexts preceding and following an ART-NOUN sequence:
```
#!bash
coquery -q "the|a|an [n*]" -c 5
```
### Maintainer ###

* Gero Kunter, [Universität Düsseldorf](http://www.anglistik.hhu.de/sections/anglistik-iii-english-language-and-linguistics/facultystaff/detailseite-kunter.html)
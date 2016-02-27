# Coquery - a free corpus query tool

Coquery is a free corpus query tool for linguistis, lexicographers, 
translators, and anybody who wishes to search and analyse text corpora.
It is available for Windows, Linux, and Mac OS X computers.

You can either build your own corpus from a collection of text files
or PDF documents in a directory on your computer, or install a corpus 
module for one of the supported corpora (the corpus data files are not
provided by Coquery).

Tutorials and documentation can be found on the Coquery website: http://www.coquery.org

## Features

An incomplete list of the things you can do with Coquery:

### Corpora
* Use the corpus manager to install one of the supported corpora, or to 
  build your own corpus
* Filter your query for example by year, genre, or speaker gender
* Choose which corpus features will be included in your query results
* View every token that matches your query within its context

### Queries
* Query by orthography, phonetic transcription, lemma, or gloss, and restrict 
  your query by part-of-speech
* Use string functions e.g. to test if a token contains a letter sequence
* Use the same query syntax for all installed corpora
* Automate queries by reading them from an input file

### Analysis
* Summarize the query results as frequency tables or contingency tables
* Calculate entropies and relative frequencies
* Fetch collocations, and calculate association statistics like mutual 
  information scores or conditional probabilities

### Visualizations

* Use bar charts, heat maps, or bubble charts to visualize frequency 
  distributions
* Illustrate diachronic changes by using time series plots
* Show the distribution of tokens within a corpus in a barcode or a beeswarm 
  plot

### Databases

* Either connect to easy-to-use internal databases, or to powerful MySQL 
  servers
* Access large databases on a MySQL server over the network
* Create links between tables from different corpora, e.g. to provide
  phonetic transcriptions for tokens in an unannotated corpus

## Supported corpora

Coquery already has installers for the following linguistic corpora and 
lexical databases:

* [British National Corpus (BNC)](http://www.natcorp.ox.ac.uk/)
* [Buckeye Corpus](http://buckeyecorpus.osu.edu/)
* [CELEX Lexical Database (English)](https://catalog.ldc.upenn.edu/LDC96L14)
* [Carnegie Mellon Pronunciation Dictionary (CMUdict)](http://www.speech.cs.cmu.edu/cgi-bin/cmudict)
* [Corpus of Contemporary American English (COCA)](http://corpus.byu.edu/coca/)
* [Corpus of Historical American English (COHA)](http://corpus.byu.edu/coha/)
* [Ġabra: an open lexicon for Maltese](http://mlrs.research.um.edu.mt/resources/gabra/)
* [ICE-Nigeria](http://sourceforge.net/projects/ice-nigeria/) 

If the list is missing a corpus that you want to see supported in Coquery, 
you can either write your own corpus installer in Python using the installer 
API, or you can [contact](http://www.coquery/org./contact) the Coquery 
maintainers and ask them for assistance.

## Installation

For Windows, an installer executable is available. For systems running Linux 
and Mac OS X, Coquery can be installed using the Python Index Packager 
`pip`:
    
```
    pip install coquery
```

See the [Download section](http://www.coquery.org/download/) of the Coquery
website for detailed instructions and requirements.
    
## License

Copyright (c) 2016 Gero Kunter

Coquery is free software released under the terms of the 
[GNU General Public license](https://www.gnu.org/licenses/gpl-3.0-standalone.html) (version 3).
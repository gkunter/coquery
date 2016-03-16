.. _overview:

About Coquery
#############

.. toctree::
    :maxdepth: 2

Features
========

Coquery is a free corpus query tool for linguists, lexicographers, 
translators, and anybody who wishes to search and analyse a text corpus.

.. image:: ../_static/interface/showcase.png
    :align: center

.. raw:: html
    
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-6">
                <h2>Corpora</h2>
                <ul>
                    <li>Use the corpus manager to install one of the 
                    supported corpora, or to build your own corpus from PDF or text files</li>
                    <li>Filter your query for example by year, genre, or speaker gender</li>
                    <li>Choose which corpus features will be included in your query results</li>
                    <li>View every token that matches your query within its context</li>
                </ul>
            </div>
            <div class="col-md-6">
                <h2>Queries</h2>
                <ul>
                    <li>Match tokens by orthography, phonetic transcription, lemma, or gloss, and restrict your query by part-of-speech</li>
                    <li>Use string functions e.g. to test if a token contains a letter sequence</li>
                    <li>Use the same query syntax for all installed corpora</li>
                    <li>Automate queries by reading them from an input file</li>
                    <li>Store your results as CSV files or <a href="http://www.praat.org">Praat</a> TextGrid files (if timing information is available)</li>
                </ul>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <h2>Analysis</h2>
                <ul>
                    <li>Summarize the query results as frequency tables</li>
                    <li>Calculate entropies and relative frequencies</li>
                    <li>Fetch collocations, and calculate association statistics like mutual information scores or conditional probabilities</li>
                </ul>
            </div>
            <div class="col-md-6">
                <h2>Visualizations</h2>
                <ul>
                    <li>Use bar charts, heat maps, or bubble charts to 
                    visualize frequency distributions</li>
                    <li>Illustrate diachronic changes by using time series plots</li>
                    <li>Show the distribution of tokens within a corpus in a barcode or a beeswarm plot</li>
                </ul>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-3">
            </div>
            <div class="col-md-6">
                <h2>Databases</h2>
                <ul>
                    <li>Either use easy-to-use internal databases, or connect to a powerful MySQL server</li>
                    <li>Access large corpora on a MySQL server over the network</li>
                    <li>Link data tables from different corpora, e.g. to include phonetic transcriptions in a corpus that does not contain them.</li>
                </ul>
            </div>
            <div class="col-md-3">
            </div>
        </div>
    </div>
    

Supported corpora
=================

Coquery already has installers for the following linguistic corpora:

.. raw:: html

    <div class="list-group">
        <a class="list-group-item" href="http://www.natcorp.ox.ac.uk/">British National Corpus (BNC)</a>
        <a class="list-group-item" href="http://buckeyecorpus.osu.edu/">Buckeye Corpus</a>
        <a class="list-group-item" href="https://catalog.ldc.upenn.edu/LDC96L14">CELEX Lexical Database (English)</a>
        <a class="list-group-item" href="http://www.speech.cs.cmu.edu/cgi-bin/cmudict">Carnegie Mellon Pronunciation Dictionary (CMUdict)</a>
        <a class="list-group-item" href="http://corpus.byu.edu/coca/">Corpus of Contemporary American English (COCA)</a>
        <a class="list-group-item" href="http://corpus.byu.edu/coha/">Corpus of Historical American English (COHA)</a>
        <a class="list-group-item" href="http://mlrs.research.um.edu.mt/resources/gabra/">Ġabra: an open lexicon for Maltese</a>
        <a class="list-group-item" href="http://sourceforge.net/projects/ice-nigeria/">ICE-Nigeria</a>
        <a class="list-group-item" href="https://catalog.ldc.upenn.edu/LDC97S62">Switchboard-1 Telephone Speech Corpus</a>
    </div>


Note that in order to use these corpora, you first need to obtain the corpus 
data from the linked websites.

If you are missing a corpus from the list of supported corpora, you can 
either program a custom installer for your corpus, or you can `contact <../contact.php>`_ 
the Coquery developer whether an installer for your corpus may be included 
in a future release of Coquery. 

License
=======

Coquery is free software released under the terms of the 
`GNU General Public License (version 3) <../license.html>`_. This license gives you 
the freedom to use Coquery for any purpose. It also allows you to copy, 
modify, and redistribute the software for as long as the modified software is 
also licensed under the GNU GPL. 
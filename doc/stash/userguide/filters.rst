.. _filters:

Corpus filters
==============

Overview
--------

.. warning::
    Currently, corpus filters are ignored by features that calculate overall 
    frequencies. Most notably, this includes the frequencies involved in the 
    Collocations aggregation. If corpus filters are active, the collocates 
    will only be obtained from the subcorpus that passes these filters, but 
    the collocate frequency will be obtained from the whole corpus. 
    
    Likewise, the *Frequency(pmw)* column will take the frequency of tokens 
    from the results table and normalize it against the overall number of 
    tokens from the corpus. 
    
    In order to avoid inconsistent results, you should not use these features 
    together with corpus filters.
    
    This inconvenience will be removed in future versions of Coquery.
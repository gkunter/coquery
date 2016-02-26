.. title:: Coquery Documentation: Corpus menu


.. _corpus_menu:

Corpus menu
+++++++++++

Corpus manager
~~~~~~~~~~~~~~

Corpus statistics
~~~~~~~~~~~~~~~~~

This menu entry gathers a summary table of descriptive statistics for the currently
selected corpus. The statistics table will be shown in the Results table view.

.. figure:: ../../_static/interface/corpus_statistics.png
    :align: left
    
    The corpus statistics table for the ALICE corpus.

The columns *Table* and *Column* of the table identify the output table and 
output column as shown in the :ref:`Output columns` tree. The column *Entries*
shows the total number of entries in that table column, including duplicate 
entries. The number of unique values is shown in *Uniques*.

The column *Uniqueness ratio* is calculated as the number of unique values 
divided by the number of entries. The values can range from just above 0.0 to
1.0. A uniqueness ratio of 1.0 indicates that every value in the table column 
occurs exactly once. In the example above, this is the case for the column 
Filename from the Files table: each text file has exactly one entry in the 
Files table. 

The inverse of the uniqueness ratio is given in the column *Average 
frequency*. The value in this column expresses the average number of 
repetitions of each entry in the corresponding table column. For example, the
column FileId from the table Column has an average frequency of 2770.167, 
which means that on average, there are 2770 tokens associated with each file,
or in other words, each file consists of 2770 tokens on average.

For corpus statistics tables, no :ref:`Aggregations` are available. The 
content of the table can be saved by using the entries from the 
:ref:`file_menu`.

.. note::
    The Corpus statistics table replaces your current query results table. 
    If your last corpus query took a long time to complete, you may want to 
    save the result table before gathering the corpus statistics.

Corpus documentation
~~~~~~~~~~~~~~~~~~~~

This menu entry opens the website for the currently selected corpus. On this 
website, you may find additional information on the structure of the corpus. 
For example, the website may contain an explanation of the labels used as
part-of-speech tags.
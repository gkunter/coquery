.. title:: Coquery Documentation: Output columns

.. _columns:

.. |tag| image:: /../../coquery/icons/small-n-flat/SVG/tag.svg

Output columns
==============

.. toctree::
    :maxdepth: 2

Overview
--------

A corpus may contain information on several levels of description. For 
example, a corpus may provide information on the orthographic wordform,
the phonological transcription, the part of speech, and the lemma for each of
the words that are contained in a text. In addition, the corpus may also 
contain information on the text itself, e.g. the title of the text, the year 
it was written, and the genre of the text. 

The different levels of description are typically arranged in different 
tables that each contain different columns. The example corpus from above 
might be described by a table layout as the following, where the first level 
indicates the two tables `Word` and `Texts` and the second levels the columns 
(i.e. `Wordform`, `Transcript`, `Part-of-speech`, `Lemma` and `Title`, `Year`,
`Genre`):
    
    * Words
        - Wordform
        - Transcript 
        - Part-of-speech 
        - Lemma
    * Texts 
        - Title 
        - Year 
        - Genre
        
This table structure is displayed in the main interface in the Output column 
tree. By default, tables are shown collapsed so that the columns stored in 
the table are not visible. You can expand the table either by clicking on the 
expansion symbol at the beginning of the table row, or by double-clicking on 
the table name.

Each table column can be selected by clicking on the checkbox. Clicking on a 
checked box deselects that column. Only those columns will be included in the 
query results table that are ticked in the Output column tree. 

Some of the columns are marked by the tag icon |tag|. This icon indicates 
that this column is used for looking the query item type that is given in 
square brackets after the column name. For example, |tag| **Lexeme [Lemma]** 
indicates that the column *Lexeme* is used when matching a lemma query item 
such as `[write]`.

Right-clicking on a column in the Output column tree opens the Output column 
context menu. Using the commands in this window, you may view the unique 
values provided by the current corpus for this column, link the current 
column to a different column from an external table (i.e. a table from a 
corpus other than the currently selected one), and add a function to the 
output column. For details, see :ref:`output_column_submenu`.

Special tables
--------------

In addition to the corpus-specific tables, there are also special tables that
are available for all corpora.

The first is the **Corpus** table, which contains at least the column *ID*. 
This column includes a token identifier in the results table which is unique 
for the whole corpus, and which can be used to refer to a token unambiguously.
Depending on the corpus, the Corpus table can contain additional columns.

Another special table is the **Statistics** table. The columns table can only 
be selected when the Frequency aggregation mode is selected (see :ref:`aggregations`).

Selecting the column *Frequency (pmw)* includes a column in the results table 
in which the frequency is normalized per million words. The columns *Overall 
entropy* and *Query entropy* calculate the Shannon entropy for the overall 
results table and for a single query string, respectively. The columns 
*Overall proportion* and *Query proportion* calculate the relative frequency 
of tokens, i.e. the proportion of that token's frequency in relation to the 
overall number of tokens matched by the query. *Overall proportion* considers
all tokens in the results table, and *Query proportion* considers the tokens 
produced by one query string. 

If your query contains only one query string, the values calculated by the 
Overall statistics and the Query statistics are initially identical. Yet, the 
columns *Overall entropy* and *Overall proportion* are calculated for the 
currently visible results table, and their values will be recalculated if you 
hide or show some of the columns in the results table. 

The last special table is the **Coquery** table. The columns of this table 
allow you to include in the results table the query string that matched the 
respective token. Three different formats of the query string are available: 
    
    * *Query string* includes the query string as it was entered
    * *Query token* includes one column for each query item in a multi-word 
      query string
    * *Expanded query string* includes that form of a query string containing 
      quantified query items that matched the token
    
Other columns in the Coquery table are the date and time the query was 
completed, and the name of the query input file if any was used.
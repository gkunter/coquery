.. title:: Coquery Documentation: Query syntax

.. _syntax:

Query syntax
============

Query strings
-------------

A valid query string in Coquery consists of one or more query item. 
Items are separated by spaces. The number of query items in a query 
string is not limited, but query duration increases with the number of 
items. 

Query items
-----------

Query items are the smallest unit in a query string. Each query string 
has to contain at least one query item. The number of query items is not 
limited, but the time required to execute a query increases with the 
number of query items.

Query items are not case-sensitive: ``Walk``, ``walk``,
and ``WALK`` all specify the same query item. There are four 
different types of query items. Word items, Transcription items, Lemma 
items, and Gloss items.

Word items
++++++++++

Word items are used to match tokens in the corpus based on how they are
spelled. For example, the Word item ``walk`` matches all
tokens that are spelled *walk*. Word items are supported by all 
corpora.

Transcription items
+++++++++++++++++++

Transcription items are used to match tokens in the corpus based on their 
phonetic or phonological transcription. Slashes are used to distinguish 
Transcription items from Word items. The format of the transcription 
(e.g. International Phonetic Alphabet, SAMPA transcription symbols) may 
differ between corpora, and not all corpora provide phonetic or 
phonological transcriptions.

In order to match the token *walk* in the CMUdict Pronunciation 
Dictionary, the Transcription item ``/W AO1 K/`` is used. In the 
CELEX Lexical Database, the token *walk* is matched by ``/'w$k/``.

Lemma items
+++++++++++

Lemma items are used to match tokens in the corpus that are assigned to 
the same lemma. Square brackets are used to distinguish Lemma items from
Word items. For example, ``[walk]`` in CELEX matches the tokens 
*walk*, *walking*, *walks*, and *walked*.

Gloss items
+++++++++++
Gloss items are used to match tokens for which a gloss or a translation is 
available, for example in a dictionary corpus. Double quotation marks are 
used to mark gloss items.

Part-of-speech specifiers
-------------------------

If you want to restrict the matches of a query item to a particular 
word-class, you can add a part-of-speech (POS) specifier to the query 
item. POS specifiers are separated from the query item by a dot
``.``, and consist of a POS tag enclosed in square brackets. 
For example, ``walk.[nn1]`` matches all *walk* tokens in 
the BNC that are tagged as singular nouns.

The set of available POS tags may differ between different corpora. For 
example, COCA uses the CLAWS7 tag set, while BNC uses CLAWS5. A list of 
the POS tags that are available in the active corpus can be displayed by 
first right-clicking on the part-of-speech column column in the Output 
column list, and then selecting "View unique values" from the context 
menu.

For convenience, and in order to retain syntactic compatibility with the
BYU syntax (see below), POS specifiers can also be used without providing
also a query item. Thus, ``[nn1]`` matches all tokens 
tagged as singular nouns (NN1) in the BNC. Note that this syntax is 
potentially ambiguous: For example, the tag POS is used in the BNC to 
tag the possessive marker *'s*. At the same time, there are a few 
tokens that have *POS* as their lemma. Similarly, articles in CLAWS7
are tagged by AT, which also exists as a lemma *at*. In the case of 
such ambiguities between POS tags and lemmas, Coquery is compatible to 
BYU-COCA and gives precedence to the part-of-speech tag. 

Some corpora (e.g. the CMUdict Pronunciation Dictionary) are not tagged 
for part-of-speech. With these corpora, POS specifiers cannot be used.

Wildcard characters
-------------------

In order to allow for partial matching, query items and POS specifiers 
can contain any number of wildcard characters. There are two types of 
wildcards characters: question marks ``?`` and asterisks 
``*``. They can be used within any query item type (i.e. Word, 
Lemma, Transcription, Gloss), as well as within the tags of POS specifiers.

Question mark wildcard
++++++++++++++++++++++

A question mark matches exactly one character. This wildcard character 
can be used to match tokens with a specific length. For example, the 
query item ``?`` matches all words in the corpus that are 
spelled using only a single character, for example *I*, the 
numericals *1*, *2*, and so on, but also tokens that consist of 
a single punctuation mark or a special character such as *.*, 
*_*, or *@*. Similarly, the query item ``???`` matches 
all tokens that consist of three characters, for example *the*, 
*web*, *911*, or *:-)*.

If the query item contains other characters in addition to question mark 
wildcards, the token has to match exactly the other characters, but can 
have any character in the position of the wildcard. For example, 
``?alk`` matches in CELEX the tokens *balk*, *calk*, 
*talk*, and *walk*, but not *chalk* or *stalk*. It 
would also not match *alk* if that token existed in
CELEX. 

Asterisk wildcard
+++++++++++++++++

The asterisk matches any number of characters, including zero and one.
A query item ``*`` consisting only of the asterisk wildcard will
match all tokens in the corpus. This can be useful in longer query 
strings, or if the query item is restricted to a particular part of 
speech (see below).

For example, ``w*`` matches any token that begins with the 
character *w*. ``w*lk`` matches any token that begins with 
the character *w* and ends with the character sequence *lk*, 
e.g. *walk*, *whelk*, and *waterfolk*. ``w*l*k``
matches any token that begins with the character *w* and ends in the 
character *k*, and which also contains the character *l* in any
position. This item matches the same tokens as ``w*lk``, but 
also tokens such as *warlock* and *woolsack*.

In combination with POS specifiers, asterisk wildcards are particularly 
useful to match only tokens that belong to a particular word-class. For 
example, ``*.[n*]`` matches any token with a POS tag that starts 
with *n*. In the BNC, this matches the singular noun *walk*
(tagged as NN1) as well as the plural noun *walks* (tagged as NN2).

Escaping characters
-------------------

If you want to query any character that has a special meaning in query 
items (for example the wildcard characters, the square brackets, the 
quotation mark, or the slashes), you must precede it by the 'escape' 
character ``\\`` (the backslash). For example, if you want to match 
all 

Quantified query items
----------------------

Union query items
-----------------

Additional examples
-------------------

``/?/`` matches all tokens with a transcription that consists of 
only a single character.

COCA/BYU syntax compatibility
-----------------------------

The syntax of the query strings used by Coquery is modelled after the 
syntax used in the Bigham Young University web corpus interfaces such as 
COCA or BYU-BNC. A description of the BYU syntax can be found here: 
`<http://corpus.byu.edu/coca/help/syntax_e.asp>`_

Most query strings that are valid in the BYU web interfaces are also
valid query strings in Coquery. However, where BYU-COCA uses 
``-`` to negate query items, Coquery uses the hash mark 
``#``. Also, Coquery currently does not support synonym matching: 
``[=beat].[v*]`` matches verbs like *hit*, *strike*,
or *defeat* in BYU-COCA. In contrast, Coquery matches this query 
string to all tokens that are tagged as verbs, and which are written as
*=beat*. Most likely, no token will be matched.

Coquery extends the BYU syntax by allowing for quantified query items.
Also, Transcription queries are not supported by the BYU syntax. 

# issues.py

# A list of issues that need to be fixed.

"""
#1      append needs testing
#2      skip lines needs testing
#3      Negation needs revision. For COCA, negation of words and lemmas 
        currently generates very long Id lists of all words/lemmas NOT
        matching the specification. This is slow (and not working); probably
        a fix would be to include NOT in the SQL query string.
#4      Negation with '-' doesn't work with argparse module
#5      TODO: implement queries.COCAQuerySummedFrequency(CorpusQuery)
#6      TODO: unify results format of CorpusQuery.run(). 
#7      TODO: use appdirs to determine paths for log files and configuration files
#8      Collapsing doesn't seem to work by text:
        python ./coquery.py --corpus BNC -q "awkward" -P -O -p -c 5 -t FREQ
        Query,W1,PoS1,Type,Date,OldName,Freq
        awkward,awkward,AJ0,ACPROSE,1987,NatLng,3
        awkward,awkward,AJ0,OTHERPUB,1993,EsquiD,231
        awkward,awkward,AJ0,OTHERPUB,1992-02,DoItYA,1
#9      TODO: add --similar functionality? (see nltk.Text.similar())
#10     TODO: fix cfg.lemmatize in SQLLexicon.get_wordid_list()
"""
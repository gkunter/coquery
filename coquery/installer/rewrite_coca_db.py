from __future__ import unicode_literals 

import csv
import progressbar
import logging
import collections
import glob
import os

# rewrite_coca_db.py

# This script rewrites the COCA files in the following way:

# n.a. --> pos.txt
# Format: PosId, Pos [label]

# lexicon.txt --> new_lexicon.txt
# Format: WordId, Word, Lemma, PosId, Frequency [always 0]

# db_*.txt --> new_db_*.txt
# Format: TextId, TokenId, WordId, PosId

def ToLog (Text, Level=logging.info):
    global Stage
    if Verbose:
        print "[%s]: %s" % (Stage, Text)
    logging.info ("[%s]: %s" % (Stage, Text))

Verbose = False

logging.basicConfig(filename='rewrite_coca.log', format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)



D = {}
POSDir = {}
Lexicon = {}
LastPosId = 0
Header = []
Row = 0

Stage = "lexicon"

if os.path.exists("../db/data/pos.txt") and os.path.exists("../db/data/new_lexicon.txt"):
    input_file = csv.reader(open("../db/data/pos.txt", "rt"), delimiter="\t")
    for current_line in input_file:
        POSDir [current_line[0]] = current_line[1]
    print "Using existing pos.txt, %s lines" % len(POSDir)
    InputFile = csv.reader(open("../db/data/new_lexicon.txt", "rt"), delimiter="\t")
    for current_line in InputFile:
        Lexicon [current_line[0]] = current_line[3]
    print "Using existing new_lexicon.txt, %s lines" % len(Lexicon)
else:
    OutputFile = csv.writer(open("../db/data/new_lexicon.txt", "wt"), delimiter="\t")

    with open("../db/data/lexicon.txt", "rt") as InputFile:
        InputCSV = csv.reader(InputFile, delimiter="\t", quoting=csv.QUOTE_NONE)
        while True:
            try:
                try:
                    Row += 1
                    CurrentLine = InputCSV.next()
                except csv.Error as e:
                    ToLog ("Row %s: %s" % (Row, e), logging.error)
                else:
                    if not Header:
                        Header = CurrentLine
                    else:
                        WordId, Word, Lemma, PoS = CurrentLine
                        try:
                            WordId = int(WordId)
                        except:
                            pass
                        else:
                            if PoS not in POSDir:
                                LastPosId += 1
                                POSDir [PoS] = LastPosId
                            OutputFile.writerow([WordId, Word, Lemma, POSDir[PoS], 0])
                            Lexicon[WordId] = POSDir[PoS]
            except StopIteration:
                break

    Stage = "pos"
    ToLog("Writing pos.txt")
    OutputFile = csv.writer(open("../db/data/pos.txt", "wt"), delimiter="\t")
    for CurrentPos in POSDir:
        OutputFile.writerow ([POSDir[CurrentPos], CurrentPos])
    
FileList = glob.glob ("../db/data/db_*.txt")

ProgressBar = progressbar.ProgressBar (len (FileList))

for CurrentFile in FileList:
    InputFile = csv.reader(open(CurrentFile, "rt"), delimiter="\t")
    OutputFile = csv.writer(open(CurrentFile.replace("data/", "data/new_"), "wt"), delimiter="\t")
    for TextId, TokenId, WordId in InputFile:
        try:
            OutputFile.writerow([TextId, TokenId, WordId, Lexicon[WordId]])
        except KeyError as e:
            OutputFile.writerow([TextId, TokenId, WordId, 0])
            ToLog ("Key %s not found in lexicon." % WordId, logging.error)
    ProgressBar.Update()

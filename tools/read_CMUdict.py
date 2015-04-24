""" create_mysql_corpus.py creates a MySQL database containing the data from
text files so that they are searchable by coquery. """

from __future__ import unicode_literals 

import MySQLdb
import os
import progressbar
import argparse
import re
import codecs
import csv
import fnmatch

import dbconnection

table_description = {
     "dict": {
        "CREATE": [
            "`WordId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Text` TEXT NOT NULL",
            "`Transcript` TEXT NOT NULL",
            "PRIMARY KEY (`WordId`)"
            ],
        "INDEX": {
            "Text": (["Text"], 14, "BTREE"),
            "Transcript": (["Text"], 14, "BTREE")
            }
        }
    }

def check_arguments():
    parser = argparse.ArgumentParser(prog="read_CMUdict", description="This program creates a MySQL database containing the data from the CMUdict pronunciation dictionary so that they are searchable by Coquery.""")
    
    parser.add_argument("db_name", help="name of the MySQL database to be used", type=str)
    parser.add_argument("path", help="location of the CMUdict file", type=str)
    parser.add_argument("-o", help="optimize field structure (can be slow)", action="store_true")
    
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            raise UnknownArgumentError(unknown)
        
    except Exception as e:
        raise e

    return args

def process_file(Con, filename, source_id):
    global word_id
    global lemma_id
    global token_id

    with codecs.open(filename, "rt", encoding="utf8") as input_file:
        for current_line in csv.reader(input_file, delimiter="\t"):
            if len(current_line) == 5:
                current_time, current_word, current_lemma_trans, current_trans, current_pos = current_line
    
                if float(current_time) >= 0:
                    lemma_key = "%s%s" % (current_word.lower(), current_lemma_trans)
                    if lemma_key in lemma_dict:
                        current_lemma_id = lemma_dict[lemma_key][0]
                    else:
                        lemma_id += 1
                        new_lemma = [lemma_id, current_word.lower(), current_lemma_trans]
                        Con.insert("lemma", new_lemma)
                        lemma_dict[lemma_key] = new_lemma
                        current_lemma_id = lemma_id
                        
                    word_key = "%s%s%s" % (current_pos, current_word, current_trans)
                    if word_key in word_dict:
                        current_word_id = word_dict[word_key][0]
                    else:
                        word_id += 1
                        new_word = [word_id, current_lemma_id, current_pos, current_word, current_trans]
                        Con.insert("word", new_word)
                        word_dict[word_key] = new_word
                        current_word_id = word_id

                    token_id += 1
                    new_token = [token_id, current_word_id, source_id, current_time]
                    Con.insert("corpus", new_token)

word_dict = {}
word_id = 0
lemma_dict = {}
lemma_id = 0
token_id = 0
source_id = 0

def main():
    global word_dict
    global word_id
    global lemma_dict
    global lemma_id
    global token_id
   
    arguments = check_arguments()
    
    Con = dbconnection.DBConnection(arguments.db_name)

    total_columns = 0
    total_indices = 0
    
    for current_table in table_description:
        total_columns += len(table_description[current_table]["CREATE"]) - 1
        if "INDEX" in table_description[current_table]:
            total_indices += len(table_description[current_table]["INDEX"])
        if not Con.has_table(current_table):
            Con.create_table(current_table, ", ".join(table_description[current_table]["CREATE"]))
    Con.commit()

    with open (arguments.path, "r") as input_file:
        for current_line in input_file:
            current_line = current_line.strip()
            if current_line and not current_line.startswith (";;;"):
                word, transcript = current_line.split ("  ")
                word_id += 1
                Con.insert("dict", [word_id, word, transcript])
    Con.commit()
    
if __name__ == "__main__":
    main()


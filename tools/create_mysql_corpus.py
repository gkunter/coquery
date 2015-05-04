""" create_mysql_corpus.py creates a MySQL database containing the data from
text files so that they are searchable by coquery. """

from __future__ import unicode_literals, print_function

import os
import progressbar
import argparse
import nltk
import codecs
import string
import re
import time
import dbconnection
import sys
import logging

corpus_table = "corpus"
corpus_token = "TokenId"
corpus_word = "WordId"
corpus_source = "SourceId"

word_table = "word"
word_id = "WordId"
word_lemma = "LemmaId"
word_pos = "Pos"
word_label = "Text"

source_table = "source"
source_id = "SourceId"
source_label = "Text"

lemma_table = "lemma"
lemma_id = "LemmaId"
lemma_label = "Text"

table_description = {
    corpus_table: {
        "CREATE": [
            "`{}` BIGINT(20) UNSIGNED NOT NULL".format(corpus_token),
            "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(corpus_word),
            "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(corpus_source),
            "PRIMARY KEY (`{}`)".format(corpus_token)
            ],
        "INDEX": {
            corpus_word: ([corpus_word], 0, "HASH"),
            corpus_source: ([corpus_source], 0, "HASH")
            }
        },
     word_table: {
        "CREATE": [
            "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(word_id),
            "`{}` MEDIUMINT(7) UNSIGNED".format(word_lemma),
            "`{}` VARCHAR(12) NOT NULL".format(word_pos),
            "`{}` VARCHAR(40) NOT NULL".format(word_label),
            "PRIMARY KEY (`{}`)".format(word_id)
            ],
        "INDEX": {
            word_lemma: ([word_lemma], 0, "HASH"),
            word_pos: ([word_pos], 0, "BTREE"),
            word_label: ([word_label], 0, "BTREE")
            }
        },
    source_table: {
        "CREATE": [
            "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(source_id),
            "`{}` TINYTEXT NOT NULL".format(source_label),
            "PRIMARY KEY (`{}`)".format(source_id)
            ]
        },    
    lemma_table: {
        "CREATE": [
            "`{}` MEDIUMINT(7) UNSIGNED NOT NULL".format(lemma_id),
            "`{}` TINYTEXT NOT NULL".format(lemma_label),
            "PRIMARY KEY (`{}`)".format(lemma_id)
            ],
        "INDEX": {
            lemma_label: ([lemma_label], 0, "BTREE")
            }
        },
    }


corpus_code = """# -*- coding: utf-8 -*-
#
# FILENAME: {name}.py -- a corpus module for the Coquery corpus query tool
# 
# This module was automatically created by create_mysql_corpus.py.
#

from corpus import *

class Resource(SQLResource):
    db_name = "{db_name}"

    word_table = "{word_table}"
    word_id_column = "{word_id}"
    word_label_column = "{word_label}"
    word_pos_id_column = "{word_pos}"
    word_lemma_id_column = "{word_lemma}"

    lemma_table = "{lemma_table}"
    lemma_id_column = "{lemma_id}"
    lemma_label_column = "{lemma_label}"

    pos_table = "{word_table}"
    pos_id_column = "{word_pos}"
    pos_label_column = "{word_pos}"
    
    corpus_table = "{corpus_table}"
    corpus_word_id_column = "{corpus_word}"
    corpus_token_id_column = "{corpus_token}"
    corpus_source_id_column = "{corpus_source}"
    
    file_table = "{source_table}"
    file_id_column = "{source_id}"
    file_label_column = "{source_label}"
    
class Lexicon(SQLLexicon):
    provides = [LEX_WORDID, LEX_LEMMA, LEX_ORTH, LEX_POS]

class Corpus(SQLCorpus):
    provides = [CORP_CONTEXT, CORP_FILENAME, CORP_STATISTICS]
"""
    

def check_arguments():
    parser = argparse.ArgumentParser(prog="create_corpus.py", description="This script populates a MySQL database with data from text files so that they can be queried by Coquery.""")
    
    parser.add_argument("name", help="name of the corpus", type=str)
    parser.add_argument("--db_name", help="name of the MySQL database to be used (default: same as 'name')", type=str)
    parser.add_argument("path", help="location of the text files", type=str)
    parser.add_argument("-o", help="optimize field structure (can be slow)", action="store_true")
    parser.add_argument("-w", help="Actually do something; default behaviour is simulation.", action="store_false", dest="dry_run")
    parser.add_argument("-v", help="produce verbose output", action="store_true", dest="verbose")
    parser.add_argument("-i", help="create indices (can be slow)", action="store_true")
    parser.add_argument("-l", help="load source files", action="store_true")
    parser.add_argument("-c", help="write corpus library", action="store_true")
    parser.add_argument("--corpus_path", help="target location of the corpus library (default: $COQUERY_HOME/corpora)", type=str)
    parser.add_argument("--self_join", help="create a self-joined table (can be very big)", action="store_true")

    args, unknown = parser.parse_known_args()
    return args

def write_python_code(path=sys.stdout):
    path = os.path.join(path, "{}.py".format(arguments.name))
    with open(path, "wt") as output_file:
        output_file.write(corpus_code.format(
            name=arguments.name,
            db_name=arguments.db_name,                                 
            word_table=word_table,
            word_id=word_id, 
            word_label=word_label,
            word_pos=word_pos,
            word_lemma=word_lemma,
            lemma_table=lemma_table,
            lemma_id=lemma_id,
            lemma_label=lemma_label,
            corpus_table=corpus_table,
            corpus_word=corpus_word,
            corpus_token=corpus_token,
            corpus_source=corpus_source,
            source_table=source_table,
            source_id=source_id,
            source_label=source_label))
    

def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel (logging.INFO)
    log_file_name = "%s.log" % name
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
    logger.addHandler(file_handler)
    return logger

logger = None

def create_tables(Con, table_description):
    progress = progressbar.ProgressBar(widgets=["Creating tables ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=len(table_description))
    progress.start()
    for i, current_table in enumerate(table_description):
        if not Con.has_table(current_table):
            Con.create_table(current_table, ", ".join(table_description[current_table]["CREATE"]), override=True)
        progress.update(i)
    Con.commit()    
    progress.finish()

def get_file_list(path, file_dict={}):
    L = []
    for source_path, folders, files in os.walk(path):
        for current_file in files:
            full_name = os.path.join(source_path, current_file)
            if full_name not in file_dict:
                L.append(full_name)
    return L


def load_files(Con, table_description):
    files = get_file_list(arguments.path)
    total_loads = len(files)
        
    progress = progressbar.ProgressBar(widgets=["Loading source files ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_loads)
    progress.start()
    file_count = 0
    
    source_dict = Con.read_table(source_table, lambda x: x[1])
    last_source_id = Con.get_max(source_table, source_id)

    word_dict = Con.read_table(word_table, lambda x: "%s%s" % (x[2], x[3]))
    last_word_id = Con.get_max(word_table, word_id)
    
    lemma_dict = Con.read_table(lemma_table, lambda x: x[1])
    last_lemma_id = Con.get_max(lemma_table, lemma_id)

    last_token_id = Con.get_max(corpus_table, corpus_token)
    
    for file_count, current_file in enumerate(files):
        if current_file not in source_dict:
            last_source_id += 1
            with codecs.open(current_file, "rt", encoding="utf8") as input_file:
                raw_text = input_file.read()
            tokens = nltk.word_tokenize(raw_text)
            
            for current_token, current_pos in nltk.pos_tag(tokens):
                if current_token in string.punctuation:
                    current_pos = "PUNCT"
                    
                lemma_key = current_token.lower()
                if lemma_key in lemma_dict:
                    current_lemma_id = lemma_dict[lemma_key][0]
                else:
                    last_lemma_id += 1
                    new_lemma = [last_lemma_id, lemma_key]
                    Con.insert(lemma_table, new_lemma)
                    lemma_dict[lemma_key] = new_lemma
                    current_lemma_id = last_lemma_id
                    
                word_key = "%s%s" % (current_pos, current_token)
                if word_key in word_dict:
                    current_word_id = word_dict[word_key][0]
                else:
                    last_word_id += 1
                    new_word = [last_word_id, current_lemma_id, current_pos, current_token]
                    Con.insert(word_table, new_word)
                    word_dict[word_key] = new_word
                    current_word_id = last_word_id
                    
                last_token_id += 1
                new_token = [last_token_id, current_word_id, last_source_id]
                Con.insert(corpus_table, new_token)

            Con.insert(source_table, [last_source_id, current_file])
        progress.update(file_count)

    Con.commit()
    progress.finish()
    
    
def self_join(Con, table_description):
    pass
    #logger.info("Creating self-join")

    #max_token_corpus = Con.get_max("corpus", "TokenId")
    #max_token_corpusBig = Con.get_max("corpusBig", "TokenId")
    #if not max_token_corpusBig:
        #max_token_corpusBig = 0

    #logger.info("Maximum TokenId in 'corpusBig': %s" % max_token_corpusBig)
    #if max_token_corpusBig < max_token_corpus - 10:
        #CurrentTokenId = max_token_corpusBig
        #Iterations = (max_token_corpus - CurrentTokenId) // 1000 + 1
        #logger.info("Inserting data, %s iterations" % Iterations)
        #Cur = Con.Con.cursor()
        
        #progress = progressbar.ProgressBar(widgets=["Inserting data ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=max_token_corpus)
        #progress.start()
        #while CurrentTokenId <= max_token_corpus:
            #MinToken = CurrentTokenId
            #MaxToken = CurrentTokenId + 999
            #ExecuteString = """
                #INSERT corpusBig (TokenId, TextId, 
                    #W1, W2, W3, W4, W5, W6, W7, W8, W9)
                #SELECT a.TokenId, a.TextId, 
                    #a.WordId, b.WordId, c.WordId, d.WordId, e.WordId, f.WordId, g.WordId, h.WordId, i.WordId
                #FROM corpus AS a, 
                    #corpus AS b, 
                    #corpus AS c, 
                    #corpus AS d, 
                    #corpus AS e, 
                    #corpus AS f, 
                    #corpus AS g, 
                    #corpus AS h, 
                    #corpus AS i, 
                #WHERE """ + "a.TokenId >= %s AND a.TokenId <= %s AND " % (MinToken, MaxToken) + """a.TokenId + 1 = b.TokenId AND
                #a.TokenId + 2 = c.TokenId AND
                #a.TokenId + 3 = d.TokenId AND
                #a.TokenId + 4 = e.TokenId AND
                #a.TokenId + 5 = f.TokenId AND
                #a.TokenId + 6 = g.TokenId AND
                #a.TokenId + 7 = h.TokenId AND
                #a.TokenId + 8 = i.TokenId AND
                #ORDER BY a.TokenId ASC"""
            #Con.execute(Cur, ExecuteString)
            #Con.commit()
            #CurrentTokenId += 1000
            #progress.update(MinToken)
        #progress.finish()

def optimize(Con, table_description):
    total_columns = 0
    for current_table in table_description:
        total_columns += len(table_description[current_table]["CREATE"]) - 1
    
    progress = progressbar.ProgressBar(widgets=["Optimizing field type ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_columns)
    progress.start()
    column_count = 0
    for i, current_table in enumerate(table_description):
        field_specs = table_description[current_table]["CREATE"]
        for current_spec in field_specs:
            match = re.match ("`(\w+)`", current_spec)
            if match:
                current_field = match.group(1)
                logger.info("Determine current and optimal type for column {}.{}".format(
                    current_table, current_field))
                optimal_type = Con.get_optimal_field_type(current_table, current_field)
                current_type = Con.get_field_type(current_table, current_field)
                if current_type != optimal_type:
                    logger.info("Optimising column {}.{} from {} to {}".format(
                        current_table, current_field, current_type, optimal_type))
                    try:
                        Con.modify_field_type(current_table, current_field, optimal_type)
                    except MySQLdb.OperationalError as e:
                        logger.error(e)
                column_count += 1
        progress.update(column_count)
        Con.commit()
    progress.finish()
    
def index(Con, table_description):
    total_indices=0
    for current_table in table_description:
        if "INDEX" in table_description[current_table]:
            total_indices += len(table_description[current_table]["INDEX"])
    
    progress = progressbar.ProgressBar(widgets=["Indexing ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_indices)
    progress.start()
    index_count = 0
    for i, current_table in enumerate(table_description):
        description = table_description[current_table]
        if "INDEX" in description:
            for current_index in description["INDEX"]:
                if not Con.has_index(current_table, current_index):
                    variables, length, index_type = description["INDEX"][current_index]
                    logger.info("Creating index {} on table '{}'".format(
                        current_index, current_table))
                    Con.create_index(current_table, current_index, variables, index_type, length)
                index_count += 1
        progress.update(index_count)
        Con.commit()
    progress.finish()

#def process_file(Con, filename, source_id):
    #global word_id
    #global lemma_id
    #global token_id
    
    #with codecs.open(filename, "rt", encoding="utf8") as input_file:
        #raw_text = input_file.read()
    #tokens = nltk.word_tokenize(raw_text)
    #for current_token, current_pos in nltk.pos_tag(tokens):
        #if current_token in string.punctuation:
            #current_pos = "PUNCT"
        #lemma_key = current_token.lower()
        #if lemma_key in lemma_dict:
            #current_lemma_id = lemma_dict[lemma_key][0]
        #else:
            #lemma_id += 1
            #new_lemma = [lemma_id, lemma_key]
            #Con.insert("lemma", new_lemma)
            #lemma_dict[lemma_key] = new_lemma
            #current_lemma_id = lemma_id
        #word_key = "%s%s" % (current_pos, current_token)
        #if word_key in word_dict:
            #current_word_id = word_dict[word_key][0]
        #else:
            #word_id += 1
            #new_word = [word_id, current_lemma_id, current_pos, current_token]
            #Con.insert("word", new_word)
            #word_dict[word_key] = new_word
            #current_word_id = word_id
        #token_id += 1
        #new_token = [token_id, token_id - 1, token_id + 1, current_word_id, source_id]
        #Con.insert("corpus", new_token)

#word_dict = {}
#word_id = 0
#lemma_dict = {}
#lemma_id = 0
#token_id = 0

corpus_path = "/opt/coquery/coquery/corpora"


if __name__ == "__main__":
    arguments = check_arguments()
    arguments.c = True

    dbconnection.verbose = arguments.verbose
    if not arguments.db_name:
        arguments.db_name = arguments.name
    logger = set_logger(arguments.db_name)
    dbconnection.logger = logger
    
    Con = dbconnection.DBConnection(arguments.db_name, local_infile=1)
    Con.dry_run = arguments.dry_run

    
    start_time = time.time()
    if arguments.dry_run:
        logger.info("--- Starting (dry run) ---")
    else:
        logger.info("--- Starting ---")
        Con.set_variable("autocommit", 0)
        Con.set_variable("unique_checks", 0)
        Con.set_variable("foreign_key_checks", 0)

    if not arguments.self_join:
        try:
            table_description.pop("corpusBig")
            logger.info("No self-join selected -- 'corpusBig' removed from table description")
        except KeyError:
            pass
    
    if arguments.c:
        create_tables(Con, table_description)
    if arguments.l:
        load_files(Con, table_description)
    if arguments.self_join:
        self_join(Con, table_description)
    if arguments.o:
        optimize(Con, table_description)
    if arguments.i:
        index(Con, table_description)
    if arguments.corpus_path:
        write_python_code(arguments.corpus_path)

    logger.info("--- Done (after %.3f seconds) ---" % (time.time() - start_time))

#def main():
    #global word_dict
    #global word_id
    #global lemma_dict
    #global lemma_id
    #global token_id
   
    #arguments = check_arguments()
    #file_list = get_file_list(arguments.path)
    
    #Con = dbconnection.DBConnection(arguments.db_name)

    #total_columns = 0
    #total_indices = 0
    
    #for current_table in table_description:
        #total_columns += len(table_description[current_table]["CREATE"]) - 1
        #if "INDEX" in table_description[current_table]:
            #total_indices += len(table_description[current_table]["INDEX"])
        #if not Con.has_table(current_table):
            #Con.create_table(current_table, ", ".join(table_description[current_table]["CREATE"]))
    #Con.commit()

    
    #source_dict = Con.read_table("source", lambda x: x[1])
    #source_id = Con.get_max("source", "SourceId")

    #word_dict = Con.read_table("word", lambda x: "%s%s" % (x[2], x[3]))
    #word_id = Con.get_max("word", "WordId")
    
    #lemma_dict = Con.read_table("lemma", lambda x: x[1])
    #lemma_id = Con.get_max("lemma", "LemmaId")

    #token_id = Con.get_max("corpus", "TokenId")
    
    #file_counter = 0

    #progress = progressbar.ProgressBar(widgets=["Reading file ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=len(file_list))
    #progress.start()
    
    #for i, current_file in enumerate(file_list):
        #if not Con.find("source", "Text", current_file):
            #source_id += 1
            #Con.insert("source", [source_id, current_file])
            #process_file(Con, current_file, source_id)
            #Con.commit()
        #progress.update(i)
    #progress.finish()

    #progress = progressbar.ProgressBar(widgets=["Optimizing field type ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_columns)
    #progress.start()
    #column_count = 0
    #for i, current_table in enumerate(table_description):
        #field_specs = table_description[current_table]["CREATE"]
        #for current_spec in field_specs:
            #match = re.match ("`(\w+)`", current_spec)
            #if match:
                #current_field = match.group(1)
                #optimal_type = Con.get_optimal_field_type(current_table, current_field)
                #current_type = Con.get_field_type(current_table, current_field)
                #if current_type != optimal_type:
                    #Con.modify_field_type(current_table, current_field, optimal_type)
                #column_count += 1
        #progress.update(column_count)
        #Con.commit()
    #progress.finish()
    
    #progress = progressbar.ProgressBar(widgets=["Indexing ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_indices)
    #progress.start()
    #index_count = 0
    #for i, current_table in enumerate(table_description):
        #description = table_description[current_table]
        #if "INDEX" in description:
            #for current_index in description["INDEX"]:
                #if not Con.has_index(current_table, current_index):
                    #variables, length, index_type = description["INDEX"][current_index]
                    #Con.create_index(current_table, current_index, variables, index_type)
                #index_count += 1
        #progress.update(index_count)
        #Con.commit()
    #progress.finish()

#if __name__ == "__main__":
    #main()

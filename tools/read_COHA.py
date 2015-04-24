from __future__ import unicode_literals 

import os, os.path
import glob
import logging
import sys

import progressbar
import argparse
import time
import re

import dbconnection
import MySQLdb

Filter = "*.txt"

table_description = {
    "sources": {
        "CREATE": [
            "`TextId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Words` MEDIUMINT(6) UNSIGNED NOT NULL",
            "`Genre` ENUM('FIC', 'MAG','NEWS','NF') NOT NULL",
            "`Year` SMALLINT(4) UNSIGNED NOT NULL",
            "`Title` TINYTEXT NOT NULL",
            "`Author` TINYTEXT NOT NULL",
            "PRIMARY KEY (`TextID`)"], 
        "SOURCE": {
            "FILES": ["sources_coha.csv"],
            "ARGS": "IGNORE 1 LINES"},
        "INDEX": {
            "Genre": (["Genre"], 0, "HASH"),
            "Year": (["Year"], 0, "HASH")
            }
        },
    "lexicon": {
        "CREATE": [
            "`WordId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`WordCS` TINYTEXT NOT NULL",
            "`Word` TINYTEXT NOT NULL",
            "`Lemma` TINYTEXT NOT NULL",
            "`PoS` VARCHAR(24) NOT NULL",
            "PRIMARY KEY (`WordId`)"],
        "SOURCE": {
            "FILES": ["lexicon.txt"],
            "ARGS": "LINES TERMINATED BY '\\r\\n' IGNORE 3 LINES" },
        "INDEX": {
            "PoS": (["PoS"], 0, "HASH"),
            "Word": (["Word"], 13, "BTREE"),
            "Lemma": (["Lemma"], 13, "BTREE")
            }
        },
    "files": {
        "CREATE": [
            "`Filename` VARCHAR (20)", 
            "PRIMARY KEY (`Filename`)"]
        },
    "corpus": {
        "CREATE": [
            "`TextId` MEDIUMINT(6) UNSIGNED NOT NULL",
            "`TokenId` INT(9) UNSIGNED NOT NULL",
            "`WordId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "PRIMARY KEY (`TokenId`)"],
        "SOURCE": {
            "FILES": ["%s.txt" % x for x in range(1810, 2010, 10)],
            "ARGS": "" },
        "INDEX": {
            "WordId": (["WordId"], 0, "HASH"),
            "TextId": (["TextId"], 0, "HASH")}
        },
    "corpusBig": {
        "CREATE": [
            "`TokenId` INT(9) UNSIGNED NOT NULL",
            "`TextId` MEDIUMINT(6) UNSIGNED NOT NULL",
            "`W1` MEDIUMINT UNSIGNED NOT NULL",
            "`W2` MEDIUMINT UNSIGNED NOT NULL",
            "`W3` MEDIUMINT UNSIGNED NOT NULL",
            "`W4` MEDIUMINT UNSIGNED NOT NULL",
            "`W5` MEDIUMINT UNSIGNED NOT NULL",
            "`W6` MEDIUMINT UNSIGNED NOT NULL",
            "`W7` MEDIUMINT UNSIGNED NOT NULL",
            "`W8` MEDIUMINT UNSIGNED NOT NULL",
            "`W9` MEDIUMINT UNSIGNED NOT NULL",
            "PRIMARY KEY (`TokenId`)" ],
        "INDEX": {
            #"TextId": (["TextId"], 0, "HASH"),
            #"Genre": (["Genre"], 0, "BTREE"),
            #"Year": (["Year"], 0, "BTREE"),
            #"W1": (["W1"], 0, "HASH"),
            #"W1_W2": (["W1", "W2"], 0, "HASH"),
            #"W1_W2_W3": (["W1", "W2", "W3"], 0, "HASH"),
            #"W1_W2_W3_W4": (["W1", "W2", "W3", "W4"], 0, "HASH")
            }
        }
    }

def check_arguments():
    parser = argparse.ArgumentParser(prog="read_COHA", description="This program populates a MySQL database containing the data from the COHA so that they are searchable by Coquery.""")
    
    parser.add_argument("db_name", help="name of the MySQL database to be used", type=str)
    parser.add_argument("path", help="location of the COHA text files", type=str)
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

def load_files(Con, table_description):
    total_loads = 0
    for current_table in table_description:
        if "SOURCE" in table_description[current_table]:
            total_loads += len(table_description[current_table]["SOURCE"]["FILES"])
    
    progress = progressbar.ProgressBar(widgets=["Loading source files ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_loads)
    progress.start()
    file_count = 0
    for current_table in table_description:
        if "SOURCE" in table_description[current_table]:
            # only load if table is still empty:
            if not Con.get_number_of_rows(current_table):
                for current_file in table_description[current_table]["SOURCE"]["FILES"]:
                    logger.info("Loading file %s into table '%s'" % (current_file, current_table))
                    try:
                        Con.load_data(
                            current_table,
                            os.path.join(arguments.path, current_file),
                            table_description[current_table]["SOURCE"]["ARGS"])
                    except MySQLdb.OperationalError as e:
                        logger.error(e)
                    file_count += 1
                    progress.update(file_count)
            else:
                logger.warning("Table '%s' not empty, do not load files." % current_table)
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

if __name__ == "__main__":
    arguments = check_arguments()
    arguments.c = True

    dbconnection.verbose = arguments.verbose
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

    logger.info("--- Done (after %.3f seconds) ---" % (time.time() - start_time))
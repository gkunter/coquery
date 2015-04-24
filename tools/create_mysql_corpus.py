""" create_mysql_corpus.py creates a MySQL database containing the data from
text files so that they are searchable by coquery. """

from __future__ import unicode_literals

import MySQLdb
import os
import progressbar
import argparse
import nltk
import re
import string
import codecs
import dbconnection

table_description = {
    "corpus": {
        "CREATE": [
            "`TokenId` BIGINT(20) UNSIGNED NOT NULL",
            "`PrevTokenId` BIGINT(20) UNSIGNED NOT NULL",
            "`NextTokenId` BIGINT(20) UNSIGNED NOT NULL",
            "`WordId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`SourceId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "PRIMARY KEY (`TokenId`)"
            ],
        "INDEX": {
            "PrevTokenId": (["PrevTokenId"], 0, "HASH"),
            "NextTokenId": (["NextTokenId"], 0, "HASH"),
            "WordId": (["WordId"], 0, "HASH"),
            "SourceId": (["SourceId"], 0, "HASH")
            }
        },
     "word": {
        "CREATE": [
            "`WordId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`LemmaId` MEDIUMINT(7) UNSIGNED",
            "`Pos` VARCHAR(12) NOT NULL",
            "`Text` VARCHAR(40) NOT NULL",
            "PRIMARY KEY (`WordId`)"
            ],
        "INDEX": {
            "LemmaId": (["LemmaId"], 0, "HASH"),
            "Pos": (["Pos"], 0, "BTREE"),
            "Text": (["Text"], 0, "BTREE")
            }
        },
    "source": {
        "CREATE": [
            "`SourceId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Text` TINYTEXT NOT NULL",
            "PRIMARY KEY (`SourceId`)"
            ]
        },    
    "lemma": {
        "CREATE": [
            "`LemmaId` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Text` TINYTEXT NOT NULL",
            "PRIMARY KEY (`LemmaId`)"
            ],
        "INDEX": {
            "Text": (["Text"], 0, "BTREE")
            }
        },
    }


def check_arguments():
    parser = argparse.ArgumentParser(prog="create_mysql_corpus", description="This program creates a MySQL database containing the data from text files so that they are searchable by Coquery.""")
    
    parser.add_argument("db_name", help="name of the MySQL database to be used", type=str)
    parser.add_argument("path", help="location of the texts to be inserted", type=str)
    parser.add_argument("-p", help="use part-of-speech tagger from NLTK", action="store_true")
    parser.add_argument("-o", help="optimize field structure (can be slow)", action="store_true")
    
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            raise UnknownArgumentError(unknown)
        
    except Exception as e:
        raise e

    return args

def get_file_list(path, file_dict={}):
    L = []
    for source_path, folders, files in os.walk(path):
        for current_file in files:
            full_name = os.path.join(source_path, current_file)
            if full_name not in file_dict:
                L.append(full_name)
    return L

def process_file(Con, filename, source_id):
    global word_id
    global lemma_id
    global token_id
    
    with codecs.open(filename, "rt", encoding="utf8") as input_file:
        raw_text = input_file.read()
    tokens = nltk.word_tokenize(raw_text)
    for current_token, current_pos in nltk.pos_tag(tokens):
        if current_token in string.punctuation:
            current_pos = "PUNCT"
        lemma_key = current_token.lower()
        if lemma_key in lemma_dict:
            current_lemma_id = lemma_dict[lemma_key][0]
        else:
            lemma_id += 1
            new_lemma = [lemma_id, lemma_key]
            Con.insert("lemma", new_lemma)
            lemma_dict[lemma_key] = new_lemma
            current_lemma_id = lemma_id
        word_key = "%s%s" % (current_pos, current_token)
        if word_key in word_dict:
            current_word_id = word_dict[word_key][0]
        else:
            word_id += 1
            new_word = [word_id, current_lemma_id, current_pos, current_token]
            Con.insert("word", new_word)
            word_dict[word_key] = new_word
            current_word_id = word_id
        token_id += 1
        new_token = [token_id, token_id - 1, token_id + 1, current_word_id, source_id]
        Con.insert("corpus", new_token)

word_dict = {}
word_id = 0
lemma_dict = {}
lemma_id = 0
token_id = 0

def main():
    global word_dict
    global word_id
    global lemma_dict
    global lemma_id
    global token_id
   
    arguments = check_arguments()
    file_list = get_file_list(arguments.path)
    
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

    
    source_dict = Con.read_table("source", lambda x: x[1])
    source_id = Con.get_max("source", "SourceId")

    word_dict = Con.read_table("word", lambda x: "%s%s" % (x[2], x[3]))
    word_id = Con.get_max("word", "WordId")
    
    lemma_dict = Con.read_table("lemma", lambda x: x[1])
    lemma_id = Con.get_max("lemma", "LemmaId")

    token_id = Con.get_max("corpus", "TokenId")
    
    file_counter = 0

    progress = progressbar.ProgressBar(widgets=["Reading file ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=len(file_list))
    progress.start()
    
    for i, current_file in enumerate(file_list):
        if not Con.find("source", "Text", current_file):
            source_id += 1
            Con.insert("source", [source_id, current_file])
            process_file(Con, current_file, source_id)
            Con.commit()
        progress.update(i)
    progress.finish()

    progress = progressbar.ProgressBar(widgets=["Optimizing field type ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_columns)
    progress.start()
    column_count = 0
    for i, current_table in enumerate(table_description):
        field_specs = table_description[current_table]["CREATE"]
        for current_spec in field_specs:
            match = re.match ("`(\w+)`", current_spec)
            if match:
                current_field = match.group(1)
                optimal_type = Con.get_optimal_field_type(current_table, current_field)
                current_type = Con.get_field_type(current_table, current_field)
                if current_type != optimal_type:
                    Con.modify_field_type(current_table, current_field, optimal_type)
                column_count += 1
        progress.update(column_count)
        Con.commit()
    progress.finish()
    
    progress = progressbar.ProgressBar(widgets=["Indexing ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_indices)
    progress.start()
    index_count = 0
    for i, current_table in enumerate(table_description):
        description = table_description[current_table]
        if "INDEX" in description:
            for current_index in description["INDEX"]:
                if not Con.has_index(current_table, current_index):
                    variables, length, index_type = description["INDEX"][current_index]
                    Con.create_index(current_table, current_index, variables, index_type)
                index_count += 1
        progress.update(index_count)
        Con.commit()
    progress.finish()

if __name__ == "__main__":
    main()


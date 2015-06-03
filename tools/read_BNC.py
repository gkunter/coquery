from __future__ import unicode_literals 

import argparse
import re
import logging
import time

from create_mysql_corpus import create_tables
from create_mysql_corpus import set_logger
from create_mysql_corpus import get_file_list
from create_mysql_corpus import optimize
from create_mysql_corpus import index

import dbconnection

from lxml import etree

source_table = "text"

table_description = {
    #"alignment": {
        #"CREATE": [
            #"`id` MEDIUMINT(7) UNSIGNED NOT NULL",
            #"`Tag` TINYTEXT NOT NULL",
            #"PRIMARY KEY (`id`)"
            #]
        #},
    "element": {
        "CREATE": [
            "`id` int(20) UNSIGNED NOT NULL",
            "`Entity_id` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Sentence_id` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Number` INT(8) NOT NULL",
            "PRIMARY KEY (`id`)"
            ],
        "INDEX": {
            "Entity_id": (["Entity_id"], 0, "HASH"),
            "Sentence_id": (["Sentence_id"], 0, "HASH")
            }
        },
     "entity": {
        "CREATE": [
            "`id` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Lemma_id` MEDIUMINT(6) UNSIGNED",
            "`Type` ENUM('c','gap','pause','vocal','w')",
            "`C5` ENUM('AJ0','AJ0-AV0','AJ0-NN1','AJ0-VVD','AJ0-VVG','AJ0-VVN','AJC','AJS','AT0','AV0','AV0-AJ0','AVP','AVP-PRP','AVQ','AVQ-CJS','CJC','CJS','CJS-AVQ','CJS-PRP','CJT','CJT-DT0','CRD','CRD-PNI','DPS','DT0','DT0-CJT','DTQ','EX0','ITJ','NN0','NN1','NN1-AJ0','NN1-NP0','NN1-VVB','NN1-VVG','NN2','NN2-VVZ','None','NP0','NP0-NN1','ORD','PNI','PNI-CRD','PNP','PNQ','PNX','POS','PRF','PRP','PRP-AVP','PRP-CJS','PUL','PUN','PUQ','PUR','TO0','UNC','VBB','VBD','VBG','VBI','VBN','VBZ','VDB','VDD','VDG','VDI','VDN','VDZ','VHB','VHD','VHG','VHI','VHN','VHZ','VM0','VVB','VVB-NN1','VVD','VVD-AJ0','VVD-VVN','VVG','VVG-AJ0','VVG-NN1','VVI','VVN','VVN-AJ0','VVN-VVD','VVZ','VVZ-NN2','XX0','ZZ0')",
            "`Text` VARCHAR(133) NOT NULL",
            "PRIMARY KEY (`id`)"
            ],
        "INDEX": {
            "Lemma_id": (["Lemma_id"], 0, "HASH"),
            "Text": (["Text"], 0, "BTREE"),
            "C5": (["C5"], 0, "BTREE")
            }
        },
    "file": {
        "CREATE": [
            "`id` SMALLINT(4) UNSIGNED NOT NULL",
            "`Filename` TINYTEXT NOT NULL",
            "PRIMARY KEY (`id`)"
            ]
        },
    "lemma": {
        "CREATE": [
            "`id` MEDIUMINT(6) UNSIGNED NOT NULL",
            "`Pos` ENUM('ADJ','ADV','ART','CONJ','INTERJ','PREP','PRON','SUBST','UNC','VERB')",
            "`Text` VARCHAR(131) NOT NULL",
            "PRIMARY KEY (`id`)"
            ]
        },
    "sentence": {
        "CREATE": [
            "`id` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Text_id` SMALLINT(4) UNSIGNED NOT NULL",
            "`Speaker_id` SMALLINT(4) UNSIGNED NOT NULL",
            "`Number` MEDIUMINT(7) NOT NULL",
            "PRIMARY KEY (`id`)"
            ]
        },
    "speaker": {
        "CREATE": [
            "`id` SMALLINT(4) UNSIGNED NOT NULL",
            "`Text` VARCHAR(8) NOT NULL",
            "PRIMARY KEY (`id`)"
            ]
        },
    "text": {
        "CREATE": [
            "`id` SMALLINT(4) UNSIGNED NOT NULL",
            "`XMLName` CHAR(3) NOT NULL",
            "`Type` ENUM('ACPROSE','CONVRSN','FICTION','NEWS','NONAC','OTHERPUB','OTHERSP','UNPUB') NOT NULL",
            "`Date` VARCHAR(21) NOT NULL",
            "`OldName` CHAR(6) NOT NULL",
            "`File_id` SMALLINT(4) UNSIGNED NOT NULL",
            "PRIMARY KEY (`id`)"
            ]
        },
     "utterance": {
        "CREATE": [
            "`id` MEDIUMINT(7) UNSIGNED NOT NULL",
            "`Text_id` SMALLINT(4) UNSIGNED NOT NULL",
            "`Speaker_id` SMALLINT(4) NOT NULL",
            "`Number` MEDIUMINT(6) NOT NULL",
            "PRIMARY KEY (`id`)"
            ]
        }
    }

db_name = "bnc_maria"

utterances_in_text = 0
sentences_in_text = 0
elements_in_text = 0
this_utterance_id = 0
this_sentence_id = 0

speaker_dict = {}
file_dict = {}
source_dict = {}
lemma_dict = {}
word_dict = {}

InfoLevel = logging.INFO
Pretend = False

transcription_path  = "/usr/local/share/BNC/Texts/"
filter = "*.xml"

SupportedTags = ["w", "vocal", "gap", "c", "s", "u", "mw", "align", "wtext", "stext", "pause", "shift"]
IgnoreTags = ["unclear", "trunc", "event", "p", "pb", "hi", "head", "div", "list", "label", "item", "quote", "corr"]

def check_arguments():
    parser = argparse.ArgumentParser(description="This script populates a MySQL database with data from text files so that they can be queried by Coquery.""")
    
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
    args.name = "bnc"
    
    return args

def GetChildrenByTagNames (Node, TagNames):
    for Child in Node.childNodes:
        if Child.nodeType == Child.ELEMENT_NODE and (TagName == '*' or Child.tagName in TagNames):
            yield Child

def xml_get_node_value(node):
    if node.tag == "w":
        Text = node.text
        if Text:
            return Text.strip ()
        else:
            return ""
    elif node.tag == "c":   
        try:
            return node.text.strip ()
        except AttributeError:
            logger.warning("c Node doesn't seem to have a text associated with it: %s" % node)
            return ""
    elif node.tag == "vocal":
        if "desc" in node.attrib:
            return node.attrib ["desc"].strip()
        else:
            return "unknown"
    elif node.tag == "gap":
        if "desc" in node.attrib:
            return node.attrib ["desc"].strip ()
        else:
            return "unknown"
    elif node.tag == "pause":
        if "dur" in node.attrib:
            return node.attrib ["dur"].strip ()
        else:
            return "unknown"

def xml_process_element(tree_element):
    global last_file_id
    global last_source_id
    global last_sentence_id
    global last_utterance_id
    global last_speaker_id
    global last_lemma_id
    global last_word_id
    global last_token_id
    
    global utterances_in_text
    global sentences_in_text
    global elements_in_text

    global this_utterance_id
    global this_sentence_id
    
    current_tag = tree_element.tag
    
    this_speaker_id = 0
    this_alignment_id = 0
    this_lemma_id = 0

    if current_tag == "u":
        last_utterance_id += 1
        utterances_in_text += 1
        
        # speaker: get or create new
        speaker_key = tree_element.attrib ["who"].strip ()
        if speaker_key in speaker_dict:
            this_speaker_id = speaker_dict[speaker_key][0]
        else:
            last_speaker_id += 1
            new_speaker = [last_speaker_id, speaker_key]
            Con.insert("speaker", new_speaker)
            speaker_dict[speaker_key] = new_speaker
            this_speaker_id = last_speaker_id
            
        current_utterance = [last_utterance_id, last_source_id, this_speaker_id, utterances_in_text]
        Con.insert("utterance", current_utterance)
        this_utterance_id = last_utterance_id
        
    elif current_tag == "s":
        sentences_in_text += 1
        last_sentence_id += 1
        new_sentence = [last_sentence_id, last_source_id, this_speaker_id , sentences_in_text]
        Con.insert("sentence", new_sentence)
        this_sentence_id = last_sentence_id
            
    elif current_tag in ["w", "vocal", "c", "gap", "pause"]:
        current_value = xml_get_node_value(tree_element).strip()

        if current_tag == "w":
            lemma_text = tree_element.attrib ["hw"].strip ()
            lemma_pos = tree_element.attrib ["pos"].strip()
            
            # lemma: get or create new
            lemma_key = "%s%s" % (lemma_text, lemma_pos)
            if lemma_key in lemma_dict:
                this_lemma_id = lemma_dict[lemma_key][0]
            else:
                last_lemma_id += 1
                new_lemma = [last_lemma_id, lemma_pos, lemma_text]
                Con.insert("lemma", new_lemma)
                lemma_dict[lemma_key] = new_lemma
                this_lemma_id = last_lemma_id

        if "c5" in tree_element.attrib:
            C5 = tree_element.attrib ["c5"].strip()
        else:
            C5 = None
        
        # word: get or create new            
        word_key = "%s%s" % (current_value, C5)
        if word_key in word_dict:
            this_word_id = word_dict[word_key][0]
        else:
            last_word_id += 1
            new_word = [last_word_id, this_lemma_id, current_tag, C5, current_value]
            Con.insert("entity", new_word)
            word_dict[word_key] = new_word
            this_word_id = last_word_id
            
        last_token_id += 1
        elements_in_text += 1
        new_token = [last_token_id, this_word_id, this_sentence_id, elements_in_text]
        Con.insert("element", new_token)

    for current_child in tree_element:
        xml_process_element(current_child)

def process_file(current_file):
    global last_file_id
    global last_source_id
    global last_sentence_id
    global last_utterance_id
    global last_speaker_id
    global last_lemma_id
    global last_word_id
    global last_token_id

    try:
        root = etree.parse(current_file).getroot()
    except lxml.etree.XMLSyntaxError as e:
            logger.error("Could not parse XML file: %s" % e) 
    idno_list = root.findall(".//idno")

    for current_idno in idno_list:
        current_type = current_idno.attrib["type"]
        current_value = current_idno.text.strip()
        if current_type == "bnc":
            xml_name = current_value
        elif current_type == "old":
            old_name = current_value
        else:
            logger.warning("unknown idno type %s" % current_type)

    stext_list = root.find("stext")
    wtext_list = root.find("wtext")
            
    source_desc = root.find(".//sourceDesc")

    if (stext_list is None) == (wtext_list is None):
        logger.waring("either: both stexts and wtexts found, or: neither stexts nor wtexts found")
    date = "unknown"
    if stext_list is not None:
        this_text = stext_list
        try:
            date = source_desc.find(".//recording").attrib["date"].strip()
        except KeyError:
            logger.warning("No recording date found.")
    
    if wtext_list is not None:
        this_text = wtext_list
        date_node = source_desc.find (".//date")
        if date_node is not None:
            if "value" in date_node.attrib:
                date = date_node.attrib["value"].strip()
            else:
                date = date_node.text.strip()
        else:
            # This is being clever. What this does is iterate through
            # the texts in the SourceDesc node, check whether it is an
            # empty string, if not insert it into the new list, and
            # finally join the elements of the list so that we end up
            # with a single string.
            # A more verbose equivalent would be:
            
            # L = []
            # for x in SourceDesc.itertext ():
            #   if x.strip():
            #     L.append (x)
            # S = " ".join (L)
            S = " ".join ([x.strip() for x in source_desc.itertext() if x.strip()])

            match = re.match(".*([12]\d\d\d[\d\-\.\:\_\s]*).*", S)
            if match:
                date = match.group(1).strip()

    if date == "unknown":
        logger.warning("Could not determine file date.")

    text_type = this_text.attrib ["type"].strip ()

    TotalElements = 0
    TagsDecl = root.find (".//tagsDecl/namespace")
    
    if xml_name in source_dict:
        logger.warning("File already in data base, skipping.")
    else:
        last_source_id += 1
        
        current_source = [last_source_id, xml_name, text_type, date, old_name, last_file_id]
        Con.insert(source_table, current_source)
        
        utterances_in_text = 0
        sentences_in_text = 0
        elements_in_text = 0
        this_utterance_id = 0
        this_sentence_id = 0

        for current_element in this_text:
            xml_process_element(current_element)

def load_files(Con, table_description):
    global last_file_id
    global last_source_id
    global last_sentence_id
    global last_utterance_id
    global last_speaker_id
    global last_lemma_id
    global last_word_id
    global last_token_id
    files = get_file_list(arguments.path)
    total_loads = len(files)
        
    progress = progressbar.ProgressBar(widgets=["Loading source files ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_loads)
    progress.start()
    file_count = 0
    
    # Read existing tables:
    file_dict = Con.read_table("file", lambda x: x[1])
    last_file_id = Con.get_max("file", "id")
    
    source_dict = Con.read_table(source_table, lambda x: x[1])
    last_source_id = Con.get_max(source_table, "id")

    speaker_dict = Con.read_table("speaker", lambda x: x[1])
    last_speaker_id = Con.get_max("speaker", "id")
    
    lemma_dict = Con.read_table("lemma", lambda x: "%s%s" % (x[2], x[1]))
    last_lemma_id = Con.get_max("lemma", "id")
    
    word_dict = Con.read_table("entity", lambda x: "%s%s" % (x[4], x[3]))
    last_word_id = Con.get_max("entity", "id")
    
    last_utterance_id = Con.get_max("utterance", "id")
    last_sentence_id = Con.get_max("sentence", "id")
    last_token_id = Con.get_max("element", "id")
    
    # Sequentially process files:
    for file_count, current_file in enumerate(files):
        if current_file not in file_dict:
            logger.info("Processing file %s" % current_file)
            last_file_id += 1
            process_file(current_file)
            Con.insert("file", [last_file_id, current_file])
            Con.commit()
        else:
            logger.info("Skipping file %s" % current_file)
        progress.update(file_count)

    Con.commit()
    progress.finish()

if __name__ == "__main__":
    arguments = check_arguments()
    arguments.c = True

    dbconnection.verbose = arguments.verbose
    if not arguments.db_name:
        arguments.db_name = arguments.name
    logger = set_logger(arguments.name)
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
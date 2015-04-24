from __future__ import unicode_literals 
import MySQLdb
import os, os.path
import fnmatch
import re
import datetime
import random
import logging
import sys
import progressbar

from lxml import etree

fake = False

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
            "Entity_id": (["Entity_Id"], 0, "HASH")
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
text_dict = {}
lemma_dict = {}
entity_dict = {}

InfoLevel = logging.INFO
Pretend = False

transcription_path  = "/usr/local/share/BNC/Texts/"
filter = "*.xml"

SupportedTags = ["w", "vocal", "gap", "c", "s", "u", "mw", "align", "wtext", "stext", "pause", "shift"]
IgnoreTags = ["unclear", "trunc", "event", "p", "pb", "hi", "head", "div", "list", "label", "item", "quote", "corr"]

def ToLog (Text, Level=logging.info):
    global CurrentFile
    Level ("%s" % (Text))

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
            ToLog ("c Node doesn't seem to have a text associated with it: %s" % node, logging.warning)
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
    global text_id
    global sentence_id
    global utterance_id
    global speaker_id
    global lemma_id
    global entity_id
    global element_id
    
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
        utterance_id += 1
        utterances_in_text += 1
        
        # speaker: get or create new
        speaker_key = tree_element.attrib ["who"].strip ()
        if speaker_key in speaker_dict:
            this_speaker_id = speaker_dict[speaker_key][0]
        else:
            speaker_id += 1
            new_speaker = [speaker_id, speaker_key]
            db_insert("speaker", new_speaker)
            speaker_dict[speaker_key] = new_speaker
            this_speaker_id = speaker_id
            
        current_utterance = [utterance_id, text_id, this_speaker_id, utterances_in_text]
        db_insert("utterance", current_utterance)
        this_utterance_id = utterance_id
        
    elif current_tag == "s":
        sentences_in_text += 1
        sentence_id += 1
        new_sentence = [sentence_id, text_id, this_speaker_id , sentences_in_text]
        db_insert("sentence", new_sentence)
        this_sentence_id = sentence_id
            
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
                lemma_id += 1
                new_lemma = [lemma_id, lemma_pos, lemma_text]
                db_insert("lemma", new_lemma)
                lemma_dict[lemma_key] = new_lemma
                this_lemma_id = lemma_id

        if "c5" in tree_element.attrib:
            C5 = tree_element.attrib ["c5"].strip()
        else:
            C5 = None
        
        # entity: get or create new            
        entity_key = "%s%s" % (current_value, C5)
        if entity_key in entity_dict:
            this_entity_id = entity_dict[entity_key][0]
        else:
            entity_id += 1
            new_entity = [entity_id, this_lemma_id, current_tag, C5, current_value]
            db_insert("entity", new_entity)
            entity_dict[entity_key] = new_entity
            this_entity_id = entity_id
            
        element_id += 1
        elements_in_text += 1
        new_element = [element_id, this_entity_id, this_sentence_id, elements_in_text]
        db_insert("element", new_element)

    for current_child in tree_element:
        xml_process_element(current_child)


def process_file(current_file):
    global text_id
    global sentence_id
    global utterance_id
    global speaker_id
    global lemma_id
    global entity_id
    global element_id

    root = etree.parse(current_file).getroot()

    idno_list = root.findall(".//idno")

    for current_idno in idno_list:
        current_type = current_idno.attrib["type"]
        current_value = current_idno.text.strip()
        if current_type == "bnc":
            xml_name = current_value
        elif current_type == "old":
            old_name = current_value
        else:
            ToLog("unknown idno type %s" % current_type, logging.warning)

    stext_list = root.find("stext")
    wtext_list = root.find("wtext")
            
    source_desc = root.find(".//sourceDesc")

    if (stext_list is None) == (wtext_list is None):
        ToLog("either: both stexts and wtexts found, or: neither stexts nor wtexts found", logging.warning)
    date = "unknown"
    if stext_list is not None:
        this_text = stext_list
        try:
            date = source_desc.find(".//recording").attrib["date"].strip()
        except KeyError:
            ToLog("No recording date found.", logging.warning)
    
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
        ToLog("Could not determine file date.", logging.warning)

    text_type = this_text.attrib ["type"].strip ()

    TotalElements = 0
    TagsDecl = root.find (".//tagsDecl/namespace")
    
    if xml_name in text_dict:
        #x = raw_input ("Delete (y/n)?")
        #if x == "y":
            #for CurrentSentence in Sentence.select ().join (Text).where (Text.XMLName == XMLName):
                #Elements = Element.delete ().where (Element.Sentence == CurrentSentence)
            #Sentence.join (Text).delete ().where (Text.XMLName == XMLName)
            #Utterance.join (Text).where (Text.XMLName == XMLName).delete ()
            #File.join (Text).where (Text.XMLName == XMLName).delete ()
            #Text.delete ().where (Text.XMLName == XMLName)
            #ToLog ("%s already in data base, deleted." % XMLName, logging.info)
        #else:
        ToLog("%s already in data base, skipping." % xml_name, logging.info)
    else:
        text_id += 1
        
        current_text = [text_id, xml_name, text_type, date, old_name, file_id]
        db_insert("text", current_text)
        
        utterances_in_text = 0
        sentences_in_text = 0
        elements_in_text = 0
        this_utterance_id = 0
        this_sentence_id = 0
    
    

        
        ##ProgressBar = progressbar.ProgressBar (TotalElements)
        
        #ProcessedElements = 0

        #CurrentSpeaker = ""
        ##CountSentences = 0
        ##CountUtterance = 0
        ##CountElements = 0
        ##CountBlock = 0
        ##MultiWordElements = 0
        ##MultiWordUnitStart = 0
        ##MultiWordUnit = []
        #LastEntity = [None, None, None, None, None]
        #ShiftStart = -1
        
        #CurrentUtterance = None
        #CurrentSentence = None
        #CurrentAlignment = None
        #ElementsInSentence = 0
        
        for current_element in this_text:
            xml_process_element(current_element)
        #except OperationalError as E:
            #ToLog ("PeeWee error %s " % str (E), logging.error)
        #else:
            #MySQLDB.commit()

        ##ProgressBar.Update(Force=True, Amount=0)
        ##if ProgressBar.Progressed <> ProgressBar.Max:
            ##ToLog ("Processed only %s out %s elements" % (ProgressBar.Progressed, ProgressBar.Max), logging.warning)


def get_file_list(path, file_dict={}, shuffle=False):
    #return ["/usr/local/share/BNC/Texts/A/A6/A60.xml"]

    #return ["/usr/local/share/BNC/A00_beautified_stripped.xml", "/usr/local/share/BNC/G5P_beautified.xml"]
    #return [ "/usr/local/share/BNC/A00_beautified_stripped.xml"]
    #return [ "/usr/local/share/BNC/G5P_beautified.xml"]
    #return [ "/usr/local/share/BNC/G5P_beautified_stripped.xml"]
    #return [ "/usr/local/share/BNC/FSA_beautified.xml"]
    #return ["/usr/local/share/BNC/Texts/F/FS/FSL.xml"]
    #return ["/usr/local/share/BNC/Texts/H/HM/HM4.xml"]
    #return ["/usr/local/share/BNC/Texts/B/BM/BMX.xml"]
    #return ["/usr/local/share/BNC/Texts/G/G2/G2B.xml"]
    #return ["/usr/local/share/BNC/Texts/F/FB/FBL.xml"]

    L = []
    for source_path, folders, files in os.walk(path):
        for current_file in files:
            if fnmatch.fnmatch(current_file, filter):
                full_name = os.path.join(source_path, current_file)
                if full_name not in file_dict:
                    L.append(full_name)
    if shuffle:
        random.shuffle(L)
    return L

def Execute(cursor, command):
    #print(command)
    try:
        return cursor.execute(command)
    except Exception as e:
        print(command)
        raise e

def db_connect():
    global Con
    Con = MySQLdb.connect (host="localhost", user="mysql", passwd="mysql", db=db_name)
    cur = Con.cursor()

    Execute(cur, "SET autocommit=0")
    Execute(cur, "SET unique_checks=0")
    Execute(cur, "SET foreign_key_checks=0")
    Con.commit()

def has_index(table_name, index_name):
    cur = Con.cursor()
    return Execute(cur, 'SHOW INDEX FROM %s WHERE Key_name = "%s"' % (table_name, index_name))

def create_index(table_name, index_name, variables, length):
    cur = Con.cursor()
    if length:
        Execute(cur, 'CREATE INDEX %s ON %s(%s)' % (index_name, table_name, ",".join(variables)))
    else:
        Execute(cur, 'CREATE INDEX %s ON %s(%s)' % (index_name, table_name, ",".join(variables)))

def db_optimize_table(table_name):
    cur = Con.cursor()
    Execute(cur, 'OPTIMIZE TABLE %s' % table_name)

def db_has_table(table_name):
    cur = Con.cursor()
    return Execute(cur, "SELECT * FROM information_schema.tables WHERE table_schema = '%s' AND table_name = '%s'" % (db_name, table_name))

def db_create_table(table_name, description, engine="MyISAM"):
    cur = Con.cursor()
    Execute(cur, 'CREATE TABLE %s (%s) ENGINE = %s' % (table_name, description, engine))

def db_read_table(table_name, FUN):
    cur = Con.cursor(MySQLdb.cursors.SSCursor)
    Execute(cur, "SELECT * FROM %s" % table_name)
    D = {}
    for current_entry in cur.fetchall():
        D[FUN(current_entry)] = current_entry
    return D

def db_get_max(table_name, column_name):
    cur = Con.cursor()
    Execute(cur, 'SELECT MAX(%s) FROM %s' % (column_name, table_name))
    return max(0, cur.fetchone() [0])

def db_find(table_name, column_name, value):
    cur = Con.cursor()
    Execute(cur, 'SELECT {column} FROM {table} WHERE {column} = "{value}"'.format(
        table=table_name, column=column_name, value=value))
    return cur.fetchall()

def db_get_field_type(table_name, column_name):
    cur = Con.cursor()
    Execute(cur, "SHOW FIELDS FROM %s WHERE Field = '%s'" % (table_name, column_name))
    Results = cur.fetchone()
    if Results:
        field_type = Results[1]
        if Results[2] == "NO":
            field_type += " NOT NULL"
        return field_type.upper()
    else:
        return None
    
def db_get_optimal_field_type(table_name, column_name):
    cur = Con.cursor()
    Execute(cur, "SELECT %s FROM %s PROCEDURE ANALYSE()" % (column_name, table_name))
    return cur.fetchone()[-1]
    
def db_modify_field_type(table_name, column_name, new_type):
    cur = Con.cursor()
    old_field = db_get_field_type(table_name, column_name)
    Execute(cur, "ALTER TABLE %s MODIFY %s %s" % (table_name, column_name, new_type))

def db_insert(table_name, data):
    if fake:
        return
    cur = Con.cursor()
    
    # take care of single quotation marks:
    if any("'" in str(x) for x in data):
        values = u", ".join(['"%s"' % x for x in data]).encode("utf-8")
    else:
        values = u", ".join(["'%s'" % x for x in data]).encode("utf-8")
    # take care of backslashes:
    values = values.replace("\\", "\\\\")

    S = "INSERT INTO {table} VALUES({values})".format(table = table_name, values = values)
    Execute(cur, S)

if __name__ == "__main__":
    logging.basicConfig(filename='bnc_db.log', format="%(asctime)s %(levelname)s %(message)s", level=InfoLevel)

    db_connect()
    
    total_columns = 0
    total_indices = 0
    
    for current_table in table_description:
        total_columns += len(table_description[current_table]["CREATE"]) - 1
        if "INDEX" in table_description[current_table]:
            total_indices += len(table_description[current_table]["INDEX"])
        if not db_has_table(current_table):
            db_create_table(current_table, ", ".join(table_description[current_table]["CREATE"]))
    Con.commit()

    file_dict = db_read_table("file", lambda x: x[1])
    file_id = db_get_max("file", "id")

    working_file_list = get_file_list(transcription_path, file_dict)

    file_counter = 0


    cur = Con.cursor()
    
    if working_file_list:
        text_dict = db_read_table("text", lambda x: x[1])
        text_id = db_get_max("text", "id")

        speaker_dict = db_read_table("speaker", lambda x: x[1])
        speaker_id = db_get_max("speaker", "id")
        
        lemma_dict = db_read_table("lemma", lambda x: "%s%s" % (x[2], x[1]))
        lemma_id = db_get_max("lemma", "id")
        
        entity_dict = db_read_table("entity", lambda x: "%s%s" % (x[4], x[3]))
        entity_id = db_get_max("entity", "id")
        
        utterance_id = db_get_max("utterance", "id")
        sentence_id = db_get_max("sentence", "id")
        element_id = db_get_max("element", "id")
        
        progress = progressbar.ProgressBar(widgets=[progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=len(working_file_list))
        progress.start()
        
        for i, current_file in enumerate(working_file_list):
            if not db_find("file", "Filename", current_file):
                file_id += 1
                db_insert("file", [file_id, current_file])
                process_file(current_file)
                Con.commit()
            progress.update(i)
        progress.finish()

    progress = progressbar.ProgressBar(widgets=["Optimizing field types ", progressbar.SimpleProgress(), " ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()], maxval=total_columns)
    progress.start()
    column_count = 0
    for i, current_table in enumerate(table_description):
        field_specs = table_description[current_table]["CREATE"]
        for current_spec in field_specs:
            match = re.match ("`(\w+)`", current_spec)
            if match:
                current_field = match.group(1)
                optimal_type = db_get_optimal_field_type(current_table, current_field)
                current_type = db_get_field_type(current_table, current_field)
                if current_type != optimal_type:
                    db_modify_field_type(current_table, current_field, optimal_type)
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
                if not has_index(current_table, current_index):
                    variables, length, index_type = description["INDEX"][current_index]
                    create_index(current_table, current_index, variables, length)
                index_count += 1
        progress.update(index_count)
        Con.commit()
    progress.finish()

# celex.py

from corpus import *
from options import * 

import csv

class Lexicon(BaseLexicon):
    provides = [LEX_WORDID, LEX_ORTH, LEX_LEMMA, LEX_POS, LEX_PHON, LEX_FREQ]    
    table_mappings = {'phono_lemma': 'epl', 
                    'morph_lemma': 'eml',
                    'syntax_lemma': 'esl',
                    'phono_word': 'epw'}
    delimiter = "\\"
    
    def __init__(self, resource):
        self.resource = resource
        base_path = cfg.celex_base_path
        for current_mapping in self.table_mappings:
            current_part = self.table_mappings[current_mapping]
            current_file = "%s.cd" % current_part
            new_by_id_table = {}
            new_by_string_table = {}
            current_path = os.path.join(base_path, current_part, current_file)
            
            with open (current_path, "rt") as input_file:
                for current_line in csv.reader(input_file, delimiter=self.delimiter, quoting=csv.QUOTE_NONE):
                    current_id, current_string = current_line[0:2]
                    new_by_id_table [int(current_id)] = current_line
                    if current_string not in new_by_string_table:
                        new_by_string_table[current_string] = []
                    new_by_string_table[current_string].append(current_line)
            
            self.__dict__["%s_by_id" % current_mapping] = new_by_id_table
            self.__dict__["%s_by_string" % current_mapping] = new_by_string_table

        self.pos_dict = {}
        self.pos_dict[1]  = "N"
        self.pos_dict[2]  = "A"   
        self.pos_dict[3]  = "NUM"
        self.pos_dict[4]  = "V"
        self.pos_dict[5]  = "ART"
        self.pos_dict[6]  = "PRON"
        self.pos_dict[7]  = "ADV"
        self.pos_dict[8]  = "PREP"
        self.pos_dict[9]  = "C"
        self.pos_dict[10] = "I"
        self.pos_dict[11] = "SCON"
        self.pos_dict[12] = "CCON"
        self.pos_dict[13] = "LET"
        self.pos_dict[14] = "ABB"
        self.pos_dict[15] = "TO"

    def get_entry(self, word_id):
        error_value = [word_id, "<na>", "<na>", "<na>", "<na>", 0]
        entry = self.Entry(self.provides)
        entry.word_id = word_id
        try:
            entry.orth = self.phono_word_by_id[word_id][1]
            lemma_id = int(self.phono_word_by_id[word_id][3])
            entry.lemma = self.phono_lemma_by_id[lemma_id][1]
            entry.pos = self.pos_dict[int(self.syntax_lemma_by_id[lemma_id][3])]
        except KeyError:
            entry.set_values(error_value)
        return entry

    def is_part_of_speech(self, pos):
        return pos in self.pos_dict.values()

    def get_pos_label(self, pos_id):
        return self.pos_dict[pos_id]
    
    def get_pos(self, word_id):
        lemma_id = int(self.phono_word_by_id[word_id][3])
        return self.get_pos_label(int(self.syntax_lemma_by_id[lemma_id][3]))

class Corpus(BaseCorpus):
    def __init__(self, lexicon, resource):
        super(Corpus, self).__init__(lexicon, resource)

    def get_wordid_list(self, Token):
        word_specifiers, lemma_specifiers, class_specifiers, negated = Token.get_parse()
        word_id_list = []
        
        if lemma_specifiers:
            lemma_id_list = []
            for current_specifier in lemma_specifiers:
                try:
                    for word_forms in self.lexicon.phono_lemma_by_string[current_specifier]:
                        lemma_id_list.append(int(word_forms[0]))
                except KeyError:
                    pass
            for current_id in self.lexicon.phono_word_by_id:
                if int(self.lexicon.phono_word_by_id[current_id][3]) in lemma_id_list:
                    word_id_list.append(current_id)
        elif word_specifiers:
            for current_specifier in word_specifiers:
                try:
                    for word_forms in self.lexicon.phono_word_by_string[current_specifier]:
                        word_id_list.append(int(word_forms[0]))
                except Exception as e:
                    pass
        if Token.class_specifiers:
            return [x for x in word_id_list if self.lexicon.get_pos(x) in Token.class_specifiers]
        else:
            return word_id_list
       
    def get_wordid_frequency(self, WordId):
        return int(self.lexicon.phono_word_by_id[WordId][2])

    def run_query(self, Query):
        L = []
        for current_token in Query.tokens:
            current_token.parse()
            wordid_list = self.get_wordid_list(current_token)
            for current_id in wordid_list:
                f = self.get_wordid_frequency(current_id)
                current_result = {"Freq": f, "W1": current_id}
                L.append(current_result)
        if not L:
            Query.Results = []
        else:
            Query.set_result_list(L)

if __name__ == "__main__":
    print """This module is part of the Coquery corpus query tool and cannot be run on its own."""
    sys.exit(1)

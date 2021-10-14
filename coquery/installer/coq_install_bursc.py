from __future__ import unicode_literals
from __future__ import print_function
import codecs
import csv
import os
import collections, difflib, string

from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.tables import (
    Identifier, Column, Link,
    varchar, enum, smallint, mediumint, real)
# The class corpus_code contains the Python source code that will be
# embedded into the corpus library. It provides the Python code that will
# override the default class methods of CorpusClass by methods that are
# tailored for the BURSC corpus.

class corpus_code():
    def sql_string_get_time_info(self, token_id):
        return "SELECT {} FROM {} WHERE {} = {}".format(
                self.resource.corpus_time,
                self.resource.corpus_table,
                self.resource.corpus_id,
                token_id)

    def get_time_info_header(self):
        return ["Time"]

#class BuilderClass(BaseCorpusBuilder):
    #file_filter = "*.txt"

    #word_table = "word"
    #word_id = "WordId"
    #word_label = "Word"
    #word_pos = "Pos"
    #word_columns = [
        #Identifier(word_id, mediumint(7, unsigned=True, not_null=True)),
        #Column(word_label, varchar(43, not_null=True)),
        #Column(word_pos, varchar(24, not_null=True))]

    #file_table = "file"
    #file_id = "FileId"
    #file_name = "Filename"
    #file_path = "Path"
    #file_columns = [
        #Identifier(file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
        #Column(file_name, "CHAR(12) NOT NULL"),
        #Column(file_path, "VARCHAR(1024) NOT NULL")]

    #source_table = "Sources"
    #source_id = "SourceId"
    #source_story = "Story"
    #source_storytype = "Storytype"
    #source_paragraph = "Paragraph"
    #source_noisy = "IsNoisy"
    #source_columns = [
        #Identifier(source_id, "SMALLINT(3) UNSIGNED NOT NULL"),
        #Column(source_story, "CHAR(3) NOT NULL"),
        #Column(source_storytype =
        #Column(file_path, "TINYTEXT NOT NULL")]


    #speaker_table = "Speakers"
    #speaker_id = "SpeakerId"
    #speaker_gender = "Gender"
    #speaker_type = "Type"

    #segment_table = "Segments"
    #segment_id = "SegmentId"
    #segment_origin_id = "FileId"
    #segment_label = "Segment"
    #segment_starttime = "SegStart"
    #segment_endtime = "SegEnd"

    #corpus_table = "corpus"
    #corpus_id = "TokenId"
    #corpus_word_id = "WordId"
    #corpus_source_id = "SourceId"
    #corpus_file_id = "FileId"
    #corpus_speaker_id = "SpeakerId"
    #corpus_starttime = "Start"
    #corpus_endtime = "End"
    #corpus_columns = [
        #Identifier(corpus_id, "INT(9) UNSIGNED NOT NULL"),
        #Column(corpus_starttime, "REAL(11,6) NOT NULL"),
        #Column(corpus_endtime, "REAL(11,6) NOT NULL"),
        #Link(corpus_word_id, word_table),
        #Link(corpus_source_id, source_table),
        #Link(corpus_file_id, file_table),
        #Link(corpus_speaker_id, speaker_table)]

    #def __init__(self):
       ## all corpus builders have to call the inherited __init__ function:
        #super(BuilderClass, self).__init__()
        
        ## Read only .txt files from the corpus path:
        
        ## specify which features are provided by this corpus and lexicon:
        #self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_PHON", "LEX_POS"]
        #self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_TIMING"]
        #self.documentation_url = "https://catalog.ldc.upenn.edu/LDC96S36"

        #self.add_time_feature(self.corpus_starttime)
        #self.add_time_feature(self.corpus_endtime)

        #self.add_annotation(self.segment_table, self.corpus_table)

        ## Specify that the corpus-specific code is contained in the dummy
        ## class 'corpus_code' defined above:
        #self._corpus_code = corpus_code
        
    #def get_description(self):
        #return "This script makes the Boston University Radio Speech Corpus available to Coquery by reading the corpus data files from {} into the MySQL database '{}'.".format(self.arguments.path, self.arguments.db_name)

    #def get_transcript(self, word):
        #try:
            #i = self._transcript_index
            #while True:
                #_, transcript = self._transcript_list[i]
                #i += 1
                #if word == _:
                    #self._transcript_index = i
                    #return transcript
        #except IndexError as e:
            #print(self._file_name)
            #print(i, word, self._transcript_index)
            #print("\n".join(["{:<3} {:<30} {}".format(i, word, transcript) for i, (word, transcript) in enumerate(self._transcript_list)]))
            #raise e
        
    #def get_pos(self, word):
        #i = self._pos_index
        ## Sometimes, words start with (undocumented) braces. They may mess
        ## up POS retrieval, and are stripped.
        #word = word.strip("}").strip("{")
        #while True:
            #try:
                #_, pos = self._pos_list[i]
            #except IndexError as e:
                #print(self._file_name)
                #print(i, self._pos_index)
                #print(word)
                ##print(self._pos_list)
                ##print(self._pos_list[i:])
                #return "<NA>"
            ## check if word matches the next word in the pos list:
            #if word.lower()[:min(len(word), len(_))] != _.lower()[:min(len(word), len(_))]:
                #i += 1
                #if i >= len(self._pos_list):
                    #pos = "<NA>"
                    #break
            #else:
                #self._pos_index = i + 1
                #break
        #return pos

    #def process_wrd_file(self, filename):
        #root, ext = os.path.splitext(filename)
        #self._wrd_list = []
        #try:
            #with codecs.open("{}.wrd".format(root), "r", encoding="latin-1") as wrd_file:
                #in_body = False
                #for row in wrd_file:
                    #row = row.strip()
                    #if row == "#":
                        #in_body = True
                    #elif in_body:
                        #try:
                            #time, _, label = row.split()
                        #except ValueError:
                            #if len(row.split()) > 3:
                                #print("[{}]".format(row))
                        #else:
                            #if label.rfind("/") > -1:
                                #label = label[:label.rfind("/")]
                            #if not label.startswith(">"):
                                #self._wrd_list.append([label, time])
            #self._wrd_index = 0
        #except IOError:
            #pass

    #def process_pos_file(self, filename):
        ## try to read the .pos file for the .wrd file:
        #self._pos_list = collections.OrderedDict()
        #root, ext = os.path.splitext(filename)
        #try:
            #with codecs.open("{}.pos".format(root), "r") as pos_file:
                #for row in pos_file:
                    #row = row.strip()
                    #if row.strip():
                        #word, pos = row.split()
                        #self._pos_list[word] = pos
            #self._pos_index = 0
        #except IOError:
            #pass

    #def process_transcript_file(self, filename):
        #self._transcript_list = collections.OrderedDict()
        #root, ext = os.path.splitext(filename)
        ## try to read the .aln file:
        #transcript_file = "{}.alb".format(root)
        #if not os.path.exists(transcript_file):
            #transcript_file = "{}.ala".format(root)
        #if os.path.exists(transcript_file):
            #with codecs.open(transcript_file, "r") as transcript_file:
                #transcript = []
                #for row in transcript_file:
                    #if row.strip():
                        #if row.startswith(">"):
                            #word = row[1:].strip()
                            #if word.lower() not in ["endsil", "sil"]:
                                #self._transcript_list[word] = " ".join(transcript)
                            #transcript = []
                        #else:
                            #if row.count("\t") == 2:
                                #phone, start, dur = row.split("\t")
                                #if phone.lower() not in ["brth", "pau", "sil", "h#"]:
                                    #transcript.append(phone)
                            #else:
                                #print(row)
        #self._transcript_index = 0
        
    #def process_txt_file(self, filename):
        #try:
            #with codecs.open(filename, "r", encoding=self.arguments.encoding) as input_file:
                #raw_text = input_file.read()
        #except UnicodeDecodeError:
            #with codecs.open(filename, "r", encoding="ISO-8859-1") as input_file:
                #raw_text = input_file.read()
        #self._word_list = []
        #for word in raw_text.split():
            #word = word.strip()
            #if word.lower() != "brth":
                #self._word_list.append(word)

    #def normalize(self, word):
        #for p in string.punctuation:
            #word = word.replace(p, '')
        #return word.lower().strip()
    
    #def store_filename(self, *args):
        #pass

    ## Redefine the process_file method so that the .words files provided
    ## by the Buckeye corpus are handled correctly:
    #def process_file(self, filename):
        #self.process_wrd_file(filename)
        #self.process_pos_file(filename)
        #self.process_transcript_file(filename)
        #self.process_txt_file(filename)
        ##print("Words in .wrd:", len(self._wrd_list))
        ##print("Words in .txt: ", len(self._word_list))
        #wrds = [self.normalize(x) for x, time in self._wrd_list]
        #txt = [self.normalize(x) for x in self._word_list]
        
        #diff = list(difflib.ndiff(wrds, txt))
        #wrds_counter = 0
        #txt_counter = 0
        #diff = [x for x in diff if not(x.startswith("?")) and x.strip()]
        #if len(diff) != len(txt):
            #print(filename)
            #for i, x in enumerate(diff):
                #fields = x.split()
                #if len(fields) == 1:
                    #code = " "
                    #word = fields[0]
                #else:
                    #code = fields[0]
                    #word = fields[1]

                #if diff[i].startswith("-"):
                    #if not diff[i+1].startswith("+"):
                        #print("Insert '{}' at {}".format(self._wrd_list[wrds_counter][0], txt_counter))
                        #self._word_list.insert(txt_counter, self._wrd_list[wrds_counter][0])
                        #txt_counter += 1
                        #wrds_counter += 1
                    #else:
                        #print("Change from '{}' to '{}'".format(self._word_list[txt_counter],
                                                        #self._wrd_list[wrds_counter][0]))
                        #self._word_list[txt_counter] = self._wrd_list[wrds_counter][0]
                #else:
                    #txt_counter += 1
                    #wrds_counter += 1

        #wrds = [self.normalize(x) for x, time in self._wrd_list]
        #txt = [self.normalize(x) for x in self._word_list]
        
        #diff = list(difflib.ndiff(wrds, txt))
        #if len(diff) != len(txt):
            #print(filename)
            #for i, x in enumerate(diff):
                #print(x)


#if __name__ == "__main__":
    #BURSCBuilder().build()

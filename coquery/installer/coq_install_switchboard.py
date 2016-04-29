# -*- coding: utf-8 -*-

"""
coq_install_switchboard.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import codecs
import tarfile
import os
import pandas as pd

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from coquery.corpusbuilder import *
from coquery.unicode import utf8
from coquery.bibliography import *

class BuilderClass(BaseCorpusBuilder):
    file_filter = "*.*"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_uttered = "UtteredWord"
    word_transcript = "Transcript"
    
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    file_duration = "Duration"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    corpus_speaker_id = "SpeakerId"
    corpus_source_id = "ConversationId"
    corpus_starttime = "Start"
    corpus_endtime = "End"

    speaker_table = "Speakers"
    speaker_id = "SpeakerId"
    speaker_label = "Speaker"
    speaker_sex = "Sex"
    speaker_birth = "BirthYear"
    speaker_dialectarea = "DialectArea"
    speaker_education = "Education"

    source_table = "Conversations"
    source_id = "ConversationId"
    # ConversationId is the number used e.g. in the file names
    source_label = "Conversation" 
    source_topic = "Topic"
    source_difficulty = "Difficulty"
    source_topicality = "Topicality"
    source_naturalness = "Naturalness"
    source_remarks = "Remarks"

    special_files = ["call_con_tab.csv", "caller_tab.csv", "topic_tab.csv", 
                     "rating_tab.csv"]
    expected_files = special_files + ["switchboard_word_alignments.tar.gz"]

    _regexp = re.compile("sw(\d\d\d\d)([A|B])-ms98-a-word\.text")

    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(32) NOT NULL"),
             Column(self.word_uttered, "VARCHAR(23) NOT NULL"),
             Column(self.word_transcript, "VARCHAR(50) NOT NULL")])

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "INT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "VARCHAR(70) NOT NULL"),
             Column(self.file_duration, "REAL NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])

        self.create_table_description(self.speaker_table,
            [Identifier(self.speaker_id, "INT(4) UNSIGNED NOT NULL"),
             Column(self.speaker_label, "VARCHAR(4) NOT NULL"),
             Column(self.speaker_sex, "ENUM('FEMALE','MALE') NOT NULL"),
             Column(self.speaker_birth, "INT(4) UNSIGNED NOT NULL"),
             Column(self.speaker_dialectarea, "VARCHAR(13) NOT NULL"),
             Column(self.speaker_education, "INT(1) UNSIGNED NOT NULL")])
    
        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "INT(3) UNSIGNED NOT NULL"),
             Column(self.source_label, "VARCHAR(4) NOT NULL"),
             Column(self.source_topic, "VARCHAR(28) NOT NULL"),
             Column(self.source_difficulty, "INT(1) UNSIGNED"),
             Column(self.source_topicality, "INT(1) UNSIGNED"),
             Column(self.source_naturalness, "INT(1) UNSIGNED"),
             Column(self.source_remarks, "VARCHAR(50)")])

        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_speaker_id, self.speaker_table),
             Link(self.corpus_source_id, self.source_table),
             Column(self.corpus_starttime, "DECIMAL(17,6) UNSIGNED NOT NULL"),
             Column(self.corpus_endtime, "DECIMAL(17,6) NOT NULL")])

        self.add_time_feature(self.corpus_starttime)
        self.add_time_feature(self.corpus_endtime)
        self.add_time_feature(self.speaker_birth)
        
        self._file_id = 0
        self._token_id = 0
        
        self.surface_feature = "word_uttered"
        
        self.add_building_stage(self._build_store_conversation_table)

    @staticmethod
    def get_name():
        return "Switchboard-1"

    @staticmethod
    def get_db_name():
        return "switchboard"
    
    @staticmethod
    def get_title():
        return "Switchboard-1 Telephone Speech Corpus"
        
    @staticmethod
    def get_language():
        return "English"
    
    @staticmethod
    def get_language_code():
        return "en-US"
        
    @staticmethod
    def get_description():
        return [
            "The Switchboard-1 Telephone Speech Corpus was originally collected by Texas Instruments in 1990-1, under DARPA sponsorship. The first release of the corpus was published by NIST and distributed by the LDC in 1992-3. Since that release, a number of corrections have been made to the data files as presented on the original CD-ROM set and all copies of the first pressing have been distributed.",
            "Switchboard is a collection of about 2,400 two-sided telephone conversations among 543 speakers (302 male, 241 female) from all areas of the United States. A computer-driven robot operator system handled the calls, giving the caller appropriate recorded prompts, selecting and dialing another person (the callee) to take part in a conversation, introducing a topic for discussion and recording the speech from the two subjects into separate channels until the conversation was finished. About 70 topics were provided, of which about 50 were used frequently. Selection of topics and callees was constrained so that: (1) no two speakers would converse together more than once and (2) no one spoke more than once on a given topic."]

    @staticmethod
    def get_references():
        return [Book(
            authors=PersonList(Person(first="John", last="Godfrey"), Person(first="Edward", last="Holliman")),
            year=1993,
            title="Switchboard-1 Release 2 LDC97S62. Web Download",
            publisher="Linguistic Data Consortium",
            address="Philadelphia")]

    @staticmethod
    def get_url():
        return "https://catalog.ldc.upenn.edu/LDC97S62"

    @staticmethod
    def get_license():
        return "<a href='https://catalog.ldc.upenn.edu/license/ldc-non-members-agreement.pdf'>LDC User Agreement for Non-Members</a>"

    @staticmethod
    def get_installation_note():
        return """
        <p><b>Data files, word alignments, and transcriptions</b></p>
        <p>Unfortunately, the Switchboard-1 corpus is a somewhat inconsistent
        release. In order to be able to use most features of this corpus in
        Coquery, several data files have to be obtained from different 
        locations. In order to proceed with the installation, you are 
        advised to copy all required files to a single directory on your 
        computer.</p>
        <p>The corpus data files which can be obtained <a href='https://catalog.ldc.upenn.edu/LDC97S62'>
        from the Linguistic Data Consortium</a> consist of only the audio
        files, without any annotations. <b>These files are not used by 
        Coquery, and you can install the Switchboard corpus module without
        buying the audio files.</b></p>
        <p>The <a href='https://catalog.ldc.upenn.edu/docs/LDC97S62/'>
        LDC Online Documentation directory</a> for Switchboard-1 contains
        files with details on the speakers and the conversations. Please 
        download the following files:
        <ul>
            <li><a href='https://catalog.ldc.upenn.edu/docs/LDC97S62/caller_tab.csv'>caller_tab.csv</a> – speaker information</li>
            <li><a href='https://catalog.ldc.upenn.edu/docs/LDC97S62/call_con_tab.csv'>call_con_tab.csv</a> – conversation details</li>
            <li><a href='https://catalog.ldc.upenn.edu/docs/LDC97S62/rating_tab.csv'>rating_tab.csv</a> – conversation ratings</li>
            <li><a href='https://catalog.ldc.upenn.edu/docs/LDC97S62/topic_tab.csv'>topic_tab.csv</a> – conversation topics</li>
        </ul></p>            
        <p>Transcriptions and word alignments are provided for free by the 
        <a href='https://www.isip.piconepress.com/'>Institute for Signal and Information Processing</a>. From their <a href='https://www.isip.piconepress.com/projects/switchboard/'>Switchboard project site</a>, the following file is required for installation:
        <ul>
            <li><a href='https://www.isip.piconepress.com/projects/switchboard/releases/switchboard_word_alignments.tar.gz'>switchboard_word_alignments.tar.gz</a> – Manually corrected word alignments</li></ul></p>
        """

    @classmethod
    def get_file_list(cls, *args, **kwargs):
        """
        Make sure that the files listed in the class variable 'special_files'
        appear first in the actual file list. The order from that variable is
        retained.
        """
        l = super(BuilderClass, cls).get_file_list(*args, **kwargs)
        new_pos = 0
        for i, x in enumerate(cls.special_files):
            if x in l:
                l.remove(x)
                l.insert(new_pos, x)
                new_pos += 1
                
        return l

    def process_file(self, filename):
        basename = os.path.basename(filename)
        if basename == "call_con_tab.csv":
            self._df_conv = pd.read_csv(filename, sep=", ",
                names=[self.source_id, "Side", "SpeakerId", "PhoneNum", "Length", "ivi_no", "ConRemarks", "Active"])
            self._df_conv.ivi_no = self._df_conv.ivi_no.apply(str)
            _idx = []
            for x in range(len(self._df_conv) // 2):
                _idx += [x + 1] * 2
            self._df_conv["_index"] = _idx
            self._df_source = self._df_conv

        elif basename == "topic_tab.csv":
            self._df_topic = pd.read_csv(filename,
                names=[self.source_topic, "ivi_no", "prompt",
                       "flg", "remarks", "prompt_cont"])
            self._df_topic.ivi_no = self._df_topic.ivi_no.apply(str)

        elif basename == "rating_tab.csv":
            self._df_rating = pd.read_csv(filename,
                names=[self.source_id, 
                       self.source_difficulty,
                       self.source_topicality,
                       self.source_naturalness,
                       "V1", "V2", "V3", "V4", "V5", "V6",
                       self.source_remarks])
            
        elif basename == "caller_tab.csv":
            self._df_caller = pd.read_csv(filename,
                names=[self.speaker_id, 
                       "V1", "V2", 
                       self.speaker_sex, 
                       self.speaker_birth, 
                       self.speaker_dialectarea, 
                       self.speaker_education,
                       "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10"])
            self._df_caller[self.speaker_dialectarea] = self._df_caller[self.speaker_dialectarea].apply(lambda x: x.strip('" '))
            self._df_caller[self.speaker_sex] = self._df_caller[self.speaker_sex].apply(lambda x: x.strip('" '))

            self._df_caller[self.speaker_label] = self._df_caller[self.speaker_id].apply(utf8)
            self._df_caller = self._df_caller[
                [self.speaker_id, self.speaker_label,
                 self.speaker_sex, self.speaker_birth,
                 self.speaker_dialectarea, self.speaker_education]]
            
            self.DB.load_dataframe(self._df_caller, self.speaker_table, None, if_exists="replace")
            
        elif basename == "switchboard_word_alignments.tar.gz":
            with tarfile.open(filename, "r:gz") as tar_file:
                for member in tar_file.getmembers():
                    if self._interrupted:
                        return
                    match = self._regexp.match(os.path.basename(member.name))
                    if match:
                        self._file_id += 1
                        self._duration = 0
                        self._process_words_file(tar_file, member, match)
                    
                        self._value_file_name = "{}/{}".format(basename, member.name)
                        self._value_file_path = os.path.split(filename)[0]
                        
                        d = {self.file_name: self._value_file_name,
                            self.file_id: self._file_id,
                            self.file_duration: self._duration,
                            self.file_path: self._value_file_path}
                        x = self.table(self.file_table).add(d)
                        self.commit_data()


    def _build_store_conversation_table(self):
        #print(self._df_source.head())
        #print(self._df_topic.head())
        #print(self._df_rating.head())
        if hasattr(self, "_df_source"):
            if hasattr(self, "_df_topic"):
                df = self._df_source.merge(self._df_topic, on="ivi_no")
            else:
                df = pd.DataFrame(self._df_source)
            if hasattr(self, "_df_rating"):
                df = df.merge(self._df_rating, on=self.source_id)
                
        df[self.source_label] = df[self.source_id].apply(str)
        df = df[
            [self.source_id, 
             self.source_label, 
             self.source_topic,
             self.source_difficulty,
             self.source_topicality,
             self.source_naturalness,
             self.source_remarks]]
        df = df.drop_duplicates()
        df[self.source_id] = range(1, len(df.index) + 1)
        self.DB.load_dataframe(df, self.source_table, None, if_exists="replace")

    def _process_words_file(self, tar_file, member, match):
        logger.info("Processing file {}".format(member.name))
              
        conv_id = int(match.group(1))
        side = '"{}"'.format(match.group(2))
        row = self._df_conv[(self._df_conv[self.source_id] == conv_id) & (self._df_conv.Side == side)]
        speaker_id = row.SpeakerId.values[0]
        source_id = row["_index"].values[0]

        input_data = list(tar_file.extractfile(member))

        for row in input_data:
            if self._interrupted:
                return
            try:
                source, start, end, label = [x.strip() for x in row.split()]
            except ValueError:
                print(member.name, row)
                print("---")
                continue
            label = utf8(label)
            source = utf8(source)
            uttered = label
            match = re.match("(.*)\[(.*)\](.*)", label)
            if match:
                matched = match.group(2)
                if matched.startswith("laughter-"):
                    label = matched.partition("laughter-")[-1]
                elif match.group(1) != "" or match.group(3) != "":
                    # incomplete utterance, e.g. 'reall[y]-' or 'sim[ilar]-'
                    label = "{}{}{}".format(*match.groups()).strip("-")
            d = {self.word_label: label.lower(),
                 self.word_uttered: uttered,
                 self.word_transcript: ""}
            self._word_id = self.table(self.word_table).get_or_insert(d)
            
            d = {self.corpus_word_id: int(self._word_id),
                 self.corpus_starttime: float(start),
                 self.corpus_endtime: float(end),
                 self.corpus_file_id: int(self._file_id),
                 self.corpus_source_id: int(source_id),
                 self.corpus_speaker_id: int(speaker_id)}
            self.add_token_to_corpus(d)
            self._duration = max(self._duration, float(end))


    def store_filename(self, file_name):
        # because of the zip file structure, the installer handles 
        # storing the filenames elsewhere, namely in process_file().
        pass
                
if __name__ == "__main__":
    BuilderClass().build()

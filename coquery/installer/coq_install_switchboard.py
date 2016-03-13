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

    # Conversation data is contained in
    # https://www.isip.piconepress.com/projects/switchboard/doc/statistics/ms98_speaker_stats.text    # https://www.isip.piconepress.com/projects/switchboard/doc/statistics/ms98_conv_stats.text
    speaker_table = "Speakers"
    speaker_id = "SpeakerId"
    speaker_label = "Speaker"
    speaker_gender = "Gender"
    
    # Conversation data is contained in
    # https://www.isip.piconepress.com/projects/switchboard/doc/statistics/ms98_conv_stats.text
    source_table = "Conversations"
    source_id = "ConversationId"
    source_label = "Conversation"
    source_topic = "Topic"
    source_difficulty = "Difficulty"

    expected_files = [
        "call_con_tab.csv", "rating_tab.csv", "caller_tab.csv",
        "switchboard_word_alignments.tar.gz"]

    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(40) NOT NULL"),
             Column(self.word_transcript, "VARCHAR(50) NOT NULL")])

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "INT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "VARCHAR(18) NOT NULL"),
             Column(self.file_duration, "REAL NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])

        self.create_table_description(self.speaker_table,
            [Identifier(self.speaker_id, "TINYINT(3) UNSIGNED NOT NULL"),
             Column(self.speaker_label, "VARCHAR(4) NOT NULL"),
             Column(self.speaker_gender, "ENUM('F','M') NOT NULL")])

        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "INT(3) UNSIGNED NOT NULL"),
             Column(self.source_label, "VARCHAR(4) NOT NULL"),
             Column(self.source_topic, "VARCHAR(28) NOT NULL"),
             Column(self.source_difficulty, "ENUM('very easy','easy','medium','hard','very hard','???') NOT NULL")])

        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_speaker_id, self.speaker_table),
             Link(self.corpus_source_id, self.source_table),
             Column(self.corpus_starttime, "DECIMAL(17,6) NOT NULL"),
             Column(self.corpus_endtime, "DECIMAL(17,6) NOT NULL")])

        self.add_time_feature(self.corpus_starttime)
        self.add_time_feature(self.corpus_endtime)
        
        self._file_id = 0
        self._token_id = 0

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
            <li><a href='https://catalog.ldc.upenn.edu/docs/LDC97S62/call_con_tab.csv'>call_con_tab.csv</a> – conversation details</li>
            <li><a href='https://catalog.ldc.upenn.edu/docs/LDC97S62/rating_tab.csv'>rating_tab.csv</a> – conversation ratings</li>
            <li><a href='https://catalog.ldc.upenn.edu/docs/LDC97S62/caller_tab.csv'>caller_tab.csv</a> – speaker information</li></ul></p>
        <p>Transcriptions and word alignments are provided for free by the 
        <a href='https://www.isip.piconepress.com/'>Institute for Signal and Information Processing</a>. From their <a href='https://www.isip.piconepress.com/projects/switchboard/'>Switchboard project site</a>, the following file is required for installation:
        <ul>
            <li><a href='https://www.isip.piconepress.com/projects/switchboard/releases/switchboard_word_alignments.tar.gz'>switchboard_word_alignments.tar.gz</a> – Manually corrected word alignments</li></ul></p>
        """


    def process_file(self, filename):

        if filename == "call_con_tab.csv":
            self._df_conv = pd.DataFrame.from_csv(filename)
        elif filename == "rating_tab.csv":
            self._df_rating = pd.DataFrame.from_csv(filename)
        elif filename == "caller_tab.csv":
            self._df_caller = pd.DataFrame.from_csv(filename)
        elif filename == "switchboard_word_alignments.tar.gz":
            tar_file = tarfile.TarFile(filename)
            
            # taken from Buckeye installer:
            
            #for small_zip_name in zip_file.namelist():
                #speaker_name = os.path.basename(small_zip_name)
                #self._speaker_id = int(speaker_name[1:3])
                #if speaker_name in self._zip_files:
                    #small_zip_file = zipfile.ZipFile(StringIO(zip_file.read(small_zip_name)))
                    #self._process_words_file(small_zip_file, speaker_name)

                    #self._value_file_name = "{}/{}".format(os.path.basename(filename), speaker_name)
                    #self._value_file_path = os.path.split(filename)[0]
                    #self._value_file_duration = self._duration
                    #d = {self.file_name: self._value_file_name,
                        #self.file_duration: self._value_file_duration,
                        #self.file_path: self._value_file_path}
                    #self._file_id = self.table(self.file_table).get_or_insert(d)
            
            pass
        return

    def _process_words_file(self, speaker_zip, filename):
        return

        ## skeleton from Buckeye installer:
        #file_name, _ = os.path.splitext(filename)
        #words_file = "{}.words".format(file_name)
        #input_data = speaker_zip.read(words_file)
        #input_data = [utf8(x.strip()) for x in input_data.splitlines() if x.strip()]
        
        #segments = self._get_segments(speaker_zip, filename)
        #last_row = None
        #for row in input_data:
            #continue

            #self.add_token_to_corpus(
                    #{self.corpus_word_id: self._token_id, 
                     #self.corpus_speaker_id: self._speaker_id,
                    #self.corpus_file_id: self._file_id + 1,
                    #self.corpus_starttime: start_time,
                    #self.corpus_endtime: end_time})

    def store_filename(self, file_name):
        # because of the zip file structure, the installer handles 
        # storing the filenames elsewhere, namely in process_file().
        pass
                
if __name__ == "__main__":
    BuilderClass().build()

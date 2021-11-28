# -*- coding: utf-8 -*-

"""
coq_install_switchboard.py is part of Coquery.

Copyright (c) 2016–2021 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import tarfile
import os
import pandas as pd
import numpy as np
import logging
import re

from coquery import options
from coquery.corpusbuilder import BaseCorpusBuilder, IO_Stream
from coquery.unicode import utf8
from coquery.bibliography import Book, PersonList, Person
from coquery.tables import Column, Identifier, Link


class resource_code():
    def audio_to_source(self, audio_name):
        path, file_name = os.path.split(audio_name)
        base, ext = os.path.splitext(file_name)
        n = base[3:]
        return [f"sw{n}A-ms98-a-word",
                f"sw{n}B-ms98-a-word"]

    def convert_source_to_audio(self, source_name):
        path, file_name = os.path.split(source_name)
        base, ext = os.path.splitext(file_name)
        n = base[2:6]
        return f"sw0{n}"


class BuilderClass(BaseCorpusBuilder):
    file_filter = "*.*"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_uttered = "UtteredWord"
    word_columns = [
        Identifier(word_id, "SMALLINT(5) UNSIGNED NOT NULL"),
        Column(word_label, "VARCHAR(33) NOT NULL"),
        Column(word_uttered, "VARCHAR(33) NOT NULL")]

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    file_duration = "Duration"
    file_audio_path = "AudioPath"
    file_columns = [
        Identifier(file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
        Column(file_name, "VARCHAR(92) NOT NULL"),
        Column(file_duration, "REAL NOT NULL"),
        Column(file_path, "VARCHAR(2048) NOT NULL"),
        Column(file_audio_path, "VARCHAR(2048) NOT NULL")]

    speaker_table = "Speakers"
    speaker_id = "SpeakerId"
    speaker_sex = "Sex"
    speaker_birth = "BirthYear"
    speaker_dialectarea = "DialectArea"
    speaker_education = "Education"
    speaker_columns = [
        Identifier(speaker_id, "SMALLINT(4) UNSIGNED NOT NULL"),
        Column(speaker_sex, "ENUM('FEMALE','MALE') NOT NULL"),
        Column(speaker_birth, "INT(4) UNSIGNED NOT NULL"),
        Column(speaker_dialectarea, "VARCHAR(13) NOT NULL"),
        Column(speaker_education, "INT(1) UNSIGNED NOT NULL")]

    source_table = "Conversations"
    source_id = "ConversationId"
    source_topic = "Topic"
    source_difficulty = "Difficulty"
    source_topicality = "Topicality"
    source_naturalness = "Naturalness"
    source_remarks = "Remarks"
    source_columns = [
        Identifier(source_id, "SMALLINT(3) UNSIGNED NOT NULL"),
        Column(source_topic, "VARCHAR(28) NOT NULL"),
        Column(source_difficulty, "INT(1) UNSIGNED"),
        Column(source_topicality, "INT(1) UNSIGNED"),
        Column(source_naturalness, "INT(1) UNSIGNED"),
        Column(source_remarks, "VARCHAR(50)")]

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    corpus_sentence = "UtteranceId"
    corpus_speaker_id = "SpeakerId"
    corpus_source_id = "ConversationId"
    corpus_starttime = "Start"
    corpus_endtime = "End"
    corpus_columns = [
        Identifier(corpus_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
        Link(corpus_file_id, file_table),
        Link(corpus_word_id, word_table),
        Link(corpus_speaker_id, speaker_table),
        Link(corpus_source_id, source_table),
        Column(corpus_sentence, "TINYINT(3) UNSIGNED NOT NULL"),
        Column(corpus_starttime, "FLOAT(17,6) UNSIGNED NOT NULL"),
        Column(corpus_endtime, "FLOAT(17,6) NOT NULL")]

    auto_create = ["word", "file", "speaker", "source", "corpus"]

    special_files = ["call_con_tab.csv", "caller_tab.csv", "topic_tab.csv",
                     "rating_tab.csv"]
    expected_files = special_files + ["switchboard_word_alignments.tar.gz"]

    _regexp = re.compile(r"sw(\d\d\d\d)([A|B])-ms98-a-word\.text")

    def __init__(self, gui=False, *args):
        # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        self.add_audio_feature(self.file_audio_path)
        self.add_time_feature(self.corpus_starttime)
        self.add_time_feature(self.corpus_endtime)
        self.add_time_feature(self.speaker_birth)
        self.add_exposed_id("source")
        self.add_exposed_id("speaker")

        self._resource_code = resource_code

        self._file_id = 1
        self._token_id = 0
        self.surface_feature = "word_uttered"
        self.add_building_stage(self._build_store_meta_data)

    @staticmethod
    def get_name():
        return "Switchboard-1"

    @staticmethod
    def get_db_name():
        return "coq_switchboard"

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
        return [("The Switchboard-1 Telephone Speech Corpus was originally "
                 "collected by Texas Instruments in 1990-1, under DARPA "
                 "sponsorship. The first release of the corpus was published "
                 "by NIST and distributed by the LDC in 1992-3. Since that "
                 "release, a number of corrections have been made to the "
                 "data files as presented on the original CD-ROM set and all "
                 "copies of the first pressing have been distributed."),
                ("Switchboard is a collection of about 2,400 two-sided "
                 "telephone conversations among 543 speakers (302 male, 241 "
                 "female) from all areas of the United States. A computer-"
                 "driven robot operator system handled the calls, giving the "
                 "caller appropriate recorded prompts, selecting and dialing "
                 "another person (the callee) to take part in a "
                 "conversation, introducing a topic for discussion and "
                 "recording the speech from the two subjects into separate "
                 "channels until the conversation was finished. About 70 "
                 "topics were provided, of which about 50 were used "
                 "frequently. Selection of topics and callees was "
                 "constrained so that: (1) no two speakers would converse "
                 "together more than once and (2) no one spoke more than "
                 "once on a given topic.")]

    @staticmethod
    def get_references():
        return [Book(
            authors=PersonList(Person(first="John", last="Godfrey"),
                               Person(first="Edward", last="Holliman")),
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
        lst = super(BuilderClass, cls).get_file_list(*args, **kwargs)
        new_pos = 0
        for i, x in enumerate(cls.special_files):
            if x in lst:
                lst.remove(x)
                lst.insert(new_pos, x)
                new_pos += 1

        cls._binary_files = {}
        for path, folders, files in os.walk(options.cfg.binary_path):
            for f in files:
                cls._binary_files[f] = path

        return lst

    @classmethod
    def process_call_con(cls, file_name):
        df = pd.read_csv(file_name,
                         sep=", ",
                         names=[cls.source_id,
                                "Side", "SpeakerId",
                                "V1",
                                "Length", "ivi_no",
                                "V2", "V3"],
                         engine="python")

        # remove unneeded characters:
        df["Side"] = df["Side"].str.strip('"\' ').apply(utf8)

        # replace unknown ivi_no by NA:
        df["ivi_no"] = df["ivi_no"].replace("UNK", np.nan).astype(float)
        return df.drop(["V1", "V2", "V3"], axis=1)

    @classmethod
    def process_topic(cls, file_name):
        # there is a problem with the ', ' delimiter; possibly due to the
        # fact that some entries mix commas and apostrophes
        # (see https://github.com/pandas-dev/pandas/pull/14582)

        # as a workaround, the context is read into a text string, then the
        # spaces around the commas are removed, and then the whole string
        # is buffered to pd.read_csv().
        with open(file_name, "r") as input_file:
            text = [x.replace("\", ", "\",").replace(", \"", ",\"")
                    for x in input_file.readlines()]

        df = pd.read_csv(IO_Stream(bytearray("\n".join(text),
                                             encoding="utf-8")),
                         sep=str(","),
                         names=[cls.source_topic,
                                "ivi_no",
                                "V1", "V2", "V3", "V4"],
                         engine="python")

        # remove unneeded characters from "Topic" column:
        df[cls.source_topic] = (df[cls.source_topic].str
                                                    .strip('"\' ')
                                                    .apply(utf8))
        return df[[cls.source_topic, "ivi_no"]]

    @classmethod
    def process_rating(cls, file_name):
        df = pd.read_csv(file_name,
                         sep=", ",
                         names=[cls.source_id,
                                cls.source_difficulty,
                                cls.source_topicality,
                                cls.source_naturalness,
                                "V1", "V2", "V3", "V4", "V5", "V6",
                                cls.source_remarks],
                         engine="python")

        # remove unneeded characters from "Remarks" column:
        df[cls.source_remarks] = (df[cls.source_remarks].str
                                                        .strip('"\' ')
                                                        .apply(utf8))
        return df.drop(["V1", "V2", "V3", "V4", "V5", "V6"], axis=1)

    @classmethod
    def process_caller(cls, file_name):
        df = pd.read_csv(file_name,
                         sep=", ",
                         names=[cls.speaker_id,
                                "V1", "V2",
                                cls.speaker_sex,
                                cls.speaker_birth,
                                cls.speaker_dialectarea,
                                cls.speaker_education,
                                "V3", "V4", "V5", "V6",
                                "V7", "V8", "V9", "V10"],
                         engine="python")

        # remove unneeded characters:
        for col in [cls.speaker_sex, cls.speaker_dialectarea]:
            df[col] = df[col].str.strip('"\' ').apply(utf8)

        return df.drop(["V1", "V2", "V3", "V4", "V5",
                        "V6", "V7", "V8", "V9", "V10"], axis=1)

    def process_file(self, file_name):
        basename = os.path.basename(file_name)
        if basename == "call_con_tab.csv":
            self._df_call = self.process_call_con(file_name)
        elif basename == "topic_tab.csv":
            self._df_topic = self.process_topic(file_name)
        elif basename == "rating_tab.csv":
            self._df_rating = self.process_rating(file_name)
        elif basename == "caller_tab.csv":
            self._df_caller = self.process_caller(file_name)

        elif basename == "switchboard_word_alignments.tar.gz":
            prog_value = self._widget.ui.progress_bar.value()
            prog_max = self._widget.ui.progress_bar.maximum()
            prog_text = self._widget.ui.progress_bar.text()
            with tarfile.open(file_name, "r:gz") as tar_file:
                members = tar_file.getmembers()
                self._widget.progressSet.emit(len(members), "")
                self._widget.progressUpdate.emit(0)
                for i, member in enumerate(members):
                    match = self._regexp.match(os.path.basename(member.name))
                    if match:
                        s = f"Processing {os.path.basename(member.name)}..."
                        self._widget.labelSet.emit(f"{s} (%v of %m)")
                        self._widget.progressUpdate.emit(i)
                        logging.info(s)

                        content = list(tar_file.extractfile(member))
                        if self._interrupted:
                            return
                        # process content of extracted file:
                        if content:
                            tokens, duration = self.process_content(
                                content,
                                conv_id=int(match.group(1)),
                                side=match.group(2))

                            # store retrieved tokens to corpus:
                            for token in tokens:
                                if self._interrupted:
                                    return
                                self.add_token_to_corpus(token)

                        # store currently extracted file:
                        self._file_id += 1
                        d = {self.file_name: os.path.join(basename,
                                                          member.name),
                             self.file_id: self._file_id,
                             self.file_duration: duration,
                             self.file_path: os.path.split(file_name)[0],
                             self.file_audio_path:
                                 self.find_audio_path(member.name)}
                        self.table(self.file_table).add(d)
                        self.commit_data()
            self._widget.progressSet.emit(prog_max, prog_text)
            self._widget.progressUpdate.emit(prog_value)

    @classmethod
    def find_audio_path(cls, file_name):
        conv_id = file_name[2:6]
        audio_name = f"sw0{conv_id}.sph"
        try:
            return os.path.join(cls._binary_files[audio_name], audio_name)
        except KeyError:
            return ""

    @classmethod
    def merge_meta_data(cls, df_source, df_topic, df_rating):
        df = df_source.merge(df_topic, on="ivi_no")
        df = df.merge(df_rating, on=cls.source_id)
        df = df.drop(["SpeakerId", "Side", "ivi_no", "Length"],
                     axis=1)
        df = df.drop_duplicates()
        return df

    def _build_store_meta_data(self):
        self.DB.load_dataframe(self._df_caller,
                               table_name=self.speaker_table,
                               index_label=None,
                               if_exists="replace")

        df = self.merge_meta_data(self._df_call,
                                  self._df_topic,
                                  self._df_rating)

        self.DB.load_dataframe(df,
                               table_name=self.source_table,
                               index_label=None,
                               if_exists="replace")

    def process_content(self, content, conv_id, side):
        row = self._df_call[(self._df_call[self.source_id] == conv_id) &
                            (self._df_call["Side"] == side)].iloc[0]
        speaker_id = row.SpeakerId
        source_id = row[self.source_id]

        tokens = []
        duration = 0

        lexicon = self.table(self.word_table)

        for n_row, row in enumerate(content):
            if self._interrupted:
                return
            if not row:
                continue
            try:
                source, start, end, label = [x.strip()
                                             for x in utf8(row).split()]
            except ValueError:
                s = f"Row number {n_row} doesn't contain valid data: '{row}'"
                logging.warning(s)
                continue

            uttered = label
            match = re.match(r"(.*)\[(.*)\](.*)", label)
            if match:
                matched = match.group(2)
                if matched.startswith("laughter-"):
                    label = matched.partition("laughter-")[-1]
                elif match.group(1) != "" or match.group(3) != "":
                    # incomplete utterance, e.g. 'reall[y]-' or 'sim[ilar]-'
                    label = "{}{}{}".format(*match.groups()).strip("-")
            self._word_id = lexicon.get_or_insert(
                                {self.word_label: label.lower(),
                                 self.word_uttered: uttered})

            tokens.append({self.corpus_word_id: int(self._word_id),
                           self.corpus_starttime: float(start),
                           self.corpus_endtime: float(end),
                           self.corpus_file_id: int(self._file_id),
                           self.corpus_source_id: int(source_id),
                           self.corpus_sentence: int(source[-4:]),
                           self.corpus_speaker_id: int(speaker_id)})
            duration = max(duration, float(end))
        return (tokens, duration)

    def store_filename(self, file_name):
        # because of the zip file structure, the installer handles
        # storing the filenames elsewhere, namely in process_file().
        pass

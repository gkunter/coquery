# -*- coding: utf-8 -*-

"""
coq_install_coraal.py is part of Coquery.

Copyright (c) 2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import os
import re
from io import StringIO
import tarfile
import tempfile
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import tgt

from coquery.corpusbuilder import (
    BaseCorpusBuilder,
    QUERY_ITEM_WORD, QUERY_ITEM_TRANSCRIPT)
from coquery.tables import Column, Identifier, Link


class corpus_code():
    def sql_string_get_time_info(self, token_id):
        return (f"SELECT {self.resource.corpus_time} "
                f"FROM {self.resource.corpus_table} "
                f"WHERE {self.resource.courpus_id} = {token_id}")

    def get_time_info_header(self):
        return ["Time"]


class BuilderClass(BaseCorpusBuilder):
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    file_duration = "Duration"
    file_columns = [
        Identifier(file_id, "SMALLINT(5) UNSIGNED NOT NULL"),
        Column(file_name, "VARCHAR(255) NOT NULL"),
        Column(file_duration, "REAL NOT NULL"),
        Column(file_path, "VARCHAR(2048) NOT NULL")]

    speaker_table = "Speakers"
    speaker_id = "SpeakerId"
    speaker_region = "Region"
    speaker_label = "Speaker"
    speaker_gender = "Gender"
    speaker_age = "Age"
    speaker_sec = "SEC"
    speaker_part = "Part"

    speaker_columns = [
        Identifier(speaker_id, "MEDIUMINT(4) UNSIGNED NOT NULL"),
        Column(speaker_label, "VARCHAR(16) NOT NULL"),
        Column(speaker_region, "VARCHAR(3) NOT NULL"),
        Column(speaker_gender, "ENUM('m','f','?') NOT NULL"),
        Column(speaker_age, "TINYINT(1) NOT NULL"),
        Column(speaker_sec, "TINYINT(1) NOT NULL"),
        Column(speaker_part, "TINYINT(1) NOT NULL")
    ]

    segment_table = "Segments"
    segment_id = "SegmentId"
    segment_origin_id = "FileId"
    segment_label = "Segment"
    segment_starttime = "SegStart"
    segment_endtime = "SegEnd"
    segment_duration = "SegDuration"

    segment_columns = [
        Identifier(segment_id, "MEDIUMINT(12) UNSIGNED NOT NULL"),
        Column(segment_origin_id, "TINYINT(3) UNSIGNED NOT NULL"),
        Column(segment_starttime, "REAL NOT NULL"),
        Column(segment_endtime, "REAL NOT NULL"),
        Column(segment_duration, "REAL NOT NULL"),
        Column(segment_label, "VARCHAR(4) NOT NULL")
    ]

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word = "Word"
    corpus_transcript = "Transcript"
    corpus_starttime = "Start"
    corpus_endtime = "End"
    corpus_duration = "Duration"
    corpus_file_id = "FileId"
    corpus_speaker_id = "SpeakerId"

    corpus_columns = [
        Identifier(corpus_id, "INT(7) UNSIGNED NOT NULL"),
        Column(corpus_word, "VARCHAR(20) NOT NULL"),
        Column(corpus_transcript, "VARCHAR(50) NOT NULL"),
        Column(corpus_starttime, "REAL(17,6) NOT NULL"),
        Column(corpus_endtime, "REAL(17,6) NOT NULL"),
        Column(corpus_duration, "REAL(17,6) NOT NULL"),
        Link(corpus_file_id, file_table),
        Link(corpus_speaker_id, speaker_table)
    ]

    auto_create = ["word", "file", "speaker", "segment", "corpus"]

    expected_files = []

    def __init__(self, gui=False, *args):
        super().__init__(gui=gui, *args)
        self._segment_id = 0
        self._speaker_id = 0
        self._file_id = 0
        self._token_id = 0

        # Specify that the corpus-specific code is contained in the dummy
        # class 'corpus_code' defined above:
        self._corpus_code = corpus_code

        self.add_time_feature(self.corpus_starttime)
        self.add_time_feature(self.corpus_endtime)
        self.add_time_feature(self.corpus_duration)
        for x in ["corpus_word", "corpus_transcript",
                  "corpus_id", "corpus_starttime", "corpus_endtime",
                  "corpus_duration"]:
            self.add_lexical_feature(x)

        self.add_annotation("segment", "corpus")

        self.map_query_item(QUERY_ITEM_TRANSCRIPT, "corpus_lemmatranscript")
        self.map_query_item(QUERY_ITEM_WORD, "corpus_word")

    @staticmethod
    def get_name():
        return "CORAAL"

    @staticmethod
    def get_db_name():
        return "coq_coraal"

    @staticmethod
    def get_title():
        return "Corpus of Regional African American Language"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en-US"

    @staticmethod
    def get_description():
        return [("The Corpus of Regional African American Language (CORAAL) "
                 "is the first public corpus of African American Language "
                 "(AAL) data. CORAAL features recorded speech from regional "
                 "varieties of AAL and includes the audio recordings along "
                 "with time-aligned orthographic transcription.")]

    @staticmethod
    def get_references():
        return [("Kendall, Tyler and Charlie Farrington. 2021. "
                 "<i>The Corpus of Regional African American Language.</i>"
                 "Version 2021.07. Eugene, OR: The Online Resources for "
                 "African American Language Project. "
                 "<a href='http://lingtools.uoregon.edu/coraal'>"
                 "http://lingtools.uoregon.edu/coraal</a>")]

    @staticmethod
    def get_url():
        s = "http://lingtools.uoregon.edu/coraal/index.php"
        return s

    @staticmethod
    def get_license():
        return ("CORAAL is licensed under a Creative Commons "
                "Attribution-NonCommercial-ShareAlike (4.0) International "
                "license (<a "
                "href='https://creativecommons.org/licenses/by-nc-sa/4.0/'>CC "
                "BY-NC-SA 4.0</a>).")

    @classmethod
    def get_file_list(cls, path, *args, **kwargs):
        grids = []
        regex_grids = re.compile(r"[A-Z]*_MFA_\d\d\d\d.\d\d.zip")
        for source_path, folders, files in os.walk(path):
            for file_name in files:
                full_name = os.path.join(source_path, file_name)
                if regex_grids.match(file_name):
                    grids.append(full_name)
        return grids

        # meta = []
        # grids = []
        # regex_meta = re.compile(
        #     r"[A-Z]*_metadata_\d{4}\.[\d.]{2,}.txt")
        # regex_grids = re.compile(
        #     r"[A-Z]*_audio_part\d+_\d{4}\.[\d.]{2,}.tar.gz")
        # for source_path, folders, files in os.walk(path):
        #     for file_name in files:
        #         full_name = os.path.join(source_path, file_name)
        #         if regex_grids.match(file_name):
        #             grids.append(full_name)
        #         elif regex_meta.match(file_name):
        #             meta.append(full_name)
        # return meta + grids

    def process_file(self, file_name):
        if re.search(r"_metadata_", file_name):
            self._load_metadata(file_name)
        else:
            self._load_textgrids(file_name)

    def process_textgrid(self, tg: tgt.TextGrid):
        _token_phones = []
        current_word = None

        word_tier = tg.tiers[0]
        for intr in tg.tiers[1]:
            if self._interrupted:
                return

            lookup = word_tier.get_annotation_by_start_time(intr.start_time)

            if lookup:
                if current_word:
                    token = {self.corpus_starttime: current_word.start_time,
                             self.corpus_endtime: current_word.end_time,
                             self.corpus_duration: current_word.duration(),
                             self.corpus_transcript: " ".join(_token_phones),
                             self.corpus_word: current_word.text,
                             self.corpus_speaker_id: self._speaker_id,
                             self.corpus_file_id: self._file_id}

                    self.add_token_to_corpus(token)
                    _token_phones = []
                current_word = lookup

            if intr.text == intr.text.upper():
                _token_phones.append(intr.text)

            segment = {self.segment_starttime: intr.start_time,
                       self.segment_origin_id: self._file_id,
                       self.segment_endtime: intr.end_time,
                       self.segment_duration: intr.duration(),
                       self.segment_label: intr.text}
            self._segment_id = self.table(self.segment_table).add(segment)

    def store_filename(self, file_name):
        # because of the zip file structure, the installer handles
        # storing the filenames elsewhere, namely in process_file().
        pass


    def _load_metadata(self, file_name):
        df = pd.read_csv(file_name, sep="\t")

    def _parse_filename(self, file_name: str) -> dict:
        """
        Parse the file name into the speaker meta data.

        The expected format of the file name is

        RRR_seS_agA_G_XX_N.TextGrid, where

        RRR is the three-character region code,
        S is the socio-economic group (0-3),
        A is the age group (0-4),
        G is the gender of the speaker (m, f, n),
        XX is the speaker id (numeric),
        N is the recording number.

        Parameters
        ----------
        file_name: str
            name of the text grid in the format

        Returns
        -------
        dct: dict
            dictionary with keys corresponding to speaker table names

        """
        match = re.search(r"(\w\w\w)_se(\d)_ag(\d)_(\w)_(\d\d)_(\d).TextGrid",
                         file_name)
        if not match:
            logging.warning(
                f"File name {file_name} doesn't match the expected pattern.")
            return {}
        else:
            label = os.path.splitext(os.path.basename(file_name))[0]
            label = f"{match.group(1)}_{match.group(2)}_{match}"
            return {self.speaker_region: match.group(1),
                    self.speaker_sec: match.group(2),
                    self.speaker_age: match.group(3),
                    self.speaker_gender: match.group(4),
                    self.speaker_label: label,
                    self.speaker_part: match.group(6)}

    def _load_textgrids(self, file_name):
        with ZipFile(file_name) as zf:
            if self._interrupted:
                return
            for entry in zf.infolist():
                if self._interrupted:
                    return
                fn = entry.filename
                if not fn.startswith("__MACOSX"):
                    content = zf.read(fn)
                    with tempfile.NamedTemporaryFile() as temp:
                        temp.write(content)
                        temp.seek(0)
                        try:
                            tg = tgt.read_textgrid(temp.name)
                            _file_duration = tg.end_time
                        except (IndexError):
                            pass
                        else:
                            dct = self._parse_filename(fn)
                            self._speaker_id = (
                                self.table(self.speaker_table).add(dct))

                            dct = {
                                self.file_name: fn,
                                self.file_duration: _file_duration,
                                self.file_path: os.path.split(file_name)[0]}
                            self._file_id = (
                                self.table(self.file_table).add(dct))

                            self.process_textgrid(tg)
                            self.commit_data()


        # with tarfile.open(file_name, "r:gz") as tar:
        #     for entry in tar.getmembers():
        #         path = Path(entry.name)
        #         print("\t", path.name)
        #         if re.match(r"[A-Z]+_se\d_ag\d_._\d\d_\d.TextGrid", path.name):
        #             f = tar.extractfile(entry)
        #             if f:
        #                 content = f.read()
        #                 print(content[:79])
        #                 with tempfile.NamedTemporaryFile() as temp:
        #                     print(f"\t\t{temp.name}")
        #                     temp.write(content)
        #                     temp.seek(0)
        #                     tg = tgt.read_textgrid(temp.name)
        #                     print(tg)

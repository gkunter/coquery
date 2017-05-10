# -*- coding: utf-8 -*-

"""
coq_install_buckeye.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import codecs
import zipfile
import pandas as pd

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO, BytesIO

from coquery.corpusbuilder import *
from coquery.unicode import utf8

# The class corpus_code contains the Python source code that will be
# embedded into the corpus library. It provides the Python code that will
# override the default class methods of CorpusClass by methods that are
# tailored for the Buckeye corpus.
#
class corpus_code():
    def sql_string_get_time_info(self, token_id):
        return "SELECT {} FROM {} WHERE {} = {}".format(
                self.resource.corpus_time,
                self.resource.corpus_table,
                self.resource.corpus_id,
                token_id)

    def get_time_info_header(self):
        return ["Time"]

class BuilderClass(BaseCorpusBuilder):
    file_filter = "s??.zip"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word = "Word"
    corpus_pos = "POS"
    corpus_transcript = "Transcript"
    corpus_lemmatranscript = "Canonical_Transcript"
    corpus_starttime = "Start"
    corpus_endtime = "End"
    corpus_file_id = "FileId"
    corpus_speaker_id = "SpeakerId"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    file_duration = "Duration"
    file_audio_path = "AudioPath"

    segment_table = "Segments"
    segment_id = "SegmentId"
    segment_origin_id = "FileId"
    segment_label = "Segment"
    segment_starttime = "SegStart"
    segment_endtime = "SegEnd"

    speaker_table = "Speakers"
    speaker_id = "SpeakerId"
    speaker_label = "Speaker"
    speaker_age = "Age"
    speaker_gender = "Gender"
    speaker_interviewer = "Interviewer_gender"

    expected_files = ["s{:02}.zip".format(x + 1) for x in range(40)]

    _zip_files = [
        's2901b.zip', 's1304a.zip', 's2503b.zip',
        's1101a.zip', 's1803b.zip', 's2702b.zip',
        's0402b.zip', 's2402a.zip', 's1104a.zip',
        's0201a.zip', 's3302b.zip', 's2902b.zip',
        's0501a.zip', 's1602b.zip', 's3802a.zip',
        's0504a.zip', 's1303a.zip', 's3102b.zip',
        's3801b.zip', 's0102b.zip', 's0802b.zip',
        's0204b.zip', 's2901a.zip', 's1801b.zip',
        's2802b.zip', 's1102a.zip', 's1603a.zip',
        's0302a.zip', 's3701a.zip', 's0404a.zip',
        's3401b.zip', 's3602b.zip', 's2101a.zip',
        's3403a.zip', 's0305b.zip', 's2503a.zip',
        's2203b.zip', 's0704a.zip', 's2502b.zip',
        's0204a.zip', 's1903a.zip', 's3601b.zip',
        's0203a.zip', 's1503a.zip', 's1002b.zip',
        's0101b.zip', 's3001a.zip', 's0502a.zip',
        's3602a.zip', 's2003a.zip', 's0803a.zip',
        's3202a.zip', 's2703b.zip', 's0205b.zip',
        's1403a.zip', 's1001a.zip', 's1901b.zip',
        's2001a.zip', 's1103a.zip', 's3304a.zip',
        's3701b.zip', 's2102a.zip', 's1301a.zip',
        's3401a.zip', 's2301b.zip', 's2002a.zip',
        's0306a.zip', 's0202b.zip', 's3603b.zip',
        's1702a.zip', 's2102b.zip', 's2001b.zip',
        's0901a.zip', 's2902a.zip', 's1203a.zip',
        's2403a.zip', 's0601a.zip', 's1403b.zip',
        's1101b.zip', 's2201a.zip', 's2903b.zip',
        's1904a.zip', 's3402a.zip', 's1804a.zip',
        's4002a.zip', 's2401a.zip', 's0901b.zip',
        's3503b.zip', 's0703a.zip', 's3101b.zip',
        's0601b.zip', 's0701b.zip', 's2701a.zip',
        's3302a.zip', 's0301b.zip', 's1102b.zip',
        's1803a.zip', 's2701b.zip', 's3703a.zip',
        's3901a.zip', 's1702b.zip', 's2704a.zip',
        's2202a.zip', 's1003a.zip', 's0205a.zip',
        's2703a.zip', 's3702a.zip', 's0403a.zip',
        's1201b.zip', 's3502a.zip', 's2501b.zip',
        's4003a.zip', 's2501a.zip', 's0201b.zip',
        's1203b.zip', 's3703b.zip', 's0102a.zip',
        's1602a.zip', 's3901b.zip', 's0703b.zip',
        's1303b.zip', 's4001b.zip', 's0202a.zip',
        's2302a.zip', 's1502a.zip', 's2502a.zip',
        's1802a.zip', 's0503b.zip', 's3403b.zip',
        's1801a.zip', 's0503a.zip', 's3301b.zip',
        's1202b.zip', 's0303b.zip', 's2401b.zip',
        's2302b.zip', 's3803a.zip', 's2202b.zip',
        's3003a.zip', 's0702b.zip', 's2601a.zip',
        's0902a.zip', 's0903b.zip', 's2101b.zip',
        's0403b.zip', 's2002b.zip', 's2803a.zip',
        's1902b.zip', 's0801b.zip', 's3902b.zip',
        's2402b.zip', 's3002a.zip', 's2802a.zip',
        's2201b.zip', 's1903b.zip', 's2303b.zip',
        's1201a.zip', 's2903a.zip', 's2004a.zip',
        's1601a.zip', 's3402b.zip', 's0803b.zip',
        's3201b.zip', 's0305a.zip', 's1802b.zip',
        's1402b.zip', 's1501a.zip', 's3002b.zip',
        's3501b.zip', 's3101a.zip', 's1904b.zip',
        's1001b.zip', 's0804a.zip', 's0502b.zip',
        's0602a.zip', 's1401b.zip', 's3501a.zip',
        's2203a.zip', 's2601b.zip', 's0702a.zip',
        's4001a.zip', 's1301b.zip', 's0603a.zip',
        's1703b.zip', 's1701b.zip', 's3001b.zip',
        's2403b.zip', 's0206a.zip', 's3303a.zip',
        's0902b.zip', 's3802b.zip', 's1003b.zip',
        's3201a.zip', 's2303a.zip', 's0203b.zip',
        's3702b.zip', 's1703a.zip', 's3801a.zip',
        's3902a.zip', 's3103a.zip', 's2003b.zip',
        's2603b.zip', 's1603b.zip', 's1601b.zip',
        's3903b.zip', 's1202a.zip', 's4004a.zip',
        's2603a.zip', 's0101a.zip', 's1701a.zip',
        's0402a.zip', 's3102a.zip', 's0802a.zip',
        's0903a.zip', 's1302a.zip', 's1002a.zip',
        's4002b.zip', 's0304b.zip', 's0103a.zip',
        's3303b.zip', 's3903a.zip', 's3504a.zip',
        's1502b.zip', 's1004a.zip', 's0304a.zip',
        's3301a.zip', 's1501b.zip', 's1901a.zip',
        's0301a.zip', 's2801a.zip', 's2702a.zip',
        's3502b.zip', 's1104b.zip', 's3503a.zip',
        's0602b.zip', 's1302b.zip', 's0501b.zip',
        's4003b.zip', 's0303a.zip', 's3601a.zip',
        's2602a.zip', 's3202b.zip', 's0401a.zip',
        's2602b.zip', 's1902a.zip', 's2801b.zip',
        's2301a.zip', 's3603a.zip', 's0302b.zip',
        's1401a.zip', 's1604a.zip', 's1103b.zip',
        's1204a.zip', 's0801a.zip', 's1402a.zip',
        's0701a.zip', 's0401b.zip']

    # the table of speaker characteristics is from p. 4 of the Buckeye
    # Corpus Manual, http://buckeyecorpus.osu.edu/php/publications.php:
    _speaker_characteristics = pd.DataFrame({
        speaker_gender:
            {1: 'f', 2: 'f', 3: 'm', 4: 'f', 5: 'f',
             6: 'm', 7: 'f', 8: 'f', 9: 'f', 10: 'm',
             11: 'm', 12: 'f', 13: 'm', 14: 'f', 15: 'm',
             16: 'f', 17: 'f', 18: 'f', 19: 'm', 20: 'f',
             21: 'f', 22: 'm', 23: 'm', 24: 'm', 25: 'f',
             26: 'f', 27: 'f', 28: 'm', 29: 'm', 30: 'm',
             31: 'f', 32: 'm', 33: 'm', 34: 'm', 35: 'm',
             36: 'm', 37: 'f', 38: 'm', 39: 'f', 40: 'm'},
        speaker_label:
            {1: 'S01', 2: 'S02', 3: 'S03', 4: 'S04', 5: 'S05',
             6: 'S06', 7: 'S07', 8: 'S08', 9: 'S09', 10: 'S10',
             11: 'S11', 12: 'S12', 13: 'S13', 14: 'S14', 15: 'S15',
             16: 'S16', 17: 'S17', 18: 'S18', 19: 'S19', 20: 'S20',
             21: 'S21', 22: 'S22', 23: 'S23', 24: 'S24', 25: 'S25',
             26: 'S26', 27: 'S27', 28: 'S28', 29: 'S29', 30: 'S30',
             31: 'S31', 32: 'S32', 33: 'S33', 34: 'S34', 35: 'S35',
             36: 'S36', 37: 'S37', 38: 'S38', 39: 'S39', 40: 'S40'},
        speaker_age:
            {1: 'y', 2: 'o', 3: 'o', 4: 'y', 5: 'o',
             6: 'y', 7: 'o', 8: 'y', 9: 'y', 10: 'o',
             11: 'y', 12: 'y', 13: 'y', 14: 'o', 15: 'y',
             16: 'o', 17: 'o', 18: 'o', 19: 'o', 20: 'o',
             21: 'y', 22: 'o', 23: 'o', 24: 'o', 25: 'o',
             26: 'y', 27: 'o', 28: 'y', 29: 'o', 30: 'y',
             31: 'y', 32: 'y', 33: 'y', 34: 'y', 35: 'o',
             36: 'o', 37: 'y', 38: 'o', 39: 'y', 40: 'y'},
        speaker_interviewer:
            {1: 'f', 2: 'm', 3: 'm', 4: 'f', 5: 'f',
             6: 'f', 7: 'f', 8: 'f', 9: 'f', 10: 'f',
             11: 'm', 12: 'm', 13: 'f', 14: 'f', 15: 'm',
             16: 'm', 17: 'm', 18: 'f', 19: 'f', 20: 'f',
             21: 'm', 22: 'f', 23: 'm', 24: 'm', 25: 'm',
             26: 'f', 27: 'm', 28: 'm', 29: 'f', 30: 'm',
             31: 'm', 32: 'f', 33: 'f', 34: 'm', 35: 'm',
             36: 'f', 37: 'm', 38: 'm', 39: 'm', 40: 'f'}})

    # The following list of POS tags is taken from p. 1 and 2 of the Buckeye
    # Corpus Manual, http://buckeyecorpus.osu.edu/php/publications.php. It
    # is used when trying to salvage incomplete rows.

    _VALID_POS = ["CC", "CD", "DT", "EX", "FW", "IN", "JJ", "JJR",
                 "JJS", "LS", "MD", "NN", "NNS", "NNP", "NNPS", "PDT",
                 "POS", "PRP", "PP$", "RB", "RBR", "RBS", "RP", "SYM",
                 "TO", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ",
                 "WDT", "WP", "WP$", "WRB", "DT_VBZ", "EX_VBZ", "NULL",
                 "PRP_MD", "PRP_VBP", "PRP_VBZ", "VBG_TO", "VBP_RB",
                 "VBP_TO", "VBZ_RB", "WP_VBZ", "WP_RB"]

    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui, *args)

        # add table descriptions for the tables used in this database.
        #
        # A table description is a dictionary with at least a 'CREATE' key
        # which takes a list of strings as its value. Each of these strings
        # represents a MySQL instruction that is used to create the table.
        # Typically, this instruction is a column specification, but you can
        # also add other table options such as the primary key for this
        # table.
        #
        # Additionaly, the table description can have an 'INDEX' key which
        # takes a list of tuples as its value. Each tuple has three
        # elements. The first element is a list of strings containing the
        # column names that are to be indexed. The second element is an
        # integer value specifying the index length for columns of Text
        # types. The third element specifies the index type (e.g. 'HASH' or
        # 'BTREE'). Note that not all MySQL storage engines support all
        # index types.

        self.create_table_description(self.segment_table,
            [Identifier(self.segment_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.segment_origin_id, "TINYINT(3) UNSIGNED NOT NULL"),
             Column(self.segment_starttime, "REAL NOT NULL"),
             Column(self.segment_endtime, "REAL NOT NULL"),
             Column(self.segment_label, "VARCHAR(14) NOT NULL")])

        # Add the main lexicon table. Each row in this table represents a
        # word-form that occurs in the corpus. It has the following columns:
        #
        # WordId
        # An int value containing the unique identifier of this word-form.
        #
        # Text
        # A text value containing the orthographic representation of this
        # word-form.
        #
        # LemmaId
        # An int value containing the unique identifier of the lemma that
        # is associated with this word-form.
        #
        # Pos
        # A text value containing the part-of-speech label of this
        # word-form.
        #
        # Transcript
        # A text value containing the phonological transcription of this
        # word-form.

        # Add the file table. Each row in this table represents a data file
        # that has been incorporated into the corpus. Each token from the
        # corpus table is linked to exactly one file from this table, and
        # more than one token may be linked to each file in this table.
        # The table contains the following columns:
        #
        # FileId
        # An int value containing the unique identifier of this file.
        #
        # Path
        # A text value containing the path that points to this data file.

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "TINYINT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "VARCHAR(18) NOT NULL"),
             Column(self.file_duration, "REAL NOT NULL"),
             Column(self.file_audio_path, "VARCHAR(2048) NOT NULL"),
             Column(self.file_path, "VARCHAR(2048) NOT NULL")])

        self.create_table_description(self.speaker_table,
            [Identifier(self.speaker_id, "TINYINT(2) UNSIGNED NOT NULL"),
             Column(self.speaker_label, "VARCHAR(3) NOT NULL"),
             Column(self.speaker_age, "ENUM('y','o') NOT NULL"),
             Column(self.speaker_gender, "ENUM('f','m') NOT NULL"),
             Column(self.speaker_interviewer, "ENUM('f','m') NOT NULL")])

        # Add the main corpus table. Each row in this table represents a
        # token in the corpus. It has the following columns:
        #
        # TokenId
        # An int value containing the unique identifier of the token
        #
        # WordId
        # An int value containing the unique identifier of the lexicon
        # entry associated with this token.
        #
        # FileId
        # An int value containing the unique identifier of the data file
        # that contains this token.

        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_speaker_id, self.speaker_table),
             Column(self.corpus_word, "VARCHAR(1028) NOT NULL"),
             Column(self.corpus_pos, "VARCHAR(13) NOT NULL"),
             Column(self.corpus_transcript, "VARCHAR(41) NOT NULL"),
             Column(self.corpus_lemmatranscript, "VARCHAR(41) NOT NULL"),
             Column(self.corpus_starttime, "REAL(17,6) NOT NULL"),
             Column(self.corpus_endtime, "REAL(17,6) NOT NULL")])

        # Specify that the corpus-specific code is contained in the dummy
        # class 'corpus_code' defined above:
        self._corpus_code = corpus_code

        self.add_audio_feature(self.file_audio_path)
        self.add_time_feature(self.corpus_starttime)
        self.add_time_feature(self.corpus_endtime)
        for x in ["corpus_word", "corpus_pos", "corpus_transcript", "corpus_lemmatranscript"]:
            self.add_lexical_feature(x)

        self.add_annotation("segment", "corpus")

        self._file_id = 0
        self._token_id = 0

        self.map_query_item(QUERY_ITEM_TRANSCRIPT, "corpus_lemmatranscript")
        self.map_query_item(QUERY_ITEM_POS, "corpus_pos")
        self.map_query_item(QUERY_ITEM_WORD, "corpus_word")
        self.map_query_item(QUERY_ITEM_LEMMA, "corpus_transcript")

    @staticmethod
    def get_name():
        return "Buckeye"

    @staticmethod
    def get_db_name():
        return "coq_buckeye"

    @staticmethod
    def get_title():
        return "Buckeye Speech Corpus"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en-US"

    @staticmethod
    def get_description():
        return [
            "The Buckeye Corpus of conversational speech contains high-quality recordings from 40 speakers in Columbus OH conversing freely with an interviewer. The speech has been orthographically transcribed and phonetically labeled."]

    @staticmethod
    def get_references():
        return ["Pitt, M.A., Dilley, L., Johnson, K., Kiesling, S., Raymond, W., Hume, E. and Fosler-Lussier, E. (2007) Buckeye Corpus of Conversational Speech (2nd release) [www.buckeyecorpus.osu.edu] Columbus, OH: Department of Psychology, Ohio State University (Distributor)"]

    @staticmethod
    def get_url():
        return "http://buckeyecorpus.osu.edu/"

    @staticmethod
    def get_license():
        return "<a href='http://buckeyecorpus.osu.edu/License.pdf'>Buckeye Corpus Content License</a>"

    @staticmethod
    def get_installation_note():
        return """
        <p><b>File format note</b></p>
        <p>After registration, the Buckeye website offers you to download
        one ZIP file for each of the 40 speakers named <code>s01.zip</code>,
        <code>s02.zip</code>, ..., <code>s39.zip</code>, <code>s40.zip</code>.
        Each of these 40 large ZIP files contains more smaller ZIP files with
        all files associated with one recording from that speaker.</p>
        <p>For the installation, please download the 40 speaker ZIP files and
        store them in a single directory. You do not need to unzip any of
        these files; this is done automatically by the corpus installer.</p>
        """

    def build_load_files(self):
        self.DB.load_dataframe(
            self._speaker_characteristics,
            self.speaker_table,
            self.speaker_id)
        super(BuilderClass, self).build_load_files()

    def process_file(self, filename):
        """
        Go through the zip file (e.g. s01.zip, s02.zip, ...), and
        process the smaller zipfiles stored in it (e.g. s0101a.zip,
        s0101b.zip, ...).
        """

        zip_file = zipfile.ZipFile(filename)
        for small_zip_name in zip_file.namelist():
            speaker_name = os.path.basename(small_zip_name)
            self._speaker_id = int(speaker_name[1:3])
            if speaker_name in self._zip_files:
                if self._interrupted:
                    return
                try:
                    # Python 2.7:
                    _io = StringIO(zip_file.read(small_zip_name))
                except TypeError:
                    # Python 3.x:
                    _io = BytesIO(zip_file.read(small_zip_name))
                small_zip_file = zipfile.ZipFile(_io)
                self._process_words_file(small_zip_file, speaker_name)

                audio_path = os.path.join(options.cfg.binary_path,
                                          self.get_name())
                audio_file = os.path.join(
                    audio_path,
                    "{}.wav".format(os.path.splitext(small_zip_name)[0]))

                if not os.path.exists(os.path.split(audio_file)[0]):
                    os.makedirs(os.path.split(audio_file)[0])

                if not os.path.exists(audio_file):
                    audio_data = self._get_audio(small_zip_file, speaker_name)
                    with open(audio_file, "wb") as output_file:
                        output_file.write(audio_data)

                self._value_file_audio_path = audio_file

                self._value_file_name = "{}/{}".format(
                    os.path.basename(filename), speaker_name)
                self._value_file_path = os.path.split(filename)[0]
                self._value_file_duration = self._duration
                d = {self.file_name: self._value_file_name,
                    self.file_duration: self._value_file_duration,
                    self.file_path: self._value_file_path,
                    self.file_audio_path: self._value_file_audio_path}
                self._file_id = self.table(self.file_table).get_or_insert(d)
                self.commit_data()

    def _get_audio(self, speaker_zip, filename):
        file_name, _ = os.path.splitext(filename)
        audio_file = "{}.wav".format(file_name)
        return speaker_zip.read(audio_file)

    def _get_segments(self, speaker_zip, filename):
        file_body = False

        file_name, _ = os.path.splitext(filename)
        phones_file = "{}.phones".format(file_name)
        input_data = speaker_zip.read(phones_file)
        input_data = [utf8(x.strip())
                      for x in input_data.splitlines() if x.strip()]
        segments = []

        for row in input_data:
            if self._interrupted:
                return
            while "  " in row:
                row = row.replace("  ", " ")
            # only process the lines after the hash mark:
            if row == "#":
                file_body = True
            elif file_body:
                try:
                    end_time, _, remain = row.partition(" ")
                    _, _, segment = remain.partition(" ")
                except ValueError:
                    logger.warn(".phones file {}: error in row partitioning ({})".format(filename, row))
                    continue
                end_time = float(end_time)

                # Some segments have the undocumented form 'n; *'. In that
                # case, strip the latter part:
                segment = segment.partition(";")[0].strip()

                if end_time >= 0:
                    segments.append((end_time, segment))
        return segments

    def _process_words_file(self, speaker_zip, filename):
        file_body = False

        file_name, _ = os.path.splitext(filename)
        words_file = "{}.words".format(file_name)
        input_data = speaker_zip.read(words_file)
        input_data = [utf8(x.strip()) for x in input_data.splitlines()
                      if x.strip()]
        self._duration = 0
        regex = re.compile("[{<].+[}>]")

        # The list ``segments'' contains all segments in this file. Each
        # entry in the list is a tuple with the end time and the segment
        # label as values.
        segments = self._get_segments(speaker_zip, filename)

        last_row = None
        # go through the input data and create the list ``tokens''. Each
        # entry in the list is a tuple with the token's ending time as the
        # first element, and as the second element a dictionary with the
        # label, POS, transcript, # and canonical transcript as values.
        tokens = []

        iter_data = iter(input_data)

        for row in iter_data:
            row = re.sub("\s+", " ", row)

            # only process the lines after the hash mark:
            if row == "#":
                file_body = True
            elif file_body:

                # There is an error in file s3504a.words: the POS field is
                # wrapped to a separate line. For this file, the installer
                # contains special treatment of the input data:
                if filename == "s3504a.zip":
                    next_row = next(iter_data)

                    # Not only is there the line-wrapping error, the file
                    # also has only one filed for non-linguistic tokens
                    # <...>, while all other files appear to have some
                    # kind of dummy lemma and word label. In order to be
                    # consistent, supply these labels if needed:
                    if next_row.endswith("null"):
                        next_row = "; U; U; null"
                    row = "{}{}".format(row, next_row)

                try:
                    self._value_corpus_time, _, remain = row.partition(" ")
                    _, _, value = remain.partition(" ")
                except ValueError:
                    logger.warn(".words file {}: error in row partitioning ({})".format(filename, row))
                    continue
                try:
                    self._value_corpus_time = float(self._value_corpus_time)
                except ValueError:
                    logger.warn(".words file {}: error in float conversion ({})".format(filename, row))
                    continue

                split_values = [x.strip() for x in value.split("; ")]

                # Rows should have four values: the orthographic word, the
                # canonical transcription, the transcribed word, and the POS
                # tag.
                try:
                    (self._value_corpus_word,
                    self._value_corpus_lemmatranscript,
                    self._value_corpus_transcript,
                    self._value_corpus_pos) = split_values
                except ValueError:
                    # if there are less than 4 values, still try to salvage
                    # the row

                    # the first value is always the word:
                    self._value_corpus_word = split_values[0]

                    # Initialize the other content fields with empty strings:
                    self._value_corpus_lemmatranscript = ""
                    self._value_corpus_transcript = ""
                    self._value_corpus_pos = ""

                    if len(split_values) == 3:
                        # check if last value is a valid POS tag, or "null",
                        # i.e. a non-speech label:
                        if split_values[-1] in [self._VALID_POS, "null"]:
                            self._value_corpus_transcript = split_values[1]
                            self._value_corpus_lemmatranscript = split_values[1]
                            self._value_corpus_pos = split_values[-1]
                        else:
                            self._value_corpus_transcript = split_values[1]
                            self._value_corpus_lemmatranscript = split_values[-1]
                            self._value_corpus_transcript = "null"

                    elif len(split_values) == 2:
                        # check if last value is a valid POS tag, or "null",
                        # i.e. a non-speech label:
                        if split_values[1] in [self._VALID_POS, "null"]:
                            self._value_corpus_pos = split_values[1]
                            if split_values[-1] == "null":
                                # apparently, 'U' is used as transcription of
                                # non-speech labels:
                                self._value_corpus_lemmatranscript = "U"
                                self._value_corpus_transcript = "U"
                        else:
                            self._value_corpus_transcript = split_values[1]

                if regex.match(self._value_corpus_word):
                    self._value_corpus_pos = "null"
                    self._value_corpus_transcript = ""
                    self._value_corpus_lemmatranscript = ""

                if self._value_corpus_time >= 0:
                    tokens.append(
                        (self._value_corpus_time,
                        {self.corpus_word: self._value_corpus_word,
                            self.corpus_pos: self._value_corpus_pos,
                            self.corpus_transcript: self._value_corpus_transcript,
                            self.corpus_lemmatranscript: self._value_corpus_lemmatranscript}))

        # Now, go through the tokens in order to add them to the corpus,
        # and to link them to their segments via the meta table.
        segment_index = 0
        last_t = 0
        for i, token in enumerate(tokens):
            # get next token in list, and insert it both into word_table and
            # content_table:
            end_time, d = token

            try:
                start_time = tokens[i-1][0]
                # start_time from previous file?
                if start_time > end_time:
                    raise IndexError
            except IndexError:
                start_time = 0.0

            d.update({self.corpus_starttime: start_time,
                      self.corpus_endtime: end_time,
                      self.corpus_speaker_id: self._speaker_id,
                      self.corpus_file_id: self._file_id + 1})

            self.add_token_to_corpus(d)

            # add segments
            try:
                while True:
                    t, segment = segments[segment_index]
                    if t <= end_time:
                        d2 = {self.segment_starttime: last_t,
                              self.segment_origin_id: self._file_id + 1,
                              self.segment_endtime: t,
                              self.segment_label: segment}
                        self._segment_id = self.table(self.segment_table).add(d2)

                        segment_index += 1
                        last_t = t
                    else:
                        break
            except IndexError:
                # all segments processed
                pass

            self._duration = max(self._duration, float(end_time))

    def store_filename(self, file_name):
        # because of the zip file structure, the installer handles
        # storing the filenames elsewhere, namely in process_file().
        pass

if __name__ == "__main__":
    BuilderClass().build()

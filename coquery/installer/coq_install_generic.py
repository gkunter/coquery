# -*- coding: utf-8 -*-

"""
coq_install_generic.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import string
import re
import pandas as pd
import os
import logging

from coquery import options
from coquery.corpusbuilder import BaseCorpusBuilder
from coquery.corpusbuilder import (Column, Identifier, Link)
from coquery.documents import (pdf_to_str, docx_to_str, odt_to_str,
                               html_to_str, plain_to_str,
                               detect_file_type,
                               FT_PDF, FT_DOCX, FT_ODT, FT_HTML, FT_PLAIN)
from coquery.capturer import Capturer

re_punct = re.compile("[.!?'\"]")


class BuilderClass(BaseCorpusBuilder):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    corpus_sentence = "Sentence_Id"

    word_table = "Lexicon"
    word_id = "WordId"
    word_lemma = "Lemma"
    word_label = "Word"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    meta_data = "metadata"

    def __init__(self, gui=False, pos=True):
        # all corpus builders have to call the inherited __init__ function:
        super(BuilderClass, self).__init__(gui)

        # Add the main lexicon table. Each row in this table represents a
        # word-form that occurs in the corpus. It has the following columns:
        #
        # WordId (Identifier)
        # An int value containing the unique identifier of this word-form.
        #
        # LemmaId
        # An int value containing the unique identifier of the lemma that
        # is associated with this word-form.
        #
        # Text
        # A text value containing the orthographic representation of this
        # word-form.
        #
        # Additionally, if NLTK is used to tag part-of-speech:
        #
        # Pos
        # A text value containing the part-of-speech label of this
        # word-form.

        self._file_id = None
        if pos:
            self.word_pos = "POS"
            self.create_table_description(
                self.word_table,
                [Identifier(self.word_id, "INT UNSIGNED NOT NULL"),
                 Column(self.word_lemma, "VARCHAR(1024) NOT NULL"),
                 Column(self.word_pos, "VARCHAR(128) NOT NULL"),
                 Column(self.word_label, "VARCHAR(1024) NOT NULL")])
        else:
            self.create_table_description(
                self.word_table,
                [Identifier(self.word_id, "INT UNSIGNED NOT NULL"),
                 Column(self.word_lemma, "VARCHAR(1024) NOT NULL"),
                 Column(self.word_label, "VARCHAR(1024) NOT NULL")])

        # Add the file table. Each row in this table represents a data file
        # that has been incorporated into the corpus. Each token from the
        # corpus table is linked to exactly one file from this table, and
        # more than one token may be linked to each file in this table.
        # The table contains the following columns:
        #
        # FileId (Identifier)
        # An int value containing the unique identifier of this file.
        #
        # File
        # A text value containing the base file name of this data file.
        #
        # Path
        # A text value containing the path that points to this data file.

        self.create_table_description(
            self.file_table,
            [Identifier(self.file_id, "INT UNSIGNED NOT NULL"),
             Column(self.file_name, "VARCHAR(1024) NOT NULL"),
             Column(self.file_path, "VARCHAR(4048) NOT NULL")])

        # Add the main corpus table. Each row in this table represents a
        # token in the corpus. It has the following columns:
        #
        # TokenId (Identifier)
        # An int value containing the unique identifier of the token
        #
        # WordId
        # An int value containing the unique identifier of the lexicon
        # entry associated with this token.
        #
        # FileId
        # An int value containing the unique identifier of the data file
        # that contains this token.

        self.create_table_description(
            self.corpus_table,
            [Identifier(self.corpus_id, "BIGINT UNSIGNED NOT NULL"),
             Column(self.corpus_sentence, "INT UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_file_id, self.file_table)])

        self._sentence_id = 0
        self._meta_table = None
        self._meta_file = None

    @staticmethod
    def validate_files(lst):
        if not lst:
            raise RuntimeError("<p>No file could be found in the selected "
                               "directory.</p> ")

    @staticmethod
    def _read_text(file_name):
        """
        Return the text content from the file as a string.

        This method uses the function detect_file_type() from the documents.py
        module in order to detect the text format type of the file. Currently
        supported file formats are: PDF, HTML, ODT, DOCX, and PLAIN. BINARY
        files are ignored.

        If the file is a PLAIN text file, and if the 'chardet' module is
        installed, it is used to detect the encoding of the files. Otherwise,
        a PLAIN text file is first decoded assuming UTF-8, and if that fails,
        assuming Latin-1/ISO-8859-1. Note that this may cause wrong character
        encodings in text files that use a different encoding! Using 'chardet'
        is therefore strongly recommended.

        Parameters
        ----------
        file_name : str
            The path to the file

        Returns
        -------
        raw_text : str
            The content of the file as a text string.
        """
        file_type = detect_file_type(file_name)

        if file_type == FT_PDF:
            if options.use_pdfminer:
                try:
                    raw_text = pdf_to_str(file_name)
                except Exception as e:
                    logging.error(f"Error in PDF file {file_name}: {e}")
                    return ""
            else:
                logging.warning(f"Ignoring PDF file {file_name} (the required "
                                "Python module 'pdfminer' is not available)")
                return ""

        elif file_type == FT_DOCX:
            if options.use_docx:
                try:
                    raw_text = docx_to_str(file_name)
                except Exception as e:
                    logging.error(f"Error in MS Word file {file_name}: {e}")
                    return ""
            else:
                logging.warning(f"Ignoring MS Word file {file_name} (the "
                                "required Python module 'python-docx' is not "
                                "available)")
                return ""

        elif file_type == FT_ODT:
            if options.use_odfpy:
                try:
                    raw_text = odt_to_str(file_name)
                except Exception as e:
                    logging.error("Error in OpenDocument Text file "
                                  f"{file_name}: {e}")
                    return ""
            else:
                logging.warning(f"Ignoring ODT file {file_name} (the required "
                                "Python module 'odtpy' is not available)")
                return ""

        elif file_type == FT_HTML:
            if options.use_bs4:
                try:
                    raw_text = html_to_str(file_name)
                except Exception as e:
                    logging.error(f"Error in HTML file {file_name}: {e}")
                    return ""
            else:
                logging.warning(f"Ignoring HTML file {file_name} (the "
                                "required Python module 'BeautifulSoup' is "
                                "not available)")
                return ""
        elif file_type == FT_PLAIN:
            raw_text = plain_to_str(file_name)
        else:
            # Unsupported format, e.g. BINARY.
            logging.warning(f"Ignoring unsupported file format {file_type}, "
                            f"file {file_name}")
            return ""

        if raw_text == "":
            logging.warning(f"No text could be retrieved from {file_type} "
                            f"file {file_name}")
        else:
            logging.info(f"Read {file_type} file {file_name}, {len(raw_text)} "
                         "characters")

        return raw_text

    def add_token(self, token_string, token_pos=None):
        # get lemma string:
        if all(x in string.punctuation for x in token_string):
            token_pos = "PUNCT"
            lemma = token_string
        else:
            try:
                # use the current lemmatizer to assign the token to a lemma:
                lemma = self._lemmatize(token_string,
                                        self._pos_translate(token_pos))
            except Exception:
                lemma = token_string

        # get word id, and create new word if necessary:
        word_dict = {self.word_lemma: lemma.lower(),
                     self.word_label: token_string}
        if token_pos and self.arguments.use_nltk:
            word_dict[self.word_pos] = token_pos
        word_id = self.table(self.word_table).get_or_insert(word_dict,
                                                            case=True)

        # store new token in corpus table:
        return self.add_token_to_corpus(
            {self.corpus_word_id: word_id,
             self.corpus_sentence: self._sentence_id,
             self.corpus_file_id: self._file_id})

    def add_metadata(self, file_name, column):
        capt = Capturer(stderr=True)
        with capt:
            df = self.arguments.metaoptions.read_file(self.arguments.metadata)
        for x in capt:
            s = f"File {self.arguments.path} – {x}"
            logging.warning(s)
            print(s)
        meta_columns = []
        for i, col in enumerate(df.columns):
            if i == column:
                self.file_name = col
            else:
                meta_columns.append(col)

        # prepare a dataframe that adds the correct file path to the meta data
        path_list = []
        file_list = []
        for root, dirs, files in os.walk(self.arguments.path):
            for filename in files:
                if (df[self.file_name] == filename).any():
                    path_list.append(root)
                    file_list.append(filename)
        df2 = pd.DataFrame({self.file_path: path_list,
                            self.file_name: file_list})

        # merge the data frames:
        df = df.merge(df2, how="inner", on=[self.file_name])

        fn_length = int(max(df[self.file_name].str.len()))
        lst = [Identifier(self.file_id, "MEDIUMINT UNSIGNED NOT NULL"),
               Column(self.file_path, "VARCHAR(4096) NOT NULL"),
               Column(self.file_name, f"VARCHAR({fn_length}) NOT NULL")]

        for col in meta_columns:
            rc_feature = f"file_{col.lower()}"
            setattr(self, rc_feature, col)
            if df[col].dtype == int:
                lst.append(Column(col, "MEDIUMINT"))
            elif df[col].dtype == float:
                lst.append(Column(col, "REAL"))
            else:
                col_length = int(max(df[col].str.len()))
                lst.append(Column(col, f"VARCHAR({col_length})"))

        self.create_table_description(self.file_table, lst)
        self.special_files.append(os.path.basename(file_name))

        self._meta_table = df
        self._meta_file = file_name

    def has_metadata(self, file_name):
        if self._meta_table is None:
            return False
        basename = os.path.basename(file_name)
        val = any(self._meta_table[self.file_name] == basename)
        return val

    def store_metadata(self):
        self.DB.load_dataframe(self._meta_table,
                               self.file_table,
                               self.file_id)

    def store_filename(self, file_name):
        if self.arguments.metadata:
            basename = os.path.basename(file_name)
            if (basename not in self.special_files and
                    self.has_metadata(basename)):
                self._file_id = self._meta_table[
                    self._meta_table[
                        self.file_name] == basename].index[0]
        else:
            super(BuilderClass, self).store_filename(file_name)

    def build_initialize(self):
        super(BuilderClass, self).build_initialize()
        if self.arguments.use_nltk:
            import nltk

            # the WordNet lemmatizer will be used to obtain the lemma for a
            # given word:
            self._lemmatize = (
                lambda x, y: nltk.stem.wordnet.WordNetLemmatizer().lemmatize(
                    x, pos=y))

            # The NLTK POS tagger produces some labels that are different from
            # the labels used in WordNet. In order to use the WordNet
            # lemmatizer for all words, we need a function that translates
            # these labels:
            self._pos_translate = lambda x: {
                'NN': nltk.corpus.wordnet.NOUN,
                'JJ': nltk.corpus.wordnet.ADJ,
                'VB': nltk.corpus.wordnet.VERB,
                'RB': nltk.corpus.wordnet.ADV}[x.upper()[:2]]
        else:
            # The default lemmatizer is pretty dumb and simply turns the
            # word-form to lower case so that at least 'Dogs' and 'dogs' are
            # assigned the same lemma -- which is a different lemma from the
            # one assigned to 'dog' and 'Dog'.
            #
            # If NLTK is used, the lemmatizer will use the data from WordNet,
            # which will result in much better results.
            self._lemmatize = lambda x, y: x
            self._pos_translate = lambda x: x

    def process_file(self, file_name):
        """
        Process a text file.

        This method reads the text content of the file. Several text file
        formats are supported (PDF, DOCX, ODT, HTML, PLAIN).

        It first attempt to tokenize, lemmatize, and POS-tag the words in the
        text. If NLTK is available, it is used for that, otherwise the dumb
        default tokenizer/lemmatizer (which is *really* dumb, and does not
        even attempt to create POS tags) is used.

        Then, if the token does not exist in the word table, add a new word
        with its lemma and POS tag to the word table. Finally, add the token
        with its word identifier to the corpus table, and proceed with the
        next token.

        Parameters
        ----------
        file_name : string
            The path name of the file that is to be processed
        """

        if file_name == self._meta_file:
            return

        basename = os.path.basename(file_name)
        if basename in self.special_files:
            return

        if not self.has_metadata(basename) and self.arguments.use_meta:
            msg = f"{basename} not in meta data."
            logging.warning(msg)

        try:
            raw_text = self._read_text(file_name)
        except Exception as e:
            msg = f"Could not read file {basename}: {str(e)}"
            logging.warning(msg)
            return

        # if possible, use NLTK for lemmatization, tokenization, and tagging:
        if self.arguments.use_nltk:
            import nltk
            # Create a list of sentences from the content of the current file
            # and process this list one by one:
            sentence_list = nltk.sent_tokenize(raw_text)
            for sentence in sentence_list:
                self._sentence_id += 1
                # use NLTK tokenizer and POS tagger on this sentence:
                tokens = nltk.word_tokenize(sentence)
                pos_map = nltk.pos_tag(tokens)

                # FIXME: the NLTK tokenizer doesn't seem to be very happy if
                # sentences start with quotation marks. This is evidenced
                # for instance in chapter_04.txt from the ALICE texts where
                # <shall> in the string
                #
                # 'But then,' thought Alice, 'shall I NEVER get any older ...
                #
                # is not separated from the initial quotation mark.

                for current_token, current_pos in pos_map:
                    # store each token:
                    self.add_token(current_token, current_pos)
        else:
            # use a dumb tokenizer that simply splits the file content by
            # spaces:

            tokens = raw_text.replace("\n", " ").split(" ")

            final_punctuation = []

            for token in [x.strip() for x in tokens if x.strip()]:
                # any punctuation at the beginning of the token is added to the
                # corpus as a punctuation token, and is also stripped from the
                # token:
                while token and token[0] in string.punctuation:
                    self.add_token(token[0], "PUNCT")
                    token = token[1:]

                # Try to detect sentence boundaries.
                # A sentence boundary is assumed if
                # (a) there is final punctuation
                # (b) final_punctuation contains only the sentence-delimiting
                #     punctuation marks .?!
                # (c) the next word starts with a captial letter

                if (token and
                        final_punctuation and
                        not re_punct.sub("", "".join(final_punctuation)) and
                        token[0] == token[0].upper()):
                    self._sentence_id += 1

                # next, detect any word-final punctuation:
                final_punctuation = []
                for ch in reversed(token):
                    if ch in string.punctuation:
                        final_punctuation.insert(0, ch)
                    else:
                        break
                if final_punctuation == ["."]:
                    # a single word-final full stop is considered to be a part
                    # of an abbreviation if there are more than one full stop
                    # in the token, e.g. in "U.S.A.". Otherwise, it is treated
                    # as sentence punctuation.
                    # This simple approach will also strip the full stop from
                    # abbreviations such as "Mr.".
                    if token.count(".") > 1:
                        final_punctuation = []

                # strip final punctuation from token:
                if final_punctuation:
                    token = token[:-len(final_punctuation)]

                # add the token to the corpus:
                if token:
                    self.add_token(token)

                # add final punctuation:
                for p in final_punctuation:
                    self.add_token(p, "PUNCT")

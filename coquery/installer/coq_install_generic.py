# -*- coding: utf-8 -*-

"""
coq_install_generic.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery.corpusbuilder import *
from coquery import options

class BuilderClass(BaseCorpusBuilder):
    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    word_table = "Lexicon"
    word_id = "WordId"
    word_lemma = "Lemma"
    word_label = "Word"
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

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
        
        if pos:
            self.word_pos = "POS"
            self.create_table_description(self.word_table,
                [Identifier(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
                Column(self.word_lemma, "VARCHAR(40) NOT NULL"),
                Column(self.word_pos, "VARCHAR(12) NOT NULL"),
                Column(self.word_label, "VARCHAR(40) NOT NULL")])
        else:
            self.create_table_description(self.word_table,
                [Identifier(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
                Column(self.word_lemma, "VARCHAR(40) NOT NULL"),
                Column(self.word_label, "VARCHAR(40) NOT NULL")])

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

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
            Column(self.file_name, "TINYTEXT NOT NULL"),
            Column(self.file_path, "TINYTEXT NOT NULL")])

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
        
        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "BIGINT(20) UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_file_id, self.file_table)])

    @staticmethod
    def validate_files(l):
        if len(l) == 0:
            raise RuntimeError("<p>No file could be found in the selected directory.</p> ")

    def _read_text(self, file_name):
        """
        Return the text content from the file as a string.
        
        This method uses a heuristic to detect the file type of the specified 
        file. Currently supported file types are PDF and MS Word documents. 
        Planned file types that are not implemented yet are HTML and ODT files.
        
        If no supported file type can be detected, the file is assumed to be 
        a plain text file. If the 'chardet' module is installed, it is used 
        to detect the encoding of the files. Otherwise, the file is first 
        decoded assuming UTF-8, and if that fails, assuming Latin-1/ISO-8859-1. 
        This may fail horribly if the file is NOT a plain text file, but for 
        example a binary file!
        
        Parameters
        ----------
        file_name : str
            The path to the file 
            
        Returns
        -------
        raw_text : str
            The content of the file as a text string.
        """
        raw_text = None
        _, ext = os.path.splitext(file_name)

        with open(file_name, "rb") as fp:
            first_line = fp.readline().decode("utf-8")
        if first_line[:5] == "%PDF-":
            file_type = "PDF"
        elif first_line[:2] == "PK" and ext.lower() == ".docx":
            file_type = "DOCX"
        elif first_line[:2] == "PK" and ext.lower() == ".odt":
            file_type = "ODT"
        elif first_line.strip().lower().startswith("<!doctype html>"):
            file_type = "HTML"
        else:
            file_type = "PLAIN"

        if file_type == "PDF" and options._use_pdfminer:
            from coquery.documents import pdf_to_txt
            try:
                raw_text = pdf_to_txt(file_name)
            except (UnicodeDecodeError, TypeError) as e:
                logger.error("Error in PDF file {}: {}".format(file_name, e))

        elif file_type == "DOCX" and options._use_docx:
            from coquery.documents import docx_to_txt
            try:
                raw_text = docx_to_txt(file_name)
            except (Exception) as e:
                logger.error("Error in MS Word file {}: {}".format(file_name, e))

        elif file_type == "ODT" and options._use_docx:
            from coquery.documents import odt_to_txt
            try:
                raw_text = odt_to_txt(file_name)
            except (Exception) as e:
                logger.error("Error in OpenDocument Text file {}: {}".format(file_name, e))

        elif file_type == "HTML":
            from coquery.documents import html_to_txt
            try:
                raw_text = html_to_txt(file_name)
            except (Exception) as e:
                logger.error("Error in OpenDocument Text file {}: {}".format(file_name, e))
                
        elif file_type == "PLAIN":
            # Use chardet module for encoding detection?
            if options._use_chardet:
                import chardet
                content = open(file_name, "rb").read()
                detection = chardet.detect(content)
                encoding = detection["encoding"]
                confidence = detection["confidence"]
                if confidence < 0.5:
                    logger.warn("Low confidence ({:.2}) about the encoding of file {}. Assuming encoding '{}'.".format(
                        confidence, file_name, encoding))
                else:
                    logger.info("Encoding '{}' detected for file {} (confidence: {:.2})".format(encoding, file_name, confidence))
                raw_text = content.decode(encoding)
            else:
                try:
                    with codecs.open(file_name, "r", encoding=self.arguments.encoding) as input_file:
                        raw_text = input_file.read()
                except UnicodeDecodeError:
                    with codecs.open(file_name, "r", encoding="ISO-8859-1") as input_file:
                        raw_text = input_file.read()

        if raw_text == None:
            logger.warn("No data from file {}".format(file_name))
        
        return raw_text

    def process_file(self, file_name):
        """ 
        Process a text file.
        
        This method reads the content of the file, and interprets it as an
        plain text file. It first attempt to tokenize the text, and to 
        assign a POS tag to each token (using NLTK if possible). Then, if
        the token does not exist in the word table, add a new word with its 
        POS tag to the word table. Then, try to lemmatize any new word. 
        Finally, add the token with its word identifier to the corpus table,
        and proceed with the next word.
        
        Parameters
        ----------
        file_name : string
            The path name of the file that is to be processed
        """

        

        # try to identify supported file types:

        raw_text = self._read_text(file_name)
            
        tokens = []

        # if possible, use NLTK for lemmatization, tokenization, and tagging:
        if self.arguments.use_nltk:
            import nltk

            # the WordNet lemmatizer will be used to obtain the lemma for a
            # given word:
            self._lemmatize = lambda x,y: nltk.stem.wordnet.WordNetLemmatizer().lemmatize(x, pos=y)
            
            # The NLTK POS tagger produces some labels that are different from
            # the labels used in WordNet. In order to use the WordNet 
            # lemmatizer for all words, we need a function that translates 
            # these labels:
            self._pos_translate = lambda x: {'NN': nltk.corpus.wordnet.NOUN, 
                'JJ': nltk.corpus.wordnet.ADJ,
                'VB': nltk.corpus.wordnet.VERB,
                'RB': nltk.corpus.wordnet.ADV} [x.upper()[:2]]

            # Create a list of sentences from the content of the current file
            # and process this list one by one:
            sentence_list = nltk.sent_tokenize(raw_text)
            for sentence in sentence_list:
                # use NLTK tokenizer and POS tagger on this sentence:
                tokens = nltk.word_tokenize(sentence)
                pos_map = nltk.pos_tag(tokens)
                    
                for current_token, current_pos in pos_map:
                    # store each token:
                    self.add_token(current_token.strip(), current_pos)
        else:
            # The default lemmatizer is pretty dumb and simply turns the 
            # word-form to lower case so that at least 'Dogs' and 'dogs' are 
            # assigned the same lemma -- which is a different lemma from the
            # one assigned to 'dog' and 'Dog'.
            #
            # If NLTK is used, the lemmatizer will use the data from WordNet,
            # which will result in much better results.
            self._lemmatize = lambda x: x.lower()
            self._pos_translate = lambda x: x
            
            # use a dumb tokenizer that simply splits the file content by 
            # spaces:            
            
            tokens = raw_text.replace("\n", " ").split(" ")
            
            for token in [x.strip() for x in tokens if x.strip()]:
                # any punctuation at the beginning of the token is added to the
                # corpus as a punctuation token, and is also stripped from the
                # token:
                while token and token[0] in string.punctuation:
                    self.add_token(token[0], "PUNCT")
                    token = token[1:]
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



def main():
    BuilderClass().build()
    
if __name__ == "__main__":
    main()
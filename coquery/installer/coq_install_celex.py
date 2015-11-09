from __future__ import unicode_literals
from __future__ import print_function

from corpusbuilder import *
import codecs

class CELEXBuilder(BaseCorpusBuilder):
    file_filter = "ep?.cd"
    
    def __init__(self, gui=False, *args):
        # all corpus builders have to call the inherited __init__ function:
        super(CELEXBuilder, self).__init__(gui, *args)

        self.corpus_table = "epw"
        self.corpus_id = "IdNum"
        self.corpus_word_id = "IdNum"
        
        self.word_table = "epw"
        self.word_id = "IdNum"
        self.word_label = "Word"
        self.word_lemma_id = "IdNumLemma"
        self.word_cob = "Word_Cob"
        #self.word_proncnt = "Word_PronCnt"
        #self.word_pronstatus = "Word_PronStatus"
        self.word_phonstrsdisc = "Word_PhonStrsDISC"
        self.word_phoncvbr = "Word_PhonCVBr"
        self.word_phonsylbclx = "Word_PhonSylBCLX"

        self.lemma_table = "epl"
        self.lemma_id = "IdNum"
        self.lemma_label = "Head"
        self.lemma_cob = "Lemma_Cob"
        #self.lemma_proncnt = "Lemma_PronCnt"
        #self.lemma_pronstatus = "Lemma_PronStatus"
        self.lemma_phonstrsdisc = "Lemma_PhonStrsDISC"
        self.lemma_phoncvbr = "Lemma_PhonCVBr"
        self.lemma_phonsylbclx = "Lemma_PhonSylBCLX"
        
        self.create_table_description(self.lemma_table,
            [Primary(self.lemma_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.lemma_label, "VARCHAR(35) NOT NULL"),
             Column(self.lemma_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             #Column(self.lemma_proncnt, "SMALLINT(2) UNSIGNED NOT NULL"),
             #Column(self.lemma_pronstatus, "ENUM('P','S')"),
             Column(self.lemma_phonstrsdisc, "VARCHAR(41) NOT NULL"),
             Column(self.lemma_phoncvbr, "VARCHAR(53) NOT NULL"),
             Column(self.lemma_phonsylbclx, "VARCHAR(53) NOT NULL")])

        self.create_table_description(self.word_table,
            [Primary(self.word_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(35) NOT NULL"),
             Column(self.word_cob, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Link(self.word_lemma_id, self.lemma_table),
             #Column(self.word_proncnt, "SMALLINT(2) UNSIGNED NOT NULL"),
             #Column(self.word_pronstatus, "ENUM('P','S')"),
             Column(self.word_phonstrsdisc, "VARCHAR(41) NOT NULL"),
             Column(self.word_phoncvbr, "VARCHAR(53) NOT NULL"),
             Column(self.word_phonsylbclx, "VARCHAR(53) NOT NULL")])



    def build_load_files(self):
        files = self.get_file_list(self.arguments.path)
        if len(files) == 0:
            raise RuntimeError("<p><b>No dictionary file could be found in the selected directory.</p><p>{}</p><p>The file name of dictionary files has to start with the sequence <code>cmudict</code>. If you have saved the CMUdict file under a different name, rename it so that its file name matches this sequence.</p><p>If you have not downloaded andictionary file yet, please go to the CMUdict website and follow the download instructions there.</p> ".format("<br/>".join(files)))

        for file_name in files:
            with open(file_name, "r") as input_file:
                content = input_file.readlines()

            if file_name.lower().endswith("epw.cd"):
                s1 = "Phonology data (word forms)"
                which = "epw"
            else:
                s1 = "Phonology data (lemmas)"
                which = "epl"

            if self._widget:
                self._widget.progressSet.emit(len(content) // 100, "Reading {}...".format(s1))
                self._widget.progressUpdate.emit(0)

            for i, current_line in enumerate(content):
                current_line = current_line.strip()
                columns = current_line.split("\\")
                
                if which == "epw":
                    (self._value_word_id, 
                    self._value_word_label,
                    self._value_word_cob,
                    self._value_word_lemma_id,
                    self._value_word_proncnt,
                    self._value_word_pronstatus,
                    self._value_word_phonstrsdisc,
                    self._value_word_phoncvbr,
                    self._value_word_phonsylbclx) = columns[:9]

                    self.table(self.word_table).add(
                        {self.word_id: self._value_word_id,
                        self.word_label: self._value_word_label,
                        self.word_cob: self._value_word_cob,
                        self.word_lemma_id: self._value_word_lemma_id,
                        #self.word_proncnt: self._value_word_proncnt,
                        #self.word_pronstatus: self._value_word_pronstatus,
                        self.word_phonstrsdisc: self._value_word_phonstrsdisc,
                        self.word_phoncvbr: self._value_word_phoncvbr,
                        self.word_phonsylbclx: self._value_word_phonsylbclx})
                elif which == "epl":
                    (self._value_lemma_id, 
                    self._value_lemma_label,
                    self._value_lemma_cob,
                    self._value_lemma_proncnt,
                    self._value_lemma_pronstatus,
                    self._value_lemma_phonstrsdisc,
                    self._value_lemma_phoncvbr,
                    self._value_lemma_phonsylbclx) = columns[:8]

                    self.table(self.lemma_table).add(
                        {self.lemma_id: self._value_lemma_id,
                        self.lemma_label: self._value_lemma_label,
                        self.lemma_cob: self._value_lemma_cob,
                        #self.lemma_proncnt: self._value_lemma_proncnt,
                        #self.lemma_pronstatus: self._value_lemma_pronstatus,
                        self.lemma_phonstrsdisc: self._value_lemma_phonstrsdisc,
                        self.lemma_phoncvbr: self._value_lemma_phoncvbr,
                        self.lemma_phonsylbclx: self._value_lemma_phonsylbclx})
                    

                if self._widget and not i % 100:
                    self._widget.progressUpdate.emit(i // 100)
            self._widget.progressSet.emit(0, "Committing {}...".format(s1))
            self.commit_data()

    @staticmethod
    def get_title():
        return "CELEX2 Lexical Database (English)"

    @staticmethod
    def get_url():
        return 'https://catalog.ldc.upenn.edu/LDC96L14'
    
    @staticmethod
    def get_name():
        return "CELEX2"
    
    @staticmethod
    def get_db_name():
        return "celex"
    
    @staticmethod
    def get_references():
        return ["Baayen, R, R Piepenbrock, and L Gulikers. 1995. <i>CELEX2 LDC96L14</i>. Web Download. Philadelphia: Linguistic Data Consortium."]

    @staticmethod
    def get_license():
        return "The CELEX Lexical Database is released under the terms of the <a href='https://catalog.ldc.upenn.edu/license/celex-user-agreement.pdf'>CELEX 2 User Agreement</a>."
    
    @staticmethod
    def get_description():
        return ["The CELEX lexical database for English contains detailed information for XXX lemmas (about 100,000 inflected forms) on:",
                """<ul><li>orthography (variations in spelling [not supported by Coquery], hyphenation)</li>
                <li>phonology (phonetic transcriptions, variations in pronunciation [not supported by Coquery], syllable structure, primary stress)</li>
                <li>morphology (derivational and compositional structure, inflectional paradigms)</li>
                <li>syntax (word class, word class-specific subcategorizations, argument structures)</li>
                <li>word frequency (summed word and lemma counts, based on representative text corpora)</li></ul>"""]

BuilderClass = CELEXBuilder

if __name__ == "__main__":
    BuilderClass().build()
    
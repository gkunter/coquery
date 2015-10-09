from __future__ import unicode_literals
from __future__ import print_function

from corpusbuilder import *
import codecs

class CELEXBuilder(BaseCorpusBuilder):
    file_filter = "epw.cd"
    
    def __init__(self, gui=False, *args):
        # all corpus builders have to call the inherited __init__ function:
        super(CELEXBuilder, self).__init__(gui, *args)

        self.corpus_table = "epw"
        self.corpus_id = "IdNum"
        self.corpus_word_id = "IdNum"
        self.word_table = "epw"
        self.word_id = "IdNum"
        self.word_label = "Word"
        self.word_cob = "Cob"
        #self.word_lemma_id = "IdNumLemma"
        self.word_proncnt = "PronCnt"
        self.word_pronstatus = "PronStatus"
        self.word_phonstrsdisc = "PhonStrsDISC"
        self.word_phoncvbr = "PhonCVBr"
        self.word_phonsylbclx = "PhonSylBCLX"

        self.create_table_description(self.word_table,
            [Primary(self.word_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Column(self.word_label, "CHAR(20) NOT NULL"),
             Column(self.word_cob, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             #Link(self.word_lemma_id, "MEDIUMINT(5) UNSIGNED NOT NULL"),
             Column(self.word_proncnt, "SMALLINT(2) UNSIGNED NOT NULL"),
             Column(self.word_pronstatus, "ENUM('P','S')"),
             Column(self.word_phonstrsdisc, "CHAR(29) NOT NULL"),
             Column(self.word_phoncvbr, "CHAR(35) NOT NULL"),
             Column(self.word_phonsylbclx, "CHAR(36) NOT NULL")])

    def build_load_files(self):
        files = self.get_file_list(self.arguments.path)
        if len(files) > 1:
            raise RuntimeError("<p><b>There is more than one file in the selected directory.</b></p><p>{}</p><p>Please remove the unneeded files, and try again to install.".format("<br/>".join(files)))
        if len(files) == 0:
            raise RuntimeError("<p><b>No dictionary file could be found in the selected directory.</p><p>{}</p><p>The file name of dictionary files has to start with the sequence <code>cmudict</code>. If you have saved the CMUdict file under a different name, rename it so that its file name matches this sequence.</p><p>If you have not downloaded andictionary file yet, please go to the CMUdict website and follow the download instructions there.</p> ".format("<br/>".join(files)))
        # FIXME: read directly into DataFrame:
        with open(files[0], "r") as input_file:
            content = input_file.readlines()

        if self._widget:
            self._widget.progressSet.emit(len(content) // 100, "Reading dictionary file...")
            self._widget.progressUpdate.emit(0)

        for i, current_line in enumerate(content):
            current_line = current_line.strip()
            columns = current_line.split("\\")
            
            (self._value_word_id, 
            self._value_word_label,
            self._value_word_cob,
            _,
            self._value_word_proncnt,
            self._value_word_pronstatus,
            self._value_word_phonstrsdisc,
            self._value_word_phoncvbr,
            self._value_word_phonsylbclx) = columns[:9]

            self.table(self.word_table).add(
                {self.word_id: self._value_word_id,
                 self.word_label: self._value_word_label,
                 self.word_cob: self._value_word_cob,
                 #self.word_idnumlemma: self._value_word_idnumlemma,
                 self.word_proncnt: self._value_word_proncnt,
                 self.word_pronstatus: self._value_word_pronstatus,
                 self.word_phonstrsdisc: self._value_word_phonstrsdisc,
                 self.word_phoncvbr: self._value_word_phoncvbr,
                 self.word_phonsylbclx: self._value_word_phonsylbclx})

            if self._widget and not i % 100:
                self._widget.progressUpdate.emit(i // 100)
        self.commit_data()

    @staticmethod
    def get_title():
        return ""

    @staticmethod
    def get_url():
        return ''
    
    @staticmethod
    def get_name():
        return "CELEX_Eng"
    
    @staticmethod
    def get_license():
        return ""
    
    @staticmethod
    def get_description():
        return [""]

BuilderClass = CELEXBuilder

if __name__ == "__main__":
    BuilderClass().build()
    